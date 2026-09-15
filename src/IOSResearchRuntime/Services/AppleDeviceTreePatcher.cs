using System.Buffers.Binary;
using System.Text;

namespace IOSResearchRuntime.Services;

public sealed class AppleDeviceTreePatcher
{
    private static readonly byte[][] SupportedDrivers =
    [
        Encoding.ASCII.GetBytes("AppleARM"),
        Encoding.ASCII.GetBytes("aic"),
        Encoding.ASCII.GetBytes("arm-io"),
        Encoding.ASCII.GetBytes("uart-1,samsung")
    ];

    private const uint Frequency = 0x100000;
    private const string FirmwareName = "qemu-sptm";
    private const int AmccBankStride = 0x100;
    private const int AmccLowerLimitRegister = 0x10;
    private const int AmccUpperLimitRegister = 0x20;

    public void PatchFile(string sourcePath, string destinationPath, string nvramPath)
    {
        var source = File.ReadAllBytes(sourcePath);
        var nvram = File.ReadAllBytes(nvramPath);

        var offset = 0;
        var root = DecodeNode(source, ref offset);

        if (offset > source.Length)
        {
            throw new InvalidDataException("DeviceTree parser consumed data past the end of the file.");
        }

        Fixup(root, nvram);
        var encoded = EncodeNode(root);
        File.WriteAllBytes(destinationPath, encoded);
    }

    private static AdtNode DecodeNode(ReadOnlySpan<byte> data, ref int offset)
    {
        EnsureAvailable(data, offset, 8);

        var propertyCount = BinaryPrimitives.ReadUInt32LittleEndian(data.Slice(offset, 4));
        var childCount = BinaryPrimitives.ReadUInt32LittleEndian(data.Slice(offset + 4, 4));
        offset += 8;

        var node = new AdtNode();

        for (var i = 0u; i < propertyCount; i++)
        {
            EnsureAvailable(data, offset, 36);

            var name = DecodeNullTerminatedString(data.Slice(offset, 32));
            var rawLength = BinaryPrimitives.ReadUInt32LittleEndian(data.Slice(offset + 32, 4));
            var actualLength = (int)(rawLength & ~0x80000000u);
            var paddedLength = RoundUpTo4(actualLength);
            offset += 36;

            EnsureAvailable(data, offset, paddedLength);
            var propertyBytes = data.Slice(offset, paddedLength).ToArray();
            offset += paddedLength;

            node.Properties[name] = DecodeProperty(name, propertyBytes);
        }

        for (var i = 0u; i < childCount; i++)
        {
            node.Children.Add(DecodeNode(data, ref offset));
        }

        return node;
    }

    private static object DecodeProperty(string name, byte[] bytes)
    {
        if (name == "name" || IsProbablyString(bytes))
        {
            return DecodeNullTerminatedString(bytes);
        }

        return bytes.Length switch
        {
            0 => AdtNull.Value,
            4 => BinaryPrimitives.ReadUInt32LittleEndian(bytes),
            8 => BinaryPrimitives.ReadUInt64LittleEndian(bytes),
            _ => bytes
        };
    }

    private static bool IsProbablyString(byte[] bytes)
    {
        if (bytes.Length == 0)
        {
            return false;
        }

        var zeroIndex = Array.IndexOf(bytes, (byte)0);
        var textLength = zeroIndex < 0 ? bytes.Length : zeroIndex;

        if (textLength < 3)
        {
            return false;
        }

        if (zeroIndex >= 0)
        {
            for (var i = zeroIndex; i < bytes.Length; i++)
            {
                if (bytes[i] != 0)
                {
                    return false;
                }
            }
        }

        for (var i = 0; i < textLength; i++)
        {
            var value = bytes[i];
            if (value is < 0x20 or > 0x7e)
            {
                return false;
            }
        }

        return true;
    }

    private static void Fixup(AdtNode root, byte[] nvram)
    {
        root.Properties["platform-name"] = GetPlatformName(root);
        var socGeneration = GetSocGeneration(root);

        var chosen = root.Child("chosen");
        if (socGeneration <= 14)
        {
            chosen.Properties["dram-base"] = 0x800000000UL;
            chosen.Properties["dram-size"] = 0x200000000UL;
        }
        else
        {
            chosen.Properties["dram-base"] = 0x10000000000UL;
            chosen.Properties["dram-size"] = 0x200000000UL;
        }

        chosen.Properties["firmware-version"] = FirmwareName;
        chosen.Properties["system-firmware-version"] = FirmwareName;

        var cpu0 = root.Child("cpus").Child("cpu0");
        cpu0.Properties["state"] = "running";

        var randomSeed = chosen.Properties["random-seed"];
        if (randomSeed is not byte[] randomSeedBytes)
        {
            throw new InvalidDataException("chosen/random-seed is not a binary property.");
        }

        chosen.Properties["random-seed"] = Enumerable.Repeat((byte)'A', randomSeedBytes.Length).ToArray();
        chosen.Properties["kernel-ctrr-to-be-enabled"] = 0u;

        var armIo = root.Child("arm-io");
        var defaults = root.Child("defaults");
        defaults.Properties["serial-device"] = armIo.Child("uart0").Properties["AAPL,phandle"];

        cpu0.Properties["memory-frequency"] = Frequency;
        cpu0.Properties["peripheral-frequency"] = Frequency;
        cpu0.Properties["fixed-frequency"] = Frequency;
        cpu0.Properties["clock-frequency"] = Frequency;
        cpu0.Properties["timebase-frequency"] = Frequency;

        chosen.Properties["nvram-bank-count"] = 1u;
        chosen.Properties["nvram-current-bank"] = 1u;
        chosen.Properties["nvram-proxy-data"] = nvram;
        chosen.Properties["nvram-total-size"] = checked((uint)nvram.Length);
        chosen.Properties["nvram-bank-size"] = checked((uint)nvram.Length);

        var sep = armIo.Child("sep").Child("iop-sep-nub");
        if (sep.TryChild("InvalidateHmac", out var invalidateHmac))
        {
            invalidateHmac.Properties["config"] = 1u;
            invalidateHmac.Properties["sio-hmac1-offset"] = 0UL;
            invalidateHmac.Properties["sio-hmac1-disable-mask"] = ulong.MaxValue;
        }

        armIo.RemoveChild("dockchannel-uart");

        root.Properties["no-rtc"] = AdtNull.Value;
        var rtc = new AdtNode();
        rtc.Properties["name"] = "rtc";
        rtc.Properties["__placeholder_val"] = AdtNull.Value;
        root.Children.Add(rtc);

        defaults.Properties["vmm-present"] = 1u;

        var amcc = chosen.Child("lock-regs").Child("amcc");
        amcc.Properties["aperture-count"] = 1u;
        amcc.Properties["aperture-size"] = 0x4000u;
        amcc.Properties["plane-count"] = 1u;
        amcc.Properties["plane-stride"] = 0u;
        amcc.Properties["plane-size"] = amcc.Properties["aperture-size"];
        amcc.Properties["aperture-phys-addr"] = 0x220000000UL;
        amcc.Properties["cache-status-reg-offset"] = 0u;
        amcc.Properties["cache-status-reg-mask"] = 0u;
        amcc.Properties["cache-status-reg-value"] = 0u;

        var banks = new[] { "a", "b", "c", "d" };
        for (var i = 0; i < banks.Length; i++)
        {
            var ctrr = amcc.Child($"amcc-ctrr-{banks[i]}");

            ctrr.Properties["page-size-shift"] = 0u;
            ctrr.Properties["lower-limit-reg-offset"] =
                checked((uint)((AmccBankStride * i) + AmccLowerLimitRegister));
            ctrr.Properties["upper-limit-reg-offset"] =
                checked((uint)((AmccBankStride * i) + AmccUpperLimitRegister));
            ctrr.Properties["upper-limit-reg-mask"] = uint.MaxValue;
            ctrr.Properties["lower-limit-reg-mask"] = uint.MaxValue;
            ctrr.Properties["lock-reg-offset"] = 0u;
            ctrr.Properties["lock-reg-mask"] = 0u;
            ctrr.Properties["lock-reg-value"] = 0u;
            ctrr.Properties["enable-reg-offset"] = 0u;
            ctrr.Properties["enable-reg-mask"] = 1u;
            ctrr.Properties["enable-reg-value"] = 1u;
            ctrr.Properties["write-disable-reg-offset"] = 0u;
            ctrr.Properties["write-disable-reg-mask"] = 1u;
            ctrr.Properties["write-disable-reg-value"] = 1u;
        }

        DeleteUnsupportedCompatible(root);
        FixupAic(armIo.Child("aic"));
        FixupSptm(root);

        root.Properties.Remove("secure-root-prefix");
    }

    private static void DeleteUnsupportedCompatible(AdtNode node)
    {
        foreach (var child in node.Children)
        {
            DeleteUnsupportedCompatible(child);
        }

        if (!node.Properties.TryGetValue("compatible", out var compatible))
        {
            return;
        }

        var bytes = compatible switch
        {
            string text => Encoding.UTF8.GetBytes(text),
            byte[] raw => raw,
            _ => Array.Empty<byte>()
        };

        if (!SupportedDrivers.Any(driver => Contains(bytes, driver)))
        {
            node.Properties.Remove("compatible");
        }
    }

    private static void FixupAic(AdtNode aic)
    {
        if (!aic.Properties.TryGetValue("compatible", out var compatible))
        {
            throw new InvalidDataException("aic does not have a compatible property.");
        }

        var bytes = compatible switch
        {
            string text => Encoding.UTF8.GetBytes(text),
            byte[] raw => raw,
            _ => throw new InvalidDataException("Unexpected aic compatible property type.")
        };

        if (Contains(bytes, Encoding.ASCII.GetBytes("aic,2")) ||
            Contains(bytes, Encoding.ASCII.GetBytes("aic,3")))
        {
            aic.Properties["aic-iack-offset"] = 0x1000UL;
        }
    }

    private static void FixupSptm(AdtNode root)
    {
        var map = root.Child("chosen").Child("memory-map");

        string[] regions =
        [
            "TXM-ro", "TXM-rx", "TXM-bx", "TXM-rw", "TXM-le", "TXM-entry", "TXM-virt",
            "TrustCache",
            "BootKC-rx", "BootKC-bx", "BootKC-ro", "BootKC-rs", "BootKC-rw", "BootKC-le",
            "BootKC-virt", "BootKC-entry",
            "DeviceTree",
            "SPTM-ro", "SPTM-rm", "SPTM-rx", "SPTM-rw", "SPTM-le", "SPTM-entry", "SPTM-virt",
            "BootArgs", "slide",
            "CL4-rx", "CL4-ro", "CL4-rw", "CL4-le", "CL4-dummypage", "CL4-entry", "CL4-virt",
            "RAMDisk"
        ];

        foreach (var region in regions)
        {
            var bytes = new byte[16];
            Array.Fill(bytes, (byte)0xff);
            map.Properties[region] = bytes;
        }

        map.Properties["slide"] = new byte[16];
        root.Child("arm-io").RemoveChild("sgx");
    }

    private static string GetPlatformName(AdtNode root)
    {
        var value = root.Child("arm-io").Properties["compatible"];
        var text = value switch
        {
            string str => str,
            byte[] bytes => DecodeNullTerminatedString(bytes),
            _ => throw new InvalidDataException("arm-io/compatible has an unexpected type.")
        };

        var parts = text.Split(',');
        if (parts.Length < 2)
        {
            throw new InvalidDataException("arm-io/compatible does not contain a platform name.");
        }

        return parts[1];
    }

    private static int GetSocGeneration(AdtNode root)
    {
        if (!root.Child("arm-io").Properties.TryGetValue("soc-generation", out var value) ||
            value is not string text ||
            text.Length < 2 ||
            text[0] != 'H')
        {
            return 0;
        }

        return int.TryParse(text.AsSpan(1), out var generation) ? generation : 0;
    }

    private static byte[] EncodeNode(AdtNode node)
    {
        using var stream = new MemoryStream();
        using var writer = new BinaryWriter(stream, Encoding.UTF8, leaveOpen: true);

        writer.Write(checked((uint)node.Properties.Count));
        writer.Write(checked((uint)node.Children.Count));

        foreach (var (name, value) in node.Properties)
        {
            var nameBytes = Encoding.UTF8.GetBytes(name);
            if (nameBytes.Length >= 32)
            {
                throw new InvalidDataException($"DeviceTree property name is too long: {name}");
            }

            var nameBuffer = new byte[32];
            nameBytes.CopyTo(nameBuffer, 0);
            writer.Write(nameBuffer);

            var (length, bytes) = EncodeProperty(value);
            writer.Write(checked((uint)length));
            writer.Write(bytes);
        }

        foreach (var child in node.Children)
        {
            writer.Write(EncodeNode(child));
        }

        writer.Flush();
        return stream.ToArray();
    }

    private static (int Length, byte[] Bytes) EncodeProperty(object value)
    {
        switch (value)
        {
            case byte[] bytes:
                if (bytes.Length % 4 != 0)
                {
                    throw new InvalidDataException("Raw DeviceTree property is not 4-byte aligned.");
                }

                return (bytes.Length, bytes);

            case uint u32:
            {
                var bytes = new byte[4];
                BinaryPrimitives.WriteUInt32LittleEndian(bytes, u32);
                return (4, bytes);
            }

            case ulong u64:
            {
                var bytes = new byte[8];
                BinaryPrimitives.WriteUInt64LittleEndian(bytes, u64);
                return (8, bytes);
            }

            case string text:
            {
                var raw = Encoding.UTF8.GetBytes(text);
                var length = raw.Length + 1;
                var bytes = new byte[RoundUpTo4(length)];
                raw.CopyTo(bytes, 0);
                return (length, bytes);
            }

            case AdtNull:
                return (0, Array.Empty<byte>());

            default:
                throw new InvalidDataException(
                    $"Unsupported DeviceTree property type: {value.GetType().FullName}");
        }
    }

    private static bool Contains(ReadOnlySpan<byte> haystack, ReadOnlySpan<byte> needle)
    {
        return haystack.IndexOf(needle) >= 0;
    }

    private static string DecodeNullTerminatedString(ReadOnlySpan<byte> bytes)
    {
        var zero = bytes.IndexOf((byte)0);
        var slice = zero >= 0 ? bytes[..zero] : bytes;
        return Encoding.UTF8.GetString(slice);
    }

    private static int RoundUpTo4(int value)
    {
        return checked((value + 3) & ~3);
    }

    private static void EnsureAvailable(ReadOnlySpan<byte> data, int offset, int count)
    {
        if (offset < 0 || count < 0 || offset > data.Length - count)
        {
            throw new InvalidDataException("DeviceTree is truncated.");
        }
    }

    private sealed class AdtNode
    {
        public Dictionary<string, object> Properties { get; } = new(StringComparer.Ordinal);
        public List<AdtNode> Children { get; } = [];

        public AdtNode Child(string name)
        {
            return Children.FirstOrDefault(
                child => child.Properties.TryGetValue("name", out var value) &&
                         value is string childName &&
                         childName == name)
                ?? throw new InvalidDataException($"DeviceTree child not found: {name}");
        }

        public bool TryChild(string name, out AdtNode child)
        {
            child = Children.FirstOrDefault(
                item => item.Properties.TryGetValue("name", out var value) &&
                        value is string childName &&
                        childName == name)!;

            return child is not null;
        }

        public void RemoveChild(string name)
        {
            var child = Child(name);
            Children.Remove(child);
        }
    }

    private sealed class AdtNull
    {
        private AdtNull()
        {
        }

        public static AdtNull Value { get; } = new();
    }
}

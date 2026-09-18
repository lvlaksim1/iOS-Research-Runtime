using System.Buffers.Binary;
using System.Text.Json;

internal static class ApfsStructuralEvidence
{
    internal sealed record Snapshot(
        long SuperblockOffset,
        uint BlockSize,
        ulong BlockCount,
        ulong Features,
        ulong ReadOnlyCompatibleFeatures,
        ulong IncompatibleFeatures,
        string ContainerUuid,
        ulong Oid,
        ulong Xid,
        ulong NextOid,
        ulong NextXid,
        uint XpDescBlocks,
        uint XpDataBlocks,
        ulong XpDescBase,
        ulong XpDataBase,
        uint XpDescNext,
        uint XpDataNext,
        uint XpDescIndex,
        uint XpDescLen,
        uint XpDataIndex,
        uint XpDataLen,
        ulong SpacemanOid,
        ulong OmapOid,
        ulong ReaperOid,
        ulong Flags);

    internal sealed record Comparison(Snapshot Source, Snapshot Rebuilt);

    internal static Snapshot Read(string path)
    {
        using var stream = File.OpenRead(path);
        var offset = FindNxSuperblock(stream);
        stream.Position = offset;
        var buffer = new byte[0x580];
        stream.ReadExactly(buffer);

        ulong U64(int at) => BinaryPrimitives.ReadUInt64LittleEndian(buffer.AsSpan(at, 8));
        uint U32(int at) => BinaryPrimitives.ReadUInt32LittleEndian(buffer.AsSpan(at, 4));

        var uuidBytes = buffer.AsSpan(72, 16).ToArray();
        var uuid = new Guid(uuidBytes).ToString("D");

        return new Snapshot(
            offset,
            U32(36),
            U64(40),
            U64(48),
            U64(56),
            U64(64),
            uuid,
            U64(8),
            U64(16),
            U64(88),
            U64(96),
            U32(104),
            U32(108),
            U64(112),
            U64(120),
            U32(128),
            U32(132),
            U32(136),
            U32(140),
            U32(144),
            U32(148),
            U64(152),
            U64(160),
            U64(168),
            U64(0x4D8));
    }

    internal static void Write(string path, Snapshot source, Snapshot rebuilt)
    {
        Directory.CreateDirectory(Path.GetDirectoryName(path)!);
        var options = new JsonSerializerOptions { WriteIndented = true };
        File.WriteAllText(path, JsonSerializer.Serialize(new Comparison(source, rebuilt), options));
    }

    private static long FindNxSuperblock(FileStream stream)
    {
        const int windowSize = 1024 * 1024;
        var buffer = new byte[windowSize + 3];
        long absolute = 0;
        var carry = 0;

        while (true)
        {
            var read = stream.Read(buffer, carry, windowSize);
            if (read == 0)
            {
                break;
            }

            var total = carry + read;
            for (var i = 32; i + 8 <= total; i++)
            {
                if (buffer[i] != (byte)'N' || buffer[i + 1] != (byte)'X' ||
                    buffer[i + 2] != (byte)'S' || buffer[i + 3] != (byte)'B')
                {
                    continue;
                }

                var blockSize = BinaryPrimitives.ReadUInt32LittleEndian(buffer.AsSpan(i + 4, 4));
                if (blockSize is >= 4096 and <= 65536 && (blockSize & (blockSize - 1)) == 0)
                {
                    return absolute - carry + i - 32;
                }
            }

            carry = Math.Min(3, total);
            Buffer.BlockCopy(buffer, total - carry, buffer, 0, carry);
            absolute += read;
        }

        throw new InvalidDataException($"No valid APFS NXSB superblock found in {stream.Name}.");
    }
}

using System.Buffers.Binary;
using System.Text.Json;

internal static class ApfsStructuralEvidence
{
    internal sealed record VolumeSnapshot(
        long SuperblockOffset,
        ulong Oid,
        ulong Xid,
        uint FsIndex,
        ulong Features,
        ulong ReadOnlyCompatibleFeatures,
        ulong IncompatibleFeatures,
        ulong FsReserveBlockCount,
        ulong FsQuotaBlockCount,
        ulong FsAllocCount,
        string MetaCryptoHex,
        uint RootTreeType,
        uint ExtentrefTreeType,
        uint SnapMetaTreeType,
        ulong OmapOid,
        ulong RootTreeOid,
        ulong ExtentrefTreeOid,
        ulong SnapMetaTreeOid,
        ulong RevertToXid,
        ulong RevertToSblockOid,
        ulong NextObjId,
        ulong NumFiles,
        ulong NumDirectories,
        ulong NumSymlinks,
        ulong NumOtherFsObjects,
        ulong NumSnapshots,
        ulong TotalBlocksAlloced,
        ulong TotalBlocksFreed,
        string VolumeUuid,
        ulong LastModTime,
        ulong FsFlags,
        string RawPrefixHex);

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
        ulong Flags,
        VolumeSnapshot Volume);

    internal sealed record Comparison(Snapshot Source, Snapshot Rebuilt);

    internal static Snapshot Read(string path)
    {
        using var stream = File.OpenRead(path);
        var offset = FindSuperblock(stream, "NXSB"u8);
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
            U64(0x4D8),
            ReadVolume(stream));
    }

    internal static void Write(string path, Snapshot source, Snapshot rebuilt)
    {
        Directory.CreateDirectory(Path.GetDirectoryName(path)!);
        var options = new JsonSerializerOptions { WriteIndented = true };
        File.WriteAllText(path, JsonSerializer.Serialize(new Comparison(source, rebuilt), options));
    }

    private static VolumeSnapshot ReadVolume(FileStream stream)
    {
        var offset = FindSuperblock(stream, "APSB"u8);
        stream.Position = offset;
        var buffer = new byte[0x400];
        stream.ReadExactly(buffer);

        ulong U64(int at) => BinaryPrimitives.ReadUInt64LittleEndian(buffer.AsSpan(at, 8));
        uint U32(int at) => BinaryPrimitives.ReadUInt32LittleEndian(buffer.AsSpan(at, 4));

        return new VolumeSnapshot(
            offset,
            U64(8),
            U64(16),
            U32(36),
            U64(40),
            U64(48),
            U64(56),
            U64(72),
            U64(80),
            U64(88),
            Convert.ToHexString(buffer.AsSpan(96, 20)),
            U32(116),
            U32(120),
            U32(124),
            U64(128),
            U64(136),
            U64(144),
            U64(152),
            U64(160),
            U64(168),
            U64(176),
            U64(184),
            U64(192),
            U64(200),
            U64(208),
            U64(216),
            U64(224),
            U64(232),
            new Guid(buffer.AsSpan(240, 16)).ToString("D"),
            U64(256),
            U64(264),
            Convert.ToHexString(buffer.AsSpan(0, 0x400)));
    }

    private static long FindSuperblock(FileStream stream, ReadOnlySpan<byte> magic)
    {
        const int windowSize = 1024 * 1024;
        var buffer = new byte[windowSize + 3];
        stream.Position = 0;
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
            for (var i = 32; i + 4 <= total; i++)
            {
                if (buffer.AsSpan(i, 4).SequenceEqual(magic))
                {
                    return absolute - carry + i - 32;
                }
            }

            carry = Math.Min(3, total);
            Buffer.BlockCopy(buffer, total - carry, buffer, 0, carry);
            absolute += read;
        }

        throw new InvalidDataException($"No {System.Text.Encoding.ASCII.GetString(magic)} superblock found in {stream.Name}.");
    }
}

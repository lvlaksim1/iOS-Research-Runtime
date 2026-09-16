using System.Buffers.Binary;
using IOSResearchRuntime.Services;

namespace IOSResearchRuntime.Tests;

public sealed class TrustCacheBuilderTests
{
    [Fact]
    public void Build_MatchesDarwinVmTrustCacheLayout()
    {
        var builder = new TrustCacheBuilder();
        var result = builder.Build(
        [
            "ffeeddccbbaa99887766554433221100ffeeddcc",
            "00112233445566778899aabbccddeeff00112233"
        ]);

        Assert.Equal(24 + (22 * 2), result.Length);
        Assert.Equal(1u, BinaryPrimitives.ReadUInt32LittleEndian(result.AsSpan(0, 4)));
        Assert.Equal(new string('A', 16), System.Text.Encoding.ASCII.GetString(result, 4, 16));
        Assert.Equal(2u, BinaryPrimitives.ReadUInt32LittleEndian(result.AsSpan(20, 4)));

        var firstEntry = result.AsSpan(24, 22);
        Assert.Equal(
            Convert.FromHexString("00112233445566778899aabbccddeeff00112233"),
            firstEntry[..20].ToArray());
        Assert.Equal(2, firstEntry[20]);
        Assert.Equal(0, firstEntry[21]);
    }

    [Theory]
    [InlineData(0u, 20)]
    [InlineData(1u, 22)]
    [InlineData(2u, 24)]
    public void Merge_PreservesAppleEntriesAndAddsCustomHash(
        uint version,
        int entrySize)
    {
        var appleLow = "00112233445566778899aabbccddeeff00112233";
        var appleHigh = "ffeeddccbbaa99887766554433221100ffeeddcc";
        var custom = "445566778899aabbccddeeff0011223344556677";

        var uuid = Enumerable.Range(0, 16).Select(i => (byte)(0x80 + i)).ToArray();
        var baseModule = BuildFixture(
            version,
            uuid,
            [
                MakeEntry(version, appleLow, 1, 3, 4),
                MakeEntry(version, appleHigh, 5, 6, 7)
            ]);

        var builder = new TrustCacheBuilder();
        var result = builder.Merge(baseModule, [custom, appleLow]);

        Assert.Equal(version, result.Version);
        Assert.Equal(2, result.BaseEntries);
        Assert.Equal(1, result.AddedEntries);
        Assert.Equal(3, result.TotalEntries);
        Assert.Equal(24 + (entrySize * 3), result.Data.Length);
        Assert.Equal(uuid, result.Data.AsSpan(4, 16).ToArray());

        var entries = Enumerable.Range(0, 3)
            .Select(index => result.Data
                .AsSpan(24 + (index * entrySize), entrySize)
                .ToArray())
            .ToArray();

        Assert.Equal(
            new[] { appleLow, custom, appleHigh },
            entries.Select(entry => Convert.ToHexString(entry.AsSpan(0, 20)).ToLowerInvariant()));

        // Apple metadata survives byte-for-byte for existing entries.
        Assert.Equal(
            MakeEntry(version, appleLow, 1, 3, 4),
            entries[0]);
        Assert.Equal(
            MakeEntry(version, appleHigh, 5, 6, 7),
            entries[2]);

        // New entries use SHA-256-truncated hash type and unrestricted flags/category.
        if (version >= 1)
        {
            Assert.Equal(2, entries[1][20]);
            Assert.Equal(0, entries[1][21]);
        }
        if (version >= 2)
        {
            Assert.Equal(0, entries[1][22]);
            Assert.Equal(0, entries[1][23]);
        }
    }

    [Fact]
    public void Merge_RejectsUnknownTrustCacheVersion()
    {
        var invalid = new byte[24];
        BinaryPrimitives.WriteUInt32LittleEndian(invalid.AsSpan(0, 4), 99);

        var builder = new TrustCacheBuilder();

        Assert.Throws<InvalidDataException>(
            () => builder.Merge(
                invalid,
                ["00112233445566778899aabbccddeeff00112233"]));
    }

    [Theory]
    [InlineData("")]
    [InlineData("abcd")]
    [InlineData("zz112233445566778899aabbccddeeff00112233")]
    public void Build_RejectsInvalidCdHash(string hash)
    {
        var builder = new TrustCacheBuilder();

        Assert.Throws<InvalidDataException>(() => builder.Build([hash]));
    }

    private static byte[] BuildFixture(
        uint version,
        byte[] uuid,
        IReadOnlyCollection<byte[]> entries)
    {
        using var stream = new MemoryStream();
        using var writer = new BinaryWriter(stream);
        writer.Write(version);
        writer.Write(uuid);
        writer.Write((uint)entries.Count);
        foreach (var entry in entries)
        {
            writer.Write(entry);
        }
        writer.Flush();
        return stream.ToArray();
    }

    private static byte[] MakeEntry(
        uint version,
        string hash,
        byte hashType,
        byte flags,
        byte category)
    {
        var cdHash = Convert.FromHexString(hash);
        return version switch
        {
            0 => cdHash,
            1 => [.. cdHash, hashType, flags],
            2 => [.. cdHash, hashType, flags, category, 0],
            _ => throw new ArgumentOutOfRangeException(nameof(version))
        };
    }
}

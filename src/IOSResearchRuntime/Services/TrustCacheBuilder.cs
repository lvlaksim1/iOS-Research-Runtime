using System.Buffers.Binary;

namespace IOSResearchRuntime.Services;

public sealed record TrustCacheMergeResult(
    byte[] Data,
    uint Version,
    int BaseEntries,
    int AddedEntries,
    int TotalEntries);

public sealed class TrustCacheBuilder
{
    private const uint Version1 = 1;
    private const byte HashTypeSha256Truncated = 2;
    private const int HeaderSize = 24;
    private const int CdHashHexLength = 40;
    private const int CdHashByteLength = 20;

    public byte[] Build(IEnumerable<string> cdHashes)
    {
        var entries = cdHashes
            .Select(NormalizeHash)
            .Distinct(StringComparer.Ordinal)
            .OrderBy(hash => hash, StringComparer.Ordinal)
            .Select(hash => BuildNewEntry(Version1, hash))
            .ToArray();

        return WriteModule(
            Version1,
            Enumerable.Repeat((byte)'A', 16).ToArray(),
            entries);
    }

    public TrustCacheMergeResult Merge(
        byte[] baseTrustCache,
        IEnumerable<string> cdHashes)
    {
        ArgumentNullException.ThrowIfNull(baseTrustCache);

        if (baseTrustCache.Length < HeaderSize)
        {
            throw new InvalidDataException(
                $"Base trust cache is too short: {baseTrustCache.Length} bytes.");
        }

        var version = BinaryPrimitives.ReadUInt32LittleEndian(
            baseTrustCache.AsSpan(0, 4));
        var entrySize = EntrySize(version);
        var uuid = baseTrustCache.AsSpan(4, 16).ToArray();
        var baseEntryCount = BinaryPrimitives.ReadUInt32LittleEndian(
            baseTrustCache.AsSpan(20, 4));

        var expectedLength = checked(
            HeaderSize + checked((long)baseEntryCount * entrySize));
        if (expectedLength > baseTrustCache.Length)
        {
            throw new InvalidDataException(
                $"Base trust cache is truncated: expected at least {expectedLength} bytes, got {baseTrustCache.Length}.");
        }

        if (expectedLength < baseTrustCache.Length &&
            baseTrustCache.AsSpan(checked((int)expectedLength)).IndexOfAnyExcept((byte)0) >= 0)
        {
            throw new InvalidDataException(
                "Base trust cache contains unexpected non-zero trailing data.");
        }

        var entries = new Dictionary<string, byte[]>(StringComparer.Ordinal);
        var offset = HeaderSize;

        for (var index = 0; index < baseEntryCount; index++)
        {
            var entry = baseTrustCache.AsSpan(offset, entrySize).ToArray();
            var key = Convert.ToHexString(entry.AsSpan(0, CdHashByteLength))
                .ToLowerInvariant();

            if (!entries.TryAdd(key, entry))
            {
                throw new InvalidDataException(
                    $"Base trust cache contains duplicate CDHash: {key}");
            }

            offset += entrySize;
        }

        var added = 0;
        foreach (var rawHash in cdHashes)
        {
            var hash = NormalizeHash(rawHash);
            if (entries.ContainsKey(hash))
            {
                continue;
            }

            entries.Add(hash, BuildNewEntry(version, hash));
            added++;
        }

        var orderedEntries = entries
            .OrderBy(pair => pair.Key, StringComparer.Ordinal)
            .Select(pair => pair.Value)
            .ToArray();

        var data = WriteModule(version, uuid, orderedEntries);
        return new TrustCacheMergeResult(
            data,
            version,
            checked((int)baseEntryCount),
            added,
            orderedEntries.Length);
    }

    public TrustCacheMergeResult MergeFile(
        string baseTrustCachePath,
        string hashListPath,
        string outputPath)
    {
        var hashes = File.ReadLines(hashListPath)
            .Where(line => !string.IsNullOrWhiteSpace(line));

        var result = Merge(File.ReadAllBytes(baseTrustCachePath), hashes);
        File.WriteAllBytes(outputPath, result.Data);
        return result;
    }

    public void BuildFile(string hashListPath, string outputPath)
    {
        var hashes = File.ReadLines(hashListPath)
            .Where(line => !string.IsNullOrWhiteSpace(line));

        File.WriteAllBytes(outputPath, Build(hashes));
    }

    private static byte[] WriteModule(
        uint version,
        byte[] uuid,
        IReadOnlyCollection<byte[]> entries)
    {
        if (uuid.Length != 16)
        {
            throw new InvalidDataException(
                $"Trust cache UUID must be 16 bytes, got {uuid.Length}.");
        }

        using var stream = new MemoryStream();
        using var writer = new BinaryWriter(stream);

        writer.Write(version);
        writer.Write(uuid);
        writer.Write(checked((uint)entries.Count));

        foreach (var entry in entries)
        {
            writer.Write(entry);
        }

        writer.Flush();
        return stream.ToArray();
    }

    private static byte[] BuildNewEntry(uint version, string normalizedHash)
    {
        var cdHash = Convert.FromHexString(normalizedHash);
        if (cdHash.Length != CdHashByteLength)
        {
            throw new InvalidDataException(
                $"CDHash has unexpected byte length: {normalizedHash}");
        }

        return version switch
        {
            0 => cdHash,
            1 => [.. cdHash, HashTypeSha256Truncated, 0],
            2 => [.. cdHash, HashTypeSha256Truncated, 0, 0, 0],
            _ => throw new InvalidDataException(
                $"Unsupported Apple trust cache version: {version}.")
        };
    }

    private static int EntrySize(uint version) => version switch
    {
        0 => 20,
        1 => 22,
        2 => 24,
        _ => throw new InvalidDataException(
            $"Unsupported Apple trust cache version: {version}.")
    };

    private static string NormalizeHash(string hash)
    {
        var normalized = hash.Trim().ToLowerInvariant();

        if (normalized.Length != CdHashHexLength)
        {
            throw new InvalidDataException(
                $"CDHash must contain exactly {CdHashHexLength} hexadecimal characters: {hash}");
        }

        try
        {
            _ = Convert.FromHexString(normalized);
        }
        catch (FormatException exception)
        {
            throw new InvalidDataException(
                $"CDHash is not valid hexadecimal: {hash}",
                exception);
        }

        return normalized;
    }
}

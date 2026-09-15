using System.Buffers.Binary;

namespace IOSResearchRuntime.Services;

public sealed class TrustCacheBuilder
{
    private const uint Version = 1;
    private const byte HashTypeSha256Truncated = 2;
    private const int CdHashHexLength = 40;
    private const int CdHashByteLength = 20;

    public byte[] Build(IEnumerable<string> cdHashes)
    {
        var hashes = cdHashes
            .Select(NormalizeHash)
            .OrderBy(hash => hash, StringComparer.Ordinal)
            .ToArray();

        using var stream = new MemoryStream();
        using var writer = new BinaryWriter(stream);

        writer.Write(Version);
        writer.Write(Enumerable.Repeat((byte)'A', 16).ToArray());
        writer.Write(checked((uint)hashes.Length));

        foreach (var hash in hashes)
        {
            var bytes = Convert.FromHexString(hash);
            if (bytes.Length != CdHashByteLength)
            {
                throw new InvalidDataException($"CDHash has unexpected byte length: {hash}");
            }

            writer.Write(bytes);
            writer.Write(HashTypeSha256Truncated);
            writer.Write((byte)0);
        }

        writer.Flush();
        return stream.ToArray();
    }

    public void BuildFile(string hashListPath, string outputPath)
    {
        var hashes = File.ReadLines(hashListPath)
            .Where(line => !string.IsNullOrWhiteSpace(line));

        File.WriteAllBytes(outputPath, Build(hashes));
    }

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
            throw new InvalidDataException($"CDHash is not valid hexadecimal: {hash}", exception);
        }

        return normalized;
    }
}

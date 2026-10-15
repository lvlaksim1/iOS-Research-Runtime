using System.Security.Cryptography;
using System.Text;
using System.Text.Json;

namespace IOSResearchRuntime.Services;

/// <summary>
/// Records one boot's QEMU serial and diagnostic streams without merging them.
/// A completed manifest is a capture receipt, not evidence of full-system boot.
/// </summary>
public sealed class BootEvidenceCapture : IDisposable
{
    private readonly object _sync = new();
    private readonly FileStream _serial;
    private readonly FileStream _stderr;
    private readonly IncrementalHash _serialHash = IncrementalHash.CreateHash(HashAlgorithmName.SHA256);
    private bool _completed;

    public string BootNonce { get; }
    public string SerialPath { get; }
    public string StderrPath { get; }
    public string ManifestPath { get; }
    public string? RunId { get; }
    public string? HeadSha { get; }

    public BootEvidenceCapture(string directory, string? runId, string? headSha)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(directory);
        Directory.CreateDirectory(directory);

        BootNonce = Convert.ToHexString(RandomNumberGenerator.GetBytes(16)).ToLowerInvariant();
        var prefix = $"boot-{DateTime.UtcNow:yyyyMMddTHHmmssfffZ}-{BootNonce}";
        SerialPath = Path.Combine(directory, $"{prefix}.serial.log");
        StderrPath = Path.Combine(directory, $"{prefix}.stderr.log");
        ManifestPath = Path.Combine(directory, $"{prefix}.capture.json");
        RunId = runId;
        HeadSha = headSha;

        _serial = new FileStream(SerialPath, FileMode.CreateNew, FileAccess.Write, FileShare.Read);
        try
        {
            _stderr = new FileStream(StderrPath, FileMode.CreateNew, FileAccess.Write, FileShare.Read);
        }
        catch
        {
            _serial.Dispose();
            throw;
        }
    }

    public void AppendSerial(string chunk) => Append(chunk, serial: true);
    public void AppendStderr(string chunk) => Append(chunk, serial: false);

    private void Append(string chunk, bool serial)
    {
        ArgumentNullException.ThrowIfNull(chunk);
        var bytes = Encoding.UTF8.GetBytes(chunk);
        lock (_sync)
        {
            if (_completed)
            {
                throw new InvalidOperationException("Boot capture is already complete.");
            }

            if (serial)
            {
                _serial.Write(bytes);
                _serialHash.AppendData(bytes);
            }
            else
            {
                _stderr.Write(bytes);
            }
        }
    }

    public string Complete()
    {
        lock (_sync)
        {
            if (_completed)
            {
                return ManifestPath;
            }

            _serial.Flush(flushToDisk: true);
            _stderr.Flush(flushToDisk: true);
            _serial.Dispose();
            _stderr.Dispose();
            var serialSha256 = Convert.ToHexString(_serialHash.GetHashAndReset()).ToLowerInvariant();
            _serialHash.Dispose();

            var receipt = new
            {
                schema = 1,
                boot_nonce = BootNonce,
                run_id = RunId,
                head_sha = HeadSha,
                serial_file = Path.GetFileName(SerialPath),
                stderr_file = Path.GetFileName(StderrPath),
                serial_sha256 = serialSha256,
                stage1_accepted = false
            };
            using var output = new FileStream(ManifestPath, FileMode.CreateNew, FileAccess.Write, FileShare.Read);
            JsonSerializer.Serialize(output, receipt, new JsonSerializerOptions { WriteIndented = true });
            output.Flush(flushToDisk: true);
            _completed = true;
            return ManifestPath;
        }
    }

    public void Dispose() => Complete();
}

using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using IOSResearchRuntime.Services;

namespace IOSResearchRuntime.Tests;

public sealed class BootEvidenceCaptureTests
{
    [Fact]
    public void Capture_SeparatesSerialAndStderr_AndNeverClaimsStage1()
    {
        var directory = NewDirectory();
        try
        {
            using var capture = new BootEvidenceCapture(directory, "38670488756", new string('a', 40));
            const string serial = "BSD root: md0\nDarwin Kernel Version\n";
            const string stderr = "qemu host diagnostic\n";
            capture.AppendSerial(serial);
            capture.AppendStderr(stderr);
            capture.Complete();
            Assert.Equal(serial, File.ReadAllText(capture.SerialPath));
            Assert.Equal(stderr, File.ReadAllText(capture.StderrPath));
            Assert.DoesNotContain("qemu host diagnostic", File.ReadAllText(capture.SerialPath));
            using var receipt = JsonDocument.Parse(File.ReadAllText(capture.ManifestPath));
            var root = receipt.RootElement;
            Assert.False(root.GetProperty("stage1_accepted").GetBoolean());
            Assert.Equal("38670488756", root.GetProperty("run_id").GetString());
            Assert.Equal(new string('a', 40), root.GetProperty("head_sha").GetString());
            Assert.Equal(capture.BootNonce, root.GetProperty("boot_nonce").GetString());
            var expected = Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(serial))).ToLowerInvariant();
            Assert.Equal(expected, root.GetProperty("serial_sha256").GetString());
        }
        finally { Directory.Delete(directory, recursive: true); }
    }

    [Fact]
    public void Capture_UsesDistinctCreateNewFilesForConsecutiveBoots()
    {
        var directory = NewDirectory();
        try
        {
            using var first = new BootEvidenceCapture(directory, "run", "head");
            using var second = new BootEvidenceCapture(directory, "run", "head");
            Assert.NotEqual(first.BootNonce, second.BootNonce);
            Assert.NotEqual(first.SerialPath, second.SerialPath);
            Assert.NotEqual(first.StderrPath, second.StderrPath);
            first.Complete();
            second.Complete();
            Assert.True(File.Exists(first.ManifestPath));
            Assert.True(File.Exists(second.ManifestPath));
        }
        finally { Directory.Delete(directory, recursive: true); }
    }

    [Fact]
    public void Capture_RejectsWritesAfterReceiptIsFinalized()
    {
        var directory = NewDirectory();
        try
        {
            using var capture = new BootEvidenceCapture(directory, null, null);
            capture.Complete();
            Assert.Throws<InvalidOperationException>(() => capture.AppendSerial("late"));
            Assert.Throws<InvalidOperationException>(() => capture.AppendStderr("late"));
        }
        finally { Directory.Delete(directory, recursive: true); }
    }

    [Fact]
    public void Capture_MissingRunAndHeadCannotImplyFullSystemProof()
    {
        var directory = NewDirectory();
        try
        {
            using var capture = new BootEvidenceCapture(directory, null, null);
            capture.AppendSerial("root\n");
            capture.Complete();
            using var receipt = JsonDocument.Parse(File.ReadAllText(capture.ManifestPath));
            var root = receipt.RootElement;
            Assert.Equal(JsonValueKind.Null, root.GetProperty("run_id").ValueKind);
            Assert.Equal(JsonValueKind.Null, root.GetProperty("head_sha").ValueKind);
            Assert.False(root.GetProperty("stage1_accepted").GetBoolean());
        }
        finally { Directory.Delete(directory, recursive: true); }
    }

    private static string NewDirectory()
    {
        var directory = Path.Combine(Path.GetTempPath(), "ios-boot-capture-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(directory);
        return directory;
    }
}

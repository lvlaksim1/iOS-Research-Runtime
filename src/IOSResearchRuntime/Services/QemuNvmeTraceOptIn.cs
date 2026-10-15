using System;
using System.IO;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;

namespace IOSResearchRuntime.Services;

/// <summary>
/// Optional, host-only QEMU NVMe IRQ trace wiring. A prepared plan is not
/// evidence of a real trace, interrupt delivery, or full-system iOS boot.
/// </summary>
internal static class QemuNvmeTraceOptIn
{
    internal const string EnvironmentVariable = "IOS_M3_NVME_IRQ_TRACE_PLAN";
    private const string PlanSchema = "ios-m3-nvme-irq-trace-launch-plan-v1";
    private const string QemuCommit = "2867d847d3471560e773120ee50c42dbcbb6d60b";
    private const string ProductCommit = "50fff7ab8fc33fa1324ea204416f7a773a191033";
    private const long MaxQemuBytes = 1024L * 1024 * 1024;
    private const long MaxPlanBytes = 64 * 1024;
    private static readonly byte[] EventBytes = Encoding.ASCII.GetBytes(
        "pci_nvme_irq_msix\npci_nvme_irq_pin\npci_nvme_irq_masked\n");

    internal static IReadOnlyList<string> GetArguments(RuntimeLayout layout)
    {
        var requestedPlan = Environment.GetEnvironmentVariable(EnvironmentVariable);
        if (requestedPlan is null)
        {
            return Array.Empty<string>();
        }

        var planPath = CheckedAbsolutePath(requestedPlan, "plan");
        var logDirectory = Path.GetFullPath(layout.LogDirectory);
        RequireInsideDirectory(planPath, logDirectory, "plan");
        var planInfo = RequireRegularFile(planPath, "plan", MaxPlanBytes);
        if (planInfo.Length == 0)
        {
            throw Invalid("empty_plan");
        }

        using var plan = JsonDocument.Parse(File.ReadAllText(planPath, Encoding.UTF8));
        var root = plan.RootElement;
        if (root.ValueKind != JsonValueKind.Object ||
            RequiredString(root, "schema") != PlanSchema ||
            RequiredString(root, "source_commit") != QemuCommit ||
            RequiredString(root, "product_main_commit") != ProductCommit ||
            RequiredString(root, "expected_trace_backend") != "log" ||
            !RequiredBoolean(root, "plan_only_no_qemu_execution"))
        {
            throw Invalid("plan_identity_or_backend_mismatch");
        }

        var binary = CheckedAbsolutePath(RequiredString(root, "qemu_binary"), "qemu_binary");
        var configuredBinary = Path.GetFullPath(layout.QemuExecutable);
        if (!string.Equals(binary, configuredBinary, StringComparison.OrdinalIgnoreCase))
        {
            throw Invalid("qemu_binary_path_mismatch");
        }
        var binaryInfo = RequireRegularFile(binary, "qemu_binary", MaxQemuBytes);
        if (binaryInfo.Length == 0 ||
            RequiredLong(root, "qemu_binary_size") != binaryInfo.Length)
        {
            throw Invalid("qemu_binary_size_mismatch");
        }
        using (var stream = File.OpenRead(binary))
        {
            var actualHash = Convert.ToHexString(SHA256.HashData(stream)).ToLowerInvariant();
            if (RequiredString(root, "qemu_binary_sha256_verified") != actualHash)
            {
                throw Invalid("qemu_binary_sha256_mismatch");
            }
        }

        var eventPath = CheckedAbsolutePath(RequiredString(root, "trace_event_file"), "trace_event_file");
        RequireInsideDirectory(eventPath, logDirectory, "trace_event_file");
        var eventInfo = RequireRegularFile(eventPath, "trace_event_file", EventBytes.Length);
        if (eventInfo.Length != EventBytes.Length ||
            !File.ReadAllBytes(eventPath).AsSpan().SequenceEqual(EventBytes))
        {
            throw Invalid("trace_event_file_content_mismatch");
        }
        var actualEventHash = Convert.ToHexString(SHA256.HashData(EventBytes)).ToLowerInvariant();
        if (RequiredString(root, "trace_event_file_sha256") != actualEventHash)
        {
            throw Invalid("trace_event_file_sha256_mismatch");
        }

        if (!root.TryGetProperty("qemu_trace_arguments", out var arguments) ||
            arguments.ValueKind != JsonValueKind.Array || arguments.GetArrayLength() != 2 ||
            arguments[0].ValueKind != JsonValueKind.String ||
            arguments[1].ValueKind != JsonValueKind.String ||
            arguments[0].GetString() != "-trace" ||
            arguments[1].GetString() != $"events={eventPath}")
        {
            throw Invalid("qemu_trace_arguments_mismatch");
        }
        return new[] { "-trace", $"events={eventPath}" };
    }

    private static string CheckedAbsolutePath(string value, string label)
    {
        if (string.IsNullOrWhiteSpace(value) || !Path.IsPathFullyQualified(value) ||
            value.IndexOfAny(new[] { ',', '=', '\r', '\n', '\0' }) >= 0)
        {
            throw Invalid($"unsafe_{label}_path");
        }
        return Path.GetFullPath(value);
    }

    private static void RequireInsideDirectory(string file, string directory, string label)
    {
        var relative = Path.GetRelativePath(directory, file);
        if (relative == "." || relative == ".." ||
            relative.StartsWith(".." + Path.DirectorySeparatorChar, StringComparison.Ordinal) ||
            Path.IsPathRooted(relative))
        {
            throw Invalid($"{label}_outside_log_directory");
        }
    }

    private static FileInfo RequireRegularFile(string path, string label, long maxSize)
    {
        var info = new FileInfo(path);
        if (!info.Exists || (info.Attributes & FileAttributes.ReparsePoint) != 0 ||
            info.Length > maxSize)
        {
            throw Invalid($"{label}_missing_symlink_or_too_large");
        }
        return info;
    }

    private static string RequiredString(JsonElement root, string name)
    {
        if (!root.TryGetProperty(name, out var value) ||
            value.ValueKind != JsonValueKind.String || string.IsNullOrEmpty(value.GetString()))
        {
            throw Invalid($"missing_or_invalid_{name}");
        }
        return value.GetString()!;
    }

    private static bool RequiredBoolean(JsonElement root, string name)
    {
        if (!root.TryGetProperty(name, out var value) ||
            (value.ValueKind != JsonValueKind.True && value.ValueKind != JsonValueKind.False))
        {
            throw Invalid($"missing_or_invalid_{name}");
        }
        return value.GetBoolean();
    }

    private static long RequiredLong(JsonElement root, string name)
    {
        if (!root.TryGetProperty(name, out var value) ||
            value.ValueKind != JsonValueKind.Number || !value.TryGetInt64(out var result))
        {
            throw Invalid($"missing_or_invalid_{name}");
        }
        return result;
    }

    private static InvalidOperationException Invalid(string reason) =>
        new($"iOS M3 QEMU NVMe IRQ trace opt-in rejected: {reason}");
}

namespace IOSResearchRuntime.Services;

public sealed record BootProofResult(bool IsValid, string Message);

public sealed class BootProofValidator
{
    public BootProofResult Validate(IEnumerable<string> lines)
    {
        var normalized = lines
            .Select(line => line.Trim())
            .Where(line => line.Length > 0)
            .ToArray();

        var hasDarwinKernel = normalized.Any(
            line => line.Contains("Darwin Kernel Version", StringComparison.Ordinal));
        if (!hasDarwinKernel)
        {
            return new BootProofResult(
                false,
                "Диагностика root shell не вернула Darwin Kernel Version.");
        }

        var hasRootIdentity = normalized.Any(
            line => string.Equals(line, "root", StringComparison.Ordinal));
        if (!hasRootIdentity)
        {
            return new BootProofResult(
                false,
                "Диагностика root shell не подтвердила whoami=root.");
        }

        return new BootProofResult(
            true,
            "Root shell подтверждён командами uname и whoami.");
    }
}

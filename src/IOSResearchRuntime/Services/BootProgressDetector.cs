namespace IOSResearchRuntime.Services;

public enum BootStage
{
    None = 0,
    QemuStarted = 1,
    Kernel = 2,
    Launchd = 3,
    RootShell = 4
}

public sealed record BootProgress(BootStage Stage, string Message);

public sealed class BootProgressDetector
{
    private BootStage _stage;

    public BootStage Stage => _stage;

    public void Reset()
    {
        _stage = BootStage.None;
    }

    public BootProgress MarkQemuStarted()
    {
        _stage = BootStage.QemuStarted;
        return new BootProgress(
            BootStage.QemuStarted,
            "QEMU запущен. Ожидаем XNU.");
    }

    public BootProgress? Observe(string line)
    {
        if (string.IsNullOrWhiteSpace(line))
        {
            return null;
        }

        if (line.Contains("Darwin Kernel Version", StringComparison.Ordinal))
        {
            return Advance(
                BootStage.Kernel,
                "XNU запущен. Ожидаем launchd.");
        }

        if (line.Contains("com.apple.xpc.launchd|", StringComparison.Ordinal) ||
            line.Contains("Darwin Bootstrapper Version", StringComparison.Ordinal))
        {
            return Advance(
                BootStage.Launchd,
                "launchd запущен. Ожидаем root shell.");
        }

        var trimmed = line.TrimEnd();
        if (trimmed.EndsWith("#", StringComparison.Ordinal) &&
            (trimmed.StartsWith("bash-", StringComparison.Ordinal) ||
             trimmed.StartsWith("sh-", StringComparison.Ordinal) ||
             trimmed.Contains("bash-", StringComparison.Ordinal)))
        {
            return Advance(
                BootStage.RootShell,
                "iOS/Darwin runtime готов: получен root shell.");
        }

        return null;
    }

    private BootProgress? Advance(BootStage stage, string message)
    {
        if (stage <= _stage)
        {
            return null;
        }

        _stage = stage;
        return new BootProgress(stage, message);
    }
}

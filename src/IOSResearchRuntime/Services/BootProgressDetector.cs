using System.Text.RegularExpressions;

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
    private const int TailLimit = 8192;

    private static readonly Regex RootShellPrompt = new(
        @"(?:^|[\r\n])(?:bash|sh)-[^\r\n#]*#\s*$",
        RegexOptions.CultureInvariant | RegexOptions.Compiled);

    private BootStage _stage;
    private string _tail = string.Empty;

    public BootStage Stage => _stage;

    public void Reset()
    {
        _stage = BootStage.None;
        _tail = string.Empty;
    }

    public BootProgress MarkQemuStarted()
    {
        _stage = BootStage.QemuStarted;
        return new BootProgress(
            BootStage.QemuStarted,
            "QEMU запущен. Ожидаем XNU.");
    }

    public BootProgress? Observe(string text)
    {
        if (string.IsNullOrEmpty(text))
        {
            return null;
        }

        _tail += text;
        if (_tail.Length > TailLimit)
        {
            _tail = _tail[^TailLimit..];
        }

        if (RootShellPrompt.IsMatch(_tail))
        {
            return Advance(
                BootStage.RootShell,
                "iOS/Darwin runtime готов: получен root shell.");
        }

        if (_tail.Contains("com.apple.xpc.launchd|", StringComparison.Ordinal) ||
            _tail.Contains("Darwin Bootstrapper Version", StringComparison.Ordinal))
        {
            return Advance(
                BootStage.Launchd,
                "launchd запущен. Ожидаем root shell.");
        }

        if (_tail.Contains("Darwin Kernel Version", StringComparison.Ordinal))
        {
            return Advance(
                BootStage.Kernel,
                "XNU запущен. Ожидаем launchd.");
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

using IOSResearchRuntime.Core;
using IOSResearchRuntime.Models;

namespace IOSResearchRuntime.Services;

public sealed class RuntimeCoordinator : IDisposable
{
    private readonly FirmwareBundleValidator _validator;
    private readonly QemuRuntime _runtime;
    private readonly BootProgressDetector _bootProgress = new();
    private RuntimeSnapshot _snapshot = RuntimeSnapshot.NotReady(
        "Среда не проверена.",
        Array.Empty<string>());

    public RuntimeCoordinator(FirmwareBundleValidator validator, QemuRuntime runtime)
    {
        _validator = validator;
        _runtime = runtime;
        _runtime.OutputReceived += RuntimeOnOutputReceived;
        _runtime.Exited += RuntimeOnExited;
    }

    public event EventHandler<RuntimeSnapshot>? StatusChanged;
    public event EventHandler<string>? LogReceived;

    public RuntimeSnapshot Snapshot => _snapshot;

    public RuntimeSnapshot Refresh()
    {
        if (_runtime.IsRunning)
        {
            return _snapshot;
        }

        SetSnapshot(_validator.Validate());
        return _snapshot;
    }

    public async Task StartAsync(CancellationToken cancellationToken = default)
    {
        var validation = _validator.Validate();
        if (validation.State != RuntimeState.Ready)
        {
            SetSnapshot(validation);
            return;
        }

        _bootProgress.Reset();
        SetSnapshot(new RuntimeSnapshot(
            RuntimeState.Booting,
            "Запуск qemu-sptm и загрузка iOS…",
            Array.Empty<string>()));

        try
        {
            await _runtime.StartAsync(cancellationToken);
            var progress = _bootProgress.MarkQemuStarted();
            SetSnapshot(new RuntimeSnapshot(
                RuntimeState.Booting,
                progress.Message,
                Array.Empty<string>()));
        }
        catch (Exception exception)
        {
            LogReceived?.Invoke(this, exception.ToString());
            SetSnapshot(new RuntimeSnapshot(
                RuntimeState.Failed,
                $"Ошибка запуска: {exception.Message}",
                Array.Empty<string>()));
        }
    }

    public async Task StopAsync(CancellationToken cancellationToken = default)
    {
        if (!_runtime.IsRunning)
        {
            Refresh();
            return;
        }

        SetSnapshot(new RuntimeSnapshot(
            RuntimeState.Stopping,
            "Остановка runtime…",
            Array.Empty<string>()));

        try
        {
            await _runtime.StopAsync(cancellationToken);
            Refresh();
        }
        catch (Exception exception)
        {
            LogReceived?.Invoke(this, exception.ToString());
            SetSnapshot(new RuntimeSnapshot(
                RuntimeState.Failed,
                $"Ошибка остановки: {exception.Message}",
                Array.Empty<string>()));
        }
    }

    private void RuntimeOnOutputReceived(object? sender, string line)
    {
        LogReceived?.Invoke(this, line);

        var progress = _bootProgress.Observe(line);
        if (progress is null)
        {
            return;
        }

        var state = progress.Stage == BootStage.RootShell
            ? RuntimeState.Running
            : RuntimeState.Booting;

        SetSnapshot(new RuntimeSnapshot(
            state,
            progress.Message,
            Array.Empty<string>()));
    }

    private void RuntimeOnExited(object? sender, int exitCode)
    {
        LogReceived?.Invoke(this, $"[runtime] qemu-sptm завершён, код {exitCode}.");

        if (_snapshot.State != RuntimeState.Stopping)
        {
            SetSnapshot(new RuntimeSnapshot(
                exitCode == 0 ? RuntimeState.Ready : RuntimeState.Failed,
                exitCode == 0
                    ? "Runtime завершён."
                    : $"Runtime аварийно завершён с кодом {exitCode}.",
                Array.Empty<string>()));
        }
    }

    private void SetSnapshot(RuntimeSnapshot snapshot)
    {
        _snapshot = snapshot;
        StatusChanged?.Invoke(this, snapshot);
    }

    public void Dispose()
    {
        _runtime.OutputReceived -= RuntimeOnOutputReceived;
        _runtime.Exited -= RuntimeOnExited;
        _runtime.Dispose();
    }
}

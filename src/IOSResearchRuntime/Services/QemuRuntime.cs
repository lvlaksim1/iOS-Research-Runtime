using System.Diagnostics;

namespace IOSResearchRuntime.Services;

public sealed class QemuRuntime : IDisposable
{
    private readonly RuntimeLayout _layout;
    private readonly QemuCommandBuilder _commandBuilder;
    private readonly object _logSync = new();
    private Process? _process;
    private StreamWriter? _logWriter;

    public QemuRuntime(RuntimeLayout layout, QemuCommandBuilder commandBuilder)
    {
        _layout = layout;
        _commandBuilder = commandBuilder;
    }

    public event EventHandler<string>? OutputReceived;
    public event EventHandler<int>? Exited;

    public bool IsRunning => _process is { HasExited: false };
    public string? CurrentLogPath { get; private set; }

    public Task StartAsync(CancellationToken cancellationToken = default)
    {
        if (IsRunning)
        {
            throw new InvalidOperationException("QEMU runtime is already running.");
        }

        _layout.EnsureDirectories();
        lock (_logSync)
        {
            _logWriter?.Dispose();
            CurrentLogPath = Path.Combine(
                _layout.LogDirectory,
                $"boot-{DateTime.Now:yyyyMMdd-HHmmss}.log");
            _logWriter = new StreamWriter(
                new FileStream(
                    CurrentLogPath,
                    FileMode.Create,
                    FileAccess.Write,
                    FileShare.Read),
                new System.Text.UTF8Encoding(encoderShouldEmitUTF8Identifier: false))
            {
                AutoFlush = true
            };
        }

        var startInfo = new ProcessStartInfo
        {
            FileName = _layout.QemuExecutable,
            WorkingDirectory = _layout.ApplicationDirectory,
            UseShellExecute = false,
            CreateNoWindow = true,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            RedirectStandardInput = true
        };

        foreach (var argument in _commandBuilder.BuildArguments())
        {
            startInfo.ArgumentList.Add(argument);
        }

        var process = new Process
        {
            StartInfo = startInfo,
            EnableRaisingEvents = true
        };

        process.OutputDataReceived += (_, eventArgs) =>
        {
            if (!string.IsNullOrWhiteSpace(eventArgs.Data))
            {
                EmitOutput(eventArgs.Data);
            }
        };

        process.ErrorDataReceived += (_, eventArgs) =>
        {
            if (!string.IsNullOrWhiteSpace(eventArgs.Data))
            {
                EmitOutput(eventArgs.Data);
            }
        };

        process.Exited += (_, _) =>
        {
            Exited?.Invoke(this, process.ExitCode);
        };

        if (!process.Start())
        {
            process.Dispose();
            lock (_logSync)
            {
                _logWriter?.Dispose();
                _logWriter = null;
            }
            throw new InvalidOperationException("Failed to start qemu-sptm.");
        }

        _process = process;
        process.BeginOutputReadLine();
        process.BeginErrorReadLine();

        cancellationToken.ThrowIfCancellationRequested();
        return Task.CompletedTask;
    }

    public async Task SendLineAsync(
        string line,
        CancellationToken cancellationToken = default)
    {
        var process = _process;
        if (process is null || process.HasExited)
        {
            throw new InvalidOperationException("QEMU runtime is not running.");
        }

        cancellationToken.ThrowIfCancellationRequested();
        await process.StandardInput.WriteLineAsync(line);
        await process.StandardInput.FlushAsync(cancellationToken);
    }

    private void EmitOutput(string line)
    {
        lock (_logSync)
        {
            _logWriter?.WriteLine(line);
        }

        OutputReceived?.Invoke(this, line);
    }

    public async Task StopAsync(CancellationToken cancellationToken = default)
    {
        var process = _process;
        if (process is null || process.HasExited)
        {
            return;
        }

        try
        {
            await process.StandardInput.WriteLineAsync("quit");
            await process.StandardInput.FlushAsync();

            var gracefulExit = process.WaitForExitAsync(cancellationToken);
            var timeout = Task.Delay(TimeSpan.FromSeconds(3), cancellationToken);
            if (await Task.WhenAny(gracefulExit, timeout) == gracefulExit)
            {
                await gracefulExit;
                return;
            }
        }
        catch (InvalidOperationException)
        {
        }

        if (!process.HasExited)
        {
            process.Kill(entireProcessTree: true);
            await process.WaitForExitAsync(cancellationToken);
        }
    }

    public void Dispose()
    {
        if (_process is { HasExited: false })
        {
            _process.Kill(entireProcessTree: true);
        }

        _process?.Dispose();

        lock (_logSync)
        {
            _logWriter?.Dispose();
            _logWriter = null;
        }
    }
}

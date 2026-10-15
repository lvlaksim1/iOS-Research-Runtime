using System.Diagnostics;
using System.Text;

namespace IOSResearchRuntime.Services;

public sealed class QemuRuntime : IDisposable
{
    private readonly RuntimeLayout _layout;
    private readonly QemuCommandBuilder _commandBuilder;
    private Process? _process;
    private Task? _captureCompletion;

    public QemuRuntime(RuntimeLayout layout, QemuCommandBuilder commandBuilder)
    {
        _layout = layout;
        _commandBuilder = commandBuilder;
    }

    public event EventHandler<string>? OutputReceived;
    public event EventHandler<string>? OutputChunkReceived;
    public event EventHandler<int>? Exited;

    public bool IsRunning => _process is { HasExited: false };
    public string? CurrentLogPath { get; private set; }

    public Task StartAsync(CancellationToken cancellationToken = default)
    {
        cancellationToken.ThrowIfCancellationRequested();

        if (IsRunning)
        {
            throw new InvalidOperationException("QEMU runtime is already running.");
        }

        if (_captureCompletion is { IsCompleted: false })
        {
            throw new InvalidOperationException("Previous boot capture is still finalizing.");
        }

        _layout.EnsureDirectories();

        // IOS-M3 transport probe: QEMU opens the host-backed raw image at startup.
        // Materialize a small sparse image before constructing/launching the command;
        // otherwise Windows QEMU exits immediately because -drive file= must exist.
        var nvmeProbePath = Path.Combine(_layout.DataDirectory, "ios-m3-nvme-probe.img");
        if (!File.Exists(nvmeProbePath))
        {
            using var probe = new FileStream(
                nvmeProbePath,
                FileMode.CreateNew,
                FileAccess.Write,
                FileShare.Read);
            probe.SetLength(64L * 1024 * 1024);
        }

        // Serial evidence and host diagnostics are deliberately separate.
        var capture = new BootEvidenceCapture(
            _layout.LogDirectory,
            Environment.GetEnvironmentVariable("GITHUB_RUN_ID"),
            Environment.GetEnvironmentVariable("GITHUB_SHA"));
        CurrentLogPath = capture.SerialPath;

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

        process.Exited += (_, _) =>
        {
            Exited?.Invoke(this, process.ExitCode);
        };

        try
        {
            if (!process.Start())
            {
                throw new InvalidOperationException("Failed to start qemu-sptm.");
            }
        }
        catch
        {
            process.Dispose();
            capture.Complete();
            throw;
        }

        _process = process;
        var serialPump = PumpStreamAsync(
            process.StandardOutput, capture.AppendSerial, emitConsoleEvents: true);
        var diagnosticPump = PumpStreamAsync(
            process.StandardError, capture.AppendStderr, emitConsoleEvents: false);
        _captureCompletion = FinalizeCaptureAsync(process, capture, serialPump, diagnosticPump);

        // Diagnostics-only host PCI snapshot. QMP is already enabled on a private
        // Unix socket; query the realized topology without changing guest-visible
        // devices or DeviceTree state. This gives evidence for NVMe BDF/BAR mapping.
        _ = CapturePciTopologyAsync(cancellationToken);

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

        // Pace guest-console input. Writing a whole proof burst to redirected
        // stdio can overrun the recovery console/TTY input path even though QEMU
        // accepted the host-side write, leaving only a suffix visible to bash.
        foreach (var character in line)
        {
            await process.StandardInput.WriteAsync(character);
            await process.StandardInput.FlushAsync(cancellationToken);
            await Task.Delay(TimeSpan.FromMilliseconds(10), cancellationToken);
        }

        await process.StandardInput.WriteAsync('\n');
        await process.StandardInput.FlushAsync(cancellationToken);
    }

    private async Task CapturePciTopologyAsync(CancellationToken cancellationToken)
    {
        var socketPath = Path.Combine(_layout.DataDirectory, "ios-m3-qmp.sock");
        var outputPath = Path.Combine(_layout.LogDirectory, "qmp-pci.json");

        try
        {
            for (var attempt = 0; attempt < 50 && !File.Exists(socketPath); attempt++)
            {
                await Task.Delay(TimeSpan.FromMilliseconds(100), cancellationToken);
            }

            if (!File.Exists(socketPath))
            {
                return;
            }

            using var socket = new System.Net.Sockets.Socket(
                System.Net.Sockets.AddressFamily.Unix,
                System.Net.Sockets.SocketType.Stream,
                System.Net.Sockets.ProtocolType.Unspecified);
            await socket.ConnectAsync(
                new System.Net.Sockets.UnixDomainSocketEndPoint(socketPath),
                cancellationToken);

            using var stream = new System.Net.Sockets.NetworkStream(socket, ownsSocket: true);
            using var reader = new StreamReader(stream, Encoding.UTF8, false, 4096, leaveOpen: true);
            using var writer = new StreamWriter(stream, new UTF8Encoding(false), 4096, leaveOpen: true)
            {
                AutoFlush = true
            };

            _ = await reader.ReadLineAsync(cancellationToken);
            await writer.WriteLineAsync("{\"execute\":\"qmp_capabilities\"}");
            _ = await reader.ReadLineAsync(cancellationToken);
            await writer.WriteLineAsync("{\"execute\":\"query-pci\"}");
            var response = await reader.ReadLineAsync(cancellationToken);
            if (!string.IsNullOrWhiteSpace(response))
            {
                await File.WriteAllTextAsync(outputPath, response, cancellationToken);
            }
        }
        catch (Exception exception) when (
            exception is IOException or
            System.Net.Sockets.SocketException or
            OperationCanceledException)
        {
            // Evidence capture must never alter boot behavior.
        }
    }

    private async Task PumpStreamAsync(
        StreamReader reader, Action<string> record, bool emitConsoleEvents)
    {
        var buffer = new char[4096];
        var pendingLine = new StringBuilder();

        try
        {
            while (true)
            {
                var read = await reader.ReadAsync(buffer.AsMemory());
                if (read == 0)
                {
                    break;
                }

                var chunk = new string(buffer, 0, read);
                record(chunk);
                if (emitConsoleEvents)
                {
                    OutputChunkReceived?.Invoke(this, chunk);
                    EmitCompletedLines(chunk, pendingLine);
                }
            }

            if (emitConsoleEvents && pendingLine.Length > 0)
            {
                OutputReceived?.Invoke(this, pendingLine.ToString());
            }
        }
        catch (ObjectDisposedException)
        {
        }
        catch (IOException)
        {
        }
    }

    private static async Task FinalizeCaptureAsync(
        Process process, BootEvidenceCapture capture, Task serialPump, Task diagnosticPump)
    {
        try
        {
            await process.WaitForExitAsync().ConfigureAwait(false);
        }
        catch (ObjectDisposedException)
        {
            // Process disposal may race with redirected-pipe completion.
        }
        catch (InvalidOperationException)
        {
            // A process can exit while its asynchronous setup is finishing.
        }
        finally
        {
            try
            {
                await Task.WhenAll(serialPump, diagnosticPump).ConfigureAwait(false);
            }
            finally
            {
                // No receipt is finalized while either stream can still append.
                capture.Complete();
            }
        }
    }

    private void EmitCompletedLines(string chunk, StringBuilder pendingLine)
    {
        foreach (var character in chunk)
        {
            if (character is '\r' or '\n')
            {
                if (pendingLine.Length > 0)
                {
                    OutputReceived?.Invoke(this, pendingLine.ToString());
                    pendingLine.Clear();
                }

                continue;
            }

            pendingLine.Append(character);
        }
    }

    public async Task StopAsync(CancellationToken cancellationToken = default)
    {
        var process = _process;
        if (process is null)
        {
            return;
        }

        if (process.HasExited)
        {
            if (_captureCompletion is { } completed)
            {
                await completed.ConfigureAwait(false);
            }
            return;
        }

        try
        {
            // -serial mon:stdio uses QEMU's stdio multiplexer.
            // Ctrl-A X is the native mux command for terminating the emulator.
            await process.StandardInput.WriteAsync("\u0001x");
            await process.StandardInput.FlushAsync();

            var gracefulExit = process.WaitForExitAsync(cancellationToken);
            var timeout = Task.Delay(TimeSpan.FromSeconds(3), cancellationToken);
            if (await Task.WhenAny(gracefulExit, timeout) == gracefulExit)
            {
                await gracefulExit;
                if (_captureCompletion is { } completed)
                {
                    await completed.ConfigureAwait(false);
                }
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

        if (_captureCompletion is { } completion)
        {
            await completion.ConfigureAwait(false);
        }
    }

    public void Dispose()
    {
        if (_process is { HasExited: false })
        {
            _process.Kill(entireProcessTree: true);
        }

        // Preserve redirected pipes until both capture tasks finish.
        var process = _process;
        if (process is not null)
        {
            if (_captureCompletion is { } completion)
            {
                _ = completion.ContinueWith(
                    _ => process.Dispose(), TaskScheduler.Default);
            }
            else
            {
                process.Dispose();
            }
        }
    }
}

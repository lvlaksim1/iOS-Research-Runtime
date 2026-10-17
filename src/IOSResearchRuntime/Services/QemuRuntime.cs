using System.Diagnostics;
using System.Text;
using System.Text.Json;

namespace IOSResearchRuntime.Services;

public sealed class QemuRuntime : IDisposable
{
    private readonly RuntimeLayout _layout;
    private readonly QemuCommandBuilder _commandBuilder;
    private Process? _process;
    private Task? _captureCompletion;
    private Task? _exitNotificationCompletion;
    private Task? _qmpCompletion;
    private CancellationTokenSource? _qmpCancellation;
    private CancellationTokenSource? _consoleCancellation;
    private readonly SemaphoreSlim _consoleInputGate = new(1, 1);
    private readonly object _lifecycleSync = new();
    private bool _stopping;
    private bool _disposed;

    public QemuRuntime(RuntimeLayout layout, QemuCommandBuilder commandBuilder)
    {
        _layout = layout;
        _commandBuilder = commandBuilder;
    }

    public event EventHandler<string>? OutputReceived;
    public event EventHandler<string>? OutputChunkReceived;
    public event EventHandler<int>? Exited;

    public bool IsRunning
    {
        get
        {
            lock (_lifecycleSync)
            {
                if (_disposed || _process is null)
                {
                    return false;
                }

                try
                {
                    return !_process.HasExited;
                }
                catch (InvalidOperationException)
                {
                    return false;
                }
                catch (ObjectDisposedException)
                {
                    // The process handle may be released by concurrent disposal.
                    return false;
                }
            }
        }
    }
    public string? CurrentLogPath { get; private set; }

    public Task StartAsync(CancellationToken cancellationToken = default)
    {
        // A synchronous lock covers the entire launch and task installation.
        // StopAsync sets _stopping before its first await, so a concurrent
        // restart cannot replace the QMP task owned by the previous stop.
        lock (_lifecycleSync)
        {
            return StartCore(cancellationToken);
        }
    }

    private Task StartCore(CancellationToken cancellationToken)
    {
        ObjectDisposedException.ThrowIf(_disposed, this);
        if (_stopping)
        {
            throw new InvalidOperationException("Previous QEMU stop is still finalizing.");
        }
        cancellationToken.ThrowIfCancellationRequested();

        if (IsRunning)
        {
            throw new InvalidOperationException("QEMU runtime is already running.");
        }

        if (_captureCompletion is { IsCompleted: false })
        {
            throw new InvalidOperationException("Previous boot capture is still finalizing.");
        }

        if (_qmpCompletion is { IsCompleted: false })
        {
            throw new InvalidOperationException("Previous QMP host capture is still finalizing.");
        }

        // Wait for the previous Process.Exited callback to finish notifying
        // listeners. WaitForExitAsync/capture completion alone does not prove
        // that an asynchronously dispatched Exited handler has returned.
        if (_exitNotificationCompletion is { IsCompleted: false })
        {
            throw new InvalidOperationException(
                "Previous QEMU exit notification is still finalizing.");
        }

        // A spontaneous QEMU exit can leave an in-flight console writer.
        // Cancel the old run before admitting a new one; do not recycle the
        // console gate while the old writer still owns it.
        if (_consoleCancellation is not null)
        {
            CancelConsoleInput(_consoleCancellation);
        }
        // StopAsync may already have disposed and cleared the previous run's
        // CTS while a canceled console writer still owns the input gate.
        // The gate check must therefore be independent of CTS presence.
        if (_consoleInputGate.CurrentCount != 1)
        {
            throw new InvalidOperationException(
                "Previous QEMU console input is still finalizing.");
        }
        if (_consoleCancellation is not null)
        {
            _consoleCancellation.Dispose();
            _consoleCancellation = null;
        }

        // A completed prior QMP task no longer owns any live socket or writer.
        _qmpCancellation?.Dispose();
        _qmpCancellation = null;
        _qmpCompletion = null;

        // Prior stream pumps, QMP capture, console writer and exit callback
        // are all quiescent here. Dispose the old exited Process before the
        // next run replaces its handle; no callback may read its ExitCode now.
        if (_process is not null)
        {
            _process.Dispose();
            _process = null;
            _captureCompletion = null;
        }
        _exitNotificationCompletion = null;

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

        // The event owns the cancellation source of THIS process, not a
        // mutable field that a later run could replace. Create it before
        // Process.Start so an immediate exit is not missed.
        var consoleCancellation = new CancellationTokenSource();
        _consoleCancellation = consoleCancellation;
        var exitNotification = new TaskCompletionSource<bool>(
            TaskCreationOptions.RunContinuationsAsynchronously);
        _exitNotificationCompletion = exitNotification.Task;
        process.Exited += (_, _) =>
        {
            try
            {
                CancelConsoleInput(consoleCancellation);
                int exitCode;
                lock (_lifecycleSync)
                {
                    // The runtime can be disposed while the OS dispatches
                    // an already-queued Process.Exited callback.
                    if (_disposed || !ReferenceEquals(_process, process))
                    {
                        return;
                    }
                    try
                    {
                        exitCode = process.ExitCode;
                    }
                    catch (InvalidOperationException)
                    {
                        return;
                    }
                    catch (ObjectDisposedException)
                    {
                        return;
                    }
                }

                // Snapshot subscribers for this exit. A throwing listener must
                // neither crash the callback thread nor suppress notifications
                // to subsequent listeners registered for the same process.
                var exitListeners = Exited;
                if (exitListeners is not null)
                {
                    foreach (EventHandler<int> listener in exitListeners.GetInvocationList())
                    {
                        try
                        {
                            listener(this, exitCode);
                        }
                        catch (Exception exception)
                        {
                            Debug.WriteLine($"QEMU exit subscriber failed: {exception}");
                        }
                    }
                }
            }
            finally
            {
                // Restart cannot supersede this run before notification
                // delivery has finished (including an exceptional listener).
                exitNotification.TrySetResult(true);
            }
        };

        // Publish the process identity before Process.Start: a fast-exiting
        // QEMU can raise Exited before Start returns. The callback takes
        // _lifecycleSync, so it observes the registered process once launch
        // releases the lock, rather than silently dropping its notification.
        _process = process;
        try
        {
            if (!process.Start())
            {
                throw new InvalidOperationException("Failed to start qemu-sptm.");
            }
        }
        catch
        {
            // A failed launch must not leave an unstarted Process installed.
            _process = null;
            CancelConsoleInput(consoleCancellation);
            consoleCancellation.Dispose();
            _consoleCancellation = null;
            _exitNotificationCompletion = null;
            process.Dispose();
            capture.Complete();
            throw;
        }
        var serialPump = PumpStreamAsync(
            process.StandardOutput, capture.AppendSerial, emitConsoleEvents: true);
        var diagnosticPump = PumpStreamAsync(
            process.StandardError, capture.AppendStderr, emitConsoleEvents: false);
        _captureCompletion = FinalizeCaptureAsync(process, capture, serialPump, diagnosticPump);

        // Diagnostics-only host PCI snapshot. QMP is already enabled on a private
        // Unix socket; query the realized topology without changing guest-visible
        // devices or DeviceTree state. This gives evidence for NVMe BDF/BAR mapping.
        _qmpCancellation = CancellationTokenSource.CreateLinkedTokenSource(cancellationToken);
        var qmpToken = _qmpCancellation.Token;
        // Run off the UI synchronization context: Dispose synchronously drains
        // this task, and must never wait for a WPF-thread continuation.
        _qmpCompletion = Task.Run(() => CapturePciTopologyAsync(
            capture.BootNonce, capture.RunId, capture.HeadSha, qmpToken), qmpToken);

        return Task.CompletedTask;
    }

    public async Task SendLineAsync(
        string line,
        CancellationToken cancellationToken = default)
    {
        Process process;
        CancellationTokenSource linked;
        lock (_lifecycleSync)
        {
            ObjectDisposedException.ThrowIf(_disposed, this);
            var currentProcess = _process;
            if (_stopping || currentProcess is null || currentProcess.HasExited ||
                _consoleCancellation is null)
            {
                throw new InvalidOperationException("QEMU runtime is not accepting console input.");
            }
            process = currentProcess;
            // Register before releasing the lock. Restart and Dispose may
            // dispose the old run's CTS only after this registration exists.
            linked = CancellationTokenSource.CreateLinkedTokenSource(
                cancellationToken, _consoleCancellation.Token);
        }

        // Cancellation is per run: StopAsync and natural process exit cancel
        // a paced guest input burst before another run can reuse the gate.
        using var ownedLinked = linked;
        var token = ownedLinked.Token;
        await _consoleInputGate.WaitAsync(token).ConfigureAwait(false);
        try
        {
            lock (_lifecycleSync)
            {
                if (_stopping || _disposed || !ReferenceEquals(_process, process))
                {
                    throw new InvalidOperationException("QEMU console is stopping.");
                }
            }

            // Pace guest-console input. Cancellation interrupts each write,
            // flush and delay; no character can interleave with the stop mux.
            for (var index = 0; index < line.Length; index++)
            {
                token.ThrowIfCancellationRequested();
                await process.StandardInput.WriteAsync(line.AsMemory(index, 1), token)
                    .ConfigureAwait(false);
                await process.StandardInput.FlushAsync(token).ConfigureAwait(false);
                await Task.Delay(TimeSpan.FromMilliseconds(10), token).ConfigureAwait(false);
            }

            token.ThrowIfCancellationRequested();
            await process.StandardInput.WriteAsync("\n".AsMemory(), token)
                .ConfigureAwait(false);
            await process.StandardInput.FlushAsync(token).ConfigureAwait(false);
        }
        finally
        {
            _consoleInputGate.Release();
        }
    }

    private async Task CapturePciTopologyAsync(
        string bootNonce, string? runId, string? headSha,
        CancellationToken cancellationToken)
    {
        var socketPath = Path.Combine(_layout.DataDirectory, "ios-m3-qmp.sock");
        var rawPath = Path.Combine(_layout.LogDirectory, $"boot-{bootNonce}.qmp-pci.json");
        var evidencePath = Path.Combine(_layout.LogDirectory, $"boot-{bootNonce}.qmp-pci-evidence.json");

        try
        {
            for (var attempt = 0; attempt < 50 && !File.Exists(socketPath); attempt++)
            {
                await Task.Delay(TimeSpan.FromMilliseconds(100), cancellationToken).ConfigureAwait(false);
            }

            if (!File.Exists(socketPath))
            {
                return;
            }

            // A bounded query never delays or changes the guest boot path.
            using var timeout = CancellationTokenSource.CreateLinkedTokenSource(cancellationToken);
            timeout.CancelAfter(TimeSpan.FromSeconds(12));
            var token = timeout.Token;

            using var socket = new System.Net.Sockets.Socket(
                System.Net.Sockets.AddressFamily.Unix,
                System.Net.Sockets.SocketType.Stream,
                System.Net.Sockets.ProtocolType.Unspecified);
            await socket.ConnectAsync(
                new System.Net.Sockets.UnixDomainSocketEndPoint(socketPath), token).ConfigureAwait(false);

            using var stream = new System.Net.Sockets.NetworkStream(socket, ownsSocket: true);
            using var reader = new StreamReader(stream, Encoding.UTF8, false, 4096, leaveOpen: true);
            using var writer = new StreamWriter(stream, new UTF8Encoding(false), 4096, leaveOpen: true)
            {
                AutoFlush = true
            };

            _ = await reader.ReadLineAsync(token).ConfigureAwait(false); // QMP greeting.
            var capabilitiesId = $"iosm3-capabilities-{bootNonce}";
            await writer.WriteLineAsync(
                JsonSerializer.Serialize(new { execute = "qmp_capabilities", id = capabilitiesId }).AsMemory(),
                token).ConfigureAwait(false);
            var capabilitiesReply = await ReadQmpReplyAsync(reader, capabilitiesId, token).ConfigureAwait(false);
            if (capabilitiesReply is null)
            {
                return;
            }

            using (var capabilities = JsonDocument.Parse(capabilitiesReply))
            {
                if (!capabilities.RootElement.TryGetProperty("return", out _))
                {
                    return;
                }
            }

            var queryId = $"iosm3-query-pci-{bootNonce}";
            await writer.WriteLineAsync(
                JsonSerializer.Serialize(new { execute = "query-pci", id = queryId }).AsMemory(),
                token).ConfigureAwait(false);
            var response = await ReadQmpReplyAsync(reader, queryId, token).ConfigureAwait(false);
            if (response is null)
            {
                return;
            }

            var classification = QmpPciStorageEvidence.Evaluate(response);
            await using (var raw = new FileStream(
                rawPath, FileMode.CreateNew, FileAccess.Write, FileShare.Read))
            {
                await raw.WriteAsync(Encoding.UTF8.GetBytes(response), token).ConfigureAwait(false);
                await raw.FlushAsync(token).ConfigureAwait(false);
            }

            // This is an independent host-model observation. It is never
            // evidence of IOKit binding, a guest BSD disk, APFS, or Stage 1.
            var receipt = new
            {
                schema = 1,
                boot_nonce = bootNonce,
                run_id = runId,
                head_sha = headSha,
                source = "QMP_QUERY_PCI_HOST_ONLY",
                raw_reply_file = Path.GetFileName(rawPath),
                valid_query_pci_reply = classification.ValidQueryPciReply,
                host_nvme_candidates = classification.HostNvmeCandidates,
                classification = classification.Classification,
                guest_nvme_bound = false,
                stage1_accepted = false
            };
            await using var evidence = new FileStream(
                evidencePath, FileMode.CreateNew, FileAccess.Write, FileShare.Read);
            await JsonSerializer.SerializeAsync(evidence, receipt, cancellationToken: token).ConfigureAwait(false);
            await evidence.FlushAsync(token).ConfigureAwait(false);
        }
        catch (Exception exception) when (
            exception is IOException or
            System.Net.Sockets.SocketException or
            OperationCanceledException or
            UnauthorizedAccessException or
            JsonException or
            ObjectDisposedException)
        {
            // Optional host-side evidence must never alter guest boot behavior.
        }
    }

    private static async Task<string?> ReadQmpReplyAsync(
        StreamReader reader, string expectedId, CancellationToken cancellationToken)
    {
        // QMP events may arrive between command responses. Correlate by ID.
        for (var lineIndex = 0; lineIndex < 32; lineIndex++)
        {
            var line = await reader.ReadLineAsync(cancellationToken).ConfigureAwait(false);
            if (line is null)
            {
                return null;
            }

            try
            {
                using var document = JsonDocument.Parse(line);
                var root = document.RootElement;
                if (root.ValueKind == JsonValueKind.Object &&
                    root.TryGetProperty("id", out var id) &&
                    id.ValueKind == JsonValueKind.String &&
                    id.GetString() == expectedId &&
                    (root.TryGetProperty("return", out _) ||
                     root.TryGetProperty("error", out _)))
                {
                    return line;
                }
            }
            catch (JsonException)
            {
                // An unrelated or malformed line is not a command response.
            }
        }

        return null;
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
                    EmitConsoleEvent(OutputChunkReceived, chunk);
                    EmitCompletedLines(chunk, pendingLine);
                }
            }

            if (emitConsoleEvents && pendingLine.Length > 0)
            {
                EmitConsoleEvent(OutputReceived, pendingLine.ToString());
            }
        }
        catch (ObjectDisposedException)
        {
        }
        catch (IOException)
        {
        }
    }

    private void EmitConsoleEvent(EventHandler<string>? subscribers, string text)
    {
        if (subscribers is null)
        {
            return;
        }

        // One faulty UI listener must not stop the serial pump or suppress
        // subsequent listeners. The boot evidence recorder runs independently.
        foreach (EventHandler<string> subscriber in subscribers.GetInvocationList())
        {
            try
            {
                subscriber(this, text);
            }
            catch (Exception exception)
            {
                Debug.WriteLine($"QEMU console event subscriber failed: {exception}");
            }
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
                    EmitConsoleEvent(OutputReceived, pendingLine.ToString());
                    pendingLine.Clear();
                }

                continue;
            }

            pendingLine.Append(character);
        }
    }

    private static void CancelQmpCapture(CancellationTokenSource? cancellation)
    {
        // Use the per-run snapshot, never the mutable current-run field.
        try
        {
            cancellation?.Cancel();
        }
        catch (ObjectDisposedException)
        {
            // Concurrent disposal has already stopped optional host evidence.
        }
        catch (AggregateException exception)
        {
            // A throwing cancellation callback must not prevent QEMU cleanup.
            Debug.WriteLine($"QMP cancellation callback failed: {exception}");
        }
    }

    private static void CancelConsoleInput(CancellationTokenSource? cancellation)
    {
        try
        {
            cancellation?.Cancel();
        }
        catch (ObjectDisposedException)
        {
            // Dispose may already own the per-run console cancellation.
        }
        catch (AggregateException exception)
        {
            // A throwing cancellation callback must not escape Process.Exited
            // or leave StopAsync with its lifecycle barrier permanently set.
            Debug.WriteLine($"QEMU console cancellation callback failed: {exception}");
        }
    }

    private static async Task JoinQmpCaptureAsync(
        Task? task, CancellationTokenSource? cancellation)
    {
        try
        {
            if (task is not null)
            {
                await task.ConfigureAwait(false);
            }
        }
        catch (Exception)
        {
            // Optional host-only evidence cannot turn StopAsync into a boot failure.
        }
        finally
        {
            cancellation?.Dispose();
        }
    }

    public async Task StopAsync(CancellationToken cancellationToken = default)
    {
        Process? process;
        Task? captureTask;
        Task? qmpTask;
        CancellationTokenSource? qmpCancellation;
        CancellationTokenSource? consoleCancellation;
        lock (_lifecycleSync)
        {
            ObjectDisposedException.ThrowIf(_disposed, this);
            if (_stopping)
            {
                throw new InvalidOperationException("QEMU stop is already in progress.");
            }

            // A stop barrier is visible to StartCore before any asynchronous
            // wait. Every resource is pinned to the run that is being stopped.
            _stopping = true;
            process = _process;
            captureTask = _captureCompletion;
            qmpTask = _qmpCompletion;
            qmpCancellation = _qmpCancellation;
            consoleCancellation = _consoleCancellation;
        }

        CancelQmpCapture(qmpCancellation);
        CancelConsoleInput(consoleCancellation);
        try
        {
            if (process is null)
            {
                return;
            }

            if (process.HasExited)
            {
                if (captureTask is not null)
                {
                    await captureTask.ConfigureAwait(false);
                }
                return;
            }

            try
            {
                // -serial mon:stdio uses QEMU's stdio multiplexer.
                // Ctrl-A X is the native mux command for terminating the emulator.
                // If a console writer cannot release the gate promptly, skip
                // the mux command and force-kill instead of hanging shutdown.
                if (await _consoleInputGate.WaitAsync(TimeSpan.FromSeconds(3))
                    .ConfigureAwait(false))
                {
                    try
                    {
                        using var muxTimeout = new CancellationTokenSource(TimeSpan.FromSeconds(3));
                        await process.StandardInput.WriteAsync("\u0001x".AsMemory(),
                            muxTimeout.Token).ConfigureAwait(false);
                        await process.StandardInput.FlushAsync(muxTimeout.Token)
                            .ConfigureAwait(false);
                    }
                    finally
                    {
                        _consoleInputGate.Release();
                    }

                    var gracefulExit = process.WaitForExitAsync(cancellationToken);
                    var timeout = Task.Delay(TimeSpan.FromSeconds(3), cancellationToken);
                    if (await Task.WhenAny(gracefulExit, timeout).ConfigureAwait(false) == gracefulExit)
                    {
                        await gracefulExit.ConfigureAwait(false);
                        if (captureTask is not null)
                        {
                            await captureTask.ConfigureAwait(false);
                        }
                        return;
                    }
                }
            }
            catch (IOException)
            {
                // Broken redirected stdin must not bypass forced termination.
            }
            catch (InvalidOperationException)
            {
            }
            catch (OperationCanceledException)
            {
                // A canceled graceful wait still requires process termination.
            }
            catch (ObjectDisposedException)
            {
                // Dispose may concurrently tear down an exited process.
                return;
            }

            try
            {
                if (!process.HasExited)
                {
                    process.Kill(entireProcessTree: true);
                    await process.WaitForExitAsync(CancellationToken.None)
                        .ConfigureAwait(false);
                }
            }
            catch (InvalidOperationException)
            {
                // QEMU exited between the HasExited check and Kill.
            }
            catch (ObjectDisposedException)
            {
                // Dispose owns the process after it marks the runtime disposed.
            }

            if (captureTask is not null)
            {
                await captureTask.ConfigureAwait(false);
            }
        }
        catch (ObjectDisposedException)
        {
            // Dispose may release process handles while a stop is in flight.
        }
        finally
        {
            await JoinQmpCaptureAsync(qmpTask, qmpCancellation).ConfigureAwait(false);
            consoleCancellation?.Dispose();
            lock (_lifecycleSync)
            {
                if (ReferenceEquals(_consoleCancellation, consoleCancellation))
                {
                    _consoleCancellation = null;
                }
                // Identity guards prevent cleanup of any later run's resources.
                if (ReferenceEquals(_qmpCompletion, qmpTask))
                {
                    _qmpCompletion = null;
                }
                if (ReferenceEquals(_qmpCancellation, qmpCancellation))
                {
                    _qmpCancellation = null;
                }
                _stopping = false;
            }
        }
    }

    public void Dispose()
    {
        Process? process;
        Task? captureTask;
        Task? qmpTask;
        CancellationTokenSource? qmpCancellation;
        CancellationTokenSource? consoleCancellation;
        lock (_lifecycleSync)
        {
            if (_disposed)
            {
                return;
            }
            _disposed = true;
            process = _process;
            captureTask = _captureCompletion;
            qmpTask = _qmpCompletion;
            qmpCancellation = _qmpCancellation;
            consoleCancellation = _consoleCancellation;
        }

        // Dispose can overlap an in-progress StopAsync, but never a new Start.
        // Both operate only on captured run identities; CTS.Dispose is idempotent.
        CancelQmpCapture(qmpCancellation);
        CancelConsoleInput(consoleCancellation);
        try
        {
            qmpTask?.GetAwaiter().GetResult();
        }
        catch (Exception)
        {
            // Host-side QMP diagnostics must not obstruct disposal.
        }
        finally
        {
            qmpCancellation?.Dispose();
            consoleCancellation?.Dispose();
            lock (_lifecycleSync)
            {
                if (ReferenceEquals(_consoleCancellation, consoleCancellation))
                {
                    _consoleCancellation = null;
                }
                if (ReferenceEquals(_qmpCompletion, qmpTask))
                {
                    _qmpCompletion = null;
                }
                if (ReferenceEquals(_qmpCancellation, qmpCancellation))
                {
                    _qmpCancellation = null;
                }
            }
        }

        try
        {
            if (process is { HasExited: false })
            {
                process.Kill(entireProcessTree: true);
            }
        }
        catch (InvalidOperationException)
        {
            // The process exited after the HasExited check.
        }
        catch (ObjectDisposedException)
        {
            // A concurrent stop already released the process handle.
        }

        // Preserve redirected pipes until both capture tasks finish.
        if (process is not null)
        {
            if (captureTask is not null)
            {
                _ = captureTask.ContinueWith(
                    _ => process.Dispose(), TaskScheduler.Default);
            }
            else
            {
                process.Dispose();
            }
        }
    }
}

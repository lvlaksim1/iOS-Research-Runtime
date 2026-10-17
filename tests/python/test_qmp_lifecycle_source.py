"""Static source contract for per-run host-only QMP task ownership.

These checks are not a C# compilation, QEMU integration test, or guest proof.
"""

from pathlib import Path
import re
import unittest

SOURCE = Path(__file__).resolve().parents[2] / "src/IOSResearchRuntime/Services/QemuRuntime.cs"


class QmpLifecycleSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE.read_text(encoding="utf-8")
        cls.start = cls.section("public Task StartAsync(", "public async Task SendLineAsync(")
        cls.capture = cls.section("private async Task CapturePciTopologyAsync(", "private async Task PumpStreamAsync(")
        cls.stop = cls.section("public async Task StopAsync(", "public void Dispose()")
        cls.dispose = cls.source.split("public void Dispose()", 1)[1]

    @classmethod
    def section(cls, begin, end):
        return cls.source.split(begin, 1)[1].split(end, 1)[0]

    def test_task_and_cancellation_have_owned_fields(self):
        self.assertIn("private Task? _qmpCompletion;", self.source)
        self.assertIn("private CancellationTokenSource? _qmpCancellation;", self.source)

    def test_restart_waits_for_prior_qmp_task(self):
        self.assertIn("_qmpCompletion is { IsCompleted: false }", self.start)
        self.assertLess(self.start.index("_qmpCompletion is { IsCompleted: false }"),
                        self.start.index("_layout.EnsureDirectories();"))
        self.assertIn("_captureCompletion is { IsCompleted: false }", self.start)

    def test_qmp_cancellation_is_linked_to_start_token(self):
        self.assertIn("CancellationTokenSource.CreateLinkedTokenSource(cancellationToken)", self.start)
        self.assertIn("_qmpCancellation.Token", self.start)

    def test_qmp_is_tracked_and_runs_off_ui_thread(self):
        self.assertRegex(self.start, r"_qmpCompletion\s*=\s*Task\.Run\(")
        self.assertNotIn("_ = CapturePciTopologyAsync", self.source)
        self.assertIn("CapturePciTopologyAsync(", self.start)

    def test_stop_cancels_before_early_return_paths(self):
        self.assertLess(self.stop.index("CancelQmpCapture(qmpCancellation);"),
                        self.stop.index("if (process is null)"))
        self.assertIn("if (process.HasExited)", self.stop)
        self.assertIn("process.Kill(entireProcessTree: true)", self.stop)

    def test_stop_joins_even_on_early_return_and_exception(self):
        self.assertRegex(self.stop, r"finally\s*\{\s*await JoinQmpCaptureAsync\(qmpTask, qmpCancellation\)\.ConfigureAwait\(false\);")
        self.assertIn("return;", self.stop)

    def test_join_drains_before_disposing_token_source(self):
        join = self.section("private static async Task JoinQmpCaptureAsync(", "public async Task StopAsync(")
        self.assertLess(join.index("await task.ConfigureAwait(false)"),
                        join.index("cancellation?.Dispose();"))
        self.assertIn("_qmpCompletion = null;", self.stop)
        self.assertIn("catch (Exception)", join)

    def test_dispose_cancels_and_synchronously_drains_qmp(self):
        self.assertLess(self.dispose.index("CancelQmpCapture(qmpCancellation);"),
                        self.dispose.index("qmpTask?.GetAwaiter().GetResult();"))
        self.assertLess(self.dispose.index("qmpTask?.GetAwaiter().GetResult();"),
                        self.dispose.index("process.Kill(entireProcessTree: true)"))
        self.assertIn("qmpCancellation?.Dispose();", self.dispose)

    def test_disposed_runtime_cannot_restart(self):
        self.assertIn("ObjectDisposedException.ThrowIf(_disposed, this)", self.start)
        self.assertIn("if (_disposed)", self.dispose)
        self.assertIn("_disposed = true;", self.dispose)

    def test_qmp_io_awaits_do_not_require_wpf_continuations(self):
        # The QMP capture is on Task.Run, and its own awaited I/O is configured
        # to avoid capturing a synchronization context in future refactors.
        self.assertIn("Task.Run(() => CapturePciTopologyAsync", self.start)
        self.assertGreaterEqual(self.capture.count(".ConfigureAwait(false)"), 10)
        self.assertEqual(self.capture.count("await writer.WriteLineAsync("), 2)
        self.assertEqual(self.capture.count(".AsMemory(),\n                token).ConfigureAwait(false);"), 2)
        self.assertIn("await Task.Delay(TimeSpan.FromMilliseconds(100), cancellationToken).ConfigureAwait(false);", self.capture)

    def test_host_only_receipt_remains_explicit(self):
        self.assertIn('source = "QMP_QUERY_PCI_HOST_ONLY"', self.capture)
        self.assertIn("guest_nvme_bound = false", self.capture)
        self.assertIn("stage1_accepted = false", self.capture)

    def test_cancel_handles_concurrent_disposal(self):
        cancel = self.section("private static void CancelQmpCapture(", "private static async Task JoinQmpCaptureAsync(")
        self.assertIn("cancellation?.Cancel();", cancel)
        self.assertIn("catch (ObjectDisposedException)", cancel)


    def test_qmp_cancellation_isolates_throwing_callbacks(self):
        helper = self.section("private static void CancelQmpCapture(",
                              "private static void CancelConsoleInput(")
        self.assertIn("cancellation?.Cancel();", helper)
        self.assertIn("catch (ObjectDisposedException)", helper)
        self.assertIn("catch (AggregateException exception)", helper)
        self.assertIn('Debug.WriteLine($"QMP cancellation callback failed:', helper)
        self.assertLess(helper.index("cancellation?.Cancel();"),
                        helper.index("catch (AggregateException exception)"))

    def test_console_cancellation_isolates_throwing_callbacks(self):
        helper = self.section("private static void CancelConsoleInput(",
                              "private static async Task JoinQmpCaptureAsync(")
        self.assertIn("cancellation?.Cancel();", helper)
        self.assertIn("catch (ObjectDisposedException)", helper)
        self.assertIn("catch (AggregateException exception)", helper)
        self.assertIn('Debug.WriteLine($"QEMU console cancellation callback failed:', helper)
        self.assertLess(helper.index("cancellation?.Cancel();"),
                        helper.index("catch (AggregateException exception)"))

    def test_start_is_serialized_with_stop_and_dispose(self):
        self.assertIn("private readonly object _lifecycleSync = new();", self.source)
        self.assertIn("private bool _stopping;", self.source)
        self.assertRegex(self.start, r"lock \(_lifecycleSync\)\s*\{\s*return StartCore\(cancellationToken\);")
        self.assertRegex(self.start, r"private Task StartCore\(CancellationToken cancellationToken\)\s*\{\s*ObjectDisposedException.ThrowIf\(_disposed, this\);\s*if \(_stopping\)")

    def test_stop_barrier_and_identity_snapshot_before_await(self):
        head = self.stop.split("CancelQmpCapture(qmpCancellation);", 1)[0]
        self.assertIn("lock (_lifecycleSync)", head)
        self.assertLess(head.index("_stopping = true;"), head.index("qmpTask = _qmpCompletion;"))
        self.assertIn("qmpCancellation = _qmpCancellation;", head)
        self.assertNotIn("await ", head)
        self.assertIn("if (_stopping)", head)

    def test_join_uses_only_captured_identity(self):
        join = self.section("private static async Task JoinQmpCaptureAsync(", "public async Task StopAsync(")
        self.assertIn("Task? task, CancellationTokenSource? cancellation", join)
        self.assertIn("await task.ConfigureAwait(false)", join)
        self.assertNotIn("_qmpCompletion", join)
        self.assertNotIn("_qmpCancellation", join)
        self.assertIn("JoinQmpCaptureAsync(qmpTask, qmpCancellation)", self.stop)

    def test_stop_identity_cleanup_under_lock(self):
        tail = self.stop.split("await JoinQmpCaptureAsync(qmpTask, qmpCancellation)", 1)[1]
        self.assertIn("lock (_lifecycleSync)", tail)
        self.assertRegex(tail, r"if \(ReferenceEquals\(_qmpCompletion, qmpTask\)\)\s*\{\s*_qmpCompletion = null;")
        self.assertRegex(tail, r"if \(ReferenceEquals\(_qmpCancellation, qmpCancellation\)\)\s*\{\s*_qmpCancellation = null;")
        self.assertIn("_stopping = false;", tail)

    def test_dispose_sets_terminal_barrier_under_lock(self):
        self.assertRegex(self.dispose, r"lock \(_lifecycleSync\)\s*\{\s*if \(_disposed\)\s*\{\s*return;\s*\}\s*_disposed = true;")
        self.assertIn("qmpTask = _qmpCompletion;", self.dispose)
        self.assertIn("qmpCancellation = _qmpCancellation;", self.dispose)
        self.assertIn("ReferenceEquals(_qmpCompletion, qmpTask)", self.dispose)
        self.assertIn("ReferenceEquals(_qmpCancellation, qmpCancellation)", self.dispose)


    def test_console_input_uses_per_run_cancel_and_serial_gate(self):
        self.assertIn("private readonly SemaphoreSlim _consoleInputGate = new(1, 1);", self.source)
        self.assertIn("private CancellationTokenSource? _consoleCancellation;", self.source)
        self.assertIn("var consoleCancellation = new CancellationTokenSource();", self.start)
        self.assertIn("_consoleCancellation = consoleCancellation;", self.start)
        send = self.section("public async Task SendLineAsync(", "private async Task CapturePciTopologyAsync(")
        self.assertIn("CancellationTokenSource.CreateLinkedTokenSource(", send)
        self.assertIn("cancellationToken, _consoleCancellation.Token", send)
        self.assertIn("await _consoleInputGate.WaitAsync(token)", send)
        self.assertIn("finally\n        {\n            _consoleInputGate.Release();", send)

    def test_console_rechecks_stop_barrier_after_gate(self):
        send = self.section("public async Task SendLineAsync(", "private async Task CapturePciTopologyAsync(")
        self.assertLess(send.index("await _consoleInputGate.WaitAsync(token)"),
                        send.index("if (_stopping || _disposed || !ReferenceEquals(_process, process))"))
        self.assertIn("lock (_lifecycleSync)", send)
        self.assertIn("ObjectDisposedException.ThrowIf(_disposed, this)", send)

    def test_each_console_write_is_cancelable(self):
        send = self.section("public async Task SendLineAsync(", "private async Task CapturePciTopologyAsync(")
        self.assertIn("WriteAsync(line.AsMemory(index, 1), token)", send)
        self.assertIn('WriteAsync("\\n".AsMemory(), token)', send)
        self.assertEqual(send.count("FlushAsync(token)"), 2)
        self.assertIn("Task.Delay(TimeSpan.FromMilliseconds(10), token)", send)

    def test_stop_cancels_console_before_mux_and_bounded_gate(self):
        self.assertIn("consoleCancellation = _consoleCancellation;", self.stop)
        self.assertLess(self.stop.index("_stopping = true;"),
                        self.stop.index("CancelConsoleInput(consoleCancellation);"))
        self.assertLess(self.stop.index("CancelConsoleInput(consoleCancellation);"),
                        self.stop.index("_consoleInputGate.WaitAsync(TimeSpan.FromSeconds(3))"))
        self.assertIn("_consoleInputGate.Release();", self.stop)
        self.assertIn("using var muxTimeout = new CancellationTokenSource(TimeSpan.FromSeconds(3));", self.stop)
        self.assertIn("muxTimeout.Token", self.stop)

    def test_broken_stdio_falls_back_to_kill(self):
        self.assertRegex(self.stop,
                         r"catch \(IOException\)\s*\{[^}]*\}\s*catch \(InvalidOperationException\)")
        self.assertLess(self.stop.index("catch (IOException)"),
                        self.stop.index("process.Kill(entireProcessTree: true)"))
        self.assertIn("catch (OperationCanceledException)", self.stop)
        self.assertIn("await process.WaitForExitAsync(CancellationToken.None)", self.stop)

    def test_console_identity_cleanup_and_dispose_cancellation(self):
        self.assertIn("consoleCancellation?.Dispose();", self.stop)
        self.assertIn("ReferenceEquals(_consoleCancellation, consoleCancellation)", self.stop)
        self.assertIn("_consoleCancellation = null;", self.stop)
        self.assertIn("CancelConsoleInput(consoleCancellation);", self.dispose)
        self.assertIn("consoleCancellation?.Dispose();", self.dispose)
        self.assertIn("ReferenceEquals(_consoleCancellation, consoleCancellation)", self.dispose)

    def test_console_cancellation_handles_dispose_race(self):
        cancel = self.section("private static void CancelConsoleInput(", "private static async Task JoinQmpCaptureAsync(")
        self.assertIn("cancellation?.Cancel();", cancel)
        self.assertIn("catch (ObjectDisposedException)", cancel)


    def test_isrunning_fails_closed_after_dispose(self):
        getter = self.section("public bool IsRunning", "public string? CurrentLogPath")
        self.assertIn("lock (_lifecycleSync)", getter)
        self.assertIn("if (_disposed || _process is null)", getter)
        self.assertIn("return !_process.HasExited;", getter)
        self.assertIn("catch (ObjectDisposedException)", getter)
        self.assertIn("catch (InvalidOperationException)", getter)

    def test_restart_cancels_old_console_and_checks_gate_before_launch(self):
        start = self.start
        self.assertLess(start.index("CancelConsoleInput(_consoleCancellation);"),
                        start.index("_consoleInputGate.CurrentCount != 1"))
        self.assertLess(start.index("_consoleInputGate.CurrentCount != 1"),
                        start.index("_consoleCancellation.Dispose();"))
        self.assertLess(start.index("_consoleCancellation.Dispose();"),
                        start.index("_layout.EnsureDirectories();"))
        self.assertIn("Previous QEMU console input is still finalizing.", start)

    def test_restart_gate_guard_is_independent_of_console_cts_presence(self):
        # StopAsync clears _consoleCancellation even if a canceled writer
        # still holds the gate; restart must reject that stale writer.
        start = self.start
        self.assertRegex(start,
                         r"CancelConsoleInput\(_consoleCancellation\);\s*\}\s*"
                         r"//[^\n]*\n\s*//[^\n]*\n\s*//[^\n]*\n\s*"
                         r"if \(_consoleInputGate\.CurrentCount != 1\)")
        self.assertLess(start.index("_consoleInputGate.CurrentCount != 1"),
                        start.index("_consoleCancellation.Dispose();"))
        self.assertLess(start.index("_consoleInputGate.CurrentCount != 1"),
                        start.index("_process.Dispose();"))

    def test_exit_event_cancels_exact_process_console_cts(self):
        start = self.start
        self.assertLess(start.index("var consoleCancellation = new CancellationTokenSource();"),
                        start.index("if (!process.Start())"))
        self.assertRegex(start, r"process\.Exited \+= \(_, _\) =>\s*\{\s*try\s*\{\s*CancelConsoleInput\(consoleCancellation\);")
        self.assertIn("CancelConsoleInput(consoleCancellation);", start)
        self.assertIn("consoleCancellation.Dispose();", start)

    def test_console_linked_token_registered_under_lifecycle_lock(self):
        send = self.section("public async Task SendLineAsync(", "private async Task CapturePciTopologyAsync(")
        head = send.split("await _consoleInputGate.WaitAsync(token)", 1)[0]
        self.assertRegex(head, r"lock \(_lifecycleSync\)[\s\S]*linked = CancellationTokenSource\.CreateLinkedTokenSource\(")
        self.assertLess(head.index("linked = CancellationTokenSource.CreateLinkedTokenSource("),
                        head.index("using var ownedLinked = linked;"))
        self.assertIn("cancellationToken, _consoleCancellation.Token", head)
        self.assertIn("!ReferenceEquals(_process, process)", send)

    def test_exit_callback_is_tracked_and_blocks_restart(self):
        self.assertIn("private Task? _exitNotificationCompletion;", self.source)
        self.assertIn("_exitNotificationCompletion = exitNotification.Task;", self.start)
        self.assertIn("_exitNotificationCompletion is { IsCompleted: false }", self.start)
        self.assertLess(self.start.index("_exitNotificationCompletion is { IsCompleted: false }"),
                        self.start.index("_process.Dispose();"))
        self.assertLess(self.start.index("_exitNotificationCompletion is { IsCompleted: false }"),
                        self.start.index("_layout.EnsureDirectories();"))

    def test_exit_callback_finishes_after_listener(self):
        self.assertIn("new TaskCompletionSource<bool>(", self.start)
        self.assertIn("TaskCreationOptions.RunContinuationsAsynchronously", self.start)
        notification_call = ("listener(this, exitCode);" if "listener(this, exitCode);" in self.start
                             else "Exited?.Invoke(this, exitCode);")
        self.assertLess(self.start.index(notification_call),
                        self.start.index("exitNotification.TrySetResult(true);"))
        self.assertRegex(self.start,
                         r"finally\s*\{[\s\S]{0,200}exitNotification\.TrySetResult\(true\);")

    def test_exit_notification_subscriber_exception_is_isolated(self):
        # An exception in an external event subscriber must not escape a
        # Process.Exited callback on a ThreadPool thread. This is a static
        # contract only; CLR execution remains a separate gate.
        callback = self.start.split("process.Exited += (_, _) =>", 1)[1]
        callback = callback.split("// Publish the process identity", 1)[0]
        self.assertRegex(callback,
                         r"foreach \(EventHandler<int> listener in exitListeners\.GetInvocationList\(\)\)"
                         r"\s*\{\s*try\s*\{\s*listener\(this, exitCode\);\s*\}\s*"
                         r"catch \(Exception exception\)")
        self.assertIn("Debug.WriteLine", callback)
        self.assertLess(callback.index("catch (Exception exception)"),
                        callback.index("exitNotification.TrySetResult(true);"))

    def test_exit_multicast_failure_does_not_starve_later_subscribers(self):
        # This verifies source structure, not CLR execution of the event.
        callback = self.start.split("process.Exited += (_, _) =>", 1)[1]
        callback = callback.split("// Publish the process identity", 1)[0]
        self.assertIn("var exitListeners = Exited;", callback)
        self.assertIn("if (exitListeners is not null)", callback)
        self.assertRegex(callback,
                         r"foreach \(EventHandler<int> listener in exitListeners\.GetInvocationList\(\)\)"
                         r"\s*\{\s*try\s*\{\s*listener\(this, exitCode\);\s*\}\s*"
                         r"catch \(Exception exception\)")
        self.assertLess(callback.index("catch (Exception exception)"),
                        callback.index("exitNotification.TrySetResult(true);"))

    def test_exit_callback_checks_process_identity_and_disposal(self):
        handler = self.start.split("process.Exited += (_, _) =>", 1)[1]
        handler = handler.split("if (!process.Start())", 1)[0]
        self.assertIn("lock (_lifecycleSync)", handler)
        self.assertIn("if (_disposed || !ReferenceEquals(_process, process))", handler)
        self.assertIn("catch (ObjectDisposedException)", handler)
        self.assertIn("catch (InvalidOperationException)", handler)

    def test_immediate_exit_callback_sees_registered_process_identity(self):
        # Process.Exited can be dispatched before Process.Start returns.
        # StartCore holds the lifecycle lock throughout launch, so the
        # callback must find the process identity when it acquires that lock.
        start = self.start
        callback = start.split("process.Exited += (_, _) =>", 1)[1]
        self.assertIn("!ReferenceEquals(_process, process)", callback)
        self.assertLess(start.index("_process = process;"),
                        start.index("if (!process.Start())"))
        self.assertRegex(start,
                         r"catch\s*\{\s*//[^\n]*\n\s*_process = null;")
        self.assertEqual(start.count("_process = process;"), 1)

    def test_prior_process_handle_disposed_only_after_all_barriers(self):
        self.assertLess(self.start.index("_captureCompletion is { IsCompleted: false }"),
                        self.start.index("_process.Dispose();"))
        self.assertLess(self.start.index("_qmpCompletion is { IsCompleted: false }"),
                        self.start.index("_process.Dispose();"))
        self.assertLess(self.start.index("_consoleInputGate.CurrentCount != 1"),
                        self.start.index("_process.Dispose();"))
        self.assertLess(self.start.index("_exitNotificationCompletion is { IsCompleted: false }"),
                        self.start.index("_process.Dispose();"))
        self.assertLess(self.start.index("_process.Dispose();"),
                        self.start.index("var process = new Process"))
        self.assertIn("_captureCompletion = null;", self.start)
        self.assertIn("_exitNotificationCompletion = null;", self.start)

    def test_console_events_isolate_throwing_subscribers_individually(self):
        helper = self.section("private void EmitConsoleEvent(",
                              "private static async Task FinalizeCaptureAsync(")
        self.assertIn("EventHandler<string>? subscribers", self.source)
        self.assertIn("subscribers.GetInvocationList()", helper)
        self.assertRegex(helper, r"foreach \(EventHandler<string> subscriber in subscribers\.GetInvocationList\(\)\)")
        self.assertRegex(helper, r"try\s*\{\s*subscriber\(this, text\);")
        self.assertRegex(helper, r"catch \(Exception exception\)")
        self.assertIn("Debug.WriteLine(", helper)

    def test_every_console_output_dispatch_uses_isolation(self):
        pump = self.section("private async Task PumpStreamAsync(",
                            "private void EmitConsoleEvent(")
        lines = self.section("private void EmitCompletedLines(",
                             "private static void CancelQmpCapture(")
        self.assertIn("EmitConsoleEvent(OutputChunkReceived, chunk);", pump)
        self.assertIn("EmitConsoleEvent(OutputReceived, pendingLine.ToString());", pump)
        self.assertIn("EmitConsoleEvent(OutputReceived, pendingLine.ToString());", lines)
        self.assertNotIn("OutputChunkReceived?.Invoke", self.source)
        self.assertNotIn("OutputReceived?.Invoke", self.source)
        self.assertLess(pump.index("record(chunk);"),
                        pump.index("EmitConsoleEvent(OutputChunkReceived, chunk);"))

    def test_console_listener_failures_do_not_bypass_capture_completion(self):
        finalize = self.section("private static async Task FinalizeCaptureAsync(",
                                "private void EmitCompletedLines(")
        self.assertIn("await Task.WhenAll(serialPump, diagnosticPump)", finalize)
        self.assertRegex(finalize, r"finally\s*\{\s*//[^\n]*\n\s*capture\.Complete\(\);")
        helper = self.section("private void EmitConsoleEvent(",
                              "private static async Task FinalizeCaptureAsync(")
        self.assertLess(helper.index("catch (Exception exception)"),
                        helper.index("Debug.WriteLine("))

    def test_guest_evidence_claims_remain_host_only(self):
        self.assertIn('source = "QMP_QUERY_PCI_HOST_ONLY"', self.capture)
        self.assertIn("guest_nvme_bound = false", self.capture)
        self.assertIn("stage1_accepted = false", self.capture)


class AbstractLifecycleInterleavingTests(unittest.TestCase):
    """Small executable *model*, not an execution of QemuRuntime C# code.

    Static source checks above tie its stop barrier and identity guards to this
    abstract state machine. These tests do not establish CLR concurrency safety.
    """

    class Model:
        def __init__(self):
            self.run = 1
            self.stopping = False
            self.disposed = False
            self.qmp_task = 1
            self.qmp_cts = 1

        def start(self):
            if self.disposed or self.stopping:
                return False
            self.run += 1
            self.qmp_task = self.run
            self.qmp_cts = self.run
            return True

        def begin_stop(self):
            if self.disposed or self.stopping:
                return None
            self.stopping = True
            return (self.qmp_task, self.qmp_cts)

        def finish_stop(self, snapshot):
            if self.qmp_task == snapshot[0]:
                self.qmp_task = None
            if self.qmp_cts == snapshot[1]:
                self.qmp_cts = None
            self.stopping = False

        def dispose(self):
            self.disposed = True

    def test_restart_rejected_while_prior_stop_pending_even_if_qmp_completed(self):
        model = self.Model()
        prior = model.begin_stop()
        self.assertEqual(prior, (1, 1))
        self.assertFalse(model.start())
        model.finish_stop(prior)
        self.assertTrue(model.start())
        self.assertEqual(model.qmp_task, 2)

    def test_identity_cleanup_does_not_clear_hypothetical_new_run(self):
        model = self.Model()
        prior = model.begin_stop()
        # Deliberate adversarial injection: a stale stop finalizer must not
        # clear a newer task even if a future refactor weakens the start gate.
        model.qmp_task, model.qmp_cts = 99, 99
        model.finish_stop(prior)
        self.assertEqual((model.qmp_task, model.qmp_cts), (99, 99))

    def test_dispose_blocks_restart_at_all_stop_boundaries(self):
        for dispose_before_stop in (True, False):
            model = self.Model()
            if dispose_before_stop:
                model.dispose()
                self.assertIsNone(model.begin_stop())
            else:
                prior = model.begin_stop()
                model.dispose()
                model.finish_stop(prior)
            self.assertFalse(model.start())

    def test_overlapping_stops_cannot_replace_snapshot(self):
        model = self.Model()
        prior = model.begin_stop()
        self.assertIsNone(model.begin_stop())
        self.assertEqual((model.qmp_task, model.qmp_cts), prior)
        model.finish_stop(prior)


if __name__ == "__main__":
    unittest.main()

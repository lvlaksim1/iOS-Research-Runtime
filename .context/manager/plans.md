# Manager plans

## PP-RM generation 15 — accepted design

Manager generation: 15.
Product authority: `main`.
Current product: `main@eaa98114031a37343e0d5184bd132830818a6b2f`.

### Topology
Use exactly five Scheduled Tasks:
1. Worker A.
2. Worker B.
3. Runtime Mailbox.
4. Trace.
5. Watchdog.

Worker A/B prompts are immutable.
Watchdog prompt is immutable.
Mailbox is the sole activation and Watchdog-state authority.

### Watchdog liveness root
Every Watchdog invocation MUST perform, as its FIRST tool operation:
- re-arm the same Watchdog task for exactly +5 minutes;
- preserve exact title and immutable prompt.

No read or other operation may precede the self-rearm.
The 5-minute Watchdog cadence is fixed and non-adaptive.

Mailbox carries current baton plus Watchdog state including:
- watch_seq;
- watch_seen_generation;
- watch_seen_activation_attempt;
- watch_seen_activation_token;
- watch_seen_message_id;
- watch_seen_owner_slot;
- watch_seen_progress_seq;
- watch_stall_checks;
- watch_last_ok.

### Worker behavior
Workers never rewrite Watchdog prompt.
Workers continue rapid fixed A↔B ping-pong.
Sender finishes/reconciles side effects, writes/stabilizes next Mailbox baton, appends Trace SEND, then arms successor worker as its final tool operation.
If Watchdog is unexpectedly disabled while a package is RUNNING, a worker may only restore the unchanged Watchdog schedule; it must never rewrite the Watchdog prompt.

### Recovery preserved
- dispatch_retry is separate from activation_attempt;
- unchanged owner last_run_time from dispatch baseline => DISPATCH_FAILURE, no activation_attempt consumption;
- repeated dispatch failure => same-generation token rotation and partner failover;
- advanced last_run_time with no ACK => confirmed RUNTIME_FAILURE and activation_attempt consumption;
- ACKed no-progress across two Watchdog observations => confirmed RUNTIME_STALL;
- max three confirmed runtime failures/stalls per generation;
- stale runtimes are fenced before mutation/handoff;
- ambiguous ref mutation requires authoritative reconciliation before replay.

### Terminal path
Watchdog self-rearms first.
On FINAL or genuine FAIL_STOP:
1. publish terminal Mailbox/Trace durably;
2. final scheduler cleanup disables the already pre-armed Watchdog.
If cleanup is lost, the next Watchdog invocation reads terminal state and disables itself without product mutation.

### OCB
Unchanged:
- explicit OSB only;
- max three exact-identical attempts total;
- no attempt 4;
- no unrelated calls between exact retries;
- ambiguous mutation requires authoritative reconciliation.

## Runtime status — DO NOT LAUNCH
Package `IOS-M1-CONTINUOUS-004` was inadvertently activated before the Owner's no-launch instruction and is now stopped with Worker A, Worker B and Watchdog disabled.
No product-main mutation resulted; live main remains `eaa98114031a37343e0d5184bd132830818a6b2f`.

Reserve next clean package:
- package: `IOS-M1-CONTINUOUS-005`
- status: DEFINED / NOT ARMED
- product start: `main@eaa98114031a37343e0d5184bd132830818a6b2f`
- start checkpoint: generation-19 factual checkpoint from package 003
- launch authority: new explicit Owner instruction required

Do not reconfigure or arm the five PP-RM tasks for package 005 until that explicit launch instruction arrives.

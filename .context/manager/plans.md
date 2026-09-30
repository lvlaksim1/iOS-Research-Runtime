# Manager plans

## PP-RM generation 17 — recurring-backstop continuity

Manager generation: 17.
Product authority: `main`.
Current product: `main@bcde5661eab70b6811a5f1fffe0552edaedf980a`.
Authorized package: `IOS-M1-CONTINUOUS-006`.

### Topology
Exactly five Scheduled Tasks:
1. Worker A
2. Worker B
3. Runtime Mailbox
4. Trace
5. Watchdog

No Lifeboat and no additional active slot.
A/B and Watchdog prompts are immutable after package configuration.

### Product mutation protocol
Generation-16 native two-phase mutation execution is retained without semantic change.

READY/PREPARE:
- one initial Scheduled Tasks read;
- validate exact package/generation/attempt/token/message/owner;
- durable ACK;
- one bounded evidence/implementation unit;
- immutable Git objects allowed;
- mutable product refs forbidden;
- when publication is required, freeze mutation_id/operation/baseline/target/force=false and hand off fresh MUTATION_READY.

MUTATION_READY:
- first Scheduled Tasks read is the native ownership fence;
- do not rebuild or choose a different target;
- reconcile authoritative main;
- main==target => already successful;
- main==baseline => update main to frozen target with force=false under OCB3;
- main neither => FAIL_STOP;
- authoritative read-back after mutation;
- success hands off ordinary READY with mutation fields cleared.

### Generation-17 Watchdog schedule
The Watchdog task itself is a persistent recovery object.

Every armed Watchdog schedule MUST contain:
`RRULE:FREQ=HOURLY`
and a DTSTART chosen for the desired next near-term check.

A Watchdog runtime follows this continuity prefix:
1. FIRST TOOL OPERATION: update only THIS SAME Watchdog with `is_enabled=true`; do not provide schedule/prompt/title/timing_mode. Capture returned `updated_at`. This operation must leave the existing recurrence intact.
2. Compute `updated_at + 5 minutes`.
3. SECOND TOOL OPERATION: update THIS SAME Watchdog with `is_enabled=true`, `timing_mode=exact_schedule`, and schedule `DTSTART=<computed>; RRULE:FREQ=HOURLY`; do not rewrite prompt/title.
4. THIRD TOOL OPERATION: read Scheduled Tasks once and execute the existing Watchdog state machine.

Failure before step 1, between steps 1–2, or during step 2 MUST NOT erase the previously persisted hourly recurrence.
The +5 minute slide is a fast-path cadence; the hourly RRULE is the independent backstop.

### Watchdog state machine
After the continuity prefix, generation-16 dispatch/runtime semantics remain:
- resync on baton identity change;
- ack=NONE + unchanged owner last_run_time => dispatch retry/failover without consuming activation_attempt;
- owner runtime observed but no ACK => confirmed runtime failure and activation_attempt consumption;
- ACKed no-progress needs two Watchdog observations before confirmed stall;
- READY stall recovery may fail over same generation;
- MUTATION_READY recovery preserves frozen descriptor and reconciles GitHub main first;
- Watchdog never constructs a product target and never moves main.

### Worker interaction with Watchdog
Workers never rewrite the Watchdog prompt.
If an initial Worker snapshot unexpectedly shows Watchdog disabled while package is RUNNING, restore the same immutable Watchdog as a recurring task with an hourly backstop before arming the successor. Do not introduce a new task.

### Terminal path
FINAL_COMPLETED or FAIL_STOP is published durably first.
Watchdog then disables itself as terminal cleanup. If cleanup is lost, a later hourly occurrence sees terminal state and disables itself without product mutation.

### Initial product unit
Freshly reconcile E2E run `36729602541` on `bcde5661...`, inspect collected failure evidence, extract post-merge bash SignatureInfo plus AMFI/root-shell evidence versus pre-SHA256 baseline, then select one bounded diagnostic/fix and exact-SHA CI.

### OCB3
- explicit OSB only
- attempt1; explicit OSB => exact-identical attempt2
- second explicit OSB => exact-identical attempt3
- third explicit OSB => OCB3_EXHAUSTED
- no attempt4
- no unrelated GitHub calls between exact retries
- ambiguous mutable request requires authoritative reconciliation

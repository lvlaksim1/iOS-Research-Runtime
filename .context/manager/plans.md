# Manager plans

## PP-RM generation 17 — recurring-backstop continuity

Manager generation: 17.
Product authority: `main`.
Current product: `main@bcde5661eab70b6811a5f1fffe0552edaedf980a`.
Active package: `IOS-M1-CONTINUOUS-006`.
Execution status: RUNNING.

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
Generation16 native two-phase mutation execution is retained without semantic change.

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

### Generation17 Watchdog schedule
The Watchdog task itself is the persistent recovery object.
Every armed Watchdog schedule contains `RRULE:FREQ=HOURLY` and a near-term DTSTART.

Healthy invocation:
1. FIRST tool operation: self-update `is_enabled=true` only and capture returned `updated_at`;
2. compute `updated_at+5m`;
3. SECOND tool operation: update same task to computed DTSTART while retaining `RRULE:FREQ=HOURLY`;
4. THIRD tool operation: read Scheduled Tasks and execute ordinary Watchdog recovery logic.

Failure before/during the slide does not erase the already-persisted hourly recurrence.
The +5 minute cadence is a fast path; hourly recurrence is the independent backstop.

### Live launch evidence
- generation1 Worker B ACKed bootstrap READY, reconciled E2E evidence and handed off
- generation2 Worker A ACKed, identified signer hash-selection root cause and handed off
- latest observed baton is generation3 Worker B READY
- Watchdog remains enabled with recurring schedule

### Current product plan
The immediate bounded unit is not another blind E2E.

Generation3 must:
1. inspect supported rcodesign/upstream mechanisms that can stop `import_settings_from_macho` from overriding explicit SHA256;
2. prefer an upstream-supported CLI/config mechanism;
3. otherwise isolate the smallest local signer/tool correction;
4. prove on a bounded post-sign sample that primary CodeDirectory digest is SHA256;
5. only then prepare an immutable product target;
6. publish through the frozen-target MUTATION_READY protocol;
7. run exact-SHA CI/E2E and compare AMFI/CT/root-shell behavior with the SHA1-primary baseline.

### Terminal path
FINAL_COMPLETED or FAIL_STOP is published durably first.
Watchdog then disables itself as terminal cleanup. If cleanup is lost, a later hourly occurrence sees terminal state and disables itself without product mutation.

### OCB3
- explicit OSB only
- attempt1; explicit OSB => exact-identical attempt2
- second explicit OSB => exact-identical attempt3
- third explicit OSB => OCB3_EXHAUSTED
- no attempt4
- no unrelated GitHub calls between exact retries
- ambiguous mutable request requires authoritative reconciliation

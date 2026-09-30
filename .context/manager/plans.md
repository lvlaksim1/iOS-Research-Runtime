# Manager plans

## PP-RM generation18 — result-first workflow evidence

Manager generation: 18.
Product authority: `main`.
Current product: `main@4821fb9a9cd72dd40af2a518962f180fb4344fe7`.
Authorized package: `IOS-M1-CONTINUOUS-007`.

### Topology
Exactly five Scheduled Tasks:
1. Worker A
2. Worker B
3. Runtime Mailbox
4. Trace
5. Watchdog

No Lifeboat and no additional PP-RM active slot.
A/B and Watchdog prompts are immutable after package configuration.

### Product mutation protocol
Generation16 native two-phase mutation execution is retained.

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

### Watchdog
Generation17 recurring-backstop semantics are retained exactly.
Every armed Watchdog schedule contains `RRULE:FREQ=HOURLY` plus a near-term DTSTART.
Healthy invocation:
1. self-update `is_enabled=true` only and capture returned updated_at;
2. set same Watchdog DTSTART=updated_at+5m while retaining hourly RRULE;
3. read Scheduled Tasks and execute normal recovery state machine.

### Result-first workflow gate protocol
When a bounded unit requires a GitHub Actions workflow result, define the acceptance condition by:
- workflow identity/name/path;
- exact required product SHA;
- required terminal conclusion/evidence;
- any test-specific semantic constraints.

Then execute in this order:
1. search existing workflow runs on the exact required SHA;
2. if a qualifying SUCCESS run exists, consume it immediately regardless of trigger event;
3. if a qualifying run is queued/in_progress, observe it and do not start a duplicate;
4. if a qualifying run failed/cancelled, use an authorized rerun-existing capability when appropriate, or diagnose the failure;
5. only if no usable exact-SHA run exists may a new start/dispatch be attempted;
6. if start-new-workflow capability is unavailable, OWNER_GATE is allowed only when a new run is actually required.

A preferred mechanism such as `workflow_dispatch` is never itself the gate unless trigger semantics are the subject of the test.

### Package007 bootstrap
Authoritative starting facts:
- main `4821fb9a9cd72dd40af2a518962f180fb4344fe7`
- `rcodesign Windows Gate` run `36771957949`: SUCCESS, event `push`
- job `verify`: SUCCESS
- signed proof upload: SUCCESS
- Windows Build `36771957738`: SUCCESS

Initial Worker B:
1. ACK package007 bootstrap;
2. reconcile run `36771957949` as already-satisfied exact-main gate;
3. inspect logs/artifacts and extract strict primary-SHA256 proof;
4. decide one smallest bounded next product unit toward exact-SHA E2E/root-shell;
5. use ordinary READY handoff unless a mutable product target is actually prepared.

### Terminal path
FINAL_COMPLETED or FAIL_STOP is published durably first.
Watchdog then disables itself as terminal cleanup.

### OCB3
- explicit OSB only
- attempt1; explicit OSB => exact-identical attempt2
- second explicit OSB => exact-identical attempt3
- third explicit OSB => OCB3_EXHAUSTED
- no attempt4
- no unrelated GitHub calls between exact retries
- ambiguous mutable request requires authoritative reconciliation

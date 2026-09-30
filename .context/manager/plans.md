# Manager plans

## PP-RM generation 16 — native two-phase mutation execution

Manager generation: 16.
Product authority: `main`.
Current product: `main@95e871e84099f10245e912659b2d964c1b3c1037`.
Authorized package: `IOS-M1-CONTINUOUS-005`.

### Topology
Exactly five Scheduled Tasks:
1. Worker A
2. Worker B
3. Runtime Mailbox
4. Trace
5. Watchdog

A/B and Watchdog prompts are immutable after package configuration.
Mailbox carries baton, mutation descriptor and Watchdog observation state.

### One-read worker rule
Each Worker runtime begins with one authoritative Scheduled Tasks read.
That initial snapshot is the runtime's native ownership fence for its permitted phase.
Generation 16 does not require a second Scheduled Tasks read before GitHub mutation.

### Phase 1 — PREPARE
A worker accepting `state=READY`:
1. validates package/generation/attempt/token/message/owner from its first read;
2. ACKs durably;
3. performs one bounded evidence/implementation unit;
4. may create immutable Git blob/tree/commit objects;
5. MUST NOT mutate `main`, releases, tags or another mutable product ref;
6. when no mutable publication is needed, may hand off ordinary READY work;
7. when a target commit is ready, freezes mutation_id, mutation_operation=UPDATE_MAIN, mutation_baseline_main_sha, mutation_target_commit and mutation_force=false;
8. hands the frozen descriptor to the partner as a fresh `MUTATION_READY` generation;
9. successor worker arm is the final tool operation.

### Phase 2 — MUTATION_READY
A worker accepting `state=MUTATION_READY`:
1. validates the exact frozen descriptor from its FIRST Scheduled Tasks read;
2. ACKs mutation execution;
3. MUST NOT create a different target commit;
4. authoritatively reads GitHub main;
5. if main==target, records mutation already resolved successfully;
6. if main==baseline, attempts exactly `update_ref(main -> target, force=false)` under OCB3;
7. if main is neither baseline nor target, durable FAIL_STOP;
8. after update_ref, authoritatively read-backs main;
9. target => success; baseline after a known failed/no-side-effect request => recoverable same frozen mutation; neither => FAIL_STOP;
10. on success, hand off a new ordinary READY generation.

### Idempotent stale-runtime property
Once `MUTATION_READY` is published, every allowed executor/recovery runtime for that mutation is constrained to the same target SHA.
A late stale executor therefore cannot legitimately publish a competing target.
No new GitHub fence request is needed.

### Watchdog
FIRST operation every invocation: re-arm same unchanged Watchdog +5 minutes.
Then read Scheduled Tasks once.

READY-state recovery retains generation-15 dispatch/runtime separation.
MUTATION_READY recovery preserves mutation_id/baseline/target/operation/force exactly, even while activation token/message/owner may rotate.
For an ACKed stalled mutation executor, reconcile GitHub main before recovery.
main==target => side effect success; main==baseline => same frozen mutation remains eligible; main neither => FAIL_STOP.
Never create/rebuild a different target inside mutation recovery.

### Terminal path
Publish FINAL/FAIL_STOP durably before disabling workers/Watchdog.
If Watchdog's pre-armed successor later starts and sees terminal state, it disables itself without product mutation.

### OCB3
- explicit OSB only
- attempt1; explicit OSB => exact-identical attempt2
- second explicit OSB => exact-identical attempt3
- third explicit OSB => OCB3_EXHAUSTED
- no attempt4
- no unrelated GitHub calls between exact retries
- ambiguous mutable request requires authoritative reconciliation

# PP-RM Launch Package — iOS Research Runtime

Status: PRODUCTION ADMITTED / IOS-M1-R1 READY TO ARM
Manager: `ios-research-runtime-project-manager`
Manager generation: 7 after seal
Product baseline: `main@85d408075ab8a66f6d16043029eb2255956eb1b9`

## Admission result

`IOS-PP-RM-PILOT-001`:
- attempt 1 safely stopped on immediate read-back mismatch; eventual server state matched the write;
- bounded read-only stabilization was added;
- attempt 2 completed A1 -> B2 -> A3 -> FINAL PASS;
- actual attempt-2 GitHub READ events: 4/4 first-attempt success;
- explicit OSB=0, other GitHub errors=0, ambiguous outcomes=0;
- Worker FINAL aggregate undercounted requests, so tagged Trace events are authoritative;
- scheduler delays of minutes were observed without baton corruption.

OCB remains provisional because the pilot did not produce an explicit OSB.

## Stable PP-RM objects

Reuse the existing five native objects:
1. Worker A
2. Worker B
3. Runtime Mailbox
4. Pulse Register
5. Trace Register

Mailbox/Pulse/Trace stay disabled permanently. Workers alternate one-shot A -> B -> A. Never self-rearm.

## Responsibility boundary

Manager owns direction, priorities, decomposition, acceptance criteria, strategy, durable state and high-level checkpoints.

A/B owns only bounded tactical execution inside the active package and PP-RM handoff.

A/B must not mutate `manager-state`, widen package scope, publish releases, or choose a new APFS/AMFI strategy at a Manager checkpoint.

## Production protocol

For every A/B runtime:

1. First protocol operation: fresh-read Mailbox and Trace.
2. Validate work_package, manager_generation, generation, owner, state, message_id, from/to, seq, exact payload hash and prior SEND/ACK requirements.
3. Deduplicate message_id before any product side effect.
4. ACK valid inbound baton.
5. Reconcile current `main` before consequential GitHub writes.
6. Execute exactly one bounded tactical turn.
7. Complete and verify all product/GitHub side effects before handoff.
8. Update Pulse.
9. Publish next Mailbox or high-level checkpoint.
10. Register read-back stabilization: make up to THREE fresh read-only Scheduled Tasks reads. Never repeat the register mutation solely because visibility is stale.
11. Append uniquely tagged Trace evidence.
12. If continuing: LAST TOOL OPERATION is arming exactly one partner one-shot; after arm, ZERO tool calls.
13. If checkpoint: do not arm successor; publish FINAL/CHECKPOINT as terminal protocol write.

## GitHub / OCB policy

For every GitHub request append a uniquely tagged Trace event with:
- work_package;
- generation;
- worker;
- operation_id;
- operation_class READ|WRITE|OTHER;
- attempt number;
- result.

Explicit OSB:
- classify as OCB;
- one exact identical retry is desired, not mandatory;
- if skipped, record reason;
- no automatic third identical request.

Non-OSB timeout/API/network/tool errors are not automatically OCB.

For a mutating request with ambiguous outcome:
- do not blindly replay;
- first reconcile actual GitHub server state when possible;
- preserve idempotency/deduplication;
- if ambiguity remains, return Manager checkpoint.

Authoritative aggregate metrics are computed from tagged Trace events by Manager. Worker-written aggregate counts are advisory only.

## Active production package — IOS-M1-R1

Objective:
Restore the known raw-APFS packaging correction onto the current rolled-back product line and establish the exact current Windows E2E boundary.

Baseline:
`main@85d408075ab8a66f6d16043029eb2255956eb1b9`.

Exact allowed restoration:
- historical `d743b2e728d9cda194c7e76909f76a5f1704194f`: only `tools/ios-ramdisk-tool/main.go`; replace DMG rewrap of rebuilt APFS with exact raw APFS output and associated messages/helper.
- historical `b3befaeb8c0f2635623d3d8a56226199d2d0753e`: only `tools/ios-ramdisk-tool/main_test.go`; add the exact-byte raw APFS regression test.

Execution stages:
1. inspect current target files and exact historical commit diffs/parents;
2. apply only the scoped semantics;
3. run minimum deterministic tests/build for `tools/ios-ramdisk-tool`;
4. if green, run exact Windows E2E;
5. keep collecting tagged OCB/passability telemetry.

High-level checkpoint / stop conditions:
- recovery `launchd` / AMFI boundary reached;
- APFS error 79 persists;
- different unexpected regression;
- package objective complete;
- ambiguous side effect;
- PP-RM invariant failure;
- a broader APFS/AMFI/security-policy decision is required.

At a checkpoint A/B must not choose the next strategic direction.

## Production bootstrap

With all five objects disabled:

1. install production Worker A/B prompts containing exact native task IDs;
2. seed Mailbox with:
   - work_package=IOS-M1-R1
   - manager_generation=7
   - generation=1
   - owner=A
   - state=READY
   - sender=MANAGER
   - seq=0
   - unique bootstrap message_id
   - exact package payload + SHA-256
3. seed Trace `status=RUNNING` and one MANAGER bootstrap SEND record;
4. seed Pulse `phase=PACKAGE_READY`;
5. fresh-read all three registers and verify exact state using read-only stabilization if necessary;
6. arm Worker A only;
7. after Worker A arm, launcher makes no further PP-RM state mutation.

## Stop / restart

Stopping both workers does not prove an already-started runtime is physically dead. Restart only after reconciling Mailbox/Trace/Pulse and ruling out ambiguous predecessor state. Never arm A and B together.

Current next action: seal Manager generation 7, configure the existing A/B pair for production, seed `IOS-M1-R1`, verify, and arm Worker A.

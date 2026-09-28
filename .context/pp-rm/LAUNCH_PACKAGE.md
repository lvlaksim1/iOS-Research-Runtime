# PP-RM Launch Package — iOS Research Runtime

Status: PREPARED / NOT ARMED
Manager: `ios-research-runtime-project-manager`
Manager-state target generation: 5
Initial work package: `IOS-M1-R1`
Product baseline at preparation: `main@85d408075ab8a66f6d16043029eb2255956eb1b9`

This file is a launch recipe, not live PP-RM control state. Live baton/mailbox/pulse/trace state belongs to native Scheduled Tasks.

## 1. Native objects to create

Create exactly five native Scheduled Task objects:

1. `PP-RM iOS Worker A`
2. `PP-RM iOS Worker B`
3. `PP-RM iOS Runtime Mailbox`
4. `PP-RM iOS Pulse`
5. `PP-RM iOS Trace`

Creation rule:
- create each object initially with a far-future one-shot schedule;
- immediately disable it;
- record its immutable task ID;
- patch Worker A/B prompts with all five task IDs;
- registers remain disabled permanently and are used only as server-side persistent state;
- only workers are armed for execution.

Do not create recurring worker schedules. Normal path is one-shot A/B alternation.

## 2. Stable authority model

Persistent commitment owner: `ios-research-runtime-project-manager`.

Manager controls:
- development direction;
- priorities;
- work-package objective and scope;
- strategic decisions;
- high-level checkpoints;
- durable `manager-state`.

A/B controls only:
- tactical execution inside the current work package;
- product/evidence operations explicitly allowed by the package;
- PP-RM handoff protocol.

A/B MUST NOT:
- change milestone or priority;
- widen the work package;
- mutate `manager-state` during ordinary execution;
- publish releases;
- revive legacy `ai-agent-lab` orchestration;
- infer authority from tool access.

## 3. Worker prompt template

Use this template for both workers, substituting:
- `<SELF>` = A or B
- `<PARTNER>` = B or A
- task IDs after creation.

---

You are PP-RM Worker <SELF> for persistent Project Manager `ios-research-runtime-project-manager` in `lvlaksim1/iOS-Research-Runtime`.

You are a disposable execution Runtime, not the Project Manager and not the project commitment owner. Execute only the Manager-issued work package carried in Runtime Mailbox.

Native task IDs:
- self worker: `<SELF_TASK_ID>`
- partner worker: `<PARTNER_TASK_ID>`
- mailbox: `<MAILBOX_TASK_ID>`
- pulse: `<PULSE_TASK_ID>`
- trace: `<TRACE_TASK_ID>`

Mandatory normal-path protocol:

1. FIRST meaningful operation: fresh-read Runtime Mailbox and Trace.
2. Validate exact expected generation, owner=<SELF>, state, message_id, seq, sender/receiver, payload hash, manager_generation, work_package_id, and prior SEND/ACK evidence.
3. If validation fails, write FAIL to Trace and STOP. Do not arm successor.
4. ACK valid inbound message in Trace.
5. Reconcile live product authority `main` before consequential product writes.
6. Execute ONE bounded turn inside the work package. Tactical decisions are allowed only inside its scope.
7. Complete all product/external side effects before publishing handoff.
8. Update Pulse with this generation and `phase=TURN_COMPLETE`.
9. If a high-level checkpoint/stop condition is reached:
   - publish Mailbox state `PAUSED_MANAGER_CHECKPOINT`;
   - include exact evidence, current SHA/run/job/artifact identifiers when applicable, completed work, unresolved point, and stop_reason;
   - exact-read-back the Mailbox;
   - record Trace `FINAL; result=CHECKPOINT`;
   - DO NOT arm successor;
   - STOP.
10. Otherwise publish the next generation to Runtime Mailbox:
   - generation=N+1;
   - owner=<PARTNER>;
   - state=READY;
   - new unique message_id;
   - monotonic seq;
   - exact payload;
   - sha256 of exact payload;
   - ack=NONE.
11. Fresh-read-back Runtime Mailbox. Exact match is mandatory.
12. If read-back mismatches, write FAIL and STOP. Do not arm successor.
13. Record Trace SEND with outbound message_id/seq/hash and next=<PARTNER>.
14. LAST TOOL OPERATION: arm exactly one partner worker as a one-shot task.
15. AFTER ARM SUCCESSOR: NO FURTHER TOOL OPERATIONS.

OCB policy:
- OCB = OSB Control Block: routine insufficiently characterized platform behavior plus its handling model; do not treat it as hostile by default.
- If an expected server response is absent, repeat safe reads/queries as routine.
- Before retrying a mutation, fresh-read authoritative server state when possible and preserve idempotency/deduplication.
- If the mutation outcome is ambiguous and cannot be safely resolved, this is a high-level checkpoint/FAIL-STOP; do not guess.
- OCB alone never changes baton ownership, project authority, or work-package scope.

Manager-return conditions:
- package objective completed;
- launchd/AMFI boundary reached;
- APFS error 79 persists after the known correction;
- unexpected different regression;
- a broader strategy/security/APFS semantic change appears necessary;
- ambiguous side effect;
- PP-RM invariant violation.

User-visible messages, if any, begin with Moscow date/time and identity `PP-RM Worker <SELF>`.

---

## 4. Initial Runtime Mailbox seed

At launch, seed Mailbox before arming any worker:

```text
experiment=IOS-PP-RM
manager_id=ios-research-runtime-project-manager
manager_generation=5
work_package_id=IOS-M1-R1
generation=1
owner=A
state=READY
message_id=ios-m1-r1-bootstrap-001
from=MANAGER
to=A
seq=1
payload=<exact initial work-package payload>
sha256=<sha256 of exact payload>
ack=NONE
```

Initial payload must encode:

```text
objective=Restore the verified raw-APFS packaging correction on the current rolled-back product line and establish the exact new Windows E2E boundary.
product_baseline=main@85d408075ab8a66f6d16043029eb2255956eb1b9
restore_from_commit=d743b2e728d9cda194c7e76909f76a5f1704194f
restore_test_from_commit=b3befaeb8c0f2635623d3d8a56226199d2d0753e
scope=Inspect exact historical diffs; reapply only the raw-APFS product semantics and its regression coverage; run minimum narrow validation; if green run Windows E2E.
forbidden=Do not restore unrelated later commits; do not mutate manager-state; do not publish a release; do not perform broad APFS/security-policy changes.
checkpoint=Return to Manager at launchd/AMFI, persistent APFS error79, unexpected regression, ambiguous side effect, or PP-RM invariant failure.
ocb=Treat OCB as routine; use safe retries/read-back/idempotency.
```

The exact payload string used at launch must be hashed after final serialization; do not copy a placeholder hash.

## 5. Initial Trace seed

Before A is armed:

```text
event=SEND
generation=0
actor=MANAGER
outbound_message_id=ios-m1-r1-bootstrap-001
outbound_seq=1
outbound_sha256=<same exact payload hash>
next=A
manager_generation=5
work_package_id=IOS-M1-R1
```

This MANAGER SEND is the bootstrap exception to ordinary A/B sender identity.

## 6. Initial Pulse seed

```text
experiment=IOS-PP-RM
generation=0
actor=MANAGER
phase=PACKAGE_READY
manager_generation=5
work_package_id=IOS-M1-R1
```

## 7. Arm sequence

Launch sequence is strict:

1. create/register all five task IDs;
2. disable all five;
3. install final Worker A/B prompts with exact IDs;
4. seed Mailbox;
5. fresh-read Mailbox and verify exact content;
6. seed Trace MANAGER SEND;
7. seed Pulse PACKAGE_READY;
8. verify all three register states;
9. arm Worker A only;
10. after Worker A arm, the launcher performs no further PP-RM state mutation.

Do not arm Worker B at bootstrap.

## 8. Manager checkpoint contract

When PP-RM stops at `PAUSED_MANAGER_CHECKPOINT`, Manager must:
1. reinstate/verify its current sealed Context Capsule generation;
2. read the exact PP-RM checkpoint;
3. reconcile the cited `main` SHA and external evidence;
4. decide whether the result confirms, supersedes, or conflicts with current beliefs;
5. persist a new sealed generation if durable meaning changed;
6. issue the next bounded work package;
7. reseed/re-arm PP-RM deliberately.

A/B must not self-author a new strategic package.

## 9. Launch readiness

Manager-side launch readiness requires:
- Manager READY and sealed;
- `main` exact baseline known;
- active work package present;
- PP-RM authority boundary persisted;
- OCB procedure persisted;
- five-object launch recipe available.

All Manager-side conditions above are satisfied by manager-state generation 5. Runtime objects remain intentionally uncreated/unarmed until explicit launch.

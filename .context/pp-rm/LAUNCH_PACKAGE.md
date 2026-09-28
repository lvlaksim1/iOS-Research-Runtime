# PP-RM Launch Package — iOS Research Runtime

Status: PREPARED / NOT ARMED
Manager: `ios-research-runtime-project-manager`
Manager-state target generation: 6
Pilot package: `IOS-PP-RM-PILOT-001`
Queued production package: `IOS-M1-R1`
Product baseline: `main@85d408075ab8a66f6d16043029eb2255956eb1b9`

This is the Manager-side launch recipe. Live Mailbox/Pulse/Trace state belongs to native Scheduled Tasks.

## 1. Slot gate

Before launch:
- list Scheduled Tasks;
- require external enabled tasks <= 3;
- keep one spare active slot for A/B handoff peak.

Expected PP-RM load:
- steady state: 1 active worker;
- handoff peak: max 2 active workers;
- disabled Mailbox/Pulse/Trace: 0 active slots.

## 2. Create exactly five objects

1. `PP-RM Worker A`
2. `PP-RM Worker B`
3. `PP-RM Runtime Mailbox`
4. `PP-RM Pulse Register`
5. `PP-RM Trace Register`

Create all five inert/disabled. Record task IDs. Patch Worker A/B prompts after all IDs are known.

Mailbox, Pulse and Trace remain disabled permanently. Workers use one-shot A -> B -> A alternation. Self-rearm is forbidden.

## 3. Authority boundary

Manager owns:
- direction and priorities;
- decomposition and acceptance criteria;
- package scope;
- strategy;
- high-level checkpoints;
- durable `manager-state`.

A/B owns only bounded tactical execution and PP-RM handoff inside the active package.

A/B must not:
- change milestone or priority;
- widen package scope;
- mutate `manager-state` during ordinary work;
- publish releases;
- revive legacy OTK/shift-worker orchestration.

## 4. Worker protocol

Both workers use the same protocol with mirrored A/B IDs.

1. First protocol operation: fresh-read Mailbox and Trace.
2. Validate generation, owner, message_id, seq, from/to, payload, SHA-256 and prior SEND.
3. On mismatch: one FAIL event, no product work, no successor arm, STOP.
4. ACK valid inbound message.
5. Restore factual checkpoint; reconcile live GitHub state when needed.
6. Execute exactly one bounded turn.
7. Complete all product/GitHub side effects before handoff.
8. Write Pulse `TURN_COMPLETE`.
9. If package checkpoint/stop condition is reached: publish checkpoint/final state, exact read-back, write FINAL/CHECKPOINT, do not arm successor, STOP.
10. Otherwise publish next generation for partner with new message_id/seq/payload/hash and ack=NONE.
11. Fresh-read-back exact Mailbox.
12. On mismatch: FAIL and STOP without successor.
13. Write Trace SEND.
14. LAST TOOL OPERATION: arm exactly one partner one-shot.
15. After successor arm: ZERO tool calls.

## 5. Initial OCB policy

OCB is the working model for an explicit OSB returned on a GitHub tool request.

Initial policy:
- treat OSB as routine platform behavior, not ownership loss or project failure;
- after an explicit OSB, one exact identical retry is DESIRED, not mandatory;
- a retry may be skipped if there is a concrete reason; record the reason;
- when retrying, tool and all request parameters must remain identical;
- no automatic third identical request in the initial policy;
- timeout, HTTP/API error, network/connection failure, tool unavailable and unknown error are not automatically OCB;
- never blindly duplicate an ambiguous mutation; reconcile actual server state first when possible;
- OCB never changes baton ownership, Manager authority or package scope.

The initial OCB policy is experimental. It MUST be reviewed after the pilot.

For every GitHub request record:
- operation_id;
- generation and worker;
- operation class READ|WRITE|OTHER;
- attempt1 result;
- retry decision;
- retry skip reason if any;
- attempt2 result if performed;
- final result;
- server-side/read-back evidence when relevant.

Suggested final-result vocabulary:
`SUCCESS`, `SUCCESS_AFTER_OCB`, `OCB_EXHAUSTED`, `OTHER_ERROR`, `AMBIGUOUS`.

Primary OCB objective:

> Minimize OCB impact on successful Scheduled Task <-> GitHub request throughput while preserving correctness, idempotency and unambiguous side effects.

## 6. Register initialization

Runtime Mailbox, disabled:

```text
PP-RM DATA REGISTER — KEEP DISABLED
schema=1
service=PP-RM
generation=1
owner=A
state=INIT
message_id=NONE
seq=0
ack=NONE
```

Pulse, disabled:

```text
PP-RM DATA REGISTER — KEEP DISABLED
schema=1
service=PP-RM
generation=0
actor=NONE
phase=INIT
```

Trace, disabled:

```text
PP-RM TRACE REGISTER — KEEP DISABLED
schema=1
service=PP-RM
status=INIT
trace_begin
```

Before first arm verify all five objects are disabled.

## 7. Mandatory pilot before production

Do NOT start `IOS-M1-R1` first.

Run `IOS-PP-RM-PILOT-001`:

```text
A1
-> test-001
-> B2 fresh read + validation + ACK
-> test-002
-> A3 fresh read + validation + ACK
-> FINAL
```

Pilot verifies:
- generation/order and A/B owner;
- exact message_id/seq/payload/hash;
- SEND/ACK;
- Pulse;
- exact Mailbox read-back;
- successor arm is last tool operation;
- zero post-arm calls;
- workers disabled after FINAL;
- registers remain disabled;
- slot budget is respected.

### GitHub observation during pilot

Pilot workers must perform bounded, non-destructive GitHub reads from `lvlaksim1/iOS-Research-Runtime` so Scheduler -> GitHub passability is actually measured.

At minimum:
- read live `main`/HEAD;
- fetch one known repository file or commit.

Do not mutate product `main` merely to provoke OCB.

Every GitHub request is recorded with OCB telemetry.

If explicit OSB occurs, one exact identical retry is desired; if skipped, record why.

Pilot FINAL must summarize:
- total GitHub requests;
- first-attempt successes;
- explicit OSB count;
- identical retries attempted;
- retries skipped and reasons;
- SUCCESS_AFTER_OCB;
- OCB_EXHAUSTED;
- non-OSB errors;
- ambiguous outcomes;
- operation classes affected.

## 8. Mandatory Manager checkpoint after pilot

After pilot FINAL, do not automatically continue to product work.

Manager must:
1. verify Mailbox/Pulse/Trace and admission invariants;
2. analyze Scheduler <-> GitHub passability;
3. analyze OCB incidence and retry effectiveness;
4. decide whether the OCB model needs adjustment;
5. persist any durable adjustment before product work;
6. only then authorize `IOS-M1-R1`.

Useful metrics:
- first-attempt success rate;
- OSB incidence;
- recovery rate after desired identical retry;
- OCB exhaustion;
- distribution by request type;
- any evidence that retry conditions/timing/operation sequencing deserve separate experiments.

If pilot data is insufficient, record that explicitly. The model remains provisional.

## 9. Production admission

PP-RM is admitted to product work only when:
- all five objects exist;
- three registers are disabled;
- A/B prompts contain correct IDs;
- slot budget is valid;
- A arms only B and B only A;
- pilot handoff PASS;
- read-back and ACK verified;
- no post-arm tool operation observed;
- Manager completed OCB/passability review.

## 10. Queued production package IOS-M1-R1

After admission:
- baseline: `main@85d408075ab8a66f6d16043029eb2255956eb1b9`;
- inspect exact historical diffs for `d743b2e728d9cda194c7e76909f76a5f1704194f` and `b3befaeb8c0f2635623d3d8a56226199d2d0753e`;
- restore only the raw-APFS correction and its regression coverage;
- run minimum deterministic validation;
- if green, run Windows E2E;
- return HIGH-LEVEL CHECKPOINT at launchd/AMFI, persistent APFS error 79, unexpected regression, ambiguous side effect or PP-RM invariant failure.

Do not independently select the next strategic APFS/AMFI direction at that checkpoint.

Continue OCB telemetry during production to refine the model using representative GitHub operations.

## 11. Launch sequence

After explicit Owner launch command:

1. enforce slot budget;
2. create all five objects disabled;
3. patch exact IDs into A/B prompts;
4. initialize Mailbox/Pulse/Trace;
5. run pilot A1 -> B2 -> A3 -> FINAL;
6. stop;
7. Manager reviews pilot and OCB/passability evidence;
8. adjust policy if needed;
9. only after Manager admission seed and arm `IOS-M1-R1`.

Current runtime status:
- native PP-RM objects: NOT YET CREATED;
- pilot: NOT YET RUN;
- `IOS-M1-R1`: QUEUED / NOT ARMED.

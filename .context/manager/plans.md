# Manager plans

## IOS-M1 production package

New package: `IOS-M1-CONTINUOUS-003`.
Manager generation: 14.
Product authority: `main`.

Current live product:
`main@649a2244f876db34e2032755b189df158667305f`

Current exact evidence:
- Windows Build on current main: SUCCESS.
- Windows End-to-End Boot run `36556048793`: FAILURE after reaching recovery launchd and attempting `/bin/bash`.
- Root-shell blocker: AMFI rejects the ad-hoc-signed `/bin/bash` with unsuitable CT policy / Launch Constraint Violation.
- Ramdisk Tool Windows run `36556048692`: regression-test nil dereference at `main_test.go:81`.

## PP-RM generation 14 topology

Use exactly five Scheduled Tasks:
1. Worker A.
2. Worker B.
3. Runtime Mailbox.
4. Trace.
5. Watchdog.

Worker A/B prompts are immutable base programs during a package. Activation identity exists only in Mailbox.

## Authoritative baton

Every baton MUST include:
- package;
- manager_generation;
- generation;
- owner_slot;
- activation_attempt;
- dispatch_retry;
- activation_token;
- message_id;
- dispatch_baseline_last_run_time;
- payload;
- payload_sha256 or UNAVAILABLE;
- ack;
- progress_seq;
- progress.

Mailbox is the sole authoritative activation state. Worker prompts MUST NOT embed the current activation tuple.

## Dispatch versus runtime failure

Watchdog distinguishes two failure classes using the owner's Scheduled Task `last_run_time` relative to `dispatch_baseline_last_run_time`.

1. `last_run_time == baseline`: the scheduled activation did not start. This is DISPATCH_FAILURE.
   - do not consume activation_attempt;
   - increment dispatch_retry;
   - retry dispatch of the same owner/token;
   - after two consecutive dispatch failures for one slot, rotate token and fail over to the partner slot on the SAME generation.

2. `last_run_time > baseline` but no durable ACK: a runtime actually started and died before ACK. This is RUNTIME_FAILURE.
   - increment activation_attempt;
   - rotate activation_token and message_id;
   - either retry the same slot or fail over to the partner;
   - maximum three CONFIRMED runtime failures for one generation.

Scheduler delivery retries and runtime attempts are separate counters.

## Fencing

A worker starts by fresh-reading Mailbox. If owner_slot does not equal its slot, it exits with no mutation.

After accepting the baton, it memorizes `generation + activation_attempt + activation_token + message_id` and ACKs durably.

Immediately before every consequential GitHub mutation and immediately before outbound baton publication it fresh-reads Mailbox and requires the same tuple. Token/generation/owner mismatch means STALE and the runtime stops.

## Progress and ambiguous mutation

Worker increments progress_seq after material phases using compact durable states such as STARTED, EVIDENCE_READ, PRE_MUTATION, MUTATION_RESOLVED and HANDOFF_READY.

If Watchdog sees ACK but no progress across two checks, it may recover only after reading the current progress state.
If progress is PRE_MUTATION or a mutation may be in flight/ambiguous, Watchdog MUST reconcile authoritative GitHub state before any replay. No blind duplicate mutation.

## Handoff ordering

Sender:
1. finish and reconcile side effects;
2. write next-generation Mailbox baton with the partner as preferred owner_slot and its current last_run_time as dispatch baseline;
3. stabilize Mailbox;
4. append Trace SEND;
5. arm Watchdog for that exact baton;
6. LAST tool operation: arm the preferred worker.

If worker dispatch never starts, the already-armed Watchdog detects it independently.

## GitHub publication / OCB

Preferred narrow publication remains:
`fresh-read main -> create_blob -> create_tree -> create_commit -> fresh-read main -> update_ref(force=false) -> authoritative read-back`.

OCB unchanged: explicit OSB only; maximum three exact-identical attempts for the same GitHub request; no fourth; ambiguous mutation requires authoritative reconciliation.

## Continuous objective

Continue without artificial stops:
1. repair the ramdisk regression-test nil dereference narrowly;
2. continue evidence-backed diagnosis/fix for AMFI / launch constraints;
3. rerun exact-SHA CI;
4. continue until verified recovery launchd + verified root shell or a genuine mandate/safety/ambiguity stop.

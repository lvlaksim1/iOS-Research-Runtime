# Manager plans

## IOS-M1 production package

New package: `IOS-M1-CONTINUOUS-004`.
Manager generation: 15.
Product authority: `main`.

Current live product:
`main@eaa98114031a37343e0d5184bd132830818a6b2f`

Current exact evidence:
- Ramdisk Tool Windows on `eaa98114...`: SUCCESS.
- Windows Build on `eaa98114...`: SUCCESS.
- Windows End-to-End Boot run `36589206204`: FAILURE.
- Primary product investigation remains AMFI / CT launch-constraint rejection of recovery `/bin/bash`.
- Generation 19 established that the source APFS recovery tree is available pre-merge and a narrow executable/signature inventory diagnostic is justified.

## PP-RM generation 15 topology

Use exactly five Scheduled Tasks:
1. Worker A.
2. Worker B.
3. Runtime Mailbox.
4. Trace.
5. Watchdog.

Worker A/B prompts are immutable during the package.
Watchdog prompt is also immutable during the package.
Mailbox is the sole activation and watch-state authority.

## Watchdog liveness root

Every Watchdog invocation MUST perform this as its FIRST tool operation:
- re-arm the same Watchdog task for exactly +5 minutes;
- preserve the exact title and immutable prompt.

No read or other operation may precede this early self-rearm.

The 5-minute Watchdog cadence is fixed and non-adaptive.

All watched generation/token/message/progress state is stored in Mailbox. Watchdog never embeds a mutable WATCH tuple in its prompt.

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
- progress;
- watch_seq;
- watch_seen_generation;
- watch_seen_activation_attempt;
- watch_seen_activation_token;
- watch_seen_message_id;
- watch_seen_owner_slot;
- watch_seen_progress_seq;
- watch_stall_checks;
- watch_last_ok.

## Dispatch versus runtime failure

Watchdog compares owner's live `last_run_time` with `dispatch_baseline_last_run_time`.

- Equal baseline + no ACK => DISPATCH_FAILURE. Do not consume activation_attempt.
- Repeated dispatch failure on one slot => rotate token and fail over same generation to partner.
- Advanced last_run_time + no ACK => confirmed RUNTIME_FAILURE. Consume activation_attempt and fail over safely.
- ACKed runtime with no progress across two Watchdog observations => confirmed RUNTIME_STALL, subject to ambiguous-mutation reconciliation.
- Maximum three confirmed runtime failures/stalls per generation.

## Fencing

Worker accepts only a Mailbox baton assigned to its slot and memorizes generation + activation_attempt + activation_token + message_id.

Immediately before every consequential GitHub mutation and before outbound baton publication, worker fresh-reads Mailbox and requires exact tuple + owner match.

Mismatch means STALE and the runtime stops without further product mutation.

## Handoff

Sender:
1. finish and reconcile side effects;
2. write next-generation Mailbox baton with partner owner and current partner last_run_time baseline;
3. reset watch state for the new baton;
4. stabilize Mailbox;
5. append Trace SEND;
6. if Watchdog is unexpectedly disabled while package is RUNNING, re-arm the unchanged Watchdog +5 minutes;
7. LAST tool operation: arm successor worker at the fixed short handoff delay.

Workers never rewrite Watchdog prompt.

## Watchdog terminal cleanup

Watchdog pre-arms itself first. If it later reaches FINAL or FAIL_STOP:
1. publish terminal Mailbox/Trace durably;
2. FINAL scheduler operation: disable the already pre-armed Watchdog.

If cleanup is lost, the next invocation reads terminal state and disables itself.

## GitHub publication / OCB

Preferred narrow publication:
`fresh-read main -> create_blob -> create_tree -> create_commit -> fresh-read main -> update_ref(force=false) -> authoritative read-back`.

OCB unchanged: explicit OSB only; maximum three exact-identical attempts; no fourth; ambiguous mutation requires authoritative reconciliation.

## Continuous objective

Continue without artificial stops:
1. add the narrow source-recovery executable/signature inventory diagnostic justified by generation 19;
2. publish with fencing;
3. run exact-SHA CI;
4. continue evidence-backed AMFI / CT / launch-constraint work;
5. continue until verified recovery launchd + verified root shell or a genuine mandate/safety/ambiguity stop.

# DEC-0012 — Immutable early-rearm Watchdog

Date: 2026-09-29
Status: ACCEPTED
Authority: direct Owner instruction after review of IOS-M1-CONTINUOUS-003 continuity loss and isolated scheduler regression test

## Evidence

Package `IOS-M1-CONTINUOUS-003` reached generation 19 and then lost continuity.

Worker A had already ACKed and reached `progress_seq=2 / EVIDENCE_READ`. No product mutation had begun. The Watchdog task later showed an advanced `last_run_time`, proving a Watchdog runtime was invoked, but no recovery event, FAIL_STOP, handoff, or durable self-rearm followed. Worker A, Worker B and Watchdog ended disabled.

Therefore generation 14 removed the Worker A/B single point of failure but left the single mutable self-rearming Watchdog as a liveness single point of failure.

Isolated experiment `PP-RM-G15-EARLY-REARM-R2` tested the proposed semantic directly:
- every invocation first re-armed the same immutable task;
- RUN1 then continued work and stopped while State remained RUN1_ACTIVE;
- the pre-armed successor still started;
- Result recorded `PASS; successor=STARTED_WITH_RUN1_ACTIVE; early_self_rearm=SURVIVED_PRIOR_RUNTIME`.

This proves that an early self-rearm can survive loss of the current runtime.

## Decision

Manager generation 15 uses an immutable Watchdog program.

The Watchdog's FIRST tool operation on every invocation MUST be to re-arm the same Watchdog task for exactly +5 minutes, preserving title and prompt.

No read, Mailbox inspection, GitHub call, Trace mutation or recovery action may occur before this first self-rearm.

All current watch identity/state moves to Mailbox. The Watchdog prompt contains no mutable generation/token/message tuple.

Workers MUST NOT rewrite the Watchdog prompt.

The fixed Watchdog self-rearm interval is 5 minutes. It is not adaptive.

## Mailbox watch state

Mailbox carries:
- watch_seq;
- watch_seen_generation;
- watch_seen_activation_attempt;
- watch_seen_activation_token;
- watch_seen_message_id;
- watch_seen_owner_slot;
- watch_seen_progress_seq;
- watch_stall_checks;
- watch_last_ok.

The Watchdog always reads the current authoritative Mailbox after early self-rearm and evaluates that current baton.

## Recovery

Generation-14 recovery semantics remain:
- unchanged worker last_run_time from dispatch baseline => DISPATCH_FAILURE; does not consume activation_attempt;
- advanced last_run_time with no ACK => confirmed RUNTIME_FAILURE; consumes activation_attempt;
- ACKed runtime with no progress across two Watchdog observations => confirmed runtime stall;
- repeated scheduler non-delivery on one slot => same-generation failover to partner with token rotation;
- maximum three confirmed runtime failures/stalls per generation;
- ambiguous GitHub ref mutation requires authoritative reconciliation before replay.

## Handoff

Workers write and stabilize the next Mailbox baton, append Trace SEND, then arm the successor worker as their final tool operation.

Workers do not normally schedule or rewrite Watchdog. At handoff they may restore Watchdog liveness only if they observe it unexpectedly disabled while Mailbox state is RUNNING/READY; recovery is by re-arming the unchanged Watchdog prompt, never by rewriting it.

## Finalization

Because every Watchdog invocation pre-arms its successor first, FINAL or FAIL_STOP requires:
1. durable final Mailbox/Trace publication;
2. explicit disabling of the already pre-armed Watchdog as the final scheduler cleanup action.

If that cleanup fails, the next Watchdog invocation reads the durable terminal state and disables itself without product mutation.

## OCB

OCB policy is unchanged: explicit OSB only; maximum three exact-identical GitHub requests; no attempt 4; mandatory authoritative reconciliation for ambiguous mutation.

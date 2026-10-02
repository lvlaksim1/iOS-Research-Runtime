# DEC-0020 — Durable Finding Gate for Manager persistence

Date: 2026-10-03
Status: ACCEPTED
Authority: direct Owner instruction
Manager generation: 25

## Problem
The existing v2 Manager Protocol already requires `Reflect → Persist`, durable-memory admission, and semantic write-back without waiting for an Owner save request. However, those rules left too much discretion around *when* a newly verified operational finding becomes mandatory durable state.

The failure mode was demonstrated during PP-RM publication recovery: a verified, reusable `update_file` fallback was recorded in runtime Mailbox/Trace but was not initially promoted into the Manager capsule. The finding would have materially changed a future Manager's behavior, yet it could have been lost across runtime/generation replacement.

## Decision
Introduce a project-local **Durable Finding Gate** immediately.

After Verify/Reflect, before substantial work can cross a runtime/generation boundary, the Manager asks:

> Would this verified finding materially change a reasonable future Manager's next action, or prevent repetition of a problem already solved?

If yes, it MUST be represented in durable manager state before relying on runtime continuity.

Mandatory candidate classes:
1. verified reusable workaround or alternate execution path;
2. new or corrected invariant, constraint, safety/authority interpretation, or failure classification;
3. evidence interpretation that changes the likely next action;
4. repeated incident with a verified resolution likely to recur;
5. durable correction to a previously incomplete/false Manager belief or procedure.

Routing:
- architecture/policy choice -> `.context/decisions/`;
- reusable procedure/workaround -> procedural memory;
- durable project fact -> beliefs/semantic memory;
- active strategy change -> plans/current views;
- significant historical context -> episodic memory.

Runtime Mailbox, Trace, logs and chat are evidence sources only; they do not satisfy the durable-memory requirement.

## Non-goals
This does not require write-back for every observation or confirming CI result. Transient telemetry, raw logs, secrets, hidden reasoning, and details that would not alter future action remain excluded unless another rule requires them.

## Consequence
High-level checkpoints remain mandatory consolidation points, but they are no longer the only persistence points. A verified durable finding is persisted promptly once it becomes actionable/reusable.

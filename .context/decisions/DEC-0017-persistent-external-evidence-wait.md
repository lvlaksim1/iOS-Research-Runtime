# DEC-0017 — Persistent external-evidence wait

Date: 2026-10-01
Status: ACCEPTED
Authority: direct Owner instruction
Manager generation: 19
Package: `IOS-M1-CONTINUOUS-008`

## Problem
Package007 generation78 performed one result-first search for an exact-SHA Windows E2E run. No run was observable at that instant. Because the connector had no start-new-workflow capability, PP-RM terminalized as OWNER_GATE.

The exact-SHA run later appeared automatically through push and produced usable failure evidence. No Owner action had actually been required.

The defect was treating temporary absence/visibility lag of external evidence as a terminal authority problem.

## Decision
Add nonterminal `WAIT_EXTERNAL_EVIDENCE`.

A Worker requiring external workflow evidence:
- consumes an already-terminal exact-SHA run immediately;
- enters WAIT when the run is queued/in_progress;
- also enters WAIT when no exact-SHA run is yet observable;
- arms no Worker while WAIT;
- leaves recurring Watchdog enabled.

Watchdog owns independent later observations.
When a terminal exact-SHA run appears, Watchdog creates a fresh READY generation and arms the designated resume Worker.

OWNER_GATE for unavailable start-new-workflow is permitted only when all are true:
1. at least 3 independent Watchdog observations found no exact-SHA run;
2. at least 15 minutes elapsed since wait_started_at;
3. no qualifying run is queued, in-progress or terminal;
4. a new run is genuinely required;
5. no authorized capability can produce it.

Any terminal workflow conclusion is evidence for analysis; workflow failure is not itself an Owner gate.

## Consequences
- no sixth task or extra slot;
- no change to generation16 mutation semantics;
- no change to generation17 recurring Watchdog;
- generation18 result-first search remains mandatory;
- package007 remains terminal and is not resumed;
- package008 starts clean from current main and existing E2E evidence.

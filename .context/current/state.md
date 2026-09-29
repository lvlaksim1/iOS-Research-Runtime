# Current state

## Governance
- manager: `ios-research-runtime-project-manager`
- manager generation: 15
- product authority: `main`
- execution package: `IOS-M1-CONTINUOUS-004`
- execution mode: continuous PP-RM with immutable early-rearm Watchdog

## Product
- live main: `eaa98114031a37343e0d5184bd132830818a6b2f`
- Ramdisk Tool Windows exact-SHA regression: SUCCESS
- Windows Build exact-SHA: SUCCESS
- Windows End-to-End Boot run `36589206204`: FAILURE
- primary root-shell investigation: AMFI / CT launch-constraint rejection of recovery `/bin/bash`
- generation-19 evidence: source APFS recovery tree is available pre-merge, so a narrow source executable/signature inventory diagnostic is justified
- no ambiguous product mutation was in flight when package 003 stopped

## PP-RM generation 14 result
Package `IOS-M1-CONTINUOUS-003` advanced through generation 19 and proved dispatch-aware A/B recovery.

It also exposed a remaining liveness defect: Watchdog itself was a single mutable self-rearming task. A Watchdog runtime was invoked after generation 19 stalled, but published no recovery/self-rearm and all PP-RM actors ended disabled.

## PP-RM generation 15 construction
Topology remains A + B + Mailbox + Trace + Watchdog.

A/B prompts remain immutable.
Watchdog prompt is now immutable.
Mailbox is the sole activation and Watchdog-state authority.

Every Watchdog invocation MUST first re-arm itself for +5 minutes before any read or recovery work.

Isolated regression experiment `PP-RM-G15-EARLY-REARM-R2` passed the critical case: RUN1 stopped while still RUN1_ACTIVE, but the successor created by the early self-rearm still started and recorded PASS.

Workers no longer rewrite Watchdog prompt. They may only re-arm the unchanged Watchdog if they observe it unexpectedly disabled while package state remains RUNNING.

## OCB
Unchanged: explicit OSB only; max three exact-identical GitHub requests; no automatic fourth request; authoritative reconciliation required for ambiguous mutation.

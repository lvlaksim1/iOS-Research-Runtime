# DEC-0007 — Continuous PP-RM production mode

Date: 2026-09-29
Status: ACCEPTED
Authority: direct Owner directive

## Decision
Run PP-RM in real production conditions without artificial stage checkpoints.

One Manager package may continue across an unbounded number of alternating fresh A/B runtimes. Each individual runtime remains bounded and must complete the PP-RM handoff protocol.

Intermediate CI failures, missing artifacts, diagnosable infrastructure defects, and tactical product regressions are not automatic Manager stops.

## OCB
Keep the current parameters unchanged:
- explicit OSB only;
- up to three exact-identical attempts total;
- no fourth automatic request;
- authoritative state reconciliation after mutation attempts;
- no blind replay under ambiguity.

## Genuine stop conditions
Stop only for objective completion, authority/scope escalation, unresolved ambiguous mutation, irrecoverable PP-RM protocol failure, or a strategic fork requiring Manager/Owner judgment.

## Scope
Current continuous package is `IOS-M1-CONTINUOUS-001`, starting from `main@cbba4060db543d4a2b800f7c15b2a700e69f6961` and the missing `qemu-sptm-windows-gate` E2E blocker.

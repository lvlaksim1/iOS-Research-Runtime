# DEC-0004 — Pilot-first PP-RM admission and empirical OCB refinement

Date: 2026-09-28
Status: ACCEPTED
Authority: direct Owner correction plus Owner-provided PP-RM specification

## Decision

Before iOS product development, PP-RM runs a bounded admission pilot using A1 -> B2 -> A3 -> FINAL. The pilot validates protocol invariants and gathers real Scheduled Task -> GitHub request evidence. After FINAL, the loop stops and returns to the Project Manager.

`IOS-M1-R1` remains queued until Manager production admission.

## OCB refinement

The initial OCB policy is provisional.

For explicit OSB on a GitHub request, one exact identical retry is desired, not mandatory. If skipped, record why. No automatic third identical request belongs to the initial policy.

Non-OSB failures are not automatically OCB. Ambiguous mutations are not blindly repeated.

## Optimization objective

After pilot, Manager analyzes evidence and may revise OCB handling.

Primary objective: minimize OCB practical impact on successful Scheduled Task <-> GitHub request throughput while preserving protocol correctness, idempotency and unambiguous side effects.

If pilot evidence is insufficient, record that and keep the model provisional.

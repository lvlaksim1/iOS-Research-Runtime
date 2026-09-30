# DEC-0014 — Native two-phase mutation fence

Date: 2026-09-30
Status: ACCEPTED
Authority: direct Owner instruction
Manager generation: 16

## Problem
PP-RM generation 15 required a fresh second Scheduled Tasks read immediately before consequential GitHub mutation.
In package `IOS-M1-CONTINUOUS-004`, Scheduled Runtime repeatedly could not satisfy this requirement after its initial task-state read.
Workers therefore stopped safely at evidence/preparation, Watchdog classified repeated stalls, and generation 46 exhausted three activation attempts and entered durable FAIL_STOP.

The Owner rejected an additional GitHub lock/fence request because it would create another GitHub operation with OCB exposure.

## Decision
Adopt a native two-phase mutation protocol.

### PREPARE phase
A runtime accepting ordinary READY work uses its first Scheduled Tasks read to validate ownership, may research and create immutable Git objects, MUST NOT change a mutable product ref, freezes a mutation descriptor when a target commit is ready, and hands it to a fresh successor runtime as MUTATION_READY.

### MUTATION phase
The fresh successor runtime uses its FIRST Scheduled Tasks read as the mutation ownership fence, may publish only the exact frozen target commit, performs no second Scheduled Tasks read before publication, and reconciles authoritative main before and after publication.

Frozen descriptor:
- mutation_id
- mutation_operation
- mutation_baseline_main_sha
- mutation_target_commit
- mutation_force=false

### Recovery
Recovery may rotate activation token/message/owner but MUST preserve the frozen mutation descriptor.
All legal executors for the mutation therefore converge on one target SHA.

Reconciliation:
- main == target => publication succeeded/already completed
- main == baseline => frozen mutation may be attempted/re-attempted
- main neither baseline nor target => FAIL_STOP

## Consequences
- No GitHub lock/fence ref.
- No extra GitHub request solely for fencing.
- Normal mutation path no longer depends on a second Scheduled Tasks read.
- Immutable object creation before publication remains safe because orphan objects do not move product refs.
- Watchdog, dispatch/runtime separation, fixed cadence and OCB3 remain.
- Package 004 remains terminal and is never resumed.
- Clean package 005 is authorized under generation 16.

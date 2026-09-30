# PP-RM Launch Package — generation 16

Status: OWNER-AUTHORIZED — CONFIGURE AND ARM
Manager generation: 16
Package: `IOS-M1-CONTINUOUS-005`
Product start: `main@95e871e84099f10245e912659b2d964c1b3c1037`

## Owner authority
Direct Owner instruction: adopt the native two-phase mutation mechanism, update durable capsule, and launch the work cycle.

## Mission
Continue IOS-M1 from the current authoritative main.
First bounded unit:
implement the post-merge `/bin/bash` Mach-O/size/primary-CDHash/injected-trust-membership diagnostic immediately after `mergeSysrootTarWithSigner`, add a pure formatting test, prepare a target commit, publish through the generation-16 two-phase mutation protocol, then run exact-SHA CI.

## Continuity objects
A=`6abac75982308191b786450088217776`
B=`6abac76297c8819182c048fcbc619ef0`
Mailbox=`6abac714ddb481919ab9cb13afc4f8f8`
Watchdog=`6abac73339dc8191ba6bf26104fc2aa9`
Trace=`6abac750fee081918af4522336615f29`

## Generation-16 mutation protocol
PREPARE runtime: one initial Scheduled Tasks read; immutable Git objects allowed; mutable product refs forbidden; freeze descriptor; hand off MUTATION_READY.
MUTATION_READY runtime: first Scheduled Tasks read is native ownership fence; descriptor immutable; reconcile live main; publish only frozen target with force=false; authoritative read-back.
No second Scheduled Tasks read before update_ref.
No GitHub lock/fence ref.
No extra GitHub request solely for fencing.

## Watchdog
Immutable prompt.
FIRST operation every invocation: self-rearm same task +5 minutes.
Dispatch/runtime separation and same-generation recovery remain active.
Mutation recovery MUST preserve the frozen descriptor exactly.

## OCB
Explicit OSB only; maximum 3 exact-identical attempts; no attempt 4; reconcile ambiguous mutable side effects.

## Launch ordering
1. Configure A/B/Watchdog prompts for generation 16/package 005 while disabled.
2. Seed Mailbox and Trace disabled.
3. Arm Watchdog.
4. Final launch operation: arm initial Worker B.

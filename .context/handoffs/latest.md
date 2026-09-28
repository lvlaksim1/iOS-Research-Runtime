# Latest handoff

Persistent manager: `ios-research-runtime-project-manager`.
Manager-state authority: `manager-state`.
Product authority: `main`.

## Recovery / readiness

The manager was recovered on 2026-09-28 from sealed generation 3 at `bba84db4666f819af9f5f69dc4facdf78b48bf1a`. Core-managed recovery files match Context Capsule Core `3a942bd269ec7ee164575589e702e5074da30a29`.

Generation 5 reconciles the Manager to the rolled-back product line, adopts PP-RM, and adds the exact Manager-side PP-RM launch recipe.

Canonical launch recipe: `.context/pp-rm/LAUNCH_PACKAGE.md`.

## Current product authority

Live `main`: `85d408075ab8a66f6d16043029eb2255956eb1b9`.

Its product code is equivalent to `3b0f5648f004f58daef526082b3d2a32d132edcf`; only Context Capsule discovery files were added.

Conservative current runtime boundary: exact E2E `35634992757` at `3b0f564...` reached `BSD root: md0` and failed APFS root mount with error 79.

Historical later evidence retained for controlled recovery:
- `d743b2e...`: raw-APFS output correction;
- `b3befaeb...`: regression test;
- `669f2b...`: reached recovery `launchd`, then failed root-shell proof on AMFI/launch constraints.

## PP-RM authority model

Manager retains project responsibility, priorities, strategy, work-package definition, high-level checkpoints, and durable Context Capsule state.

A/B runtimes execute only the current bounded package using Runtime Mailbox + ACK, Pulse, Trace, exact read-back, and successor-arm-last. They do not mutate `manager-state` during ordinary execution.

OCB is routine system behavior plus its handling model; safe retries are expected for missing server responses, with read-back/idempotency before repeating side-effecting operations.

## First PP-RM package

`IOS-M1-R1`: restore only the known raw-APFS packaging change from `d743b2e...` and its regression test from `b3befaeb...`, validate narrowly, then run exact Windows E2E. Return to Manager at launchd/AMFI, persistent APFS error 79, unexpected regression, ambiguous side effect, or PP-RM invariant failure.

Launch recipe specifies exact five-object creation order, worker prompt template, bootstrap Mailbox/Trace/Pulse state, and arm sequence.

PP-RM is PREPARED, NOT YET ARMED.

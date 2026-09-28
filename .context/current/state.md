# Current state

## Governance topology

- persistent manager: `ios-research-runtime-project-manager`;
- manager-state authority: `manager-state`;
- product authority: `main`;
- discovery branch: `main`;
- Context Capsule Core: `3a942bd269ec7ee164575589e702e5074da30a29`;
- manager-state coherence protection: enabled and sealed;
- PP-RM: approved execution Runtime mechanism, prepared but not yet armed.

## Manager readiness

Manager identity, mandate, BDI state, Core provenance, and sealed-state integrity are READY.

PP-RM responsibility boundary:
- Manager: development direction, priorities, strategy, work packages, high-level checkpoints, durable project state.
- A/B: continuous bounded execution, evidence production, Mailbox/Pulse/Trace handoff.
- A/B do not own the project commitment and do not mutate `manager-state` during ordinary execution.

## Product reconciliation

Current live product: `main@85d408075ab8a66f6d16043029eb2255956eb1b9`.

Live compare proves this commit is the old product baseline `3b0f5648f004f58daef526082b3d2a32d132edcf` plus three discovery-only files. Product code is therefore on the old pre-raw-APFS line.

Conservative current technical boundary:
- exact E2E `35634992757` at `3b0f564...`: failure;
- runtime reached `BSD root: md0`;
- APFS root mounting failed with error 79.

Historical verified later progress is retained as evidence but is not current state:
- `d743b2e...` raw-APFS output correction;
- `b3befaeb...` regression test;
- `669f2b...` later reached recovery `launchd`, then failed root-shell proof due AMFI/launch constraints for `/bin/bash`.

## Active commitments

- `IOS-M1`: active — recovery launchd + verified root shell.
- `IOS-PP-RM-001`: active — run development through PP-RM A/B under Manager authority.

## Initial execution package

`IOS-M1-R1` is prepared. It restores only the known raw-APFS packaging correction/test, validates the exact current product line, and returns to Manager at the first high-level checkpoint.

PP-RM launch is the next runtime action; it has not been armed by this manager-state Persist.

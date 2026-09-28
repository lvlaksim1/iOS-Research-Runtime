# Current state

## Governance topology
- persistent manager: `ios-research-runtime-project-manager`;
- manager-state authority: `manager-state`;
- product authority: `main`;
- Context Capsule Core: `3a942bd269ec7ee164575589e702e5074da30a29`;
- PP-RM: approved execution Runtime; pilot-first launch package prepared;
- native PP-RM objects: not yet created or armed.

## Responsibility boundary
- Manager: direction, priorities, decomposition, acceptance criteria, strategy, packages, high-level checkpoints, durable state.
- A/B: bounded execution, evidence and handoff only.
- A/B do not own commitments and do not ordinarily mutate `manager-state`.

Canonical launch recipe: `.context/pp-rm/LAUNCH_PACKAGE.md`.

## Product
Live product: `main@85d408075ab8a66f6d16043029eb2255956eb1b9`, code-equivalent to `3b0f564...` plus discovery metadata.

Conservative boundary: exact E2E `35634992757` reached `BSD root: md0` and failed APFS root mount with error 79.

Historical restoration evidence remains `d743b2e...`, `b3befaeb...`, and later `669f2b...` launchd/AMFI evidence.

## Launch stage
First live package is `IOS-PP-RM-PILOT-001`, not `IOS-M1-R1`.

Pilot purpose:
- prove PP-RM admission invariants;
- observe Scheduled Task -> GitHub passability;
- collect OCB telemetry;
- return to Manager for mandatory analysis.

Initial OCB policy is provisional: after explicit OSB, one exact identical retry is desired, not mandatory.

`IOS-M1-R1` is QUEUED / NOT ARMED pending Manager pilot review and production admission.

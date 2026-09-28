# Latest handoff

Persistent manager: `ios-research-runtime-project-manager`.
Manager-state authority: `manager-state`.
Product authority: `main`.

## Readiness
Generation 6 corrects the PP-RM launch package to pilot-first admission plus the Owner's OCB refinement.

Canonical launch recipe: `.context/pp-rm/LAUNCH_PACKAGE.md`.

PP-RM remains PREPARED / NOT ARMED.

## Product
Live `main`: `85d408075ab8a66f6d16043029eb2255956eb1b9`, code-equivalent to `3b0f564...` plus discovery metadata.
Conservative boundary: E2E `35634992757` failed APFS root mount with error 79.
Historical controlled-restoration evidence: `d743b2e...`, `b3befaeb...`, and later `669f2b...` launchd/AMFI result.

## Launch order
1. enforce slot budget;
2. create five objects disabled;
3. install exact A/B IDs/prompts;
4. run `IOS-PP-RM-PILOT-001`, A1 -> B2 -> A3 -> FINAL;
5. collect GitHub request/OCB telemetry;
6. stop for Manager review;
7. refine OCB policy if evidence supports it;
8. only then admit `IOS-M1-R1`.

## OCB correction
- explicit OSB is handled as OCB;
- one exact identical retry is desired, not mandatory;
- retry skip requires a reason;
- non-OSB errors are not automatically OCB;
- ambiguous mutations are not blindly repeated;
- Manager analyzes pilot results with the primary goal of reducing OCB impact on Scheduler <-> GitHub throughput while preserving correctness.

`IOS-M1-R1` remains QUEUED / NOT ARMED.

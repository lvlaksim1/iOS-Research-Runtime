# Manager plans

## Current authority
- product: `main@85d408075ab8a66f6d16043029eb2255956eb1b9`
- Manager: `manager-state`
- canonical PP-RM launch recipe: `.context/pp-rm/LAUNCH_PACKAGE.md`

## PP-RM launch and admission
1. Enforce slot budget: external active Scheduled Tasks <= 3.
2. Create five canonical PP-RM objects disabled.
3. Patch exact IDs into Worker A/B.
4. Run `IOS-PP-RM-PILOT-001`, not product work.
5. Pilot executes A1 -> B2 -> A3 -> FINAL and proves read-back/ACK/Pulse/Trace/successor-arm-last.
6. Pilot also performs bounded read-only GitHub requests and records OCB telemetry.
7. Stop after pilot FINAL.
8. Manager analyzes first-attempt success, explicit OSB incidence, desired identical-retry recovery, exhaustion, non-OSB errors and ambiguity.
9. If evidence justifies a change, revise OCB policy and seal a new generation.
10. Only after Manager production admission seed `IOS-M1-R1`.

## Initial OCB policy
- explicit OSB -> OCB event;
- one exact identical retry is desired, not mandatory;
- retry skip requires a reason;
- no automatic third identical request;
- non-OSB errors are not automatically OCB;
- ambiguous mutations are not blindly duplicated;
- OCB never changes baton ownership or authority;
- policy is provisional and empirically reviewed after pilot.

Optimization target: maximize successful Scheduled Task <-> GitHub request throughput by reducing practical OCB impact while preserving correctness.

## Queued IOS-M1-R1
After admission:
1. inspect exact diffs of `d743b2e...` and `b3befaeb...`;
2. restore only raw-APFS correction plus regression coverage;
3. run minimum deterministic validation;
4. if green, run Windows E2E;
5. return HIGH-LEVEL CHECKPOINT at launchd/AMFI, persistent APFS error 79, unexpected regression, ambiguous side effect or PP-RM invariant failure.

## Coherence
Every replacement Manager runtime must verify sealed manager state before consequential continuation. PP-RM operational state does not replace Context Capsule persistence.

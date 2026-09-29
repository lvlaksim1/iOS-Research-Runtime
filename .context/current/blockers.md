# Current blockers and open risks

## Product blocker
The current E2E reaches recovery launchd and attempts `/bin/bash`, but AMFI rejects execution:
- ad-hoc signed binary;
- unsuitable CT policy for platform/device;
- code signature validation failed;
- Launch Constraint Violation.

This is now the primary IOS-M1 product blocker.

## Test blocker
`Ramdisk Tool Windows` fails due a regression-test nil dereference at `tools/ios-ramdisk-tool/main_test.go:81`.
Repair narrowly before relying on that regression suite as green evidence.

## Continuity blocker addressed by generation 13
The prior PP-RM had no independent observer for a runtime that was scheduled and started but died before ACK.
Generation 13 introduces Watchdog plus fencing tokens.

## Remaining continuity limitation
Fencing cannot revoke an already in-flight external request. Therefore:
- workers revalidate token immediately before consequential mutation;
- Watchdog uses a grace/progress protocol instead of instant takeover after ACK;
- GitHub publication remains non-force and parent/reconciliation guarded.

## Genuine stop conditions
- IOS-M1 achieved;
- required action exceeds Manager mandate or needs Owner approval;
- unresolved ambiguous side effect;
- Watchdog exhausts attempt 3 for one generation;
- true strategic fork outside tactical IOS-M1 execution.

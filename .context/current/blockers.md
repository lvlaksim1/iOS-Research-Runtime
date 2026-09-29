# Current blockers and open risks

## Product blocker
The current E2E reaches recovery launchd and attempts `/bin/bash`, but AMFI rejects execution:
- ad-hoc signed binary;
- unsuitable CT policy for platform/device;
- code signature validation failed;
- Launch Constraint Violation.

This is the primary IOS-M1 product blocker.

## Test blocker
`Ramdisk Tool Windows` fails due a regression-test nil dereference at `tools/ios-ramdisk-tool/main_test.go:81`.
Repair narrowly before relying on that regression suite as green evidence.

## Continuity defect corrected by generation 14
Generation 13 Watchdog could detect a missing ACK, but it conflated scheduler non-delivery with a runtime that actually started and died.
Observed evidence: Worker A last_run_time did not advance for recovery attempts 2 and 3.

Generation 14 records dispatch_baseline_last_run_time and keeps separate dispatch_retry and activation_attempt counters.
Repeated non-delivery on one slot causes same-generation failover to the partner slot instead of consuming runtime attempts.

## Remaining continuity limitations
- fencing cannot cancel an external request already in flight;
- Watchdog must reconcile ambiguous GitHub mutation state before replay;
- Scheduled Task delivery itself is not guaranteed, so A/B are treated as interchangeable executor slots.

## Genuine stop conditions
- IOS-M1 achieved;
- required action exceeds Manager mandate or needs Owner approval;
- unresolved ambiguous side effect;
- three confirmed runtime failures for one generation after safe recovery/failover;
- both executor slots repeatedly cannot be dispatched after bounded retries;
- true strategic fork outside tactical IOS-M1 execution.

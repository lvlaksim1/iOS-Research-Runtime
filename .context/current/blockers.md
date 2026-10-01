# Current blockers and open risks

Updated: 2026-10-01 14:14 MSK

## IOS-M1
No blocker remains for IOS-M1. The milestone is complete with exact-SHA evidence on `main@95caa93fc8fd0db827491e679628efa40612b55c`.

## Known residual technical issues
These are real technical issues, but they are not blockers to the completed IOS-M1 acceptance:
- post-proof QEMU/integration harness nontermination causes the E2E workflow to conclude FAILURE even after verified root-shell proof;
- repeated `AppleSEPManager` endpoint timeouts remain;
- broader iOS service completeness, GUI/SpringBoard and ordinary user-device behavior remain outside the proven milestone.

## Product-direction gate
The next blocker is strategic, not technical: the next product milestone has not yet been selected by Owner with the Project Manager. No autonomous continuation should infer that goal.

## Runtime
PP-RM package008 is terminal `FINAL_COMPLETED`.
Worker A, Worker B and Watchdog are disabled.
No continuity recovery is required.

## Residual PP-RM risks for future packages
- GitHub/run visibility can lag.
- Scheduled Task delivery can be delayed; DTSTART is not an SLA.
- hourly Watchdog recurrence is a recovery floor, not a five-minute guarantee.
- Scheduled Tasks have no CAS; stale already-running control-plane work remains possible.
- frozen mutation descriptor must remain unchanged across recovery.
- authoritative main neither frozen baseline nor target => FAIL_STOP.
- OCB: explicit OSB only, maximum three exact-identical attempts, no fourth.

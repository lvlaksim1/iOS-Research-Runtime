# Current blockers and open risks

Updated: 2026-09-29 22:57 MSK

## Product blocker
Exact-SHA E2E still fails before verified recovery root shell. Current investigation remains AMFI / CT launch constraints around recovery executable signature policy.

## Runtime status
There is no authorized PP-RM execution at this checkpoint.
Worker A, Worker B and Watchdog are disabled.
Package `IOS-M1-CONTINUOUS-005` is reserved but NOT ARMED.

## Generation-15 residual continuity risk
Early Watchdog self-rearm closes predecessor-loss after the first tool operation, but a runtime could still fail before that first operation executes.
The independent hourly `отчет PPRM` task is detection-only and is not a recovery actor.

## Remaining continuity limitations
- fencing cannot cancel an external request already in flight;
- ambiguous GitHub ref mutation must be reconciled before replay;
- Scheduled Task delivery itself is not guaranteed;
- A/B remain interchangeable physical executor slots;
- Watchdog cadence is fixed at 5 minutes and intentionally non-adaptive.

## OCB
OCB remains explicit OSB only, maximum three exact-identical attempts, no fourth request, with authoritative reconciliation for ambiguous mutation.

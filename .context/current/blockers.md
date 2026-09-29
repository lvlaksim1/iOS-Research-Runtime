# Current blockers and open risks

## Product blocker
Exact-SHA E2E still fails before verified recovery root shell. Current investigation remains AMFI / CT launch constraints around recovery executable signature policy.

## Continuity defect addressed by generation 15
Package `IOS-M1-CONTINUOUS-003` lost continuity when the sole Watchdog runtime was invoked but produced no durable recovery/self-rearm.

Generation 15 removes mutable Watchdog state from its prompt and makes early self-rearm (+5 minutes) the first operation of every Watchdog invocation.

The isolated early-rearm regression test passed the critical predecessor-loss scenario.

## Residual continuity risk
A Watchdog runtime could theoretically fail before its first tool operation. This narrow residual window is not closed by a single-task Watchdog.

The independent hourly `отчет PPRM` task remains read-only and provides external detection only; it is not a recovery actor.

## Remaining continuity limitations
- fencing cannot cancel an external request already in flight;
- ambiguous GitHub ref mutation must be reconciled before replay;
- Scheduled Task delivery itself is not guaranteed;
- A/B remain interchangeable physical executor slots;
- Watchdog cadence is fixed at 5 minutes and intentionally non-adaptive.

## Genuine stop conditions
- IOS-M1 achieved;
- required action exceeds Manager mandate or needs Owner approval;
- unresolved ambiguous side effect;
- three confirmed runtime failures/stalls for one generation after safe failover;
- both executor slots cannot be dispatched after bounded retries;
- true strategic fork outside tactical IOS-M1 execution.

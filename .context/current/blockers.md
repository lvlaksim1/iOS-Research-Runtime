# Current blockers and open risks

Updated: 2026-10-01 15:13 MSK

## IOS-M1
No blocker remains. IOS-M1 is complete on `main@95caa93fc8fd0db827491e679628efa40612b55c`.

## IOS-M2
The immediate blocker is technical rather than strategic: the actual post-recovery boot boundary has not yet been measured.

Unknowns for the first probe:
- whether full-system/preboot volumes or required material are present in the current runtime;
- what storage/device nodes the current QEMU Darwin machine exposes;
- whether current launchd can see/start the service graph needed for transition;
- whether the first hard dependency is provisioning, mount topology, launchd/bootstrap, trust/security/SEP, or missing QEMU hardware behavior.

No one possibility is yet promoted to root cause.

## Known residual issues
- post-proof QEMU/integration harness nontermination can make an evidence-producing E2E run conclude FAILURE;
- repeated `AppleSEPManager` endpoint timeouts remain;
- graphical/user iOS and SpringBoard remain unproved.

## Runtime
Fresh successor package is reserved as `IOS-M2-CONTINUOUS-009`.
The current direct live carrier owns the first probe. PP-RM Workers and Watchdog remain unarmed until scheduler handoff is needed.

## Residual PP-RM risks
GitHub visibility lag, Scheduled Task delivery delay, hourly Watchdog floor, lack of CAS, stale already-running work, frozen mutation descriptor requirements, and OCB3 remain applicable.

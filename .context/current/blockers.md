# Current blockers and open risks

Updated: 2026-10-01 15:18 MSK

## IOS-M1
No blocker remains. IOS-M1 is complete.

## IOS-M2
The immediate blocker is evidence availability/classification, not project direction.
A post-root diagnostic probe is now committed on `main@24730a74051378d228efd370f3baee5a4f46bdfa`; the next required fact is exact-SHA Windows E2E output.

Unknowns to classify from that output:
- whether full-system/preboot volumes or required material are present;
- what storage/device nodes the current QEMU Darwin machine exposes;
- whether current launchd can see/start the service graph needed for transition;
- whether the first hard dependency is provisioning, mount topology, launchd/bootstrap, trust/security/SEP, QEMU hardware behavior, or another class.

No one possibility is yet promoted to root cause.

## Known residual issues
- post-proof QEMU/integration harness nontermination can make an evidence-producing E2E run conclude FAILURE;
- repeated `AppleSEPManager` endpoint timeouts remain;
- graphical/user iOS and SpringBoard remain unproved.

## Runtime
Package `IOS-M2-CONTINUOUS-009` is initialized in `WAIT_EXTERNAL_EVIDENCE`.
Mailbox/Trace and Worker programs are prepared for package009.
Watchdog is the designated read-only evidence-wait carrier; Workers stay disabled until terminal exact-SHA evidence is available.

## Residual PP-RM risks
GitHub visibility lag, Scheduled Task delivery delay, hourly Watchdog floor, lack of CAS, stale already-running work, frozen mutation descriptor requirements, and OCB3 remain applicable.

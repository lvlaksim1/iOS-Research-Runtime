# Current state

## Governance
- manager: `ios-research-runtime-project-manager`
- manager generation: 14
- product authority: `main`
- execution package: `IOS-M1-CONTINUOUS-003`
- execution mode: continuous PP-RM with dispatch-aware fenced Watchdog recovery

## Product
- live main: `649a2244f876db34e2032755b189df158667305f`
- commit message: `Preserve Apple recovery bash during sysroot merge`
- Windows Build: SUCCESS
- Windows End-to-End Boot run `36556048793`: FAILURE
- exact root-shell blocker: AMFI rejects ad-hoc-signed `/bin/bash` due unsuitable CT policy / Launch Constraint Violation
- Ramdisk Tool Windows run `36556048692`: FAILURE, regression-test nil dereference at `main_test.go:81`

## PP-RM generation 13 result
Package `IOS-M1-CONTINUOUS-002` proved that Watchdog detects silent continuity loss, but its recovery classified every missing ACK as a runtime failure.
Generation 2 Worker A did not advance last_run_time on watchdog redispatches; therefore attempts 2/3 were scheduler delivery failures, not confirmed runtime failures.
The old policy incorrectly consumed the three-attempt runtime budget and fail-stopped.

## PP-RM generation 14 construction
Topology remains A + B + Mailbox + Trace + Watchdog.
Worker prompts no longer contain mutable activation tuples.
Mailbox is the sole activation authority.

Recovery now distinguishes:
- DISPATCH_FAILURE: last_run_time did not advance from dispatch baseline;
- RUNTIME_FAILURE: last_run_time advanced but no durable ACK.

Dispatch retries do not consume activation_attempt.
After repeated dispatch failure on one slot, Watchdog rotates token and fails over to the partner slot on the same generation.
Maximum three activation attempts applies only to confirmed runtime failures.

## OCB
Unchanged: explicit OSB only; max three exact-identical GitHub requests; no automatic fourth request; mandatory authoritative reconciliation for ambiguous writes.

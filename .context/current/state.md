# Current state

## Governance
- manager: `ios-research-runtime-project-manager`
- manager generation: 13
- product authority: `main`
- execution package: `IOS-M1-CONTINUOUS-002`
- execution mode: continuous PP-RM with fenced Watchdog recovery

## Product
- live main: `649a2244f876db34e2032755b189df158667305f`
- commit message: `Preserve Apple recovery bash during sysroot merge`
- Windows Build: SUCCESS
- Windows End-to-End Boot run `36556048793`: FAILURE
- exact root-shell blocker: AMFI rejects ad-hoc-signed `/bin/bash` due unsuitable CT policy / Launch Constraint Violation
- Ramdisk Tool Windows run `36556048692`: FAILURE, regression-test nil dereference at `main_test.go:81`

## Previous PP-RM
Package `IOS-M1-CONTINUOUS-001` reached generation 139.
Generation 138 handed a valid baton to A. Scheduler started A, but A produced no durable ACK/Trace/handoff and both workers became disabled.
This exposed a silent-death window between runtime start and first durable checkpoint.

## New PP-RM construction
The Pulse task is retired and repurposed as Watchdog.
Topology: A + B + Mailbox + Trace + Watchdog.

Every activation is fenced by `generation/attempt/activation_token/message_id`.
Workers revalidate the current token before ACK, before every consequential GitHub mutation, and before outbound handoff.
Watchdog can rotate a stalled baton to a new attempt/token and re-arm the owner, up to three attempts per generation.

## OCB
Unchanged: explicit OSB only; max three exact-identical requests; no automatic fourth request; mandatory authoritative reconciliation for ambiguous writes.

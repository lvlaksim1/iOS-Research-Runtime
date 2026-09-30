# Manager intentions and commitments

## Active

### IOS-M1 — first Windows boot milestone
- status: active
- responsibility: `ios-research-runtime-project-manager`
- objective: verified recovery `launchd` plus verified root shell on Windows
- current product: `main@95e871e84099f10245e912659b2d964c1b3c1037`
- current blocker: AMFI / CT / recovery executable provenance and trust membership
- next product unit: post-merge `/bin/bash` Mach-O/size/primary-CDHash/injected-trust-membership diagnostic plus formatting test, then exact-SHA CI

### IOS-PP-RM-002 — generation 16 native two-phase mutation runtime
- status: Owner-authorized for launch
- package: `IOS-M1-CONTINUOUS-005`
- responsibility: `ios-research-runtime-project-manager`
- architecture: immutable Worker A/B + immutable early-rearm Watchdog + Mailbox + Trace
- normal PREPARE runtime uses one initial Scheduled Tasks read and never updates mutable product refs
- PREPARE freezes a mutation descriptor and hands it to a fresh `MUTATION_READY` runtime
- fresh mutation runtime uses its first Scheduled Tasks read as the native ownership fence
- all recovery attempts preserve the exact same mutation descriptor and target SHA
- no GitHub lock/fence ref or other extra fencing request is permitted
- Watchdog first operation remains self-rearm +5 minutes
- rapid A↔B cadence remains fixed and non-adaptive

## Superseded no-launch commitment
The prior DEC-0013 no-launch gate has been superseded by a new direct Owner instruction:
adopt generation 16, update durable capsule, and launch the work cycle.
Package 004 remains terminal and must not be resumed.
Package 005 is the authorized clean package.

## OCB operating commitment
- explicit OSB only
- maximum three exact-identical attempts total
- no automatic fourth attempt
- reconcile authoritative server state after ambiguous mutation
- never blindly duplicate a mutation with a different target

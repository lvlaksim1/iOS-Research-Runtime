# Manager intentions and commitments

## Active

### IOS-M1 — first Windows boot milestone
- status: active
- responsibility: `ios-research-runtime-project-manager`
- objective: verified recovery `launchd` plus verified root shell on Windows.
- current product: `main@eaa98114031a37343e0d5184bd132830818a6b2f`
- current product blocker: AMFI / CT launch-constraint rejection of recovery root-shell execution.
- next justified product unit when execution is explicitly resumed: narrow source-recovery executable/signature/xattr inventory diagnostic and tests, then exact-SHA CI.

### IOS-PP-RM-001 — generation 15 runtime construction
- status: defined, not running
- responsibility: `ios-research-runtime-project-manager`
- architecture: immutable Worker A/B + immutable early-rearm Watchdog + Mailbox + Trace.
- Watchdog first operation: self-rearm same unchanged task for exactly +5 minutes.
- Mailbox owns current baton and all Watchdog observation/recovery state.
- rapid A↔B cadence remains fixed; no adaptive handoff interval.
- stop conditions and recovery semantics remain those defined by DEC-0012 plus generation-14 dispatch-aware failover.

## No-launch commitment
- Direct Owner instruction: update PP-RM in durable context only; do not launch it.
- Package `IOS-M1-CONTINUOUS-004` was already inadvertently active before this instruction; all PP-RM execution actors were disabled in response.
- Reserve `IOS-M1-CONTINUOUS-005` as the next clean package.
- Do not seed/arm package 005 and do not re-arm package 004 without a new explicit Owner launch instruction.

## OCB operating commitment
- Explicit OSB only.
- Maximum three exact-identical attempts total for the same request after consecutive explicit OSB.
- No automatic fourth attempt.
- Reconcile authoritative server state after ambiguous mutation.
- Never blindly duplicate an ambiguous mutation.

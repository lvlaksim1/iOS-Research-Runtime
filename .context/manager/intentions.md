# Manager intentions and commitments

## Active

### IOS-M1 — first Windows boot milestone
- status: active
- responsibility: `ios-research-runtime-project-manager`
- objective: verified recovery `launchd` plus verified root shell on Windows
- current product: `main@bcde5661eab70b6811a5f1fffe0552edaedf980a`
- exact-head E2E run `36729602541`: FAILURE at provisioning / Darwin root-shell proof
- evidence collection/upload: SUCCESS
- next product unit: inspect terminal evidence from run 36729602541, extract post-merge bash SignatureInfo and AMFI/root-shell evidence versus the pre-SHA256 baseline, then execute one bounded diagnostic/fix and exact-SHA CI

### IOS-PP-RM-003 — generation 17 recurring-backstop Watchdog
- status: Owner-authorized for launch
- package: `IOS-M1-CONTINUOUS-006`
- responsibility: `ios-research-runtime-project-manager`
- architecture: immutable Worker A/B + immutable recurring-backstop Watchdog + Mailbox + Trace
- generation-16 native two-phase product mutation protocol is preserved unchanged
- Watchdog is always armed with `RRULE:FREQ=HOURLY` plus a near-term DTSTART
- Watchdog continuity no longer depends on a successful first runtime operation
- healthy invocation first performs a schedule-preserving self-touch, then may slide the same recurring task by +5 minutes while keeping the hourly RRULE
- failure before/during sliding degrades to the already-persisted hourly recurrence rather than permanent stop
- no Lifeboat, no sixth task, no new slot, no GitHub continuity fence

## Superseded runtime package
Package `IOS-M1-CONTINUOUS-005` is superseded and must not be resumed. Its final observed control-plane state was generation 262, owner A, READY, ACK=NONE, while A/B/Watchdog ended disabled. Product main remained authoritative and unambiguous.

## OCB operating commitment
- explicit OSB only
- maximum three exact-identical attempts total
- no automatic fourth attempt
- reconcile authoritative server state after ambiguous mutation
- never duplicate a mutation with a different target

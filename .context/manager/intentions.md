# Manager intentions and commitments

## Active

### IOS-M1 — first Windows boot milestone
- status: active
- responsibility: `ios-research-runtime-project-manager`
- objective: verified recovery `launchd` plus verified root shell on Windows
- current product: `main@bcde5661eab70b6811a5f1fffe0552edaedf980a`
- exact-head E2E run `36729602541`: FAILURE at provisioning / Darwin root-shell proof
- failure evidence collection/upload: SUCCESS
- current diagnosis: intended SHA256-primary signing was not achieved because later `rcodesign` Mach-O settings import overrides the CLI digest selection and restores SHA1 primary
- next product unit: generation3 bounded override design; prove post-sign SHA256 primary before preparing a target and rerunning exact-SHA CI/E2E

### IOS-PP-RM-003 — generation 17 recurring-backstop Watchdog
- status: active / running in production
- package: `IOS-M1-CONTINUOUS-006`
- responsibility: `ios-research-runtime-project-manager`
- architecture: immutable Worker A/B + immutable recurring-backstop Watchdog + Mailbox + Trace
- generation-16 native two-phase product mutation protocol remains authoritative
- Watchdog remains enabled with `RRULE:FREQ=HOURLY` plus near-term sliding when healthy
- hourly recurrence is the survival backstop; +5 minute sliding is the fast path
- no Lifeboat, no sixth task, no new slot, no GitHub continuity fence
- live launch evidence: generation1 B handoff to generation2 A; generation2 A handoff to generation3 B

## Superseded runtime package
Package `IOS-M1-CONTINUOUS-005` is superseded and MUST NOT be resumed.

## OCB operating commitment
- explicit OSB only
- maximum three exact-identical attempts total
- no automatic fourth attempt
- reconcile authoritative server state after ambiguous mutation
- never duplicate a mutation with a different target

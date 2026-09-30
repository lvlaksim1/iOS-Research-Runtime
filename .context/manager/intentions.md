# Manager intentions and commitments

## Active

### IOS-M1 — first Windows boot milestone
- status: active
- responsibility: `ios-research-runtime-project-manager`
- objective: verified recovery `launchd` plus verified root shell on Windows
- current product: `main@4821fb9a9cd72dd40af2a518962f180fb4344fe7`
- exact-main rcodesign Windows Gate `36771957949`: SUCCESS
- exact-main Windows Build `36771957738`: SUCCESS
- next product unit: extract strict primary-SHA256 proof from the successful gate, then continue the smallest exact-SHA E2E/root-shell path

### IOS-PP-RM-004 — generation18 result-first workflow evidence
- status: Owner-authorized for launch
- package: `IOS-M1-CONTINUOUS-007`
- responsibility: `ios-research-runtime-project-manager`
- architecture: immutable Worker A/B + immutable recurring-backstop Watchdog + Mailbox + Trace
- generation16 native two-phase product mutation is preserved
- generation17 recurring-hourly Watchdog is preserved
- workflow gates are result-first: existing qualifying exact-SHA evidence is consumed before any dispatch attempt
- trigger event is irrelevant unless the specific test contract requires trigger semantics
- no Lifeboat, sixth task, extra PP-RM slot or GitHub continuity fence

## Superseded runtime packages
- package005 is stranded/superseded and must not resume
- package006 is terminal `FAIL_STOP_OWNER_GATE` and must not resume

## OCB operating commitment
- explicit OSB only
- maximum three exact-identical attempts total
- no automatic fourth attempt
- reconcile authoritative server state after ambiguous mutation
- never duplicate a mutation with a different target

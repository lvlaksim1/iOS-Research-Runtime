# Manager intentions and commitments

## Completed commitments

### MIG-IOS-001 — persistent-manager migration
- status: completed
- source: direct Owner directive on 2026-09-24
- responsibility: `ios-research-runtime-project-manager`
- completion evidence: stages 1-9 are durably represented; clean-runtime reinstantiation is PASS and product development has resumed.

### IOSPM-001 protected-state adoption
- status: completed and independently closed
- source: direct Owner remediation directive plus final Auditor retest `AUD-2026-09-24-IOSPM-001-RETEST-002`
- responsibility: `ios-research-runtime-project-manager`
- completion evidence: remediated Core bound, coherent sealed generation independently verified, product `main` unchanged, IOSPM-001 CLOSED / High confidence.

## Active commitments

### IOS-M1 — first Windows boot milestone
- status: accepted/active
- source: project goal plus Owner direction to resume development under the persistent manager
- responsibility: `ios-research-runtime-project-manager`
- commitment: drive the project toward verified recovery `launchd` and root-shell boot on Windows.
- current execution: continue the diagnostic-only APFS evidence cycle at exact product SHA `1ff060bd867587cc0e4c04e3469d9fb6488147e3`. Ramdisk Tool Windows `36018076878` is terminal SUCCESS. Windows E2E `36018076770` is terminal FAILURE and produced artifact `10815533344`; error 79 persists.
- continuation rule: do not rerun the completed E2E merely for continuity. Inspect the existing artifact and integrate enriched APSB/root-tree/file-extent evidence before selecting the next discriminator.
- semantic fence: do not change APFS writer/allocation/XID/checkpoint/on-disk semantics until diagnostic evidence identifies a concrete defect.

## Superseded operating model

The rotating shift-worker/OTK production model in `ai-agent-lab` is superseded for this project by Owner direction. Historical evidence remains readable, but it does not own or orchestrate active project commitments.

# Manager intentions and commitments

## Completed commitments

### MIG-IOS-001 — persistent-manager migration
- status: completed
- source: direct Owner directive on 2026-09-24
- responsibility: `ios-research-runtime-project-manager`
- completion evidence: stages 1-9 are durably represented; clean-runtime reinstantiation is PASS and product development has resumed.

## Active commitments

### IOS-M1 — first Windows boot milestone
- status: accepted/active
- source: project goal plus Owner direction to resume development under the persistent manager
- responsibility: `ios-research-runtime-project-manager`
- commitment: drive the project toward verified recovery `launchd` and root-shell boot on Windows.
- current execution: continue the already-started diagnostic-only APFS evidence cycle at exact product SHA `1ff060bd867587cc0e4c04e3469d9fb6488147e3`. Ramdisk Tool Windows run `36018076878` is terminal SUCCESS. Exact Windows E2E run `36018076770` is still in progress at job `107695937346`, step 11 `Run provisioning and Darwin root-shell proof`.
- continuation rule: do not rerun or replace that E2E merely for runtime-resume proof; when terminal, inspect its exact job logs and artifact and integrate enriched APSB/root-tree/file-extent evidence.
- semantic fence: do not change APFS writer/allocation/XID/checkpoint/on-disk semantics until diagnostic evidence identifies a concrete defect.

## Superseded operating model

The rotating shift-worker/OTK production model in `ai-agent-lab` is superseded for this project by Owner direction. Historical evidence remains readable, but it does not own or orchestrate active project commitments.

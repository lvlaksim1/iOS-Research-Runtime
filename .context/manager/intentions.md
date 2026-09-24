# Manager intentions and commitments

## Completed commitments

### MIG-IOS-001 — persistent-manager migration
- status: completed
- source: direct Owner directive on 2026-09-24
- responsibility: `ios-research-runtime-project-manager`
- completion evidence: stages 1-9 are durably represented; `.context/runtime-tests/2026-09-24-clean-reinstantiation.md` records the terminal clean-runtime result **PASS**, and that result was reconciled before product development resumed.

## Active commitments

### IOS-M1 — first Windows boot milestone
- status: accepted/active
- source: project goal plus Owner direction to resume development under the new model
- responsibility: `ios-research-runtime-project-manager`
- commitment: drive the project toward verified recovery `launchd` and root-shell boot on Windows.
- current execution: first post-migration diagnostic-only APFS evidence cycle is running against product commit `ff0e637733c2b1365d39e0af6152f75de34e0984`; exact Windows E2E run `36017905181` is non-terminal at the current checkpoint.
- semantic fence: do not change APFS writer/allocation/XID/checkpoint/on-disk semantics until diagnostic evidence identifies a concrete defect.

## Superseded operating model

The rotating shift-worker/OTK production model in `ai-agent-lab` is superseded for this project by Owner direction. Historical evidence remains readable, but the old queue/shift machinery no longer owns active project commitments.

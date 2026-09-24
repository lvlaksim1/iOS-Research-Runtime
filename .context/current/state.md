# Current state

## Governance topology

- persistent manager: `ios-research-runtime-project-manager`;
- manager-state authority: `manager-state`;
- product authority: `main`;
- discovery branch: `main`;
- legacy `ai-agent-lab` iOS autonomy: archived/migrated and not an orchestrator.

## Commitment state

Persistent-manager migration and clean-runtime reinstantiation are complete. `MIG-IOS-001` is terminal completed. `IOS-M1` remains accepted/active.

## Verified technical boundary

Prior baseline `3b0f5648f004f58daef526082b3d2a32d132edcf` and E2E `35634992757` established repeated APFS `mountroot error 79` after `BSD root: md0`. Independent extentref reconciliation established that raw extentref record-count divergence is not an active discriminator.

## Active diagnostic cycle

Current exact product commit is `1ff060bd867587cc0e4c04e3469d9fb6488147e3`, verified as live `main`. The diagnostic-only change emits fuller APSB diagnostics, recursively read root-tree evidence and file-extent summaries. APFS writer/allocation/XID/checkpoint/on-disk semantics were not changed.

Initial SHA `ff0e637733c2b1365d39e0af6152f75de34e0984` exposed a compile-only diagnostic defect in Ramdisk Tool Windows run `36017905169`; correction to the pinned parser field `NumberOfBlocks` produced current SHA `1ff060bd...`.

Exact validation at current SHA:
- Ramdisk Tool Windows run `36018076878` — COMPLETED / SUCCESS. Its build job completed tests, Windows x64 build, smoke test and helper artifact upload.
- Windows End-to-End Boot run `36018076770` — IN PROGRESS. Job `107695937346` completed environment/QEMU/helper/harness preparation and is currently at step 11 `Run provisioning and Darwin root-shell proof`; failure-evidence collection and artifact uploads remain pending.

No boot/APFS conclusion is inferred while E2E `36018076770` remains non-terminal. The next operation is to continue that exact existing run to terminal evidence, not start a new cycle or rerun it for continuity proof.

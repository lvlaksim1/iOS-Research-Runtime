# Current state

## Governance topology

- persistent manager: `ios-research-runtime-project-manager`;
- manager-state authority: `manager-state`;
- product authority: `main`;
- discovery branch: `main`;
- Agent Control Plane registration: verified at `705346c3bc702343ac1e1a25fd6e4a0bde1a3d6f`;
- legacy `ai-agent-lab` iOS autonomy: ARCHIVED / MIGRATED.

## Migration progress

Stages 1-9 are COMPLETE. The clean-runtime reinstantiation gate is PASS as recorded in `.context/runtime-tests/2026-09-24-clean-reinstantiation.md` and was reconciled before product work resumed. `MIG-IOS-001` is complete; `IOS-M1` remains active.

## Verified technical boundary before this cycle

Product-code baseline before the diagnostic cycle: `3b0f5648f004f58daef526082b3d2a32d132edcf`.
Prior exact Windows E2E `35634992757` reached XNU, identified `md0`, and repeatedly failed APFS root mount with error 79. Independent extentref reconciliation remains valid: raw extentref record-count divergence is not an active discriminator.

## First post-migration engineering cycle

A diagnostic-only APFS evidence change has been implemented on `main`; APFS writer, allocation, XID/checkpoint and other on-disk writer semantics were not changed.

Initial diagnostic SHA `ff0e637733c2b1365d39e0af6152f75de34e0984` exposed a compile-only defect in Ramdisk Tool Windows run `36017905169`: diagnostic code referenced nonexistent `ContainerSuperblock.BlockCount`. The exact job log was inspected and the diagnostic implementation only was corrected to the pinned library field `NumberOfBlocks`.

Current exact product commit: `1ff060bd867587cc0e4c04e3469d9fb6488147e3`.

The change emits fuller APSB diagnostics, a recursively read root-tree snapshot, and a file-extent summary containing owner/logical/physical/length/block/crypto data plus container-bounds and physical-overlap checks. Focused unit tests cover normal, overlap and out-of-bounds summaries.

Exact validation bound to current SHA:
- Ramdisk Tool Windows run `36018076878` — queued at checkpoint;
- Windows End-to-End Boot run `36018076770` — pending at checkpoint.

No boot or APFS conclusion is inferred until those exact runs become terminal and their logs/artifacts are inspected.

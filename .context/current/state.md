# Current state

## Governance topology

- persistent manager: `ios-research-runtime-project-manager`;
- manager-state authority: `manager-state`;
- product authority: `main`;
- discovery branch: `main`;
- Agent Control Plane registration: verified at `705346c3bc702343ac1e1a25fd6e4a0bde1a3d6f`;
- legacy `ai-agent-lab` iOS autonomy: ARCHIVED / MIGRATED.

## Migration progress

Stages 1-9 are COMPLETE. The clean-runtime reinstantiation gate is PASS as recorded in `.context/runtime-tests/2026-09-24-clean-reinstantiation.md` and was reconciled before product work resumed.

`MIG-IOS-001` is therefore complete. Ordinary product development continues under `IOS-M1` with this same persistent Project Manager.

## Verified technical boundary before this cycle

Product-code baseline before the diagnostic cycle: `3b0f5648f004f58daef526082b3d2a32d132edcf`.

Prior exact Windows E2E:
- run `35634992757`;
- artifact `10655952032 / ios-darwin-windows-e2e`;
- digest `sha256:49ea4772133376adcf79f2e5604e6a196d4b4d9c8d9fe12814ce6d03a98c1d73`;
- XNU identifies `md0` and APFS repeatedly fails root mount with error 79.

Independent extentref reconciliation remains valid: raw extentref record-count divergence is not an active discriminator and no writer semantic mutation is justified by it.

## First post-migration engineering cycle

A diagnostic-only APFS evidence change has been implemented on product authority `main` without changing APFS writer, allocation, XID/checkpoint, or other on-disk writer semantics.

Exact product commit: `ff0e637733c2b1365d39e0af6152f75de34e0984`.

The change:
- emits APSB fields already exposed by pinned `go-apfs-v2`: unmount time, reserved/quota/allocated blocks, formatted-by, modified-by history, next document ID, ER-state OID and clone-info fields;
- persists the recursively read root-tree snapshot including leaf records;
- derives a compact file-extent summary with owner OID, logical offset, physical block, length, block count, crypto ID, container-bounds validation and physical-overlap count;
- adds focused unit coverage for normal, overlap and out-of-bounds extent summaries.

Exact Windows paths triggered for this SHA include Ramdisk Tool Windows run `36017905169` and Windows End-to-End Boot run `36017905181`. At this checkpoint both are still non-terminal, so no E2E outcome is inferred.

# Current state

## Governance topology

- persistent manager: `ios-research-runtime-project-manager`;
- manager-state authority: `manager-state`;
- product authority: `main`;
- discovery branch: `main`;
- Agent Control Plane registration: verified at `705346c3bc702343ac1e1a25fd6e4a0bde1a3d6f`;
- legacy `ai-agent-lab` iOS autonomy: ARCHIVED / MIGRATED.

## Migration progress

Completed: stages 1-8.
Next: stage 9 clean-runtime reinstantiation proof.

No product-code mutation has occurred during stages 1-8.

## Verified technical boundary

Product-code baseline:
`3b0f5648f004f58daef526082b3d2a32d132edcf`.

Exact Windows E2E:
- run `35634992757`;
- artifact `10655952032 / ios-darwin-windows-e2e`;
- digest `sha256:49ea4772133376adcf79f2e5604e6a196d4b4d9c8d9fe12814ce6d03a98c1d73`;
- XNU identifies `md0` and APFS repeatedly fails root mount with error 79.

Independent extentref reconciliation:
- source: 719 records, all refcount 1, 719 unique owners, 46,740 blocks; APSB net allocation 46,740;
- rebuilt: 1,360 records, all refcount 1, 1,360 unique owners, 51,651 blocks; APSB net allocation 51,844;
- rebuilt delta: 193 blocks, consistent with pinned writer-owned metadata allocation;
- root/extentref/snapshot-metadata checksums exposed by the artifact are valid.

Conclusion: extentref count/conservation is no longer the active discriminator. Next engineering evidence is fuller APSB and root-tree semantics.

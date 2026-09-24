# Technical reconciliation — APFS mount error 79

Date: 2026-09-24
Product evidence baseline: `3b0f5648f004f58daef526082b3d2a32d132edcf`
Windows E2E run: `35634992757`
Artifact: `ios-darwin-windows-e2e`
Artifact digest: `sha256:49ea4772133376adcf79f2e5604e6a196d4b4d9c8d9fe12814ce6d03a98c1d73`

## Purpose

Independently revalidate the useful technical claims from legacy checkpoint
`lvlaksim1/ai-agent-lab@fde4f271641096f20249686f0bd730c2d1a7241f`
without inheriting authority from the fenced legacy worker.

## Reproduced facts from the immutable E2E artifact

The extent-reference child leaves were decoded directly from
`boot-logs/apfs-structural-evidence.json` using the on-disk physical-extent
record layout used by the pinned writer.

Source:
- extentref records: 719;
- unique owning object IDs: 719;
- every refcount: 1;
- summed physical extent length: 46,740 blocks;
- APSB net allocation: 49,426 - 2,686 = 46,740 blocks.

Rebuilt:
- extentref records: 1,360;
- unique owning object IDs: 1,360;
- every refcount: 1;
- summed physical extent length: 51,651 blocks;
- APSB net allocation: 51,844 - 0 = 51,844 blocks;
- difference above physical file extents: 193 blocks.

The source and rebuilt root-tree, extentref-tree and snapshot-metadata tree
checksums present in the artifact are valid.

## Reproduced writer semantics from the exact product revision

At the same product SHA:

- `file.go::physFiles()` returns every stream file with `blocks > 0`;
- `makeExtentrefRoot()` writes one physical-extent record per such file;
- `fileDataBlocks` is the sum of blocks owned by all stream files;
- `spaceman.go::placePostPool()` sets `ownedBlocks` to the sum of object-map
  leaves, file-system-tree leaves/index nodes, extentref leaves, file-data
  blocks and snapshot blocks;
- `super.go::volumeSuperblock()` writes
  `FsAllocCount = 5 + ownedBlocks - snapshotCount`;
- the evidence artifact reports snapshot count 0 for both source and rebuilt.

Therefore the rebuilt 193-block difference is consistent with writer-owned
filesystem metadata plus the five fixed empty-volume allocations. It is not
evidence that 193 file-data extentref records are missing.

## Reconciliation result

The legacy checkpoint's narrow extentref-conservation conclusion is
independently reproduced and may now be admitted as project knowledge:

- raw `719 vs 1360` extentref record-count divergence does not justify an APFS
  semantic mutation;
- the rebuilt 193-block allocation delta is explainable by the writer's own
  allocation model;
- the investigation should move away from raw extentref-count comparison.

This does **not** prove the writer is mount-correct. APFS `mountroot error 79`
remains unresolved.

## Highest-value evidence gap

The current JSON already resolves and recursively reads APFS B-trees, but it
only emits full records for the extentref and snapshot-metadata trees. For the
root tree it persists only header/checksum metadata.

The pinned upstream `go-apfs-v2 v0.3.0` volume-superblock parser already
exposes additional APSB fields that the current JSON omits, including:
- unmount time;
- reserved-block count;
- quota-block count;
- formatted-by record;
- modified-by history;
- next document ID;
- encryption rolling-state OID;
- clone-info ID epoch and transaction ID.

These omissions create a read-only evidence gap before any further writer
mutation.

## Decision

The next product experiment must be diagnostic-only: expand APSB/root-tree
evidence, run the exact Windows E2E again, and use the resulting comparison to
select the next writer hypothesis.

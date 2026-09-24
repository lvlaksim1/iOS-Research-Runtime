# Current blockers and open risks

## Active product blocker

The rebuilt APFS recovery ramdisk is rejected during Darwin root mounting with error 79 in the last terminal boot evidence.

## Resolved gates / uncertainty

- Persistent-manager migration and clean-runtime reinstantiation gate are complete; they no longer pause product work.
- Legacy shift-154 extentref-conservation claims were independently reproduced. Raw extentref record-count divergence is not a justified writer-mutation discriminator.
- Current diagnostic implementation at product SHA `1ff060bd867587cc0e4c04e3469d9fb6488147e3` passes Ramdisk Tool Windows run `36018076878`.

## Current evidence gate

Exact Windows End-to-End Boot run `36018076770`, bound to `1ff060bd...`, is still in progress. Until it becomes terminal and its exact logs/artifact are inspected, enriched APSB/root-tree/file-extent evidence is not available for a new semantic conclusion.

APFS writer/allocation/XID/checkpoint/on-disk semantics remain fenced against change until concrete discriminator evidence identifies a defect.

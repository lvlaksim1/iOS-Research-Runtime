# Current blockers and open risks

## Active technical blocker

The rebuilt APFS recovery ramdisk is rejected during root mounting:
`apfs_vfsop_mount ... root_device: 79` / `mountroot failed, error: 79`.

Technical work on this blocker is intentionally paused until migration/reconciliation acceptance gates are complete.

## Evidence risk requiring reconciliation

Legacy checkpoint `lvlaksim1/ai-agent-lab@fde4f271641096f20249686f0bd730c2d1a7241f` contains potentially useful APFS extentref conclusions but was written after its worker had been fenced. Its technical claims are candidate evidence only until independently reproduced.

## Governance risk being removed

The old autonomy accumulated its own scheduler/worker/OTK/fencing complexity and suffered a post-fence zombie write. The migration explicitly avoids repairing or reinstating that factory.

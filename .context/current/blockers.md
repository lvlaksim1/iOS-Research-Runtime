# Current blockers and open risks

## Active product blocker

The rebuilt APFS recovery ramdisk is still rejected during Darwin root mounting with error 79 in exact E2E `36018076770` at product SHA `1ff060bd867587cc0e4c04e3469d9fb6488147e3`.

## Resolved governance blocker

The local exposure underlying IOSPM-001 is being removed by this same sealed generation: the manager is bound to remediated Context Capsule Core `3a942bd...` and gains fail-closed manager-state integrity checking before READY/recover. Final finding closure still requires independent Auditor verification of this deployed snapshot.

## Current evidence gate

The enriched E2E artifact `10815533344` exists and must be analyzed before choosing the next APFS hypothesis. Error 79 persistence alone does not identify the concrete writer defect.

APFS writer/allocation/XID/checkpoint/on-disk semantics remain fenced against change until concrete discriminator evidence identifies a defect.

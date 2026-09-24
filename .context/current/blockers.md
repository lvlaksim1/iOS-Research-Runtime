# Current blockers and open risks

## Active product blocker

The rebuilt APFS recovery ramdisk is still rejected during Darwin root mounting with error 79 in exact E2E `36018076770` at product SHA `1ff060bd867587cc0e4c04e3469d9fb6488147e3`.

## Governance status

IOSPM-001 is CLOSED / Medium severity / High confidence. No governance blocker prevents ordinary IOS-M1 development.

## Current evidence gate

Analyze enriched artifact `10815533344` before choosing the next APFS hypothesis. Error 79 persistence alone does not identify the concrete writer defect.

APFS writer/allocation/XID/checkpoint/on-disk semantics remain fenced against change until concrete discriminator evidence identifies a defect.

# Current blockers and open risks

## Active product blocker

The rebuilt APFS recovery ramdisk is rejected during Darwin root mounting with error 79.

## Resolved evidence uncertainty

The legacy shift-154 extentref-conservation claim is no longer untrusted candidate knowledge: its numerical and writer-model claims were independently reproduced from exact E2E evidence and exact product code.

## Remaining evidence gap

Current APFS evidence omits several APSB fields already parsed by the pinned upstream library and does not persist the full recursively read root tree. Therefore no specific writer defect is yet proven.

## Migration gate

Product mutation remains paused only until stage 9 clean-runtime reinstantiation proof is complete. After that, the first allowed product change is diagnostic-only according to the engineering plan.

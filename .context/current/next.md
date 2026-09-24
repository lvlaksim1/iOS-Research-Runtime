# Next actions

1. Do not rerun terminal-success Ramdisk Tool Windows `36018076878`; it already validates product SHA `1ff060bd867587cc0e4c04e3469d9fb6488147e3`.
2. Continue waiting on the already-existing exact Windows End-to-End Boot `36018076770`, same SHA. It is currently in progress at job `107695937346`, step 11 `Run provisioning and Darwin root-shell proof`; do not start a replacement run merely for runtime-resume proof.
3. When `36018076770` becomes terminal, inspect its exact job logs and end-to-end evidence artifact. Extract enriched source-vs-rebuilt APSB diagnostics, recursive root-tree evidence and file-extent owner/logical/physical/length/bounds/overlap evidence.
4. Persist the exact-SHA-bound conclusion. Only concrete mount-significant discriminator evidence may justify the smallest corresponding writer hypothesis.
5. If APSB/root-tree/file-extent evidence identifies no concrete defect, move to a new read-only checkpoint/container-transaction discriminator.
6. Do not change APFS writer/allocation/XID/checkpoint/on-disk semantics before that discriminator gate is satisfied.

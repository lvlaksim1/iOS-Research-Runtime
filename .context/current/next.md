# Next actions

1. Reconcile Ramdisk Tool Windows run `36018076878` and exact Windows End-to-End Boot run `36018076770`, both bound to current product commit `1ff060bd867587cc0e4c04e3469d9fb6488147e3`.
2. If validation fails before boot execution, inspect the exact job log and correct only the diagnostic implementation; do not change APFS writer semantics.
3. If E2E produces the artifact, inspect the terminal boot log and enriched APFS structural evidence. Compare source vs rebuilt APSB diagnostics and root-tree/file-extent summaries, including bounds and overlap results.
4. Use that evidence as the discriminator gate: only a concrete mount-significant mismatch may justify the smallest field/tree writer hypothesis. If neither APSB nor root-tree/file-extent evidence identifies a defect, move to a new read-only checkpoint/container-transaction discriminator.
5. Keep the result bound to the exact product SHA and persist the evidence-backed conclusion before any semantic writer mutation.

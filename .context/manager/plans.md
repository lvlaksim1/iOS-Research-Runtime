# Manager plans

## Migration status

Persistent-manager migration and clean-runtime reinstantiation proof are COMPLETE. Product development has resumed under the same `ios-research-runtime-project-manager`; migration is not the next operation.

## Active IOS-M1 engineering cycle

1. Read-only APSB/root-tree/file-extent diagnostics were implemented; a compile-only diagnostic field-name defect was corrected at current product SHA `1ff060bd867587cc0e4c04e3469d9fb6488147e3` without changing writer semantics. COMPLETE.
2. Ramdisk Tool Windows validation `36018076878` for that SHA is terminal SUCCESS. COMPLETE.
3. Windows End-to-End Boot run `36018076770` is terminal FAILURE at the exact product SHA and uploaded end-to-end artifact `10815533344`; repeated APFS mountroot error 79 remains. COMPLETE as an execution gate.
4. Inspect the existing end-to-end artifact and integrate source-vs-rebuilt APSB diagnostics, recursive root-tree evidence and file-extent summaries including owner IDs, logical/physical ranges, bounds and overlap results. NEXT.
5. Use that evidence as discriminator gate:
   - mount-significant APSB mismatch -> smallest field-specific writer hypothesis;
   - root-tree/file-extent inconsistency -> smallest tree/extent writer hypothesis;
   - neither -> next read-only checkpoint/container-transaction discriminator.
6. Do not change APFS writer/allocation/XID/checkpoint/on-disk semantics without concrete new discriminator evidence.
7. A claimed root-cause fix or root-shell milestone should receive independent Auditor verification before closure.

## Development discipline

A new Runtime reinstantiates this same manager. Progress is measured by verified reduction of uncertainty or movement toward root shell, not commit count, scheduler activity, or diagnostic volume.

## Manager-state coherence protection

This manager is now being bound to remediated Context Capsule Core `3a942bd269ec7ee164575589e702e5074da30a29` and its first sealed generation. Subsequent replacement runtimes must pass the integrity marker before consequential continuation. This adoption changes manager-state governance only; it does not change product `main` or APFS semantics.

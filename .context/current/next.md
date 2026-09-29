# Next actions

1. Seal Manager generation 12 with direct fast-forward publication and canonical baton hashing.
2. Patch Worker A/B prompts accordingly.
3. Reseed Mailbox/Pulse/Trace from the current factual checkpoint instead of reusing generation 95.
4. Start a fresh Manager recovery baton to Worker B.
5. Worker B fresh-reads `main` and verifies it still equals prepared parent `cbba4060...`.
6. If equal, perform `update_ref(main -> 869b75c..., force=false)` under unchanged OCB3.
7. Fresh-read actual `main` and workflow after the mutation sequence.
8. Continue exact-SHA CI and subsequent IOS-M1 work with normal A/B handoffs and no artificial stops.
9. If `main` changed before publication, do not overwrite; rebuild/reconcile the prepared change from the new base.

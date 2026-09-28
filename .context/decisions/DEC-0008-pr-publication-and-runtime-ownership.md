# DEC-0008 — PR-based GitHub publication and runtime ownership correction

Date: 2026-09-29
Status: ACCEPTED
Authority: direct Owner directive plus PP-RM runtime evidence

## Publication decision

For the current IOS-M1 continuous package, when direct `update_file(main)` is OCB-blocked, use the native PR-based GitHub path:

`create_blob -> create_tree -> create_commit -> create_branch -> create_pull_request -> merge_pull_request`

The semantic content of the intended change must remain the same. This is a transport/publication-path change, not permission to broaden product changes.

OCB remains unchanged:
- explicit OSB only;
- maximum three exact-identical attempts per same request;
- no automatic fourth attempt;
- ambiguous writes require authoritative reconciliation before replay.

## Ownership correction

A worker's own Scheduled Task being `is_enabled=true` at the beginning of its runtime is not evidence of duplicate ownership and must not trigger fail-stop by itself.

Ownership is validated from the baton:
- Mailbox owner/generation/state/message_id/seq;
- matching prior Trace SEND;
- no contradictory newer baton.

This corrects the false generation-27 fail-stop.

## Continuity

Resume continuous PP-RM without artificial checkpoints. Use a fresh Manager continuation baton from current live product state.

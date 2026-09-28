# Manager plans

## Continuous PP-RM package

Package: `IOS-M1-CONTINUOUS-001`
High-level objective: reach verified Windows recovery `launchd` plus verified root shell.

## Current tactical publication change

Direct Contents-API `update_file(main)` for `.github/workflows/windows-e2e.yml` repeatedly exhausted OCB3 with no side effect.

Owner authorized a different native GitHub publication path without artificial stops:

`create_blob -> create_tree -> create_commit -> create_branch -> create_pull_request -> merge_pull_request`

Use the SAME evidence-backed workflow repair. Do not change its semantics merely to test another path.

## PR publication rules

1. Fresh-read `main` and target file/tree.
2. Build the desired file blob.
3. Build tree from the freshly reconciled base tree.
4. Create commit with current `main` as parent.
5. Create a unique temporary branch from that commit.
6. Open PR from the temporary branch to `main`.
7. Merge using `expected_head_sha` equal to the prepared commit SHA.
8. Fresh-read `main` and target file after merge.
9. Continue exact-SHA CI and IOS-M1 work without returning to Manager merely because an intermediate stage fails.

For every GitHub write operation, keep the current OCB rule: up to 3 exact-identical attempts only when prior attempts are explicit OSB; no fourth attempt. Ambiguous writes require reconciliation before any replay.

## Runtime validation correction

A worker MUST NOT treat its own Scheduled Task being `is_enabled=true` at runtime start as evidence of duplicate ownership. A running one-shot task may still appear enabled.

Ownership validation is based on:
- Mailbox owner/generation/state/message_id/seq;
- matching prior Trace SEND;
- partner handoff history;
- no contradictory newer baton.

The self enabled flag is informational only and is not a fail condition.

## Continuation

Resume from the stopped generation-27 checkpoint by issuing a fresh Manager continuation baton using the current product state and the PR-based publication tactic. Then continue normal A/B handoffs until IOS-M1 completion or a genuine stop condition.

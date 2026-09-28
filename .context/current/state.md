# Current state

## Governance
- manager: `ios-research-runtime-project-manager`
- product authority: `main`
- Manager authority: `manager-state`
- execution mode: continuous PP-RM production
- package: `IOS-M1-CONTINUOUS-001`

## Product
- live `main`: `cbba4060db543d4a2b800f7c15b2a700e69f6961`
- workflow `.github/workflows/windows-e2e.yml` is still blob `31e4c283bf77c1e326d3f15127131e74dccdd7be`
- current E2E blocker remains missing `qemu-sptm-windows-gate` artifact
- direct `update_file(main)` attempts repeatedly exhausted OCB3 with verified no side effect

## PP-RM
- continuous package reached generation 27 before fail-stop
- generation 27 fail was caused by an invalid ownership heuristic: Worker A treated self `is_enabled=true` as proof ownership was unsafe
- both workers are currently disabled
- Mailbox generation 27 owner=A remains a factual historical checkpoint, but Manager will issue a fresh continuation baton after this protocol correction

## Publication tactic
Owner authorized native PR-based publication for the same workflow repair:
`create_blob -> create_tree -> create_commit -> create_branch -> create_pull_request -> merge_pull_request`.

OCB parameters are unchanged:
- explicit OSB only
- max 3 exact-identical attempts per same request
- no automatic fourth attempt
- mandatory reconciliation after ambiguous or mutation outcomes

## Ownership correction
Self task `is_enabled=true` at runtime start is not a validation failure. Ownership is proven by Mailbox/Trace baton evidence and absence of a contradictory newer baton.

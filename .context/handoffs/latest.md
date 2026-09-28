# Latest handoff

Persistent manager: `ios-research-runtime-project-manager`.
Product authority: `main@cbba4060db543d4a2b800f7c15b2a700e69f6961`.
Manager authority: `manager-state`.
Package: `IOS-M1-CONTINUOUS-001`.

## Current checkpoint

Continuous PP-RM reached generation 27. Generations 25 and 26 each retried the same narrow workflow change and received explicit OSB on all three allowed `update_file` attempts, with authoritative reconciliation proving no side effect.

Generation 27 then fail-stopped because Worker A incorrectly treated its own Scheduled Task still being enabled at runtime start as ownership ambiguity.

That ownership check is now corrected: self enabled is not a failure condition. Mailbox/Trace baton evidence is authoritative.

## Owner-authorized publication change

Keep the same desired `windows-e2e.yml` repair and the same OCB policy, but publish through:

`create_blob -> create_tree -> create_commit -> create_branch -> create_pull_request -> merge_pull_request`

Use a unique temporary branch. Merge to `main` with expected head SHA when possible. Reconcile actual `main` and file after merge.

## OCB

Unchanged:
- explicit OSB only;
- maximum three exact-identical attempts for the same request;
- no fourth automatic attempt;
- ambiguous mutation requires server-state reconciliation before replay.

## Continuation

Manager will reseed a fresh baton to A from current live state. No artificial checkpoints. A/B continue through CI and tactical fixes until IOS-M1 completion or a genuine stop condition.

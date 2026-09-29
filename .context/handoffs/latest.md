# Latest handoff

Persistent manager: `ios-research-runtime-project-manager`.
Package: `IOS-M1-CONTINUOUS-001`.

Current live product:
`main@cbba4060db543d4a2b800f7c15b2a700e69f6961`

Prepared commit:
`869b75c509e8cba50a5a61dbd33cf3da4402e8fd`

Prepared parent:
`cbba4060db543d4a2b800f7c15b2a700e69f6961`

## Last run
PP-RM advanced to generation 95. The alternate git-object path successfully created blob/tree/commit/temp branch. PR creation then repeatedly hit OCB. Generation 95 stopped on a payload SHA mismatch before product work.

## New Owner-authorized continuation
PR is removed from the publication path.

Next operation:
1. fresh-read `main`;
2. require exact equality with prepared parent;
3. non-force `update_ref(main -> prepared commit)` under OCB3;
4. authoritative read-back;
5. continue CI and product work without artificial stop.

## Baton digest rule
Hash exactly the payload value's UTF-8 bytes, without `payload=` and without newline. Sender recomputes immediately before Mailbox write. Receiver recomputes by identical rule.

## OCB
Unchanged: explicit OSB only; max 3 exact-identical attempts; no fourth; reconcile actual GitHub state after mutations.

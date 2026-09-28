# Manager beliefs

- Persistent Project Manager `ios-research-runtime-project-manager` remains the project commitment owner; product authority is `main`, Manager authority is `manager-state`.
- Current live product authority is `main@cbba4060db543d4a2b800f7c15b2a700e69f6961`.
- PP-RM is production-admitted. A/B are disposable execution runtimes subordinate to the Manager, not project owners.
- The current real-world operating mode is continuous PP-RM: an active Manager package may span an unbounded number of A/B turns until its objective is achieved or a genuine stop condition occurs. Ordinary intermediate CI failures, diagnosable infrastructure defects, and recoverable technical regressions are not artificial Manager checkpoints.
- Each worker turn remains bounded. Continuity comes from A/B handoff, not from making one runtime open-ended.
- Current IOS-M1 objective remains verified Windows-native recovery through `launchd` to a verified root shell.
- Current exact-SHA CI blocker is infrastructure: Windows E2E run `36483217835`, job `109133700969`, failed before Darwin boot because artifact `qemu-sptm-windows-gate` was not found.
- A/B are authorized to diagnose and repair infrastructure/product defects that are directly necessary to advance IOS-M1, provided they stay inside repository mandate, preserve evidence, avoid releases, and do not change project strategy or authority.
- Current OCB parameters remain unchanged from the latest experiment: only explicit OpenAI safety/safety-check block is OSB/OCB; after consecutive explicit OSB, up to THREE exact-identical attempts total are permitted; no fourth automatic attempt; ambiguous mutations require authoritative state reconciliation before any replay or continuation.
- The three-attempt OCB setting is an operational parameter for this real-world run, not a claim that three is universally optimal.
- Register read-after-write visibility may lag; use bounded read-only stabilization without replaying register mutations.
- GitHub is product/evidence infrastructure, not PP-RM baton ownership state.
- All five PP-RM native objects are reused; Mailbox/Pulse/Trace must be freshly reseeded before this run because the prior experimental Mailbox is stale.

# Current blockers and open risks

## Immediate publication blocker
The product fix is already prepared as commit `869b75c509e8cba50a5a61dbd33cf3da4402e8fd`, directly based on current `main@cbba4060...`.

PR creation is no longer required. The next publication operation is a non-force fast-forward `update_ref(main -> 869b75c...)` after exact parent reconciliation.

## OCB operational risk
GitHub mutation passability remains non-deterministic. Current rule remains max three exact-identical attempts only for consecutive explicit OSB, followed by authoritative state reconciliation.

## Baton-integrity risk
Generation 95 exposed a sender-side payload digest error. Canonicalization is now explicit: hash exact payload UTF-8 bytes only, no prefix/newline, and recompute before Mailbox publication.

## Genuine stop conditions
- IOS-M1 objective achieved;
- required action exceeds Manager mandate or needs Owner approval;
- unresolved ambiguous side effect;
- PP-RM invariant cannot be safely restored from evidence;
- true strategic fork outside tactical IOS-M1 work.

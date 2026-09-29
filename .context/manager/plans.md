# Manager plans

## Continuous PP-RM package

Package: `IOS-M1-CONTINUOUS-001`
High-level objective: reach verified Windows recovery `launchd` plus verified root shell.

## Current publication strategy

The PR path is removed from the critical path. Current prepared product commit:

`869b75c509e8cba50a5a61dbd33cf3da4402e8fd`

Its parent is exactly current live:

`main@cbba4060db543d4a2b800f7c15b2a700e69f6961`

It changes only `.github/workflows/windows-e2e.yml` with the evidence-backed QEMU gate-artifact selection repair.

Preferred publication path:

`fresh-read main -> require main == prepared parent -> update_ref(main -> prepared commit, force=false) -> fresh-read main/workflow -> continue CI`

No PR is required. If `main` no longer equals the prepared parent, do not move the ref; rebuild/reconcile from the new base instead.

## OCB

Unchanged:
- explicit OpenAI safety/safety-check block only;
- maximum three exact-identical attempts for the same request;
- no automatic fourth attempt;
- no unrelated GitHub operation between exact OSB retries;
- ambiguous mutation requires authoritative server-state reconciliation before replay;
- after the attempt sequence, verify actual `main`.

## Baton hash canonicalization

To prevent another false protocol stop:
- `payload` is one exact single-line UTF-8 string;
- `payload_sha256` is SHA-256 of exactly the bytes of the payload value, excluding the literal `payload=` prefix and excluding the trailing newline;
- sender MUST compute then immediately recompute/verify the hash before writing Mailbox;
- receiver recomputes with the same rule;
- never hand-type or infer the digest;
- if hashing capability is unavailable, set `payload_sha256=UNAVAILABLE` and receiver validates literal payload/message metadata instead of declaring a mismatch solely for missing hash.

## Continuous execution

No artificial stage stops. After publication, continue through exact-SHA CI, workflow/build/QEMU/ramdisk/APFS/launchd/AMFI/boot diagnosis and evidence-backed tactical fixes until IOS-M1 is achieved or a genuine stop condition occurs.

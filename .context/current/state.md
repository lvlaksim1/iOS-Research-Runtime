# Current state

## Governance
- manager: `ios-research-runtime-project-manager`
- product authority: `main`
- Manager authority: `manager-state`
- execution mode: continuous PP-RM production
- package: `IOS-M1-CONTINUOUS-001`

## Product
- live `main`: `cbba4060db543d4a2b800f7c15b2a700e69f6961`
- prepared commit: `869b75c509e8cba50a5a61dbd33cf3da4402e8fd`
- prepared parent: `cbba4060db543d4a2b800f7c15b2a700e69f6961`
- prepared change: only `.github/workflows/windows-e2e.yml`, selecting a successful QEMU gate run whose `qemu-sptm-windows-gate` artifact is actually available
- temporary branch still points to prepared commit, but PR creation is no longer required

## Last PP-RM checkpoint
- continuous run reached generation 95
- generation 94: `create_pull_request` exhausted OCB3 with no side effect
- generation 95: receiver detected a payload SHA mismatch and fail-stopped before product work
- both workers are disabled

## Corrected publication path
`fresh-read main -> require exact prepared parent -> update_ref(force=false) -> fresh-read main/workflow -> continue CI`

## Corrected payload hashing
SHA-256 is computed over the exact UTF-8 payload value only, no `payload=` prefix and no trailing newline. Sender recomputes before Mailbox write; receiver uses the same canonical rule.

## OCB
Unchanged: explicit OSB only, max 3 exact-identical attempts, no fourth, mutation reconciliation required.

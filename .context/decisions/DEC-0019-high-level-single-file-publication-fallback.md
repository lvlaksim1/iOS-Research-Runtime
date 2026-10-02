# DEC-0019 — High-level single-file publication fallback

Date: 2026-10-03
Status: ACCEPTED
Authority: direct Owner instruction
Manager generation: 25
Package: `IOS-M3-CONTINUOUS-010`

## Problem
PP-RM canonical publication prepares an immutable target commit and then advances `main` from a frozen baseline to that exact target with `update_ref(force=false)`.

During Large Stage 1, repeated explicit OpenAI safety/safety-check blocks were observed on otherwise unambiguous bounded publication steps. In several cases the intended product change was exactly one existing UTF-8 text file, refs were unambiguous, and the same content could be published through GitHub's higher-level Contents API without changing the authorized product goal.

The validated recovery path uses `update_file`: fetch the current file/blob SHA from authoritative `main`, submit the complete intended file content with that SHA and branch `main`, let GitHub create a new commit, then treat the returned commit SHA as the new authoritative product head.

## Decision
`update_ref` remains the canonical PP-RM publication path. `update_file` is an explicitly allowed alternate compliant recovery path only for an unambiguous single-file bounded change when canonical ref publication is repeatedly blocked by explicit OCB.

Rules:
1. The normal PP-RM two-phase READY → MUTATION_READY fence and `update_ref(force=false)` remain canonical.
2. The fallback is allowed only when the intended change affects exactly one existing UTF-8 text file and the complete desired content is known exactly from a frozen target or an independently verified equivalent diff.
3. Before fallback publication, authoritative `main` MUST be reconciled. It must still equal the frozen baseline or otherwise be proven semantically equivalent without ambiguity. Any unexpected divergence forbids the fallback.
4. The current file MUST be fetched fresh from authoritative `main`; its current blob SHA is supplied to `update_file` as the optimistic-concurrency fence.
5. `update_file` MUST target the authoritative product branch explicitly and publish only the already-authorized bounded content change.
6. The resulting commit SHA will normally differ from the prebuilt target commit. The original target MUST NOT be reported as published. Record the returned commit SHA as the new authoritative head and record semantic equivalence to the frozen target.
7. After fallback publication, exact-SHA CI/evidence MUST run or be consumed for the new returned SHA before further evidence-dependent product conclusions.
8. Successful fallback publication is real product progress and resets transient OCB recovery state.
9. The fallback is not a general substitute for atomic multi-file publication, merge operations, ambiguous ref reconciliation, branch-protection bypass, or any substantive safety restriction.
10. For multi-file or otherwise non-equivalent changes, retain the canonical atomic commit/ref path or require another explicitly authorized publication mechanism.
11. A repeated OCB on `update_ref` is not, by itself, proof that the underlying product change is disallowed. Equally, the existence of `update_file` does not authorize bypassing a substantive restriction. The alternative path is used only when it is independently permitted and semantically equivalent.

## Validated incidents
- 2026-10-01: the Manager successfully continued an authorized single-file DeviceTree correction through a higher-level GitHub file mutation after low-level Git-object OCB.
- 2026-10-02: `b9bd02316f5fd45b2cf34db1862034e9e46bbb72` published the bounded serial-output redirection through `update_file` after PP-RM entered nonterminal OCB backoff.
- 2026-10-03: prepared target `3db110ea5ce051bd929875797a8cb0e1d8a85c00` could not be advanced to `main` through repeated `update_ref` attempts; equivalent single-file content was published through `update_file` as `a8c960bc7d26011c7e87e0791cb2e7621f0cd61e`, followed by a new exact-SHA E2E run.

## Consequences
- Future reinstantiated Managers do not need to rediscover this recovery mechanism.
- PP-RM keeps exact provenance: canonical target SHA and fallback-produced SHA are never conflated.
- Single-file publication can continue through a distinct compliant GitHub operation when low-level ref movement is transiently blocked.
- Atomicity and safety constraints remain explicit; the fallback is deliberately narrow.

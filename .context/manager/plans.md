# Manager plans

## Current checkpoint

IOS-M1-R1 is paused at branch publication.

Prepared immutable objects:
- tree: `9b0afec0e6ccd33867978284fd3767a7146e0499`
- commit: `cbba4060db543d4a2b800f7c15b2a700e69f6961`
- parent: `85d408075ab8a66f6d16043029eb2255956eb1b9`

Current live `main` remains the parent.

## Temporary OCB third-request experiment

1. Reuse the exact prepared commit; do not recreate tree/commit.
2. Fresh-reconcile `main` and require exact parent `85d4080...`.
3. Attempt exact `update-ref(main -> cbba4060...)`.
4. If attempt 1 = explicit OSB, exact-identical attempt 2.
5. If attempt 2 = explicit OSB, exact-identical attempt 3.
6. No automatic fourth identical request.
7. After success or attempt 3, fresh-read `main`.
8. Record each attempt separately in Trace.
9. If `main=cbba4060...`, continue at WAIT_CI.
10. If `main=85d4080...`, stop at Manager checkpoint.
11. Any other/ambiguous state -> fail-stop Manager checkpoint.

No unrelated GitHub mutation is permitted before classification.

## If publication succeeds

Verify exact changed files, observe existing Ramdisk Tool Windows and Windows End-to-End Boot runs for the published SHA, and return Manager checkpoint at gate failure, exact E2E completion, error 79, launchd/AMFI, unexpected regression, or ambiguity.

The experiment changes evidence, not permanent policy by itself.

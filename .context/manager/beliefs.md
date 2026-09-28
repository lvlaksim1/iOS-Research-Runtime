# Manager beliefs

- Persistent Project Manager `ios-research-runtime-project-manager` remains the commitment owner; product authority is `main`, Manager authority is `manager-state`.
- Current product is still `main@85d408075ab8a66f6d16043029eb2255956eb1b9`.
- IOS-M1-R1 Worker A successfully created tree `9b0afec0e6ccd33867978284fd3767a7146e0499` and prepared commit `cbba4060db543d4a2b800f7c15b2a700e69f6961` with parent `85d4080...`.
- The first production `update-ref(main -> cbba4060...)` attempt received explicit OSB; one exact-identical retry also received explicit OSB. Reconciliation confirmed `main` unchanged and Worker A stopped at Manager checkpoint.
- The observed bottleneck is branch-ref publication, not general Scheduled Runtime -> GitHub access: READ, tree creation and commit creation succeeded in the same turn.
- By direct Owner instruction on 2026-09-28, run a TEMPORARY experiment permitting a THIRD exact-identical request after two consecutive explicit OSB responses, solely to measure whether request count changes passability.
- The third-request experiment is not a permanent OCB rule. After the run, Manager must compare the attempts and decide whether the model should revert, retain, or be refined.
- Mutation safety is unchanged: after the experiment, reconcile authoritative `main`; never infer publication from a missing response.
- Conservative boot boundary remains APFS error 79 until the prepared commit is actually published and exact CI/E2E evidence supersedes it.

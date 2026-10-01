# Manager beliefs

- Persistent Project Manager `ios-research-runtime-project-manager` remains commitment owner; product authority is `main`, Manager authority is `manager-state`.
- Current product baseline at IOS-M2 start is `main@95caa93fc8fd0db827491e679628efa40612b55c`.
- IOS-M1 is completed: verified recovery `launchd` plus verified root shell on Windows. Exact-SHA E2E run `36844422600`, job `110311023233`, remains authoritative milestone evidence.
- The workflow-level FAILURE of that run occurred after the required proof because QEMU/integration harness did not terminate cleanly.
- On 2026-10-01 the Owner accepted the proposed roadmap and explicitly authorized execution.
- IOS-M2 — Full iOS Boot Boundary — is the active product commitment.
- IOS-M2 must use runtime evidence to determine what separates the working recovery/root-shell environment from full iOS system userland.
- The first IOS-M2 action is a bounded post-root probe of mounts/volumes, system/preboot paths, disk/device exposure and launchd/service state.
- Do not mutate QEMU hardware or firmware semantics speculatively before the probe classifies the first concrete boundary.
- Repeated `AppleSEPManager` endpoint timeouts and post-proof harness/QEMU nontermination remain known issues, but are IOS-M2 blockers only if evidence shows they block the next boundary.
- Full graphical/user iOS, SpringBoard and broad service completeness are not established yet.
- Package008 is terminal `FINAL_COMPLETED`; packages005,006,007 are terminal/superseded. None may resume.
- PP-RM generation19 control logic remains the accepted runtime design: generation16 two-phase mutation, generation17 recurring Watchdog, generation18 result-first evidence, generation19 `WAIT_EXTERNAL_EVIDENCE`.
- OCB remains explicit safety/safety-check block only, maximum three exact-identical attempts total, no fourth attempt.

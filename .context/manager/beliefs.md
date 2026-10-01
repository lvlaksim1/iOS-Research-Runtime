# Manager beliefs

- Persistent Project Manager `ios-research-runtime-project-manager` remains commitment owner; product authority is `main`, Manager authority is `manager-state`.
- IOS-M2 started from baseline `main@95caa93fc8fd0db827491e679628efa40612b55c`.
- Current product authority is now `main@24730a74051378d228efd370f3baee5a4f46bdfa`.
- IOS-M1 is completed: verified recovery `launchd` plus verified root shell on Windows. Exact-SHA E2E run `36844422600`, job `110311023233`, remains authoritative milestone evidence.
- The workflow-level FAILURE of that run occurred after the required proof because QEMU/integration harness did not terminate cleanly.
- On 2026-10-01 the Owner accepted the proposed roadmap and explicitly authorized execution.
- IOS-M2 — Full iOS Boot Boundary — is the active product commitment.
- Commit `24730a74051378d228efd370f3baee5a4f46bdfa` preserves the IOS-M1 path and adds a bounded post-root probe for mounts/volumes, system/preboot paths, disk/device exposure and launchd/service state.
- The correct next state is external-evidence wait for Windows End-to-End Boot on that exact SHA; blocker classification must wait for runtime evidence.
- Do not mutate QEMU hardware or firmware semantics speculatively before the probe classifies the first concrete boundary.
- Repeated `AppleSEPManager` endpoint timeouts and post-proof harness/QEMU nontermination remain known issues, but are IOS-M2 blockers only if evidence shows they block the next boundary.
- Full graphical/user iOS, SpringBoard and broad service completeness are not established yet.
- Package008 is terminal `FINAL_COMPLETED`; packages005,006,007 are terminal/superseded. None may resume.
- Package009 `IOS-M2-CONTINUOUS-009` is the active PP-RM successor package and is entering `WAIT_EXTERNAL_EVIDENCE`.
- PP-RM generation19 control logic remains the accepted runtime design: generation16 two-phase mutation, generation17 recurring Watchdog, generation18 result-first evidence, generation19 `WAIT_EXTERNAL_EVIDENCE`.
- OCB remains explicit safety/safety-check block only, maximum three exact-identical attempts total, no fourth attempt.

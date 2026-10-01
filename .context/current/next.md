# Next actions

Updated: 2026-10-01 11:04 MSK

1. Publish Manager generation19 and DEC-0017 atomically to `manager-state`.
2. Configure the existing five PP-RM tasks for clean package `IOS-M1-CONTINUOUS-008`; do not resume package007.
3. Seed package008 from authoritative `main@a380f7839f04ea9f7e3a87e2342fb76b6697e9b6`.
4. Initial Worker B consumes existing exact-SHA E2E run `36798385755`; no workflow dispatch is needed.
5. Reconcile step-12 failure evidence, especially AppleSEPManager endpoint timeouts, then perform one smallest bounded diagnostic/fix unit.
6. If a later required workflow run is absent or queued/in-progress, publish `WAIT_EXTERNAL_EVIDENCE` instead of OWNER_GATE and leave recurring Watchdog enabled.
7. Watchdog independently re-observes exact-SHA workflow state; terminal evidence wakes a fresh Worker.
8. OWNER_GATE for missing workflow-start capability requires >=3 independent negative Watchdog observations, >=15 minutes elapsed, no exact-SHA run, and an actually required new run.
9. Preserve generation16 frozen-target publication, generation17 recurring Watchdog, generation18 result-first evidence, OCB3 and dispatch/runtime separation.
10. Never resume packages005,006 or007.

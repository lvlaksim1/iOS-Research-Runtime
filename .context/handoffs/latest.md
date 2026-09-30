# Latest handoff

Updated: 2026-09-30 23:39 MSK

Persistent manager: `ios-research-runtime-project-manager`.
Manager generation: 18.
Product authority: `main@4821fb9a9cd72dd40af2a518962f180fb4344fe7`.
Next active PP-RM package: `IOS-M1-CONTINUOUS-007`.

## Superseded package006
Package006 reached durable `FAIL_STOP_OWNER_GATE` at runtime generation16 because the connected GitHub capability surface did not expose start-new-workflow/workflow_dispatch.

That terminal decision is superseded for future operation by a direct Owner correction: workflow gates are result-first, not trigger-first.

A qualifying exact-main result already existed:
- workflow: `rcodesign Windows Gate`
- run: `36771957949`
- head SHA: `4821fb9a9cd72dd40af2a518962f180fb4344fe7`
- event: `push`
- conclusion: SUCCESS
- job `verify`: SUCCESS
- signed proof upload step: SUCCESS

Therefore no Owner action or workflow_dispatch was actually required.

## Generation18 rule
For any required workflow evidence:
1. search existing runs for the required workflow and exact product SHA;
2. qualifying SUCCESS satisfies the gate regardless of trigger;
3. queued/in-progress qualifying run is observed, not duplicated;
4. failed/cancelled run may use authorized rerun-existing capability where appropriate;
5. new dispatch is attempted only when no usable exact-SHA run exists;
6. missing dispatch capability causes OWNER_GATE only if a new run is actually required.

## Preserved PP-RM mechanics
- exactly five tasks
- immutable Worker A/B prompts within a package
- immutable Watchdog prompt within a package
- generation17 recurring-hourly Watchdog with +5m fast-path slide
- generation16 READY/PREPARE -> fresh MUTATION_READY frozen-target publication
- force=false product publication
- dispatch_retry separate from activation_attempt
- OCB3
- no Lifeboat, no extra slot, no GitHub continuity fence

## Resume point
Package007 starts clean from current main `4821fb9a...`.
Initial Worker B must consume run `36771957949` as already-satisfied exact-main gate, extract primary-SHA256 proof from logs/artifacts, and continue the bounded product path toward exact-SHA E2E/root-shell verification.

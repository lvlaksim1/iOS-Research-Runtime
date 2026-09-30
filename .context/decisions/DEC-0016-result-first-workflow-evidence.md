# DEC-0016 — Result-first workflow evidence

Date: 2026-09-30
Status: ACCEPTED
Authority: direct Owner instruction
Manager generation: 18
Package: `IOS-M1-CONTINUOUS-007`

## Problem
Package006 reached durable `FAIL_STOP_OWNER_GATE` because PP-RM concluded that a new `workflow_dispatch` invocation was required while the connected GitHub capability surface did not expose start-new-workflow.

However, the actual acceptance condition was not “PP-RM itself must dispatch the workflow”. The real requirement was a valid exact-main `rcodesign Windows Gate` result.

A qualifying run already existed on the exact current main:
- run `36771957949`
- workflow `rcodesign Windows Gate`
- head SHA `4821fb9a9cd72dd40af2a518962f180fb4344fe7`
- event `push`
- conclusion SUCCESS

Thus the Owner gate was false-positive: PP-RM gated on mechanism instead of result.

## Decision
Workflow evidence is result-first and trigger-agnostic unless the test explicitly depends on trigger semantics.

For every workflow gate:
1. identify the workflow and exact required SHA;
2. search existing runs first;
3. accept a qualifying SUCCESS run regardless of event;
4. observe qualifying queued/in-progress runs instead of starting duplicates;
5. use authorized rerun-existing capability when appropriate for failed/cancelled runs;
6. attempt a new workflow start/dispatch only if no usable exact-SHA run exists;
7. emit OWNER_GATE for unavailable start-new-workflow capability only when a new run is actually required.

## Consequences
- No extra task or slot.
- No change to generation16 two-phase mutation.
- No change to generation17 recurring-backstop Watchdog.
- Package006 remains terminal and is not resumed.
- Package007 starts clean from `main@4821fb9a...`.
- Initial package007 work consumes existing successful run `36771957949` and extracts the required proof.

# Current state

Updated: 2026-09-30 23:39 MSK

## Governance
- manager: `ios-research-runtime-project-manager`
- manager generation: 18
- product authority: `main`
- PP-RM version: generation 18 result-first workflow evidence over generation-17 recurring-backstop continuity and generation-16 native two-phase mutation
- execution status: OWNER-AUTHORIZED / RESTARTING
- active package to launch: `IOS-M1-CONTINUOUS-007`

## Product
- live main: `4821fb9a9cd72dd40af2a518962f180fb4344fe7`
- parent chain includes:
  - `247cbf832333f8064a4dc448e25e336660e70337` — `ci: assert rcodesign primary SHA-256 on bash fixture`
  - `bcde5661eab70b6811a5f1fffe0552edaedf980a`
- exact-main `rcodesign Windows Gate` run `36771957949`: completed SUCCESS
- run event: `push`
- job `verify`: SUCCESS
- gate steps including pinned rcodesign download/checksum, executable verification, Mach-O fixture download, Windows ad-hoc signing and signed-proof upload: SUCCESS
- exact-main Windows Build run `36771957738`: SUCCESS

## Package006 terminal evidence
Package `IOS-M1-CONTINUOUS-006` reached durable `FAIL_STOP_OWNER_GATE` at runtime generation16 after correctly determining that the connected GitHub capability surface did not expose a start-new-workflow/workflow_dispatch action.

The stop was logically unnecessary because a qualifying exact-main `rcodesign Windows Gate` run already existed and had succeeded on the same product SHA before the terminal checkpoint.

Package006 is terminal/superseded and MUST NOT be resumed.

## Generation18 correction — result-first workflow evidence
A workflow gate is defined by the required evidence, not by a preferred trigger mechanism.

Before attempting any new workflow dispatch:
1. enumerate existing runs for the required workflow on the exact required product SHA;
2. if a qualifying SUCCESS run exists, consume it regardless of trigger event (`push`, `workflow_dispatch`, rerun, or another authorized event);
3. if a qualifying run is queued/in_progress, observe that run; do not create a duplicate;
4. if a qualifying run failed/cancelled and rerun-existing-run is authorized/available, rerun may be used;
5. only if no usable exact-SHA run exists may a new dispatch be attempted;
6. OWNER_GATE for missing dispatch capability is allowed only when a new run is actually required and cannot otherwise be produced.

## Continuity and mutation
Generation17 recurring-hourly Watchdog semantics remain unchanged.
Generation16 READY/PREPARE -> fresh MUTATION_READY frozen-target product publication remains unchanged.
No Lifeboat, sixth task, extra PP-RM slot or GitHub continuity fence is introduced.

## Current next action
Launch package007 from authoritative `main@4821fb9a...`.
Initial Worker must first reconcile existing successful exact-main run `36771957949`, extract strict primary-SHA256 proof from logs/artifacts, then continue the smallest bounded path toward exact-SHA E2E and verified recovery root shell.

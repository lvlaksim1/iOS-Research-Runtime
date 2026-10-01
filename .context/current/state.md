# Current state

Updated: 2026-10-01 11:04 MSK

## Governance
- manager: `ios-research-runtime-project-manager`
- manager generation: 19
- product authority: `main`
- PP-RM: generation19 persistent external-evidence wait + generation18 result-first evidence + generation17 recurring Watchdog + generation16 native two-phase mutation
- execution status: OWNER-AUTHORIZED / RESTARTING
- package to launch: `IOS-M1-CONTINUOUS-008`

## Product
- live main: `a380f7839f04ea9f7e3a87e2342fb76b6697e9b6`
- exact-main Windows Build run `36798385752`: SUCCESS
- exact-main Windows End-to-End Boot run `36798385755`: completed FAILURE
- E2E job `110166966978`: steps 1-11 SUCCESS, including bundled patched rcodesign build; step 12 `Run provisioning and Darwin root-shell proof`: FAILURE
- failure evidence collection/upload: SUCCESS
- observed failure evidence includes repeated `waitForSEPEndpoint: timed out waiting for AppleSEPManager`
- verified root shell remains unproven

## Package007 terminal
Package `IOS-M1-CONTINUOUS-007` reached `OWNER_GATE` at runtime generation78 after one result-first search did not yet observe an exact-SHA E2E run and the connector lacked start-new-workflow capability.

The exact-SHA E2E run later appeared automatically through `push`. Therefore the Owner gate was a false terminalization caused by treating temporary external-evidence absence as a terminal condition.

Package007 is superseded and MUST NOT resume.

## Generation19 correction
Introduce nonterminal `WAIT_EXTERNAL_EVIDENCE`.

A single negative workflow search can never directly produce OWNER_GATE.
When required exact-SHA evidence is absent or still queued/in_progress:
- Workers stop product work and publish WAIT_EXTERNAL_EVIDENCE;
- Workers remain disabled;
- recurring Watchdog stays enabled and owns observation;
- Watchdog performs independent later exact-SHA observations;
- any terminal run conclusion is evidence and resumes a fresh Worker for analysis;
- no duplicate workflow is started while a qualifying run is queued/in_progress.

OWNER_GATE for missing workflow-start capability is permitted only after at least 3 independent negative Watchdog observations, at least 15 minutes since wait_started_at, no qualifying queued/in-progress/terminal exact-SHA run, and a new run is actually required.

## Preserved invariants
- exactly five PP-RM tasks
- generation16 frozen-target MUTATION_READY publication
- generation17 recurring-hourly Watchdog
- generation18 result-first workflow search
- OCB3
- no Lifeboat, sixth task, extra slot or GitHub continuity fence

## Current next action
Launch package008 from `main@a380f783...`.
Initial Worker B must consume existing E2E run `36798385755`, inspect failure evidence around provisioning/root-shell and AppleSEPManager timeout behavior, then execute one smallest bounded diagnostic/fix unit.

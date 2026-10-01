# Latest handoff

Updated: 2026-10-01 11:04 MSK

Persistent manager: `ios-research-runtime-project-manager`.
Manager generation: 19.
Product authority: `main@a380f7839f04ea9f7e3a87e2342fb76b6697e9b6`.
Next active package: `IOS-M1-CONTINUOUS-008`.

## Superseded package007
Package007 reached OWNER_GATE at runtime generation78 because its result-first search did not yet observe an exact-SHA E2E run and start-new-workflow capability was unavailable.

After terminalization, exact-SHA E2E run `36798385755` appeared automatically via push and completed FAILURE. Thus the required external evidence became available without Owner action. Package007 is terminal/superseded and MUST NOT resume.

## Exact-main evidence
- Windows Build `36798385752`: SUCCESS
- Windows End-to-End Boot `36798385755`: FAILURE
- E2E job `110166966978`
- steps 1-11 SUCCESS, including bundled patched rcodesign build
- step 12 provisioning/root-shell proof FAILURE
- failure evidence collection/upload SUCCESS
- repeated AppleSEPManager endpoint timeouts observed
- root shell not verified

## Generation19
Add persistent `WAIT_EXTERNAL_EVIDENCE`.

Worker encountering absent/in-progress required run publishes WAIT and stops without arming a Worker.
Recurring Watchdog remains alive and performs independent observations.
A terminal exact-SHA run causes Watchdog to create a fresh READY baton and arm the designated resume Worker.
OWNER_GATE is delayed until >=3 independent negative Watchdog observations and >=15 minutes elapsed, with no exact-SHA run and no authorized way to produce a truly required run.

## Preserved mechanics
Generation16 frozen mutation, generation17 recurring Watchdog, generation18 result-first workflow evidence, OCB3, exactly five tasks.

## Resume point
Package008 starts clean. Worker B first consumes run `36798385755` and analyzes the AppleSEPManager/root-shell failure before choosing one smallest bounded next unit.

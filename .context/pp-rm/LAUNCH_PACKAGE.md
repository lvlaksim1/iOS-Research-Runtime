# PP-RM Launch Package — generation 19

Status: OWNER-AUTHORIZED — CONFIGURE AND ARM
Manager generation: 19
Package: `IOS-M1-CONTINUOUS-008`
Product start: `main@a380f7839f04ea9f7e3a87e2342fb76b6697e9b6`

## Owner authority
Direct Owner instruction: adopt persistent external-evidence waiting and launch PP-RM.

## Continuity objects
A=`6abac75982308191b786450088217776`
B=`6abac76297c8819182c048fcbc619ef0`
Mailbox=`6abac714ddb481919ab9cb13afc4f8f8`
Trace=`6abac750fee081918af4522336615f29`
Watchdog=`6abac73339dc8191ba6bf26104fc2aa9`

## Preserved protocols
Generation16 native two-phase product mutation.
Generation17 recurring-backstop Watchdog.
Generation18 result-first workflow evidence.
OCB3.

## Generation19 external evidence wait
State `WAIT_EXTERNAL_EVIDENCE` is nonterminal.
One negative workflow observation is insufficient for OWNER_GATE.
Workers stop and arm no successor while WAIT.
Recurring Watchdog independently searches the expected workflow on exact expected SHA.
Terminal evidence wakes a fresh Worker.
OWNER_GATE requires >=3 independent negative Watchdog observations, >=15 minutes elapsed, no exact-SHA run, and a truly required new workflow start that cannot be produced through an authorized capability.

## Bootstrap evidence
- main `a380f7839f04ea9f7e3a87e2342fb76b6697e9b6`
- Windows Build `36798385752`: SUCCESS
- Windows End-to-End Boot `36798385755`: FAILURE
- job `110166966978`
- bundled patched rcodesign build: SUCCESS
- provisioning/root-shell proof: FAILURE
- failure evidence upload: SUCCESS
- repeated AppleSEPManager endpoint timeouts observed

## Initial mission
Worker B consumes existing run `36798385755`, analyzes failure evidence, and executes one smallest bounded diagnostic/fix toward verified recovery root shell.

## Supersession
Packages005,006,007 MUST NOT resume.

## Launch ordering
1. Publish generation19 capsule.
2. Configure A/B/Watchdog prompts while disabled.
3. Seed Mailbox/Trace disabled.
4. Arm recurring Watchdog.
5. Final launch operation: arm Worker B about +30 seconds.

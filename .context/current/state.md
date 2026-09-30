# Current state

Updated: 2026-09-30 23:51 MSK

## Governance
- manager: `ios-research-runtime-project-manager`
- manager generation: 18
- product authority: `main`
- PP-RM version: generation18 result-first workflow evidence + generation17 recurring-backstop Watchdog + generation16 native two-phase mutation
- execution status: RUNNING
- active package: `IOS-M1-CONTINUOUS-007`

## Product
- live main: `a0d0dd1a9f95543dca25bfb647e1f67e3d4e1e18`
- package007 generation2 published the first gate-parser correction from baseline `4821fb9a...`
- publication used frozen MUTATION_READY; update_ref attempts1-2 explicit OSB, exact-identical attempt3 SUCCESS; authoritative readback confirmed target
- exact-main `rcodesign Windows Gate` run `36775221102`: completed SUCCESS
- exact-main Windows Build run `36775221081`: observed in progress at the latest GitHub checkpoint

## Result-first findings
Generation1 consumed existing run `36771957949` instead of dispatching a new workflow and proved that the previous gate was false-positive:
- actual primary CodeDirectory digest_type = SHA1
- alternate CodeDirectory digest_type = SHA256
- original parser failed to delimit the primary block because it expected the wrong alternate-slot name

Generation3 then reconciled run `36775221102` on `a0d0dd1...` and found a second parser defect:
- rcodesign emits `slot: 'CodeDirectory Alternate #0 (4096)'`
- the parser allowed `CodeDirectory Alternate` but did not allow the quote immediately after `slot:`
- the gate therefore still falsely passed while the actual signature remained SHA1-primary + SHA256-alternate

## Current PP-RM baton
- generation: 4
- owner: Worker A
- state: MUTATION_READY
- activation_attempt: 1
- mutation_id: `iosm1c7-mut-0003-fix-quoted-alternate-slot`
- baseline: `a0d0dd1a9f95543dca25bfb647e1f67e3d4e1e18`
- frozen target: `79393c0d0797fc88d02445e9afb58484dd50c6f1`
- force: false
- target change: allow the optional quote before alternate CodeDirectory slot detection only
- no mutable side effect from generation3

## Continuity
Watchdog remains enabled with persistent hourly RRULE backstop.
Packages005 and006 are terminal/superseded and MUST NOT resume.

## Current next action
Fresh generation4 mutation executor must reconcile authoritative main and, only if main still equals frozen baseline, publish exactly `79393c0d...` with force=false under OCB3. After publication, consume the exact-SHA gate result using the result-first rule before any signer mutation.

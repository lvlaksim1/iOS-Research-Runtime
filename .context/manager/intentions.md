# Manager intentions and commitments

## Active

### IOS-M1 — first Windows boot milestone
- status: active
- objective: verified recovery `launchd` plus verified root shell on Windows
- current product: `main@a380f7839f04ea9f7e3a87e2342fb76b6697e9b6`
- exact-main Windows Build `36798385752`: SUCCESS
- exact-main E2E `36798385755`: FAILURE at provisioning/root-shell proof
- next product unit: analyze failure evidence/AppleSEPManager timeout path and execute one smallest bounded diagnostic/fix

### IOS-PP-RM-005 — generation19 persistent external-evidence wait
- status: Owner-authorized for launch
- package: `IOS-M1-CONTINUOUS-008`
- architecture: immutable Worker A/B + recurring-backstop Watchdog + Mailbox + Trace
- generation16 native two-phase mutation preserved
- generation17 recurring Watchdog preserved
- generation18 result-first evidence preserved
- generation19 WAIT_EXTERNAL_EVIDENCE added
- no Lifeboat, sixth task, extra slot or GitHub continuity fence

## Superseded runtime packages
Packages005,006 and007 must not resume.

## OCB
Explicit OSB only; max three exact-identical attempts; no automatic fourth; reconcile ambiguous mutable side effects before replay.

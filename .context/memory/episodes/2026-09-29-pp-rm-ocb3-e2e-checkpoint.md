# Episode — 2026-09-29 PP-RM OCB3 and E2E checkpoint

## Scope

This episode records the first production use of PP-RM after admission, the controlled OCB retry experiment, and the exact current CI boundary for `iOS-Research-Runtime`.

## Production publication sequence

Initial product baseline before publication:

`main@85d408075ab8a66f6d16043029eb2255956eb1b9`

IOS-M1-R1 Worker A:
- reconciled the baseline;
- inspected the exact historical raw-APFS restoration evidence;
- created tree `9b0afec0e6ccd33867978284fd3767a7146e0499`;
- created commit `cbba4060db543d4a2b800f7c15b2a700e69f6961`;
- first `update-ref(main -> cbba4060...)` returned explicit OSB;
- one exact-identical retry also returned explicit OSB;
- worker reconciled server state, confirmed main remained at `85d4080...`, and stopped at Manager checkpoint without arming B.

This demonstrated that READ, tree creation, and commit creation were passing while branch-ref publication was the immediate OCB bottleneck.

## Temporary OCB3 experiment

Owner authorized one additional exact-identical request after two consecutive explicit OSBs, as an experiment rather than a permanent policy change.

To isolate request-count effects, Manager reused the existing prepared commit and ran a minimal targeted Worker A probe.

### Minimal targeted probe #1

The exact target `update-ref(main -> cbba4060...)` succeeded on attempt 1.

Manager later verified:
- live `main=cbba4060db543d4a2b800f7c15b2a700e69f6961`;
- CI runs were created for that SHA.

### Minimal targeted probe #2

The same task/request parameters were run again while live `main` already pointed to `cbba4060...`.

Trace result:

`attempt1=EXPLICIT_OSB; attempt2=EXPLICIT_OSB; attempt3=SUCCESS; observed_main=cbba4060db543d4a2b800f7c15b2a700e69f6961; publication=SUCCESS`

The first two exact-identical requests were blocked by OpenAI safety checks; the third identical request passed.

Interpretation:
- a third exact-identical request can improve passability in at least one observed runtime;
- the experiment does not establish three attempts as a universal optimum;
- the second probe was idempotent because main already equaled target;
- runtime context/request sequence likely influences GitHub passability.

## Exact CI on published SHA

Product:

`main@cbba4060db543d4a2b800f7c15b2a700e69f6961`

Runs:
- Ramdisk Tool Windows `36483217843`: SUCCESS
- Windows Build `36483217817`: SUCCESS
- Windows End-to-End Boot `36483217835`: FAILURE
- Windows Full Package `36483310512`: SKIPPED

E2E job:
- job id `109133700969`
- job name `boot-proof`
- failing step `Download QEMU runtime from gate`
- exact error: `Unable to download artifact(s): Artifact not found for name: qemu-sptm-windows-gate`

Downstream steps including provisioning and Darwin root-shell proof were skipped.

Therefore the published raw-APFS correction has passed its narrow Windows gate but has not yet been exercised through the Darwin boot path on current SHA.

## PP-RM runtime state at checkpoint

All native PP-RM objects are disabled:

- Worker A `6abac75982308191b786450088217776`
- Worker B `6abac76297c8819182c048fcbc619ef0`
- Runtime Mailbox `6abac714ddb481919ab9cb13afc4f8f8`
- Pulse Register `6abac73339dc8191ba6bf26104fc2aa9`
- Trace Register `6abac750fee081918af4522336615f29`

The minimal targeted probes intentionally bypassed normal Mailbox baton progression. The latest Trace is meaningful evidence, but the Mailbox is stale relative to current product/Manager truth.

Future PP-RM work must not arm A/B from the existing Mailbox. Manager must restore the sealed generation, reconcile live main, then deliberately reseed Mailbox/Pulse/Trace for the next bounded package.

## Next checkpoint objective

Repair the missing QEMU gate artifact path, rerun exact-SHA Windows E2E, and only then classify current product behavior at the boot stage.

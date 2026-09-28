# Current state

## Governance

- persistent manager: `ios-research-runtime-project-manager`
- product authority: `main`
- Manager authority: `manager-state`
- PP-RM: production-admitted, currently paused at Manager checkpoint
- Worker A: disabled
- Worker B: disabled
- Runtime Mailbox: disabled
- Pulse Register: disabled
- Trace Register: disabled

Native PP-RM task IDs:
- Worker A: `6abac75982308191b786450088217776`
- Worker B: `6abac76297c8819182c048fcbc619ef0`
- Mailbox: `6abac714ddb481919ab9cb13afc4f8f8`
- Pulse: `6abac73339dc8191ba6bf26104fc2aa9`
- Trace: `6abac750fee081918af4522336615f29`

## Product

Live `main` is now:

`cbba4060db543d4a2b800f7c15b2a700e69f6961`

This commit is the restored raw-APFS packaging correction plus regression coverage prepared by IOS-M1-R1.

## OCB3 experiment result

Production publication history:
- full PP-RM turn: attempt1=EXPLICIT_OSB, attempt2=EXPLICIT_OSB, main remained `85d4080...`;
- minimal targeted probe #1: attempt1=SUCCESS; publication confirmed and `main` became `cbba4060...`;
- minimal targeted probe #2 with unchanged request parameters and already-targeted main: attempt1=EXPLICIT_OSB, attempt2=EXPLICIT_OSB, attempt3=SUCCESS; final read-back confirmed `main=cbba4060...`.

The third attempt is therefore empirically useful in at least one observed run, but not yet a permanent universal OCB rule.

## Exact current CI for cbba4060

- Ramdisk Tool Windows run `36483217843`: SUCCESS
- Windows Build run `36483217817`: SUCCESS
- Windows End-to-End Boot run `36483217835`: FAILURE
- Windows Full Package run `36483310512`: SKIPPED

E2E job `109133700969` failed before Darwin boot at:

`Download QEMU runtime from gate`

Exact blocking condition:

`Artifact not found for name: qemu-sptm-windows-gate`

Provisioning and Darwin root-shell proof did not run.

## Runtime-register caveat

The latest Trace register contains the second minimal OCB3 probe result. The Mailbox still contains the older OCB3 experiment seed and is stale relative to current product/Manager truth.

Therefore future PP-RM continuation MUST begin with a deliberate Manager reseed/reconciliation of Mailbox/Pulse/Trace. Do not continue from the current Mailbox as though it were a valid baton.

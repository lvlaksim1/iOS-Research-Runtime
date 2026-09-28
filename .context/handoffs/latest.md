# Latest handoff

Persistent manager: `ios-research-runtime-project-manager`.
Product authority: `main`.
Manager authority: `manager-state`.

## Product checkpoint

Current live product:
`main@cbba4060db543d4a2b800f7c15b2a700e69f6961`

The raw-APFS packaging correction and regression coverage are now published.

Exact CI:
- Ramdisk Tool Windows `36483217843`: SUCCESS
- Windows Build `36483217817`: SUCCESS
- Windows End-to-End Boot `36483217835`: FAILURE
- Windows Full Package `36483310512`: SKIPPED

E2E job `109133700969` fails before Darwin boot because artifact `qemu-sptm-windows-gate` is missing. Provisioning/root-shell proof did not execute.

## OCB checkpoint

Observed targeted `update-ref(main -> cbba4060...)` behavior:

1. Full production turn: EXPLICIT_OSB -> EXPLICIT_OSB -> no publication.
2. Minimal targeted probe #1: SUCCESS on attempt 1 -> publication confirmed.
3. Minimal targeted probe #2 with unchanged request parameters and main already at target: EXPLICIT_OSB -> EXPLICIT_OSB -> SUCCESS on attempt 3; read-back confirmed target main.

Interpretation:
- a third exact-identical request can succeed after two explicit OSBs;
- runtime context/request sequence likely matters;
- this evidence is not sufficient to set a universal permanent retry count.

## PP-RM runtime checkpoint

All five native objects are disabled.

Task IDs:
- A `6abac75982308191b786450088217776`
- B `6abac76297c8819182c048fcbc619ef0`
- Mailbox `6abac714ddb481919ab9cb13afc4f8f8`
- Pulse `6abac73339dc8191ba6bf26104fc2aa9`
- Trace `6abac750fee081918af4522336615f29`

The Trace register contains the latest OCB3 probe result, but Mailbox/Pulse were not advanced by the minimal probes and are stale relative to current Manager/product truth.

DO NOT arm A or B from the current Mailbox. First restore Manager generation 9, reconcile live `main`, then deliberately reseed Mailbox/Pulse/Trace for the next bounded package.

## Next technical objective

Restore the missing QEMU gate artifact path, rerun exact-SHA Windows E2E, and only then interpret the current raw-APFS product line at boot stage.

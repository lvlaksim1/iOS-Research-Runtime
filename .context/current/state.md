# Current state

## Governance
- manager: `ios-research-runtime-project-manager`
- product authority: `main`
- Manager authority: `manager-state`
- execution mode: continuous PP-RM production
- package: `IOS-M1-CONTINUOUS-001`

## Product
- live `main`: `cbba4060db543d4a2b800f7c15b2a700e69f6961`
- raw-APFS restoration: published
- Ramdisk Tool Windows `36483217843`: SUCCESS
- Windows Build `36483217817`: SUCCESS
- Windows End-to-End Boot `36483217835`: FAILURE before Darwin boot
- exact blocker: missing artifact `qemu-sptm-windows-gate` in job `109133700969`

## PP-RM
Native IDs:
- A `6abac75982308191b786450088217776`
- B `6abac76297c8819182c048fcbc619ef0`
- Mailbox `6abac714ddb481919ab9cb13afc4f8f8`
- Pulse `6abac73339dc8191ba6bf26104fc2aa9`
- Trace `6abac750fee081918af4522336615f29`

Before launch all five are disabled. Previous Mailbox/Pulse state is stale and must be replaced by the new continuous package seed.

## OCB
- explicit OSB classification only
- up to 3 exact-identical attempts total
- no automatic fourth attempt
- mandatory server-state reconciliation for mutation outcomes
- ambiguity never authorizes blind duplication

## Stop semantics
No artificial stage checkpoints. Continue through ordinary failures and tactical fixes. Stop only at objective completion or genuine authority/safety/strategy ambiguity.

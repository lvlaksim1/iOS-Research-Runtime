# PP-RM Launch Package — iOS Research Runtime

Status: PAUSED AT MANAGER CHECKPOINT
Manager: `ios-research-runtime-project-manager`
Target sealed generation after save: 9
Product: `main@cbba4060db543d4a2b800f7c15b2a700e69f6961`

## Native object IDs

- Worker A: `6abac75982308191b786450088217776`
- Worker B: `6abac76297c8819182c048fcbc619ef0`
- Runtime Mailbox: `6abac714ddb481919ab9cb13afc4f8f8`
- Pulse Register: `6abac73339dc8191ba6bf26104fc2aa9`
- Trace Register: `6abac750fee081918af4522336615f29`

All five objects are currently disabled.

## Current checkpoint

The raw-APFS restoration is published.

Exact current CI:
- Ramdisk Tool Windows: PASS
- Windows Build: PASS
- Windows End-to-End Boot: FAIL before Darwin boot because `qemu-sptm-windows-gate` artifact is missing.

OCB3 evidence:
- full production publication turn: explicit OSB -> explicit OSB -> no publication;
- minimal targeted probe #1: SUCCESS on attempt 1 -> publication;
- minimal targeted probe #2: explicit OSB -> explicit OSB -> SUCCESS on attempt 3.

The third exact-identical request is experimentally supported as potentially useful but is not yet a permanent universal retry rule.

## Important runtime fence

The latest Trace is valid experiment evidence, but the current Mailbox/Pulse are stale relative to Manager/product truth because the minimal probes bypassed ordinary baton progression.

DO NOT arm Worker A or B from the current register contents.

Before any next run:

1. restore and verify sealed Manager generation 9;
2. reconcile live `main`;
3. inspect current CI/infrastructure state;
4. define one bounded Manager package;
5. reseed Mailbox/Pulse/Trace to a new clean generation/package;
6. verify all three registers disabled and exact;
7. patch worker prompts if package logic changed;
8. arm exactly one owner worker.

## Next intended package

Objective: restore current-SHA Windows E2E execution by resolving the missing `qemu-sptm-windows-gate` artifact path without changing unrelated iOS/APFS semantics.

Expected stop conditions:
- infrastructure restored and E2E reaches a real boot-stage boundary;
- persistent APFS error 79;
- recovery `launchd` / AMFI boundary;
- verified root shell;
- unexpected regression;
- ambiguous side effect or PP-RM invariant failure.

Successor arm remains the final tool operation of each worker turn. After arm, zero tool calls.

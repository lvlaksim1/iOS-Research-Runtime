# PP-RM Launch Package — continuous production

Status: READY TO ARM
Manager generation: 10
Package: `IOS-M1-CONTINUOUS-001`
Product start: `main@cbba4060db543d4a2b800f7c15b2a700e69f6961`

## Mission
Run continuous bounded A/B development until IOS-M1 reaches verified Windows recovery `launchd` plus verified root shell, or a genuine stop condition occurs.

## Immediate start
Diagnose and repair the missing `qemu-sptm-windows-gate` path that blocks exact-SHA Windows E2E before Darwin boot.

## No artificial stops
Do not stop merely because:
- a CI run fails;
- an artifact is missing;
- a tactical fix is required;
- E2E reaches a diagnosable product failure;
- CI is still running.

Instead hand off the factual checkpoint and next bounded action to the partner.

## OCB
Keep current parameters:
- explicit OSB only;
- maximum 3 exact-identical attempts total;
- no attempt 4;
- reconcile authoritative state after mutation attempts;
- ambiguous mutation is never blindly replayed.

## Final/genuine stop
Stop only on:
- IOS-M1 objective complete;
- authority/scope/Owner approval required;
- unresolved ambiguous side effect;
- irrecoverable PP-RM invariant failure;
- true strategic fork outside tactical IOS-M1 execution.

## Existing native IDs
A=`6abac75982308191b786450088217776`
B=`6abac76297c8819182c048fcbc619ef0`
Mailbox=`6abac714ddb481919ab9cb13afc4f8f8`
Pulse=`6abac73339dc8191ba6bf26104fc2aa9`
Trace=`6abac750fee081918af4522336615f29`

Registers stay disabled. Only one worker is normally active; handoff may briefly use A+B.

# Latest handoff

Persistent manager: `ios-research-runtime-project-manager`.
Product authority: `main@cbba4060db543d4a2b800f7c15b2a700e69f6961`.
Manager authority: `manager-state`.

## New operating mode
Owner authorized PP-RM to run in real production conditions without artificial stage stops.

Package: `IOS-M1-CONTINUOUS-001`.

A/B should continue across as many bounded turns as required. Intermediate CI failures, missing artifacts, diagnosable workflow defects, and tactical product regressions are work, not automatic Manager checkpoints.

## Immediate starting evidence
- Ramdisk Tool Windows PASS
- Windows Build PASS
- E2E run `36483217835` failed before Darwin boot
- missing artifact: `qemu-sptm-windows-gate`
- job: `109133700969`

## OCB parameters
Unchanged:
- explicit OSB only;
- maximum three exact-identical attempts total;
- no fourth;
- reconcile actual GitHub state after mutation attempts;
- never blindly replay ambiguous mutation.

## Runtime startup
All existing native object IDs are retained. Mailbox/Pulse/Trace must be cleanly reseeded before A is armed.

## Genuine return-to-Manager conditions
Return only if IOS-M1 is complete, a decision exceeds current authority/scope, mutation state remains ambiguous, PP-RM safety cannot be restored from evidence, or a true strategic fork is reached.

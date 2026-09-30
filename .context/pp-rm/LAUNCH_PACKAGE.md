# PP-RM Launch Package — generation 18

Status: RUNNING
Manager generation: 18
Package: `IOS-M1-CONTINUOUS-007`
Product start: `main@4821fb9a9cd72dd40af2a518962f180fb4344fe7`
Current product: `main@a0d0dd1a9f95543dca25bfb647e1f67e3d4e1e18`

## Owner authority
Direct Owner instruction: correct the workflow-gate logic and continue PP-RM.

## Continuity objects
A=`6abac75982308191b786450088217776`
B=`6abac76297c8819182c048fcbc619ef0`
Mailbox=`6abac714ddb481919ab9cb13afc4f8f8`
Watchdog=`6abac73339dc8191ba6bf26104fc2aa9`
Trace=`6abac750fee081918af4522336615f29`

## Runtime rules
Generation16 native two-phase frozen-target publication remains authoritative.
Generation17 recurring-hourly Watchdog remains authoritative.
Generation18 result-first workflow evidence remains authoritative.

## Production checkpoint
- generation1 B consumed existing exact-SHA run and found the first gate-parser false positive
- generation2 A published parser target `a0d0dd1...` via OCB3 attempt3 success
- generation3 B consumed exact-SHA run `36775221102`, found the quoted alternate-slot parser defect and prepared target `79393c0d...`
- current generation4 A is MUTATION_READY for frozen target `79393c0d0797fc88d02445e9afb58484dd50c6f1`
- baseline `a0d0dd1a9f95543dca25bfb647e1f67e3d4e1e18`
- force=false
- Watchdog remains recurring

## Critical evidence requirement
Do not infer strict SHA256-primary from workflow conclusion alone.
Require raw evidence showing the actual primary CodeDirectory `digest_type: sha256`.
The observed baseline remains SHA1-primary with SHA256 alternate.

## Supersession
Packages005 and006 are terminal/superseded and MUST NOT resume.

# Latest handoff

Persistent manager: `ios-research-runtime-project-manager`.
Product authority: `main`.
Manager authority: `manager-state`.

## Manager checkpoint

PP-RM admission pilot has completed and been reviewed.

Attempt 1:
- two GitHub READ operations succeeded first attempt;
- runtime stopped safely on immediate read-back mismatch;
- server Mailbox later showed the exact intended generation-2 state;
- no successor was armed.

Attempt 2:
- exact A1 -> B2 -> A3 -> FINAL;
- SEND/ACK test-001 and test-002 verified;
- both workers ended disabled;
- Mailbox/Pulse/Trace remained disabled;
- four actual GitHub READ events, all successful on first attempt;
- explicit OSB=0, other GitHub errors=0, ambiguous outcomes=0.

Manager finding:
- bounded read-only register stabilization is required after writes;
- final telemetry counts are derived from tagged Trace events because Worker FINAL undercounted 4 reads as 3;
- scheduler delay is tolerated and does not authorize timeout takeover;
- OCB policy remains provisional because no OSB occurred.

## Production admission

PP-RM is admitted for `IOS-M1-R1` after sealed generation 7.

Current product: `main@85d408075ab8a66f6d16043029eb2255956eb1b9`.

Exact scoped restoration:
- `d743b2e...` -> `tools/ios-ramdisk-tool/main.go`, write rebuilt recovery image as exact raw APFS bytes rather than DMG rewrap;
- `b3befaeb...` -> `tools/ios-ramdisk-tool/main_test.go`, exact-byte raw-APFS regression test.

A/B execute bounded tactical turns only. At launchd/AMFI, persistent APFS error 79, unexpected regression, ambiguous side effect, protocol failure, or objective completion, stop chaining and return evidence to Manager.

Production PP-RM has not yet been armed by this Persist.

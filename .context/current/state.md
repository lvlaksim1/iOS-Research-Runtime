# Current state

## Governance topology
- persistent manager: `ios-research-runtime-project-manager`
- product authority: `main`
- Manager authority: `manager-state`
- Context Capsule Core: `3a942bd269ec7ee164575589e702e5074da30a29`
- PP-RM: production-admitted after pilot review
- native Mailbox/Pulse/Trace: present and disabled
- Worker A/B: present and currently disabled after pilot FINAL

## Pilot result

`IOS-PP-RM-PILOT-001`:
- attempt 1: safe FAIL on immediate `OUTBOUND_READBACK_MISMATCH`; written Mailbox state later proved correct; no successor was armed.
- corrective action: bounded read-only stabilization, up to three fresh reads, no mutation replay.
- attempt 2: PASS, exact A1 -> B2 -> A3 -> FINAL.
- attempt-2 GitHub READ events: 4 actual, 4 first-attempt successes, explicit OSB 0, other errors 0, ambiguous outcomes 0.
- both attempts combined: 6/6 GitHub READ first-attempt successes.
- Worker FINAL summary incorrectly reported 3 requests; authoritative metric source is individual tagged Trace events.
- scheduler execution latency of minutes was observed but did not break baton continuity.
- OCB retry path remains untested because no explicit OSB occurred.

## Product state

Live product remains `main@85d408075ab8a66f6d16043029eb2255956eb1b9`, code-equivalent to `3b0f564...` plus discovery metadata.

Conservative runtime boundary remains APFS root mount error 79 from exact E2E `35634992757`.

Historical scoped recovery evidence:
- `d743b2e...`: raw APFS output correction in `tools/ios-ramdisk-tool/main.go`
- `b3befaeb...`: regression test in `tools/ios-ramdisk-tool/main_test.go`
- `669f2b...`: later launchd/AMFI boundary, historical only

## Active work

`IOS-M1-R1` is PRODUCTION-ADMITTED and ready to seed into PP-RM after generation 7 is sealed.

Manager remains responsible for strategic decisions and the next high-level checkpoint.

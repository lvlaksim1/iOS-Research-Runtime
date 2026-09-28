# Manager plans

## Authority
- product: `main@85d408075ab8a66f6d16043029eb2255956eb1b9`
- Manager: sealed generation 7 on `manager-state` after this Persist
- PP-RM runtime: admitted for production after pilot review

## Production admission review

`IOS-PP-RM-PILOT-001` is PASS on attempt 2.

Verified:
1. A1 -> B2 -> A3 -> FINAL completed.
2. exact SEND/ACK handoffs succeeded.
3. Mailbox/Pulse/Trace remained disabled.
4. both workers ended disabled.
5. successor arm was the final tool operation on A1 and B2.
6. attempt-2 GitHub READ passability was 4/4 first-attempt success.
7. no explicit OSB, other GitHub error, or ambiguous GitHub result occurred.

Corrections adopted:
- after a register mutation, verify with up to three fresh read-only reads; never repeat the mutation merely because the first read is stale;
- authoritative GitHub telemetry totals are calculated from uniquely tagged Trace operation events, not from a worker-written aggregate;
- scheduler delay alone is not failure and never authorizes timeout takeover.

OCB remains provisional because the pilot produced zero explicit OSB events.

## Active production package — IOS-M1-R1

Objective: restore the previously verified raw-APFS packaging correction on the rolled-back product line and establish the exact new Windows E2E boundary.

Exact recovery scope:
- `d743b2e728d9cda194c7e76909f76a5f1704194f`: only `tools/ios-ramdisk-tool/main.go`; remove DMG rewrap and write the rebuilt image as exact raw APFS bytes.
- `b3befaeb8c0f2635623d3d8a56226199d2d0753e`: only `tools/ios-ramdisk-tool/main_test.go`; add exact-byte raw-APFS regression test.

Execution:
1. fresh-reconcile live `main`;
2. inspect exact commit diffs/parents before mutation;
3. apply only the two scoped semantics above to current `main`;
4. run the minimum deterministic Go test/build gate covering `ios-ramdisk-tool`;
5. if green, run exact Windows E2E;
6. return HIGH-LEVEL CHECKPOINT to Manager at:
   - recovery `launchd` / AMFI boundary;
   - persistent APFS error 79;
   - different unexpected regression;
   - ambiguous side effect;
   - PP-RM invariant failure;
   - package objective complete.

A/B must not select a new APFS/AMFI strategy at that checkpoint.

## Production runtime procedure

Each A/B turn:
1. fresh-read Mailbox and Trace; validate generation/owner/message/seq/hash and deduplicate message_id;
2. ACK valid inbound baton;
3. reconcile live product state before consequential GitHub mutation;
4. execute one bounded tactical turn;
5. complete and verify all external/product side effects;
6. write Pulse;
7. publish next Mailbox or Manager checkpoint;
8. verify register state with up to three fresh read-only reads, never repeating the mutation solely for visibility;
9. append tagged Trace evidence;
10. if continuing, arm exactly one successor as LAST TOOL OPERATION and make zero tool calls afterward.

## OCB

- explicit OSB on GitHub request -> OCB;
- one exact identical retry is desired, not mandatory;
- no automatic third identical request;
- ambiguous mutations are reconciled, never blindly duplicated;
- collect production telemetry because read-only pilot did not exercise OSB.

## Manager-state coherence

A/B ordinary work does not mutate `manager-state`. Durable project meaning is persisted by Manager at high-level checkpoints.

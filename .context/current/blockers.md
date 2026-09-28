# Current blockers and open risks

## Active product boundary

Current product is `main@85d408075ab8a66f6d16043029eb2255956eb1b9`, code-equivalent to the old `3b0f564...` line plus discovery metadata.

Conservative current boot boundary: APFS `mountroot failed, error: 79` from exact Windows E2E `35634992757`.

Historical evidence shows the narrow raw-APFS correction `d743b2e...` plus test `b3befaeb...` previously moved this path past APFS mounting.

## PP-RM

No production-admission blocker remains after pilot attempt 2 PASS.

Known runtime risks:
- immediate register read-after-write can expose stale visibility; bounded read-only stabilization is required;
- scheduler DTSTART latency can be several minutes; delay alone must not trigger takeover;
- Worker-authored aggregate telemetry can be wrong; authoritative counts come from tagged Trace events;
- OCB retry effectiveness remains unproven because the pilot saw zero explicit OSB events.

## Safety / strategy gates

- restore only the two evidence-backed raw-APFS changes first;
- A/B do not mutate `manager-state`;
- no product release without Owner authorization;
- no broad speculative APFS/AMFI/security-policy work inside `IOS-M1-R1`;
- ambiguous GitHub mutation outcome => reconcile, do not blindly replay;
- at a high-level checkpoint A/B stop and return evidence to Manager.

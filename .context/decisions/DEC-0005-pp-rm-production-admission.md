# DEC-0005 — PP-RM production admission after pilot

Date: 2026-09-28
Status: ACCEPTED
Authority: Project Manager review under Owner-approved PP-RM model

## Evidence

Pilot attempt 2 completed A1 -> B2 -> A3 -> FINAL with exact SEND/ACK handoffs, disabled registers, disabled workers at FINAL, and successor-arm-last behavior.

Attempt 2 produced four actual tagged GitHub READ operations, all successful on first attempt. No explicit OSB, other GitHub error, or ambiguous GitHub result occurred.

Attempt 1 exposed a separate register-visibility issue: immediate read-back reported mismatch even though the server later exposed the exact written Mailbox state. No successor was armed, so the failure was safe.

## Decision

PP-RM is admitted to production execution for `IOS-M1-R1`.

Adopt these protocol corrections:
1. after a register mutation, allow up to three fresh read-only reads for stabilization; do not repeat the mutation solely for visibility;
2. calculate authoritative GitHub telemetry from tagged Trace events, not from worker aggregate summaries;
3. scheduler delay alone is not a failure and cannot justify timeout takeover.

The pilot does not validate OCB retry effectiveness because explicit OSB count was zero. OCB policy remains provisional and production telemetry continues.

## Production scope

`IOS-M1-R1` restores only the exact raw-APFS change from `d743b2e...` and regression test from `b3befaeb...`, validates narrowly, then runs Windows E2E and returns to Manager at the defined checkpoint.

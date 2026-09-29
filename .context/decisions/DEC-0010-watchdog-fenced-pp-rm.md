# DEC-0010 — Watchdog-fenced PP-RM

Date: 2026-09-29
Status: ACCEPTED
Authority: direct Owner instruction after production generation-139 silent runtime loss

## Problem

Package `IOS-M1-CONTINUOUS-001` handed generation 139 to Worker A. The scheduler started A, but no durable ACK, Trace event, product mutation, or successor handoff was published. The chain had no independent component capable of detecting and safely recovering this start-before-ACK failure.

## Decision

Replace Pulse with Watchdog while keeping the five-task ceiling.

Topology:
- Worker A
- Worker B
- Mailbox
- Trace
- Watchdog

Every activation is fenced by:
`generation + attempt + activation_token + message_id`.

The target worker's task prompt and Mailbox must contain the same activation tuple.

Workers must revalidate the token before ACK, before every consequential GitHub mutation, and before handoff.

## Watchdog recovery

Watchdog is armed for each outbound baton before the successor is armed.
If the baton is stale, Watchdog exits.
If there is no ACK after grace, Watchdog rotates attempt/token and re-arms the owner.
If ACK exists but progress_seq stops advancing across two Watchdog checks, Watchdog rotates attempt/token and re-arms the owner.
Maximum attempts per generation: 3.

A runtime holding an old token is fenced and must stop without further mutation.

## Limitation

A token cannot revoke a request already in flight. Recovery therefore uses delayed progress checks and workers validate immediately before consequential mutations.

## Production continuation

Launch new package `IOS-M1-CONTINUOUS-002` from `main@649a2244f876db34e2032755b189df158667305f` and continue IOS-M1 without artificial checkpoints.

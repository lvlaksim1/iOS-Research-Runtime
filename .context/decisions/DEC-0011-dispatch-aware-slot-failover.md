# DEC-0011 — Dispatch-aware PP-RM slot failover

Date: 2026-09-29
Status: ACCEPTED
Authority: direct Owner instruction after review of package IOS-M1-CONTINUOUS-002 failure

## Evidence

Generation 13 introduced a Watchdog and fencing, which correctly detected missing durable ACK.
However generation 2 recovery consumed attempts 1 through 3 against Worker A and fail-stopped.
Reconciliation showed Worker A last_run_time did not advance on watchdog redispatches. Therefore the later events were scheduler dispatch non-delivery, not confirmed runtime starts followed by pre-ACK death.

## Decision

Separate scheduler delivery from runtime execution.

Mailbox becomes the sole activation authority. Worker prompts are immutable and do not embed per-generation tokens.

Every dispatch records the target worker's current last_run_time as dispatch_baseline_last_run_time.

If live last_run_time remains equal to baseline after grace, classify DISPATCH_FAILURE. Retry dispatch without consuming activation_attempt.

After two consecutive dispatch failures for one slot, rotate activation token and fail over to the partner slot on the same generation.

Only if last_run_time advances beyond baseline and no durable ACK appears may Watchdog classify RUNTIME_FAILURE and consume activation_attempt.

The maximum of three attempts applies only to confirmed runtime failures, not scheduler dispatch calls.

## Fencing

Workers accept only the Mailbox baton assigned to their slot and memorize its generation/attempt/token/message_id.
They revalidate that tuple immediately before every consequential GitHub mutation and before handoff.
Failover rotates token, fencing any late runtime from the prior slot.

## Ambiguous mutations

A token does not cancel a request already in flight.
If recovery sees PRE_MUTATION or otherwise cannot prove no side effect, authoritative GitHub reconciliation is mandatory before replay.

## Production continuation

Launch package `IOS-M1-CONTINUOUS-003` from `main@649a2244f876db34e2032755b189df158667305f`.

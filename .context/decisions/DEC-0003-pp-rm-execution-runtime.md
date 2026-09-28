# DEC-0003 — Adopt PP-RM as Project Manager execution Runtime

Date: 2026-09-28
Status: ACCEPTED
Authority: direct Owner directive

## Decision

`ios-research-runtime-project-manager` remains the single persistent Project Manager and commitment owner for ordinary iOS Research development.

PP-RM is adopted as the continuous execution Runtime mechanism beneath the Manager:

`Manager -> bounded work package -> Worker A/B loop -> evidence/high-level checkpoint -> Manager`.

The Manager controls development direction, priorities, milestone interpretation, strategy, durable Context Capsule state, and high-level checkpoints.

Worker A and Worker B are disposable execution carriers. They may continuously perform tactical work inside the active Manager-issued work package, but they do not become Project Managers, do not acquire project responsibility, and do not independently redefine goals or priorities.

## Runtime protocol

PP-RM normal path follows:
- fresh runtime validation;
- inbound ACK;
- one bounded turn;
- complete all external/product side effects;
- Pulse;
- publish Runtime Mailbox;
- exact fresh read-back;
- Trace SEND;
- arm exactly one successor as the final tool operation;
- no tool operations after successor arm.

GitHub remains product/evidence infrastructure, not PP-RM ownership, heartbeat, Mailbox, or baton control plane.

## Manager-state boundary

A/B ordinary execution must not mutate `manager-state`. At strategic/high-level checkpoints, A/B returns an evidence package and stops strategic continuation. The Manager then reconciles, decides, and persists a coherent sealed manager generation before issuing the next package when durable meaning changed.

## OCB

Use `OCB` (`OSB Control Block`) instead of the older OSB term. OCB is routine system behavior plus its control response, not a hostile condition by default. Missing expected server responses may be retried safely; side-effecting operations require read-back/idempotency safeguards before retry.

## Relationship to retired autonomy

This decision does not reactivate the retired `ai-agent-lab` shift-worker/OTK factory. PP-RM is a narrower runtime mechanism subordinate to the persistent Manager.

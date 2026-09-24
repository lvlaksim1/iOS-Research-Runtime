# DEC-0001 — Persistent Project Manager migration

Date: 2026-09-24
Status: ACCEPTED
Authority: Owner directive

## Decision

`iOS-Research-Runtime` is assigned to the persistent repository-local Project Manager `ios-research-runtime-project-manager`.

Durable manager state is stored on `manager-state`. Product authority remains `main`. The product branch carries only the discovery bootstrap needed to find the manager state.

The previous rotating-worker development model in `lvlaksim1/ai-agent-lab` is historical only for this project. Its technical evidence may be consulted, but its queue, worker identities, review scores, timers, and old production state do not govern new work.

Ordinary product development belongs to the persistent Project Manager. Independent Auditor or bounded specialist help may be requested when useful.

## Consequences

- runtime replacement does not create a new manager;
- direct Owner to iOS Project Manager work remains valid;
- shared Agent Control Plane is generic delivery/continuation infrastructure;
- legacy technical claims are admitted only after provenance-aware reconciliation;
- APFS product changes remain paused until the agreed migration acceptance gates are complete.

# Procedural memory

- Reconcile exact live `main` before product mutation.
- PP-RM handoff remains validate -> ACK -> bounded work -> finish side effects -> Pulse -> Mailbox -> read-back stabilization -> Trace SEND -> successor arm last.
- Register read-back stabilization uses up to three fresh reads and never replays a register mutation merely for visibility.
- GitHub telemetry uses unique Trace events per request/attempt.
- Normal OCB policy before this experiment allowed one desired exact-identical retry after explicit OSB.
- TEMPORARY experiment authorized 2026-09-28: for targeted `update-ref(main -> cbba4060...)` only, if attempts 1 and 2 both return explicit OSB, make attempt 3 with the exact same operation and parameters.
- No automatic fourth request.
- After targeted attempts, always fresh-reconcile authoritative `main`.
- This third-attempt allowance is experimental evidence collection, not a permanent rule.
- Non-OSB failures are not automatically OCB. Ambiguous mutations are never blindly repeated.
- A/B ordinary execution never mutates `manager-state`.

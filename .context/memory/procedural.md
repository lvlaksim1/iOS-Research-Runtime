# Procedural memory

- PP-RM package continuity and runtime boundedness are different: a package may run indefinitely across A/B, but each runtime executes one bounded meaningful turn.
- Normal turn: fresh-read/validate -> ACK -> reconcile product state -> bounded work -> complete/verify side effects -> Pulse -> outbound Mailbox -> read-back stabilization -> Trace SEND -> successor arm last -> zero tool calls.
- No artificial Manager checkpoints after ordinary CI failures or diagnosable technical defects in continuous mode.
- CI waiting is handled by handoff, not by terminating the package.
- Register read-back stabilization uses fresh reads only; never replay a register mutation merely due to stale visibility.
- GitHub OCB parameters for current continuous run: explicit OSB only, up to three exact-identical attempts total, no fourth automatic request.
- Never blindly replay an ambiguous mutation. Reconcile authoritative server state first.
- GitHub writes must be based on a freshly reconciled branch/ref. If the base changed unexpectedly, resolve from evidence before publishing.
- Keep changes narrow and evidence-backed; ordinary tactical decisions are delegated, strategic project decisions remain with Manager.
- A/B never mutate `manager-state`.
- Successor arm is always the final tool operation.

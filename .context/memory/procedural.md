# Procedural memory

- PP-RM package continuity and runtime boundedness are different: a package may run indefinitely across A/B, but each runtime executes one bounded meaningful turn.
- Normal turn: fresh-read/validate -> ACK -> reconcile product state -> bounded work -> complete/verify side effects -> Pulse -> outbound Mailbox -> read-back stabilization -> Trace SEND -> successor arm last -> zero tool calls.
- No artificial Manager checkpoints after ordinary CI failures or diagnosable technical defects in continuous mode.
- CI waiting is handled by handoff, not by terminating the package.
- Register read-back stabilization uses fresh reads only; never replay a register mutation merely due to stale visibility.
- GitHub OCB parameters for current continuous run: explicit OSB only, up to three exact-identical attempts total, no fourth automatic request.
- Never blindly replay an ambiguous mutation. Reconcile authoritative server state first.
- Current preferred write-path experiment for blocked file publication is PR-based: create_blob -> create_tree -> create_commit -> create_branch -> create_pull_request -> merge_pull_request -> authoritative read-back.
- Apply OCB3 independently to each GitHub write request in that path; do not change request parameters between exact OSB retries.
- For merge, use expected_head_sha when available and verify actual main after the operation.
- Direct update_file(main) is not the only allowed publication mechanism; choose the native write-path supported by evidence and current Manager policy.
- A worker's own Scheduled Task may legitimately still report is_enabled=true when the runtime starts. SELF ENABLED IS NOT AN OWNERSHIP FAILURE.
- Single-owner validation uses Mailbox owner/generation/message_id/seq, prior Trace SEND, and absence of a contradictory newer baton. The self enabled flag is informational only.
- GitHub writes must be based on a freshly reconciled branch/ref. If the base changed unexpectedly, resolve from evidence before publishing.
- A/B never mutate manager-state.
- Successor arm is always the final tool operation.

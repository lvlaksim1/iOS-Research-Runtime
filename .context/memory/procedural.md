# Procedural memory

- PP-RM package continuity may span many A/B runtimes; each runtime remains one bounded meaningful turn.
- Normal turn: validate baton -> ACK -> reconcile product state -> bounded work -> verify side effects -> Pulse -> outbound Mailbox -> read-back stabilization -> Trace SEND -> successor arm last -> zero calls after arm.
- No artificial Manager checkpoints after ordinary CI failures or diagnosable technical defects.
- GitHub OCB: explicit OSB only, max three exact-identical attempts for the same request, no fourth. No unrelated GitHub operation between exact OSB retries.
- Ambiguous mutation is never blindly replayed; reconcile authoritative state first.
- Current preferred publication for a prepared direct child commit is `fresh-read main -> parent equality check -> update_ref(force=false) -> authoritative read-back`.
- PR creation/merge is not required when a prepared commit is already a direct child of current main and Manager authorized publication.
- If current main differs from prepared parent, never force; rebuild/reconcile from current main.
- Baton payload hashing canonicalization: SHA-256 over exact UTF-8 bytes of the payload value only; exclude `payload=` prefix and trailing newline. Sender must recompute/verify before Mailbox write; receiver uses identical rule.
- If hashing is unavailable, use `payload_sha256=UNAVAILABLE` and validate literal payload/message metadata rather than inventing a digest.
- A worker's own Scheduled Task may still report enabled at start; self enabled is informational, not an ownership failure.
- A/B never mutate `manager-state`.
- Successor arm is always the final tool operation.

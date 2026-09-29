# Procedural memory

- PP-RM topology is now exactly five tasks: Worker A, Worker B, Mailbox, Trace, Watchdog. Pulse is retired.
- Each baton carries package, manager_generation, generation, owner, attempt, activation_token, message_id, payload/hash, ack, and progress_seq.
- The target worker task prompt carries the same activation tuple. Prompt token and Mailbox token must match.
- First durable worker mutation after validation is Mailbox ACK with progress_seq=1.
- A worker fresh-reads and validates its fencing token immediately before every consequential GitHub mutation and immediately before outbound baton publication.
- Token mismatch means stale runtime: stop with no further external mutation.
- Sender writes and verifies outbound Mailbox, writes Trace SEND, arms Watchdog, then arms successor as the final tool operation. No calls after successor arm.
- Watchdog exits if its expected baton is stale because generation advanced or token changed.
- If expected baton has no ACK after grace, Watchdog rechecks, then rotates attempt/token and re-arms owner.
- If ACK exists, Watchdog tracks progress_seq. Progress causes another delayed check; no progress across two checks causes fenced recovery.
- Maximum three activation attempts per generation. No blind fourth runtime.
- Fencing cannot cancel an already in-flight external request; grace/progress checks and pre-mutation token validation reduce overlap risk.
- GitHub publication remains fresh-read main -> blob/tree/commit -> fresh-read main -> update_ref(force=false) -> authoritative read-back.
- GitHub OCB remains explicit-OSB only, max 3 exact-identical attempts, no fourth, reconcile ambiguous mutations.
- CI waiting must be handed off rather than holding a disposable runtime open.
- A/B never mutate manager-state.

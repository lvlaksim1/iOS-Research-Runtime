# Procedural memory

Updated: 2026-09-29 22:57 MSK

- PP-RM topology is exactly five tasks: Worker A, Worker B, Mailbox, Trace, Watchdog.
- Worker A/B prompts are immutable during a package.
- Watchdog prompt is immutable during a package.
- Mailbox is the sole authoritative activation and Watchdog observation state.
- Every Watchdog invocation MUST re-arm the same Watchdog for +5 minutes as its FIRST tool operation. No read or other call may precede it.
- Watchdog 5-minute cadence is fixed and non-adaptive.
- The early-self-rearm semantic was validated by `PP-RM-G15-EARLY-REARM-R2`: predecessor runtime stopped while RUN1_ACTIVE; successor still started and recorded PASS.
- Workers never rewrite Watchdog prompt.
- Rapid A↔B cadence remains fixed; do not introduce adaptive WAIT_CI backoff.
- Each baton carries package, manager_generation, generation, owner_slot, activation_attempt, dispatch_retry, activation_token, message_id, dispatch_baseline_last_run_time, payload/hash, ack, progress_seq, progress and Watchdog observation fields.
- A worker accepts work only when Mailbox owner_slot equals its slot and state=READY.
- Worker ACKs durably before product work.
- Before every consequential GitHub mutation and outbound baton publication, fresh-read Mailbox and require the same generation/attempt/token/message/owner tuple.
- Watchdog distinguishes scheduler delivery failure from runtime failure by comparing live Worker.last_run_time with dispatch_baseline_last_run_time.
- Scheduler non-delivery does not consume activation_attempt.
- Repeated dispatch failure uses same-generation partner failover with token rotation.
- Confirmed runtime failure/stall consumes activation_attempt; max three per generation.
- ACKed runtime stall requires two Watchdog observations.
- PRE_REF_UPDATE or other ambiguous ref mutation requires authoritative GitHub reconciliation before replay.
- Watchdog terminal path publishes FINAL/FAIL_STOP durably first, then disables the already pre-armed Watchdog.
- GitHub publication remains fresh-read main -> blob/tree/commit -> fresh-read main -> update_ref(force=false) -> authoritative read-back.
- OCB remains explicit-OSB only, max 3 exact-identical attempts, no fourth, with ambiguous mutation reconciliation.
- Current Owner directive is capsule-only update / no launch. Package 004 is stopped. Package 005 is reserved and must remain unarmed until a new explicit Owner launch instruction.

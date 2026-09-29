# Manager beliefs

- Persistent Project Manager `ios-research-runtime-project-manager` remains the project commitment owner; product authority is `main`, Manager authority is `manager-state`.
- Current live product authority is `main@eaa98114031a37343e0d5184bd132830818a6b2f`.
- PP-RM generation 15 is the accepted runtime-continuity construction. A/B are disposable execution runtimes subordinate to the Manager, not project owners.
- The generation-15 topology remains exactly five Scheduled Tasks: Worker A, Worker B, Runtime Mailbox, Trace, Watchdog.
- Worker A/B prompts are immutable during a package. Watchdog prompt is also immutable.
- Mailbox is the sole authoritative activation and Watchdog observation-state authority.
- Every Watchdog invocation MUST make self-rearm of the same unchanged Watchdog for exactly +5 minutes its FIRST tool operation. No Mailbox read, GitHub read, Trace mutation or recovery action may precede it.
- The fixed Watchdog interval is 5 minutes and is non-adaptive.
- Workers never rewrite Watchdog prompt. Rapid A↔B handoff cadence remains fixed and non-adaptive.
- Dispatch retry remains separate from activation_attempt; repeated scheduler non-delivery uses same-generation token rotation and A/B failover without consuming activation_attempt.
- Confirmed runtime failure/stall consumes activation_attempt; maximum three confirmed runtime failures/stalls per generation.
- Fencing remains generation + activation_attempt + activation_token + message_id + owner_slot, revalidated before consequential GitHub mutation and before handoff.
- Ambiguous GitHub ref mutation requires authoritative reconciliation before replay.
- OCB remains explicit OpenAI safety/safety-check block only, maximum three exact-identical attempts total, no fourth attempt, with authoritative mutation reconciliation.
- Isolated experiment `PP-RM-G15-EARLY-REARM-R2` validated that an early self-rearm can survive loss of the predecessor runtime.
- Package `IOS-M1-CONTINUOUS-004` was inadvertently activated before the Owner's capsule-only/no-launch instruction, advanced to generation 3, and was then stopped. It produced no product-main mutation; current main remains `eaa98114031a37343e0d5184bd132830818a6b2f`.
- A clean future package is reserved as `IOS-M1-CONTINUOUS-005`; it is NOT ARMED and MUST NOT be launched without a new explicit Owner instruction.
- Current IOS-M1 product checkpoint remains the pre-launch generation-19 factual checkpoint: source APFS recovery tree is available pre-merge; the next intended product unit is a narrow recovery executable/signature/xattr inventory diagnostic followed by exact-SHA CI.

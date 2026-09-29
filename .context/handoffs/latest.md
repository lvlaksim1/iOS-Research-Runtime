# Latest handoff

Updated: 2026-09-29 22:57 MSK

Persistent manager: `ios-research-runtime-project-manager`.
Manager generation: 15.
Product authority: `main@eaa98114031a37343e0d5184bd132830818a6b2f`.

## PP-RM version
Generation 15 is the accepted construction:
- immutable Worker A/B prompts;
- immutable Watchdog prompt;
- Mailbox as sole activation/watch-state authority;
- Watchdog FIRST operation = self-rearm same unchanged task +5 minutes;
- fixed non-adaptive 5-minute Watchdog cadence;
- workers never rewrite Watchdog;
- rapid fixed A↔B cadence;
- dispatch_retry separate from activation_attempt;
- same-generation failover, fencing and ambiguous-mutation reconciliation preserved;
- OCB3 unchanged.

Validated semantic evidence: `PP-RM-G15-EARLY-REARM-R2` PASS.

## Runtime status
Package `IOS-M1-CONTINUOUS-004` was inadvertently activated before the Owner's capsule-only/no-launch instruction and then stopped.
All PP-RM execution actors A/B/Watchdog are disabled.
No product-main mutation resulted from that accidental activation.

Reserve `IOS-M1-CONTINUOUS-005` as the next clean package.
Status: DEFINED / NOT ARMED.
Launch requires a new explicit Owner instruction.

## Product checkpoint
Current main remains `eaa98114031a37343e0d5184bd132830818a6b2f`.
The next intended technical unit, when explicitly launched, is the generation-19 source-recovery executable/signature/xattr inventory diagnostic and tests, followed by exact-SHA CI and continued AMFI/CT work.

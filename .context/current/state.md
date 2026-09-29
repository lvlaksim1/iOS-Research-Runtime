# Current state

Updated: 2026-09-29 22:57 MSK

## Governance
- manager: `ios-research-runtime-project-manager`
- manager generation: 15
- product authority: `main`
- PP-RM version: generation 15 immutable early-rearm Watchdog construction
- execution status: STOPPED / NOT ARMED

## Product
- live main: `eaa98114031a37343e0d5184bd132830818a6b2f`
- Ramdisk Tool Windows exact-SHA regression: SUCCESS
- Windows Build exact-SHA: SUCCESS
- Windows End-to-End Boot `36589206204`: FAILURE
- primary product blocker: AMFI / CT launch-constraint rejection of recovery root-shell execution
- clean resume checkpoint: generation-19 evidence that source APFS recovery tree is available pre-merge; next intended unit is narrow executable/signature/xattr inventory diagnostic and tests
- no ambiguous product mutation is in flight

## PP-RM generation 15
Accepted construction:
- exactly A + B + Mailbox + Trace + Watchdog;
- A/B prompts immutable;
- Watchdog prompt immutable;
- Mailbox owns baton and Watchdog observation state;
- Watchdog FIRST operation is self-rearm of the same unchanged task for exactly +5 minutes;
- workers never rewrite Watchdog prompt;
- rapid A↔B cadence fixed and non-adaptive;
- dispatch_retry separate from activation_attempt;
- same-generation A/B failover preserved;
- fencing and ambiguous-mutation reconciliation preserved;
- OCB3 unchanged.

Semantic evidence:
- `PP-RM-G15-EARLY-REARM-R2`: PASS for predecessor-loss / early-self-rearm survival.

## Runtime correction
Package `IOS-M1-CONTINUOUS-004` had already been inadvertently activated before the Owner's capsule-only/no-launch instruction and advanced to generation 3.
It was stopped immediately after reconciliation:
- Worker A disabled;
- Worker B disabled;
- Watchdog disabled.
No product-main mutation occurred; main remains `eaa98114031a37343e0d5184bd132830818a6b2f`.

Next clean package is reserved as `IOS-M1-CONTINUOUS-005`, but it is NOT ARMED and MUST NOT be launched without a new explicit Owner instruction.

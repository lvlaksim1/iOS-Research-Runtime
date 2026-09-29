# DEC-0013 — Capsule-only generation 15 update; no runtime launch

Date: 2026-09-29
Status: ACCEPTED
Authority: direct Owner instruction

## Instruction
Update PP-RM generation 15 in durable Context Capsules only.
Do not launch PP-RM as part of this update.

The accepted generation-15 architecture is the DEC-0012 immutable early-rearm Watchdog design:
- immutable Watchdog prompt;
- first operation self-rearm +5 minutes;
- Mailbox-owned watch state;
- immutable A/B prompts;
- workers never rewrite Watchdog;
- rapid fixed A↔B cadence;
- generation-14 dispatch/runtime separation, same-generation failover, fencing and reconciliation preserved;
- OCB3 unchanged.

## Reconciliation
At the time this instruction was applied, package `IOS-M1-CONTINUOUS-004` had already been inadvertently activated by another runtime and had advanced to generation 3.

The Owner's no-launch instruction takes precedence.
Worker A, Worker B and Watchdog were disabled.
No product-main mutation had resulted from package 004; authoritative main remained `eaa98114031a37343e0d5184bd132830818a6b2f`.

## Clean future package
Package 004 is not to be resumed.

Reserve `IOS-M1-CONTINUOUS-005` as the next clean generation-15 package.
It is DEFINED / NOT ARMED.
A new explicit Owner instruction is required before any task reconfiguration, Mailbox/Trace reseed or arm operation for package 005.

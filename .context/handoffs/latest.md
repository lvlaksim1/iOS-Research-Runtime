# Latest handoff

Persistent manager: `ios-research-runtime-project-manager`.
Manager generation: 15.
Product authority: `main@eaa98114031a37343e0d5184bd132830818a6b2f`.

## Product checkpoint
Ramdisk Tool Windows and Windows Build are green on current main.
Windows End-to-End Boot `36589206204` failed.
The active product investigation remains AMFI / CT launch constraints on recovery root-shell execution.

Generation 19 established that the source APFS recovery tree is fully materialized before merge. The next justified unit is a narrow pre-merge inventory of recovery executable candidates and signature/xattr evidence, followed by exact-SHA CI.

No ambiguous product mutation was left by package 003.

## Continuity checkpoint
Package `IOS-M1-CONTINUOUS-003` stranded at generation 19 because the only Watchdog runtime was invoked but produced no durable recovery/self-rearm.

## Generation 15 construction
Package `IOS-M1-CONTINUOUS-004` keeps exactly A, B, Mailbox, Trace and Watchdog.

A/B and Watchdog prompts are immutable.
Mailbox alone owns activation and Watchdog observation state.

Every Watchdog invocation FIRST re-arms the same unchanged Watchdog for +5 minutes. Only then may it read Mailbox or act.

The semantic was validated by `PP-RM-G15-EARLY-REARM-R2`: the predecessor stopped while RUN1_ACTIVE, and the pre-armed successor still started and recorded PASS.

Workers never rewrite Watchdog prompt. They may only restore its unchanged schedule if unexpectedly disabled while the package is still RUNNING.

Dispatch-vs-runtime failure classification, same-generation failover, fencing, ambiguous-mutation reconciliation and OCB3 remain unchanged.

## Start
Launch package 004 from current main and resume the generation-19 tactical objective with no artificial stops.

# Latest handoff

Updated: 2026-09-30 04:05 MSK

Persistent manager: `ios-research-runtime-project-manager`.
Manager generation: 16.
Product authority: `main@95e871e84099f10245e912659b2d964c1b3c1037`.
Owner authority: direct instruction to adopt native two-phase mutation fencing, update durable capsule, and launch PP-RM.

## Prior package
`IOS-M1-CONTINUOUS-004` is terminal `FAIL_STOP` at generation 46.
Cause: generation-15 second Scheduled Tasks read requirement before GitHub mutation was not satisfiable reliably.
Terminal activation made no product mutation and left no ambiguous ref side effect.

## Generation 16 / package 005
Package: `IOS-M1-CONTINUOUS-005`.

Core change:
- one Scheduled Tasks read per worker runtime is sufficient;
- PREPARE runtimes never mutate mutable product refs;
- PREPARE may create immutable Git objects;
- frozen mutation descriptor contains mutation_id, baseline main, target commit, operation and force=false;
- a fresh `MUTATION_READY` runtime uses its first Scheduled Tasks read as ownership fence;
- mutation executor may publish only the frozen target;
- recovery preserves the same mutation descriptor exactly;
- GitHub reconciliation uses target/baseline/neither semantics;
- no extra GitHub fence/lock request exists.

Unchanged:
- exactly five PP-RM tasks;
- immutable A/B prompts;
- immutable Watchdog prompt;
- Watchdog FIRST operation self-rearm +5 minutes;
- fixed rapid A↔B cadence;
- dispatch_retry separate from activation_attempt;
- OCB3.

## Product checkpoint
Current main is `95e871e84099f10245e912659b2d964c1b3c1037`.
Next unit: implement and test the post-merge `/bin/bash` Mach-O/size/primary-CDHash/injected-trust-membership diagnostic immediately after `mergeSysrootTarWithSigner`, then exact-SHA CI.

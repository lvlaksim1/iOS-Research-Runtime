# PP-RM Launch Package — continuous production

Status: READY TO ARM
Manager generation: 15
Package: `IOS-M1-CONTINUOUS-004`
Product start: `main@eaa98114031a37343e0d5184bd132830818a6b2f`

## Mission
Run continuous bounded A/B development until IOS-M1 reaches verified Windows recovery `launchd` plus verified root shell, or a genuine stop condition occurs.

## Immediate start
Resume from the generation-19 factual checkpoint:
add a narrow source-recovery executable/signature inventory diagnostic and tests, publish with fencing, then run exact-SHA CI and continue AMFI / CT launch-constraint investigation.

## Continuity
Five tasks:
A=`6abac75982308191b786450088217776`
B=`6abac76297c8819182c048fcbc619ef0`
Mailbox=`6abac714ddb481919ab9cb13afc4f8f8`
Watchdog=`6abac73339dc8191ba6bf26104fc2aa9`
Trace=`6abac750fee081918af4522336615f29`

A/B and Watchdog prompts are immutable.

Every Watchdog invocation FIRST re-arms itself +5 minutes before any other call.

Mailbox is the only activation and Watchdog-state authority.

Dispatch failures remain separate from confirmed runtime failures.
Repeated dispatch failure on one worker causes same-generation failover to partner.
ACKed stalls require two Watchdog observations and ambiguous-mutation reconciliation where relevant.

Workers never rewrite Watchdog prompt.

## OCB
- explicit OSB only;
- maximum 3 exact-identical attempts total for one GitHub request;
- no attempt 4;
- reconcile authoritative state after ambiguous mutation attempts.

## Final/genuine stop
Stop only on IOS-M1 completion, authority/scope gate, unresolved ambiguous side effect, bounded continuity exhaustion across both slots, or true strategic fork.

Watchdog terminal cleanup: durable terminal state first, then disable pre-armed Watchdog.

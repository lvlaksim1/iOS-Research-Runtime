# PP-RM Launch Package — continuous production

Status: READY TO ARM
Manager generation: 14
Package: `IOS-M1-CONTINUOUS-003`
Product start: `main@649a2244f876db34e2032755b189df158667305f`

## Mission
Run continuous bounded A/B development until IOS-M1 reaches verified Windows recovery `launchd` plus verified root shell, or a genuine stop condition occurs.

## Immediate start
Repair the ramdisk regression-test nil dereference narrowly, then continue exact-evidence work on the AMFI / launch-constraint root-shell blocker.

## Continuity
Five tasks:
A=`6abac75982308191b786450088217776`
B=`6abac76297c8819182c048fcbc619ef0`
Mailbox=`6abac714ddb481919ab9cb13afc4f8f8`
Watchdog=`6abac73339dc8191ba6bf26104fc2aa9`
Trace=`6abac750fee081918af4522336615f29`

Worker prompts are immutable. Mailbox is the only activation authority.
Dispatch failures are counted separately from confirmed runtime failures.
Repeated dispatch failure on one worker causes same-generation failover to the partner.

## OCB
- explicit OSB only;
- maximum 3 exact-identical attempts total for one GitHub request;
- no attempt 4;
- reconcile authoritative state after ambiguous mutation attempts.

## Final/genuine stop
Stop only on IOS-M1 completion, authority/scope gate, unresolved ambiguous side effect, bounded continuity exhaustion across both slots, or true strategic fork.

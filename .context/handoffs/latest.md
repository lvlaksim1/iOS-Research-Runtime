# Latest handoff

Persistent manager: `ios-research-runtime-project-manager`.
Manager generation: 13.
Product authority: `main@649a2244f876db34e2032755b189df158667305f`.

## Product checkpoint

Windows Build is green.
E2E run `36556048793` reached recovery launchd and attempted root-shell startup, then failed because AMFI rejected ad-hoc-signed `/bin/bash` under CT / launch constraints.
Ramdisk Tool run `36556048692` independently exposes a regression-test nil dereference at `main_test.go:81`.

## Continuity checkpoint

Previous package `IOS-M1-CONTINUOUS-001` stopped at generation 139 after Worker A started but wrote no durable ACK or successor handoff.

New package `IOS-M1-CONTINUOUS-002` uses five tasks:
A, B, Mailbox, Trace, Watchdog.

Every activation is fenced with generation + attempt + activation_token + message_id.
Watchdog may rotate a stalled baton to a new token and re-arm its owner. Old runtimes must stop when their prompt token no longer matches Mailbox.

## Start

Launch the new package from current main. No artificial stops.
Initial tactical work: reconcile the completed E2E failure, fix the regression-test nil dereference narrowly, and continue evidence-backed work on the AMFI / launch-constraint blocker.

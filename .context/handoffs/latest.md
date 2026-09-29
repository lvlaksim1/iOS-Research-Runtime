# Latest handoff

Persistent manager: `ios-research-runtime-project-manager`.
Manager generation: 14.
Product authority: `main@649a2244f876db34e2032755b189df158667305f`.

## Product checkpoint
Windows Build is green.
E2E run `36556048793` reached recovery launchd and attempted root-shell startup, then failed because AMFI rejected ad-hoc-signed `/bin/bash` under CT / launch constraints.
Ramdisk Tool run `36556048692` exposes a regression-test nil dereference at `main_test.go:81`.

## Continuity checkpoint
Package `IOS-M1-CONTINUOUS-002` fail-stopped at generation 2 after Watchdog exhausted attempts against Worker A.
Post-run reconciliation shows Worker A last_run_time did not advance on the watchdog redispatches. Those events were scheduler dispatch failures, not three confirmed runtime deaths.

## New construction
Package `IOS-M1-CONTINUOUS-003` retains A, B, Mailbox, Trace and Watchdog.

Mailbox alone owns the activation tuple.
A/B prompts are immutable.
Each baton records dispatch_baseline_last_run_time.
Watchdog compares live last_run_time to the baseline:
- unchanged => dispatch failure; retry without consuming activation_attempt;
- advanced without ACK => confirmed runtime failure; rotate attempt/token;
- repeated dispatch failure on one slot => rotate token and fail over to the partner on the same generation.

Workers revalidate the fencing tuple before every consequential GitHub mutation and before handoff.

## Start
Launch the new package from current main with no artificial stops.
Initial tactical work: fix the nil dereference narrowly, then continue evidence-backed AMFI / launch-constraint diagnosis.

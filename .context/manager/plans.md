# Manager plans

## IOS-M1 production package

New package: `IOS-M1-CONTINUOUS-002`.
Manager generation: 13.
Product authority: `main`.

Current live product:
`main@649a2244f876db34e2032755b189df158667305f`

Current exact evidence:
- Windows Build on current main: SUCCESS.
- Windows End-to-End Boot run `36556048793`: FAILURE after reaching recovery launchd and attempting `/bin/bash`.
- Root-shell blocker: AMFI rejects the ad-hoc-signed `/bin/bash` with unsuitable CT policy / Launch Constraint Violation.
- Ramdisk Tool Windows run `36556048692`: regression-test nil dereference at `main_test.go:81`.

## PP-RM vNext topology

Use exactly five Scheduled Tasks:
1. Worker A.
2. Worker B.
3. Runtime Mailbox.
4. Trace.
5. Watchdog.

The former Pulse register is retired and its task slot is repurposed as Watchdog.

## Fenced activation identity

Every baton MUST include:
- package;
- manager_generation;
- generation;
- owner;
- attempt;
- activation_token;
- message_id;
- payload;
- payload_sha256 or UNAVAILABLE;
- ack;
- progress_seq.

The owner worker task prompt MUST carry the exact same activation tuple:
`generation + attempt + activation_token + message_id`.

A runtime whose prompt activation tuple does not match the current Mailbox is stale and performs no product mutation.

## Runtime fencing

A worker MUST fresh-read the Mailbox:
- at activation before ACK;
- immediately before every consequential GitHub mutation;
- immediately before publishing the outbound baton.

If generation/attempt/token/owner no longer match, the runtime terminates with no further external mutation.

## ACK and progress

After validation, the worker's first durable mutation is Mailbox ACK for the same baton and `progress_seq=1`.
During a bounded turn the worker advances `progress_seq` after material phases.
Long CI waiting is never held in one runtime; publish a handoff.

## Watchdog

For each outbound baton, sender arms Watchdog before arming successor.
The successor arm remains the sender's final tool operation.

Watchdog checks the exact expected baton after a grace interval.
- If Mailbox advanced or token changed: stale watchdog exits.
- If ACK is absent: re-read once, then rotate to a new attempt/token and re-arm the owner.
- If ACK exists: compare progress_seq. If progress advanced, re-arm Watchdog for another check. If no progress across two checks, rotate attempt/token and re-arm the owner.
- Maximum three attempts for one generation. After attempt 3 stalls, fail-stop with Trace evidence; no blind fourth runtime.
- Watchdog recovery writes the replacement baton before re-arming the owner. A previous runtime is fenced by the old activation token.

## GitHub publication

Preferred narrow change publication remains:
`fresh-read main -> create_blob -> create_tree -> create_commit -> fresh-read main -> update_ref(force=false) -> authoritative read-back`.

OCB is unchanged: explicit OSB only; maximum three exact-identical attempts for the same request; no fourth; ambiguous mutation requires reconciliation.

## Continuous objective

Continue without artificial stops:
1. preserve current main evidence;
2. repair the ramdisk regression-test nil dereference narrowly;
3. analyze and address the AMFI / launch-constraint root-shell blocker from exact E2E evidence;
4. rerun exact-SHA CI;
5. continue until verified recovery launchd + verified root shell or a genuine mandate/safety/ambiguity stop.

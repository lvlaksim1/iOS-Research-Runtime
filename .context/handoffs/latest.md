# Latest handoff

Updated: 2026-09-30 22:43 MSK

Persistent manager: `ios-research-runtime-project-manager`.
Manager generation: 17.
Product authority: `main@bcde5661eab70b6811a5f1fffe0552edaedf980a`.
Active PP-RM package: `IOS-M1-CONTINUOUS-006`.
Execution status: RUNNING.

## Superseded package
`IOS-M1-CONTINUOUS-005` is stranded/superseded at runtime generation262 and MUST NOT be resumed.
No ambiguous product-ref side effect is indicated by the stop; authoritative main remains unambiguous.

## Generation17 continuity
The existing five-task topology is retained.
Watchdog is persistent recurring state with `RRULE:FREQ=HOURLY`.
Healthy Watchdog runtime uses a safe self-touch followed by a +5 minute recurring slide.
The hourly recurrence is the independent survival backstop.
No Lifeboat, no sixth task, no extra slot and no GitHub continuity fence.

## Live production evidence
Package006 launch is proven by successful bounded handoffs:
- generation1 Worker B ACKed bootstrap READY, reconciled E2E run `36729602541`, extracted signature/AMFI evidence and handed off to A
- generation2 Worker A ACKed, identified the signer root cause and handed off to B
- latest observed baton: generation3, owner B, READY, activation_attempt=1, ACK=NONE
- Watchdog remains enabled with recurring hourly schedule
- product main has not moved during these evidence-only generations

## Current product finding
Observed post-merge bash still has SHA1 primary CodeDirectory and SHA256 alternate despite the repository invoking `rcodesign` with `--digest sha256`.

Generation2 reconciled upstream behavior:
- explicit CLI digest selection can request SHA256 primary
- later `SigningSettings::import_settings_from_macho` runs after CLI configuration
- for missing/old target metadata it forces SHA1 primary and adds SHA256 extra
- this explains the observed SHA1-primary result

## Current next action
Generation3 must design the smallest bounded override/correction that demonstrably preserves SHA256 as the primary post-sign digest before another E2E. Prefer an upstream-supported mechanism; otherwise isolate a local signer/tool correction. Any mutable publication still requires the frozen-target MUTATION_READY protocol.

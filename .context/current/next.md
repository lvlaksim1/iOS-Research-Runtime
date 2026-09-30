# Next actions

Updated: 2026-09-30 22:43 MSK

1. Continue package `IOS-M1-CONTINUOUS-006` from the live generation3 READY baton; do not resume package005.
2. Generation3 Worker B: design the smallest bounded method that prevents `rcodesign import_settings_from_macho` from overriding the explicitly requested SHA256 primary digest.
3. Prefer an upstream-supported CLI/configuration mechanism if one exists; otherwise isolate the smallest local signer/tool correction.
4. Before preparing any product target, obtain direct post-sign evidence that the primary CodeDirectory digest is SHA256 rather than SHA1.
5. In READY/PREPARE, immutable Git objects are allowed but mutable product refs remain forbidden.
6. If a target is prepared, freeze the descriptor and hand off a fresh `MUTATION_READY` runtime under the generation-16 native two-phase protocol.
7. Mutation executor reconciles authoritative main and may publish only the exact frozen target with `force=false`.
8. After successful publication, run exact-SHA CI and E2E and compare AMFI/CT/root-shell evidence with the SHA1-primary baseline.
9. Keep the generation17 Watchdog enabled with persistent hourly recurrence; +5 minute sliding is the fast path, not the survival dependency.
10. Preserve OCB3, dispatch_retry/activation_attempt separation, immutable Worker/Watchdog prompts and same-generation recovery semantics.

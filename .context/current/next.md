# Next actions

1. Seal Manager generation 7 with pilot PASS, read-back stabilization, authoritative Trace counting, and production admission.
2. Reconfigure existing PP-RM Worker A/B from pilot-only prompts to production package `IOS-M1-R1`; do not create another worker pair.
3. Seed production Mailbox/Trace/Pulse while all five PP-RM objects are disabled.
4. Fresh-read and verify all production register state.
5. Arm Worker A only.
6. A/B fresh-reconcile live `main`, inspect exact historical diffs, and restore only:
   - raw APFS output semantics from `d743b2e...`;
   - regression coverage from `b3befaeb...`.
7. Run minimum deterministic validation; if green, run exact Windows E2E.
8. Continue A/B bounded turns until a defined high-level checkpoint.
9. At launchd/AMFI, persistent error 79, unexpected regression, ambiguous side effect, protocol failure, or objective completion: stop successor chaining and return exact evidence to Manager.
10. Continue tagged OCB telemetry in production; do not infer OCB optimization from the zero-OSB pilot.

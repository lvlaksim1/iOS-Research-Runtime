# Procedural memory

Updated: 2026-10-01 11:04 MSK

- Manager generation19/package008 is Owner-authorized.
- Packages005,006,007 are terminal/superseded and must not resume.
- Product main at package008 bootstrap is `a380f7839f04ea9f7e3a87e2342fb76b6697e9b6`.
- Exact-main E2E run `36798385755` exists and completed FAILURE; Windows Build `36798385752` SUCCESS.
- E2E steps 1-11 succeeded, including bundled patched rcodesign build; provisioning/root-shell proof failed; failure evidence upload succeeded.
- AppleSEPManager endpoint timeout repetition is current product evidence.
- Generation19 adds nonterminal `WAIT_EXTERNAL_EVIDENCE`.
- A single negative exact-SHA run search never produces OWNER_GATE.
- Workers enter WAIT when required run is absent or queued/in_progress and do not arm another Worker.
- Recurring Watchdog owns later external-evidence observation.
- Terminal external evidence creates a fresh READY generation and wakes wait_resume_owner_slot.
- OWNER_GATE for unavailable start-new-workflow requires >=3 independent negative Watchdog observations AND >=15 minutes elapsed AND no exact-SHA run AND a genuinely required new run.
- Generation16 frozen mutation, generation17 recurring Watchdog, generation18 result-first evidence and OCB3 remain unchanged.

# Current blockers and open risks

Updated: 2026-10-01 11:04 MSK

## Product blocker
Verified recovery root shell remains unproven.

Current exact-main E2E run `36798385755` completed FAILURE at `Run provisioning and Darwin root-shell proof` after successful build/setup and bundled patched rcodesign construction. Failure evidence repeatedly reports AppleSEPManager endpoint timeouts. The next bounded unit is evidence-driven diagnosis of that failure, not another blind rerun.

## Runtime defect corrected by generation19
Package007 falsely terminalized because a single exact-SHA run search returned no observable run shortly before the automatic push-triggered E2E became visible.

Generation19 makes external evidence absence nonterminal:
- `WAIT_EXTERNAL_EVIDENCE` is Watchdog-owned;
- one negative observation never yields OWNER_GATE;
- queued/in-progress runs are observed, not duplicated;
- terminal success/failure/cancelled/timed-out/action-required conclusions are all usable evidence for a fresh Worker to analyze;
- OWNER_GATE for unavailable start-new-workflow requires >=3 independent negative Watchdog observations AND >=15 minutes elapsed AND no exact-SHA run of any observable state.

## Residual risks
- GitHub/run visibility can lag.
- Scheduled Task delivery can be delayed; DTSTART is not an SLA.
- hourly Watchdog recurrence is a recovery floor, not a five-minute guarantee.
- Scheduled Tasks have no CAS; stale already-running control-plane work remains possible.
- frozen mutation descriptor must remain unchanged across recovery.
- main neither frozen baseline nor target => FAIL_STOP.

## OCB
Explicit OSB only; maximum three exact-identical attempts total; no fourth.
Ambiguous mutable result requires authoritative reconciliation.

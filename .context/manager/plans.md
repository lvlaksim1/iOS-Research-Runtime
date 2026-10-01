# Manager plans

## PP-RM generation19 — persistent external-evidence wait

Manager generation: 19.
Product authority: `main`.
Current product: `main@a380f7839f04ea9f7e3a87e2342fb76b6697e9b6`.
Authorized package: `IOS-M1-CONTINUOUS-008`.

### Topology
Exactly five Scheduled Tasks: Worker A, Worker B, Runtime Mailbox, Trace, Watchdog.
No Lifeboat or additional PP-RM slot.
Worker A/B and Watchdog prompts are immutable after package configuration.

### Preserved protocols
Generation16 READY/PREPARE -> fresh MUTATION_READY frozen-target publication is unchanged.
Generation17 recurring-hourly Watchdog with +5m fast-path slide is unchanged.
Generation18 result-first workflow evidence is unchanged.

### New state: WAIT_EXTERNAL_EVIDENCE
Purpose: represent a healthy pause while required external GitHub Actions evidence is not yet terminal/visible.

Mailbox wait fields:
- `expected_workflow`
- `expected_head_sha`
- `wait_started_at`
- `wait_last_observation_at`
- `wait_observation_count`
- `wait_negative_observation_count`
- `wait_resume_owner_slot`
- `wait_last_run_id`
- `wait_last_run_status`
- `wait_last_run_conclusion`

Worker behavior:
1. search existing exact-SHA runs before any dispatch.
2. terminal run => consume/analyze result.
3. queued/in_progress => publish WAIT_EXTERNAL_EVIDENCE, arm no Worker.
4. no observable exact-SHA run => publish WAIT_EXTERNAL_EVIDENCE with negative_observation_count=1, arm no Worker.
5. ensure recurring Watchdog remains enabled.
6. one negative observation MUST NOT produce OWNER_GATE.

Watchdog WAIT behavior:
1. perform normal recurring self-preservation prefix.
2. read Scheduled Tasks once.
3. when state=WAIT_EXTERNAL_EVIDENCE, perform read-only exact-SHA workflow search.
4. terminal run found => increment generation, create fresh READY baton for wait_resume_owner_slot, clear wait fields, Trace EVIDENCE_READY; FINAL operation arm that Worker.
5. queued/in_progress => keep WAIT, update observation metadata, do not arm Worker.
6. no run => increment independent negative observations.
7. if negative count <3 OR elapsed <15 minutes => keep WAIT.
8. only when negative count>=3 AND elapsed>=15m AND no exact-SHA run exists may start-new-workflow necessity be evaluated.
9. OWNER_GATE for missing start capability only if a new run is truly required and no authorized alternative exists.

Any terminal workflow conclusion is evidence. Success/failure/cancelled/timed_out/action_required does not itself decide product success; a fresh Worker analyzes the evidence.

### Package008 bootstrap
Initial Worker B consumes existing E2E run `36798385755` on exact main.
It must analyze failure evidence around provisioning/root-shell and AppleSEPManager endpoint timeouts, then perform one bounded diagnostic/fix unit.

### Terminal path
FINAL_COMPLETED, FAIL_STOP, or genuine OWNER_GATE is published durably first; Watchdog then disables itself.

### OCB3
Explicit OSB only; three exact-identical attempts maximum; no attempt4; reconcile ambiguous mutable results.

# Manager plans

## Governance and recovery

Persistent-manager migration is COMPLETE. IOSPM-001 is independently CLOSED. Manager-state generation 3 was recovered and verified coherent on 2026-09-28. Product authority and Manager authority remain split: `main` vs `manager-state`.

## Product reconciliation after rollback

1. Verify live product `main`. COMPLETE: `85d408075ab8a66f6d16043029eb2255956eb1b9`.
2. Compare it to the old product baseline `3b0f5648f004f58daef526082b3d2a32d132edcf`. COMPLETE: only Context Capsule discovery files differ; product code is unchanged.
3. Reclassify the previous `669f2b...` launchd/AMFI state as historical verified evidence, not current product state. COMPLETE.
4. Use exact E2E `35634992757` at the code-equivalent baseline as the conservative current technical boundary until new exact-current-SHA runtime evidence exists. COMPLETE.

## PP-RM operating plan

The Manager owns strategy. PP-RM A/B owns only bounded execution of the current work package.

Normal cycle:
1. Manager publishes one high-level work package: objective, product baseline, allowed scope/effects, forbidden effects, verification contract, and checkpoint/stop conditions.
2. Fresh A/B runtime validates inbound Mailbox state and ACKs the prior baton.
3. It reconciles live `main` before consequential product writes.
4. It executes one bounded turn only.
5. It completes all product side effects before publishing handoff.
6. It writes Pulse, Runtime Mailbox, performs exact read-back, records SEND/Trace, then arms exactly one successor as the final tool operation.
7. After arming successor, the predecessor performs no further tool operations.
8. If a high-level checkpoint/stop condition is reached, it writes the evidence/checkpoint and does not continue strategic work; Manager must review and issue the next work package.

A/B MUST NOT:
- change the project milestone, Manager mandate, priority ordering, or work-package objective;
- mutate `manager-state` as part of ordinary execution;
- revive the retired shift-worker factory;
- publish production releases;
- perform broad speculative APFS/security-policy mutations outside the active work package;
- treat OCB itself as ownership/authority change.

OCB handling:
- absence of an expected server response is routine OCB, not proof of hostile blocking;
- retry read/query operations as needed;
- before retrying a mutating operation, read back authoritative server state when possible and preserve idempotency/deduplication;
- escalate to Manager only if side-effect state becomes ambiguous, the protocol invariant cannot be re-established, or a new strategic decision is required.

## Initial PP-RM work package — IOS-M1-R1

Objective: restore the previously verified raw-APFS packaging correction onto the current rolled-back product line and determine the new exact runtime boundary.

Baseline:
- product authority: `main@85d408075ab8a66f6d16043029eb2255956eb1b9`;
- manager authority: sealed generation 4 on `manager-state` after this Persist.

Evidence-backed changes to recover:
- product change from historical commit `d743b2e728d9cda194c7e76909f76a5f1704194f`: emit rebuilt ramdisk as raw APFS rather than wrapping it back into DMG;
- regression test from `b3befaeb8c0f2635623d3d8a56226199d2d0753e`.

Execution:
1. Inspect the exact diffs of `d743b2e...` and `b3befaeb...` against their parents; do not blindly restore unrelated later commits.
2. Reapply only the evidence-backed product/test semantics to current `main`.
3. Run the minimum relevant deterministic test/build gate.
4. If the narrow gate passes, run the Windows E2E needed to establish the exact current boot boundary.
5. Classify result:
   - reaches launchd / AMFI boundary again -> HIGH-LEVEL CHECKPOINT to Manager with exact SHA/run/log evidence; do not independently choose the next AMFI strategy;
   - still fails APFS error 79 -> HIGH-LEVEL CHECKPOINT to Manager with exact evidence and comparison against historical successful correction;
   - unexpected different regression -> HIGH-LEVEL CHECKPOINT to Manager;
   - tooling/OCB without ambiguous side effects -> handle routinely and continue;
   - ambiguous mutating side effect or PP-RM invariant violation -> FAIL-STOP and return to Manager.

## Manager-state coherence protection

Every replacement Manager runtime must pass the sealed-generation integrity marker before consequential continuation. PP-RM operational baton/mailbox state is not manager identity and does not replace Context Capsule persistence.

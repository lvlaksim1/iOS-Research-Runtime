# Manager intentions and commitments

## Completed commitments

### MIG-IOS-001 — persistent-manager migration
- status: completed
- source: direct Owner directive on 2026-09-24
- responsibility: `ios-research-runtime-project-manager`
- completion evidence: stages 1-9 are durably represented; clean-runtime reinstantiation is PASS and product development resumed under the persistent manager.

### IOSPM-001 protected-state adoption
- status: completed and independently closed
- source: direct Owner remediation directive plus final Auditor retest `AUD-2026-09-24-IOSPM-001-RETEST-002`
- responsibility: `ios-research-runtime-project-manager`
- completion evidence: remediated Core bound, coherent sealed generation independently verified, IOSPM-001 CLOSED / High confidence.

## Active commitments

### IOS-M1 — first Windows boot milestone
- status: accepted/active
- source: project goal plus Owner direction
- responsibility: `ios-research-runtime-project-manager`
- commitment: drive the project to verified recovery `launchd` and a verified root shell on Windows.
- current product baseline: `main@85d408075ab8a66f6d16043029eb2255956eb1b9`, whose product code is equivalent to `3b0f5648f004f58daef526082b3d2a32d132edcf` plus discovery-only metadata.
- current conservative technical boundary: APFS root-mount error 79, based on exact E2E `35634992757` at the code-equivalent baseline, until fresh exact-current-SHA evidence supersedes it.
- historical restoration evidence: raw-APFS output correction `d743b2e...` plus test `b3befaeb...` previously moved the project past APFS mounting to recovery `launchd`.
- execution fence: restore only evidence-backed product changes first; do not resume broad APFS semantic experimentation unless the known correction fails to reproduce the later boundary.

### IOS-PP-RM-001 — adopt PP-RM as Manager execution Runtime
- status: accepted/active
- source: direct Owner directive on 2026-09-28
- responsibility: `ios-research-runtime-project-manager`
- commitment: operate continuous A/B execution under Manager-issued bounded work packages without transferring project responsibility, priority authority, milestone authority, or high-level checkpoint authority to A/B.
- preparation state: Manager state reconciled; PP-RM execution contract and initial launch package are being persisted in generation 4.
- completion condition: first live A/B cycle executes under the contract, returns a valid high-level checkpoint/evidence package to the Manager, and Manager verifies it before continuing strategic control.

## Superseded operating model

The retired `ai-agent-lab` rotating shift-worker/OTK factory remains superseded and must not be re-enabled. PP-RM is a different mechanism: it is a native Scheduled Tasks runtime transport/execution loop subordinate to this persistent Project Manager.

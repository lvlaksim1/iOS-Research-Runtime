# Current state

Updated: 2026-10-01 22:39 MSK

## Governance
- manager: `ios-research-runtime-project-manager`
- manager generation: 24
- macro stage: LARGE STAGE 1 — Full iOS System Boot
- product authority: `main@32dd17014113543862e756c7daa52822e2eec073`
- execution status: ACTIVE / WAIT_EXTERNAL_EVIDENCE
- active package: `IOS-M3-CONTINUOUS-010`
- PP-RM runtime schema: 10

## Product progress
Recovery/root-shell foundation remains reproducible.
GPEX/PCIe root plumbing and bounded ECAM/MMIO windows are present in the darwin machine.
Exact-SHA E2E `36908440572` on `82c710bd243a57f89964a8c381879e14f1a0b4fc` succeeded, but `/dev/disk*` remained absent.
Generation45 identified Apple I/O hierarchy as the next bounded dependency.

Commit `32dd17014113543862e756c7daa52822e2eec073` moves the PCIe discovery node from DeviceTree root under `arm-io`.

## Current wait
Workflow: Windows End-to-End Boot.
Exact head: `32dd17014113543862e756c7daa52822e2eec073`.
Run: `36915159246`.
State: in progress / WAIT_EXTERNAL_EVIDENCE.
Resume owner: Worker B.

## PP-RM resilience
DEC-0018 adopted.
OCB3 no longer implies OWNER_GATE.
Transient OCB is recovered by fresh Worker runtime, alternate compliant path, or Watchdog OCB_BACKOFF.
Only a genuine no-compliant-path safety/governance boundary may terminalize on safety grounds.

## Constraints
Do not stage SystemOS until guest-visible storage is evidenced.
Packages005–009 remain terminal/superseded and must not resume.

# Current state

Updated: 2026-10-01 15:18 MSK

## Governance
- manager: `ios-research-runtime-project-manager`
- manager generation: 21
- product authority: `main@24730a74051378d228efd370f3baee5a4f46bdfa`
- PP-RM architecture: generation19 persistent external-evidence wait + generation18 result-first evidence + generation17 recurring Watchdog + generation16 native two-phase mutation
- execution status: ACTIVE / IOS-M2 / WAIT_EXTERNAL_EVIDENCE
- active package: `IOS-M2-CONTINUOUS-009`
- scheduler handoff: Mailbox/Trace/Worker programs prepared; Watchdog is the designated external-evidence carrier

## Completed foundation
IOS-M1 remains COMPLETE. Exact-SHA E2E run `36844422600`, job `110311023233`, proved recovery Darwin, launchd, interactive root shell, Darwin uname, `whoami=root`, root filesystem listing and `__IOS_RESEARCH_PROOF_END__`.

## IOS-M2 product progress
Commit `24730a74051378d228efd370f3baee5a4f46bdfa` was published to `main`.
It adds a bounded post-root boundary probe to the existing integration harness after the verified IOS-M1 proof.
Probe evidence requested:
- mounts/filesystem topology;
- `/System/Volumes`;
- `/private/preboot`;
- `/dev/disk*`;
- `launchctl list`.

The normal `windows-e2e.yml` push path includes the integration harness and is expected to produce exact-SHA evidence for this commit.

## Current execution state
Package009 Mailbox is `WAIT_EXTERNAL_EVIDENCE` for `.github/workflows/windows-e2e.yml` on exact head `24730a74051378d228efd370f3baee5a4f46bdfa`.
Worker A/B remain disabled until Watchdog observes terminal evidence.
The Watchdog may only perform read-only GitHub reconciliation while waiting.

## Known residual issues
Post-proof QEMU/harness nontermination and repeated `AppleSEPManager` endpoint timeouts remain observations, not yet promoted to the IOS-M2 root blocker.

Packages005–008 must not resume.

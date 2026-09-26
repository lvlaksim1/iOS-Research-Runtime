# Current state

## Governance topology

- persistent manager: `ios-research-runtime-project-manager`;
- manager-state authority: `manager-state`;
- product authority: `main`;
- discovery branch: `main`;
- legacy `ai-agent-lab` iOS autonomy: archived/migrated and not an orchestrator;
- Context Capsule Core: `3a942bd269ec7ee164575589e702e5074da30a29`;
- manager-state coherence protection: enabled and sealed.

## Commitment state

`MIG-IOS-001` is completed. IOSPM-001 protected-state adoption is completed and independently closed by `AUD-2026-09-24-IOSPM-001-RETEST-002`.

`IOS-M1` remains accepted/active. Recovery `launchd` is now reached; verified root shell remains outstanding.

## Verified technical boundary

Live product `main`: `669f2b989cf2ab5a0958ca517334a485062e8406`.

Post-capsule product changes include:
- `d743b2e728d9cda194c7e76909f76a5f1704194f` — emit rebuilt ramdisk as raw APFS rather than wrapping it back into DMG;
- `b3befaeb8c0f2635623d3d8a56226199d2d0753e` — regression test for exact raw APFS byte output;
- later commits primarily reduce Actions artifact publication/retention.

Current exact CI:
- Ramdisk Tool Windows `36125764919` — COMPLETED / SUCCESS.
- qemu-sptm Windows Gate `36125764912` — COMPLETED / SUCCESS.
- Windows End-to-End Boot `36127395221` — COMPLETED / FAILURE at root-shell proof.
- E2E artifact: `10862632528 / ios-darwin-windows-e2e`;
- digest: `sha256:456d1d12887572fa60570ce717c3bf32c850c46a6eebc9df93049a089601d809`.

Runtime evidence from job `108046547984`:
- `BSD root: md0` is reached;
- no `mountroot failed` line is present;
- `launchd` starts;
- the harness reports “launchd запущен. Ожидаем root shell”;
- repeated `AMFI: code signature validation failed` and `Launch Constraint Violation (enforcing)` occur for `/bin/bash`;
- verified root shell is not reached.

The former APFS error-79 blocker is therefore superseded for current `main`. The active product boundary is AMFI/launch-constraint rejection of the shell execution path.

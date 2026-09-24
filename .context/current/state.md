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

`IOS-M1` remains accepted/active under direct Owner direction to resume planned project development.

## Verified technical boundary

Current exact product commit is `1ff060bd867587cc0e4c04e3469d9fb6488147e3`, verified as live `main`.

Exact CI at that product SHA:
- Ramdisk Tool Windows `36018076878` — COMPLETED / SUCCESS.
- Windows End-to-End Boot `36018076770` — COMPLETED / FAILURE at Darwin root-shell proof.
- artifact: `10815533344 / ios-darwin-windows-e2e`;
- digest: `sha256:163ec0f9cdca8542818dd4bb48b023ba1d9a46c1b38d03eeb8c6eb6ef3d10956`;
- serial evidence still reports APFS `mountroot failed, error: 79`.

The active product operation is analysis of that already-produced enriched artifact. No E2E rerun and no speculative APFS writer mutation is authorized merely for continuation.

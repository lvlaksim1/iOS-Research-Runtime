# Current state

## Governance topology

- persistent manager: `ios-research-runtime-project-manager`;
- manager-state authority: `manager-state`;
- product authority: `main`;
- discovery branch: `main`;
- legacy `ai-agent-lab` iOS autonomy: archived/migrated and not an orchestrator;
- Context Capsule Core: `3a942bd269ec7ee164575589e702e5074da30a29`;
- manager-state coherence protection: enabled and sealed in this generation.

## Commitment state

Persistent-manager migration and clean-runtime reinstantiation are complete. `MIG-IOS-001` remains completed. `IOS-M1` remains accepted/active.

Owner-authorized IOSPM-001 remediation adoption is completed by binding this manager to the remediated Core and sealing the coupled BDI/current/handoff state. This changes manager-state governance only; product `main` remains `1ff060bd867587cc0e4c04e3469d9fb6488147e3`.

## Verified technical boundary

Current exact product commit is `1ff060bd867587cc0e4c04e3469d9fb6488147e3`, verified as live `main`. The diagnostic-only change emits fuller APSB diagnostics, recursively read root-tree evidence and file-extent summaries; APFS writer/allocation/XID/checkpoint/on-disk semantics were not changed.

Exact CI at that product SHA:
- Ramdisk Tool Windows `36018076878` — COMPLETED / SUCCESS.
- Windows End-to-End Boot `36018076770` — COMPLETED / FAILURE at step 11 `Run provisioning and Darwin root-shell proof`.
- failure-evidence collection and end-to-end artifact upload succeeded;
- artifact: `10815533344 / ios-darwin-windows-e2e`;
- digest: `sha256:163ec0f9cdca8542818dd4bb48b023ba1d9a46c1b38d03eeb8c6eb6ef3d10956`;
- serial evidence repeatedly reports `BSD root: md0` followed by APFS `mountroot failed, error: 79`.

The next product operation is analysis of the already-produced enriched artifact, not another E2E rerun and not a speculative writer mutation.

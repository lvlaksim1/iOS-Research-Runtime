# Latest handoff

Persistent manager: `ios-research-runtime-project-manager`.
Manager-state authority: `manager-state`.
Product authority: `main`.

## Durable commitment

`MIG-IOS-001` is completed. `IOS-M1` remains active: reach verified recovery `launchd` and root-shell boot on Windows.

## Exact recovered product coordinates

Current product SHA: `1ff060bd867587cc0e4c04e3469d9fb6488147e3` (live `main`).
The change is diagnostic-only: enriched APSB/root-tree/file-extent evidence; no APFS writer/allocation/XID/checkpoint/on-disk semantic mutation.

Ramdisk Tool Windows `36018076878`: terminal SUCCESS at the exact SHA; tests, Windows build, smoke test and helper artifact upload succeeded.

Windows End-to-End Boot `36018076770`: still IN PROGRESS at the exact SHA. Job `107695937346` is executing step 11 `Run provisioning and Darwin root-shell proof`; evidence collection/upload remains pending.

## Continuation

Do not restart the engineering cycle and do not rerun the existing E2E merely because the Runtime changed. When `36018076770` becomes terminal, inspect its exact job logs and artifact, integrate enriched APSB/root-tree/file-extent evidence, and only then choose the next discriminator or smallest evidence-backed writer hypothesis. Writer semantics remain fenced until concrete discriminator evidence exists.

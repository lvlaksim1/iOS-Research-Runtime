# Manager plans

## Current checkpoint

Product authority:
- `main@cbba4060db543d4a2b800f7c15b2a700e69f6961`

Exact current CI:
- Ramdisk Tool Windows `36483217843`: SUCCESS
- Windows Build `36483217817`: SUCCESS
- Windows End-to-End Boot `36483217835`: FAILURE before Darwin boot
- Windows Full Package `36483310512`: SKIPPED

Current E2E blocker:
- job `109133700969`
- failed step: `Download QEMU runtime from gate`
- exact failure: artifact `qemu-sptm-windows-gate` not found
- downstream provisioning/root-shell steps were skipped

## OCB evidence checkpoint

Observed publication sequence across targeted runs:
1. full production turn: update-ref attempt1=EXPLICIT_OSB, attempt2=EXPLICIT_OSB, no publication;
2. minimal targeted probe #1: same target update-ref attempt1=SUCCESS, publication confirmed;
3. minimal targeted probe #2, same request parameters with main already at target: attempt1=EXPLICIT_OSB, attempt2=EXPLICIT_OSB, attempt3=SUCCESS.

Interpretation:
- request context/sequence appears to affect passability;
- a third exact-identical attempt can succeed after two explicit OSBs;
- current evidence is too small and partly idempotent to set a universal permanent retry count;
- any mutation retry policy must preserve exact server-state reconciliation.

## Next development sequence

1. Keep PP-RM paused while Manager owns this checkpoint.
2. Before any new A/B run, deliberately reseed Mailbox/Pulse/Trace because the current Mailbox is stale after the minimal targeted probes.
3. Resolve the current E2E infrastructure blocker by restoring/producing the expected `qemu-sptm-windows-gate` artifact or otherwise repairing the existing gate path using repository evidence; do not change iOS/APFS product semantics merely to bypass the missing artifact.
4. Rerun Windows End-to-End Boot against exact product SHA `cbba4060...`.
5. Classify the first genuine boot-stage result for `cbba4060...`:
   - persistent APFS error 79 -> Manager checkpoint;
   - recovery `launchd` / AMFI boundary -> Manager checkpoint;
   - unexpected regression -> Manager checkpoint;
   - root shell -> evaluate IOS-M1 completion;
   - infrastructure/tool ambiguity -> Manager checkpoint.
6. Separately review OCB retry policy from the accumulated Trace evidence. Until a deliberate Manager decision is persisted, treat the third attempt as experimentally supported but not universal.

## Continuity

Every replacement Manager runtime must verify the sealed generation before consequential action. Live Scheduled Task registers never replace Manager-state authority.

# Manager intentions and commitments

## Completed

### MIG-IOS-001
- status: completed
- responsibility: `ios-research-runtime-project-manager`

### IOSPM-001 protected-state adoption
- status: completed and independently closed

### IOS-PP-RM-PILOT-001
- status: completed / PASS on attempt 2
- result: A1 -> B2 -> A3 -> FINAL completed with exact SEND/ACK handoffs and safe terminal state.
- durable corrections: bounded read-only register stabilization; authoritative GitHub operation counts come from tagged Trace events.

### OCB3 targeted retry experiment
- status: completed / evidence captured
- first minimal targeted publication probe: attempt1=SUCCESS and `main` moved to `cbba4060...`.
- repeated minimal probe with same request parameters while `main` already equaled target: attempt1=EXPLICIT_OSB, attempt2=EXPLICIT_OSB, attempt3=SUCCESS.
- conclusion: third identical attempt can improve passability in at least one observed run; evidence is insufficient to make three attempts a permanent universal rule.
- responsibility: `ios-research-runtime-project-manager`

## Active

### IOS-M1 — first Windows boot milestone
- status: active
- responsibility: `ios-research-runtime-project-manager`
- current product: `main@cbba4060db543d4a2b800f7c15b2a700e69f6961`
- current exact-SHA gate state: ramdisk tool and Windows build PASS; E2E blocked before boot because artifact `qemu-sptm-windows-gate` is missing.
- commitment: restore exact E2E execution for current SHA, then continue evidence-driven boot investigation to verified `launchd` and root shell.

### IOS-PP-RM-001 — PP-RM production execution
- status: admitted / paused at Manager checkpoint
- responsibility: `ios-research-runtime-project-manager`
- next runtime action requires deliberate Manager reseed because current Mailbox is stale relative to project truth.
- A/B remain execution carriers only; Manager retains strategy and durable state ownership.

## Superseded

The retired `ai-agent-lab` rotating shift-worker/OTK factory remains superseded and must not be re-enabled.

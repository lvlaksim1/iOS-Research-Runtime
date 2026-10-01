# PP-RM Launch Package — generation 19

Status: RUNNING / WAIT_EXTERNAL_EVIDENCE
Manager generation: 21
Package: `IOS-M2-CONTINUOUS-009`
Product start: `main@95caa93fc8fd0db827491e679628efa40612b55c`
Current product: `main@24730a74051378d228efd370f3baee5a4f46bdfa`
Previous package: `IOS-M1-CONTINUOUS-008` — FINAL_COMPLETED / MUST NOT RESUME

## Mission
IOS-M2 — Full iOS Boot Boundary.

Determine the first verified technical boundary between the working recovery/root-shell environment and full iOS system userland.

## Acceptance
Complete IOS-M2 when exact runtime evidence establishes either:
- progression into full system userland/system-launchd territory; or
- the first concrete blocking dependency with enough reproducible evidence to define the next bounded mutation without speculation.

## First bounded step — published
Commit `24730a74051378d228efd370f3baee5a4f46bdfa` preserves the proven IOS-M1 root-shell path and adds a post-root diagnostic probe for:
- mounts/filesystem topology;
- `/System/Volumes`;
- `/private/preboot`;
- visible `/dev/disk*` nodes;
- `launchctl list`.

No QEMU hardware, provisioning or trust/security semantics were changed.

## Current wait
Expected workflow: `.github/workflows/windows-e2e.yml`.
Expected exact head: `24730a74051378d228efd370f3baee5a4f46bdfa`.
Mailbox state: `WAIT_EXTERNAL_EVIDENCE`.
Resume slot after terminal evidence: Worker A.
Watchdog may perform read-only GitHub reconciliation only while waiting.

## Runtime architecture retained
- generation16 native two-phase mutation;
- generation17 recurring-backstop Watchdog;
- generation18 result-first workflow evidence;
- generation19 WAIT_EXTERNAL_EVIDENCE;
- OCB3.

## Supersession
Packages005,006,007 and completed package008 MUST NOT resume.

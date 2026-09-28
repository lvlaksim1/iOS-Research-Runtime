# Project architecture

## DECISION — Product architecture

The first-milestone product has four main layers:

1. Windows WPF GUI in `src/IOSResearchRuntime`;
2. provisioning services that acquire pinned tools/resources, extract IPSW material, patch firmware metadata, rebuild the recovery ramdisk, and construct trust-cache inputs;
3. a Windows-packaged `qemu-sptm` runtime with the Darwin machine and project portability patches;
4. evidence-producing integration automation, especially `.github/workflows/qemu-sptm-windows.yml` and `.github/workflows/windows-e2e.yml`.

The GUI delegates product work to services such as the runtime coordinator, tool/resource bootstrap, raw firmware provisioning, ramdisk provisioning, and QEMU runtime management.

## Authority topology

- product authority branch: `main`;
- durable Project Manager state branch: `manager-state`;
- discovery branch: `main`.

Manager-state commits are not product releases and must not be used as substitutes for live product evidence on `main`.

## Execution architecture — PP-RM

PP-RM is the approved continuous execution Runtime for ordinary manager-directed development.

- persistent Agent / commitment owner: `ios-research-runtime-project-manager`;
- disposable execution carriers: alternating Worker A and Worker B Scheduled Task runtimes;
- operational transport: Runtime Mailbox;
- progress evidence: Pulse Register;
- delivery/audit evidence: Trace / Result Register with SEND / ACK / FINAL / FAIL;
- predecessor publishes and verifies handoff, then arms one successor as its final tool operation;
- GitHub remains product/evidence infrastructure and is not the PP-RM ownership, heartbeat, mailbox, or baton control plane.

Manager and PP-RM responsibilities are intentionally asymmetric: Manager decides direction, priority, work package, and high-level checkpoints; A/B continuously execute within that package and return evidence when strategic review is required.

## Current boot boundary

Current product code is equivalent to baseline `3b0f564...`; exact historical E2E on that code reached `BSD root: md0` and failed APFS root mount with error 79. Later historical commits proved a raw-APFS packaging correction can move this path to recovery `launchd`, but that later product state is not currently on `main`.

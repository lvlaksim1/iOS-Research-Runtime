# Project architecture

## DECISION — Product architecture

The product has four main layers:

1. Windows WPF GUI in `src/IOSResearchRuntime`;
2. provisioning services that acquire pinned tools/resources, extract IPSW material, patch firmware metadata, rebuild the recovery ramdisk, and construct trust-cache inputs;
3. a Windows-packaged `qemu-sptm` runtime with the Darwin machine and project portability patches;
4. evidence-producing integration automation, especially `.github/workflows/qemu-sptm-windows.yml` and `.github/workflows/windows-e2e.yml`.

The GUI delegates product work to services such as the runtime coordinator, tool/resource bootstrap, raw firmware provisioning, ramdisk provisioning, and QEMU runtime management.

## Authority topology

- product authority branch: `main`;
- durable Project Manager state branch: `manager-state`;
- discovery branch: `main`.

Manager-state commits are not product releases and must not substitute for live product evidence on `main`.

## Execution architecture — PP-RM

PP-RM is the approved continuous execution Runtime for ordinary manager-directed development.

- persistent Agent / commitment owner: `ios-research-runtime-project-manager`;
- disposable execution carriers: alternating Worker A and Worker B Scheduled Task runtimes;
- operational transport: Runtime Mailbox;
- progress evidence: Pulse Register;
- delivery/audit evidence: Trace / Result Register with SEND / ACK / FINAL / FAIL;
- predecessor publishes and verifies handoff, then arms one successor as its final tool operation;
- GitHub remains product/evidence infrastructure and is not the PP-RM ownership, heartbeat, mailbox, or baton control plane.

Manager and PP-RM responsibilities are asymmetric: Manager decides direction, priority, package, and strategic checkpoints; A/B execute within that package.

## Verified current boot boundary

IOS-M1 is complete on `main@95caa93fc8fd0db827491e679628efa40612b55c`.
Exact-SHA Windows E2E run `36844422600` / job `110311023233` proves recovery Darwin, recovery `launchd`, an interactive root shell, Darwin kernel identity, `whoami=root`, root filesystem listing and the proof-end marker.

The same run later fails at workflow level because QEMU/integration harness does not terminate cleanly after proof. Repeated `AppleSEPManager` endpoint timeout messages are also present. Neither observation invalidates IOS-M1.

The active architecture question is IOS-M2: identify the exact boundary between this recovery/root-shell environment and full iOS system userland. The first method is a post-root diagnostic probe; speculative QEMU hardware changes are deferred until runtime evidence classifies the blocker.

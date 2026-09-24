# Project architecture

## DECISION — High-level architecture

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

## Current boot boundary

The verified Windows E2E path reaches XNU, exposes the ramdisk as `md0`, enters APFS `mountroot`, and currently fails before `launchd` because the rebuilt APFS recovery ramdisk is rejected with error 79.

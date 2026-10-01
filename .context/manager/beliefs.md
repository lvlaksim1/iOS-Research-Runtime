# Manager beliefs

- Persistent Project Manager `ios-research-runtime-project-manager` remains commitment owner; product authority is `main`, Manager authority is `manager-state`.
- Owner-facing work is organized into four large stages; IOS-M* labels are internal checkpoints and do not create routine Owner gates.
- LARGE STAGE 1 — Full iOS System Boot — is active.
- IOS-M1 and IOS-M2 are complete.
- IOS-M2 proved recovery md0/devfs only, without guest-visible full-system disk, System/Volumes or private/preboot.
- BootKC evidence for iPhone17,3 contains IONVMeFamily and APFS, while a usable VirtIO storage path is absent.
- The darwin QEMU path now contains bounded GPEX/PCIe plumbing with ECAM/MMIO windows and remains capable of booting recovery/root shell.
- Exact-SHA E2E `36908440572` on `82c710bd243a57f89964a8c381879e14f1a0b4fc` succeeded but `/dev/disk*` remained absent.
- Current product authority is `main@32dd17014113543862e756c7daa52822e2eec073`, which moves the PCIe discovery node under `arm-io`.
- Current correct runtime state is WAIT_EXTERNAL_EVIDENCE for E2E run `36915159246` on that exact head.
- SystemOS staging remains deferred until guest-visible block transport is evidenced.
- Package009 is terminal FINAL_COMPLETED. Package010 is active. Packages005–009 must not resume.
- PP-RM runtime schema 10 and DEC-0018 are authoritative: OCB3 exhausts a disposable Worker runtime, not the package. Transient OCB self-heals through fresh-runtime failover / alternate compliant path / Watchdog OCB_BACKOFF.
- PP-RM must never bypass a substantive safety restriction; only a genuine no-compliant-path safety boundary may become OWNER_GATE.

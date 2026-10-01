# PP-RM Launch Package — runtime schema 10

Status: RUNNING / WAIT_EXTERNAL_EVIDENCE
Manager generation: 24
Package: `IOS-M3-CONTINUOUS-010`
Macro stage: LARGE STAGE 1 — Full iOS System Boot
Current product: `main@32dd17014113543862e756c7daa52822e2eec073`
Previous package: `IOS-M2-CONTINUOUS-009` — FINAL_COMPLETED / MUST NOT RESUME

## Mission
Continue autonomously from verified recovery/root-shell execution to real full-iOS system userland:
storage transport → guest-visible disk → SystemOS/Preboot/Data staging → APFS discovery/mounting → system launchd → core full-system userland.

IOS-M3 and later IOS-M* labels are internal engineering checkpoints only. They do not stop PP-RM or require Owner participation.

## Current bounded step
BootKC evidence established:
- IONVMeFamily present;
- VirtIO storage absent;
- APFS present.

The darwin QEMU machine now has bounded GPEX/PCIe plumbing and ECAM/MMIO windows. Recovery/root shell remains reproducible.

Exact-SHA E2E `36908440572` on `82c710bd243a57f89964a8c381879e14f1a0b4fc` succeeded but `/dev/disk*` remained absent.

Generation45 identified the next smallest correction: attach the PCIe discovery node under Apple `arm-io` instead of the DeviceTree root. Legacy OCB3 interrupted that Worker runtime. Manager recovery published:
`32dd17014113543862e756c7daa52822e2eec073` — `Attach PCIe discovery node under arm-io`.

## Current wait
Expected workflow: Windows End-to-End Boot.
Expected exact head: `32dd17014113543862e756c7daa52822e2eec073`.
Run: `36915159246`.
State: WAIT_EXTERNAL_EVIDENCE.
Resume owner after terminal evidence: Worker B.
Do not duplicate the run.

## OCB resilience
DEC-0018 is authoritative.
OCB3 exhausts only the current Worker runtime.
Fresh-runtime failover, alternate compliant path and Watchdog-owned OCB_BACKOFF are nonterminal recovery states.
A transient OCB must not become OWNER_GATE.

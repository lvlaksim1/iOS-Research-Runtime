# Current state

Updated 2026-10-27 MSK. Sealed manager generation: 28.
Manager: `ios-research-runtime-project-manager`. Product authority `main`; manager authority `manager-state`.
Macro stage: LARGE STAGE 1 — Full iOS System Boot, ACTIVE / NOT_PROVEN.
Product: `main@0b633cbafd2a0198a9053c6f760d9590c2496e14` (10 commits ahead of prior capsule baseline).

## Exact-head GitHub evidence
- Windows Build `39016012852`: FAILURE at Build.
- Windows End-to-End Boot `39016012955`: FAILURE at Run provisioning and Darwin root-shell proof.
- qemu-sptm Windows Gate `39016012886`: SUCCESS.
- Repository Storage Policy `40478805063`: SUCCESS on 2026-10-27; not a boot check.
Latest product commit reports consolidation of 61 archived change bundles. Full-system disk, APFS SystemOS/Preboot/Data and system launchd remain NOT_PROVEN. Historical recovery root shell and PCIe/NVMe capability facts do not establish current-head boot.

## PP-RM observation
Execution package `IOS-M3-CONTINUOUS-011` pinned to manager generation27 / `f26dd70e1b6687ffed72703ff809af5e16a0558d`; updating this capsule does not modify that fence.
Last inspected canonical Mailbox: GEN195 B READY, ACK NONE, progress_seq0; 64 mixed-status Library ZIP records. G194 5/5 synthetic negative tests, archive reported saved to Library and PENDING_GITHUB. G30/G71 PENDING_OCB; not retried.
Latest scheduler inspection: Workers A/B disabled, Watchdog enabled. B last reported scheduler-service failure before verified GEN195 ACK; live ownership is not established. No task changes performed during reconciliation.

## Next
Resolve scheduler control-plane ownership and exact-head Build/E2E failures before claiming progress. Continue storage proof thereafter, without treating recovery `md0` as full-system acceptance.

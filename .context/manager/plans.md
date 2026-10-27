# Manager plans

Updated 2026-10-27 MSK. Manager generation 28.
Macro stage: LARGE STAGE 1 ACTIVE / NOT_PROVEN; product `main@0b633cbafd2a0198a9053c6f760d9590c2496e14`.
Package `IOS-M3-CONTINUOUS-011` remains frozen to manager generation27 / `f26dd70e1b6687ffed72703ff809af5e16a0558d`.

## Verified position
Windows Build run `39016012852` FAILURE (Build step); E2E `39016012955` FAILURE (Run provisioning and Darwin root-shell proof); QEMU Gate `39016012886` SUCCESS. Root causes require logs.
Canonical Mailbox header GEN195 B READY ACK NONE progress_seq0; last Worker B result reported scheduler error, A/B disabled and Watchdog enabled in last readback. Not proof of active GEN195 execution.
Mailbox records 64 Library entries with mixed publication statuses. G194 5/5 synthetic tests and Library ZIP reported PENDING_GITHUB; G30/G71 explicit safety-refused publications PENDING_OCB.

## Ordered plan
1. Fresh-read `main` and full current PP-RM five-task identity, Mailbox canonical header, Trace, owner ACK/progress, latest A/B results. Do not dispatch until exact unique ownership and scheduler readiness are established.
2. Examine exact-head Windows Build and E2E failing job logs/annotations. Classify failures separately and do not invent root cause.
3. Review current `main` code and independently read back applicable immutable Library bundles before using them. Separate published archive records from genuinely pending changes.
4. Select the smallest distinct permitted source correction or diagnostic prerequisite; retain exact-SHA source, local-test, Windows Build, QEMU and E2E evidence gates. Synthetic parser tests do not prove guest interrupts.
5. Use actual PCIe/IOKit matching, NVMe device/IRQ-to-AIC and guest block-node evidence to locate the first missing dependency. Do not infer native `#ports` or write unsupported APFS semantics.
6. After authentic non-ramdisk `/dev/disk*` appears, stage outside Git and validate real SystemOS/Preboot/Data mounts, system launchd and full userland.
7. Reflect/Persist durable findings promptly in a coherently sealed manager generation.

Publication: no forced refs, no duplicate ambiguous writes, no alternate-route bypass of G30/G71 explicit refusals, no major binaries or release without Owner approval. Manager-state reconciliation is not a product change.

# Current blockers and open risks

Updated: 2026-10-27 MSK.
1. **CI:** exact `main@0b633cbafd2a0198a9053c6f760d9590c2496e14` Windows Build `39016012852` failed at Build; E2E `39016012955` failed at provisioning/root-shell proof; QEMU Gate `39016012886` passed. Specific causes not established until detailed logs are read.
2. **Guest storage:** historical BootKC has IONVMeFamily/APFS/AppleEmbeddedPCIE/AppleT8140PCIe and native `apcie` structure, but no proven real PCIe/IOKit binding, NVMe interrupt delivery, non-ramdisk `/dev/disk*`, APFS SystemOS/Preboot/Data mounts or system `launchd` on current head.
3. **Runtime ownership:** Mailbox GEN195 B READY/ACK NONE/seq0 conflicts with last B scheduler-service error and disabled A/B task flags. Watchdog enabled, its last audit inconclusive. Do not assume successful dispatch or repeat work without full canonical readback.
4. **Unpublished evidence:** 64 Mailbox Library records combine published and pending statuses; G194 5/5 synthetic fixture change is reported preserved in Library but PENDING_GITHUB. Library preservation is not GitHub publication or runtime proof.
5. **Explicit refusals:** G30/G71 GitHub write attempts remain PENDING_OCB; do not repeat or reroute refused operations. Preserve independently permissible work only.
6. **Generation boundary:** Manager capsule becomes generation28 while existing scheduler package remains frozen to generation27 / `f26dd70e1b6687ffed72703ff809af5e16a0558d`. No implied scheduler reauthorization.

Stage1 acceptance still requires reproducible Windows exact-SHA evidence of non-ramdisk guest storage, SystemOS/Preboot/Data, APFS and system launchd/core userland; recovery `md0` does not qualify.

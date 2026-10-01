# Next actions

Updated: 2026-10-01 17:09 MSK

1. Treat IOS-M2 as CLOSED / FINAL_COMPLETED on `main@4542112c90bb0f84a9a904726c54a3480ba07947`.
2. Add storage-driver capability diagnostics to `RawFirmwareProvisioningService` using the existing BootKC kext listing.
3. Publish the smallest diagnostic mutation to `main` without changing QEMU or downloading SystemOS.
4. Run/consume exact-SHA Windows E2E and record storage candidates: ANS/NVMe/embedded storage, VirtIO block, APFS.
5. Choose the guest storage transport from that evidence.
6. Implement a minimal host-backed block-device proof and require guest-visible disk-node evidence.
7. Only after transport proof, extract/stage SystemOS with `ipsw --dmg sys --device iPhone17,3` outside Git.
8. Proceed to APFS System/Preboot discovery.
9. Do not resume packages005–009.

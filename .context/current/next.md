# Next actions

Updated: 2026-10-01 22:39 MSK

1. Preserve `main@32dd17014113543862e756c7daa52822e2eec073`; do not duplicate the arm-io DeviceTree mutation.
2. Consume terminal exact-SHA Windows E2E run `36915159246`.
3. Check specifically for PCIe/NVMe discovery and `/dev/disk*`.
4. If disk visibility is achieved, add explicit proof and proceed automatically to SystemOS/APFS staging outside Git.
5. If not, isolate the next smallest PCIe/NVMe binding dependency from actual boot evidence and perform one bounded mutation.
6. Continue internal IOS-M* work without Owner gates until LARGE STAGE 1 acceptance or a genuine strategic/safety boundary.
7. Apply DEC-0018 on any OCB: fresh-runtime failover → alternate compliant path → Watchdog OCB_BACKOFF/replan; transient OCB must not stop the package.
8. Do not resume packages005–009.

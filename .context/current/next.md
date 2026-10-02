# Next actions

Updated: 2026-10-03 00:42 MSK

1. Preserve `main@a8c960bc7d26011c7e87e0791cb2e7621f0cd61e`; do not duplicate the unfiltered IORegistry mutation.
2. Consume terminal exact-SHA Windows E2E run `37068183031`.
3. Inspect unfiltered IODeviceTree and IOService output for the actual live PCIe hierarchy, provider classes, matching properties and any IONVMe-related service.
4. If no relevant PCIe provider is instantiated, isolate the smallest DeviceTree/service-matching dependency.
5. If PCIe binding exists but no NVMe endpoint binds, isolate the next endpoint/device-model/IOMMU/interrupt dependency.
6. If guest disk visibility is achieved, add explicit proof and proceed automatically to SystemOS/APFS staging outside Git.
7. Continue internal IOS-M* work without Owner gates until LARGE STAGE 1 acceptance or a genuine strategic/safety boundary.
8. Apply DEC-0018 on transient OCB.
9. Apply DEC-0019 for publication only when its strict conditions hold: canonical `update_ref(force=false)` first; after repeated explicit OCB on an unambiguous existing single-file bounded change, fresh-fetch the current blob SHA, publish the exact content through `update_file`, record the returned new authoritative SHA and obtain new exact-SHA CI evidence.
10. Do not use the DEC-0019 fallback for multi-file/ambiguous/non-equivalent publication or to bypass a substantive restriction.
11. Do not resume packages005–009.

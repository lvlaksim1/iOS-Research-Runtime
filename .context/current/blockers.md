# Current blockers and open risks

Updated: 2026-10-15 04:23 MSK

## Large Stage 1
Immediate technical boundary: native Apple PCIe/NVMe code and source DeviceTree descriptions are present, but XNU still has not registered a guest-visible disk.

Evidence now establishes:
- recovery boot and root shell work;
- IONVMeFamily and APFS are present;
- AppleEmbeddedPCIE and AppleT8140PCIe are present;
- source DeviceTree contains native apcie nodes, DART/IOMMU relationships and PCIe ranges;
- exact-SHA E2E `37063868899` is green;
- `/dev/disk*` remains absent;
- filtered runtime IORegistry did not expose matching PCIe/NVMe providers.

Latest verified product authority is `main@89cf1e04571545010c2433f24264bae25f5c5f2d`. Prior run `37068183031` belongs to earlier evidence and must be independently reconciled before reusing it.

The next technical blocker must be isolated from that evidence among DeviceTree-to-IOService matching, provider/class/property mismatch, bridge/endpoint instantiation, interrupt/IOMMU relationships, or NVMe device-model compatibility.

SystemOS extraction remains intentionally deferred.

## Current engineering and execution blocker
Package010 generations649–651 could not create a valid atomic host ADT plus QEMU PMGR pair. Six identical host source writes met explicit safety blocks. No preexisting complete exact direct-child target was found. The new package begins with read-only material prerequisite investigation; the blocked source write remains prohibited from blind retry.

## Runtime continuity and publication risk
Repeated explicit OCB on low-level `update_ref` publication has been demonstrated even for unambiguous bounded changes.
DEC-0018 keeps transient OCB nonterminal.
DEC-0019 records the narrow existing-single-file `update_file` fallback with fresh blob-SHA fencing, explicit semantic-equivalence recording, new authoritative commit SHA, and mandatory new exact-SHA evidence.
This fallback must not be generalized to ambiguous or multi-file publication and must never bypass a substantive safety restriction.

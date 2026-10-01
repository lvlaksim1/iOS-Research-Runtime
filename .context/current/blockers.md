# Current blockers and open risks

Updated: 2026-10-01 17:09 MSK

## IOS-M1 / IOS-M2
No blocker remains. Both milestones are complete.

## IOS-M3
The first blocker is storage transport selection.

Proven:
- full-system disk nodes are absent in the guest;
- the current application does not attach a system disk;
- upstream qemu-sptm `-M darwin` does not currently create the `vmapple` PCI/virtio storage path.

Unknown to resolve next:
- whether the iPhone17,3 BootKC contains a native VirtIO block driver;
- which ANS/NVMe/embedded-storage drivers are present and therefore represent the more native emulation target;
- whether a minimal DeviceTree/device-model addition can expose a host-backed block image without broad machine-model surgery.

SystemOS extraction is deliberately deferred until this transport question is answered, to avoid expensive CI downloads without a guest consumer.

## Residual observations
Repeated `AppleSEPManager` endpoint timeouts remain unassigned as a causal blocker.
GUI/SpringBoard remain later milestones.

## Runtime
Package009 is terminal FINAL_COMPLETED.
Package010 is the clean IOS-M3 successor and may be activated when external evidence is required.

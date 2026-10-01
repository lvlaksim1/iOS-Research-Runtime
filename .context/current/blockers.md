# Current blockers and open risks

Updated: 2026-10-01 17:13 MSK

## IOS-M3
Immediate blocker: exact evidence about storage drivers present in the actual iPhone17,3 BootKC.

Current architecture proves no full-system device is attached to `-M darwin`.
Upstream `vmapple-virtio-blk` cannot be adopted blindly because it belongs to another machine model.

Await exact-SHA E2E for `main@951575209542d70d9f370049b3d17cde83ee64cf`.

After evidence, the next blocker will be one of:
- native ANS/NVMe-compatible device emulation;
- Apple VirtIO transport integration if the iPhone kernel actually contains a usable driver;
- another directly evidenced storage class.

SystemOS extraction remains intentionally deferred.

## Runtime
Package010 is active in WAIT_EXTERNAL_EVIDENCE.
Packages005–009 are terminal/superseded.

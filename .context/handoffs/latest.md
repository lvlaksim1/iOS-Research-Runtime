# Latest handoff

Persistent manager: `ios-research-runtime-project-manager`.
Manager-state authority: `manager-state`.
Product authority: `main`.

## Governance closure

IOSPM-001 is CLOSED / Medium severity / High confidence by final independent retest `AUD-2026-09-24-IOSPM-001-RETEST-002`.

The manager remains bound to Context Capsule Core `3a942bd269ec7ee164575589e702e5074da30a29` with fail-closed sealed-generation integrity.

## Durable product commitment

`IOS-M1` remains active: verified recovery `launchd` plus verified root shell on Windows.

Live product SHA: `669f2b989cf2ab5a0958ca517334a485062e8406`.

Verified current boundary:
- raw-APFS packaging correction: `d743b2e728d9cda194c7e76909f76a5f1704194f`;
- regression test: `b3befaeb8c0f2635623d3d8a56226199d2d0753e`;
- Ramdisk Tool Windows `36125764919`: SUCCESS;
- qemu-sptm Windows Gate `36125764912`: SUCCESS;
- Windows End-to-End Boot `36127395221`: FAILURE at root-shell proof;
- artifact `10862632528`, digest `sha256:456d1d12887572fa60570ce717c3bf32c850c46a6eebc9df93049a089601d809`.

The current E2E reaches `BSD root: md0` and `launchd`; APFS mount error 79 is not present. Root shell is blocked by repeated AMFI code-signature validation failure and launch-constraint enforcement for `/bin/bash`.

## Continuation

Continue from the launchd/AMFI boundary. Inspect shell signature/CDHash/trust-cache/service evidence, define one narrow discriminator, and make no broad speculative security-policy mutation. Do not restart the obsolete APFS error-79 cycle unless fresh evidence reproduces it.

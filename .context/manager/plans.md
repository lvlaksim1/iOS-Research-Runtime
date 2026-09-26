# Manager plans

## Migration status

Persistent-manager migration and clean-runtime reinstantiation proof are COMPLETE. IOSPM-001 is independently CLOSED. Product development remains under the same `ios-research-runtime-project-manager`.

## Active IOS-M1 engineering cycle

1. Reconcile the post-capsule product history from `1ff060bd...` through live `main` `669f2b989cf2ab5a0958ca517334a485062e8406`. COMPLETE.
2. Confirm the raw-APFS packaging change at `d743b2e...` and its test at `b3befaeb...`. COMPLETE.
3. Verify current Windows gates and E2E. Ramdisk Tool Windows `36125764919` SUCCESS; qemu-sptm Windows Gate `36125764912` SUCCESS; Windows E2E `36127395221` reaches `launchd` but fails root-shell proof. COMPLETE as an evidence gate.
4. Treat APFS mount error 79 as superseded for the current branch unless a future exact-SHA run reproduces it. COMPLETE.
5. NEXT: inspect the current root-shell execution path, trust-cache/CDHash generation and launchd service configuration against exact artifact/log evidence from `36127395221` / artifact `10862632528`, with focus on why AMFI classifies `/bin/bash` as violating launch constraints despite the intended trust-cache path.
6. Form one narrow discriminator for the AMFI failure before changing product code. Prefer read-only or validation-only evidence first.
7. If the discriminator identifies a concrete signing/trust-cache/launch-constraint defect, implement the smallest corresponding change and rerun the minimum exact Windows validation plus E2E needed to prove root-shell behavior.
8. A claimed root-shell milestone should receive independent Auditor verification before closure.

## Development discipline

A new Runtime reinstantiates this same manager. Progress is measured by verified reduction of uncertainty or movement toward root shell, not commit count, scheduler activity, or diagnostic volume.

## Manager-state coherence protection

This manager remains bound to remediated Context Capsule Core `3a942bd269ec7ee164575589e702e5074da30a29`. Every replacement Runtime must pass the sealed-generation integrity marker before consequential continuation.

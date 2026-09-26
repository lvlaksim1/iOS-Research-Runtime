# Next actions

1. Use current exact evidence from `669f2b989cf2ab5a0958ca517334a485062e8406`, E2E `36127395221`, job `108046547984`, and artifact `10862632528`.
2. Inspect the root-shell execution path end-to-end: the injected launchd service, `/bin/bash` binary provenance/signature, generated CDHash/trust-cache content, and how that trust cache is supplied to the boot runtime.
3. Define one concrete AMFI/launch-constraint discriminator before mutating product behavior.
4. Prefer read-only validation first; only concrete evidence may justify the smallest signing/trust-cache/launch-constraint change.
5. Run the minimum exact Windows validation necessary to prove the hypothesis, then E2E for root-shell proof.
6. If root shell is verified, request independent Auditor verification before closing IOS-M1.
7. Do not resume APFS error-79 investigation unless fresh exact-SHA evidence shows the mount failure has returned.
8. Preserve product authority on `main`; manager-state changes do not constitute product progress.

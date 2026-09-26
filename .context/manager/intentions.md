# Manager intentions and commitments

## Completed commitments

### MIG-IOS-001 — persistent-manager migration
- status: completed
- source: direct Owner directive on 2026-09-24
- responsibility: `ios-research-runtime-project-manager`
- completion evidence: stages 1-9 are durably represented; clean-runtime reinstantiation is PASS and product development has resumed.

### IOSPM-001 protected-state adoption
- status: completed and independently closed
- source: direct Owner remediation directive plus final Auditor retest `AUD-2026-09-24-IOSPM-001-RETEST-002`
- responsibility: `ios-research-runtime-project-manager`
- completion evidence: remediated Core bound, coherent sealed generation independently verified, product `main` unchanged during adoption, IOSPM-001 CLOSED / High confidence.

## Active commitments

### IOS-M1 — first Windows boot milestone
- status: accepted/active
- source: project goal plus Owner direction to resume development under the persistent manager
- responsibility: `ios-research-runtime-project-manager`
- commitment: drive the project to verified recovery `launchd` and a verified root shell on Windows.
- reconciled execution boundary: live `main` is `669f2b989cf2ab5a0958ca517334a485062e8406`. The raw-APFS packaging correction (`d743b2e...`) and regression test (`b3befaeb...`) superseded the former APFS error-79 boundary. Exact E2E `36127395221` reaches `launchd` but does not obtain root shell because AMFI rejects `/bin/bash` with code-signature validation and launch-constraint violations.
- current evidence: Ramdisk Tool Windows `36125764919` SUCCESS; qemu-sptm Windows Gate `36125764912` SUCCESS; Windows E2E `36127395221` FAILURE at root-shell proof; artifact `10862632528`, digest `sha256:456d1d12887572fa60570ce717c3bf32c850c46a6eebc9df93049a089601d809`.
- continuation rule: do not return to APFS error-79 diagnostics unless live evidence regresses to an APFS mount failure. Continue from the current launchd/AMFI boundary.
- semantic fence: avoid speculative broad signing/trust-cache/security-policy changes. Select the smallest evidence-backed change that can prove `/bin/bash` execution and the root-shell milestone.

## Superseded operating model

The rotating shift-worker/OTK production model in `ai-agent-lab` is superseded for this project by Owner direction. Historical evidence remains readable, but it does not own or orchestrate active project commitments.

# Current blockers and open risks

## Active product blocker

Current `main` reaches recovery `launchd`, but the root-shell proof fails because AMFI repeatedly rejects `/bin/bash` with code-signature validation failure and `Launch Constraint Violation (enforcing)`.

Exact current evidence:
- product SHA: `669f2b989cf2ab5a0958ca517334a485062e8406`;
- Windows E2E: `36127395221`;
- job: `108046547984`;
- artifact: `10862632528`;
- artifact digest: `sha256:456d1d12887572fa60570ce717c3bf32c850c46a6eebc9df93049a089601d809`.

## Superseded blocker

APFS `mountroot failed, error: 79` was the earlier boundary at `1ff060bd...` and prior revisions. It is not reproduced in the current exact E2E after the raw-APFS packaging correction and must not drive new work unless it reappears in fresh exact-SHA evidence.

## Governance status

IOSPM-001 is CLOSED / Medium severity / High confidence. No governance blocker prevents ordinary IOS-M1 development.

## Current evidence gate

Before changing signing/trust-cache/launch policy semantics, identify a narrow discriminator for why the intended `/bin/bash` execution is rejected by AMFI. Broad speculative security-policy changes are not justified.

# Current state

## Governance topology

- persistent manager: `ios-research-runtime-project-manager`;
- manager-state authority branch: `manager-state`;
- product authority branch: `main`;
- discovery branch: `main`;
- old `ai-agent-lab` shift-worker production is superseded for this project and remains disabled.

## Migration progress

Completed:
- stages 1-2: exact baseline capture and separation of durable technical knowledge from retired orchestration;
- stage 3: project-local Context Capsule v2 installation is being published;
- stage 4: the manager mandate is being established without rotating workers.

Pending:
- stage 5: shared Agent Control Plane registration;
- stage 6: formal retirement/migration marker in the legacy autonomy;
- stage 7: independent technical reconciliation;
- stage 8: engineering plan from verified evidence;
- stage 9: clean-runtime reinstantiation proof;
- later development/resume tests.

## Product baseline

Last product-code baseline before migration documentation:
`3b0f5648f004f58daef526082b3d2a32d132edcf`.

Exact Windows E2E evidence:
- run `35634992757`;
- branch `main`;
- head SHA `3b0f5648f004f58daef526082b3d2a32d132edcf`;
- artifact `ios-darwin-windows-e2e`;
- artifact digest `sha256:49ea4772133376adcf79f2e5604e6a196d4b4d9c8d9fe12814ce6d03a98c1d73`;
- result: FAILURE at Darwin root-shell proof;
- repeated runtime discriminator: APFS `mountroot failed, error: 79` after `BSD root: md0`.

No product code has been changed by migration stages 1-4.

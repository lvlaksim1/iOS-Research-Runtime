# Episode — migration to persistent Project Manager

Date: 2026-09-24

The Owner selected `iOS-Research-Runtime` as the first real viability test of the persistent-agent model.

The previous development system used rotating workers and an external control layer in `lvlaksim1/ai-agent-lab`. It produced useful diagnostics but did not complete the root-shell milestone. Its final preserved state also contained a control-layer write after the corresponding worker had already lost ownership.

The migration keeps verified technical evidence and replaces the rotating-worker model with one repository-local persistent Project Manager.

The product-code baseline entering migration was `3b0f5648f004f58daef526082b3d2a32d132edcf`. Exact E2E run `35634992757` confirmed the current runtime boundary: XNU sees `md0`, APFS root mounting is attempted, and the rebuilt ramdisk is rejected with error 79.

Legacy checkpoint `fde4f271...` contains candidate extentref conclusions. Those conclusions require independent revalidation before admission as durable technical knowledge.

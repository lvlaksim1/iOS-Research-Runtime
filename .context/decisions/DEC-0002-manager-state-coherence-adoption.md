# DEC-0002 — Adopt protected manager-state generations

Date: 2026-09-24
Status: ACCEPTED
Authority: direct Owner remediation directive for IOSPM-001

## Decision

The persistent `ios-research-runtime-project-manager` adopts remediated Context Capsule Core `3a942bd269ec7ee164575589e702e5074da30a29`.

Its durable manager state is sealed with `.context/manager/state-integrity.json`. Replacement runtimes must fail READY/recover if a coupled BDI/current/handoff file does not match the sealed generation.

This adoption changes manager-state continuity protection only. It does not modify product branch `main`, product code, APFS writer semantics, or the active IOS-M1 product objective.

## Verification gate

IOSPM-001 remains pending until independent Auditor verifies the deployed iOS manager snapshot and confirms the marker against the actual Git blobs.

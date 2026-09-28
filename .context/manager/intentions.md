# Manager intentions and commitments

## Active

### IOS-M1 — first Windows boot milestone
- status: active
- responsibility: `ios-research-runtime-project-manager`
- objective: verified recovery `launchd` plus verified root shell on Windows.
- current product: `main@cbba4060db543d4a2b800f7c15b2a700e69f6961`
- immediate technical state: raw-APFS restoration published; narrow Windows gates pass; E2E is blocked before Darwin boot by missing `qemu-sptm-windows-gate` artifact.

### IOS-PP-RM-001 — continuous production execution
- status: active
- responsibility: `ios-research-runtime-project-manager`
- mode: continuous A/B turns under one Manager package, without artificial stops after intermediate stages.
- worker responsibility: one bounded technical turn, verified side effects, durable handoff, then successor arm as the final tool operation.
- stop only for genuine Manager conditions: objective achieved; authority/scope change required; destructive/high-impact action outside mandate; unresolved ambiguous mutation; PP-RM invariant failure that cannot be safely repaired; or a strategic fork that changes milestone/architecture rather than tactics.
- ordinary CI failure, missing artifact, reproducible build/test failure, and evidence-backed tactical fixes remain inside the continuous package.

## OCB operating commitment

- Explicit OSB only.
- Maximum three exact-identical attempts total for the same request when each previous attempt is explicit OSB.
- No automatic fourth attempt.
- After any mutation attempt sequence, reconcile authoritative server state.
- Never blindly duplicate an ambiguous mutation.

## Completed evidence

- PP-RM admission pilot PASS.
- Raw-APFS restoration published at `cbba4060...`.
- OCB3 experiments captured, including one observed `OSB -> OSB -> SUCCESS` sequence.

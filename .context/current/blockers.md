# Current blockers and open risks

## Active blocker — current exact-SHA E2E infrastructure

Product `main@cbba4060db543d4a2b800f7c15b2a700e69f6961` is published and its narrow Windows gates pass.

Windows End-to-End Boot run `36483217835` fails before Darwin execution because expected artifact `qemu-sptm-windows-gate` cannot be downloaded.

Exact failing job/step:
- job `109133700969` (`boot-proof`)
- step `Download QEMU runtime from gate`
- error: `Unable to download artifact(s): Artifact not found for name: qemu-sptm-windows-gate`

Consequence:
- no current-SHA APFS/root-shell evidence exists yet;
- do not attribute this E2E failure to raw-APFS product semantics;
- restore the gate artifact path before interpreting boot behavior.

## OCB operational risk

Observed `update-ref` passability is non-deterministic across runtime context:
- full production turn: OSB, OSB;
- minimal targeted publication probe: SUCCESS on first attempt;
- repeated minimal probe: OSB, OSB, SUCCESS on third attempt.

A third exact-identical request is now empirically justified as potentially useful, but evidence remains too small to declare a universal permanent retry count.

Safety controls remain:
- exact-identical replay only for explicit OSB when policy permits;
- no blind replay of ambiguous mutations;
- authoritative server-state reconciliation after mutation attempts.

## PP-RM continuity risk

All five PP-RM objects are disabled, but Mailbox state is stale because the minimal probes intentionally bypassed normal baton progression.

Before any further A/B execution, Manager must reseed and verify Mailbox/Pulse/Trace from current sealed Manager state.

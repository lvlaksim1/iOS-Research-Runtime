# Procedural memory

- Reconcile exact live `main` before product mutation.
- PP-RM handoff remains validate -> ACK -> bounded work -> finish side effects -> Pulse -> Mailbox -> bounded read-back stabilization -> Trace SEND -> successor arm last.
- Register read-back stabilization uses up to three fresh read-only Scheduled Task reads and never replays the register mutation merely for visibility.
- GitHub telemetry uses unique Trace events per request/attempt; Manager derives authoritative counts from those events, not worker aggregate prose.
- Explicit OSB on a GitHub request is handled as OCB. Timeout/API/network/tool-unavailable/unknown failures are not automatically OCB.
- The baseline OCB policy remains provisional. One exact-identical retry after explicit OSB was the initial working rule.
- Owner-authorized OCB3 experiment showed that a third exact-identical request can succeed after two explicit OSBs in one observed minimal runtime. This is evidence that a third attempt may be useful, not a universal permanent rule.
- For any exact-identical retry, preserve operation and parameters exactly. Do not insert unrelated GitHub operations between attempts when measuring retry-count effects.
- Never blindly replay an ambiguous mutation. Reconcile authoritative server state first; if ambiguity remains, stop at Manager checkpoint.
- When comparing OCB passability, distinguish full runtime context from minimal targeted probes. The same `update-ref` showed OSB/OSB in a full production turn, SUCCESS on first attempt in one minimal probe, and OSB/OSB/SUCCESS in another minimal probe.
- Current PP-RM registers are stale relative to Manager truth after the minimal targeted probes. Before any future worker arm, Manager must reseed Mailbox/Pulse/Trace and verify disabled state.
- If a current-SHA CI failure occurs before the product-under-test executes, classify it as infrastructure until exact evidence proves otherwise. Do not mutate APFS/iOS semantics merely to bypass missing infrastructure.
- For current `main@cbba4060...`, restore the expected `qemu-sptm-windows-gate` path, rerun exact-SHA E2E, then classify boot behavior.
- A/B ordinary execution never mutates `manager-state`; Manager persists durable semantic state at checkpoints.

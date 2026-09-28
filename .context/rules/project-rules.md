# Project rules

1. `main` is product authority. `manager-state` is durable Project Manager authority. Neither branch silently substitutes for the other.
2. The retired `ai-agent-lab` shift-worker/OTK factory is not an execution authority and must not be re-enabled.
3. PP-RM is the approved continuous execution Runtime: A/B are disposable bounded execution carriers of `ios-research-runtime-project-manager`, not new managers or commitment owners.
4. Manager owns development direction, priorities, strategy, work packages, and high-level checkpoints. A/B may make only tactical decisions inside the active work package.
5. A/B ordinary execution must not mutate `manager-state`; Manager persists durable semantic state at high-level checkpoints.
6. Direct Owner ↔ Project Manager work remains first-class. Supervisor is not a mandatory intermediary for ordinary project development.
7. The immediate milestone remains Windows provisioning and Darwin recovery boot through `launchd` to a verified root shell.
8. APFS semantic changes require discriminating evidence tied to an immutable product revision; speculative metadata changes are forbidden.
9. Product progress claims require exact repository/CI/runtime evidence. Manager-state prose, historical verdicts, or A/B reports are not sufficient proof.
10. PP-RM normal path requires fresh validation, inbound ACK, bounded turn, completion of side effects before handoff, exact Mailbox read-back, Trace SEND, and successor arm as the final tool operation.
11. After successor arm, predecessor performs no further tool operations.
12. OCB is routine system behavior plus its handling model. Retry missing expected server responses safely; use read-back/idempotency before repeating mutations.
13. OCB alone never changes project authority, baton ownership, or Manager commitment ownership.
14. At a high-level checkpoint, unexpected regression, ambiguous side effect, or PP-RM invariant failure, A/B must stop strategic continuation and return evidence to Manager.
15. Existing GitHub product verification workflows remain test infrastructure, not PP-RM control-plane state.

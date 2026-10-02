# Project rules

1. `main` is product authority. `manager-state` is durable Project Manager authority. Neither silently substitutes for the other.
2. The retired `ai-agent-lab` shift-worker/OTK factory is not an execution authority and must not be re-enabled.
3. PP-RM is the approved execution Runtime: A/B are disposable bounded carriers of `ios-research-runtime-project-manager`, not new managers or commitment owners.
4. Manager owns direction, priorities, decomposition, acceptance criteria, strategy, packages and high-level checkpoints. A/B may make only tactical decisions inside the active package.
5. A/B ordinary execution must not mutate `manager-state`; Manager persists durable semantic state promptly when a verified finding becomes reusable/actionable. High-level checkpoints are mandatory consolidation points, not the only persistence points.
6. Direct Owner <-> Project Manager work remains first-class. Supervisor is not a mandatory intermediary.
7. The immediate milestone remains Windows recovery through `launchd` to a verified root shell.
8. APFS semantic changes require discriminating immutable-revision evidence; speculative metadata changes are forbidden.
9. Product progress claims require exact repository/CI/runtime evidence.
10. PP-RM normal path requires fresh validation, ACK, bounded turn, completed side effects, Pulse, outbound Mailbox, exact read-back, Trace SEND and successor arm as the final tool operation.
11. After successor arm, predecessor performs zero further tool operations.
12. Before production admission PP-RM must pass A1 -> B2 -> A3 -> FINAL pilot and Manager must review the evidence.
13. OCB handles explicit OSB on GitHub requests. One exact identical retry is desired as the initial policy, not mandatory.
14. Non-OSB errors are not automatically OCB; ambiguous mutations must not be blindly duplicated.
15. OCB alone never changes project authority, baton ownership or Manager commitment ownership.
16. Pilot and production GitHub requests should record enough OCB telemetry to measure and reduce OCB impact on Scheduler <-> GitHub throughput.
17. At a high-level checkpoint, unexpected regression, ambiguous side effect or PP-RM invariant failure, A/B stops strategic continuation and returns evidence to Manager.
18. Existing GitHub verification workflows remain test infrastructure, not PP-RM control-plane state.
19. After Verify/Reflect, the Manager MUST run a Durable Finding Gate before allowing the finding to remain only in chat, PP-RM Mailbox/Trace, runtime checkpoint, or other volatile state.
20. A verified finding MUST be admitted to durable manager state before a runtime/generation boundary when it can materially change a future Manager's action or prevent repetition of an already-solved problem. Automatic durable candidates include: a verified reusable workaround or alternate execution path; a new invariant/constraint; a corrected failure classification; a new interpretation of evidence that changes the next action; or a repeated incident whose resolution is expected to recur.
21. Route admitted findings by meaning: architecture/policy choice -> `.context/decisions/`; reusable method/workaround -> procedural memory; durable project fact -> beliefs/semantic memory; changed execution strategy -> plans/current views; historically significant one-off context -> episodic memory. One finding may update more than one surface when semantics require it.
22. Runtime logs, Mailbox, Trace and chat history are evidence, not substitutes for durable managerial memory. If a future runtime would reasonably benefit from the finding, leaving it only in runtime evidence is a persistence defect.
23. Do not persist every observation. Mere confirmation, transient telemetry, raw logs, secrets, hidden reasoning, and details that would not alter a future decision remain non-durable unless another rule requires them.

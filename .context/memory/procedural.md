# Procedural memory

- Before product work, reconcile exact live `main` and distinguish current product state from historical evidence.
- PP-RM A/B executes one bounded turn per runtime and uses Mailbox/Pulse/Trace for transport and evidence.
- Handoff order: validate -> ACK -> bounded work -> finish side effects -> Pulse -> outbound Mailbox -> bounded read-back stabilization -> Trace SEND -> successor arm as LAST TOOL OPERATION -> zero post-arm tool calls.
- Register read-back stabilization: after one register mutation, use up to three fresh read-only Scheduled Tasks reads to observe the exact intended state. Never repeat the mutation solely because the first read is stale.
- Repeated message_id must never repeat product side effects; deduplicate before work.
- Scheduler delay alone is not protocol failure and never authorizes timeout takeover.
- GitHub telemetry uses one uniquely tagged Trace event per request/attempt. Authoritative totals are calculated from those events by Manager; worker aggregate summaries are advisory only.
- OCB: explicit OSB on a GitHub request may receive one desired exact-identical retry; retry is not mandatory; no automatic third identical request.
- Non-OSB timeout/API/network/tool failures are not automatically OCB.
- Never blindly repeat an ambiguous GitHub mutation; reconcile server state first when possible.
- Pilot admission evidence: attempt 2 A1 -> B2 -> A3 -> FINAL PASS; 4/4 GitHub READ first-attempt success; zero explicit OSB. OCB retry effectiveness remains untested.
- At a high-level checkpoint, A/B stops successor chaining and returns exact repository/CI/runtime evidence to Manager.
- A/B ordinary execution never mutates `manager-state`; Manager persists durable meaning.

# Manager intentions and commitments

## Completed

### MIG-IOS-001
- status: completed
- responsibility: `ios-research-runtime-project-manager`

### IOSPM-001 protected-state adoption
- status: completed and independently closed

### IOS-PP-RM-PILOT-001
- status: completed / PASS on attempt 2
- result: A1 -> B2 -> A3 -> FINAL completed with exact SEND/ACK handoffs and all workers/registers in safe terminal state.
- corrective finding: single immediate read-back can false-fail; bounded read-only stabilization is now required.
- telemetry finding: Worker aggregate undercounted GitHub operations; Manager must derive authoritative counts from Trace events.
- GitHub passability: attempt 2 = 4/4 first-attempt READ success; both attempts combined = 6/6; explicit OSB = 0.
- OCB conclusion: insufficient OSB evidence to optimize retry policy; keep provisional.

## Active

### IOS-M1 — first Windows boot milestone
- status: active
- responsibility: `ios-research-runtime-project-manager`
- goal: verified recovery `launchd` plus verified root shell on Windows.

### IOS-PP-RM-001 — PP-RM production execution
- status: admitted/active
- responsibility: `ios-research-runtime-project-manager`
- production package: `IOS-M1-R1`
- admission basis: pilot PASS plus Manager review in generation 7.
- execution boundary: A/B execute bounded tactical work only; Manager retains direction, priorities, acceptance criteria, strategy and high-level checkpoints.
- completion condition for current package: return a high-level evidence checkpoint at launchd/AMFI, persistent APFS error 79, unexpected regression, ambiguous side effect, protocol failure, or package objective completion.

## Superseded

The retired `ai-agent-lab` rotating shift-worker/OTK factory remains superseded and must not be re-enabled.

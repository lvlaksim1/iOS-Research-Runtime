# Current state

Updated: 2026-09-30 04:05 MSK

## Governance
- manager: `ios-research-runtime-project-manager`
- manager generation: 16
- product authority: `main`
- PP-RM version: generation 16 native two-phase mutation execution
- execution status: OWNER-AUTHORIZED / LAUNCH IN PROGRESS
- active package to configure and launch: `IOS-M1-CONTINUOUS-005`

## Product
- live main: `95e871e84099f10245e912659b2d964c1b3c1037`
- Windows Build on this SHA: SUCCESS
- Windows End-to-End Boot `36640653275`: FAILURE at provisioning / Darwin root-shell proof
- failure evidence was collected successfully
- primary blocker remains AMFI / CT / recovery executable provenance and trust membership
- next bounded product unit: post-merge `/bin/bash` Mach-O/size/primary-CDHash/injected-trust-membership diagnostic immediately after `mergeSysrootTarWithSigner`, plus a pure formatting test, followed by exact-SHA CI
- no ambiguous product mutation is currently in flight

## Package 004 terminal evidence
`IOS-M1-CONTINUOUS-004` reached durable `FAIL_STOP` at generation 46 after activation_attempt=3 stalled at `EVIDENCE_READ`.
The root runtime defect was not loss of Watchdog continuity: workers could not satisfy the generation-15 mandatory second Scheduled Tasks read immediately before GitHub mutation.
No product mutation occurred in the terminal activation; token was revoked.

## PP-RM generation 16
Generation 16 removes the second Scheduled Tasks read from the normal mutation path.

Native two-phase mutation protocol:
1. PREPARE runtime performs one initial Scheduled Tasks read, validates baton, ACKs, researches, and may create immutable Git objects only.
2. PREPARE runtime MUST NOT mutate a mutable Git ref.
3. When a target commit is ready it publishes an immutable mutation descriptor to Mailbox and hands off to a fresh runtime in `MUTATION_READY`.
4. The fresh MUTATION executor's FIRST Scheduled Tasks read is the ownership fence.
5. The executor may publish only the exact frozen `mutation_target_commit` against exact `mutation_baseline_main_sha` with `force=false`.
6. No second Scheduled Tasks read is required before `update_ref`.
7. All recovery runtimes for the same mutation preserve exactly the same mutation_id, baseline and target.
8. Before replay/recovery, authoritative GitHub main is reconciled:
   - main == target => side effect already succeeded;
   - main == baseline => same frozen mutation may be attempted;
   - otherwise => FAIL_STOP.
9. Watchdog remains immutable, FIRST operation self-rearm same task +5 minutes.
10. dispatch_retry/runtime-failure separation and OCB3 remain unchanged.

Owner explicitly approved this generation-16 mechanism and authorized launch.

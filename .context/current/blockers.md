# Current blockers and open risks

## Active product boundary

Current product code is back on the `3b0f564...` line (live `main@85d408075ab8a66f6d16043029eb2255956eb1b9` adds discovery metadata only).

The conservative current boot boundary is APFS `mountroot failed, error: 79`, supported by exact Windows E2E `35634992757` at the code-equivalent baseline.

This is not an unknown starting point: historical verified evidence shows that the raw-APFS packaging correction `d743b2e...` plus regression test `b3befaeb...` previously moved the project past APFS mounting to recovery `launchd`.

## PP-RM launch blockers

No Manager-governance blocker remains.

The only pre-launch requirement is external runtime instantiation of the native PP-RM Scheduled Tasks/registers. Manager-side contract, initial work package, stop conditions, and OCB handling policy are prepared in generation 4.

## Safety / strategy gates

- Do not restore the whole later history blindly; recover only the evidence-backed product/test semantics first.
- A/B must stop for Manager at a high-level checkpoint rather than choosing a new strategic direction.
- A/B ordinary execution must not mutate `manager-state`.
- Product releases remain Owner-gated.
- OCB is routine unless it creates ambiguous side effects or prevents re-establishing protocol invariants.

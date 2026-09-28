# Next actions

1. Seal Manager generation 8 with the temporary third-request experiment.
2. Reconfigure Worker A for targeted IOS-M1-R1-OCB3 continuation; keep B disabled initially.
3. Seed Mailbox/Trace/Pulse with prepared commit `cbba4060...` and current `main=85d4080...`.
4. Verify register state.
5. Arm Worker A only.
6. A reconciles `main`, then attempts exact update-ref.
7. On explicit OSB: exact-identical retry #2; on second explicit OSB: exact-identical retry #3.
8. No fourth request.
9. Fresh-reconcile `main`.
10. If published, continue at WAIT_CI; if unchanged or ambiguous, stop at Manager checkpoint.
11. Manager evaluates whether third-attempt behavior changes the OCB model.

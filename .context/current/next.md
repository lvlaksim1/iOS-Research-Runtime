# Next actions

1. Seal Manager generation 10 for continuous PP-RM production.
2. Verify slot budget and all five PP-RM objects disabled.
3. Replace Worker A/B prompts with continuous production protocol and unchanged OCB parameters.
4. Reseed Mailbox/Pulse/Trace for `IOS-M1-CONTINUOUS-001`.
5. Verify exact register contents and disabled state.
6. Arm Worker A only.
7. Worker A begins from current E2E blocker: missing `qemu-sptm-windows-gate`.
8. A/B continue automatically through bounded turns, CI waits, fixes, commits, and reruns.
9. Do not stop at ordinary technical failures. Stop only on the genuine conditions defined in Manager state.
10. On final objective completion, publish FINAL_COMPLETED and do not arm successor.

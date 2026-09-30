# Next actions

Updated: 2026-09-30 23:39 MSK

1. Publish Manager generation18 capsule and DEC-0016 atomically to `manager-state`.
2. Configure existing five PP-RM tasks for package `IOS-M1-CONTINUOUS-007` while A/B/Watchdog are disabled.
3. Keep Worker A/B and Watchdog prompts immutable after package configuration.
4. Seed Mailbox/Trace from authoritative `main@4821fb9a9cd72dd40af2a518962f180fb4344fe7`.
5. Arm Watchdog with generation17 recurring-backstop semantics.
6. Final launch operation: arm initial Worker B about +30 seconds.
7. Initial Worker first reconciles existing exact-main `rcodesign Windows Gate` run `36771957949` and extracts strict primary-SHA256 evidence from available logs/artifacts.
8. For every future workflow gate, search existing exact-SHA runs before attempting dispatch; trigger event is not part of the acceptance condition unless the product test itself requires a specific trigger.
9. Only if no usable run exists may dispatch/rerun/start capability be considered; OWNER_GATE for missing dispatch is last resort.
10. Preserve generation16 frozen-target MUTATION_READY publication, generation17 recurring Watchdog, OCB3, dispatch_retry/activation_attempt separation and same-generation recovery.
11. Never resume package006 or package005.

# Next actions

1. Seal Manager generation 14.
2. Reconfigure Worker A/B as immutable slot programs with activation read only from Mailbox.
3. Reconfigure Mailbox schema for activation_attempt, dispatch_retry and dispatch_baseline_last_run_time.
4. Reconfigure Watchdog to distinguish scheduler DISPATCH_FAILURE from confirmed RUNTIME_FAILURE.
5. Enable same-generation A/B failover after repeated dispatch non-delivery.
6. Start package `IOS-M1-CONTINUOUS-003` from current `main@649a2244f876db34e2032755b189df158667305f`.
7. First production unit: repair the ramdisk regression-test nil dereference narrowly, then continue AMFI / launch-constraint work.
8. Continue exact-SHA CI and bounded handoffs without artificial stops.

# Manager beliefs

Updated: 2026-10-27 MSK. Manager generation: 28.

## Identity and authority
- Stable manager: `ios-research-runtime-project-manager`. Durable manager authority: `manager-state`. Product authority: `main`. Source: identity.json / manifest / Owner mandate; authority: Owner and repository contract.
- LARGE STAGE 1 — Full iOS System Boot is ACTIVE / NOT_PROVEN. IOS-M1 recovery launchd/root shell and IOS-M2 storage-boundary work were historically completed. Source: Owner roadmap and historical E2E; authority: Owner and past exact-SHA evidence.

## Product reconciliation, current as of 2026-10-27
- Live `main@0b633cbafd2a0198a9053c6f760d9590c2496e14` is 10 commits ahead of the prior capsule baseline `89cf1e04571545010c2433f24264bae25f5c5f2d`. Source: GitHub refs and compare; authority: verified repository.
- The latest main commit reports consolidation of 61 archived changes and 515 offline tests; these are commit-message claims, not independent guest-boot verification. Source: commit metadata; authority: verified publication, unverified test claim.
- Exact-head Windows Build `39016012852` failed at Build step. Windows End-to-End Boot `39016012955` failed at provisioning/root-shell proof step. qemu-sptm Windows Gate `39016012886` passed. Storage Policy run `40478805063` passed, but is not a boot test. Source: GitHub Actions jobs/runs 2026-10-27; authority: verified CI.
- Historical exact-SHA recovery observations identify IONVMeFamily, APFS, AppleEmbeddedPCIE, AppleT8140PCIe, native DeviceTree `apcie` and no non-ramdisk `/dev/disk*`. These historical observations do not prove guest PCIe/NVMe, APFS system volumes or system launchd on current main. Source: historical E2E `37063868899` and present failed E2E; authority: historical/current CI.
- Full-system iOS has NOT been proven. No independently accepted exact-head guest disk + SystemOS/Preboot/Data + system launchd evidence exists. Source: Stage1 acceptance and current CI; authority: acceptance contract.

## PP-RM and outstanding work
- Existing `IOS-M3-CONTINUOUS-011` tasks are frozen to manager generation 27 and `f26dd70e1b6687ffed72703ff809af5e16a0558d`. Advancing capsule to generation 28 does not change their immutable execution anchor. Source: scheduler task prompts; authority: live task configuration.
- Disabled Mailbox canonical header reports GEN195, owner B, READY, ACK NONE, progress_seq0; Mailbox includes 64 mixed published/pending Library archive records, not 64 uniformly unpublished items. G194 tests 5/5 were reported and its archive was recorded Library-saved, still PENDING_GITHUB. Source: scheduler Mailbox/Trace prompts; authority: inspected runtime record (archive bytes not independently rechecked in this manager turn).
- Last scheduler read showed A and B disabled and Watchdog enabled. Last Worker B result reports a scheduler service error before verified ACK. Successful GEN195 ownership/dispatch is unconfirmed; Watchdog prior audit was inconclusive. Source: task metadata and Worker B last run 2026-10-27; authority: scheduler readback + execution result.
- G30/G71 GitHub publication attempts remain PENDING_OCB after explicit safety refusals and must not be retried or circumvented through alternative tools. Source: Mailbox/Trace; authority: inspected control-plane record and safety rule.
- Separate iOS Expert research automation is outside this PP-RM product package. Source: task metadata; authority: inspected configuration.

# Semantic memory

Updated: 2026-10-27 MSK. Superseding earlier statements of the *current* product; historical lessons retained.

## Current project facts, with provenance
- GitHub product `main@0b633cbafd2a0198a9053c6f760d9590c2496e14` is current as of 2026-10-27, ten commits beyond earlier capsule `89cf1e04571545010c2433f24264bae25f5c5f2d`. source: GitHub refs+comparison; authority: verified-repository.
- Exact current-head Windows Build `39016012852` FAIL at Build step; E2E `39016012955` FAIL at provisioning/root-shell proof; QEMU Gate `39016012886` PASS. Specific causes not determined. source: Actions runs and jobs 2026-10-27; authority: verified CI.
- Latest main commit text describes 61 archived changes and 515 offline tests; published source is real, but claims about offline tests are not independently replayed and do not prove guest storage or full iOS. source: GitHub commit metadata; authority: published source/limited metadata claim.
- PP-RM `IOS-M3-CONTINUOUS-011` immutable task package is manager-generation27 anchored at `f26dd70e1b6687ffed72703ff809af5e16a0558d` while capsule advances to generation28. source: task prompts and repository; authority: live configuration.
- Mailbox canonical header GEN195 B READY ACK NONE/seq0 and 64 mixed-status Library archive records; G194 5/5 synthetic negative tests reported Library-saved, PENDING_GITHUB. Scheduler A/B disabled, Watchdog enabled, B's reported task-service error: active execution unconfirmed. source: Mailbox/Trace and task readback 2026-10-27; authority: inspected runtime metadata, not all archived bytes reverified.
- G30/G71 explicit safety-refused GitHub publications stay PENDING_OCB; never retry or evade. source: canonical Mailbox+Trace; authority: inspected runtime record / safety policy.
- Recovery shell and BootKC/DeviceTree PCIe/NVMe data are historical exact-SHA observations. No accepted guest disk + APFS SystemOS/Preboot/Data + system launchd proof on current head. source: historical E2E and current-head CI; authority: historical/current verification.

## Superseded historical product-current statements
- Earlier `main@cbba4060db543d4a2b800f7c15b2a700e69f6961` was then current with an APFS packaging correction; this is no longer current.
- Earlier Windows run `36483217835` failed due to missing QEMU gate artifact; historical, not current-head diagnosis.
- Earlier APFS error79 and later recovery-root-shell results remain historical evidence, not current-full-system acceptance.

## Retained durable execution/procedure facts
- PP-RM remains subordinate to persistent Project Manager `ios-research-runtime-project-manager`. A/B are replaceable execution runtimes and never become the project commitment owner. source: Owner directive; authority: owner-directive.
- PP-RM control plane is native Scheduled Tasks: Worker A/B plus disabled Mailbox/Pulse/Trace. GitHub is product/evidence infrastructure, not baton ownership state. source: Owner-provided PP-RM mechanism and verified deployment; authority: owner-provided-evidence plus verified-runtime.
- Register read-after-write visibility can lag. Correct handling is bounded fresh read-only stabilization, not replaying the register mutation merely because one immediate read mismatches. source: PP-RM pilot attempt 1/2; authority: verified-runtime plus manager-analysis.
- OCB means the working model around explicit OSB on GitHub tool requests and its routine handling. Non-OSB timeout/API/network/tool failures are not automatically OCB. source: Owner correction 2026-09-28; authority: owner-directive.
- The first production branch-publication turn observed `update-ref` = explicit OSB, explicit OSB, then safe reconciliation showing no publication. source: PP-RM production Trace plus live GitHub; authority: verified-runtime plus verified-repository.
- A minimal targeted probe of the same prepared publication later succeeded on its first `update-ref` and published `cbba4060...`. A second minimal probe with unchanged request parameters, while main already equaled target, observed explicit OSB, explicit OSB, then SUCCESS on a third exact-identical request. source: live Scheduled Tasks Trace and live GitHub; authority: verified-runtime plus verified-repository.
- The OCB3 evidence establishes only that a third exact-identical attempt can pass after two explicit OSBs in at least one observed runtime. It does not establish a universal optimal retry count; runtime context/request sequence likely influences passability and further evidence is required. source: Manager analysis of verified runtime evidence; authority: manager-analysis.
- Ambiguous GitHub mutations must never be blindly replayed. After any uncertain write outcome, authoritative server-state reconciliation takes precedence over tool-return narrative. source: PP-RM safety model and production experiment; authority: owner-directive plus verified-runtime.
- HISTORICAL / SUPERSEDED: earlier Mailbox stale after minimal probes; package011 GEN195 later superseded that condition. Re-read current canonical ownership, do not reseed blindly. source: earlier runtime and 2026-10-27 scheduler; authority: historical verified runtime.
- Manager continuity and product truth remain separate: durable Manager state lives on `manager-state`; product/CI claims are reconciled against `main` and exact runtime evidence. source: Context Capsule split-authority contract; authority: core-contract plus owner-directive.

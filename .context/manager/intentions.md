# Manager intentions and commitments

Manager generation: 24.

## Completed foundation
- IOS-M1: COMPLETED — recovery launchd + root shell.
- IOS-M2: COMPLETED — exact-SHA E2E `36870111560` / job `110395408194` SUCCESS isolated the missing full-system storage boundary.

## Active macro stage
### LARGE STAGE 1 — Full iOS System Boot
Status: ACTIVE / WAIT_EXTERNAL_EVIDENCE.
Active runtime package: `IOS-M3-CONTINUOUS-010`.
Current product: `main@32dd17014113543862e756c7daa52822e2eec073`.
Current evidence run: `36915159246`.

Current bounded objective:
verify whether moving the bounded PCIe discovery node under `arm-io` causes XNU to bind/discover the emulated NVMe path and produce guest disk nodes.

When guest-visible storage is proven, continue automatically through SystemOS/Preboot/Data staging, APFS discovery/mounting, system launchd and core full-system userland.

## Runtime continuity commitment
DEC-0018 / schema10 applies:
- OCB3 exhausts one disposable Worker runtime only;
- first recovery rotates to a fresh partner runtime;
- repeated transient OCB enters nonterminal Watchdog-owned OCB_BACKOFF and later safe replan;
- successful progress resets OCB recovery state;
- only genuine strategy/authority/safety boundaries may require Owner intervention.

## Constraints
Do not stage large SystemOS assets until guest-visible storage transport is evidenced.
Do not infer AppleSEPManager as causal without evidence.
Packages005–009 must not resume.

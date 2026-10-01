# Owner-facing roadmap

Updated: 2026-10-01 17:47 MSK

## Planning granularity

The Owner-facing roadmap uses large stages. IOS-M1, IOS-M2, IOS-M3 and future IOS-M* labels remain internal engineering checkpoints only.

Completing an internal checkpoint does NOT require Owner participation and does NOT stop PP-RM. The Project Manager may autonomously create, execute, verify and supersede as many bounded IOS-M* work units and PP-RM packages as needed inside the currently authorized large stage.

Owner involvement is required only when:
- a large stage reaches its acceptance criteria;
- a true strategic fork would materially change product direction or architecture;
- new authority/scope/resources are required;
- safety/governance requires an Owner decision.

Ordinary failures, CI retries, diagnostic forks, transport selection, implementation changes, exact-SHA verification, PP-RM failover and internal milestone completion are Manager responsibilities and must not create routine Owner gates.

## LARGE STAGE 1 — Full iOS System Boot

Status: ACTIVE.

Goal:
Advance from the already verified Windows recovery/root-shell environment to a reproducible full iOS system boot boundary with full-system storage, APFS volume discovery/mounting, system launchd and the core service graph required for normal userland.

Includes, without separate Owner gates:
- current IOS-M3 storage transport work;
- host-backed block-device proof;
- SystemOS/Preboot/Data material extraction and staging;
- APFS container and volume-group discovery;
- required DeviceTree/QEMU storage implementation;
- boot arguments and mount topology;
- trust/security/SEP work only where evidence makes it causal;
- transition from recovery launchd to system launchd;
- core daemon bring-up sufficient to establish full system userland;
- all diagnostics, regressions and exact-SHA E2E loops needed to reach the acceptance boundary.

Acceptance:
Exact reproducible Windows evidence demonstrates that the runtime has crossed from recovery-only execution into the real full-iOS system userland with full-system volumes and system service bootstrap, or establishes a hard external feasibility boundary that cannot be crossed within the authorized architecture.

Owner report:
One consolidated report at completion or at a genuine strategic/feasibility fork.

## LARGE STAGE 2 — Interactive iOS Environment

Status: PLANNED.

Goal:
Turn the full-system boot into an actually interactive iOS environment.

Includes:
- framebuffer/display path;
- graphics transport required by the guest;
- keyboard/mouse/touch input translation;
- WindowServer/backboard/frontboard dependencies as applicable;
- SpringBoard bring-up;
- stable interactive session;
- restart/recovery behavior for the UI stack.

Acceptance:
A reproducible Windows run reaches an interactive SpringBoard-based iOS session with working display and usable input.

## LARGE STAGE 3 — Apple Ecosystem Feasibility

Status: PLANNED.

Goal:
Determine, through runtime evidence, which Apple ecosystem functions can work in this environment and implement those that are technically and operationally feasible.

Includes:
- activation path;
- network/device identity dependencies;
- Apple Account sign-in feasibility;
- Family Sharing visibility;
- Screen Time / parental-control workflows;
- push/keychain/device-attestation dependencies where relevant;
- clear separation between implemented functionality, blocked functionality and functionality requiring real Apple hardware or unsupported server-side trust.

Acceptance:
Produce a verified capability matrix and working implementations for the feasible functions needed by the product. Do not claim unsupported Apple-service functionality without end-to-end evidence.

## LARGE STAGE 4 — Windows Product + Release

Status: PLANNED.

Goal:
Convert the research runtime into a repeatable Windows product suitable for ordinary use.

Includes:
- GUI-only lifecycle;
- automatic provisioning;
- firmware/tool acquisition;
- persistent runtime data;
- configuration and diagnostics;
- clean start/stop/recovery;
- packaging and updates;
- reproducibility across clean Windows machines;
- failure handling;
- endurance/reliability;
- final documentation and release packaging.

Acceptance:
A clean Windows installation can provision, launch and use the supported iOS environment through the application without developer tooling or manual command-line intervention, with documented limitations and reproducible release evidence.

## Current mapping

Completed internal checkpoints:
- IOS-M1 — recovery launchd + root shell;
- IOS-M2 — isolated missing full-system storage boundary.

Current internal work:
- IOS-M3 and package IOS-M3-CONTINUOUS-010 are implementation work inside LARGE STAGE 1.
- Current product head is in the NVMe host-backed transport experiment sequence.

Future IOS-M* labels are allowed for engineering bookkeeping, but they are subordinate to the four large stages above and are not Owner-facing approval gates.

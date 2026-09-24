# Persistent-agent migration baseline

Date: 2026-09-24

Purpose: durable target-owned baseline for migration of `lvlaksim1/iOS-Research-Runtime` from the retired shift-worker autonomy in `lvlaksim1/ai-agent-lab` to a project-local persistent Project Manager.

This document is migration evidence. It does not authorize technical product changes by itself.

## 1. Canonical target state

Repository: `lvlaksim1/iOS-Research-Runtime`

Authoritative product branch: `main`

Baseline product commit:
`3b0f5648f004f58daef526082b3d2a32d132edcf`

Additional branch:
- `apfs-multilevel` is behind `main` and contains no commits ahead of `main`; it is not an alternate active development line.

At migration baseline capture:
- open issues: none;
- open pull requests: none;
- technical development is intentionally paused for the agent-model migration.

## 2. Product goal and first milestone

The repository goal is a Windows-native GUI runtime for provisioning, booting and investigating modern iOS/Darwin environments with QEMU without requiring the user to install macOS/Xcode or development command-line toolchains.

The first milestone remains intentionally narrow:
1. native Windows application;
2. prepare the firmware/runtime bundle;
3. launch and stop `qemu-sptm`;
4. capture serial boot logs;
5. boot modern iOS/Darwin recovery to `launchd` and a root shell;
6. keep user-facing operation GUI-only.

SpringBoard, graphical interaction, Apple Account, Family Sharing and Screen Time are later work and are not part of the current blocker.

## 3. Independently verified current blocker

The exact Windows end-to-end run `35634992757` is bound by GitHub artifact metadata to:
- branch: `main`;
- head SHA: `3b0f5648f004f58daef526082b3d2a32d132edcf`;
- evidence artifact: `ios-darwin-windows-e2e`;
- artifact digest: `sha256:49ea4772133376adcf79f2e5604e6a196d4b4d9c8d9fe12814ce6d03a98c1d73`.

The run successfully completed environment setup, QEMU staging, ramdisk-helper build and integration-harness setup. It failed only at the Darwin root-shell proof.

The serial evidence repeatedly shows:
- `BSD root: md0`;
- APFS `mountroot` is invoked;
- APFS reports `unable to root ... (root_device): 79`;
- `apfs: mountroot failed, error: 79`.

Therefore the migration baseline blocker is not “QEMU does not run”; it is the failure of the rebuilt APFS recovery ramdisk at root mounting.

## 4. Build/test infrastructure to preserve

The repository already contains useful product verification infrastructure:
- `.github/workflows/qemu-sptm-windows.yml` — builds/stages a pinned Windows `qemu-sptm` runtime and verifies the Darwin machine;
- `.github/workflows/windows-e2e.yml` — prepares the current product, runs provisioning and attempts a Darwin root-shell proof on Windows;
- `.github/workflows/apfs-evidence-marker.yml` — exposes focused APFS failure evidence.

These workflows are product test infrastructure. They are not the future agent orchestrator.

## 5. Retired autonomy provenance

The previous autonomy lived outside this repository in `lvlaksim1/ai-agent-lab`.

Owner conservation record:
`lvlaksim1/ai-agent-lab@61d98b2c21f7cb7bd188725c17e89c1ff241ea3f`.

At conservation:
- production was already idle;
- no live worker was interrupted;
- management had `stop_production=true`;
- the iOS object was PAUSED;
- the five old shop-clock Scheduled Tasks were disabled;
- the separate `iOS Runtime CI Watch` Scheduled Task is also disabled;
- the preserved legacy event was `ios-runtime-release-20260918-032`.

The old system used rotating shift workers, OTK/review machinery, heartbeat/lease/fencing, recovery guards, ratings/reporting and dedicated schedule slots. None of those mechanisms is transferred as live authority into the new project-manager model.

## 6. Legacy control-plane defect

The old orchestration had a confirmed post-fence zombie-write defect:
- recovery/fence anchor: `d8681f004c84d1536c5c1cc65a557aa0a45c9c73`;
- a fenced shift later wrote checkpoint commit `fde4f271641096f20249686f0bd730c2d1a7241f`.

This defect belongs to the retired `ai-agent-lab` orchestration and did not mutate the `iOS-Research-Runtime` repository.

The migration does not resume or repair that old factory. The defect is retained only as historical evidence explaining why its post-fence state cannot be treated as authoritative.

## 7. Knowledge admitted vs knowledge requiring revalidation

### Admitted now from live target evidence

- Windows `qemu-sptm`/Darwin infrastructure exists and the E2E path reaches XNU/APFS root mounting.
- The current exact target commit still fails at APFS mountroot with error 79.
- The project already has GUI/provisioning/runtime/E2E code; this is not a greenfield scaffold.

### Candidate knowledge from the fenced shift-154 checkpoint

The old checkpoint claims:
- source extentref conservation is internally consistent;
- rebuilt extentref conservation is internally explainable by writer-owned metadata;
- raw extentref record-count divergence alone does not justify an APFS semantic mutation;
- the next higher-value discriminator should move toward fuller APSB/root-tree semantic comparison and root file-extent semantics.

Because the checkpoint was published by a fenced worker, these conclusions are **candidate knowledge only** until independently reproduced from authoritative target code/artifacts by the new Project Manager.

### Explicitly not transferred as project authority

- shift numbers or worker identities;
- worker ratings;
- OTK verdicts as product truth;
- old queue state as executable work;
- old heartbeat/lease/fence generations;
- old scheduler cadence;
- Telegram reporting machinery;
- old factory directives as current project-manager commands.

## 8. Migration boundary

Until the agreed migration/reconciliation gates are complete:
- do not resume speculative APFS writer changes;
- do not re-enable the old iOS scheduler/factory;
- do not treat `fde4f271...` as authoritative;
- do not widen the milestone beyond root-shell boot;
- preserve existing product CI/E2E infrastructure.

The next intended governance step is installation of a project-local persistent Project Manager and registration of that manager in the shared Agent Control Plane.

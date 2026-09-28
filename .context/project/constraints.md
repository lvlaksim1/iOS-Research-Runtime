# Project constraints

## RULE — Durable constraints

- The user-facing product is Windows-native and GUI-only; end users must not need macOS, Xcode, Python, Go, Rust, MSYS2, or command-line tooling installed separately.
- Apple firmware and copyrighted Apple binaries are not stored in this repository.
- Upstream tools/runtime inputs must remain pinned and provenance-checkable.
- The current milestone is recovery `launchd` plus verified root shell; later UI/Apple-service milestones must not distract from this blocker.
- APFS writer semantics must not be changed speculatively. A semantic change requires discriminating evidence tied to an immutable target revision and test evidence.
- The retired `ai-agent-lab` shift-worker/OTK factory remains prohibited as project orchestration.
- PP-RM is separately approved as a native execution Runtime subordinate to the persistent Project Manager; A/B are disposable execution carriers, not persistent project owners or managers.
- A runtime/chat replacement does not change `ios-research-runtime-project-manager` identity or commitment ownership.
- PP-RM A/B may mutate product `main` only inside the Manager-issued work package and must not ordinarily mutate `manager-state`.
- Product claims require verification against `main` and exact CI/runtime evidence; Manager-state prose or A/B narrative alone is never proof of product behavior.
- Product release/publication remains Owner-gated.

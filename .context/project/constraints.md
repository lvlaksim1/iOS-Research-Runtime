# Project constraints

## RULE — Durable constraints

- The user-facing product is Windows-native and GUI-only; end users must not need macOS, Xcode, Python, Go, Rust, MSYS2, or command-line tooling installed separately.
- Apple firmware and copyrighted Apple binaries are not stored in this repository.
- Upstream tools/runtime inputs must remain pinned and provenance-checkable.
- The current milestone is recovery `launchd` plus verified root shell; later UI/Apple-service milestones must not distract from this blocker.
- APFS writer semantics must not be changed speculatively. A semantic change requires discriminating evidence tied to an immutable target revision and test evidence.
- The retired `ai-agent-lab` shift-worker factory is not an execution authority for this project and must not be re-enabled as part of normal development.
- A runtime/chat replacement creates a new execution carrier of the same Project Manager, not a new worker or manager.
- Product claims require verification against `main` and exact CI/runtime evidence; manager-state prose alone is never proof of product behavior.

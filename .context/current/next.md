# Next actions

Canonical launch recipe: `.context/pp-rm/LAUNCH_PACKAGE.md`.

1. Instantiate exactly five PP-RM native objects: Worker A, Worker B, Runtime Mailbox, Pulse Register, Trace/Result Register, initially inert/disabled as defined by the launch recipe.
2. Patch Worker A/B prompts with the created task IDs.
3. Seed the first Manager-issued work package `IOS-M1-R1` into Runtime Mailbox, with exact payload SHA-256.
4. Seed bootstrap Trace SEND and Pulse PACKAGE_READY; fresh-read and verify all register state.
5. Arm Worker A only. Do not arm B at bootstrap.
6. A/B must first reconcile live `main@85d408075ab8a66f6d16043029eb2255956eb1b9`.
7. Reapply only the product semantics from historical `d743b2e...` and the regression coverage from `b3befaeb...`; do not import unrelated later commits.
8. Run the minimum narrow validation; if green, run Windows E2E to establish the exact new boundary.
9. At launchd/AMFI, persistent APFS error 79, an unexpected regression, ambiguous side effect, or PP-RM invariant failure: stop the continuous strategic loop and return an evidence-backed HIGH-LEVEL CHECKPOINT to the Manager.
10. Manager reviews the checkpoint, persists any durable semantic change, then issues the next work package.
11. Treat OCB as routine: retry missing expected server responses safely with read-back/idempotency safeguards.
12. Preserve product authority on `main` and Manager authority on `manager-state`.

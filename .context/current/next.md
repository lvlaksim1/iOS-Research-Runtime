# Next actions

1. Instantiate PP-RM native runtime objects: Worker A, Worker B, Runtime Mailbox, Pulse Register, and Trace/Result Register.
2. Seed the first Manager-issued work package `IOS-M1-R1` into PP-RM.
3. Start exactly one initial worker generation.
4. A/B must first reconcile live `main@85d408075ab8a66f6d16043029eb2255956eb1b9`.
5. Reapply only the product semantics from historical `d743b2e...` and the regression coverage from `b3befaeb...`; do not import unrelated later commits.
6. Run the minimum narrow validation; if green, run Windows E2E to establish the exact new boundary.
7. At launchd/AMFI, persistent APFS error 79, an unexpected regression, ambiguous side effect, or PP-RM invariant failure: stop the continuous strategic loop and return an evidence-backed HIGH-LEVEL CHECKPOINT to the Manager.
8. Manager reviews the checkpoint, persists any durable semantic change, then issues the next work package.
9. Treat OCB as routine: retry missing expected server responses safely with read-back/idempotency safeguards.
10. Preserve product authority on `main` and Manager authority on `manager-state`.

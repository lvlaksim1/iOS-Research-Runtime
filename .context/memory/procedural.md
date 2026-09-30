# Procedural memory

Updated: 2026-09-30 23:51 MSK

- PP-RM generation18/package007 is RUNNING.
- Result-first workflow evidence is mandatory: search existing exact-SHA runs before any dispatch attempt.
- A workflow SUCCESS is accepted only if its actual evidence satisfies the gate; a defective assertion can yield a false-positive SUCCESS and must be detected by log/artifact reconciliation.
- Package007 generation1 consumed existing run `36771957949` and found SHA1-primary + SHA256-alternate despite SUCCESS.
- First parser correction was published as `main@a0d0dd1a9f95543dca25bfb647e1f67e3d4e1e18`.
- That publication used frozen MUTATION_READY and OCB3: attempts1-2 explicit OSB, attempt3 SUCCESS.
- Exact-SHA run `36775221102` on `a0d0dd1...` also completed SUCCESS but raw log still showed SHA1-primary + SHA256-alternate.
- Second parser defect: rcodesign emits `slot: 'CodeDirectory Alternate #0 (4096)'`; parser did not allow the quote immediately after `slot:`.
- Current frozen target `79393c0d0797fc88d02445e9afb58484dd50c6f1` changes alternate-slot detection only.
- Current baton: generation4 Worker A MUTATION_READY, baseline `a0d0dd1...`, target `79393c0d...`, force=false.
- Do not mutate signer until the gate itself truthfully detects SHA1-primary versus SHA256-primary.
- Generation16 two-phase mutation, generation17 recurring Watchdog and OCB3 remain unchanged.
- Packages005 and006 must not resume.

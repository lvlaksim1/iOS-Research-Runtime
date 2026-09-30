# Next actions

Updated: 2026-09-30 23:51 MSK

1. Continue package `IOS-M1-CONTINUOUS-007` from generation4 Worker A MUTATION_READY.
2. Reconcile authoritative main against frozen baseline `a0d0dd1a...` and target `79393c0d...`.
3. If main==baseline, publish exactly the frozen target with `force=false` under OCB3; if main==target, treat mutation as already successful; if neither, FAIL_STOP.
4. After successful publication, use result-first workflow logic: consume the automatically created exact-SHA rcodesign Windows Gate run before considering any dispatch.
5. Verify from raw log/artifact that the corrected gate now fails when actual signature is SHA1-primary + SHA256-alternate.
6. Only after the gate itself is trustworthy, design or apply the smallest signer correction that can produce true SHA256-primary.
7. Require direct post-sign evidence of `digest_type: sha256` in the primary CodeDirectory and absence/acceptable treatment of alternate CodeDirectory according to the test contract.
8. Preserve generation16 frozen-target publication, generation17 recurring Watchdog, generation18 result-first workflow evidence, OCB3 and dispatch/runtime separation.
9. Never resume package005 or package006.

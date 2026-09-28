# PP-RM Launch Package — iOS Research Runtime

Status: PRODUCTION / TEMPORARY OCB3 EXPERIMENT
Manager: `ios-research-runtime-project-manager`
Manager generation: 8 after seal
Product main before experiment: `85d408075ab8a66f6d16043029eb2255956eb1b9`
Prepared commit: `cbba4060db543d4a2b800f7c15b2a700e69f6961`

## Stable protocol

Reuse existing Worker A/B and disabled Mailbox/Pulse/Trace. Manager owns strategy; A/B own bounded execution only. Successor arm remains the final tool operation.

## Temporary targeted OCB3 experiment

Scope ONLY:
`update-ref(main -> cbba4060db543d4a2b800f7c15b2a700e69f6961)`.

Procedure:
1. Fresh-read `main`; require `85d408075ab8a66f6d16043029eb2255956eb1b9`.
2. Attempt update-ref once.
3. If explicit OSB, exact-identical attempt 2.
4. If attempt 2 is explicit OSB, exact-identical attempt 3.
5. No attempt 4.
6. After success or attempt 3, fresh-read `main`.
7. Classify from actual branch state:
   - `main=cbba4060...` => success; continue WAIT_CI.
   - `main=85d4080...` => not published; Manager checkpoint.
   - anything else/ambiguous => fail-stop Manager checkpoint.
8. Trace each attempt independently.

This temporary three-attempt allowance does not replace permanent OCB policy. Manager reviews evidence afterward.

## After successful publication

Observe existing CI for the published SHA. Do not add workflows. Return high-level checkpoint at gate failure, exact Windows E2E completion, APFS error 79, launchd/AMFI, unexpected regression, ambiguity or package objective completion.

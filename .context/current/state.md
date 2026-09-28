# Current state

## Governance
- manager: `ios-research-runtime-project-manager`
- product authority: `main`
- Manager authority: `manager-state`
- PP-RM: production-admitted, paused at Manager checkpoint
- Worker A/B: disabled
- Mailbox/Pulse/Trace: disabled

## Prepared publication

Live `main`: `85d408075ab8a66f6d16043029eb2255956eb1b9`.

Prepared but unpublished:
- tree `9b0afec0e6ccd33867978284fd3767a7146e0499`
- commit `cbba4060db543d4a2b800f7c15b2a700e69f6961`

First production turn:
- update-ref attempt 1: EXPLICIT_OSB
- exact-identical attempt 2: EXPLICIT_OSB
- reconciliation: main unchanged
- CI/E2E: not triggered

## Temporary experiment

Owner authorized one temporary third exact-identical update-ref request if the first two requests in the repeated run are explicit OSB.

Purpose: measure whether increasing identical request count improves Scheduled Runtime -> GitHub mutation passability.

No fourth request. Final server-state reconciliation is mandatory. Permanent OCB policy is not yet changed by this experiment.

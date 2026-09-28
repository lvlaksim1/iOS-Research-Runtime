# DEC-0006 — Temporary third identical OCB request experiment

Date: 2026-09-28/29
Status: EXPERIMENT COMPLETED / PERMANENT POLICY UNCHANGED
Authority: direct Owner directive

## Decision

For the targeted `update-ref(main -> cbba4060db543d4a2b800f7c15b2a700e69f6961)` experiment only, allow a third exact-identical GitHub request when attempts 1 and 2 each return explicit OSB.

No automatic fourth request was authorized.

## Purpose

Measure whether request count affects Scheduled Task -> GitHub mutation passability.

## Observations

- Full production turn: attempt1=EXPLICIT_OSB, attempt2=EXPLICIT_OSB; reconciliation showed no publication.
- Minimal targeted probe #1: attempt1=SUCCESS; publication confirmed.
- Minimal targeted probe #2 with unchanged request parameters while main already equaled target: attempt1=EXPLICIT_OSB, attempt2=EXPLICIT_OSB, attempt3=SUCCESS; final read-back confirmed target main.

## Interpretation

A third exact-identical request can pass after two explicit OSBs in at least one observed runtime.

This does not establish three attempts as a universal optimum because:
- sample size is small;
- the second minimal probe was idempotent against an already-targeted branch;
- runtime context/request sequence appears to influence passability.

## Consequence

The experiment is evidence for later OCB policy refinement.

Permanent OCB retry count remains an explicit future Manager decision. Mutation ambiguity controls and authoritative server-state reconciliation remain mandatory.

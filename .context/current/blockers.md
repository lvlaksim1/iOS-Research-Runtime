# Current blockers and open risks

## Active blocker

Prepared raw-APFS restoration commit `cbba4060...` exists but is unpublished because the first production `update-ref` and its exact-identical retry both received explicit OSB.

Current `main` remains `85d4080...`; CI/E2E for the prepared commit has not started.

## Temporary experiment

Owner authorized a controlled third-request experiment:
- same update-ref;
- attempts 1 -> 2 -> 3 only when each preceding attempt returns explicit OSB;
- no fourth request;
- reconcile `main` afterward.

Controls:
- reuse existing prepared commit;
- no unrelated mutation before classification;
- unexpected/ambiguous branch state => Manager checkpoint;
- result does not automatically become permanent policy.

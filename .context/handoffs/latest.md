# Latest handoff

Persistent manager: `ios-research-runtime-project-manager`.
Manager-state authority: `manager-state`.
Product authority: `main`.

## Completed

Migration stages 1-8 are complete.

The manager is installed and registered in the shared Agent Control Plane; the old rotating-worker iOS autonomy is archived and has no pending executable event.

Legacy shift-154 extentref claims were independently reproduced from exact E2E artifact 10655952032 and exact product code. The raw extentref-count difference does not justify another semantic writer change.

## Verified product boundary

Product-code baseline: `3b0f5648f004f58daef526082b3d2a32d132edcf`.
Windows E2E run: `35634992757`.
Current failure: repeated APFS `mountroot error 79` after `BSD root: md0`.

## Next operation

Stage 9: clean-runtime reinstantiation proof.

After that proof, resume development with the diagnostic-only APSB/root-tree evidence experiment recorded in `.context/manager/plans.md`.

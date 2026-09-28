# Manager plans

## Continuous PP-RM package

Package: `IOS-M1-CONTINUOUS-001`

High-level objective:
Advance the current product from `main@cbba4060db543d4a2b800f7c15b2a700e69f6961` to verified Windows recovery `launchd` plus verified root shell, using evidence-driven bounded A/B turns.

## Immediate work

1. Reconcile current `main` and exact current CI.
2. Diagnose why E2E expects `qemu-sptm-windows-gate` but cannot download it.
3. Repair the existing gate/artifact path with the smallest evidence-backed repository change. Do not change iOS/APFS semantics merely to bypass infrastructure.
4. Run/observe exact-SHA Windows E2E.
5. If E2E reaches a product/boot failure, diagnose and fix the next evidence-supported defect within IOS-M1 scope.
6. Continue A/B turns through subsequent build/CI/boot iterations without returning to Manager merely because an intermediate stage failed.
7. Continue until IOS-M1 is achieved or a genuine stop condition is reached.

## Worker autonomy inside this package

Workers MAY:
- inspect repository history, workflows, source, tests, logs, artifacts metadata, and exact run/job evidence;
- make narrow repository changes needed to repair build, workflow, QEMU gate, ramdisk, boot integration, or other IOS-M1 execution defects;
- add/adjust deterministic regression coverage directly related to a fix;
- commit/publish changes to `main` when the live branch still matches the worker's reconciled base;
- observe and classify resulting CI;
- choose tactical implementation details when evidence supports them.

Workers MUST NOT:
- publish releases;
- mutate `manager-state`;
- change milestone, authority topology, or persistent-agent architecture;
- introduce broad speculative APFS/security changes without evidence;
- perform destructive unrelated repository operations.

## OCB

Operational parameters remain:
- explicit OSB only;
- exact request attempt 1;
- if explicit OSB, exact-identical attempt 2;
- if attempt 2 also explicit OSB, exact-identical attempt 3;
- no attempt 4;
- authoritative state reconciliation after mutation attempt sequences;
- ambiguous mutation => no blind replay.

## Handoff behavior

Each runtime does one bounded meaningful unit of work. If the objective is not complete and no genuine stop condition exists:
- publish next Mailbox generation with factual checkpoint and next bounded action;
- verify read-back;
- append Trace SEND;
- arm partner as LAST TOOL OPERATION;
- zero tool calls afterward.

CI waiting is not a Manager stop. If evidence is still running, hand off a WAIT_CI turn to the partner.

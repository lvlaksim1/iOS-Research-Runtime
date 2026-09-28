# Latest handoff

Persistent manager: `ios-research-runtime-project-manager`.
Product authority: `main`.
Manager authority: `manager-state`.

IOS-M1-R1 prepared:
- tree `9b0afec0e6ccd33867978284fd3767a7146e0499`
- commit `cbba4060db543d4a2b800f7c15b2a700e69f6961`
- parent `85d408075ab8a66f6d16043029eb2255956eb1b9`

Two exact update-ref attempts both received explicit OSB. Reconciliation proved main unchanged. Both workers are disabled and PP-RM is safely paused.

Owner temporarily permits a third exact-identical request when attempts 1 and 2 both return explicit OSB, to measure request-count influence on Scheduler -> GitHub passability.

Repeat only the failed publication step using the existing prepared commit. After at most three attempts, reconcile authoritative main.

If publication succeeds, continue IOS-M1-R1 at WAIT_CI. Otherwise stop and return evidence to Manager. No fourth identical request is authorized.

# Current state

Updated: 2026-09-30 22:43 MSK

## Governance
- manager: `ios-research-runtime-project-manager`
- manager generation: 17
- product authority: `main`
- PP-RM version: generation 17 recurring-backstop Watchdog over generation-16 native two-phase mutation
- execution status: RUNNING
- active package: `IOS-M1-CONTINUOUS-006`

## Product
- live main: `bcde5661eab70b6811a5f1fffe0552edaedf980a`
- exact-head Windows E2E run `36729602541`: FAILURE at step 11 `Run provisioning and Darwin root-shell proof`
- steps 1–10: SUCCESS
- failure evidence collection/upload: SUCCESS
- root shell: NOT VERIFIED
- no ambiguous product ref mutation is known in flight

## Active product diagnosis
Package006 generation1 reconciled terminal E2E evidence:
- post-merge `/bin/bash` is Mach-O, size 1744336
- identifier: `com.apple.bash`
- injected trust membership: true
- primary CodeDirectory digest remained SHA1
- SHA256 remained alternate
- primary CDHash: `35099b663d01fc7e0f7fbd2da53d57c16a9be029`
- AMFI still reports adhoc/unsuitable CT policy/signature validation failure and Launch Constraint Violation

Package006 generation2 identified the signer root cause:
- repo signer invokes `rcodesign sign --binary-identifier com.apple.bash --digest sha256`
- upstream CLI supports explicit SHA256 primary
- later `SigningSettings::import_settings_from_macho` overrides the CLI-configured digest
- for absent/old Mach-O target it forces SHA1 primary and adds SHA256 as extra

Therefore the prior run did not actually test SHA256-primary behavior.

## PP-RM generation 17 production evidence
- package006 bootstrap generation1 Worker B ACKed and handed off normally
- generation2 Worker A ACKed, completed bounded root-cause analysis and handed off normally
- current observed baton: generation3, owner B, state READY, activation_attempt=1, ACK=NONE
- Watchdog is enabled with persistent `RRULE:FREQ=HOURLY` backstop
- Worker A/B and Watchdog prompts are immutable for this package
- package005 remains superseded and MUST NOT be resumed

## Current next action
Design the smallest bounded way to prevent `rcodesign import_settings_from_macho` from overriding explicit SHA256 for this bash diagnostic. Prefer an upstream-supported CLI/config mechanism; otherwise isolate a local signer/tool correction. Create a product target only after evidence shows post-sign primary becomes SHA256.

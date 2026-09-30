# Latest handoff

Updated: 2026-09-30 23:51 MSK

Persistent manager: `ios-research-runtime-project-manager`.
Manager generation: 18.
Product authority: `main@a0d0dd1a9f95543dca25bfb647e1f67e3d4e1e18`.
Active package: `IOS-M1-CONTINUOUS-007`.
Execution status: RUNNING.

## Generation18 correction in production
The result-first workflow rule is active and has already prevented a repeat of the package006 false Owner gate. Existing exact-SHA runs are consumed before any dispatch attempt.

## Package007 evidence
Generation1 / Worker B:
- consumed existing run `36771957949` on exact main instead of dispatching;
- raw evidence disproved strict SHA256-primary despite workflow SUCCESS;
- found first parser bug in alternate-slot detection;
- prepared parser-only target `a0d0dd1...`.

Generation2 / Worker A:
- executed the frozen mutation;
- update_ref attempts1-2 explicit OSB; exact-identical attempt3 SUCCESS;
- readback confirmed `main@a0d0dd1...`.

Generation3 / Worker B:
- consumed automatically generated exact-SHA run `36775221102` by result-first logic;
- raw log again showed primary `digest_type: sha1` and alternate `digest_type: sha256`;
- found second parser bug: actual slot text contains a quote after `slot:`;
- prepared immutable parser-only target `79393c0d0797fc88d02445e9afb58484dd50c6f1`;
- no mutable ref change in generation3.

## Current baton
Generation4 / Worker A / `MUTATION_READY`.
Frozen descriptor:
- mutation_id `iosm1c7-mut-0003-fix-quoted-alternate-slot`
- baseline `a0d0dd1a9f95543dca25bfb647e1f67e3d4e1e18`
- target `79393c0d0797fc88d02445e9afb58484dd50c6f1`
- force=false

## Next
Execute only the frozen parser mutation after authoritative reconciliation, then consume the resulting exact-SHA gate run and require truthful strict-primary evidence before any signer mutation.

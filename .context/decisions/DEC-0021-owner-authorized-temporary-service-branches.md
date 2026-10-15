# DEC-0021 — Owner authorization for temporary GitHub service branches

Date: 2026-10-15
Status: ACCEPTED
Authority: direct Owner instruction in the active project conversation
Project: lvlaksim1/iOS-Research-Runtime

## Owner decision

The Owner explicitly authorizes creating temporary service branches in GitHub for preparing atomic project changes, or in other cases where a temporary branch is necessary and justified.

Original instruction (Russian):
> Разрешаю создавать временные служебные ветки GitHub для подготовки атомарных изменений проекта или в иных случаях, когда это необхоимо и обоснованно

## Scope and boundaries

- A temporary service branch must have a concrete, justified purpose and a verified base ref.
- This permission does not authorize force-updating `main`, bypassing required evidence gates, publishing releases, or claiming code that was never constructed.
- The PP-RM two-phase publication, exact-SHA reconciliation, and DEC-0020 ordered-prerequisite evidence gates remain in force.
- Explicit tool-safety blocks must not be bypassed or misclassified as successful writes.

## Verified implementation checkpoint

A temporary branch `pp-rm/g649-pmgr-two-file-staging` was created with base commit `89cf1e04571545010c2433f24264bae25f5c5f2d` and subsequently verified by reading the GitHub ref.

The authorized ADT-preservation and QEMU PMGR-MMIO paired code change was **not** constructed at this checkpoint. Worker B at generation 649 and Worker A at generation 650 encountered explicit safety-check blocks; generation 651 did not identify a preexisting complete paired exact-SHA target. The PP-RM Mailbox reports `OCB_BACKOFF`. Neither a new product commit nor a new build/e2e result may be inferred from this decision.

## Durability

This is a project authority decision under DEC-0020 Durable Finding Gate. It was previously recorded in runtime Mailbox/Trace but not durably published because the earlier GitHub writes were blocked.

This document records the Owner permission; it is **not** itself a product-code implementation or an authorization to mark Large Stage 1 complete.

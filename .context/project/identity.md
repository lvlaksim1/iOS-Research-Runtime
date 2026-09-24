# Project identity

## FACT — Identity

`lvlaksim1/iOS-Research-Runtime` is the product repository for a Windows-native research runtime that provisions, boots, and investigates modern iOS/Darwin environments with QEMU.

The repository owns the Windows GUI, provisioning pipeline, pinned runtime/tool integration, ramdisk preparation, QEMU launch/runtime management, and evidence-producing Windows end-to-end tests.

The project-local persistent Project Manager is `ios-research-runtime-project-manager`. Durable manager state lives on `manager-state`; product truth lives on `main`.

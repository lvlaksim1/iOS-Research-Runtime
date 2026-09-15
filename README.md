# iOS Research Runtime

Windows-native research runtime for booting and investigating modern iOS/Darwin environments with QEMU.

## Goal

The project aims to provide a normal Windows GUI that manages the complete runtime lifecycle without requiring the user to install macOS, Xcode, Python, Go, Rust, MSYS2, or command-line tooling.

Target architecture:

```text
Windows GUI
   |
   +-- Provisioning
   |     +-- Apple IPSW
   |     +-- firmware extraction
   |     +-- ramdisk preparation
   |     +-- trust cache
   |
   +-- Runtime Manager
         +-- qemu-sptm
         +-- -M darwin
         +-- SPTM / TXM / XNU
         +-- serial log
```

## First milestone

The first milestone is intentionally narrow:

1. Run as a native Windows desktop application.
2. Detect a prepared iOS firmware bundle.
3. Start and stop `qemu-sptm` from the GUI.
4. Capture the serial boot log in the GUI.
5. Boot a modern iOS/Darwin recovery environment to `launchd` and a root shell.
6. Keep all user-facing operation GUI-only.

SpringBoard, graphical display, touch input, Apple Account, Family Sharing and Screen Time are later milestones.

## Upstream research base

The initial runtime design is based on the architecture demonstrated by:

- `jprx/darwin-vm`
- `jprx/qemu-sptm`

No Apple firmware or copyrighted Apple binaries are stored in this repository.

## Status

Early development. The initial Windows runtime scaffold is being built.

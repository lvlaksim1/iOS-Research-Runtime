# Project goals

## REQUIREMENT — Primary goals

- Deliver a reliable Windows-native GUI runtime that can prepare the required iOS/Darwin boot assets and launch the runtime without requiring macOS or Xcode on the user's machine.
- Complete the first milestone by reaching modern iOS/Darwin recovery `launchd` and a verified root shell through the Windows end-to-end path.
- Keep user-facing operation GUI-only while allowing build/test automation to provide reproducible engineering evidence.
- Preserve exact provenance for pinned upstream runtime/tool inputs and for product evidence used to accept milestones.
- Treat SpringBoard, graphical interaction, Apple Account, Family Sharing, and Screen Time as later milestones after the root-shell foundation is verified.

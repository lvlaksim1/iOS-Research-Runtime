# M3 NVMe IRQ trace opt-in — isolated C# compile prerequisite

Scope: `IOS-M3-CONTINUOUS-011`, generation 45. This is a bounded **offline compile prerequisite**, not a Windows product build, QEMU runtime trace, NVMe/IOKit binding or Stage 1 proof.

The G44 Library bundle (`iosm3c11-g0044-optin-trace-wiring-ac331e795f6d`) adds `QemuNvmeTraceOptIn.cs` and changes `QemuCommandBuilder.cs`. The published baseline `50fff7ab8fc33fa1324ea204416f7a773a191033` contains `RuntimeLayout.cs`, Git blob `b1d798089e065d84a40da5f95727d0660a09f9fc`. G44 is **not published**; do not run GitHub Actions against main expecting the G44 code to exist.

`scripts/check_m3_trace_csharp_compile.py` requires these exact three files under `--source-root`. It checks SHA-256 of both G44 files and the Git blob SHA-1 of the published layout before doing anything. A temporary generated `net8.0` project contains only those three C# files and no project-specific build targets, custom package dependencies, or remote Git configuration. `dotnet restore` uses a newly created empty local package source; `dotnet build --no-restore` follows. Temporary directories are removed. Exit 0 with `ISOLATED_CSHARP_COMPILE_PASS_NOT_PRODUCT_BUILD` only after actual successful restore, build, and nonempty assembly output. Exit 2 means unavailable or unsupported SDK; exit 3 means source mismatch, restore/compile failure or missing assembly.

Run from a locally reconstructed tree containing G44 and the published RuntimeLayout:

```text
python scripts/check_m3_trace_csharp_compile.py --source-root . --plan-only
python scripts/check_m3_trace_csharp_compile.py --source-root . --dotnet dotnet
python -m unittest discover -s tests/python -p test_check_m3_trace_csharp_compile.py -v
```

A plan-only success **never** counts as C# compilation. The local Linux environment at generation 45 has Git 2.47.3 but no `dotnet`, `csc` or `msbuild`; actual C# compile and Windows CI remain `NOT_RUN`. Even a successful isolated compile must precede, not substitute for, a real Windows product Build on an exact published SHA. Full-system E2E remains blocked by the earlier AppleEmbeddedPCIE `#ports` prerequisite; no native `#ports` value is inferred.

No code in this gate changes PCIe topology, ADT, AIC, QEMU binaries or runtime boot arguments. The previously safety-refused main ref update for frozen target `49d5de208e7b797c1acb2e48cf3e0dff20ea0948` is not retried.

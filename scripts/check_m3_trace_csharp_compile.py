#!/usr/bin/env python3
"""Offline, isolated .NET 8 compile prerequisite for the G44 QEMU trace opt-in.

Requires exact G44 Library bytes and published RuntimeLayout blob. This is a
compile-only prerequisite, never evidence of QEMU execution or iOS boot.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

BASELINE_MAIN = "50fff7ab8fc33fa1324ea204416f7a773a191033"
PARENT_CHANGE = "iosm3c11-g0044-optin-trace-wiring-ac331e795f6d"
SOURCES = {
    "QemuCommandBuilder.cs": (
        "src/IOSResearchRuntime/Services/QemuCommandBuilder.cs",
        "6069560c1bf8cddef51fea4959bca23a275a49f9745d79d1a9d56ff95bf62197",
    ),
    "QemuNvmeTraceOptIn.cs": (
        "src/IOSResearchRuntime/Services/QemuNvmeTraceOptIn.cs",
        "98456e8b37f381523238a1f8bbd5f970e7a625fbe63056822564a6b4c0d4bbab",
    ),
}
LAYOUT_PATH = "src/IOSResearchRuntime/Services/RuntimeLayout.cs"
LAYOUT_BLOB = "b1d798089e065d84a40da5f95727d0660a09f9fc"
PROJECT = '''<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
    <EnableDefaultCompileItems>false</EnableDefaultCompileItems>
    <GenerateAssemblyInfo>false</GenerateAssemblyInfo>
    <UseAppHost>false</UseAppHost>
    <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
  </PropertyGroup>
  <ItemGroup>
    <Compile Include="src/QemuCommandBuilder.cs" />
    <Compile Include="src/QemuNvmeTraceOptIn.cs" />
    <Compile Include="src/RuntimeLayout.cs" />
  </ItemGroup>
</Project>
'''


def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def read_exact_sources(root: Path) -> dict[str, bytes]:
    result: dict[str, bytes] = {}
    for name, (relative, expected) in SOURCES.items():
        content = (root / relative).read_bytes()
        actual = hashlib.sha256(content).hexdigest()
        if actual != expected:
            raise ValueError(f"SOURCE_SHA256_MISMATCH:{name}:expected={expected}:actual={actual}")
        result[name] = content
    layout = (root / LAYOUT_PATH).read_bytes()
    actual_blob = git_blob_sha1(layout)
    if actual_blob != LAYOUT_BLOB:
        raise ValueError(f"LAYOUT_GIT_BLOB_MISMATCH:expected={LAYOUT_BLOB}:actual={actual_blob}")
    result["RuntimeLayout.cs"] = layout
    return result


def receipt(status: str, **fields: object) -> None:
    print(json.dumps({"status": status, "baseline_main_sha": BASELINE_MAIN,
                      "parent_change_id": PARENT_CHANGE, **fields}, sort_keys=True))


def run(root: Path, dotnet: str, plan_only: bool, timeout: int) -> int:
    try:
        sources = read_exact_sources(root)
    except (ValueError, OSError) as exc:
        receipt("INVALID_SOURCE", reason=str(exc))
        return 3
    if plan_only:
        receipt("PLAN_ONLY_NO_CSHARP_COMPILATION", sources={
            k: {"sha256": hashlib.sha256(v).hexdigest(), "bytes": len(v)}
            for k, v in sources.items()}, project_sha256=hashlib.sha256(PROJECT.encode()).hexdigest())
        return 0
    executable = shutil.which(dotnet)
    if not executable:
        receipt("NOT_RUN_DOTNET_UNAVAILABLE", dotnet=dotnet)
        return 2
    with tempfile.TemporaryDirectory(prefix="ios-m3-csharp-gate-") as temp:
        work = Path(temp)
        (work / "src").mkdir()
        (work / "offline-feed").mkdir()
        for name, content in sources.items():
            (work / "src" / name).write_bytes(content)
        project = work / "CompilePrerequisite.csproj"
        project.write_bytes(PROJECT.encode("utf-8"))
        env = __import__("os").environ.copy()
        env.update({"DOTNET_CLI_HOME": str(work / "cli-home"),
                    "DOTNET_CLI_TELEMETRY_OPTOUT": "1",
                    "DOTNET_SKIP_FIRST_TIME_EXPERIENCE": "1",
                    "NUGET_PACKAGES": str(work / "nuget-packages")})
        commands = [
            [executable, "--version"],
            [executable, "restore", str(project), "--source", str(work / "offline-feed"),
             "--ignore-failed-sources", "--nologo"],
            [executable, "build", str(project), "--no-restore", "--configuration", "Release",
             "--nologo", "-p:UseSharedCompilation=false"],
        ]
        records = []
        for index, command in enumerate(commands):
            try:
                completed = subprocess.run(command, cwd=work, env=env, capture_output=True,
                                           text=True, timeout=timeout, check=False)
            except (OSError, subprocess.TimeoutExpired) as exc:
                receipt("NOT_RUN_OR_FAILED_TOOL", step=index, reason=type(exc).__name__, records=records)
                return 2 if index == 0 else 3
            combined = (completed.stdout + "\n" + completed.stderr)[-2500:]
            records.append({"step": ("version", "offline_restore", "compile")[index],
                            "exit_code": completed.returncode, "output_tail": combined})
            if completed.returncode != 0:
                receipt("COMPILE_PREREQUISITE_FAILED", records=records)
                return 3
            if index == 0:
                version = completed.stdout.strip()
                if not re.fullmatch(r"\d+\.\d+\.\d+(?:[-+][\w.-]+)?", version) or int(version.split(".")[0]) < 8:
                    receipt("NOT_RUN_UNSUPPORTED_DOTNET_SDK", version=version, records=records)
                    return 2
        dll = work / "bin" / "Release" / "net8.0" / "CompilePrerequisite.dll"
        if not dll.is_file() or dll.stat().st_size == 0:
            receipt("COMPILE_OUTPUT_MISSING", records=records)
            return 3
        receipt("ISOLATED_CSHARP_COMPILE_PASS_NOT_PRODUCT_BUILD", records=records,
                assembly_sha256=hashlib.sha256(dll.read_bytes()).hexdigest())
        return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--dotnet", default="dotnet")
    parser.add_argument("--plan-only", action="store_true")
    parser.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args(argv)
    if args.timeout < 1 or args.timeout > 600:
        parser.error("timeout must be 1..600 seconds")
    return run(args.source_root, args.dotnet, args.plan_only, args.timeout)


if __name__ == "__main__":
    sys.exit(main())

param(
    [Parameter(Mandatory = $true)]
    [string]$AppPublishDirectory,

    [Parameter(Mandatory = $true)]
    [string]$QemuRuntimeDirectory,

    [Parameter(Mandatory = $true)]
    [string]$OutputDirectory
)

$ErrorActionPreference = "Stop"

$app = (Resolve-Path $AppPublishDirectory).Path
$qemu = (Resolve-Path $QemuRuntimeDirectory).Path

if (Test-Path $OutputDirectory) {
    Remove-Item $OutputDirectory -Recurse -Force
}
New-Item -ItemType Directory -Path $OutputDirectory -Force | Out-Null

Copy-Item (Join-Path $app "*") $OutputDirectory -Recurse -Force

$qemuTarget = Join-Path $OutputDirectory "tools\qemu-sptm"
New-Item -ItemType Directory -Path $qemuTarget -Force | Out-Null
Copy-Item (Join-Path $qemu "*") $qemuTarget -Recurse -Force

$required = @(
    (Join-Path $OutputDirectory "iOSResearchRuntime.exe"),
    (Join-Path $OutputDirectory "tools\ios-ramdisk-tool.exe"),
    (Join-Path $qemuTarget "qemu-system-aarch64.exe")
)

foreach ($path in $required) {
    if (!(Test-Path $path)) {
        throw "Required runtime file is missing: $path"
    }
}

$files = Get-ChildItem $OutputDirectory -Recurse -File |
    Where-Object { $_.Name -ne "SHA256SUMS.txt" } |
    Sort-Object FullName

$manifestPath = Join-Path $OutputDirectory "SHA256SUMS.txt"
$lines = foreach ($file in $files) {
    $hash = (Get-FileHash $file.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
    $relative = [System.IO.Path]::GetRelativePath($OutputDirectory, $file.FullName).Replace("\", "/")
    "$hash  $relative"
}
$lines | Set-Content -Encoding ascii $manifestPath

Write-Host "Integrated Windows runtime prepared:"
Write-Host "  App:  $app"
Write-Host "  QEMU: $qemu"
Write-Host "  Out:  $OutputDirectory"
Write-Host "  Files: $($files.Count)"

param()

$ErrorActionPreference = "Stop"
$module = "github.com/deploymenttheory/go-apfs-v2"
$moduleDir = (go list -m -f "{{.Dir}}" $module).Trim()
if ([string]::IsNullOrWhiteSpace($moduleDir) -or !(Test-Path $moduleDir)) {
    throw "Unable to resolve $module"
}

$stagingRoot = Join-Path $PSScriptRoot ".apfs-patched"
$patchedModule = Join-Path $stagingRoot "go-apfs-v2"
$overrideRoot = Join-Path $PSScriptRoot "overrides/go-apfs-v2/pkg/apfswrite"

if (Test-Path $stagingRoot) {
    Remove-Item $stagingRoot -Recurse -Force
}
New-Item -ItemType Directory -Path $patchedModule -Force | Out-Null

Copy-Item (Join-Path $moduleDir "*") $patchedModule -Recurse -Force
Get-ChildItem $patchedModule -Recurse -Force | ForEach-Object {
    if (-not $_.PSIsContainer) {
        $_.IsReadOnly = $false
    }
}

$patchedWriter = Join-Path $patchedModule "pkg/apfswrite"
foreach ($name in @("file.go", "fstree.go", "btree.go", "writer.go", "spaceman.go", "super.go")) {
    $source = Join-Path $overrideRoot $name
    $destination = Join-Path $patchedWriter $name
    if (!(Test-Path $source)) {
        throw "Missing APFS writer override: $source"
    }
    if (!(Test-Path $destination)) {
        throw "Missing pinned upstream file: $destination"
    }
    Copy-Item $source $destination -Force
}

$workFile = Join-Path $PSScriptRoot "go.work"
if (Test-Path $workFile) {
    Remove-Item $workFile -Force
}
Push-Location $PSScriptRoot
try {
    go work init .
    if ($LASTEXITCODE -ne 0) {
        throw "go work init failed: $LASTEXITCODE"
    }
    go work use ./.apfs-patched/go-apfs-v2
    if ($LASTEXITCODE -ne 0) {
        throw "go work use patched APFS module failed: $LASTEXITCODE"
    }
}
finally {
    Pop-Location
}

Write-Host "Patched APFS module: $patchedModule"
Write-Host "Go workspace: $workFile"

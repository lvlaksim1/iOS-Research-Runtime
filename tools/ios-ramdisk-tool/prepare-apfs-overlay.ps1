param(
    [string]$Output = "apfs-overlay.json"
)

$ErrorActionPreference = "Stop"
$module = "github.com/deploymenttheory/go-apfs-v2"
$moduleDir = (go list -m -f "{{.Dir}}" $module).Trim()
if ([string]::IsNullOrWhiteSpace($moduleDir) -or !(Test-Path $moduleDir)) {
    throw "Unable to resolve $module"
}

$overrideRoot = Join-Path $PSScriptRoot "overrides/go-apfs-v2/pkg/apfswrite"
$replace = [ordered]@{}
foreach ($name in @("file.go", "fstree.go", "btree.go", "writer.go", "spaceman.go", "super.go")) {
    $source = Join-Path $moduleDir "pkg/apfswrite/$name"
    $target = Join-Path $overrideRoot $name
    if (!(Test-Path $source)) { throw "Missing upstream source: $source" }
    if (!(Test-Path $target)) { throw "Missing overlay source: $target" }
    $replace[$source] = (Resolve-Path $target).Path
}

$document = [ordered]@{ Replace = $replace }
$outPath = Join-Path $PSScriptRoot $Output
$document | ConvertTo-Json -Depth 4 | Set-Content -Encoding utf8NoBOM $outPath
Write-Host "APFS overlay: $outPath"

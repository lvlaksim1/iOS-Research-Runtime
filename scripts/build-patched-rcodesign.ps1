param(
    [string]$OutputDirectory = (Join-Path $PSScriptRoot "..\tools\rcodesign")
)

$ErrorActionPreference = "Stop"
$sourceCommit = "0ebbd2ef3b96d5adccc30b1cad4deea38cd735c4"
$version = "0.29.0-patched-primary-sha256-$($sourceCommit.Substring(0, 12))"
$work = Join-Path $env:RUNNER_TEMP "apple-platform-rs-$($sourceCommit.Substring(0, 12))"

if (Test-Path $work) {
    Remove-Item $work -Recurse -Force
}

git clone https://github.com/indygreg/apple-platform-rs.git $work
git -C $work checkout $sourceCommit
if ((git -C $work rev-parse HEAD).Trim() -ne $sourceCommit) {
    throw "apple-platform-rs pin mismatch"
}

$path = Join-Path $work "apple-codesign/src/signing_settings.rs"
$text = Get-Content $path -Raw
$old = "        if need_sha1_sha256 {"
$new = "        let digest_is_explicit = self.digest_type.contains_key(&scope_main)`n            || self.digest_type.contains_key(&scope_index)`n            || self.digest_type.contains_key(&scope_arch);`n`n        if need_sha1_sha256 && !digest_is_explicit {"
if (!$text.Contains($old)) {
    throw "expected signing_settings.rs patch anchor not found"
}
$text = $text.Replace($old, $new)
Set-Content -Path $path -Value $text -NoNewline

git -C $work diff --check

if ($text -notmatch 'digest_is_explicit = self\.digest_type\.contains_key\(&scope_main\)') {
    throw "explicit-digest guard missing"
}
if ($text -notmatch 'if need_sha1_sha256 && !digest_is_explicit') {
    throw "compatibility fallback guard missing"
}

Push-Location $work
try {
    cargo build --locked --release -p apple-codesign --bin rcodesign
}
finally {
    Pop-Location
}

$exe = Join-Path $work "target/release/rcodesign.exe"
if (!(Test-Path $exe)) {
    throw "patched rcodesign.exe was not built"
}

New-Item -ItemType Directory -Path $OutputDirectory -Force | Out-Null
Copy-Item $exe (Join-Path $OutputDirectory "rcodesign.exe") -Force
Set-Content -Path (Join-Path $OutputDirectory ".version") -Value $version -NoNewline

& (Join-Path $OutputDirectory "rcodesign.exe") --version
if ($LASTEXITCODE -ne 0) {
    throw "staged patched rcodesign.exe failed version probe"
}

Write-Host "PATCHED_RCODESIGN_VERSION=$version"
Write-Host "PATCHED_RCODESIGN_SOURCE=$sourceCommit"

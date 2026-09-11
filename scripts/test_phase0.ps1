# Phase 0 local verification (Windows)
# Usage: .\scripts\test_phase0.ps1
#        .\scripts\test_phase0.ps1 -Quick

param(
    [switch]$Quick,
    [switch]$SkipCompose
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

$argsList = @()
if ($Quick) { $argsList += "--quick" }
if ($SkipCompose) { $argsList += "--skip-compose" }

python scripts/test_phase0.py @argsList
exit $LASTEXITCODE

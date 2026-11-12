$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$circuitPython = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $circuitPython)) {
    throw 'Run setup.ps1 on this computer first. Virtual environments cannot be copied between laptops.'
}
Write-Host 'Open http://127.0.0.1:8000. Missing local models are reported in the workspace.'
& $circuitPython manage.py serve
exit $LASTEXITCODE

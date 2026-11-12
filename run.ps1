$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$circuitPython = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $circuitPython)) {
    throw 'Run setup.ps1 on this computer first. Virtual environments cannot be copied between laptops.'
}
& $circuitPython manage.py doctor
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Host 'Open http://127.0.0.1:8000 and wait for models to be ready before uploading.'
& $circuitPython manage.py serve
exit $LASTEXITCODE

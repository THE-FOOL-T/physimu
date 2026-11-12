# Run from PowerShell: powershell -ExecutionPolicy Bypass -File .\setup.ps1
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot

function Invoke-Checked {
    param([string]$Program, [string[]]$Arguments)
    & $Program @Arguments
    if ($LASTEXITCODE -ne 0) { throw "Setup failed: $Program $Arguments" }
}

if (-not (Get-Command py -ErrorAction SilentlyContinue)) {
    throw 'Install Python 3.12 (including its Windows py launcher), then rerun setup.'
}
if (-not (Get-Command npm.cmd -ErrorAction SilentlyContinue)) {
    throw 'Install Node.js 22 or newer, then reopen PowerShell and rerun setup.'
}
if (-not (Test-Path -LiteralPath '.venv\Scripts\python.exe')) {
    Invoke-Checked 'py' @('-3.12', '-m', 'venv', '.venv')
}
$circuitPython = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
Invoke-Checked $circuitPython @('-m', 'pip', 'install', '-e', '.')
Push-Location -LiteralPath (Join-Path $PSScriptRoot 'frontend')
try {
    Invoke-Checked 'npm.cmd' @('ci')
    Invoke-Checked 'npm.cmd' @('run', 'build')
} finally {
    Pop-Location
}
Write-Host 'Setup complete. Models are optional for startup; automatic extraction needs local weights.'
Write-Host 'To check manually supplied models: .\.venv\Scripts\python.exe manage.py doctor'
Write-Host 'Run: powershell -ExecutionPolicy Bypass -File .\run.ps1'

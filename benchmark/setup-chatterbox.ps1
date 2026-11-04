$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
$env:PIP_CACHE_DIR = Join-Path (Get-Location) '.cache\pip'
if (-not (Test-Path '.venvs\chatterbox\Scripts\python.exe')) {
    py -3.12 -m venv .venvs\chatterbox
    if ($LASTEXITCODE) { throw 'venv creation failed' }
}
$python = '.venvs\chatterbox\Scripts\python.exe'
& $python -m pip install torch==2.10.0 torchaudio==2.10.0 --index-url https://download.pytorch.org/whl/cu128
if ($LASTEXITCODE) { throw 'PyTorch failed' }
if (-not (Test-Path 'vendor\chatterbox\.git')) {
    git clone https://github.com/resemble-ai/chatterbox.git vendor/chatterbox
    if ($LASTEXITCODE) { throw 'clone failed' }
}
$revision = git -C vendor/chatterbox rev-parse HEAD
if ($revision -ne '5de7a54aa4e5e2baadb0182dde554908b48b85c2') {
    throw 'Expected pinned source 5de7a54aa4e5e2baadb0182dde554908b48b85c2; check out that commit in a clean vendor clone.'
}
& $python -m pip install -r requirements-chatterbox.txt
if ($LASTEXITCODE) { throw 'dependencies failed' }
# Explicit --no-deps avoids downgrading the Blackwell-compatible torch build.
& $python -m pip install --no-deps ./vendor/chatterbox
if ($LASTEXITCODE) { throw 'Chatterbox installation failed' }

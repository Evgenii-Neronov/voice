$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
$env:PIP_CACHE_DIR = Join-Path (Get-Location) '.cache\pip'
$env:HF_HOME = Join-Path (Get-Location) '.cache\huggingface'
if (-not (Test-Path '.venvs\qwen\Scripts\python.exe')) {
    py -3.12 -m venv .venvs\qwen
    if ($LASTEXITCODE) { throw 'venv creation failed' }
}
$python = '.venvs\qwen\Scripts\python.exe'
& $python -m pip install torch==2.10.0 torchaudio==2.10.0 --index-url https://download.pytorch.org/whl/cu128
if ($LASTEXITCODE) { throw 'CUDA PyTorch installation failed' }
& $python -m pip install -r requirements-qwen.txt
if ($LASTEXITCODE) { throw 'Qwen dependencies failed' }
& $python -m pip check
if ($LASTEXITCODE) { throw 'Dependency consistency check failed' }
& $python -c "import torch; print(torch.__version__, torch.cuda.is_available()); assert torch.cuda.is_available(); print(torch.cuda.get_device_name()); print((torch.ones(4, device='cuda')*2).cpu())"
if ($LASTEXITCODE) { throw 'CUDA smoke test failed' }

# Autositcom launcher — everything BelowNormal so the machine never hangs.
# Usage: .\scripts\run.ps1 [dashboard|pipeline|tray|all]
param([string]$Target="all")
$ErrorActionPreference="Stop"; $py = if (Test-Path .venv312\Scripts\python.exe) { ".venv312\Scripts\python.exe" } else { "python" }  # 3.12 venv: only env with av/moviepy wheels Set-Location (Split-Path $PSScriptRoot)
function Start-Below($a){ Start-Process $py -ArgumentList $a -PassThru | ForEach-Object { $_.PriorityClass="BelowNormal"; $_ } }
switch($Target){
 "dashboard"{ Start-Below "-m streamlit run src/dashboard.py --server.port 8501" }
 "pipeline"{ Start-Below "-m src.main" }
 "tray"{ Start-Below "-m src.tray" }
 default{ Start-Below "-m src.main"; Start-Below "-m streamlit run src/dashboard.py --server.port 8501"; Start-Below "-m src.tray" }
}


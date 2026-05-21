$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -LiteralPath $Root

$LogDir = Join-Path $Root "reports"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$Stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$LogPath = Join-Path $LogDir "case_study_brain_$Stamp.log"

$Limit = if ($env:PLR_AGENT_CASE_STUDY_LIMIT) { $env:PLR_AGENT_CASE_STUDY_LIMIT } else { "300" }

Write-Host "Starting Case Study Brain build from old backup data..."
Write-Host "Source: $env:PLR_AGENT_FILE_BACKUP_DIR"
Write-Host "Limit: $Limit files. Set PLR_AGENT_CASE_STUDY_LIMIT=0 for full scan."
Write-Host "Log: $LogPath"

& uv run --with-requirements requirements.txt python build_case_study_brain.py --limit $Limit 2>&1 | Tee-Object -FilePath $LogPath -Append
if ($LASTEXITCODE -ne 0) {
    throw "Case Study Brain build failed with exit code $LASTEXITCODE"
}

Write-Host "Case Study Brain build finished."
Write-Host "Log: $LogPath"

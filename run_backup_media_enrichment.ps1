$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -LiteralPath $Root

$LogDir = Join-Path $Root "reports"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$Stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$LogPath = Join-Path $LogDir "backup_media_enrichment_$Stamp.log"

$ArgsList = @(
    "run",
    "--with-requirements", "requirements.txt",
    "--with", "faster-whisper",
    "--with", "imageio-ffmpeg",
    "--with", "rapidocr-onnxruntime",
    "--with", "pillow",
    "python",
    "enrich_brains_from_backup.py",
    "--backup-root", "G:\file_backup\agent_input_backup_20260515_024325",
    "--mode", "all",
    "--whisper-model", "tiny"
)

Write-Host "Starting backup media enrichment..."
Write-Host "This will OCR images, transcribe audio/video, then rebuild the 3 role brains."
Write-Host "Log: $LogPath"

$ErrorActionPreference = "Continue"
& uv @ArgsList 2>&1 | Tee-Object -FilePath $LogPath -Append
if ($LASTEXITCODE -ne 0) {
    throw "Backup media enrichment failed with exit code $LASTEXITCODE"
}

Write-Host "Backup media enrichment finished."
Write-Host "Log: $LogPath"

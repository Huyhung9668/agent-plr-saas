$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -LiteralPath $Root

$LogDir = Join-Path $Root "reports"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$Stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$LogPath = Join-Path $LogDir "full_media_brain_$Stamp.log"

function Run-Step {
    param(
        [string]$Name,
        [string[]]$ArgsList
    )

    Write-Host ""
    Write-Host "===== $Name ====="
    Add-Content -LiteralPath $LogPath -Value ""
    Add-Content -LiteralPath $LogPath -Value "===== $Name ====="
    & uv @ArgsList 2>&1 | Tee-Object -FilePath $LogPath -Append
    if ($LASTEXITCODE -ne 0) {
        throw "$Name failed with exit code $LASTEXITCODE"
    }
}

$Common = @(
    "run",
    "--with-requirements", "requirements.txt",
    "--with", "faster-whisper",
    "--with", "imageio-ffmpeg",
    "--with", "rapidocr-onnxruntime",
    "--with", "pillow"
)

Run-Step "OCR images" ($Common + @("python", "media_text_extractor.py", "--mode", "ocr"))
Run-Step "Transcribe audio/video" ($Common + @("python", "media_text_extractor.py", "--mode", "transcribe", "--whisper-model", "tiny"))
Run-Step "Build media catalog" ($Common + @("python", "media_catalog.py"))
Run-Step "Rebuild brain" ($Common + @("python", "-c", "from brain import ingest_brain, brain_summary; stats=ingest_brain(rebuild=True); print(stats); print(brain_summary())"))

Write-Host ""
Write-Host "===== Backup raw inboxes ====="
Add-Content -LiteralPath $LogPath -Value ""
Add-Content -LiteralPath $LogPath -Value "===== Backup raw inboxes ====="
& powershell -ExecutionPolicy Bypass -File ".\backup_raw_inboxes.ps1" 2>&1 | Tee-Object -FilePath $LogPath -Append
if ($LASTEXITCODE -ne 0) {
    throw "Backup raw inboxes failed with exit code $LASTEXITCODE"
}

Write-Host ""
Write-Host "Full media brain run finished."
Write-Host "Log: $LogPath"

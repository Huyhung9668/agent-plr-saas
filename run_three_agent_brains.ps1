$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -LiteralPath $Root

$LogDir = Join-Path $Root "reports"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$Stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$LogPath = Join-Path $LogDir "three_agent_brains_$Stamp.log"

$ArgsList = @(
    "run",
    "--with-requirements", "requirements.txt",
    "--with", "faster-whisper",
    "--with", "imageio-ffmpeg",
    "--with", "rapidocr-onnxruntime",
    "--with", "pillow",
    "python",
    "build_three_agent_brains.py",
    "--whisper-model", "tiny"
)

Write-Host "Starting 3-agent brain build..."
Write-Host "Log: $LogPath"

& uv @ArgsList 2>&1 | Tee-Object -FilePath $LogPath -Append
if ($LASTEXITCODE -ne 0) {
    throw "3-agent brain build failed with exit code $LASTEXITCODE"
}

Write-Host "3-agent brain build finished."
Write-Host "Log: $LogPath"

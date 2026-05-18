param(
    [switch]$Force
)

$ErrorActionPreference = "Stop"

$Workspace = "G:\Documents\warriorplus MMO\Agent PLR Saas"
$SaasInbox = Join-Path $Workspace "saas_files\_INBOX_DROP_HERE"
$PlrInbox = Join-Path $Workspace "plr_files\_INBOX_DROP_HERE"
$BackupRoot = "G:\file_backup_PLR_Saas"
$MediaTextRoot = Join-Path $Workspace "database\media_extracted_text"

$countsJson = & uv run --with-requirements requirements.txt python -c "import json; from media_text_extractor import ROOTS, IMAGE_EXTENSIONS, AUDIO_VIDEO_EXTENSIONS; images=[]; av=[]; [images.extend([p for p in r.rglob('*') if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS]) for r in ROOTS if r.exists()]; [av.extend([p for p in r.rglob('*') if p.is_file() and p.suffix.lower() in AUDIO_VIDEO_EXTENSIONS]) for r in ROOTS if r.exists()]; print(json.dumps({'images': len(images), 'av': len(av)}))"
if ($LASTEXITCODE -ne 0) {
    throw "Could not count media files with Python extractor."
}
$counts = $countsJson | ConvertFrom-Json
$imageTotal = [int]$counts.images
$avTotal = [int]$counts.av
$ocrDone = 0
$transcriptDone = 0
$ocrAttempted = 0
$transcriptAttempted = 0

$ocrDir = Join-Path $MediaTextRoot "ocr"
$transcriptDir = Join-Path $MediaTextRoot "transcripts"
$manifest = Join-Path $MediaTextRoot "manifest.jsonl"
if (Test-Path -LiteralPath $ocrDir) {
    $ocrDone = @(Get-ChildItem -LiteralPath $ocrDir -File -ErrorAction SilentlyContinue).Count
}
if (Test-Path -LiteralPath $transcriptDir) {
    $transcriptDone = @(Get-ChildItem -LiteralPath $transcriptDir -File -ErrorAction SilentlyContinue).Count
}
if (Test-Path -LiteralPath $manifest) {
    $records = Get-Content -LiteralPath $manifest -ErrorAction SilentlyContinue | ForEach-Object {
        try { $_ | ConvertFrom-Json } catch { $null }
    }
    $ocrAttempted = @($records | Where-Object { $_ -and $_.kind -eq "ocr" } | Select-Object -ExpandProperty source -Unique).Count
    $transcriptAttempted = @($records | Where-Object { $_ -and $_.kind -eq "transcribe" } | Select-Object -ExpandProperty source -Unique).Count
}

Write-Host "Image OCR: $ocrDone / $imageTotal"
Write-Host "Audio/video transcripts: $transcriptDone / $avTotal"
Write-Host "Image OCR attempted: $ocrAttempted / $imageTotal"
Write-Host "Audio/video attempted: $transcriptAttempted / $avTotal"

if (-not $Force -and ($ocrAttempted -lt $imageTotal -or $transcriptAttempted -lt $avTotal)) {
    throw "Media extraction is not complete. Run .\run_full_media_brain.ps1 first, or rerun this script with -Force if you accept moving raw files now."
}

New-Item -ItemType Directory -Force -Path $BackupRoot | Out-Null
$Stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$BackupDir = Join-Path $BackupRoot "backup_$Stamp"
New-Item -ItemType Directory -Force -Path $BackupDir | Out-Null

$targets = @(
    @{ Source = $SaasInbox; Name = "saas_files__INBOX_DROP_HERE" },
    @{ Source = $PlrInbox; Name = "plr_files__INBOX_DROP_HERE" }
)

foreach ($target in $targets) {
    $source = (Resolve-Path -LiteralPath $target.Source).Path
    if (-not $source.StartsWith($Workspace, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to move outside workspace: $source"
    }
    $destination = Join-Path $BackupDir $target.Name
    Move-Item -LiteralPath $source -Destination $destination
    New-Item -ItemType Directory -Force -Path $target.Source | Out-Null
    New-Item -ItemType File -Force -Path (Join-Path $target.Source ".keep") | Out-Null
    Write-Host "Moved $source -> $destination"
}

Write-Host "Backup complete: $BackupDir"

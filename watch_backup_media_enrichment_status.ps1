$ErrorActionPreference = "SilentlyContinue"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -LiteralPath $Root

$LogPath = Join-Path $Root "reports\backup_media_enrichment_progress_live.log"
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $LogPath) | Out-Null

while ($true) {
    $Now = Get-Date -Format "yyyy-MM-dd HH:mm:ss K"
    $Running = Get-CimInstance Win32_Process |
        Where-Object { $_.CommandLine -match 'enrich_brains_from_backup|run_backup_media_enrichment' }

    @(
        ""
        "===== $Now ====="
        if ($Running) { "STATUS: RUNNING" } else { "STATUS: STOPPED" }
        ""
    ) | Add-Content -LiteralPath $LogPath -Encoding UTF8

    powershell -NoProfile -ExecutionPolicy Bypass -File .\check_backup_media_enrichment_status.ps1 |
        Add-Content -LiteralPath $LogPath -Encoding UTF8

    if (-not $Running) {
        "===== MONITOR STOPPED: enrichment process not found =====" |
            Add-Content -LiteralPath $LogPath -Encoding UTF8
        break
    }

    Start-Sleep -Seconds 60
}

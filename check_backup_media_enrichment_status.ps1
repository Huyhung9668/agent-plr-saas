$ErrorActionPreference = "SilentlyContinue"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -LiteralPath $Root

Write-Host "Running enrichment processes:"
Get-CimInstance Win32_Process |
    Where-Object { $_.CommandLine -match 'enrich_brains_from_backup|run_backup_media_enrichment' } |
    Select-Object ProcessId, ParentProcessId, Name, CommandLine |
    Format-Table -AutoSize

Write-Host ""
Write-Host "Extractor-aligned media completion:"
@'
from pathlib import Path
from media_text_extractor import IMAGE_EXTENSIONS, AUDIO_VIDEO_EXTENSIONS, _stable_id

backup = Path("G:/file_backup/agent_input_backup_20260515_024325")
roles = [
    ("build_product", "01_BUILD_PRODUCT"),
    ("jv_manager", "02_JV_MANAGER"),
    ("sale_page", "03_SALE_PAGE"),
]

def pct(done: int, total: int) -> str:
    return "n/a" if total == 0 else f"{done / total * 100:.1f}%"

print(f"{'Role':<14} {'OCR':<22} {'Transcript':<22} {'Total':<22} {'LastWrite'}")
print("-" * 100)
for role, folder in roles:
    root = backup / folder
    out = Path("database/agent_brains") / role / "backup_media_extracted_text"
    images = []
    av = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        ext = path.suffix.lower()
        if ext in IMAGE_EXTENSIONS:
            images.append(path)
        elif ext in AUDIO_VIDEO_EXTENSIONS:
            av.append(path)

    ocr_done = sum(1 for path in images if (out / "ocr" / (_stable_id(path) + ".md")).exists())
    tr_done = sum(1 for path in av if (out / "transcripts" / (_stable_id(path) + ".md")).exists())
    total_done = ocr_done + tr_done
    total = len(images) + len(av)
    files = list(out.rglob("*")) if out.exists() else []
    files = [path for path in files if path.is_file()]
    last = max((path.stat().st_mtime for path in files), default=None)
    if last:
        import datetime
        last_text = datetime.datetime.fromtimestamp(last).strftime("%Y-%m-%d %H:%M:%S")
    else:
        last_text = ""

    print(
        f"{role:<14} "
        f"{ocr_done}/{len(images)} ({pct(ocr_done, len(images))})".ljust(22)
        + " "
        + f"{tr_done}/{len(av)} ({pct(tr_done, len(av))})".ljust(22)
        + " "
        + f"{total_done}/{total} ({pct(total_done, total)})".ljust(22)
        + f" {last_text}"
    )
'@ | python -

Write-Host ""
Write-Host "Brain database summaries:"
@'
from pathlib import Path
from brain import brain_summary

print(f"{'Role':<14} {'Documents':>10} {'Chunks':>10} {'TextMB':>10} {'DBMB':>10} {'Errors':>8}")
print("-" * 70)
for db in Path("database/agent_brains").glob("*/*_brain.sqlite"):
    summary = brain_summary(db)
    print(
        f"{db.parent.name:<14} "
        f"{summary['documents']:>10} "
        f"{summary['chunks']:>10} "
        f"{summary['text_mb']:>10} "
        f"{summary['db_size_mb']:>10} "
        f"{summary['errors']:>8}"
    )
'@ | python -

Write-Host ""
Write-Host "Latest reports:"
Get-ChildItem reports -Filter "*enrichment*.log" -ErrorAction SilentlyContinue |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 5 FullName, Length, LastWriteTime |
    Format-Table -AutoSize

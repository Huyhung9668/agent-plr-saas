from __future__ import annotations

import argparse
import json
from pathlib import Path

from agent_profiles import AgentProfile, get_agent_profiles
from brain import brain_summary, ingest_brain
from media_catalog import build_media_catalog
from media_text_extractor import AUDIO_VIDEO_EXTENSIONS, IMAGE_EXTENSIONS, extract_media_text

DEFAULT_BACKUP_ROOT = Path("G:/file_backup/agent_input_backup_20260515_024325")


def main() -> None:
    parser = argparse.ArgumentParser(description="OCR/transcribe backup media and rebuild 3 role brains.")
    parser.add_argument("--backup-root", default=str(DEFAULT_BACKUP_ROOT))
    parser.add_argument("--only", choices=[profile.key for profile in get_agent_profiles()])
    parser.add_argument("--mode", choices=["scan", "ocr", "transcribe", "all", "rebuild"], default="scan")
    parser.add_argument("--whisper-model", default="tiny")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--no-rebuild", action="store_true")
    args = parser.parse_args()

    backup_root = Path(args.backup_root)
    profiles = [profile for profile in get_agent_profiles() if args.only is None or profile.key == args.only]
    results = []
    for profile in profiles:
        results.append(
            process_profile(
                profile,
                backup_root=backup_root,
                mode=args.mode,
                whisper_model=args.whisper_model,
                limit=args.limit,
                rebuild=not args.no_rebuild,
            )
        )
    print(json.dumps({"backup_root": str(backup_root), "results": results}, ensure_ascii=False, indent=2, default=str))


def process_profile(
    profile: AgentProfile,
    *,
    backup_root: Path,
    mode: str,
    whisper_model: str,
    limit: int | None,
    rebuild: bool,
) -> dict:
    backup_input_dir = backup_root / profile.input_dir.name
    if not backup_input_dir.exists():
        raise FileNotFoundError(f"Missing backup input folder: {backup_input_dir}")

    profile.brain_dir.mkdir(parents=True, exist_ok=True)
    catalog_dir = profile.brain_dir / "backup_media_brain_text"
    extracted_dir = profile.brain_dir / "backup_media_extracted_text"

    scan = scan_backup_media(backup_input_dir)
    result: dict = {
        "key": profile.key,
        "name": profile.name,
        "backup_input_dir": str(backup_input_dir),
        "scan": scan,
    }

    if mode == "scan":
        return result

    if mode in {"ocr", "all", "rebuild"}:
        catalog_stats = build_media_catalog([backup_input_dir], output_dir=catalog_dir)
        result["catalog"] = {
            "output_dir": str(catalog_stats.output_dir),
            "files_scanned": catalog_stats.files_scanned,
            "cataloged_files": catalog_stats.cataloged_files,
            "catalog_files": catalog_stats.catalog_files,
            "total_gb": catalog_stats.total_gb,
        }

    if mode in {"ocr", "all"}:
        result["ocr"] = {
            key: value.__dict__
            for key, value in extract_media_text(
                mode="ocr",
                roots=[backup_input_dir],
                output_dir=extracted_dir,
                limit=limit,
            ).items()
        }

    if mode in {"transcribe", "all"}:
        result["transcribe"] = {
            key: value.__dict__
            for key, value in extract_media_text(
                mode="transcribe",
                roots=[backup_input_dir],
                output_dir=extracted_dir,
                whisper_model=whisper_model,
                limit=limit,
            ).items()
        }

    if rebuild and mode in {"all", "rebuild"}:
        roots = [backup_input_dir, catalog_dir, extracted_dir]
        stats = ingest_brain(roots=roots, db_path=profile.db_path, rebuild=True)
        result["ingest"] = stats.__dict__
        result["brain_summary"] = brain_summary(profile.db_path)

    return result


def scan_backup_media(root: Path) -> dict:
    extensions = IMAGE_EXTENSIONS | AUDIO_VIDEO_EXTENSIONS | {".avi", ".mkv", ".webm", ".wmv", ".bmp", ".tif", ".tiff"}
    by_extension: dict[str, dict[str, float | int]] = {}
    total_files = 0
    total_bytes = 0
    media_files = 0
    media_bytes = 0

    for path in root.rglob("*"):
        if not path.is_file():
            continue
        total_files += 1
        size = path.stat().st_size
        total_bytes += size
        suffix = path.suffix.lower()
        if suffix not in extensions:
            continue
        media_files += 1
        media_bytes += size
        current = by_extension.setdefault(suffix or "[none]", {"count": 0, "gb": 0.0})
        current["count"] = int(current["count"]) + 1
        current["gb"] = float(current["gb"]) + size / 1024 / 1024 / 1024

    normalized = [
        {"extension": ext, "count": int(value["count"]), "gb": round(float(value["gb"]), 3)}
        for ext, value in sorted(by_extension.items(), key=lambda item: int(item[1]["count"]), reverse=True)
    ]
    return {
        "total_files": total_files,
        "total_gb": round(total_bytes / 1024 / 1024 / 1024, 3),
        "media_files": media_files,
        "media_gb": round(media_bytes / 1024 / 1024 / 1024, 3),
        "by_extension": normalized,
    }


if __name__ == "__main__":
    main()

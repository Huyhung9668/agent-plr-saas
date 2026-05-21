from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime
from pathlib import Path

from agent_profiles import AgentProfile, get_agent_profiles
from brain import brain_summary, ingest_brain
from config import ROOT_DIR
from media_catalog import build_media_catalog
from media_text_extractor import AUDIO_VIDEO_EXTENSIONS, IMAGE_EXTENSIONS, extract_media_text

BACKUP_ROOT = Path("G:/file_backup")


def build_all_agents(*, whisper_model: str = "tiny", backup: bool = True, only: str | None = None) -> None:
    profiles = [profile for profile in get_agent_profiles() if only is None or profile.key == only]
    if not profiles:
        raise ValueError(f"No matching agent profile: {only}")

    summaries = []
    for profile in profiles:
        summaries.append(build_one_agent(profile, whisper_model=whisper_model))

    if backup and only is None:
        backup_input_dirs([profile for profile in get_agent_profiles() if profile.input_dir.is_relative_to(ROOT_DIR)])

    print(json.dumps({"agents": summaries}, ensure_ascii=False, indent=2))


def build_one_agent(profile: AgentProfile, *, whisper_model: str = "tiny") -> dict:
    if not profile.input_dir.exists():
        raise FileNotFoundError(f"Input folder missing for {profile.name}: {profile.input_dir}")

    profile.brain_dir.mkdir(parents=True, exist_ok=True)
    catalog_dir = profile.brain_dir / "media_brain_text"
    extracted_dir = profile.brain_dir / "media_extracted_text"

    print(f"\n===== {profile.name} =====")
    write_agent_profile(profile)

    print("Building media catalog...")
    catalog_stats = build_media_catalog([profile.input_dir], output_dir=catalog_dir)
    print(catalog_stats)

    print("OCR images...")
    ocr_stats = extract_media_text(mode="ocr", roots=[profile.input_dir], output_dir=extracted_dir)
    print(ocr_stats)

    print("Transcribing audio/video...")
    transcribe_stats = extract_media_text(
        mode="transcribe",
        roots=[profile.input_dir],
        output_dir=extracted_dir,
        whisper_model=whisper_model,
    )
    print(transcribe_stats)

    verify_media_attempted(profile, extracted_dir)

    print("Rebuilding brain database...")
    stats = ingest_brain(
        roots=[profile.input_dir, catalog_dir, extracted_dir],
        db_path=profile.db_path,
        rebuild=True,
    )
    summary = brain_summary(profile.db_path)
    print(stats)
    print(summary)
    return {
        "key": profile.key,
        "name": profile.name,
        "input_dir": str(profile.input_dir),
        "brain_db": str(profile.db_path),
        "brain_summary": summary,
        "catalog": {
            "output_dir": str(catalog_stats.output_dir),
            "files_scanned": catalog_stats.files_scanned,
            "cataloged_files": catalog_stats.cataloged_files,
            "catalog_files": catalog_stats.catalog_files,
            "total_gb": catalog_stats.total_gb,
        },
        "ocr": {key: value.__dict__ for key, value in ocr_stats.items()},
        "transcribe": {key: value.__dict__ for key, value in transcribe_stats.items()},
    }


def write_agent_profile(profile: AgentProfile) -> None:
    lines = [
        f"# {profile.name}",
        "",
        f"Mission: {profile.mission}",
        "",
        "## Main Brain",
        "",
        f"- Input folder: {profile.input_dir}",
        f"- Brain database: {profile.db_path}",
        "",
        "## Sub Agents",
        "",
    ]
    for subagent in profile.subagents:
        lines.extend([f"### {subagent.name}", "", subagent.job, ""])
    (profile.brain_dir / "agent_profile.md").write_text("\n".join(lines), encoding="utf-8")


def verify_media_attempted(profile: AgentProfile, extracted_dir: Path) -> None:
    manifest = extracted_dir / "manifest.jsonl"
    records = []
    if manifest.exists():
        for line in manifest.read_text(encoding="utf-8", errors="ignore").splitlines():
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    ocr_sources = {record.get("source") for record in records if record.get("kind") == "ocr"}
    transcript_sources = {record.get("source") for record in records if record.get("kind") == "transcribe"}

    images = _media_files(profile.input_dir, IMAGE_EXTENSIONS)
    audio_video = _media_files(profile.input_dir, AUDIO_VIDEO_EXTENSIONS)
    missing_ocr = [path for path in images if str(path) not in ocr_sources]
    missing_transcripts = [path for path in audio_video if str(path) not in transcript_sources]

    if missing_ocr or missing_transcripts:
        raise RuntimeError(
            f"Media extraction incomplete for {profile.name}. "
            f"Missing OCR: {len(missing_ocr)}. Missing transcripts: {len(missing_transcripts)}."
        )


def backup_input_dirs(profiles: list[AgentProfile]) -> Path:
    BACKUP_ROOT.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = BACKUP_ROOT / f"agent_input_backup_{stamp}"
    backup_dir.mkdir(parents=True, exist_ok=True)

    workspace = ROOT_DIR.resolve()
    for profile in profiles:
        source = profile.input_dir.resolve()
        if not str(source).lower().startswith(str(workspace).lower()):
            print(f"Skipping external input folder backup: {source}")
            continue
        if not source.exists():
            continue
        destination = backup_dir / profile.input_dir.name
        print(f"Moving {source} -> {destination}")
        shutil.move(str(source), str(destination))
        profile.input_dir.mkdir(parents=True, exist_ok=True)
        (profile.input_dir / ".keep").write_text("", encoding="utf-8")

    print(f"Backup complete: {backup_dir}")
    return backup_dir


def _media_files(root: Path, extensions: set[str]) -> list[Path]:
    if not root.exists():
        return []
    return [path for path in root.rglob("*") if path.is_file() and path.suffix.lower() in extensions]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--whisper-model", default="tiny")
    parser.add_argument("--no-backup", action="store_true")
    parser.add_argument("--only", choices=[profile.key for profile in get_agent_profiles()])
    args = parser.parse_args()
    build_all_agents(whisper_model=args.whisper_model, backup=not args.no_backup, only=args.only)


if __name__ == "__main__":
    main()

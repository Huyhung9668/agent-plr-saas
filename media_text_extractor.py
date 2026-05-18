from __future__ import annotations

import argparse
import hashlib
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from config import DATABASE_DIR, PLR_INBOX_DIR, SAAS_INBOX_DIR

MEDIA_TEXT_DIR = DATABASE_DIR / "media_extracted_text"

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"}
AUDIO_VIDEO_EXTENSIONS = {".mp4", ".mov", ".mp3", ".wav", ".m4a", ".avi", ".mkv", ".webm", ".wmv"}
ROOTS = [SAAS_INBOX_DIR, PLR_INBOX_DIR]


@dataclass
class ExtractStats:
    scanned: int = 0
    processed: int = 0
    skipped: int = 0
    errors: int = 0


def extract_media_text(
    *,
    mode: str = "all",
    limit: int | None = None,
    whisper_model: str = "tiny",
    roots: list[Path] | None = None,
    output_dir: Path = MEDIA_TEXT_DIR,
) -> dict[str, ExtractStats]:
    output_dir.mkdir(parents=True, exist_ok=True)
    stats = {}
    if mode in {"all", "ocr"}:
        stats["ocr"] = extract_ocr(limit=limit, roots=roots, output_dir=output_dir)
    if mode in {"all", "transcribe"}:
        stats["transcribe"] = extract_transcripts(limit=limit, whisper_model=whisper_model, roots=roots, output_dir=output_dir)
    return stats


def extract_ocr(
    limit: int | None = None,
    *,
    roots: list[Path] | None = None,
    output_dir: Path = MEDIA_TEXT_DIR,
) -> ExtractStats:
    from rapidocr_onnxruntime import RapidOCR

    ocr_dir = output_dir / "ocr"
    ocr_dir.mkdir(parents=True, exist_ok=True)
    engine = RapidOCR()
    stats = ExtractStats()
    for path in _iter_media_files(IMAGE_EXTENSIONS, roots=roots):
        stats.scanned += 1
        output = ocr_dir / f"{_stable_id(path)}.md"
        if output.exists():
            stats.skipped += 1
            continue
        if limit is not None and stats.processed >= limit:
            break
        try:
            start = time.time()
            result, _ = engine(str(path))
            lines = []
            if result:
                for item in result:
                    if len(item) >= 2 and item[1]:
                        lines.append(str(item[1]).strip())
            text = "\n".join(line for line in lines if line)
            if not text:
                text = "No OCR text detected."
            output.write_text(_media_markdown(path, "OCR image text", text), encoding="utf-8")
            _append_manifest(path, output, "ocr", "ok", round(time.time() - start, 2), output_dir=output_dir)
            stats.processed += 1
            if stats.processed % 100 == 0:
                print(f"OCR processed {stats.processed} images...")
        except Exception as error:
            output.write_text(
                _media_markdown(path, "OCR image text", f"OCR failed or image is unreadable: {error}"),
                encoding="utf-8",
            )
            _append_manifest(path, output, "ocr", f"error: {error}", 0, output_dir=output_dir)
            stats.errors += 1
    return stats


def extract_transcripts(
    limit: int | None = None,
    whisper_model: str = "tiny",
    *,
    roots: list[Path] | None = None,
    output_dir: Path = MEDIA_TEXT_DIR,
) -> ExtractStats:
    from faster_whisper import WhisperModel

    transcript_dir = output_dir / "transcripts"
    transcript_dir.mkdir(parents=True, exist_ok=True)
    model = WhisperModel(whisper_model, device="cpu", compute_type="int8")
    stats = ExtractStats()
    for path in _iter_media_files(AUDIO_VIDEO_EXTENSIONS, roots=roots):
        stats.scanned += 1
        output = transcript_dir / f"{_stable_id(path)}.md"
        if output.exists():
            stats.skipped += 1
            continue
        if limit is not None and stats.processed >= limit:
            break
        try:
            start = time.time()
            segments, info = model.transcribe(str(path), beam_size=1, vad_filter=True)
            lines = []
            for segment in segments:
                text = segment.text.strip()
                if text:
                    lines.append(f"[{segment.start:.2f}-{segment.end:.2f}] {text}")
            transcript = "\n".join(lines) if lines else "No speech detected."
            header = [
                f"Detected language: {getattr(info, 'language', 'unknown')}",
                f"Language probability: {getattr(info, 'language_probability', 0):.2f}",
                "",
                transcript,
            ]
            output.write_text(_media_markdown(path, "Audio/video transcript", "\n".join(header)), encoding="utf-8")
            _append_manifest(path, output, "transcribe", "ok", round(time.time() - start, 2), output_dir=output_dir)
            stats.processed += 1
            print(f"Transcribed {stats.processed}: {path.name}")
        except Exception as error:
            output.write_text(
                _media_markdown(path, "Audio/video transcript", f"Transcription failed or media is unreadable: {error}"),
                encoding="utf-8",
            )
            _append_manifest(path, output, "transcribe", f"error: {error}", 0, output_dir=output_dir)
            stats.errors += 1
    return stats


def _iter_media_files(extensions: set[str], roots: list[Path] | None = None) -> Iterable[Path]:
    for root in roots or ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.is_file() and path.suffix.lower() in extensions:
                yield path


def _media_markdown(path: Path, extraction_type: str, text: str) -> str:
    return f"""# {extraction_type}: {path.stem}

- Source path: {path}
- Extension: {path.suffix.lower()}
- Size MB: {round(path.stat().st_size / 1024 / 1024, 2)}

## Extracted Text

{text}
"""


def _stable_id(path: Path) -> str:
    raw = str(path).lower().encode("utf-8", errors="ignore")
    return hashlib.sha1(raw).hexdigest()


def _append_manifest(source: Path, output: Path, kind: str, status: str, seconds: float, *, output_dir: Path = MEDIA_TEXT_DIR) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    record = {
        "source": str(source),
        "output": str(output),
        "kind": kind,
        "status": status,
        "seconds": seconds,
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    with (output_dir / "manifest.jsonl").open("a", encoding="utf-8") as file:
        file.write(json.dumps(record, ensure_ascii=False) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["all", "ocr", "transcribe"], default="all")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--whisper-model", default="tiny")
    parser.add_argument("--root", action="append", default=[])
    parser.add_argument("--output-dir", default=str(MEDIA_TEXT_DIR))
    args = parser.parse_args()
    roots = [Path(item) for item in args.root] if args.root else None
    stats = extract_media_text(
        mode=args.mode,
        limit=args.limit,
        whisper_model=args.whisper_model,
        roots=roots,
        output_dir=Path(args.output_dir),
    )
    for name, value in stats.items():
        print(name, value)


if __name__ == "__main__":
    main()

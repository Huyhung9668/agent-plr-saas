from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from config import DATABASE_DIR, PLR_INBOX_DIR, SAAS_INBOX_DIR

MEDIA_BRAIN_TEXT_DIR = DATABASE_DIR / "media_brain_text"

MEDIA_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".gif",
    ".ico",
    ".psd",
    ".mp4",
    ".mov",
    ".mp3",
    ".wav",
    ".swf",
    ".ttf",
    ".woff",
    ".woff2",
    ".eot",
    ".atn",
    ".download",
    ".db",
    "",
}

ROOTS = [SAAS_INBOX_DIR, PLR_INBOX_DIR]


@dataclass
class MediaCatalogStats:
    output_dir: Path
    files_scanned: int
    cataloged_files: int
    catalog_files: int
    total_gb: float


def build_media_catalog(
    roots: list[Path] | None = None,
    *,
    output_dir: Path = MEDIA_BRAIN_TEXT_DIR,
    batch_size: int = 500,
) -> MediaCatalogStats:
    roots = roots or ROOTS
    output_dir.mkdir(parents=True, exist_ok=True)
    for old_file in output_dir.glob("media_catalog_*.md"):
        old_file.unlink()

    records: list[str] = []
    files_scanned = 0
    cataloged = 0
    total_bytes = 0
    catalog_index = 1

    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            files_scanned += 1
            suffix = path.suffix.lower()
            if suffix not in MEDIA_EXTENSIONS:
                continue
            total_bytes += path.stat().st_size
            records.append(_record_for(path, root))
            cataloged += 1
            if len(records) >= batch_size:
                _write_catalog(output_dir, catalog_index, records)
                catalog_index += 1
                records = []

    if records:
        _write_catalog(output_dir, catalog_index, records)

    catalog_files = len(list(output_dir.glob("media_catalog_*.md")))
    return MediaCatalogStats(
        output_dir=output_dir,
        files_scanned=files_scanned,
        cataloged_files=cataloged,
        catalog_files=catalog_files,
        total_gb=round(total_bytes / 1024 / 1024 / 1024, 2),
    )


def _record_for(path: Path, root: Path) -> str:
    stat = path.stat()
    relative = _safe_relative(path, root)
    product = _product_folder(path, root)
    asset_type = _asset_type(path)
    keywords = _keywords(path)
    size_mb = round(stat.st_size / 1024 / 1024, 2)
    return f"""## Media Asset: {path.stem}

- Asset type: {asset_type}
- Product/pack: {product}
- Extension: {path.suffix.lower() or "[none]"}
- Size MB: {size_mb}
- Source path: {path}
- Relative path: {relative}
- Search keywords: {keywords}
- Brain note: This is a media/design/source asset catalog record. Use it to know the asset exists and where to find it. It is not a transcript or OCR extraction.
"""


def _write_catalog(output_dir: Path, index: int, records: list[str]) -> None:
    path = output_dir / f"media_catalog_{index:04d}.md"
    path.write_text("# Media Brain Catalog\n\n" + "\n".join(records), encoding="utf-8")


def _safe_relative(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def _product_folder(path: Path, root: Path) -> str:
    try:
        relative = path.relative_to(root)
    except ValueError:
        return path.parent.name
    return relative.parts[0] if len(relative.parts) > 1 else path.parent.name


def _asset_type(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".mp4", ".mov", ".mp3", ".wav"}:
        return "video/audio"
    if suffix in {".png", ".jpg", ".jpeg", ".webp", ".gif", ".ico"}:
        return "image/graphic"
    if suffix == ".psd":
        return "photoshop/design source"
    if suffix in {".ttf", ".woff", ".woff2", ".eot"}:
        return "font"
    if suffix == ".swf":
        return "legacy flash asset"
    if suffix == ".atn":
        return "photoshop action"
    return "binary/support asset"


def _keywords(path: Path) -> str:
    raw = " ".join([path.stem, path.parent.name, path.suffix.lower()])
    words = re.findall(r"[A-Za-z0-9]+", raw)
    return ", ".join(dict.fromkeys(word.lower() for word in words if len(word) > 1))


if __name__ == "__main__":
    stats = build_media_catalog()
    print(stats)

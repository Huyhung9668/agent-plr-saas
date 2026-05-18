from __future__ import annotations

import shutil
from pathlib import Path

from config import NEEDS_LICENSE_DIR, PLR_DIR, PLR_INBOX_DIR, SUPPORTED_EXTENSIONS


CATEGORY_KEYWORDS = {
    "AI": ["ai", "chatgpt", "gpt", "prompt", "automation"],
    "Marketing": ["marketing", "affiliate", "traffic", "funnel", "email", "seo", "ads"],
    "Planner": ["planner", "journal", "tracker", "calendar"],
    "Kids-Story": ["kids", "children", "story", "coloring", "activity"],
    "Etsy": ["etsy", "printable", "canva", "template"],
    "Self-Help": ["self", "mindset", "habit", "productivity", "confidence"],
    "Health": ["health", "fitness", "weight", "diet", "wellness"],
    "Business": ["business", "startup", "agency", "client", "entrepreneur"],
}

LICENSE_KEYWORDS = [
    "license",
    "licence",
    "rights",
    "plr",
    "mrr",
    "resell",
    "private label",
]


def import_downloaded_files(source_dir: Path, copy_mode: bool = True) -> list[dict]:
    source_dir = source_dir.expanduser().resolve()
    if not source_dir.exists():
        raise FileNotFoundError(f"Source folder not found: {source_dir}")

    PLR_DIR.mkdir(parents=True, exist_ok=True)
    NEEDS_LICENSE_DIR.mkdir(parents=True, exist_ok=True)

    imported = []
    for path in source_dir.iterdir():
        if not path.is_file() or path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue
        category = guess_category(path.name)
        target_root = PLR_DIR / category if has_license_hint(path.name) else NEEDS_LICENSE_DIR / category
        target_root.mkdir(parents=True, exist_ok=True)
        target = unique_path(target_root / path.name)

        if copy_mode:
            shutil.copy2(path, target)
            action = "copied"
        else:
            shutil.move(str(path), str(target))
            action = "moved"

        imported.append(
            {
                "source": str(path),
                "target": str(target),
                "category": category,
                "license_hint_found": has_license_hint(path.name),
                "action": action,
            }
        )
    return imported


def import_plr_inbox(move_mode: bool = True) -> list[dict]:
    PLR_INBOX_DIR.mkdir(parents=True, exist_ok=True)
    PLR_DIR.mkdir(parents=True, exist_ok=True)
    NEEDS_LICENSE_DIR.mkdir(parents=True, exist_ok=True)

    imported = []
    for path in PLR_INBOX_DIR.iterdir():
        if not path.is_file() or path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        category = guess_category(path.name)
        target_root = PLR_DIR / category if has_license_hint(path.name) else NEEDS_LICENSE_DIR / category
        target_root.mkdir(parents=True, exist_ok=True)
        target = unique_path(target_root / path.name)

        if move_mode:
            shutil.move(str(path), str(target))
            action = "moved"
        else:
            shutil.copy2(path, target)
            action = "copied"

        imported.append(
            {
                "source": str(path),
                "target": str(target),
                "category": category,
                "license_hint_found": has_license_hint(path.name),
                "action": action,
            }
        )
    return imported


def guess_category(name: str) -> str:
    lower = name.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in lower for keyword in keywords):
            return category
    return "Unsorted"


def has_license_hint(name: str) -> bool:
    lower = name.lower()
    return any(keyword in lower for keyword in LICENSE_KEYWORDS)


def unique_path(path: Path) -> Path:
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    parent = path.parent
    counter = 2
    while True:
        candidate = parent / f"{stem}-{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def default_downloads_dir() -> Path:
    return Path.home() / "Downloads"

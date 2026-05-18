from __future__ import annotations

import shutil
from pathlib import Path

from config import SAAS_DIR, SAAS_INBOX_DIR


SAAS_SUPPORTED_EXTENSIONS = {
    ".txt",
    ".md",
    ".pdf",
    ".docx",
    ".csv",
    ".xlsx",
    ".json",
    ".zip",
    ".rar",
    ".7z",
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".html",
    ".htm",
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
}

KEYWORD_FOLDERS = {
    "ideas": ["idea", "concept", "brainstorm", "saas idea"],
    "specs": ["spec", "requirements", "prd", "feature", "workflow", "mvp"],
    "mockups": ["mockup", "wireframe", "screenshot", "ui", "ux", "design"],
    "code_samples": ["code", "script", "bot", "api", "sample", "prototype"],
    "pricing": ["pricing", "price", "tier", "ltd", "plan"],
    "validation": ["feedback", "beta", "survey", "validation", "customer"],
    "whitelabel": ["white", "whitelabel", "agency", "license", "client"],
    "research": ["research", "report", "market", "competitor", "crypto", "alert"],
}

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
CODE_EXTENSIONS = {".py", ".js", ".ts", ".tsx", ".jsx", ".html", ".htm"}
DATA_EXTENSIONS = {".csv", ".xlsx", ".json"}


def import_saas_inbox(move_mode: bool = True) -> list[dict]:
    SAAS_INBOX_DIR.mkdir(parents=True, exist_ok=True)
    _ensure_saas_folders()

    imported = []
    for path in SAAS_INBOX_DIR.iterdir():
        if not path.is_file() or path.suffix.lower() not in SAAS_SUPPORTED_EXTENSIONS:
            continue

        folder = guess_saas_folder(path)
        target_root = SAAS_DIR / folder
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
                "folder": folder,
                "action": action,
            }
        )
    return imported


def guess_saas_folder(path: Path) -> str:
    suffix = path.suffix.lower()
    lower = path.name.lower()

    if suffix in IMAGE_EXTENSIONS:
        return "mockups"
    if suffix in CODE_EXTENSIONS:
        return "code_samples"
    if suffix in DATA_EXTENSIONS:
        return "research"

    for folder, keywords in KEYWORD_FOLDERS.items():
        if any(keyword in lower for keyword in keywords):
            return folder
    return "research"


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


def _ensure_saas_folders() -> None:
    for folder in [
        "ideas",
        "specs",
        "mockups",
        "code_samples",
        "research",
        "pricing",
        "validation",
        "whitelabel",
    ]:
        (SAAS_DIR / folder).mkdir(parents=True, exist_ok=True)

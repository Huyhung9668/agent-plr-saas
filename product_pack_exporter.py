from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from config import EXPORTS_DIR
from funnel_writer import build_offer_funnel


def export_product_pack(idea_context: str, product_name: str = "AI PLR Rebrand Kit") -> Path:
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    folder_name = f"{_safe_name(product_name)}-{stamp}"
    pack_dir = EXPORTS_DIR / folder_name
    pack_dir.mkdir(parents=True, exist_ok=True)

    files = build_offer_funnel(idea_context)
    for filename, content in files.items():
        (pack_dir / filename).write_text(content, encoding="utf-8")

    manifest = {
        "product_name": product_name,
        "created_at": stamp,
        "files": sorted(files.keys()),
    }
    (pack_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return pack_dir


def _safe_name(name: str) -> str:
    cleaned = "".join(char if char.isalnum() else "-" for char in name.strip())
    while "--" in cleaned:
        cleaned = cleaned.replace("--", "-")
    return cleaned.strip("-") or "product-pack"

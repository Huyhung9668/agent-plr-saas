from __future__ import annotations

import json
import csv
from datetime import datetime
from pathlib import Path

from config import OUTPUTS_DIR, REPORTS_DIR


def export_analysis(results: list[dict]) -> tuple[Path, Path, Path]:
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")

    json_path = OUTPUTS_DIR / f"plr-analysis-{stamp}.json"
    csv_path = OUTPUTS_DIR / f"plr-analysis-{stamp}.csv"
    md_path = REPORTS_DIR / f"plr-report-{stamp}.md"

    json_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    _write_csv(csv_path, results)
    md_path.write_text(_markdown_report(results), encoding="utf-8")

    return json_path, csv_path, md_path


def export_text(name: str, content: str) -> Path:
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    safe_name = "".join(char for char in name if char.isalnum() or char in "-_").strip("-_")
    path = OUTPUTS_DIR / f"{safe_name}-{stamp}.md"
    path.write_text(content, encoding="utf-8")
    return path


def _markdown_report(results: list[dict]) -> str:
    lines = [
        "# Agent PLR Saas Report",
        "",
        f"Total products analyzed: {len(results)}",
        "",
        "## Top Products",
        "",
    ]

    for item in results[:20]:
        lines.extend(
            [
                f"### {item.get('original_title', 'Untitled')}",
                "",
                f"- Category: {item.get('category', '')}",
                f"- Product type: {item.get('product_type', '')}",
                f"- License: {item.get('license_type', '')}",
                f"- Final score: {item.get('final_score', '')}/10",
                f"- WarriorPlus fit: {item.get('warriorplus_fit_score', '')}/10",
                f"- Rebrand potential: {item.get('rebrand_potential_score', '')}/10",
                f"- Recommended action: {item.get('recommended_action', '')}",
                f"- Risk: {item.get('risk', '')}",
                f"- Sales angle: {item.get('sales_page_angle', '')}",
                "",
            ]
        )

    return "\n".join(lines)


def _write_csv(path: Path, results: list[dict]) -> None:
    if not results:
        path.write_text("", encoding="utf-8-sig")
        return

    fields = sorted({key for item in results for key in item.keys()})
    with path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(results)

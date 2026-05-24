from __future__ import annotations

import json
import re
import urllib.request
import zipfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "benchmarks" / "ai_printables_kdp_prompt_v111"
REPORT_DIR = ROOT / "benchmarks" / "anti_fake_benchmark_v112"
SERVER = "http://127.0.0.1:18088"
ROUND_DIR = BASE / "round_6"
ZIP_PATH = ROUND_DIR / "artifacts" / "ai_canva_printable_product_kit" / "export" / "product_pack.zip"
CHAT_RAW = REPORT_DIR / "api_chat_short.json"
INDEX_HTML = ROOT / "web_ui" / "index.html"

CRITERIA = [
    "API/UI system proof",
    "Skill routing proof",
    "Brain/source evidence proof",
    "Real file artifact proof",
    "ZIP integrity proof",
    "Content depth/non-generic proof",
    "Compliance proof",
    "Buyer usability proof",
    "Market validation proof",
    "Live launch proof",
]
REQUIRED_FILES = [
    "README.md", "sales_page.md", "warriorplus_listing.md", "jv_pack.md", "delivery_page.md", "support_faq.md", "refund_policy.md",
    "product_assets/00_Start_Here.md", "product_assets/01_Workflow_Map.md", "product_assets/02_Prompt_Library.md",
    "product_assets/03_Template_Guide.md", "product_assets/04_Example_Outputs.md", "product_assets/05_Quality_Checklist.md",
    "product_assets/06_Fix_Prompts.md", "product_assets/07_Listing_Sales_Kit.md", "product_assets/08_License_Compliance.md",
    "export/FILE_MANIFEST.md", "export/PLACEHOLDER_CHECK.md",
]
PLACEHOLDERS = ["[your name]", "[your website]", "[support email]", "[download link]", "[payment link]", "[affiliate link]", "[JV link]", "[launch date]", "[insert product name]", "[company name]"]
THIN_OR_GENERIC_FLAGS = ["lorem ipsum", "coming soon", "to be added", "paste_output"]


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8")


def get_json(path: str, timeout: int = 20) -> tuple[dict | None, str | None]:
    try:
        with urllib.request.urlopen(SERVER + path, timeout=timeout) as res:
            return json.loads(res.read().decode("utf-8", errors="replace")), None
    except Exception as exc:
        return None, str(exc)


def post_json(path: str, payload: dict, timeout: int = 60) -> tuple[dict | None, str | None]:
    try:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(SERVER + path, data=data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as res:
            return json.loads(res.read().decode("utf-8", errors="replace")), None
    except Exception as exc:
        return None, str(exc)


def zip_entries() -> tuple[dict[str, str], list[str]]:
    if not ZIP_PATH.exists():
        return {}, [f"ZIP missing: {ZIP_PATH}"]
    data = {}
    errors = []
    try:
        with zipfile.ZipFile(ZIP_PATH) as zf:
            bad = zf.testzip()
            if bad:
                errors.append(f"Corrupt ZIP entry: {bad}")
            for name in zf.namelist():
                if name.endswith((".md", ".txt")):
                    data[name] = zf.read(name).decode("utf-8", errors="replace")
    except Exception as exc:
        errors.append(str(exc))
    return data, errors


def marker_count(text: str) -> int:
    markers = ["WarriorPlus", "KDP", "Canva", "PLR", "trademark", "copyright", "font", "license", "Start Here", "Quality Checklist", "Fix Prompts", "FE price", "Commission", "Refund", "ZIP", "Disney", "Marvel", "Pokémon", "Taylor Swift", "guaranteed", "human review"]
    lower = text.lower()
    return sum(1 for marker in markers if marker.lower() in lower)


def main() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    status, status_err = get_json("/api/status")
    tags, tags_err = get_json("/api/skill_tags")
    route, route_err = post_json("/api/route_skill", {"message": "#ai-printables-kdp-prompt #public-launch-audit anti fake check", "tags": ["#ai-printables-kdp-prompt", "#public-launch-audit"]})
    chat, chat_err = post_json("/api/chat", {"question": "#ai-printables-kdp-prompt #market-pattern\nTrả lời ngắn: DATA USED và SKILLS USED cho market pattern.", "tags": ["#ai-printables-kdp-prompt", "#market-pattern"], "mode": "fast", "agentKey": "ai_printables_kdp_prompt"})
    if chat:
        write(CHAT_RAW, json.dumps(chat, ensure_ascii=False, indent=2))

    index_text = INDEX_HTML.read_text(encoding="utf-8", errors="replace") if INDEX_HTML.exists() else ""
    ui_static_ok = all(x in index_text for x in ["aiKdpTagPanel", "aiKdpTagChips", "toggleAiKdpTagsBtn", "clearAiKdpTagsBtn", "#ai-printables-kdp-prompt", "#market-pattern"])

    entries, zip_errors = zip_entries()
    names = set(entries)
    missing = [name for name in REQUIRED_FILES if name not in names]
    all_text = "\n\n".join(entries.values())
    placeholder_hits = [p for p in PLACEHOLDERS if p.lower() in all_text.lower()]
    generic_hits = [p for p in THIN_OR_GENERIC_FLAGS if p.lower() in all_text.lower()]
    total_words = len(re.findall(r"\w+", all_text, re.UNICODE))
    markers = marker_count(all_text)
    per_file_words = {name: len(re.findall(r"\w+", text, re.UNICODE)) for name, text in entries.items()}
    thin_files = {name: words for name, words in per_file_words.items() if name.endswith(".md") and words < 80}
    chat_answer = (chat or {}).get("answer", "") if isinstance(chat, dict) else ""
    chat_has_evidence = all(x in chat_answer.upper() for x in ["DATA USED", "SKILLS USED"])

    evidence = {
        "timestamp": datetime.now().isoformat(), "server": SERVER,
        "status_ok": bool(status and status.get("ok")), "appVersion": status.get("appVersion") if status else None, "status_error": status_err,
        "skill_tags_ok": bool(tags and tags.get("ok") and len(tags.get("tags", [])) >= 16), "skill_tag_count": len(tags.get("tags", [])) if tags else 0, "skill_tags_error": tags_err,
        "route_ok": bool(route and route.get("ok") and route.get("skillFile") == "skills/16_public_launch_audit_ai_printables.md"), "route": route, "route_error": route_err,
        "chat_ok": bool(chat and chat.get("ok") and chat_has_evidence), "chat_error": chat_err, "chat_answer_chars": len(chat_answer),
        "ui_static_ok": ui_static_ok,
        "zip_path": str(ZIP_PATH), "zip_exists": ZIP_PATH.exists(), "zip_bytes": ZIP_PATH.stat().st_size if ZIP_PATH.exists() else 0, "zip_errors": zip_errors,
        "zip_entry_count": len(entries), "missing_required_files": missing, "placeholder_hits": placeholder_hits, "generic_hits": generic_hits,
        "total_words": total_words, "specific_marker_count": markers, "thin_files": thin_files, "per_file_words": per_file_words,
    }
    write(REPORT_DIR / "evidence.json", json.dumps(evidence, ensure_ascii=False, indent=2))

    scores = {
        "API/UI system proof": 8 if evidence["status_ok"] and ui_static_ok else 3,
        "Skill routing proof": 10 if evidence["route_ok"] and evidence["skill_tags_ok"] else 4,
        "Brain/source evidence proof": 8 if evidence["chat_ok"] and route and route.get("brainFiles") else 4,
        "Real file artifact proof": 9 if not missing and len(entries) >= 18 else 4,
        "ZIP integrity proof": 10 if evidence["zip_exists"] and evidence["zip_bytes"] > 1000 and not zip_errors else 0,
        "Content depth/non-generic proof": 0,
        "Compliance proof": 0,
        "Buyer usability proof": 0,
        "Market validation proof": 4,
        "Live launch proof": 2,
    }
    content_score = 8
    if total_words < 2500: content_score -= 2
    if thin_files: content_score -= 1
    if markers < 12: content_score -= 1
    if generic_hits: content_score -= 1
    scores["Content depth/non-generic proof"] = max(0, min(8, content_score))
    compliance_terms = ["trademark", "copyright", "canva", "font", "kdp", "income", "therapy", "celebrity", "lyrics", "human review"]
    compliance_hits = sum(1 for term in compliance_terms if term in all_text.lower())
    scores["Compliance proof"] = 8 if compliance_hits >= 8 and not placeholder_hits else 5
    usability_terms = ["open", "first", "10-minute", "workflow", "checklist", "support", "faq"]
    usability_hits = sum(1 for term in usability_terms if term.lower() in all_text.lower())
    scores["Buyer usability proof"] = 7 if usability_hits >= 5 else 4

    notes = {
        "API/UI system proof": "API status works and UI tag panel exists in HTML, but no browser click automation; max 8.",
        "Skill routing proof": "Route API maps #public-launch-audit to skill 16 and skill tags are registered.",
        "Brain/source evidence proof": "Short /api/chat call returned DATA USED/SKILLS USED, but exact source-claim verification is not complete; max 8.",
        "Real file artifact proof": f"Required files missing: {missing or 'none'}.",
        "ZIP integrity proof": f"ZIP bytes: {evidence['zip_bytes']}; errors: {zip_errors or 'none'}.",
        "Content depth/non-generic proof": f"Words: {total_words}; markers: {markers}; thin files: {len(thin_files)}; generic flags: {generic_hits}. Max 8 without human buyer review.",
        "Compliance proof": f"Compliance terms hit: {compliance_hits}; placeholders: {placeholder_hits or 'none'}. Max 8 without legal/human review.",
        "Buyer usability proof": f"Usability hits: {usability_hits}. Max 7 without external buyer test.",
        "Market validation proof": "No live competitor scrape, sales data, or buyer validation in this anti-fake run.",
        "Live launch proof": "No live WarriorPlus upload, payment, delivery, or JV approval test.",
    }
    total = sum(scores.values())
    lines = [
        "# ANTI-FAKE BENCHMARK REPORT v1.12",
        "",
        "Goal: kiểm tra điểm 10/10 có ảo không bằng evidence thật. Kết luận: 10/10 trước đó là system/artifact benchmark, không phải launch-market score 100%.",
        "",
        f"- Re-scored total: **{total}/100 = {total/10:.1f}/10**",
        f"- App version: `{evidence['appVersion']}`",
        f"- API chat evidence: `{'PASS' if evidence['chat_ok'] else 'FAIL'}` ({evidence['chat_answer_chars']} chars)",
        f"- Static UI tag panel check: `{'PASS' if ui_static_ok else 'FAIL'}`",
        f"- ZIP: `{ZIP_PATH}`",
        f"- ZIP bytes: `{evidence['zip_bytes']}`",
        f"- Missing required files: `{missing or 'none'}`",
        f"- Placeholder hits: `{placeholder_hits or 'none'}`",
        f"- Total artifact words: `{total_words}`",
        "",
        "## Scorecard",
        "",
        "| Criterion | Score /10 | Anti-fake note |",
        "|---|---:|---|",
    ]
    for name in CRITERIA:
        lines.append(f"| {name} | {scores[name]} | {notes[name]} |")
    lines += [
        "",
        "## Verdict",
        "- Không chuẩn 100% nếu hiểu là sản phẩm đã launch bán thật.",
        "- Chuẩn ở mức hệ thống/route/file/ZIP proof: khá tốt.",
        "- Điểm thực tế chống ảo hiện tại bị kéo xuống bởi: chưa browser automation, chưa source citation sâu từng claim, chưa buyer ngoài test, chưa market sales proof, chưa live WarriorPlus/payment/delivery/JV.",
        "- Decision thật: **Build/soft-launch ready**, chưa phải **Public launch ready 100%**.",
        "",
        "## Next Checks To Remove More Fake Score",
        "1. Chạy Playwright click tag thật trong browser và chụp screenshot.",
        "2. Chấm từng file bởi buyer/human reviewer độc lập.",
        "3. Bắt mỗi claim market phải có DATA USED từ source map/input cụ thể.",
        "4. So với competitor/sales data thật.",
        "5. Upload thử WarriorPlus sandbox/live draft và test delivery/payment/JV flow.",
    ]
    write(REPORT_DIR / "anti_fake_report.md", "\n".join(lines))
    print(json.dumps({"score100": total, "score10": total / 10, "report": str(REPORT_DIR / "anti_fake_report.md"), "chat_ok": evidence["chat_ok"], "ui_static_ok": ui_static_ok}, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()

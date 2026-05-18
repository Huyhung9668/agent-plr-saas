from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUTS = [ROOT / "database" / "agent_brains", ROOT / "playbooks"]
DEFAULT_OUTPUT = ROOT / "database" / "clean_chunks.jsonl"

TOPIC_RULES = {
    "sales_page": ("sales page", "headline", "copywriting", "objection", "cta", "faq"),
    "jv_manager": ("jv", "affiliate", "outreach", "review access", "commission", "swipe"),
    "warriorplus_funnel": ("warriorplus", "oto", "order bump", "funnel", "frontend", "fe "),
    "saas_upgrade": ("saas", "membership", "whitelabel", "mvp", "recurring"),
    "email_funnel": ("email", "subject line", "sequence", "campaign", "lead magnet"),
    "license_risk": ("license", "plr rights", "mrr", "resell", "copyright", "human review"),
    "quality_control": ("checklist", "quality", "risk", "compliance", "refund", "claim"),
    "free_traffic": ("facebook", "youtube", "quora", "medium", "traffic", "group post"),
    "plr_rebrand": ("plr", "rebrand", "rewrite", "private label", "resell rights"),
    "build_product": ("product", "template", "planner", "workflow", "bonus", "kit"),
}

ROLE_BY_TOPIC = {
    "sales_page": "sales_page_copywriter",
    "jv_manager": "jv_manager",
    "saas_upgrade": "saas_architect",
    "license_risk": "risk_checker",
    "quality_control": "risk_checker",
    "free_traffic": "traffic_strategist",
}

USE_CASE_RULES = {
    "analyze_offer": ("score", "analyze", "decision", "buyer"),
    "analyze_plr": ("license", "plr", "source", "risk"),
    "upgrade_kit": ("upgrade", "productize", "kit", "workflow"),
    "create_product_assets": ("file", "asset", "planner", "checklist"),
    "write_sales_page": ("sales page", "headline", "cta", "faq"),
    "create_funnel": ("funnel", "oto", "bump", "commission"),
    "build_jv_pack": ("jv", "affiliate", "outreach", "swipe"),
    "build_listing": ("listing", "warriorplus", "short description"),
    "create_delivery_page": ("delivery", "thank you", "download", "support"),
    "saas_upgrade": ("saas", "mvp", "membership", "whitelabel"),
    "export_zip": ("zip", "export", "package", "deliver"),
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Clean and label local agent chunks.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--min-chars", type=int, default=120)
    parser.add_argument("inputs", nargs="*", default=[str(path) for path in DEFAULT_INPUTS])
    args = parser.parse_args()

    records = []
    seen_hashes: set[str] = set()
    for raw in args.inputs:
        path = Path(raw)
        for source_file, text in iter_sources(path):
            for chunk in split_text(text):
                cleaned = clean_text(chunk)
                if len(cleaned) < args.min_chars or is_noise(cleaned):
                    continue
                digest = hashlib.sha1(cleaned.lower().encode("utf-8")).hexdigest()
                if digest in seen_hashes:
                    continue
                seen_hashes.add(digest)
                records.append(label_record(digest, cleaned, source_file))

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(f"Wrote {len(records)} clean chunks to {output}")


def iter_sources(path: Path):
    if not path.exists():
        return
    if path.is_file():
        yield from iter_file(path)
        return
    for item in path.rglob("*"):
        if item.is_file():
            yield from iter_file(item)


def iter_file(path: Path):
    suffix = path.suffix.lower()
    if suffix in {".txt", ".md", ".jsonl", ".csv"}:
        try:
            yield str(path), path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return
    elif suffix in {".sqlite", ".db"}:
        yield from iter_sqlite(path)


def iter_sqlite(path: Path):
    try:
        conn = sqlite3.connect(path)
    except sqlite3.Error:
        return
    with conn:
        tables = [row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")]
        for table in tables:
            try:
                columns = [row[1] for row in conn.execute(f"PRAGMA table_info({table})")]
            except sqlite3.Error:
                continue
            text_columns = [col for col in columns if col.lower() in {"text", "content", "chunk", "body", "excerpt", "summary"}]
            title_columns = [col for col in columns if col.lower() in {"title", "source_path", "source", "file"}]
            if not text_columns:
                continue
            select_cols = text_columns + title_columns[:2]
            query = f"SELECT {', '.join(select_cols)} FROM {table}"
            try:
                for row in conn.execute(query):
                    text = "\n".join(str(value or "") for value in row[: len(text_columns)])
                    source = " | ".join(str(value or "") for value in row[len(text_columns) :]) or str(path)
                    yield f"{path}:{table}:{source}", text
            except sqlite3.Error:
                continue


def split_text(text: str, max_chars: int = 1800):
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", text or "") if part.strip()]
    current = ""
    for paragraph in paragraphs:
        if len(current) + len(paragraph) > max_chars and current:
            yield current
            current = paragraph
        else:
            current = f"{current}\n\n{paragraph}".strip()
    if current:
        yield current


def clean_text(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text or "")
    text = re.sub(r"\b\d{1,2}:\d{2}(?::\d{2})?\b", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def is_noise(text: str) -> bool:
    if len(set(text)) < 12:
        return True
    alpha_ratio = sum(char.isalpha() for char in text) / max(len(text), 1)
    if alpha_ratio < 0.35:
        return True
    low = text.lower()
    noise_markers = ("__macosx", "thumbs.db", "zoom meeting", "downloaded from", "copyright ©")
    return any(marker in low for marker in noise_markers)


def label_record(chunk_id: str, text: str, source_file: str) -> dict:
    low = text.lower()
    topic = best_match(low, TOPIC_RULES, "build_product")
    role = ROLE_BY_TOPIC.get(topic, "product_builder")
    use_case = best_match(low, USE_CASE_RULES, "upgrade_kit")
    return {
        "chunk_id": chunk_id,
        "text": text,
        "topic": topic,
        "role": role,
        "use_case": use_case,
        "quality_score": quality_score(text, topic, use_case),
        "source_file": source_file,
    }


def best_match(text: str, rules: dict[str, tuple[str, ...]], default: str) -> str:
    scores = {name: sum(1 for marker in markers if marker in text) for name, markers in rules.items()}
    best, score = max(scores.items(), key=lambda item: item[1])
    return best if score else default


def quality_score(text: str, topic: str, use_case: str) -> int:
    score = 5
    if len(text) > 400:
        score += 1
    if any(marker in text.lower() for marker in ("checklist", "workflow", "template", "score", "step")):
        score += 2
    if topic in {"sales_page", "jv_manager", "warriorplus_funnel", "license_risk"}:
        score += 1
    if use_case in {"write_sales_page", "build_jv_pack", "create_funnel", "saas_upgrade"}:
        score += 1
    return max(1, min(score, 10))


if __name__ == "__main__":
    main()

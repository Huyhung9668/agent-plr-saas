from __future__ import annotations

import json
import re
import sqlite3
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

from brain import BrainStats, brain_summary, ingest_brain, search_brain
from config import DATABASE_DIR, FILE_BACKUP_DIR, ROOT_DIR

CASE_STUDY_BRAIN_DIR = DATABASE_DIR / "agent_brains" / "case_study"
CASE_STUDY_DB_PATH = CASE_STUDY_BRAIN_DIR / "case_study_brain.sqlite"
TRAINING_MANIFEST_PATH = CASE_STUDY_BRAIN_DIR / "case_study_training_manifest.json"
PATTERN_LIBRARY_PATH = CASE_STUDY_BRAIN_DIR / "case_study_pattern_library.json"
TRAINING_REPORT_PATH = CASE_STUDY_BRAIN_DIR / "CASE_STUDY_TRAINING_REPORT.md"

CATEGORY_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("01_Product_Research", ("research", "market", "niche", "competitor", "idea", "etsy", "udemy")),
    ("02_Sales_Page", ("sales", "sale page", "salespage", "copy", "headline", "landing")),
    ("03_Email_Swipes", ("email", "swipe", "sequence", "subject", "newsletter")),
    ("04_WarriorPlus_JV", ("warriorplus", "jv", "affiliate", "commission", "review access")),
    ("05_Funnel_OTO", ("funnel", "oto", "bump", "downsell", "upsell", "backend")),
    ("06_PLR_License", ("plr", "mrr", "resell", "license", "rights", "commercial")),
    ("07_SaaS_Ideas", ("saas", "software", "tool", "app", "dashboard", "mvp")),
    ("08_KDP_Printables", ("kdp", "printable", "planner", "journal", "interior", "canva")),
    ("09_Kids_Printables", ("kids", "children", "coloring", "worksheet", "preschool", "learning")),
    ("10_Case_Studies", ("case study", "casestudy", "example", "analysis", "breakdown", "transcript")),
)


@dataclass(frozen=True)
class CaseStudyIngestResult:
    status: str
    source_root: str
    db_path: str
    max_files: int | None
    scanned_files: int
    ingested_documents: int
    skipped_files: int
    chunks: int
    errors: int
    manifest_path: str


def case_study_roots() -> list[Path]:
    return [FILE_BACKUP_DIR]


def ingest_case_study_brain(*, rebuild: bool = False, max_files: int | None = None) -> CaseStudyIngestResult:
    CASE_STUDY_BRAIN_DIR.mkdir(parents=True, exist_ok=True)
    source_root = FILE_BACKUP_DIR
    if not source_root.exists():
        result = CaseStudyIngestResult(
            status="MISSING_SOURCE_ROOT",
            source_root=str(source_root),
            db_path=str(CASE_STUDY_DB_PATH),
            max_files=max_files,
            scanned_files=0,
            ingested_documents=0,
            skipped_files=0,
            chunks=0,
            errors=0,
            manifest_path=str(TRAINING_MANIFEST_PATH),
        )
        _write_manifest(result, notes=["Source folder does not exist on this machine."])
        return result

    stats: BrainStats = ingest_brain(
        roots=[source_root],
        db_path=CASE_STUDY_DB_PATH,
        rebuild=rebuild,
        max_files=max_files,
    )
    result = CaseStudyIngestResult(
        status="CREATED" if stats.ingested_documents or CASE_STUDY_DB_PATH.exists() else "EMPTY",
        source_root=str(source_root),
        db_path=str(stats.db_path),
        max_files=max_files,
        scanned_files=stats.scanned_files,
        ingested_documents=stats.ingested_documents,
        skipped_files=stats.skipped_files,
        chunks=stats.chunks,
        errors=stats.errors,
        manifest_path=str(TRAINING_MANIFEST_PATH),
    )
    _write_manifest(result, notes=training_system_notes())
    return result


def case_study_summary() -> dict:
    summary = brain_summary(CASE_STUDY_DB_PATH)
    summary["source_root"] = str(FILE_BACKUP_DIR)
    summary["source_exists"] = FILE_BACKUP_DIR.exists()
    summary["manifest_path"] = str(TRAINING_MANIFEST_PATH)
    summary["categories"] = category_counts()
    summary["training_mode"] = "RAG / searchable case-study memory, not model-weight fine-tuning"
    return summary


def search_case_study_brain(query: str, *, limit: int = 8) -> list[dict]:
    hits = search_brain(query, limit=limit, db_path=CASE_STUDY_DB_PATH)
    for hit in hits:
        hit["category"] = classify_source(str(hit.get("source_path", "")), str(hit.get("title", "")))
        hit["pattern_score"] = score_case_study_hit(hit)
        hit["patterns"] = detect_patterns(str(hit.get("text", "")), str(hit.get("title", "")))
    return hits


def score_case_study_hit(hit: dict) -> int:
    text = f"{hit.get('title', '')} {hit.get('source_path', '')} {hit.get('text', '')[:3000]}".lower()
    score = 20
    marker_groups = {
        "product": ("product", "bundle", "pack", "template", "worksheet", "planner", "printable"),
        "sales": ("headline", "sales page", "offer", "cta", "guarantee", "faq", "bonus"),
        "launch": ("funnel", "oto", "order bump", "affiliate", "jv", "commission", "launch"),
        "execution": ("step", "checklist", "workflow", "example", "case study", "prompt", "swipe"),
        "risk": ("license", "rights", "plr", "mrr", "refund", "disclaimer", "compliance"),
    }
    for markers in marker_groups.values():
        if any(marker in text for marker in markers):
            score += 12
    if re.search(r"\n\s*(?:\d+\.|-|\*)\s+", str(hit.get("text", ""))):
        score += 8
    if "|" in str(hit.get("text", "")) and "---" in str(hit.get("text", "")):
        score += 5
    return max(0, min(100, score))


def detect_patterns(text: str, title: str = "") -> list[str]:
    haystack = f"{title}\n{text[:5000]}".lower()
    patterns: list[str] = []
    checks = (
        ("Product Pack", ("bundle", "pack", "template", "planner", "worksheet", "printable")),
        ("Sales Page", ("headline", "sales page", "cta", "faq", "bonus", "guarantee")),
        ("Funnel / OTO", ("funnel", "oto", "order bump", "downsell", "upsell", "backend")),
        ("JV / Affiliate", ("jv", "affiliate", "commission", "swipe", "review access")),
        ("Prompt / Template", ("prompt", "template", "chatgpt", "ai", "fill in", "placeholder")),
        ("KDP / Printable", ("kdp", "printable", "canva", "interior", "coloring", "worksheet")),
        ("Kids / Education", ("kids", "children", "preschool", "learning", "coloring", "activity")),
        ("Compliance / License", ("license", "plr", "mrr", "rights", "refund", "disclaimer")),
    )
    for name, markers in checks:
        if any(marker in haystack for marker in markers):
            patterns.append(name)
    return patterns or ["General Research"]


def extract_case_study_patterns(query: str, *, limit: int = 16) -> dict:
    hits = search_case_study_brain(query, limit=limit)
    pattern_counter: Counter[str] = Counter()
    category_counter: Counter[str] = Counter()
    top_hits = []
    for hit in hits:
        category_counter[str(hit.get("category", "00_Unsorted"))] += 1
        for pattern in hit.get("patterns", []):
            pattern_counter[pattern] += 1
        top_hits.append(
            {
                "title": hit.get("title", ""),
                "source_path": hit.get("source_path", ""),
                "category": hit.get("category", ""),
                "score": hit.get("pattern_score", 0),
                "patterns": hit.get("patterns", []),
                "excerpt": " ".join(str(hit.get("text", "")).split())[:900],
            }
        )
    output = {
        "query": query,
        "summary": case_study_summary(),
        "top_patterns": pattern_counter.most_common(12),
        "top_categories": category_counter.most_common(12),
        "top_hits": sorted(top_hits, key=lambda item: int(item["score"]), reverse=True),
        "training_readiness": training_readiness_score(),
        "reuse_rules": training_system_notes(),
    }
    PATTERN_LIBRARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    PATTERN_LIBRARY_PATH.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    return output


def training_readiness_score() -> dict:
    summary = case_study_summary()
    documents = int(summary.get("documents") or 0)
    chunks = int(summary.get("chunks") or 0)
    categories = [item for item in summary.get("categories", []) if int(item.get("count") or 0) > 0 and item.get("category") != "00_Unsorted"]
    category_coverage = len(categories)
    score = 0
    score += min(35, documents // 20)
    score += min(30, chunks // 80)
    score += min(25, category_coverage * 3)
    score += 10 if summary.get("source_exists") else 0
    score = max(0, min(100, score))
    if score >= 80:
        decision = "TRAINING READY"
    elif score >= 45:
        decision = "PARTIAL TRAINING READY"
    elif score > 0:
        decision = "SEED TRAINING ONLY"
    else:
        decision = "MISSING TRAINING DATA"
    return {
        "score": score,
        "decision": decision,
        "documents": documents,
        "chunks": chunks,
        "category_coverage": category_coverage,
        "recommendation": training_recommendation(score),
    }


def training_recommendation(score: int) -> str:
    if score >= 80:
        return "Use Case Study Brain in production answers, with citations and anti-copy checks."
    if score >= 45:
        return "Use for research/pattern extraction, then index more files before relying on niche-specific conclusions."
    if score > 0:
        return "This is only a seed brain. Run /train_full_case_study_brain 1000 or more."
    return "No usable data yet. Check PLR_AGENT_FILE_BACKUP_DIR and run training."


def category_counts() -> list[dict]:
    if not CASE_STUDY_DB_PATH.exists():
        return [{"category": name, "count": 0} for name, _ in CATEGORY_RULES]
    counts = {name: 0 for name, _ in CATEGORY_RULES}
    counts["00_Unsorted"] = 0
    try:
        with sqlite3.connect(CASE_STUDY_DB_PATH) as conn:
            rows = conn.execute("SELECT source_path, title FROM documents").fetchall()
    except sqlite3.Error:
        rows = []
    for source_path, title in rows:
        counts[classify_source(source_path, title)] = counts.get(classify_source(source_path, title), 0) + 1
    return [{"category": key, "count": value} for key, value in counts.items()]


def classify_source(source_path: str, title: str = "") -> str:
    haystack = f"{source_path} {title}".replace("\\", "/").lower()
    for category, markers in CATEGORY_RULES:
        if any(marker in haystack for marker in markers):
            return category
    return "00_Unsorted"


def format_case_study_context(query: str, *, limit: int = 6) -> str:
    hits = search_case_study_brain(query, limit=limit)
    if not hits:
        return "Case Study Brain: chưa có kết quả phù hợp. Hãy chạy /train_case_study_brain hoặc kiểm tra G:\\file_backup."
    lines = [f"Case Study Brain results for: {query}"]
    for index, hit in enumerate(hits, start=1):
        excerpt = " ".join(str(hit.get("text", "")).split())[:700]
        lines.extend(
            [
                "",
                f"{index}. [{hit.get('category')}] {hit.get('title')}",
                f"Source: {hit.get('source_path')}",
                excerpt,
            ]
        )
    return "\n".join(lines)


def write_training_report(query: str = "AI PLR Prompt Template Packs for KDP Printables") -> dict:
    patterns = extract_case_study_patterns(query, limit=20)
    readiness = patterns["training_readiness"]
    lines = [
        "# Case Study Brain Training Report",
        "",
        f"Created At: {datetime.now().isoformat(timespec='seconds')}",
        f"Source Root: `{FILE_BACKUP_DIR}`",
        f"Brain DB: `{CASE_STUDY_DB_PATH}`",
        f"Pattern Library: `{PATTERN_LIBRARY_PATH}`",
        "",
        "## Training Readiness",
        "",
        f"Score: {readiness['score']}/100",
        f"Decision: {readiness['decision']}",
        f"Documents: {readiness['documents']}",
        f"Chunks: {readiness['chunks']}",
        f"Category Coverage: {readiness['category_coverage']}/10",
        f"Recommendation: {readiness['recommendation']}",
        "",
        "## Top Patterns",
        "",
    ]
    for name, count in patterns["top_patterns"]:
        lines.append(f"- {name}: {count}")
    lines.extend(["", "## Top Categories", ""])
    for name, count in patterns["top_categories"]:
        lines.append(f"- {name}: {count}")
    lines.extend(["", "## Best Case Study Hits", ""])
    for index, hit in enumerate(patterns["top_hits"][:10], start=1):
        lines.extend(
            [
                f"### {index}. {hit['title']}",
                "",
                f"- Score: {hit['score']}/100",
                f"- Category: {hit['category']}",
                f"- Patterns: {', '.join(hit['patterns'])}",
                f"- Source: `{hit['source_path']}`",
                f"- Extract: {hit['excerpt']}",
                "",
            ]
        )
    lines.extend(
        [
            "## Rules",
            "",
            "- Use old files as case-study memory, not model weights.",
            "- Reuse structure, sequence, quality gates, and packaging patterns.",
            "- Do not copy old product text verbatim into new sellable assets.",
            "- Always run license/compliance checks before resale or client-use claims.",
        ]
    )
    TRAINING_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    TRAINING_REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    return {
        "report_path": str(TRAINING_REPORT_PATH),
        "pattern_library_path": str(PATTERN_LIBRARY_PATH),
        "training_readiness": readiness,
        "patterns": patterns,
    }


def training_system_notes() -> list[str]:
    return [
        "Use G:\\file_backup as input data / case-study brain.",
        "Do not copy old assets verbatim into products for sale.",
        "Do not upload the raw backup folder to GitHub.",
        "Do not pretend the files are model weights.",
        "Agent should retrieve patterns, structures, mistakes, examples, and launch workflows from the indexed brain.",
    ]


def workflow_completion_steps() -> list[str]:
    return [
        "Research thị trường",
        "Chọn ngách nhỏ",
        "Phân tích sản phẩm bán tốt",
        "Chọn buyer mục tiêu",
        "Tạo offer angle",
        "Lên cấu trúc pack",
        "Tạo bản nháp từng file",
        "Chấm điểm từng file",
        "Kiểm tra AI Replace Risk",
        "Kiểm tra Beginner Confusion",
        "Test prompt thật",
        "Test như buyer thật",
        "Ghi lỗi bị kẹt",
        "Fix / nâng cấp từng phần",
        "Chấm điểm lại",
        "Thêm example output",
        "Thêm checklist",
        "Thêm fix prompt",
        "Thêm sales material",
        "Thêm license / compliance",
        "Đóng gói folder",
        "Check placeholder",
        "Export ZIP",
        "Test ZIP",
        "Soft launch / gửi review",
        "Lấy feedback",
        "Sửa bản V2",
        "Public launch",
        "Theo dõi refund / câu hỏi buyer",
        "Update / tạo OTO / bundle",
    ]


def ai_workflow_steps() -> list[str]:
    return [
        "Ra lệnh cho AI nghiên cứu ngách",
        "Ra lệnh cho AI phân tích sản phẩm mẫu",
        "Ra lệnh cho AI tìm điểm yếu của đối thủ",
        "Ra lệnh cho AI chọn buyer cụ thể",
        "Ra lệnh cho AI tạo offer angle",
        "Ra lệnh cho AI tạo cấu trúc pack",
        "Ra lệnh cho AI viết từng file",
        "Ra lệnh cho AI chấm điểm từng file",
        "Ra lệnh cho AI kiểm tra 'ChatGPT cũng làm được không?'",
        "Ra lệnh cho AI tìm chỗ người mới sẽ bị kẹt",
        "Ra lệnh cho AI nâng cấp phần yếu",
        "Ra lệnh cho AI tạo ví dụ mẫu",
        "Ra lệnh cho AI tạo checklist",
        "Ra lệnh cho AI tạo fix prompt",
        "Ra lệnh cho AI tạo sales material",
        "Ra lệnh cho AI tạo license/compliance",
        "Ra lệnh cho AI giả làm buyer test",
        "Ra lệnh cho AI giả làm refund auditor",
        "Ra lệnh cho AI kiểm tra pack đủ bán chưa",
        "Ra lệnh cho AI tạo bản V2 sau khi fix",
    ]


def _write_manifest(result: CaseStudyIngestResult, *, notes: list[str]) -> None:
    TRAINING_MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        **asdict(result),
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "repo_root": str(ROOT_DIR),
        "notes": notes,
        "categories": [name for name, _ in CATEGORY_RULES],
        "completion_workflow": workflow_completion_steps(),
        "ai_workflow": ai_workflow_steps(),
    }
    TRAINING_MANIFEST_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

from brain import BrainStats, brain_summary, ingest_brain, search_brain
from config import DATABASE_DIR, FILE_BACKUP_DIR, ROOT_DIR

CASE_STUDY_BRAIN_DIR = DATABASE_DIR / "agent_brains" / "case_study"
CASE_STUDY_DB_PATH = CASE_STUDY_BRAIN_DIR / "case_study_brain.sqlite"
TRAINING_MANIFEST_PATH = CASE_STUDY_BRAIN_DIR / "case_study_training_manifest.json"

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
    return hits


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

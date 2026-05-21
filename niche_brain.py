from __future__ import annotations

import json
import re
import sqlite3
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

from brain import BrainStats, brain_summary, ingest_brain, search_brain
from config import DATABASE_DIR, ROOT_DIR, UDEMY_TRANSCRIPT_OUTPUT_DIR

NICHE_KEY = "ai_printables"
NICHE_NAME = "AI Printables"
NICHE_BRAIN_DIR = DATABASE_DIR / "agent_brains" / NICHE_KEY
NICHE_DB_PATH = NICHE_BRAIN_DIR / "ai_printables_brain.sqlite"
NICHE_MANIFEST_PATH = NICHE_BRAIN_DIR / "ai_printables_training_manifest.json"
NICHE_PATTERN_LIBRARY_PATH = NICHE_BRAIN_DIR / "ai_printables_pattern_library.json"
NICHE_REPORT_PATH = NICHE_BRAIN_DIR / "AI_PRINTABLES_TRAINING_REPORT.md"

DEFAULT_NICHE_QUERY = (
    "AI-assisted PLR products KDP covers coloring book journal poster social media assets "
    "Etsy printable bundle Canva kids worksheet puzzle book MidJourney ChatGPT"
)

MARKET_PATTERN_QUERY = (
    "AI printable product Etsy KDP coloring journal worksheet Canva prompt pack sales page "
    "bundle kit funnel deliverables price"
)

CATEGORY_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("01_KDP_Kindle", ("kindle", "kdp", "book marketing", "publish on kindle", "amazon")),
    ("02_Etsy_Printables", ("etsy", "printable", "digital product", "sell 30")),
    ("03_Canva_Bulk_Assets", ("canva", "bulk content", "social media", "poster", "template")),
    ("04_AI_Image_Prompts", ("midjourney", "image generation", "generative ai", "chatgpt image")),
    ("05_Coloring_Drawing", ("coloring", "drawing", "kids", "children", "art")),
    ("06_Journals_Planners", ("journal", "planner", "notion", "interior", "worksheet")),
    ("07_Marketing_Launch", ("marketing", "ecommerce", "content marketing", "sales", "business")),
    ("08_Automation_Workflow", ("automation", "prompt engineering", "workflow", "ai complete")),
)


@dataclass(frozen=True)
class NicheIngestResult:
    status: str
    niche: str
    source_root: str
    db_path: str
    max_files: int | None
    scanned_files: int
    ingested_documents: int
    skipped_files: int
    chunks: int
    errors: int
    manifest_path: str


def niche_roots() -> list[Path]:
    return [UDEMY_TRANSCRIPT_OUTPUT_DIR]


def ingest_niche_brain(*, rebuild: bool = False, max_files: int | None = None) -> NicheIngestResult:
    NICHE_BRAIN_DIR.mkdir(parents=True, exist_ok=True)
    source_root = UDEMY_TRANSCRIPT_OUTPUT_DIR
    if not source_root.exists():
        result = NicheIngestResult(
            status="MISSING_SOURCE_ROOT",
            niche=NICHE_NAME,
            source_root=str(source_root),
            db_path=str(NICHE_DB_PATH),
            max_files=max_files,
            scanned_files=0,
            ingested_documents=0,
            skipped_files=0,
            chunks=0,
            errors=0,
            manifest_path=str(NICHE_MANIFEST_PATH),
        )
        _write_manifest(result, notes=niche_system_notes())
        return result

    stats: BrainStats = ingest_brain(
        roots=[source_root],
        db_path=NICHE_DB_PATH,
        rebuild=rebuild,
        max_files=max_files,
    )
    result = NicheIngestResult(
        status="CREATED" if stats.ingested_documents or NICHE_DB_PATH.exists() else "EMPTY",
        niche=NICHE_NAME,
        source_root=str(source_root),
        db_path=str(stats.db_path),
        max_files=max_files,
        scanned_files=stats.scanned_files,
        ingested_documents=stats.ingested_documents,
        skipped_files=stats.skipped_files,
        chunks=stats.chunks,
        errors=stats.errors,
        manifest_path=str(NICHE_MANIFEST_PATH),
    )
    _write_manifest(result, notes=niche_system_notes())
    return result


def niche_summary() -> dict:
    summary = brain_summary(NICHE_DB_PATH)
    summary["niche"] = NICHE_NAME
    summary["source_root"] = str(UDEMY_TRANSCRIPT_OUTPUT_DIR)
    summary["source_exists"] = UDEMY_TRANSCRIPT_OUTPUT_DIR.exists()
    summary["source_required"] = False
    summary["safe_to_delete_source"] = int(summary.get("documents") or 0) > 0
    summary["manifest_path"] = str(NICHE_MANIFEST_PATH)
    summary["categories"] = category_counts()
    summary["training_mode"] = "RAG / searchable niche brain from Udemy transcripts, not model-weight fine-tuning"
    return summary


def search_niche_brain(query: str, *, limit: int = 8) -> list[dict]:
    hits = search_brain(query or DEFAULT_NICHE_QUERY, limit=limit, db_path=NICHE_DB_PATH)
    for hit in hits:
        hit["category"] = classify_source(str(hit.get("source_path", "")), str(hit.get("title", "")))
        hit["pattern_score"] = score_niche_hit(hit)
        hit["patterns"] = detect_patterns(str(hit.get("text", "")), str(hit.get("title", "")))
    return hits


def score_niche_hit(hit: dict) -> int:
    text = f"{hit.get('title', '')} {hit.get('source_path', '')} {hit.get('text', '')[:3000]}".lower()
    score = 20
    marker_groups = {
        "product": ("bundle", "pack", "kit", "journal", "planner", "worksheet", "cover", "coloring", "printable"),
        "ai": ("chatgpt", "prompt", "midjourney", "ai", "generative", "automation"),
        "market": ("etsy", "kdp", "kindle", "amazon", "canva", "social media"),
        "launch": ("marketing", "sell", "sales", "product", "business", "ecommerce"),
        "execution": ("step", "workflow", "template", "example", "create", "design"),
    }
    for markers in marker_groups.values():
        if any(marker in text for marker in markers):
            score += 13
    if re.search(r"\n\s*(?:\d+\.|-|\*)\s+", str(hit.get("text", ""))):
        score += 8
    return max(0, min(100, score))


def detect_patterns(text: str, title: str = "") -> list[str]:
    haystack = f"{title}\n{text[:5000]}".lower()
    checks = (
        ("AI Etsy Printable Bundle Builder", ("etsy", "printable", "bundle", "canva")),
        ("AI Kids Worksheet Factory", ("kids", "children", "worksheet", "learning", "activity")),
        ("AI KDP Puzzle Book Launch Kit", ("kdp", "kindle", "puzzle", "book", "amazon")),
        ("AI Coloring Page Niche Pack", ("coloring", "drawing", "art", "kids")),
        ("AI Journal Interior System", ("journal", "planner", "interior", "notion")),
        ("AI Canva Printable Product Kit", ("canva", "poster", "social media", "template")),
        ("Prompt / Workflow System", ("prompt", "chatgpt", "midjourney", "workflow", "automation")),
        ("Launch / Marketing Pattern", ("marketing", "sales", "sell", "ecommerce", "business")),
    )
    patterns = [name for name, markers in checks if any(marker in haystack for marker in markers)]
    return patterns or ["General Niche Research"]


def extract_niche_patterns(query: str = DEFAULT_NICHE_QUERY, *, limit: int = 18) -> dict:
    hits = search_niche_brain(query, limit=limit)
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
        "summary": niche_summary(),
        "top_patterns": pattern_counter.most_common(12),
        "top_categories": category_counter.most_common(12),
        "top_hits": sorted(top_hits, key=lambda item: int(item["score"]), reverse=True),
        "training_readiness": niche_readiness_score(),
        "reuse_rules": niche_system_notes(),
    }
    NICHE_PATTERN_LIBRARY_PATH.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    return output

def evidence_summary(query: str = DEFAULT_NICHE_QUERY, *, limit: int = 12) -> dict:
    hits = search_niche_brain(query, limit=limit)
    pattern_counter: Counter[str] = Counter()
    category_counter: Counter[str] = Counter()
    docs = []
    for hit in hits:
        category_counter[str(hit.get("category", "00_Unsorted"))] += 1
        for pattern in hit.get("patterns", []):
            pattern_counter[pattern] += 1
        docs.append(
            {
                "title": hit.get("title", ""),
                "source_path": hit.get("source_path", ""),
                "category": hit.get("category", ""),
                "score": hit.get("pattern_score", 0),
                "patterns": hit.get("patterns", []),
                "excerpt": " ".join(str(hit.get("text", "")).split())[:420],
            }
        )
    readiness = niche_readiness_score()
    confidence = "HIGH" if hits and readiness.get("score", 0) >= 80 else "MEDIUM" if hits else "LOW"
    return {
        "query": query,
        "hits_used": len(hits),
        "summary": niche_summary(),
        "training_readiness": readiness,
        "top_patterns": pattern_counter.most_common(10),
        "top_categories": category_counter.most_common(10),
        "top_documents": docs,
        "confidence": confidence,
        "evidence_rule": "Use source-backed patterns only. Do not invent sales numbers, vendor names, or claims that are not present in retrieved chunks.",
    }

def market_pattern_extractor(query: str = MARKET_PATTERN_QUERY, *, limit: int = 24) -> dict:
    hits = search_niche_brain(query, limit=limit)
    combined = "\n".join(f"{hit.get('title', '')}\n{hit.get('text', '')[:3500]}" for hit in hits)
    price_values = _extract_prices(combined)
    return {
        "query": query,
        "evidence": evidence_summary(query, limit=min(limit, 12)),
        "top_niches": _rank_markers(combined, {
            "Coloring pages": ("coloring", "line art", "drawing"),
            "Kids worksheets": ("kids", "children", "worksheet", "activity"),
            "KDP books/covers": ("kdp", "kindle", "amazon", "cover", "book"),
            "Journal interiors": ("journal", "planner", "interior", "notion"),
            "Canva/social assets": ("canva", "poster", "social media", "template"),
            "Etsy printable bundles": ("etsy", "printable", "bundle"),
        }),
        "common_price_range": _price_range(price_values),
        "common_deliverables": _rank_markers(combined, {
            "Prompt pack": ("prompt", "chatgpt", "midjourney"),
            "Canva templates": ("canva", "template", "layout"),
            "Workflow/checklist": ("workflow", "checklist", "step by step"),
            "Examples/samples": ("example", "sample", "preview"),
            "Listing/sales copy": ("listing", "sales page", "copy", "description"),
            "License/compliance note": ("license", "commercial", "rights", "terms"),
        }),
        "common_funnel_structure": _rank_markers(combined, {
            "FE low-ticket kit": ("front end", "fe", "$17", "$27", "low ticket"),
            "Order bump asset bank": ("order bump", "bump", "bonus"),
            "OTO advanced pack": ("oto", "upsell", "advanced"),
            "Agency/commercial license": ("agency", "commercial license", "client"),
            "Membership/SaaS backend": ("membership", "subscription", "saas", "monthly"),
        }),
        "buyer_pains": _rank_markers(combined, {
            "Too slow to create products": ("save time", "faster", "quickly", "speed"),
            "Does not know what to design": ("idea", "niche", "topic", "blank"),
            "Needs editable templates": ("editable", "template", "canva"),
            "Needs listing/sales help": ("listing", "description", "marketing", "sell"),
            "Afraid output is low quality": ("quality", "mistake", "check", "review"),
        }),
        "weaknesses_repeated": [
            "Many hits point to prompts/templates, but fewer prove a complete buyer workflow.",
            "Listing, delivery, refund-risk, and quality-check assets appear less often than raw creation assets.",
            "Evidence often supports product creation, but not public-launch proof such as payment/delivery/JV feedback.",
        ],
        "opportunity_gap": [
            "Build implementation kits, not raw prompt packs.",
            "Add filled examples, QC checklists, fix prompts, listing worksheet, delivery page, and onboarding emails.",
            "Keep Public Launch Gate separate from ZIP creation so the agent cannot overclaim readiness.",
        ],
    }

def competitor_matrix(query: str = MARKET_PATTERN_QUERY, *, limit: int = 14) -> dict:
    hits = search_niche_brain(query, limit=limit * 3)
    rows = []
    seen: set[str] = set()
    for hit in hits:
        text = str(hit.get("text", ""))
        source_path = str(hit.get("source_path", ""))
        title = str(hit.get("title", "")) or Path(source_path).stem
        dedupe_key = f"{source_path}|{title}".lower()
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)
        rows.append(
            {
                "vendor": _infer_vendor(source_path),
                "product": title,
                "niche": hit.get("category", ""),
                "price": _first_price(text) or "UNKNOWN",
                "sales": _first_sales(text) or "UNKNOWN",
                "angle": ", ".join(hit.get("patterns", [])[:3]),
                "deliverables": ", ".join(name for name, count in _rank_markers(text, {
                    "Prompt pack": ("prompt", "chatgpt", "midjourney"),
                    "Canva templates": ("canva", "template"),
                    "Checklist/workflow": ("checklist", "workflow", "step"),
                    "Listing copy": ("listing", "description", "sales page"),
                    "Examples": ("example", "sample", "preview"),
                }) if count > 0) or "UNKNOWN",
                "strength": _strength_from_hit(hit),
                "weakness": _weakness_from_text(text),
                "improvement_opportunity": "Add deeper implementation files, buyer test, prompt-output test, refund-risk audit, and export proof.",
                "source_path": source_path,
            }
        )
        if len(rows) >= limit:
            break
    return {
        "query": query,
        "evidence": evidence_summary(query, limit=min(limit, 10)),
        "matrix": rows,
        "rule": "Rows are inferred from retrieved local documents/chunks. UNKNOWN means the source chunk did not expose that field.",
    }

def offer_gap_detector(query: str = "Lead Magnet Printable Builder For Coaches", *, limit: int = 18) -> dict:
    market = market_pattern_extractor(query, limit=limit)
    return {
        "query": query,
        "evidence": market["evidence"],
        "too_common": [
            "Raw prompt packs without filled examples.",
            "Generic Canva/template bundles without a buyer journey.",
            "Broad AI printable bundles that do not pick one buyer and one use case.",
        ],
        "missing_in_market": market["opportunity_gap"],
        "recommended_positioning": "Lead Magnet Printable Builder For Coaches: a workflow-first implementation kit with worksheet prompts, Canva layout guide, opt-in copy, thank-you page, welcome emails, buyer test, and ZIP proof.",
        "must_include_to_win": [
            "A filled example such as Instagram Bio Audit.",
            "Prompt Output Test that rewrites weak AI output.",
            "Refund Risk and AI Replace Risk audits.",
            "Delivery page and onboarding emails.",
            "Export ZIP plus ZIP_PATH, EXPORT_LOG, FILE_MANIFEST.",
        ],
        "quality_gate_rule": "If product files or ZIP are missing, final score cannot exceed 6/10. If placeholders remain, Public Launch Gate stays FAIL.",
    }


def format_niche_context(query: str, *, limit: int = 6) -> str:
    hits = search_niche_brain(query or DEFAULT_NICHE_QUERY, limit=limit)
    if not hits:
        return "AI Printables Brain: chưa có dữ liệu phù hợp. Hãy chạy /ai_print_train 300 trước."
    lines = [f"AI Printables Brain results for: {query or DEFAULT_NICHE_QUERY}"]
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


def niche_readiness_score() -> dict:
    summary = niche_summary()
    documents = int(summary.get("documents") or 0)
    chunks = int(summary.get("chunks") or 0)
    categories = [item for item in summary.get("categories", []) if int(item.get("count") or 0) > 0 and item.get("category") != "00_Unsorted"]
    category_coverage = len(categories)
    score = min(35, documents // 8) + min(35, chunks // 40) + min(20, category_coverage * 3)
    score += 10 if summary.get("source_exists") else 0
    score = max(0, min(100, score))
    decision = "NICHE AGENT READY" if score >= 80 else "PARTIAL NICHE BRAIN" if score >= 45 else "SEED ONLY" if score > 0 else "MISSING DATA"
    return {
        "score": score,
        "decision": decision,
        "documents": documents,
        "chunks": chunks,
        "category_coverage": category_coverage,
        "recommendation": niche_recommendation(score),
    }


def niche_recommendation(score: int) -> str:
    if score >= 80:
        return "Use this agent for deep AI printable/KDP/Etsy/Canva product planning with source-backed patterns."
    if score >= 45:
        return "Usable for pattern extraction; index more transcripts before treating it as a strong niche brain."
    if score > 0:
        return "Seed brain only. Run /ai_print_train 300 or /ai_print_full_train 1000."
    return "No usable transcript data yet. Check G:\\Documents\\udemy-transcript-downloader\\output."


def category_counts() -> list[dict]:
    if not NICHE_DB_PATH.exists():
        return [{"category": name, "count": 0} for name, _ in CATEGORY_RULES]
    counts = {name: 0 for name, _ in CATEGORY_RULES}
    counts["00_Unsorted"] = 0
    try:
        with sqlite3.connect(NICHE_DB_PATH) as conn:
            rows = conn.execute("SELECT source_path, title FROM documents").fetchall()
    except sqlite3.Error:
        rows = []
    for source_path, title in rows:
        category = classify_source(source_path, title)
        counts[category] = counts.get(category, 0) + 1
    return [{"category": key, "count": value} for key, value in counts.items()]


def classify_source(source_path: str, title: str = "") -> str:
    haystack = f"{source_path} {title}".replace("\\", "/").lower()
    for category, markers in CATEGORY_RULES:
        if any(marker in haystack for marker in markers):
            return category
    return "00_Unsorted"

def _rank_markers(text: str, marker_map: dict[str, tuple[str, ...]]) -> list[tuple[str, int]]:
    haystack = str(text or "").lower()
    rows = []
    for name, markers in marker_map.items():
        count = sum(haystack.count(marker.lower()) for marker in markers)
        rows.append((name, count))
    return sorted(rows, key=lambda item: item[1], reverse=True)

def _extract_prices(text: str) -> list[int]:
    values = []
    for match in re.finditer(r"\$(\d{1,4})(?:\.\d{2})?", str(text or "")):
        value = int(match.group(1))
        if 1 <= value <= 997:
            values.append(value)
    return values

def _price_range(values: list[int]) -> str:
    if not values:
        return "UNKNOWN from retrieved chunks"
    values = sorted(values)
    return f"${values[0]} - ${values[-1]} from retrieved chunks"

def _first_price(text: str) -> str:
    values = _extract_prices(text)
    return f"${values[0]}" if values else ""

def _first_sales(text: str) -> str:
    match = re.search(r"(\d{2,6})\s*(?:sales|sold|customers|buyers)", str(text or ""), flags=re.IGNORECASE)
    return match.group(0) if match else ""

def _infer_vendor(source_path: str) -> str:
    parts = [part for part in Path(str(source_path or "")).parts if part and part not in {"output", "Documents"}]
    if len(parts) >= 2:
        candidate = parts[-2]
        return candidate[:80] or "UNKNOWN"
    return "UNKNOWN"

def _strength_from_hit(hit: dict) -> str:
    patterns = hit.get("patterns") or []
    score = int(hit.get("pattern_score") or 0)
    if score >= 80:
        return "Strong source match with product/AI/market/execution signals."
    if patterns:
        return f"Relevant pattern: {', '.join(patterns[:2])}."
    return "Relevant retrieved chunk, but weak explicit product signals."

def _weakness_from_text(text: str) -> str:
    haystack = str(text or "").lower()
    if "example" not in haystack and "sample" not in haystack:
        return "No filled example visible in retrieved chunk."
    if "checklist" not in haystack and "quality" not in haystack:
        return "No clear QC/checklist visible in retrieved chunk."
    if "delivery" not in haystack and "zip" not in haystack:
        return "No delivery/export proof visible in retrieved chunk."
    return "Needs validation against full product files before copying the pattern."


def write_niche_report(query: str = DEFAULT_NICHE_QUERY) -> dict:
    patterns = extract_niche_patterns(query, limit=22)
    readiness = patterns["training_readiness"]
    lines = [
        "# AI Printables Agent Training Report",
        "",
        f"Created At: {datetime.now().isoformat(timespec='seconds')}",
        f"Source Root: `{UDEMY_TRANSCRIPT_OUTPUT_DIR}`",
        f"Brain DB: `{NICHE_DB_PATH}`",
        f"Pattern Library: `{NICHE_PATTERN_LIBRARY_PATH}`",
        "",
        "## Training Readiness",
        "",
        f"Score: {readiness['score']}/100",
        f"Decision: {readiness['decision']}",
        f"Documents: {readiness['documents']}",
        f"Chunks: {readiness['chunks']}",
        f"Category Coverage: {readiness['category_coverage']}/{len(CATEGORY_RULES)}",
        f"Recommendation: {readiness['recommendation']}",
        "",
        "## Offer Seeds",
        "",
        "- AI Etsy Printable Bundle Builder",
        "- AI Kids Worksheet Factory",
        "- AI KDP Puzzle Book Launch Kit",
        "- AI Coloring Page Niche Pack",
        "- AI Journal Interior System",
        "- AI Canva Printable Product Kit",
        "",
        "## Top Patterns",
        "",
    ]
    lines.extend(f"- {name}: {count}" for name, count in patterns["top_patterns"])
    lines.extend(["", "## Best Hits", ""])
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
    lines.extend(["## Rules", "", *[f"- {item}" for item in niche_system_notes()]])
    NICHE_REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    return {
        "report_path": str(NICHE_REPORT_PATH),
        "pattern_library_path": str(NICHE_PATTERN_LIBRARY_PATH),
        "training_readiness": readiness,
        "patterns": patterns,
    }


def niche_system_notes() -> list[str]:
    return [
        "Use Udemy transcripts as searchable niche memory/RAG, not model weights.",
        "Focus on AI-assisted PLR products + KDP covers + coloring books + journals + posters/social media assets.",
        "Turn lessons into rebrandable systems, packs, prompts, workflow checklists, and launch assets.",
        "Do not copy course text verbatim into products for sale.",
        "Every answer should include productization, AI-replacement defense, license/risk caution, and next build action.",
    ]


def _write_manifest(result: NicheIngestResult, *, notes: list[str]) -> None:
    NICHE_MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        **asdict(result),
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "repo_root": str(ROOT_DIR),
        "notes": notes,
        "offer_seeds": [
            "AI Etsy Printable Bundle Builder",
            "AI Kids Worksheet Factory",
            "AI KDP Puzzle Book Launch Kit",
            "AI Coloring Page Niche Pack",
            "AI Journal Interior System",
            "AI Canva Printable Product Kit",
        ],
        "categories": [name for name, _ in CATEGORY_RULES],
    }
    NICHE_MANIFEST_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

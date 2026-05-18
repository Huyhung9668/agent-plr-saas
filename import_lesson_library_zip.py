from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import zipfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from agent_profiles import profile_by_key
from brain import brain_summary, ingest_brain
from config import ROOT_DIR

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DEFAULT_ZIP = Path("G:/Documents/Auto Youtube/File_Kết_Quả/Thu_Vien_Bai_Hoc_Da_Sap_Xep.zip")
IMPORT_ROOT = ROOT_DIR / "training_imports"
INPUT_ROOT = ROOT_DIR / "input_files"


@dataclass(frozen=True)
class Route:
    role: str
    child_agent: str
    reason: str


TOPIC_ROUTES: dict[str, tuple[Route, ...]] = {
    "01_Tu_Duy_Vendor_San_Pham_So_WarriorPlus": (
        Route("build_product", "offer_architect", "Vendor/product/funnel strategy for digital products."),
        Route("jv_manager", "launch_ops", "WarriorPlus/JVZoo launch and affiliate coordination."),
        Route("sale_page", "conversion_editor", "Sales funnel, offer flow, and approval-friendly copy."),
    ),
    "02_Research_Tao_San_Pham_PLR_Template_Autoblog": (
        Route("build_product", "product_researcher", "PLR research, product creation, template and autoblog ideas."),
    ),
    "03_Sales_Page_Offer_Bonus_Thanh_Toan": (
        Route("sale_page", "copywriter", "Sales page, offer, bonus, VSL, checkout and payment pages."),
        Route("build_product", "offer_architect", "Offer packaging, bonus logic, and product promise."),
    ),
    "04_Free_Traffic_Facebook_Group_Profile": (
        Route("jv_manager", "traffic_channel_planner", "Facebook group/profile traffic and social promo operations."),
    ),
    "05_Affiliate_SEO_Medium_Quora_Linkedin": (
        Route("jv_manager", "affiliate_researcher", "Affiliate, SEO, Medium, Quora and LinkedIn traffic research."),
        Route("sale_page", "hook_miner", "Review angles, hooks, objections and buyer intent from SEO traffic."),
    ),
    "06_Email_Funnel_Lead_Page_Cham_Soc": (
        Route("jv_manager", "swipe_writer", "Email funnel, lead page and follow-up assets."),
        Route("sale_page", "conversion_editor", "Lead-page and thank-you-page conversion flow."),
    ),
    "07_Thu_Thach_7_Ngay_Dropship_Traffic": (
        Route("build_product", "digital_product_curriculum_builder", "7-day product/dropship curriculum and packaging."),
        Route("jv_manager", "traffic_channel_planner", "Free traffic and list-building for digital offers."),
        Route("sale_page", "copywriter", "Offer, page and conversion messaging for simple digital products."),
    ),
    "08_SaaS_AI_Agent_App_Frontend_Backend": (
        Route("build_product", "saas_tool_packager", "SaaS, AI agent, app, frontend/backend and tool packaging."),
        Route("jv_manager", "launch_ops", "SaaS/JVZoo launch, email and membership/AppSumo positioning."),
    ),
    "09_Cong_Cu_Cai_Dat_Canva_Website": (
        Route("build_product", "asset_packager", "Canva, mockup, website setup and product presentation assets."),
        Route("sale_page", "conversion_editor", "Landing page and presentation polish."),
    ),
    "10_Hoi_Dap_Case_Study_Khac": (
        Route("build_product", "product_researcher", "General Q&A, case study and miscellaneous product lessons."),
    ),
}


ROLE_CHILD_AGENT_NOTES: dict[str, dict[str, str]] = {
    "build_product": {
        "product_researcher": "Research niches, PLR angles, demand, buyer pains, and product opportunities.",
        "offer_architect": "Design product promise, USP, funnel logic, bonuses, pricing and OTO structure.",
        "asset_packager": "Package files, mockups, Canva/website assets, delivery structure and buyer-friendly bundles.",
        "license_risk_checker": "Check rights, copyright, license assumptions and risky claims.",
        "digital_product_curriculum_builder": "Turn lesson libraries, challenges and workflows into paid digital products.",
        "saas_tool_packager": "Package SaaS, AI agents, apps and tool demos into sellable offers.",
    },
    "jv_manager": {
        "affiliate_researcher": "Find affiliate angles, partner fit, review traffic and marketplace positioning.",
        "jv_page_writer": "Prepare JV page copy, affiliate instructions, contest notes and promo framing.",
        "swipe_writer": "Write email swipes, lead nurture, follow-up, bonus and urgency sequences.",
        "launch_ops": "Plan WarriorPlus/JVZoo launches, Muncheye listing, delivery, refunds and approval workflow.",
        "traffic_channel_planner": "Plan Facebook, Medium, Quora, SEO, LinkedIn and free traffic operations.",
        "email_list_growth_operator": "Build lead magnets, opt-in pages, buyer list and nurture systems.",
    },
    "sale_page": {
        "hook_miner": "Extract headlines, hooks, pains, intent, objections and proof substitutes.",
        "copywriter": "Write sales page, VSL, bullets, FAQ, CTA, bonus and payment-page copy.",
        "compliance_editor": "Remove fake income claims, unsafe scarcity, rights issues and platform-risk copy.",
        "conversion_editor": "Improve page flow, offer stack, lead page, checkout and objection handling.",
    },
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Import sorted lesson ZIP into 3 role brains as child-agent training.")
    parser.add_argument("--zip", default=str(DEFAULT_ZIP))
    parser.add_argument("--no-ingest", action="store_true")
    args = parser.parse_args()

    source_zip = Path(args.zip)
    if not source_zip.exists():
        raise FileNotFoundError(source_zip)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    import_dir = IMPORT_ROOT / f"lessonzip_{stamp}"
    raw_dir = import_dir / "r"
    routed_root = import_dir / "routed"
    raw_dir.mkdir(parents=True, exist_ok=True)
    routed_root.mkdir(parents=True, exist_ok=True)

    extract_zip_safely(source_zip, raw_dir)
    routes = route_lessons(raw_dir, routed_root)
    write_import_report(import_dir, source_zip, routes)

    summaries = {}
    if not args.no_ingest:
        summaries = ingest_routes(routed_root)

    print(
        json.dumps(
            {
                "source_zip": str(source_zip),
                "import_dir": str(import_dir),
                "routed_files": len(routes),
                "brain_summaries": summaries,
            },
            ensure_ascii=False,
            indent=2,
            default=str,
        )
    )


def extract_zip_safely(source_zip: Path, raw_dir: Path) -> None:
    destination = raw_dir.resolve()
    with zipfile.ZipFile(source_zip) as archive:
        for member in archive.infolist():
            if member.is_dir():
                continue
            member_path = Path(member.filename)
            clean_parts = [part for part in member_path.parts if part not in {"", ".", ".."}]
            if not clean_parts:
                continue
            if clean_parts and clean_parts[0].lower() == "thu_vien_bai_hoc_da_sap_xep":
                clean_parts = clean_parts[1:]
            safe_parts = [shorten_part(sanitize_filename(part), is_file=(index == len(clean_parts) - 1)) for index, part in enumerate(clean_parts)]
            target = destination.joinpath(*safe_parts).resolve()
            if not str(target).lower().startswith(str(destination).lower()):
                raise RuntimeError(f"Unsafe zip path: {member.filename}")
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(member) as src, target.open("wb") as dst:
                shutil.copyfileobj(src, dst)


def route_lessons(raw_dir: Path, routed_root: Path) -> list[dict]:
    records: list[dict] = []
    files = [path for path in raw_dir.rglob("*") if path.is_file()]
    for path in files:
        topic = detect_topic(path)
        route_set = route_for_path(path, topic)
        if not route_set:
            route_set = (Route("build_product", "product_researcher", "Fallback import for uncategorized lesson."),)

        for route in route_set:
            role_input = INPUT_ROOT / role_input_folder(route.role)
            target_dir = role_input / "child_agent_training" / route.child_agent / slugify(topic or "uncategorized")
            target_dir.mkdir(parents=True, exist_ok=True)
            target = unique_path(target_dir / sanitize_filename(path.name))
            shutil.copy2(path, target)

            meta = target.with_suffix(target.suffix + ".meta.md")
            meta.write_text(
                "\n".join(
                    [
                        f"# Child Agent Training Metadata: {target.stem}",
                        "",
                        f"- Main agent: {route.role}",
                        f"- Child agent: {route.child_agent}",
                        f"- Source ZIP topic: {topic or 'uncategorized'}",
                        f"- Original extracted path: {path}",
                        f"- Routing reason: {route.reason}",
                        "",
                        "Use this lesson as supporting knowledge for PLR, SaaS, WarriorPlus, sales-page, funnel, JV, and traffic decisions.",
                    ]
                ),
                encoding="utf-8",
            )
            records.append(
                {
                    "source": str(path),
                    "target": str(target),
                    "role": route.role,
                    "child_agent": route.child_agent,
                    "topic": topic,
                    "reason": route.reason,
                }
            )

    for role in ("build_product", "jv_manager", "sale_page"):
        write_child_agent_index(role)
    return records


def detect_topic(path: Path) -> str:
    for part in path.parts:
        if re.match(r"^\d{2}_", part):
            return part
    return ""


def route_for_path(path: Path, topic: str) -> tuple[Route, ...]:
    routes = list(TOPIC_ROUTES.get(topic, ()))
    text = f"{path.name} {topic}".lower()

    if any(word in text for word in ("bản quyền", "ban quyen", "copyright", "license", "paypal", "duyet", "duyệt")):
        routes.append(Route("build_product", "license_risk_checker", "Rights, platform approval or payment risk signal."))
        routes.append(Route("sale_page", "compliance_editor", "Compliance/risk copy editing signal."))
    if any(word in text for word in ("email", "lead", "opt-in", "chăm sóc", "cham soc")):
        routes.append(Route("jv_manager", "email_list_growth_operator", "Email/list/lead nurture signal."))
    if any(word in text for word in ("sales page", "sale page", "vsl", "offer", "bonus", "thanh toán", "thanh toan")):
        routes.append(Route("sale_page", "copywriter", "Sales page, offer, VSL, bonus or payment copy signal."))
    if any(word in text for word in ("saas", "app", "agent", "frontend", "backend", "tool")):
        routes.append(Route("build_product", "saas_tool_packager", "SaaS/app/tool packaging signal."))
    if any(word in text for word in ("affiliate", "jv", "warriorplus", "jvzoo", "muncheye", "traffic", "facebook", "quora", "medium", "seo")):
        routes.append(Route("jv_manager", "traffic_channel_planner", "Affiliate/JV/traffic channel signal."))

    deduped: dict[tuple[str, str], Route] = {}
    for route in routes:
        deduped[(route.role, route.child_agent)] = route
    return tuple(deduped.values())


def write_child_agent_index(role: str) -> None:
    profile = profile_by_key(role)
    role_input = INPUT_ROOT / role_input_folder(role)
    root = role_input / "child_agent_training"
    lines = [
        f"# {profile.name} - Child Agent Training Index",
        "",
        f"Mission: {profile.mission}",
        "",
        "This folder contains imported lesson-library training routed into child-agent memory.",
        "",
    ]
    for child, note in sorted(ROLE_CHILD_AGENT_NOTES[role].items()):
        folder = root / child
        file_count = len([path for path in folder.rglob("*") if path.is_file()]) if folder.exists() else 0
        lines.extend(
            [
                f"## {child}",
                "",
                note,
                "",
                f"- Folder: {folder}",
                f"- Files including metadata: {file_count}",
                "",
            ]
        )
    index_path = root / "_child_agent_index.md"
    root.mkdir(parents=True, exist_ok=True)
    index_path.write_text("\n".join(lines), encoding="utf-8")


def write_import_report(import_dir: Path, source_zip: Path, records: list[dict]) -> None:
    report = import_dir / "lesson_library_import_report.json"
    report.write_text(json.dumps({"source_zip": str(source_zip), "records": records}, ensure_ascii=False, indent=2), encoding="utf-8")

    md = import_dir / "lesson_library_import_report.md"
    counts: dict[str, int] = {}
    child_counts: dict[str, int] = {}
    for record in records:
        counts[record["role"]] = counts.get(record["role"], 0) + 1
        key = f"{record['role']}/{record['child_agent']}"
        child_counts[key] = child_counts.get(key, 0) + 1

    lines = [
        "# Lesson Library Import Report",
        "",
        f"- Source ZIP: {source_zip}",
        f"- Routed copies: {len(records)}",
        "",
        "## Main Agent Counts",
        "",
    ]
    for role, count in sorted(counts.items()):
        lines.append(f"- {role}: {count}")
    lines.extend(["", "## Child Agent Counts", ""])
    for key, count in sorted(child_counts.items()):
        lines.append(f"- {key}: {count}")
    md.write_text("\n".join(lines), encoding="utf-8")


def ingest_routes(routed_root: Path) -> dict[str, dict]:
    summaries: dict[str, dict] = {}
    for role in ("build_product", "jv_manager", "sale_page"):
        profile = profile_by_key(role)
        role_input_root = INPUT_ROOT / role_input_folder(role) / "child_agent_training"
        print(f"\n===== Additive ingest: {profile.name} =====")
        stats = ingest_brain(roots=[role_input_root], db_path=profile.db_path, rebuild=False)
        summary = brain_summary(profile.db_path)
        summaries[role] = {"stats": stats.__dict__, "summary": summary}
        print(stats)
        print(summary)
    return summaries


def role_input_folder(role: str) -> str:
    return {
        "build_product": "01_BUILD_PRODUCT",
        "jv_manager": "02_JV_MANAGER",
        "sale_page": "03_SALE_PAGE",
    }[role]


def sanitize_filename(name: str) -> str:
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", name)
    return name.strip(" .") or "lesson"


def shorten_part(name: str, *, is_file: bool) -> str:
    limit = 64 if is_file else 44
    if len(name) <= limit:
        return name
    path = Path(name)
    suffix = path.suffix if is_file else ""
    stem = path.stem if is_file and suffix else name
    keep = max(24, limit - len(suffix) - 9)
    return f"{stem[:keep].rstrip()}__short{suffix}"


def slugify(value: str) -> str:
    value = value.strip().replace(" ", "_")
    value = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", value)
    return value or "uncategorized"


def unique_path(path: Path) -> Path:
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    for index in range(2, 10_000):
        candidate = path.with_name(f"{stem}_{index}{suffix}")
        if not candidate.exists():
            return candidate
    raise RuntimeError(f"Cannot create unique path for {path}")


if __name__ == "__main__":
    main()

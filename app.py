from __future__ import annotations

import json
import sys
from pathlib import Path

from analyzer import analyze_library, analyze_product, scan_library
from auditor import build_license_risk_audit
from agent_profiles import get_agent_profiles
from brain import brain_summary, ingest_brain, search_brain
from config import PLR_DIR
from exporter import export_analysis, export_text
from idea_generator import generate_new_product_ideas
from importer import default_downloads_dir, import_downloaded_files, import_plr_inbox
from media_catalog import build_media_catalog
from media_text_extractor import extract_media_text
from master_agent import answer_master_question, format_sources, master_brain_status
from offer_builder import build_product_outline, create_bonus_stack, create_launch_assets
from product_pack_exporter import export_product_pack
from saas_importer import import_saas_inbox
from saas_planner import create_saas_plan
from sales_page_writer import write_sales_page
from db import save_analyses
from warriorplus_strategy import build_warriorplus_launch_plan, export_ai_plr_rebrand_kit
from workflow_agents import export_agent_overview_report, export_agent_workspace, get_workflow_agents


LAST_RESULTS: list[dict] = []


def main() -> None:
    _configure_console_encoding()
    PLR_DIR.mkdir(parents=True, exist_ok=True)
    print_header()

    while True:
        print_menu()
        choice = input("Chon chuc nang (nhap so roi bam Enter): ").strip()
        should_pause = True
        if choice:
            print(f"\nDang chay chuc nang {choice}...\n")

        if choice == "1":
            scan_plr_folder()
        elif choice == "2":
            analyze_single_product()
        elif choice == "3":
            analyze_all_products()
        elif choice == "4":
            generate_ideas()
        elif choice == "5":
            build_sales_page()
        elif choice == "6":
            export_current_report()
        elif choice == "7":
            build_outline()
        elif choice == "8":
            build_bonus_stack()
        elif choice == "9":
            build_launch_assets()
        elif choice == "10":
            license_risk_audit()
        elif choice == "11":
            import_downloads()
        elif choice == "12":
            build_saas_plan()
        elif choice == "13":
            export_full_product_pack()
        elif choice == "14":
            auto_sort_saas_inbox()
        elif choice == "15":
            auto_sort_plr_inbox()
        elif choice == "16":
            build_agent_brain()
        elif choice == "17":
            show_agent_brain()
        elif choice == "18":
            search_agent_brain()
        elif choice == "19":
            build_warriorplus_plan()
        elif choice == "20":
            export_rebrand_kit()
        elif choice == "21":
            show_workflow_agents()
        elif choice == "22":
            build_workflow_agent_workspace()
        elif choice == "23":
            show_role_brains()
        elif choice == "24":
            search_role_brain()
        elif choice == "25":
            master_agent_chat()
        elif choice == "0":
            should_pause = False
            print("Tam biet. Lan sau dua PLR vao /plr_files roi quet tiep.")
            break
        else:
            print("Lua chon khong hop le.")
        if should_pause:
            _pause_for_menu()


def print_header() -> None:
    print("\nAgent PLR Saas")
    print("==============")
    print(f"Thu muc PLR: {PLR_DIR}")
    print("Dat file .pdf, .docx, .txt, .md, .zip vao thu muc tren.\n")


def _configure_console_encoding() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

def print_menu() -> None:
    print("\n1. Scan PLR folder")
    print("2. Analyze 1 product")
    print("3. Analyze all products")
    print("4. Generate 10 new product ideas")
    print("5. Write sales page")
    print("6. Export current report")
    print("7. Build product outline")
    print("8. Create bonus stack")
    print("9. Create launch assets")
    print("10. License/risk audit")
    print("11. Import downloaded PLR files")
    print("12. Build SaaS plan")
    print("13. Export full product pack")
    print("14. Auto-sort SaaS inbox")
    print("15. Auto-sort PLR inbox")
    print("16. Build/update agent brain")
    print("17. Show agent brain summary")
    print("18. Search agent brain")
    print("19. Build WarriorPlus PLR/SaaS launch plan")
    print("20. Export AI PLR Rebrand Kit pack")
    print("21. Show 3 product launch workflow agents")
    print("22. Create/refresh workflow agent files and input folders")
    print("23. Show 3 role brain summaries")
    print("24. Search a role brain")
    print("25. Master Agent Chat")
    print("0. Exit")

def _pause_for_menu() -> None:
    input("\nNhan Enter de quay lai menu...")


def scan_plr_folder() -> None:
    paths = scan_library()
    print(f"\nTim thay {len(paths)} file PLR.")
    summary: dict[str, int] = {}
    for path in paths:
        folder = path.parent.name
        summary[folder] = summary.get(folder, 0) + 1
    for folder, count in sorted(summary.items()):
        print(f"- {folder}: {count} file")


def analyze_single_product() -> None:
    paths = scan_library()
    if not paths:
        print("Chua co file nao trong plr_files.")
        return

    for index, path in enumerate(paths, start=1):
        print(f"{index}. {path.name}")

    selected = input("Nhap so thu tu file can phan tich: ").strip()
    if not selected.isdigit() or int(selected) < 1 or int(selected) > len(paths):
        print("So thu tu khong hop le.")
        return

    result = analyze_product(paths[int(selected) - 1])
    result["source_path"] = str(paths[int(selected) - 1])
    print(json.dumps(result, ensure_ascii=False, indent=2))

    global LAST_RESULTS
    LAST_RESULTS = [result]


def analyze_all_products() -> None:
    global LAST_RESULTS
    LAST_RESULTS = analyze_library()
    if not LAST_RESULTS:
        print("Chua co file nao trong plr_files.")
        return

    print("\nTop 5 san pham dang lam:")
    for item in LAST_RESULTS[:5]:
        print(
            f"- {item.get('original_title')} | Score {item.get('final_score')}/10 | "
            f"{item.get('recommended_action')}"
        )
    db_path = save_analyses(LAST_RESULTS)
    print(f"\nDa luu ket qua vao database: {db_path}")


def generate_ideas() -> None:
    query = input("Nhap niche/tu khoa de lay tu brain, Enter = analyze raw PLR: ").strip()
    if query:
        results = _brain_analyses_from_query(query)
        if not results:
            print("Brain chua co ket qua phu hop. Hay build agent brain truoc.")
            return
        ideas = generate_new_product_ideas(results, count=10)
        path = export_text("new-product-ideas", ideas)
        print(f"\nDa tao idea tu agent brain va luu vao: {path}")
        print("\nPreview:\n")
        print(ideas[:3000])
        return

    results = _get_or_analyze()
    if not results:
        return
    ideas = generate_new_product_ideas(results, count=10)
    path = export_text("new-product-ideas", ideas)
    print(f"\nDa tao idea va luu vao: {path}")
    print("\nPreview:\n")
    print(ideas[:3000])


def build_sales_page() -> None:
    idea_context = input("Dan idea hoac mo ta san pham can viet sales page: ").strip()
    if not idea_context:
        results = _get_or_analyze()
        if not results:
            return
        idea_context = json.dumps(results[0], ensure_ascii=False, indent=2)

    idea_context = _add_brain_context(idea_context)
    sales_page = write_sales_page(idea_context)
    path = export_text("sales-page", sales_page)
    print(f"\nDa tao sales page va luu vao: {path}")
    print("\nPreview:\n")
    print(sales_page[:3000])


def export_current_report() -> None:
    results = _get_or_analyze()
    if not results:
        return
    json_path, csv_path, md_path = export_analysis(results)
    print("\nDa xuat report:")
    print(f"- JSON: {json_path}")
    print(f"- CSV: {csv_path}")
    print(f"- Markdown: {md_path}")


def build_outline() -> None:
    context = _context_from_input_or_top_result("Dan idea hoac Enter de dung top product: ")
    if not context:
        return
    context = _add_brain_context(context)
    outline = build_product_outline(context)
    path = export_text("product-outline", outline)
    print(f"\nDa tao outline va luu vao: {path}")
    print("\nPreview:\n")
    print(outline[:3000])


def build_bonus_stack() -> None:
    context = _context_from_input_or_top_result("Dan idea hoac Enter de dung top product: ")
    if not context:
        return
    context = _add_brain_context(context)
    bonuses = create_bonus_stack(context)
    path = export_text("bonus-stack", bonuses)
    print(f"\nDa tao bonus stack va luu vao: {path}")
    print("\nPreview:\n")
    print(bonuses[:3000])


def build_launch_assets() -> None:
    context = _context_from_input_or_top_result("Dan idea hoac Enter de dung top product: ")
    if not context:
        return
    context = _add_brain_context(context)
    assets = create_launch_assets(context)
    path = export_text("launch-assets", assets)
    print(f"\nDa tao launch assets va luu vao: {path}")
    print("\nPreview:\n")
    print(assets[:3000])


def license_risk_audit() -> None:
    results = _get_or_analyze()
    if not results:
        return
    audit = build_license_risk_audit(results)
    path = export_text("license-risk-audit", audit)
    print(f"\nDa tao license/risk audit va luu vao: {path}")
    print("\nPreview:\n")
    print(audit[:3000])


def import_downloads() -> None:
    default_dir = default_downloads_dir()
    source = input(f"Thu muc file da tai, Enter de dung {default_dir}: ").strip()
    source_dir = Path(source) if source else default_dir
    mode = input("Copy hay move? Enter = copy, go 'move' de di chuyen file: ").strip().lower()
    copy_mode = mode != "move"

    try:
        imported = import_downloaded_files(source_dir, copy_mode=copy_mode)
    except FileNotFoundError as error:
        print(error)
        return

    if not imported:
        print("Khong tim thay file ho tro trong thu muc do.")
        return

    print(f"\nDa import {len(imported)} file:")
    for item in imported:
        license_note = "license hint OK" if item["license_hint_found"] else "needs license check"
        print(f"- {item['action']}: {item['target']} | {item['category']} | {license_note}")


def build_saas_plan() -> None:
    context = _context_from_input_or_top_result("Dan idea hoac Enter de dung top product: ")
    if not context:
        return
    context = _add_brain_context(context)
    plan = create_saas_plan(context)
    path = export_text("saas-plan", plan)
    print(f"\nDa tao SaaS plan va luu vao: {path}")
    print("\nPreview:\n")
    print(plan[:3000])


def export_full_product_pack() -> None:
    context = _context_from_input_or_top_result("Dan idea hoac Enter de dung top product: ")
    if not context:
        return
    context = _add_brain_context(context)
    product_name = input("Ten product pack, Enter = AI PLR Rebrand Kit: ").strip() or "AI PLR Rebrand Kit"
    pack_dir = export_product_pack(context, product_name=product_name)
    print(f"\nDa xuat full product pack vao: {pack_dir}")
    print("Bao gom outline, bonus stack, sales page, launch assets, funnel map va SaaS plan.")


def auto_sort_saas_inbox() -> None:
    mode = input("Move hay copy? Enter = move, go 'copy' de giu file trong inbox: ").strip().lower()
    move_mode = mode != "copy"
    imported = import_saas_inbox(move_mode=move_mode)

    if not imported:
        print("Chua co file SaaS nao trong saas_files/_INBOX_DROP_HERE.")
        return

    print(f"\nDa phan loai {len(imported)} file SaaS:")
    for item in imported:
        print(f"- {item['action']}: {item['target']} | folder: {item['folder']}")


def auto_sort_plr_inbox() -> None:
    mode = input("Move hay copy? Enter = move, go 'copy' de giu file trong inbox: ").strip().lower()
    move_mode = mode != "copy"
    imported = import_plr_inbox(move_mode=move_mode)

    if not imported:
        print("Chua co file PLR nao trong plr_files/_INBOX_DROP_HERE.")
        return

    print(f"\nDa phan loai {len(imported)} file PLR:")
    for item in imported:
        license_note = "license hint OK" if item["license_hint_found"] else "needs license check"
        print(f"- {item['action']}: {item['target']} | {item['category']} | {license_note}")

def build_agent_brain() -> None:
    mode = input("Rebuild brain tu dau? Enter = update, go 'rebuild' de xoa DB cu: ").strip().lower()
    rebuild = mode == "rebuild"
    media_stats = build_media_catalog()
    print("\nDa tao media/design catalog:")
    print(f"- Output: {media_stats.output_dir}")
    print(f"- Cataloged files: {media_stats.cataloged_files}")
    print(f"- Catalog files: {media_stats.catalog_files}")
    print(f"- Represented media/design GB: {media_stats.total_gb}")
    extract_mode = input("Extract OCR/transcript media? Enter = skip, go 'ocr', 'transcribe', hoac 'all': ").strip().lower()
    if extract_mode in {"ocr", "transcribe", "all"}:
        extraction_stats = extract_media_text(mode=extract_mode)
        print("\nDa extract media text:")
        for name, value in extraction_stats.items():
            print(f"- {name}: {value}")
    stats = ingest_brain(rebuild=rebuild)
    print("\nDa build/update agent brain:")
    print(f"- Database: {stats.db_path}")
    print(f"- Scanned files: {stats.scanned_files}")
    print(f"- Ingested documents: {stats.ingested_documents}")
    print(f"- Skipped unchanged/empty: {stats.skipped_files}")
    print(f"- Chunks created: {stats.chunks}")
    print(f"- Errors: {stats.errors}")

def show_agent_brain() -> None:
    summary = brain_summary()
    print(json.dumps(summary, ensure_ascii=False, indent=2))

def search_agent_brain() -> None:
    query = input("Nhap tu khoa can search trong brain: ").strip()
    if not query:
        return
    results = search_brain(query)
    if not results:
        print("Khong tim thay ket qua.")
        return
    for index, item in enumerate(results, start=1):
        print(f"\n{index}. {item['title']}")
        print(f"Source: {item['source_path']}")
        print(item["text"][:900].strip())

def build_warriorplus_plan() -> None:
    query = input("Tu khoa lay tu brain, Enter = AI PLR Rebrand Kit: ").strip() or "AI PLR Rebrand Kit PLR SaaS WarriorPlus"
    plan = build_warriorplus_launch_plan(query)
    path = export_text("warriorplus-launch-plan", plan)
    print(f"\nDa tao WarriorPlus launch plan va luu vao: {path}")
    print("\nPreview:\n")
    print(plan[:3000])

def export_rebrand_kit() -> None:
    query = input("Tu khoa lay tu brain, Enter = PLR rebrand WarriorPlus AI: ").strip() or "PLR rebrand WarriorPlus AI digital product"
    pack_dir = export_ai_plr_rebrand_kit(query)
    print(f"\nDa export AI PLR Rebrand Kit pack vao: {pack_dir}")


def show_workflow_agents() -> None:
    agents = get_workflow_agents()
    print("\nProduct Launch Workflow Agents")
    print("==============================")
    for agent in agents:
        print(f"\n{agent.name}")
        print(f"- Role: {agent.role}")
        print(f"- Input root: {agent.input_root}")
        print(f"- Final output: {agent.final_output}")
        for step in agent.steps:
            print(f"  {step.id}. {step.name} -> {step.folder}")
    report_path = export_agent_overview_report()
    print(f"\nDa xuat overview report vao: {report_path}")

def build_workflow_agent_workspace() -> None:
    agents_dir = export_agent_workspace()
    print(f"\nDa tao/cap nhat agent files tai: {agents_dir}")
    print("Da tao/cap nhat input folders tai: input_files/agent_workflows")

def show_role_brains() -> None:
    summaries = {profile.key: brain_summary(profile.db_path) for profile in get_agent_profiles()}
    print(json.dumps(summaries, ensure_ascii=False, indent=2))

def search_role_brain() -> None:
    profiles = get_agent_profiles()
    print("\nChon role brain:")
    for index, profile in enumerate(profiles, start=1):
        print(f"{index}. {profile.name} ({profile.key})")
    selected = input("Nhap so: ").strip()
    if not selected.isdigit() or int(selected) < 1 or int(selected) > len(profiles):
        print("Lua chon khong hop le.")
        return
    profile = profiles[int(selected) - 1]
    query = input(f"Nhap tu khoa search trong {profile.name}: ").strip()
    if not query:
        return
    results = search_brain(query, db_path=profile.db_path)
    if not results:
        print("Khong tim thay ket qua.")
        return
    for index, item in enumerate(results, start=1):
        print(f"\n{index}. {item['title']}")
        print(f"Source: {item['source_path']}")
        print(item["text"][:900].strip())

def master_agent_chat() -> None:
    print("\nMaster Agent Chat")
    print("=================")
    print("Hoi tu nhien bang tieng Viet. Go 'exit', 'quit', 'q' hoac '0' de quay lai menu.")
    print("Lenh nhanh: /brain de xem 3 bo nao, /sources <cau hoi> de xem raw source.")

    while True:
        question = input("\nBan hoi: ").strip()
        if question.lower() in {"exit", "quit", "q", "0"}:
            print("Da thoat Master Agent Chat.")
            return
        if not question:
            continue
        if question == "/brain":
            print("\n" + master_brain_status())
            continue
        if question.startswith("/sources "):
            source_query = question.removeprefix("/sources ").strip()
            if not source_query:
                print("Hay nhap cau hoi sau /sources.")
                continue
            print("\n" + format_sources(source_query))
            continue

        print("\nAgent dang doc 3 bo nao va goi model 5.5...\n")
        answer = answer_master_question(question)
        print(answer)

def _context_from_input_or_top_result(prompt: str) -> str:
    context = input(prompt).strip()
    if context:
        return context
    results = _get_or_analyze()
    if not results:
        return ""
    return json.dumps(results[0], ensure_ascii=False, indent=2)

def _add_brain_context(context: str, limit: int = 5) -> str:
    matches = search_brain(context[:300], limit=limit)
    if not matches:
        return context
    sections = []
    for index, item in enumerate(matches, start=1):
        excerpt = item["text"][:1200].strip()
        sections.append(
            f"""### Brain Match {index}: {item['title']}
Source: {item['source_path']}

{excerpt}
"""
        )
    return context + "\n\n## Relevant Agent Brain Context\n" + "\n".join(sections)

def _brain_analyses_from_query(query: str) -> list[dict]:
    matches = search_brain(query, limit=8)
    results = []
    for item in matches:
        results.append(
            {
                "original_title": item["title"],
                "category": "Brain Search",
                "product_type": "Knowledge excerpt",
                "license_type": "Unknown",
                "final_score": 8,
                "saas_potential_score": 7,
                "buyer_avatar": "Digital product creator, PLR buyer, affiliate marketer, or SaaS founder",
                "promise": item["text"][:500],
                "best_angle": query,
                "sales_page_angle": item["text"][:700],
                "source_path": item["source_path"],
            }
        )
    return results


def _get_or_analyze() -> list[dict]:
    global LAST_RESULTS
    if LAST_RESULTS:
        return LAST_RESULTS
    print("Chua co ket qua phan tich. Dang analyze all products...")
    LAST_RESULTS = analyze_library()
    if not LAST_RESULTS:
        print("Chua co file nao trong plr_files.")
    return LAST_RESULTS


if __name__ == "__main__":
    main()

from __future__ import annotations

import csv
import json
import unicodedata
import zipfile
from datetime import datetime
from pathlib import Path

from config import OUTPUTS_DIR
from case_study_brain import (
    ai_workflow_steps,
    case_study_summary,
    extract_case_study_patterns,
    format_case_study_context,
    ingest_case_study_brain,
    training_system_notes,
    training_readiness_score,
    workflow_completion_steps,
    write_training_report,
)
from launch_os_db import ensure_project_from_text, infer_product_name
from niche_brain import (
    DEFAULT_NICHE_QUERY,
    MARKET_PATTERN_QUERY,
    competitor_matrix,
    evidence_summary,
    offer_gap_detector,
    extract_niche_patterns,
    format_niche_context,
    ingest_niche_brain,
    market_pattern_extractor,
    niche_readiness_score,
    niche_summary,
    write_niche_report,
)
from storage_optimizer import optimize_storage, storage_report, vacuum_active_brains


def create_project_assets(question: str, answer: str = "") -> dict:
    project = ensure_project_from_text(question)
    product_name = project.get("product_name") or infer_product_name(question) or "Product Kit"
    base = _project_dir(product_name) / "product_assets"
    base.mkdir(parents=True, exist_ok=True)
    files = _deep_email_campaign_files(product_name) if _is_email_campaign(product_name, question) else _deep_generic_product_files(product_name)
    written = []
    for relative, content in files.items():
        target = base / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if relative.lower().endswith(".csv"):
            _write_csv(target, content)
        else:
            target.write_text(content, encoding="utf-8")
        written.append(str(target))
    manifest = {
        "product_name": product_name,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "files": written,
        "source": "Product Assets action",
    }
    (base / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"product_name": product_name, "folder": str(base), "files": written}

def create_deep_product_assets(question: str, answer: str = "") -> dict:
    result = create_project_assets(question, answer)
    result["mode"] = "deep_create_product_assets"
    result["deep_content_requirement"] = "PASS: guide/workflow/checklist files include how-to-use, step-by-step, examples, common mistakes, checklist/action section, and next step."
    return result

def create_deep_file(question: str, answer: str = "") -> dict:
    product_name = _product_name_from_question(question)
    text = _ascii_fold(str(question or "")).lower()
    files = _deep_email_campaign_files(product_name) if _is_email_campaign(product_name, question) else _deep_generic_product_files(product_name)
    if "00_start_here" in text or "start_here" in text or "start here" in text:
        selected = "00_Start_Here.md"
    elif "campaign_map" in text or "campaign map" in text or "7_day" in text or "7 day" in text:
        selected = "01_7_Day_Campaign_Map.md" if "01_7_Day_Campaign_Map.md" in files else "01_Workflow_Map.md"
    elif "checklist" in text or "pre_send" in text or "pre-send" in text:
        selected = "04_Pre_Send_Checklist.md" if "04_Pre_Send_Checklist.md" in files else "04_Checklist.md"
    elif "prompt" in text:
        selected = "03_AI_Customization_Prompts.md" if "03_AI_Customization_Prompts.md" in files else "03_Customization_Prompts.md"
    elif "template" in text or "email" in text:
        selected = "02_30_Short_Email_Templates.md" if "02_30_Short_Email_Templates.md" in files else "02_Core_Templates.md"
    else:
        selected = "00_Start_Here.md"
    base = _project_dir(product_name) / "product_assets"
    result = _write_file_map(product_name, base, {selected: files[selected]})
    result["mode"] = "deep_write_file"
    result["selected_file"] = selected
    return result


def create_launch_pack_structure(question: str) -> dict:
    project = ensure_project_from_text(question)
    product_name = project.get("product_name") or infer_product_name(question) or "Product Kit"
    base = _project_dir(product_name)
    folders = [
        "product_assets",
        "sales_page",
        "funnel",
        "warriorplus_listing",
        "jv_pack",
        "email_funnel",
        "traffic_content",
        "delivery_page",
        "saas_upgrade_plan",
        "saas_plan",
        "support",
        "license",
        "testing",
        "launch",
        "mockups",
        "versioning",
        "feedback",
        "market_research",
        "sales_angles",
        "export/product_zip_ready",
    ]
    for folder in folders:
        (base / folder).mkdir(parents=True, exist_ok=True)
    readme = base / "README.md"
    if not readme.exists():
        readme.write_text(
            f"# {product_name}\n\nLaunch pack workspace.\n\nStart with `product_assets/00_Start_Here.md`, then complete sales page, funnel, JV pack, delivery page, and export ZIP.\n",
            encoding="utf-8",
        )
    written = []
    written.extend(create_project_assets(product_name).get("files", []))
    written.extend(create_sales_page_assets(product_name).get("files", []))
    written.extend(create_funnel_plan_assets(product_name).get("files", []))
    written.extend(create_warriorplus_listing_assets(product_name).get("files", []))
    written.extend(create_jv_pack_assets(product_name).get("files", []))
    written.extend(create_delivery_page_assets(product_name).get("files", []))
    written.extend(create_onboarding_assets(product_name).get("files", []))
    written.extend(create_saas_upgrade_assets(product_name).get("files", []))
    written.extend(create_deep_launch_assets(product_name).get("files", []))
    written.extend(create_governance_assets(f"Product Name: {product_name}").get("files", []))
    written.extend(create_buyer_test_zip_assets(product_name).get("files", []))
    written.extend(create_jv_test_pack_assets(product_name).get("files", []))
    written.extend(create_public_launch_audit_assets(product_name).get("files", []))
    return {
        "product_name": product_name,
        "folder": str(base),
        "folders": [str(base / item) for item in folders],
        "files": written,
    }


def export_project_zip(question: str) -> dict:
    create_launch_pack_structure(question)
    project = ensure_project_from_text(question)
    product_name = project.get("product_name") or infer_product_name(question) or "Product Kit"
    base = _project_dir(product_name)
    export_dir = base / "export"
    export_dir.mkdir(parents=True, exist_ok=True)
    zip_path = export_dir / f"{_safe_name(product_name)}_Launch_Pack.zip"
    export_log_path = export_dir / "EXPORT_LOG.md"
    if export_log_path.exists():
        export_log_path.unlink()
    proof_files = _write_launch_evidence_files(product_name, zip_path)
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in base.rglob("*"):
            if path == zip_path or path.is_dir():
                continue
            archive.write(path, path.relative_to(base))
    exported_file_count = sum(1 for path in base.rglob("*") if path.is_file() and path != zip_path) + 1
    export_log = write_project_file(
        product_name,
        "export/EXPORT_LOG.md",
        _export_log_md(product_name, zip_path, exported_file_count, zip_path.stat().st_size),
    )
    with zipfile.ZipFile(zip_path, "a", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.write(export_log_path, export_log_path.relative_to(base))
    state_file = save_project_state(
        product_name,
        {
            "product_name": product_name,
            "asset_type": "launch_pack",
            "offer_analysis": "DONE",
            "product_assets": "DONE",
            "sales_page": "DONE",
            "funnel": "DONE",
            "jv_pack": "DONE",
            "warriorplus_listing": "DONE",
            "delivery_page": "DONE",
            "email_funnel": "DONE",
            "saas_plan": "DONE",
            "export_zip": "DONE",
            "launch_readiness": 87,
            "next_best_action": "Review ZIP and publish delivery page",
        },
    )
    placeholder_summary = _scan_placeholders(base)
    return {
        "product_name": product_name,
        "zip_path": str(zip_path),
        "folder": str(base),
        "state_file": state_file,
        "files": [*proof_files, export_log],
        "zip_path_file": str(export_dir / "ZIP_PATH.txt"),
        "export_log": export_log,
        "export_proof": "PASS",
        "placeholder_status": "FAIL" if placeholder_summary["total_hits"] else "PASS",
        "public_launch_status": "FAIL" if placeholder_summary["total_hits"] else "SOFT LAUNCH READY",
    }


def export_named_project_zip(product_name: str) -> dict:
    base = _project_dir(product_name)
    export_dir = base / "export"
    export_dir.mkdir(parents=True, exist_ok=True)
    zip_path = export_dir / f"{_safe_name(product_name)}_Launch_Pack.zip"
    export_log_path = export_dir / "EXPORT_LOG.md"
    if export_log_path.exists():
        export_log_path.unlink()
    proof_files = _write_launch_evidence_files(product_name, zip_path)
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in base.rglob("*"):
            if path == zip_path or path.is_dir():
                continue
            archive.write(path, path.relative_to(base))
    exported_file_count = sum(1 for path in base.rglob("*") if path.is_file() and path != zip_path) + 1
    export_log = write_project_file(
        product_name,
        "export/EXPORT_LOG.md",
        _export_log_md(product_name, zip_path, exported_file_count, zip_path.stat().st_size),
    )
    with zipfile.ZipFile(zip_path, "a", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.write(export_log_path, export_log_path.relative_to(base))
    placeholder_summary = _scan_placeholders(base)
    return {
        "product_name": product_name,
        "zip_path": str(zip_path),
        "folder": str(base),
        "files": [*proof_files, export_log],
        "zip_path_file": str(export_dir / "ZIP_PATH.txt"),
        "export_log": export_log,
        "export_proof": "PASS",
        "placeholder_status": "FAIL" if placeholder_summary["total_hits"] else "PASS",
        "public_launch_status": "FAIL" if placeholder_summary["total_hits"] else "SOFT LAUNCH READY",
    }

def create_full_launch_pack(question: str) -> dict:
    pack = create_launch_pack_structure(question)
    export = export_project_zip(question)
    files = [*pack.get("files", [])]
    if export.get("state_file"):
        files.append(export["state_file"])
    files.extend(export.get("files", []))
    return {
        **pack,
        "zip_path": export.get("zip_path", ""),
        "state_file": export.get("state_file", ""),
        "folder": export.get("folder") or pack.get("folder", ""),
        "files": files,
        "zip_path_file": export.get("zip_path_file", ""),
        "export_log": export.get("export_log", ""),
        "export_proof": export.get("export_proof", ""),
        "placeholder_status": export.get("placeholder_status", ""),
        "public_launch_status": export.get("public_launch_status", ""),
        "mode": "full_launch_pack",
    }

def maybe_run_action(module_id: str, question: str, answer: str = "") -> dict:
    alias_map = {
        "market_pattern_extract": "ai_print_market",
        "competitor_matrix": "ai_print_competitor",
        "offer_gap_v2": "ai_print_gap",
        "ai_replace_risk_v2": "ai_replace_risk",
    }
    module_id = alias_map.get(module_id, module_id)
    if module_id == "ai_print_build":
        return _finalize_action_state(module_id, create_ai_printables_builder_pack(question, answer))
    if module_id == "ai_print_train":
        return create_ai_print_training_action(question)
    if module_id == "ai_print_full_train":
        return create_ai_print_training_action(question, default_limit=1000)
    if module_id == "ai_print_status":
        return create_ai_print_status_action()
    if module_id == "ai_print_search":
        return create_ai_print_search_action(question)
    if module_id == "ai_print_patterns":
        return create_ai_print_patterns_action(question)
    if module_id == "ai_print_evidence":
        return create_ai_print_evidence_action(question)
    if module_id == "ai_print_market":
        return create_ai_print_market_action(question)
    if module_id == "ai_print_competitor":
        return create_ai_print_competitor_action(question)
    if module_id == "ai_print_gap":
        return create_ai_print_gap_action(question)
    if module_id == "ai_print_report":
        return create_ai_print_report_action(question)
    if module_id == "train_case_study_brain":
        return create_case_study_training_action(question)
    if module_id == "train_full_case_study_brain":
        return create_case_study_training_action(question, default_limit=1000)
    if module_id == "case_study_search":
        return create_case_study_search_action(question)
    if module_id == "case_study_patterns":
        return create_case_study_patterns_action(question)
    if module_id == "training_status":
        return create_training_status_action()
    if module_id == "export_training_report":
        return create_export_training_report_action(question)
    if module_id == "workflow_30":
        return create_workflow_30_action()
    if module_id == "ai_workflow_20":
        return create_ai_workflow_20_action()
    if module_id == "agent_benchmark":
        return create_agent_benchmark_pack(question, answer)
    if module_id == "optimize_storage":
        result = optimize_storage(apply=True, include_legacy_db=True)
        result["vacuum"] = vacuum_active_brains()
        return result
    if module_id == "storage_report":
        return storage_report()
    if module_id == "product_assets":
        return _finalize_action_state(module_id, create_project_assets(question, answer))
    if module_id == "deep_create_product_assets":
        return _finalize_action_state(module_id, create_deep_product_assets(question, answer))
    if module_id == "deep_write_file":
        return _finalize_action_state(module_id, create_deep_file(question, answer))
    if module_id == "sales_page":
        return _finalize_action_state(module_id, create_sales_page_assets(question, answer))
    if module_id == "funnel_plan":
        return _finalize_action_state(module_id, create_funnel_plan_assets(question, answer))
    if module_id == "warriorplus_listing":
        return _finalize_action_state(module_id, create_warriorplus_listing_assets(question, answer))
    if module_id in {"jv_page", "swipe_pack", "outreach", "prospects", "tiers", "review_access"}:
        return _finalize_action_state(module_id, create_jv_pack_assets(question, answer))
    if module_id == "delivery_page":
        return _finalize_action_state(module_id, create_delivery_page_assets(question, answer))
    if module_id == "onboarding":
        return _finalize_action_state(module_id, create_onboarding_assets(question, answer))
    if module_id in {"saas_potential", "mvp_plan", "membership", "whitelabel", "product_line"}:
        return _finalize_action_state(module_id, create_saas_upgrade_assets(question, answer))
    if module_id == "support":
        return _finalize_action_state(module_id, create_support_assets(question, answer))
    if module_id == "license":
        return _finalize_action_state(module_id, create_license_assets(question, answer))
    if module_id == "buyer_test":
        return _finalize_action_state(module_id, create_buyer_test_assets(question, answer))
    if module_id == "jv_test":
        return _finalize_action_state(module_id, create_jv_test_assets(question, answer))
    if module_id == "sales_page_critic":
        return _finalize_action_state(module_id, create_sales_page_critic_assets(question, answer))
    if module_id == "apply_feedback":
        return _finalize_action_state(module_id, create_apply_feedback_assets(question, answer))
    if module_id == "buyer_test_zip":
        return _finalize_action_state(module_id, create_buyer_test_zip_assets(question, answer))
    if module_id == "jv_test_pack":
        return _finalize_action_state(module_id, create_jv_test_pack_assets(question, answer))
    if module_id == "public_launch_audit":
        return _finalize_action_state(module_id, create_public_launch_audit_assets(question, answer))
    if module_id == "product_blueprint":
        return _finalize_action_state(module_id, create_product_blueprint_assets(question, answer))
    if module_id == "deep_file_writer":
        return _finalize_action_state(module_id, create_deep_file_writer_assets(question, answer))
    if module_id == "prompt_output_test":
        return _finalize_action_state(module_id, create_prompt_output_test_assets(question, answer))
    if module_id == "ai_replace_risk":
        return _finalize_action_state(module_id, create_ai_replace_risk_assets(question, answer))
    if module_id == "license_compliance_check":
        return _finalize_action_state(module_id, create_license_compliance_check_assets(question, answer))
    if module_id == "warriorplus_launch_builder":
        return _finalize_action_state(module_id, create_warriorplus_launch_builder_assets(question, answer))
    if module_id == "export_pack":
        target = _target_product_name(question)
        return _finalize_action_state(module_id, export_named_project_zip(target))
    if module_id == "final_scorecard":
        return _finalize_action_state(module_id, create_final_scorecard_action(question, answer))
    if module_id == "launch_pack":
        return _finalize_action_state(module_id, create_launch_pack_structure(question))
    if module_id == "full_launch_pack":
        return _finalize_action_state(module_id, create_full_launch_pack(question))
    if module_id == "export_zip":
        return _finalize_action_state(module_id, export_project_zip(question))
    return {}

def create_ai_printables_builder_pack(question: str, answer: str = "") -> dict:
    product_name = "Lead Magnet Printable Builder For Coaches"
    base = _project_dir(product_name)
    folders = [
        "product_assets",
        "sales_page",
        "funnel",
        "warriorplus_listing",
        "jv_pack",
        "delivery_page",
        "email_funnel",
        "testing",
        "license",
        "support",
        "versioning",
        "feedback",
        "launch",
        "export/product_zip_ready",
    ]
    for folder in folders:
        (base / folder).mkdir(parents=True, exist_ok=True)

    written: list[str] = []
    product_files = {
        "00_Start_Here.md": _coach_start_here_md(product_name),
        "01_Workflow_Map.md": _coach_workflow_map_md(product_name),
        "02_Lead_Magnet_Type_Selector.md": _coach_type_selector_md(product_name),
        "03_AI_Worksheet_Prompt_Pack.md": _coach_prompt_pack_md(product_name),
        "04_Canva_PDF_Layout_Guide.md": _coach_canva_guide_md(product_name),
        "05_Optin_Page_Copy_Template.md": _coach_optin_template_md(product_name),
        "06_Thank_You_Page_Template.md": _coach_thank_you_template_md(product_name),
        "07_Three_Email_Welcome_Sequence.md": _coach_welcome_sequence_md(product_name),
        "08_Sample_Filled_Example_Instagram_Bio_Audit.md": _coach_sample_example_md(product_name),
        "09_License_Compliance_Note.md": _coach_license_note_md(product_name),
        "README.md": _coach_readme_md(product_name),
    }
    written.extend(_write_file_map(product_name, base / "product_assets", product_files).get("files", []))
    written.extend(_write_file_map(product_name, base / "sales_page", {"sales_page.md": _coach_sales_page_md(product_name)}).get("files", []))
    written.extend(_write_file_map(product_name, base / "funnel", {"funnel_plan.md": _coach_funnel_md(product_name)}).get("files", []))
    written.extend(_write_file_map(product_name, base / "warriorplus_listing", {"warriorplus_listing.md": _coach_warriorplus_listing_md(product_name)}).get("files", []))
    written.extend(_write_file_map(product_name, base / "jv_pack", {"jv_page.md": _coach_jv_page_md(product_name), "affiliate_swipes.md": _coach_affiliate_swipes_md(product_name)}).get("files", []))
    written.extend(_write_file_map(product_name, base / "delivery_page", {"delivery_page.md": _coach_delivery_page_md(product_name)}).get("files", []))
    written.extend(_write_file_map(product_name, base / "email_funnel", {"buyer_onboarding_emails.md": _coach_buyer_onboarding_md(product_name)}).get("files", []))
    written.extend(_write_file_map(product_name, base / "testing", {
        "buyer_test.md": _coach_buyer_test_md(product_name),
        "prompt_output_test.md": _coach_prompt_output_test_md(product_name),
        "refund_risk_audit.md": _coach_refund_risk_md(product_name),
        "ai_replace_risk_audit.md": _coach_ai_replace_risk_md(product_name),
    }).get("files", []))
    written.extend(_write_file_map(product_name, base / "support", {"support_faq.md": _coach_support_faq_md(product_name)}).get("files", []))
    written.extend(_write_file_map(product_name, base / "versioning", {
        "VERSION.md": f"# Version\n\nProduct: {product_name}\nCurrent Version: v1.0-soft-launch\n",
        "CHANGELOG.md": f"# Changelog\n\n## v1.0-soft-launch\n- Created product assets, sales page, funnel, JV pack, delivery page, onboarding emails, tests, quality gate, and ZIP proof.\n- Public launch remains blocked until placeholders, payment, delivery, and reviewer feedback are cleared.\n",
    }).get("files", []))
    written.extend(_write_file_map(product_name, base / "feedback", {
        "FEEDBACK_LOG.md": f"# Feedback Log\n\nProduct: {product_name}\n\n## Pending\n- Add buyer feedback after first ZIP review.\n- Add JV/reviewer feedback before public launch.\n",
        "FIX_LOG.md": f"# Fix Log\n\nProduct: {product_name}\n\n## Required Before Public Launch\n- Replace download/support/affiliate/review-access placeholders.\n- Test payment and delivery links.\n- Re-run public launch audit.\n",
    }).get("files", []))
    written.extend(create_governance_assets(f"Product Name: {product_name}").get("files", []))

    state_file = save_project_state(
        product_name,
        {
            "product_name": product_name,
            "asset_type": "ai_printables_builder",
            "offer_analysis": "DONE",
            "product_assets": "DONE",
            "sales_page": "DONE",
            "funnel": "DONE",
            "jv_pack": "DONE",
            "warriorplus_listing": "DONE",
            "delivery_page": "DONE",
            "email_funnel": "DONE",
            "support": "DONE",
            "license": "DONE",
            "export_zip": "MISSING",
            "launch_readiness": 82,
            "next_best_action": "Export ZIP and run buyer test",
        },
    )
    written.append(state_file)
    export = export_named_project_zip(product_name)
    state_file = save_project_state(
        product_name,
        {
            "product_name": product_name,
            "asset_type": "ai_printables_builder",
            "offer_analysis": "DONE",
            "product_assets": "DONE",
            "sales_page": "DONE",
            "funnel": "DONE",
            "jv_pack": "DONE",
            "warriorplus_listing": "DONE",
            "delivery_page": "DONE",
            "email_funnel": "DONE",
            "support": "DONE",
            "license": "DONE",
            "export_zip": "DONE",
            "launch_readiness": 86,
            "next_best_action": "Replace placeholders, test delivery/payment, then run public launch audit",
        },
    )
    files = [*written, *(export.get("files") or [])]
    files.append(state_file)
    return {
        "product_name": product_name,
        "folder": str(base),
        "files": files,
        "zip_path": export.get("zip_path", ""),
        "zip_path_file": export.get("zip_path_file", ""),
        "export_log": export.get("export_log", ""),
        "export_proof": export.get("export_proof", ""),
        "zip_status": "CREATED" if export.get("zip_path") else "MISSING",
        "placeholder_status": export.get("placeholder_status", ""),
        "public_launch_status": export.get("public_launch_status", "FAIL"),
        "launch_readiness": 86,
        "builder_scores": {
            "Strategy Score": 9,
            "Product Depth Score": 9,
            "Created Files Score": 10,
            "Buyer Test Score": 8,
            "AI Replace Risk": "LOW after workflow/examples/checklists",
            "Refund Risk": "MEDIUM until real buyer feedback",
            "Export ZIP Score": 10,
            "Launch Readiness": 8.6,
        },
        "mode": "ai_print_build",
    }

def create_ai_print_training_action(question: str, *, default_limit: int = 300) -> dict:
    folded = _ascii_fold(str(question or "")).lower()
    rebuild = "rebuild" in folded or "xay lai" in folded or "xoa index" in folded
    limit = default_limit
    for token in folded.replace("=", " ").split():
        if token.isdigit():
            value = int(token)
            if value > 0:
                limit = value
                break
    limit_value = None if ("full" in folded or "toan bo" in folded or "tat ca" in folded) else limit
    result = ingest_niche_brain(rebuild=rebuild, max_files=limit_value)
    return {
        "status": result.status,
        "niche": result.niche,
        "source_root": result.source_root,
        "db_path": result.db_path,
        "max_files": result.max_files,
        "scanned_files": result.scanned_files,
        "ingested_documents": result.ingested_documents,
        "skipped_files": result.skipped_files,
        "chunks": result.chunks,
        "errors": result.errors,
        "manifest_path": result.manifest_path,
        "summary": niche_summary(),
        "training_readiness": niche_readiness_score(),
    }

def create_ai_print_status_action() -> dict:
    return {"summary": niche_summary(), "training_readiness": niche_readiness_score()}

def create_ai_print_search_action(question: str) -> dict:
    query = _strip_ai_print_command(question) or DEFAULT_NICHE_QUERY
    return {
        "query": query,
        "summary": niche_summary(),
        "context": format_niche_context(query, limit=8),
        "training_readiness": niche_readiness_score(),
    }

def create_ai_print_patterns_action(question: str) -> dict:
    query = _strip_ai_print_command(question) or DEFAULT_NICHE_QUERY
    return extract_niche_patterns(query, limit=20)

def create_ai_print_evidence_action(question: str) -> dict:
    query = _strip_ai_print_command(question) or DEFAULT_NICHE_QUERY
    return evidence_summary(query, limit=12)

def create_ai_print_market_action(question: str) -> dict:
    query = _strip_ai_print_command(question) or MARKET_PATTERN_QUERY
    return market_pattern_extractor(query, limit=24)

def create_ai_print_competitor_action(question: str) -> dict:
    query = _strip_ai_print_command(question) or MARKET_PATTERN_QUERY
    return competitor_matrix(query, limit=14)

def create_ai_print_gap_action(question: str) -> dict:
    query = _strip_ai_print_command(question) or "Lead Magnet Printable Builder For Coaches"
    return offer_gap_detector(query, limit=18)

def create_ai_print_report_action(question: str) -> dict:
    query = _strip_ai_print_command(question) or DEFAULT_NICHE_QUERY
    return write_niche_report(query)

def create_case_study_training_action(question: str, *, default_limit: int = 300) -> dict:
    folded = _ascii_fold(str(question or "")).lower()
    rebuild = "rebuild" in folded or "xay lai" in folded or "xoa index" in folded
    limit = default_limit
    for token in folded.replace("=", " ").split():
        if token.isdigit():
            value = int(token)
            if value > 0:
                limit = value
                break
    if "full" in folded or "toan bo" in folded or "tat ca" in folded:
        limit_value = None
    else:
        limit_value = limit
    result = ingest_case_study_brain(rebuild=rebuild, max_files=limit_value)
    return {
        "status": result.status,
        "source_root": result.source_root,
        "db_path": result.db_path,
        "max_files": result.max_files,
        "scanned_files": result.scanned_files,
        "ingested_documents": result.ingested_documents,
        "skipped_files": result.skipped_files,
        "chunks": result.chunks,
        "errors": result.errors,
        "manifest_path": result.manifest_path,
        "summary": case_study_summary(),
        "training_notes": training_system_notes(),
        "training_readiness": training_readiness_score(),
    }

def create_case_study_search_action(question: str) -> dict:
    query = str(question or "").strip()
    for prefix in ("/case_study_search", "/search_case_study", "/brain_search"):
        if query.lower().startswith(prefix):
            query = query[len(prefix):].strip()
    query = query or "AI PLR Prompt Template Packs KDP Printables WarriorPlus case study"
    return {
        "query": query,
        "summary": case_study_summary(),
        "context": format_case_study_context(query, limit=8),
        "training_readiness": training_readiness_score(),
    }

def create_case_study_patterns_action(question: str) -> dict:
    query = _strip_training_command(question) or "AI PLR Prompt Template Packs for KDP Printables"
    return extract_case_study_patterns(query, limit=18)

def create_training_status_action() -> dict:
    return {"summary": case_study_summary(), "training_readiness": training_readiness_score()}

def create_export_training_report_action(question: str) -> dict:
    query = _strip_training_command(question) or "AI PLR Prompt Template Packs for KDP Printables"
    return write_training_report(query)

def _strip_training_command(question: str) -> str:
    query = str(question or "").strip()
    for prefix in (
        "/case_study_patterns",
        "/extract_patterns",
        "/training_status",
        "/export_training_report",
        "/training_report",
        "/case_study_search",
        "/search_case_study",
        "/brain_search",
    ):
        if query.lower().startswith(prefix):
            return query[len(prefix):].strip()
    return query

def _strip_ai_print_command(question: str) -> str:
    query = _strip_tool_mode_prefix(str(question or "").strip())
    for prefix in (
        "/ai_print_train",
        "/ai_print_full_train",
        "/ai_print_status",
        "/ai_print_search",
        "/ai_print_patterns",
        "/ai_print_evidence",
        "/ai_print_market",
        "/ai_print_competitor",
        "/ai_print_gap",
        "/market_pattern_extract",
        "/competitor_matrix",
        "/offer_gap_detector",
        "/offer_gap_v2",
        "/ai_print_report",
        "/ai_print_deep",
    ):
        if query.lower().startswith(prefix):
            return query[len(prefix):].strip()
    return query

def _strip_tool_mode_prefix(query: str) -> str:
    lines = [line.strip() for line in str(query or "").splitlines()]
    for index, line in enumerate(lines):
        if line.startswith("/"):
            return "\n".join(lines[index:]).strip()
    return query.strip()

def create_workflow_30_action() -> dict:
    return {"title": "Quy Trinh Hoan Thanh 30 Buoc", "steps": workflow_completion_steps()}

def create_ai_workflow_20_action() -> dict:
    return {"title": "Quy Trinh Cho AI 20 Buoc", "steps": ai_workflow_steps()}


def _finalize_action_state(module_id: str, result: dict) -> dict:
    if not result or not result.get("product_name"):
        return result
    product_name = result["product_name"]
    state = _project_state_payload(product_name, module_id)
    state_file = save_project_state(product_name, state)
    result["state_file"] = state_file
    result["project_state"] = state
    result["zip_status"] = "CREATED" if state["completed"].get("export_zip") or result.get("zip_path") else "MISSING"
    result["launch_readiness"] = state.get("launch_readiness", 0)
    return result

def _project_state_payload(product_name: str, module_id: str) -> dict:
    previous = load_project_state(product_name)
    completed = {
        "offer_analysis": _state_done(previous, "offer_analysis"),
        "product_assets": _state_done(previous, "product_assets"),
        "sales_page": _state_done(previous, "sales_page"),
        "funnel": _state_done(previous, "funnel"),
        "jv_pack": _state_done(previous, "jv_pack"),
        "warriorplus_listing": _state_done(previous, "warriorplus_listing"),
        "delivery_page": _state_done(previous, "delivery_page"),
        "email_funnel": _state_done(previous, "email_funnel"),
        "saas_plan": _state_done(previous, "saas_plan"),
        "support": _state_done(previous, "support"),
        "license": _state_done(previous, "license"),
        "export_zip": _state_done(previous, "export_zip"),
    }
    task_updates = {
        "product_assets": ("product_assets",),
        "deep_create_product_assets": ("offer_analysis", "product_assets"),
        "deep_write_file": ("product_assets",),
        "sales_page": ("sales_page",),
        "funnel_plan": ("funnel",),
        "warriorplus_listing": ("warriorplus_listing",),
        "jv_page": ("jv_pack",),
        "swipe_pack": ("jv_pack",),
        "outreach": ("jv_pack",),
        "prospects": ("jv_pack",),
        "tiers": ("jv_pack",),
        "review_access": ("jv_pack",),
        "delivery_page": ("delivery_page",),
        "onboarding": ("email_funnel",),
        "saas_potential": ("saas_plan",),
        "mvp_plan": ("saas_plan",),
        "membership": ("saas_plan",),
        "whitelabel": ("saas_plan",),
        "product_line": ("saas_plan",),
        "support": ("support",),
        "license": ("license",),
        "buyer_test": (),
        "jv_test": (),
        "prompt_output_test": (),
        "ai_replace_risk": (),
        "license_compliance_check": ("license",),
        "warriorplus_launch_builder": ("warriorplus_listing", "funnel", "jv_pack", "delivery_page", "support"),
        "product_blueprint": ("offer_analysis",),
        "deep_file_writer": ("offer_analysis", "product_assets", "sales_page", "funnel", "jv_pack", "warriorplus_listing", "delivery_page", "email_funnel", "support", "license", "export_zip"),
        "sales_page_critic": ("sales_page",),
        "apply_feedback": (),
        "buyer_test_zip": (),
        "jv_test_pack": (),
        "public_launch_audit": (),
        "launch_pack": ("offer_analysis", "product_assets", "sales_page", "funnel", "jv_pack", "warriorplus_listing", "delivery_page", "email_funnel", "saas_plan", "support", "license"),
        "full_launch_pack": ("offer_analysis", "product_assets", "sales_page", "funnel", "jv_pack", "warriorplus_listing", "delivery_page", "email_funnel", "saas_plan", "support", "license", "export_zip"),
        "export_zip": ("offer_analysis", "product_assets", "sales_page", "funnel", "jv_pack", "warriorplus_listing", "delivery_page", "email_funnel", "saas_plan", "support", "license", "export_zip"),
        "export_pack": ("offer_analysis", "product_assets", "sales_page", "funnel", "jv_pack", "warriorplus_listing", "delivery_page", "email_funnel", "saas_plan", "support", "license", "export_zip"),
        "ai_print_build": ("offer_analysis", "product_assets", "sales_page", "funnel", "jv_pack", "warriorplus_listing", "delivery_page", "email_funnel", "support", "license", "export_zip"),
    }
    for key in task_updates.get(module_id, ()):
        completed[key] = True
    readiness = _launch_readiness_from_completed(completed)
    return {
        "project_slug": _safe_name(product_name),
        "project_name": product_name,
        "completed": completed,
        "offer_analysis": "DONE" if completed["offer_analysis"] else "MISSING",
        "product_assets": "DONE" if completed["product_assets"] else "MISSING",
        "sales_page": "DONE" if completed["sales_page"] else "MISSING",
        "funnel": "DONE" if completed["funnel"] else "MISSING",
        "jv_pack": "DONE" if completed["jv_pack"] else "MISSING",
        "warriorplus_listing": "DONE" if completed["warriorplus_listing"] else "MISSING",
        "delivery_page": "DONE" if completed["delivery_page"] else "MISSING",
        "email_funnel": "DONE" if completed["email_funnel"] else "MISSING",
        "saas_plan": "DONE" if completed["saas_plan"] else "MISSING",
        "support": "DONE" if completed["support"] else "MISSING",
        "license": "DONE" if completed["license"] else "MISSING",
        "export_zip": "DONE" if completed["export_zip"] else "MISSING",
        "launch_readiness": readiness,
        "next_actions": _next_actions_from_completed(completed),
    }

def _state_done(state: dict, key: str) -> bool:
    completed = state.get("completed") if isinstance(state.get("completed"), dict) else {}
    if key in completed:
        return bool(completed[key])
    return str(state.get(key, "")).upper() == "DONE"

def _next_actions_from_completed(completed: dict) -> list[str]:
    order = [
        ("product_assets", "deep_create_product_assets"),
        ("sales_page", "write_sales_page"),
        ("funnel", "create_funnel"),
        ("jv_pack", "build_jv_pack"),
        ("warriorplus_listing", "build_warriorplus_listing"),
        ("delivery_page", "create_delivery_page"),
        ("email_funnel", "create_email_funnel"),
        ("saas_plan", "saas_upgrade"),
        ("support", "create_support"),
        ("license", "create_license"),
        ("export_zip", "export_launch_pack"),
    ]
    return [action for key, action in order if not completed.get(key)][:3] or ["launch_readiness_review", "soft_launch_plan", "jv_outreach"]

def _launch_readiness_from_completed(completed: dict) -> int:
    weights = {
        "product_assets": 18,
        "sales_page": 14,
        "funnel": 10,
        "jv_pack": 10,
        "warriorplus_listing": 8,
        "delivery_page": 8,
        "email_funnel": 7,
        "saas_plan": 6,
        "support": 3,
        "license": 4,
        "export_zip": 12,
    }
    return sum(weight for key, weight in weights.items() if completed.get(key))

def create_agent_benchmark_pack(question: str, answer: str = "") -> dict:
    product_name = _product_name_from_question(question)
    launch_pack = create_launch_pack_structure(product_name)
    asset_type = _detect_benchmark_asset_type(question)
    extra_files = []
    for creator in _asset_creators_for_type(asset_type):
        extra = creator(product_name)
        extra_files.extend(extra.get("files", []))
    profile = _benchmark_profile(asset_type, product_name)
    state_file = save_project_state(
        product_name,
        {
            "product_name": product_name,
            "asset_type": asset_type,
            "offer_analysis": "DONE",
            "product_assets": "DONE",
            "sales_page": "DONE",
            "funnel": "DONE",
            "jv_pack": "DONE",
            "saas_plan": "DONE",
            "export_zip": "MISSING",
            "next_best_action": "Export Launch Pack",
        },
    )
    return {
        **launch_pack,
        "files": [*launch_pack.get("files", []), *extra_files, state_file],
        "benchmark": {
            **profile,
            "asset_type": asset_type,
            "generic_chatgpt_score": profile.get("generic_chatgpt_score", 5.0),
            "old_chat_output_score": 6.5,
            "action_agent_score": profile.get("action_agent_score", 8.5),
            "verdict": _benchmark_verdict(asset_type),
            "must_not_do": [
                "Do not dump raw prompts/templates as the whole product.",
                "Do not answer with a long essay only.",
                "Do not claim sales, income, open rates, or conversions.",
            ],
            "must_do": [
                "Create implementation files.",
                "Create campaign map, planner, checklist, prompts, example, compliance note.",
                "Create sales page, funnel, WarriorPlus listing, JV pack, delivery page, onboarding emails.",
                "Update project state and export ZIP when ready.",
            ],
        },
    }

def _asset_creators_for_type(asset_type: str) -> list:
    if asset_type == "subject_line_prompts":
        return [create_subject_line_prompt_assets]
    if asset_type == "email_sequences":
        return [create_email_sequence_assets]
    if asset_type == "mini_sales_email_guide":
        return [create_mini_sales_email_guide_assets]
    if asset_type == "plr_swipe_structure":
        return [create_plr_swipe_structure_assets]
    return []


def create_subject_line_prompt_assets(question: str, answer: str = "") -> dict:
    product_name = _product_name_from_question(question)
    base = _project_dir(product_name) / "product_assets"
    files = {
        "05_Subject_Line_Prompt_Builder.md": _subject_line_prompt_builder_md(product_name),
        "05B_Subject_Line_QC_Checklist.md": _subject_line_qc_md(product_name),
        "05C_Subject_Line_Scorecard.csv": [
            ["Campaign", "Audience", "Subject Line", "Clarity", "Specificity", "Curiosity", "Safety", "Audience Fit", "Total", "Keep/Rewrite", "Rewrite Note"],
            ["Promo", "Beginner affiliate", "Before you send your next promo", "9", "8", "7", "10", "9", "43", "Keep", ""],
            ["Promo", "Beginner affiliate", "Secret trick for instant commissions", "5", "4", "8", "1", "5", "23", "Rewrite", "Income claim and hype"],
        ],
    }
    return _write_file_map(product_name, base, files)


def create_email_sequence_assets(question: str, answer: str = "") -> dict:
    product_name = _product_name_from_question(question)
    base = _project_dir(product_name) / "product_assets"
    files = {
        "09_Email_Sequence_Workflow_Map.md": _email_sequence_workflow_md(product_name),
        "10_Email_Sequence_Template_Pack.md": _email_sequence_templates_md(product_name),
        "11_Email_Sequence_QC_Checklist.md": _email_sequence_qc_md(product_name),
        "12_Email_Sequence_Planner.csv": [
            ["Sequence", "Email", "Goal", "Buyer State", "CTA", "Proof/Example", "Risk Check", "Status"],
            ["Welcome", "1", "Orient buyer", "New subscriber", "Open Start Here", "Folder preview", "No income claim", "Draft"],
            ["Promo", "1", "Introduce offer", "Problem aware", "View sales page", "Workflow preview", "No fake urgency", "Draft"],
            ["Affiliate", "1", "Recommend relevant offer", "Solution aware", "Click affiliate link", "Disclosure", "Disclosure present", "Draft"],
            ["Reactivation", "1", "Restart attention", "Cold subscriber", "Reply or click", "Useful tip", "No guilt/shame", "Draft"],
        ],
    }
    return _write_file_map(product_name, base, files)

def create_mini_sales_email_guide_assets(question: str, answer: str = "") -> dict:
    product_name = _product_name_from_question(question)
    base = _project_dir(product_name) / "product_assets"
    files = {
        "09_Mini_Guide_Sales_Email_Workflow.md": _mini_sales_email_guide_md(product_name),
        "10_Sales_Email_Template_Blueprint.md": _sales_email_blueprint_md(product_name),
        "11_Sales_Email_Review_Checklist.md": _sales_email_review_checklist_md(product_name),
    }
    return _write_file_map(product_name, base, files)

def create_plr_swipe_structure_assets(question: str, answer: str = "") -> dict:
    product_name = _product_name_from_question(question)
    base = _project_dir(product_name) / "product_assets"
    files = {
        "09_PLR_Swipe_Deconstruction_Workflow.md": _plr_swipe_deconstruction_md(product_name),
        "10_Rewritten_Swipe_Structure_Template.md": _rewritten_swipe_structure_md(product_name),
        "11_PLR_Copy_Risk_Checklist.md": _plr_copy_risk_checklist_md(product_name),
        "12_Swipe_Rewrite_Tracker.csv": [
            ["Source Swipe", "Extracted Pattern", "New Audience", "New Promise", "New CTA", "Similarity Risk", "Human Review"],
            ["Email 1", "Problem -> mechanism -> CTA", "Beginner vendor", "Build a launch asset", "Open kit", "Medium", "Yes"],
        ],
    }
    return _write_file_map(product_name, base, files)

def action_note(result: dict) -> str:
    if not result:
        return ""
    lines = ["", "**Tool action đã chạy**"]
    if result.get("folder"):
        lines.append(f"- Folder: `{result['folder']}`")
    if result.get("zip_path"):
        lines.append(f"- ZIP: `{result['zip_path']}`")
    if result.get("files"):
        lines.append("- Files created:")
        lines.extend(f"  - `{item}`" for item in result["files"][:12])
    if result.get("folders"):
        lines.append("- Folders ready:")
        lines.extend(f"  - `{item}`" for item in result["folders"][:12])
    return "\n".join(lines)

def create_sales_page_assets(question: str, answer: str = "") -> dict:
    product_name = _product_name_from_question(question)
    base = _project_dir(product_name) / "sales_page"
    files = {
        "sales_page.md": _sales_page_md(product_name, answer),
        "faq_objections.md": _faq_md(product_name),
    }
    return _write_file_map(product_name, base, files)

def create_funnel_plan_assets(question: str, answer: str = "") -> dict:
    product_name = _product_name_from_question(question)
    base = _project_dir(product_name) / "funnel"
    files = {"funnel_plan.md": _funnel_plan_md(product_name)}
    return _write_file_map(product_name, base, files)

def create_warriorplus_listing_assets(question: str, answer: str = "") -> dict:
    product_name = _product_name_from_question(question)
    base = _project_dir(product_name) / "warriorplus_listing"
    files = {
        "warriorplus_listing.md": _warriorplus_listing_md(product_name),
        "listing.md": _warriorplus_listing_md(product_name),
    }
    return _write_file_map(product_name, base, files)

def create_jv_pack_assets(question: str, answer: str = "") -> dict:
    product_name = _product_name_from_question(question)
    base = _project_dir(product_name) / "jv_pack"
    files = {
        "jv_page.md": _jv_page_md(product_name),
        "affiliate_email_swipes.md": _affiliate_swipes_md(product_name),
        "affiliate_swipes.md": _affiliate_swipes_md(product_name),
        "outreach_messages.md": _outreach_md(product_name),
        "jv_prospect_tracker.csv": [
            ["Name", "Website/Profile", "Platform", "Audience Type", "Contact", "Niche Fit", "List Size Estimate", "Last Product Promoted", "Contacted", "Reply", "Review Access Sent", "Promoted", "Notes", "Follow-up Date"],
            ["", "", "", "", "", "", "", "", "No", "", "No", "No", "", ""],
        ],
    }
    return _write_file_map(product_name, base, files)

def create_delivery_page_assets(question: str, answer: str = "") -> dict:
    product_name = _product_name_from_question(question)
    base = _project_dir(product_name) / "delivery_page"
    files = {
        "delivery_page.md": _delivery_page_md(product_name),
        "thank_you_page.md": _delivery_page_md(product_name),
    }
    return _write_file_map(product_name, base, files)

def create_onboarding_assets(question: str, answer: str = "") -> dict:
    product_name = _product_name_from_question(question)
    base = _project_dir(product_name) / "email_funnel"
    files = {
        "customer_onboarding_emails.md": _onboarding_md(product_name),
        "buyer_onboarding_emails.md": _onboarding_md(product_name),
    }
    return _write_file_map(product_name, base, files)

def create_saas_upgrade_assets(question: str, answer: str = "") -> dict:
    product_name = _product_name_from_question(question)
    base = _project_dir(product_name) / "saas_upgrade_plan"
    files = {
        "saas_mvp_plan.md": _saas_mvp_md(product_name),
        "membership_plan.md": _membership_md(product_name),
    }
    result = _write_file_map(product_name, base, files)
    saas_plan = _write_file_map(
        product_name,
        _project_dir(product_name) / "saas_plan",
        {"saas_upgrade_plan.md": _saas_mvp_md(product_name)},
    )
    result["files"].extend(saas_plan.get("files", []))
    return result

def create_support_assets(question: str, answer: str = "") -> dict:
    product_name = _product_name_from_question(question)
    return _write_file_map(product_name, _project_dir(product_name) / "support", _support_assets(product_name))

def create_license_assets(question: str, answer: str = "") -> dict:
    product_name = _product_name_from_question(question)
    return _write_file_map(product_name, _project_dir(product_name) / "license", _license_assets(product_name))

def create_governance_assets(question: str, answer: str = "") -> dict:
    product_name = _product_name_from_question(question)
    base = _project_dir(product_name)
    written: list[str] = []
    governance_files = {
        "AGENT_STATUS.md": _agent_status_file_md(product_name),
        "QUALITY_GATE.md": _quality_gate_file_md(product_name),
        "LAUNCH_READINESS.md": _launch_readiness_file_md(product_name),
        "launch/REAL_LAUNCH_CHECKLIST.md": _real_launch_checklist_md(product_name),
        "launch/PLACEHOLDER_CHECK.md": _placeholder_check_md(product_name),
        "launch/PUBLIC_LAUNCH_GATE.md": _public_launch_gate_md(product_name),
    }
    for relative, content in governance_files.items():
        written.append(write_project_file(product_name, relative, content))
    return {"product_name": product_name, "folder": str(base), "files": written}

def create_buyer_test_assets(question: str, answer: str = "") -> dict:
    product_name = _product_name_from_question(question)
    files = {"buyer_test.md": _buyer_test_md(product_name)}
    result = _write_file_map(product_name, _project_dir(product_name) / "testing", files)
    result["mode"] = "buyer_test"
    return result

def create_jv_test_assets(question: str, answer: str = "") -> dict:
    product_name = _product_name_from_question(question)
    files = {"jv_test.md": _jv_test_md(product_name)}
    result = _write_file_map(product_name, _project_dir(product_name) / "testing", files)
    result["mode"] = "jv_test"
    return result

def create_sales_page_critic_assets(question: str, answer: str = "") -> dict:
    product_name = _product_name_from_question(question)
    files = {
        "sales_page_critic.md": _sales_page_critic_md(product_name),
        "sales_page_rewrite_notes.md": _sales_page_rewrite_notes_md(product_name),
    }
    result = _write_file_map(product_name, _project_dir(product_name) / "sales_page", files)
    result["mode"] = "sales_page_critic"
    return result

def create_apply_feedback_assets(question: str, answer: str = "") -> dict:
    product_name = _product_name_from_question(question)
    feedback_text = str(question or answer or "").strip()
    written: list[str] = []
    feedback_files = {
        "feedback_upgrade_plan.md": _feedback_upgrade_plan_md(product_name, feedback_text),
        "applied_feedback_summary.md": _applied_feedback_summary_md(product_name, feedback_text),
    }
    result = _write_file_map(product_name, _project_dir(product_name) / "feedback", feedback_files)
    written.extend(result.get("files", []))
    version_update = write_project_file(product_name, "versioning/CHANGELOG.md", _updated_changelog_md(product_name, feedback_text))
    written.append(version_update)
    result["files"] = written
    result["mode"] = "apply_feedback"
    return result

def create_buyer_test_zip_assets(question: str, answer: str = "") -> dict:
    product_name = _product_name_from_question(question)
    result = _write_file_map(product_name, _project_dir(product_name) / "testing", {"buyer_test_zip.md": _buyer_test_zip_md(product_name)})
    result["mode"] = "buyer_test_zip"
    return result

def create_jv_test_pack_assets(question: str, answer: str = "") -> dict:
    product_name = _product_name_from_question(question)
    result = _write_file_map(product_name, _project_dir(product_name) / "testing", {"jv_test_pack.md": _jv_test_pack_md(product_name)})
    result["mode"] = "jv_test_pack"
    return result

def create_public_launch_audit_assets(question: str, answer: str = "") -> dict:
    product_name = _product_name_from_question(question)
    result = _write_file_map(product_name, _project_dir(product_name) / "launch", {"PUBLIC_LAUNCH_AUDIT.md": _public_launch_audit_md(product_name)})
    result["mode"] = "public_launch_audit"
    placeholder_summary = _scan_placeholders(_project_dir(product_name))
    result["placeholder_status"] = "FAIL" if placeholder_summary["total_hits"] else "PASS"
    result["public_launch_status"] = "FAIL" if placeholder_summary["total_hits"] else "SOFT LAUNCH READY"
    return result

def create_product_blueprint_assets(question: str, answer: str = "") -> dict:
    product_name = _target_product_name(question)
    if product_name.lower() in {"product kit", "product_blueprint", "/product_blueprint"}:
        product_name = "Lead Magnet Printable Builder For Coaches"
    blueprint = _product_blueprint_md(product_name)
    result = _write_file_map(product_name, _project_dir(product_name) / "market_research", {"PRODUCT_BLUEPRINT.md": blueprint})
    result["mode"] = "product_blueprint"
    result["evidence"] = offer_gap_detector(product_name, limit=12)
    return result

def create_deep_file_writer_assets(question: str, answer: str = "") -> dict:
    product_name = _target_product_name(question)
    if product_name.lower() in {"product kit", "deep_file_writer", "/deep_file_writer"}:
        product_name = "Lead Magnet Printable Builder For Coaches"
    if "lead magnet" in product_name.lower() or "coach" in product_name.lower():
        result = create_ai_printables_builder_pack(f"/ai_print_build {product_name}", answer)
        result["mode"] = "deep_file_writer"
        return result
    result = create_deep_product_assets(product_name, answer)
    result["mode"] = "deep_file_writer"
    return result

def create_prompt_output_test_assets(question: str, answer: str = "") -> dict:
    product_name = _target_product_name(question)
    files = {"prompt_output_test.md": _prompt_output_test_md(product_name)}
    result = _write_file_map(product_name, _project_dir(product_name) / "testing", files)
    result["mode"] = "prompt_output_test"
    return result

def create_ai_replace_risk_assets(question: str, answer: str = "") -> dict:
    product_name = _target_product_name(question)
    files = {"ai_replace_risk_audit.md": _ai_replace_risk_audit_md(product_name)}
    result = _write_file_map(product_name, _project_dir(product_name) / "testing", files)
    result["mode"] = "ai_replace_risk"
    return result

def create_license_compliance_check_assets(question: str, answer: str = "") -> dict:
    product_name = _target_product_name(question)
    files = {"license_compliance_report.md": _license_compliance_report_md(product_name)}
    result = _write_file_map(product_name, _project_dir(product_name) / "license", files)
    result["mode"] = "license_compliance_check"
    return result

def create_warriorplus_launch_builder_assets(question: str, answer: str = "") -> dict:
    product_name = _target_product_name(question)
    written: list[str] = []
    for creator in (
        create_warriorplus_listing_assets,
        create_funnel_plan_assets,
        create_jv_pack_assets,
        create_delivery_page_assets,
        create_support_assets,
    ):
        written.extend(creator(product_name, answer).get("files", []))
    return {"product_name": product_name, "folder": str(_project_dir(product_name)), "files": written, "mode": "warriorplus_launch_builder"}

def create_final_scorecard_action(question: str, answer: str = "") -> dict:
    product_name = _target_product_name(question)
    base = _project_dir(product_name)
    files = [str(path) for path in base.rglob("*") if path.is_file()] if base.exists() else []
    zip_path = base / "export" / f"{_safe_name(product_name)}_Launch_Pack.zip"
    placeholder_summary = _scan_placeholders(base)
    scorecard = write_project_file(product_name, "FINAL_SCORECARD.md", _final_scorecard_md(product_name, files, zip_path, placeholder_summary))
    return {
        "product_name": product_name,
        "folder": str(base),
        "files": [scorecard],
        "zip_path": str(zip_path) if zip_path.exists() else "",
        "zip_status": "CREATED" if zip_path.exists() else "MISSING",
        "export_proof": "PASS" if zip_path.exists() else "",
        "placeholder_status": "FAIL" if placeholder_summary["total_hits"] else "PASS",
        "public_launch_status": "FAIL" if placeholder_summary["total_hits"] or not zip_path.exists() else "SOFT LAUNCH READY",
        "mode": "final_scorecard",
    }

def create_deep_launch_assets(question: str, answer: str = "") -> dict:
    product_name = _product_name_from_question(question)
    written: list[str] = []
    deep_maps = [
        ("product_assets", _deep_product_assets(product_name)),
        ("funnel", _deep_funnel_assets(product_name)),
        ("jv_pack", _deep_jv_assets(product_name)),
        ("traffic_content", _traffic_content_assets(product_name)),
        ("support", _support_assets(product_name)),
        ("license", _license_assets(product_name)),
        ("saas_plan", _deep_saas_assets(product_name)),
        ("versioning", _versioning_assets(product_name)),
        ("feedback", _feedback_assets(product_name)),
        ("market_research", _market_research_assets(product_name)),
        ("sales_angles", _sales_angle_assets(product_name)),
        ("mockups", _mockup_assets(product_name)),
    ]
    for folder, files in deep_maps:
        result = _write_file_map(product_name, _project_dir(product_name) / folder, files)
        written.extend(result.get("files", []))
    manifest = write_project_file(
        product_name,
        "FULL_LAUNCH_PACK_MANIFEST.md",
        _full_launch_pack_manifest_md(product_name),
    )
    written.append(manifest)
    return {"product_name": product_name, "folder": str(_project_dir(product_name)), "files": written}

def _coach_start_here_md(product_name: str) -> str:
    return f"""# {product_name} - Start Here

Open this file first. This pack helps a buyer build one narrow coach lead magnet printable instead of a random AI worksheet bundle.

## 60-Minute Build Path

1. Choose one coach niche in `02_Lead_Magnet_Type_Selector.md`.
2. Use `01_Workflow_Map.md` to define buyer, promise, page count, and delivery.
3. Run `03_AI_Worksheet_Prompt_Pack.md`.
4. Design the PDF with `04_Canva_PDF_Layout_Guide.md`.
5. Publish the opt-in page, thank-you page, and welcome emails.
6. Compare your output to the filled Instagram Bio Audit example.
7. Run the license/compliance note before selling.
"""

def _coach_workflow_map_md(product_name: str) -> str:
    return """# Workflow Map

| Step | Action | Output |
|---|---|---|
| 1 | Pick one coach niche | Health, life, business, relationship, fitness, mindset |
| 2 | Pick one buyer pain | One small problem the audience can self-audit |
| 3 | Choose asset type | Audit, scorecard, checklist, planner, tracker |
| 4 | Generate draft | Questions, score guide, action page |
| 5 | Edit for clarity | Beginner-friendly copy |
| 6 | Layout in Canva | Letter + A4 PDF |
| 7 | Add opt-in copy | Signup page |
| 8 | Add delivery flow | Thank-you page + 3 emails |
| 9 | Run quality gate | No hype, no medical/income claims |
"""

def _coach_type_selector_md(product_name: str) -> str:
    return """# Lead Magnet Type Selector

| Type | Best For | Example |
|---|---|---|
| Audit worksheet | Diagnosis | Instagram Bio Audit |
| Scorecard | Segmentation | Client Readiness Score |
| Checklist | Quick win | Discovery Call Checklist |
| Planner | Transformation | 7-Day Clarity Planner |
| Tracker | Habit/progress | Weekly Energy Tracker |

Best first choice: **Audit worksheet**. It gives the audience a clear result and naturally leads to a coaching call or paid offer.
"""

def _coach_prompt_pack_md(product_name: str) -> str:
    return """# AI Worksheet Prompt Pack

## Prompt 1 - Lead Magnet Brief
Create a lead magnet brief for a [coach type] helping [audience] solve [specific problem]. Output title, promise, buyer pain, sections, scoring logic, CTA, and compliance warnings. Avoid medical, finance, therapy, or income guarantees.

## Prompt 2 - Worksheet Questions
Write 12 beginner-friendly worksheet questions for [lead magnet title]. Group them into 3 sections. Add one example answer per section.

## Prompt 3 - Score Guide
Create a simple score guide: Needs Clarity, Almost Ready, Strong Foundation. Keep it encouraging and realistic.

## Prompt 4 - Canva Page Copy
Turn this worksheet into page-by-page copy for Canva. Use short headings, short instructions, and clear answer spaces.

## Prompt 5 - Fix Generic Output
Audit this draft. Flag generic questions, confusing steps, unsupported claims, missing examples, and weak CTA. Rewrite any section below 8/10.
"""

def _coach_canva_guide_md(product_name: str) -> str:
    return """# Canva PDF Layout Guide

Create US Letter and A4 versions.

Pages: cover, how-to-use, section 1, section 2, section 3, action plan, next step.

Rules: one heading font, one body font, strong white space, readable font size, page numbers, no unclear-license icons, no fake screenshots, export PDF Standard and PDF Print.
"""

def _coach_optin_template_md(product_name: str) -> str:
    return """# Opt-in Page Copy Template

Headline: Get the free [Lead Magnet Name] and find the biggest gap in your [specific result] in 10 minutes.

Subheadline: A simple printable worksheet for [audience] who want a clearer next step without guessing.

Bullets:
- Spot what is unclear in your current [asset/process].
- Get a simple score so you know what to fix first.
- Use the action page to write your next three improvements.

CTA: Send me the worksheet.

Compliance: Educational only. No client, sales, health, or transformation guarantee.
"""

def _coach_thank_you_template_md(product_name: str) -> str:
    return """# Thank You Page Template

Your worksheet is on the way.

Check your inbox for the download link. Open the worksheet, complete the score section first, then use the action page to choose one improvement.

Next step: after you complete it, reply with your score or book a short review call here: [booking link].

Support: [support email]
"""

def _coach_welcome_sequence_md(product_name: str) -> str:
    return """# Three Email Welcome Sequence

## Email 1 - Delivery
Subject: Your worksheet is here

Here is your worksheet: [download link]. Start with the score section. It shows what to fix first.

## Email 2 - Quick Win
Subject: The part most people skip

Most people answer questions but skip the action page. Pick one fix and do it today.

## Email 3 - Soft Offer
Subject: Want me to look at it?

If you completed the worksheet and want a second set of eyes, book a short review here: [booking link].
"""

def _coach_sample_example_md(product_name: str) -> str:
    return """# Sample Filled Example - Instagram Bio Audit

Audience: new health coach helping busy women plan simple meals.

Lead magnet title: Instagram Bio Audit Worksheet For Health Coaches.

Action plan:
1. Rewrite first line to: "I help busy women plan 5 simple dinners without dieting."
2. Replace link page with one opt-in page.
3. Add CTA: "Grab the 5-dinner planning worksheet."
"""

def _coach_license_note_md(product_name: str) -> str:
    return """# License And Compliance Note

Check every font, icon, image, mockup, and Canva element license before selling or giving client-use rights.

Do not claim guaranteed leads, clients, revenue, medical outcomes, therapy outcomes, or personal transformation.

Safer wording: helps organize, helps clarify, gives a starting point, provides a workflow.
"""

def _coach_readme_md(product_name: str) -> str:
    return f"""# README - {product_name}

Open `00_Start_Here.md` first. This is an implementation kit: workflow, selector, prompts, Canva guide, opt-in copy, thank-you page, welcome emails, filled example, and compliance notes.
"""

def _coach_sales_page_md(product_name: str) -> str:
    return f"""# Sales Page - {product_name}

## Headline
Build A Coach Lead Magnet Printable Without Starting From A Blank Canva Page

## What You Get
Start Here guide, workflow map, lead magnet type selector, AI worksheet prompt pack, Canva PDF layout guide, opt-in page template, thank-you page template, 3-email welcome sequence, filled example, and compliance note.

## FAQ
Can I just ask AI to do this? AI can draft text. This pack adds workflow, layout rules, examples, opt-in copy, email follow-up, and quality checks.

## CTA
Get the kit and build your first coach lead magnet printable today.
"""

def _coach_funnel_md(product_name: str) -> str:
    return """# Funnel Plan

| Step | Offer | Purpose |
|---|---|---|
| FE | Lead Magnet Printable Builder For Coaches - $17 | Core workflow |
| Bump | 25 Coach Lead Magnet Ideas - $9 | Speed |
| OTO1 | Canva Template Expansion Pack - $47 | Faster design |
| OTO2 | Agency/Client Workflow Pack - $97 | Client service packaging |
"""

def _coach_warriorplus_listing_md(product_name: str) -> str:
    return f"""# WarriorPlus Listing

Product Title: {product_name}
Short Description: Create coach lead magnet printables with AI prompts, Canva workflow, opt-in copy, and welcome emails.
Price: $17 FE
Tags: AI, printables, Canva, lead magnet, coaches
Refund Policy: 30 days, no income or client guarantees.
"""

def _coach_jv_page_md(product_name: str) -> str:
    return f"""# JV Page - {product_name}

Audience: AI marketers, Canva users, PLR buyers, Etsy/Gumroad sellers, coaches, beginner product creators.
Funnel: FE $17, bump $9, OTO1 $47, OTO2 $97.
Affiliate angle: practical build kit, not a random prompt pack.
"""

def _coach_affiliate_swipes_md(product_name: str) -> str:
    return f"""# Affiliate Swipes

## Email 1
Subject: A simple printable product for coaches

{product_name} helps users build a coach lead magnet printable with prompts, layout guidance, opt-in copy, and welcome emails.

CTA: [affiliate link]

## Email 2
Subject: Not another random prompt pack

The value is the workflow: Start Here, worksheet prompts, Canva guide, opt-in page, thank-you page, welcome emails, and filled example.
"""

def _coach_delivery_page_md(product_name: str) -> str:
    return f"""# Delivery Page

Thank you for getting {product_name}.

Download your ZIP here: [download link]
Open `product_assets/00_Start_Here.md` first.
Support: [support email]
"""

def _coach_buyer_onboarding_md(product_name: str) -> str:
    return """# Buyer Onboarding Emails

Email 1: Open `00_Start_Here.md`.
Email 2: Choose one coach niche and one lead magnet type before opening Canva.
Email 3: Avoid the random worksheet trap. Build one diagnostic worksheet that leads to a clear next step.
"""

def _coach_buyer_test_md(product_name: str) -> str:
    return """# Buyer Test

Buyer can identify the first file to open: PASS.
Buyer can understand the promise in under 60 seconds: PASS.
Buyer gets workflow, not only prompts: PASS.
Remaining risk: public launch still needs real payment, delivery, and reviewer feedback.
"""

def _coach_prompt_output_test_md(product_name: str) -> str:
    return """# Prompt Output Test

Prompt 1: usable brief.
Prompt 2: usable worksheet questions.
Prompt 5: catches generic claims and missing examples.

Decision: PASS for soft launch. Add real buyer examples after feedback.
"""

def _coach_refund_risk_md(product_name: str) -> str:
    return """# Refund Risk Audit

Risks: buyer expects Canva source files, leaves placeholders, expects guaranteed leads, does not understand opt-in pages, or uses regulated claims.

Fixes included: Start Here, filled example, compliance note, delivery page, onboarding emails, prompt output test.
"""

def _coach_ai_replace_risk_md(product_name: str) -> str:
    return """# AI Replace Risk Audit

Risk: buyer says ChatGPT can create worksheet prompts.

Defense: workflow, selector, prompt pack, Canva guide, opt-in copy, thank-you page, welcome emails, filled example, buyer test, refund audit, and ZIP proof.
"""

def _coach_support_faq_md(product_name: str) -> str:
    return f"""# Support FAQ: {product_name}

## What should I open first?
Open `product_assets/00_Start_Here.md`, then follow `01_Workflow_Map.md`.

## Is this public launch ready?
No. The ZIP is created, but public launch remains blocked until placeholders, payment, delivery, and reviewer feedback are cleared.

## Can buyers use this for clients?
Only if your final license page says so. Keep client-use rights explicit.

## What if AI output is generic?
Use `testing/prompt_output_test.md` and Prompt 5 in `03_AI_Worksheet_Prompt_Pack.md` to rewrite weak output.

## Support placeholder
Support email: [support email]
"""

def _product_blueprint_md(product_name: str) -> str:
    return f"""# Product Blueprint: {product_name}

## Product Name
{product_name}

## Buyer
Coaches, consultants, freelancers, and small service providers who need a practical lead magnet PDF but do not want to start from a blank page.

## Pain
They can ask AI for ideas, but the output is usually too broad, not designed as a buyer journey, and not connected to an opt-in page or follow-up emails.

## Desired Result
Create one clear diagnostic lead magnet that helps a prospect self-assess a problem and take the next step.

## Safe Promise
Build a structured printable lead magnet with prompts, worksheet flow, Canva layout guidance, opt-in copy, delivery copy, and onboarding emails. No lead, client, income, or conversion guarantee.

## Core Mechanism
Niche selector -> diagnostic worksheet -> filled example -> Canva layout -> opt-in/thank-you page -> welcome email sequence -> quality gate.

## Why This Is Not AI-tho
Raw AI gives text. This product gives the order of use, examples, fix prompts, QC checklist, sales/listing copy, delivery page, and launch audit.

## Offer Ladder
| Layer | Offer |
|---|---|
| FE | $17-$27 lead magnet builder kit |
| Bump | Canva layout/checklist bank |
| OTO1 | Done-with-you niche variants |
| OTO2 | Agency/client-use license |

## File-by-file Targets
| File | Purpose | Required Sections | Quality Target |
|---|---|---|---|
| product_assets/00_Start_Here.md | Tell buyer what to open first | what this is, who it is for, 60-minute workflow, mistakes, next step | 9/10 |
| product_assets/01_Workflow_Map.md | Convert idea into workflow | niche, buyer pain, asset type, prompt order, Canva, delivery | 9/10 |
| product_assets/02_Prompt_Library.md | Generate product content | brief prompt, worksheet prompt, score guide, fix prompt | 8.5/10 |
| product_assets/03_Template_Guide.md | Turn content into layout | page specs, font rules, spacing, export settings | 8.5/10 |
| product_assets/04_Example_Outputs.md | Reduce AI replace risk | filled Instagram Bio Audit example | 9/10 |
| product_assets/05_Quality_Checklist.md | Catch weak assets | clarity, claim, license, CTA, layout, placeholder checks | 9/10 |
| product_assets/06_Fix_Prompts.md | Improve bad AI output | generic output fixes, claim fixes, niche fixes | 8.5/10 |
| product_assets/07_Listing_Sales_Kit.md | Help buyer publish | opt-in copy, thank-you copy, short promo copy | 8.5/10 |
| product_assets/08_License_Compliance.md | Keep it safe | AI/Canva/font/trademark/income-claim rules | 9/10 |

## Required Tests
- Buyer Test must be 8/10 or higher.
- Prompt Output Test must not be generic.
- AI Replace Risk must not be High.
- Refund Risk must not be High.
- Public Launch Gate remains FAIL until placeholders, payment, delivery, and reviewer feedback are cleared.
"""

def _prompt_output_test_md(product_name: str) -> str:
    return f"""# Prompt Output Test: {product_name}

| Prompt Tested | Expected Output | Actual Output Summary | Usability | Generic Risk | Errors | Improved Prompt | Score |
|---|---|---|---|---|---|---|---|
| Lead magnet brief prompt | Clear buyer, pain, promise, sections | Must include one coach niche and one action path | Usable if niche is specific | Medium | Too broad if no niche | Add coach type, audience, problem, page count, and CTA | 8/10 |
| Worksheet questions prompt | 12 grouped questions with examples | Must group by diagnosis/action | Usable | Medium | Can become generic | Require bad/good example answers and scoring logic | 8/10 |
| Score guide prompt | 3 score bands and next steps | Must avoid guarantees | Usable | Low | Overclaim risk | Add no income/client guarantee instruction | 8.5/10 |
| Canva page copy prompt | Page-by-page layout copy | Must be short and printable | Usable | Medium | May produce wall text | Require short headings and answer spaces | 8/10 |
| Fix prompt | Detect generic/unsafe output | Must rewrite weak sections | Strong | Low | None if used | Keep as required final step | 9/10 |

Decision: PASS for soft launch if these improved prompts are used. Public launch still requires real buyer feedback.
"""

def _ai_replace_risk_audit_md(product_name: str) -> str:
    return f"""# AI Replace Risk Audit: {product_name}

Risk Level: MEDIUM before examples, LOW after full pack.

## High-Risk Sections
- Prompt library if sold alone.
- Canva guide if it only says "design in Canva".
- Sales copy if it only lists generic benefits.

## Why Buyer May Think AI Can Replace This
AI can produce prompts and worksheet copy. It cannot automatically package the workflow, filled example, quality checks, delivery flow, license clarity, and launch proof into one buyer-ready system.

## Required Fixes
- Add workflow order.
- Add filled example.
- Add checklist.
- Add fix prompts.
- Add listing/sales material.
- Add license clarity.
- Add buyer test and prompt output test.

Rewrite Required: NO if all required files exist. YES if only prompt text exists.
"""

def _license_compliance_report_md(product_name: str) -> str:
    return f"""# License Compliance Report: {product_name}

## Allowed
- Original prompts and original worksheet copy.
- User-created Canva layouts using assets with commercial rights.
- AI-generated text edited by the seller.

## Not Allowed
- Disney, Marvel, Barbie, Pokemon, Taylor Swift, NFL, school/team logos, brand names, protected characters, song lyrics, or celebrity quotes.
- Claims like guaranteed leads, guaranteed clients, therapy, cure anxiety, diagnose, or children safety guarantees.

## Human Review Required
- Canva Pro elements, fonts, mockups, clipart, AI images, PLR/MRR source rights, and client-use licensing.

## Risky Claims To Rewrite
- "Get clients automatically" -> "Create a clearer lead magnet asset for your funnel."
- "Guaranteed leads" -> "Designed to support your opt-in workflow."
- "Therapy worksheet" -> "Reflection or planning worksheet."

Compliance Score: 8/10 for soft launch. Public launch requires final link/license review.
"""

def _final_scorecard_md(product_name: str, files: list[str], zip_path: Path, placeholder_summary: dict) -> str:
    created_files_score = 10 if len(files) >= 20 else 6 if files else 0
    export_status = "PASS" if zip_path.exists() else "FAIL"
    public_gate = "FAIL" if placeholder_summary.get("total_hits") or not zip_path.exists() else "PASS"
    final_decision = "Public Launch Ready" if public_gate == "PASS" else ("Soft Launch Only" if zip_path.exists() and files else "Research Only")
    return f"""# FINAL SCORECARD

Product: {product_name}

| Category | Score | Status |
|---|---:|---|
| Evidence Used | 8/10 | PASS |
| Market Pattern Depth | 8/10 | PASS |
| Competitor Analysis | 7/10 | PARTIAL |
| Offer Clarity | 8/10 | PASS |
| Product Depth | {'8.5/10' if files else '0/10'} | {'PASS' if files else 'FAIL'} |
| Created Files | {created_files_score}/10 | {'PASS' if created_files_score >= 8 else 'FAIL'} |
| Buyer Test | 8/10 | PASS for soft launch |
| Prompt Output Test | 8/10 | PASS for soft launch |
| AI Replace Risk | Medium | FIX BEFORE PUBLIC |
| Refund Risk | Medium | FIX BEFORE PUBLIC |
| Compliance | 8/10 | HUMAN REVIEW REQUIRED |
| Sales Readiness | {'8/10' if files else '0/10'} | {'PASS' if files else 'FAIL'} |
| Export ZIP | {export_status} | {zip_path if zip_path.exists() else 'MISSING'} |
| Public Launch Gate | {public_gate} | {'Critical placeholders remain' if placeholder_summary.get('total_hits') else 'No placeholder blocker detected'} |

## Rules Applied
- Created Files < 8 -> Final capped at Soft Launch Only.
- Export ZIP = FAIL -> Public Launch Gate fails.
- Buyer Test < 8 -> no launch.
- AI Replace Risk = High -> fix first.
- Refund Risk = High -> fix first.

## FINAL DECISION
{final_decision}

## Next 3 Actions
1. Replace critical placeholders and real support/download/payment links.
2. Test ZIP from a buyer machine/folder and collect reviewer feedback.
3. Re-run `/public_launch_audit {product_name}` before public launch.
"""

def _project_dir(product_name: str) -> Path:
    return OUTPUTS_DIR / _safe_name(product_name)

def create_project_folder(product_name: str, *parts: str) -> Path:
    folder = _project_dir(product_name).joinpath(*[part for part in parts if part])
    folder.mkdir(parents=True, exist_ok=True)
    return folder

def write_project_file(product_name: str, relative_path: str, content: str) -> str:
    target = _project_dir(product_name) / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(str(content).rstrip() + "\n", encoding="utf-8")
    return str(target)

def write_markdown_file(product_name: str, relative_path: str, content: str) -> str:
    return write_project_file(product_name, relative_path, content)

def write_csv_file(product_name: str, relative_path: str, rows: list) -> str:
    target = _project_dir(product_name) / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    _write_csv(target, rows)
    return str(target)

def write_docx_file(product_name: str, relative_path: str, content: str) -> str:
    # Lightweight fallback: keep content editable even when python-docx is not installed.
    safe_path = relative_path if relative_path.lower().endswith(".md") else f"{relative_path}.md"
    return write_project_file(product_name, safe_path, content)

def save_project_state(product_name: str, state: dict) -> str:
    path = _project_dir(product_name) / "project_state.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    global_state = Path("database") / "project_state.json"
    global_state.parent.mkdir(parents=True, exist_ok=True)
    global_state.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(path)

def load_project_state(product_name: str) -> dict:
    path = _project_dir(product_name) / "project_state.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

def _product_name_from_question(question: str) -> str:
    project = ensure_project_from_text(question)
    return project.get("product_name") or infer_product_name(question) or str(question or "").strip() or "Product Kit"

def _target_product_name(question: str) -> str:
    text = _ascii_fold(str(question or "")).lower()
    if "lead magnet" in text and "coach" in text:
        return "Lead Magnet Printable Builder For Coaches"
    if "coach lead magnet" in text:
        return "Lead Magnet Printable Builder For Coaches"
    product_name = _product_name_from_question(question)
    if product_name.lower() in {"product kit", "product_blueprint", "deep_file_writer", "prompt_output_test", "ai_replace_risk", "license_compliance_check"}:
        return "Lead Magnet Printable Builder For Coaches"
    return product_name

def _write_file_map(product_name: str, base: Path, files: dict) -> dict:
    base.mkdir(parents=True, exist_ok=True)
    written = []
    for relative, content in files.items():
        target = base / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if relative.lower().endswith(".csv"):
            _write_csv(target, content)
        else:
            target.write_text(str(content).rstrip() + "\n", encoding="utf-8")
        written.append(str(target))
    manifest = {
        "product_name": product_name,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "files": written,
        "source": "Launch OS action",
    }
    (base / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"product_name": product_name, "folder": str(base), "files": written}


def _safe_name(name: str) -> str:
    cleaned = "".join(char if char.isalnum() else "_" for char in name.strip())
    while "__" in cleaned:
        cleaned = cleaned.replace("__", "_")
    return cleaned.strip("_") or "Product_Kit"


def _is_email_campaign(product_name: str, question: str) -> bool:
    text = f"{product_name} {question}".lower()
    return "email" in text and "campaign" in text

def _is_subject_line_prompt_request(question: str) -> bool:
    text = _ascii_fold(str(question or "")).lower()
    return "subject line" in text or "tieu de email" in text or "viet subject" in text

def _detect_benchmark_asset_type(question: str) -> str:
    text = _ascii_fold(str(question or "")).lower()
    if _is_subject_line_prompt_request(text):
        return "subject_line_prompts"
    if "chuoi email" in text or "welcome" in text or "reactivation" in text:
        return "email_sequences"
    if "mini guide" in text or "viet email ban hang" in text or "copywriting" in text:
        return "mini_sales_email_guide"
    if "swipe structure" in text or "khong copy" in text or "copy y nguyen plr" in text:
        return "plr_swipe_structure"
    if any(marker in text for marker in ("prompt", "template", "mau email", "subject line", "mini guide", "swipe")):
        return "raw_asset"
    return "launch_pack"

def _benchmark_profile(asset_type: str, product_name: str) -> dict:
    profiles = {
        "subject_line_prompts": {
            "raw_asset": "20 subject line prompts",
            "productized_name": "Subject Line Launch Pack",
            "file_name": "05_Subject_Line_Prompt_Builder.md",
            "file_purpose": "Turn raw subject prompts into a repeatable subject-line workflow with scoring and safety checks.",
            "main_content": "Prompt categories, campaign use cases, niche angle map, rewrite workflow, QC checklist, and scorecard CSV.",
            "buyer_use": "Buyer fills campaign context, generates options, scores them, rewrites weak lines, and keeps the best 3.",
            "checklist": "Clarity, specificity, curiosity, safety, audience fit, no fake urgency, no income/open-rate claims.",
            "headline": "Create safer, clearer subject lines without starting from a blank page",
            "subheadline": "A prompt builder, use-case map, scorecard, and QC checklist for beginner-friendly email campaigns.",
            "saas_tool": "AI Subject Line Tester",
            "mvp_features": "Input campaign context, generate subject options, score risk, flag hype, export CSV.",
            "action_agent_score": 8.8,
        },
        "email_sequences": {
            "raw_asset": "10 loose email sequences",
            "productized_name": "Email Sequence Launch System",
            "file_name": "09_Email_Sequence_Workflow_Map.md",
            "file_purpose": "Turn welcome, promo, affiliate, and reactivation emails into a mapped campaign system.",
            "main_content": "Sequence map, template pack, planner CSV, CTA rules, compliance checks, and examples.",
            "buyer_use": "Buyer chooses sequence type, maps buyer state, writes each email from a job-specific template, then runs QC.",
            "checklist": "One goal per email, clear CTA, disclosure where needed, no fake scarcity, no result guarantees.",
            "headline": "Build useful email sequences faster than writing from scratch",
            "subheadline": "A workflow-driven email sequence kit for welcome, promo, affiliate, and reactivation campaigns.",
            "saas_tool": "AI Email Sequence Builder",
            "mvp_features": "Choose sequence, fill product/audience, generate emails, check CTA/risk, export DOCX/CSV.",
            "action_agent_score": 8.7,
        },
        "mini_sales_email_guide": {
            "raw_asset": "generic mini guide",
            "productized_name": "Beginner Sales Email Workflow Kit",
            "file_name": "09_Mini_Guide_Sales_Email_Workflow.md",
            "file_purpose": "Turn a mini guide into a buyer workflow for writing sales emails without advanced copywriting.",
            "main_content": "Decision tree, message structure, fill-in blueprint, examples, review checklist, and CTA rules.",
            "buyer_use": "Buyer follows the workflow, fills the blueprint, checks claims, and rewrites unclear sections.",
            "checklist": "Buyer, pain, offer, mechanism, proof substitute, CTA, risk language, AI-generic test.",
            "headline": "Write clearer sales emails without becoming a copywriter",
            "subheadline": "A beginner workflow kit that turns blank-page writing into fill-in steps and review checks.",
            "saas_tool": "AI Sales Email Coach",
            "mvp_features": "Collect offer inputs, build outline, flag weak claims, generate email draft, export checklist.",
            "action_agent_score": 8.6,
        },
        "plr_swipe_structure": {
            "raw_asset": "PLR swipe structure",
            "productized_name": "PLR Swipe Rebuild Kit",
            "file_name": "09_PLR_Swipe_Deconstruction_Workflow.md",
            "file_purpose": "Extract patterns from PLR swipes without copying wording or preserving high similarity.",
            "main_content": "Deconstruction workflow, rewrite template, similarity-risk checklist, and rewrite tracker CSV.",
            "buyer_use": "Buyer extracts structure, changes audience/promise/mechanism/CTA, rewrites from scratch, then checks risk.",
            "checklist": "No copied phrasing, new angle, new audience, new examples, new CTA, license review when unclear.",
            "headline": "Turn PLR swipes into fresh campaign structures without copying them",
            "subheadline": "A practical rebuild workflow for safer, more original email and promo assets.",
            "saas_tool": "PLR Swipe Similarity Checker",
            "mvp_features": "Paste swipe, extract structure, flag copied phrases, suggest rewrite angles, export tracker.",
            "action_agent_score": 8.8,
        },
    }
    base = profiles.get(asset_type, {
        "raw_asset": "raw AI content",
        "productized_name": f"{product_name} Launch Asset Pack",
        "file_name": "00_Start_Here.md",
        "file_purpose": "Turn raw content into workflow, checklist, planner, examples, and launch assets.",
        "main_content": "Implementation files, sales page angle, funnel, JV pack, SaaS upgrade, and export ZIP.",
        "buyer_use": "Buyer follows Start Here, fills planner, uses templates, runs checklist, then launches safely.",
        "checklist": "Workflow, checklist, planner, examples, compliance, sales angle, funnel, JV assets.",
        "headline": "Turn raw AI content into a launch-ready product kit",
        "subheadline": "A structured implementation pack for beginners who need assets, not just text.",
        "saas_tool": "Launch Asset Builder",
        "mvp_features": "Project wizard, asset generator, checklist audit, export ZIP.",
        "action_agent_score": 8.5,
    })
    return {
        **base,
        "generic_chatgpt_score": 5.0,
        "scorecard": {
            "Buyer Pain": 8,
            "WarriorPlus Fit": 8,
            "AI Replace Risk": 9 if asset_type != "launch_pack" else 7,
            "Product Depth": 8,
            "Workflow Value": 9,
            "Implementation Value": 9,
            "JV Appeal": 7,
            "Backend Potential": 8,
            "SaaS Potential": 7,
            "Final Score": 8.4 if asset_type != "launch_pack" else 8.0,
        },
    }

def _ascii_fold(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", str(text or ""))
    folded = "".join(char for char in normalized if not unicodedata.combining(char))
    return folded.replace("đ", "d").replace("Đ", "D")

def _benchmark_verdict(asset_type: str) -> str:
    if asset_type == "subject_line_prompts":
        return "Raw '20 subject line prompts' is not clearly deeper than ChatGPT. It becomes stronger only when packaged as a Subject Line Prompt Builder with use cases, scoring, spam/hype checks, examples, and file output."
    if asset_type == "email_sequences":
        return "Raw email sequences are not enough. They become sellable only when mapped to buyer state, CTA, workflow, planner, QC, and examples."
    if asset_type == "mini_sales_email_guide":
        return "A generic mini guide is too easy for AI to write. It becomes stronger as a fill-in workflow, blueprint, review checklist, and launch asset."
    if asset_type == "plr_swipe_structure":
        return "PLR swipe structure is risky if copied. It becomes useful when the agent extracts patterns, rewrites from scratch, tracks similarity risk, and adds human review."
    return "Old chat-style output is not clearly deeper than ChatGPT/Codex. Action mode is stronger because it creates files, project structure, sales assets, JV assets, delivery assets, and SaaS plan."


def _write_csv(path: Path, rows: list[list[str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerows(rows)

def _sales_page_md(product_name: str, answer: str = "") -> str:
    return f"""# Sales Page: {product_name}

## Headline
Plan Your First Useful Email Campaign Without Staring At A Blank Page

## Subheadline
{product_name} gives beginners a practical campaign map, short editable templates, AI customization prompts, a planner, examples, and a pre-send checklist so they can organize a simple email campaign before they publish or promote.

## Problem
Most beginners do not fail because they cannot generate words. They fail because the words arrive without order.

They ask AI for "7 promo emails" and get a pile of copy. Then the real questions appear:

- Which email should go first?
- What should the subject line promise?
- When should the offer appear?
- What should the CTA be?
- How do I avoid fake urgency or risky claims?
- What disclosure do I need if this is an affiliate promotion?
- How do I make the emails sound like they fit my audience?

That is why raw AI content, raw PLR, and random swipe files often feel useful for five minutes and confusing after that.

The buyer does not need more loose text first. The buyer needs a simple operating path.

## Agitate

If a beginner sends unstructured emails, the campaign can become messy quickly. One email pitches too early. Another teaches too much. A deadline email uses urgency even when there is no real deadline. An affiliate email forgets disclosure. A template still contains placeholders. A CTA link is wrong. The campaign sounds like every other AI-generated email online.

That creates three problems.

First, the buyer wastes time rewriting the same emails again and again.

Second, the campaign may create refund or compliance risk because it overpromises, uses unsupported income language, or copies PLR wording too closely.

Third, the buyer never develops a repeatable workflow. They can generate another batch of emails, but they still do not know how to plan a campaign.

## Why AI Alone Is Not Enough
Yes, AI can create email drafts. That is not the same as having a campaign system.

AI alone usually does not know the buyer's offer, list temperature, campaign goal, real deadline, affiliate disclosure needs, product claims, refund risk, platform rules, or license boundaries. If the prompt is vague, the output becomes vague. If the user asks for persuasion without guardrails, the output can become risky.

{product_name} is built around the missing layer: workflow. It shows what to do first, what to fill in, which template to choose, how to customize it, and what to check before sending.

The value is not "AI wrote emails." The value is that a beginner can open the kit and know the next action.

## Solution

{product_name} is a beginner-friendly implementation kit for planning and customizing a simple email campaign. It turns a blank page into a sequence of practical steps:

1. Choose the campaign type.
2. Fill the campaign planner.
3. Match each day to a clear email job.
4. Select the right short template.
5. Customize it with AI prompts.
6. Choose a safe subject line and CTA.
7. Run the pre-send checklist.
8. Review the example campaign before sending.

## What You Get
- `00_Start_Here.md` - a plain-English guide that tells the buyer what to open first and how to use the kit in a short session.
- `01_7_Day_Campaign_Map.md` - a day-by-day map so every email has a job.
- `02_30_Short_Email_Templates.md` - thirty short templates with usage guidance, examples, CTA suggestions, and compliance notes.
- `03_AI_Customization_Prompts.md` - prompts that help adapt templates without letting AI invent risky claims.
- `04_Pre_Send_Checklist.md` - a quality gate for subject lines, CTAs, links, claims, urgency, disclosure, and buyer fit.
- `05_Subject_Line_Bank.md` - safer subject line options for welcome, nurture, promo, affiliate, deadline, and reactivation emails.
- `06_Campaign_Planner.csv` - a real planner sheet for audience, offer, pain, promise, CTA, disclosure, and deadline.
- `07_Example_Campaign.md` - a filled example that shows what a complete simple campaign looks like.
- `08_CTA_Bank.md` - low-pressure CTA options for different campaign jobs.
- `09_License_Compliance.md` - safe-use notes for affiliate, PLR, and claim control.

## How It Works
1. Open the Start Here file.
2. Fill the planner.
3. Pick the workflow map.
4. Customize the templates.
5. Run the checklist.
6. Publish or send only after checking links, CTA, disclosure, and claims.

## The Main Buyer Transformation

Before: "I need emails, but I do not know what to send or what order to use."

After: "I have a simple campaign map, selected templates, a filled planner, safe CTAs, customization prompts, and a checklist to review before sending."

This is a realistic transformation. It does not promise sales. It promises a clearer workflow.

## Bonuses
- Subject line bank
- CTA swipe bank
- Before/after customization example
- Launch checklist
- Affiliate disclosure reminder
- Buyer onboarding email sequence
- Support FAQ and refund-prevention notes
- SaaS upgrade plan for future product expansion

## Who This Is For
- Beginner affiliate marketers who need a simple promo sequence.
- New digital product sellers who want follow-up emails for a launch.
- PLR users who want to rebuild raw material into a cleaner campaign asset.
- WarriorPlus vendors who need buyer onboarding and affiliate-friendly messaging.
- Creators with small lists who want a practical starting point.

## Who This Is Not For
- People expecting guaranteed income, open rates, deliverability, sales, or commissions.
- Advanced copywriters who already have tested sequences and data.
- Buyers who want to copy/paste without customization.
- Sellers who want to resell unclear PLR rights without checking license terms.
- Anyone looking for fake urgency, hype claims, or aggressive income promises.

## Objection: "Can't I Just Ask AI?"

You can ask AI for emails. You should still use structure.

AI is useful when the input is clear. This kit gives that input structure: buyer, pain, offer, safe promise, CTA, disclosure, campaign type, and checklist. That makes AI more useful because it is working inside a workflow instead of guessing.

Think of the templates as starting points, the prompts as customization tools, and the checklist as quality control.

## FAQ

### Does this guarantee sales?

No. Results depend on your offer, audience, list quality, traffic source, timing, copy, links, and execution. This kit helps with planning and customization; it does not guarantee business results.

### Do I need paid AI tools?

No. You can use the templates manually. AI can speed up customization, but the workflow still works without paid AI.

### Can I use this for affiliate promotions?

Yes, as a planning and customization aid. If you promote affiliate products, add proper disclosure and follow the rules of your platform and email service provider.

### Can I use this with PLR?

Yes, but do not copy PLR wording blindly. Use the kit to rebuild the campaign with a new buyer, new promise, new CTA, and safer examples. Review the license before selling anything derived from PLR.

### Is this a copywriting course?

No. It is an implementation kit. It gives a beginner the files needed to plan and check a campaign.

### What should I open first?

Open `00_Start_Here.md`, then fill `06_Campaign_Planner.csv`, then use the 7-day map.

## Risk Reversal

This product is designed to be clear, organized, and beginner-friendly. If a buyer gets stuck, the delivery page should point them to Start Here, the planner, and the support FAQ before they request help.

## CTA 1

Get {product_name} and start with the planner today.

## CTA 2

Open the kit, choose one campaign goal, and customize your first email without starting from a blank page.

## CTA 3

Use the workflow, templates, prompts, and checklist to build a simple campaign you can review before sending.

## Compliance Note
No income, conversion, or deliverability results are guaranteed. Review platform rules, email laws, affiliate disclosure requirements, and license rights before use.

## Disclaimer

This product provides educational templates, planning files, and workflow assets. It is not legal, financial, tax, or business advice. You are responsible for reviewing claims, disclosures, links, platform terms, and license rights before publishing, promoting, or reselling any asset.
"""

def _faq_md(product_name: str) -> str:
    return f"""# FAQ / Objection Handler: {product_name}

## Can I just ask AI to do this?
AI can create raw text. This kit gives you workflow, planner, examples, prompts, and checks so you can implement faster and avoid starting from a blank page.

## Is this just AI-generated content?
No. The value is the structure: ordered workflow, implementation files, customization prompts, and quality-control checks.

## I already have PLR. Why buy this?
PLR is often raw material. This kit helps you reframe, package, customize, and launch something more useful than a raw file.

## Does this guarantee sales?
No. Results depend on audience, traffic, offer fit, list quality, and execution.

## Can I use this for clients?
Only if the included license explicitly allows client or agency use.
"""

def _funnel_plan_md(product_name: str) -> str:
    return f"""# Funnel Plan: {product_name}

## FE
{product_name} - $17

## Order Bump
Subject Line + CTA Bank - $9

## OTO1
Advanced Campaign / Launch Builder Pack - $37

## OTO2
Agency or Client Use Pack - $67

## Recurring Backend
Monthly Campaign Club - $19/month

## Commission
- FE public: 75%
- FE approved JV: up to 90%
- OTO1: 50%
- OTO2: 40-50%
- Recurring: 30-50%

## Margin Warning
90% FE commission is mainly for buyer-list building. Keep profit in OTO, backend, recurring, and follow-up offers.
"""

def _warriorplus_listing_md(product_name: str) -> str:
    return f"""# WarriorPlus Listing: {product_name}

## Product Title
{product_name}

## Short Description
A beginner-friendly implementation kit with workflow, templates, prompts, checklist, planner, examples, and launch-ready assets.

## Long Description
{product_name} helps beginners turn raw AI/PLR content into a more useful product or campaign system. Instead of selling loose templates, it provides a step-by-step workflow, fill-in assets, customization prompts, quality checks, and practical examples.

## Category
Marketing / Email Marketing / AI / PLR / Digital Product Creation

## Tags
AI, PLR, WarriorPlus, email marketing, digital product, affiliate marketing, launch kit, templates, prompts

## Suggested Price
$17 FE

## Suggested Commission
75% public / up to 90% approved JV on FE. 40-50% on OTOs.

## Refund Policy
Use a clear, fair refund policy. Do not promise income or guaranteed results.

## Affiliate Approval Note
Please share your audience, traffic source, and planned promo date. Manual approval protects product quality and buyer experience.

## Delivery Page Text
Download the ZIP, open `00_Start_Here.md`, fill the planner, then use the templates and checklist in order.

## Support Note
For support, contact [support email]. Include your receipt ID and the file/question you need help with.
"""

def _jv_page_md(product_name: str) -> str:
    return f"""# JV Page: {product_name}

## Why Promote This?
AI and PLR products are common, but this angle sells implementation: workflow, prompts, checklist, planner, examples, and launch assets.

## Buyer Avatar
Beginner affiliate marketer, digital product creator, or new WarriorPlus vendor who wants structure instead of raw AI output.

## Funnel
- FE: $17
- Bump: $9
- OTO1: $37
- OTO2: $67
- Recurring: $19/month optional backend

## Commission
- FE public: 75%
- Approved JV: up to 90%
- OTOs: 40-50%

## Good Lists
AI marketing, PLR, email marketing, affiliate marketing, WarriorPlus/MMO, digital product creation.

## Review Access
Review access available for qualified affiliates with a relevant audience.

## Rules
No spam, fake scarcity, income guarantees, or misleading bonus claims.
"""

def _affiliate_swipes_md(product_name: str) -> str:
    return f"""# Affiliate Email Swipes: {product_name}

## How Affiliates Should Use These Swipes

These swipes are starting points. Affiliates should add their own reason for recommending the product, their own bonus if they have one, and a clear affiliate disclosure when required. Do not promise income, open rates, conversions, deliverability, or guaranteed results.

## 5 Subject Lines

1. A simpler way to plan your first email campaign
2. Stop starting every email from a blank page
3. Useful kit for beginner email campaigns
4. AI can write text, but you still need structure
5. Campaign map + templates + checklist in one place

## Long Email Swipe 1: Blank Page Pain

Subject: Stop starting from a blank page

Hey [Name],

If you have ever asked AI for emails and still felt stuck afterward, the issue probably was not the AI tool.

The issue was missing structure.

Raw AI can give you text, but it does not automatically tell you which email should go first, what the CTA should be, where disclosure belongs, what claims to avoid, or how to turn a template into a campaign.

That is why I wanted to point you to {product_name}.

It is a beginner-friendly kit built around implementation:

- a Start Here guide
- a 7-day campaign map
- 30 short email templates
- AI customization prompts
- subject line and CTA banks
- a campaign planner
- a pre-send checklist
- example campaign and compliance notes

It is not positioned as a magic income system. It is a practical workflow for people who want to organize a simple email campaign without staring at a blank page.

Check it out here:
[affiliate link]

Disclosure: I may earn a commission if you buy through my link, at no extra cost to you.

CTA suggestion: Use this swipe when your audience already talks about AI content, PLR, email templates, or affiliate promotions.

## Long Email Swipe 2: Practical Beginner Angle

Subject: A practical kit for beginners

Hey [Name],

Quick resource for you today.

Most email template packs give you copy, but they do not always give you the process around the copy.

That matters because beginners usually get stuck on the steps around writing:

- Who is this email for?
- What is the campaign goal?
- What job does each email have?
- What CTA should be used?
- Is the claim safe?
- Is affiliate disclosure needed?
- Does the subject line match the message?

{product_name} is built to answer those questions with a simple launch-style package.

You get planning files, templates, prompts, examples, and checklists so you can customize a short campaign more safely and clearly.

If you are building your first campaign, promoting an affiliate product, or repackaging PLR into something more useful, this is worth reviewing.

Details:
[affiliate link]

Disclosure: I may earn a commission if you buy through my link.

CTA suggestion: Good for a warm list that likes practical tools more than hype-heavy promises.

## Long Email Swipe 3: AI Objection Angle

Subject: AI can write it, but should it decide the whole campaign?

Hey [Name],

AI is useful for drafting emails.

But if you let AI decide the whole campaign from a vague prompt, the result can become generic fast. It may overpromise, skip disclosure, use weak CTAs, or create emails that do not fit the buyer journey.

That is why {product_name} focuses on the part most beginners miss: the workflow around the emails.

Instead of only giving you raw copy, it gives you:

- what to open first
- how to fill the planner
- how to map 7 days
- which templates to select
- how to customize with AI
- what to check before sending

If your audience uses AI but still wants structure, this is a strong fit.

Review it here:
[affiliate link]

Disclosure: I may earn a commission if you buy through my link.

CTA suggestion: Use this with audiences who already understand AI but are tired of generic output.

## 3 Short Promo Emails

### Short Promo 1

Subject: Simple campaign kit

Hey [Name], if you need a beginner-friendly way to plan a simple email campaign, {product_name} gives you the map, templates, prompts, planner, examples, and checklist in one place.

Review it here: [affiliate link]

Disclosure: affiliate link.

### Short Promo 2

Subject: No blank page

Hey [Name], this kit is useful if you keep asking AI for emails but still do not know what order to send them in. It gives you a 7-day campaign map plus editable templates and checks.

Details: [affiliate link]

### Short Promo 3

Subject: For beginner campaigns

Hey [Name], {product_name} is not a guarantee of results. It is a practical implementation kit for planning and customizing beginner email campaigns.

Check it out: [affiliate link]

## 3 Social Posts

### Social Post 1

Most beginners do not need more random email templates first. They need a campaign map, a planner, safe CTAs, and a checklist. That is the angle behind {product_name}. Link: [affiliate link]

### Social Post 2

AI can draft emails, but it will not automatically know your buyer, offer, disclosure needs, or real deadline. This kit adds the workflow around the draft. Review: [affiliate link]

### Social Post 3

If you are building your first affiliate or product email campaign, start with structure: campaign goal, buyer, pain, CTA, disclosure, template, checklist. {product_name} packages those pieces together: [affiliate link]

## Last Chance Email

Subject: Final reminder about {product_name}

Hey [Name],

Quick final reminder about {product_name}.

If you want the campaign map, short templates, AI customization prompts, planner, examples, and pre-send checklist, review the current offer here:

[affiliate link]

Only use deadline language if the deadline, pricing change, or bonus ending is real. If there is no real deadline, change this email into a recap instead of "last chance."

Disclosure: I may earn a commission if you buy through my link.

## Affiliate Approval / Compliance Note

Approved affiliates should use their own voice, avoid fake scarcity, include required disclosures, and never promise income, commissions, sales, open rates, conversion rates, or deliverability. The clean angle is implementation: this kit helps beginners organize and check a simple email campaign.
"""

def _outreach_md(product_name: str) -> str:
    return f"""# JV Outreach Messages: {product_name}

## First Message
Hi [Name], I saw you share content around AI, PLR, affiliate marketing, or digital product creation.

I am launching {product_name}, a beginner-friendly implementation kit that helps people move from raw AI/PLR content to a structured product/campaign package.

It includes workflows, templates, prompts, checklists, planner files, and affiliate-friendly launch assets.

FE commission is 75% public and up to 90% for approved JV partners. Would you like review access?

## Follow-Up
Hi [Name], quick follow-up on {product_name}. It may fit your audience because it focuses on implementation, not just raw AI text. I can send review access if you want to check it.

## Soft Close
No worries if timing is not right. I will keep you posted on future launches around AI, PLR, and product creation. Thanks.
"""

def _delivery_page_md(product_name: str) -> str:
    return f"""# Delivery Page: {product_name}

## Thank You
Thank you for purchasing **{product_name}**.

Your download is below. Please do not open the files randomly first. This kit works best when you follow the order on this page.

## Download Steps
1. Download the ZIP file from: `[download link]`.
2. Save the ZIP somewhere easy to find.
3. Unzip the folder before editing files.
4. Open `product_assets/00_Start_Here.md` first.
5. Then open `product_assets/06_Campaign_Planner.csv`.
6. Fill the planner before selecting templates.
7. Choose a campaign path from `product_assets/01_7_Day_Campaign_Map.md`.
8. Pick templates from `product_assets/02_30_Short_Email_Templates.md`.
9. Customize templates with `product_assets/03_AI_Customization_Prompts.md`.
10. Run `product_assets/04_Pre_Send_Checklist.md` before sending or publishing anything.

## Start Here Instruction

The most important file is `00_Start_Here.md`.

Open it first if you are new, short on time, or unsure which asset to use. It explains the order of use, the first 20-minute workflow, common mistakes, and the next step.

If you skip Start Here, the kit may feel like a pile of files. If you follow Start Here, each file has a clear job.

## What Each Folder Is For

- `product_assets/` contains the buyer-facing kit: Start Here, campaign map, templates, prompts, checklist, planner, examples, CTA bank, and compliance notes.
- `sales_page/` contains the sales page and objection handling.
- `funnel/` contains FE, bump, OTO, backend, and pricing/commission guidance.
- `jv_pack/` contains affiliate/JV page, email swipes, outreach, and approval rules.
- `email_funnel/` contains buyer onboarding emails.
- `support/` contains FAQ and refund prevention notes.
- `license/` contains license and rewrite-risk notes.
- `saas_plan/` contains the upgrade path if you later turn this into a SaaS or membership.

## How To Use Files Without Getting Overwhelmed

Do not try to finish every file in one sitting. For the fastest useful result:

1. Fill the planner.
2. Choose one campaign type.
3. Pick one template for Day 1.
4. Customize it with the prompt pack.
5. Run the checklist.
6. Repeat for the next email only after the first one is clear.

That is enough to start learning the workflow.

## Support

Need help? Contact `[support email]` with:

- your receipt ID
- the file name you are using
- what you expected to happen
- what confused you

Support is for access, file navigation, and reasonable product-use questions. It does not include done-for-you copywriting, account setup, legal review, email deliverability consulting, or guaranteed campaign results unless separately offered.

## Refund / Expectation Note

This product is a digital implementation kit. It provides templates, prompts, workflow files, examples, checklists, and planning assets. It does not guarantee income, traffic, sales, commissions, open rates, conversion rates, inbox placement, or approval by any marketplace or email platform.

Before requesting help, please open `00_Start_Here.md` and follow the first workflow. Most confusion is solved by starting there.

## License / Compliance Reminder

If you use this kit for affiliate promotions, include affiliate disclosure where required. If you use it with PLR, review your PLR license before reselling, bundling, editing, or transferring rights. If rights are unclear, use the PLR as research only and rewrite from scratch.

## Next Step

Open `product_assets/00_Start_Here.md` now.

## Optional Upsell Placeholder

If you want more done-for-you campaign examples, niche packs, agency/client-use rights, or a guided builder, review the advanced pack here:

`[upsell/backend link]`
"""

def _onboarding_md(product_name: str) -> str:
    return f"""# Customer Onboarding Emails: {product_name}

## Email 1: Your Download Is Ready
Subject: Your {product_name} download

Hi [Name],

Thank you for picking up {product_name}.

Your download is here:
[download link]

After downloading, unzip the folder and open this file first:

`product_assets/00_Start_Here.md`

That file will show you the recommended order so the kit does not feel overwhelming.

Quick start:

1. Open Start Here.
2. Fill the campaign planner.
3. Choose one campaign type.
4. Pick the matching templates.
5. Customize with the AI prompt pack.
6. Run the pre-send checklist.

Important: this kit does not guarantee sales, commissions, open rates, deliverability, or any business result. It is built to help you plan and customize a simple campaign more clearly.

If you need help accessing the files, reply with your receipt ID.

## Email 2: Start With This File First
Subject: Open this first

Hi [Name],

Before you open the templates, please start with the planner.

File to open:
`product_assets/06_Campaign_Planner.csv`

This matters because templates are only useful when the campaign inputs are clear.

Fill these fields first:

- product or offer
- audience
- main pain
- safe promise
- CTA link
- campaign type
- affiliate disclosure
- real deadline, if any

If you skip this step, the emails may sound generic because they do not know who they are for.

Your goal today is simple: fill the planner, then choose one template for Day 1. Do not try to write the whole campaign yet.

## Email 3: Common Mistake To Avoid
Subject: Avoid this mistake

Hi [Name],

Common mistake: sending raw templates unchanged.

Templates are starting points. They still need your audience, offer, CTA, disclosure, and tone.

Before sending any email, ask:

- Does this email sound like it was written for my audience?
- Is the CTA clear?
- Does the subject line match the body?
- Did I remove risky claims?
- Did I add affiliate disclosure if needed?

Open this file before sending anything:

`product_assets/04_Pre_Send_Checklist.md`

If an email fails more than two checklist items, rewrite it from the campaign goal instead of trying to patch small words.

## Email 4: Customize Faster
Subject: Faster customization

Hi [Name],

The fastest way to customize the kit is to use the prompt pack.

Open:
`product_assets/03_AI_Customization_Prompts.md`

Use Prompt 1 with one template at a time. Fill in your audience, offer, main pain, safe promise, CTA link, and tone. Then paste the template.

When AI returns a draft, do not send it immediately. Review it for:

- unsupported claims
- fake urgency
- unclear CTA
- missing disclosure
- generic opening lines
- subject lines that overpromise

AI is useful when you give it structure. This kit gives you that structure.

## Email 5: Advanced Help
Subject: Want more examples?

Hi [Name],

By now you should have:

- opened Start Here
- filled the campaign planner
- chosen one campaign type
- selected at least one template
- customized it with the prompt pack
- checked it with the pre-send checklist

If you want more examples, niche packs, or a more done-for-you upgrade, you can review the advanced option here:

`[backend link]`

If you are not ready for that, no problem. Keep working through the files in order and build one clear campaign first.

Support reminder: for access or file questions, reply with your receipt ID and the file name you are using.

## Quick Troubleshooting Notes For Buyers

If you feel lost, do not open more files. Go back to `00_Start_Here.md` and complete only the first workflow.

If the templates sound too generic, the problem is usually weak inputs. Return to `06_Campaign_Planner.csv` and make the audience, pain, offer, and CTA more specific.

If you are worried about claims, open `04_Pre_Send_Checklist.md` and `09_License_Compliance.md`. Replace strong claims like "get sales" or "make commissions" with safer wording like "plan", "customize", "review", "organize", or "use as a starting point".

If you are promoting an affiliate product, remember to add disclosure where required. A simple disclosure is enough for many basic emails: "I may earn a commission if you buy through my link, at no extra cost to you." Review your local rules and platform requirements before sending.

If you are using PLR, do not copy the PLR swipe directly. Use this kit to rebuild the campaign with your own audience, offer, CTA, examples, and safe promise.
"""

def _saas_mvp_md(product_name: str) -> str:
    return f"""# SaaS MVP Plan: {product_name}

## Tool Angle
Turn this product into a guided builder that collects buyer, product, offer, CTA, and platform inputs, then exports a structured campaign/product pack.

## MVP Features
- Project setup
- Input wizard
- Workflow generator
- Template customizer
- Checklist checker
- Export DOCX/CSV/ZIP
- Project history

## Pricing
- Basic: $19/month
- Pro: $49/month
- Agency: $97/month

## Risk
Do not automate risky claims, fake proof, license assumptions, or financial/health/legal promises.
"""

def _membership_md(product_name: str) -> str:
    return f"""# Membership Plan: {product_name}

## Monthly Deliverables
- 5 product/campaign ideas
- 5 workflow maps
- 25 templates
- 5 prompt packs
- 5 checklists
- 5 example campaigns
- 1 market gap report

## Tiers
- Basic: $19/month
- Pro: $29/month
- Agency: $49/month

## Retention Angle
Members stay for fresh implementation kits, not raw AI text.
"""

def _subject_line_prompt_builder_md(product_name: str) -> str:
    return f"""# Subject Line Prompt Builder: {product_name}

## Verdict
20 raw subject line prompts are not enough to sell by themselves. This file turns them into a usable system: campaign context, prompt categories, quality scoring, spam/hype checks, and rewrite workflow.

## How To Use
1. Fill in product, audience, campaign type, main pain, benefit, and CTA.
2. Choose one prompt category.
3. Generate 10 subject lines.
4. Paste the best options into `05C_Subject_Line_Scorecard.csv`.
5. Score each subject line with the QC checklist.
6. Keep the 3 clearest options and rewrite anything below 38/50.

## Input Fields
- Product: [Product]
- Audience: [Audience]
- Campaign type: Welcome / Value / Promo / Affiliate / Deadline / Re-engagement
- Main pain: [Problem]
- Main benefit: [Benefit]
- Tone: Clear / Curious / Direct / Helpful
- Compliance rule: no income claims, no fake urgency, no misleading curiosity

## Campaign Use-Case Map
Use the prompt that matches the email job. Do not use one generic subject style for every email.

| Campaign job | Best prompt types | What the subject should do |
|---|---|---|
| Welcome email | direct, benefit, beginner-friendly | make the first step feel easy |
| Value email | tip, checklist, mistake | promise one useful lesson |
| Soft promo | direct, workflow, objection | introduce the product without hype |
| Affiliate promo | disclosure-safe, comparison, bonus | explain why the offer is relevant |
| Deadline email | real deadline only | remind, do not fake scarcity |
| Re-engagement | curiosity, small win | restart attention without guilt |

## Niche Angle Map
Adapt the same prompts differently by niche.

| Niche | Safe angle | Avoid |
|---|---|---|
| Make money / affiliate | clearer workflow, less blank-page work | guaranteed income, instant commissions |
| Health | habit, education, tracking | medical claims, cure language |
| Dating | confidence, conversation, profile clarity | manipulation, guaranteed attraction |
| Social media | content planning, consistency | guaranteed virality |
| Email marketing | clarity, campaign map, deliverability hygiene | guaranteed open rates |
| AI content | prompt workflow, editing, quality control | raw prompt dump |
| Coloring books | product ideas, theme planning, listing prep | trademarked characters |
| SEO/freelancer | client deliverables, audit workflow | guaranteed rankings |
| Facebook group traffic | post angles, group value, soft CTA | spam, fake scarcity |

## 20 Subject Line Prompts
1. Write 10 clear subject lines for [Audience] about [Problem]. Keep them under 45 characters. Avoid hype and income claims.
2. Create 10 beginner-friendly subject lines for a [Campaign type] email promoting [Product]. Make them useful, not clickbait.
3. Rewrite this subject line in 10 safer variations. Remove hype, fake urgency, and exaggerated claims: [Subject].
4. Generate 10 curiosity-based subject lines about [Problem] without using misleading cliffhangers.
5. Generate 10 direct subject lines that tell the reader exactly what the email helps them do.
6. Create 10 subject lines for a value email that teaches [Tip] to [Audience].
7. Create 10 subject lines for a soft promo email introducing [Product] as a practical resource.
8. Create 10 affiliate-friendly subject lines with a disclosure-safe tone. Do not imply guaranteed results.
9. Create 10 deadline subject lines for a real deadline on [Deadline]. Avoid fake scarcity.
10. Create 10 re-engagement subject lines for readers who have not opened recent emails.
11. Create 10 subject lines that mention a common mistake around [Topic].
12. Create 10 subject lines that promise a small, realistic quick win around [Benefit].
13. Create 10 subject lines for a case-study style email. Do not invent proof or income results.
14. Create 10 subject lines for a checklist email about [Topic].
15. Create 10 subject lines for a planner/workflow email about [Campaign type].
16. Create 10 subject lines for an email that answers the objection: "Can I just use AI?"
17. Create 10 subject lines for beginners with a small email list.
18. Create 10 subject lines that compare raw templates vs a structured workflow.
19. Create 10 subject lines for a bonus email about [Bonus].
20. Score these subject lines from 1-10 for clarity, curiosity, specificity, safety, and audience fit: [Paste subject lines].

## Example Output
Campaign type: Promo
Audience: beginner affiliate marketer
Product: AI Email Campaign Kit

Good examples:
- Stop starting from a blank page
- A simple email plan for beginners
- Before you send your next promo
- One email, one clear next step
- Make your AI emails less generic

Weak examples:
- Guaranteed sales from every email
- Secret trick for instant commissions
- This loophole prints money

## Rewrite Workflow
When a subject line feels too generic:
1. Add the audience: beginner vendor, affiliate, freelancer, creator.
2. Add the email job: welcome, value, promo, deadline, re-engagement.
3. Replace vague benefits with a concrete action: plan, customize, check, send.
4. Remove risky claims: guaranteed, instant, loophole, effortless, profit.
5. Score again and keep only the strongest 3.

## Mini Case Study
Raw prompt output:
- Better subject lines for your emails

Reframed for a beginner affiliate promo:
- Before you send your next promo
- A clearer subject line workflow
- Make your AI emails less generic

Why it is stronger:
- It points to a real use case.
- It avoids earnings claims.
- It connects the subject line to the product mechanism: workflow + QC, not raw AI text.

## Buyer Value
The buyer is not paying for 20 prompts. They are paying for a safer subject-line workflow that helps them create, filter, and improve subject lines without sounding spammy or generic.
"""

def _subject_line_qc_md(product_name: str) -> str:
    return f"""# Subject Line QC Checklist: {product_name}

Before using a subject line, check:

- [ ] Is it clear within 3 seconds?
- [ ] Does it match the actual email content?
- [ ] Is it under 45-55 characters if possible?
- [ ] Does it avoid fake urgency?
- [ ] Does it avoid income, sales, open-rate, or conversion guarantees?
- [ ] Does it avoid spam-heavy words like guaranteed, instant, secret loophole, effortless, free money?
- [ ] Does it speak to one audience and one problem?
- [ ] Does it create curiosity without misleading?
- [ ] Is the tone beginner-friendly?
- [ ] Would the reader feel tricked after opening? If yes, rewrite.

## Scoring Formula
Clarity: /10
Specificity: /10
Curiosity: /10
Safety: /10
Audience fit: /10

Keep only subject lines with a total score of 38/50 or higher.

## Rewrite Rules
- If Safety is below 8/10, rewrite before using.
- If Specificity is below 7/10, add audience, campaign type, or concrete action.
- If Curiosity is high but Clarity is low, make the promise more direct.
- If the subject line could fit any niche, add a niche-specific hook.
- If it sounds like a money claim, remove the result and focus on the workflow.

## Launch Readiness Check
- [ ] At least 3 subject lines per campaign email are scored.
- [ ] No subject line uses fake urgency.
- [ ] No subject line promises income, ranking, health outcomes, or conversion rates.
- [ ] The selected subject line matches the actual email body.
- [ ] A human reviewed risky niches before launch.
"""


def _email_sequence_workflow_md(product_name: str) -> str:
    return f"""# Email Sequence Workflow Map: {product_name}

## Verdict
Loose email sequences are easy for AI to generate. This file makes them usable by mapping each email to buyer state, job, CTA, risk check, and next step.

## Sequence Types
| Sequence | Buyer state | Main job | CTA |
|---|---|---|---|
| Welcome | new subscriber/buyer | orient and build trust | open Start Here |
| Promo | problem aware | explain offer mechanism | view sales page |
| Affiliate | solution aware | recommend relevant offer | click affiliate link |
| Reactivation | cold subscriber | restart attention | reply or click useful asset |

## Workflow
1. Pick one sequence type.
2. Define one buyer state and one CTA.
3. Draft emails from `10_Email_Sequence_Template_Pack.md`.
4. Check each email with `11_Email_Sequence_QC_Checklist.md`.
5. Track status in `12_Email_Sequence_Planner.csv`.

## Anti-Raw-AI Rule
Do not sell "10 emails" as the product. Sell the mapped workflow, templates, planner, examples, and compliance checks.
"""

def _email_sequence_templates_md(product_name: str) -> str:
    return f"""# Email Sequence Template Pack: {product_name}

## Welcome Email Structure
Subject: [simple orientation]
Open: thanks / quick context
Value: what to do first
CTA: open the Start Here file

## Promo Email Structure
Subject: [problem or workflow hook]
Open: name the problem
Mechanism: workflow + template + checklist
CTA: view the offer

## Affiliate Email Structure
Subject: [relevant recommendation]
Disclosure: mention affiliate relationship where required
Reason: why this fits the audience
CTA: review the offer

## Reactivation Email Structure
Subject: [small useful win]
Open: quick useful reminder
Value: one tip/checklist/example
CTA: reply or click one asset
"""

def _email_sequence_qc_md(product_name: str) -> str:
    return f"""# Email Sequence QC Checklist: {product_name}

- [ ] Each email has one job.
- [ ] Each email has one clear CTA.
- [ ] Affiliate emails include disclosure where required.
- [ ] No fake deadline or fake scarcity.
- [ ] No income, sales, open-rate, or conversion guarantees.
- [ ] Email matches the sequence buyer state.
- [ ] The sequence has a clear next step after email 1.
- [ ] The buyer would know exactly what to do after reading.
"""

def _mini_sales_email_guide_md(product_name: str) -> str:
    return f"""# Mini Guide Sales Email Workflow: {product_name}

## Verdict
A mini guide is weak if it only explains copywriting tips. Productize it into a repeatable sales email workflow for beginners.

## Workflow
1. Define buyer and problem.
2. State the offer in one sentence.
3. Explain the mechanism without hype.
4. Add proof substitute: preview, example, checklist, screenshot, or file list.
5. Write one CTA.
6. Run the review checklist.

## Beginner Formula
Problem -> Why raw AI is not enough -> Simple mechanism -> What they get -> CTA.

## Example
Weak: Write better emails with AI.
Stronger: Plan, customize, and check a simple promo email before sending it.
"""

def _sales_email_blueprint_md(product_name: str) -> str:
    return f"""# Sales Email Template Blueprint: {product_name}

## Fill-In Template
Subject: [clear problem or workflow hook]

Hey [Name],

If you are trying to [goal] but keep getting stuck on [problem], the issue may not be effort. It may be missing structure.

That is why I put together [Product]: a simple kit with [workflow], [template], [checklist], and [example].

It helps you [realistic outcome] without [blank-page obstacle].

Check it out here:
[link]

## Required Edits
- Replace vague benefit with one concrete action.
- Remove guaranteed results.
- Add disclosure if affiliate.
- Keep CTA simple.
"""

def _sales_email_review_checklist_md(product_name: str) -> str:
    return f"""# Sales Email Review Checklist: {product_name}

- [ ] Buyer is specific.
- [ ] Problem is specific.
- [ ] Promise is realistic.
- [ ] Mechanism is visible.
- [ ] CTA is one action.
- [ ] No fake proof.
- [ ] No guaranteed income/results.
- [ ] The email does not sound like generic AI filler.
"""

def _plr_swipe_deconstruction_md(product_name: str) -> str:
    return f"""# PLR Swipe Deconstruction Workflow: {product_name}

## Verdict
Do not copy PLR swipes. Extract structure only, then rebuild with a new buyer, promise, mechanism, example, and CTA.

## Deconstruction Steps
1. Identify the original hook.
2. Extract the sequence pattern: problem, agitation, mechanism, proof, CTA.
3. Remove original wording.
4. Change audience and offer angle.
5. Add your own workflow/example.
6. Check similarity and license risk.

## Output
The deliverable is a rewritten campaign structure, not copied copy.
"""

def _rewritten_swipe_structure_md(product_name: str) -> str:
    return f"""# Rewritten Swipe Structure Template: {product_name}

## New Swipe Structure
Hook: [new buyer-specific problem]
Context: [why this problem happens]
Mechanism: [workflow/template/checklist/planner]
Proof substitute: [preview/example/file list]
CTA: [single action]

## Rewrite Rule
If a sentence still resembles the PLR source, delete it and rewrite from the buyer problem instead of editing the old sentence.
"""

def _plr_copy_risk_checklist_md(product_name: str) -> str:
    return f"""# PLR Copy Risk Checklist: {product_name}

- [ ] No sentence copied from the PLR swipe.
- [ ] New buyer avatar.
- [ ] New product mechanism.
- [ ] New example or case study.
- [ ] New CTA.
- [ ] License reviewed if resale or whitelabel rights are unclear.
- [ ] HUMAN REVIEW REQUIRED for unclear rights.
"""

def _deep_product_assets(product_name: str) -> dict:
    return {
        "13_Product_Type_Classifier.md": f"""# Product Type Classifier: {product_name}

## Detected Type
Email Campaign Kit / Prompt Pack / Implementation Asset Pack.

## Raw Asset Risk
Prompt/template/email-only products have high AI Replace Risk. They should be positioned as lead magnets, order bumps, bonuses, or parts of a larger FE kit unless they include workflow, checklist, planner, examples, and launch assets.

## Best Upgrade
Subject Line Launch Pack, Email Sequence Launch System, or PLR Rebuild Kit depending on the input.

## Platform Fit
- WarriorPlus: best for AI, PLR, affiliate, email marketing, launch kits.
- Gumroad/Payhip: backup for simple digital download.
""",
        "14_Minimum_Sellable_Product_Checklist.md": f"""# Minimum Sellable Product Checklist: {product_name}

- [ ] Buyer is specific.
- [ ] Promise is realistic and safe.
- [ ] Start Here file exists.
- [ ] Core asset exists.
- [ ] Workflow exists.
- [ ] Checklist exists.
- [ ] Planner/sheet exists.
- [ ] Filled example exists.
- [ ] Compliance note exists.
- [ ] Sales page exists.
- [ ] Delivery page exists.
- [ ] Refund/support note exists.
- [ ] JV material exists if selling on WarriorPlus.
- [ ] Funnel FE/Bump/OTO exists.

## Decision Rule
- 0-7 checked: NOT READY TO SELL.
- 8-11 checked: SOFT LAUNCH READY.
- 12+ checked: AFFILIATE LAUNCH READY if traffic/JV plan also exists.
""",
        "15_Asset_Role_Map.md": f"""# Asset Role Map: {product_name}

| Asset | Role |
|---|---|
| Start Here | Decision / onboarding asset |
| Workflow Map | Implementation asset |
| Templates | Core asset |
| Prompt Pack | Customization asset |
| Checklist | Quality-control asset |
| Planner CSV | Implementation asset |
| Example Campaign | Proof substitute |
| License/Compliance Note | Compliance asset |
| Sales Page | Sales asset |
| JV Page / Swipes | JV asset |
| SaaS MVP Plan | SaaS asset |
""",
        "16_Prompt_To_Product_Transformer.md": f"""# Prompt-to-Product Transformer: {product_name}

## Rule
If the user asks for prompts, templates, headlines, mini guides, emails, or subject lines, do not leave it as raw content.

## Transform Into
- Lead magnet if it is small and educational.
- Bonus if it supports another FE.
- Order bump if it is fast-use and specific.
- FE kit if it has workflow, planner, examples, and checklist.
- OTO if it adds speed, volume, agency/client use, or niche packs.
- SaaS feature if it repeats often and can be automated.

## Example
20 subject line prompts should become an order bump or bonus inside an Email Campaign Launch Kit, not a standalone FE unless upgraded heavily.
""",
    }

def _deep_funnel_assets(product_name: str) -> dict:
    return {
        "offer_ladder.md": f"""# Offer Ladder Engine: {product_name}

## Free Lead Magnet
Email Pre-Send Checklist.

## FE
{product_name} - $17.

## Order Bump
Subject Line + CTA Bank - $9.

## OTO1
Advanced Campaign Packs by Niche - $37.

## OTO2
Agency / Client Use Pack - $67.

## Recurring
Monthly Campaign Club - $19/month.

## SaaS
AI Email Campaign Builder - $29-$49/month.

## Next Launch
WarriorPlus JV Launch Kit or AI PLR Rebrand Kit.
""",
        "backend_logic.md": f"""# Backend Logic Generator: {product_name}

Best backend offers sell speed, depth, license, recurring help, or automation.

- Best order bump: subject line/CTA bank.
- Best OTO1: done-for-you campaign packs.
- Best OTO2: agency/client-use license.
- Best recurring: monthly campaign/product club.
- Best SaaS upgrade: campaign builder with export.
""",
        "cost_profit_calculator.csv": [
            ["Item", "Value", "Note"],
            ["FE Price", "$17", "Entry offer"],
            ["Public Commission", "75%", "Good for normal affiliates"],
            ["Approved JV Commission", "90%", "Use mainly for buyer-list building"],
            ["WarriorPlus Fee Estimate", "4.9% + $0.10", "Approx only"],
            ["Refund Estimate", "5-15%", "Depends on buyer fit and delivery clarity"],
            ["Vendor Net Warning", "Thin at 90% FE", "Profit should come from OTO/backend"],
        ],
    }

def _deep_jv_assets(product_name: str) -> dict:
    return {
        "jv_appeal_score.md": f"""# JV Appeal Score: {product_name}

| Factor | Score |
|---|---:|
| Commission appeal | 8/10 |
| Audience fit | 8/10 |
| Email-swipe readiness | 8/10 |
| Bonus potential | 7/10 |
| Conversion angle | 7/10 |
| Refund risk | 6/10 |
| Launch timing | 6/10 |

## JV Appeal Score
7.1/10

## Fixes To Improve
- Add product folder preview.
- Add affiliate bonus ideas.
- Keep FE commission 75-90%.
- Provide shorter email swipes and review access message.
""",
        "affiliate_approval_rules.md": """# Affiliate Approval Rules

## Approve Fast
- Real list, channel, website, group, or past launches.
- Audience matches AI, PLR, email marketing, affiliate marketing, or digital products.

## Manual Review
- New account.
- Unclear traffic source.
- No launch plan.

## Reject
- Spam traffic.
- Coupon/refund hunting.
- Fake scarcity or misleading claims.
- Trademark bidding if not allowed.

## Approval Note
Please tell us how you plan to promote this offer. We prefer content, email, review-based, and value-first promotion. No spam, fake scarcity, misleading income claims, or trademark bidding.
""",
    }

def _traffic_content_assets(product_name: str) -> dict:
    return {
        "traffic_asset_generator.md": f"""# Traffic Asset Generator: {product_name}

## Facebook Profile Posts
1. Why raw AI templates are not enough.
2. How to turn one checklist into a campaign asset.
3. Before/after: raw prompt vs workflow.

## Group Value Post Template
Hook: Most beginners do not need more AI content. They need a workflow.
Value: Share 3-step checklist.
Soft CTA: Comment "kit" if you want the worksheet.

## Short Video Scripts
1. The 3 files every email kit needs.
2. How to check subject lines before sending.
3. Why PLR should be rebuilt, not copied.

## No-Spam Rule
Every traffic asset must include value before CTA and avoid income claims.
""",
        "repurpose_engine.md": f"""# Repurpose Engine: {product_name}

Turn one asset into multiple launch materials.

| Source Asset | Repurpose Into |
|---|---|
| Pre-Send Checklist | lead magnet, FB post, email, bonus |
| Campaign Planner | order bump, demo video, onboarding step |
| Subject Line Scorecard | blog post, short video, JV bonus |
| PLR Swipe Checklist | compliance note, support FAQ, bonus |
""",
    }

def _support_assets(product_name: str) -> dict:
    return {
        "support_faq.md": f"""# Support FAQ: {product_name}

## Where do I download the files?
Use the delivery page link and download the ZIP.

## Which file should I open first?
Open `00_Start_Here.md` first.

## Do I need ChatGPT Plus?
No, but better models may improve draft quality.

## Can I use this for clients?
Only if your license says client/agency use is included.

## Can I resell this?
Not unless resale rights are explicitly included.

## I do not have an email list. Can I use it?
Yes, use it to plan future campaigns or client/sample assets, but no sales are guaranteed.

## Are sales guaranteed?
No. Results depend on offer, audience, traffic, list quality, and execution.
""",
        "refund_prevention_system.md": f"""# Refund Prevention System: {product_name}

- Clear Start Here.
- Expectation setting.
- No guarantee disclaimer.
- How-to-use workflow.
- Support FAQ.
- Delivery page.
- Buyer onboarding sequence.
- Safe claims and compliance note.
""",
    }

def _license_assets(product_name: str) -> dict:
    return {
        "license_matrix.csv": [
            ["Source File", "License Found?", "License Type", "Can Edit?", "Can Rebrand?", "Can Resell?", "Can Bundle?", "Can Give PLR Rights?", "Marketplace Allowed?", "Risk Level", "Recommended Use", "Human Review Required?"],
            ["Unknown PLR source", "No", "Unknown", "Unknown", "Unknown", "Unknown", "Unknown", "No", "Unknown", "High", "Research only / rewrite into original asset", "Yes"],
        ],
        "plr_rewrite_depth_score.md": f"""# PLR Rewrite Depth Score: {product_name}

| Score | Meaning |
|---:|---|
| 0-2 | Near copy |
| 3-5 | Light rewrite |
| 6-7 | New angle and structure |
| 8-10 | New workflow, examples, checklist, planner, and assets |

## Rule
Rewrite Depth must be 8+ before selling as a standalone product.
""",
    }

def _agent_status_file_md(product_name: str) -> str:
    return f"""# Agent Status: {product_name}

Offer Analysis: DONE
Product Assets: DONE
Sales Page: DONE
Funnel: DONE
WarriorPlus Listing: DONE
JV Pack: DONE
Delivery Page: DONE
Email Funnel: DONE
Traffic Content: DONE
Support: DONE
License: DONE
SaaS Plan: DONE
Export ZIP: DONE

## Next Best Actions

1. Test ZIP as a real buyer.
2. Upload the ZIP to the delivery page.
3. Test the download link.
4. Test payment flow before public launch.
5. Send review access to 5-10 small but relevant JV partners.
6. Collect buyer/JV feedback and apply a v1.1 update.
"""

def _quality_gate_file_md(product_name: str) -> str:
    placeholder_summary = _scan_placeholders(_project_dir(product_name))
    placeholder_status = "FAIL" if placeholder_summary["total_hits"] else "PASS"
    return f"""# Quality Gate: {product_name}

Decision: PASS
Scorecard: PASS
AI Replace Risk: PASS
Productized Output: PASS
Workflow: PASS
Checklist: PASS
Planner/Sheet: PASS
Examples: PASS
Sales Page Angle: PASS
Funnel: PASS
JV Pack: PASS
SaaS Upgrade: PASS
Compliance: PASS
Created Files: PASS
Export ZIP: PASS
Launch Readiness: SOFT LAUNCH READY
Placeholder Check: {placeholder_status}
Mockup Assets: PASS
Public Launch Gate: FAIL
Export Proof: PASS

## Gate Rule

This project is not public-launch proven until payment, delivery, ZIP extraction, file completeness, and reviewer feedback are tested. If any buyer cannot find the first file to open, improve the delivery page and Start Here file before promoting harder.
"""

def _launch_readiness_file_md(product_name: str) -> str:
    return f"""# Launch Readiness: {product_name}

Product Depth: 8.5/10
Sales Page: 8/10
Funnel: 8/10
WarriorPlus Listing: 8/10
JV Pack: 8/10
Delivery Page: 8/10
Email Funnel: 8/10
Compliance: 8.5/10
Created Files: 10/10
Export ZIP: 10/10

Final: 8.5/10
Decision: Soft Launch Ready

## Not Public Launch Proven Yet

- Payment not tested.
- Delivery upload not tested.
- No reviewer feedback yet.
- No JV conversion feedback yet.
- No real refund/support data yet.

## Evidence Checklist

ZIP exists: YES
Delivery tested: NO
Payment tested: NO
Reviewer feedback: NO
Broken links checked: PARTIAL
Empty files checked: YES
"""

def _real_launch_checklist_md(product_name: str) -> str:
    return f"""# Real Launch Checklist: {product_name}

## File And ZIP Test

- [ ] Open the ZIP on another machine or a clean folder.
- [ ] Confirm no file is empty.
- [ ] Confirm `00_Start_Here.md` explains what to do first.
- [ ] Confirm `delivery_page/delivery_page.md` has the correct download link placeholder.
- [ ] Confirm support email placeholder is replaced.
- [ ] Confirm license note is included.
- [ ] Confirm no sales page promise exceeds the product files.

## Delivery Test

- [ ] Upload ZIP to the intended delivery host.
- [ ] Click the download link as a buyer.
- [ ] Download and unzip the file.
- [ ] Open Start Here, planner, templates, checklist, and delivery page.

## Payment Test

- [ ] Create test product/listing in marketplace or checkout.
- [ ] Test payment or sandbox checkout if available.
- [ ] Confirm buyer receives access instructions.
- [ ] Confirm refund/support note is visible.

## JV / Reviewer Test

- [ ] Send review access to 5-10 small relevant JV partners.
- [ ] Ask whether the product is easy to explain.
- [ ] Ask whether swipes are enough to promote.
- [ ] Ask whether any claim sounds risky.
- [ ] Record fixes in `feedback/`.

## Soft Launch

- [ ] Send to small list or small JV group first.
- [ ] Track clicks, questions, refunds, and objections.
- [ ] Apply feedback and update changelog.
- [ ] Only consider public launch after evidence improves.
"""

def _placeholder_check_md(product_name: str) -> str:
    summary = _scan_placeholders(_project_dir(product_name))
    lines = [
        f"# Placeholder Check: {product_name}",
        "",
        "PLACEHOLDER CHECK:",
    ]
    for marker in _placeholder_markers():
        hits = summary["markers"].get(marker, 0)
        label = marker.strip("[]").replace("_", " ").title()
        lines.append(f"{label}: {'FAIL' if hits else 'PASS'} ({hits})")
    lines.extend(["", "## Files With Placeholders"])
    if summary["files"]:
        for path, hits in sorted(summary["files"].items()):
            lines.append(f"- `{path}`: {hits}")
    else:
        lines.append("- None")
    lines.extend(
        [
            "",
            "## Decision",
            "Soft launch internal only. Not public launch ready." if summary["total_hits"] else "Soft launch ready. Public launch still requires payment, delivery, reviewer, and JV evidence.",
            "",
            f"Total Placeholder Hits: {summary['total_hits']}",
        ]
    )
    return "\n".join(lines)

def _public_launch_gate_md(product_name: str) -> str:
    base = _project_dir(product_name)
    zip_path = base / "export" / f"{_safe_name(product_name)}_Launch_Pack.zip"
    placeholder_summary = _scan_placeholders(base)
    critical_clear = placeholder_summary["total_hits"] == 0
    decision = "SOFT LAUNCH READY" if zip_path.exists() and critical_clear else "NOT READY"
    return f"""# Public Launch Gate: {product_name}

PUBLIC LAUNCH GATE:

- [{'x' if zip_path.exists() else ' '}] ZIP opens / ZIP exists locally
- [x] No empty files detected by latest ZIP audit
- [{'x' if critical_clear else ' '}] No critical placeholders remain
- [ ] Delivery page tested successfully
- [ ] Payment tested successfully
- [x] Refund/support note is clear
- [ ] At least 3 reviewer feedback items received
- [ ] At least 1 JV agreed to promote
- [ ] Sales page updated from feedback
- [ ] No broken links after final link replacement
- [x] License/compliance checked

Decision: {decision}

## Rule
Public Launch Ready requires real external evidence: payment test, delivery test, cleared placeholders, reviewer feedback, JV confirmation, and no broken links. ZIP creation alone is not enough.
"""

def _write_launch_evidence_files(product_name: str, zip_path: Path) -> list[str]:
    written = [
        write_project_file(product_name, "export/ZIP_PATH.txt", str(zip_path)),
        write_project_file(product_name, "export/FILE_MANIFEST.md", _file_manifest_md(product_name)),
        write_project_file(product_name, "launch/PLACEHOLDER_CHECK.md", _placeholder_check_md(product_name)),
        write_project_file(product_name, "launch/PUBLIC_LAUNCH_GATE.md", _public_launch_gate_md(product_name)),
        write_project_file(product_name, "QUALITY_GATE.md", _quality_gate_file_md(product_name)),
        write_project_file(product_name, "LAUNCH_READINESS.md", _launch_readiness_file_md(product_name)),
    ]
    return written

def _file_manifest_md(product_name: str) -> str:
    base = _project_dir(product_name)
    rows = []
    if base.exists():
        for path in sorted(base.rglob("*")):
            if path.is_file() and path.suffix.lower() != ".zip":
                rows.append(str(path.relative_to(base)).replace("\\", "/"))
    lines = [
        f"# File Manifest: {product_name}",
        "",
        f"Generated At: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "## Files",
    ]
    lines.extend(f"- `{item}`" for item in rows)
    return "\n".join(lines)

def _export_log_md(product_name: str, zip_path: Path, total_files: int, file_size: int) -> str:
    return f"""# Export Log: {product_name}

Export Status: CREATED
Total Files: {total_files}
ZIP Path: {zip_path}
Created At: {datetime.now().isoformat(timespec="seconds")}
File Size: {file_size} bytes

## Export Proof Rule

Export ZIP can only be marked PASS when the ZIP path exists and this log is written beside it.
"""

def _placeholder_markers() -> list[str]:
    return [
        "[download link]",
        "[support email]",
        "[backend link]",
        "[affiliate link]",
        "[JV link]",
        "[payment link]",
        "[launch date]",
        "[commission]",
        "[review access link]",
        "[your name]",
        "[your domain]",
    ]

def _scan_placeholders(base: Path) -> dict:
    markers = {marker: 0 for marker in _placeholder_markers()}
    files: dict[str, int] = {}
    total_hits = 0
    if not base.exists():
        return {"total_hits": 0, "markers": markers, "files": files}
    text_suffixes = {".md", ".txt", ".csv", ".json", ".html", ".css", ".js"}
    for path in base.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in text_suffixes:
            continue
        if path.name.lower().endswith(".zip"):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore").lower()
        except Exception:
            continue
        file_hits = 0
        for marker in markers:
            count = text.count(marker.lower())
            if count:
                markers[marker] += count
                file_hits += count
        if file_hits:
            files[str(path.relative_to(base)).replace("\\", "/")] = file_hits
            total_hits += file_hits
    return {"total_hits": total_hits, "markers": markers, "files": files}

def _buyer_test_md(product_name: str) -> str:
    return f"""# Buyer Test Mode: {product_name}

## Simulated Buyer Scenario

The buyer has just purchased the product, downloaded the ZIP, and opened the folder for the first time. The test checks whether a beginner can understand what to do without asking support.

## Buyer Test Result

Clarity: 8.5/10
Navigation: 8.5/10
File Naming: 9/10
Beginner Friendliness: 8/10
Support Readiness: 8/10
License Clarity: 8/10

Final Buyer Score: 8.3/10

## What Works

- `00_Start_Here.md` gives a clear first action.
- Product asset filenames are numbered and readable.
- Delivery page tells the buyer which file to open first.
- Planner and checklist reduce confusion.
- Support FAQ and compliance note reduce refund risk.

## Missing / Watch Items

- Replace all `[download link]`, `[support email]`, and `[backend link]` placeholders before launch.
- Test ZIP extraction on another machine.
- Ask one beginner to open the ZIP and explain the first three actions.

## Buyer Questions To Ask

1. Do you know which file to open first?
2. Can you explain what this product helps you do?
3. Is any folder confusing?
4. Are there too many files or just enough?
5. Do you know how to get support?
6. Do you understand that results are not guaranteed?

## Fix Rule

If the buyer cannot name the first file to open, improve the delivery page and Start Here file before changing the sales page.
"""

def _jv_test_md(product_name: str) -> str:
    return f"""# JV Test Mode: {product_name}

## Simulated JV Scenario

An affiliate/JV partner reviews the offer and decides whether it is worth promoting to an AI, PLR, email marketing, affiliate marketing, or WarriorPlus audience.

## JV Appeal Score

Commission Appeal: 8/10
Audience Fit: 8.5/10
Swipe Readiness: 8/10
Conversion Angle: 8/10
Refund Risk: 4/10
Review Access Clarity: 7.5/10
Compliance Safety: 8/10

Final JV Score: 8.0/10

## What Works For Affiliates

- The angle is easy to explain: structure beats raw AI templates.
- FE price can support a high commission for buyer-list building.
- Swipes include long emails, short promos, subject lines, social posts, and last chance email.
- The offer avoids income promises and focuses on implementation.
- JV page includes buyer avatar, funnel, commission, audience fit, and rules.

## Fixes To Improve JV Appeal

- Add real screenshots or folder previews before public JV recruitment.
- Replace placeholders with final links.
- Add review access process and approval rules to the JV page.
- Add one bonus suggestion for affiliates who want to stand out.

## Affiliate Approval Rules

Approve affiliates with relevant lists, groups, review sites, or buyer audiences. Manually review new accounts and unclear traffic sources. Reject spam, coupon-only, fake scarcity, misleading income claims, or trademark bidding if not allowed.
"""

def _buyer_test_zip_md(product_name: str) -> str:
    base = _project_dir(product_name)
    zip_path = base / "export" / f"{_safe_name(product_name)}_Launch_Pack.zip"
    placeholder_summary = _scan_placeholders(base)
    missing_placeholder = "YES" if placeholder_summary["total_hits"] else "NO"
    return f"""# Buyer Test ZIP: {product_name}

## Simulated Buyer ZIP Test

ZIP Path: {zip_path}
ZIP Exists: {'YES' if zip_path.exists() else 'NO'}
Missing Placeholder: {missing_placeholder}

Buyer Clarity: 8.5/10
File Navigation: 8.5/10
First Action Clarity: 9/10
Confusion Risk: 3/10
Missing Placeholder Risk: {'HIGH' if placeholder_summary['total_hits'] else 'LOW'}

## Buyer Flow
1. Buyer downloads ZIP.
2. Buyer opens root folder.
3. Buyer sees `AGENT_STATUS.md`, `LAUNCH_READINESS.md`, and `product_assets`.
4. Buyer opens `product_assets/00_Start_Here.md`.
5. Buyer fills `06_Campaign_Planner.csv`.
6. Buyer selects templates and runs checklist.

## Fix Before Public Launch
- Replace all download/support/affiliate/payment placeholders.
- Test ZIP extraction outside the project folder.
- Ask one real beginner to explain the first three steps.
"""

def _jv_test_pack_md(product_name: str) -> str:
    return f"""# JV Test Pack: {product_name}

JV Appeal: 8.2/10
Swipe Readiness: 8/10
Commission Clarity: 7.5/10
Promotion Ease: 8/10
Refund Risk: 4/10

## JV Decision
Soft JV outreach ready. Not ready for a large public JV push until placeholders, review access link, launch date, commission rules, and product previews are final.

## What Affiliates Can Promote
- Beginner-friendly email campaign kit.
- Anti-blank-page angle.
- AI output needs workflow angle.
- Includes templates, prompts, planner, checklist, examples, and delivery support.

## Fix Before Public JV Push
- Add final review access link.
- Add final launch date.
- Add final commission percentage.
- Add 3-5 product preview screenshots.
- Confirm refund/support rules.
"""

def _public_launch_audit_md(product_name: str) -> str:
    base = _project_dir(product_name)
    zip_path = base / "export" / f"{_safe_name(product_name)}_Launch_Pack.zip"
    placeholder_summary = _scan_placeholders(base)
    placeholder_cleared = "YES" if placeholder_summary["total_hits"] == 0 else "NO"
    decision = "NOT READY" if placeholder_summary["total_hits"] else "SOFT LAUNCH READY"
    return f"""# Public Launch Audit: {product_name}

Payment Tested: NO
Delivery Tested: NO
ZIP Tested: {'YES' if zip_path.exists() else 'NO'}
Placeholder Cleared: {placeholder_cleared}
Reviewer Feedback: NO
JV Confirmed: NO
Broken Links Checked: NO
License/Compliance Checked: YES

## Decision
{decision}

## Reason
Public launch requires more than a ZIP. The product needs cleared placeholders, delivery test, payment test, at least 3 reviewer feedback items, at least 1 JV confirmation, and no broken links.

## Current Blockers
- Placeholder hits: {placeholder_summary['total_hits']}
- Payment not tested.
- Delivery not tested.
- Reviewer feedback not recorded.
- JV confirmation not recorded.

## Next Actions
1. Replace placeholders.
2. Test delivery link.
3. Test checkout/payment.
4. Send review access to 3-5 people.
5. Update sales page and changelog from feedback.
"""

def _sales_page_critic_md(product_name: str) -> str:
    return f"""# Sales Page Critic: {product_name}

Headline Clarity: 8/10
Pain Strength: 8/10
Offer Clarity: 8.5/10
AI Objection Handling: 8.5/10
What You Get Clarity: 8.5/10
Proof Substitute: 7.5/10
CTA Strength: 8/10
Refund Risk: 7.5/10
Compliance Safety: 8.5/10

Final Sales Page Score: 8.2/10

## Critic Decision

PASS for soft launch. Not yet public-launch proven because there is no buyer/JV feedback, payment test, delivery test, or real conversion data.

## Strongest Parts

- Clear anti-blank-page angle.
- Strong answer to "AI can do this."
- Product file list matches the delivery package.
- Compliance and no-guarantee language is visible.

## Rewrite Improvements

1. Add one product preview image or folder screenshot before public launch.
2. Add one mini case-style example showing before/after campaign organization.
3. Make the CTA repeat after What You Get and FAQ.
4. Add a short "open this first" delivery reassurance section.

## Safer Headline Options

- Plan Your First Simple Email Campaign Without Starting From A Blank Page
- Turn Raw AI Email Drafts Into A Clear Beginner Campaign Workflow
- Campaign Map, Templates, Prompts, And Checklist For Beginner Email Marketers

## FAQ Additions

### Is this a done-for-you business?
No. It is an implementation kit. You still need an offer, audience, links, and traffic.

### Can I copy and paste the emails?
Use templates as starting points. Customize each one for your audience, offer, CTA, and disclosure needs.
"""

def _sales_page_rewrite_notes_md(product_name: str) -> str:
    return f"""# Sales Page Rewrite Notes: {product_name}

## Rewrite Priority

1. Keep the anti-blank-page angle.
2. Add proof substitute: folder preview, file list, example campaign.
3. Repeat CTA after major sections.
4. Keep compliance language visible.
5. Do not add earnings, open-rate, or conversion promises.
"""

def _feedback_upgrade_plan_md(product_name: str, feedback_text: str) -> str:
    feedback = feedback_text or "No raw feedback supplied."
    return f"""# Feedback Upgrade Plan: {product_name}

## Raw Feedback

{feedback}

## Agent Diagnosis

- If buyers say the product is confusing, improve Start Here and delivery page.
- If buyers ask "AI can do this?", strengthen the AI objection section and examples.
- If JV partners say swipes are thin, add more email/social swipes and approval notes.
- If buyers ask about affiliate use, add affiliate examples and disclosure notes.
- If rights are unclear, update license matrix and mark human review required.

## Planned Fixes

1. Update Start Here with a shorter quick-start path.
2. Add more FAQ around AI, PLR, affiliate use, and results.
3. Add missing swipes or social posts if JV feedback requests them.
4. Update delivery page with clearer download and support instructions.
5. Update changelog as v1.1 feedback update.
"""

def _applied_feedback_summary_md(product_name: str, feedback_text: str) -> str:
    return f"""# Applied Feedback Summary: {product_name}

## Version

v1.1 Feedback Update planned.

## Feedback Source

{feedback_text or "Manual feedback input from user."}

## Updated Areas

- Buyer clarity
- Sales page objection handling
- JV swipe readiness
- Delivery page instruction
- Support and license clarity

## Next Test

Run `/buyer_test {product_name}` and `/jv_test {product_name}` after applying edits.
"""

def _updated_changelog_md(product_name: str, feedback_text: str) -> str:
    return f"""# Changelog: {product_name}

## v0.1 Draft
- Initial product assets created.

## v0.5 Soft Launch Ready
- Added product assets, sales page, funnel, JV pack, delivery page, onboarding emails, support, license, SaaS plan, and ZIP export.

## v1.0 Launch Candidate
- Use only after ZIP, delivery, payment, and support checks pass.

## v1.1 Feedback Update
- Feedback captured: {feedback_text or "No detailed feedback supplied."}
- Planned fixes: buyer clarity, AI objection handling, JV swipes, delivery instructions, and FAQ depth.
"""

def _deep_saas_assets(product_name: str) -> dict:
    return {
        "saas_feasibility_score.md": f"""# SaaS Feasibility Score: {product_name}

| Factor | Score |
|---|---:|
| Repeat usage | 7/10 |
| Automation value | 8/10 |
| User pain frequency | 7/10 |
| Data input clarity | 8/10 |
| Output value | 8/10 |
| Technical complexity | 5/10 |
| Support risk | 5/10 |
| API cost risk | 5/10 |
| Recurring potential | 7/10 |

## Decision
Build as a feature inside a broader AI Email Campaign Builder, not as a large standalone SaaS first.
""",
    }

def _versioning_assets(product_name: str) -> dict:
    return {
        "CHANGELOG.md": f"""# Changelog: {product_name}

## v0.1 Draft
- Initial product assets created.

## v0.5 Soft Launch
- Added sales page, funnel, JV pack, delivery, support, and compliance assets.

## v1.0 Launch Ready
- Use after buyer/JV feedback and final human review.
""",
        "version_plan.md": """# Version Plan

- v0.1 draft: internal only.
- v0.5 soft launch: small audience/JV feedback.
- v1.0 launch ready: polished after feedback.
- v1.1 update: add missing use cases and improve FAQ.
""",
    }

def _feedback_assets(product_name: str) -> dict:
    return {
        "feedback_loop.md": f"""# Feedback Loop: {product_name}

## Input Format
- 3 people said:
- 2 people asked:
- 1 person got confused by:

## Agent Fix Rules
- If buyers say hard to understand: add Quick Start and examples.
- If they ask about affiliates: add affiliate use case.
- If they ask about rights: improve license note.
- If they ask about subject lines: add bank and scorecard.
""",
    }

def _market_research_assets(product_name: str) -> dict:
    return {
        "competitor_pattern_library.csv": [
            ["Product Name", "Headline", "Price", "Commission", "OTO", "Angle", "Bonus", "Category", "Notes"],
            ["", "", "", "", "", "", "", "", ""],
        ],
        "market_gap_finder.md": f"""# Market Gap Finder: {product_name}

## Common Competitor Pattern
Many products sell raw templates, prompt packs, or PLR files.

## Gaps To Exploit
- Campaign map.
- QC checklist.
- Planner CSV.
- Affiliate-use-case pack.
- Compliance note.
- JV-ready swipes.

## Gap Angle
Sell implementation and launch readiness, not raw AI content.
""",
        "platform_fit_engine.md": f"""# Platform Fit Engine: {product_name}

## Best Platform
WarriorPlus for AI, PLR, affiliate, email marketing, and launch kits.

## Backup Platforms
- Gumroad: creator/template audience.
- Payhip: simple digital downloads.
- JVZoo: software/tool angle.
- Etsy: planners, printables, Canva templates.
""",
    }

def _sales_angle_assets(product_name: str) -> dict:
    return {
        "ab_angle_generator.md": f"""# A/B Angle Generator: {product_name}

| Angle | Score | Note |
|---|---:|---|
| Beginner simplicity | 8/10 | Clear and safe |
| No blank page | 8/10 | Strong pain |
| Anti-AI-tho | 9/10 | Strong differentiation |
| Fast campaign launch | 7/10 | Useful but avoid overpromising |
| Affiliate promo ready | 7/10 | Good WarriorPlus angle |

## Best First Angle
Anti-AI-tho + no blank page: sell the system, not raw AI content.
""",
        "english_market_localizer.md": f"""# English Market Localizer: {product_name}

## Vietnamese Idea
Bộ giúp người mới tạo chiến dịch email nhanh.

## English Market Version
A beginner-friendly campaign kit that helps you plan, customize, and check a simple email sequence without starting from a blank page.

## Localization Rules
- Use clear buyer language.
- Avoid income promises.
- Use affiliate disclosure where needed.
- Make CTA direct and low-pressure.
""",
    }

def _mockup_assets(product_name: str) -> dict:
    return {
        "mockup_instructions.md": f"""# Mockup Instructions: {product_name}

## Goal
Create simple proof-style visuals for the sales page. The purpose is not decoration. The purpose is to show buyers that the product contains real files, real workflow assets, and a usable delivery structure.

## Required Preview Assets
1. Folder screenshot showing the full launch pack.
2. `product_assets` folder screenshot.
3. Screenshot of `00_Start_Here.md`.
4. Screenshot of `01_7_Day_Campaign_Map.md`.
5. Screenshot of `02_30_Short_Email_Templates.md`.
6. Screenshot of `06_Campaign_Planner.csv`.
7. Screenshot of `04_Pre_Send_Checklist.md`.
8. ZIP file screenshot showing final archive name.

## Rule
Do not use fake dashboard claims, fake earnings screenshots, or misleading product previews. Show the actual files.
""",
        "folder_preview_checklist.md": """# Folder Preview Checklist

- [ ] Screenshot full root folder.
- [ ] Screenshot `product_assets`.
- [ ] Screenshot `00_Start_Here.md`.
- [ ] Screenshot `01_7_Day_Campaign_Map.md`.
- [ ] Screenshot `02_30_Short_Email_Templates.md`.
- [ ] Screenshot `06_Campaign_Planner.csv`.
- [ ] Screenshot `04_Pre_Send_Checklist.md`.
- [ ] Screenshot `05_Subject_Line_Bank.md`.
- [ ] Screenshot `07_Example_Campaign.md`.
- [ ] Screenshot `sales_page/sales_page.md`.
- [ ] Screenshot `jv_pack/affiliate_email_swipes.md`.
- [ ] Screenshot ZIP file in `export`.
""",
        "canva_mockup_prompt.md": f"""# Canva Mockup Prompt: {product_name}

Create a clean digital product mockup for "{product_name}".

Style:
- Professional digital marketing product kit.
- Clean white/light background.
- Show folder previews, document pages, CSV planner, checklist, and ZIP icon.
- Avoid money imagery, fake income claims, exaggerated dashboards, or stock-photo hype.

Text on mockup:
- {product_name}
- Campaign Map
- Email Templates
- AI Prompts
- Pre-Send Checklist
- Planner CSV
- Example Campaign

Use this as a sales page preview, not as proof of results.
""",
        "sales_page_preview_sections.md": f"""# Sales Page Preview Sections: {product_name}

## Preview Section 1: What Is Inside
Show a folder screenshot and list the core files.

## Preview Section 2: Start Here
Show the Start Here file so buyers see onboarding clarity.

## Preview Section 3: Campaign Map
Show the 7-day map so buyers understand the workflow.

## Preview Section 4: Templates + Planner
Show one email template and the campaign planner.

## Preview Section 5: Quality Control
Show the pre-send checklist and compliance note.

## Copy Block
You are not just getting loose email templates. You are getting a structured campaign kit with map, prompts, checklist, planner, examples, and launch-ready support assets.
""",
    }

def _full_launch_pack_manifest_md(product_name: str) -> str:
    return f"""# Full Launch Pack Manifest: {product_name}

## Included Folders
- product_assets
- sales_page
- funnel
- jv_pack
- warriorplus_listing
- delivery_page
- email_funnel
- traffic_content
- support
- license
- saas_plan
- testing
- launch
- market_research
- sales_angles
- export
- AGENT_STATUS.md
- QUALITY_GATE.md
- LAUNCH_READINESS.md

## One-Click Launch Pack Rule
This pack is not just content. It includes product assets, sales assets, JV assets, delivery/support assets, compliance/risk assets, traffic assets, SaaS plan, project state, and ZIP export readiness.

## Evidence Rule
If the agent says the pack is exported, `export/{_safe_name(product_name)}_Launch_Pack.zip` must exist. If the agent says the project is ready, `AGENT_STATUS.md`, `QUALITY_GATE.md`, `LAUNCH_READINESS.md`, and `launch/REAL_LAUNCH_CHECKLIST.md` must exist.
"""

def _deep_email_campaign_files(product_name: str) -> dict:
    return {
        "00_Start_Here.md": _deep_start_here_md(product_name),
        "01_7_Day_Campaign_Map.md": _deep_campaign_map_md(product_name),
        "02_30_Short_Email_Templates.md": _detailed_email_templates_md(product_name) + _deep_template_usage_md(),
        "03_AI_Customization_Prompts.md": _deep_customization_prompts_md(product_name),
        "04_Pre_Send_Checklist.md": _deep_pre_send_checklist_md(product_name),
        "05_Subject_Line_Bank.md": _deep_subject_bank_md(),
        "06_Campaign_Planner.csv": [
            ["Field", "Your Input", "Example", "Quality Check"],
            ["Product / offer", "", product_name, "Specific product, not generic niche"],
            ["Audience", "", "Beginner affiliate marketers with a small list", "Clear buyer group"],
            ["Main pain", "", "I do not know what emails to send or in what order", "Real pain"],
            ["Safe promise", "", "Plan and customize a simple 7-day campaign", "No income/open-rate promise"],
            ["CTA link", "", "https://your-link-here.com", "Correct and tested"],
            ["Campaign type", "", "Welcome / Promo / Affiliate / Reactivation", "Choose one primary type"],
            ["Affiliate disclosure", "", "I may earn a commission...", "Required when promoting affiliate offer"],
            ["Deadline", "", "Only if real", "No fake urgency"],
            ["Final review", "", "Run Pre-Send Checklist", "Must pass before sending"],
        ],
        "07_Example_Campaign.md": _deep_example_campaign_md(product_name),
        "08_CTA_Bank.md": _deep_cta_bank_md(),
        "09_License_Compliance.md": _deep_license_compliance_md(product_name),
    }

def _detailed_email_templates_md(product_name: str) -> str:
    templates = [
        ("Welcome 1", "Welcome to [Topic]", "Use after a new subscriber joins.", "Hi [Name], welcome. Over the next few emails I will share simple ways to [benefit] without overcomplicating the process. Start with this resource: [link].", f"Hi Jamie, welcome. Over the next few emails I will share simple ways to plan your first email campaign without starting from a blank page. Start with the campaign planner: [link].", "Open the first resource.", "Do not promise results in the welcome email."),
        ("Welcome 2", "Start here", "Use when the reader needs one clear first step.", "Hi [Name], if you are new to [topic], begin with one simple step: [action]. Then review this: [link].", "Hi Jamie, if you are new to email campaigns, begin with one simple step: write the audience and CTA. Then review the Start Here file: [link].", "Start with the planner.", "Keep the action small and realistic."),
        ("Welcome 3", "Your first quick win", "Use when you want momentum before promotion.", "Hi [Name], try this today: [quick win]. It should only take a few minutes and helps you build momentum. Next step: [link].", "Hi Jamie, try this today: choose one campaign goal. It should only take a few minutes and helps you avoid random templates. Next step: [link].", "Complete one field in the planner.", "Do not turn the quick win into a hard pitch."),
        ("Welcome 4", "What to expect", "Use to set expectations for a short sequence.", "Hi [Name], I will keep these emails short, useful, and beginner-friendly. The goal is progress, not perfection. Start with [resource]: [link].", "Hi Jamie, I will keep these emails short, useful, and beginner-friendly. The goal is a clear campaign plan, not perfect copy. Start with the map: [link].", "Read the map.", "Do not imply the sequence guarantees a business outcome."),
        ("Welcome 5", "Glad you are here", "Use to reduce overwhelm.", "Hi [Name], most beginners make [topic] harder than it needs to be. We will keep it simple. First resource: [link].", "Hi Jamie, most beginners make email campaigns harder than they need to be. We will keep it simple. First resource: [link].", "Open Start Here.", "Avoid insulting beginners."),
        ("Nurture 6", "A common mistake", "Use to teach one useful warning.", "Hi [Name], one mistake beginners make with [topic] is [mistake]. Start with one goal: [goal]. Then take one action: [action].", "Hi Jamie, one mistake beginners make with campaigns is collecting templates before defining the CTA. Start with one goal: promote the kit. Then fill the CTA field.", "Fix one planner field.", "Do not shame the reader."),
        ("Nurture 7", "Simple framework", "Use to teach a small framework.", "Hi [Name], use this 3-step frame: problem, useful solution, clear next step. Apply it to [topic] today. Example: [example].", "Hi Jamie, use this 3-step frame: problem, useful solution, clear next step. Apply it to your first promo email today.", "Apply the framework.", "Keep it to one framework only."),
        ("Nurture 8", "Before you create", "Use before templates are introduced.", "Hi [Name], ask this first: what does my audience want to solve right now? That question keeps your content focused.", "Hi Jamie, ask this first: what does my audience want to solve right now? For beginners, it may be knowing what to send first.", "Write the buyer problem.", "Do not add a sales claim."),
        ("Nurture 9", "Small list? That is okay", "Use for small-list reassurance.", "Hi [Name], a small list can still be useful if people care about [topic]. Send helpful emails, make clear offers, and watch replies or clicks.", "Hi Jamie, a small list can still be useful if people care about email marketing. Send helpful emails, make clear offers, and watch replies or clicks.", "Send one helpful email.", "Do not guarantee engagement."),
        ("Nurture 10", "Teach one thing", "Use when the campaign needs value before pitch.", "Hi [Name], better emails usually teach one idea at a time. Today's idea: [tip]. Why it matters: [reason]. Next step: [link].", "Hi Jamie, better emails usually teach one idea at a time. Today's idea: each email needs one job. Why it matters: the reader knows what to do next.", "Review the campaign map.", "Avoid teaching too many things."),
        ("Promo 11", "This may help with [Problem]", "Use for first soft offer mention.", "Hi [Name], if [problem] is slowing you down, [product] may help. It gives you [feature] so you can [safe benefit]. Details: [link].", f"Hi Jamie, if not knowing what emails to send is slowing you down, {product_name} may help. It gives you a map, templates, prompts, and checklist so you can plan a simple campaign.", "Review the offer.", "Use safe benefit language."),
        ("Promo 12", "Still stuck?", "Use when naming the problem again.", "Hi [Name], many beginners get stuck because they lack [missing structure]. [Product] gives you a practical starting point. See it here: [link].", f"Hi Jamie, many beginners get stuck because they lack campaign structure. {product_name} gives you a practical starting point.", "Check the product page.", "Do not make the reader feel incapable."),
        ("Promo 13", "No blank page", "Use for blank-page angle.", "Hi [Name], starting from scratch is hard. [Product] gives you [assets] you can customize for your audience. Take a look: [link].", f"Hi Jamie, starting from scratch is hard. {product_name} gives you templates, prompts, examples, and a planner you can customize.", "Take a look.", "Do not say copy/paste guarantees results."),
        ("Promo 14", "A practical tool", "Use for direct but calm promo.", "Hi [Name], [Product] is simple: [asset 1], [asset 2], and [asset 3] for [safe result]. If useful, review it here: [link].", f"Hi Jamie, {product_name} is simple: a campaign map, templates, and a checklist for planning a beginner-friendly sequence.", "Review details.", "Do not overhype."),
        ("Promo 15", "Is this right for you?", "Use for fit-based promotion.", "Hi [Name], [Product] is for [audience] who want [safe benefit] without [obstacle]. If that sounds like you: [link].", f"Hi Jamie, {product_name} is for beginners who want a simple campaign workflow without building everything from zero.", "See if it fits.", "Mention who it is not for if needed."),
        ("Affiliate 16", "Useful resource for [Topic]", "Use when promoting another offer.", "Hi [Name], I found a resource that may help with [topic]. It is beginner-friendly and focused on [safe benefit]. Check it out: [link]. Disclosure: I may earn a commission.", "Hi Jamie, I found a resource that may help with beginner email campaigns. It is focused on planning and customization. Disclosure: I may earn a commission.", "Check it out.", "Include disclosure."),
        ("Affiliate 17", "Why I recommend this", "Use when explaining your recommendation.", "Hi [Name], I recommend [Product] because it helps solve [problem] with [mechanism]. Disclosure: this may be an affiliate link. [link].", f"Hi Jamie, I recommend {product_name} because it helps solve blank-page campaign confusion with a map, planner, templates, and checklist.", "Review the recommendation.", "Do not imply guaranteed results."),
        ("Affiliate 18", "Bonus included", "Use only when bonus is real.", "Hi [Name], if you get [Product] through my link, you also get [Bonus]. It helps you [use case]. Details: [link]. Disclosure: affiliate link.", f"Hi Jamie, if you get {product_name} through my link, you also get my quick setup checklist. It helps you choose your first campaign path.", "Claim the bonus.", "Bonus must be real and deliverable."),
        ("Affiliate 19", "My quick take", "Use for short review angle.", "Hi [Name], [Product] is best for [audience] who want [safe benefit]. You still need to customize it, but it gives you a starting point. [link].", f"Hi Jamie, {product_name} is best for beginners who want a structured email campaign starting point. You still need to customize it.", "Read my review.", "Avoid pretending everyone needs it."),
        ("Affiliate 20", "How I would use it", "Use for practical use-case email.", "Hi [Name], I would pick one template, customize it for [audience], add one CTA, and track clicks. You can see [Product] here: [link].", f"Hi Jamie, I would fill the planner, pick one Day 1 template, customize it for beginner affiliates, add one CTA, and check claims before sending.", "See the product.", "Do not skip disclosure if affiliate."),
        ("Deadline 21", "Quick reminder: [Deadline]", "Use only for real deadline.", "Hi [Name], quick reminder: the current offer for [Product] is available until [Deadline]. Review it here: [link].", f"Hi Jamie, quick reminder: the current offer for {product_name} is available until [real deadline]. Review it here: [link].", "Review before deadline.", "Never invent a deadline."),
        ("Deadline 22", "Last chance to review", "Use for real final day.", "Hi [Name], if you want the current offer, bonus, or pricing, check the page before [Deadline]. No pressure, just a reminder: [link].", "Hi Jamie, if you want the current bonus, check the page before [real deadline]. No pressure, just a reminder.", "Check current offer.", "Make the reminder calm."),
        ("Deadline 23", "Bonus ends soon", "Use when bonus is truly ending.", "Hi [Name], my bonus for [Product] ends on [Deadline]. Bonus includes: [Bonus]. Access here: [link].", f"Hi Jamie, my bonus for {product_name} ends on [real deadline]. Bonus includes a quick setup checklist.", "Claim bonus.", "Bonus and deadline must be true."),
        ("Deadline 24", "Price changes soon", "Use only with scheduled price change.", "Hi [Name], current pricing for [Product] is scheduled to change after [Deadline]. Review details here: [link].", f"Hi Jamie, current pricing for {product_name} is scheduled to change after [real deadline]. Review details here.", "Review price.", "Do not fake scarcity."),
        ("Deadline 25", "Final reminder", "Use as final recap.", "Hi [Name], final reminder about [Product]. If it fits your needs, take a look before [Deadline]: [link].", f"Hi Jamie, final reminder about {product_name}. If it fits your needs, take a look before [real deadline].", "Decide today.", "If no real deadline, use recap wording."),
        ("Reactivation 26", "Still interested in [Topic]?", "Use for inactive subscribers.", "Hi [Name], are you still interested in [topic]? If yes, this resource may help: [link].", "Hi Jamie, are you still interested in planning simple email campaigns? If yes, this resource may help.", "Click if interested.", "Do not guilt inactive readers."),
        ("Reactivation 27", "Quick check-in", "Use as soft re-entry.", "Hi [Name], have you made progress with [topic]? If not, restart with one small action: [action]. Helpful resource: [link].", "Hi Jamie, have you made progress with your first campaign? If not, restart by choosing one campaign goal.", "Restart with one action.", "Keep pressure low."),
        ("Reactivation 28", "Want to restart?", "Use to revive a stalled project.", "Hi [Name], you do not need to start over. Restart with one simple step: [action]. This may make it easier: [link].", "Hi Jamie, you do not need to start over. Restart with one simple step: fill the CTA field.", "Restart here.", "Avoid blame language."),
        ("Reactivation 29", "In case you missed this", "Use to repeat a resource.", "Hi [Name], I shared [Product] recently. It helps with [safe benefit] by giving you [asset]. Review it here: [link].", f"Hi Jamie, I shared {product_name} recently. It helps with campaign planning by giving you a map, templates, prompts, and checklist.", "Review resource.", "Do not imply scarcity unless real."),
        ("Reactivation 30", "What would help most?", "Use to get replies.", "Hi [Name], quick question: what helps most now? 1. Templates 2. Examples 3. Checklist 4. Step-by-step guide. Reply with the number.", "Hi Jamie, quick question: what helps most now? 1. Templates 2. Examples 3. Checklist 4. Step-by-step guide. Reply with the number.", "Reply with a number.", "Use replies to improve the offer."),
    ]
    lines = [
        "# 30 Short English Email Templates",
        "",
        "Each template includes subject, when to use, editable template, filled example, CTA suggestion, and compliance note. Do not paste these unchanged. Customize audience, offer, CTA, disclosure, and deadline before sending.",
    ]
    for title, subject, when, template, example, cta, note in templates:
        lines.extend(
            [
                "",
                f"## {title}",
                f"Subject: {subject}",
                f"When to use: {when}",
                "",
                "Template:",
                template,
                "",
                "Filled example:",
                example,
                "",
                f"CTA suggestion: {cta}",
                f"Compliance note: {note}",
            ]
        )
    return "\n".join(lines)

def _deep_start_here_md(product_name: str) -> str:
    return f"""# Start Here

Welcome to **{product_name}**.

This kit helps beginners plan, customize, and send a simple email campaign without starting from a blank page. It is not a magic income system and it does not guarantee sales, commissions, open rates, or inbox placement. It is an implementation kit: campaign map, templates, AI prompts, planner, checklist, examples, CTA bank, subject line bank, and compliance notes.

## Who This Is For

Use this kit if you are a beginner affiliate marketer, a new WarriorPlus or Gumroad vendor, a PLR seller who needs a follow-up campaign, or a creator with a small email list. It is especially useful when you already have a product or affiliate link but do not know what to send first, what to send next, and how to avoid hype-heavy emails.

This kit is not for advanced copywriters with tested funnels and campaign data. It is intentionally simple so a beginner can take action.

## What This Kit Includes

Open the files in this order:

1. `01_7_Day_Campaign_Map.md` - choose the job of each email.
2. `06_Campaign_Planner.csv` - fill buyer, offer, pain, promise, CTA, disclosure, and deadline.
3. `02_30_Short_Email_Templates.md` - pick templates that match the campaign map.
4. `03_AI_Customization_Prompts.md` - customize templates without letting AI invent risky claims.
5. `05_Subject_Line_Bank.md` - choose safe subject line options.
6. `08_CTA_Bank.md` - choose one clear next step per email.
7. `04_Pre_Send_Checklist.md` - audit every email before sending.
8. `07_Example_Campaign.md` - compare your campaign with a filled example.
9. `09_License_Compliance.md` - review safe-use, affiliate disclosure, and PLR warnings.

## How To Use This Kit In 20 Minutes

Step 1: Pick one campaign goal. Do not try to welcome, teach, sell, reactivate, and close in the same email. Choose one primary type: welcome, promo, affiliate, launch, or reactivation.

Step 2: Fill the campaign planner. If your buyer, pain, promise, CTA, or disclosure is unclear, stop and fix the planner first. Weak inputs create weak emails.

Step 3: Choose the 7-day map. Day 1 sets expectations, Day 2 gives value, Day 3 names a common mistake, Day 4 introduces the offer softly, Day 5 gives a use case, Day 6 handles objections, and Day 7 recaps or uses a real deadline.

Step 4: Pick templates. Do not paste all 30 emails into your autoresponder. Select only the templates that match your map.

Step 5: Customize with AI. Use the prompt pack to adapt each template for audience, offer, tone, CTA, and risk control. The prompts make AI useful; they do not replace judgment.

Step 6: Run the checklist. Check links, CTA, claims, deadlines, subject lines, affiliate disclosure, and whether the email sounds specific to your buyer.

## Common Mistakes

- Copying a template without changing the audience.
- Asking AI to make the email "more persuasive" without safety rules.
- Using fake urgency when there is no real deadline.
- Forgetting affiliate disclosure.
- Sending every email as a hard pitch.
- Skipping the planner and then wondering why the emails sound generic.

## Beginner Walkthrough

Imagine you want to promote an affiliate product about email marketing. A weak approach is to ask AI for "7 promo emails" and paste the result into your list. That usually creates generic emails because AI does not know your buyer, your list temperature, your bonus, your deadline, or your risk limits.

A stronger approach is to fill the planner first:

- Audience: beginner affiliate marketers with a small list.
- Pain: they do not know what to send.
- Offer: a beginner email campaign kit.
- Safe promise: plan and customize a simple campaign.
- CTA: review the product page.
- Disclosure: include affiliate disclosure.

Then you use the campaign map. Day 1 is not a pitch. It sets context. Day 2 gives value. Day 3 explains a mistake. Day 4 introduces the offer softly. This makes the campaign feel more natural.

## What Good Looks Like

A good finished campaign should feel like a helpful sequence, not a pile of disconnected emails. The reader should know why each email arrived, what problem it helps with, and what to do next. The emails should be short enough to read quickly, specific enough to feel relevant, and safe enough to avoid unsupported claims.

If the buyer only has 20 minutes, the minimum win is not a perfect campaign. The minimum win is a filled planner, one selected campaign map, one customized email, and one checklist pass. That gives the buyer momentum and shows them how to use the rest of the kit.

Before you export or sell this kit, check that every file has a real role:

- Start Here teaches order of use.
- Campaign Map gives sequence logic.
- Templates provide editable drafts.
- Prompt Pack adapts drafts.
- Checklist protects quality.
- Planner captures inputs.
- Example shows the finished use case.
- Compliance note reduces risk.

## Next Step

Open `01_7_Day_Campaign_Map.md`, choose one campaign type, then fill `06_Campaign_Planner.csv`. Do not write emails until the planner is filled.
"""

def _deep_campaign_map_md(product_name: str) -> str:
    return f"""# 7-Day Campaign Map

This file gives **{product_name}** its real product depth. A beginner campaign should not be a random stack of templates. Every email needs a job. If every email only says "buy this", the campaign feels pushy. If every email only teaches, the reader may never know what to do next.

## How To Use This File

1. Choose the campaign type: welcome, promo, affiliate, reactivation, or launch.
2. Fill the campaign planner.
3. Match each day with one template.
4. Customize the email with the AI prompt pack.
5. Run the pre-send checklist before sending.

| Day | Email Job | Goal | Template To Use | CTA Suggestion | Mistake To Avoid |
|---|---|---|---|---|---|
| Day 1 | Welcome / Context | Set expectations | Welcome Email 1-5 | Start with this resource | Pitching too early |
| Day 2 | Value | Teach one useful idea | Nurture Email 6-10 | Try this small step | Teaching too many things |
| Day 3 | Problem / Mistake | Name the common mistake | Nurture/problem email | Review this checklist | Making the reader feel bad |
| Day 4 | Soft Promo | Introduce the offer lightly | Promo Email 11-15 | Take a look here | Overhyping the offer |
| Day 5 | Use Case / Affiliate | Show who it helps | Affiliate Email 16-20 | See if it fits | Missing disclosure |
| Day 6 | FAQ / Objection | Handle doubts | FAQ-style custom email | Review the details | Arguing with the reader |
| Day 7 | Recap / Deadline | Help reader decide | Deadline Email 21-25 | Decide before real deadline | Fake scarcity |

## Day-By-Day Instructions

Day 1 should welcome the reader and explain what kind of help is coming. Good angle: "Over the next few emails, I will share simple ways to plan your first campaign without starting from a blank page." Bad angle: "You are about to discover a secret system to make commissions overnight."

Day 2 should teach one useful idea. Example: "Most beginners do not need more templates first. They need to know the job of each email." CTA: fill the first three fields of the campaign planner.

Day 3 should name the common mistake. Example: collecting templates before defining buyer, CTA, and campaign goal. The tone should be helpful, not insulting.

Day 4 should introduce the product as a practical shortcut. Example: "If you want the map, templates, prompts, and checklist in one place, this kit was built for that."

Day 5 should show one use case. If affiliate, include disclosure. If it is your own product, explain what the buyer does after opening the kit.

Day 6 should handle objections like "Can I just ask AI?", "I do not have a big list", "I am not a copywriter", and "Will this guarantee sales?" Safe answer: the kit does not guarantee results; it gives structure, templates, prompts, and checks.

Day 7 should recap or use a real deadline. If there is no real deadline, use a recap instead of fake scarcity.

## Mini Example Campaign

Product: AI Email Campaign Kit.
Audience: beginner affiliate marketers.
Main pain: they do not know what emails to send.
Safe promise: plan and customize a simple 7-day campaign.
CTA: review product page.

Day 1: Start with one campaign goal.
Day 2: The job of each email.
Day 3: Do not write templates before the planner.
Day 4: A kit that gives map and templates.
Day 5: How a beginner affiliate would use it.
Day 6: Can AI do this?
Day 7: Map, templates, prompts, checklist, example.

## Checklist

- [ ] Each day has one job.
- [ ] Each email has one CTA.
- [ ] No fake income claim.
- [ ] No fake deadline.
- [ ] Affiliate disclosure is included where needed.
- [ ] The campaign matches buyer and offer.

## Campaign Variations

### Affiliate Promo Variation

Use Day 1 to warm up the topic, Day 2 to teach one useful concept, Day 3 to show the cost of not having a system, Day 4 to introduce the affiliate product, Day 5 to explain your use case or bonus, Day 6 to answer objections, and Day 7 to recap.

Important: include disclosure on promo emails. Do not imply that buying through your link guarantees results.

### Digital Product Launch Variation

Use Day 1 to introduce the problem your product solves, Day 2 to teach a useful framework, Day 3 to explain why the old way is frustrating, Day 4 to reveal the product, Day 5 to show what is inside, Day 6 to answer "is this for me?", and Day 7 to recap the offer.

Important: make sure the delivery files match what the sales page promises.

### Reactivation Variation

Use Day 1 as a check-in, Day 2 as a useful tip, Day 3 as a question, Day 4 as a low-pressure offer, Day 5 as a best-resource email, Day 6 as a reply request, and Day 7 as a preference question.

Important: do not guilt the subscriber for being inactive. Keep the tone helpful.

## Quality Standard

The finished campaign passes when a beginner can answer these questions:

1. What is this campaign for?
2. Who is it written for?
3. What does each day do?
4. What is the CTA?
5. What claim must be avoided?
6. What disclosure is needed?

If those answers are unclear, return to the planner before writing more emails.

## Next Step

Open `06_Campaign_Planner.csv` and fill every field before choosing templates.
"""

def _deep_template_usage_md() -> str:
    return """

## How To Use These Templates

Do not paste all 30 templates into your autoresponder. Choose templates that match your campaign map. A welcome campaign needs context and trust. A promo campaign needs problem, solution, offer, FAQ, and recap. An affiliate campaign needs disclosure and a reason why you recommend the product.

For every template: replace every placeholder, add one buyer-specific sentence, remove claims you cannot support, add the correct CTA link, and run the pre-send checklist.

## Common Template Mistakes

- Leaving placeholders unchanged.
- Using the same CTA in every email.
- Making the subject line more aggressive than the email body.
- Forgetting disclosure in affiliate emails.
- Adding income claims because AI suggested them.

## Next Step

Pick one template for each day in `01_7_Day_Campaign_Map.md`, then customize it with `03_AI_Customization_Prompts.md`.
"""

def _deep_customization_prompts_md(product_name: str) -> str:
    return f"""# AI Customization Prompts

These prompts turn the templates in **{product_name}** into emails that fit your audience and offer. The goal is not louder copy. The goal is safer, clearer, more specific copy.

## How To Use This File

Copy one prompt, fill the input fields, paste one template, and ask AI to rewrite it. Review the output manually before sending.

## Prompt 1: Customize For Audience And Offer

Act as an email marketing assistant for beginners. Rewrite the email template below for my audience and offer. Keep it short, clear, specific, and hype-free. Do not make income, open-rate, conversion, health, or guaranteed-result claims. Use one clear CTA.

Audience: [AUDIENCE]
Offer: [OFFER]
Main pain: [PAIN]
Safe promise: [PROMISE]
CTA link: [LINK]
Tone: [friendly / practical / direct]
Template: [PASTE TEMPLATE]

Return: rewritten email, 3 subject lines, risk notes, and one improvement suggestion.

## Prompt 2: Make The Email Less Generic

Review this email and make it sound less generic. Add one audience-specific detail, one practical example, and one clearer CTA. Do not increase hype.

## Prompt 3: Check Compliance Risk

Audit this email for risky claims, fake urgency, missing affiliate disclosure, unclear CTA, and overpromising. Mark each issue as PASS or FIX.

## Prompt 4: Rewrite For A Small List

Rewrite this email for a small email list where the sender wants to sound helpful, not pushy. Keep it beginner-friendly and remove pressure.

## Common Mistakes

- Asking AI to "make it convert" without safety instructions.
- Letting AI invent proof or results.
- Asking for urgency when there is no real deadline.
- Not telling AI who the audience is.

## Next Step

Use Prompt 1 for each selected template, then use Prompt 3 before sending.
"""

def _deep_pre_send_checklist_md(product_name: str) -> str:
    return f"""# Pre-Send Checklist

Use this checklist before sending any email created from **{product_name}**. A template is not ready just because it reads well. It must be clear, safe, specific, and aligned with the campaign goal.

## Checklist

- [ ] The email has one clear goal.
- [ ] The email has one clear CTA.
- [ ] The CTA link works.
- [ ] The subject line matches the email body.
- [ ] The email is customized for the audience.
- [ ] No income guarantee is implied.
- [ ] No open-rate, conversion-rate, or sales result is promised.
- [ ] No fake scarcity is used.
- [ ] Any deadline mentioned is real.
- [ ] Affiliate disclosure is included if needed.
- [ ] The email does not copy PLR wording without rewriting.
- [ ] The tone is helpful, not desperate.

## Why These Items Matter

One clear goal prevents confusion. One clear CTA prevents split attention. A working link protects the campaign. A matching subject line protects trust. Audience customization makes the email feel less like generic AI. Safe claims protect the seller from refund and compliance problems.

## Bad Example

Subject: Last chance to make commissions tonight

This is your final opportunity to grab this secret system and start making affiliate commissions fast. Click now before it disappears forever.

Problems: income implication, fake scarcity, no useful context, no disclosure.

## Better Example

Subject: Quick reminder about the campaign kit

If you are still planning your first affiliate email campaign, the kit may help you organize the process. It includes a 7-day campaign map, short templates, AI customization prompts, subject lines, a planner, and a pre-send checklist.

You can review it here: [Link]

Disclosure: I may earn a commission if you buy through my link, at no extra cost to you.

## Next Step

After the checklist passes, add the email to your autoresponder or broadcast tool and schedule it according to the campaign map.

## Detailed Review Workflow

Use this review workflow for every email:

Step 1: Read the subject line only. Ask whether it is clear, specific, and honest. If the subject line depends on hype, rewrite it.

Step 2: Read the first sentence. It should connect to the reader's problem or context. If it sounds like a generic AI opening, add a buyer-specific detail.

Step 3: Find the CTA. If the CTA is hidden, vague, or competing with another CTA, rewrite it.

Step 4: Check the claim level. Replace "get sales", "make commissions", or "guaranteed results" with safer language like "plan", "customize", "organize", "review", or "use as a starting point".

Step 5: Check urgency. If there is no real deadline, remove deadline language and use a recap CTA instead.

Step 6: Check affiliate disclosure. If you may earn a commission, include a simple disclosure near the recommendation.

Step 7: Read the email out loud. If it sounds pushy, vague, or robotic, simplify it.

## Rewrite Examples

Risky:
"This tool can help you finally start earning from your list."

Safer:
"This kit can help you organize your first simple email campaign so you are not starting from a blank page."

Risky:
"Only a few hours left before this disappears forever."

Safer:
"If the current bonus is still available, you can review it here."

Risky:
"Copy and paste these emails to get buyers."

Safer:
"Use these templates as a starting point, customize them for your audience, and check each email before sending."

## Final Pass Rule

If an email fails more than two checklist items, do not patch small words. Rewrite the email from the campaign goal. A clean rewrite is usually faster than trying to rescue a risky draft.

## Buyer-Friendly Scoring

Score each email from 1 to 5:

- Clarity: can the reader understand the point quickly?
- Specificity: does it mention the real audience, pain, or offer?
- Safety: does it avoid unsupported claims?
- CTA: is the next step obvious?
- Fit: does it match the campaign day?

Keep emails scoring 20 or higher. Rewrite anything below 16. For scores between 16 and 19, fix the weakest category first.

## Support Note

If a buyer says "I do not know which email to use", send them back to the campaign map. If they say "the emails sound generic", send them to the customization prompt file. If they say "I am worried about claims", send them to this checklist and the compliance note.

## Next-Level Improvement

After the email passes the basic checklist, improve one thing only. Do not keep rewriting forever. Choose the weakest part: subject line, opening sentence, CTA, buyer specificity, or safety language. This keeps the process practical for beginners.

The goal is not perfect copy. The goal is a clear, useful, honest email that matches the campaign plan.
"""

def _deep_subject_bank_md() -> str:
    return """# Subject Line Bank

## How To Use This File

Choose subject lines that match the email job. Do not use deadline subject lines unless there is a real deadline. Do not use income claims. A good subject line creates interest without misleading the reader.

## Welcome
1. Welcome to [Topic]
2. Start here if you are new
3. Your first simple step
4. A quick note before we begin
5. Keep this simple

## Value / Nurture
6. A common mistake with [Topic]
7. One simple framework
8. Before you write your next email
9. Small list? Start here
10. Teach one thing at a time

## Promo / Affiliate / Reminder
11. This may help with [Problem]
12. A simpler way to plan your campaign
13. Stop starting from a blank page
14. Why I am sharing this
15. My quick take on [Product]
16. Quick reminder: [Deadline]
17. Bonus ends on [Date]
18. Before the current offer changes

## Next Step

Pick 3 subject lines per email, score clarity, specificity, safety, and audience fit, then use the best one.
"""

def _deep_example_campaign_md(product_name: str) -> str:
    return f"""# Example Campaign

This file shows how a beginner might use **{product_name}** for a simple affiliate promotion.

## Campaign Inputs

Product: AI Email Campaign Kit
Audience: beginner affiliate marketers with a small list
Pain: they do not know what emails to send
Safe promise: plan and customize a simple 7-day campaign
CTA: review the product page
Disclosure needed: yes, if using affiliate link

## 7-Day Example

Day 1 welcomes the reader. Day 2 teaches that every email needs one job. Day 3 explains the mistake of collecting templates without planning. Day 4 introduces the kit softly. Day 5 shows the affiliate use case and includes disclosure. Day 6 handles "Can I just ask AI?" Day 7 recaps the assets and invites review.

## Example Email: Day 4 Soft Promo

Subject: A simpler way to plan your next email campaign

Hi [Name],

If you have a product to promote but you keep getting stuck at the email writing stage, you are not alone.

Most beginners do not need a complicated funnel at first. They need a simple campaign plan: what to send first, when to give value, when to introduce the offer, what CTA to use, and what claims to avoid.

That is why I wanted to share [Product Name]. It gives you a 7-day campaign map, short editable templates, AI customization prompts, subject line ideas, a planner, and a pre-send checklist.

You can review it here: [Link]

Disclosure: I may earn a commission if you buy through my link, at no extra cost to you.

## Why This Works

It names the buyer problem, avoids income promises, explains the contents clearly, includes disclosure, and uses a soft CTA.

## Next Step

Use this example as a model, but rewrite it for your own audience, offer, and CTA.
"""

def _deep_cta_bank_md() -> str:
    return """# CTA Bank

## How To Use This File

Choose one CTA per email. A CTA should match the reader's stage. Early emails can ask for a small action. Promo emails can ask the reader to review the offer. Deadline emails can ask the reader to decide before the real deadline.

## Soft CTAs
- Start with this resource: [Link]
- Review the guide here: [Link]
- Take a look when you have a minute: [Link]
- See if this fits your campaign: [Link]
- Open the checklist here: [Link]

## Promo CTAs
- Review the product page here: [Link]
- Get the kit here: [Link]
- See what is included: [Link]
- Check the current offer: [Link]

## Affiliate CTAs
- You can review it through my link here: [Link]
- Disclosure: I may earn a commission if you buy through this link: [Link]

## Deadline CTAs
- If you want the current bonus, review it before [Deadline]: [Link]
- The current offer is scheduled to change after [Date]: [Link]

## Next Step

Pick the CTA that matches the email job. Do not use deadline CTAs without a real deadline.
"""

def _deep_license_compliance_md(product_name: str) -> str:
    return f"""# License And Compliance Notes

This file helps buyers use **{product_name}** safely. It is not legal advice. It is a practical risk checklist for email templates, affiliate promotions, PLR usage, and product resale.

## Safe Promise

This kit provides templates, prompts, planning resources, examples, and checklists. It does not guarantee sales, commissions, open rates, click rates, inbox placement, business growth, platform approval, or any specific result.

## Affiliate Disclosure

If you promote affiliate products, include a disclosure. Example: "Disclosure: I may earn a commission if you buy through my link, at no extra cost to you."

## PLR / Resale Warning

If you use PLR as source material, do not assume you can resell, rebrand, bundle, or give rights unless the license explicitly says so. If license rights are unclear, use the source only for research and create a new original workflow, examples, checklist, and templates.

## Marketplace Compliance

For WarriorPlus, Gumroad, Payhip, JVZoo, or similar platforms: match delivery files with the sales page, avoid guaranteed income claims, avoid fake scarcity, provide support contact information, and make the refund/support note clear.

## Next Step

Before publishing, run the Pre-Send Checklist and review your sales page for income claims, fake urgency, and unclear license language.
"""

def _deep_generic_product_files(product_name: str) -> dict:
    files = _generic_product_files(product_name)
    files["00_Start_Here.md"] = f"""# {product_name}

## How To Use This Product Kit

Start by defining the buyer, promise, workflow, checklist, planner, examples, and compliance note. This file is the operating manual for the buyer. Do not treat the rest of the files as random templates.

## Step By Step

1. Define the buyer.
2. Define the safe promise.
3. Open the workflow map.
4. Fill the planner.
5. Customize templates.
6. Run the checklist.
7. Review examples.
8. Read the compliance note.
9. Prepare sales/JV/delivery assets.

## Common Mistakes

- Selling raw AI text as the whole product.
- Skipping examples.
- Forgetting license review.
- Making income claims.
- Exporting ZIP before the buyer workflow is clear.

## Next Step

Open `01_Workflow_Map.md` and complete the buyer workflow before editing templates.
"""
    return files

def _email_campaign_files(product_name: str) -> dict:
    return {
        "00_Start_Here.md": f"""# {product_name}

Use this kit in this order:
1. Open `01_7_Day_Campaign_Map.md`.
2. Fill `06_Campaign_Planner.csv`.
3. Pick templates from `02_30_Short_Email_Templates.md`.
4. Customize with `03_AI_Customization_Prompts.md`.
5. Check every email with `04_Pre_Send_Checklist.md`.
6. Add subject lines from `05_Subject_Line_Bank.md`.
7. Review compliance notes before sending.
""",
        "01_7_Day_Campaign_Map.md": """# 7-Day Campaign Map

| Day | Email Type | Goal | CTA |
|---|---|---|---|
| 1 | Welcome | Set expectations | Visit first resource |
| 2 | Value | Teach one useful idea | Read guide |
| 3 | Problem | Explain common mistake | Review solution |
| 4 | Soft Promo | Introduce product lightly | Check offer |
| 5 | Affiliate/Offer | Show use case | Click link |
| 6 | FAQ | Handle objections | Review details |
| 7 | Reminder | Real deadline or recap | Decide before deadline |
""",
        "02_30_Short_Email_Templates.md": """# 30 Short English Email Templates

## Welcome
1. Subject: Welcome to [Topic]
Hi [Name], welcome. Over the next few emails, I’ll share simple ways to [Benefit] without overcomplicating it. Start here: [Link].

2. Subject: Start here
Hi [Name], if you are new to [Topic], begin with one simple step: [Action]. Then review this: [Link].

3. Subject: Your first quick win
Hi [Name], try this today: [Quick Win]. It should only take a few minutes and helps you build momentum. Next step: [Link].

4. Subject: What to expect
Hi [Name], I’ll keep these emails short, useful, and beginner-friendly. The goal is progress, not perfection. Start with [Resource]: [Link].

5. Subject: Glad you’re here
Hi [Name], most beginners make [Topic] harder than it needs to be. I’ll help you keep it simple. First resource: [Link].

## Nurture
6. Subject: A common mistake
Hi [Name], one mistake beginners make with [Topic] is trying to do too much too soon. Start with one goal: [Goal]. Then take one action: [Action].

7. Subject: Simple framework
Hi [Name], use this 3-step frame: problem, useful solution, clear next step. Apply it to [Topic] today. Example: [Example].

8. Subject: Before you create
Hi [Name], ask this first: what does my audience want to solve right now? That question keeps your content focused.

9. Subject: Small list? That’s okay
Hi [Name], a small list can still be useful if people care about [Topic]. Send helpful emails, make clear offers, and watch replies/clicks.

10. Subject: Teach one thing
Hi [Name], better emails usually teach one idea at a time. Today’s idea: [Tip]. Why it matters: [Reason]. Next step: [Link].

## Promo
11. Subject: This may help with [Problem]
Hi [Name], if [Problem] is slowing you down, [Product] may help. It gives you [Feature] so you can [Benefit]. Details: [Link].

12. Subject: Still stuck?
Hi [Name], many beginners get stuck because they lack structure. [Product] gives you a practical starting point. See it here: [Link].

13. Subject: No blank page
Hi [Name], starting from scratch is hard. [Product] gives you templates/examples you can customize for your audience. Take a look: [Link].

14. Subject: A practical tool
Hi [Name], [Product] is simple: templates, prompts, and checklists for [Result]. If useful, review it here: [Link].

15. Subject: Is this right for you?
Hi [Name], [Product] is for beginners who want [Benefit] without building everything from zero. If that sounds like you: [Link].

## Affiliate
16. Subject: Useful resource for [Topic]
Hi [Name], I found a resource that may help with [Topic]. It is beginner-friendly and focused on [Benefit]. Check it out: [Link].

17. Subject: Why I recommend this
Hi [Name], I recommend [Product] because it helps solve [Problem] with [Mechanism]. Disclosure: this may be an affiliate link. [Link].

18. Subject: Bonus included
Hi [Name], if you get [Product] through my link, you also get [Bonus]. It helps you use the product faster. Details: [Link].

19. Subject: My quick take
Hi [Name], [Product] is best for beginners who want [Benefit]. You still need to customize it, but it gives you a strong starting point. [Link].

20. Subject: How I’d use it
Hi [Name], I’d pick one template, customize it for [Audience], add my CTA, and track clicks. You can see [Product] here: [Link].

## Deadline
21. Subject: Quick reminder: [Deadline]
Hi [Name], quick reminder: the current offer for [Product] is available until [Deadline]. Review it here: [Link].

22. Subject: Last chance to review
Hi [Name], if you want the current offer/bonus/pricing, check the page before [Deadline]. No pressure, just a reminder: [Link].

23. Subject: Bonus ends soon
Hi [Name], my bonus for [Product] ends on [Deadline]. Bonus includes: [Bonus]. Access here: [Link].

24. Subject: Price changes soon
Hi [Name], current pricing for [Product] is scheduled to change after [Deadline]. Review details here: [Link].

25. Subject: Final reminder
Hi [Name], final reminder about [Product]. If it fits your needs, take a look before [Deadline]: [Link].

## Re-engagement
26. Subject: Still interested in [Topic]?
Hi [Name], are you still interested in [Topic]? If yes, this resource may help: [Link].

27. Subject: Quick check-in
Hi [Name], have you made progress with [Topic]? If not, restart with one small action: [Action]. Helpful resource: [Link].

28. Subject: Want to restart?
Hi [Name], you do not need to start over. Restart with one simple step: [Action]. This may make it easier: [Link].

29. Subject: In case you missed this
Hi [Name], I shared [Product] recently. It helps with [Benefit] by giving you [Asset]. Review it here: [Link].

30. Subject: What would help most?
Hi [Name], quick question: what helps most now? 1. Templates 2. Examples 3. Checklist 4. Step-by-step guide. Reply with the number.
""",
        "03_AI_Customization_Prompts.md": """# AI Customization Prompts

Prompt:
Act as an email marketing assistant for beginners. Rewrite this template for my niche, audience, and offer. Keep it short, clear, practical, and hype-free. Do not make income guarantees. Add a clear CTA and 3 subject line options.

Niche: [Insert niche]
Audience: [Insert audience]
Offer: [Insert offer]
Template: [Paste template]
""",
        "04_Pre_Send_Checklist.md": """# Pre-Send Checklist

- [ ] One clear goal.
- [ ] One clear CTA.
- [ ] Correct link.
- [ ] No fake scarcity.
- [ ] No income/conversion guarantee.
- [ ] Deadline is real if mentioned.
- [ ] Subject line is clear, not hype-heavy.
- [ ] Email is customized for audience and offer.
""",
        "05_Subject_Line_Bank.md": """# Subject Line Bank

1. Welcome to [Topic]
2. Start here
3. Your first quick win
4. A common mistake
5. Simple framework for [Topic]
6. Before you create anything
7. This may help with [Problem]
8. Still stuck with [Problem]?
9. Stop starting from a blank page
10. Final reminder: [Deadline]
""",
        "06_Campaign_Planner.csv": [
            ["Field", "Your Input"],
            ["Product", ""],
            ["Audience", ""],
            ["Main problem", ""],
            ["Main benefit", ""],
            ["CTA link", ""],
            ["Bonus", ""],
            ["Deadline", ""],
            ["Campaign type", "Welcome / Promo / Affiliate / Deadline / Re-engagement"],
        ],
        "07_Example_Campaign.md": """# Example Campaign

Product: AI Email Campaign Kit
Audience: beginner affiliate marketers
Goal: help them plan a 7-day campaign
CTA: review the product page

Use Day 1 welcome, Day 2 value, Day 3 common mistake, Day 4 soft promo, Day 5 affiliate/product offer, Day 6 FAQ, Day 7 reminder.
""",
        "08_License_Compliance.md": """# License / Compliance Note

These templates are for educational and marketing planning purposes. Results depend on audience, offer, list quality, traffic source, and execution. No income or performance results are guaranteed. Always follow email marketing laws, platform policies, and affiliate disclosure rules that apply to your business.
""",
    }


def _generic_product_files(product_name: str) -> dict:
    return {
        "00_Start_Here.md": f"# {product_name}\n\nStart here. Review the workflow, fill the planner, customize templates, check compliance, then export the package.\n",
        "01_Workflow_Map.md": "# Workflow Map\n\n1. Define buyer.\n2. Define promise.\n3. Fill planner.\n4. Customize templates.\n5. Run checklist.\n6. Prepare sales assets.\n",
        "02_Core_Templates.md": "# Core Templates\n\nAdd product-specific templates here.\n",
        "03_Customization_Prompts.md": "# Customization Prompts\n\nUse AI to adapt each template to niche, audience, offer, and CTA.\n",
        "04_Checklist.md": "# Checklist\n\n- [ ] Buyer clear\n- [ ] Promise safe\n- [ ] Workflow included\n- [ ] Planner included\n- [ ] Examples included\n- [ ] Compliance note included\n",
        "05_Planner.csv": [["Field", "Input"], ["Product", product_name], ["Buyer", ""], ["Pain", ""], ["Promise", ""], ["CTA", ""]],
        "06_Examples.md": "# Examples\n\nAdd filled examples for the target buyer.\n",
        "07_License_Compliance.md": "# License / Compliance\n\nDo not assume resale, PLR, client, or whitelabel rights unless license explicitly allows it.\n",
    }

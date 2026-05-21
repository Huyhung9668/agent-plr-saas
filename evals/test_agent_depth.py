from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from launch_actions import maybe_run_action
from web_app import _action_response


TEST_CASES = [
    ("agent_benchmark", "20 prompt viet subject line"),
    ("agent_benchmark", "10 chuoi email: welcome, promo, affiliate, reactivation"),
    ("agent_benchmark", "Mini guide: viet email ban hang khong can gioi copywriting"),
    ("agent_benchmark", "Swipe structure, khong copy y nguyen PLR"),
    ("agent_benchmark", "Tao AI PLR Rebrand Kit"),
    ("agent_benchmark", "Viet sale page cho AI PLR Rebrand Kit"),
    ("agent_benchmark", "Tao JV Pack cho san pham WarriorPlus"),
    ("agent_benchmark", "Tao funnel FE/Bump/OTO"),
    ("agent_benchmark", "Tao SaaS upgrade plan"),
    ("agent_benchmark", "Export launch pack"),
    ("deep_create_product_assets", "AI Email Campaign Kit for Beginners - create full product assets"),
    ("deep_write_file", "AI Email Campaign Kit for Beginners - deep write file 00_Start_Here.md"),
    ("support", "AI Email Campaign Kit for Beginners - create support FAQ"),
    ("license", "AI Email Campaign Kit for Beginners - create license matrix"),
    ("full_launch_pack", "AI Email Campaign Kit for Beginners - one click full launch pack"),
    ("buyer_test", "AI Email Campaign Kit for Beginners - buyer test"),
    ("jv_test", "AI Email Campaign Kit for Beginners - jv test"),
    ("sales_page_critic", "AI Email Campaign Kit for Beginners - sales page critic"),
    ("apply_feedback", "AI Email Campaign Kit for Beginners - apply feedback: buyer says product is confusing, JV says swipes need more detail"),
    ("buyer_test_zip", "AI Email Campaign Kit for Beginners - buyer test zip"),
    ("jv_test_pack", "AI Email Campaign Kit for Beginners - jv test pack"),
    ("public_launch_audit", "AI Email Campaign Kit for Beginners - public launch audit"),
    ("workflow_30", "Show 30-step completion workflow"),
    ("ai_workflow_20", "Show AI workflow"),
    ("case_study_search", "AI PLR Prompt Template Packs for KDP Printables"),
    ("case_study_patterns", "AI PLR Prompt Template Packs for KDP Printables"),
    ("training_status", "Show training status"),
    ("export_training_report", "AI PLR Prompt Template Packs for KDP Printables"),
]

REQUIRED_KEYWORDS = [
    "VERDICT",
    "SCORECARD",
    "AI Replace Risk",
    "Productized Output",
    "Sales Page Angle",
    "Funnel",
    "JV Manager Pack",
    "SaaS Upgrade",
    "Agent Status",
    "Next Actions",
    "AGENT STATUS",
    "QUALITY GATE",
    "SPECIALIST CHECK",
    "ZIP STATUS",
    "CRITIC AGENT CHECK",
    "QUALITY GATE",
    "Created Files",
    "Export ZIP",
    "Launch Readiness",
    "Product Type Classifier",
    "Prompt-to-Product Transformer",
    "Offer Ladder Engine",
    "Minimum Sellable Product Checklist",
    "JV Appeal Score",
    "License Matrix",
    "Cost & Profit Calculator",
    "Refund Prevention",
    "Versioning",
]

ANTI_GENERIC_KEYWORDS = [
    "Output nay con giong AI thuong",
    "workflow",
    "checklist",
    "planner",
    "launch asset",
]


def _render(module_id: str, prompt: str) -> str:
    action = maybe_run_action(module_id, prompt)
    return _action_response(module_id, action)


def test_agent_depth_contract() -> None:
    failures: list[str] = []
    non_launch_contract_modules = {"workflow_30", "ai_workflow_20", "case_study_search", "case_study_patterns", "training_status", "export_training_report"}
    for module_id, prompt in TEST_CASES:
        output = _render(module_id, prompt)
        for keyword in REQUIRED_KEYWORDS:
            if module_id in non_launch_contract_modules:
                continue
            if module_id != "agent_benchmark" and keyword in {"VERDICT", "Product Type Classifier", "Prompt-to-Product Transformer", "Offer Ladder Engine", "Minimum Sellable Product Checklist", "JV Appeal Score", "License Matrix", "Cost & Profit Calculator", "Refund Prevention", "Versioning"}:
                continue
            if keyword.lower() not in output.lower():
                failures.append(f"{module_id}:{prompt!r} missing {keyword!r}")
        if module_id == "agent_benchmark":
            for keyword in ANTI_GENERIC_KEYWORDS:
                if keyword.lower() not in output.lower():
                    failures.append(f"{prompt!r} missing anti-generic marker {keyword!r}")
        if module_id not in non_launch_contract_modules and "CREATED FILES" not in output:
            failures.append(f"{module_id}:{prompt!r} did not report CREATED FILES")
        if module_id == "full_launch_pack":
            for keyword in ("ZIP PATH", "Email Funnel: DONE", "Support: DONE", "License: DONE", "Created Files: PASS", "Export ZIP: PASS", "Export Proof: PASS", "Placeholder Check:", "Public Launch Gate:"):
                if keyword.lower() not in output.lower():
                    failures.append(f"{module_id}:{prompt!r} missing execution marker {keyword!r}")
        if module_id == "workflow_30" and "30. Update / tạo OTO / bundle".lower() not in output.lower():
            failures.append("workflow_30 missing final workflow step")
        if module_id == "ai_workflow_20" and "20. Ra lệnh cho AI tạo bản V2 sau khi fix".lower() not in output.lower():
            failures.append("ai_workflow_20 missing final AI workflow step")
        if module_id == "case_study_search" and "CASE STUDY BRAIN SEARCH" not in output:
            failures.append("case_study_search missing search header")
        if module_id == "case_study_patterns" and "CASE STUDY PATTERN EXTRACTOR" not in output:
            failures.append("case_study_patterns missing pattern extractor header")
        if module_id == "training_status" and "TRAINING STATUS" not in output:
            failures.append("training_status missing status header")
        if module_id == "export_training_report" and "TRAINING REPORT EXPORTED" not in output:
            failures.append("export_training_report missing report header")

    start_here = ROOT / "outputs" / "AI_Email_Campaign_Kit" / "product_assets" / "00_Start_Here.md"
    campaign_map = ROOT / "outputs" / "AI_Email_Campaign_Kit" / "product_assets" / "01_7_Day_Campaign_Map.md"
    checklist = ROOT / "outputs" / "AI_Email_Campaign_Kit" / "product_assets" / "04_Pre_Send_Checklist.md"
    for path in (start_here, campaign_map, checklist):
        if not path.exists():
            failures.append(f"missing deep file {path}")
            continue
        words = len(path.read_text(encoding="utf-8").split())
        if words < 800:
            failures.append(f"{path.name} too shallow: {words} words")
    required_launch_files = [
        ROOT / "outputs" / "AI_Email_Campaign_Kit" / "product_assets" / "02_30_Short_Email_Templates.md",
        ROOT / "outputs" / "AI_Email_Campaign_Kit" / "product_assets" / "06_Campaign_Planner.csv",
        ROOT / "outputs" / "AI_Email_Campaign_Kit" / "sales_page" / "sales_page.md",
        ROOT / "outputs" / "AI_Email_Campaign_Kit" / "funnel" / "funnel_plan.md",
        ROOT / "outputs" / "AI_Email_Campaign_Kit" / "warriorplus_listing" / "listing.md",
        ROOT / "outputs" / "AI_Email_Campaign_Kit" / "jv_pack" / "affiliate_swipes.md",
        ROOT / "outputs" / "AI_Email_Campaign_Kit" / "delivery_page" / "thank_you_page.md",
        ROOT / "outputs" / "AI_Email_Campaign_Kit" / "email_funnel" / "buyer_onboarding_emails.md",
        ROOT / "outputs" / "AI_Email_Campaign_Kit" / "saas_plan" / "saas_upgrade_plan.md",
        ROOT / "outputs" / "AI_Email_Campaign_Kit" / "support" / "support_faq.md",
        ROOT / "outputs" / "AI_Email_Campaign_Kit" / "license" / "license_matrix.csv",
        ROOT / "outputs" / "AI_Email_Campaign_Kit" / "AGENT_STATUS.md",
        ROOT / "outputs" / "AI_Email_Campaign_Kit" / "QUALITY_GATE.md",
        ROOT / "outputs" / "AI_Email_Campaign_Kit" / "LAUNCH_READINESS.md",
        ROOT / "outputs" / "AI_Email_Campaign_Kit" / "launch" / "REAL_LAUNCH_CHECKLIST.md",
        ROOT / "outputs" / "AI_Email_Campaign_Kit" / "launch" / "PLACEHOLDER_CHECK.md",
        ROOT / "outputs" / "AI_Email_Campaign_Kit" / "launch" / "PUBLIC_LAUNCH_GATE.md",
        ROOT / "outputs" / "AI_Email_Campaign_Kit" / "launch" / "PUBLIC_LAUNCH_AUDIT.md",
        ROOT / "outputs" / "AI_Email_Campaign_Kit" / "export" / "ZIP_PATH.txt",
        ROOT / "outputs" / "AI_Email_Campaign_Kit" / "export" / "EXPORT_LOG.md",
        ROOT / "outputs" / "AI_Email_Campaign_Kit" / "testing" / "buyer_test.md",
        ROOT / "outputs" / "AI_Email_Campaign_Kit" / "testing" / "jv_test.md",
        ROOT / "outputs" / "AI_Email_Campaign_Kit" / "testing" / "buyer_test_zip.md",
        ROOT / "outputs" / "AI_Email_Campaign_Kit" / "testing" / "jv_test_pack.md",
        ROOT / "outputs" / "AI_Email_Campaign_Kit" / "sales_page" / "sales_page_critic.md",
        ROOT / "outputs" / "AI_Email_Campaign_Kit" / "feedback" / "feedback_upgrade_plan.md",
        ROOT / "outputs" / "AI_Email_Campaign_Kit" / "versioning" / "CHANGELOG.md",
        ROOT / "outputs" / "AI_Email_Campaign_Kit" / "mockups" / "mockup_instructions.md",
        ROOT / "outputs" / "AI_Email_Campaign_Kit" / "mockups" / "folder_preview_checklist.md",
        ROOT / "outputs" / "AI_Email_Campaign_Kit" / "mockups" / "canva_mockup_prompt.md",
        ROOT / "outputs" / "AI_Email_Campaign_Kit" / "mockups" / "sales_page_preview_sections.md",
        ROOT / "outputs" / "AI_Email_Campaign_Kit" / "export" / "AI_Email_Campaign_Kit_Launch_Pack.zip",
    ]
    for path in required_launch_files:
        if not path.exists():
            failures.append(f"missing launch file {path}")
    deep_core_min_words = {
        ROOT / "outputs" / "AI_Email_Campaign_Kit" / "product_assets" / "02_30_Short_Email_Templates.md": 1200,
        ROOT / "outputs" / "AI_Email_Campaign_Kit" / "sales_page" / "sales_page.md": 900,
        ROOT / "outputs" / "AI_Email_Campaign_Kit" / "jv_pack" / "affiliate_email_swipes.md": 700,
        ROOT / "outputs" / "AI_Email_Campaign_Kit" / "delivery_page" / "delivery_page.md": 450,
        ROOT / "outputs" / "AI_Email_Campaign_Kit" / "email_funnel" / "buyer_onboarding_emails.md": 650,
    }
    for path, minimum in deep_core_min_words.items():
        if not path.exists():
            failures.append(f"missing deep core file {path}")
            continue
        words = len(path.read_text(encoding="utf-8").split())
        if words < minimum:
            failures.append(f"{path.name} too shallow: {words} words, expected {minimum}+")
    assert not failures, "\n".join(failures)


if __name__ == "__main__":
    test_agent_depth_contract()
    print("Agent depth eval passed")

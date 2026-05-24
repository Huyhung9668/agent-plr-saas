from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from product_pipeline import extract_explicit_step, resolve_skill_route


def test_explicit_steps_1_44_route_to_matching_skill():
    for step in range(1, 45):
        route = resolve_skill_route(f"Product: AI Coloring Page Niche Pack\n\nStep {step} test")
        assert route["selected_skill"].startswith(f"{step:02d}_"), route
        assert route["explicit_step"] == step


def test_key_skill_routes():
    assert resolve_skill_route("Step 1 Product Idea / Niche")["selected_skill"] == "01_product_idea_niche"
    assert resolve_skill_route("Step 12 Product Core Review")["selected_skill"] == "12_product_core_review"
    assert resolve_skill_route("Step 34 Final Folder Packaging")["selected_skill"] == "34_final_folder_packaging"
    assert resolve_skill_route("Step 44 OTO Decision hoặc SP2 Decision")["selected_skill"] == "44_oto_decision_sp2_decision"
    assert resolve_skill_route("buyer test product hiện tại")["selected_skill"] == "17_buyer_simulation_test"
    assert resolve_skill_route("refund risk product hiện tại")["selected_skill"] == "18_refund_auditor_test"
    assert resolve_skill_route("sales page copy")["selected_skill"] == "26_sales_page_copy"
    assert resolve_skill_route("export zip")["selected_skill"] == "36_export_zip_test_delivery_flow"
    assert resolve_skill_route("OTO decision")["selected_skill"] == "44_oto_decision_sp2_decision"


def test_explicit_step_beats_keywords():
    route = resolve_skill_route("Step 44 Final Folder Packaging export zip OTO decision")
    assert route["selected_skill"] == "44_oto_decision_sp2_decision"
    assert route["selected_skill"] != "34_final_folder_packaging"


def test_debug_complaint_stops_normal_route():
    route = resolve_skill_route("Hỏi Step 44 mà trả Step 34 là lỗi gì? Debug route và không trả lời bằng mẫu cũ.")
    assert route["selected_route"] == "ROUTE_DEBUG_OR_CONFLICT"
    assert route["selected_skill"] is None


def test_extract_step_40_and_44():
    assert extract_explicit_step("step 40 post-launch feedback plan") == 40
    assert extract_explicit_step("Bước 44 OTO decision") == 44

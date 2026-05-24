import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from product_pipeline import extract_explicit_step, resolve_product_route


def test_explicit_step_routes():
    assert resolve_product_route("step 12 final audit")["selected_route"] == "STEP_12_PRODUCT_CORE_REVIEW"
    assert resolve_product_route("bước 12 lập fix plan")["selected_route"] == "STEP_12_PRODUCT_CORE_REVIEW"
    assert resolve_product_route("step 7 buyer test")["selected_route"] == "STEP_7_BUYER_RISK_TEST"
    assert resolve_product_route("step 8 export zip")["selected_route"] == "STEP_8_EXPORT_ZIP_MANIFEST"
    assert resolve_product_route("step 4 templates and prompts")["selected_route"] == "STEP_4_TEMPLATES_AND_PROMPTS"
    assert resolve_product_route("step 13 chấm điểm từng file")["selected_route"] == "STEP_13_FILE_QUALITY_SCORE"
    assert resolve_product_route("step 14 ai replace risk audit")["selected_route"] == "STEP_14_AI_REPLACE_RISK_AUDIT"
    assert resolve_product_route("step 15 beginner confusion audit")["selected_route"] == "STEP_15_BEGINNER_CONFUSION_AUDIT"
    assert resolve_product_route("step 16 prompt output test")["selected_route"] == "STEP_16_PROMPT_OUTPUT_TEST"
    assert resolve_product_route("step 17 buyer simulation test")["selected_route"] == "STEP_17_BUYER_SIMULATION_TEST"
    assert resolve_product_route("step 18 refund auditor test")["selected_route"] == "STEP_18_REFUND_AUDITOR_TEST"
    assert resolve_product_route("STEP 19 ONLY — FIX WEAK PARTS")["selected_route"] == "STEP_19_FIX_WEAK_PARTS"
    assert resolve_product_route("STEP 20 ONLY — RE-SCORE PRODUCT")["selected_route"] == "STEP_20_RESCORE_PRODUCT"
    assert resolve_product_route("STEP 21 ONLY — ADD MORE EXAMPLE OUTPUTS")["selected_route"] == "STEP_21_MORE_EXAMPLE_OUTPUTS"
    assert resolve_product_route("STEP 22 ONLY — ADD CHECKLISTS")["selected_route"] == "STEP_22_ADD_CHECKLISTS"
    assert resolve_product_route("STEP 23 ONLY — ADD FIX PROMPTS")["selected_route"] == "STEP_23_ADD_FIX_PROMPTS"
    assert resolve_product_route("STEP 24 ONLY — FINAL COMPLIANCE REVIEW")["selected_route"] == "STEP_24_FINAL_COMPLIANCE_REVIEW"


def test_route_debug_does_not_run_old_step():
    route = resolve_product_route("hỏi step 12 lại trả lời step 5")
    assert route["selected_route"] == "ROUTE_DEBUG_OR_CONFLICT"
    assert route["selected_route"] != "STEP_5_EXAMPLES_QUALITY_COMPLIANCE"


def test_step35_uses_real_ai_export_manifest():
    route = resolve_product_route("Product: AI Coloring Page Niche Pack\n\nstep 35 export zip + manifest test")
    assert route["selected_route"] == "REAL_AI_CHAT_STEP_35_EXPORT_ZIP_MANIFEST_TEST"
    assert route["route_type"] in {"ai_content", "hybrid_action"}
    assert route["api_called"] is True
    assert route["from_cache"] is False
    assert route["prebuilt_answer_used"] is False

def test_generic_future_step_uses_ai_for_content():
    route = resolve_product_route("step 36 unknown plan")
    assert route["selected_route"] == "GENERIC_STEP_AI_HANDLER"
    assert route["route_type"] == "ai_content"
    assert route["api_called"] is True
    assert route["prebuilt_answer_used"] is False

def test_unsupported_tool_still_stops():
    route = resolve_product_route("step 36 upload warriorplus t? ??ng")
    assert route["selected_route"] == "STEP_UNSUPPORTED"
    assert route["route_type"] == "unsupported_tool"
    assert route["no_answer_generated"] is True

def test_phase5_uses_real_ai_chat():
    cases = [
        "Product: AI Coloring Page Niche Pack\n\nPHASE 5 ONLY — SALES PAGE + JV MANAGER + FUNNEL",
        "Product: AI Coloring Page Niche Pack\n\nSTEP 25 Sales Page Strategy",
        "Product: AI Coloring Page Niche Pack\n\nSTEP 33 Bonus / Order Bump / OTO Map",
    ]
    for text in cases:
        route = resolve_product_route(text)
        assert route["selected_route"] == "REAL_AI_CHAT_PHASE_5"
        assert route["api_called"] is True
        assert route["from_cache"] is False
        assert route["prebuilt_answer_used"] is False

def test_step34_uses_real_ai_packaging():
    route = resolve_product_route("Product: AI Coloring Page Niche Pack\n\nSTEP 34 ONLY — FINAL FOLDER PACKAGING")
    assert route["selected_route"] == "REAL_AI_CHAT_STEP_34_PACKAGING"
    assert route["api_called"] is True
    assert route["from_cache"] is False
    assert route["prebuilt_answer_used"] is False


def test_extract_explicit_step_range():
    assert extract_explicit_step("BƯỚC 36 update oto") == 36
    assert extract_explicit_step("step 44 OTO decision") == 44


def run_all():
    tests = [
        test_explicit_step_routes,
        test_route_debug_does_not_run_old_step,
        test_step35_uses_real_ai_export_manifest,
        test_generic_future_step_uses_ai_for_content,
        test_unsupported_tool_still_stops,
        test_phase5_uses_real_ai_chat,
        test_step34_uses_real_ai_packaging,
        test_extract_explicit_step_range,
    ]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")


if __name__ == "__main__":
    run_all()

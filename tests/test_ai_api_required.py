from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from product_pipeline import resolve_skill_route


def test_ai_api_required_by_route_type():
    cases = {
        12: True,
        17: True,
        25: True,
        34: True,
        36: False,
        44: True,
    }
    for step, must_call in cases.items():
        route = resolve_skill_route(f"Step {step} test")
        if route["route_type"] in {"ai_content", "hybrid_action"}:
            assert route["api_called"] is True
            assert route["prebuilt_answer_used"] is False
            assert route["old_answer_reused"] is False
        if route["route_type"] == "tool_action":
            assert route["api_called"] is False

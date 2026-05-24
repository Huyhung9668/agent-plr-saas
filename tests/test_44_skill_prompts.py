from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from product_pipeline import resolve_skill_route


def test_all_44_skill_prompts_have_three_routeable_prompts():
    index = json.loads((ROOT / "skills" / "_index.json").read_text(encoding="utf-8"))
    for skill in index:
        step = skill["step_number"]
        explicit = resolve_skill_route(f"Product: AI Coloring Page Niche Pack\n\nStep {step} {skill['skill_name']} cho product hiện tại")
        assert explicit["selected_skill"] == skill["skill_id"]
        natural = resolve_skill_route(skill["trigger_keywords"][0])
        assert natural["selected_skill"] == skill["skill_id"]
        debug = resolve_skill_route(f"Hỏi Step {step} mà trả step khác là lỗi gì?")
        assert debug["selected_route"] == "ROUTE_DEBUG_OR_CONFLICT"

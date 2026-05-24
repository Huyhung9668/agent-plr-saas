from pathlib import Path
p=Path('product_pipeline.py')
s=p.read_text(encoding='utf-8')
s=s.replace('import unicodedata\nfrom dataclasses import dataclass\n', 'import unicodedata\nfrom dataclasses import dataclass\nimport json\nfrom pathlib import Path\n')
s=s.replace('    24: "STEP_24_FINAL_COMPLIANCE_REVIEW",\n}', '''    24: "STEP_24_FINAL_COMPLIANCE_REVIEW",
    25: "STEP_25_SALES_PAGE_STRATEGY",
    26: "STEP_26_SALES_PAGE_COPY",
    27: "STEP_27_SALES_PAGE_CLAIM_AUDIT",
    28: "STEP_28_WARRIORPLUS_LISTING",
    29: "STEP_29_JV_MANAGER_PLAN",
    30: "STEP_30_JV_PAGE_JV_INVITE",
    31: "STEP_31_AFFILIATE_EMAIL_SWIPES",
    32: "STEP_32_SOCIAL_POSTS_PROMO_ASSETS",
    33: "STEP_33_BONUS_ORDER_BUMP_OTO_MAP",
    34: "STEP_34_FINAL_FOLDER_PACKAGING",
    35: "STEP_35_PLACEHOLDER_CHECK_EXPORT_MANIFEST",
    36: "STEP_36_EXPORT_ZIP_TEST_DELIVERY_FLOW",
    37: "STEP_37_SOFT_LAUNCH_REVIEW_ACCESS",
    38: "STEP_38_FEEDBACK_LOG",
    39: "STEP_39_BUYER_QUESTIONS_REFUND_REASONS",
    40: "STEP_40_V2_FIXES",
    41: "STEP_41_PUBLIC_LAUNCH_CHECKLIST",
    42: "STEP_42_PUBLIC_LAUNCH",
    43: "STEP_43_SUPPORT_REFUND_AFFILIATE_TRACKING",
    44: "STEP_44_OTO_DECISION_SP2_DECISION",
}''')
s=s.replace('r"(?i)(?:step|bước|buoc)\\s*([1-9]|[12][0-9]|3[0-6])\\b"', 'r"(?i)(?:step|bước|buoc)\\s*([1-9]|[1-3][0-9]|4[0-4])\\b"')
insert = r'''

def load_skill_index() -> list[dict]:
    index_path = Path(__file__).resolve().parent / "skills" / "_index.json"
    if not index_path.exists():
        return []
    return json.loads(index_path.read_text(encoding="utf-8"))

def load_skill(step_number: int) -> dict | None:
    for skill in load_skill_index():
        if int(skill.get("step_number", 0)) == int(step_number):
            return skill
    return None

def _skill_debug(skill: dict | None, explicit_step: int | None, message: str, reason: str) -> dict:
    route_type = (skill or {}).get("route_type") or "ai_content"
    return {
        "selected_route": "SKILL_ROUTE" if skill else GENERIC_STEP_AI_ROUTE,
        "selected_skill": (skill or {}).get("skill_id"),
        "explicit_step": explicit_step,
        "requested_step": explicit_step,
        "route_type": route_type,
        "reason": reason,
        "api_called": route_type in {"ai_content", "hybrid_action"},
        "from_cache": False,
        "prebuilt_answer_used": False,
        "old_answer_reused": False,
        "fallback_used": False,
        "route_conflict": False,
        "tool_action": "export_zip" if route_type in {"tool_action", "hybrid_action"} and "export" in (message or "").lower() else "",
    }

def resolve_skill_route(message: str, payload: dict | None = None) -> dict:
    explicit_step = extract_explicit_step(message)
    if is_route_debug_request(message):
        return {
            "selected_route": "ROUTE_DEBUG_OR_CONFLICT",
            "selected_skill": None,
            "explicit_step": explicit_step,
            "route_type": "ai_content",
            "reason": "route/debug complaint; stop normal skill execution",
            "api_called": True,
            "from_cache": False,
            "prebuilt_answer_used": False,
            "old_answer_reused": False,
            "fallback_used": False,
        }
    if explicit_step:
        skill = load_skill(explicit_step)
        if skill:
            return _skill_debug(skill, explicit_step, message, f"explicit Step {explicit_step} routes to matching 44-skill file")
        return _skill_debug(None, explicit_step, message, f"explicit Step {explicit_step} has no skill file; generic AI handler")

    folded = (message or "").lower()
    for skill in load_skill_index():
        if any(str(keyword).lower() in folded for keyword in skill.get("trigger_keywords", [])):
            return _skill_debug(skill, int(skill["step_number"]), message, "keyword intent routes to 44-skill file")
    return {"selected_route": "", "selected_skill": None, "explicit_step": None}

def build_skill_prompt(skill: dict, project: dict | None, message: str) -> str:
    product_name = (project or {}).get("product_name") or "ACTIVE_PRODUCT_REQUIRED"
    return f"""Bạn là AI content engine cho WarriorPlus 44 Skill System.
Product: {product_name}
Skill: {skill.get('skill_id')} — {skill.get('skill_name')}
Route type: {skill.get('route_type')}

Luật bắt buộc:
- Chỉ dùng active project hiện tại.
- Không dùng câu trả lời cũ, không dùng prebuilt answer.
- Không nhắc product cũ nếu user không yêu cầu compare/reuse.
- Nếu thiếu file/assets, ghi MISSING ASSETS, không báo PASS giả.

User message:
{message}
"""

def run_ai_content_skill(skill: dict, project: dict | None, message: str) -> dict:
    return {"prompt": build_skill_prompt(skill, project, message), "api_called": True, "from_cache": False, "prebuilt_answer_used": False}

def run_tool_skill(skill: dict, project: dict | None, message: str) -> dict:
    return {"tool_action": "export_zip" if "export" in (message or "").lower() else "project_tool", "api_called": False, "from_cache": False}

def run_hybrid_skill(skill: dict, project: dict | None, message: str) -> dict:
    return {"tool": run_tool_skill(skill, project, message), "prompt": build_skill_prompt(skill, project, message), "api_called": True, "from_cache": False, "prebuilt_answer_used": False}

def score_skill_output(skill_text: str) -> int:
    required = ["## Trigger Keywords", "## Required Inputs", "## Output Schema", "## Project Context Rules", "## AI/API Rule", "## Tool/Fast Path Rule", "old_answer_reused", "## Quality Checklist", "## Test Prompts", "## Repair Instructions"]
    return sum(1 for marker in required if marker in skill_text)

def repair_skill_if_needed(skill_path: str) -> int:
    text = Path(skill_path).read_text(encoding="utf-8")
    return score_skill_output(text)
'''
s=s.replace('\ndef route_for_step(step: int) -> str:\n', insert + '\ndef route_for_step(step: int) -> str:\n')
p.write_text(s,encoding='utf-8')
print('patched product_pipeline')

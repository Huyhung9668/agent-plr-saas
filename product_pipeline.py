from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
import json
from pathlib import Path

STEP_ROUTE_TABLE: dict[int, str] = {
    1: "STEP_1_MARKET_RESEARCH",
    2: "STEP_2_PRODUCT_BLUEPRINT",
    3: "STEP_3_CORE_PRODUCT_FILES",
    4: "STEP_4_TEMPLATES_AND_PROMPTS",
    5: "STEP_5_EXAMPLES_QUALITY_COMPLIANCE",
    6: "STEP_6_DELIVERY_SUPPORT",
    7: "STEP_7_BUYER_RISK_TEST",
    8: "STEP_8_EXPORT_ZIP_MANIFEST",
    9: "STEP_9_SALES_PAGE",
    10: "STEP_10_WARRIORPLUS_LISTING",
    11: "STEP_11_JV_PACK",
    12: "STEP_12_PRODUCT_CORE_REVIEW",
    13: "STEP_13_FILE_QUALITY_SCORE",
    14: "STEP_14_AI_REPLACE_RISK_AUDIT",
    15: "STEP_15_BEGINNER_CONFUSION_AUDIT",
    16: "STEP_16_PROMPT_OUTPUT_TEST",
    17: "STEP_17_BUYER_SIMULATION_TEST",
    18: "STEP_18_REFUND_AUDITOR_TEST",
    19: "STEP_19_FIX_WEAK_PARTS",
    20: "STEP_20_RESCORE_PRODUCT",
    21: "STEP_21_MORE_EXAMPLE_OUTPUTS",
    22: "STEP_22_ADD_CHECKLISTS",
    23: "STEP_23_ADD_FIX_PROMPTS",
    24: "STEP_24_FINAL_COMPLIANCE_REVIEW",
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
}

REAL_AI_PHASE5_ROUTE = "REAL_AI_CHAT_PHASE_5"
PHASE5_STEP_RANGE = set(range(25, 34))
REAL_AI_STEP34_ROUTE = "REAL_AI_CHAT_STEP_34_PACKAGING"
REAL_AI_STEP35_ROUTE = "REAL_AI_CHAT_STEP_35_EXPORT_ZIP_MANIFEST_TEST"
GENERIC_STEP_AI_ROUTE = "GENERIC_STEP_AI_HANDLER"

IMPLEMENTED_STEP_ROUTES = {
    "STEP_2_PRODUCT_BLUEPRINT",
    "STEP_3_CORE_PRODUCT_FILES",
    "STEP_4_TEMPLATES_AND_PROMPTS",
    "STEP_5_EXAMPLES_QUALITY_COMPLIANCE",
    "STEP_6_DELIVERY_SUPPORT",
    "STEP_7_BUYER_RISK_TEST",
    "STEP_8_EXPORT_ZIP_MANIFEST",
    "STEP_12_PRODUCT_CORE_REVIEW",
    "STEP_13_FILE_QUALITY_SCORE",
    "STEP_14_AI_REPLACE_RISK_AUDIT",
    "STEP_15_BEGINNER_CONFUSION_AUDIT",
    "STEP_16_PROMPT_OUTPUT_TEST",
    "STEP_17_BUYER_SIMULATION_TEST",
    "STEP_18_REFUND_AUDITOR_TEST",
    "STEP_19_FIX_WEAK_PARTS",
    "STEP_20_RESCORE_PRODUCT",
    "STEP_21_MORE_EXAMPLE_OUTPUTS",
    "STEP_22_ADD_CHECKLISTS",
    "STEP_23_ADD_FIX_PROMPTS",
    "STEP_24_FINAL_COMPLIANCE_REVIEW",
}

ROUTE_DEBUG_TERMS = [
    "route sai",
    "route nhầm",
    "trả lời nhầm",
    "tra loi nham",
    "lỗi gì",
    "loi gi",
    "lại trả lời",
    "lai tra loi",
]


def slugify_project_name(name: str) -> str:
    normalized = unicodedata.normalize("NFKD", name or "")
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", ascii_text).strip("_").lower()
    return slug or "untitled_product"


def extract_explicit_step(message: str) -> int | None:
    text = message or ""
    match = re.search(r"(?i)(?:step|bước|buoc)\s*([1-9]|[1-3][0-9]|4[0-4])\b", text)
    if match:
        return int(match.group(1))
    return None



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
    best_match: tuple[int, dict] | None = None
    for skill in load_skill_index():
        for keyword in skill.get("trigger_keywords", []):
            keyword_text = str(keyword).lower()
            if keyword_text and keyword_text in folded:
                match_len = len(keyword_text)
                if best_match is None or match_len > best_match[0]:
                    best_match = (match_len, skill)
    if best_match:
        skill = best_match[1]
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

def route_for_step(step: int) -> str:
    return STEP_ROUTE_TABLE.get(step, "STEP_UNSUPPORTED")


def is_route_implemented(route: str) -> bool:
    return route in IMPLEMENTED_STEP_ROUTES


def is_route_debug_request(message: str) -> bool:
    folded = (message or "").lower()
    return any(term in folded for term in ROUTE_DEBUG_TERMS)


def is_real_ai_phase5_request(message: str) -> bool:
    folded = (message or "").lower()
    explicit_step = extract_explicit_step(message)
    if explicit_step in PHASE5_STEP_RANGE:
        return True
    phase5_terms = [
        "phase 5 only",
        "phase 5",
        "sales page + jv manager + funnel",
        "sales page strategy",
        "jv manager",
        "affiliate email swipes",
        "bonus / order bump / oto",
    ]
    return any(term in folded for term in phase5_terms)


def is_real_ai_step34_packaging_request(message: str) -> bool:
    folded = (message or "").lower()
    explicit_step = extract_explicit_step(message)
    if explicit_step == 34:
        return True
    packaging_terms = [
        "final folder packaging",
        "folder packaging",
        "final folder",
        "đóng gói folder",
        "dong goi folder",
        "đóng gói thư mục",
        "dong goi thu muc",
    ]
    return any(term in folded for term in packaging_terms)


def is_real_ai_step35_export_manifest_request(message: str) -> bool:
    folded = (message or "").lower()
    explicit_step = extract_explicit_step(message)
    if explicit_step == 35:
        return True
    export_terms = [
        "export zip + manifest",
        "export zip manifest",
        "manifest test",
        "final zip",
        "test zip",
        "ki?m tra zip",
        "kiem tra zip",
    ]
    return any(term in folded for term in export_terms)

def _base_real_ai_route(route: str, explicit_step: int | None, reason: str, route_type: str = "ai_content") -> dict:
    return {
        "selected_route": route,
        "explicit_step": explicit_step,
        "requested_step": explicit_step,
        "reason": reason,
        "route_type": route_type,
        "fallback_used": False,
        "route_conflict": False,
        "api_called": True,
        "from_cache": False,
        "prebuilt_answer_used": False,
        "old_answer_reused": False,
    }

def _is_hybrid_export_report_request(message: str) -> bool:
    folded = (message or "").lower()
    has_export = any(term in folded for term in ["export zip", "final zip", "manifest", "placeholder scan"])
    has_report = any(term in folded for term in ["vi?t report", "viet report", "public launch report", "audit report", "launch report", "b?o c?o", "bao cao"])
    return has_export and has_report

def _is_tool_only_export_request(message: str) -> bool:
    folded = (message or "").lower()
    has_export = any(term in folded for term in ["export zip", "final export", "placeholder scan", "manifest"])
    return has_export and not _is_hybrid_export_report_request(message)

def _is_unsupported_tool_request(message: str) -> bool:
    folded = (message or "").lower()
    unsupported_terms = [
        "upload warriorplus t? ??ng",
        "upload warriorplus tu dong",
        "payment test th?t",
        "payment test that",
        "export video",
        "auto publish",
    ]
    return any(term in folded for term in unsupported_terms)

def resolve_product_route(message: str) -> dict:
    explicit_step = extract_explicit_step(message)
    if is_real_ai_phase5_request(message):
        return _base_real_ai_route(
            REAL_AI_PHASE5_ROUTE,
            explicit_step,
            "Phase 5 / Step 25-33 must use real AI chat, not deterministic builders",
        )
    if is_real_ai_step34_packaging_request(message):
        return _base_real_ai_route(
            REAL_AI_STEP34_ROUTE,
            explicit_step or 34,
            "Step 34 Final Folder Packaging must use real AI chat, not deterministic builders",
        )
    if is_real_ai_step35_export_manifest_request(message):
        route_type = "hybrid_action" if _is_hybrid_export_report_request(message) else "ai_content"
        return _base_real_ai_route(
            REAL_AI_STEP35_ROUTE,
            explicit_step or 35,
            "Step 35 Export ZIP + Manifest Test must use hybrid/real AI route, not unsupported",
            route_type=route_type,
        )
    if is_route_debug_request(message):
        return {
            "selected_route": "ROUTE_DEBUG_OR_CONFLICT",
            "explicit_step": explicit_step,
            "reason": "route/debug complaint; no product builder should run",
            "fallback_used": False,
            "route_conflict": False,
        }
    if explicit_step:
        route = route_for_step(explicit_step)
        if _is_unsupported_tool_request(message):
            return {
                "selected_route": "STEP_UNSUPPORTED",
                "requested_route": route,
                "explicit_step": explicit_step,
                "requested_step": explicit_step,
                "reason": f"explicit Step {explicit_step} requests an unsupported tool",
                "route_type": "unsupported_tool",
                "fallback_used": False,
                "route_conflict": False,
                "no_answer_generated": True,
            }
        if route == "STEP_UNSUPPORTED" or not is_route_implemented(route):
            return _base_real_ai_route(
                GENERIC_STEP_AI_ROUTE,
                explicit_step,
                f"explicit Step {explicit_step} has no deterministic builder; use generic AI step handler",
            )
        if route in {
            "STEP_7_BUYER_RISK_TEST",
            "STEP_12_PRODUCT_CORE_REVIEW",
            "STEP_13_FILE_QUALITY_SCORE",
            "STEP_14_AI_REPLACE_RISK_AUDIT",
            "STEP_15_BEGINNER_CONFUSION_AUDIT",
            "STEP_16_PROMPT_OUTPUT_TEST",
            "STEP_17_BUYER_SIMULATION_TEST",
            "STEP_18_REFUND_AUDITOR_TEST",
            "STEP_19_FIX_WEAK_PARTS",
            "STEP_20_RESCORE_PRODUCT",
            "STEP_21_MORE_EXAMPLE_OUTPUTS",
            "STEP_22_ADD_CHECKLISTS",
            "STEP_23_ADD_FIX_PROMPTS",
            "STEP_24_FINAL_COMPLIANCE_REVIEW",
        }:
            return _base_real_ai_route(
                route,
                explicit_step,
                f"explicit Step {explicit_step} is a content/audit step; use AI API",
            )
        if route == "STEP_8_EXPORT_ZIP_MANIFEST":
            route_type = "hybrid_action" if _is_hybrid_export_report_request(message) else "tool_action"
        else:
            route_type = "tool_action" if _is_tool_only_export_request(message) else "hybrid_action"
        return {
            "selected_route": route,
            "explicit_step": explicit_step,
            "requested_step": explicit_step,
            "reason": f"explicit Step {explicit_step} has priority over keywords",
            "route_type": route_type,
            "fallback_used": False,
            "route_conflict": False,
            "api_called": route_type == "hybrid_action",
            "from_cache": False,
            "prebuilt_answer_used": False,
            "old_answer_reused": False,
        }
    folded = (message or "").lower()
    if any(term in folded for term in ["buyer test", "risk test", "refund risk", "ai replace risk"]):
        return _base_real_ai_route("STEP_7_BUYER_RISK_TEST", 7, "intent: buyer/risk test", route_type="ai_content")
    if any(term in folded for term in ["public launch audit", "launch audit", "export zip", "final export"]):
        return {"selected_route": "STEP_8_EXPORT_ZIP_MANIFEST", "explicit_step": 8, "requested_step": 8, "reason": "intent: export/audit", "route_type": "hybrid_action" if _is_hybrid_export_report_request(message) else "tool_action", "fallback_used": True, "route_conflict": False, "api_called": _is_hybrid_export_report_request(message), "from_cache": False, "prebuilt_answer_used": False, "old_answer_reused": False}
    return {"selected_route": ""}


def step_unsupported_response(route: dict, product_name: str, active_project_path: str) -> tuple[str, dict]:
    step = route.get("explicit_step") or route.get("requested_step") or ""
    requested_route = route.get("requested_route") or (route_for_step(int(step)) if str(step).isdigit() else "STEP_UNSUPPORTED")
    action = {
        "ok": True,
        "type": "step_unsupported",
        "product": product_name,
        "no_answer_generated": True,
        "route_debug": {
            "explicit_step": step,
            "selected_route": "STEP_UNSUPPORTED",
            "requested_route": requested_route,
            "active_project_path": active_project_path,
            "fallback_used": False,
            "route_conflict": False,
            "from_cache": False,
            "stale_context_detected": False,
        },
    }
    answer = f"""# STEP UNSUPPORTED

User requested Step {step}.

This step is explicit but not implemented yet.

- selected_route: STEP_UNSUPPORTED
- requested_route: {requested_route}
- no_answer_generated: true
- model_fallback_used: false
- old_answer_reused: false

# REQUEST DEBUG
- explicit_step: {step}
- selected_route: STEP_UNSUPPORTED
- active_project_path: {active_project_path}
- fallback_used: false
- route_conflict: false
- from_cache: false
- stale_context_detected: false
"""
    return answer, action

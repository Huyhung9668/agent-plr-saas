from __future__ import annotations

import unicodedata
import re
from dataclasses import dataclass
from pathlib import Path

from agent_profiles import AgentProfile, get_agent_profiles
from brain import brain_summary, search_brain
from case_study_brain import format_case_study_context
from llm_client import chat_with_llm, has_api_key, stream_chat_with_llm

MAX_EXCERPT_CHARS = 1400
ROOT_DIR = Path(__file__).resolve().parent
PLAYBOOK_DIR = ROOT_DIR / "playbooks"

ASSET_QUALITY_GATE = """
Asset quality gate:
- Audience is specific, not generic.
- Promise is concrete and realistic, with no income guarantee.
- Offer contains clear deliverables, not vague benefits only.
- Copy includes problem, agitate, solution, mechanism, bullets, objections, FAQ, compliance, and CTA when relevant.
- WarriorPlus assets include FE, OTO/bump when requested, affiliate angle, refund language, and delivery clarity.
- PLR/license claims are cautious: never assume rights if license is unclear.
- Final output must be usable immediately with minimal editing.
"""

PRODUCT_CREATION_OS = """
Universal Product Creation OS:
- Mandatory internal modules: Offer Evaluator, AI Content To Product Kit Builder, Workflow Builder, Quality Control Checker, Product Packaging Generator, Sales Page Builder, Funnel/OTO Planner, and PLR Rebrand Mode.
- Treat every product idea as a sellable product pack, not a loose list of content.
- Always clarify: target buyer, painful problem, safe promise, product mechanism, deliverables, bonuses, usage rights, and delivery format.
- Every product pack should normally include: Start Here, core training/template asset, implementation checklist, prompt pack or worksheet, examples/swipes, bonus asset, license/compliance note, and README.
- For WarriorPlus/Gumroad/Payhip products, map FE, order bump, OTO1, OTO2/agency license, price range, affiliate angle, and delivery ZIP structure.
- For PLR/SaaS/AI products, add license/risk checks and avoid assuming resale/private-label rights unless license is explicit.
- Upgrade thin products by adding systems: worksheets, calculators, campaign flows, done-for-you examples, checklists, prompt packs, and productized file structure.
- Prefer tables with clear borders for comparisons, package structures, pricing, asset lists, and build checklists.
- Never sell raw AI content as the main value. Reposition it as a curated implementation system with workflow, examples, checks, and deployment assets.
- For any template/prompt/swipe product, include use-case variants, sequence/order of use, customization prompts, pre-use checklist, compliance note, and a planner sheet.
- For email products specifically, include use cases such as welcome, nurture, promo, affiliate, deadline/urgency, re-engagement, plus subject lines, CTA bank, spam/hype checks, and campaign map.
- For any niche/topic, add proof substitutes: sample filled example, before/after transformation, worksheet screenshot idea, demo campaign, or walkthrough.
- If the user asks whether a product is "ok" or asks to upgrade it, start with a direct verdict, then show exactly how to make it harder for a normal AI answer to replace.
- Offer Evaluator scoring must include: Buyer Pain, AI Replace Risk, Workflow Value, Implementation Value, WarriorPlus Fit, Asset Completeness, Compliance Risk, and Final Recommendation.
- Product Kit Builder must convert raw content into: campaign map/workflow, templates, customization prompts, checklist, planner/sheet, examples, compliance note, README, sales angle, and funnel plan.
- Quality Control must check: overhyped income/conversion claims, fake scarcity, unclear CTA, missing placeholders, duplicate sections, missing usage guide, missing examples, missing compliance note, and weak differentiation from ordinary AI output.
- Product Packaging Generator must always show a clean folder/ZIP structure with numbered files and bonus folder when relevant.
- Sales Page Builder must include the objection block: "Can I just ask AI to make this?" and answer it honestly.
- Funnel Planner must explain what FE sells, what bump/OTO sells, and why the upsell is speed/depth/license rather than more raw AI text.
- Market Research / Competitor Spy must identify competitor patterns, common headlines, common bonuses, pricing patterns, saturation risk, and exploitable gaps.
- Buyer Avatar Builder must define buyer stage, platform, current assets, pain, desired result, objections, buying trigger, and messaging angle.
- Objection Handler must create FAQ/sales blocks for AI can do it, I already have PLR, no list yet, no guaranteed results, niche transferability, and license concerns.
- Proof Substitute Generator must suggest ethical proof substitutes: previews, screenshots, before/after examples, walkthrough videos, sample outputs, demo workflows, and checklist previews.
- License & Risk Checker must inspect/ask for license terms and classify risk. If unclear, recommend using source material only for research/outline and creating fresh assets.
- Product Depth Checker must score depth from 0-10 and warn when the product is too thin to sell as a standalone offer.
- Asset Generator must output concrete file names and contents, not only general advice.
- WarriorPlus Listing Builder must produce product title, short description, long description, category, tags, price, commission, refund policy, vendor note, affiliate approval note, and delivery page text.
- Affiliate/JV Material Builder must produce JV invite, affiliate swipes, social posts, review access message, follow-up message, launch calendar, commission explanation, and bonus ideas.
- Traffic Content Generator must create value-first free traffic content and avoid spammy group/comment behavior.
- Email List Builder must produce lead magnet, opt-in copy, thank-you copy, welcome sequence, buyer onboarding, post-purchase, and backend promotion emails.
- SaaS Upgrade Planner must map a digital product into MVP features, pricing, recurring potential, agency/whitelabel angle, and export workflow.
- Final Decision Score must end major product evaluations with: NEN LAM / CHUA NEN LAM / BO QUA plus score table and condition for doing it.
- Operate as "AI PLR WarriorPlus Launch Command Center" with five work areas:
  1. Build Product: analyze PLR, score ideas, check depth, upgrade raw content, create assets, QC, export ZIP.
  2. Sale Page / Funnel: offer angle, sales page, objection handler, funnel plan, WarriorPlus listing, proof substitutes.
  3. JV Manager: JV page, affiliate swipes, prospect tracker, outreach, affiliate tiers, review access.
  4. SaaS Upgrade / Membership: SaaS potential, MVP planner, membership planner, whitelabel/license planner.
  5. PLR Library / Market Research: scan PLR library, market gap finder, competitor pattern analyzer.
- When a module name appears in the user request, answer in that module's operating format, not as a generic chat answer.
- Default project output structure:
  /outputs/[Product_Name]/product_assets/
  /outputs/[Product_Name]/sales_page/
  /outputs/[Product_Name]/jv_pack/
  /outputs/[Product_Name]/saas_plan/
  /outputs/[Product_Name]/export/product_zip_ready/
- For export/asset requests, list exact file names, purpose, required contents, and quality checks for each file.
- Database-backed thinking should organize work around products, plr_files, market_research, buyer_avatars, sales_pages, funnels, jv_prospects, affiliate_swipes, saas_plans, and exports.
"""

BRAIN_DIFFERENTIATION_ENGINE = """
Brain-backed Differentiation Engine:
- Always use the local brains to create a difference a normal AI answer usually misses: product packaging, launch fit, buyer psychology, compliance, and implementation workflow.
- For any product, explicitly answer: "Why would someone pay instead of asking AI?"
- Create three differentiation layers:
  1. Strategy layer: buyer, pain, market gap, final decision score, what to build/skip.
  2. Implementation layer: workflow, planner, checklist, examples, templates, prompts, quality control.
  3. Launch layer: sales page angle, objection handling, proof substitutes, WarriorPlus listing, JV/affiliate assets, traffic and follow-up.
- If the output looks like raw prompts/templates/headlines/emails, mark it as weak and upgrade it into a kit/system.
- Prefer concrete files, tables, and filled examples over broad advice.
- Every product strategy answer should include at least one "AI-tho vs Product-system" comparison table when relevant.
"""

MASTER_AGENT_OUTPUT_DISCIPLINE = """
Master Agent output discipline:
- You are not a normal AI generator. You are a PLR + SaaS + WarriorPlus Launch Operating System.
- Do not answer as a long essay unless the user explicitly asks for teaching/theory.
- Convert input into decision, score, package, assets, launch steps, and next action.
- When a module is requested, obey that module contract exactly. Do not drift into unrelated modules.
- Always prefer concrete files, exact sections, sample assets, checklists, scorecards, and next actions over broad advice.
- Before sending the final answer, internally check:
  [ ] Decision exists when evaluating or upgrading a product.
  [ ] Scorecard exists for analysis/depth/offer requests.
  [ ] The answer explains why free AI output is not enough when relevant.
  [ ] The answer includes specific workflow/checklist/planner/example assets when relevant.
  [ ] The answer avoids income guarantees, fake scarcity, and unsafe PLR/license assumptions.
  [ ] The next action is operational, not a vague invitation.
- Use Project Memory from recent conversation when present. If the user asks "write sale page", "build JV pack", "export ZIP", etc. without a product name, continue from the active project.
- Treat Product Memory task state as project-management truth: say what is done, what is missing, and what next module/action should run.
- If the output is mostly prompts/templates/content text, apply the Anti-AI-Tho Filter: flag AI Replace Risk and add workflow, planner, checklist, examples, use cases, and implementation guide.
- In Fast/No-Fluff mode, keep product strategy answers tight: Decision, Score, Missing Files, Next Action. Use deeper explanation only in Balanced/Deep or when creating full assets.
- Add "HUMAN REVIEW REQUIRED" for unclear license, income claims, health/finance/legal niches, or resale/client-use rights.
- When useful, include a compact "Knowledge used" section with internal lesson/source titles from retrieved brain context, not long citations.
"""

DEFAULT_LAUNCH_OS_CONTRACT = """
Default Launch OS Output Contract for product/PLR/WarriorPlus requests:
1. DECISION: NEN LAM / CHUA NEN LAM / BO QUA.
2. SCORECARD: Demand, Buyer Pain, WarriorPlus Fit, AI Replace Risk, Workflow Value, Product Depth, Backend Potential, SaaS Potential, Risk, Final Score.
3. DIAGNOSIS: why the current idea is strong/weak and where "AI can do this" applies.
4. UPGRADE PLAN: workflow, checklist, planner, examples, prompts, compliance/risk notes.
5. PRODUCT PACKAGE: exact folder/file tree.
6. SALES PAGE ANGLE: headline, mechanism, objection block, what you get, CTA.
7. FUNNEL: FE, order bump, OTO1, OTO2, recurring if useful.
8. JV MANAGER PACK: JV angle, commission, affiliate targets, outreach/swipe ideas.
9. SAAS UPGRADE: possible tool, MVP features, pricing/user flow.
10. NEXT ACTIONS: exactly 3 operational next actions.
Keep each section compact unless the user asks for full assets.
"""

SHORT_EMAIL_KIT_CONTRACT = """
Short Email Kit Output Contract:
Use this when the user asks to create short email templates for an email kit.
Do not write a long strategy essay. Output:
1. VERDICT: 2-3 lines on why raw email templates are weak and how this becomes a kit.
2. PRODUCT ANGLE: buyer, promise, safe positioning.
3. CAMPAIGN LOGIC: map the 30 emails into welcome, nurture, promo, affiliate, deadline, re-engagement.
4. 30 SHORT EMAIL ASSETS: create the actual emails, grouped by use case. Keep each email short and editable with placeholders.
5. WHY BUY IF AI CAN DO THIS: one buyer-facing objection block.
6. PACKAGING: exact files to include.
7. COMPLIANCE CHECK: no income guarantees, no fake scarcity, clear placeholders, CTA/link check.
Do not expand into full sales page, JV pack, or SaaS plan unless the user asks for those modules.
"""

MODULE_OUTPUT_CONTRACTS = {
    "analyze_plr": """
Module Contract: Analyze PLR File / Folder.
Output only:
# PLR ANALYSIS
## Summary
## Niche / Buyer
## License And Risk
Risk Level: Low / Medium / High / Unknown
## What To Use
## What To Remove
## Rebrand Recommendation
## Missing Assets To Add
## Decision
USE / USE ONLY AS RESEARCH / SKIP
Do not create a full product unless the user asks for Product Assets or Upgrade Kit.
""",
    "idea_score": """
Module Contract: Product Idea Scoring.
Output only:
# OFFER ANALYSIS
## Decision
NEN LAM / CHUA NEN LAM / BO QUA
## Scorecard
Use a Markdown table with Demand, Buyer Pain, WarriorPlus Fit, AI Replace Risk, Workflow Value, Product Depth, Backend Potential, SaaS Potential, Risk, Final Score.
## Main Weakness
## Required Upgrade
## Best Positioning
## Next Best Action
Do not write templates or a sales page in this mode.
""",
    "depth_check": """
Module Contract: Product Depth Checker.
Output only:
# PRODUCT DEPTH CHECK
## Decision
## Depth Score
Current depth /10 and upgraded depth /10.
## Why It Is Thin Or Strong
## Missing Implementation Assets
## Product Kit Upgrade
## Required File Tree
## Next Best Module
Do not create the full asset content yet. Tell the user which module to run next.
""",
    "upgrade_kit": """
Module Contract: Upgrade Raw Content Into Product Kit.
Output only:
# PRODUCT KIT UPGRADE
## Original Weak Product
## Upgraded Product Name
## Buyer
## Promise
## Why Buyers Pay Instead Of Asking AI
## Product Folder Tree
## File-by-file Content Plan
## Quality Gate
## Next Best Action
""",
    "product_assets": """
Module Contract: Create Product Assets.
Create real file contents, not just ideas.
Output:
# CREATED PRODUCT ASSETS
## Target Folder
## Created Files
For each file: filename, purpose, complete starter content or CSV rows.
## Build Checklist
## Export Notes
Do not spend most of the answer diagnosing. Produce assets.
""",
    "qc_checklist": """
Module Contract: Quality Control Checklist.
Output a practical audit:
# QUALITY CONTROL AUDIT
## Pass / Fix / Risk Table
## Hype And Compliance Issues
## AI-Replacement Weaknesses
## Missing Assets
## Fix List In Priority Order
## Final Sell-Readiness Score
""",
    "export_zip": """
Module Contract: Export Product ZIP Plan.
Output:
# EXPORT ZIP PLAN
## Final Folder Tree
## Files To Convert To PDF/DOCX/CSV
## README
## License / Compliance Note
## Delivery Page Text
## Pre-export Checklist
""",
    "offer_angle": """
Module Contract: Build Offer Angle.
Output:
# OFFER ANGLE
## Buyer
## Pain
## Safe Promise
## Mechanism
## Unique Angle
## Deliverables
## Proof Substitutes
## Why AI Alone Is Not Enough
## One-Sentence Positioning
""",
    "sales_page": """
Module Contract: Write Sales Page.
Output a complete sales page only:
# SALES PAGE
Headline, subheadline, problem, why raw AI/PLR is not enough, solution, what you get, how it works, bonuses, who it is for, who it is not for, price framing, FAQ, compliance-safe risk reversal, CTA.
Must include FAQ: "Can't I just ask AI to do this?"
Do not include JV pack or SaaS roadmap unless asked.
""",
    "objections": """
Module Contract: Objection Handler.
Output FAQ/sales blocks for:
AI can do it, I already have PLR, I have no list, no guaranteed results, no tech skills, niche transferability, license/client use.
Keep answers sales-page ready and compliance-safe.
""",
    "funnel_plan": """
Module Contract: Create Funnel Plan.
Output:
# FUNNEL PLAN
## FE
## Order Bump
## OTO1
## OTO2
## Downsell
## Recurring / Backend
## Commission Plan
## Launch Checklist
Explain what each step sells and why.
""",
    "warriorplus_listing": """
Module Contract: Build WarriorPlus Listing.
Output fields only:
Product Title, Short Description, Long Description, Category, Tags, Price, Commission, Refund Policy, Vendor Note, Affiliate Approval Note, Delivery Page Text, Vendor Support Note.
""",
    "proof": """
Module Contract: Proof Substitute Generator.
Do not invent income proof. Output ethical proof assets: preview, workflow screenshot idea, before/after example, sample checklist, sample swipe, sales-page block preview, demo video outline, preview copy.
""",
    "jv_page": """
Module Contract: Build JV Page.
Output JV page copy only: product name, launch date placeholder, niche, buyer avatar, why promote, FE/OTO prices, commission, funnel map, review access, affiliate link placeholder, promo assets, rules, contact.
""",
    "swipe_pack": """
Module Contract: Create Affiliate Swipe Pack.
Output actual affiliate assets: 3 email swipes, 3 short promo emails, 5 Facebook posts, 5 X posts, 3 subject-line sets, launch announcement, last-chance email, 10 bonus ideas.
""",
    "prospects": """
Module Contract: Create JV Prospect Tracker.
Output CSV-ready columns and rows/examples plus prospect source ideas. Focus on JV discovery and tracking, not sales page copy.
""",
    "outreach": """
Module Contract: Generate Outreach Messages.
Output 3-message JV outreach sequence: first contact, follow-up, final soft close. Include review access angle, commission note, audience fit, no hype.
""",
    "tiers": """
Module Contract: Affiliate Tier Manager.
Output affiliate tiers, FE/OTO commissions, approval rules, backend protection, fraud/risk warnings, and when not to offer high commission.
""",
    "review_access": """
Module Contract: Review Access Manager.
Output review access message, approval checklist, follow-up checklist, and tracking fields.
""",
    "saas_potential": """
Module Contract: SaaS Potential Analyzer.
Output score, tool name, MVP features, input/output flow, export workflow, recurring potential, pricing, agency/whitelabel angle, and risks.
""",
    "mvp_plan": """
Module Contract: SaaS MVP Planner.
Output phased roadmap: internal tool, user-facing MVP, paid SaaS, agency/whitelabel. Include features, data tables, export flow, pricing, and priority.
""",
    "membership": """
Module Contract: Membership Planner.
Output monthly deliverables, tiers, price points, retention angle, launch offer, content calendar, compliance-safe positioning.
""",
    "whitelabel": """
Module Contract: Whitelabel License Planner.
Output license options: Personal, Commercial, Agency, Whitelabel, Developer; rights, restrictions, risk warnings, and when not to sell license because PLR rights are unclear.
""",
    "scan_library": """
Module Contract: Scan PLR Library.
Output scan plan and report format: category groups, license/risk fields, rebrand score, WarriorPlus fit, SaaS potential, next products to build.
""",
    "case_study_search": """
Module Contract: Case Study Brain Search.
Use old-file brain as searchable case-study memory, not model fine-tuning.
Output:
# CASE STUDY BRAIN
## Search Intent
## Relevant Patterns Found
## Product / Sales / Funnel Lessons
## What To Reuse As Pattern
## What Not To Copy
## Next Build Action
""",
    "train_case_study_brain": """
Module Contract: Train Case Study Brain.
Explain that training here means indexing old files into searchable memory/RAG.
Output source folder, category map, status, and next search/build actions.
""",
    "case_study_patterns": """
Module Contract: Case Study Pattern Extractor.
Extract reusable patterns from old-file brain:
# CASE STUDY PATTERN EXTRACTOR
## Query
## Top Product Patterns
## Sales Page / Funnel / JV Lessons
## What To Reuse
## What Not To Copy
## Build Recommendation
""",
    "training_status": """
Module Contract: Training Status.
Report Case Study Brain documents, chunks, category coverage, readiness score, and next indexing action.
""",
    "export_training_report": """
Module Contract: Export Training Report.
Create a training report and pattern library from Case Study Brain, then show paths and readiness.
""",
    "market_gap": """
Module Contract: Market Gap Finder.
Output competitor patterns, missing implementation assets, buyer gaps, unique angle, saturation risk, stronger kit structure.
""",
    "competitor": """
Module Contract: Competitor Pattern Analyzer.
Output patterns only: product names/angles to research, headline styles, bonuses, FE prices, OTOs, commissions, proof style, saturation risk, gaps to exploit without copying.
""",
    "asset_completeness": """
Module Contract: Asset Completeness Checker.
Use Active Project Memory. Output:
# ASSET COMPLETENESS CHECK
## Launch Decision
LAUNCH / SOFT LAUNCH ONLY / DO NOT LAUNCH YET
## Required Asset Checklist
Start Here, Workflow/Campaign Map, Templates/Core Asset, Customization Prompts, Checklist, Planner Sheet, Example/Case Study, License/Compliance Note, Sales Page, Funnel Plan, WarriorPlus Listing, JV Page/Swipes, Delivery Page, Onboarding Emails, ZIP Export.
## Missing Assets
## Fix Priority
## Next 3 Actions
""",
    "buyer_journey": """
Module Contract: Buyer Journey Builder.
Output buyer journey from before buying to post-purchase and backend. Include sales-page expectations, first-use path, day-3 check-in, day-7 backend offer, and refund-reduction touchpoints.
""",
    "use_cases": """
Module Contract: Use Case Generator.
Output 6-10 concrete use cases for the product, each with buyer situation, file used, workflow steps, and expected non-guaranteed outcome.
""",
    "before_after": """
Module Contract: Before/After Reframe.
Output a before/after table that turns raw AI/PLR content into a premium kit/system. Include new product name, mechanism, files added, and stronger positioning.
""",
    "offer_gap": """
Module Contract: Offer Gap Detector.
Output missing buyer, promise, workflow, proof substitute, reason-why-now, backend, JV angle, compliance gaps, then rewrite the offer.
""",
    "pricing_commission": """
Module Contract: Pricing & Commission Calculator.
Output price, suggested public/JV commissions, approximate fee/risk notes, vendor margin warning, backend protection, and recommended commission tiers. Do not claim exact platform fees unless the user provides them.
""",
    "launch_readiness": """
Module Contract: Launch Readiness Score.
Use Active Project Memory. Score Product Depth, Sales Page, JV Material, Delivery, Funnel, Traffic Plan, Risk/Compliance. Output final score and LAUNCH / SOFT LAUNCH / WAIT decision.
""",
    "soft_launch": """
Module Contract: Soft Launch Planner.
Output a 7-day low-risk test plan: profile post, group posts, feedback asks, small affiliate outreach, sales-page fixes, bonus improvement, public launch decision.
""",
    "refund_risk": """
Module Contract: Refund Risk Checker.
Output refund risk level, risk reasons, claim fixes, delivery fixes, Start Here/support note needs, expectation-setting FAQ, and final risk after fixes.
""",
    "delivery_page": """
Module Contract: Delivery Page Builder.
Output thank-you page copy, download instructions, Start Here steps, support email placeholder, refund/support note, next step, and gentle backend/upsell bridge.
""",
    "onboarding": """
Module Contract: Customer Onboarding Emails.
Output 5 post-purchase emails: download, start file first, common mistake, customize faster, advanced/backend offer. Keep helpful and compliance-safe.
""",
    "backend_recommendation": """
Module Contract: Backend Recommendation Engine.
Output OTO/backend/membership/SaaS recommendations based on the FE. Explain what each backend sells: speed, depth, license, recurring support, or automation.
""",
    "jv_fit": """
Module Contract: JV Fit Score.
Score Audience Match, Traffic Quality, Platform Fit, Past Promotion Fit, Risk, Final JV Fit. Assign Tier 1/2/3 and commission recommendation.
""",
    "product_line": """
Module Contract: Product Line Planner.
Output a 3-6 month product roadmap with FE, backend, membership, SaaS/tool beta, and bundle/license plan.
""",
    "translate_english": """
Module Contract: Vietnamese-to-English Product Mode.
Do not only translate. Localize for WarriorPlus/Gumroad English market: product name, positioning, promise, bullets, CTA, FAQ, compliance note.
""",
    "platform_fit": """
Module Contract: Platform Fit Selector.
Compare WarriorPlus, Gumroad, Payhip, Etsy, JVZoo for this product. Output best platform, backup platforms, why, price fit, and marketplace risk.
""",
    "launch_pack": """
Module Contract: One-Click Launch Pack.
Use Active Project Memory. If core assets are missing, list missing assets first. Otherwise output full launch pack structure: product_assets, sales_page, warriorplus_listing, jv_pack, email_funnel, traffic_content, delivery_page, saas_upgrade_plan, export ZIP name.
""",
    "evidence_mode": """
Module Contract: RAG Citation / Evidence Mode.
Output the practical answer plus a compact Knowledge Used section listing the most relevant internal brain titles/source names. Do not dump long excerpts.
""",
}

MODE_SETTINGS = {
    "quick": {
        "name": "Nhanh gon",
        "reasoning": "off",
        "excerpt_chars": 0,
        "max_output_tokens": 260,
        "contract": (
            "Mode: QUICK ANSWER. The user asked a short question. Answer directly in Vietnamese. "
            "Target 60-140 words. Use bullets only if useful. Do not include long plans, long context, "
            "or source discussion."
        ),
    },
    "fast": {
        "name": "Nhanh",
        "reasoning": "off",
        "excerpt_chars": 260,
        "max_output_tokens": 700,
        "contract": (
            "Mode: FAST PREMIUM. Answer quickly, skip long setup, but keep the answer useful: "
            "direct diagnosis, 3-5 numbered steps, one compact checklist/template, and today's task. "
            "Target 250-450 Vietnamese words. Do not expand into a long report."
        ),
    },
    "balanced": {
        "name": "Can bang",
        "reasoning": "low",
        "excerpt_chars": 1000,
        "max_output_tokens": 3800,
        "contract": (
            "Mode: BALANCED PREMIUM. Give a deeper answer with enough reasoning, examples, "
            "checklists, and operational detail, while avoiding unnecessary theory."
        ),
    },
    "asset": {
        "name": "Asset",
        "reasoning": "off",
        "excerpt_chars": 700,
        "max_output_tokens": 3200,
        "contract": (
            "Mode: ASSET BUILDER. Create a complete usable marketing asset in Vietnamese, "
            "but keep it production-ready and specific. Target 1000-1800 Vietnamese words when the user asks to create or upgrade a product. "
            "Before writing the final answer, internally review it against the asset quality gate, "
            "then output only the improved final asset plus a short 'Tự kiểm chất lượng' checklist at the end."
        ),
    },
    "deep": {
        "name": "Sau",
        "reasoning": "high",
        "excerpt_chars": MAX_EXCERPT_CHARS,
        "max_output_tokens": 7000,
        "contract": (
            "Mode: DEEP PROFESSOR. Analyze thoroughly, compare options, include risks, "
            "templates, detailed execution plan, and quality checks."
        ),
    },
}


@dataclass(frozen=True)
class BrainHit:
    brain_key: str
    brain_name: str
    title: str
    source_path: str
    text: str
    subagent: str = ""
    query_variant: str = ""
    score: float = 0.0

@dataclass(frozen=True)
class RetrievalPlan:
    task_type: str
    query_variants: tuple[str, ...]
    profile_boost: dict[str, int]
    subagent_boost: dict[str, tuple[str, ...]]
    memory_notes: tuple[str, ...]


def answer_master_question(
    question: str,
    *,
    limit_per_brain: int = 5,
    conversation_context: str = "",
    response_mode: str = "fast",
) -> str:
    question = question.strip()
    if not question:
        return "Bạn hãy nhập câu hỏi trước."

    instant = _instant_answer(question, response_mode)
    if instant:
        return instant

    plan = _build_retrieval_plan(question, response_mode)
    hits = search_all_role_brains(question, limit_per_brain=limit_per_brain, response_mode=response_mode) if limit_per_brain > 0 else []
    if not has_api_key():
        return _fallback_answer(question, hits)

    settings = _mode_settings(response_mode)
    prompt = _build_master_prompt(question, hits, conversation_context=conversation_context, mode_settings=settings, retrieval_plan=plan)
    try:
        answer = chat_with_llm(
            prompt,
            reasoning_effort=str(settings["reasoning"]),
            max_output_tokens=int(settings["max_output_tokens"]),
        )
        return _finalize_answer(answer, response_mode=response_mode, question=question)
    except Exception as error:
        fallback = _fallback_answer(question, hits)
        return f"API model đang tạm lỗi: {error}\n\n{fallback}"


def stream_master_answer(
    question: str,
    *,
    limit_per_brain: int = 5,
    conversation_context: str = "",
    response_mode: str = "fast",
):
    question = question.strip()
    if not question:
        yield "Bạn hãy nhập câu hỏi trước."
        return

    instant = _instant_answer(question, response_mode)
    if instant:
        yield instant
        return

    plan = _build_retrieval_plan(question, response_mode)
    hits = search_all_role_brains(question, limit_per_brain=limit_per_brain, response_mode=response_mode) if limit_per_brain > 0 else []
    if not has_api_key():
        yield _fallback_answer(question, hits)
        return

    settings = _mode_settings(response_mode)
    prompt = _build_master_prompt(question, hits, conversation_context=conversation_context, mode_settings=settings, retrieval_plan=plan)
    try:
        accumulated: list[str] = []
        for delta in stream_chat_with_llm(
            prompt,
            reasoning_effort=str(settings["reasoning"]),
            max_output_tokens=int(settings["max_output_tokens"]),
        ):
            yield delta
            accumulated.append(delta)
        footer = _asset_quality_footer_delta(
            "".join(accumulated),
            response_mode=response_mode,
            question=question,
        )
        if footer:
            yield footer
    except Exception as error:
        fallback = _fallback_answer(question, hits)
        yield f"API model đang tạm lỗi: {error}\n\n{fallback}"

def search_all_role_brains(question: str, *, limit_per_brain: int = 5, response_mode: str = "fast") -> list[BrainHit]:
    plan = _build_retrieval_plan(question, response_mode)
    best_by_signature: dict[tuple[str, str, str], BrainHit] = {}
    allowed_profiles = _allowed_profile_keys(plan)
    for profile in get_agent_profiles():
        if profile.key not in allowed_profiles:
            continue
        profile_limit = max(1, min(6, limit_per_brain + plan.profile_boost.get(profile.key, 0)))
        variants = plan.query_variants[:4]
        per_variant_limit = max(4, min(10, profile_limit * 2))
        for variant in variants:
            for item in _search_profile(profile, variant, per_variant_limit):
                if _is_noise_hit(item):
                    continue
                subagent = _detect_subagent(profile, str(item.get("source_path", "")))
                score = _score_hit(profile, item, plan, subagent, variant)
                hit = BrainHit(
                    brain_key=profile.key,
                    brain_name=profile.name,
                    title=str(item.get("title", "")),
                    source_path=str(item.get("source_path", "")),
                    text=str(item.get("text", "")).strip(),
                    subagent=subagent,
                    query_variant=variant,
                    score=score,
                )
                signature = (hit.brain_key, hit.source_path, hit.text[:160])
                previous = best_by_signature.get(signature)
                if previous is None or hit.score > previous.score:
                    best_by_signature[signature] = hit
    hits = sorted(best_by_signature.values(), key=lambda hit: hit.score, reverse=True)
    return hits[: max(6, limit_per_brain * 3)]

def _allowed_profile_keys(plan: RetrievalPlan) -> set[str]:
    if plan.task_type == "sales_page":
        return {"sale_page", "build_product", "case_study"}
    if plan.task_type == "launch_funnel":
        return {"jv_manager", "sale_page", "build_product", "case_study"}
    if plan.task_type == "traffic_growth":
        return {"jv_manager", "build_product", "case_study"}
    if plan.task_type == "product_build":
        return {"build_product", "sale_page", "jv_manager", "case_study"}
    return {"build_product", "sale_page", "jv_manager", "case_study"}

def _is_noise_hit(item: dict) -> bool:
    text = " ".join(str(item.get("text", "")).split())
    source_path = str(item.get("source_path", "")).lower()
    title = str(item.get("title", "")).lower()
    if len(text) < 180:
        return True
    noisy_path_markers = ("__macosx", ".ds_store", "error", "log", "cookie", "privacy policy", "terms of service")
    if any(marker in source_path or marker in title for marker in noisy_path_markers):
        return True
    alpha = sum(ch.isalpha() for ch in text)
    if alpha / max(1, len(text)) < 0.45:
        return True
    repeated = max((text.count(token) for token in ("http", "www", "subscribe", "unsubscribe")), default=0)
    return repeated > 20

def _detect_subagent(profile: AgentProfile, source_path: str) -> str:
    lowered = source_path.replace("\\", "/").lower()
    for subagent in profile.subagents:
        if f"/{subagent.key.lower()}/" in lowered or subagent.key.lower() in lowered:
            return subagent.name
    return ""

def _score_hit(profile: AgentProfile, item: dict, plan: RetrievalPlan, subagent: str, variant: str) -> float:
    score = 10.0
    score += plan.profile_boost.get(profile.key, 0) * 2.5
    boosted_subagents = plan.subagent_boost.get(profile.key, ())
    if subagent and any(name.lower() in subagent.lower() for name in boosted_subagents):
        score += 4.0
    source_path = str(item.get("source_path", "")).lower()
    title = str(item.get("title", "")).lower()
    if "child_agent_training" in source_path:
        score += 1.0
    if "index" in title or "_child_agent_index" in source_path:
        score += 0.5
    task_terms = _task_terms(plan.task_type)
    haystack = f"{title} {source_path} {str(item.get('text', '')[:1200]).lower()}"
    score += sum(1.2 for term in task_terms if term in haystack)
    score += _actionability_score(str(item.get("text", "")))
    if variant != plan.query_variants[0]:
        score += 0.4
    try:
        rank = abs(float(item.get("rank", 0)))
        score += max(0.0, 1.5 - min(rank, 1.5))
    except Exception:
        pass
    return score

def _task_terms(task_type: str) -> tuple[str, ...]:
    return {
        "sales_page": ("headline", "sales page", "offer", "objection", "faq", "cta", "guarantee", "copy"),
        "launch_funnel": ("warriorplus", "jv", "affiliate", "swipe", "oto", "order bump", "commission", "launch"),
        "product_build": ("product", "plr", "template", "checklist", "workflow", "planner", "license", "bonus"),
        "traffic_growth": ("traffic", "facebook", "quora", "medium", "seo", "lead magnet", "email list"),
    }.get(task_type, ("product", "offer", "workflow", "checklist"))

def _actionability_score(text: str) -> float:
    folded = _fold_for_match(text[:2200])
    markers = ("step", "checklist", "template", "example", "framework", "workflow", "plan", "copy", "swipe", "bonus", "offer", "cta")
    score = sum(0.7 for marker in markers if marker in folded)
    if re.search(r"\n\s*(?:\d+\.|-|\*)\s+", text):
        score += 1.0
    if "|" in text and "---" in text:
        score += 0.8
    return min(score, 5.0)

def _build_retrieval_plan(question: str, response_mode: str = "fast") -> RetrievalPlan:
    folded = _fold_for_match(question)
    task_type = "general"
    profile_boost = {"build_product": 0, "jv_manager": 0, "sale_page": 0, "case_study": 0}
    subagent_boost: dict[str, tuple[str, ...]] = {}
    notes = ["Use local brain chunks as searchable memory, not model-weight training."]
    expansions: list[str] = []

    if _contains_any(folded, ("sales page", "sale page", "trang ban", "landing page", "headline", "copy", "cta")):
        task_type = "sales_page"
        profile_boost.update({"sale_page": 3, "build_product": 1, "jv_manager": 1, "case_study": 2})
        subagent_boost["sale_page"] = ("Hook Miner", "Copywriter", "Compliance Editor", "Conversion Editor")
        expansions.extend(["hook pain mechanism objection faq guarantee cta compliance", "sales page offer stack bonus refund"])
        notes.append("Prioritize hook, mechanism, objection handling, compliance, and conversion editing.")
    elif _contains_any(folded, ("funnel", "oto", "order bump", "jv", "affiliate", "launch", "email swipe", "warriorplus")):
        task_type = "launch_funnel"
        profile_boost.update({"jv_manager": 3, "build_product": 2, "sale_page": 1, "case_study": 2})
        subagent_boost["jv_manager"] = ("JV Page Writer", "Swipe Writer", "Launch Ops", "Affiliate Researcher")
        subagent_boost["build_product"] = ("Offer Architect", "Asset Packager")
        expansions.extend(["warriorplus launch affiliate jv page email swipe commission", "front end oto order bump downsell bonus stack"])
        notes.append("Prioritize FE/OTO/bump structure, affiliate angle, launch ops, and delivery clarity.")
    elif _contains_any(folded, ("san pham", "tao san pham", "nang cap san pham", "chu de", "use case", "workflow", "product", "plr", "kit", "pack", "outline", "module", "dong goi", "zip", "license", "saas", "analyze offer", "competitor", "market research", "buyer avatar", "objection", "proof substitute", "depth checker", "warriorplus listing", "jv pack", "affiliate pack", "traffic content", "email funnel", "saas upgrade", "export product", "launch pack")):
        task_type = "product_build"
        profile_boost.update({"build_product": 3, "sale_page": 1, "jv_manager": 1, "case_study": 2})
        subagent_boost["build_product"] = ("Product Researcher", "Offer Architect", "Asset Packager", "License/Risk Checker", "SaaS Tool Packager")
        expansions.extend(["product outline checklist prompt pack template bonus license", "offer architecture digital product packaging plr saas", "start here readme zip delivery order bump oto agency license", "workflow implementation assets use case examples planner checklist compliance", "competitor spy buyer avatar objection proof substitute warriorplus listing jv affiliate traffic email funnel saas upgrade"])
        notes.append("Prioritize product structure, packaging, license/risk, and sellable deliverables.")
    elif _contains_any(folded, ("traffic", "facebook", "medium", "quora", "seo", "email list", "free traffic")):
        task_type = "traffic_growth"
        profile_boost.update({"jv_manager": 3, "build_product": 1, "case_study": 2})
        subagent_boost["jv_manager"] = ("Traffic Channel Planner", "Email/List Growth Operator")
        expansions.extend(["free traffic facebook group medium quora linkedin seo", "lead magnet opt in email list nurture"])
        notes.append("Prioritize channel plan, lead magnet, list growth, and non-spam execution.")

    if (response_mode or "").lower() in {"asset", "deep"}:
        expansions.append("template checklist framework mistakes quality check")
    if _contains_any(folded, ("case study", "du lieu cu", "file cu", "training", "train", "kdp", "kids", "printable", "prompt template")):
        profile_boost["case_study"] = max(profile_boost.get("case_study", 0), 4)
        expansions.extend([
            "case study product pattern sales page funnel jv email swipe",
            "kdp printable kids worksheet canva plr prompt template pack",
        ])
        notes.append("Prioritize Case Study Brain from old files as RAG memory; extract patterns, do not copy assets verbatim.")

    variants = [question]
    variants.extend(expansions)
    variants.append(f"{question} {' '.join(expansions[:2])}".strip())
    deduped = tuple(dict.fromkeys(item for item in variants if item.strip()))
    return RetrievalPlan(task_type, deduped, profile_boost, subagent_boost, tuple(notes))

def _contains_any(text: str, markers: tuple[str, ...]) -> bool:
    return any(marker in text for marker in markers)

def _retrieval_plan_summary(plan: RetrievalPlan) -> str:
    boosts = ", ".join(f"{key}+{value}" for key, value in plan.profile_boost.items() if value)
    subagents = []
    for key, names in plan.subagent_boost.items():
        if names:
            subagents.append(f"{key}: {', '.join(names)}")
    lines = [
        f"Detected task type: {plan.task_type}",
        f"Brain priority: {boosts or 'balanced'}",
        f"Query variants used: {len(plan.query_variants)}",
    ]
    if subagents:
        lines.append("Child-agent priority: " + " | ".join(subagents))
    if plan.memory_notes:
        lines.append("Memory use notes: " + " ".join(plan.memory_notes))
    return "\n".join(lines)

def _uses_product_creation_os(plan: RetrievalPlan, question: str) -> bool:
    if plan.task_type in {"product_build", "launch_funnel"}:
        return True
    folded = _fold_for_match(question)
    return _contains_any(
        folded,
        (
            "san pham",
            "product",
            "kit",
            "pack",
            "plr",
            "saas",
            "warriorplus",
            "gumroad",
            "payhip",
            "oto",
            "order bump",
            "dong goi",
            "zip",
            "ban duoc",
            "analyze offer",
            "competitor",
            "market research",
            "buyer avatar",
            "objection",
            "proof substitute",
            "depth checker",
            "warriorplus listing",
            "jv pack",
            "affiliate pack",
            "traffic content",
            "email funnel",
            "saas upgrade",
            "launch pack",
        ),
    )

def _format_hit_label(hit: BrainHit) -> str:
    pieces = [f"{hit.brain_name} ({hit.brain_key})"]
    if hit.subagent:
        pieces.append(f"child: {hit.subagent}")
    if hit.query_variant:
        pieces.append(f"query: {_clip(hit.query_variant, 120)}")
    return " | ".join(pieces)

def master_brain_status() -> str:
    lines = ["Trạng thái bộ não chủ", "====================="]
    for profile in get_agent_profiles():
        summary = brain_summary(profile.db_path)
        lines.append("")
        lines.append(profile.name)
        lines.append(f"- Nhiệm vụ: {profile.mission}")
        lines.append(f"- Database: {summary['db_path']}")
        lines.append(f"- Kích thước: {summary['db_size_mb']} MB")
        lines.append(f"- Tài liệu: {summary['documents']}")
        lines.append(f"- Chunk: {summary['chunks']}")
        lines.append(f"- Text trích xuất: {summary['text_mb']} MB")
        lines.append(f"- Lỗi: {summary['errors']}")
    return "\n".join(lines)


def format_sources(question: str, *, limit_per_brain: int = 5) -> str:
    hits = search_all_role_brains(question, limit_per_brain=limit_per_brain)
    if not hits:
        return "Không tìm thấy source phù hợp trong 3 bộ não."
    lines = [f"Sources for: {question}"]
    for index, hit in enumerate(hits, start=1):
        excerpt = _clip(hit.text, 600)
        lines.append("")
        lines.append(f"{index}. [{hit.brain_name}] {hit.title}")
        lines.append(f"Source: {hit.source_path}")
        lines.append(excerpt)
    return "\n".join(lines)


def _search_profile(profile: AgentProfile, question: str, limit: int) -> list[dict]:
    try:
        return search_brain(question, limit=limit, db_path=profile.db_path)
    except Exception:
        return []


def _instant_answer(question: str, response_mode: str) -> str:
    if response_mode not in {"quick", "fast"}:
        return ""
    q = " ".join(question.lower().split())
    if len(q) > 120:
        return ""
    if "plr" in q and ("blr" in q or "bl r" in q or "b l r" in q):
        return (
            "**PLR** = *Private Label Rights*: quyền nhãn riêng. Thường cho phép sửa, rebrand, "
            "đổi tên/bìa và bán lại tùy license.\n\n"
            "**BLR** không phải thuật ngữ license chuẩn phổ biến. Nhiều trường hợp là viết nhầm, "
            "tên vendor tự đặt, hoặc một biến thể quyền riêng.\n\n"
            "Kết luận: **PLR có nghĩa rõ hơn; BLR phải mở file license kiểm tra**. Đừng mặc định BLR = PLR."
        )
    if q in {"plr là gì", "plr la gi", "plr"}:
        return (
            "**PLR = Private Label Rights**: tài liệu/sản phẩm số có quyền nhãn riêng. "
            "Bạn có thể sửa, rebrand, đóng gói lại và bán theo điều kiện trong license. "
            "Luôn kiểm tra license trước khi bán trên WarriorPlus."
        )
    if q in {"mrr là gì", "mrr la gi", "mrr"}:
        return (
            "**MRR = Master Resell Rights**: bạn được bán lại sản phẩm và thường được bán kèm quyền resale cho khách. "
            "Nhưng đa số MRR không cho sửa sâu như PLR."
        )
    if q in {"rr là gì", "rr la gi", "rr"}:
        return (
            "**RR = Resell Rights**: bạn được bán lại sản phẩm, nhưng thường không được chỉnh sửa và không được chuyển quyền bán lại cho khách."
        )
    return ""


def _mode_settings(response_mode: str) -> dict[str, str | int]:
    key = (response_mode or "fast").strip().lower()
    return MODE_SETTINGS.get(key, MODE_SETTINGS["fast"])

def _build_master_prompt(
    question: str,
    hits: list[BrainHit],
    *,
    conversation_context: str = "",
    mode_settings: dict[str, str | int] | None = None,
    retrieval_plan: RetrievalPlan | None = None,
) -> str:
    settings = mode_settings or MODE_SETTINGS["fast"]
    plan = retrieval_plan or _build_retrieval_plan(question)
    context = _format_context(hits, max_chars=int(settings["excerpt_chars"]))
    playbook_context = _load_playbooks_for_plan(plan, question)
    recent_chat = conversation_context.strip() or "No recent conversation."
    output_contract = _output_contract_for(question, plan)
    return f"""You are the Master Agent for a PLR + SaaS + WarriorPlus business.

Answer in Vietnamese with natural tone, like a practical professor and senior strategist.
Output quality must stay premium: detailed, structured, step-by-step, practical, with checklists, examples, and exact next actions when useful.
{settings["contract"]}
{ASSET_QUALITY_GATE if settings.get("name") in {"Asset", "Sau"} else ""}
{PRODUCT_CREATION_OS if _uses_product_creation_os(plan, question) else ""}
{BRAIN_DIFFERENTIATION_ENGINE if _uses_product_creation_os(plan, question) else ""}
{MASTER_AGENT_OUTPUT_DISCIPLINE if _uses_product_creation_os(plan, question) or settings.get("name") in {"Asset", "Sau"} else ""}
{output_contract}
Use the four trained local/searchable brains as your main evidence:
- Build Product Agent: product creation, offer, product packs, licensing risk.
- JV Manager Agent: WarriorPlus launch, affiliate, JV, email swipe, launch ops.
- Sale Page Agent: direct response copy, sales page, hook, objection handling, compliance.
- Case Study Brain Agent: old files from G:\\file_backup used as searchable case studies for product patterns, sales pages, funnels, JV packs, KDP/kids printables, and prompt/template packs.

Each main brain also contains child-agent training folders:
- Build Product child agents: product research, offer architecture, asset packaging, license/risk, digital curriculum, SaaS/tool packaging.
- JV Manager child agents: affiliate research, JV page, swipe/email, launch ops, traffic channel planning, email/list growth.
- Sale Page child agents: hook mining, copywriting, compliance editing, conversion editing.
- Case Study child agents: product research, sales page patterns, email swipes, WarriorPlus/JV, funnel/OTO, KDP/kids printables.

Current retrieval plan:
{_retrieval_plan_summary(plan)}

Priority playbook context:
{playbook_context}

Rules:
1. First answer the user directly.
2. Use the provided brain context when it is relevant.
3. If the brain context is weak or missing, say what is missing and give a practical next step.
4. Do not pretend the raw 60GB is inside the model weights. Explain it as local searchable memory/brain when needed.
5. Avoid income guarantees, fake scarcity, and unsafe license assumptions.
6. End with clear next actions the user can execute now.
7. Do not add a source/brain footer. Do not write "Nguồn brain hữu ích nhất", "Nguon brain huu ich nhat", or similar source summaries.
8. Do not end with "Nếu bạn muốn..." / "Neu ban muon..." follow-up offers. Keep the answer decisive and clean.
9. For beginner/how-to questions, use this structure: short diagnosis, 7-14 day plan, daily actions, templates/prompts, mistakes to avoid, today's task.
10. Prefer a complete useful answer over asking follow-up questions unless the task is impossible without one.
11. Always answer in Vietnamese unless the user explicitly asks for English. Product names and short headlines can remain English, but explanations, body copy, FAQ, and notes must be Vietnamese.
12. For sales page, WarriorPlus, funnel, OTO, email swipe, bonus stack, offer, or launch asset requests, produce a complete usable deliverable, not a short outline. For a sales page, include: headline, subheadline, problem, agitate, solution, what is inside, bonus stack, who it is for, who it is not for, license/compliance note, FAQ, refund/guarantee language, and CTA. Keep claims realistic and avoid income promises.
13. For sales page output, do not stop at a minimal page. Use direct-response structure: hook, pain, consequence, mechanism, offer stack, benefit bullets, objection handling, bonuses, FAQ, risk reversal/refund language, compliance note, and final CTA.
14. For funnel output, include FE, order bump, OTO1, OTO2, optional downsell, delivery assets, affiliate angle, email sequence, and launch checklist.
15. When comparing items, scoring niches, planning funnels, listing packages, pricing, schedules, or giving research results, use real Markdown tables with header row and divider row. Do not fake tables with plain text separators.
16. Use the retrieval plan to decide which internal expertise to emphasize. Blend evidence from multiple brains when the task crosses product, launch, and copy.
17. For product creation or product-upgrade requests, always output a productized structure: verdict, buyer, promise, FE contents, bonuses, OTO/bump ideas, file/ZIP structure, build checklist, pricing, compliance notes, and next action.
18. For full product strategy requests, include these modules when relevant: market/competitor patterns, buyer avatar, objections, proof substitutes, license/risk, product depth score, specific asset files, WarriorPlus listing, JV pack, free traffic content, email list builder, SaaS upgrade, and final NEN LAM / CHUA NEN LAM / BO QUA decision.
19. Always make the answer different from ordinary AI by adding local-brain strategy: what to build, what to skip, how to package, how to launch, what risk to remove, and what file assets to create.
20. Include the buyer-facing answer to "AI can do this, why buy?" whenever the product contains prompts, templates, swipes, headlines, captions, ebook text, or AI-generated content.
15. For any generated asset, include a compact final section named "Tự kiểm chất lượng" with 5-7 checklist lines. Do not include hidden reasoning or source dumps.

User question:
{question}

Recent conversation:
{recent_chat}

Relevant local brain context:
{context}
"""

def _output_contract_for(question: str, plan: RetrievalPlan) -> str:
    module_key = _requested_module_key(question)
    if module_key and module_key in MODULE_OUTPUT_CONTRACTS:
        return MODULE_OUTPUT_CONTRACTS[module_key]
    if _is_short_email_kit_request(question):
        return SHORT_EMAIL_KIT_CONTRACT
    if _uses_product_creation_os(plan, question):
        return DEFAULT_LAUNCH_OS_CONTRACT
    return ""

def _load_playbooks_for_plan(plan: RetrievalPlan, question: str) -> str:
    names = []
    folded = _fold_for_match(question)
    if plan.task_type == "sales_page":
        names.extend(["sales_page_playbook.md", "warriorplus_funnel_playbook.md"])
    elif plan.task_type == "launch_funnel":
        names.extend(["jv_manager_playbook.md", "warriorplus_funnel_playbook.md", "sales_page_playbook.md"])
    elif plan.task_type == "traffic_growth":
        names.extend(["jv_manager_playbook.md", "warriorplus_funnel_playbook.md"])
    elif plan.task_type == "product_build":
        names.extend(["build_product_playbook.md", "warriorplus_funnel_playbook.md"])
    if "email" in folded and "campaign" in folded:
        names.insert(0, "email_campaign_kit_playbook.md")
    if "saas" in folded or "membership" in folded or "whitelabel" in folded:
        names.append("saas_upgrade_playbook.md")
    if not names:
        names.append("build_product_playbook.md")
    sections = []
    seen = set()
    for name in names:
        if name in seen:
            continue
        seen.add(name)
        path = PLAYBOOK_DIR / name
        if path.exists():
            sections.append(f"## {name}\n{_clip(path.read_text(encoding='utf-8'), 1800)}")
    return "\n\n".join(sections) if sections else "No playbook found."

def _requested_module_key(question: str) -> str:
    folded = _fold_for_match(question)
    explicit = re.search(r"\[module:\s*([a-z0-9_\- ]+)\]", folded)
    if explicit:
        return explicit.group(1).strip().replace("-", "_").replace(" ", "_")
    mapping = (
        ("analyze plr file", "analyze_plr"),
        ("analyze plr folder", "analyze_plr"),
        ("analyze plr", "analyze_plr"),
        ("product idea scoring", "idea_score"),
        ("idea score", "idea_score"),
        ("product depth checker", "depth_check"),
        ("depth check", "depth_check"),
        ("upgrade raw content", "upgrade_kit"),
        ("upgrade raw ai content", "upgrade_kit"),
        ("upgrade kit", "upgrade_kit"),
        ("create product assets", "product_assets"),
        ("product assets", "product_assets"),
        ("quality control checklist", "qc_checklist"),
        ("qc checklist", "qc_checklist"),
        ("export product zip", "export_zip"),
        ("export zip", "export_zip"),
        ("build offer angle", "offer_angle"),
        ("offer angle", "offer_angle"),
        ("write sales page", "sales_page"),
        ("sales page", "sales_page"),
        ("objection handler", "objections"),
        ("objections", "objections"),
        ("create funnel plan", "funnel_plan"),
        ("funnel plan", "funnel_plan"),
        ("warriorplus listing", "warriorplus_listing"),
        ("w+ listing", "warriorplus_listing"),
        ("proof substitute generator", "proof"),
        ("proof", "proof"),
        ("build jv page", "jv_page"),
        ("jv page", "jv_page"),
        ("affiliate swipe pack", "swipe_pack"),
        ("swipe pack", "swipe_pack"),
        ("jv prospect tracker", "prospects"),
        ("prospect tracker", "prospects"),
        ("prospects", "prospects"),
        ("outreach messages", "outreach"),
        ("outreach", "outreach"),
        ("affiliate tier manager", "tiers"),
        ("tiers", "tiers"),
        ("review access manager", "review_access"),
        ("review access", "review_access"),
        ("saas potential analyzer", "saas_potential"),
        ("saas potential", "saas_potential"),
        ("saas mvp planner", "mvp_plan"),
        ("mvp plan", "mvp_plan"),
        ("membership planner", "membership"),
        ("membership", "membership"),
        ("whitelabel license planner", "whitelabel"),
        ("whitelabel", "whitelabel"),
        ("scan plr library", "scan_library"),
        ("scan library", "scan_library"),
        ("market gap finder", "market_gap"),
        ("market gap", "market_gap"),
        ("competitor pattern analyzer", "competitor"),
        ("competitor", "competitor"),
        ("asset completeness checker", "asset_completeness"),
        ("asset completeness", "asset_completeness"),
        ("buyer journey builder", "buyer_journey"),
        ("buyer journey", "buyer_journey"),
        ("use case generator", "use_cases"),
        ("use cases", "use_cases"),
        ("before after reframe", "before_after"),
        ("before/after", "before_after"),
        ("offer gap detector", "offer_gap"),
        ("offer gap", "offer_gap"),
        ("pricing commission calculator", "pricing_commission"),
        ("pricing", "pricing_commission"),
        ("commission calculator", "pricing_commission"),
        ("launch readiness score", "launch_readiness"),
        ("launch readiness", "launch_readiness"),
        ("soft launch planner", "soft_launch"),
        ("soft launch", "soft_launch"),
        ("refund risk checker", "refund_risk"),
        ("refund risk", "refund_risk"),
        ("delivery page builder", "delivery_page"),
        ("delivery page", "delivery_page"),
        ("customer onboarding emails", "onboarding"),
        ("onboarding emails", "onboarding"),
        ("backend recommendation engine", "backend_recommendation"),
        ("backend recommendation", "backend_recommendation"),
        ("jv fit score", "jv_fit"),
        ("jv fit", "jv_fit"),
        ("product line planner", "product_line"),
        ("product line", "product_line"),
        ("translate & localize", "translate_english"),
        ("translate english", "translate_english"),
        ("english market", "translate_english"),
        ("platform fit selector", "platform_fit"),
        ("platform fit", "platform_fit"),
        ("one-click launch pack", "launch_pack"),
        ("one click launch pack", "launch_pack"),
        ("launch pack", "launch_pack"),
        ("case study brain", "case_study_search"),
        ("case study search", "case_study_search"),
        ("case study patterns", "case_study_patterns"),
        ("extract patterns", "case_study_patterns"),
        ("pattern extractor", "case_study_patterns"),
        ("training agent", "case_study_search"),
        ("train case study", "train_case_study_brain"),
        ("full case study train", "train_full_case_study_brain"),
        ("training status", "training_status"),
        ("training report", "export_training_report"),
        ("30 step workflow", "workflow_30"),
        ("ai workflow", "ai_workflow_20"),
        ("evidence mode", "evidence_mode"),
        ("knowledge used", "evidence_mode"),
    )
    for marker, key in mapping:
        if marker in folded:
            return key
    return ""

def _is_short_email_kit_request(question: str) -> bool:
    folded = _fold_for_match(question)
    has_email = "email" in folded
    has_templates = any(marker in folded for marker in ("template", "mau", "mẫu", "short email", "email ngan", "email ngắn"))
    has_quantity = any(marker in folded for marker in ("30", "ba muoi", "thirty"))
    has_create = any(marker in folded for marker in ("tao", "viet", "cho toi", "create", "write"))
    return has_email and has_templates and has_quantity and has_create


def _format_context(hits: list[BrainHit], *, max_chars: int = MAX_EXCERPT_CHARS) -> str:
    if not hits:
        return "No relevant chunks were found in the three local brains."

    sections: list[str] = []
    for index, hit in enumerate(hits, start=1):
        sections.append(
            f"""[Source {index}]
Brain: {_format_hit_label(hit)}
Title: {hit.title}
Path: {hit.source_path}
Excerpt:
{_clip(hit.text, max_chars)}
"""
        )
    return "\n".join(sections)


def _fallback_answer(question: str, hits: list[BrainHit]) -> str:
    if not hits:
        return (
            "API model đang tạm không sẵn sàng, nhưng bộ não local vẫn hoạt động.\n\n"
            "Với người mới tinh, đi theo 5 bước đầu tiên:\n\n"
            "1. Chọn một ngách nhỏ: PLR cho người bán sản phẩm số, SaaS email, AI prompt cho marketer, hoặc sales page kit.\n"
            "2. Chọn một sản phẩm đầu tiên thật đơn giản. Đừng làm SaaS lớn ngay.\n"
            "3. Viết một lời hứa rõ: ai nhận được kết quả gì, bằng cách nào.\n"
            "4. Tạo bản sản phẩm tối thiểu gồm PDF hướng dẫn, checklist, prompt pack, template sales page và email swipe.\n"
            "5. Đưa lên WarriorPlus/JVZoo để test buyer, lấy phản hồi rồi mới nâng cấp.\n\n"
            "Việc cần làm ngay hôm nay: chọn 1 ngách, 1 buyer, 1 vấn đề đau nhất, rồi viết tên sản phẩm đầu tiên."
        )

    concepts = _fallback_concepts(hits)
    lines = [
        "API model đang tạm không sẵn sàng, nên mình dùng bộ não local để trả lời gọn cho bạn.",
        "",
        f"Câu hỏi: {question}",
        "",
        "Lộ trình cho người mới tinh:",
        "",
        "1. Đừng bắt đầu bằng SaaS lớn.",
        "Bắt đầu bằng một sản phẩm số nhỏ để học thị trường: PDF guide, checklist, prompt pack, template, swipe file hoặc mini toolkit.",
        "",
        "2. Chọn một ngách có buyer rõ.",
        "Ưu tiên PLR, AI, WarriorPlus, affiliate, sales page, email funnel hoặc SaaS tool nhỏ. Ngách phải trả lời được: ai mua, họ đau gì, họ muốn kết quả gì.",
        "",
        "3. Tạo offer đầu tiên trong 7 ngày.",
        "Bản tối thiểu nên có: Start Here, hướng dẫn chính, checklist, prompt pack, sales page template, email swipe và bonus stack.",
        "",
        "4. Tạo trang bán hàng đơn giản.",
        "Trang chỉ cần rõ: headline, vấn đề, giải pháp, bên trong có gì, bonus, giá, FAQ, nút mua. Tránh cam kết thu nhập và tránh copy nguyên văn PLR.",
        "",
        "5. Kéo traffic miễn phí trước.",
        "Dùng Facebook profile/group, bài hành trình 7 ngày, Medium/Quora hoặc email list nhỏ. Mỗi bài nên dẫn về lead magnet hoặc trang bán hàng.",
        "",
        "6. Test bằng WarriorPlus/JVZoo.",
        "Đặt giá thấp để lấy buyer list, proof và phản hồi. Sau đó mới làm OTO, agency license, membership hoặc SaaS.",
        "",
        "Việc làm ngay hôm nay:",
        "",
        "- Chọn 1 chủ đề sản phẩm.",
        "- Viết 1 lời hứa sản phẩm trong 1 câu.",
        "- Tạo outline 7 phần.",
        "- Viết 3 bài content hành trình đầu tiên.",
        "- Tạo Google Sheet ghi đối thủ, angle, giá, bonus và bài học học được.",
    ]
    if concepts:
        lines.extend(["", "Gợi ý từ brain local đang khớp với câu hỏi của bạn:", ""])
        for item in concepts[:4]:
            lines.append(f"- {item}")
    return "\n".join(lines)


def _fallback_concepts(hits: list[BrainHit]) -> list[str]:
    concepts: list[str] = []
    seen = set()
    for hit in hits:
        title = " ".join(hit.title.split())
        if title and title not in seen:
            concepts.append(title)
            seen.add(title)
    return concepts


def _clip(text: str, max_chars: int) -> str:
    cleaned = " ".join(text.split())
    if len(cleaned) <= max_chars:
        return cleaned
    return cleaned[: max_chars - 3].rstrip() + "..."


def _clean_answer(text: str) -> str:
    lines = text.strip().splitlines()
    cleaned: list[str] = []
    skip_rest = False
    stop_prefixes = (
        "Nguồn brain hữu ích",
        "Nguon brain huu ich",
        "Nguồn hữu ích",
        "Brain/source hữu ích",
        "Sources used",
        "Useful brain sources",
        "Nếu bạn muốn",
        "Neu ban muon",
    )
    for line in lines:
        stripped = line.strip().lstrip("#*- ").strip()
        if any(stripped.startswith(prefix) for prefix in stop_prefixes):
            skip_rest = True
        if not skip_rest:
            cleaned.append(line)
    return "\n".join(cleaned).strip()

def _finalize_answer(text: str, *, response_mode: str, question: str) -> str:
    cleaned = _clean_answer(text)
    footer = _asset_quality_footer_delta(cleaned, response_mode=response_mode, question=question)
    if footer:
        return f"{cleaned.rstrip()}{footer}"
    return cleaned

def _asset_quality_footer_delta(text: str, *, response_mode: str, question: str) -> str:
    if not _is_asset_request(response_mode, question):
        return ""
    if _has_quality_footer(text):
        return ""
    return "\n\n" + _quality_footer(question)

def _is_asset_request(response_mode: str, question: str) -> bool:
    if (response_mode or "").strip().lower() == "asset":
        return True
    folded = _fold_for_match(question)
    markers = (
        "sales page",
        "sale page",
        "warriorplus",
        "funnel",
        "oto",
        "bonus stack",
        "email swipe",
        "affiliate swipe",
        "jv page",
        "landing page",
        "trang ban hang",
        "viet sales",
        "viet sale",
        "viet trang ban",
        "tao sales",
        "tao funnel",
        "email ban hang",
        "bonus",
        "offer",
        "san pham",
        "product",
        "kit",
        "pack",
        "workflow",
        "use case",
        "campaign map",
        "planner",
        "checklist",
        "compliance",
        "analyze offer",
        "market research",
        "competitor",
        "buyer avatar",
        "objection",
        "proof substitute",
        "license",
        "risk",
        "warriorplus listing",
        "jv pack",
        "affiliate pack",
        "traffic content",
        "email funnel",
        "saas upgrade",
        "export product",
        "launch pack",
    )
    return any(marker in folded for marker in markers)

def _has_quality_footer(text: str) -> bool:
    folded = _fold_for_match(text)
    return (
        "tu kiem chat luong" in folded
        or "quality checklist" in folded
        or "asset quality" in folded
        or "kiem chat luong" in folded
    )

def _quality_footer(question: str) -> str:
    folded = _fold_for_match(question)
    lines = [
        "**Tu kiem chat luong**",
        "- Loi hua ro rang, thuc te, khong cam ket thu nhap.",
        "- Doi tuong mua va van de dau duoc neu cu the.",
        "- Offer co deliverables, bonus, FAQ, CTA va ngon ngu hoan tien/an toan.",
        "- Neu co PLR/license: khong tu gan quyen, luon yeu cau kiem tra license.",
        "- Noi dung co the dung ngay, chi can thay ten san pham, gia va link mua.",
    ]
    if any(marker in folded for marker in ("funnel", "oto", "order bump", "jv", "affiliate")):
        lines.insert(4, "- Funnel/JV co FE, OTO/bump, goc affiliate va tai san launch can giao.")
    if any(marker in folded for marker in ("sales page", "sale page", "trang ban", "landing page")):
        lines.insert(4, "- Sales page co hook, pain, mechanism, offer stack, objections, FAQ va CTA.")
    return "\n".join(lines)

def _fold_for_match(text: str) -> str:
    normalized = (text or "").lower()
    normalized = (
        normalized.replace("đ", "d")
        .replace("Đ", "d")
        .replace("Ä‘", "d")
        .replace("Ä", "d")
    )
    normalized = normalized.replace("đ", "d").replace("Đ", "d")
    decomposed = unicodedata.normalize("NFKD", normalized)
    return "".join(char for char in decomposed if not unicodedata.combining(char))

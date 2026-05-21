from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from config import DATABASE_DIR, FILE_BACKUP_DIR, ROOT_DIR

INPUT_ROOT = ROOT_DIR / "input_files"
AGENT_BRAINS_ROOT = DATABASE_DIR / "agent_brains"


@dataclass(frozen=True)
class SubAgentProfile:
    key: str
    name: str
    job: str


@dataclass(frozen=True)
class AgentProfile:
    key: str
    name: str
    input_dir: Path
    brain_dir: Path
    db_path: Path
    mission: str
    subagents: tuple[SubAgentProfile, ...]


def get_agent_profiles() -> list[AgentProfile]:
    return [
        AgentProfile(
            key="build_product",
            name="Build Product Agent",
            input_dir=INPUT_ROOT / "01_BUILD_PRODUCT",
            brain_dir=AGENT_BRAINS_ROOT / "build_product",
            db_path=AGENT_BRAINS_ROOT / "build_product" / "build_product_brain.sqlite",
            mission="Build complete digital product packs from PLR/SaaS source material.",
            subagents=(
                SubAgentProfile("product_researcher", "Product Researcher", "Find source angles, niches, buyer pains, and product opportunities."),
                SubAgentProfile("offer_architect", "Offer Architect", "Create product promise, outline, modules, bonuses, and OTO structure."),
                SubAgentProfile("asset_packager", "Asset Packager", "Turn outputs into clean deliverables, checklists, prompts, templates, and ZIP structure."),
                SubAgentProfile("license_risk_checker", "License/Risk Checker", "Flag unclear rights, risky claims, and regulated-topic concerns."),
                SubAgentProfile("digital_product_curriculum_builder", "Digital Product Curriculum Builder", "Turn lesson libraries, challenges, and workflows into paid digital product training."),
                SubAgentProfile("saas_tool_packager", "SaaS Tool Packager", "Package SaaS, AI agents, apps, frontend/backend demos, and tool workflows into sellable offers."),
            ),
        ),
        AgentProfile(
            key="jv_manager",
            name="JV Manager Agent",
            input_dir=INPUT_ROOT / "02_JV_MANAGER",
            brain_dir=AGENT_BRAINS_ROOT / "jv_manager",
            db_path=AGENT_BRAINS_ROOT / "jv_manager" / "jv_manager_brain.sqlite",
            mission="Prepare WarriorPlus/JV launch assets, affiliate pages, swipes, commission angles, and partner outreach.",
            subagents=(
                SubAgentProfile("affiliate_researcher", "Affiliate Researcher", "Extract affiliate angles, buyer avatars, and promotion hooks."),
                SubAgentProfile("jv_page_writer", "JV Page Writer", "Create JV page copy, affiliate instructions, contest notes, and promo assets."),
                SubAgentProfile("swipe_writer", "Swipe Writer", "Write prelaunch, launch day, follow-up, and bonus-angle email swipes."),
                SubAgentProfile("launch_ops", "Launch Ops", "Build launch checklist, delivery notes, refund terms, and approval workflow."),
                SubAgentProfile("traffic_channel_planner", "Traffic Channel Planner", "Plan Facebook, Medium, Quora, SEO, LinkedIn, and free-traffic promotion systems."),
                SubAgentProfile("email_list_growth_operator", "Email/List Growth Operator", "Build lead magnets, opt-in flows, buyer list nurture, and follow-up systems."),
            ),
        ),
        AgentProfile(
            key="sale_page",
            name="Sale Page Agent",
            input_dir=INPUT_ROOT / "03_SALE_PAGE",
            brain_dir=AGENT_BRAINS_ROOT / "sale_page",
            db_path=AGENT_BRAINS_ROOT / "sale_page" / "sale_page_brain.sqlite",
            mission="Create compliant direct-response sales pages from source offers, PLR, examples, screenshots, and transcripts.",
            subagents=(
                SubAgentProfile("hook_miner", "Hook Miner", "Find headlines, pain points, mechanisms, objections, and proof substitutes."),
                SubAgentProfile("copywriter", "Copywriter", "Draft sales page sections, bullets, CTAs, FAQ, and guarantee copy."),
                SubAgentProfile("compliance_editor", "Compliance Editor", "Remove fake scarcity, income guarantees, unsafe claims, and license assumptions."),
                SubAgentProfile("conversion_editor", "Conversion Editor", "Improve flow, clarity, offer stack, objection handling, and CTA strength."),
            ),
        ),
        AgentProfile(
            key="ai_printables",
            name="AI Printables Agent",
            input_dir=AGENT_BRAINS_ROOT / "ai_printables",
            brain_dir=AGENT_BRAINS_ROOT / "ai_printables",
            db_path=AGENT_BRAINS_ROOT / "ai_printables" / "ai_printables_brain.sqlite",
            mission="Build AI-assisted PLR products, KDP covers, coloring books, journals, posters, social assets, Etsy/Canva printable bundles, and fast rebrandable product packs from Udemy transcript lessons.",
            subagents=(
                SubAgentProfile("niche_miner", "Niche Miner", "Find profitable printable/KDP/Etsy/Canva angles from course transcripts."),
                SubAgentProfile("product_system_builder", "Product System Builder", "Turn AI workflows into sellable PLR packs, journals, coloring books, worksheets, covers, and bundles."),
                SubAgentProfile("asset_prompt_builder", "Asset Prompt Builder", "Create prompts, style systems, asset specs, and production workflows for image/text products."),
                SubAgentProfile("launch_packager", "Launch Packager", "Package offers with FE, bump, OTO, license, delivery, and WarriorPlus/Gumroad/Etsy positioning."),
            ),
        ),
        AgentProfile(
            key="case_study",
            name="Case Study Brain Agent",
            input_dir=FILE_BACKUP_DIR,
            brain_dir=AGENT_BRAINS_ROOT / "case_study",
            db_path=AGENT_BRAINS_ROOT / "case_study" / "case_study_brain.sqlite",
            mission="Use old files as searchable case-study memory for PLR, SaaS, WarriorPlus, KDP, kids printables, sales pages, funnels, JV packs, and launch proof patterns.",
            subagents=(
                SubAgentProfile("product_research", "Product Research Miner", "Find market patterns, product angles, buyer pains, and useful product structures from old files."),
                SubAgentProfile("sales_page", "Sales Page Pattern Miner", "Extract sales page structures, hooks, offer stacks, objections, and proof substitutes."),
                SubAgentProfile("email_swipes", "Email Swipe Pattern Miner", "Find email sequences, subject lines, launch swipes, and follow-up patterns."),
                SubAgentProfile("warriorplus_jv", "WarriorPlus/JV Pattern Miner", "Find JV page, affiliate, commission, review access, and launch operation patterns."),
                SubAgentProfile("funnel_oto", "Funnel/OTO Pattern Miner", "Find FE, bump, OTO, backend, downsell, and bundle structures."),
                SubAgentProfile("kdp_kids_printables", "KDP/Kids Printable Miner", "Find KDP printable, kids worksheet, Canva, planner, and educational bundle patterns."),
            ),
        ),
    ]


def profile_by_key(key: str) -> AgentProfile:
    for profile in get_agent_profiles():
        if profile.key == key:
            return profile
    raise KeyError(f"Unknown agent profile: {key}")

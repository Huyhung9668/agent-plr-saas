from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

from config import EXPORTS_DIR, ROOT_DIR


@dataclass(frozen=True)
class AgentStep:
    id: str
    name: str
    folder: str
    output: str
    checklist: tuple[str, ...]


@dataclass(frozen=True)
class WorkflowAgent:
    id: str
    name: str
    role: str
    mission: str
    input_root: str
    final_output: str
    steps: tuple[AgentStep, ...]


AGENTS: tuple[WorkflowAgent, ...] = (
    WorkflowAgent(
        id="build_product",
        name="BUILD PRODUCT",
        role="Product builder agent for PLR, MRR, RR, prompt packs, templates, mini courses, and digital assets.",
        mission="Turn raw source material into a packaged, deliverable digital product with bonuses, backend offers, and an improvement path.",
        input_root="input_files/agent_workflows/01_build_product",
        final_output="A complete product pack: core product, bonuses, delivery structure, upsell/backend plan, and version roadmap.",
        steps=(
            AgentStep(
                "01",
                "Nghien cuu san pham",
                "01_product_research",
                "Research brief with niche, market demand, competitors, buyer pains, and validation notes.",
                (
                    "Read source files, PLR licenses, market notes, buyer comments, and competitor examples.",
                    "Score demand, freshness, rebrand potential, risk, and ease of creation.",
                    "Reject weak or risky angles before product creation starts.",
                ),
            ),
            AgentStep(
                "02",
                "Len y tuong va dinh vi",
                "02_idea_positioning",
                "Product concept with buyer avatar, promise, title angles, USP, and pricing idea.",
                (
                    "Pick a narrow buyer segment.",
                    "Transform generic PLR into a fresh promise.",
                    "Write product names, positioning angles, and offer boundaries.",
                ),
            ),
            AgentStep(
                "03",
                "Tao san pham so",
                "03_digital_product_creation",
                "Core product assets such as ebook, prompt pack, templates, checklist, mini course, or digital files.",
                (
                    "Choose the simplest format that can deliver the promise.",
                    "Create reusable assets instead of only long-form theory.",
                    "Keep claims realistic and license-safe.",
                ),
            ),
            AgentStep(
                "04",
                "Xay dung noi dung",
                "04_content_building",
                "Module content, lessons, worksheets, examples, scripts, and implementation steps.",
                (
                    "Rewrite source material with a new angle.",
                    "Add examples, checklists, prompts, and current workflows.",
                    "Remove outdated claims, copied copy, and unsupported income promises.",
                ),
            ),
            AgentStep(
                "05",
                "Dong goi san pham",
                "05_product_packaging",
                "Clean product structure with start-here file, modules, filenames, bundle map, and manifest.",
                (
                    "Organize files in buyer-friendly order.",
                    "Use simple names and numbered folders.",
                    "Add a start-here guide and usage instructions.",
                ),
            ),
            AgentStep(
                "06",
                "Tao bonus",
                "06_bonus_creation",
                "Bonus stack with quick wins, templates, swipe files, extra prompts, and value logic.",
                (
                    "Add bonuses that help buyers implement faster.",
                    "Avoid fake inflated values.",
                    "Match each bonus to a real objection or desired shortcut.",
                ),
            ),
            AgentStep(
                "07",
                "Thiet ke va trinh bay",
                "07_design_presentation",
                "Design notes, cover/mockup direction, formatting checklist, and presentation polish.",
                (
                    "Make product easy to scan and use.",
                    "Prepare cover, mockup, thumbnails, or layout guidance.",
                    "Check visual consistency across PDFs, docs, and delivery assets.",
                ),
            ),
            AgentStep(
                "08",
                "Setup giao hang",
                "08_delivery_setup",
                "Delivery page, download page, member access notes, hosting checklist, and buyer email.",
                (
                    "Confirm files are zipped and accessible.",
                    "Create simple access instructions.",
                    "Include refund/support and license reminders.",
                ),
            ),
            AgentStep(
                "09",
                "Tao upsell backend",
                "09_upsell_backend",
                "OTO/backend plan with upsell, downsell, agency license, and continuity ideas.",
                (
                    "Build backend offers from logical next steps.",
                    "Keep upsells complementary, not required for the front-end promise.",
                    "Add pricing and delivery notes.",
                ),
            ),
            AgentStep(
                "10",
                "Cai tien san pham",
                "10_product_improvement",
                "Feedback plan, update log, rebrand ideas, and version 2.0 roadmap.",
                (
                    "Collect buyer questions and failure points.",
                    "Turn support issues into updates.",
                    "Plan v2.0 with stronger assets and clearer positioning.",
                ),
            ),
        ),
    ),
    WorkflowAgent(
        id="jv_manager",
        name="JV MANAGER",
        role="Launch partner manager for affiliate recruitment, JV coordination, traffic pushes, and long-term relationships.",
        mission="Prepare and manage the affiliate/JV side of a launch from recruitment through post-launch follow-up.",
        input_root="input_files/agent_workflows/02_jv_manager",
        final_output="A launch partner system: prospect list, outreach, calendar, promo assets, support scripts, contest, and relationship tracker.",
        steps=(
            AgentStep(
                "01",
                "Tim affiliate doi tac",
                "01_affiliate_partner_research",
                "Affiliate and partner prospect list with contact notes, fit score, and priority.",
                (
                    "Find affiliates who already promote similar offers.",
                    "Segment by relationship strength and traffic source.",
                    "Avoid partners whose audience is a poor fit.",
                ),
            ),
            AgentStep(
                "02",
                "Outreach va ket noi",
                "02_outreach_relationship",
                "DM/email outreach sequence, follow-up scripts, and relationship notes.",
                (
                    "Personalize outreach by partner type.",
                    "Lead with why the offer fits their audience.",
                    "Track replies, objections, and next action.",
                ),
            ),
            AgentStep(
                "03",
                "Lap ke hoach launch",
                "03_launch_planning",
                "Launch calendar, timeline, pre-launch tasks, and responsibility checklist.",
                (
                    "Set dates for warmup, review access, cart open, and close.",
                    "Define daily tasks and promo pushes.",
                    "Prepare fallback actions for weak early traction.",
                ),
            ),
            AgentStep(
                "04",
                "Chuan bi promo materials",
                "04_promo_materials",
                "JV page, affiliate swipe, email swipes, banners, review access, and bonus details.",
                (
                    "Give affiliates ready-to-send copy.",
                    "Include angles for different list types.",
                    "Make review access and commission details easy to find.",
                ),
            ),
            AgentStep(
                "05",
                "Ho tro affiliate",
                "05_affiliate_support",
                "Support FAQ, reply scripts, bonus coordination, and performance updates.",
                (
                    "Answer affiliate questions quickly.",
                    "Share promo reminders without spamming.",
                    "Help affiliates choose the best angle for their audience.",
                ),
            ),
            AgentStep(
                "06",
                "Leaderboard va contest",
                "06_leaderboard_contest",
                "Contest rules, prizes, leaderboard tracking, and incentive notes.",
                (
                    "Define fair contest rules before launch.",
                    "Track top affiliates and milestone prizes.",
                    "Use incentives to increase promo frequency.",
                ),
            ),
            AgentStep(
                "07",
                "Quan ly traffic va promo",
                "07_traffic_promo_management",
                "Traffic plan, promo schedule, daily check-ins, and channel performance notes.",
                (
                    "Coordinate email, social, community, and paid/partner traffic.",
                    "Watch conversions and refund risk.",
                    "Shift emphasis toward angles that convert.",
                ),
            ),
            AgentStep(
                "08",
                "Sau launch",
                "08_post_launch",
                "Thank-you follow-up, payout notes, results recap, and relaunch ideas.",
                (
                    "Thank every serious affiliate.",
                    "Summarize numbers, lessons, and testimonials.",
                    "Plan the next promo window.",
                ),
            ),
            AgentStep(
                "09",
                "Quan ly network JV lau dai",
                "09_long_term_jv_network",
                "Long-term JV CRM, partner tiers, future launch notes, and relationship schedule.",
                (
                    "Keep partner notes current.",
                    "Tag affiliates by traffic quality and reliability.",
                    "Create a calendar for future collaborations.",
                ),
            ),
        ),
    ),
    WorkflowAgent(
        id="sale_page",
        name="SALE PAGE",
        role="Direct-response sales page agent for offer research, copy, page structure, funnel pages, and conversion testing.",
        mission="Turn offer notes and product assets into conversion-focused sales pages and funnel copy with realistic claims.",
        input_root="input_files/agent_workflows/03_sale_page",
        final_output="A complete front-end sales page plus funnel page copy, CTA map, FAQ, guarantee, and optimization checklist.",
        steps=(
            AgentStep(
                "01",
                "Nghien cuu offer va buyer",
                "01_offer_buyer_research",
                "Buyer research brief with pains, desires, objections, proof needs, and competing offers.",
                (
                    "Study buyer language and urgent problems.",
                    "Identify what the buyer already tried.",
                    "List objections that the page must answer.",
                ),
            ),
            AgentStep(
                "02",
                "Xay offer",
                "02_offer_building",
                "Offer stack with promise, mechanism, value proposition, price anchor, and risk reversal.",
                (
                    "Define what the buyer gets and why it matters.",
                    "Make the offer specific enough to visualize.",
                    "Keep promises useful but believable.",
                ),
            ),
            AgentStep(
                "03",
                "Headline va hook",
                "03_headline_hook",
                "Headline bank, subheadline options, opening hook, curiosity angle, and pain angle.",
                (
                    "Write multiple headline angles.",
                    "Match hook to buyer awareness level.",
                    "Avoid exaggerated results claims.",
                ),
            ),
            AgentStep(
                "04",
                "Viet sales copy",
                "04_sales_copy",
                "Full sales copy with problem, story, bullets, objection handling, and close.",
                (
                    "Translate features into practical buyer outcomes.",
                    "Use proof and specificity where available.",
                    "Remove hype that increases refund or compliance risk.",
                ),
            ),
            AgentStep(
                "05",
                "Trinh bay san pham",
                "05_product_presentation",
                "What-is-inside section, module breakdown, use cases, and who-it-is-for section.",
                (
                    "Show product components clearly.",
                    "Explain how each module helps the buyer.",
                    "Make product assets easy to understand before purchase.",
                ),
            ),
            AgentStep(
                "06",
                "Bonus stack",
                "06_bonus_stack",
                "Bonus section with bonus names, reasons, quick-win logic, and scarcity/urgency notes.",
                (
                    "Connect bonuses to objections or speed.",
                    "Avoid fake value math.",
                    "Use scarcity only when it is true.",
                ),
            ),
            AgentStep(
                "07",
                "Guarantee va FAQ",
                "07_guarantee_faq",
                "Refund policy, guarantee copy, FAQ, and objection removal section.",
                (
                    "Answer buying friction directly.",
                    "Keep refund terms clear.",
                    "Handle license, access, skill level, and time objections.",
                ),
            ),
            AgentStep(
                "08",
                "CTA va conversion elements",
                "08_cta_conversion_elements",
                "CTA copy, button labels, proof elements, countdown notes, trust elements, and page flow checklist.",
                (
                    "Place CTA after belief-building sections.",
                    "Use clear action language.",
                    "Add proof and trust where available.",
                ),
            ),
            AgentStep(
                "09",
                "Funnel pages",
                "09_funnel_pages",
                "Front-end, OTO, upsell, downsell, thank-you, and delivery page copy notes.",
                (
                    "Keep each page to one decision.",
                    "Make upsells logical next steps.",
                    "Confirm thank-you and access instructions are clear.",
                ),
            ),
            AgentStep(
                "10",
                "Toi uu va test",
                "10_optimization_testing",
                "Testing plan with headline tests, CTA tests, objections, heatmap notes, and conversion log.",
                (
                    "Test headline, offer stack, proof, price, and CTA.",
                    "Track conversion rate and refund signals.",
                    "Keep a changelog for each page version.",
                ),
            ),
        ),
    ),
)


def get_workflow_agents() -> tuple[WorkflowAgent, ...]:
    return AGENTS


def render_agent_overview() -> str:
    lines = [
        "# Product Launch Agent System",
        "",
        "This system splits the product launch workflow into three focused agents.",
        "Each agent has its own input folders, step outputs, and final deliverable.",
        "",
    ]
    for agent in AGENTS:
        lines.extend(_agent_summary_lines(agent))
        lines.append("")
    return "\n".join(lines)


def render_agent_playbook(agent: WorkflowAgent) -> str:
    lines = [
        f"# {agent.name} Agent",
        "",
        f"Role: {agent.role}",
        "",
        f"Mission: {agent.mission}",
        "",
        f"Input root: `{agent.input_root}`",
        "",
        f"Final output: {agent.final_output}",
        "",
        "## Operating Rules",
        "",
        "- Use the files in the matching step folder first.",
        "- If a step has no files yet, create a placeholder recommendation and mark assumptions clearly.",
        "- Keep claims realistic. Do not promise guaranteed income, traffic, rankings, or sales.",
        "- Check license rights before reusing PLR/MRR/RR content.",
        "- Transform source material into a new angle, structure, or asset instead of copying it unchanged.",
        "",
        "## Workflow",
        "",
    ]
    for step in agent.steps:
        lines.extend(
            [
                f"### {step.id}. {step.name}",
                "",
                f"Folder: `{agent.input_root}/{step.folder}`",
                "",
                f"Output: {step.output}",
                "",
                "Checklist:",
                "",
            ]
        )
        lines.extend(f"- {item}" for item in step.checklist)
        lines.append("")
    return "\n".join(lines)


def export_agent_workspace() -> Path:
    agents_dir = ROOT_DIR / "agents"
    workspace_dir = ROOT_DIR / "input_files" / "agent_workflows"
    agents_dir.mkdir(parents=True, exist_ok=True)
    workspace_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "created_at": datetime.now().strftime("%Y%m%d-%H%M%S"),
        "agents": [_agent_to_manifest(agent) for agent in AGENTS],
    }
    (agents_dir / "00_agent_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (agents_dir / "README.md").write_text(render_agent_overview(), encoding="utf-8")

    for index, agent in enumerate(AGENTS, start=1):
        agent_file = agents_dir / f"{index:02d}_{agent.id}_agent.md"
        agent_file.write_text(render_agent_playbook(agent), encoding="utf-8")
        agent_root = ROOT_DIR / agent.input_root
        agent_root.mkdir(parents=True, exist_ok=True)
        (agent_root / "_inbox").mkdir(parents=True, exist_ok=True)
        for step in agent.steps:
            (agent_root / step.folder).mkdir(parents=True, exist_ok=True)

    (workspace_dir / "README.md").write_text(_workspace_readme(), encoding="utf-8")
    return agents_dir


def export_agent_overview_report() -> Path:
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    path = EXPORTS_DIR / f"product-launch-agent-system-{stamp}.md"
    path.write_text(render_agent_overview(), encoding="utf-8")
    return path


def _agent_summary_lines(agent: WorkflowAgent) -> list[str]:
    lines = [
        f"## {agent.name}",
        "",
        f"- Role: {agent.role}",
        f"- Mission: {agent.mission}",
        f"- Input root: `{agent.input_root}`",
        f"- Final output: {agent.final_output}",
        "",
        "Steps:",
        "",
    ]
    lines.extend(f"{step.id}. {step.name} -> `{step.folder}`" for step in agent.steps)
    return lines


def _agent_to_manifest(agent: WorkflowAgent) -> dict:
    data = asdict(agent)
    data["steps"] = [asdict(step) for step in agent.steps]
    return data


def _workspace_readme() -> str:
    lines = [
        "# Agent Workflow Inputs",
        "",
        "Drop source files into the matching agent and step folder.",
        "Use `_inbox` when you are not sure where a file belongs yet.",
        "",
    ]
    for agent in AGENTS:
        lines.append(f"## {agent.name}")
        lines.append("")
        lines.append(f"Root: `{agent.input_root}`")
        lines.append("")
        for step in agent.steps:
            lines.append(f"- `{step.id}_{step.folder}`: {step.name}")
        lines.append("")
    return "\n".join(lines)

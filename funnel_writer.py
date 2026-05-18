from __future__ import annotations

from offer_builder import build_product_outline, create_bonus_stack, create_launch_assets
from saas_planner import create_saas_plan
from sales_page_writer import write_sales_page


def build_offer_funnel(idea_context: str) -> dict[str, str]:
    return {
        "01-product-outline.md": build_product_outline(idea_context),
        "02-bonus-stack.md": create_bonus_stack(idea_context),
        "03-sales-page.md": write_sales_page(idea_context),
        "04-launch-assets.md": create_launch_assets(idea_context),
        "05-saas-plan.md": create_saas_plan(idea_context),
        "06-funnel-map.md": _funnel_map(idea_context),
    }


def _funnel_map(idea_context: str) -> str:
    return f"""# Funnel Map

## Front-End
AI PLR Rebrand Kit - $17

Promise: Turn existing PLR into a fresh product offer with outline, bonuses, sales page, and launch assets.

## OTO 1
Advanced PLR Funnel Builder - $37

Includes deeper prompt workflows, more templates, and done-for-you funnel structures.

## OTO 2
Agency / Whitelabel License - $67-$197

Allows buyers to use the templates and workflows for clients or internal agency projects.

## OTO 3
Monthly PLR Idea Club - $19/month

Monthly product ideas, prompt packs, sales page templates, and niche research reports.

## SaaS Upsell Later
PLR Rebrand Engine - $19-$49/month

Upload PLR -> Analyze -> Generate Ideas -> Build Offer -> Export Pack.

## Traffic Angles
- WarriorPlus affiliate launch
- YouTube demo showing one PLR file turned into an offer
- Facebook group posts for PLR buyers and digital product sellers
- Email list campaign around "dusty PLR to fresh offer"

## Source Context
{idea_context}
"""

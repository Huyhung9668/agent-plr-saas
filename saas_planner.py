from __future__ import annotations

from llm_client import create_saas_plan_with_llm, has_api_key


def create_saas_plan(idea_context: str, use_ai: bool = True) -> str:
    if use_ai and has_api_key():
        return create_saas_plan_with_llm(idea_context)
    return f"""# Micro SaaS Plan

## SaaS Product Name
PLR Rebrand Engine

## Target User
PLR buyers, affiliate marketers, WarriorPlus vendors, Gumroad sellers, and digital product creators who own content assets but do not know how to turn them into a fresh offer.

## Core Workflow
Upload or paste PLR details -> analyze niche/license/risk -> generate new product angles -> build offer pack -> export sales assets.

## MVP Features
- Upload TXT, PDF, DOCX, or ZIP
- Detect niche, format, license clues, and risk
- Score Demand, WarriorPlus Fit, Rebrand Potential, SaaS Potential, Ease, and Risk
- Generate 10 product ideas
- Build outline, bonus stack, sales page, launch emails, and FAQ
- Export Markdown/CSV/product pack folder

## User Input
- PLR file or product title
- Target marketplace
- Preferred niche
- Desired product format
- Pricing range

## App Output
- PLR analysis report
- New product idea list
- Product outline
- Sales page draft
- Bonus stack
- Launch emails and social posts
- SaaS/membership upsell angle

## Pricing Tiers
- Basic: $19/month for 20 analyses/month
- Pro: $49/month for 100 analyses/month and full funnel generation
- Agency: $97/month for client reports and whitelabel exports

## Lifetime Deal
$47-$97 one-time for early adopters with limited credits.

## Agency/Whitelabel Option
$197-$297 for whitelabel reports, client mode, and commercial usage rights.

## 14-Day MVP Build Plan
1. Lock one workflow: upload PLR -> export offer pack.
2. Add file reader and scanner.
3. Add analysis scoring.
4. Add idea generator.
5. Add product outline builder.
6. Add sales page and bonus writer.
7. Add export pack folder.
8. Add simple Streamlit UI.
9. Add SQLite history.
10. Add user settings.
11. Test with 20 PLR files.
12. Create demo video.
13. Prepare WarriorPlus/Gumroad offer.
14. Launch beta.

## Sell First As Digital Product
Before coding the full SaaS, sell "AI PLR Rebrand Kit" with prompts, checklist, templates, and a 7-day launch workflow.

## Risks And Validation
- Risk: users expect magic from poor PLR. Fix with clear examples and limits.
- Risk: unclear licenses. Add license/risk audit and disclaimers.
- Risk: overbuilding. Validate with a $17-$47 digital product first.

## Source Context
{idea_context}
"""

from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

from brain import search_brain
from config import EXPORTS_DIR

PRODUCT_NAME = "AI PLR Rebrand Kit"


def build_warriorplus_launch_plan(query: str = "AI PLR Rebrand Kit PLR SaaS WarriorPlus") -> str:
    brain_context = _brain_context(query)
    return f"""# WarriorPlus Launch Plan: {PRODUCT_NAME}

## Positioning

**Core offer:** Turn old PLR into a fresh digital product with a sales page, bonus stack, email swipes, and launch funnel in 7 days using AI.

This offer is built for WarriorPlus because it combines:

- AI
- PLR
- Digital product creation
- Fast launch workflow
- Funnel and affiliate assets

Do not position it as generic PLR. Position it as a practical rebrand-and-launch system.

## Front-End

- Product: {PRODUCT_NAME}
- Price: $9.95 to $17
- Commission: 50% to 75%
- Goal: buyer list, proof, feedback, affiliate interest

## OTO 1

- Name: Advanced PLR Funnel Pack
- Price: $27 to $37
- Includes: 100 advanced prompts, 10 sales page templates, 10 funnel maps, 20 bonus ideas, 20 product name templates, 10 WarriorPlus listing templates
- Commission: 40% to 50%

## OTO 2

- Name: Agency / Whitelabel License
- Price: $47 to $67
- Includes: client report rights, freelancer usage, agency delivery checklist, proposal template
- Restriction: buyers cannot resell the original product unchanged

## Later Backend

- Name: PLR Idea Club
- Price: $19/month
- Includes: monthly PLR ideas, sales angles, prompt packs, funnel maps, bonus packs

## Product ZIP Structure

```txt
AI-PLR-Rebrand-Kit/
├── 01-Start-Here.md
├── 02-7-Day-PLR-Rebrand-Blueprint.md
├── 03-PLR-Evaluation-Checklist.md
├── 04-50-AI-PLR-Rebrand-Prompts.md
├── 05-Sale-Page-Template.md
├── 06-WarriorPlus-Launch-Checklist.md
├── 07-Email-Swipe-Pack.md
├── 08-Bonus-Stack-Generator.md
├── 09-PLR-Score-Calculator.csv
├── 10-JV-Affiliate-Page.md
└── README.txt
```

## 7-Day Build Plan

1. Research 20 WarriorPlus products and 20 PLR/SaaS threads.
2. Create the PDF guide outline, checklist outline, prompt pack outline, and bonus list.
3. Write the 7-Day Blueprint, 50 prompts, and PLR Evaluation Checklist.
4. Create the sales page template, email swipe pack, bonus stack generator, and launch checklist.
5. Write the sales page and create a simple mockup.
6. Setup WarriorPlus product, delivery page, affiliate terms, and refund policy.
7. Launch test, ask for feedback, and improve the sales page.

## Compliance

- Do not promise income.
- Do not tell buyers to copy raw PLR unchanged.
- Always tell buyers to check license rights before resale.
- Use realistic claims: saves time, gives structure, helps create an offer faster.

## Source Brain Context

{brain_context}
"""


def export_ai_plr_rebrand_kit(query: str = "PLR rebrand WarriorPlus AI digital product") -> Path:
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    pack_dir = EXPORTS_DIR / f"AI-PLR-Rebrand-Kit-WarriorPlus-{stamp}"
    pack_dir.mkdir(parents=True, exist_ok=True)

    files = {
        "01-Start-Here.md": _start_here(),
        "02-7-Day-PLR-Rebrand-Blueprint.md": _blueprint(),
        "03-PLR-Evaluation-Checklist.md": _evaluation_checklist(),
        "04-50-AI-PLR-Rebrand-Prompts.md": _prompt_pack(),
        "05-Sale-Page-Template.md": _sales_page_template(),
        "06-WarriorPlus-Launch-Checklist.md": _launch_checklist(),
        "07-Email-Swipe-Pack.md": _email_swipes(),
        "08-Bonus-Stack-Generator.md": _bonus_stack_generator(),
        "10-JV-Affiliate-Page.md": _jv_page(),
        "11-SaaS-Upgrade-Roadmap.md": _saas_upgrade_roadmap(),
        "README.txt": "Start with 01-Start-Here.md. Check all PLR source licenses before resale or redistribution.",
    }
    for filename, content in files.items():
        (pack_dir / filename).write_text(content, encoding="utf-8")
    _write_score_calculator(pack_dir / "09-PLR-Score-Calculator.csv")
    (pack_dir / "00-WarriorPlus-Launch-Plan.md").write_text(build_warriorplus_launch_plan(query), encoding="utf-8")
    return pack_dir


def _brain_context(query: str, limit: int = 8) -> str:
    results = search_brain(query, limit=limit)
    if not results:
        return "No strong brain context found. Use the fixed WarriorPlus strategy."
    blocks = []
    for index, item in enumerate(results, start=1):
        blocks.append(
            f"""### Brain Match {index}: {item['title']}
Source: {item['source_path']}

{item['text'][:1200].strip()}
"""
        )
    return "\n".join(blocks)


def _start_here() -> str:
    return f"""# Start Here

Welcome to {PRODUCT_NAME}.

Use this kit to evaluate an old PLR asset, create a new buyer-specific angle, build a fresh product stack, and prepare a simple WarriorPlus launch.

Best path:

1. Choose one PLR asset.
2. Check the license.
3. Score the asset.
4. Pick a new buyer and promise.
5. Create the guide, checklist, prompts, bonuses, and sales page.
6. Launch a small test offer.

This kit does not guarantee income. It gives you a practical creation and launch workflow.
"""


def _blueprint() -> str:
    return """# 7-Day AI PLR Rebrand Blueprint

## Day 1: Pick And Audit
- Choose one PLR asset.
- Find the license file.
- Identify niche, buyer, age, and risk.
- Reject assets with unclear or restrictive rights.

## Day 2: Reposition
- Choose a narrower buyer.
- Write a new promise.
- Replace generic claims with a specific workflow.
- Rename the product.

## Day 3: Build Core Content
- Rewrite the main lesson flow.
- Add current AI workflows.
- Add examples, checklists, and templates.

## Day 4: Add Offer Assets
- Build bonus stack.
- Create worksheets.
- Create prompt pack.
- Create implementation checklist.

## Day 5: Write Sales Page
- Headline.
- Subheadline.
- Problem.
- Solution.
- What's inside.
- Bonuses.
- FAQ.
- CTA.

## Day 6: Prepare WarriorPlus
- Product zip.
- Delivery page.
- Refund policy.
- Affiliate swipe.
- JV page.

## Day 7: Launch Test
- Send to small affiliates.
- Post to relevant audiences.
- Collect feedback.
- Improve headline and offer.
"""


def _evaluation_checklist() -> str:
    return """# PLR Evaluation Checklist

- License file exists.
- License allows intended use.
- Topic has buyer intent.
- Content is not dangerously outdated.
- Can be narrowed to a specific buyer.
- Can be modernized with AI workflows.
- Can become templates/checklists/prompts.
- Has WarriorPlus appeal.
- Can be finished in 7 days.
- Risk is manageable.
"""


def _prompt_pack() -> str:
    sections = {
        "PLR Analysis": ["Summarize this PLR asset", "Identify the buyer", "Find weak points", "Find fresh angles", "Score license risk"],
        "Rebrand": ["Create product names", "Create a core promise", "Create USP options", "Build product outline", "Create bonus ideas"],
        "Sales Page": ["Write headlines", "Write bullets", "Write FAQ", "Write guarantee", "Write CTA"],
        "Funnel": ["Create OTO ideas", "Create backend offer", "Create membership idea", "Create agency license", "Create affiliate swipe"],
    }
    lines = ["# 50 AI PLR Rebrand Prompts", ""]
    count = 1
    while count <= 50:
        for group, prompts in sections.items():
            for prompt in prompts:
                if count > 50:
                    break
                lines.append(f"## Prompt {count}: {prompt}")
                lines.append("")
                lines.append(f"Act as a PLR product strategist. Task: {prompt}. Input: [paste PLR notes]. Constraints: avoid income guarantees, check license risk, transform rather than copy. Output: actionable Markdown.")
                lines.append("")
                count += 1
    return "\n".join(lines)


def _sales_page_template() -> str:
    return """# Sales Page Template

## Headline
Turn Old PLR Into Fresh Digital Products You Can Launch In 7 Days Using AI

## Subheadline
A step-by-step kit that helps you evaluate, rebrand, package, and launch PLR-based digital products without starting from scratch.

## Problem
[Describe unused PLR, unclear positioning, weak offers, and launch confusion.]

## Solution
[Introduce the kit as prompts, templates, checklists, and launch assets.]

## What's Inside
[List guide, checklist, prompts, calculator, sales template, swipes.]

## Bonuses
[List 5-8 practical bonuses.]

## FAQ
[Answer license, time, skills, refund, and results questions.]

## CTA
Get Instant Access To AI PLR Rebrand Kit Today
"""


def _launch_checklist() -> str:
    return """# WarriorPlus Launch Checklist

- Product zip prepared.
- Download page prepared.
- Sales page written.
- Product mockup created.
- Refund policy added.
- Support email ready.
- WarriorPlus product created.
- Price and commission set.
- Affiliate page ready.
- Email swipes ready.
- Bonus ideas ready.
- Test purchase completed.
"""


def _email_swipes() -> str:
    return """# Email Swipe Pack

## Pre-Launch Email 1
Subject: Got old PLR sitting unused?

Many creators own PLR but never turn it into a focused offer. This kit shows a simple 7-day workflow to evaluate, rebrand, package, and launch a fresh product.

## Launch Email
Subject: AI PLR Rebrand Kit is live

AI PLR Rebrand Kit gives you prompts, templates, checklists, and launch assets for turning old PLR into a new digital product offer.

## Follow-Up Email
Subject: The fastest product may be hidden in assets you already own

Instead of starting from zero, use existing PLR as raw material, then add a new angle, buyer, templates, and funnel.
"""


def _bonus_stack_generator() -> str:
    return """# Bonus Stack Generator

Use these bonus types:

- Product name generator.
- Buyer avatar worksheet.
- Headline template pack.
- OTO planner.
- License check checklist.
- Affiliate swipe template.
- 7-day action plan.
- Launch setup checklist.
"""


def _jv_page() -> str:
    return """# JV / Affiliate Page

## Product
AI PLR Rebrand Kit

## Audience
PLR buyers, affiliate marketers, beginner product creators, AI prompt users, WarriorPlus vendors.

## Price
Front-end: $9.95 to $17

## Commission
50% to 75% front-end.

## Affiliate Angle
Help your audience turn unused PLR into a fresh digital product offer with prompts, templates, and launch assets.

## Compliance
No income guarantees. Buyers must check PLR licenses before resale.
"""


def _saas_upgrade_roadmap() -> str:
    return """# SaaS Upgrade Roadmap

## Digital Product First
Sell AI PLR Rebrand Kit as a downloadable product.

## Internal Agent
Use the local agent to analyze PLR, generate ideas, create sales pages, and export packs.

## Micro SaaS MVP
Build PLR Rebrand Engine:

- Upload PLR notes or documents.
- Analyze niche and license clues.
- Score WarriorPlus fit.
- Generate product angles.
- Create offer, sales page, funnel, and email swipes.
- Export product pack.

## Membership
Launch PLR Product Club with monthly ideas, prompts, funnel maps, and bonus packs.
"""


def _write_score_calculator(path: Path) -> None:
    rows = [
        ["Product Name", "Niche", "License", "Demand Score", "WarriorPlus Fit", "Rebrand Potential", "SaaS Potential", "Ease Score", "Risk Score", "Final Score", "Recommended Angle"],
        ["Example PLR Asset", "AI Marketing", "PLR", "8", "9", "8", "7", "8", "3", "=D2*0.25+E2*0.25+F2*0.2+G2*0.15+H2*0.1-I2*0.05", "AI PLR Rebrand Kit"],
    ]
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(rows)

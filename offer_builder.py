from __future__ import annotations

from llm_client import (
    build_outline_with_llm,
    create_bonus_stack_with_llm,
    create_launch_assets_with_llm,
    has_api_key,
)


def build_product_outline(idea_context: str, use_ai: bool = True) -> str:
    if use_ai and has_api_key():
        return build_outline_with_llm(idea_context)
    return f"""# Product Outline

## Product Name
AI Product Sprint Kit

## Buyer Avatar
Beginner digital product seller who wants to turn PLR into a focused offer without starting from zero.

## Core Promise
Create a simple, realistic digital product offer in 7 days using PLR as the raw material and AI as the production assistant.

## Format
PDF guide, prompt pack, checklist, templates, and email swipes.

## Modules
1. Pick the best PLR asset and check the license.
2. Choose a buyer and narrow the promise.
3. Rewrite the core content with a fresh angle.
4. Create prompts, checklists, and templates.
5. Build the bonus stack.
6. Write the sales page and launch emails.
7. Publish and test the offer.

## Assets To Create
- 7-day checklist
- Product idea generator
- Sales page template
- Bonus planner
- 10 launch email swipes

## What To Rewrite
Rewrite generic PLR claims, outdated tactics, income promises, and broad advice.

## New Value To Add
Add current AI workflows, examples, templates, checklists, realistic implementation steps, and compliance notes.

## Source Context
{idea_context}
"""


def create_bonus_stack(idea_context: str, use_ai: bool = True) -> str:
    if use_ai and has_api_key():
        return create_bonus_stack_with_llm(idea_context)
    return f"""# Bonus Stack

1. 7-Day Product Sprint Checklist - PDF checklist - Helps buyers act fast - Easy - $17
2. 50 AI Product Prompts - Prompt pack - Removes blank-page friction - Easy - $27
3. Sales Page Template - Doc template - Speeds up launch - Medium - $27
4. 10 Email Swipes - Swipe file - Helps with promotion - Medium - $37
5. Bonus Builder Worksheet - Worksheet - Helps stack value - Easy - $17
6. WarriorPlus Launch Checklist - PDF checklist - Helps avoid missing setup steps - Easy - $17
7. Product Name Generator - Prompt/template - Helps positioning - Easy - $17
8. Buyer Avatar Worksheet - Worksheet - Clarifies audience - Easy - $17
9. OTO Planner - Worksheet - Helps backend planning - Medium - $27
10. Compliance Claim Checker - Checklist - Reduces risky copy - Medium - $27

Source context:
{idea_context}
"""


def create_launch_assets(idea_context: str, use_ai: bool = True) -> str:
    if use_ai and has_api_key():
        return create_launch_assets_with_llm(idea_context)
    return f"""# Launch Assets

## WarriorPlus Listing Title
AI Product Sprint Kit: Turn PLR Into A Simple Digital Product Offer In 7 Days

## Short Description
A practical toolkit for beginners who want to transform existing PLR into a focused product offer with templates, prompts, bonuses, and launch assets.

## Affiliate Email
Subject: New toolkit helps beginners turn PLR into a real offer

Hi,

This new toolkit shows beginners how to take existing PLR, choose a fresh angle, add useful assets, and package it into a simple digital product offer. It includes prompts, checklists, templates, bonus ideas, and launch assets.

No hype, no guaranteed income claims, just a practical 7-day product creation workflow.

## Buyer Email
Subject: Your AI Product Sprint Kit access

Thanks for joining. Start with the 7-day checklist, then use the prompt pack and sales page template to build your first version.

## Social Posts
1. Got PLR collecting dust? Turn it into a focused offer with a 7-day build plan.
2. The fastest product idea is often hidden inside assets you already own.
3. Rebrand, rewrite, add bonuses, launch. That is the simple PLR upgrade path.
4. AI can help you turn rough PLR into prompts, checklists, templates, and email swipes.
5. Do not sell generic PLR unchanged. Package a better offer.

## JV Page Bullets
- Beginner-friendly
- Practical 7-day workflow
- Includes templates and prompts
- Realistic claims
- Works for AI, marketing, productivity, and planner niches

## FAQ
**Can buyers resell the PLR directly?** They should follow the license of the source files.

**Is income guaranteed?** No. The product teaches a workflow, not guaranteed results.

## Refund Policy
30-day refund policy for buyers who review the material and decide it is not a fit.

## Compliance Notes
Avoid exaggerated income claims. Check license rights before selling. Add original value before publishing.

Source context:
{idea_context}
"""

from __future__ import annotations

from llm_client import has_api_key, write_sales_page_with_llm


def write_sales_page(idea_context: str, use_ai: bool = True) -> str:
    if use_ai and has_api_key():
        return write_sales_page_with_llm(idea_context)
    return f"""# Sales Page Draft

## Headline
Turn Your PLR Into A Sellable Digital Product In 7 Days

## Subheadline
A practical starter kit for creators who want a clear offer, simple assets, and a realistic launch plan.

## The Problem
Most PLR sits unused because it is generic, old, or hard to position. The fix is not copying it. The fix is turning it into a focused offer with a new angle, useful bonuses, and a buyer-specific promise.

## The Offer
{idea_context}

## What Is Inside
- PDF implementation guide
- 7-day action checklist
- Prompt pack
- Sales page template
- Email swipe pack
- Bonus stack planner

## Who It Is For
Beginners, affiliate marketers, and digital product sellers who want to create a simple product without starting from a blank page.

## Bonuses
- 30 headline templates
- 10 launch email swipes
- WarriorPlus launch checklist

## FAQ
**Do I need coding?** No.

**Can I copy the PLR directly?** Check the license first. Best practice is to rebrand and add new value.

**How long does it take?** The plan is designed for 7 days.

## Refund Policy
30-day refund policy for customers who try the material and feel it is not a fit.

## Call To Action
Start building your new digital product today.
"""

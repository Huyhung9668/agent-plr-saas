from __future__ import annotations

import json

from llm_client import generate_ideas_with_llm, has_api_key


def generate_new_product_ideas(analyses: list[dict], count: int = 10, use_ai: bool = True) -> str:
    top_items = sorted(analyses, key=lambda item: item.get("final_score", 0), reverse=True)[:5]
    context = json.dumps(top_items, ensure_ascii=False, indent=2)
    if use_ai and has_api_key():
        return generate_ideas_with_llm(context, count=count)
    return _heuristic_ideas(top_items, count)


def _heuristic_ideas(items: list[dict], count: int) -> str:
    ideas = []
    seeds = items or [{"category": "AI / Make Money", "best_angle": "AI product sprint"}]
    for index in range(count):
        seed = seeds[index % len(seeds)]
        category = seed.get("category", "Digital Product")
        name = _name_for(category, index + 1)
        ideas.append(
            f"""## Idea {index + 1}: {name}

- Product name: {name}
- Buyer: {seed.get("buyer_avatar", "Nguoi moi muon tao san pham so nhanh.")}
- Promise: {seed.get("promise", "Bien PLR thanh offer moi trong 7 ngay.")}
- What is inside: PDF guide, checklist, prompt pack, sales page template, email swipes
- Bonuses: headline templates, launch checklist, product idea generator
- Front-end price: $17
- OTO1: $47 Done-for-you bundle builder
- OTO2: $97 Agency/commercial license pack
- Sales page angle: {seed.get("sales_page_angle", "Turn existing assets into a sellable offer.")}
- 7-day build plan: Day 1 pick niche, Day 2 rewrite offer, Day 3 create assets, Day 4 bonuses, Day 5 sales page, Day 6 emails, Day 7 publish.
"""
        )
    return "\n".join(ideas)


def _name_for(category: str, number: int) -> str:
    names = {
        "AI / Make Money": "AI Product Sprint Kit",
        "Marketing": "Affiliate Launch Asset Kit",
        "Planner": "Digital Planner Profit Pack",
        "Etsy": "Etsy Download Starter Kit",
        "Self Help": "7-Day Productivity Reset Kit",
        "Health": "Wellness Content Starter Pack",
        "Kids Story": "Storybook Creator Kit",
        "Business": "Micro Business Launch Kit",
    }
    base = names.get(category, "Digital Product Starter Kit")
    return base if number == 1 else f"{base} #{number}"

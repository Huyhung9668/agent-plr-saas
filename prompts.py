from pathlib import Path


def _load_prompt_file(name: str, fallback: str) -> str:
    path = Path(__file__).resolve().parent / "prompts" / name
    if path.exists():
        return path.read_text(encoding="utf-8").strip()
    return fallback.strip()


SYSTEM_PROMPT = _load_prompt_file(
    "system_prompt_200_lines.txt",
    """
You are a PLR Product Strategist Agent specializing in analyzing PLR/MRR/RR assets
and turning them into practical new digital product offers for WarriorPlus, JVZoo,
Gumroad, or Payhip.

Never recommend copying original content when the license is unclear.
Always transform PLR into a new offer with fresh positioning, useful bonuses,
realistic claims, and a clear build plan.
""",
)

ANALYSIS_PROMPT = """
Analyze this PLR/MRR/RR product and return valid JSON only.

Required JSON schema:
{
  "original_title": "",
  "category": "",
  "product_type": "",
  "license_type": "",
  "freshness_score": 1,
  "demand_score": 1,
  "warriorplus_fit_score": 1,
  "rebrand_potential_score": 1,
  "saas_potential_score": 1,
  "ease_of_creation_score": 1,
  "backend_potential_score": 1,
  "risk_score": 1,
  "final_score": 1.0,
  "best_angle": "",
  "buyer_avatar": "",
  "promise": "",
  "recommended_action": "",
  "risk": "",
  "bonus_ideas": [],
  "oto_ideas": [],
  "sales_page_angle": "",
  "traffic_angle": "",
  "notes": ""
}

Scoring formula:
Final Score =
Demand * 0.25
+ WarriorPlus Fit * 0.25
+ Rebrand Potential * 0.20
+ SaaS Potential * 0.15
+ Ease of Creation * 0.10
- Risk * 0.05

Product information:
{product_context}
"""

IDEA_PROMPT = """
Generate {count} new product ideas from the PLR analysis below.

Return Markdown. Each idea must include:
- Product name
- Buyer
- Promise
- What is inside
- Bonuses
- Front-end price
- OTO1
- OTO2
- Sales page angle
- 7-day build plan

PLR analysis:
{analysis_context}
"""

SALES_PAGE_PROMPT = """
Write a practical sales page for the product idea below.

Keep claims realistic. Avoid guaranteed income promises.
Include:
- headline
- subheadline
- problem
- offer
- what is inside
- bonuses
- who it is for
- price anchor
- FAQ
- refund policy
- call to action

Product idea:
{idea_context}
"""

OUTLINE_PROMPT = """
Build a practical product outline from this PLR analysis or product idea.

Return Markdown with:
- Product name
- Buyer avatar
- Core promise
- Product format
- Module outline
- Worksheets/templates/checklists needed
- 7-day creation plan
- What to rewrite from the PLR
- What new value to add

Context:
{idea_context}
"""

BONUS_STACK_PROMPT = """
Create a bonus stack for this product idea.

Return Markdown with 8-12 bonuses. For each bonus include:
- Bonus name
- Format
- Why buyers want it
- How hard it is to create
- Suggested value

Avoid fake inflated value claims.

Context:
{idea_context}
"""

LAUNCH_ASSETS_PROMPT = """
Create launch assets for this product idea.

Return Markdown with:
- WarriorPlus listing title
- Short product description
- Affiliate email
- Buyer email
- 5 social posts
- JV page bullet points
- FAQ
- Refund policy
- Compliance notes

Keep claims realistic and avoid guaranteed income promises.

Context:
{idea_context}
"""

SAAS_PLAN_PROMPT = """
Create a practical micro SaaS plan from this PLR analysis or product idea.

Return Markdown with:
- SaaS product name
- Target user
- Core workflow
- MVP features
- What the user uploads or enters
- What the app generates
- Pricing tiers
- Lifetime deal option
- Agency/whitelabel option
- 14-day MVP build plan
- What to sell first as a digital product before building SaaS
- Risks and validation steps

Keep the plan small, realistic, and buildable by a solo founder.

Context:
{idea_context}
"""

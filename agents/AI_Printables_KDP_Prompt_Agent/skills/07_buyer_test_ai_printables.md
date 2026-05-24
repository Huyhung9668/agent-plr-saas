# Buyer Test AI Printables

## Tags
#ai-printables
#kdp
#plr
#warriorplus
#prompt-pack
#canva-printable
#coloring-book
#journal
#kids-worksheet
#etsy-printable
#buyer-test

## Purpose
Simulate buyer experience for a $17?$27 product pack.

## When To Use
Use for test nh? buyer, ??ng ti?n kh?ng, ng??i mua c? hi?u kh?ng.

## Input Needed
User request, matched tag/intent, relevant product/niche details, and brain evidence. For evidence-based analysis, require DATA USED from brain/source map.

## Brain To Load
- brain/AI_PRINTABLES_KDP_BRAIN.json
- brain/AI_PRINTABLES_KDP_BRAIN.md
- brain/QUALITY_RULES.md
- quality_gates/PRODUCT_QUALITY_GATE.md

## Data Source
Default data source:
G:\Documents\warriorplus MMO\Agent PLR Saas\input_files\AI Printables KDP Promt Skill

Do not forget recovered folder:
G:\Documents\warriorplus MMO\Agent PLR Saas\input_files\AI Printables KDP Promt Skill\_RECOVERED_3500_20260522

For fast responses, load brain first. If answer requires proof beyond brain, inspect source map and then source files. If exact evidence is missing, write UNKNOWN; do not invent.

## Steps
- Load the listed Brain To Load files.
- Identify whether the answer is source evidence or inference.
- Include DATA USED for research/audit tasks.
- Follow the required Output Format exactly.
- Apply Quality Rules and Failure Conditions before final answer.
- End with Next Action.

## Output Format
BUYER TEST REPORT
- Buyer profile:
- Price paid:
- First impression:
- Open first file?:
- First output in 10 minutes?:
- Stuck points:
- Valuable parts:
- Generic parts:
- Would refund?:
- Score:
- Fix required:
- Next Action:

## Quality Rules
- No Start Here => FAIL.
- Score below 8 => not launch ready.

## Failure Conditions
- FAIL if required file evidence is claimed but no DATA USED is listed.
- FAIL if unsupported sales numbers, prices, license rights, or platform results are invented.
- FAIL if output marks PASS for assets that were not actually created or tested.

## Auto-Update Rule
If user says "next time do it this way", "missing this part", "this is wrong", "fix l?i", "score more strictly", or "do not do it this way again":
1. Identify the related skill.
2. Patch this markdown file.
3. Increase Version.
4. Write to skills/_changelog.md.
5. Write to skills/_usage_log.md.
6. Write to memory/user_feedback_log.md.
If the same issue happens twice, update the skill before answering again.

## Example Trigger
#ai-printables #kdp #buyer-test Run Buyer Test AI Printables for this product or niche.

## Version
v1.0

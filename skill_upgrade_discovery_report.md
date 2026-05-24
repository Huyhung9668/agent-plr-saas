# Skill Upgrade Discovery Report

## Files Found
- `web_app.py`
- `web_ui/app.js`
- `product_pipeline.py`
- `tests/`
- `exports/products/`
- `skills/`

## Existing Routes
- Existing product pipeline already contains Step 1–24, Phase 5 real AI, Step 34/35 real AI, and generic AI handler.

## Existing Skills
- Legacy skill markdown files existed in `skills/`; new 44-step skill files and `_index.json` were added.

## Broken / Hard-Coded Product Text
- `web_app.py` still contains legacy literal `AI Etsy Printable Bundle Builder` in older deterministic builders; runtime guards should replace/avoid it for active products.
- `web_ui/app.js` vendor-ready prompt already uses `Product: {{ACTIVE_PRODUCT_NAME}}`.

## Old Product Leak Risks
- Any deterministic builder that returns static product text can leak old product unless routed through hybrid/AI path or sanitized.

## Current Test Gaps
- Full browser API timing and AI provider reliability are not fully covered by unit tests.

## Recommended Code Changes
- Keep Step 1–44 explicit router as source of truth.
- Prefer skill metadata from `skills/_index.json` for future backend execution.
- Continue shrinking legacy hard-coded builders after tests stabilize.

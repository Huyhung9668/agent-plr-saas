# UI Hotfix v1.13-prompt-clean.3

## Fixed
- Added a prominent `10 ý tưởng` quick prompt for AI Printables/KDP ideation.
- Quick prompt selection now switches simple idea/test prompts to FAST mode automatically.
- Composer height reduced so prompt/tags no longer dominate the screen.
- Quick prompts wrap cleanly instead of horizontal overlap/scroll clutter.
- Selected tags are smaller and limited to one compact row.
- Fixed visible input placeholder and send button text in `index.html`.
- Bumped app/cache version to `v1.13-prompt-clean.3`.

## Verified
- `node --check web_ui/app.js`: PASS
- `python -m py_compile web_app.py`: PASS
- `GET /api/status`: PASS, appVersion `v1.13-prompt-clean.3`
- `POST /api/route_skill #ai-printables-kdp-prompt #market-pattern`: PASS before restart; route maps to `skills/01_market_pattern_ai_printables.md`.

## User note
- Refresh browser with Ctrl+F5 to load `/styles.css?v=1.13-prompt-clean.3` and `/app.js?v=1.13-prompt-clean.3`.

# WEB UI CLEAN UI V113 REPORT

## Files changed
- `VERSION` -> `v1.13-clean-ui`
- `web_ui/index.html` -> cache query updated, topbar actions moved into More menu
- `web_ui/app.js` -> More menu, prompt drawer behavior, Advanced panel, Proof Mode, grouped AI KDP tags
- `web_ui/styles.css` -> clean UI overrides, drawer, grouped tags, hover-only icons, responsive cleanup
- `web_app.py` -> `/api/skill_tags` returns all 27 AI KDP tags with fixed Vietnamese descriptions

## UI changes
- Topbar is cleaner: keeps model/tool controls and one `⋯` More menu.
- Prompt library is now a drawer by default instead of occupying composer height.
- AI Printables KDP tags are collapsed by default and grouped only when `Show tags` is clicked.
- Composer keeps textarea central with selected tags in a compact row.
- Advanced panel is collapsed by default and contains prompt library, full tags, status/router, export, and Proof Mode.

## Removed / hidden clutter
- Copy/download/close style controls are set to hover-only in chat/file/artifact areas.
- Jump up/down navigation is hidden from normal chat view.
- Scroll-bottom button remains visible only when the user is not at the bottom.
- Benchmark/proof/debug UI is hidden unless Proof Mode is enabled or status is manually opened.

## Prompt library behavior
- Default: closed.
- Opens from More menu, composer `Thư viện prompt`, or Advanced panel.
- Has search and existing prompt groups.
- Click prompt still inserts/runs through the existing handlers.

## Tag panel behavior
- Default: compact header + selected tags only.
- `Show tags` renders grouped tags: Agent, Niche, Product Type, Research, Build, Test, Export.
- Clicking a tag prepends it to the textarea and avoids duplicates.
- Selected tag chips can remove individual tags.
- Clear removes selected AI KDP tags from textarea.

## Advanced behavior
- `Advanced ▾` is collapsed by default.
- Opens shortcuts for prompt drawer, full tag list, status/brain/router, export chat, and Proof Mode.

## Proof mode behavior
- OFF by default for normal clean chat.
- ON shows proof/debug/status style UI without removing backend logs.

## Tests PASS/FAIL
- `node --check web_ui/app.js`: PASS
- `python -m py_compile web_app.py`: PASS
- `GET /api/status`: PASS, appVersion `v1.13-clean-ui`
- `GET /api/skill_tags`: PASS, 27 tags returned
- `POST /api/route_skill #buyer-test`: PASS, routes to `skills/07_buyer_test_ai_printables.md`
- Static UI checks for More menu / drawer / grouped tags / Proof Mode / hover icons: PASS
- `/api/chat` FAST smoke test: FAIL/TIMEOUT at 60s; backend/model call is still slow, not a frontend syntax failure
- Browser console check: NOT RUN, local Playwright package not installed in this repo

## Notes
- No old API/skill/router modules were removed.
- Server was restarted on `127.0.0.1:18088` after version update.
- Next fix should target backend chat latency if `/api/chat` continues timing out.

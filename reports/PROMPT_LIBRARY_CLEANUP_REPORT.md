# PROMPT LIBRARY CLEANUP REPORT

## Files changed
- `VERSION` -> `v1.13-prompt-clean`
- `web_ui/index.html` -> cache query updated to `v1.13-prompt-clean`
- `web_ui/app.js` -> added clean prompt data, 6 quick prompt chips, 4-tab prompt drawer, search, Pin/Unpin, and `Dùng` insert behavior
- `web_ui/styles.css` -> added compact quick prompt bar, tabbed drawer cards, and hidden legacy prompt groups while drawer is clean mode

## Prompt count before
- Legacy prompt buttons kept in HTML: 38
- No prompt data was deleted; old prompt groups remain in the DOM/source for compatibility.

## Prompt count shown by default
- Default quick prompts: 6
- Default quick prompts:
  - Market Pattern
  - Product Blueprint
  - Deep File Writer / Write Files
  - Buyer Test
  - Sales Page
  - Export ZIP

## Groups created
- Research: Market Pattern, Competitor Matrix, Offer Gap
- Build: Product Blueprint, Deep File Writer, Sales Page, WarriorPlus Listing
- Test: Buyer Test, AI Replace Risk, Refund Risk, License Check
- Launch: JV Pack, Delivery Support, Export ZIP, Public Launch Audit
- Total clean prompt cards: 15

## Search added
- Drawer search uses `promptSearchInput` and filters clean prompt cards by title, description, and tags.
- Existing legacy prompt filtering code is preserved.

## Favorites added
- Added Pin / Unpin for clean prompt cards.
- Favorites are stored in localStorage key `clean_prompt_pins_v113`.
- Default pinned prompts are the 6 quick prompts.
- Pinned prompts render in the compact `Prompt nhanh` bar.

## Behavior
- Composer no longer shows long prompt groups by default.
- `Thư viện prompt ▾` opens the drawer.
- Drawer shows 4 tabs and compact prompt cards.
- Each card shows title, one-line description, tags, Pin/Unpin, and `Dùng`.
- `Dùng` inserts the full prompt into textarea and closes the drawer; it does not auto-send.
- Quick chips insert prompt into textarea without auto-sending.

## Tests PASS/FAIL
- `node --check web_ui/app.js`: PASS
- `python -m py_compile web_app.py`: PASS
- `GET /api/status`: PASS, appVersion `v1.13-prompt-clean`
- `GET /api/skill_tags`: PASS, 27 tags returned
- `POST /api/route_skill #export-zip`: PASS, routes to `skills/15_export_zip_ai_printables.md`
- Static check: legacy prompt data kept: PASS, 38 prompt buttons still present
- Static check: default quick prompt count 6: PASS
- Static check: clean prompt cards 15: PASS
- Static check: search/pin/use button code present: PASS
- Browser console check: NOT RUN, local Playwright package not installed
- `/api/chat` full send: NOT RETESTED here because previous v1.13 clean UI run showed backend/model timeout; routing API still passes

## Next action
- Open `http://127.0.0.1:18088/`, hard refresh, confirm only the compact `Prompt nhanh` row is visible near the composer.
- If chat send still times out, optimize backend/model call separately; prompt library cleanup is frontend-focused.

## Hotfix v1.13-prompt-clean.1 — overlap fix
- Problem: AI KDP tag panel, quick prompt bar, advanced panel, and mode selector were sharing/overriding the same composer grid row; older v1.11 CSS also forced tag panel to `position:absolute`, causing it to float over prompt chips.
- Fix: Added final CSS override so composer rows are separated: head -> quick prompts -> tags -> advanced -> mode -> input -> files.
- Fix: Forced `.ai-kdp-tag-panel` back to static positioning and removed old absolute bottom/left/right behavior.
- Fix: Assigned dedicated grid areas to `.quick-prompt-bar`, `.ai-kdp-tag-panel`, `.advanced-panel`, `.mode-selector`, textarea, attach, send, and files.
- Version/cache bumped to `v1.13-prompt-clean.1`.
- Tests: `node --check web_ui/app.js` PASS, `python -m py_compile web_app.py` PASS, `/api/status` returns `v1.13-prompt-clean.1` PASS.

## Hotfix v1.13-prompt-clean.2 — restore timestamps
- Problem: clean UI CSS hid `.thread-time`, `.thread-preview`, and `.msg.user .msg-meta`, so chat history and message timestamps disappeared.
- Fix: Added final CSS override to show thread date/time, preview, pin badges, and user/assistant message metadata again.
- JS already stored `createdAt` for threads and messages and already rendered `VN dd/mm/yyyy hh:mm`; no data migration needed.
- Version/cache bumped to `v1.13-prompt-clean.2`.
- Tests: `node --check web_ui/app.js` PASS, `python -m py_compile web_app.py` PASS, `/api/status` returns `v1.13-prompt-clean.2` PASS.

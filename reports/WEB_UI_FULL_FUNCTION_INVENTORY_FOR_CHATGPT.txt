# WEB UI FULL FUNCTION INVENTORY + UPGRADE PLANNING PROMPT

Project: `G:\Documents\warriorplus MMO\Agent PLR Saas`
Local URL: `http://127.0.0.1:18088/`
Public URL target: `http://103.82.26.216:8088/`
Current version from `/api/status`: `v1.12-artifact-proof-16pt`
Main files:
- `web_app.py` — Python backend HTTP server, API, routing, chat, upload, skill routing, SSE stream.
- `web_ui/index.html` — Web UI layout.
- `web_ui/app.js` — Frontend state, chat, history, tag panel, quick actions, streaming, prompt library.
- `web_ui/styles.css` — UI styling.
- `web_ui/utils/renderFileCard.js` — File card rendering.

## 1. Goal For ChatGPT/UI Planner

You are asked to create a detailed upgrade plan for this Web UI Chat system. The web is an agentic chat dashboard for PLR/SaaS/WarriorPlus/KDP/AI Printables product creation. It currently works but has accumulated too many features, tags, quick actions, benchmark tools, and panels. The next UI upgrade should make it cleaner, faster to use, easier to understand, and less cluttered.

Main UX problem reported by user:
- Too many keywords/tags can cover content and make the UI hard to read.
- Tag selection sometimes feels unclear.
- The Web UI is powerful but visually overloaded.
- User wants a better plan before coding more UI changes.

Need plan for:
- Cleaner layout.
- Better grouping of features.
- Better chat input/tag UX.
- Better quick actions library.
- Better status and benchmark proof panels.
- Better mobile/desktop responsive design.
- Keep all existing modules working.

## 2. Current High-Level Web UI Layout

### Left sidebar
- Workspace/channel tabs via `#workspaceTabs`.
- `+ Chat mới` button via `#newChatBtn`.
- Search chat history via `#threadSearch`.
- Thread list via `#threadList`.
- Sidebar close/open/backdrop controls:
  - `#sidebarCloseBtn`
  - `#sidebarToggleBtn`
  - `#sidebarBackdrop`

### Top bar
- Main title: `Agent chủ`.
- Workspace badge: `#workspaceBadge`.
- Version badge: `[data-app-version]`.
- Brain summary line: `#brainSummary`.
- Project status strip:
  - `#psProduct`
  - `#psLaunch`
  - `#psReadiness`
  - `#psNextAction`
  - Refresh button `#psRefreshBtn`.
- Config controls:
  - Model/persona select: `#modelSelect`.
  - Tool mode select: `#toolModeSelect`.
- Icon actions:
  - Prompt library: `#promptLibraryBtn`.
  - Status panel: `#statusBtn`.
  - Export current chat markdown: `#exportBtn`.
  - Theme toggle: `#themeToggleBtn`.
  - Clear current chat: `#clearBtn`.

### Main chat area
- Status panel: `#statusPanel`.
- Chat transcript: `#chat`.
- Chat jump navigation:
  - `#jumpPrevBtn`
  - `#jumpNextBtn`
- Scroll bottom button: `#scrollBottomBtn`.
- Reply status: `#replyStatus`.
- Retry failed send: `#retryLastBtn`.

### Composer/footer
- Quick actions / prompt library: `#quickActions`, toggle `#quickActionsToggle`.
- Mode selector: `#modeSelector` with `FAST`, `BALANCED`, `DEEP`.
- File input: `#fileInput`.
- AI KDP tag panel:
  - Container: `#aiKdpTagPanel`.
  - Header: `AI Printables KDP Tags`.
  - Show/Hide tags button: `#toggleAiKdpTagsBtn`.
  - Clear selected tags: `#clearAiKdpTagsBtn`.
  - Selected tags area: `#aiKdpSelectedTags`.
  - Full tag chip list: `#aiKdpTagChips`.
- Prompt navigation:
  - `#promptJumpPrevBtn`
  - `#promptJumpNextBtn`
- Attach button: `#attachBtn`.
- Textarea: `#prompt`.
- Send button: `#sendBtn`.
- Attachment preview bar: `#attachmentBar`.

### Artifact/canvas panel
- Right side result canvas: `#artifactPanel`.
- Title: `#artifactTitle`.
- Body: `#artifactBody`.
- Copy: `#artifactCopyBtn`.
- Download: `#artifactDownloadBtn`.
- Close: `#artifactCloseBtn`.

### Toast
- `#toast` for feedback.

## 3. Current Run Modes

Mode selector near input:
- `FAST`
  - Intended for quick chat.
  - Low RAG topK.
  - No benchmark/export by default.
- `BALANCED`
  - Uses skill + brain moderately.
  - Good for analysis/blueprint.
- `DEEP`
  - More RAG/audit/export.
  - Slower.
  - For product build, buyer test, public launch audit, export.

Backend topK config from status:
- `fast`: 6
- `balanced`: 12
- `deep`: 20
- `quick`: 4
- `asset`: 12
- `auto`: 6

UX improvement request:
- Make modes clearer with short descriptions and cost/time expectations.
- Default to FAST or BALANCED.
- Avoid DEEP running accidentally.
- If user chooses DEEP, show warning that it may be slow and write files.

## 4. Current AI Printables KDP Prompt Tag System

Frontend tag list in `web_ui/app.js`:

```txt
#ai-printables-kdp-prompt
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
#market-pattern
#competitor-matrix
#offer-gap
#product-blueprint
#deep-file-writer
#prompt-output-test
#buyer-test
#ai-replace-risk
#refund-risk
#license-check
#sales-page
#warriorplus-listing
#jv-pack
#delivery-support
#export-zip
#public-launch-audit
```

Skill mapping:

```txt
#market-pattern => skills/01_market_pattern_ai_printables.md
#competitor-matrix => skills/02_competitor_matrix_ai_printables.md
#offer-gap => skills/03_offer_gap_ai_printables.md
#product-blueprint => skills/04_product_blueprint_ai_printables.md
#deep-file-writer => skills/05_deep_file_writer_ai_printables.md
#prompt-output-test => skills/06_prompt_output_test_ai_printables.md
#buyer-test => skills/07_buyer_test_ai_printables.md
#ai-replace-risk => skills/08_ai_replace_risk_ai_printables.md
#refund-risk => skills/09_refund_risk_ai_printables.md
#license-check => skills/10_license_compliance_ai_printables.md
#sales-page => skills/11_sales_page_ai_printables.md
#warriorplus-listing => skills/12_warriorplus_listing_ai_printables.md
#jv-pack => skills/13_jv_pack_ai_printables.md
#delivery-support => skills/14_delivery_support_ai_printables.md
#export-zip => skills/15_export_zip_ai_printables.md
#public-launch-audit => skills/16_public_launch_audit_ai_printables.md
```

Current tag behavior:
- `Show tags` expands full chip list.
- Clicking a tag inserts it at the beginning of textarea.
- Selected tags are displayed in `#aiKdpSelectedTags`.
- `Clear` removes all known AI KDP tags from textarea.
- Active tag chip should get `.active` class.
- Backend also parses tags from message and payload.

Potential bug/UX issue to inspect:
- In `removeAiKdpTag`, regex string appears as `` `(^|\s)...(?=\s|$)` `` in source view but verify actual escaping. If escaping is wrong, selected tag removal may fail.
- Too many chips create visual clutter. Need compact grouped chips, search/filter, or dropdown command palette.
- Suggested UI: collapsed by default, show only selected tags as pills, put full tag list inside popover/drawer.

## 5. Current Quick Action Groups

### Build Product
Buttons include:
- `Analyze PLR`
- `Idea Score`
- `Upgrade Kit`
- `Product Assets`
- `Full Launch Pack`

### Launch Assets
Buttons include:
- `Offer Angle`
- `Sales Page`
- `Funnel Plan`
- `W+ Listing`
- `Swipe Pack`

### Case Study Brain
Buttons include:
- `1. Kiểm tra kho` → `/training_status`
- `2. Index 300 file` → `/train_case_study_brain 300`
- `3. Rút pattern` → `/case_study_patterns ...`

### AI Printables
Buttons include:
- `Kho` → `/ai_print_status`
- `Pattern` → `/ai_print_patterns ...`
- `Market` → `/ai_print_market ...`
- `Matrix` → `/ai_print_competitor ...`
- `Gap` → `/ai_print_gap ...`
- `Chuyên sâu` → `/ai_print_deep ...`
- `Tạo ZIP` → `/ai_print_build ...`

### AI Printables KDP Prompt
Buttons include:
- `Fast Market Pattern` — FAST mode.
- `Fast Buyer Test` — FAST mode.
- `Fast Product Blueprint` — BALANCED mode.
- `1. Brain Status` → `/ai_printables_kdp_prompt_status`
- `2. Market Pattern` → tags `#ai-printables-kdp-prompt #market-pattern`
- `3. Competitor Matrix` → tags `#ai-printables-kdp-prompt #competitor-matrix`
- `4. Product Blueprint` → tags `#ai-printables-kdp-prompt #product-blueprint`
- `5. Deep File Writer` → tags `#ai-printables-kdp-prompt #deep-file-writer`
- `6. Buyer Test` → tags `#ai-printables-kdp-prompt #buyer-test`
- `7. Export ZIP` → tags `#ai-printables-kdp-prompt #export-zip`
- `8. Public Launch Audit` → tags `#ai-printables-kdp-prompt #public-launch-audit`

### Launch QA / Agent Contract group
Buttons include:
- `1. Market Pattern` → `/market_pattern_extract`
- `2. Competitor Matrix` → `/competitor_matrix`
- `3. Buyer Test` → `/buyer_test ...`
- `4. Prompt Test` → `/prompt_output_test ...`
- `5. AI Risk` → `/ai_replace_risk ...`
- `6. Launch Gate` → `/public_launch_audit ...`
- `7. Final Score` → `/final_scorecard ...`

Prompt library dynamic features in `app.js`:
- Search prompt library.
- Pin prompt buttons.
- Recent prompt group.
- Prompt preview on hover.
- Keyboard shortcuts.

UX problem:
- Too many quick action buttons are visible at once.
- Need tabs/categories/search/favorites, perhaps default collapsed groups.

## 6. Current Backend APIs

### Static/frontend
- `GET /` — serve `web_ui/index.html`.
- Workspace pages also serve index.
- `GET /styles.css`
- `GET /app.js`
- `GET /utils/renderFileCard.js`
- `GET /favicon.ico`

### Status / state
- `GET /api/status`
  - Returns appVersion, API ready, brain status, modes, RAG topK, upload limits, brain cards, AI Printables KDP Prompt Agent status, active project, sources preview.
- `GET /api/project_status`
- `GET /api/project_state`

### Brain/search
- `GET /api/case_study_brain`
- `GET /api/case_study_search?q=...`
- `GET /api/ai_printables_brain`
- `GET /api/ai_printables_search?q=...`
- `GET /api/sources?q=...`

### Skill routing
- `GET /api/skill_tags`
  - Returns AI Printables KDP Prompt tags with skill descriptions.
- `POST /api/route_skill`
  - Input: message + tags.
  - Output: matched agent, matched tags, skillFile, brainFiles, routeReason.

### Chat
- `POST /api/chat`
  - Payload includes:
    - `question`
    - `mode`
    - `history`
    - `attachments`
    - `tags`
    - `agentKey`
    - `skillRoute`
    - `skillFile`
    - `module`
    - `requestId`
  - Backend routes AI KDP tags, loads skill/brain context, applies module context, calls LLM, returns answer + sources + timings.
- `POST /api/chat_stream`
  - SSE/chunked streaming with step status such as routing/loading/searching/calling/finalizing.

### Upload/files
- `GET /api/upload_limits`
- `POST /api/upload`
- `GET /api/upload_file?...`
- `GET /api/generated_file?...`
- `GET /api/prompt_file?...`
- `POST /api/create_file`

### Threads/history
- `GET /api/threads?workspace=...`
- `POST /api/threads?workspace=...`

### Control
- `POST /api/cancel`

## 7. Current Backend Behavior Important For UI Plan

Chat request flow:
1. Receive question/history/attachments/mode/tags.
2. Route AI Printables KDP Prompt tags using `_route_ai_printables_kdp_prompt`.
3. Load skill + related brain with `_skill_context_for_question`.
4. If no skill context, infer command/module from slash command or text.
5. Compute response mode via `_effective_chat_mode`.
6. Add attachment context.
7. Use RAG topK based on mode.
8. If action-only module, run tool action and return action response.
9. Else call LLM.
10. Run optional action after answer.
11. Add agent contract footer/quality gate.
12. Search sources for display.
13. Append performance log.
14. Return answer, sources, mode, timings.

Performance features:
- `_read_text_cached` caches text by modified time.
- Chat latency log written to `reports/chat_latency.jsonl`.
- RAG mode topK prevents heavy retrieval in FAST/BALANCED.
- `/api/chat_stream` supports progress status and partial response.

## 8. Current Benchmark / Artifact Proof Feature

Recent benchmark artifacts:
- `scripts/artifact_proof_benchmark_v125.py`
- `benchmarks/artifact_proof_compare_v125/final_report.md`
- `benchmarks/artifact_proof_compare_v125/comparison_summary.md`
- `benchmarks/artifact_proof_compare_v125/ANTI_FAKE_AUDIT.md`
- `exports/artifact_proof_compare_v125/round_2_agent_pack.zip`
- `exports/artifact_proof_compare_v125/round_2_baseline_pack.zip`

Latest benchmark result:
- Agent round 2: `160/160 = 16.0/16`, normalized `10.0/10`.
- Codex baseline round 2: `157/160 = 15.7/16`, normalized `9.8/10`.
- Anti-fake note: this is artifact proof only, not live WarriorPlus/payment/JV/buyer proof.

UI improvement idea:
- Add a dedicated `Proof / Benchmark` panel instead of mixing benchmark with chat.
- Show artifact proof with manifest/ZIP/checks in a clean table.
- Do not run benchmark from normal chat.
- Add “Open latest report”, “Open latest ZIP”, “Run benchmark” buttons in a separate advanced/admin tab.

## 9. Existing Data/Brain/Agent Structure

Main agent:
- `agents/AI_Printables_KDP_Prompt_Agent/`

Important subfolders:
- `brain/`
- `skills/`
- `routing/`
- `memory/`
- `quality_gates/`
- `logs/`
- `exports/`

Skill folder expected files:
- `01_market_pattern_ai_printables.md`
- `02_competitor_matrix_ai_printables.md`
- `03_offer_gap_ai_printables.md`
- `04_product_blueprint_ai_printables.md`
- `05_deep_file_writer_ai_printables.md`
- `06_prompt_output_test_ai_printables.md`
- `07_buyer_test_ai_printables.md`
- `08_ai_replace_risk_ai_printables.md`
- `09_refund_risk_ai_printables.md`
- `10_license_compliance_ai_printables.md`
- `11_sales_page_ai_printables.md`
- `12_warriorplus_listing_ai_printables.md`
- `13_jv_pack_ai_printables.md`
- `14_delivery_support_ai_printables.md`
- `15_export_zip_ai_printables.md`
- `16_public_launch_audit_ai_printables.md`
- `_index.json`
- `_changelog.md`
- `_usage_log.md`

## 10. Known UX / UI Problems To Solve

1. Tag overload
- Full AI KDP tag list is long.
- If displayed fully near textarea, it takes vertical space and distracts from chat.
- Better: selected tags only visible by default; full list in popover, searchable drawer, or modal.

2. Quick action overload
- Many buttons from multiple systems are visible.
- Better: use category tabs, accordion, search, favorites, recent.

3. Mode clarity
- FAST/BALANCED/DEEP exists but users may not understand when to use each.
- Better: show small helper text and expected time/cost.

4. Chat vs deep work separation
- Benchmark/export/deep audit should not appear like normal chat.
- Better: separate “Chat”, “Build”, “Audit”, “Benchmark”, “Files” sections.

5. Status panel too dense
- `/api/status` returns large brain status and sources.
- Better: summarized cards with expandable details.

6. Artifact proof not visualized
- Reports/ZIPs exist but UI may not show them clearly.
- Better: Proof panel with checks: files exist, placeholder scan, manifest, ZIP size, benchmark score.

7. Mobile layout risk
- Sidebar, quick library, tag panel, and artifact panel can crowd small screens.
- Better: bottom sheet for prompt library/tags and slide-over for artifact canvas.

8. Language/encoding
- Some text appears mojibake in terminal dumps; verify browser displays Vietnamese correctly.
- UI labels should be consistent Vietnamese or bilingual, not mixed randomly.

9. Tag insertion/removal reliability
- Verify tag chips add to textarea, selected tag pills remove correctly, clear removes all tags.
- Verify direct typed tags route correctly.

10. Accessibility
- Need better aria labels, focus states, keyboard navigation for tag popover and prompt library.

## 11. Suggested UI Information Architecture

Propose a cleaner layout:

### Main nav sections
1. `Chat`
   - normal chat, fast/balanced mode, selected tags only.
2. `Prompt Library`
   - searchable grouped quick actions.
3. `Agent Skills`
   - AI Printables KDP Prompt tags/skills as cards.
4. `Files & Exports`
   - uploads, generated files, ZIPs, manifests.
5. `Proof & Benchmarks`
   - artifact proof, anti-fake audit, scores, latest ZIP/report.
6. `System Status`
   - API, brains, storage, RAG, version.

### Composer recommendation
- Row 1: selected tags as compact pills + `+ Add Skill` button.
- Row 2: textarea + attach + send.
- Row 3: mode selector + small status: `FAST · topK 6 · no file write`.
- Full tag list appears only in popover when clicking `+ Add Skill`.

### Skill picker recommendation
- Search input: “Search skill or tag…”
- Groups:
  - Niche tags: AI Printables/KDP/PLR/WarriorPlus/etc.
  - Research skills: market pattern, competitor matrix, offer gap.
  - Build skills: product blueprint, deep file writer, sales page, listing, JV.
  - Audit skills: buyer test, AI replace risk, refund risk, license, public launch audit.
  - Export skills: export ZIP.
- Each skill card shows:
  - tag
  - skill name
  - short description
  - mode suggestion
  - expected latency

### Quick action recommendation
- Keep only 3–5 pinned actions visible.
- Put the rest behind search/category.
- Add recently used actions.
- Add “Run” vs “Insert prompt” distinction.

### Proof panel recommendation
- Show latest benchmark summary:
  - Agent score normalized /10.
  - Baseline score normalized /10.
  - Files created.
  - Placeholder scan.
  - ZIP existence + size.
  - Anti-fake limitations.
- Add buttons:
  - Open report.
  - Open manifest.
  - Download ZIP.
  - Run benchmark, with confirmation.

## 12. Must Not Break Existing Modules

Do not remove or break:
- `/api/status`
- `/api/chat`
- `/api/chat_stream`
- `/api/skill_tags`
- `/api/route_skill`
- `/ai_print_status`
- `/ai_print_patterns`
- `/ai_print_market`
- `/ai_print_competitor`
- `/ai_print_gap`
- `/ai_print_deep`
- `/ai_print_build`
- Case Study Brain actions
- Build Product actions
- Sales Page actions
- JV Manager actions
- Export ZIP modules
- Chat history/workspaces
- File upload and attachments
- Artifact canvas
- FAST/BALANCED/DEEP mode behavior

## 13. Requested Output From ChatGPT

Please create a practical UI upgrade plan for this Web UI.

Return:

1. `UX Diagnosis`
- What is overloaded?
- What is confusing?
- What can be hidden by default?

2. `Target Layout`
- Desktop layout.
- Mobile layout.
- Composer layout.
- Skill/tag picker layout.
- Proof/benchmark layout.

3. `Component Plan`
- Components to add/refactor.
- Data each component needs.
- Props/state if using vanilla JS.

4. `Interaction Rules`
- How tag add/remove/clear should work.
- How mode selection should work.
- How quick actions should run/insert.
- How benchmark should be separated from normal chat.

5. `Visual Design`
- Spacing.
- Tag chips.
- Accordions.
- Cards.
- Status colors.
- Typography.

6. `Implementation Plan`
- Phase 1: no backend change, CSS/HTML/JS layout cleanup.
- Phase 2: better skill picker and quick action search.
- Phase 3: proof/benchmark panel.
- Phase 4: mobile polish and accessibility.

7. `Exact File Changes`
- What to change in `web_ui/index.html`.
- What to change in `web_ui/app.js`.
- What to change in `web_ui/styles.css`.
- Optional backend additions in `web_app.py`.

8. `Acceptance Tests`
- Tag appears in textarea after click.
- Selected tags visible but compact.
- Clear tags works.
- Direct typed tags route correctly.
- FAST/BALANCED/DEEP payload correct.
- Quick action group works.
- Status panel loads.
- Artifact panel copy/download works.
- Mobile layout usable.
- No old module broken.

9. `Risks`
- What can break.
- How to avoid regressions.

10. `Codex Implementation Prompt`
- Write a final concise prompt that I can paste into Codex to implement your plan safely.

## 14. Current Files To Inspect In Codebase

Ask Codex/engineer to inspect:
- `web_ui/index.html`
- `web_ui/app.js`
- `web_ui/styles.css`
- `web_ui/utils/renderFileCard.js`
- `web_app.py`
- `reports/ui_buttons_inventory.json`
- `benchmarks/artifact_proof_compare_v125/final_report.md`
- `benchmarks/artifact_proof_compare_v125/ANTI_FAKE_AUDIT.md`

## 15. Current Validation Commands

```powershell
Invoke-RestMethod http://127.0.0.1:18088/api/status
Invoke-RestMethod http://127.0.0.1:18088/api/skill_tags
python scripts/test_skill_routing.py
```

Route test:

```powershell
Invoke-RestMethod http://127.0.0.1:18088/api/route_skill `
  -Method POST `
  -ContentType 'application/json' `
  -Body '{"message":"#ai-printables-kdp-prompt #market-pattern test","tags":["#ai-printables-kdp-prompt","#market-pattern"]}'
```

Expected route:
- Agent: `AI Printables KDP Prompt Agent`
- Skill file: `skills/01_market_pattern_ai_printables.md`

## 16. Final Planning Instruction

Do not propose deleting features. The goal is to organize and hide advanced features behind better UI, not remove power. Prioritize reducing clutter while preserving all agent/skill/brain/proof functionality.

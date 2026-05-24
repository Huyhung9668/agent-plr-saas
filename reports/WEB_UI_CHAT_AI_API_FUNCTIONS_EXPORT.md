# WEB UI CHAT AI API FUNCTIONS EXPORT

Generated: 2026-05-24 19:46:43
Project: G:\Documents\warriorplus MMO\Agent PLR Saas
Server: http://127.0.0.1:18088/
Version: ﻿v1.14-vendor-ready-builder.7

## 1. Main Files

- web_app.py — Python backend HTTP server, chat API, skill routing, product file export, project/product fast paths.
- web_ui/index.html — Web UI shell.
- web_ui/app.js — Chat UI logic, streaming call, mode/tags/prompt library/file cards integration.
- web_ui/styles.css — Layout, composer, panels, responsive UI.
- web_ui/utils/renderFileCard.js — File card rendering/copy/download UI.
- launch_os_db.py — Launch/project memory snapshot used by /api/project_state.

## 2. Backend API Overview

### Core Chat

- POST /api/chat — Main chat endpoint. Accepts question, mode, module, history, ttachments, 	ags, equestId. Returns JSON answer/action.
- POST /api/chat_stream — Streaming/SSE-style chat endpoint. Used by UI for progressive response/status.
- POST /api/cancel — Cancels active request by request id.

### Routing / Skills / Tags

- GET /api/skill_tags — Returns available AI Printables KDP prompt tags/chips.
- POST /api/route_skill — Tests/returns skill route for a prompt/tag combination.
- Internal router: esolve_ai_etsy_route(...) — Explicit product-step router for fast paths and route debug.
- Internal runner: _run_ai_etsy_route(...) — Executes selected product builder route and appends route debug.

### Project / Status

- GET /api/status — App status, version, brain summaries, modes, RAG topK, active project.
- GET /api/project_status — Active project snapshot.
- GET /api/project_state — Active project state/memory.
- GET /api/upload_limits — Upload limits and storage status.

### Files / Downloads

- POST /api/upload — Upload attachment(s) for chat.
- POST /api/upload_file — Upload file helper endpoint.
- POST /api/create_file — Create generated file from UI/API action.
- GET /api/generated_file?name=... — Download generated web file.
- GET /api/product_file?product=...&file=... — Download product ZIP/file from exports/products/<product>/.
- GET /api/prompt_file?name=... — Download prompt file.

### Brain/Search Helpers

- GET /api/sources?q=... — Formatted sources for a query.
- GET /api/case_study_brain — Case-study brain summary.
- GET /api/case_study_search?q=... — Case-study search.
- GET /api/ai_printables_brain — AI printables brain summary.
- GET /api/ai_printables_search?q=... — AI printables search.

### Threads

- GET /api/threads — Load thread state.
- POST /api/threads — Save thread state.

## 3. Chat Modes

- FAST — Fast chat, lower RAG topK, no benchmark/export by default.
- BALANCED — Skill + brain context, medium depth.
- DEEP — Product generation/audit/export tasks.

## 4. AI Printables Product Fast Paths

Current product-step fast paths include:

- Step 2 — Product Blueprint
- Step 3 — Core Product Files
- Step 4 — Templates And Prompts
- Step 5 — Examples / Quality / Compliance
- Step 6 — Delivery / Support
- Step 7 — Buyer Test / Risk Test
- Step 8 — Final Export Folder + ZIP + Manifest

Important behavior:

- Explicit step route should beat keyword route.
- Product name should come from Product: line or active project marker.
- Fast-path responses include ROUTE DEBUG where implemented.
- Product files are written under exports/products/<Product Name>/.
- ZIP downloads use /api/product_file.

## 5. Current Backend Route / Function Inventory

- web_app.py:210: `if parsed.path == "/styles.css":`
- web_app.py:212: `if parsed.path == "/app.js":`
- web_app.py:214: `if parsed.path == "/utils/renderFileCard.js":`
- web_app.py:216: `if parsed.path == "/favicon.ico":`
- web_app.py:220: `if parsed.path == "/api/status":`
- web_app.py:248: `if parsed.path == "/api/project_status":`
- web_app.py:250: `if parsed.path == "/api/project_state":`
- web_app.py:253: `if parsed.path == "/api/case_study_brain":`
- web_app.py:255: `if parsed.path == "/api/case_study_search":`
- web_app.py:258: `if parsed.path == "/api/ai_printables_brain":`
- web_app.py:260: `if parsed.path == "/api/ai_printables_search":`
- web_app.py:263: `if parsed.path == "/api/skill_tags":`
- web_app.py:265: `if parsed.path == "/api/upload_limits":`
- web_app.py:267: `if parsed.path == "/api/upload_file":`
- web_app.py:269: `if parsed.path == "/api/generated_file":`
- web_app.py:271: `if parsed.path == "/api/product_file":`
- web_app.py:273: `if parsed.path == "/api/prompt_file":`
- web_app.py:275: `if parsed.path == "/api/sources":`
- web_app.py:280: `if parsed.path == "/api/threads":`
- web_app.py:287: `if parsed.path == "/api/upload":`
- web_app.py:289: `if parsed.path == "/api/threads":`
- web_app.py:291: `if parsed.path == "/api/create_file":`
- web_app.py:293: `if parsed.path == "/api/cancel":`
- web_app.py:295: `if parsed.path == "/api/route_skill":`
- web_app.py:297: `if parsed.path not in {"/api/chat", "/api/chat_stream"}:`
- web_app.py:322: `if parsed.path == "/api/chat_stream":`
- web_app.py:361: `if parsed.path == "/api/chat_stream":`
- web_app.py:365: `if parsed.path == "/api/chat_stream":`
- web_app.py:371: `if parsed.path == "/api/chat_stream":`
- web_app.py:403: `def _send_chat_stream(`
- web_app.py:481: `def _send_prebuilt_stream(self, answer: str, response_mode: str, action: dict, timings: dict | None = None) -> None:`
- web_app.py:526: `def _handle_upload(self) -> None:`
- web_app.py:575: `def _handle_multipart_upload(self, length: int, content_type: str) -> None:`
- web_app.py:617: `def _handle_threads_save(self, workspace_id: str) -> None:`
- web_app.py:628: `def _handle_create_file(self) -> None:`
- web_app.py:650: `def _handle_upload_file(self, query: str) -> None:`
- web_app.py:681: `def _handle_route_skill(self) -> None:`
- web_app.py:692: `def _handle_prompt_file(self, query: str) -> None:`
- web_app.py:717: `def _handle_generated_file(self, query: str) -> None:`
- web_app.py:744: `def _handle_product_file(self, query: str) -> None:`
- web_app.py:770: `def _handle_cancel(self) -> None:`
- web_app.py:2374: `def _skill_tags_payload() -> dict:`
- web_app.py:2423: `def _route_ai_printables_kdp_prompt(message: str, tags: list | None = None) -> dict:`
- web_app.py:3386: `def _build_ai_etsy_step2_blueprint_answer(project: dict | None = None) -> tuple[str, dict]:`
- web_app.py:3572: `def _build_ai_etsy_step3_core_files_answer(project: dict | None = None) -> tuple[str, dict]:`
- web_app.py:4045: `def _write_step_product_bundle(product_name: str, step_slug: str, bundle_name: str, answer: str, action_type: str) -> dict:`
- web_app.py:4273: `def resolve_ai_etsy_route(question: str, payload: dict | None = None) -> dict:`
- web_app.py:4337: `def _run_ai_etsy_route(route: dict) -> tuple[str, dict]:`
- web_app.py:4402: `def _build_ai_etsy_step4_templates_answer(project: dict | None = None) -> tuple[str, dict]:`
- web_app.py:4618: `def _build_ai_etsy_step5_examples_quality_answer(project: dict | None = None) -> tuple[str, dict]:`
- web_app.py:4781: `def _build_ai_etsy_step6_delivery_support_answer(project: dict | None = None) -> tuple[str, dict]:`
- web_app.py:5018: `def _build_ai_etsy_step7_buyer_risk_answer(project: dict | None = None) -> tuple[str, dict]:`
- web_app.py:5135: `def _build_ai_etsy_step8_final_export_answer(project: dict | None = None) -> tuple[str, dict]:`

## 6. Current UI/API Call Inventory

- web_ui/app.js:3: `const prompt = document.getElementById("prompt");`
- web_ui/app.js:8: `const promptJumpPrevBtn = document.getElementById("promptJumpPrevBtn");`
- web_ui/app.js:9: `const promptJumpNextBtn = document.getElementById("promptJumpNextBtn");`
- web_ui/app.js:20: `const promptLibraryBtn = document.getElementById("promptLibraryBtn");`
- web_ui/app.js:27: `const modelSelect = document.getElementById("modelSelect");`
- web_ui/app.js:28: `const toolModeSelect = document.getElementById("toolModeSelect");`
- web_ui/app.js:30: `const activeModeLabel = document.getElementById("activeModeLabel");`
- web_ui/app.js:50: `const modeSelector = document.getElementById("modeSelector");`
- web_ui/app.js:53: `const aiKdpTagPanel = document.getElementById("aiKdpTagPanel");`
- web_ui/app.js:54: `const aiKdpTagChips = document.getElementById("aiKdpTagChips");`
- web_ui/app.js:55: `const aiKdpSelectedTags = document.getElementById("aiKdpSelectedTags");`
- web_ui/app.js:56: `const clearAiKdpTagsBtn = document.getElementById("clearAiKdpTagsBtn");`
- web_ui/app.js:57: `const toggleAiKdpTagsBtn = document.getElementById("toggleAiKdpTagsBtn");`
- web_ui/app.js:60: `let proofModeToggle = null;`
- web_ui/app.js:61: `let promptDrawerBackdrop = null;`
- web_ui/app.js:62: `let quickPromptBar = null;`
- web_ui/app.js:63: `let cleanPromptLibrary = null;`
- web_ui/app.js:64: `let activePromptTab = "Research";`
- web_ui/app.js:65: `const aiKdpPromptTags = ["#ai-printables-kdp-prompt", "#ai-printables", "#kdp", "#plr", "#warriorplus", "#prompt-pack", "#canva-printable", "#coloring-book", "#journal", "#kids-worksheet", "#etsy-printable", "#market-pattern", "#competitor-matrix", "#offer-gap", "#product-blueprint", "#deep-file-writer", "#prompt-output-test", "#buyer-test", "#ai-replace-risk", "#refund-risk", "#license-check", "#sales-page", "#warriorplus-listing", "#jv-pack", "#delivery-support", "#export-zip", "#public-launch-audit"];`
- web_ui/app.js:66: `const aiKdpTagGroups = {`
- web_ui/app.js:67: `Agent: ["#ai-printables-kdp-prompt"],`
- web_ui/app.js:69: `"Product Type": ["#prompt-pack", "#canva-printable", "#coloring-book", "#journal", "#kids-worksheet", "#etsy-printable"],`
- web_ui/app.js:75: `const cleanPromptGroups = {`
- web_ui/app.js:77: `{ id: "idea-matrix", title: "10 Ý Tưởng", desc: "Gợi ý 10 ý tưởng AI Printables/KDP dễ hiểu, có điểm và chọn top 3.", tags: ["#ai-printables-kdp-prompt", "#market-pattern", "#offer-gap"], prompt: "#ai-printables-kdp-prompt #market-pattern #offer-gap\nHãy tạo 10 ý tưởng sản phẩm AI Printables/KDP/PLR để bán trên WarriorPlus. Trả lời dạng bảng: Tên ý tưởng, buyer, pain, deliverables, vì sao không chỉ là prompt thô, rủi ro AI replace, độ dễ làm, điểm /10. Cuối cùng chọn Top 3 và 1 ý tưởng nên làm đầu tiên." },`
- web_ui/app.js:78: `{ id: "market-pattern", title: "Market Pattern", desc: "Rút market pattern cho AI Printables/KDP/PLR.", tags: ["#ai-printables-kdp-prompt", "#market-pattern"], prompt: "#ai-printables-kdp-prompt #market-pattern\nRút market pattern cho ngách AI Printables/KDP/PLR." },`
- web_ui/app.js:79: `{ id: "competitor-matrix", title: "Competitor Matrix", desc: "So sánh vendor, sản phẩm, giá, sales angle.", tags: ["#ai-printables-kdp-prompt", "#competitor-matrix"], prompt: "#ai-printables-kdp-prompt #competitor-matrix\nSo sánh vendor/sản phẩm/ngách/price/sales/angle/deliverables." },`
- web_ui/app.js:80: `{ id: "offer-gap", title: "Offer Gap", desc: "Tìm khoảng trống offer và cách khác prompt pack thô.", tags: ["#ai-printables-kdp-prompt", "#offer-gap"], prompt: "#ai-printables-kdp-prompt #offer-gap\nTìm offer gap cho sản phẩm AI Printables/KDP/PLR này." },`
- web_ui/app.js:83: `{ id: "vendor-ready", title: "Vendor Ready", desc: "Tạo full product pack vendor-ready, file dày, manifest, proof và ZIP.", tags: ["#ai-printables-kdp-prompt", "#product-blueprint", "#deep-file-writer", "#export-zip"], prompt: "#ai-printables-kdp-prompt #product-blueprint #deep-file-writer #sales-page #warriorplus-listing #jv-pack #delivery-support #buyer-test #ai-replace-risk #refund-risk #license-check #export-zip\n\nTôi chọn sản phẩm: AI Etsy Printable Bundle Builder.\n\nHãy tạo VENDOR READY product pack, không phải skeleton. Xuất chung vào thư mục tên sản phẩm, mỗi file chính phải có nội dung sâu/copy-ready, tạo manifest, placeholder scan, proof log và ZIP." },`
- web_ui/app.js:84: `{ id: "product-blueprint", title: "Product Blueprint", desc: "Tạo blueprint sản phẩm bán trên WarriorPlus.", tags: ["#ai-printables-kdp-prompt", "#product-blueprint"], prompt: "#ai-printables-kdp-prompt #product-blueprint\nTạo blueprint sản phẩm bán trên WarriorPlus." },`
- web_ui/app.js:85: `{ id: "deep-file-writer", title: "Deep File Writer", desc: "Tạo product assets thật, không chỉ mô tả file.", tags: ["#ai-printables-kdp-prompt", "#deep-file-writer"], prompt: "#ai-printables-kdp-prompt #deep-file-writer\nTạo product assets thật, không chỉ mô tả file." },`
- web_ui/app.js:86: `{ id: "sales-page", title: "Sales Page", desc: "Viết sales page compliance-safe cho sản phẩm.", tags: ["#ai-printables-kdp-prompt", "#sales-page"], prompt: "#ai-printables-kdp-prompt #sales-page\nViết sales page cho sản phẩm này." },`
- web_ui/app.js:87: `{ id: "warriorplus-listing", title: "WarriorPlus Listing", desc: "Tạo title, description, FE price, commission, delivery.", tags: ["#ai-printables-kdp-prompt", "#warriorplus-listing"], prompt: "#ai-printables-kdp-prompt #warriorplus-listing\nTạo WarriorPlus listing cho sản phẩm này." },`
- web_ui/app.js:90: `{ id: "buyer-test", title: "Buyer Test", desc: "Test sản phẩm như buyer mới mua giá $17-$27.", tags: ["#ai-printables-kdp-prompt", "#buyer-test"], prompt: "#ai-printables-kdp-prompt #buyer-test\nTest sản phẩm như buyer mới mua giá $17-$27." },`
- web_ui/app.js:91: `{ id: "ai-replace-risk", title: "AI Replace Risk", desc: "Chấm rủi ro buyer nghĩ ChatGPT cũng làm được.", tags: ["#ai-printables-kdp-prompt", "#ai-replace-risk"], prompt: "#ai-printables-kdp-prompt #ai-replace-risk\nKiểm tra sản phẩm này có bị buyer nghĩ ChatGPT cũng làm được không." },`
- web_ui/app.js:92: `{ id: "refund-risk", title: "Refund Risk", desc: "Tìm lý do refund và kế hoạch giảm rủi ro.", tags: ["#ai-printables-kdp-prompt", "#refund-risk"], prompt: "#ai-printables-kdp-prompt #refund-risk\nChấm refund risk và đề xuất fix plan cho sản phẩm này." },`
- web_ui/app.js:93: `{ id: "license-check", title: "License Check", desc: "Kiểm tra copyright, trademark, Canva, KDP, PLR claims.", tags: ["#ai-printables-kdp-prompt", "#license-check"], prompt: "#ai-printables-kdp-prompt #license-check\nKiểm tra license/compliance cho sản phẩm này." },`
- web_ui/app.js:96: `{ id: "jv-pack", title: "JV Pack", desc: "Tạo JV invite, affiliate swipes và promo rules.", tags: ["#ai-printables-kdp-prompt", "#jv-pack"], prompt: "#ai-printables-kdp-prompt #jv-pack\nTạo JV pack và affiliate swipes cho sản phẩm này." },`
- web_ui/app.js:97: `{ id: "delivery-support", title: "Delivery Support", desc: "Tạo delivery page, onboarding, FAQ, refund policy.", tags: ["#ai-printables-kdp-prompt", "#delivery-support"], prompt: "#ai-printables-kdp-prompt #delivery-support\nTạo delivery page, buyer onboarding, support FAQ và refund policy." },`
- web_ui/app.js:98: `{ id: "export-zip", title: "Export ZIP", desc: "Đóng gói ZIP, tạo manifest và placeholder check.", tags: ["#ai-printables-kdp-prompt", "#export-zip"], prompt: "#ai-printables-kdp-prompt #export-zip\nĐóng gói sản phẩm thành ZIP, tạo manifest và placeholder check." },`
- web_ui/app.js:99: `{ id: "public-launch-audit", title: "Public Launch Audit", desc: "Kiểm tra gate trước khi public launch.", tags: ["#ai-printables-kdp-prompt", "#public-launch-audit"], prompt: "#ai-printables-kdp-prompt #public-launch-audit\nKiểm tra sản phẩm đã public launch được chưa." },`
- web_ui/app.js:102: `const defaultCleanPromptPins = ["idea-matrix", "vendor-ready", "product-blueprint", "deep-file-writer", "buyer-test", "export-zip"];`
- web_ui/app.js:109: `"#prompt-output-test": "skills/06_prompt_output_test_ai_printables.md",`
- web_ui/app.js:128: `const modeStorageKey = "master_agent_response_mode_v2";`
- web_ui/app.js:129: `const modelStorageKey = "master_agent_model_persona_v1";`
- web_ui/app.js:130: `const toolModeStorageKey = "master_agent_tool_mode_v1";`
- web_ui/app.js:132: `const promptLibraryStorageKey = "master_agent_prompt_library_open_v1";`
- web_ui/app.js:133: `const promptPinnedStorageKey = "master_agent_prompt_pins_v110";`
- web_ui/app.js:134: `const promptRecentStorageKey = "master_agent_prompt_recent_v110";`
- web_ui/app.js:135: `const readingModeStorageKey = "master_agent_reading_mode_v113";`
- web_ui/app.js:141: `let aiKdpTagsExpanded = false;`
- web_ui/app.js:150: `let responseMode = loadResponseMode();`
- web_ui/app.js:155: `let activePromptChip = null;`
- web_ui/app.js:156: `let promptChipBar = null;`
- web_ui/app.js:157: `let promptSearchInput = null;`
- web_ui/app.js:158: `let pinnedPromptGroup = null;`
- web_ui/app.js:159: `let recentPromptGroup = null;`
- web_ui/app.js:160: `let promptPreviewTooltip = null;`
- web_ui/app.js:161: `let promptPreviewTimer = null;`
- web_ui/app.js:162: `const defaultPromptPlaceholder = "Nhập câu hỏi, dán ảnh, hoặc kéo file vào đây...";`
- web_ui/app.js:166: `let selectedModelPersona = loadSelectValue(modelStorageKey, "agent");`
- web_ui/app.js:167: `let selectedToolMode = loadSelectValue(toolModeStorageKey, "auto");`
- web_ui/app.js:176: `let readingModeBtn = null;`
- web_ui/app.js:180: `applyResponseMode(responseMode);`
- web_ui/app.js:203: `function workspaceApiUrl(path) {`
- web_ui/app.js:205: `return apiUrl(`${path}${separator}workspace=${encodeURIComponent(workspaceId)}`);`
- web_ui/app.js:208: `function apiUrl(path) {`
- web_ui/app.js:228: `installPromptLibraryUpgrade();`
- web_ui/app.js:232: `installReadingModeToggle();`
- web_ui/app.js:269: `// Ignore private mode/localStorage errors.`
- web_ui/app.js:286: `quickActions?.classList.toggle("prompt-drawer", true);`
- web_ui/app.js:287: `if (quickActionsToggle) quickActionsToggle.textContent = "Thư viện prompt";`
- web_ui/app.js:288: `if (modelSelect) modelSelect.value = selectedModelPersona;`
- web_ui/app.js:289: `if (toolModeSelect) toolModeSelect.value = selectedToolMode;`
- web_ui/app.js:293: `function loadReadingMode() {`
- web_ui/app.js:295: `return localStorage.getItem(readingModeStorageKey) === "1";`
- web_ui/app.js:301: `function saveReadingMode(enabled) {`
- web_ui/app.js:303: `localStorage.setItem(readingModeStorageKey, enabled ? "1" : "0");`
- web_ui/app.js:309: `function applyReadingMode(enabled, { persist = false } = {}) {`
- web_ui/app.js:310: `document.body.classList.toggle("reading-mode", Boolean(enabled));`
- web_ui/app.js:311: `app?.classList.toggle("reading-mode", Boolean(enabled));`
- web_ui/app.js:312: `if (readingModeBtn) {`
- web_ui/app.js:313: `readingModeBtn.classList.toggle("active", Boolean(enabled));`
- web_ui/app.js:314: `readingModeBtn.textContent = enabled ? "Viết" : "Đọc";`
- web_ui/app.js:315: `readingModeBtn.title = enabled ? "Hiện lại thanh nhập để viết" : "Ẩn thanh trên/dưới để đọc nội dung";`
- web_ui/app.js:316: `readingModeBtn.setAttribute("aria-label", readingModeBtn.title);`
- web_ui/app.js:318: `if (persist) saveReadingMode(Boolean(enabled));`
- web_ui/app.js:322: `function toggleReadingMode() {`
- web_ui/app.js:323: `const enabled = !document.body.classList.contains("reading-mode");`
- web_ui/app.js:324: `applyReadingMode(enabled, { persist: true });`
- web_ui/app.js:328: `function installReadingModeToggle() {`
- web_ui/app.js:329: `if (readingModeBtn) return;`
- web_ui/app.js:330: `readingModeBtn = document.createElement("button");`
- web_ui/app.js:331: `readingModeBtn.id = "readingModeBtn";`
- web_ui/app.js:332: `readingModeBtn.className = "reading-mode-btn";`
- web_ui/app.js:333: `readingModeBtn.type = "button";`
- web_ui/app.js:334: `readingModeBtn.addEventListener("click", toggleReadingMode);`
- web_ui/app.js:335: `document.body.appendChild(readingModeBtn);`
- web_ui/app.js:336: `applyReadingMode(loadReadingMode());`
- web_ui/app.js:356: `function togglePromptLibrary(forceOpen = null) {`
- web_ui/app.js:359: `quickActions.classList.toggle("prompt-drawer", true);`
- web_ui/app.js:360: `document.body.classList.toggle("prompt-drawer-open", willOpen);`
- web_ui/app.js:361: `promptDrawerBackdrop?.toggleAttribute("hidden", !willOpen);`
- web_ui/app.js:362: `if (quickActionsToggle) quickActionsToggle.textContent = "Thư viện prompt";`
- web_ui/app.js:363: `saveSelectValue(promptLibraryStorageKey, "0");`
- web_ui/app.js:381: `function toggleProofMode() {`
- web_ui/app.js:382: `const enabled = Boolean(proofModeToggle?.checked);`
- web_ui/app.js:383: `document.body.classList.toggle("proof-mode-on", enabled);`
- web_ui/app.js:384: `showToast(enabled ? "Proof Mode ON" : "Proof Mode OFF");`
- web_ui/app.js:388: `const modelMap = {`
- web_ui/app.js:392: `critic: "Persona: Launch critic. Audit thẳng tay, tìm lỗi bán hàng, thiếu proof, license risk, missing assets, rồi đưa fix list.",`
- web_ui/app.js:395: `auto: "Tool mode: Auto. Tự dùng brain, project memory và file đính kèm khi hữu ích.",`
- web_ui/app.js:396: `files: "Tool mode: Files/RAG. Ưu tiên nội dung file đính kèm, Case Study Brain từ dữ liệu cũ, và brain/source đã index.",`
- web_ui/app.js:397: `case: "Tool mode: Case Study Brain. Ưu tiên kho dữ liệu cũ G:\\file_backup để rút pattern, case study, sales page, funnel, JV, KDP/kids printable; không copy nguyên văn.",`
- web_ui/app.js:398: `launch: "Tool mode: Launch OS. Ưu tiên active project, launch readiness, asset checklist, funnel/JV/export status.",`
- web_ui/app.js:399: `none: "Tool mode: Off. Trả lời trực tiếp, chỉ dùng ngữ cảnh chat khi đủ.",`
- web_ui/app.js:401: `return [modelMap[selectedModelPersona] || "", toolMap[selectedToolMode] || ""].filter(Boolean).join("\n");`
- web_ui/app.js:409: `function loadResponseMode() {`
- web_ui/app.js:411: `const saved = localStorage.getItem(modeStorageKey);`
- web_ui/app.js:418: `function applyResponseMode(mode) {`
- web_ui/app.js:419: `responseMode = ["fast", "balanced", "deep"].includes(mode) ? mode : "fast";`
- web_ui/app.js:421: `localStorage.setItem(modeStorageKey, responseMode);`
- web_ui/app.js:423: `// Ignore private mode/localStorage errors.`
- web_ui/app.js:425: `if (!modeSelector) return;`
- web_ui/app.js:426: `for (const button of modeSelector.querySelectorAll("button[data-mode]")) {`
- web_ui/app.js:427: `button.classList.toggle("active", button.dataset.mode === responseMode);`
- web_ui/app.js:429: `if (responseMode === "deep") {`
- web_ui/app.js:430: `showToast("DEEP mode chậm hơn vì dùng nhiều RAG, audit hoặc ghi file.");`
- web_ui/app.js:434: `function selectedResponseMode() {`
- web_ui/app.js:435: `const activeButton = modeSelector?.querySelector("button.active[data-mode]");`
- web_ui/app.js:436: `const selected = activeButton?.dataset?.mode || responseMode || "fast";`
- web_ui/app.js:440: `function effectiveModeLabel(text, attachments) {`
- web_ui/app.js:441: `const selected = selectedResponseMode();`
- web_ui/app.js:494: `const response = await fetch(workspaceApiUrl("/api/threads"));`
- web_ui/app.js:636: `await fetch(workspaceApiUrl("/api/threads"), {`
- web_ui/app.js:667: `focusPrompt();`
- web_ui/app.js:776: `const nextTitle = window.prompt("Đổi tên đoạn chat", thread.title);`
- web_ui/app.js:912: `<p>Chọn một prompt mẫu hoặc nhập trực tiếp để phân tích PLR, tạo product kit, sales page, funnel, JV pack và kế hoạch SaaS.</p>`
- web_ui/app.js:914: `<button type="button" data-starter-prompt="Phân tích 3 ý tưởng sản phẩm PLR + SaaS dễ bán trên WarriorPlus nhất dựa trên brain hiện tại. Với mỗi ý tưởng: buyer pain, deliverables, FE/OTO, SaaS angle, risk, next action.">Ý tưởng có thể bán</button>`
- web_ui/app.js:915: `<button type="button" data-starter-prompt="Audit active project hiện tại. Chấm điểm launch readiness, liệt kê missing assets, rủi ro license/compliance, và 10 việc cần làm tiếp theo theo thứ tự ưu tiên.">Audit launch</button>`
- web_ui/app.js:916: `<button type="button" data-starter-prompt="Tạo full launch pack cho AI PLR Rebrand Kit: product assets, sales page, WarriorPlus listing, JV pack, email funnel, traffic content, delivery page, export checklist.">Full launch pack</button>`

## 7. Known Design Notes / Risks

- Product step fast paths were added incrementally; route conflicts can happen if unsupported steps fall back into general chat.
- Some older chat messages in browser history will still show old wrong outputs; regenerate after Ctrl + F5.
- Some builders may still contain product-specific text in templates, although output replacement is partially implemented.
- For any future Step 9–36, add explicit route first; do not let it fall through to brain/model.

## 8. Recommended Next Fixes

1. Add a general STEP_UNSUPPORTED route for explicit steps not implemented.
2. Add Step 9–36 route table before model/RAG.
3. Move product builders out of web_app.py into a module like product_pipeline.py.
4. Add automated route tests script for Step 4/7/8/12 and new-product isolation.
5. Add UI debug panel showing selected route/project/action from API response.

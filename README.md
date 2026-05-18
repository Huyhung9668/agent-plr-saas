# Agent PLR Saas

Version: 1.04

Agent local de bien kho PLR/MRR/RR thanh idea san pham so, offer, funnel, SaaS plan va product pack co the test ban tren WarriorPlus/Gumroad/Payhip.

## Cau truc

```txt
Agent PLR Saas/
  app.py
  analyzer.py
  config.py
  exporter.py
  file_reader.py
  idea_generator.py
  llm_client.py
  prompts.py
  sales_page_writer.py
  scoring.py
  plr_files/
  saas_files/
  extracted/
  outputs/
  exports/
  database/
  reports/
```

## Cach dung nhanh

1. Dat file PLR hop phap cua ban vao:

```txt
C:\Users\Admin\Documents\warriorplus MMO\Agent PLR Saas\plr_files
```

Ban co the chia folder:

```txt
plr_files/
  AI/
  Marketing/
  Health/
  Planner/
  Kids-Story/
  Etsy/
  Self-Help/
```

2. Cai thu vien:

```bash
pip install -r requirements.txt
```

3. Chay agent:

```bash
python app.py
```

## Chuc nang MVP

- Scan PLR folder
- Analyze 1 product
- Analyze all products
- Generate 10 new product ideas
- Write sales page
- Export report Markdown/CSV/JSON
- Build product outline
- Create bonus stack
- Create launch assets
- License/risk audit
- Import downloaded PLR files
- Build SaaS plan
- Export full product pack
- Save analysis history to SQLite
- Auto-sort SaaS inbox
- Auto-sort PLR inbox
- Show 3 product launch workflow agents
- Create optimized input folders for workflow agents

## Simple PLR file workflow

Neu khong biet file PLR nen bo vao dau, cu vut tat ca vao:

```txt
C:\Users\Admin\Documents\warriorplus MMO\Agent PLR Saas\plr_files\_INBOX_DROP_HERE
```

Sau do chay `python app.py` va chon:

```txt
15. Auto-sort PLR inbox
```

Agent se tu chuyen sang folder ngach phu hop. File chua ro license se vao `_Needs-License-Check`.

## Simple SaaS file workflow

Neu khong biet file SaaS nen bo vao dau, cu vut tat ca vao:

```txt
C:\Users\Admin\Documents\warriorplus MMO\Agent PLR Saas\saas_files\_INBOX_DROP_HERE
```

Sau do chay `python app.py` va chon:

```txt
14. Auto-sort SaaS inbox
```

Agent se tu chuyen sang `ideas`, `specs`, `mockups`, `code_samples`, `research`, `pricing`, `validation`, hoac `whitelabel`.

## Agent brain / knowledge base

Neu muon agent khong phai doc lai kho raw PLR/SaaS nang hang chuc GB moi lan chay, build local brain database:

```bash
uv run --with-requirements requirements.txt python app.py
```

Sau do chon:

```txt
16. Build/update agent brain
17. Show agent brain summary
18. Search agent brain
```

Brain duoc luu tai:

```txt
database/agent_brain.sqlite
```

Day la SQLite full-text search database. Agent se dung brain context cho cac chuc nang tao sales page, outline, bonus stack, launch assets, SaaS plan va idea theo keyword. Raw file van nen giu cho den khi ban da kiem tra brain search hoat dong dung.

Menu `16` cung tao media/design catalog truoc khi ingest. Catalog nay dai dien cho video, audio, anh, PSD, font va binary asset bang text metadata nhe, de brain biet asset ton tai va nam o dau. Neu muon noi dung transcript/OCR that su tu video/anh, can cai them ffmpeg/Whisper/OCR engine roi chay buoc transcribe/OCR rieng.

## Full media brain run

De rut text tu anh/video/audio va rebuild brain mot luot, chay:

```powershell
.\run_full_media_brain.ps1
```

Script nay co resume theo output da tao trong `database/media_extracted_text`, nen neu bi dung giua chung thi chay lai se tiep tuc. Buoc nay co the mat nhieu gio vi phai OCR hang ngan anh va transcribe hang tram video/audio.

Sau khi OCR/transcribe/rebuild brain xong, script se tu move 2 inbox raw vao:

```txt
G:\file_backup_PLR_Saas
```

Neu muon move raw inbox ngay ca khi media extraction chua xong:

```powershell
.\backup_raw_inboxes.ps1 -Force
```

## WarriorPlus workflow

Chay app:

```powershell
uv run --with-requirements requirements.txt python app.py
```

Menu moi:

```txt
19. Build WarriorPlus PLR/SaaS launch plan
20. Export AI PLR Rebrand Kit pack
21. Show 3 product launch workflow agents
22. Create/refresh workflow agent files and input folders
```

Dung `19` de tao launch plan tu brain. Dung `20` de tao product pack gom blueprint, checklist, prompt pack, sale page template, launch checklist, email swipes, bonus stack, score calculator, JV page va SaaS roadmap.

## Product launch workflow agents

Agent files duoc luu tai:

```txt
agents/
  01_build_product_agent.md
  02_jv_manager_agent.md
  03_sale_page_agent.md
```

Input files cho workflow moi duoc luu tai:

```txt
input_files/agent_workflows/
  01_build_product/
  02_jv_manager/
  03_sale_page/
```

Moi agent co `_inbox` de tha nhanh file chua phan loai va cac thu muc step theo dung so do workflow.

## Dung chung voi Codex / GPT-5.5

Dung Codex nhu operator/developer agent:

```txt
1. Bao Codex chay .\run_full_media_brain.ps1 neu can rut het raw media thanh brain.
2. Bao Codex mo app va dung menu 19/20 de tao offer pack.
3. Bao Codex sua code khi can them workflow moi.
4. Dung GPT-5.5/OpenAI API trong app neu muon output copywriting chat luong cao hon heuristic local.
```

Trong app, model OpenAI lay tu bien moi truong:

```powershell
$env:OPENAI_API_KEY="sk-..."
$env:OPENAI_MODEL="ten-model-ban-co-quyen-dung"
uv run --with-requirements requirements.txt python app.py
```

Neu dung model Codex qua Responses API, set them:

```powershell
$env:OPENAI_API_MODE="responses"
$env:OPENAI_MODEL="ten-codex-model-trong-api-account-cua-ban"
uv run --with-requirements requirements.txt python app.py
```

Neu ban dang dung Codex/GPT-5.5 trong VS Code, cach ket hop tot nhat la de Codex lam operator: sua code, chay script, tao pack, doc report va toi uu workflow. App local se la engine san xuat offer/brain, con Codex la dev agent dieu khien va nang cap no.

## 3 role brains tu input_files

Neu co du lieu chia theo 3 thu muc:

```txt
input_files/01_BUILD_PRODUCT
input_files/02_JV_MANAGER
input_files/03_SALE_PAGE
```

Chay full build:

```powershell
.\run_three_agent_brains.ps1
```

Script se tao 3 brain rieng:

```txt
database/agent_brains/build_product/build_product_brain.sqlite
database/agent_brains/jv_manager/jv_manager_brain.sqlite
database/agent_brains/sale_page/sale_page_brain.sqlite
```

Moi brain co agent profile va sub-agent roles trong:

```txt
database/agent_brains/<agent_key>/agent_profile.md
```

Sau khi ca 3 brain build xong va media extraction duoc verify, script moi move raw input sang:

```txt
G:\file_backup\agent_input_backup_<timestamp>
```

Trong app:

```txt
23. Show 3 role brain summaries
24. Search a role brain
```

## Scoring formula

```txt
Final Score =
Demand Score x 25%
+ WarriorPlus Fit x 25%
+ Rebrand Potential x 20%
+ SaaS Potential x 15%
+ Ease of Creation x 10%
- Risk Score x 5%
```

## Recommended path

```txt
Internal Agent -> Digital Product -> WarriorPlus test -> Micro SaaS / Membership
```

San pham dau tien nen test:

```txt
AI PLR Rebrand Kit
```

Sau nay nang thanh SaaS:

```txt
PLR Rebrand Engine
Upload PLR -> Analyze -> Rebrand -> Create Offer -> Generate Funnel -> Export Pack
```

## Safe forum workflow

Use forums as research sources for title, niche, format, views/replies, and offer angles. Only download files you are allowed to access and use.

Recommended flow:

1. Open the thread manually in your browser.
2. Check the visible license/right note.
3. Download only the file you are allowed to use.
4. Keep any license/readme file with the product.
5. Run menu option `11. Import downloaded PLR files`.
6. Run `10. License/risk audit` before turning anything into an offer.

Files without a license hint in the filename are imported into:

```txt
plr_files/_Needs-License-Check/
```

## Dung OpenAI API

Neu co API key, set bien moi truong:

```powershell
$env:OPENAI_API_KEY="sk-..."
$env:OPENAI_MODEL="gpt-4.1-mini"
python app.py
```

Neu chua co API key, agent van chay bang bo cham diem heuristic.

## Ghi chu an toan

Agent nay khong khuyen nghi copy nguyen ban neu license khong ro. Cach dung tot nhat la lay PLR lam nen, rebrand, viet lai angle, bo sung bonus va tao offer moi co gia tri rieng.

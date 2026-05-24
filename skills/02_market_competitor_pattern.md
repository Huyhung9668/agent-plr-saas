# Market / Competitor Pattern

## Purpose
Điều phối và sinh nội dung cho Step 2: Market / Competitor Pattern trong hệ thống WarriorPlus AI Printables/KDP/PLR Product Builder.

## When To Use
Dùng khi user gọi rõ `Step 2` / `Bước 2` hoặc dùng intent tự nhiên khớp với skill này.

## Trigger Keywords
- `market`
- `competitor`
- `pattern`
- `đối thủ`
- `doi thu`

## Required Inputs
- `product_name` hoặc active project hiện tại.
- `active_project_path` dưới `exports/products/<project_slug>/`.
- User goal/message hiện tại.

## Optional Inputs
- Project files hiện có trong active project.
- Prior step outputs chỉ khi nằm trong active project.
- Notes từ buyer/support nếu user cung cấp.

## Project Context Rules
- Chỉ đọc/ghi trong `active_project_path`.
- `Product:` trong prompt thắng mọi memory/history cũ.
- Không dùng project cũ trừ khi user ghi rõ compare/reuse/copy from previous project.
- Không nhắc `AI Etsy Printable Bundle Builder` nếu đó không phải active product hoặc yêu cầu compare.

## AI/API Rule
- Route type: `ai_content`.
- Nếu route type là `ai_content` hoặc `hybrid_action`, bắt buộc `api_called=true`, `from_cache=false`, `prebuilt_answer_used=false`, `old_answer_reused=false`.
- AI API sinh nội dung mới; template chỉ là schema/guard, không phải final answer cứng.

## Tool/Fast Path Rule
- Fast path chỉ được route, lock project, đọc manifest, ghi file/export tool.
- Tool-only skill không được giả vờ AI đã phân tích nếu không gọi API.
- Hybrid skill phải chạy tool + AI report nếu prompt yêu cầu phân tích/giải thích/audit.

## Step-by-Step Procedure
1. Xác nhận explicit step = 2 hoặc keyword match.
2. Resolve product từ `payload.product_name` → dòng `Product:` → active project.
3. Lock `active_project_path` và scan file liên quan trong project.
4. Build guard prompt theo schema skill này.
5. Chạy AI/tool theo route type `ai_content`.
6. Ghi output/missing assets/quality gate vào response và debug.

## Output Schema
```txt
PRODUCT USED:
STEP USED: 2 — Market / Competitor Pattern
FILES USED:
FILES CREATED/UPDATED:
MAIN RESULT:
QUALITY GATE:
MISSING ASSETS:
NEXT FIX:
REQUEST DEBUG:
- selected_skill: 02_market_competitor_pattern
- route_type: ai_content
- api_called:
- from_cache: false
- prebuilt_answer_used: false
- old_answer_reused: false
```

## Files To Read
- `project_state.json`
- Active project markdown/csv/txt files needed for Step 2

## Files To Create/Update
- No fixed file; write response/report as requested.

## Quality Checklist
- [ ] Đúng Step 2, không route sang step khác.
- [ ] Đúng product/active project.
- [ ] Không dùng cache/answer cũ cho content.
- [ ] Có files used/missing rõ ràng.
- [ ] Có quality gate pass/fail thật.

## Failure Conditions
- Route sai step hoặc chạy keyword fallback dù user có explicit step.
- Dính product cũ hoặc đọc file ngoài active project.
- Content request mà `api_called=false`.
- Báo PASS giả khi thiếu asset.

## Test Prompts
- `Product: AI Coloring Page Niche Pack

Step 2 Market / Competitor Pattern cho product hiện tại.`
- `market cho active project, chấm điểm và nêu missing assets.`
- `Hỏi Step 2 mà trả step khác là lỗi gì? Debug route, không dùng mẫu cũ.`

## Scoring Rubric /10
1. Trigger rõ.
2. Input rõ.
3. Output schema rõ.
4. Project isolation đúng.
5. AI/API rule đúng.
6. Tool/hybrid rule đúng.
7. Anti-stale đúng.
8. Quality gate rõ.
9. Có ít nhất 3 test prompt.
10. Có repair instruction.

## Repair Instructions
- Nếu route sai: cập nhật `skills/_index.json` và `product_pipeline.resolve_skill_route`.
- Nếu thiếu input/schema: bổ sung section tương ứng trong file skill.
- Nếu dính product cũ: tăng guard Project Context Rules và test product isolation.
- Nếu content không gọi API: đổi route_type hoặc backend execution để bắt `api_called=true`.

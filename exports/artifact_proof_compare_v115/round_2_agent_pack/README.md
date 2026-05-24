# README.md

Source: agent raw benchmark output.

This file could not be cleanly section-extracted, so the relevant raw answer is preserved below for audit.

## Raw Content

# DATA USED

| Mục | Dữ liệu dùng |
|---|---|
| Query used | `AI Printables KDP Prompt Agent`, `market-pattern`, `product-blueprint`, `WarriorPlus`, `AI replace risk`, `license-check` |
| Retrieved chunks | 36 đoạn context trong request |
| Brain Files Loaded | `brain/AI_PRINTABLES_KDP_BRAIN.json`, `brain/AI_PRINTABLES_KDP_BRAIN.md`, `brain/MARKET_PATTERNS.md`, `brain/COMPETITOR_PATTERNS.md`, `brain/OFFER_ANGLES.md` |
| Patterns found | Prompt pack đơn thuần dễ bị AI thay thế; pack mạnh cần workflow, ví dụ, checklist, fix prompts, listing kit, license note. Niche printables/KDP/Canva/PLR có tín hiệu từ coloring book, digital planner, Canva template, KDP/POD/Etsy tool ZIP. |
| Confidence | Trung bình-khá cho pattern đóng gói; thấp cho giá/market proof vì nguồn không có số bán/giá live. |
| What is inferred | FE $17–$27, bump $7–$17, OTO $47–$97 là launch heuristic, không phải dữ liệu chứng minh từ nguồn. |
| What is not proven | Không có bằng chứng sales, buyer, refund rate, JV approval, live checkout, platform ranking, quyền PLR cụ thể. |

# SKILLS USED

`#market-pattern`, `#product-blueprint`, `#deep-file-writer`, `#sales-page`, `#warriorplus-listing`, `#jv-pack`, `#delivery-support`, `#buyer-test`, `#ai-replace-risk`, `#refund-risk`, `#license-check`, `#public-launch-audit`

# PRODUCT NAME

**Seasonal Printable Launch Sprint**  
Góc mới Round 2: bộ triển khai giúp người mới tạo một mini bundle printable theo mùa cho Etsy/KDP/Payhip/lead magnet, không bán “1000 prompts” thô.

**Buyer:** beginner digital product seller, Canva/KDP/Etsy creator, PLR reseller.  
**Safe promise:** giúp tạo, kiểm tra và đóng gói một seasonal printable mini bundle bằng AI + checklist + listing assets, không hứa doanh thu.  
**FE price inference:** $17.  
**Usage rights:** buyer có thể dùng output tự tạo cho sản phẩm riêng; không được bán lại nguyên bộ file này dưới dạng PLR trừ khi có license riêng.

---

# FILE CONTENTS

## 00_Start_Here.md

```md
# Start Here - Seasonal Printable Launch Sprint

Mục tiêu: tạo một mini bundle printable theo mùa trong 1-2 ngày:
1. Chọn mùa/sự kiện: New Year, Spring Cleaning, Summer Travel, Back To School, Halloween, Christmas.
2. Chọn buyer: mom planner user, teacher, coach, small business, Etsy printable buyer.
3. Tạo 5-10 trang printable: planner, checklist, tracker, worksheet, gift tag, habit sheet.
4. Kiểm tra bản quyền, trademark, font, Canva element.
5. Đóng gói PDF + PNG preview + listing copy.

Không dùng: nhân vật nổi tiếng, thương hiệu, quote có bản quyền, claim giáo dục/trị liệu quá mức.
```

## 01_Workflow_Map.md

```md
# 7-Step Workflow Map

1. Niche Pick: chọn 1 mùa + 1 buyer + 1 outcome.
Example: Back To School + busy moms + morning routine checklist.

2. Bundle Plan:
- 1 cover
- 3 planner pages
- 2 checklists
- 1 tracker
- 1 instruction page

3. Prompt Generate: dùng prompt trong 02_Prompt_Library.md.

4. Design Build: Canva/PowerPoint/Google Slides, size Letter + A4.

5. QC Pass:
- readable
- printer friendly
- no trademark
- no unsupported claims
- placeholders removed

6. Listing Pack:
- title
- description
- 5 benefit bullets
- tags
- mockup ideas

7. Delivery:
- PDF printable
- PNG previews
- README
- license note
```

## 02_Prompt_Library.md

```md
# Prompt Library

## Prompt 1 - Seasonal Bundle Planner
Role: You are a printable product strategist.
Input: season=[SEASON], buyer=[BUYER], outcome=[OUTCOME].
Task: Create a 7-page printable bundle plan.
Constraints: no trademarks, no medical/legal/financial c

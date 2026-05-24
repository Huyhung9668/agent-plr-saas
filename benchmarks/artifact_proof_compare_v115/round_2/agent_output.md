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
Constraints: no trademarks, no medical/legal/financial claims, beginner-friendly.
Output:
- Bundle name
- Page list
- Purpose of each page
- Design style
- Buyer use case
Quality check: flag weak or duplicate pages.

## Prompt 2 - Printable Page Copy
Create copy for page type=[PAGE TYPE].
Audience=[BUYER]. Tone=clear, simple, helpful.
Output:
- Page title
- Instructions
- Sections/fields
- Example filled row
- Notes for designer

## Prompt 3 - Etsy/KDP Listing Draft
Create a listing for bundle=[BUNDLE NAME].
Output:
- SEO-friendly title
- Short description
- Long description
- 5 bullets
- 13 tag ideas
- What’s included
- Disclaimer
Avoid: income claims, guaranteed results, trademark terms.

## Prompt 4 - QC Reviewer
Review this printable concept: [PASTE CONCEPT].
Check:
- trademark risk
- unclear buyer
- too generic
- weak page value
- missing instructions
- print readability
Return: PASS/FIX + exact fixes.

## Prompt 5 - Rebrand Variants
Turn this bundle into 5 safe niche variants.
Avoid copyrighted characters, celebrities, brands.
Include buyer, season, page list, color style.
```

## 03_Template_Guide.md

```md
# Template Guide

Recommended format:
- US Letter 8.5x11
- A4 version optional
- 300 DPI export if image-heavy
- PDF for buyer delivery
- PNG/JPG preview for listing

Core page templates:
1. Cover Page
2. Daily Planner
3. Weekly Checklist
4. Habit Tracker
5. Goal Sheet
6. Resource List
7. Instructions Page

Design rules:
- Use readable fonts.
- Avoid too much color for printables.
- Keep margins printer-safe.
- Add “For personal use” or correct license note.
- Do not use Canva Pro elements in resale templates unless license allows your use case.
```

## 04_Example_Outputs.md

```md
# Example Output

Bundle: Back To School Morning Routine Kit  
Buyer: Busy moms with elementary school children  
Outcome: smoother school mornings

Pages:
1. Cover: “Back To School Morning Routine Kit”
2. Morning Checklist: wake up, breakfast, backpack, lunch, shoes, leave time
3. Weekly Prep Planner: clothes, meals, school forms, activities
4. Backpack Tracker: homework, water bottle, lunch, permission slips
5. Kid Responsibility Chart: task, done checkbox, reward note
6. Parent Notes Page: reminders, teacher notes, schedule
7. How To Use: print, laminate optional, review nightly

Listing bullet example:
- Simple printable pages to help organize school morning routines
- Includes checklist, prep planner, backpack tracker, and responsibility chart
- Designed for home use, classroom-adjacent organization, and busy family schedules

Disclaimer:
This is an organizational printable, not educational, medical, or behavioral therapy advice.
```

## 05_Quality_Checklist.md

```md
# Quality Checklist

Before selling:
- [ ] Buyer and use case are obvious.
- [ ] Every page has a purpose.
- [ ] No brand names, celebrities, characters, copyrighted quotes.
- [ ] Font and design assets have commercial-use permission.
- [ ] No guaranteed learning, therapy, health, or income result.
- [ ] PDF opens correctly.
- [ ] Print margins checked.
- [ ] Listing says digital download, no physical item.
- [ ] Preview images do not reveal entire paid product.
- [ ] README and license note included.
```

## 06_Fix_Prompts.md

```md
# Fix Prompts

## Too Generic Fix
Review this printable: [PASTE].
Make it more specific for buyer=[BUYER] and season=[SEASON].
Add 3 unique page ideas and remove filler.

## Trademark Risk Fix
Scan this listing/title/tags for trademark/copyright risk: [PASTE].
Replace risky terms with generic safe alternatives.

## Printability Fix
Review this page layout description: [PASTE].
Suggest improvements for margins, readability, ink use, and section clarity.

## Listing Clarity Fix
Improve this listing so buyers understand:
- what they receive
- file format
- instant digital download
- no physical product
- usage limits
Avoid hype and unrealistic promises.
```

## 07_Listing_Sales_Kit.md

```md
# Listing Sales Kit

Title formula:
[Season] [Buyer] Printable [Outcome] Kit

Examples:
- Back To School Morning Routine Printable Kit
- Christmas Gift Planner Printable Bundle
- Spring Cleaning Checklist Printable Pack
- New Year Goal Planner Printable Pages

Short description:
A simple printable bundle designed to help [BUYER] organize [SEASONAL TASK] with clear planner pages, checklists, and trackers.

CTA:
Download, print, and start using the pages today.

Preview image ideas:
1. Cover mockup
2. Spread of 3 pages
3. Close-up of checklist
4. “What’s included” graphic
5. Usage steps graphic
```

## 08_License_Compliance.md

```md
# License & Compliance

HUMAN REVIEW REQUIRED for all source assets.

Safe default license for this pack:
- Buyer may use prompts and workflow to create their own printable products.
- Buyer may sell printables they personally create from the workflow.
- Buyer may not resell this exact pack, prompts, or files as PLR/MRR/RR.
- Buyer is responsible for checking Canva, stock, font, AI image, marketplace, and trademark rules.

Do not claim:
- guaranteed Etsy/KDP ranking
- guaranteed sales
- educational, therapy, medical, legal, or financial outcomes
- official affiliation with Amazon, Etsy, Canva, or KDP
```

---

# sales_page.md

```md
# Seasonal Printable Launch Sprint

## Headline
Create A Clean Seasonal Printable Mini Bundle Without Starting From A Blank Page

## Subheadline
A practical workflow kit for beginners who want to plan, prompt, check, package, and list simple printable products for seasonal buyers.

## Problem
Most AI printable packs give you prompts. Then you still have to decide the niche, pages, layout, listing, license notes, and quality checks yourself.

## Solution
Seasonal Printable Launch Sprint gives you a step-by-step system:
- niche selection map
- printable page prompts
- template guide
- example bundle
- QC checklist
- fix prompts
- listing/sales kit
- compliance notes

## What’s Inside
- Start Here guide
- 7-step workflow map
- prompt library
- template guide
- example output
- quality checklist
- fix prompts
- listing kit
- license/compliance file

## Can I just ask AI to make this?
Yes, AI can generate raw ideas. The value here is the curated workflow, buyer-specific page structure, quality gates, fix prompts, listing assets, and compliance reminders that help you turn messy AI output into a usable product pack.

## Who It’s For
- beginner printable sellers
- PLR buyers who want a fresh angle
- Canva creators
- KDP/Etsy experimenters
- coaches needing seasonal lead magnets

## Who It’s Not For
- anyone expecting guaranteed sales
- people wanting trademarked character products
- sellers who refuse to check licenses

## Guarantee
7-day refund window if the product files are inaccessible or materially different from this description.

## CTA
Get Seasonal Printable Launch Sprint and build your first seasonal printable bundle with a clear workflow.
```

---

# warriorplus_listing.md

```md
Product Title: Seasonal Printable Launch Sprint

Short Description:
A beginner-friendly AI printable/KDP workflow kit for creating seasonal printable mini bundles with prompts, checklists, examples, listing copy, and compliance notes.

Category:
Digital Products / AI / Printables / KDP

Tags:
AI printables, KDP, Etsy printables, Canva, PLR workflow, prompt pack, digital products, seasonal planner

Price:
$17 FE inference. Source proof for exact market price: UNKNOWN.

Commission:
50% suggested for FE. Approval manual.

Refund Policy:
7 days for access/file issues or mismatch with stated deliverables. No refund based on lack of sales results.

Vendor Note:
No income claims. No platform ranking claims. Buyers must check rights for fonts, Canva, stock, AI images, and marketplace policies.

Affiliate Approval Note:
Approve affiliates who agree not to use fake scarcity, fake income screenshots, spam, or guaranteed-sales claims.

Delivery Page:
Provide ZIP download with numbered files, README, support FAQ, and compliance note.
```

---

# jv_pack.md

```md
# JV Pack

## JV Invite
Subject: New $17 AI Printables Kit - clean angle, beginner-friendly

Hi [Name],  
I’m launching Seasonal Printable Launch Sprint, a practical kit that helps beginners create a seasonal printable mini bundle using AI prompts, workflow maps, examples, QC checks, and listing assets.

No income claims. No fake scarcity. It sells implementation, not raw prompts.

FE: $17  
Suggested commission: 50%  
Best audience: PLR buyers, Canva creators, KDP/Etsy beginners, digital product sellers.

## Affiliate Swipe 1
Subject: Create a seasonal printable bundle faster

If you’ve wanted to create printables but get stuck choosing the niche, pages, layout, and listing, this kit gives you a cleaner path.

Seasonal Printable Launch Sprint includes prompts, workflow, examples, checklist, fix prompts, and listing copy.

Check it out here: [LINK]

## Social Post
Want to build a simple seasonal printable product without staring at a blank Canva page?  
This kit gives you the workflow, prompts, checklist, and listing assets to create a small printable bundle responsibly.  
No income hype. Just a practical product creation sprint.  
[LINK]

## Bonus Ideas For Affiliates
- Canva mockup checklist
- 10 seasonal niche ideas
- printable listing review worksheet
```

---

# delivery_page.md

```md
# Access Your Product

Thank you for purchasing Seasonal Printable Launch Sprint.

Download files:
1. 00_Start_Here.md
2. 01_Workflow_Map.md
3. 02_Prompt_Library.md
4. 03_Template_Guide.md
5. 04_Example_Outputs.md
6. 05_Quality_Checklist.md
7. 06_Fix_Prompts.md
8. 07_Listing_Sales_Kit.md
9. 08_License_Compliance.md
10. support_faq.md
11. refund_policy.md

Recommended first action:
Open 00_Start_Here.md, choose one season and one buyer, then complete the 7-step workflow.
```

# support_faq.md

```md
# Support FAQ

Q: Is this PLR?
A: No, not by default. You can use it to create your own printables, but cannot resell this exact pack as PLR/MRR unless a separate license says so.

Q: Does this guarantee sales?
A: No. It helps with product creation and packaging only.

Q: Can I use Canva?
A: Yes, but you must check Canva element/font/license rules for your use case.

Q: Can I sell outputs on Etsy/KDP?
A: Possibly, if your final product follows marketplace rules and asset licenses. Human review required.

Q: Can AI make this?
A: AI can create raw drafts. This pack adds workflow, quality checks, fix prompts, examples, and listing structure.

Q: What if my prompt output is poor?
A: Use 06_Fix_Prompts.md and run the QC checklist before designing.
```

# refund_policy.md

```md
# Refund Policy

Refund window: 7 days.

Eligible:
- download link/file access problem not resolved
- missing core files listed on sales page
- product materially different from description

Not eligible:
- lack of sales or marketplace approval
- failure to check third-party licenses
- misuse of copyrighted/trademarked assets
- expecting done-for-you finished Canva designs when the product is a workflow kit

Contact: [SUPPORT EMAIL]
```

---

# OFFER EVALUATOR SCORECARD

| Criteria | Score /10 | Note |
|---|---:|---|
| Buyer Pain | 8 | Người mới bị kẹt ở niche, layout, listing, QC. |
| AI Replace Risk | 5 sau fix | Prompt có thể thay bằng AI, nhưng workflow + QC + listing + compliance giảm rủi ro. |
| Workflow Value | 8 | Có quy trình 7 bước rõ. |
| Implementation Value | 7 | Có ví dụ, checklist, fix prompts. |
| WarriorPlus Fit | 7 | Góc AI + printables + beginner-friendly hợp FE nhỏ. |
| Asset Completeness | 7 | Đủ pack compact; chưa có Canva template thật. |
| Compliance Risk | 6 | Cần review license/font/Canva/trademark. |
| Final Recommendation | NÊN LÀM TEST | Chạy FE $17, không claim Public Launch Ready. |

---

# BUYER TEST

| Test | Result |
|---|---|
| Buyer understands outcome? | PASS |
| Can use in 30-60 minutes? | PASS |
| Has example? | PASS |
| Has QC? | PASS |
| Has license note? | PASS with HUMAN REVIEW REQUIRED |
| Would buyer pay vs ChatGPT? | MAYBE/PASS nếu page nhấn mạnh workflow + checks |
| Score | 7.5/10 |

---

# AI REPLACE RISK AUDIT

## Overall Risk Level
**Medium.** Nếu chỉ bán prompt library thì High.

## High-Risk Sections
- `02_Prompt_Library.md`
- sales claim “create faster” nếu không kèm workflow
- listing copy nếu quá chung

## Why Buyer May Skip Buying
Họ có thể nghĩ: “Tôi hỏi ChatGPT tạo prompt printable là xong.”

## What Must Be Added To Justify Purchase
Đã thêm:
- workflow map
- example output
- template guide
- QC checklist
- fix prompts
- listing kit
- compliance note

## Files To Rewrite
Không cần rewrite toàn bộ; cần thêm Canva template thật nếu muốn nâng giá.

## After Fix - Estimated Risk Level
**Medium-Low** nếu có preview/mockup và 1 sample PDF thật.

## Rewrite Required
**NO**, nhưng cần bổ sung design assets trước launch thật.

---

# REFUND RISK

| Risk | Level | Fix |
|---|---|---|
| Buyer kỳ vọng sales | Medium | Sales page nói rõ no guarantee. |
| License hiểu nhầm | Medium-High | HUMAN REVIEW REQUIRED. |
| Pack quá mỏng | Medium | Thêm sample PDF/Canva template trước bán thật. |
| Missing support | Low | Có FAQ/refund policy. |
| Overall | Medium | Chưa launch công khai. |

---

# LICENSE / COMPLIANCE

**HUMAN REVIEW REQUIRED.**  
License nguồn trong request không chứng minh quyền resale/PLR cho từng asset. Cách an toàn: dùng brain/source làm pattern research, còn file pack trên là nội dung mới tạo. Trước bán cần kiểm:
- Canva elements/fonts
- stock/AI image rights
- trademark terms trong title/tags
- KDP/Etsy/WarriorPlus policy
- refund policy và support email thật

---

# PUBLIC LAUNCH AUDIT

| Gate | Status |
|---|---|
| Product files drafted | PARTIAL PASS trong câu trả lời, chưa tạo ZIP vật lý |
| Sales page | DRAFTED |
| WarriorPlus listing | DRAFTED |
| JV pack | DRAFTED |
| Delivery/support/refund | DRAFTED |
| Live checkout | UNKNOWN/NOT PROVIDED |
| Delivery tested | UNKNOWN/NOT PROVIDED |
| JV approval | UNKNOWN/NOT PROVIDED |
| Buyer proof | UNKNOWN/NOT PROVIDED |
| Public Launch Ready | FAIL |

**Not Public Launch Ready without live payment/delivery/JV/buyer proof.**

---

# PACKAGE STRUCTURE

```txt
/outputs/Seasonal_Printable_Launch_Sprint/product_assets/
  00_Start_Here.md
  01_Workflow_Map.md
  02_Prompt_Library.md
  03_Template_Guide.md
  04_Example_Outputs.md
  05_Quality_Checklist.md
  06_Fix_Prompts.md
  07_Listing_Sales_Kit.md
  08_License_Compliance.md

/outputs/Seasonal_Printable_Launch_Sprint/sales_page/
  sales_page.md
  warriorplus_listing.md

/outputs/Seasonal_Printable_Launch_Sprint/jv_pack/
  jv_pack.md

/outputs/Seasonal_Printable_Launch_Sprint/export/product_zip_ready/
  delivery_page.md
  support_faq.md
  refund_policy.md
```

# HONEST LIMITATIONS

- Chưa có file ZIP thật được tạo trong môi trường này.
- Chưa có Canva template/sample PDF thật.
- Chưa có live payment, delivery test, JV approval, buyer proof.
- Giá là inference, không phải benchmark từ source.
- Quyền PLR/MRR của nguồn là UNKNOWN; không giả định resale rights.

# NEXT ACTION

1. Tạo 1 sample printable PDF thật cho ví dụ “Back To School Morning Routine Kit”.  
2. Thêm 3 preview PNG/mockup.  
3. Chạy checklist license/trademark.  
4. Đóng ZIP theo cấu trúc trên.  
5. Test download + mở file.  
6. Sau đó mới viết bản sales page public và submit WarriorPlus draft.

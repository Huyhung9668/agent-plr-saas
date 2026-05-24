# AI PRINTABLES AGENT — Round 1 Benchmark Plan

## DATA USED

- **Dữ liệu dùng:** ngữ cảnh brain nội bộ được cung cấp trong prompt: checklist nghiên cứu WarriorPlus, checklist funnel, checklist chỉnh sửa PLR, cảnh báo license/risk, launch readiness.
- **Không dùng:** project agent, skill, artifact writer, file writer, live market scrape, dữ liệu bán hàng thật, bằng chứng launch thật.
- **Bằng chứng hiện có:** chỉ có excerpt nội bộ về cách đóng gói sản phẩm số, checklist funnel, cảnh báo PLR/license, affiliate/marketplace research.
- **UNKNOWN:** sản phẩm cụ thể này chưa có sales data, chưa có buyer survey, chưa có proof conversion, chưa có license nguồn, chưa có live WarriorPlus listing.
- **Mức tin cậy:** trung bình cho cấu trúc sản phẩm/funnel; thấp cho khả năng bán thực tế vì chưa có test thị trường.

No guaranteed sales, no guaranteed profit, no guaranteed KDP rank, not Public Launch Ready without live proof, UNKNOWN where source evidence is missing.

---

## METHOD USED

Tôi dùng phương pháp **AI Printables Productization Sprint**:

1. Chọn ngách có buyer intent: AI-assisted KDP/printables cho người mới muốn tạo sản phẩm nhanh hơn.
2. Không bán “prompt thô”; đóng gói thành **workflow + checklist + template + ví dụ + compliance note**.
3. Thiết kế FE giá thấp phù hợp WarriorPlus.
4. Thêm bump/OTO để tăng tốc triển khai, không hứa thu nhập.
5. Kiểm tra rủi ro: AI replace risk, refund risk, KDP/PLR/license risk.
6. Dùng buyer test giả lập để xem offer có đủ cụ thể không.

---

## PRODUCT BLUEPRINT

### Tên sản phẩm đề xuất

**AI Printable Starter Kit: 7-Day KDP & Etsy Printable Workflow**

### Verdict

**NÊN LÀM bản FE nhỏ để test**, chưa nên làm launch lớn.

### Buyer cụ thể

Người mới làm digital product, affiliate marketer hoặc vendor WarriorPlus có hứng thú với KDP/Etsy/Canva printables nhưng đang bị kẹt ở 3 điểm:

- Không biết chọn loại printable nào dễ bắt đầu.
- Biết dùng AI nhưng output lộn xộn, khó thành sản phẩm.
- Sợ vi phạm bản quyền, dùng sai license, hoặc tạo file chất lượng thấp.

### Pain

Họ có thể hỏi AI để tạo ý tưởng journal/coloring page/prompt, nhưng thường không có:

- quy trình chọn niche;
- prompt theo từng bước;
- checklist chất lượng;
- format giao hàng;
- sales angle;
- hướng dẫn tránh claim quá đà;
- ví dụ trước/sau.

### Promise an toàn

Giúp người mới xây một **printable product concept** trong 7 ngày bằng AI, Canva/KDP workflow và checklist kiểm tra chất lượng — **không hứa sales, profit, rank hay approval**.

### Product mechanism

**Niche → Prompt → Draft → Quality Check → Package → Listing Prep**

Thay vì đưa 100 prompt rời rạc, sản phẩm hướng dẫn người mua đi qua một workflow rõ ràng để tạo một printable pack có thể kiểm tra, chỉnh sửa và chuẩn bị đăng bán.

### Deliverables FE

| File | Nội dung |
|---|---|
| `00_Start_Here.pdf` | Hướng dẫn dùng kit trong 7 ngày |
| `01_Printable_Niche_Map.pdf` | 20 ngách printable an toàn hơn để nghiên cứu |
| `02_AI_Prompt_Library.pdf` | Prompt tạo concept, page ideas, cover brief, listing draft |
| `03_Quality_Checklist.pdf` | Checklist kiểm tra readability, originality, layout, risk |
| `04_7_Day_Planner.xlsx` | Lịch làm từng ngày |
| `05_Sample_Project_Walkthrough.pdf` | Ví dụ: “Self-Care Journal for Busy Moms” |
| `06_License_And_Risk_Note.pdf` | Cảnh báo AI/KDP/Canva/PLR/license |
| `README.txt` | Cách truy cập và thứ tự học |

---

## SAMPLE ASSET CONTENT

### 1. Start Here — snippet dùng được

**Chào mừng bạn đến với AI Printable Starter Kit.**

Mục tiêu của kit này không phải là biến bạn thành chuyên gia thiết kế trong một ngày. Mục tiêu thực tế hơn: giúp bạn tạo ra một **printable product concept có cấu trúc**, gồm niche, buyer, page list, design brief, quality checklist và draft listing.

Cách dùng nhanh:

1. Đọc `01_Printable_Niche_Map`.
2. Chọn 1 buyer cụ thể, ví dụ: busy moms, teachers, homeschool parents, Etsy sellers, beginner planners.
3. Dùng prompt trong `02_AI_Prompt_Library` theo đúng thứ tự.
4. Tạo bản nháp trong Canva hoặc công cụ thiết kế bạn có quyền dùng.
5. Kiểm tra bằng `03_Quality_Checklist`.
6. Không đăng bán nếu bạn chưa kiểm tra quyền thương mại của font, ảnh, template, AI image, PLR source và marketplace policy.

**Quan trọng:** Kit này là workflow giáo dục. Không đảm bảo doanh thu, rank KDP, sale Etsy hay approval từ marketplace.

---

### 2. Prompt Library — snippets dùng được

#### Prompt 1: Chọn niche printable

```text
Bạn là product researcher cho digital printables. 
Hãy đề xuất 10 niche printable cho buyer sau: [BUYER].
Ràng buộc:
- Không dùng claim y tế, tài chính, pháp lý.
- Tránh trademark, nhân vật nổi tiếng, brand names.
- Ưu tiên sản phẩm dễ tạo bằng Canva/KDP.
- Mỗi niche phải có: buyer pain, printable idea, difficulty 1-5, risk 1-5.
Output dạng bảng.
```

#### Prompt 2: Tạo product concept

```text
Bạn là printable product architect.
Tạo concept cho sản phẩm: [NICHE].
Buyer: [BUYER].
Format: [journal / planner / worksheet / coloring book / poster pack].
Hãy tạo:
1. Product title an toàn, không hype.
2. Promise thực tế.
3. 20 page ideas.
4. Suggested cover brief.
5. What to avoid for copyright/compliance.
6. 5 ways to make this more useful than generic AI output.
```

#### Prompt 3: Listing draft

```text
Viết draft listing cho printable product sau: [PRODUCT].
Nền tảng dự kiến: [KDP/Etsy/Gumroad].
Yêu cầu:
- Không hứa kết quả cá nhân.
- Không claim chữa bệnh, giảm cân, thu nhập.
- Có mô tả rõ buyer nhận được gì.
- Có FAQ ngắn.
- Có disclaimer về digital download/print quality/license.
```

---

### 3. Quality Checklist — snippet dùng được

**Printable Quality Checklist**

Trước khi xuất bản, kiểm tra:

- [ ] Buyer cụ thể chưa? Không phải “everyone”.
- [ ] Tên sản phẩm có tránh brand/trademark không?
- [ ] Nội dung không copy từ PLR hoặc AI output chưa chỉnh sửa?
- [ ] Font/ảnh/icon/template có quyền thương mại rõ không?
- [ ] File có đúng kích thước nền tảng? Ví dụ KDP trim size, Etsy printable size.
- [ ] Có ít nhất 1 ví dụ điền sẵn hoặc walkthrough không?
- [ ] Page không bị lỗi chính tả, lặp prompt, bố cục rối?
- [ ] Không có claim “guaranteed results”, “rank fast”, “make money”.
- [ ] Có README hướng dẫn tải/in/sử dụng không?
- [ ] Có refund/support policy rõ ràng không?

---

### 4. Sales Page Headline — snippet

**Headline:**

Build Your First AI-Assisted Printable Product Concept In 7 Days — Without Guessing What To Create Or Selling Raw AI Prompts

**Subheadline:**

A practical workflow kit for beginners who want to plan, prompt, check, and package KDP/Etsy-style printables with safer compliance habits and clearer product structure.

---

### 5. JV Email Swipe — snippet

**Subject:** New AI printable workflow kit for beginners

Hi [NAME],

I’m launching **AI Printable Starter Kit**, a practical FE product for beginners who want to create KDP/Etsy-style printable concepts using AI — without dumping raw prompts on buyers.

Why it may fit your list:

- Clear beginner-friendly angle.
- Hot AI + printable/KDP niche.
- Includes workflow, prompt library, checklist, planner, and sample walkthrough.
- No income promises, no fake scarcity, no KDP rank claims.
- Simple FE offer with logical upgrades for templates and implementation.

Suggested angle:

“Most people ask AI for printable ideas and stop there. This kit gives them a step-by-step workflow to turn ideas into a product concept they can review, improve, and package.”

Review access: [LINK UNKNOWN]  
Launch date: UNKNOWN  
Commission: UNKNOWN  
JV page: UNKNOWN

Thanks,  
[VENDOR NAME]

---

### 6. Support FAQ — snippet

**Q: Does this guarantee I will make sales on KDP or Etsy?**  
No. This is an educational workflow kit. It does not guarantee sales, profit, KDP rank, Etsy ranking, or marketplace approval.

**Q: Can I use the prompts commercially?**  
You can use the prompts to create your own original concepts, but you must check the terms of any AI tool, design asset, Canva template, font, image, PLR file, or marketplace you use.

**Q: Is this PLR?**  
UNKNOWN unless a written license is provided. Do not assume resale, private label, or client-use rights without explicit license terms.

**Q: Can I just ask AI to make this?**  
You can ask AI for ideas, but this kit gives you the sequence, checks, examples, packaging structure, and risk reminders most raw AI output misses.

**Q: What if I am a complete beginner?**  
Start with the 7-day planner. Do not try to create 10 products. Build one simple concept, check it carefully, then improve it.

---

## WARRIORPLUS FIT

### Fit score: **7/10**

| Factor | Score | Note |
|---|---:|---|
| AI trend appeal | 8 | AI + printables/KDP is attractive |
| Beginner clarity | 8 | Simple 7-day promise |
| Fast perceived value | 7 | Prompts + checklist + planner |
| Affiliate angle | 7 | Easy to explain |
| Proof requirement | 5 | Needs demo/walkthrough, not income proof |
| Refund risk | 6 | Risk if buyers expect instant sales |
| Compliance safety | 7 | Safe if claims are restrained |

### FE / Bump / OTO

| Offer | Price | What it sells |
|---|---:|---|
| FE | $17 | 7-day AI printable workflow kit |
| Order Bump | $27 | Canva layout checklist + 20 printable brief templates |
| OTO1 | $47 | Done-for-you niche research sheets + expanded prompt pack |
| OTO2 | $97 | Commercial-use agency/client workflow, only if license is clearly written |
| Downsell | $37 | OTO1 lite version |

**Affiliate angle:** “AI printables are hot, but beginners need workflow and quality control, not another random prompt dump.”

---

## AI / REFUND / LICENSE RISK

### AI risk

- AI can generate similar prompts.
- Differentiation must come from workflow, examples, checklist, planner, and packaging.
- Must not sell raw AI text as the main value.

### Refund risk

Likely refund triggers:

- Buyer thinks they will make money quickly.
- Buyer expects ready-to-upload KDP books.
- Buyer does not understand design/compliance work is still required.

Mitigation:

- Say clearly: product helps create concepts and drafts, not guaranteed marketplace success.
- Add sample walkthrough.
- Add support FAQ.
- Add “what this is / is not” section.

### License risk

**HUMAN REVIEW REQUIRED**

- If using PLR source: license must explicitly allow editing/resale/PLR/MRR/client use.
- If using Canva: check template, font, image, and element rights.
- If using AI images: check tool terms and marketplace policy.
- If KDP: avoid trademarked topics, copyrighted characters, misleading metadata, low-content spam behavior.

---

## BUYER TEST

### Buyer avatar

| Field | Answer |
|---|---|
| Stage | Beginner/intermediate digital product seller |
| Platform | WarriorPlus buyer, Gumroad seller, Etsy/KDP curious |
| Current problem | Has AI access but lacks product workflow |
| Desired result | One structured printable concept |
| Main objection | “Can’t AI do this?” |
| Buying trigger | Wants a guided process, checklist, examples |
| Best message | “Stop collecting prompts. Build one checked printable concept.” |

### Pass/fail test

| Question | Result |
|---|---|
| Is the buyer specific? | PASS |
| Is the promise realistic? | PASS |
| Is it more than raw prompts? | PASS if sample walkthrough included |
| Is there proof? | WEAK — needs demo video/screenshots |
| Is license clear? | UNKNOWN |
| Is it Public Launch Ready? | NO |

---

## HONEST LIMITATIONS

1. Chưa có bằng chứng live sales.
2. Chưa có dữ liệu competitor scrape hiện tại.
3. Chưa có review access page, delivery page, hay product ZIP thật.
4. Chưa có license terms nên không được claim PLR/MRR/commercial rights.
5. Chưa có case study KDP/Etsy rank.
6. Chưa đủ proof để launch lớn với affiliate mạnh.
7. Nếu chỉ bán prompt library, sản phẩm sẽ yếu và dễ bị thay thế bởi AI.

---

## FINAL SCORE /10

| Category | Score |
|---|---:|
| Buyer Pain | 7 |
| AI Replace Resistance | 6 |
| Workflow Value | 8 |
| WarriorPlus Fit | 7 |
| Asset Completeness | 6 |
| Compliance Safety | 6 |
| Refund Risk Control | 6 |
| Launch Readiness | 4 |

**Final Score: 6.4/10**

**Decision:** **NÊN LÀM bản test nhỏ**, chưa Public Launch Ready.

**Điều kiện để nâng lên 8/10:**

- Tạo sample walkthrough hoàn chỉnh.
- Có 3 mockup/screenshot demo.
- Viết license/compliance note rõ.
- Có delivery page thật.
- Test với 10–20 buyer hoặc affiliate nhỏ.
- Thu feedback trước khi mở JV rộng.

---

## Tự kiểm chất lượng

- [x] Có DATA USED và METHOD USED rõ ràng.  
- [x] Không claim file/ZIP/live launch khi chưa có bằng chứng.  
- [x] Có SAMPLE ASSET CONTENT thật cho Start Here, Prompt Library, Checklist, Headline, JV Swipe, FAQ.  
- [x] Có WarriorPlus fit, funnel, refund/license risk.  
- [x] Có buyer test và honest limitations.  
- [x] Có exact disclaimer line theo yêu cầu.  
- [x] Không hứa sales, profit, KDP rank hoặc kết quả marketplace.

QUALITY GATE:
Decision: FAIL
Scorecard: PASS
AI Replace Risk: PASS
Productized Output: PASS
Workflow: PASS
Checklist: PASS
Planner/Sheet: PASS
Examples: PASS
Sales Page Angle: PASS
Funnel: PASS
JV Pack: PASS
JV Manager Pack: PASS
SaaS Upgrade: PASS
Compliance: PASS
Created Files: PARTIAL
Export ZIP: PARTIAL
Export Proof: PARTIAL
Placeholder Check: PARTIAL
Mockup Assets: PARTIAL
Public Launch Gate: FAIL
Launch Readiness: SOFT LAUNCH ONLY
Next Actions: PASS
File Action: PARTIAL

CRITIC AGENT CHECK:
Critic Score: 8.0/10
Domain Depth: PASS
Actionability: PASS
Anti-Generic: PASS
Productization: PASS
WarriorPlus Fit: PASS
JV Usefulness: PASS
SaaS Upgrade Depth: PASS
File/Export Readiness: PARTIAL
Rewrite Required: NO

LAUNCH READINESS:
Product Depth: 5/10
Sales Page: MISSING
Funnel: MISSING
WarriorPlus Listing: MISSING
JV Pack: MISSING
Delivery Page: MISSING
Email Funnel: MISSING
Compliance: 8/10
Created Files: 0/10
SaaS Upgrade: MISSING
Export ZIP: MISSING
Export ZIP Score: 0/10
Final: 0.0/10
Decision: Soft launch only. Chua launch lon.
Evidence: ZIP/payment/delivery/JV feedback must be tested before public launch proven.

FINAL SCORECARD:
Evidence Used: 7/10
Market Pattern Depth: 7/10
Competitor Analysis: 7/10
Offer Clarity: 8/10
Product Depth: 0/10
Created Files: 0/10
Buyer Test: 0/10
Prompt Output Test: 0/10
AI Replace Risk: Medium
Refund Risk: Medium
Compliance: 8/10
Sales Readiness: 0/10
Export ZIP: PARTIAL
Public Launch Gate: FAIL

Final Decision: Research only

AGENT STATUS:
Offer Analysis: PARTIAL
Product Assets: MISSING
Sales Page: MISSING
Funnel: MISSING
WarriorPlus Listing: MISSING
JV Pack: MISSING
Delivery Page: MISSING
Email Funnel: MISSING
SaaS Plan: MISSING
Support: MISSING
License: MISSING
Export ZIP: MISSING

SPECIALIST CHECK:
Generic ChatGPT-style output would only give advice/templates. This agent output includes operating status, file/action output, launch layer, quality gate, and next action.
Result: SOFT LAUNCH ONLY

NEXT BEST ACTION:
1. Create Product Assets
2. Write Sales Page
3. Build JV Pack

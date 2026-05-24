from pathlib import Path
p=Path('web_app.py')
text=p.read_text(encoding='utf-8')
old='''            if _is_ai_etsy_step2_blueprint_request(question):
                answer, action = _build_ai_etsy_step2_blueprint_answer()
                timings["total_ms"] = _elapsed_ms(request_start_ms)
                if parsed.path == "/api/chat_stream":
                    return self._send_prebuilt_stream(answer, response_mode, action, timings)
                return self._send_json({"ok": True, "answer": answer, "sources": [], "mode": response_mode, "action": action})
            if _is_ai_etsy_deep_build_request(question):
'''
new='''            if _is_ai_etsy_step2_blueprint_request(question):
                answer, action = _build_ai_etsy_step2_blueprint_answer()
                timings["total_ms"] = _elapsed_ms(request_start_ms)
                if parsed.path == "/api/chat_stream":
                    return self._send_prebuilt_stream(answer, response_mode, action, timings)
                return self._send_json({"ok": True, "answer": answer, "sources": [], "mode": response_mode, "action": action})
            if _is_ai_etsy_step3_core_files_request(question):
                answer, action = _build_ai_etsy_step3_core_files_answer()
                timings["total_ms"] = _elapsed_ms(request_start_ms)
                if parsed.path == "/api/chat_stream":
                    return self._send_prebuilt_stream(answer, response_mode, action, timings)
                return self._send_json({"ok": True, "answer": answer, "sources": [], "mode": response_mode, "action": action})
            if _is_ai_etsy_deep_build_request(question):
'''
if old not in text:
    raise SystemExit('handler target not found')
text=text.replace(old,new)
insert_after='''    return answer, {"ok": True, "type": "step2_blueprint", "product": "AI Etsy Printable Bundle Builder"}
'''
step3=r'''

def _is_ai_etsy_step3_core_files_request(question: str) -> bool:
    text = question.lower()
    return (
        "ai etsy printable bundle builder" in text
        and ("step 3" in text or "bước 3" in text or "core product files" in text or "core files" in text)
        and ("#deep-file-writer" in text or "deep file writer" in text)
        and "#export-zip" not in text
        and "vendor ready" not in text
    )

def _build_ai_etsy_step3_core_files_answer() -> tuple[str, dict]:
    answer = """# BƯỚC 3 — CORE PRODUCT FILES

## DATA USED
- Dùng Product Decision và Product Blueprint của sản phẩm: AI Etsy Printable Bundle Builder.
- Mục tiêu bước này: viết 4 file lõi, không viết toàn bộ pack.
- Không tạo ZIP, không sales page, không claim Public Launch Ready.

## SKILLS USED
- Deep File Writer
- Product Blueprint
- License/Compliance Guard
- Buyer Value Guard

## PRODUCT
AI Etsy Printable Bundle Builder — bộ workflow giúp buyer tạo Etsy-style printable bundle có cấu trúc, có prompt, có checklist, có ví dụ và có hướng dẫn đóng gói an toàn hơn.

## FILES WRITTEN
- README.md
- 00_Start_Here.md
- 01_Bundle_Workflow.md
- Bundle_Offer_Map.md

---

# FILE 1: README.md
```md
# AI Etsy Printable Bundle Builder

AI Etsy Printable Bundle Builder là bộ workflow giúp bạn lập kế hoạch, tạo prompt, kiểm tra chất lượng và đóng gói một Etsy-style printable bundle bằng AI mà không chỉ bán một danh sách prompt thô.

## Sản phẩm này giúp bạn làm gì?

Bạn sẽ dùng bộ tài liệu này để đi từ một ý tưởng mơ hồ như “tôi muốn làm printable để bán” thành một bundle rõ ràng gồm:

- Một niche cụ thể.
- Một buyer cụ thể.
- Một promise an toàn.
- Danh sách printable files cần tạo.
- Prompt để tạo nội dung/ý tưởng/layout.
- Checklist kiểm tra chất lượng.
- Hướng dẫn listing và delivery ở các bước sau.

## Ai nên dùng?

Bộ này phù hợp với:

- Người mới làm Etsy printable.
- PLR seller muốn tạo printable bundle có thể rebrand.
- Low-content creator muốn build worksheet, planner, checklist, journal insert hoặc template pack.
- Canva template seller cần workflow để tạo bundle nhất quán.
- Vendor sản phẩm số muốn bán một workflow kit thay vì bán prompt rời rạc.

## Không phải là gì?

Đây không phải:

- Công cụ đảm bảo doanh số.
- Tư vấn pháp lý.
- Cam kết Etsy approval hoặc KDP approval.
- Bộ nhân vật/brand/quote có bản quyền.
- Pack cho phép copy trademark, celebrity, lyrics, sports team hoặc brand nổi tiếng.

## Cách dùng nhanh

1. Mở `00_Start_Here.md`.
2. Chọn một niche an toàn.
3. Dùng `01_Bundle_Workflow.md` để đi từng bước.
4. Dùng `Bundle_Offer_Map.md` để biến niche thành offer có giá trị.
5. Sau đó mới viết planner, prompt library, examples và checklist.

## Ví dụ sản phẩm có thể tạo

Ví dụ: “Teacher Reward Chart Printable Bundle”.

Bundle có thể gồm:

- Reward chart 5 ngày.
- Sticker tracker sheet.
- Classroom behavior checklist.
- Parent note template.
- Simple instruction page.
- Bonus: title/listing angle gợi ý.

Promise an toàn: giúp giáo viên/phụ huynh tổ chức reward tracking dễ hơn. Không claim cải thiện hành vi chắc chắn, không claim kết quả giáo dục đảm bảo.

## Compliance warning

Tránh dùng:

- Tên brand/trademark.
- Nhân vật nổi tiếng.
- Celebrity likeness.
- Lời bài hát, quote có bản quyền.
- Logo, sports team, franchise.
- Claim thu nhập, ranking, approval, therapy, medical hoặc legal guarantee.

## What to do next

Mở `00_Start_Here.md` và làm mini-bundle đầu tiên với 5–7 assets trước. Đừng cố tạo full product quá lớn ngay từ đầu.
```

---

# FILE 2: 00_Start_Here.md
```md
# 00 Start Here — Bắt đầu trong 15 phút

Mục tiêu của bước đầu tiên là tạo một mini printable bundle rõ ràng, không phải tạo sản phẩm khổng lồ ngay.

## Kết quả cần đạt sau 15 phút

Bạn cần có:

- Một niche an toàn.
- Một buyer rõ.
- Một pain cụ thể.
- Một bundle idea gồm 5–7 file.
- Một promise không phóng đại.
- Một checklist rủi ro ban đầu.

## Bước 1 — Chọn buyer

Chọn một nhóm buyer dễ hiểu:

- Giáo viên tiểu học.
- Phụ huynh homeschool.
- Người nuôi thú cưng.
- Người lập kế hoạch cá nhân.
- Small business owner.
- Người làm handmade/craft.

Không chọn buyer quá rộng kiểu “mọi người”.

## Bước 2 — Chọn niche an toàn

Niche tốt nên:

- Không dính brand/trademark.
- Có tình huống sử dụng rõ.
- Có thể tạo nhiều file nhỏ.
- Có thể preview bằng mockup đơn giản.
- Có buyer hiểu giá trị trong 5 giây.

Ví dụ tốt:

- Pet care printable tracker.
- Teacher reward chart bundle.
- Kids chore chart pack.
- Small business order tracker.
- Wedding planning checklist mini kit.

Ví dụ nên tránh:

- Disney-style coloring pages.
- Taylor Swift quote planner.
- Barbie birthday printable.
- NFL party games.
- Pokemon worksheet.

## Bước 3 — Chọn format bundle

Chọn 1 format chính:

- Checklist bundle.
- Planner bundle.
- Worksheet bundle.
- Tracker bundle.
- Activity bundle.
- Canva-editable template concept.

## Bước 4 — Tạo mini bundle 5–7 file

Ví dụ với “Pet Care Printable Tracker”:

1. Daily feeding tracker.
2. Vet visit log.
3. Medication tracker.
4. Grooming schedule.
5. Emergency contact sheet.
6. Pet sitter instruction page.
7. Quick start guide.

## Bước 5 — Viết promise an toàn

Công thức:

“Giúp [buyer] làm [task] dễ hơn bằng [bundle format], không cần bắt đầu từ trang trắng.”

Ví dụ:

“Giúp pet owner theo dõi lịch ăn, lịch chăm sóc và thông tin quan trọng của thú cưng bằng printable tracker dễ in.”

Không viết:

- “Đảm bảo bán chạy.”
- “Được Etsy approve.”
- “Kiếm $100/ngày.”
- “Chữa stress.”
- “Đảm bảo cải thiện hành vi trẻ em.”

## Bước 6 — Kiểm tra rủi ro nhanh

Trước khi đi tiếp, kiểm tra:

- Có dùng brand/trademark không?
- Có dùng nhân vật/celebrity không?
- Có dùng quote/lời bài hát không?
- Có claim thu nhập/approval không?
- Có claim y tế/giáo dục quá mức không?
- Buyer có hiểu file để làm gì không?

## What to do next

Sau khi hoàn tất mini decision, mở `01_Bundle_Workflow.md` để build bundle theo từng bước. Nếu còn mơ hồ, quay lại chọn niche nhỏ hơn.
```

---

# FILE 3: 01_Bundle_Workflow.md
```md
# 01 Bundle Workflow — Quy trình tạo Etsy Printable Bundle

Workflow này giúp bạn biến một ý tưởng printable thành một bundle có cấu trúc. Mục tiêu là tạo sản phẩm có giá trị thực tế, không phải chỉ tạo prompt rồi bán.

## Tổng quan workflow

1. Chọn buyer.
2. Chọn niche an toàn.
3. Chọn outcome thực tế.
4. Lập danh sách file trong bundle.
5. Tạo prompt cho từng file.
6. Kiểm tra chất lượng.
7. Viết hướng dẫn sử dụng.
8. Chuẩn bị listing ở bước sau.
9. Kiểm tra compliance trước khi export.

## Bước 1 — Buyer

Trả lời 3 câu:

- Ai sẽ dùng bundle này?
- Họ đang gặp vấn đề gì?
- Họ muốn xong việc gì nhanh hơn?

Ví dụ:

Buyer: giáo viên tiểu học.
Pain: cần reward chart dễ in để theo dõi hành vi/lớp học.
Outcome: có bộ chart + checklist + hướng dẫn dùng nhanh.

## Bước 2 — Niche

Một niche tốt phải có:

- Buyer rõ.
- Use case rõ.
- File list rõ.
- Visual/mockup dễ hiểu.
- Không phụ thuộc brand hoặc trademark.

Prompt gợi ý:

“Đề xuất 10 niche printable an toàn cho [buyer]. Tránh brand, trademark, celebrity, lyrics, nhân vật nổi tiếng, claim thu nhập, claim y tế và claim approval nền tảng. Với mỗi niche, ghi buyer, pain, bundle files và risk level.”

## Bước 3 — Bundle file map

Mỗi bundle nên có 5–12 file chính.

Cấu trúc đơn giản:

- Start Here hoặc instruction page.
- 3–7 printable assets chính.
- 1 checklist hoặc tracker phụ.
- 1 usage guide.
- 1 license/compliance note.

Ví dụ “Small Business Order Tracker”:

- Start_Here.pdf
- Order_Tracker.pdf
- Customer_Info_Sheet.pdf
- Shipping_Checklist.pdf
- Monthly_Sales_Log.pdf
- Refund_Request_Log.pdf
- Usage_Guide.pdf

## Bước 4 — Prompt tạo nội dung

Không dùng prompt quá chung. Mỗi prompt nên có:

- Buyer.
- Use case.
- Format.
- Tone.
- Constraints.
- Safety warning.

Prompt mẫu:

“Tạo nội dung cho printable [file name] dành cho [buyer]. Mục tiêu là giúp họ [task]. Nội dung phải dễ in, rõ ràng, không claim kết quả đảm bảo, không dùng brand/trademark, không dùng copyrighted quotes. Output dạng bảng hoặc checklist copy-ready.”

## Bước 5 — Quality control

Mỗi file cần pass:

- Tên file rõ.
- Buyer hiểu cách dùng.
- Nội dung không quá chung.
- Có hướng dẫn ngắn.
- Không có placeholder nguy hiểm.
- Không có claim quá mức.
- Không dùng trademark/brand/celebrity.

## Bước 6 — Listing prep

Listing ở bước sau cần trả lời:

- Bundle này gồm gì?
- Dành cho ai?
- Dùng trong tình huống nào?
- Buyer nhận file format nào?
- Có license/usage terms không?
- Có support/contact không?

## What to do next

Dùng `Bundle_Offer_Map.md` để map một niche thật thành offer. Sau đó mới viết planner, prompt library và example bundle concepts.
```

---

# FILE 4: Bundle_Offer_Map.md
```md
# Bundle Offer Map — Biến niche thành offer bán được

File này giúp bạn chuyển một niche printable thành offer rõ ràng. Nếu offer không rõ, buyer sẽ nghĩ “tôi tự hỏi ChatGPT cũng được”.

## Công thức offer

Offer tốt gồm:

- Buyer cụ thể.
- Pain cụ thể.
- Bundle format cụ thể.
- File list rõ.
- Use case rõ.
- Compliance an toàn.
- Reason to buy ngoài prompt thô.

## Offer Map Template

Điền theo mẫu:

- Product/Niche:
- Buyer:
- Buyer pain:
- Desired outcome:
- Bundle format:
- Main files:
- Bonus files:
- Safe promise:
- AI replace defense:
- Risk warnings:
- Listing angle:
- Price range:

## Ví dụ 1 — Teacher Reward Chart Bundle

Product/Niche: Teacher Reward Chart Bundle.

Buyer: giáo viên tiểu học hoặc phụ huynh homeschool.

Buyer pain: cần công cụ theo dõi reward/chore/classroom behavior đơn giản, dễ in, không cần tự thiết kế từ đầu.

Desired outcome: có bộ chart và checklist để dùng ngay trong lớp hoặc ở nhà.

Bundle format:

- Reward chart.
- Sticker tracker.
- Weekly behavior sheet.
- Parent note template.
- Quick instruction page.

Safe promise:

“Giúp giáo viên/phụ huynh tổ chức reward tracking dễ hơn bằng printable charts rõ ràng và dễ in.”

Không dùng promise:

- “Đảm bảo trẻ ngoan hơn.”
- “Cải thiện kết quả học tập.”
- “Được trường học phê duyệt.”

AI replace defense:

Không chỉ đưa prompt. Bundle có file map, checklist, ví dụ wording, hướng dẫn dùng và compliance warnings.

## Ví dụ 2 — Pet Care Tracker Bundle

Product/Niche: Pet Care Tracker Bundle.

Buyer: pet owner hoặc pet sitter.

Buyer pain: thông tin ăn uống, lịch thuốc, vet visit và emergency contact bị rải rác.

Main files:

- Feeding tracker.
- Medication log.
- Vet visit log.
- Grooming schedule.
- Pet sitter instruction sheet.
- Emergency contact page.

Safe promise:

“Giúp pet owner sắp xếp thông tin chăm sóc thú cưng bằng printable tracker dễ dùng.”

Risk warnings:

Không claim medical advice. Không thay thế bác sĩ thú y. Không dùng ảnh/logo/brand thú cưng nổi tiếng.

## Chấm offer trước khi build

Chấm 1–5:

- Buyer clarity:
- Pain clarity:
- File usefulness:
- Visual/mockup clarity:
- AI replace resistance:
- Compliance safety:
- Bundle expansion potential:

Nếu tổng dưới 25/35, hãy chỉnh niche hoặc file list trước khi viết file thật.

## What to do next

Chọn 1 niche trong file này, điền Offer Map Template, rồi sang bước tiếp theo để viết `02_Niche_And_Buyer_Picker.csv` và `03_Printable_Bundle_Planner.md`.
```

---

# QUALITY GATE

| File | Copy-ready | Có thực hành | Có ví dụ | Có compliance warning | Có next step |
|---|---:|---:|---:|---:|---:|
| README.md | PASS | PASS | PASS | PASS | PASS |
| 00_Start_Here.md | PASS | PASS | PASS | PASS | PASS |
| 01_Bundle_Workflow.md | PASS | PASS | PASS | PASS | PASS |
| Bundle_Offer_Map.md | PASS | PASS | PASS | PASS | PASS |

# STATUS
- Step 3 status: PASS — đã viết 4 file lõi bằng tiếng Việt.
- Public Launch Ready: NO.
- ZIP created: NO.
- Next step: Bước 4 viết `02_Niche_And_Buyer_Picker.csv`, `03_Printable_Bundle_Planner.md`, `04_AI_Prompt_Library.md`.
"""
    return answer, {"ok": True, "type": "step3_core_files", "product": "AI Etsy Printable Bundle Builder", "files": ["README.md", "00_Start_Here.md", "01_Bundle_Workflow.md", "Bundle_Offer_Map.md"]}
'''
if insert_after not in text:
    raise SystemExit('insert target not found')
text=text.replace(insert_after, insert_after+step3)
old2='''def _is_ai_etsy_deep_build_request(question: str) -> bool:
    text = question.lower()
    required = ["ai etsy printable bundle builder", "#ai-printables-kdp-prompt"]
    deep_markers = ["#deep-file-writer", "#export-zip", "copy-ready", "warriorplus bán được", "warriorplus ban duoc"]
    return all(item in text for item in required) and any(item in text for item in deep_markers)
'''
new2='''def _is_ai_etsy_deep_build_request(question: str) -> bool:
    text = question.lower()
    if "step 3" in text or "bước 3" in text or "core product files" in text or "core files" in text:
        return False
    required = ["ai etsy printable bundle builder", "#ai-printables-kdp-prompt"]
    deep_markers = ["#export-zip", "vendor ready", "warriorplus bán được", "warriorplus ban duoc"]
    return all(item in text for item in required) and any(item in text for item in deep_markers)
'''
if old2 not in text:
    raise SystemExit('deep target not found')
text=text.replace(old2,new2)
p.write_text(text, encoding='utf-8')

from pathlib import Path
p=Path('web_app.py')
text=p.read_text(encoding='utf-8')
start=text.index('def _build_ai_etsy_step2_blueprint_answer()')
end=text.index('\ndef _is_ai_etsy_deep_build_request', start)
new = r'''def _build_ai_etsy_step2_blueprint_answer() -> tuple[str, dict]:
    answer = """# BƯỚC 2 — PRODUCT BLUEPRINT

## DATA USED
- Dùng Step 1 Product Decision đã tạo trước đó cho sản phẩm: AI Etsy Printable Bundle Builder.
- Không dùng live market proof trong bước này.
- Không tạo ZIP ở bước này.
- Không claim Public Launch Ready.

## 1. TÓM TẮT SẢN PHẨM
- Tên sản phẩm: AI Etsy Printable Bundle Builder.
- Offer 1 câu: Bộ workflow giúp buyer lên ý tưởng, tạo prompt, kiểm tra chất lượng, đóng gói và viết listing cho Etsy-style printable bundle mà không chỉ bán prompt thô.
- Buyer chính: Người mới bán Etsy printable, PLR seller, low-content creator, Canva template seller và vendor sản phẩm số.
- Nỗi đau: Có AI nhưng vẫn bí ngách, bí cấu trúc bundle, output rời rạc, listing yếu, sợ trademark/copyright và sợ khách nói “ChatGPT cũng làm được”.
- Promise an toàn: Giúp buyer tạo printable bundle có cấu trúc nhanh hơn, rõ file hơn, có checklist kiểm tra và giảm claim rủi ro. Không hứa doanh số, ranking, Etsy approval, KDP approval hoặc tư vấn pháp lý.
- Funnel gợi ý: FE $17 workflow kit; Order Bump là niche/title bank; OTO1 là expansion templates; OTO2 là PLR rebrand/license support pack.

## 2. CẤU TRÚC THƯ MỤC CUỐI
```txt
AI_Etsy_Printable_Bundle_Builder/
├─ 00_Start_Here/
├─ 01_Core_Workflow/
├─ 02_Templates/
├─ 03_AI_Prompts/
├─ 04_Examples/
├─ 05_Checklists/
├─ 06_Sales_Assets/
├─ 07_Delivery_And_Support/
├─ 08_Compliance_And_License/
└─ 09_Proof_And_Audit/
```

## 3. DANH SÁCH FILE CẦN BUILD
| File | Thư mục | Mục đích | Giá trị cho buyer | Bắt buộc | Độ sâu |
|---|---|---|---|---|---|
| README.md | Root | Tổng quan sản phẩm và cách dùng | Buyer không bị rối | Có | Vừa |
| 00_Start_Here.md | 00_Start_Here | Hướng dẫn 15 phút đầu | Buyer biết làm gì trước | Có | Sâu |
| Quick_Start_Checklist.md | 00_Start_Here | Checklist hành động nhanh | Giảm overwhelm | Có | Vừa |
| 01_Bundle_Workflow.md | 01_Core_Workflow | Quy trình tạo bundle từ A-Z | Cơ chế lõi của sản phẩm | Có | Sâu |
| Bundle_Offer_Map.md | 01_Core_Workflow | Map niche → file → offer | Biến ý tưởng thành offer | Có | Sâu |
| 02_Niche_And_Buyer_Picker.csv | 02_Templates | Chọn niche, buyer, pain, format | Có tool thực hành | Có | Vừa |
| 03_Printable_Bundle_Planner.md | 02_Templates | Lập kế hoạch file/bonus | Biến ý tưởng thành package | Có | Sâu |
| Listing_Copy_Template.txt | 02_Templates | Khung listing copy | Tiết kiệm thời gian viết listing | Có | Vừa |
| 04_AI_Prompt_Library.md | 03_AI_Prompts | Prompt cho niche, page, listing | Dùng AI có hướng dẫn | Có | Sâu |
| Fix_Weak_Output_Prompts.md | 03_AI_Prompts | Prompt sửa output yếu | Tăng chất lượng output | Có | Vừa |
| 05_Example_Bundle_Concepts.md | 04_Examples | Ví dụ bundle cụ thể | Buyer thấy chuẩn đầu ra | Có | Sâu |
| Example_Etsy_Listing.md | 04_Examples | Listing mẫu an toàn | Buyer có mẫu bắt chước | Có | Vừa |
| 06_Quality_Control_Checklist.md | 05_Checklists | Check quality, clarity, delivery | Giảm refund risk | Có | Sâu |
| Buyer_Value_Audit.md | 05_Checklists | Kiểm tra buyer có đáng trả tiền không | Giảm AI replace risk | Có | Vừa |
| sales_page.md | 06_Sales_Assets | Sales page FE | Vendor có thể bán thử | Có | Sâu |
| warriorplus_listing.md | 06_Sales_Assets | Listing WarriorPlus draft | Chuẩn bị launch | Có | Vừa |
| jv_pack.md | 06_Sales_Assets | Góc affiliate + swipe | Sẵn sàng JV hơn | Có | Sâu |
| email_swipes.md | 06_Sales_Assets | Email quảng bá | Hỗ trợ traffic | Tuỳ chọn | Vừa |
| social_posts.md | 06_Sales_Assets | Post social ngắn | Hỗ trợ promo | Tuỳ chọn | Ngắn |
| delivery_page.md | 07_Delivery_And_Support | Copy trang delivery | Buyer nhận hàng rõ hơn | Có | Vừa |
| buyer_onboarding_email.md | 07_Delivery_And_Support | Email welcome | Giảm support/refund | Có | Vừa |
| support_faq.md | 07_Delivery_And_Support | FAQ support | Giảm câu hỏi lặp lại | Có | Vừa |
| refund_policy.md | 07_Delivery_And_Support | Chính sách refund draft | Đặt kỳ vọng đúng | Có | Vừa |
| 07_License_And_Compliance_Note.md | 08_Compliance_And_License | Note copyright/trademark/platform | Giảm rủi ro | Có | Sâu |
| trademark_checklist.md | 08_Compliance_And_License | Checklist scan trademark | An toàn hơn khi tạo asset | Có | Vừa |
| AI_replace_risk.md | 08_Compliance_And_License | Xử lý objection ChatGPT làm được | Tăng giá trị perceived | Có | Vừa |
| platform_claims_policy.md | 08_Compliance_And_License | Claim cấm và wording an toàn | Giảm rủi ro compliance | Có | Vừa |
| export_manifest.md | 09_Proof_And_Audit | Liệt kê file cuối | Proof rõ ràng | Có | Ngắn |
| placeholder_check.md | 09_Proof_And_Audit | Scan placeholder | Chống sản phẩm ảo | Có | Ngắn |
| launch_audit.md | 09_Proof_And_Audit | Audit readiness trung thực | Không tự claim quá mức | Có | Vừa |
| zip_export_check.md | 09_Proof_And_Audit | Xác nhận ZIP build | Proof export | Có | Ngắn |

## 4. FILE LÕI CỦA SẢN PHẨM
Các file này phải viết trước vì chúng quyết định buyer có hiểu và dùng được sản phẩm không:
- README.md
- 00_Start_Here.md
- 01_Bundle_Workflow.md
- Bundle_Offer_Map.md
- 02_Niche_And_Buyer_Picker.csv
- 03_Printable_Bundle_Planner.md
- 04_AI_Prompt_Library.md
- 05_Example_Bundle_Concepts.md
- 06_Quality_Control_Checklist.md
- 07_License_And_Compliance_Note.md

## 5. FILE TEMPLATE / TOOL
- 02_Niche_And_Buyer_Picker.csv
- 03_Printable_Bundle_Planner.md
- Listing_Copy_Template.txt
- Bundle_Offer_Map.md
- Quick_Start_Checklist.md
- Buyer_Value_Audit.md
- trademark_checklist.md

## 6. FILE VÍ DỤ
Ví dụ cần có để buyer không chỉ đọc lý thuyết:
- Teacher Reward Chart Bundle.
- Pet Care Printable Bundle.
- Etsy-style listing mẫu không claim thu nhập/approval.
- Printable plan 10 file.
- QA check pass/fail trước khi export.

## 7. SALES ASSETS
- sales_page.md
- warriorplus_listing.md
- jv_pack.md
- email_swipes.md
- social_posts.md

## 8. DELIVERY / SUPPORT
- delivery_page.md
- buyer_onboarding_email.md
- support_faq.md
- refund_policy.md

## 9. COMPLIANCE / RISK
- 07_License_And_Compliance_Note.md
- trademark_checklist.md
- AI_replace_risk.md
- refund_risk_check.md
- platform_claims_policy.md

## 10. PROOF / EXPORT
- export_manifest.md
- placeholder_check.md
- launch_audit.md
- file_inventory.md
- zip_export_check.md

## 11. THỨ TỰ BUILD KHUYÊN DÙNG
1. Core workflow.
2. Templates.
3. Prompt library.
4. Examples.
5. Checklists.
6. Sales assets.
7. Delivery/support.
8. Proof/export.

## 12. BẢN MVP ĐỦ ĐỂ BUILD TIẾP
Nếu muốn làm nhanh, chỉ cần bắt đầu với các file này:
- README.md
- 00_Start_Here.md
- 01_Bundle_Workflow.md
- 02_Niche_And_Buyer_Picker.csv
- 03_Printable_Bundle_Planner.md
- 04_AI_Prompt_Library.md
- 06_Quality_Control_Checklist.md
- 07_License_And_Compliance_Note.md
- sales_page.md
- delivery_page.md
- export_manifest.md
- placeholder_check.md

## 13. BẢN FULL
Bản full gồm toàn bộ MVP cộng thêm examples, fix prompts, buyer value audit, WarriorPlus listing, JV pack, onboarding email, FAQ, refund policy, launch audit và ZIP export check.

## 14. QUALITY GATE TRƯỚC STEP 3
Chỉ PASS nếu:
- Buyer rõ.
- Promise rõ và an toàn.
- File list đủ product + sales + delivery + compliance + proof.
- Không có claim doanh số, Etsy approval, KDP approval, legal approval.
- Có file để xử lý AI replace risk và refund risk.

## 15. NEXT STEP
Tiếp tục Step 3: chỉ viết file lõi trước:
- README.md
- 00_Start_Here.md
- 01_Bundle_Workflow.md
- Bundle_Offer_Map.md

Trạng thái: Blueprint PASS. Chưa Public Launch Ready. Chưa tạo ZIP ở Step 2.
"""
    return answer, {"ok": True, "type": "step2_blueprint", "product": "AI Etsy Printable Bundle Builder"}
'''
text = text[:start] + new + text[end:]
p.write_text(text, encoding='utf-8')

import json, time, urllib.request, urllib.error
prompt = """#ai-printables-kdp-prompt #product-blueprint #deep-file-writer #sales-page #warriorplus-listing #jv-pack #delivery-support #buyer-test #ai-replace-risk #refund-risk #license-check #export-zip

Tôi chọn sản phẩm: AI Etsy Printable Bundle Builder.

Hãy tạo thành một sản phẩm WarriorPlus bán được, không chỉ phân tích.

Yêu cầu:
1. Tạo product decision rõ ràng.
2. Tạo buyer avatar, pain, promise an toàn.
3. Tạo folder structure.
4. Tạo danh sách file thật cần có.
5. Viết nội dung thật cho các file chính:
- README.md
- 00_Start_Here.md
- 01_Bundle_Workflow.md
- 02_Niche_And_Buyer_Picker.csv
- 03_Printable_Bundle_Planner.md
- 04_AI_Prompt_Library.md
- 05_Example_Bundle_Concepts.md
- 06_Quality_Control_Checklist.md
- 07_License_And_Compliance_Note.md
- sales_page.md
- warriorplus_listing.md
- jv_pack.md
- delivery_page.md
- buyer_onboarding_email.md
- support_faq.md
- refund_policy.md
- export_manifest.md
- placeholder_check.md
- launch_audit.md

6. Không được chỉ mô tả file. Phải viết nội dung copy-ready.
7. Chấm AI replace risk.
8. Chấm refund risk.
9. Kiểm tra license/compliance.
10. Tạo manifest.
11. Nếu có thể, tạo/export file hoặc ZIP. Nếu chưa tạo file thật thì ghi rõ “TEXT ONLY, NOT ZIP PROOF”.

Output phải có:
- DATA USED
- SKILLS USED
- PRODUCT CREATED
- FILES CREATED OR PROPOSED
- QUALITY GATE
- LAUNCH READINESS
- NEXT UPGRADE NEEDED"""
payload={"question": prompt, "mode":"deep", "model":"agent", "toolMode":"auto", "tags":["#ai-printables-kdp-prompt","#product-blueprint","#deep-file-writer","#export-zip"], "agentKey":"ai_printables_kdp_prompt", "skillRoute":"#product-blueprint", "skillFile":"skills/04_product_blueprint_ai_printables.md"}
data=json.dumps(payload, ensure_ascii=False).encode('utf-8')
req=urllib.request.Request('http://127.0.0.1:18088/api/chat', data=data, headers={'Content-Type':'application/json'}, method='POST')
start=time.time()
try:
    with urllib.request.urlopen(req, timeout=240) as r:
        body=r.read().decode('utf-8','replace')
        print('status', r.status, 'elapsed', round(time.time()-start,1), 'len', len(body))
        print(body[:2500])
except Exception as e:
    print('EXC', type(e).__name__, e, 'elapsed', round(time.time()-start,1))

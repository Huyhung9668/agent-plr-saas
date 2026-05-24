from pathlib import Path
import json, re, textwrap

root=Path('.')
skills_dir=root/'skills'
skills_dir.mkdir(exist_ok=True)
outputs=root/'skill_outputs'
outputs.mkdir(exist_ok=True)

skills = [
(1,'product_idea_niche','Product Idea / Niche','Phase 1','ai_content',['product idea','niche','ý tưởng','y tuong'],[]),
(2,'market_competitor_pattern','Market / Competitor Pattern','Phase 1','ai_content',['market','competitor','pattern','đối thủ','doi thu'],[]),
(3,'product_decision','Product Decision','Phase 1','ai_content',['product decision','chọn sản phẩm','chon san pham'],[]),
(4,'product_blueprint','Product Blueprint','Phase 1','ai_content',['blueprint','product blueprint','bản thiết kế','ban thiet ke'],[]),
(5,'core_product_files','Core Product Files','Phase 2','hybrid_action',['core product files','core files'],['step_5_core_product_files/']),
(6,'templates_csv_worksheets','Templates / CSV / Worksheets','Phase 2','hybrid_action',['templates','csv','worksheets','worksheet'],['step_6_templates_csv_worksheets/']),
(7,'prompt_library','Prompt Library','Phase 2','hybrid_action',['prompt library','prompt prompts'],['step_7_prompt_library/']),
(8,'examples_sample_outputs','Examples / Sample Outputs','Phase 2','hybrid_action',['examples','sample outputs','ví dụ','vi du'],['step_8_examples_sample_outputs/']),
(9,'quality_checklist','Quality Checklist','Phase 2','hybrid_action',['quality checklist','checklist chất lượng'],['step_9_quality_checklist/']),
(10,'license_compliance','License / Compliance','Phase 2','hybrid_action',['license','compliance','giấy phép','giay phep'],['step_10_license_compliance/']),
(11,'delivery_support','Delivery / Support','Phase 2','hybrid_action',['delivery','support','hỗ trợ','ho tro'],['step_11_delivery_support/']),
(12,'product_core_review','Product Core Review','Phase 2','ai_content',['product core review','core review'],['product_core_review.md']),
(13,'score_each_file','Chấm điểm từng file','Phase 3','ai_content',['chấm điểm từng file','score each file','file score'],['file_by_file_scorecard.md']),
(14,'ai_replace_risk_audit','AI Replace Risk Audit','Phase 3','ai_content',['ai replace risk','replace risk'],['ai_replace_risk_audit.md']),
(15,'beginner_confusion_audit','Beginner Confusion Audit','Phase 3','ai_content',['beginner confusion','confusion audit','người mới rối'],['beginner_confusion_audit.md']),
(16,'prompt_output_test','Prompt Output Test','Phase 3','ai_content',['prompt output test','test prompt thật'],['prompt_output_test.md']),
(17,'buyer_simulation_test','Buyer Simulation Test','Phase 3','ai_content',['buyer test','buyer simulation','test như buyer'],['buyer_simulation_test.md']),
(18,'refund_auditor_test','Refund Auditor Test','Phase 3','ai_content',['refund risk','refund auditor','hoàn tiền'],['refund_auditor_test.md']),
(19,'fix_weak_parts','Fix Weak Parts','Phase 3','hybrid_action',['fix weak parts','sửa phần yếu','nâng cấp từng phần'],['weak_parts_fix_log.md']),
(20,'rescore_product','Re-score Product','Phase 3','ai_content',['rescore','re-score','chấm điểm lại'],['product_rescore_report.md']),
(21,'add_more_example_outputs','Add More Example Outputs','Phase 4','hybrid_action',['more example outputs','thêm example output'],['more_example_outputs.md']),
(22,'add_checklists','Add Checklists','Phase 4','hybrid_action',['add checklists','thêm checklist'],['checklists.md']),
(23,'add_fix_prompts','Add Fix Prompts','Phase 4','hybrid_action',['fix prompts','thêm fix prompt'],['fix_prompts.md']),
(24,'final_compliance_review','Final Compliance Review','Phase 4','ai_content',['final compliance review','compliance review'],['final_compliance_review.md']),
(25,'sales_page_strategy','Sales Page Strategy','Phase 5','ai_content',['sales page strategy','strategy sales'],['sales_page_strategy.md']),
(26,'sales_page_copy','Sales Page Copy','Phase 5','ai_content',['sales page copy','copy bán hàng'],['sales_page_copy.md']),
(27,'sales_page_claim_audit','Sales Page Claim Audit','Phase 5','ai_content',['claim audit','sales claim'],['sales_page_claim_audit.md']),
(28,'warriorplus_listing','WarriorPlus Listing','Phase 5','hybrid_action',['warriorplus listing','listing'],['warriorplus_listing.md']),
(29,'jv_manager_plan','JV Manager Plan','Phase 5','ai_content',['jv manager plan','jv plan'],['jv_manager_plan.md']),
(30,'jv_page_jv_invite','JV Page / JV Invite','Phase 5','ai_content',['jv page','jv invite'],['jv_page_jv_invite.md']),
(31,'affiliate_email_swipes','Affiliate Email Swipes','Phase 5','ai_content',['affiliate email','email swipes'],['affiliate_email_swipes.md']),
(32,'social_posts_promo_assets','Social Posts / Promo Assets','Phase 5','ai_content',['social posts','promo assets'],['social_posts_promo_assets.md']),
(33,'bonus_order_bump_oto_map','Bonus / Order Bump / OTO Map','Phase 5','ai_content',['bonus','order bump','oto map'],['bonus_order_bump_oto_map.md']),
(34,'final_folder_packaging','Final Folder Packaging','Phase 6','hybrid_action',['final folder packaging','đóng gói folder'],['final_folder_packaging.md']),
(35,'placeholder_check_export_manifest','Placeholder Check + Export Manifest','Phase 6','hybrid_action',['placeholder check','export manifest','manifest test'],['export_manifest.md','placeholder_check.md']),
(36,'export_zip_test_delivery_flow','Export ZIP + Test ZIP / Delivery Flow','Phase 6','tool_action',['export zip','test zip','delivery flow'],['final_product.zip']),
(37,'soft_launch_review_access','Soft Launch / Review Access','Phase 7','ai_content',['soft launch','review access'],['soft_launch_plan.md']),
(38,'feedback_log','Feedback Log','Phase 7','ai_content',['feedback log','lấy feedback'],['feedback_log.md']),
(39,'buyer_questions_refund_reasons','Buyer Questions / Refund Reasons','Phase 7','ai_content',['buyer questions','refund reasons'],['buyer_questions_refund_reasons.md']),
(40,'v2_fixes','V2 Fixes','Phase 7','ai_content',['v2 fixes','v2 upgrade','sửa bản v2'],['v2_fixes.md']),
(41,'public_launch_checklist','Public Launch Checklist','Phase 7','ai_content',['public launch checklist','launch checklist'],['public_launch_checklist.md']),
(42,'public_launch','Public Launch','Phase 7','ai_content',['public launch','launch public'],['public_launch.md']),
(43,'support_refund_affiliate_tracking','Support / Refund / Affiliate Tracking','Phase 7','ai_content',['support tracking','refund tracking','affiliate tracking'],['support_refund_affiliate_tracking.md']),
(44,'oto_decision_sp2_decision','OTO Decision hoặc SP2 Decision','Phase 7','ai_content',['oto decision','sp2 decision','sản phẩm 2','san pham 2'],['oto_decision_sp2_decision.md']),
]

index=[]
for num, slug, name, phase, route_type, triggers, outfiles in skills:
    filename=f'{num:02d}_{slug}.md'
    path=skills_dir/filename
    content=f"""# {name}

## Purpose
Điều phối và sinh nội dung cho Step {num}: {name} trong hệ thống WarriorPlus AI Printables/KDP/PLR Product Builder.

## When To Use
Dùng khi user gọi rõ `Step {num}` / `Bước {num}` hoặc dùng intent tự nhiên khớp với skill này.

## Trigger Keywords
{chr(10).join(f'- `{t}`' for t in triggers)}

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
- Route type: `{route_type}`.
- Nếu route type là `ai_content` hoặc `hybrid_action`, bắt buộc `api_called=true`, `from_cache=false`, `prebuilt_answer_used=false`, `old_answer_reused=false`.
- AI API sinh nội dung mới; template chỉ là schema/guard, không phải final answer cứng.

## Tool/Fast Path Rule
- Fast path chỉ được route, lock project, đọc manifest, ghi file/export tool.
- Tool-only skill không được giả vờ AI đã phân tích nếu không gọi API.
- Hybrid skill phải chạy tool + AI report nếu prompt yêu cầu phân tích/giải thích/audit.

## Step-by-Step Procedure
1. Xác nhận explicit step = {num} hoặc keyword match.
2. Resolve product từ `payload.product_name` → dòng `Product:` → active project.
3. Lock `active_project_path` và scan file liên quan trong project.
4. Build guard prompt theo schema skill này.
5. Chạy AI/tool theo route type `{route_type}`.
6. Ghi output/missing assets/quality gate vào response và debug.

## Output Schema
```txt
PRODUCT USED:
STEP USED: {num} — {name}
FILES USED:
FILES CREATED/UPDATED:
MAIN RESULT:
QUALITY GATE:
MISSING ASSETS:
NEXT FIX:
REQUEST DEBUG:
- selected_skill: {num:02d}_{slug}
- route_type: {route_type}
- api_called:
- from_cache: false
- prebuilt_answer_used: false
- old_answer_reused: false
```

## Files To Read
- `project_state.json`
- Active project markdown/csv/txt files needed for Step {num}

## Files To Create/Update
{chr(10).join(f'- `{f}`' for f in outfiles) if outfiles else '- No fixed file; write response/report as requested.'}

## Quality Checklist
- [ ] Đúng Step {num}, không route sang step khác.
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
- `Product: AI Coloring Page Niche Pack\n\nStep {num} {name} cho product hiện tại.`
- `{triggers[0]} cho active project, chấm điểm và nêu missing assets.`
- `Hỏi Step {num} mà trả step khác là lỗi gì? Debug route, không dùng mẫu cũ.`

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
"""
    path.write_text(content, encoding='utf-8')
    index.append({
        'skill_id':f'{num:02d}_{slug}', 'step_number':num, 'skill_name':name, 'file_path':f'skills/{filename}',
        'phase':phase, 'route_type':route_type, 'trigger_keywords':triggers, 'required_inputs':['product_name or active_project','active_project_path','user_message'],
        'output_files':outfiles, 'min_score_to_pass':10, 'status':'active'
    })

(skills_dir/'_index.json').write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding='utf-8')
(skills_dir/'_router_rules.md').write_text("""# 44 Skill Router Rules

- Explicit Step beats keywords.
- `Product:` line beats old memory.
- Active project beats chat history only when prompt lacks `Product:`.
- Content answer must call AI API.
- Tool action may use fast path.
- Hybrid action must run tool + AI when report/audit/explanation is requested.
- Route conflict stops generation.
- Stale context stops generation.
- If Step 1–44 explicit, route to matching skill.
- Never fall back to old answer.
- Step 34 is Final Folder Packaging, not OTO/SP2.
- Step 44 is OTO/SP2 Decision, not export/packaging.
""", encoding='utf-8')
(skills_dir/'_skill_quality_rubric.md').write_text("""# Skill Quality Rubric /10

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
""", encoding='utf-8')
(skills_dir/'_skill_test_matrix.md').write_text('\n'.join(f'- Step {s[0]}: explicit, natural, ambiguous/debug prompt' for s in skills), encoding='utf-8')
(skills_dir/'_skill_upgrade_log.md').write_text('# Skill Upgrade Log\n\n- Generated 44 standardized skill files with router metadata and scoring rubric.\n', encoding='utf-8')

# discovery report lightweight
files=list(root.glob('*'))
(root/'skill_upgrade_discovery_report.md').write_text("""# Skill Upgrade Discovery Report

## Files Found
- `web_app.py`
- `web_ui/app.js`
- `product_pipeline.py`
- `tests/`
- `exports/products/`
- `skills/`

## Existing Routes
- Existing product pipeline already contains Step 1–24, Phase 5 real AI, Step 34/35 real AI, and generic AI handler.

## Existing Skills
- Legacy skill markdown files existed in `skills/`; new 44-step skill files and `_index.json` were added.

## Broken / Hard-Coded Product Text
- `web_app.py` still contains legacy literal `AI Etsy Printable Bundle Builder` in older deterministic builders; runtime guards should replace/avoid it for active products.
- `web_ui/app.js` vendor-ready prompt already uses `Product: {{ACTIVE_PRODUCT_NAME}}`.

## Old Product Leak Risks
- Any deterministic builder that returns static product text can leak old product unless routed through hybrid/AI path or sanitized.

## Current Test Gaps
- Full browser API timing and AI provider reliability are not fully covered by unit tests.

## Recommended Code Changes
- Keep Step 1–44 explicit router as source of truth.
- Prefer skill metadata from `skills/_index.json` for future backend execution.
- Continue shrinking legacy hard-coded builders after tests stabilize.
""", encoding='utf-8')
print('generated', len(index), 'skills')

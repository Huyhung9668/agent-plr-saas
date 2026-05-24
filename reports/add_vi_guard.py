from pathlib import Path
p=Path('web_app.py')
text=p.read_text(encoding='utf-8')
old='''            if attachment_context:\n                full_question = f"{full_question}\\n\\n## File nguoi dung vua gui\\n{attachment_context}"\n            limit_per_brain = RAG_MODE_TOPK.get(response_mode, RAG_MODE_TOPK["fast"])\n'''
new='''            if attachment_context:\n                full_question = f"{full_question}\\n\\n## File người dùng vừa gửi\\n{attachment_context}"\n            vietnamese_guard = (\n                "## BẮT BUỘC NGÔN NGỮ\\n"\n                "- Trả lời bằng TIẾNG VIỆT rõ ràng, dễ hiểu cho người dùng Việt Nam.\\n"\n                "- Chỉ giữ thuật ngữ tiếng Anh khi đó là tên file, tag, lệnh, brand, hoặc tiêu đề kỹ thuật cần giữ nguyên.\\n"\n                "- Không tự chuyển toàn bộ câu trả lời sang tiếng Anh.\\n"\n            )\n            full_question = f"{vietnamese_guard}\\n\\n{full_question}"\n            limit_per_brain = RAG_MODE_TOPK.get(response_mode, RAG_MODE_TOPK["fast"])\n'''
if old not in text:
    raise SystemExit('target not found')
p.write_text(text.replace(old,new), encoding='utf-8')

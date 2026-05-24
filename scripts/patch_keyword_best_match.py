from pathlib import Path
p=Path('product_pipeline.py')
s=p.read_text(encoding='utf-8')
old='''    folded = (message or "").lower()\n    for skill in load_skill_index():\n        if any(str(keyword).lower() in folded for keyword in skill.get("trigger_keywords", [])):\n            return _skill_debug(skill, int(skill["step_number"]), message, "keyword intent routes to 44-skill file")\n    return {"selected_route": "", "selected_skill": None, "explicit_step": None}\n'''
new='''    folded = (message or "").lower()\n    best_match: tuple[int, dict] | None = None\n    for skill in load_skill_index():\n        for keyword in skill.get("trigger_keywords", []):\n            keyword_text = str(keyword).lower()\n            if keyword_text and keyword_text in folded:\n                match_len = len(keyword_text)\n                if best_match is None or match_len > best_match[0]:\n                    best_match = (match_len, skill)\n    if best_match:\n        skill = best_match[1]\n        return _skill_debug(skill, int(skill["step_number"]), message, "keyword intent routes to 44-skill file")\n    return {"selected_route": "", "selected_skill": None, "explicit_step": None}\n'''
if old not in s:
    raise SystemExit('target not found')
s=s.replace(old,new)
p.write_text(s,encoding='utf-8')
print('patched keyword best match')

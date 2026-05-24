import json, pathlib, sys
data=json.loads(pathlib.Path('chat_history/threads.json').read_text(encoding='utf-8'))
t=data['threads'][0]
out=f"active={data['activeThreadId']}\ntitle={t['title']}\nmessages={len(t['messages'])}\npinned={t.get('pinned')}\nfirst={t['messages'][0]['content']}\n"
sys.stdout.buffer.write(out.encode('utf-8'))

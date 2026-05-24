import json
p='chat_history/threads.json'
d=json.load(open(p,encoding='utf-8'))
print(d.keys())
print('active',d.get('activeThreadId'))
for t in d.get('threads',[])[:8]:
    print('THREAD', t.get('id'), t.get('title'), t.get('updatedAt'), len(t.get('messages',[])))
    for m in t.get('messages',[])[-5:]:
        print(' ', m.get('role'), str(m.get('content',''))[:500].replace('\n',' | '), 'files', len(m.get('files',[]) or []))
    print()

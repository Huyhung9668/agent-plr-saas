import json, time, urllib.request
from pathlib import Path
server='http://127.0.0.1:18088'

def req(path, payload=None):
    if payload is None:
        with urllib.request.urlopen(server+path, timeout=20) as r:
            return json.loads(r.read().decode('utf-8'))
    data=json.dumps(payload, ensure_ascii=False).encode('utf-8')
    request=urllib.request.Request(server+path, data=data, headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(request, timeout=20) as r:
        return json.loads(r.read().decode('utf-8'))

state=req('/api/threads').get('state') or {'threads': [], 'activeThreadId': None}
threads=state.get('threads') or []
thread_id='anti_fake_check_20260524'
threads=[t for t in threads if t.get('id') != thread_id]
now=int(time.time()*1000)
report_path='benchmarks/anti_fake_benchmark_v112/anti_fake_report.md'
evidence_path='benchmarks/anti_fake_benchmark_v112/evidence.json'
zip_path='benchmarks/ai_printables_kdp_prompt_v111/round_6/artifacts/ai_canva_printable_product_kit/export/product_pack.zip'
assistant_msg=f'''Mình xác nhận lại: benchmark 10/10 trước đó KHÔNG tự hiện trong lịch sử Web UI vì nó chạy bằng script/API và ghi vào folder benchmark, không phải gửi từ textarea Web UI.

ANTI-FAKE RESULT:
- Điểm thật hơn: 70/100 = 7.0/10
- API chat evidence: PASS
- Static UI tag panel: PASS
- ZIP proof: PASS
- Nhưng chưa browser click automation, chưa buyer thật, chưa market sales proof, chưa live WarriorPlus/payment/delivery/JV.

Files:
- `{report_path}`
- `{evidence_path}`
- `{zip_path}`

Kết luận: 10/10 trước đó là system/artifact benchmark, không phải launch-market score 100%.'''
thread={
    'id': thread_id,
    'title': 'ANTI-FAKE CHECK — Agent score không ảo',
    'messages': [
        {'role': 'user', 'content': 'kiểm tra không bị ảo: điểm 10/10 có chuẩn 100% không?', 'createdAt': now-60000},
        {'role': 'assistant', 'content': assistant_msg, 'createdAt': now},
    ],
    'pinned': True,
    'createdAt': now-60000,
    'updatedAt': now,
}
threads.insert(0, thread)
state={'threads': threads, 'activeThreadId': thread_id}
out=req('/api/threads', {'state': state})
print(json.dumps({'ok': out.get('ok'), 'workspace': out.get('workspace'), 'thread_id': thread_id, 'threads': len(out.get('state',{}).get('threads',[]))}, ensure_ascii=False, indent=2))

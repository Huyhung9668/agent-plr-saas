import json, urllib.request, time
prompt = "#ai-printables-kdp-prompt #product-blueprint #deep-file-writer #sales-page #warriorplus-listing #jv-pack #delivery-support #buyer-test #ai-replace-risk #refund-risk #license-check #export-zip\n\nTôi chọn sản phẩm: AI Etsy Printable Bundle Builder.\n\nHãy tạo thành một sản phẩm WarriorPlus bán được, không chỉ phân tích."
payload={"question":prompt,"mode":"deep","model":"agent","toolMode":"auto","tags":["#ai-printables-kdp-prompt","#deep-file-writer","#export-zip"]}
req=urllib.request.Request('http://127.0.0.1:18088/api/chat_stream', data=json.dumps(payload,ensure_ascii=False).encode('utf-8'), headers={'Content-Type':'application/json'}, method='POST')
start=time.time()
with urllib.request.urlopen(req, timeout=20) as r:
    body=r.read(2000).decode('utf-8','replace')
print('elapsed', round(time.time()-start,2))
print(body[:1800])

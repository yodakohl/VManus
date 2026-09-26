#!/usr/bin/env python3
"""Verify/fetch fixed later external-source receipts; never a target fetcher."""
import hashlib,json,urllib.request,urllib.parse
from pathlib import Path
B=Path(__file__).resolve().parent
rows=[]
for x in json.loads((B/'COSMIC_CONTINUATION_RECEIPTS.json').read_text())['images']:
    rows.append((x['image_url'],x['sha256'],x['bytes'],Path(x['cached_path']).name))
m=json.loads((B/'MUNICH_PICTURE_INSTRUCTIONS_RECEIPTS.json').read_text())
for x in m['images']:
    rows.append((x['image_url'],x['sha256'],x['bytes'],Path(x['cache_path']).name))
for x in m.get('clarification_20260926',{}).get('comparison_receipts',[]):
    rows.append((x['url'],x['sha256'],x['bytes'],Path(x['cache_path']).name))
x=m.get('clarification_20260926',{}).get('context_page_receipt')
if x:
    rows.append((x['image_url'],x['sha256'],x['bytes'],Path(x['cache_path']).name))
c=json.loads((B/'CPG644_COMPARISON_RECEIPT.json').read_text())
rows.append((c['url'],c['sha256'],c['bytes'],Path(c['path']).name))
hosts={'digital.blb-karlsruhe.de','api.digitale-sammlungen.de','kdih.badw.de','diglib.hab.de'}
seen=set()
for url,sha,n,name in rows:
    if (url,sha) in seen: continue
    seen.add((url,sha))
    u=urllib.parse.urlparse(url)
    assert u.scheme=='https' and u.hostname in hosts,url
    p=B/'external_cache'/name
    data=p.read_bytes() if p.exists() else urllib.request.urlopen(url,timeout=45).read()
    assert hashlib.sha256(data).hexdigest()==sha,url
    assert len(data)==n,url
    p.parent.mkdir(exist_ok=True);p.write_bytes(data)
    print('OK',name,sha)
print(len(seen),'fixed external images verified; not visual or semantic validation')

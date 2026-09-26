#!/usr/bin/env python3
"""Fetch/check the fixed external passage witnesses, never Voynich material."""
from pathlib import Path
import hashlib,json,urllib.request,urllib.parse
B=Path(__file__).resolve().parent
entries=json.loads((B/'PRINT_CONTINUATION_RECEIPTS.json').read_text())['images']
for name,row in json.loads((B/'SOURCE_ELEMENT_PASSAGE_RECEIPTS.json').read_text())['sources'].items():
    if 'image_url' in row and 'sha256' in row:
        entries.append(dict(url=row['image_url'],sha256=row['sha256'],filename=name+'.jpg'))
seen={}
for row in entries:
    url=row['url'];parsed=urllib.parse.urlparse(url)
    assert parsed.scheme=='https' and parsed.hostname in {'digital.blb-karlsruhe.de','diglib.hab.de'}
    if url in seen:
        assert seen[url]==row['sha256'];continue
    seen[url]=row['sha256']
    dest=B/'external_cache'/('passage_'+row.get('filename',Path(row.get('path','image.jpg')).name))
    if dest.exists():data=dest.read_bytes()
    else:
        with urllib.request.urlopen(url,timeout=60) as response:data=response.read()
    actual=hashlib.sha256(data).hexdigest()
    assert actual==row['sha256'],'Changed source bytes: '+url
    dest.parent.mkdir(exist_ok=True);dest.write_bytes(data)
    print('OK',url,actual)
print(len(seen),'external image sources hash-verified; no visual/meaning validation')

#!/usr/bin/env python3
"""Fetch final admitted panel/details, never wider navigation-error image."""
from pathlib import Path
import hashlib,json,urllib.request
B=Path(__file__).resolve().parents[1]
R=B.parents[2]
records=[json.loads((B/'artifacts/SOURCE_FINAL.json').read_text())]
records+=json.loads((B/'artifacts/DETAIL_SOURCES_B.json').read_text())['details']
for d in records:
    x,y,w,h=d['region']
    assert min(x,y)>=0 and w>0 and h>0 and x+w<=3000 and y+h<=3890
    assert d['url'].startswith('https://collections.library.yale.edu/iiif/2/1006229/')
    p=R/d['path']
    if p.exists() and hashlib.sha256(p.read_bytes()).hexdigest()==d['sha256']: continue
    data=urllib.request.urlopen(d['url'],timeout=60).read()
    assert hashlib.sha256(data).hexdigest()==d['sha256'],'Source changed: '+d['url']
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_bytes(data)
print('Final panel and nine bounded details verified.')

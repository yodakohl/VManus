#!/usr/bin/env python3
"""Reproduce the three fixed external cosmic-image receipts only."""
import hashlib,json,urllib.request,urllib.parse
from pathlib import Path
B=Path(__file__).resolve().parent
receipt=json.loads((B/'COSMIC_BANDS_RECEIPTS.json').read_text())
rows=receipt['karlsruhe_images']+[receipt['tuebingen_comparator']]
for row in rows:
 url=row['image_url']; u=urllib.parse.urlparse(url)
 assert u.scheme=='https' and u.hostname in {'digital.blb-karlsruhe.de','opendigi.ub.uni-tuebingen.de'}
 dest=B/'external_cache'/Path(row['repository_relative_cached_path']).name
 data=dest.read_bytes() if dest.exists() else urllib.request.urlopen(url,timeout=60).read()
 assert hashlib.sha256(data).hexdigest()==row['sha256'],url
 assert len(data)==row['bytes'],url
 dest.parent.mkdir(exist_ok=True);dest.write_bytes(data)
 print('OK',url,row['sha256'])
print('3 fixed external images hash-verified; no image interpretation or meaning validation')

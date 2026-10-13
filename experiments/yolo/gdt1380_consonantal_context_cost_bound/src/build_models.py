"""Optional reconstruction from locally owned, hash-matched prepared packs."""
from pathlib import Path
from collections import defaultdict
import gzip,hashlib,json
B=Path(__file__).resolve().parents[1];R=B.parents[2];C='bcdfghjklmnpqrstvwxyz';A=C+' '
m=json.loads((R/'gdt001_language_pack_manifest.json').read_text());out={}
for name,entry in sorted(m['packs'].items()):
 p=R/'.gdt001/language_packs'/f'{name}.txt';raw=p.read_bytes();assert hashlib.sha256(raw).hexdigest()==entry['prepared_sha256']
 rows=defaultdict(lambda:[0]*22);lines=events=0
 for line in raw.decode().splitlines():
  ws=[''.join(c for c in w if c not in 'aeiou') for w in line.split()];text=' '.join(w for w in ws if w)
  if not text:continue
  assert set(text)<=set(A);h=('^','^');lines+=1
  for c in text:rows[h][A.index(c)]+=1;events+=1;h=(h[1],c)
 out[name]={'provenance':entry,'rows':[{'context':list(k),'counts':v} for k,v in sorted(rows.items())],'source_lines':lines,'events':events}
 print(name,lines,events,flush=True)
(B/'artifacts/MODEL_COUNTS.json.gz').write_bytes(gzip.compress((json.dumps(out,sort_keys=True,separators=(',',':'))+'\n').encode(),mtime=0))

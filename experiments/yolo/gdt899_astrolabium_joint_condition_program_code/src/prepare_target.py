#!/usr/bin/env python3
"""Project the already exposed odd-only GDT893 packet; no new corpus query."""
import argparse,gzip,hashlib,json,re
from pathlib import Path
EXPECTED='1b536c8f46dca72522d9cd059869a963aad124ee5da44218b886c88d91ddf2ed'
p=argparse.ArgumentParser();p.add_argument('--packet',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
raw=a.packet.read_bytes();assert hashlib.sha256(raw).hexdigest()==EXPECTED
d=json.loads(gzip.decompress(raw));assert d['schema']=='GDT893_ODD_ONLY_FIT_PACKET_V1'
counts={'ZL3b':14,'IT2a':259,'RF1b':11,'CONSENSUS':1};panels={}
for edition,n in counts.items():
 rows=d['panels'][edition];assert len(rows)==n;out=[]
 for r in rows:
  assert not r['page'].startswith('f84')
  assert re.fullmatch(r'f[0-9]+',r['physical_folio']) and int(r['physical_folio'][1:])%2==1
  assert r['words'] and all(re.fullmatch('[a-z]+',w) for w in r['words'])
  assert len(r['words'])==len(r['source_group_ids'])
  out.append({k:r[k] for k in ('id','page','physical_folio','words','source_group_ids')}|{'text':' '.join(r['words'])})
 assert len({r['id'] for r in out})==len(out);panels[edition]=out
answer={'schema':'GDT899_TARGET_INPUT_V1','inherited_packet_sha256':EXPECTED,'inherited_input_lock':d['input_lock'],'panels':panels,'projection':'All raw eligible paragraph groups, joined by one U+0020 between successive groups including across source lines. This is the fixed transcription channel, not a claim about physical space width or native line-break encoding. No group removed or merged.','scope':'Only the already exposed GDT893 odd-leaf eligible paragraph packet; no complete-manuscript coverage or held access. Readings are panels of one manuscript.','source_coverage_required':24,'capacity':{e:('SUFFICIENT_COUNT_FOR_FIT' if n>=24 else 'INSUFFICIENT_PARAGRAPH_COUNT') for e,n in counts.items()}}
a.output.write_text(json.dumps(answer,ensure_ascii=False,indent=2)+'\n');print('frozen counts',counts,'sha256',hashlib.sha256(a.output.read_bytes()).hexdigest())

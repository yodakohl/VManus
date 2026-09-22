#!/usr/bin/env python3
"""Fetch only the four preregistered historical images; never manuscript targets."""
from pathlib import Path
import hashlib,json,urllib.request,tempfile
ROOT=Path(__file__).resolve().parents[4]
EXP=Path(__file__).resolve().parents[1]
spec=json.loads((EXP/'src/SOURCE.json').read_text())
cache=Path(tempfile.gettempdir())/'vmanus_gdt1032_owned_images';cache.mkdir(exist_ok=True)
rows=[]
for r in spec['images']:
 row=dict(r);dst=cache/(r['id']+'.jpg')
 try:
  req=urllib.request.Request(r['url'],headers={'User-Agent':'VManus source verification'})
  with urllib.request.urlopen(req,timeout=spec['download_timeout_seconds']) as f:
   data=f.read(spec['max_download_bytes']+1)
  row['bytes']=len(data);row['observed_sha256']=hashlib.sha256(data).hexdigest()
  if len(data)>spec['max_download_bytes']:row['status']='SIZE_LIMIT'
  elif row['observed_sha256']!=r['expected_sha256']:row['status']='HASH_MISMATCH_DO_NOT_OPEN'
  else:dst.write_bytes(data);row['status']='HASH_VERIFIED'
 except Exception as e:row['status']='TRANSPORT_FAILURE';row['error_type']=type(e).__name__
 rows.append(row)
(EXP/'artifacts/FETCH.json').write_text(json.dumps(rows,indent=2)+'\n')
print(json.dumps([{k:r[k] for k in ('id','status')} for r in rows]))

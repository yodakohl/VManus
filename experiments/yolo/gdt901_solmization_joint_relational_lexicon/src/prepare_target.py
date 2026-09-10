#!/usr/bin/env python3
import argparse,gzip,hashlib,json
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('packet',type=Path);a=p.parse_args()
 raw=a.packet.read_bytes();sha=hashlib.sha256(raw).hexdigest()
 assert sha=='1b536c8f46dca72522d9cd059869a963aad124ee5da44218b886c88d91ddf2ed'
 parent=json.loads(gzip.decompress(raw));panels=parent['panels']
 for rows in panels.values():
  for row in rows:
   assert not row['page'].startswith('f84') and int(row['physical_folio'][1:])%2==1
   assert row['words'] and len(row['words'])==len(row['source_group_ids'])
 result={'schema':'GDT901_ODD_COMPLETE_PARAGRAPHS_V1','parent_sha256':sha,'panels':panels,'scope':'Alreadyexposed GDT893 odd fitting packet; no even bodies.'}
 dest=BASE/'artifacts/TARGET_INPUT.json';dest.write_text(json.dumps(result,ensure_ascii=False,separators=(',',':'))+'\n')
 print(hashlib.sha256(dest.read_bytes()).hexdigest(),{k:len(v) for k,v in panels.items()})
if __name__=='__main__':main()

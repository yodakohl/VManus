#!/usr/bin/env python3
import argparse,gzip,hashlib,json
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--parent-packet',type=Path,required=True);a=p.parse_args()
 raw=a.parent_packet.read_bytes();sha=hashlib.sha256(raw).hexdigest();assert sha=='1b536c8f46dca72522d9cd059869a963aad124ee5da44218b886c88d91ddf2ed'
 parent=json.loads(gzip.decompress(raw));out={'schema':'GDT902_ODD_COMPLETE_PARAGRAPHS_V1','parent_sha256':sha,'panels':parent['panels']}
 (BASE/'artifacts/TARGET_INPUT.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'paragraph_counts':{p:len(rs) for p,rs in out['panels'].items()},'target_sha256':hashlib.sha256((BASE/'artifacts/TARGET_INPUT.json').read_bytes()).hexdigest()}))
if __name__=='__main__':main()

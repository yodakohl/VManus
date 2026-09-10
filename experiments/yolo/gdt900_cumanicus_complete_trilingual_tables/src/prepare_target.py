#!/usr/bin/env python3
"""Project every eighteen-group window from the already odd-only frozen packet."""
import argparse,gzip,hashlib,json
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
def build(packet):
    out={}
    for panel, paragraphs in packet['panels'].items():
        windows=[]
        for p in paragraphs:
            assert not p['page'].startswith('f84') and int(p['physical_folio'][1:])%2==1
            words=p['words'];ids=p['source_group_ids'];assert len(words)==len(ids)
            for start in range(max(0,len(words)-17)):
                windows.append({'id':p['id']+'@'+str(start),'paragraph_id':p['id'],'page':p['page'],
                    'physical_folio':p['physical_folio'],'start':start,'words':words[start:start+18],
                    'source_group_ids':ids[start:start+18]})
        out[panel]=windows
    return out
def main():
    ap=argparse.ArgumentParser();ap.add_argument('packet',type=Path);a=ap.parse_args()
    digest=hashlib.sha256(a.packet.read_bytes()).hexdigest()
    assert digest=='1b536c8f46dca72522d9cd059869a963aad124ee5da44218b886c88d91ddf2ed'
    packet=json.loads(gzip.decompress(a.packet.read_bytes()))
    out={'schema':'GDT900_COMPLETE_ODD_WINDOW_TARGET_V1','parent_packet_sha256':digest,
         'scope':'Every complete18-group consecutivewindow whollyinside onealreadyexposed893oddparagraph; not newly certified native tables.',
         'panels':build(packet)}
    (BASE/'artifacts/TARGET_INPUT.json').write_text(json.dumps(out,ensure_ascii=False,separators=(',',':'))+'\n')
    print(json.dumps({k:len(v) for k,v in out['panels'].items()}))
if __name__=='__main__':main()

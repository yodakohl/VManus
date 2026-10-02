#!/usr/bin/env python3
"""Read-only registered source/census check; no pixel interpretation."""
from pathlib import Path
import json, hashlib
BASE=Path(__file__).resolve().parents[1]
ROOT=BASE.parents[2]
def check():
    source=json.loads((BASE/'src/SOURCE.json').read_text())
    for name in ('image','native_packet'):
        item=source[name]
        assert hashlib.sha256((ROOT/item['path']).read_bytes()).hexdigest()==item['sha256']
    native=json.loads((ROOT/source['native_packet']['path']).read_text())
    rows=native['rows']
    assert len(rows)==97
    it={(x['locus'],int(x['source_group_index'])):x for x in rows if x['edition']=='IT2a'}
    assert len(it)==32 and len(source['focal_positions'])==10
    for x in source['focal_positions']+source['controls']:
        assert it[x['locus'],x['IT_group']]['ivtff_group_raw']==x['literal']
    assert {x['locus'] for x in rows}=={'f83r.'+str(i) for i in range(25,31)}
    return {'status':'REGISTERED_SOURCE_CENSUS_PASS_NOT_VISUAL_JUDGMENT','native_groups':97,'focal_positions':10,'confirmed_words':0}
if __name__=='__main__': print(json.dumps(check(),indent=2))

#!/usr/bin/env python3
"""Registered one-sign whole-group inventory; selector-first source access."""
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone
import csv, hashlib, io, json, subprocess
D=Path(__file__).resolve().parents[1]; ROOT=D.parents[2]; A=D/'artifacts'
def main():
    assert not (A/'RESULT.json').exists()
    started=datetime.now(timezone.utc).isoformat()
    for p,h in json.loads((A/'REGISTRATION_LOCK.json').read_text())['files'].items():
        assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    s=json.loads((D/'src/SPEC.json').read_text())
    allowed=json.loads((ROOT/s['scope_spec']).read_text())['allowed']
    assert len(allowed)==179 and all(not x.startswith('f84') and x!='f116v' for x in allowed)
    cmd=['./vmanus-exp','query-tsv',s['source'],'--selector','page']
    for x in allowed: cmd+=['--allow',x]
    cmd+=['--columns','edition,page,locus,kind,source_group_index,ivtff_group_raw,left_separator,right_separator']
    call=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True,check=True)
    out={ed:{'counts':Counter(),'pages':{},'witnesses':{}} for ed in ['IT2a','RF1b','ZL3b']}
    ids=set()
    for r in csv.DictReader(io.StringIO(call.stdout),delimiter='\t'):
        key=f"{r['edition']}|{r['locus']}|G{int(r['source_group_index']):03d}"
        assert key not in ids; ids.add(key)
        ed=r['edition']; assert ed in out
        if r['kind']!='P' or r['left_separator']!='DEFINITE_SPACE' or r['right_separator']!='DEFINITE_SPACE':continue
        word=r['ivtff_group_raw']
        if word not in s['signs']:continue
        o=out[ed];o['counts'][word]+=1;o['pages'].setdefault(word,set()).add(r['page'])
        o['witnesses'].setdefault(word,dict(id=key,word=word,page=r['page'],locus=r['locus'],source_group_index=int(r['source_group_index']),left_separator=r['left_separator'],right_separator=r['right_separator']))
    for o in out.values():
        o['types']=len(o['counts']);o['tokens']=sum(o['counts'].values())
        o['counts']=dict(sorted(o['counts'].items()))
        o['pages']={k:sorted(v) for k,v in sorted(o['pages'].items())}
        o['witnesses']=dict(sorted(o['witnesses'].items()))
        o['exceeds_capacity']=o['types']>s['capacity']
        o['literal_reserved_conflicts']={k:v for k,v in o['counts'].items() if k in s['forbidden_single_roots']}
    n=sum(o['exceeds_capacity'] for o in out.values())
    status=('ALL_GLOBAL_RELABELINGS_EXCLUDED' if n==3 else 'GLOBAL_RELABELING_EXCLUDED_SOME_READINGS' if n else 'NO_ONE_SIGN_CARDINALITY_CONTRADICTION')
    result={'experiment':'GDT1227','status':status,'capacity':s['capacity'],'readings':out,'claim_ceiling':s['claim_ceiling']}
    (A/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    (A/'RUN_RECEIPT.json').write_text(json.dumps({'started_utc':started,'finished_utc':datetime.now(timezone.utc).isoformat(),'guard_command':cmd,'guard_receipt':call.stderr.strip(),'guard_output_sha256':hashlib.sha256(call.stdout.encode()).hexdigest(),'unique_source_ids':len(ids)},indent=2)+'\n')
    print(json.dumps({'status':status,'readings':{k:{x:v[x] for x in ['types','tokens','counts','literal_reserved_conflicts']} for k,v in out.items()}},indent=2))
if __name__=='__main__': main()

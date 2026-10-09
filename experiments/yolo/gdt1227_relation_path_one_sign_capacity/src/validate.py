#!/usr/bin/env python3
"""Independent regex grouping and sorted-list reconstruction, without runner."""
from pathlib import Path
from datetime import datetime, timezone
import csv,hashlib,io,json,re,subprocess
D=Path(__file__).resolve().parents[1]; ROOT=D.parents[2]; A=D/'artifacts'
s=json.loads((D/'src/SPEC.json').read_text());r=json.loads((A/'RESULT.json').read_text())
for p,h in json.loads((A/'REGISTRATION_LOCK.json').read_text())['files'].items():
    assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
rule=json.loads((ROOT/s['rules']).read_text())
assert 'other13 one-mark roots' in rule['lexical_words']['root']
assert len(s['signs'])==22 and len(set(s['forbidden_single_roots']))==9
assert set(s['forbidden_single_roots']) < set(s['signs']) and s['capacity']==13
allowed=json.loads((ROOT/s['scope_spec']).read_text())['allowed']
assert len(allowed)==179 and all(not p.startswith('f84') and p!='f116v' for p in allowed)
cmd=['./vmanus-exp','query-tsv',s['source'],'--selector','page']
for p in allowed:cmd+=['--allow',p]
cmd+=['--columns','edition,page,locus,kind,source_group_index,ivtff_group_raw,left_separator,right_separator']
call=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True,check=True)
pattern=re.compile(r'(?:c[ktpf]h|ch|sh|[aoeindqysrlmktpf])')
collected={ed:[] for ed in ('IT2a','RF1b','ZL3b')};seen=set()
for row in csv.DictReader(io.StringIO(call.stdout),delimiter='\t'):
    ident='{}|{}|G{:03d}'.format(row['edition'],row['locus'],int(row['source_group_index']))
    assert ident not in seen;seen.add(ident)
    assert row['edition'] in collected
    if row['kind']=='P' and (row['left_separator'],row['right_separator'])==('DEFINITE_SPACE','DEFINITE_SPACE') and pattern.fullmatch(row['ivtff_group_raw']):
        collected[row['edition']].append((row['ivtff_group_raw'],row,ident))
for ed,items in collected.items():
    actual=r['readings'][ed]; words=sorted(set(x[0] for x in items))
    expected_counts={w:sum(x[0]==w for x in items) for w in words}
    assert actual['counts']==expected_counts
    assert actual['types']==len(words) and actual['tokens']==len(items)
    assert actual['exceeds_capacity']==(len(words)>13)
    assert actual['literal_reserved_conflicts']=={w:expected_counts[w] for w in words if w in {'a','o','e','i','n','d','y','s','r'}}
    for w in words:
        assert actual['pages'][w]==sorted(set(row['page'] for word,row,_ in items if word==w))
        word,row,ident=next(x for x in items if x[0]==w)
        assert actual['witnesses'][w]==dict(id=ident,word=w,page=row['page'],locus=row['locus'],source_group_index=int(row['source_group_index']),left_separator='DEFINITE_SPACE',right_separator='DEFINITE_SPACE')
n=sum(len(set(x[0] for x in v))>13 for v in collected.values())
expected_status='ALL_GLOBAL_RELABELINGS_EXCLUDED' if n==3 else 'GLOBAL_RELABELING_EXCLUDED_SOME_READINGS' if n else 'NO_ONE_SIGN_CARDINALITY_CONTRADICTION'
assert r['status']==expected_status
receipt=json.loads((A/'RUN_RECEIPT.json').read_text())
assert receipt['guard_output_sha256']==hashlib.sha256(call.stdout.encode()).hexdigest()
assert receipt['unique_source_ids']==len(seen)
v={'experiment':'GDT1227','status':'PASS','validated_utc':datetime.now(timezone.utc).isoformat(),'checks':['frozen inputs and code','independent regex source reconstruction','counts, dispersion, first witnesses and decisions','13-root mathematical capacity separately reviewed in preregistration'],'native_meanings':0}
(A/'VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v,indent=2))

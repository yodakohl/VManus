#!/usr/bin/env python3
"""Frozen, guarded corpus extraction and formal code capacity search."""
from pathlib import Path
from datetime import datetime,timezone
from functools import lru_cache
from collections import Counter
import json,csv,io,re,hashlib,gzip,subprocess
from engine import solve
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts'

def sha(data):return hashlib.sha256(data).hexdigest()
def save(name,obj):
    data=(json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n').encode()
    (A/name).write_bytes(gzip.compress(data,compresslevel=9,mtime=0) if name.endswith('.gz') else data)

def main():
    assert not (A/'RESULT.json').exists()
    started=datetime.now(timezone.utc).isoformat()
    lock=json.loads((A/'REGISTRATION_LOCK.json').read_text())
    for p,h in lock['files'].items():assert sha((ROOT/p).read_bytes())==h,p
    spec=json.loads((D/'src/SPEC.json').read_text());signs=spec['signs']
    allowed=json.loads((ROOT/spec['scope_spec']).read_text())['allowed']
    assert len(allowed)==179 and all(not p.startswith('f84') and p!='f116v' for p in allowed)
    cmd=['./vmanus-exp','query-tsv',spec['source'],'--selector','page']
    for p in allowed:cmd+=['--allow',p]
    cmd+=['--columns','edition,page,locus,kind,source_group_index,ivtff_group_raw,left_separator,right_separator']
    call=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,check=True)
    @lru_cache(None)
    def parses(raw):
        if raw=='':return ((),)
        out=[]
        for g in signs:
            if raw.startswith(g):
                out.extend((g,)+tail for tail in parses(raw[len(g):]))
                if len(out)>1:return tuple(out[:2])
        return tuple(out)
    grouped={ed:[]for ed in ['IT2a','RF1b','ZL3b']};counts={ed:Counter()for ed in grouped};seen=set()
    for r in csv.DictReader(io.StringIO(call.stdout),delimiter='\t'):
        ed=r['edition'];assert ed in grouped
        identifier=f"{ed}|{r['locus']}|G{int(r['source_group_index']):03d}"
        assert identifier not in seen;seen.add(identifier);c=counts[ed];c['raw']+=1
        if r['kind']!='P':c['non_prose']+=1;continue
        if r['left_separator']!='DEFINITE_SPACE'or r['right_separator']!='DEFINITE_SPACE':c['non_interior']+=1;continue
        raw=r['ivtff_group_raw']
        if not re.fullmatch('[a-z]+',raw):c['non_literal']+=1;continue
        units=parses(raw)
        if len(units)!=1:c['non_unique_parse']+=1;continue
        c['eligible']+=1;r['id']=identifier;r['units']=list(units[0]);grouped[ed].append(r)
    save('GROUPS.json.gz',grouped)
    result={'experiment':'GDT1233','readings':{},'claim_ceiling':spec['claim_ceiling']}
    for ed,rows in grouped.items():
        first={}
        for row in rows:first.setdefault(row['ivtff_group_raw'],row)
        unique=[first[k]for k in sorted(first)]
        words=[(r['id'],tuple(r['units']))for r in unique]
        local_start=datetime.now(timezone.utc).isoformat()
        out=solve(words,signs,spec['per_reader_seconds'])
        cert=out.pop('certificate');save(f'CERTIFICATE_{ed}.json.gz',cert)
        result['readings'][ed]={'status':out['status'],'counts':dict(counts[ed]),'types':len(words),'glyph_tokens':sum(len(r['units'])for r in rows),'alphabet_present':sorted({g for r in rows for g in r['units']}),'eligible_ids_sha256':sha('\n'.join(r['id']for r in rows).encode()),'type_order_ids_sha256':sha('\n'.join(r['id']for r in unique).encode()),'statistics':out['statistics'],'witness':out['witness'],'started_utc':local_start,'finished_utc':datetime.now(timezone.utc).isoformat()}
        print(ed,out['status'],out['statistics'],flush=True)
    statuses=[v['status']for v in result['readings'].values()]
    result['status']=('ALL_USED_CODES_SINGLETON_ALL_READINGS'if all(x=='ALL_USED_CODES_SINGLETON'for x in statuses)else'READER_SPECIFIC_CODE_CAPACITY')
    save('RESULT.json',result)
    save('RUN_RECEIPT.json',{'started_utc':started,'finished_utc':datetime.now(timezone.utc).isoformat(),'guard_command':cmd,'guard_receipt':call.stderr.strip(),'guard_output_sha256':sha(call.stdout.encode()),'unique_source_ids':len(seen)})
    print(result['status'])
if __name__=='__main__':main()

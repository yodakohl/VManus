#!/usr/bin/env python3
"""Independent odd-only complete window replay; no primary runner imports."""
import json,re,hashlib
from pathlib import Path
from collections import defaultdict
E=Path(__file__).resolve().parents[1]
R=E.parents[2]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text())
def eligible(gs):
    return all(re.fullmatch('[a-z]+',g['ivtff_group_raw']) for g in gs) and all(int(b['source_group_index'])==int(a['source_group_index'])+1 and a['right_separator']==b['left_separator']=='DEFINITE_SPACE' for a,b in zip(gs,gs[1:]))
def census(data):
    counts=dict.fromkeys(['lines','raw_triples','eligible_triples','distinct_triples','raw_fives','eligible_fives','serial_fives'],0)
    triples=defaultdict(lambda:[[],[]])
    for line in data['lines']:
        m=line['metadata']; page=m['page']; leaf=int(re.match(r'f(\d+)',page)[1])
        assert not page.startswith('f84') and leaf%2==1
        if m['kind']!='P': continue
        counts['lines']+=1
        gs=[dict(zip(data['group_columns'],g)) for g in line['groups']]
        for size,name in [(3,'triples'),(5,'fives')]:
            for i in range(len(gs)-size+1):
                counts['raw_'+name]+=1; window=gs[i:i+size]
                if not eligible(window): continue
                counts['eligible_'+name]+=1
                w=[g['ivtff_group_raw'] for g in window]
                if size==5:
                    counts['serial_fives']+=int(w[1]==w[3] and len({w[0],w[2],w[4]})==3 and w[1] not in (w[0],w[2],w[4]))
                elif len(set(w))==3:
                    counts['distinct_triples']+=1
                    a,b=sorted((w[0],w[2]))
                    triples[(w[1],a,b)][int(w[0]!=a)].append(dict(leaf=leaf,locus=m['locus'],page=page,source_ids=[g['source_group_id'] for g in window],start_index=int(window[0]['source_group_index']),words=w))
    pairs=[]; centers=defaultdict(list)
    for (center,a,b),(f,v) in sorted(triples.items()):
        if not any(x['leaf']!=y['leaf'] for x in f for y in v): continue
        p=dict(center=center,endpoints=[a,b],forward=f,reverse=v,leaves=sorted({x['leaf'] for x in f+v}))
        pairs.append(p);centers[center].append(p)
    candidates=[]
    for center,ps in sorted(centers.items()):
        leaves=sorted({l for p in ps for l in p['leaves']})
        if len(ps)>=2 and len(leaves)>=3: candidates.append(dict(center=center,leaves=leaves,reciprocal_pairs=ps))
    return dict(candidates=candidates,denominators=counts,reciprocal_pairs=pairs)
def canonical(x):
    if isinstance(x,dict): return {k:canonical(v) for k,v in sorted(x.items())}
    if isinstance(x,list): return sorted((canonical(v) for v in x),key=lambda v:json.dumps(v,sort_keys=True))
    return x
def fixtures():
    cols=['source_group_id','source_group_index','ivtff_group_raw','left_separator','right_separator']
    def line(leaf,words,uncertain=False):
        return {'metadata':dict(page=f'f{leaf}r',locus=f'f{leaf}r.1',kind='P'),'groups':[[str(i),str(i),w,'DEFINITE_SPACE','UNCERTAIN_SPACE' if uncertain and i==2 else 'DEFINITE_SPACE'] for i,w in enumerate(words,1)]}
    def test(lines): return census(dict(group_columns=cols,lines=lines))
    assert len(test([line(1,['a','x','b']),line(3,['b','x','a'])])['reciprocal_pairs'])==1
    assert not test([line(1,['a','x','b']),line(1,['b','x','a'])])['reciprocal_pairs']
    assert test([line(1,['a','x','b','x','c'])])['denominators']['serial_fives']==1
    assert test([line(1,['a','x','b','x','a'])])['denominators']['serial_fives']==0
    assert test([line(1,['a','x','b','x','c'],True)])['denominators']['eligible_fives']==0
    assert len(test([line(1,['a','x','b']),line(3,['b','x','a']),line(3,['c','x','d']),line(5,['d','x','c'])])['candidates'])==1
    return 6

def main():
    lock=read(E/'PREREG_LOCK.json')
    for path,h in lock['files'].items(): assert sha(R/path)==h,path
    assert not list(E.rglob('EVALUATION_*'))
    assert not list(E.rglob('DISCOVERY_LOCK*'))
    summary={};sources={};outputs={}
    for ed in ['ZL3b','IT2a','RF1b']:
        p=R/f'experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts/SOURCE_DISCOVERY_{ed}.json'
        actual=census(read(p)); expected=read(E/f'artifacts/DISCOVERY_{ed}.json')
        assert canonical(actual)==canonical(expected),ed
        sources[str(p.relative_to(R))]=sha(p)
        summary[ed]=dict(candidates=[x['center'] for x in actual['candidates']],denominators=actual['denominators'],reciprocal_pairs=len(actual['reciprocal_pairs']))
    assert not summary['ZL3b']['candidates']
    assert read(E/'artifacts/DISCOVERY_RESULT.json')==summary
    assert read(E/'artifacts/CANDIDATES.json')==read(E/'artifacts/PREDICTIONS.json')==[]
    result=read(E/'artifacts/RESULT.json')
    assert result==dict(discovery=summary,evaluation_payload_parsed=False,meaning_claims=0,primary_nominees=[],significance_claim=False,source_exposed=True,status='NOMINATION_CAPACITY_STOP_NO_EVALUATION')
    for p in sorted((E/'artifacts').glob('*.json')):
        if p.name!='VALIDATION.json': outputs[p.name]=sha(p)
    receipt=dict(status='PASS',validator_sha256=sha(Path(__file__)),prereg_lock_sha256=sha(E/'PREREG_LOCK.json'),locked_files_verified=len(lock['files']),source_sha256=sources,output_sha256=outputs,discovery=summary,synthetic_checks=fixtures(),comparison='Complete occurrence multiset, all windows and denominators; canonical ordering preserves duplicates.',evaluation_payload_parsed=False,evaluation_files_absent=True,limits='Nomination capacity stop in ZL primary. IT chedy is descriptive only. No grammar, conjunction, meaning or absence-of-meaning conclusion.')
    (E/'artifacts/VALIDATION.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(json.dumps(receipt,sort_keys=True))
if __name__=='__main__': main()

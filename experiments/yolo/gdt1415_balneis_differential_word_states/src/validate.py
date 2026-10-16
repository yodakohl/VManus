#!/usr/bin/env python3
"""Independent direct state reconstruction for fixed source windows."""
import argparse,hashlib,itertools,json
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2];A=E/'artifacts'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def construct(groups,chars,b,m=27):
    if not groups or len(groups)!=len(chars):return None
    states={groups[0]:0};last=0
    for word,char in zip(groups[1:],chars[1:]):
        last=(last+char-b)%m
        if word in states and states[word]!=last:return None
        states[word]=last
    return {'states':states,'incoming':(b-chars[0])%m}

def rgs(n):
    def rec(p):
        if len(p)==n:yield tuple(p)
        else:
            for x in range(max(p,default=-1)+2):yield from rec(p+[x])
    yield from rec([])

def brute(pattern,chars,m):
    labels=sorted(set(pattern));found=set()
    for vals in itertools.product(range(m),repeat=len(labels)-1):
        h=dict(zip(labels,[0]+list(vals)))
        for b in range(m):
            if all((h[pattern[i]]-h[pattern[i-1]]+b)%m==chars[i] for i in range(1,len(pattern))):found.add(b)
    return found

def controls():
    total=0
    for m in [2,3]:
        for n in range(1,5):
            for pattern in rgs(n):
                for chars in itertools.product(range(m),repeat=n):
                    actual={b for b in range(m) if construct(pattern,chars,b,m) is not None}
                    assert actual==brute(pattern,chars,m);total+=1
    # A return over distance3 determines b only modulo9, not uniquely modulo27.
    p=['A','B','C','A'];c=[5,1,1,1]
    assert {b for b in range(27) if construct(p,c,b)}=={1,10,19}
    groups=['w'+str(i%13) for i in range(77)];h={w:(i*7)%27 for i,w in enumerate(sorted(set(groups)))};b=4;incoming=12
    chars=[];last=incoming
    for w in groups:chars.append((h[w]-last+b)%27);last=h[w]
    for cseq in [chars,list(reversed(chars))]:
        for beta in range(27):
            got=construct(groups,cseq,beta)
            if got:
                last=got['incoming']
                for w,c in zip(groups,cseq):assert (got['states'][w]-last+beta)%27==c;last=got['states'][w]
    planted=construct(groups,chars,b);assert planted is not None
    return {'status':'PASS','exhaustive_small_pattern_messages':total,'composite_noninvertible_fixture':True,'planted_77_and_reverse_direct_reencoding':True}

def evaluate(groups,values,b,m):
    table={groups[0]:0};last=0;comparison=0
    for i in range(1,len(groups)):
        last=(last+values[i]-b)%m;word=groups[i]
        if word in table:
            if table[word]!=last:return comparison,None
            comparison+=1
        table[word]=last
    return None,{'states':table,'incoming':(b-values[0])%m}

def validate():
    lock=read(E/'LOCK.json')
    for p,h in lock['files'].items():assert not Path(p).is_absolute() and sha(ROOT/p)==h,p
    for p in [Path(__file__),E/'src/run.py',E/'src/SPEC.json',E/'reproduce.py']:assert p.relative_to(ROOT).as_posix() in lock['files']
    s=read(E/'src/SPEC.json');worksheet=read(ROOT/s['worksheet_path'])
    unit=worksheet['source_original_wrapper']['source_unit'];old=read(ROOT/s['native_path'])
    assert old['original_source']==unit and unit['edition']==s['required_native_edition']
    assert [l['metadata']['locus'] for l in unit['lines']]==s['required_loci']
    col=unit['group_columns'].index('ivtff_group_raw')
    groups=[g[col] for line in unit['lines'] for g in line['groups']]
    assert len(groups)==s['width']==s['required_native_groups']==77
    first={};constraints=[]
    for j,g in enumerate(groups):
        if g in first:constraints.append([first[g],j])
        else:first[g]=j
    proj=read(ROOT/s['projections_path']);assert len(proj['projections'])==70
    for pin in ['source_pin','record_pin']:assert sha(ROOT/proj[pin]['path'])==proj[pin]['sha256']
    result=read(A/'RESULT.json')
    assert result['experiment_id']=='GDT1415' and result['status']=='COMPLETE_FIXED_SOURCE_DIFFERENTIAL_CAPACITY'
    assert result['native_group_count']==77 and result['distinct_native_forms']==len(set(groups))
    assert result['return_constraints']==constraints and result['word_meanings_assigned']==0 and result['claim_ceiling']==s['claim_ceiling']
    assert len(result['cases'])==140
    summaries=[]
    for pi,p in enumerate(proj['projections']):
        text=p['text'];offsets=p['source_offsets'];assert len(text)==len(offsets)==p['characters']
        bad=sorted(set(text)-set('abcdefghijklmnopqrstuvwxyz'));windows=max(0,len(text)-76)
        values=[ord(c)-96 for c in text]
        for di,direction in enumerate(s['directions']):
            pairs=[];witnesses=[];fail=[0]*len(constraints)
            if not bad:
                for start in range(windows):
                    vals=values[start:start+77]
                    if direction=='REVERSE':vals=vals[::-1]
                    for beta in range(27):
                        failure,state=evaluate(groups,vals,beta,27)
                        if failure is not None:fail[failure]+=1;continue
                        pairs.append([start,beta])
                        if len(witnesses)<s['witness_limit_per_case']:
                            physical=text[start:start+77];decoded=physical if direction=='FWD' else physical[::-1]
                            direct=construct(groups,[ord(c)-96 for c in decoded],beta)
                            assert direct==state
                            witnesses.append({'start':start,'beta':beta,'source_window':physical,'decoded_text':decoded,'state_by_form':state['states'],'incoming_state':state['incoming'],'source_start_offset':offsets[start],'source_last_offset':offsets[start+76]})
            surviving=[] if bad else [27*windows]
            if not bad:
                for count in fail:surviving.append(surviving[-1]-count)
                assert surviving[-1]==len(pairs)
            expected={'projection_id':p['id'],'direction':direction,'source_characters':len(text),'source_windows':windows,'unsupported_chars':bad,'decision':'SOURCE_UNSUPPORTED' if bad else 'DIFFERENTIAL_CAPACITY_ONLY' if pairs else 'NO_DIFFERENTIAL_WINDOW','offset_pairs':0 if bad else 27*windows,'surviving_pairs':len(pairs),'surviving_windows':len({x[0] for x in pairs}),'pairs':pairs,'survivor_pairs_by_constraint':surviving,'witnesses':witnesses}
            assert result['cases'][2*pi+di]==expected,(p['id'],direction)
            summaries.append({k:expected[k] for k in ['projection_id','direction','decision','surviving_pairs','surviving_windows']})
    receipt={'experiment_id':'GDT1415','status':'PASS_INDEPENDENT_DIRECT_STATE_RECONSTRUCTION','controls':controls(),'lock_sha256':sha(E/'LOCK.json'),'result_sha256':sha(A/'RESULT.json'),'pins':lock['files'],'cases':summaries,'scope':'Frozen source projection provenance inherited. All states directly reconstructed, no interval sums or modular inverses; source-window reversal only, original native order fixed. No native meaning or general source/cipher identification.'}
    destination=A/'VALIDATION.json'
    if destination.exists():assert read(destination)==receipt
    else:destination.write_text(json.dumps(receipt,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':receipt['status'],'cases':len(summaries)}))
if __name__=='__main__':
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True);g.add_argument('--controls',action='store_true');g.add_argument('--validate',action='store_true');a=p.parse_args()
    if a.controls:print(json.dumps(controls()))
    else:validate()

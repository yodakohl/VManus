#!/usr/bin/env python3
"""Finite shared-key panel and dictionary compatibility control. No gold reads."""
import argparse,collections,gzip,hashlib,json,math,subprocess,tempfile
from datetime import datetime,timezone
from pathlib import Path
EXP=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def packed(p,x):p.write_bytes(gzip.compress((json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n').encode(),mtime=0))
def unpack(p):return json.loads(gzip.decompress(p.read_bytes()))
def arr(s):return [] if s=='-' else list(map(int,s.split(',')))
def build(exe):subprocess.run(['g++','-std=c++17','-O3',str(EXP/'src/channel.cpp'),'-o',str(exe)],check=True)
def residuals(carriers,word):
    d=len(word)-len(carriers)
    if not 0<=d<=4:return set()
    states={(0,'')}
    for char in word:
        nxt=set()
        for j,r in states:
            if j<len(carriers) and carriers[j]==char:nxt.add((j+1,r))
            if len(r)<d:nxt.add((j,r+char))
        states=nxt
    return {r for j,r in states if j==len(carriers)}
def compatible(atoms,word,key,alphabet,marker,model,residual,fit_atoms):
    if any(a not in fit_atoms for a in atoms):return False
    k=atoms.count(marker) if marker>=0 and model!='L' else 0
    carriers=''.join(alphabet[key[a]] for a in atoms if not(k and a==marker))
    if not k:return carriers==word
    if len(carriers)<2:return False
    d=len(word)-len(carriers)
    if not 0<=d<=4:return False
    if model=='C':return len(residual)*k==d and residual*k in residuals(carriers,word)
    it=iter(word)
    return all(any(c==a for c in it) for a in carriers)
def check_bindings(bindings):
    for rel,h in bindings.items():assert sha(EXP/rel)==h,rel

def fit(args):
    release=read(EXP/'artifacts/FIT_RELEASE.json');assert release['status']=='FIT_RELEASED';check_bindings(release['bindings'])
    assert release['registered_commit']
    # Only these two real-source payloads are opened before key selection.
    train=read(EXP/'artifacts/TRAIN_INPUT.json');ref=read(EXP/'artifacts/REFERENCE_INPUT.json')
    known_train=[w for w in train['words'] if -1 not in w['atoms']]
    words=sorted(known_train,key=lambda w:(-w['count'],w['atoms']))[:512]
    assert len({tuple(w['atoms']) for w in train['words']})==len(train['words'])
    references=sorted(ref['words'],key=lambda w:w['word']);assert len({w['word'] for w in references})==len(references)
    assert all(w['word'] and not any(c.isspace() for c in w['word']) and w['count']>0 for w in references)
    alphabet=sorted({c for w in references for c in w['word']});ci={c:i for i,c in enumerate(alphabet)}
    atoms=sorted({a for w in words for a in w['atoms']});assert len(atoms)>=2 and 2<=len(alphabet)<=1024
    assert all(0<=a<train['n_atoms'] for a in atoms)
    args.runtime.mkdir(parents=True,exist_ok=True);payload=args.runtime/'input.txt';exe=args.runtime/'channel';prefix=args.runtime/'fit'
    lines=[f"ALPHABETS {train['n_atoms']} {len(alphabet)}",f'TRAIN {len(words)}']
    lines += [f"{w['count']} {len(w['atoms'])} "+' '.join(map(str,w['atoms'])) for w in words]
    lines += [f'REFERENCE {len(references)}']
    lines += [f"{w['count']} {len(w['word'])} "+' '.join(str(ci[c]) for c in w['word']) for w in references]
    payload.write_text('\n'.join(lines)+'\n');build(exe);subprocess.run([str(exe),str(payload),str(prefix)],check=True)
    panel=[]
    for line in prefix.with_suffix('.panel.tsv').read_text().splitlines():
        i,start,step,marker,score,key=line.split('\t');panel.append({'panel':int(i),'start':int(start),'step':int(step),'surrogate_marker':int(marker),'surrogate_score':float(score),'key':arr(key),'anneal_arm':'FORCED_NO_OMISSION' if int(start)<4 else 'LATENT_OMISSION'})
    assert len(panel)==32
    scores=[]
    for line in prefix.with_suffix('.scores.tsv').read_text().splitlines():
        model,p,m,r,s=line.split('\t');scores.append({'model':model,'panel':int(p),'marker':int(m),'residual_ids':arr(r),'score':float(s)})
    selected={};ties={}
    for model in ['L','C','V']:
        rows=[s for s in scores if s['model']==model];maximum=max(s['score'] for s in rows)
        tied=[s for s in rows if s['score']>=maximum-1e-12]
        tied.sort(key=lambda s:(panel[s['panel']]['key'],s['marker'],s['residual_ids'],s['panel']))
        winner=tied[0];selected[model]={**winner,'key':panel[winner['panel']]['key'],'residual':''.join(alphabet[j] for j in winner['residual_ids']),'maximum_score':maximum,'score_tie_count':len(tied)};ties[model]=tied
    packed(EXP/'artifacts/KEY_PANEL.json.gz',{'panel':panel,'alphabet':alphabet,'fit_atoms':atoms})
    packed(EXP/'artifacts/SEARCH_SCORES.json.gz',{'scores':scores,'ties':ties})
    selection={'experiment':'GDT1166','status':'KEYS_SELECTED_BEFORE_HELD_INPUT','selected':selected,'alphabet':alphabet,'fit_atoms':atoms,'fit_types':len(words),'fit_occurrences':sum(w['count'] for w in words),'all_train_types':len(train['words']),'known_train_types':len(known_train),'excluded_unknown_training_types':len(train['words'])-len(known_train),'excluded_unknown_training_occurrences':sum(w['count'] for w in train['words'] if -1 in w['atoms']),'reference_types':len(references),'n_atoms':train['n_atoms'],'panel_states':32,'starts':8,'steps_per_start':20000,'search_rows':len(scores),'registered_commit':release['registered_commit'],'held_input_read':False,'gold_read':False,'score_interpretation':'Unnormalized compatibility/search score, not likelihood or calibrated probability'}
    dump(EXP/'artifacts/KEY_SELECTION.json',selection)
    bind=['SPEC.json','METHOD.md','src/run.py','src/channel.cpp','artifacts/TRAIN_INPUT.json','artifacts/REFERENCE_INPUT.json','artifacts/KEY_PANEL.json.gz','artifacts/SEARCH_SCORES.json.gz','artifacts/KEY_SELECTION.json','artifacts/FIT_RELEASE.json']
    lock={'status':'KEY_SELECTION_LOCKED_BEFORE_HELD_INPUT','locked_utc':datetime.now(timezone.utc).isoformat(),'bindings':{r:sha(EXP/r) for r in bind},'held_input_read':False,'gold_read':False}
    dump(EXP/'artifacts/KEY_SELECTION_LOCK.json',lock);print(json.dumps({'status':lock['status'],'search_rows':len(scores),'selected':{m:{k:v for k,v in z.items() if k not in ['key','residual']} for m,z in selected.items()}}),flush=True)

def predict(args):
    release=read(EXP/'artifacts/PREDICTION_RELEASE.json');assert release['status']=='PREDICTION_RELEASED'
    lock=read(EXP/'artifacts/KEY_SELECTION_LOCK.json');assert lock['status']=='KEY_SELECTION_LOCKED_BEFORE_HELD_INPUT';assert sha(EXP/'artifacts/KEY_SELECTION_LOCK.json')==release['key_lock_sha256'];check_bindings(lock['bindings'])
    selection=read(EXP/'artifacts/KEY_SELECTION.json');held=read(EXP/'artifacts/HOLDOUT_INPUT.json');ref=read(EXP/'artifacts/REFERENCE_INPUT.json');train=read(EXP/'artifacts/TRAIN_INPUT.json')
    train_types={tuple(w['atoms']) for w in train['words']};alphabet=selection['alphabet'];fit_atoms=set(selection['fit_atoms']);total=sum(w['count'] for w in ref['words']);references=sorted(ref['words'],key=lambda r:r['word']);rankings=[]
    for atoms in sorted({tuple(w) for r in held['records'] for w in r['words']}):
        models={}
        for model,s in selection['selected'].items():
            marker=s['marker'];k=atoms.count(marker) if marker>=0 and model!='L' else 0;carrier_length=len(atoms)-k
            candidates=[]
            for ri,r in enumerate(references):
                if compatible(atoms,r['word'],s['key'],alphabet,marker,model,s['residual'],fit_atoms):
                    d=len(r['word'])-carrier_length;weight=r['count']/total*2.0**(-d);candidates.append({'reference_index':ri,'word':r['word'],'weight':weight,'omitted_characters':d})
            candidates.sort(key=lambda r:(-r['weight'],r['word']));cut=candidates[4]['weight'] if len(candidates)>=5 else None
            models[model]={'ranking':candidates,'top5':[r['word'] for r in candidates[:5]],'cutoff_ties':[r['word'] for r in candidates if r['weight']==cut] if cut is not None else []}
        rankings.append({'atoms':list(atoms),'novel_vs_all_training':atoms not in train_types,'contains_unsupported_fit_atom':bool(set(atoms)-fit_atoms),'models':models})
    packed(EXP/'artifacts/PREDICTIONS.json.gz',{'types':rankings,'held_records':held['records'],'reference_words':[r['word'] for r in references],'gold_read':False})
    result={'status':'ALL_HELD_PREDICTIONS_LOCKED_BEFORE_GOLD','locked_utc':datetime.now(timezone.utc).isoformat(),'key_selection_lock_sha256':sha(EXP/'artifacts/KEY_SELECTION_LOCK.json'),'bindings':{r:sha(EXP/r) for r in ['artifacts/HOLDOUT_INPUT.json','artifacts/PREDICTIONS.json.gz','artifacts/PREDICTION_RELEASE.json']},'held_types':len(rankings),'gold_read':False}
    dump(EXP/'artifacts/PREDICTION_LOCK.json',result);print(json.dumps(result),flush=True)

def selftest(args):
    args.runtime.mkdir(parents=True,exist_ok=True);exe=args.runtime/'fixture_channel';build(exe);subprocess.run([str(exe),'--selftest'],check=True)
    assert residuals('ac','zabc')=={'zb'}
    assert compatible((0,2,1),'abc',[0,2,1],list('abc'),2,'V','',{0,1,2})
    assert compatible((0,2,1),'abc',[0,2,1],list('abc'),2,'C','b',{0,1,2})
    assert not compatible((0,2,1),'abc',[0,2,1],list('abc'),2,'C','a',{0,1,2})
    assert compatible((0,2,2,1),'abbc',[0,2,1],list('abc'),2,'C','b',{0,1,2})
    assert not compatible((0,2,2,1),'abc',[0,2,1],list('abc'),2,'C','b',{0,1,2})
    assert not compatible((0,2,1),'abc',[0,2,1],list('abc'),2,'V','',{0,1})
    assert not compatible((0,2),'ab',[0,2,1],list('abc'),2,'V','',{0,1,2})
    assert not compatible((0,1),'abc',[0,2,1],list('abc'),-1,'L','',{0,1,2})
    # Complete synthetic search: compare every emitted C++ panel objective with
    # the separate Python compatibility implementation (including repeated marks).
    tw=[([0,1],30),([0,2,1],12),([0,2,2,1],6),([1,0],9),([0,3,1],7)]
    rw=[('ac',30),('abc',15),('abbc',8),('ca',9),('adbc',5),('bac',4),('ab',7)]
    alph=list('abcd'); payload=args.runtime/'synthetic.txt';prefix=args.runtime/'synthetic'
    lines=['ALPHABETS 4 4',f'TRAIN {len(tw)}']+[f'{n} {len(w)} '+' '.join(map(str,w)) for w,n in tw]
    lines += [f'REFERENCE {len(rw)}']+[f'{n} {len(w)} '+' '.join(str(alph.index(c)) for c in w) for w,n in rw]
    payload.write_text('\n'.join(lines)+'\n');subprocess.run([str(exe),str(payload),str(prefix)],check=True)
    keys=[arr(z.split('\t')[5]) for z in prefix.with_suffix('.panel.tsv').read_text().splitlines()]
    checked=0;maxerr=0.;total=sum(n for w,n in rw)
    for line in prefix.with_suffix('.scores.tsv').read_text().splitlines():
        model,pi,m,res,value=line.split('\t');key=keys[int(pi)];marker=int(m);res=''.join(alph[j] for j in arr(res));score=0.
        for atoms,n in tw:
            k=atoms.count(marker) if marker>=0 and model!='L' else 0
            mass=sum(c/total*2.**(-(len(w)-(len(atoms)-k))) for w,c in rw if compatible(atoms,w,key,alph,marker,model,res,{0,1,2,3}))
            score+=n*math.log(1e-8+(1-1e-8)*mass)
        error=abs(score-float(value));maxerr=max(maxerr,error);assert error<1e-9,(line,score);checked+=1
    assert len(keys)==32
    print(json.dumps({'status':'SYNTHETIC_FULL_SEARCH_PASS','panel_states':len(keys),'objectives_checked':checked,'maximum_objective_error':maxerr}))

def main():
    p=argparse.ArgumentParser();p.add_argument('--stage',choices=['fit','predict','selftest'],required=True);p.add_argument('--runtime',type=Path,required=True);a=p.parse_args();{'fit':fit,'predict':predict,'selftest':selftest}[a.stage](a)
if __name__=='__main__':main()

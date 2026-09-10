#!/usr/bin/env python3
"""Exhaust unchanged GDT905 observed-key space with durable case receipts."""
import argparse, collections, csv, gzip, hashlib, io, json, multiprocessing, pickle, sys, time
from pathlib import Path
E=Path(__file__).resolve().parents[1]; ROOT=E.parents[2]
OLD=ROOT/'experiments/yolo/gdt905_joint_cv_complete_passage_candidates'
PRE=ROOT/'experiments/yolo/gdt892_joint_abugida_paradigm_reconstruction'
sys.path.insert(0,str(PRE/'src'))
import core, csp, grammar
ALPHABET='acdefghiklmnopqrstxy'
REF=None; INDEXES=None; WORK=None; PLAN=None; TABLE_CACHE={}
def enc(x): return (json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False)+'\n').encode()
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
def write(p,x):
    data=enc(x)
    if p.suffix=='.gz': data=gzip.compress(data,mtime=0)
    q=p.with_suffix(p.suffix+'.tmp');q.write_bytes(data);q.replace(p)
def cid(p,g,v): return p['edition']+'_'+p['paragraph_id']+'_'+str(g['mask'])+'_'+v
def check_bindings():
    for p,h in read(E/'artifacts/BINDINGS.json')['files'].items(): assert sha(ROOT/p)==h,p
def tasks(plan):
    for pi,p in enumerate(plan['paragraphs']):
        for gi,g in enumerate(p['groups']):
            for vi,v in enumerate(core.VOWELS):
                if g['inherent_bits']&(1<<vi): yield pi,gi,v
def prepare(work):
    check_bindings()
    target=read(OLD/'artifacts/TARGET.json');scans=read(OLD/'artifacts/SCANS.json')
    sx={(x['edition'],x['paragraph_id']):x for x in scans};paragraphs=[]
    for ed,rs in sorted(target['panels'].items()):
        for r in sorted(rs,key=lambda x:x['paragraph_id']):
            if not 12<=len(r['words'])<=24: continue
            scan=sx[ed,r['paragraph_id']];assert scan['status']=='COMPLETE'
            path=OLD/scan['masks_path'];assert sha(path)==scan['masks_sha256']
            data=gzip.decompress(path.read_bytes());assert hashlib.sha256(data).hexdigest()==scan['uncompressed_sha256']
            words=sorted(set(r['words']));groups={};n=0
            for row in csv.DictReader(io.StringIO(data.decode())):
                mask=int(row['mask']);bits=int(row['inherent_bits'])
                singles={c for i,c in enumerate(ALPHABET) if mask&(1<<i)}
                seg=tuple(core.segment(w,singles) for w in words);assert all(seg)
                groups.setdefault((seg,bits),[]).append(mask);n+=1
            assert n==scan['surviving_masks']
            gs=[dict(group_id=i,mask=ms[0],equivalent_masks=ms,segments=seg,inherent_bits=bits) for i,((seg,bits),ms) in enumerate(groups.items())]
            paragraphs.append(dict(edition=ed,paragraph_id=r['paragraph_id'],raw_words=r['words'],words=words,page=r['page'],loci=r['loci'],groups=gs))
    plan=dict(schema_version=1,paragraphs=paragraphs)
    write(E/'artifacts/PLAN.json.gz',plan)
    old=read(OLD/'artifacts/CANDIDATES.json.gz');ox={}
    for p in old:
        for c in p['cases']:
            if c['status']=='COMPLETE': ox[p['edition']+'_'+p['paragraph_id']+'_'+str(c['mask'])+'_'+c['inherent']]=c
    explanation=read(OLD/'artifacts/LEXICAL_KEY_EXPLANATION.json');keys={}
    for p in explanation['records']:
        for k in p['keys']:
            key=p['edition']+'_'+p['paragraph_id']+'_'+str(k['mask'])+'_'+k['inherent'];keys.setdefault(key,[]).append(k)
    dest=work/'cases';dest.mkdir(parents=True,exist_ok=True);reused=0;count=0
    for pi,gi,v in tasks(plan):
        count+=1;p=paragraphs[pi];g=p['groups'][gi];key=cid(p,g,v)
        if key not in ox: continue
        oldcase=ox.pop(key);assert oldcase['equivalent_masks']==g['equivalent_masks']
        codes=sorted({c for seg in g['segments'] for c in seg});parts=core.inventory(v)
        vs=[[parts.index(k['observed_key'][c]) for c in codes] for k in keys.get(key,[])]
        assert len(vs)==oldcase['stats']['complete_assignments']
        flags=[bool(k['grammar_accepted']) for k in keys.get(key,[])]
        assert sum(flags)==oldcase['stats']['solutions_accepted']
        receipt=dict(case_id=key,edition=p['edition'],paragraph_id=p['paragraph_id'],mask=g['mask'],inherent=v,status='COMPLETE',origin='GDT905_REUSED',values=vs,grammar_accepted=flags,stats=oldcase['stats'])
        out=dest/(key+'.json')
        if out.exists(): assert read(out)==receipt
        else: write(out,receipt)
        reused+=1
    assert not ox
    summary=dict(paragraphs=len(paragraphs),mask_rows=sum(len(g['equivalent_masks']) for p in paragraphs for g in p['groups']),segmentation_groups=sum(len(p['groups']) for p in paragraphs),cases=count,reused_complete_cases=reused,remaining_cases=count-reused,plan_sha256=sha(E/'artifacts/PLAN.json.gz'))
    write(E/'artifacts/SCOPE.json',summary);print(enc(summary).decode(),flush=True)
def load_reference(cache):
    global REF,INDEXES
    meta=read(PRE/'artifacts/REFERENCE.json');names=['reference.pkl']+['patterns_'+v+'.pkl' for v in core.VOWELS]
    for n in names: assert sha(cache/n)==meta['cache_files'][n]['sha256'],n
    with (cache/'reference.pkl').open('rb') as f: REF=pickle.load(f)
    INDEXES={}
    for v in core.VOWELS:
        with (cache/('patterns_'+v+'.pkl')).open('rb') as f: INDEXES[v]=pickle.load(f)
    assert len(REF['forms'])==425561

def solve(task):
    pi,gi,v=task;p=PLAN['paragraphs'][pi];g=p['groups'][gi];key=cid(p,g,v)
    out=WORK/'cases'/(key+'.json')
    if out.exists():
        r=read(out);assert r['case_id']==key and r['status']=='COMPLETE';return key,len(r['values']),sum(r['grammar_accepted']),'REUSED_CHECKPOINT'
    codewords=sorted({c for seg in g['segments'] for c in seg});ids={c:i for i,c in enumerate(codewords)}
    parts=core.inventory(v);part_ids={x:i for i,x in enumerate(parts)};tables=[]
    for seg in g['segments']:
        unique=list(dict.fromkeys(seg));first=[seg.index(c) for c in unique];pat=core.pattern(seg);ck=(v,pat)
        if ck not in TABLE_CACHE:
            TABLE_CACHE[ck]=sorted({tuple(part_ids[cs[i]] for i in first) for _,cs in INDEXES[v][pat]})
        tables.append(dict(vars=[ids[c] for c in unique],rows=TABLE_CACHE[ck]))
    values=[];flags=[]
    def accept(mapping):
        decoded={}
        for w,seg in zip(p['words'],g['segments']):
            plain=core.decode_components(tuple(parts[mapping[ids[c]]] for c in seg),v)
            assert plain in REF['analyses'];decoded[w]=plain
        text=[decoded[w] for w in p['raw_words']]
        ok=grammar.accepts(REF['grammar'],[REF['analyses'][w] for w in text])
        values.append(list(mapping));flags.append(bool(ok));return bool(ok)
    result=csp.solve_tables(tables,len(codewords),27,float('inf'),accept=accept)
    assert result['status']=='COMPLETE' and result['stats']['complete_assignments']==len(values)
    assert len(result['solutions'])==sum(flags)
    receipt=dict(case_id=key,edition=p['edition'],paragraph_id=p['paragraph_id'],mask=g['mask'],inherent=v,status='COMPLETE',origin='GDT906_ENUMERATED',values=values,grammar_accepted=flags,stats=result['stats'])
    write(out,receipt);return key,len(values),sum(flags),'NEW'
def fit(cache,work,workers):
    global WORK,PLAN
    check_bindings();load_reference(cache);WORK=work;PLAN=read(E/'artifacts/PLAN.json.gz')
    assert sha(E/'artifacts/PLAN.json.gz')==read(E/'artifacts/SCOPE.json')['plan_sha256']
    todo=[];done=lexical=accepted=0
    for t in tasks(PLAN):
        p=PLAN['paragraphs'][t[0]];g=p['groups'][t[1]];path=work/'cases'/(cid(p,g,t[2])+'.json')
        if path.exists():
            r=read(path);assert r['status']=='COMPLETE' and r['case_id']==cid(p,g,t[2]);done+=1;lexical+=len(r['values']);accepted+=sum(r['grammar_accepted'])
        else: todo.append(t)
    total=done+len(todo);began=time.monotonic();last=0
    print(enc(dict(event='START',completed=done,total=total,lexical=lexical,grammar_accepted=accepted)).decode(),flush=True)
    with multiprocessing.get_context('fork').Pool(workers) as pool:
        for key,n,a,origin in pool.imap_unordered(solve,todo,chunksize=1):
            done+=1;lexical+=n;accepted+=a
            now=time.monotonic()
            if n or now-last>=30 or done==total:
                progress=dict(event='PROGRESS',case_id=key,completed=done,total=total,remaining=total-done,lexical=lexical,grammar_accepted=accepted,elapsed_seconds=round(now-began,3))
                write(E/'artifacts/PROGRESS.json',progress);print(enc(progress).decode(),flush=True);last=now
    print('All registered cases have durable COMPLETE receipts.',flush=True)
def collect(work):
    check_bindings();plan=read(E/'artifacts/PLAN.json.gz');rows=[]
    for pi,gi,v in tasks(plan):
        p=plan['paragraphs'][pi];g=p['groups'][gi];key=cid(p,g,v);r=read(work/'cases'/(key+'.json'))
        assert r['case_id']==key and r['status']=='COMPLETE';rows.append(r)
    write(E/'artifacts/CASES.json.gz',rows)
    summary=dict(experiment_id='GDT906',status='PRIMARY_ENUMERATION_COMPLETE_VALIDATION_PENDING',cases=len(rows),paragraphs=len(plan['paragraphs']),origins=dict(collections.Counter(r['origin'] for r in rows)),lexical_keys=sum(len(r['values']) for r in rows),grammar_accepted=sum(sum(r['grammar_accepted']) for r in rows),confirmed_meanings=0,cases_sha256=sha(E/'artifacts/CASES.json.gz'))
    write(E/'artifacts/RESULT.json',summary);print(enc(summary).decode(),flush=True)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--stage',choices=['prepare','fit','collect'],required=True);ap.add_argument('--work-dir',type=Path,required=True);ap.add_argument('--cache-dir',type=Path);ap.add_argument('--workers',type=int,default=28);a=ap.parse_args();assert 1<=a.workers<=28
    a.work_dir.mkdir(parents=True,exist_ok=True)
    if a.stage=='prepare': prepare(a.work_dir)
    elif a.stage=='fit': fit(a.cache_dir,a.work_dir,a.workers)
    else: collect(a.work_dir)
if __name__=='__main__':main()

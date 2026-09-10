#!/usr/bin/env python3
"""Exact local necessary domains for the complete registered source model."""
import argparse, collections, csv, functools, hashlib, importlib.util, io, json, multiprocessing, re, subprocess
from pathlib import Path
E=Path(__file__).resolve().parents[1]; ROOT=E.parents[2]
FIT='experiments/yolo/gdt888_alphita_joint_name_incidence/artifacts/FIT_INPUT.json'
OLD='experiments/yolo/gdt887_tacuinum_joint_entry_reconstruction/src/run.py'
LIMIT=200000

def enc(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,x): (E/'artifacts'/n).write_text(enc(x))
def intake():
    spec=importlib.util.spec_from_file_location('registered_intake887',ROOT/OLD); old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
    fit=json.loads((ROOT/FIT).read_text()); panels={ed:p['train'] for ed,p in fit['panels'].items()}
    pages=sorted({r['page'] for rows in panels.values() for r in rows})
    assert all(not p.startswith('f84') and int(re.match(r'f(\d+)',p).group(1))%2 for p in pages)
    frames,g1=old.query(old.ATLAS,'page',pages,old.FRAMECOLS)
    frames={r['paragraph_id']:r for r in frames}
    raw,g2=old.query(old.RAW,'page',pages,old.RAWCOLS)
    lines=collections.defaultdict(list)
    for r in raw:
        if r['edition'] in old.EDITIONS: lines[r['edition'],r['locus']].append(r)
    for rows in lines.values():rows.sort(key=lambda r:int(r['source_group_index']))
    loci=sorted({loc for ed,loc in lines})
    sta,g3=old.query(old.STA,'locus',loci,old.STACOLS)
    sx={r['source_group_id']:r for r in sta}; out={}
    for ed,records in panels.items():
        out[ed]=[]; real_ed='ZL3b' if ed=='CONSENSUS' else ed
        for rec in records:
            f=frames[rec['paragraph_id']]; assert f['page']==rec['page']
            lo,hi=int(f['start_line_number']),int(f['end_line_number'])
            locs=sorted([loc for e,loc in lines if e==real_ed and loc.split('.')[0]==f['page'] and lo<=old.number(loc)<=hi],key=old.number)
            assert len(locs)==int(f['source_line_count']) and locs[0]==f['start_locus'] and locs[-1]==f['end_locus']
            rows=[r for loc in locs for r in lines[real_ed,loc]]
            assert [sx[r['source_group_id']]['primary_sta_codes'].split() for r in rows]==[rec['head']]+rec['body']
            assert all(re.fullmatch('[a-z]+',r['ivtff_group_raw']) and r['kind']=='P' for r in rows)
            if ed=='CONSENSUS':
                for alt in ['IT2a','RF1b']:
                    rs=[r for loc in locs for r in lines[alt,loc]]
                    assert [(r['locus'],r['ivtff_group_raw']) for r in rs]==[(r['locus'],r['ivtff_group_raw']) for r in rows]
            out[ed].append(dict(paragraph_id=rec['paragraph_id'],page=rec['page'],physical_folio=rec['physical_folio'],
                               words=[r['ivtff_group_raw'] for r in rows],source_group_ids=[r['source_group_id'] for r in rows],loci=[r['locus'] for r in rows]))
    return dict(source=FIT,source_sha256=sha(ROOT/FIT),guards=[g1,g2,g3],panels=out)

class Budget(Exception):pass

def local(source,target,limit=LIMIT):
    if len(source)>len(target):return dict(status='UNSAT_LENGTH',states=0)
    counts=collections.Counter(source); positions=collections.defaultdict(list)
    for i,w in enumerate(target):positions[w].append(i)
    need=collections.Counter(counts.values()); have=collections.Counter(map(len,positions.values()))
    if any(have[k]<v for k,v in need.items()):return dict(status='UNSAT_MULTIPLICITY',states=0)
    order={a:i for i,a in enumerate(dict.fromkeys(source))}; atoms=list(order)
    pattern=[order[a] for a in source]; cnt=[counts[a] for a in atoms]
    words=list(positions); pos=[positions[w] for w in words]
    domains={k:[j for j,p in enumerate(pos) if len(p)==k] for k in set(cnt)}
    seen=collections.Counter(); nth=[]
    for a in pattern: nth.append(seen[a]); seen[a]+=1
    states=0
    @functools.lru_cache(None)
    def dfs(i,previous,active):
        nonlocal states
        states+=1
        if states>limit:raise Budget()
        if i==len(pattern):return ()
        if len(pattern)-i>len(target)-previous-1:return None
        a=pattern[i]; n=nth[i]; mapping=dict(active)
        choices=[mapping[a]] if n else domains[cnt[a]]
        for j in choices:
            p=pos[j][n]
            if p<=previous:continue
            nxt=dict(mapping)
            if cnt[a]>1 and n==0:nxt[a]=j
            if n==cnt[a]-1:nxt.pop(a,None)
            ans=dfs(i+1,p,tuple(sorted(nxt.items())))
            if ans is not None:return ((j,p),)+ans
        return None
    try: answer=dfs(0,-1,())
    except Budget:return dict(status='UNKNOWN_STATE_BUDGET',states=states)
    if answer is None:return dict(status='UNSAT_ORDER',states=states)
    mapping={}; inverse={}
    for a,(j,p) in zip(source,answer):
        w=words[j];assert a not in mapping or mapping[a]==w
        assert w not in inverse or inverse[w]==a
        mapping[a]=w;inverse[w]=a
    assert [inverse[w] for w in target if w in inverse]==source
    return dict(status='SAT_RELAXED_LOCAL',states=states,mapping=mapping,positions=[p for j,p in answer])

def job(x):
    ed,sid,pid,source,target=x
    return dict(edition=ed,source_id=sid,paragraph_id=pid,**local(source,target))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--workers',type=int,default=32);ap.add_argument('--selftest',action='store_true');args=ap.parse_args()
    if args.selftest:
        assert local(['a','b','a'],['x','z','y','x'])['status']=='SAT_RELAXED_LOCAL'
        assert local(['a','b','a'],['x','y','y'])['status'].startswith('UNSAT')
        assert local(['a','b'],['x','x'])['status'].startswith('UNSAT')
        assert local(['a','a'],['x','x','x'])['status'].startswith('UNSAT')
        print('four nontrivial projection fixtures PASS');return
    for p,h in json.loads((E/'src/PREREG_LOCK.json').read_text()).items(): assert sha(ROOT/p)==h,p
    assert json.loads((E/'artifacts/SOURCE_VALIDATION.json').read_text())['status']=='PASS'
    inp=intake();write('TARGET.json',inp)
    source=json.loads((E/'artifacts/SOURCE.json').read_text())['records']
    jobs=[(ed,s['id'],t['paragraph_id'],s['lexical'],t['words']) for ed,rows in inp['panels'].items() for s in source for t in rows]
    with multiprocessing.Pool(min(32,args.workers)) as pool: results=list(pool.imap(job,jobs,chunksize=8))
    results.sort(key=lambda r:(r['edition'],r['source_id'],r['paragraph_id']));write('LOCAL_DOMAINS.json',results)
    panels={}
    for ed,rows in inp['panels'].items():
        domains={s['id']:[r for r in results if r['edition']==ed and r['source_id']==s['id']] for s in source}
        zero=[sid for sid,rs in domains.items() if rs and all(r['status'].startswith('UNSAT') for r in rs)]
        unknown=[sid for sid,rs in domains.items() if any(r['status'].startswith('UNKNOWN') for r in rs)]
        counts={sid:dict(collections.Counter(r['status'] for r in rs)) for sid,rs in domains.items()}
        panels[ed]=dict(target_records=len(rows),target_leaves=len({r['physical_folio'] for r in rows}),mandatory_record_count_possible=len(rows)>=38,
                        zero_domain_sources=zero,sources_with_unknown=unknown,local_counts=counts,
                        status='FULL_MODEL_EXCLUDED_BY_LEXICAL_NECESSITY' if zero else 'MANDATORY_RECORD_COUNT_IMPOSSIBLE' if len(rows)<38 else 'GLOBAL_NOT_DECIDED')
    result=dict(experiment_id='GDT904',panels=panels,source_records=38,claim_ceiling='Exact conditional whole-group source-model test; no meaning, no held data, no general recipe-language exclusion.')
    write('RESULT.json',result);print(enc(result))
if __name__=='__main__':main()

#!/usr/bin/env python3
"""Reused exact finite string-code search; fixed full source and target scope."""
import collections, concurrent.futures, csv, gzip, hashlib, importlib.util, json, sys, time
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
P900=ROOT/'experiments/yolo/gdt900_cumanicus_complete_trilingual_tables/src'
sys.path.insert(0,str(P900));sys.setrecursionlimit(10000)
sp=importlib.util.spec_from_file_location('gdt900_reused',P900/'run.py');OLD=importlib.util.module_from_spec(sp);sp.loader.exec_module(OLD)
TP=ROOT/'experiments/yolo/gdt963_dioscorides_complete_content_code/artifacts/TARGET_FRAMES.json.gz'
EDS=('ZL3b','IT2a','RF1b')

def save(name,data):
    (E/'artifacts'/name).write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n')

def valid(seq,text,key):
    vals=sorted(key.values())
    return all(vals) and all(not b.startswith(a) for a,b in zip(vals,vals[1:])) and ''.join(key[u] for u in seq)==text

def necessary(seq,text):
    cs=collections.Counter(seq);ct=collections.Counter(text);n=len(seq);m=len(text)
    same=seq[0]==seq[-1];upper=(m-(n-cs[seq[0]]))//cs[seq[0]]
    borders=[k for k in range(1,max(0,upper)+1) if text.endswith(text[:k])] if same else []
    obs={'required_characters':n,'observed_characters':m,
         'first_source_unit':seq[0],'required_first_character_count':cs[seq[0]],'target_first_character':text[0],'observed_first_character_count':ct[text[0]],
         'last_source_unit':seq[-1],'required_last_character_count':cs[seq[-1]],'target_last_character':text[-1],'observed_last_character_count':ct[text[-1]],
         'same_boundary_unit':same,'boundary_code_max_length':upper if same else None,'allowed_equal_boundary_lengths':borders if same else None}
    failures=[]
    if m<n:failures.append('NONEMPTY_LENGTH')
    if ct[text[0]]<cs[seq[0]]:failures.append('FIRST_UNIT_RECURRENCE')
    if ct[text[-1]]<cs[seq[-1]]:failures.append('LAST_UNIT_RECURRENCE')
    if same and not borders:failures.append('SAME_BOUNDARY_UNIT')
    return obs,failures

def local(job):
    seq,text=job;started=time.monotonic()
    try:
        key=next(OLD.extend_word(seq,text,{},started+2),None)
        if key is None:return {'status':'UNSAT_EXACT','elapsed_seconds':time.monotonic()-started}
        assert valid(seq,text,key)
        return {'status':'SAT_WITNESS','code':key,'elapsed_seconds':time.monotonic()-started}
    except OLD.Budget:return {'status':'UNKNOWN_COMPUTATION','elapsed_seconds':time.monotonic()-started}

def joint(records,domains,seconds=120):
    start=time.monotonic();deadline=start+seconds;order=sorted(records,key=lambda r:(len(domains[r['id']]),r['id']));witnesses=[]
    def rec(i,key,chosen,leaves):
        if time.monotonic()>deadline:raise OLD.Budget
        if i==len(order):
            yield {'code':key,'assignments':dict(chosen)};return
        r=order[i]
        for t in sorted(domains[r['id']],key=lambda t:t['id']):
            if t['physical_leaf'] in leaves:continue
            for extended in OLD.extend_word(r['units'],t['text'],key,deadline):
                assert valid(r['units'],t['text'],extended)
                yield from rec(i+1,extended,chosen+[(r['id'],t['id'])],leaves|{t['physical_leaf']})
    exhaustive=False
    try:
        for w in rec(0,{},[],set()):
            witnesses.append(w)
            if len(witnesses)==2:break
        else:exhaustive=True
    except OLD.Budget:pass
    status='SAT_AT_LEAST_TWO' if len(witnesses)==2 else 'SAT_ONE_EXHAUSTIVE' if len(witnesses)==1 and exhaustive else 'SAT_ONE_UNRESOLVED' if witnesses else 'UNSAT_LITERAL_JOINT' if exhaustive else 'UNKNOWN_JOINT'
    return {'status':status,'complete_enumeration':exhaustive,'witnesses':witnesses,'elapsed_seconds':time.monotonic()-start,'source_search_order':[r['id'] for r in order]}

def main():
    for p,h in json.loads((E/'PREREG_LOCK.json').read_text())['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    source=json.loads((E/'src/SOURCE.json').read_text());records=source['records']
    for r in records:r['units']=[u for w in r['grapheme_words'] for u in w]
    frames=json.loads(gzip.decompress(TP.read_bytes()));assert len(frames)==357
    cases=[];todo=[]
    for t in frames:
        assert t['page'] not in ('f1r','f116v') and not t['page'].startswith('f84')
        for r in records:
            case={'id':t['id']+':'+r['id'],'frame_id':t['id'],'edition':t['edition'],'page':t['page'],'physical_leaf':t['physical_leaf'],'source_id':r['id'],'source_group_count':r['word_count'],'target_group_count':t['group_count'],'independent_confirmation_capacity':0}
            if not t['eligible']:case.update(status='UNKNOWN_SOURCE',source_reasons=t['reasons'])
            else:
                obs,bad=necessary(r['units'],t['text']);case.update(observations=obs,contradictions=bad)
                if bad:case['status']='CONTRADICTED_NECESSARY'
                else:case['status']='PENDING';todo.append((len(cases),(r['units'],t['text'])))
            cases.append(case)
    save('NECESSARY_CASES.json',cases)
    print('necessary',dict(collections.Counter(c['status'] for c in cases)),flush=True)
    with concurrent.futures.ProcessPoolExecutor(max_workers=8) as pool:
        for (i,job),answer in zip(todo,pool.map(local,[job for i,job in todo])):cases[i].update(answer)
    save('ALL_CASES.json',cases);by_id={t['id']:t for t in frames};joints={}
    for ed in EDS:
        cf=[t for t in frames if t['edition']==ed];unknown=[t['id'] for t in cf if not t['eligible']]
        domains={r['id']:[by_id[c['frame_id']] for c in cases if c['edition']==ed and c['source_id']==r['id'] and c['status'] in ('SAT_WITNESS','UNKNOWN_COMPUTATION')] for r in records}
        if any(not v for v in domains.values()):j={'status':'UNSAT_LITERAL_DOMAIN','witnesses':[],'complete_enumeration':True,'empty_roles':[k for k,v in domains.items() if not v]}
        elif len({t['physical_leaf'] for v in domains.values() for t in v})<3:j={'status':'NO_LITERAL_CAPACITY','witnesses':[],'complete_enumeration':True}
        else:j=joint(records,domains)
        j.update(source_unknown_frames=unknown,whole_scope_exclusion=not unknown and j['status'].startswith('UNSAT'))
        for w in j['witnesses']:
            for r in records:assert valid(r['units'],by_id[w['assignments'][r['id']]]['text'],w['code'])
            assert len({by_id[i]['physical_leaf'] for i in w['assignments'].values()})==3
        joints[ed]=j;print(ed,j['status'],flush=True)
    # Equivalent necessary-prediction signatures retain all candidate identities.
    groups=collections.defaultdict(list)
    for c in cases:
        sig=json.dumps({'source_id':c['source_id'],'observations':c.get('observations'),'status':c['status'],'contradictions':c.get('contradictions')},ensure_ascii=False,sort_keys=True)
        groups[sig].append(c['id'])
    save('EQUIVALENT_OBSERVATIONS.json',[{'signature':json.loads(k),'cases':v} for k,v in groups.items()])
    fields=['id','source_id','edition','page','physical_leaf','status','required_characters','observed_characters','required_first_character_count','observed_first_character_count','required_last_character_count','observed_last_character_count','same_boundary_unit','allowed_equal_boundary_lengths','contradictions','independent_confirmation_capacity']
    with (E/'artifacts/CANDIDATE_TABLE.tsv').open('w') as f:
        out=csv.DictWriter(f,fieldnames=fields,delimiter='\t');out.writeheader()
        for c in cases:
            row=dict(c,**c.get('observations',{}));out.writerow({k:json.dumps(row[k],ensure_ascii=False) if isinstance(row.get(k),(list,dict)) else row.get(k,'') for k in fields})
    result={'status':'FIXED_PANEL_EVALUATED','case_count':len(cases),'counts':dict(collections.Counter(c['status'] for c in cases)),'exact_local_search_count':len(todo),'joint':joints,'observation_groups':len(groups),'confirmed_words':0,'independent_confirmation_capacity':0,'claim_ceiling':'Exact printed-source/common-code model only; no language or plant-name identification; no significance. Source unknowns remain.'}
    save('RESULT.json',result);print(json.dumps(result,ensure_ascii=False),flush=True)
if __name__=='__main__':main()

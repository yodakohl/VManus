#!/usr/bin/env python3
"""All whole exposed paragraph cases under the fixed complete typed source tree."""
import argparse,collections,concurrent.futures,csv,datetime,hashlib,json,re,subprocess,sys,time
from pathlib import Path
from finite import solve
E=Path(__file__).resolve().parents[1];R=E.parents[2];A=E/'artifacts'
def read(p):return json.loads(p.read_text())
def put(n,x):(A/n).write_text(json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n')
def serial(tree,order):
    if isinstance(tree,str):return [tree]
    children=[a for child in tree[1:] for a in serial(child,order)]
    return [tree[0]]+children if order=='PREFIX' else children+[tree[0]]
def check_tree(tree,source):
    if isinstance(tree,str):assert tree in source['types'];return
    assert isinstance(tree,list) and tree and source['types'][tree[0]]=='OP'
    assert len(tree)-1==source['arities'][tree[0]],tree[0]
    for child in tree[1:]:check_tree(child,source)
def lockcheck():
    for p,h in read(E/'PREREG_LOCK.json')['files'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p

def isolated(job):
    try:
        r=subprocess.run([sys.executable,str(Path(__file__).resolve()),'--solve-json'],input=json.dumps(job),text=True,capture_output=True,timeout=20)
        return json.loads(r.stdout) if r.returncode==0 else dict(status='ERROR_WORKER',exit_code=r.returncode)
    except subprocess.TimeoutExpired:return dict(status='UNKNOWN_WALL_LIMIT')

def full_fixture():
    from reverse import ground,replay
    source=read(E/'src/SOURCE.json');check_tree(source['tree'],source);code={}
    for typ in sorted(set(source['types'].values())):
        for i,a in enumerate(sorted(a for a,t in source['types'].items() if t==typ)):code[a]=chr(97+i//26)+chr(97+i%26)
    rows=[]
    for writer in ('PREFIX','POSTFIX'):
        atoms=serial(source['tree'],writer);assert set(atoms)==set(source['types'])
        words=[''.join(code[a] for a in atoms[i:i+2]) for i in range(0,len(atoms),2)]
        a=solve(atoms,words,source['types'],pinned=code,seconds=5);b=replay(atoms,words,source['types'],pinned=code,seconds=5)
        assert a['status']=='SAT' and a['exhaustive'] and a['codes']==[code]
        assert b['status']=='SAT_REPLAY' and b['exhaustive'] and b['codes']==[code]
        ground(atoms,words,source['types'],code)
        broken=[words[0][:1],words[0][1:],*words[1:]]
        assert solve(atoms,broken,source['types'],pinned=code)['status']=='UNSAT_FINITE'
        assert replay(atoms,broken,source['types'],pinned=code)['status']=='UNSAT_REPLAY'
        rows.append(dict(writer=writer,source_atoms=len(atoms),types=len(set(atoms)),pinned_full_code='PASS',broken_seam='REJECTED'))
    out=dict(status='PASS',cases=rows,scope='Full source tree serialization and typed code interface; no target data or source identification')
    put('FULL_SOURCE_PREFLIGHT.json',out);print(json.dumps(out,indent=2))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--solve-json',action='store_true');ap.add_argument('--full-fixture',action='store_true');args=ap.parse_args()
    if args.solve_json:
        j=json.load(sys.stdin);print(json.dumps(solve(j['atoms'],j['words'],j['types'],seconds=j['seconds'],max_nodes=j['max_nodes'],max_solutions=2)));return
    if args.full_fixture:full_fixture();return
    lockcheck();spec=read(E/'src/SPEC.json');source=read(E/'src/SOURCE.json');check_tree(source['tree'],source)
    streams={w:serial(source['tree'],w) for w in spec['writers']}
    for stream in streams.values():assert set(stream)==set(source['types'])
    started=datetime.datetime.now(datetime.timezone.utc).isoformat();t=time.monotonic();target=read(R/spec['input']);cases=[];jobs=[]
    for ed,ps in target.items():
        for p in ps:
            assert not p['page'].startswith('f84') and p['page']!='f116v'
            words=[w for line in p['lines'] for w in line['words']]
            literal=all(l['anchor_eligible'] for l in p['lines']) and all(re.fullmatch('[a-z]+',w) for w in words)
            for writer,atoms in streams.items():
                row=dict(index=len(cases),edition=ed,paragraph=p['id'],page=p['page'],leaf=p['leaf'],writer=writer,words=words,source_ids=[x for l in p['lines'] for x in l['source_ids']],groups=len(words),characters=sum(map(len,words)),source_atoms=len(atoms),source_types=len(set(atoms)),independent_meaning_capacity=0)
                if not literal:row.update(status='UNKNOWN_SOURCE',ineligible_lines=[l['locus'] for l in p['lines'] if not l['anchor_eligible']])
                else:jobs.append((len(cases),dict(atoms=atoms,words=words,types=source['types'],seconds=spec['solver_seconds'],max_nodes=spec['max_nodes'])))
                cases.append(row)
    print(json.dumps(dict(whole_cases=len(cases),literal_jobs=len(jobs),source_atoms={w:len(a) for w,a in streams.items()},source_types=len(source['types']))),flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=spec['workers']) as pool:
        fs={pool.submit(isolated,j):i for i,j in jobs}
        for n,f in enumerate(concurrent.futures.as_completed(fs),1):
            i=fs[f];cases[i].update(f.result())
            if n%32==0 or n==len(fs):print(json.dumps(dict(done=n,total=len(fs),last=cases[i]['status'])),flush=True)
    put('CASES.json',cases)
    panels={}
    for ed in target:
        panels[ed]={w:dict(collections.Counter(c['status'] for c in cases if c['edition']==ed and c['writer']==w)) for w in streams}
    counts=collections.Counter(c['status'] for c in cases);unknown=sum(v for k,v in counts.items() if k.startswith(('UNKNOWN','ERROR')))
    result=dict(status='COMPLETE_CONDITIONAL_CODES' if counts['SAT'] else 'NO_LITERAL_CODE_SOURCE_OR_COMPUTATION_UNRESOLVED' if unknown else 'ALL_COMPLETE_CODES_CONTRADICTED',paragraphs={ed:len(ps) for ed,ps in target.items()},cases=len(cases),literal_jobs=len(jobs),source_atoms={w:len(a) for w,a in streams.items()},source_types=len(source['types']),case_status_counts=dict(counts),panels=panels,witness_cases=counts['SAT'],saved_codes=sum(len(c.get('codes',[])) for c in cases),unknown_source=counts['UNKNOWN_SOURCE'],computational_unknown_or_errors=sum(v for k,v in counts.items() if k!='UNKNOWN_SOURCE' and k.startswith(('UNKNOWN','ERROR'))),confirmed_words=0,independent_meaning_capacity=0,reserve_accesses=0,significance_claim=False)
    put('RESULT.json',result);put('EXECUTION_RECEIPT.json',dict(started_utc=started,finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),wall_seconds=time.monotonic()-t,workers=spec['workers']))
    with (A/'CANDIDATES.tsv').open('w',newline='') as f:
        w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(['index','edition','paragraph','leaf','writer','source_atoms','source_types','groups','characters','status','nodes','exhaustive','saved_codes','independent_meaning_capacity'])
        for c in cases:w.writerow([c['index'],c['edition'],c['paragraph'],c['leaf'],c['writer'],c['source_atoms'],c['source_types'],c['groups'],c['characters'],c['status'],c.get('nodes',''),c.get('exhaustive',''),len(c.get('codes',[])),0])
    lines=['# Every complete conditional typed-tree code','','All meanings are fixed source hypotheses. No historical source or word is confirmed.']
    for c in cases:
        if c['status']!='SAT':continue
        lines+=['',f"## {c['edition']} {c['paragraph']} {c['writer']}",'',f"Complete target: `{' '.join(c['words'])}`",'',f"Code ambiguity: {c['code_ambiguity']}."]
        for ci,code in enumerate(c['codes']):
            lines+=['',f'### Code {ci+1}','','| Atom | Code class | Proposed string |','|---|---|---|']
            lines += [f"| {a} | {source['types'][a]} | {v} |" for a,v in sorted(code.items())]
            atoms=streams[c['writer']];cursor=0
            lines+=['','| Complete word | Source components |','|---|---|']
            for word in c['words']:
                suffix=word;parts=[]
                while suffix:
                    a=atoms[cursor];value=code[a];assert suffix.startswith(value);suffix=suffix[len(value):];parts.append(a);cursor+=1
                lines.append(f"| {word} | {' + '.join(parts)} |")
            assert cursor==len(atoms)
    if not counts['SAT']:lines+=['','No complete code witness was found; all source/computational unknowns remain in the table.']
    (A/'READINGS.md').write_text('\n'.join(lines)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()

#!/usr/bin/env python3
"""All exposed paragraph pairs, finite writer, bounded joint constraints."""
import argparse,collections,concurrent.futures,csv,datetime,gzip,hashlib,io,json,re,subprocess,sys,time
from pathlib import Path
from model import prelim,joint_numeric,solve,ground
E=Path(__file__).resolve().parents[1];R=E.parents[2];A=E/'artifacts'
def read(p):return json.loads(p.read_text())
def put(name,x):(A/name).write_text(json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n')
def stamp():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def lockcheck():
    for p,h in read(E/'PREREG_LOCK.json')['files'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p

def isolated(job):
    try:
        r=subprocess.run([sys.executable,str(Path(__file__).resolve()),'--solve-json'],input=json.dumps(job),text=True,capture_output=True,timeout=12)
        if r.returncode:return dict(status='ERROR_WORKER',exit_code=r.returncode)
        return json.loads(r.stdout)
    except subprocess.TimeoutExpired:return dict(status='UNKNOWN_WALL_LIMIT')

def pair_status(a,b):
    if a['status'].startswith('CONTRADICTED'):return 'CONTRADICTED_IV15'
    if b['status'].startswith('CONTRADICTED'):return 'CONTRADICTED_V19'
    if a['status']=='UNKNOWN_SOURCE' or b['status']=='UNKNOWN_SOURCE':return 'UNKNOWN_SOURCE'
    return None

def fixtures():
    source=read(E/'src/SOURCE.json');streams=[v['atoms'] for v in source['recipes'].values()]
    ordinary=sorted(set().union(*map(set,streams))-{'QD1','QD2','QS1'})
    code={a:'z'+chr(97+i//26)+chr(97+i%26) for i,a in enumerate(ordinary)}
    code.update(QD1='dix',QD2='diix',QS1='six');cases=[]
    for writer in ['FORWARD','REVERSE_ATOMS']:
        st=streams if writer=='FORWARD' else [list(reversed(v)) for v in streams];words=[]
        for stream in st:
            ws=[];pending=[]
            for a in stream:
                if a.startswith('Q'):
                    if pending:ws.append(''.join(pending));pending=[]
                    ws.append(code[a])
                else:
                    pending.append(code[a])
                    if len(pending)==2:ws.append(''.join(pending));pending=[]
            if pending:ws.append(''.join(pending))
            words.append(ws)
        pa=prelim('IV15',st[0],words[0]);pb=prelim('V19',st[1],words[1]);num=joint_numeric(pa['options'],pb['options']);assert num
        result=solve(dict(streams=st,words=words,numeric=num,pinned_code=code,seconds=2))
        assert result['status']=='SAT' and result['alternative_status']=='UNSAT_SOLVER'
        cases.append(dict(writer=writer,status=result['status'],ground=ground(st,words,code,num)['valid']))
        assert not ground(st,[words[0]+['z'],words[1]],code,num)['valid']
        # A real word break inside an ordinary atom must fail despite identical characters.
        wi=next(i for i,w in enumerate(words[0]) if w.startswith('z'))
        broken=[*words[0][:wi],words[0][wi][:1],words[0][wi][1:],*words[0][wi+1:]]
        assert not ground(st,[broken,words[1]],code,num)['valid']
    put('PREFLIGHT.json',dict(status='PASS',cases=cases,scope='Pinned synthetic writer correctness, no search significance or source meaning validation'))
    print(json.dumps(read(A/'PREFLIGHT.json'),indent=2))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--solve-json',action='store_true');ap.add_argument('--fixtures',action='store_true');args=ap.parse_args()
    if args.solve_json:print(json.dumps(solve(json.load(sys.stdin))));return
    if args.fixtures:fixtures();return
    lockcheck();spec=read(E/'src/SPEC.json');source=read(E/'src/SOURCE.json');start=time.monotonic();started=stamp()
    target=read(R/spec['input']);singles=[];panels={};streams={}
    for writer in spec['writers']:
        streams[writer]={k:v['atoms'] if writer=='FORWARD' else list(reversed(v['atoms'])) for k,v in source['recipes'].items()}
        for ed,paras in target.items():
            panels[(writer,ed)]={'IV15':[],'V19':[]}
            for name in spec['source_ids']:
                for p in paras:
                    assert not p['page'].startswith('f84') and p['page']!='f116v'
                    ws=[w for line in p['lines'] for w in line['words']];assert len(ws)==p['groups']
                    literal=all(line['anchor_eligible'] for line in p['lines']) and all(re.fullmatch(spec['literal_pattern'],w) for w in ws)
                    row=dict(index=len(singles),writer=writer,edition=ed,recipe=name,paragraph=p['id'],page=p['page'],leaf=p['leaf'],groups=len(ws),characters=sum(map(len,ws)),words=ws,source_ids=[x for l in p['lines'] for x in l['source_ids']],source_atoms=len(streams[writer][name]),independent_meaning_capacity=0)
                    row.update(prelim(name,streams[writer][name],ws) if literal else dict(status='UNKNOWN_SOURCE',options=[]))
                    panels[(writer,ed)][name].append(row);singles.append(row)
    put('PARAGRAPH_CASES.json',singles)
    jobs=[];excluded_same_leaf=0;population=0
    for (writer,ed),panel in panels.items():
        for a in panel['IV15']:
            for b in panel['V19']:
                if a['leaf']==b['leaf']:excluded_same_leaf+=1;continue
                population+=1
                if pair_status(a,b):continue
                num=joint_numeric(a['options'],b['options'])
                if not num:continue
                key=f"{ed}|{a['paragraph']}|{b['paragraph']}|{writer}"
                jobs.append(dict(a=a['index'],b=b['index'],sort_key=hashlib.sha256(key.encode()).hexdigest(),streams=[streams[writer]['IV15'],streams[writer]['V19']],words=[a['words'],b['words']],numeric=num,seconds=spec['solver_seconds'],alternative_seconds=spec['alternative_code_seconds']))
    jobs.sort(key=lambda j:(j['sort_key'],j['a'],j['b']));chosen=jobs[:spec['max_joint_jobs']];results={};print(json.dumps(dict(paragraph_cases=len(singles),candidate_pairs=population,compatible_numeric_pairs=len(jobs),solver_jobs=len(chosen))),flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=spec['workers']) as pool:
        futures={pool.submit(isolated,j):j for j in chosen}
        for n,f in enumerate(concurrent.futures.as_completed(futures),1):
            j=futures[f];r=f.result();results[(j['a'],j['b'])]=r
            if n%32==0 or n==len(chosen):print(json.dumps(dict(done=n,total=len(chosen),status=r['status'])),flush=True)
    details=[]
    for j in jobs:
        r=results.get((j['a'],j['b']),dict(status='UNKNOWN_JOB_CAP'))
        details.append(dict(iv15_index=j['a'],v19_index=j['b'],numeric_options=j['numeric'],**r))
    put('JOINT_CASES.json',details)
    detailmap={(d['iv15_index'],d['v19_index']):d for d in details};counts=collections.Counter();by_writer=collections.defaultdict(collections.Counter)
    with (A/'PAIR_DECISIONS.tsv.gz').open('wb') as raw:
        with gzip.GzipFile(fileobj=raw,mode='wb',mtime=0) as gz:
            with io.TextIOWrapper(gz,encoding='utf-8',newline='') as tf:
                w=csv.writer(tf,delimiter='\t',lineterminator='\n');w.writerow(['iv15_index','v19_index','status'])
                for (writer,ed),panel in panels.items():
                    for a in panel['IV15']:
                        for b in panel['V19']:
                            if a['leaf']==b['leaf']:continue
                            status=pair_status(a,b)
                            if status is None:status=detailmap.get((a['index'],b['index']),{}).get('status','CONTRADICTED_SHARED_QUANTITY')
                            w.writerow([a['index'],b['index'],status]);counts[status]+=1;by_writer[writer][status]+=1
    with (A/'CANDIDATES.tsv').open('w',newline='') as f:
        w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(['index','writer','edition','recipe','paragraph','leaf','predicted_atoms','observed_groups','status','quantity_options','independent_meaning_capacity'])
        for r in singles:w.writerow([r['index'],r['writer'],r['edition'],r['recipe'],r['paragraph'],r['leaf'],r['source_atoms'],r['groups'],r['status'],len(r['options']),0])
    unknown=sum(v for k,v in counts.items() if k.startswith(('UNKNOWN','ERROR')));sat=counts['SAT']
    result=dict(status='CONDITIONAL_JOINT_WITNESSES' if sat else 'BOUNDED_JOINT_SEARCH_UNRESOLVED' if unknown else 'NO_COMPLETE_JOINT_FIT',paragraph_population={ed:len(p) for ed,p in target.items()},paragraph_cases=len(singles),candidate_pairs=population,same_leaf_pairs_excluded=excluded_same_leaf,compatible_numeric_pairs=len(jobs),solver_jobs=len(chosen),pair_status_counts=dict(counts),by_writer={k:dict(v) for k,v in by_writer.items()},single_status_counts=dict(collections.Counter(r['status'] for r in singles)),full_joint_witnesses=sat,unknown_pairs=unknown,confirmed_words=0,independent_meaning_capacity=0,significance_claim=False,reserve_accesses=0)
    put('RESULT.json',result);put('EXECUTION_RECEIPT.json',dict(started_utc=started,finished_utc=stamp(),wall_seconds=time.monotonic()-start,solver_python_version=sys.version.split()[0],workers=spec['workers']))
    lines=['# Complete conditional joint readings','','All source meanings remain hypotheses. Every matching complete pair is included.']
    for d in details:
        if d['status']!='SAT':continue
        a,b=singles[d['iv15_index']],singles[d['v19_index']]
        lines+=['',f"## {a['edition']} / {a['writer']} / {a['paragraph']} + {b['paragraph']}",'',f"Numeric alternatives: `{json.dumps(d['witness']['numeric_frames'])}`",'','| Atom | Proposed code |','|---|---|']
        lines += [f"| {k} | {v} |" for k,v in sorted(d['code'].items())]
        for row,align in zip((a,b),d['witness']['alignment']):
            lines+=['',f"Whole {row['recipe']}: `{' '.join(row['words'])}`",'','| Word | Proposed source parts |','|---|---|']
            for wi,w in enumerate(row['words']):lines.append(f"| {w} | {' + '.join(x['atom'] for x in align if x['word_index']==wi)} |")
        lines += ['',f"Different-code search: {d['alternative_status']}. Ingredient identity, source choice, numerical scale and historical meaning remain unconfirmed."]
    if not sat:lines+=['','No complete joint reading was found. The table retains all contradictions and unknowns.']
    (A/'READINGS.md').write_text('\n'.join(lines)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()

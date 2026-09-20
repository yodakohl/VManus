#!/usr/bin/env python3
"""Complete preregistered Cennini record census; no source or surface repairs."""
import argparse,collections,concurrent.futures,csv,datetime,hashlib,itertools,json,re,subprocess,sys,time
from pathlib import Path
from records import FIELDS,build,profile,prelim
from finite import solve
sys.setrecursionlimit(10000)
E=Path(__file__).resolve().parents[1];R=E.parents[2];A=E/'artifacts'
def read(p):return json.loads(p.read_text())
def put(n,x):(A/n).write_text(json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def lockcheck():
    for p,h in read(E/'PREREG_LOCK.json')['files'].items():assert sha(R/p)==h,p
def execute(job,reverse=False):
    from reverse import replay
    s=job['spec'];records=job['records'];writer=job['writer'];words=job['words'];started=time.monotonic()
    budget=s['independent_seconds_per_bundle'] if reverse else s['seconds_per_bundle']
    nodecap=s['independent_max_total_nodes'] if reverse else s['max_total_nodes_per_bundle']
    rows=[];witnesses=[];nodes=0
    for oi,order in enumerate(itertools.permutations(FIELDS)):
        left=budget-(time.monotonic()-started)
        if left<=0 or nodes>=nodecap or len(witnesses)>=s['max_solutions']:
            rows.append(dict(order=oi,status='UNKNOWN_UNSTARTED',exhaustive=False));continue
        b=build(records,writer,order);f=replay if reverse else solve
        result=f(b['atoms'],words,b['types'],seconds=max(.001,left),max_nodes=min(s['max_nodes_per_order'],nodecap-nodes),max_solutions=s['max_solutions']-len(witnesses),record_ends=b['record_ends'])
        nodes+=result['nodes']
        for code in result.pop('codes',[]):witnesses.append(dict(order=oi,fields=list(order),code=code))
        result.pop('initial_domain_sizes',None);rows.append(dict(order=oi,**result))
    exhaustive=all(r['exhaustive'] for r in rows)
    status='SAT' if witnesses else 'UNSAT_EXACT' if exhaustive else 'UNKNOWN_EXACT_LIMIT'
    return dict(status=status,orders=rows,codes=witnesses,exhaustive=exhaustive,nodes=nodes,elapsed_seconds=time.monotonic()-started,ambiguity='MULTIPLE_CODES_OR_ORDERS' if len(witnesses)>1 else 'ONE_CODE_IN_FIXED_MODEL' if witnesses and exhaustive else 'UNRESOLVED' if witnesses else 'NO_WITNESS')
def isolated(job,reverse=False):
    try:
        p=subprocess.run([sys.executable,str(Path(__file__).resolve()),'--reverse-json' if reverse else '--solve-json'],input=json.dumps(job),capture_output=True,text=True,timeout=job['spec']['outer_seconds_per_job'])
        return json.loads(p.stdout) if p.returncode==0 else dict(status='ERROR_WORKER',exit_code=p.returncode,codes=[],exhaustive=False)
    except subprocess.TimeoutExpired:return dict(status='UNKNOWN_WALL_LIMIT',codes=[],exhaustive=False)
def predictions():
    s=read(E/'src/SPEC.json');source=read(R/s['source_facts']);out={}
    for w in s['writers']:
        canonical=build(source['records'],w,FIELDS);dictionary=sorted(set(canonical['atoms']));ix={a:i for i,a in enumerate(dictionary)}
        out[w]=dict(dictionary=dictionary,record_ends=canonical['record_ends'],profile=profile(source['records'],w),streams=[dict(order=i,fields=list(order),atoms=[ix[a] for a in build(source['records'],w,order)['atoms']]) for i,order in enumerate(itertools.permutations(FIELDS))])
    put('PREDICTIONS.json',out);print(json.dumps({w:dict(atoms=v['profile']['atoms'],records=v['profile']['records'],atom_types=len(v['dictionary']),orders=len(v['streams'])) for w,v in out.items()}))
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--predictions',action='store_true');ap.add_argument('--solve-json',action='store_true');ap.add_argument('--reverse-json',action='store_true');args=ap.parse_args()
    if args.solve_json or args.reverse_json:print(json.dumps(execute(json.load(sys.stdin),args.reverse_json)));return
    if args.predictions:predictions();return
    lockcheck();assert (A/'PUBLIC_REGISTRATION.json').exists();s=read(E/'src/SPEC.json');source=read(R/s['source_facts']);ps=read(R/s['input'])
    profiles={w:profile(source['records'],w) for w in s['writers']};bundles=[];cases=[];pending=[]
    started=datetime.datetime.now(datetime.timezone.utc).isoformat();t=time.monotonic()
    for ed,paragraphs in ps.items():
        pages=collections.defaultdict(list)
        for p in paragraphs:
            assert not p['page'].startswith('f84') and p['page']!='f116v';pages[p['page']].append(p)
        for page,parts in sorted(pages.items()):
            parts.sort(key=lambda p:p['lines'][0]['row'])
            for size in s['bundle_sizes']:
                for start in range(len(parts)-size+1):
                    seq=parts[start:start+size];words=[w for p in seq for l in p['lines'] for w in l['words']]
                    gaps=[i for i in range(size-1) if int(seq[i]['lines'][-1]['locus'].rsplit('.',1)[1])+1!=int(seq[i+1]['lines'][0]['locus'].rsplit('.',1)[1])]
                    literal=all(l['anchor_eligible'] for p in seq for l in p['lines']) and all(re.fullmatch(s['literal_pattern'],w) for w in words)
                    b=dict(bundle=len(bundles),edition=ed,page=page,leaf=seq[0]['leaf'],paragraphs=[p['id'] for p in seq],paragraph_groups=[p['groups'] for p in seq],words=words,groups=len(words),characters=sum(map(len,words)),gaps=gaps,literal=literal);bundles.append(b)
                    for writer in s['writers']:
                        c=dict(case=len(cases),bundle=b['bundle'],edition=ed,page=page,leaf=b['leaf'],writer=writer,groups=len(words),characters=b['characters'])
                        if gaps:c['status']='UNKNOWN_GAP'
                        elif not literal:c['status']='UNKNOWN_SOURCE'
                        else:c.update(prelim(profiles[writer],words))
                        if c['status']=='EXACT_SEARCH_REQUIRED':
                            key=hashlib.sha256(json.dumps([ed,page,b['paragraphs'],writer],separators=(',',':')).encode()).hexdigest();c['job_hash']=key
                            pending.append((key,c['case'],dict(spec=s,records=source['records'],words=words,writer=writer)))
                        if 'bound' in c:c['bound'].pop('merges',None)
                        cases.append(c)
    selected=sorted(pending)[:s['max_exact_jobs']]
    for _,i,_ in sorted(pending)[s['max_exact_jobs']:]:cases[i]['status']='UNKNOWN_JOB_CAP'
    print(json.dumps(dict(bundles=len(bundles),cases=len(cases),exact_candidates=len(pending),selected_exact_jobs=len(selected))),flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=s['workers']) as pool:
        fs={pool.submit(isolated,j):i for _,i,j in selected}
        for done,f in enumerate(concurrent.futures.as_completed(fs),1):
            cases[fs[f]].update(f.result())
            if done%32==0 or done==len(fs):print(json.dumps(dict(exact_finished=done,total=len(fs))),flush=True)
    counts=collections.Counter(c['status'] for c in cases)
    result=dict(experiment='GDT1005',status='COMPLETE_CONDITIONAL_RECORD_CODES' if counts['SAT'] else 'NO_COMPLETE_LITERAL_RECORD_CODE_WITH_UNKNOWN_SOURCE_OR_LIMITS',paragraph_counts={ed:len(rows) for ed,rows in ps.items()},source_records=len(source['records']),source_value_types=len({r[k] for r in source['records'] for k in FIELDS}),source_atoms={w:p['atoms'] for w,p in profiles.items()},bundles=len(bundles),cases=len(cases),field_orders_per_case=120,status_counts=dict(counts),panels={ed:{w:dict(collections.Counter(c['status'] for c in cases if c['edition']==ed and c['writer']==w)) for w in s['writers']} for ed in ps},exact_candidates=len(pending),selected_exact_jobs=len(selected),saved_codes=sum(len(c.get('codes',[])) for c in cases),confirmed_words=0,independent_meaning_capacity=0,reserve_accesses=0,significance_claim=False)
    put('BUNDLES.json',bundles);put('CASES.json',cases);put('RESULT.json',result)
    put('EXECUTION_RECEIPT.json',dict(started_utc=started,finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),wall_seconds=time.monotonic()-t,registered_utc=read(E/'PREREG_LOCK.json')['registered_utc'],prior_exposure=True,new_admissions=0))
    with (A/'CANDIDATES.tsv').open('w',newline='') as f:
        w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(['case','bundle','edition','page','leaf','paragraphs','writer','groups','characters','status','codes','independent_meaning_capacity'])
        for c in cases:w.writerow([c['case'],c['bundle'],c['edition'],c['page'],c['leaf'],';'.join(bundles[c['bundle']]['paragraphs']),c['writer'],c['groups'],c['characters'],c['status'],len(c.get('codes',[])),0])
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()

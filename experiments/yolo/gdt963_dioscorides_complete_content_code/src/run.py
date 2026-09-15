#!/usr/bin/env python3
"""Fixed finite whole-record code equations; no source or target repair."""
import argparse, collections, concurrent.futures, gzip, hashlib, heapq, itertools, json, re, subprocess, sys, time
from pathlib import Path
E=Path(__file__).resolve().parents[1]; ROOT=E.parents[2]
PARENT=ROOT/'experiments/yolo/gdt915_terminal_lr_phrase_transfer'
EDITIONS=('ZL3b','IT2a','RF1b')

def dump(name, value):
    p=E/'artifacts'/name
    s=json.dumps(value,ensure_ascii=False,separators=(',',':'))+'\n'
    if p.suffix=='.gz':
        with gzip.GzipFile(filename=str(p),mode='wb',mtime=0) as f:f.write(s.encode())
    else:p.write_text(s)

def lower_bound(counts, d):
    vals=list(counts.values())
    if len(vals)==1:return vals[0]
    if d<2:return None
    pad=(-(len(vals)-1))%(d-1)
    heap=vals+[0]*pad;heapq.heapify(heap);cost=0
    while len(heap)>1:
        v=sum(heapq.heappop(heap) for _ in range(d));cost+=v;heapq.heappush(heap,v)
    return cost

def intake():
    frames=[]
    spec=json.loads((PARENT/'src/SPEC.json').read_text())
    for ed in EDITIONS:
        pages=collections.defaultdict(list)
        for phase in ('DISCOVERY','EVALUATION'):
            d=json.loads((PARENT/'artifacts'/f'SOURCE_{phase}_{ed}.json').read_text())
            for row in d['lines']:
                m=row['metadata'];assert m['page'] in spec['partitions'][phase]
                assert not m['page'].startswith('f84') and m['page']!='f116v'
                if m['section']=='H' and m['kind']=='P' and m['page']!='f1r':
                    pages[m['page']].append((m,[dict(zip(d['group_columns'],g)) for g in row['groups']]))
        for page, rows in sorted(pages.items()):
            rows.sort(key=lambda x:int(x[0]['source_row_index']))
            reasons=[];words=[];groups=[]
            for m,gs in rows:
                loc=m['locus'];n=int(m['source_group_count'])
                if [int(g['source_group_index']) for g in gs]!=list(range(1,n+1)) or not gs:reasons.append([loc,'INCOMPLETE_GROUP_INDICES'])
                if any(not re.fullmatch('[a-z]+',g['ivtff_group_raw']) for g in gs):reasons.append([loc,'NONLITERAL_GROUP'])
                if gs and (gs[0]['left_separator']!='LINE_START' or gs[-1]['right_separator']!='LINE_END'):reasons.append([loc,'OUTER_BOUNDARY'])
                for a,b in zip(gs,gs[1:]):
                    if a['right_separator']!=b['left_separator'] or a['right_separator'] not in ('DEFINITE_SPACE','DRAWING_INTERRUPTION'):reasons.append([loc,'UNKNOWN_INTERNAL_SEAM',a['source_group_id'],b['source_group_id']])
                words.extend(g['ivtff_group_raw'] for g in gs)
                groups.extend(dict(locus=loc,**g) for g in gs)
            text=''.join(words) if not reasons else None
            frames.append(dict(id=f'{ed}:{page}',edition=ed,page=page,physical_leaf=re.match(r'f\d+',page).group(),eligible=not reasons,reasons=reasons,line_count=len(rows),group_count=len(groups),groups=groups,text=text,characters=len(text) if text else None,alphabet=sorted(set(text)) if text else []))
    return frames

def verify_code(records, code, outputs):
    if any(not isinstance(v,str) or not v for v in code.values()):return False
    ss=sorted(code.values())
    if any(b.startswith(a) for a,b in zip(ss,ss[1:])):return False
    return all(''.join(code[a] for a in r['atoms'])==outputs[r['id']] for r in records)

def solve_job(job):
    import cvc5
    from cvc5 import Kind as K
    started=time.monotonic();records=job['records'];domains=job['domains']
    atoms=sorted({a for r in records for a in r['atoms']});counts={r['id']:collections.Counter(r['atoms']) for r in records}
    if any(not domains[r['id']] for r in records):return {'status':'UNSAT_EMPTY_DOMAIN'}
    bounds={a:min((max(len(t['text']) for t in domains[r['id']])-(len(r['atoms'])-counts[r['id']][a]))//counts[r['id']][a] for r in records if counts[r['id']][a]) for a in atoms}
    if min(bounds.values())<1:return {'status':'UNSAT_NONEMPTY_LENGTH'}
    s=cvc5.Solver();s.setLogic('QF_SLIA');s.setOption('produce-models','true');s.setOption('incremental','true');s.setOption('strings-exp','true')
    vs={a:s.mkConst(s.getStringSort(),f'a{i}') for i,a in enumerate(atoms)}
    for a,v in vs.items():
        le=s.mkTerm(K.STRING_LENGTH,v);s.assertFormula(s.mkTerm(K.GEQ,le,s.mkInteger(1)));s.assertFormula(s.mkTerm(K.LEQ,le,s.mkInteger(bounds[a])))
    for a,b in itertools.combinations(atoms,2):
        s.assertFormula(s.mkTerm(K.NOT,s.mkTerm(K.STRING_PREFIX,vs[a],vs[b])))
        s.assertFormula(s.mkTerm(K.NOT,s.mkTerm(K.STRING_PREFIX,vs[b],vs[a])))
    expr={};selectors={}
    for ri,r in enumerate(records):
        rid=r['id'];terms=[vs[a] for a in r['atoms']];expr[rid]=s.mkTerm(K.STRING_CONCAT,*terms) if len(terms)>1 else terms[0]
        selectors[rid]=s.mkConst(s.getIntegerSort(),f'page_{ri}')
        branches=[]
        for j,t in enumerate(domains[rid]):
            branches.append(s.mkTerm(K.AND,s.mkTerm(K.EQUAL,selectors[rid],s.mkInteger(j)),s.mkTerm(K.EQUAL,expr[rid],s.mkString(t['text']))))
        s.assertFormula(s.mkTerm(K.OR,*branches) if len(branches)>1 else branches[0])
    for a,b in itertools.combinations(records,2):
        for i,ta in enumerate(domains[a['id']]):
            for j,tb in enumerate(domains[b['id']]):
                if ta['physical_leaf']==tb['physical_leaf']:
                    pair=s.mkTerm(K.AND,s.mkTerm(K.EQUAL,selectors[a['id']],s.mkInteger(i)),s.mkTerm(K.EQUAL,selectors[b['id']],s.mkInteger(j)))
                    s.assertFormula(s.mkTerm(K.NOT,pair))
    def check(seconds):
        s.setOption('tlimit-per',str(max(1,int(seconds*1000))))
        ans=s.checkSat()
        return 'SAT' if ans.isSat() else 'UNSAT_SOLVER' if ans.isUnsat() else 'UNKNOWN_SOLVER'
    status=check(job['seconds']);out=dict(status=status,solver='cvc5',version=cvc5.__version__,elapsed_seconds=time.monotonic()-started,atom_count=len(atoms),codeword_length_bounds=bounds)
    if status!='SAT':return out
    code={a:s.getValue(v).getStringValue() for a,v in vs.items()};outputs={rid:s.getValue(x).getStringValue() for rid,x in expr.items()}
    assignments={rid:domains[rid][int(str(s.getValue(sel)))] for rid,sel in selectors.items()}
    assert verify_code(records,code,outputs)
    assert len({t['physical_leaf'] for t in assignments.values()})==len(records)
    out.update(code=code,outputs=outputs,assignments=assignments,witness_check='EXACT_PASS')
    if job.get('projections'):
        deadline=time.monotonic()+120;projections={}
        for a in sorted(x for x in atoms if not x.startswith('LEX:')):
            if time.monotonic()>=deadline:projections[a]='UNKNOWN_PROJECTION_BUDGET';continue
            s.push();s.assertFormula(s.mkTerm(K.NOT,s.mkTerm(K.EQUAL,vs[a],s.mkString(code[a]))));projections[a]=check(min(2,deadline-time.monotonic()));s.pop()
        out['atom_alternative_queries']=projections
    out['elapsed_seconds']=time.monotonic()-started
    return out

def isolated(job):
    started=time.monotonic()
    cap=15 if len(job['records'])==1 else job['seconds']+150
    try:
        p=subprocess.run([sys.executable,str(Path(__file__).resolve()),'--solve-job'],input=json.dumps(job),text=True,capture_output=True,timeout=cap)
        if p.returncode:return dict(status='ERROR_SOLVER_PROCESS',returncode=p.returncode,elapsed_seconds=time.monotonic()-started)
        return json.loads(p.stdout)
    except subprocess.TimeoutExpired:return dict(status='UNKNOWN_WALL_CEILING',elapsed_seconds=time.monotonic()-started,wall_ceiling=cap)

def main():
    lock=json.loads((E/'PREREG_LOCK.json').read_text())
    for p,h in lock['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    source=json.loads((E/'src/SOURCE.json').read_text());records=source['records'];frames=intake();dump('TARGET_FRAMES.json.gz',frames)
    dump('IDENTICAL_TARGET_STRINGS.json',[[t['id'] for t in frames if t['eligible'] and t['text']==text] for text in sorted({t['text'] for t in frames if t['eligible']})])
    cases=[];jobs=[]
    for t in frames:
        for r in records:
            c=dict(edition=t['edition'],page=t['page'],target_id=t['id'],record=r['id'],source_atoms=len(r['atoms']),target_characters=t['characters'])
            if not t['eligible']:c.update(status='UNKNOWN_SOURCE',reasons=t['reasons'])
            else:
                bound=lower_bound(r['counts'],len(t['alphabet']));c['prefix_length_lower_bound']=bound
                if bound is None or bound>len(t['text']):c['status']='CONTRADICTED_LENGTH_BOUND'
                else:
                    c['status']='PENDING';job=dict(records=[{'id':r['id'],'atoms':r['atoms']}],domains={r['id']:[{k:t[k] for k in ('id','page','physical_leaf','text')}]},seconds=5)
                    jobs.append((len(cases),job))
            cases.append(c)
    print('frames',len(frames),'cases',len(cases),'local_solver_jobs',len(jobs),flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        future={pool.submit(isolated,job):idx for idx,job in jobs}
        for done,f in enumerate(concurrent.futures.as_completed(future),1):
            idx=future[f];res=f.result();cases[idx].update(status=res['status'],solver_result=res)
            if done%40==0:print('local_completed',done,'of',len(jobs),flush=True)
    dump('ALL_LOCAL_CASES.json.gz',cases)
    header=['edition','page','record','status','source_atoms','target_characters','prefix_length_lower_bound']
    (E/'artifacts/CANDIDATE_TABLE.tsv').write_text('\t'.join(header)+'\n'+'\n'.join('\t'.join(str(c.get(k,'')) for k in header) for c in cases)+'\n')
    joint={}
    excluded={'CONTRADICTED_LENGTH_BOUND','UNSAT_SOLVER','UNSAT_EMPTY_DOMAIN','UNSAT_NONEMPTY_LENGTH','UNKNOWN_SOURCE'}
    for ed in EDITIONS:
        eligible=[t for t in frames if t['edition']==ed and t['eligible']]
        if len({t['physical_leaf'] for t in eligible})<4:joint[ed]=dict(status='NO_CAPACITY',eligible_pages=len(eligible),eligible_leaves=len({t['physical_leaf'] for t in eligible}));continue
        domains={r['id']:[{k:t[k] for k in ('id','page','physical_leaf','text')} for t in eligible if next(c for c in cases if c['target_id']==t['id'] and c['record']==r['id'])['status'] not in excluded] for r in records}
        if any(not x for x in domains.values()):joint[ed]=dict(status='CONTRADICTED_EMPTY_LOCAL_ROLE',empty_roles=[k for k,v in domains.items() if not v])
        else:
            print('joint_start',ed,{k:len(v) for k,v in domains.items()},flush=True)
            joint[ed]=isolated(dict(records=[{'id':r['id'],'atoms':r['atoms']} for r in records],domains=domains,seconds=600,projections=True))
        dump('JOINT_RESULTS.json',joint)
    dump('JOINT_RESULTS.json',joint)
    for ed,res in joint.items():
        if res['status']=='SAT':
            singleton=set(source['global_singletons']);res['singleton_target_characters']={r['id']:sum(len(res['code'][a]) for a in r['atoms'] if a in singleton) for r in records}
            alignment=[]
            for r in records:
                pos=0
                for i,a in enumerate(r['atoms']):
                    value=res['code'][a];alignment.append(dict(edition=ed,record=r['id'],target=res['assignments'][r['id']]['id'],atom_index=i,atom=a,start=pos,end=pos+len(value),written=value,source_singleton=a in singleton));pos+=len(value)
            dump(f'COMPLETE_ALIGNMENT_{ed}.json',alignment)
    dump('JOINT_RESULTS.json',joint)
    statuses=[v['status'] for v in joint.values()]
    status='COMPLETE_CONDITIONAL_CODE_WITNESS' if 'SAT' in statuses else 'BOUNDED_SEARCH_UNRESOLVED' if any(s.startswith(('UNKNOWN','ERROR')) for s in statuses) else 'COMPLETE_FIXED_CODE_NO_WITNESS'
    result=dict(status=status,source_records=4,source_atoms=sum(len(r['atoms']) for r in records),distinct_source_atoms=source['atom_count'],global_source_singletons=len(source['global_singletons']),frames=len(frames),local_cases=len(cases),local_statuses=dict(collections.Counter(c['status'] for c in cases)),joint_statuses={ed:x['status'] for ed,x in joint.items()},confirmed_words=0,significance_claim=False,independent_confirmation_leaves=0,solver_seconds_local=5,solver_seconds_joint=600)
    dump('RESULT.json',result);print(json.dumps(result),flush=True)

if __name__=='__main__':
    if '--solve-job' in sys.argv:
        try:print(json.dumps(solve_job(json.load(sys.stdin)),ensure_ascii=False))
        except Exception as exc:
            print(json.dumps({'status':'ERROR_MODEL_IMPLEMENTATION','exception_type':type(exc).__name__}));sys.exit(0)
    else:main()

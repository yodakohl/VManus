"""Independent backward path and finite SAT checker; no runner/core import."""
import collections,csv,datetime,hashlib,importlib.util,json
from pathlib import Path
import z3
E=Path(__file__).resolve().parents[1];R=E.parents[2];A=E/'artifacts'
REQ=('INITIAL','GOAL','SAFETY','CAPACITY','CONCLUSION');BITS={k:2**i for i,k in enumerate(REQ)}
def read(p):return json.loads(p.read_text())
def load(path,name):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def options(spec,item):return list(spec['types'][item[1:]]) if item[0]=='@' else [item]
def independent_endpoints(raw,lex,spec):
    problems=[];d={};n=len(raw);least=sum(len(spec['patterns'][k]) for k in REQ)
    if n<least:problems.append(dict(kind='MINIMUM_COMPLETE_SCOPE',observed=n,required=least))
    for name in ('INITIAL','CONCLUSION'):
        pat=spec['patterns'][name];start=0 if name=='INITIAL' else n-len(pat)
        if start<0 or start+len(pat)>n:continue
        for offset,slot in enumerate(pat):
            pos=start+offset;w=raw[pos];want=set(options(spec,slot))
            if w in lex:
                if lex[w] not in want:problems.append(dict(kind='KNOWN_VALUE',position=pos+1,raw=w,value=lex[w],required=sorted(want),clause=name))
            else:
                d[w]=want if w not in d else d[w].intersection(want)
                if not d[w]:problems.append(dict(kind='SHARED_ENDPOINT_VALUE',position=pos+1,raw=w,clause=name))
    return dict(pass_=len(problems)==0,conflicts=problems,unknown_domains={w:sorted(v) for w,v in sorted(d.items())})

def transitions(raw,lex,spec):
    n=len(raw);edges=[]
    for kind,pattern in spec['patterns'].items():
        width=len(pattern)
        for left in range(n-width+1):
            right=left+width
            if (left==0)!=(kind=='INITIAL') or (right==n)!=(kind=='CONCLUSION'):continue
            allowed=[options(spec,t) for t in pattern]
            if all(raw[i] not in lex or lex[raw[i]] in allowed[i-left] for i in range(left,right)):
                edges.append((left,right,kind,allowed))
    return edges

def backward(raw,lex,spec):
    es=transitions(raw,lex,spec);dp=[set() for _ in range(len(raw)+1)];dp[-1].add(0)
    for left in range(len(raw)-1,-1,-1):
        for a,b,k,_ in es:
            if a!=left:continue
            bit=BITS.get(k,0)
            for used in dp[b]:
                if used&bit==0:dp[a].add(used|bit)
    return 31 in dp[0]

def sat_shared(raw,lex,spec,timeout):
    es=transitions(raw,lex,spec);symbols=sorted(set(lex.values())|{x for vs in spec['types'].values() for x in vs}|{t for p in spec['patterns'].values() for t in p if not t.startswith('@')});num={s:i for i,s in enumerate(symbols)}
    slv=z3.Solver();slv.set(timeout=timeout);xs={w:z3.Int('w'+str(i)) for i,w in enumerate(sorted(set(raw)-lex.keys()))}
    for x in xs.values():slv.add(x>=0,x<len(symbols))
    bs=[z3.Bool('edge'+str(i)) for i in range(len(es))]
    for pos in range(len(raw)):slv.add(z3.Sum([z3.If(b,1,0) for b,(lo,hi,_,_) in zip(bs,es) if lo<=pos<hi])==1)
    for kind in REQ:slv.add(z3.Sum([z3.If(b,1,0) for b,(_,_,k,_) in zip(bs,es) if k==kind])==1)
    for b,(lo,hi,k,allowed) in zip(bs,es):
        for i in range(lo,hi):
            w=raw[i]
            if w in xs:slv.add(z3.Implies(b,z3.Or([xs[w]==num[v] for v in allowed[i-lo]])))
    return str(slv.check())

def witness_check(raw,lex,spec,w):
    assert set(w['aliases'])==set(raw)-lex.keys()
    whole={**lex,**w['aliases']};assert len(w['alias_domains'])==len(w['aliases'])
    pos=0;kinds=[];observed={}
    for c in w['parse']:
        assert c['start']==pos and c['end']==pos+len(spec['patterns'][c['kind']])
        actual=[whole[s] for s in raw[c['start']:c['end']]];assert actual==c['symbols']
        for i,slot in enumerate(spec['patterns'][c['kind']]):
            assert actual[i] in options(spec,slot)
            word=raw[pos+i]
            if word not in lex:observed[word]=set(options(spec,slot)) if word not in observed else observed[word]&set(options(spec,slot))
        pos=c['end'];kinds.append(c['kind'])
    assert pos==len(raw) and kinds[0]=='INITIAL' and kinds[-1]=='CONCLUSION'
    assert all(kinds.count(k)==1 for k in REQ)
    assert w['alias_domains']=={s:sorted(d) for s,d in sorted(observed.items())}
    assert w['aliases']=={s:sorted(d)[0] for s,d in sorted(observed.items())}

def main():
    for n,h in read(E/'PREREG_LOCK.json')['files'].items():assert hashlib.sha256((R/n).read_bytes()).hexdigest()==h,n
    cfg=read(E/'src/SPEC.json');g=read(R/cfg['grammar']);lex={x['raw']:x['symbol'] for x in read(R/cfg['source_draft'])['lexicon']};src=read(R/cfg['source_paragraphs']);rows=read(A/'ROWS.json');result=read(A/'RESULT.json');pred=read(A/'PREDICTIONS.json')
    old=read(R/cfg['old_cases']);variants={c['id']:c['variant'] for c in old if c['id'] in cfg['retained_variants']}
    checks=load(R/'experiments/yolo/gdt994_frozen_transport_whole_transfer/src/validate.py','independent994')
    replay=load(R/'experiments/yolo/gdt993_complete_transport_consequence_audit/src/validate.py','independent993')
    todo=[(ed,p) for ed,ps in src.items() for p in ps];assert len(todo)==len(rows)==len(pred)==1349
    sat_checks=[];cases_count=0
    for (ed,p),row,prediction in zip(todo,rows,pred):
        raw=[w for line in p['lines'] for w in line['words']];ids=[s for line in p['lines'] for s in line['source_ids']]
        part='ORIGINAL_PARAGRAPH' if p['id']=='f83r|f83r.18-f83r.24' else 'OTHER_SAME_LEAF' if p['leaf']==83 else 'OTHER_EXPOSED_LEAF'
        assert row['id']==ed+'|'+p['id'] and row['partition']==part and row['source_ids']==ids
        for k in ('page','leaf','groups'):assert row[k]==p[k]
        assert row['edition']==ed and row['paragraph']==p['id'] and row['groups']==len(raw)
        assert row['known_groups']==sum(w in lex for w in raw) and row['unknown_types']==sorted(set(raw)-lex.keys())
        assert row['strict_anchor_eligible']==all(line['anchor_eligible'] for line in p['lines']) and row['independent_meaning_capacity']==0
        assert prediction==dict(id=row['id'],partition=part,groups=len(raw),required_first=g['patterns']['INITIAL'],required_last=g['patterns']['CONCLUSION'],required_once=cfg['required'],known_values=[dict(position=i+1,raw=w,symbol=lex[w]) for i,w in enumerate(raw) if w in lex],unknown_types=row['unknown_types'],prediction='FULL_COVERAGE_SHARED_ALIAS_WITH_FIXED_GRAMMAR')
        expected=independent_endpoints(raw,lex,g);assert row['endpoints']==expected
        if not expected['pass_']:assert row['status']=='CONTRADICTED_ENDPOINT_SCOPE';continue
        feasible=backward(raw,lex,g);assert row['relaxed']['feasible']==feasible
        if not feasible:assert row['status']=='CONTRADICTED_RELAXED_FULL_GRAMMAR';continue
        shared=row['shared']
        if shared['status']=='UNKNOWN_SEARCH_LIMIT':assert row['status']=='UNKNOWN_SEARCH_LIMIT';continue
        answer=sat_shared(raw,lex,g,cfg['validator_solver_milliseconds']);sat_checks.append(dict(id=row['id'],z3=answer,runner=shared['status']))
        if shared['status']=='SHARED_UNSAT':assert answer=='unsat' and row['status']=='CONTRADICTED_SHARED_ALIAS';continue
        assert shared['status']=='SHARED_SAT' and answer=='sat';witness_check(raw,lex,g,shared)
        assert [c['variant_id'] for c in row['cases']]==list(variants);good=False
        for c in row['cases']:
            cases_count+=1;v=variants[c['variant_id']];assert c['variant']==v
            error=checks.binding_error(shared['parse'],v)
            if error:assert c['status']=='WITNESS_BINDING_CONTRADICTION' and c['error']==error and c['paths']==[];continue
            paths,hazards,refs=replay.replay(shared['parse'],v)
            named={s for clause in shared['parse'] for s in clause['symbols'] if s in ('W','G','C')}
            for path in paths:
                for state in [path,*path['trace']]:state['positions']={k:value for k,value in state['positions'].items() if k in named|{'M','B'}}
            assert paths==c['paths'] and hazards==c['program']['hazards'] and refs==c['program']['references']
            ok=any(x['consistent'] for x in paths);good|=ok
            assert c['status']==('COHERENT_WITNESS' if ok else 'WITNESS_SEMANTIC_CONTRADICTION')
        assert row['status']==('COHERENT_LOCAL_EXTENSION' if good else 'SYNTACTIC_EXTENSION_SEMANTICS_UNRESOLVED')
    assert result['paragraphs']==len(rows) and result['status_counts']==dict(collections.Counter(r['status'] for r in rows))
    for ed,ps in src.items():
        rs=[r for r in rows if r['edition']==ed];assert result['readers'][ed]==dict(paragraphs=len(ps),physical_leaves=len({r['leaf'] for r in rs}),counts=dict(collections.Counter(r['status'] for r in rs)))
    for part in ('ORIGINAL_PARAGRAPH','OTHER_SAME_LEAF','OTHER_EXPOSED_LEAF'):
        rs=[r for r in rows if r['partition']==part];assert result['partitions'][part]==dict(paragraphs=len(rs),physical_leaves=len({r['leaf'] for r in rs}),counts=dict(collections.Counter(r['status'] for r in rs)))
    coherent=[r['id'] for r in rows if r['partition']!='ORIGINAL_PARAGRAPH' and r['status']=='COHERENT_LOCAL_EXTENSION'];syntax=[r['id'] for r in rows if r['partition']!='ORIGINAL_PARAGRAPH' and r['status']=='SYNTACTIC_EXTENSION_SEMANTICS_UNRESOLVED'];unknown=[r['id'] for r in rows if r['status'].startswith('UNKNOWN')]
    assert result['additional_coherent_witnesses']==coherent and result['additional_syntactic_only']==syntax and result['unresolved']==unknown
    assert result['decision']==('RETAIN_COMPLETE_EXPOSED_EXTENSION' if coherent else 'RETAIN_UNRESOLVED_COMPLETION_CAPACITY' if syntax or unknown else 'NO_ADDITIONAL_FINITE_ALIAS_EXTENSION') and result['claims']==cfg['claims']
    with (A/'CANDIDATES.tsv').open() as f:table=list(csv.DictReader(f,delimiter='\t'))
    assert len(table)==len(rows)
    for t,r in zip(table,rows):
        expected={k:str(r[k]) for k in ('id','partition','groups','known_groups','strict_anchor_eligible','status','independent_meaning_capacity')};expected.update(unknown_types=str(len(r['unknown_types'])),endpoint_conflicts=str(len(r['endpoints']['conflicts'])),new_aliases=str(len(r.get('shared',{}).get('aliases',{}))),coherent_variants=str(sum(c['status']=='COHERENT_WITNESS' for c in r.get('cases',[]))));assert t==expected
    out=dict(status='PASS',completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),rows_checked=len(rows),semantic_cases_checked=cases_count,independent_finite_solver_checks=sat_checks,z3_version=z3.get_version_string(),scope='All source rows,predictions,endpoint conflicts,backward necessary grammar,shared witnesses/UNSAT,exact full replay,totals and TSV;same author;no independent meaning test',confirmed_words=0)
    (A/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()

#!/usr/bin/env python3
"""Exact finite shared morphology and global projection, with necessary lazy cuts."""
import argparse, gzip, hashlib, itertools, json, time
from collections import Counter, defaultdict
from pathlib import Path
from ortools.sat.python import cp_model
from role_source import CASES, compile_case

def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def save(path, value):
    path=Path(path); tmp=path.with_suffix(path.suffix+'.tmp')
    tmp.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');tmp.replace(path)

class ExactModel:
    def __init__(self, compiled, paragraphs, domains):
        self.source=compiled;self.paragraphs=paragraphs;self.atoms=compiled['atoms']
        self.words=sorted({w for p in paragraphs for w in p['words']}|{w for values in domains.values() for w in values});self.wid={w:i for i,w in enumerate(self.words)}
        self.model=cp_model.CpModel();m=self.model
        self.x={a:m.new_int_var_from_domain(cp_model.Domain.from_values([self.wid[w] for w in domains[a]]),'x_'+a) for a in self.atoms}
        m.add_all_different(list(self.x.values()))
        counters=[Counter(p['words']) for p in paragraphs]
        self.y=[];self.ydomains=[];self.expected=[];self.positions=[]
        for p in paragraphs:
            pos=defaultdict(list)
            for k,w in enumerate(p['words']):pos[self.wid[w]].append(k)
            self.positions.append(pos)
        self.stats={'count_allowed_rows':0,'count_forbidden_rows':0,'factorization_rows':0}
        for i,r in enumerate(compiled['records']):
            yd=[j for j,p in enumerate(paragraphs) if len(p['words'])>=len(r['sequence']) and p['words'][0] in domains[r['head_atom']]]
            self.ydomains.append(yd)
            if not yd:
                m.add_bool_or([]);yd=[0]
            y=m.new_int_var_from_domain(cp_model.Domain.from_values(yd),'y_'+str(i));self.y.append(y)
            m.add_allowed_assignments([y,self.x[r['head_atom']]],[(j,self.wid[paragraphs[j]['words'][0]]) for j in yd])
            counts=Counter(r['sequence'])
            for a in self.atoms:
                n=counts[a]
                rows=[(j,self.wid[w]) for j in yd for w in domains[a] if (counters[j][w]==n if n else counters[j][w]>0)]
                if n:
                    m.add_allowed_assignments([y,self.x[a]],rows);self.stats['count_allowed_rows']+=len(rows)
                elif rows:
                    m.add_forbidden_assignments([y,self.x[a]],rows);self.stats['count_forbidden_rows']+=len(rows)
            self.expected.append({(a,b):tuple(0 if c==a else 1 for c in r['sequence'] if c in (a,b)) for a,b in itertools.combinations(sorted(counts),2)})
        m.add_all_different(self.y)
        # Enumerate every literal factorization, including empty prefix/suffix.
        pieces={''};triples={}
        for a,f in compiled['forms'].items():
            if f['family'] is None:continue
            triples[a]=[]
            for w in domains[a]:
                for i in range(len(w)):
                    for j in range(i+1,len(w)+1):
                        t=(w[:i],w[i:j],w[j:]);pieces.update(t);triples[a].append((self.wid[w],*t))
        self.pieces=sorted(pieces);sid={s:i for i,s in enumerate(self.pieces)}
        possible=defaultdict(set)
        for a,rows in triples.items():
            f=compiled['forms'][a];rk=('root',f['family'],f['root']);pk=('prefix',f['roleclass']);sk=('suffix',f['roleclass'])
            for _,p,r,s in rows:
                possible[rk].add(sid[r]);possible[pk].add(sid[p]);possible[sk].add(sid[s])
        self.morph={k:m.new_int_var_from_domain(cp_model.Domain.from_values(sorted(v)),'/'.join(k)) for k,v in possible.items()}
        for a,rows in triples.items():
            f=compiled['forms'][a]
            vars_=[self.x[a],self.morph[('root',f['family'],f['root'])],self.morph[('prefix',f['roleclass'])],self.morph[('suffix',f['roleclass'])]]
            m.add_allowed_assignments(vars_,[(w,sid[r],sid[p],sid[s]) for w,p,r,s in rows]);self.stats['factorization_rows']+=len(rows)
        self.cuts=set();self.rounds=0

    def witness(self,solver):
        return {'lexicon':{a:self.words[solver.value(v)] for a,v in self.x.items()},
                'paragraph_indices':[solver.value(v) for v in self.y],
                'morphology':{'/'.join(k):self.pieces[solver.value(v)] for k,v in self.morph.items()}}

    def bad_pairs(self,witness):
        cuts=[];lex=witness['lexicon'];reverse={v:k for k,v in lex.items()}
        for i,j in enumerate(witness['paragraph_indices']):
            seq=[reverse[w] for w in self.paragraphs[j]['words'] if w in reverse]
            if seq==self.source['records'][i]['sequence']:continue
            found=False
            for (a,b),expected in self.expected[i].items():
                wa=self.wid[lex[a]];wb=self.wid[lex[b]]
                actual=tuple(v for _,v in sorted([(k,0) for k in self.positions[j][wa]]+[(k,1) for k in self.positions[j][wb]]))
                if actual!=expected:cuts.append((i,a,b,j,wa,wb));found=True
            assert found,'Counts plus all binary projections must determine the complete word'
        return cuts

    def query(self, deadline, workers=2, restriction=None):
        q=self.model.clone()
        if restriction is not None:
            var,value=restriction;q.add(q.get_int_var_from_proto_index(var.index)!=value)
        rounds=0
        while time.monotonic()<deadline:
            s=cp_model.CpSolver();s.parameters.max_time_in_seconds=max(.001,deadline-time.monotonic())
            s.parameters.num_search_workers=workers;s.parameters.random_seed=901
            status=s.solve(q);rounds+=1;self.rounds+=1
            if status==cp_model.INFEASIBLE:return {'status':'UNSAT','rounds':rounds}
            if status not in (cp_model.OPTIMAL,cp_model.FEASIBLE):
                return {'status':'UNKNOWN','solver_status':s.status_name(status),'rounds':rounds}
            witness=self.witness(s);cuts=self.bad_pairs(witness)
            if not cuts:
                replay(self.source,self.paragraphs,witness)
                return {'status':'SAT','witness':witness,'rounds':rounds}
            new=[c for c in cuts if c not in self.cuts];assert new,'Invalid candidate survived existing necessary cuts'
            for c in new:
                i,a,b,j,wa,wb=c;self.cuts.add(c)
                variables=[self.y[i],self.x[a],self.x[b]]
                self.model.add_forbidden_assignments(variables,[(j,wa,wb)])
                q.add_forbidden_assignments([q.get_int_var_from_proto_index(v.index) for v in variables],[(j,wa,wb)])
        return {'status':'UNKNOWN','solver_status':'SHARED_DEADLINE','rounds':rounds}

def replay(compiled,paragraphs,witness):
    lex=witness['lexicon'];indices=witness['paragraph_indices'];morph=witness['morphology']
    assert set(lex)==set(compiled['atoms']) and len(set(lex.values()))==len(lex)
    assert len(indices)==len(compiled['records']) and len(set(indices))==len(indices)
    rev={v:k for k,v in lex.items()}
    for r,j in zip(compiled['records'],indices):
        p=paragraphs[j];assert p['words'][0]==lex[r['head_atom']]
        assert [rev[w] for w in p['words'] if w in rev]==r['sequence']
    for a,f in compiled['forms'].items():
        if f['family'] is None:continue
        root=morph['root/'+f['family']+'/'+f['root']]
        assert root and morph['prefix/'+f['roleclass']]+root+morph['suffix/'+f['roleclass']]==lex[a]
    return True

def main():
    p=argparse.ArgumentParser();p.add_argument('--case-index',type=int,required=True);p.add_argument('--budget-seconds',type=float,default=1800)
    p.add_argument('--workers',type=int,default=2);p.add_argument('--output',required=True);args=p.parse_args()
    started=time.monotonic();deadline=started+args.budget_seconds;base=Path(__file__).resolve().parents[1]
    sp=base/'artifacts/SOURCE_INPUT.json';tp=base/'artifacts/TARGET_INPUT.json';mp=base/'artifacts/MODEL_SPEC.json';dp=base/'artifacts'/f'DOMAINS_IT2a_{args.case_index:02}.json.gz'
    assert digest(sp)=='0daf60d86d63ec371137378310871dd0f3bc0b7d16ac78770986b66647fe5d65'
    assert digest(tp)=='6244c721c3d48c88a8a855e1dea038a39d3f0b291493d333fa28f8458d9f3544'
    assert digest(mp)=='119be016d348b28d0915792bdb59a2c4f40496ed821be9c5fcddae2c2856b17a'
    assert digest(base/'src/role_source.py')==json.loads(mp.read_text())['role_compiler_sha256']
    assert digest(base/'artifacts/RESULT.json')=='ea29d822a71cc963e9efb145a5a54f3d06ca670407f17a623cbd65b920e65bed'
    gate=json.loads((base/'artifacts/RESULT.json').read_text())
    binding=next(r for r in gate['cases'] if r['panel']=='IT2a' and r['case']==args.case_index)
    assert binding['artifact']==dp.name and binding['artifact_sha256']==digest(dp)
    source=json.loads(sp.read_text());target=json.loads(tp.read_text());spec=json.loads(mp.read_text());assert spec['cases']==CASES
    compiled=compile_case(source,CASES[args.case_index]);domains=json.loads(gzip.decompress(dp.read_bytes()))['domains']
    out={'schema':'GDT901_EXACT_MORPHOLOGICAL_FIT_V1','case':args.case_index,'panel':'IT2a','source_sha256':digest(sp),'target_sha256':digest(tp),'model_spec_sha256':digest(mp),'domains_sha256':digest(dp),
         'code_sha256':digest(__file__),'budget_seconds':args.budget_seconds,'workers':args.workers,'projections':[]}
    model=ExactModel(compiled,target['panels']['IT2a'],domains);out['build_seconds']=time.monotonic()-started;out['model_stats']=model.stats
    first=model.query(deadline,args.workers);out['initial']=first;out['status']=first['status'];out['elapsed_seconds']=time.monotonic()-started;save(args.output,out)
    if first['status']=='SAT':
        w=first['witness'];queries=[('form',a,v,model.wid[w['lexicon'][a]]) for a,v in model.x.items()]
        queries += [('paragraph',str(i),v,w['paragraph_indices'][i]) for i,v in enumerate(model.y)]
        queries += [('morphology','/'.join(k),v,model.pieces.index(w['morphology']['/'.join(k)])) for k,v in model.morph.items()]
        for kind,key,var,value in queries:
            r=model.query(min(deadline,time.monotonic()+30),args.workers,(var,value)) if time.monotonic()<deadline else {'status':'UNKNOWN','solver_status':'SHARED_DEADLINE'}
            out['projections'].append({'kind':kind,'key':key,'result':r});out['elapsed_seconds']=time.monotonic()-started;save(args.output,out)
    out['cuts']=[list(c) for c in sorted(model.cuts)];out['total_rounds']=model.rounds;out['elapsed_seconds']=time.monotonic()-started
    out['claim_ceiling']='Within this fixed partition and source/compiler/head/background conjunction only; a witness or fixed surface value is not a confirmed meaning.'
    save(args.output,out);print(json.dumps({'case':args.case_index,'status':out['status'],'seconds':out['elapsed_seconds'],'cuts':len(model.cuts),'rounds':model.rounds}),flush=True)
if __name__=='__main__':main()

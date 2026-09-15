#!/usr/bin/env python3
"""Complete fixed source incidence; no character/affix decoder."""
from pathlib import Path
from collections import defaultdict,Counter
import csv,gzip,hashlib,json,math,re
import z3
P=Path(__file__).resolve().parents[1];R=P.parents[2];A=P/'artifacts'
BOUND={'DEFINITE_SPACE','LINE_START','LINE_END'}
def read(p):return json.loads(p.read_text())
def dump(name,obj):
    payload=json.dumps(obj,ensure_ascii=False,separators=(',',':'))+'\n'
    if name.endswith('.gz'):
        with gzip.GzipFile(filename=str(A/name),mode='wb',mtime=0) as f:f.write(payload.encode())
    else:(A/name).write_text(payload)
def tab(name,rows):
    with (A/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t');w.writeheader();w.writerows(rows)
def bits(indices):return sum(1<<(i-1) for i in indices)
def materialize():
    spec=read(P/'src/SPEC.json');allow=set(read(R/spec['allow_source'])['allowed_selectors'])
    assert len(allow)==179 and not any(x.startswith('f84') or x=='f116v' for x in allow)
    lines={}
    for rel in spec['sources']:
        src=read(R/rel)
        for line in src['lines']:
            md=line['metadata'];assert md['page'] in allow
            key=md['edition'],md['locus'];assert key not in lines
            lines[key]=[dict(md,**dict(zip(src['group_columns'],g))) for g in line['groups']]
    pars=read(R/spec['paragraph_source']);windows=[];denom={}
    for ed in spec['editions']:
        by=defaultdict(list)
        for p in pars.get(ed,[]):
            assert p['page'] in allow
            by[p['page']].append(p)
        n=0;gaps=0
        for page,ps in sorted(by.items()):
            ps.sort(key=lambda p:p['lines'][0]['row'])
            for start in range(len(ps)-14):
                chosen=ps[start:start+15]
                if not all(int(b['lines'][0]['locus'].rsplit('.',1)[1])==int(a['lines'][-1]['locus'].rsplit('.',1)[1])+1 for a,b in zip(chosen,chosen[1:])):gaps+=1;continue
                w={'window_id':ed+'|'+chosen[0]['id'],'edition':ed,'page':page,'physical_leaf':chosen[0]['leaf'],'paragraph_ids':[p['id'] for p in chosen],'paragraphs':[],'word_masks':{},'unknown_slots':[0]*15}
                for i,p in enumerate(chosen):
                    groups=[]
                    for ln in p['lines']:
                        gs=lines[ed,ln['locus']]
                        assert [g['ivtff_group_raw'] for g in gs]==ln['words']
                        assert [g['source_group_id'] for g in gs]==ln['source_ids']
                        groups.extend(gs)
                    assert len(groups)==p['groups']
                    annotated=[]
                    for g in groups:
                        reasons=[]
                        if not re.fullmatch('[a-z]+',g['ivtff_group_raw']):reasons.append('NONLITERAL')
                        if g['left_separator'] not in BOUND or g['right_separator'] not in BOUND:reasons.append('UNCERTAIN_BOUNDARY')
                        g=dict(g,known=not reasons,unknown_reasons=reasons)
                        annotated.append(g)
                        if reasons:w['unknown_slots'][i]+=1
                        else:w['word_masks'][g['ivtff_group_raw']]=w['word_masks'].get(g['ivtff_group_raw'],0)|(1<<i)
                    w['paragraphs'].append({'id':p['id'],'lines':[l['locus'] for l in p['lines']],'groups':annotated})
                w['word_masks']=dict(sorted(w['word_masks'].items()));windows.append(w);n+=1
        denom[ed]={'complete_paragraphs':len(pars.get(ed,[])),'windows':n,'gapped_windows':gaps,'capacity':'AVAILABLE' if n else 'NO_CAPACITY'}
    assert len(windows)==22
    return windows,denom

def evaluate(w,source_model,direction,incidence):
    required={plant:bits([16-i if direction=='REVERSED' else i for i in positions]) for plant,positions in incidence.items()}
    lower={plant:[word for word,mask in w['word_masks'].items() if mask==req] for plant,req in required.items()}
    classes=defaultdict(list)
    for plant,req in required.items():classes[req].append(plant)
    count=1
    for req,plants in classes.items():
        k=len(lower[plants[0]]);n=len(plants)
        count*=0 if k<n else math.factorial(k)//math.factorial(k-n)
    domains={};variables={};solver=z3.Solver();solver.set(timeout=5000);byword=defaultdict(list);costs=defaultdict(list)
    constraints=[]
    for pi,(plant,req) in enumerate(required.items()):
        ds=[]
        for word,mask in w['word_masks'].items():
            missing=req & ~mask
            if mask & ~req:continue
            if any((missing>>i)&1 and w['unknown_slots'][i]==0 for i in range(15)):continue
            ds.append({'word':word,'known_mask':mask,'missing_mask':missing,'fresh_unknown':False})
        if all(not ((req>>i)&1) or w['unknown_slots'][i]>0 for i in range(15)):
            ds.append({'word':'<UNKNOWN:'+plant+'>','known_mask':0,'missing_mask':req,'fresh_unknown':True})
        domains[plant]=ds;vs=[]
        for di,d in enumerate(ds):
            b=z3.Bool(f'p{pi}d{di}');variables[plant,di]=b;vs.append(b)
            if not d['fresh_unknown']:byword[d['word']].append(b)
            for i in range(15):
                if (d['missing_mask']>>i)&1:costs[i].append(b)
        constraints.append((f'plant_{pi}',z3.PbEq([(b,1) for b in vs],1) if vs else z3.BoolVal(False)))
    for wi,(word,vs) in enumerate(sorted(byword.items())):
        if len(vs)>1:constraints.append((f'injective_{wi}',z3.PbLe([(b,1) for b in vs],1)))
    for i,bs in costs.items():constraints.append((f'unknown_capacity_row_{i+1}',z3.PbLe([(b,1) for b in bs],w['unknown_slots'][i])))
    for tag,c in constraints:solver.assert_and_track(c,tag)
    checked=solver.check();upper=str(checked);witness={};marginals={};core=[]
    if checked==z3.sat:
        model=solver.model()
        for plant,ds in domains.items():
            witness[plant]=next(d['word'] for di,d in enumerate(ds) if z3.is_true(model.eval(variables[plant,di])))
        for plant,ds in domains.items():
            vals=[]
            for di,d in enumerate(ds):
                solver.push();solver.add(variables[plant,di]);s=solver.check();solver.pop()
                vals.append({'word':d['word'],'feasibility':str(s)})
            marginals[plant]=vals
    elif checked==z3.unsat:core=[str(t) for t in solver.unsat_core()]
    status='KNOWN_SUPPORT' if count else 'UNKNOWN_COMPLETION_ONLY' if upper=='sat' else 'CONTRADICTED' if upper=='unsat' else 'COMPUTATION_UNRESOLVED'
    assert not count or upper=='sat'
    return {'case_id':w['window_id']+'|'+source_model+'|'+direction,'window_id':w['window_id'],'edition':w['edition'],'page':w['page'],'physical_leaf':w['physical_leaf'],'paragraph_ids':w['paragraph_ids'],'source_model':source_model,'direction':direction,'status':status,'required_masks':required,'known_support_domains':lower,'known_support_assignment_count':str(count),'upper_domains':domains,'upper_solver_result':upper,'upper_assignment_count':'NOT_COUNTED','upper_witness':witness,'upper_feasible_marginals':marginals,'unsat_core':core,'constraint_tags':[t for t,c in constraints],'unknown_slots':w['unknown_slots'],'independent_confirmation_leaves':0}

def main():
    for rel,h in read(P/'PREREG_LOCK.json').items():assert hashlib.sha256((R/rel).read_bytes()).hexdigest()==h,rel
    windows,denom=materialize();source=read(P/'src/SOURCE.json');cases=[]
    dump('ALL_WINDOWS.json.gz',windows)
    for w in windows:
        for name,model in source['models'].items():
            for direction in ['ORIGINAL','REVERSED']:
                c=evaluate(w,name,direction,model['incidence']);cases.append(c)
    assert len(cases)==88
    dump('ALL_CASES.json.gz',cases)
    compact=[];domains=[]
    for c in cases:
        compact.append({k:c[k] for k in ['case_id','edition','page','physical_leaf','source_model','direction','status','known_support_assignment_count','upper_solver_result','independent_confirmation_leaves']}|{'unknown_slots':sum(c['unknown_slots']),'plants_with_empty_upper_domain':sum(not x for x in c['upper_domains'].values()),'unsat_core':';'.join(c['unsat_core'])})
        for plant,req in c['required_masks'].items():
            domains.append({'case_id':c['case_id'],'plant':plant,'required_rows':','.join(str(i+1) for i in range(15) if req>>i&1),'known_support_forms':' | '.join(c['known_support_domains'][plant]),'upper_domain_forms':' | '.join(d['word'] for d in c['upper_domains'][plant]),'feasible_upper_forms':' | '.join(v['word'] for v in c['upper_feasible_marginals'].get(plant,[]) if v['feasibility']=='sat'),'known_support_assignment_count':c['known_support_assignment_count'],'case_status':c['status']})
    tab('CANDIDATE_TABLE.tsv',compact);tab('PLANT_PREDICTION_TABLE.tsv',domains)
    tab('ALL_WINDOW_WORD_MASKS.tsv',[{'window_id':w['window_id'],'word':word,'observed_rows':','.join(str(i+1) for i in range(15) if mask>>i&1),'mask':mask} for w in windows for word,mask in w['word_masks'].items()])
    eq={}
    for name,model in source['models'].items():
        d=defaultdict(list)
        for plant,rs in model['incidence'].items():d[tuple(rs)].append(plant)
        eq[name]=[{'rows':list(rs),'indistinguishable_source_names':plants} for rs,plants in sorted(d.items())]
    dump('SOURCE_EQUIVALENCE_CLASSES.json',eq)
    support=[];ws={w['window_id']:w for w in windows}
    for c in cases:
        if c['upper_solver_result']!='sat':continue
        for plant,req in c['required_masks'].items():
            if req.bit_count()<2:continue
            ds=[v['word'] for v in c['upper_feasible_marginals'][plant] if v['feasibility']=='sat']
            real=[x for x in ds if not x.startswith('<UNKNOWN:')]
            maximum=max([ws[c['window_id']]['word_masks'][x].bit_count() for x in real] or [0])
            support.append({'case_id':c['case_id'],'plant':plant,'required_rows':req.bit_count(),'feasible_named_forms':len(real),'fresh_unknown_possible':len(real)<len(ds),'maximum_known_required_rows':maximum,'minimum_rows_requiring_unknown':req.bit_count()-maximum,'unique_named_form':real[0] if len(real)==1 and len(ds)==1 else ''})
    if support:tab('REPEATED_PLANT_OBSERVED_SUPPORT.tsv',support)
    result={'experiment_id':'GDT960','status':'COMPLETE_FIXED_PLANT_INCIDENCE_SCREEN','windows':denom,'case_count':len(cases),'source_plant_models':{n:{'plant_identities':m['plant_identities'],'plant_row_mentions':m['plant_row_mentions']} for n,m in source['models'].items()},'outcomes':dict(Counter(c['status'] for c in cases)),'outcomes_by_edition':{ed:dict(Counter(c['status'] for c in cases if c['edition']==ed)) for ed in denom},'physical_leaves':sorted({w['physical_leaf'] for w in windows}),'confirmed_words':0,'independent_confirmation_leaves_per_candidate':0,'no_reserved_data_opened':True,'significance':'NOT_ASSESSED_NO_SEARCH_CONTROL'}
    dump('RESULT.json',result);print(json.dumps(result,indent=2))
if __name__=='__main__':main()

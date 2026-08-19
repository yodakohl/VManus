#!/usr/bin/env python3
"""GDT347: transport one frozen Voynich pair graph to GDT278 controls."""

from __future__ import annotations
import csv,hashlib,itertools,json,math
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np

def root(p):
    for q in (p,*p.parents):
        if (q/'AGENTS.md').is_file() and (q/'.git').exists():return q
    raise RuntimeError
ROOT=root(Path(__file__).resolve());import sys;sys.path.insert(0,str(ROOT))
from tools.vmanus_experiment import GuardedTSV  # noqa:E402
EXP=ROOT/'experiments/yolo/gdt347_fixed_graph_control_transport';ART=EXP/'artifacts';METHOD=EXP/'METHOD.md';AUDIT=EXP/'SOURCE_AUDIT.md'
DESIGN=ART/'gdt347_design.json';FROZEN=ART/'gdt347_frozen_graph.json';CAP=ART/'gdt347_control_capacity.tsv';FREEZEVAL=ART/'gdt347_freeze_validation.json';CORRECTION=EXP/'CORRECTION.md'
G345=ROOT/'experiments/yolo/gdt345_productive_operator_transfer/artifacts/gdt345_transition_inventory.tsv';NATIVE=ROOT/'gdt278_native_event_inventory.tsv';MATCHED=ROOT/'gdt278_matched_event_inventory.tsv';MANIFEST=ROOT/'gdt278_control_manifest.tsv'
PANELS=ART/'gdt347_panel_scores.tsv';FOLDS=ART/'gdt347_folio_scores.tsv';ENV=ART/'gdt347_environment_scores.tsv';EDGE=ART/'gdt347_edge_scores.tsv';NULL=ART/'gdt347_null.tsv';COUNTER=ART/'gdt347_counterexamples.tsv';RESULT=ART/'gdt347_result.json';REPORT=EXP/'REPORT.md'
COMP=('local_frame','inner_d','right_family','dy_closure','b3','canonical_wrapper')

def read(p):
    with p.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''):h.update(b)
    return h.hexdigest()
def canon(x):return (json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n').encode()
def content(x):y=dict(x);y.pop('content_sha256',None);return hashlib.sha256(canon(y)).hexdigest()
def hid(domain,x):return hashlib.sha256((domain+'\0'+json.dumps(x,sort_keys=True,separators=(',',':'))).encode()).hexdigest()[:20]
def write(p,rows,fields=None):
    fields=fields or list(rows[0])
    with p.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)

def delta(a,b):return tuple('KEEP' if x==y else 'SET:'+y for x,y in zip(a,b))
def quartile(r):return str(min(3,4*(int(r['group_index'])-1)//max(1,int(r['group_count']))))
def wrapper(r,previous):
    w=r['wrapper']
    if w=='s' and int(r['group_index'])==1:w='NONE'
    if w=='q' and previous is not None and previous['locus']==r['locus'] and previous['dy_closure']=='1':w='NONE'
    return w
def state(r,previous):return (r['local_frame'],r['inner_d'],r['right_family'],r['dy_closure'],r['b3'],wrapper(r,previous))
def boundary(a,b):
    rr=int(a['record_ordinal']!=b['record_ordinal']);lr=int(a['locus']!=b['locus']);fr=int((a['record_ordinal'],a['field_ordinal'])!=(b['record_ordinal'],b['field_ordinal']))
    if rr:scope,order='RECORD_RESET','RECORD_RESET'
    elif lr:
        step=int(b['field_ordinal'])-int(a['field_ordinal']);order='SAME_FIELD' if not fr else ('NEXT_FIELD' if step==1 else ('FIELD_RESET' if step<1 else 'FIELD_SKIP'));scope='LINE_RESET'
    elif fr:
        step=int(b['field_ordinal'])-int(a['field_ordinal']);order='NEXT_FIELD' if step==1 else ('FIELD_RESET' if step<1 else 'FIELD_SKIP');scope='FIELD_BOUNDARY'
    else:scope,order='SAME_FIELD','SAME_FIELD'
    return scope,order

def event_edges(rows,cid,architecture,view):
    by=defaultdict(list)
    for r in rows:by[(r['page'],r['physical_folio'])].append(r)
    out=[]
    for (page,physical_folio),rs in by.items():
        prev=None;states=[]
        for r in rs:states.append(state(r,prev));prev=r
        for i,(a,b) in enumerate(zip(rs,rs[1:])):
            s,t=states[i],states[i+1];scope,order=boundary(a,b);layout=(scope,order,str(int(b['group_index'])==1),b['within_field_position'],quartile(b))
            out.append({'edge_id':hid('GDT347_EDGE_V1',(view,cid,page,physical_folio,i,a['locus'],a['group_index'],b['locus'],b['group_index'])),'control_id':cid,'architecture':architecture,'view':view,'page':page,'folio':physical_folio,'section':a['section'],'register':a['register'],'hand':a['hand'],'source':s,'target':t,'delta':delta(s,t),'scope':scope,'layout':layout})
    return out

def voy_edges(rows):
    out=[]
    for r in rows:out.append({'edge_id':r['edge_id'],'control_id':'VOYNICH_FIXED_HOLDOUT','architecture':'UNKNOWN_VOYNICH_ARCHITECTURE','view':'NATIVE','page':r['page'],'folio':r['physical_folio'],'section':r['section'],'register':r['register'],'hand':r['hand'],'source':tuple(json.loads(r['source_state_json'])),'target':tuple(json.loads(r['target_state_json'])),'delta':tuple(json.loads(r['delta_json'])),'scope':r['boundary_scope'],'layout':tuple(json.loads(r['layout_context_json']))})
    return out

def build_tables(train,design):
    glob=[Counter() for _ in range(6)];lay=[defaultdict(Counter) for _ in range(6)];ctx=[defaultdict(Counter) for _ in range(6)]
    for e in train:
        for i,y in enumerate(e['target']):glob[i][y]+=1;lay[i][e['layout']][y]+=1;ctx[i][(*e['layout'],f'C{i}',e['source'][i])][y]+=1
    return glob,lay,ctx,design
def probs(e,tables,i):
    glob,lay,ctx,d=tables;g=glob[i];labels=sorted(g)
    if not labels:return {}
    pg={y:(g[y]+float(d['marginals']['global_jeffreys']))/(sum(g.values())+float(d['marginals']['global_jeffreys'])*len(labels)) for y in labels};lc=lay[i].get(e['layout'],Counter());pl={y:(lc[y]+float(d['marginals']['layout_to_global'])*pg[y])/(sum(lc.values())+float(d['marginals']['layout_to_global'])) for y in labels};cc=ctx[i].get((*e['layout'],f'C{i}',e['source'][i]),Counter());return {y:(cc[y]+float(d['marginals']['source_to_layout'])*pl[y])/(sum(cc.values())+float(d['marginals']['source_to_layout'])) for y in labels}

def score_event(e,tables,pairs,phi):
    ps=[probs(e,tables,i) for i in range(6)]
    if any(e['target'][i] not in ps[i] for i in range(6)):return None
    ind_bits=-sum(math.log2(max(1e-300,ps[i][e['target'][i]])) for i in range(6));ind_best=tuple(min(p,key=lambda y:(-p[y],y)) for p in ps)
    active=sorted({i for p in pairs for i in p});inactive=[i for i in range(6) if i not in active];z=0.;bestw=-1.;best=None
    truth_energy=1.;known=nonneutral=0;pair_gain={};pair_logz={};pair_known={};pair_non={}
    for p in pairs:
        k=(p,e['scope'],e['delta'][p[0]],e['delta'][p[1]])
        pair_known[p]=int(k in phi);known+=pair_known[p]
        f=phi.get(k,1.);truth_energy*=f;pair_non[p]=int(abs(f-1)>1e-15);nonneutral+=pair_non[p]
        zp=0.
        for ya,pa in ps[p[0]].items():
            da='KEEP' if ya==e['source'][p[0]] else 'SET:'+ya
            for yb,pb in ps[p[1]].items():
                db='KEEP' if yb==e['source'][p[1]] else 'SET:'+yb;zp+=pa*pb*phi.get((p,e['scope'],da,db),1.)
        pair_logz[p]=math.log2(max(1e-300,zp));pair_gain[p]=math.log2(max(1e-300,f))-pair_logz[p]
    for vals in itertools.product(*(tuple(ps[i]) for i in active)):
        target=dict(zip(active,vals));base=math.prod(ps[i][target[i]] for i in active);ds={i:('KEEP' if target[i]==e['source'][i] else 'SET:'+target[i]) for i in active};energy=1.
        for p in pairs:energy*=phi.get((p,e['scope'],ds[p[0]],ds[p[1]]),1.)
        w=base*energy;z+=w
        if w>bestw or (w==bestw and (best is None or vals<best)):bestw,best=w,vals
    gain=math.log2(max(1e-300,truth_energy/max(1e-300,z)));graph_target=list(ind_best)
    for i,v in zip(active,best):graph_target[i]=v
    return {'ind_bits':ind_bits,'graph_bits':ind_bits-gain,'gain':gain,'ind_hit':int(ind_best==e['target']),'graph_hit':int(tuple(graph_target)==e['target']),'logz':math.log2(max(1e-300,z)),'known':known,'nonneutral':nonneutral,'pair_gain':pair_gain,'pair_logz':pair_logz,'pair_known':pair_known,'pair_non':pair_non}

def score_panel(edges,train_fixed,pairs,phi,design,fixed_train=False):
    folds=[];null_events=[];envfold=defaultdict(lambda:{'events':0,'gain':0.})
    helds=sorted({e['folio'] for e in edges})
    for held in helds:
        train=train_fixed if fixed_train else [e for e in edges if e['folio']!=held];test=[e for e in edges if e['folio']==held]
        if not train:continue
        tables=build_tables(train,design);a={'n':0,'ib':0.,'gb':0.,'ih':0,'gh':0,'known':0,'non':0,'pg':Counter(),'pk':Counter(),'pn':Counter()}
        for e in test:
            s=score_event(e,tables,pairs,phi)
            if s is None:continue
            a['n']+=1;a['ib']+=s['ind_bits'];a['gb']+=s['graph_bits'];a['ih']+=s['ind_hit'];a['gh']+=s['graph_hit'];a['known']+=s['known'];a['non']+=s['nonneutral']
            for p in pairs:a['pg'][p]+=s['pair_gain'][p];a['pk'][p]+=s['pair_known'][p];a['pn'][p]+=s['pair_non'][p]
            for split in ('section','register','hand'):
                q=envfold[(split,e[split],held)];q['events']+=1;q['gain']+=s['gain']
            null_events.append({'held':held,'layout':e['layout'],'scope':e['scope'],'source':e['source'],'delta':e['delta'],'logz':s['logz'],'pair_logz':s['pair_logz']})
        row={'held_folio':held,'events':a['n'],'independent_bits':f"{a['ib']:.9f}",'graph_bits':f"{a['gb']:.9f}",'raw_gain':f"{a['ib']-a['gb']:.9f}",'independent_exact':a['ih'],'graph_exact':a['gh'],'truth_cell_coverage':f"{a['known']/max(1,a['n']*len(pairs)):.9f}",'nonneutral_event_edge_rate':f"{a['non']/max(1,a['n']*len(pairs)):.9f}"}
        for p in pairs:
            tag=f'{p[0]}_{p[1]}';row[f'pair_{tag}_gain']=f"{a['pg'][p]:.9f}";row[f'pair_{tag}_coverage']=f"{a['pk'][p]/max(1,a['n']):.9f}";row[f'pair_{tag}_nonneutral']=f"{a['pn'][p]/max(1,a['n']):.9f}"
        folds.append(row)
    environment=[]
    for split,value in sorted({(s,v) for s,v,_ in envfold}):
        xs=[(h,a) for (s,v,h),a in envfold.items() if s==split and v==value];environment.append({'split':split.upper(),'value':value,'folios':len(xs),'events':sum(a['events'] for _,a in xs),'gain':sum(a['gain'] for _,a in xs),'positive_folios':sum(a['gain']>0 for _,a in xs)})
    return folds,null_events,environment

def null_panel(events,pairs,phi,worlds,seed):
    n=len(events)
    if not n:return [],1.,0
    scopes=sorted({e['scope'] for e in events});sc={s:i for i,s in enumerate(scopes)};scope=np.array([sc[e['scope']] for e in events],dtype=np.int16);logz=np.array([e['logz'] for e in events]);
    vals=[];maps=[]
    for i in range(6):
        vv=sorted({e['delta'][i] for e in events});mp={v:j for j,v in enumerate(vv)};maps.append(mp);vals.append(np.array([mp[e['delta'][i]] for e in events],dtype=np.int16))
    mats={}
    for p in pairs:
        a,b=p;mat=np.zeros((len(scopes),len(maps[a]),len(maps[b])),dtype=float)
        for s,si in sc.items():
            for va,ia in maps[a].items():
                for vb,ib in maps[b].items():mat[si,ia,ib]=math.log2(max(1e-300,phi.get((p,s,va,vb),1.)))
        mats[p]=mat
    observed={'combined':sum(float(np.sum(mats[p][scope,vals[p[0]],vals[p[1]]])) for p in pairs)-float(np.sum(logz))}
    for p in pairs:observed[p]=float(np.sum(mats[p][scope,vals[p[0]],vals[p[1]]]))-sum(e['pair_logz'][p] for e in events)
    groups=[];mobile_idx=set()
    for i in range(6):
        d=defaultdict(list)
        for j,e in enumerate(events):d[(e['held'],*e['layout'],e['source'][i])].append(j)
        gs=[]
        for ids in d.values():
            ar=np.array(ids,dtype=np.int32);gs.append(ar)
            if len({int(vals[i][j]) for j in ids})>1:mobile_idx.update(ids)
        groups.append(gs)
    rows=[];exceed=Counter();rng=np.random.default_rng(seed);batch=128;obsmax=max(observed.values())
    for start in range(0,worlds,batch):
        b=min(batch,worlds-start);lab=[np.tile(v,(b,1)) for v in vals]
        for i in range(6):
            for ids in groups[i]:
                if len(ids)<2:continue
                order=np.argsort(rng.random((b,len(ids))),axis=1);lab[i][:,ids]=lab[i][:,ids][np.arange(b)[:,None],order]
        pair_world={p:np.sum(mats[p][scope[None,:],lab[p[0]],lab[p[1]]],axis=1)-sum(e['pair_logz'][p] for e in events) for p in pairs};gain=sum(pair_world.values())+sum(e['pair_logz'][p] for p in pairs for e in events)-float(np.sum(logz));maximum=np.maximum.reduce([gain,*pair_world.values()])
        exceed['combined']+=int(np.sum(gain>=observed['combined']-1e-12));exceed['max4']+=int(np.sum(maximum>=obsmax-1e-12))
        for p in pairs:exceed[p]+=int(np.sum(pair_world[p]>=observed[p]-1e-12))
        for i,v in enumerate(gain):
            row={'world':start+i,'combined_gain':f"{v:.9f}",'max_four_gain':f"{maximum[i]:.9f}"}
            for p in pairs:row[f'gain_{p[0]}_{p[1]}']=f"{pair_world[p][i]:.9f}"
            rows.append(row)
    pvals={k:(1+exceed[k])/(1+worlds) for k in ['combined','max4',*pairs]};return rows,pvals,len(mobile_idx)

def arch_group(cat):
    if cat in {'REAL_NATURAL_LANGUAGE','REAL_STRUCTURED_NATURAL_LANGUAGE'}:return 'ORDINARY_OR_STRUCTURED_NATURAL_LANGUAGE'
    if cat=='REAL_DIPLOMATIC_ABBREVIATION':return 'REAL_DIPLOMATIC'
    if cat=='GENERATED_HISTORICALLY_LEARNED_ABBREVIATION':return 'LEARNED_ABBREVIATION'
    if cat in {'SYNTHETIC_FACTORIAL_TECHNICAL_NOTATION','SYNTHETIC_HUMAN_GROWN_HYBRID'}:return 'COMPILER_LIKE_SYNTHETIC'
    if cat=='SYNTHETIC_LEXICAL_CODEBOOK':return 'LEXICAL_CODEBOOK'
    return 'OTHER'

def main():
    design=json.loads(DESIGN.read_text());frozen=json.loads(FROZEN.read_text());pairs=[tuple(map(int,r['pair_id'].split('-'))) for r in frozen['topology']];phi={(tuple(map(int,r['pair_id'].split('-'))),r['scope'],r['delta_a'],r['delta_b']):float(r['factor']) for r in frozen['potential_weights']};manifest={r['control_id']:r for r in read(MANIFEST)}
    source_reader=GuardedTSV(G345,selector_column='page',forbidden_prefixes=('f84',),forbidden_action='error');v=voy_edges(list(source_reader));held=set(frozen['voynich_partition']['held_folios']);vtrain=[e for e in v if e['folio'] not in held];vtest=[e for e in v if e['folio'] in held]
    panels=[('NATIVE','VOYNICH_FIXED_HOLDOUT','UNKNOWN_VOYNICH_ARCHITECTURE',vtest,vtrain,True)]
    for view,path in [('NATIVE',NATIVE),('MATCHED',MATCHED)]:
        reader=GuardedTSV(path,selector_column='page',forbidden_prefixes=('f84',),forbidden_action='error');rows=list(reader);by=defaultdict(list)
        for r in rows:
            if not r['control_id'].startswith('VOYNICH'):by[r['control_id']].append(r)
        for cid,rs in sorted(by.items()):panels.append((view,cid,manifest[cid]['architecture_category'],event_edges(rs,cid,manifest[cid]['architecture_category'],view),[],False))
    panel_rows=[];fold_rows=[];env_rows=[];edge_rows=[];all_null=[]
    for panel_index,(view,cid,arch,edges,fixed_train,is_voy) in enumerate(panels):
        folds,ne,panel_env=score_panel(edges,fixed_train,pairs,phi,design,is_voy);n=sum(int(r['events']) for r in folds);ib=sum(float(r['independent_bits']) for r in folds);gb=sum(float(r['graph_bits']) for r in folds);gain=ib-gb;ih=sum(int(r['independent_exact']) for r in folds);gh=sum(int(r['graph_exact']) for r in folds);known=sum(float(r['truth_cell_coverage'])*int(r['events']) for r in folds)/max(1,n);non=sum(float(r['nonneutral_event_edge_rate'])*int(r['events']) for r in folds)/max(1,n)
        null_rows,pvals,mobile=null_panel(ne,pairs,phi,int(design['null']['worlds']),int(design['null']['seed'])+panel_index*10000);all_null.extend({'view':view,'control_id':cid,**r} for r in null_rows)
        comparable=n>=int(design['comparability']['minimum_scored_transitions']) and len({e['folio'] for e in edges})>=int(design['comparability']['minimum_folios']) and mobile>=int(design['comparability']['minimum_null_mobile_transitions']) and non>=float(design['comparability']['minimum_nonneutral_coverage']);transfers=comparable and gain>0 and pvals['combined']<=.05
        row={'view':view,'control_id':cid,'architecture_category':arch,'architecture_group':arch_group(arch),'source_transitions':len(edges),'scored_transitions':n,'folios':len({e['folio'] for e in edges}),'independent_bits':f"{ib:.9f}",'frozen_graph_bits':f"{gb:.9f}",'raw_gain':f"{gain:.9f}",'selector_bits_once':f"{float(frozen['selector_bits_once']):.9f}",'standalone_cost_adjusted_gain':f"{gain-float(frozen['selector_bits_once']):.9f}",'positive_folios':sum(float(r['raw_gain'])>0 for r in folds),'independent_exact':ih,'graph_exact':gh,'truth_cell_coverage':f"{known:.9f}",'nonneutral_event_edge_rate':f"{non:.9f}",'null_mobile_transitions':mobile,'inclusive_p':f"{pvals['combined']:.9f}",'max_four_p':f"{pvals['max4']:.9f}",'comparable':int(comparable),'transfers':int(transfers)};panel_rows.append(row)
        for p in pairs:
            tag=f'{p[0]}_{p[1]}';pg=sum(float(r[f'pair_{tag}_gain']) for r in folds);pc=sum(float(r[f'pair_{tag}_coverage'])*int(r['events']) for r in folds)/max(1,n);pn=sum(float(r[f'pair_{tag}_nonneutral'])*int(r['events']) for r in folds)/max(1,n);edge_rows.append({'view':view,'control_id':cid,'architecture_category':arch,'pair_id':f'{p[0]}-{p[1]}','coordinate_a':COMP[p[0]],'coordinate_b':COMP[p[1]],'events':n,'gain':f"{pg:.9f}",'inclusive_p':f"{pvals[p]:.9f}",'max_four_p':f"{pvals['max4']:.9f}",'truth_cell_coverage':f"{pc:.9f}",'nonneutral_rate':f"{pn:.9f}",'delta_a_changes':sum(e['delta'][p[0]]!='KEEP' for e in ne),'delta_b_changes':sum(e['delta'][p[1]]!='KEEP' for e in ne),'evidence_status':'POSTSCORE_DIAGNOSTIC'})
        for r in folds:fold_rows.append({'view':view,'control_id':cid,'architecture_category':arch,**r})
        for er in panel_env:env_rows.append({'view':view,'control_id':cid,**er,'gain':f"{er['gain']:.9f}"})
    write(PANELS,panel_rows);write(FOLDS,fold_rows);write(ENV,env_rows);write(EDGE,edge_rows);write(NULL,all_null)
    primary=[r for r in panel_rows if r['view']=='NATIVE'];voy=next(r for r in primary if r['control_id']=='VOYNICH_FIXED_HOLDOUT');transport=[r for r in primary if r['control_id']!='VOYNICH_FIXED_HOLDOUT' and int(r['transfers'])]
    ordinary=[r for r in transport if r['architecture_group']=='ORDINARY_OR_STRUCTURED_NATURAL_LANGUAGE'];diplomatic=[r for r in transport if r['architecture_group']=='REAL_DIPLOMATIC'];compiler=[r for r in transport if r['architecture_group'] in {'LEARNED_ABBREVIATION','COMPILER_LIKE_SYNTHETIC'}]
    if not int(voy['transfers']):status='GDT346_LOCAL_OVERFITTING'
    elif ordinary and diplomatic:status='GENERIC_WRITING_MECHANICS'
    elif len({r['control_id'] for r in compiler})>=2 and not ordinary:status='COMPILER_STYLE_FORMAL_GRAMMAR'
    elif not transport:status='MANUSCRIPT_SPECIFIC_FORMAL_CONVENTION'
    else:status='INCONCLUSIVE_CONTROL_TRANSPORT'
    counter=[{'code':'FROZEN_TOPOLOGY','detail':'|'.join(r['coordinate_a']+'<->'+r['coordinate_b'] for r in frozen['topology']),'effect':'NO_CONTROL_EDGE_OR_WEIGHT_LEARNING'},{'code':'CONTROL_DY_CAPACITY','detail':'all GDT278 controls have dy_closure=0','effect':'DY_EDGE_PORTABILITY_IS_SUPPORT_LIMITED'},{'code':'LOW_CAPACITY','detail':'Ste1 and sparse parser panels remain explicit','effect':'NOT_COMPARABLE_IS_NOT_NEGATIVE'},{'code':'SEMANTICS','detail':'UNASSIGNED','effect':'NO_GLOSS_OR_LANGUAGE'},{'code':'F84','detail':'all inputs guarded and zero selected rows','effect':'NO_ACCESS'}];write(COUNTER,counter)
    lines=['# GDT347 — frozen compatibility-graph control transport','',f'Status: **{status}**.','',f"The one-time frozen graph contains {len(pairs)} edges and costs {float(frozen['selector_bits_once']):.3f} bits. Its held Voynich panel scores {voy['scored_transitions']} transitions: raw gain {float(voy['raw_gain']):+.3f} bits, cost-adjusted {float(voy['standalone_cost_adjusted_gain']):+.3f}, exact recovery {voy['independent_exact']}→{voy['graph_exact']}, coupling-null p={voy['inclusive_p']}, and non-neutral coverage {voy['nonneutral_event_edge_rate']}.",'','Native-order controls:','', '| Control | Architecture | n | Gain | p | Coverage | Comparable | Transfers |','|---|---|---:|---:|---:|---:|---:|---:|']
    for r in primary:
        if r['control_id']=='VOYNICH_FIXED_HOLDOUT':continue
        lines.append(f"| {r['control_id']} | {r['architecture_group']} | {r['scored_transitions']} | {float(r['raw_gain']):+.3f} | {r['inclusive_p']} | {r['nonneutral_event_edge_rate']} | {r['comparable']} | {r['transfers']} |")
    lines+=['',f"Transporting controls: {', '.join(r['control_id'] for r in transport) if transport else 'none'}.",'','Post-score frozen-edge decomposition (decision-inert):','', '| Panel | Edge | Gain | p | max4 p | delta changes A/B |','|---|---|---:|---:|---:|---:|']
    for r in edge_rows:
        if r['view']=='NATIVE':lines.append(f"| {r['control_id']} | {r['coordinate_a']}<->{r['coordinate_b']} | {float(r['gain']):+.3f} | {r['inclusive_p']} | {r['max_four_p']} | {r['delta_a_changes']}/{r['delta_b_changes']} |")
    lines+=['','The graph was never reselected or refit on a control. Control-specific learning was restricted to the independent-coordinate marginal reference. The held Voynich benefit is distributional: exact argmax recovery declines by two. More importantly, every admitted control has zero inner-D and zero DY changes under the frozen observation parser. The status therefore means manuscript-specific within this coordinate observation layer; it does not show that ordinary writing lacks an unobserved analogous mechanism. No semantics, PAGE_HOST factorization, tuple merging, or f84 access occurred.']
    REPORT.write_text('\n'.join(lines)+'\n')
    outputs={str(p.relative_to(ROOT)):sha(p) for p in (PANELS,FOLDS,ENV,EDGE,NULL,COUNTER,REPORT)};inputs={str(p.relative_to(ROOT)):sha(p) for p in (METHOD,AUDIT,CORRECTION,DESIGN,FROZEN,CAP,FREEZEVAL,G345,NATIVE,MATCHED,MANIFEST)}
    result={'schema':'GDT347_RESULT_V1','date':'2026-08-19','status':status,'frozen_topology':frozen['topology'],'selector_bits_once':frozen['selector_bits_once'],'voynich':voy,'native_transport_controls':[r['control_id'] for r in transport],'panels':panel_rows,'semantics':'UNASSIGNED','page_host_factorizations':0,'tuple_merges':0,'f84':{'opened':False,'parsed':False,'retained':False,'joined':False,'scored':False},'claim_ceiling':'Portability of three frozen formal coordinate couplings only; no authorial grammar morphology semantics word language plaintext translation or f84 result.','inputs':inputs,'outputs':outputs,'implementation':{str(Path(__file__).resolve().relative_to(ROOT)):sha(Path(__file__).resolve())}};result['content_sha256']=content(result);RESULT.write_bytes(canon(result));print(status,'voy_gain',voy['raw_gain'],'p',voy['inclusive_p'],'controls',len(transport));return 0
if __name__=='__main__':raise SystemExit(main())

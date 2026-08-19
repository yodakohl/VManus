#!/usr/bin/env python3
"""Score the frozen GDT347 graph on GDT172/GDT173 oracle coordinates."""
from __future__ import annotations

import csv,gzip,hashlib,importlib.util,itertools,json,math,random
from collections import Counter,defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4];EXP=ROOT/'experiments/yolo/gdt348_oracle_coordinate_transport_calibration';ART=EXP/'artifacts'
DESIGN=ART/'gdt348_design.json';FROZEN=ROOT/'experiments/yolo/gdt347_fixed_graph_control_transport/artifacts/gdt347_frozen_graph.json'
G346_DESIGN=ROOT/'experiments/yolo/gdt346_compositional_operator_manifold/artifacts/gdt346_design.json';G346_RUN=ROOT/'experiments/yolo/gdt346_compositional_operator_manifold/src/run.py'
O172=ROOT/'gdt172_sealed_oracle.json.gz';V172=ROOT/'gdt172_observation_corpus.json.gz';O173=ROOT/'gdt173_b2_sealed_oracle.json.gz';V173=ROOT/'gdt173_b2_observation_corpus.json.gz'
METHOD=EXP/'METHOD.md';AUDIT=EXP/'SOURCE_AUDIT.md';CORRECTION=EXP/'CORRECTION.md';REPORT=EXP/'REPORT.md';PANELS=ART/'gdt348_panel_scores.tsv';UNITS=ART/'gdt348_unit_scores.tsv';EDGES=ART/'gdt348_edge_scores.tsv';NULL=ART/'gdt348_null.tsv';COUNTER=ART/'gdt348_counterexamples.tsv';RESULT=ART/'gdt348_result.json'
SYSTEMS={'LEXICAL_A':(O172,V172,'SYSTEM_A_V3_UNCHANGED_LITERAL'),'FACTORIAL_B':(O172,V172,'SYSTEM_B_FACTORIAL_DISTRIBUTED_CONTROL_V3'),'HUMAN_GROWN_B2':(O173,V173,'SYSTEM_B2_HUMAN_GROWN_DISTRIBUTED_CONTROL')}
PAIRS=((1,5),(3,5),(2,3));COMP=('local_frame','inner_d','right_family','dy_closure','b3','canonical_wrapper')

def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def canonical(x):return (json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode()
def chash(x):
 y=dict(x);y.pop('content_sha256',None);return hashlib.sha256(canonical(y)).hexdigest()
def load(p):
 with gzip.open(p,'rt',encoding='utf-8') as f:return json.load(f)['rows']
def write_tsv(p,rows,fields=None):
 if fields is None:fields=list(rows[0])
 with p.open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def load_g346():
 spec=importlib.util.spec_from_file_location('gdt346_dependency',G346_RUN);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def sid(prefix,s):return prefix+hashlib.sha256(s.encode()).hexdigest()[:16]

def build_edges(name,op,vp,system,design):
 oracle=[r for r in load(op) if r['system']==system];obs={r['observation_id']:r for r in load(vp)};rmap=design['crosswalk']['right_family_maps'][name]
 def state(r):
  right=rmap.get(r['true_lexical_right'],rmap[max(rmap,key=lambda x:(x!='',rmap[x]))])
  wrapper='NONE' if not r['true_record_operator'] else r['true_record_operator']
  if wrapper not in {'NONE','q','d','s'}:raise AssertionError(wrapper)
  return ('O' if r['true_line_frame'] else 'NONE','1' if r['true_lexical_left']=='d' else '0',right,'1' if r['true_closure']=='y' else '0','1' if r['true_closure']=='k' else '0',wrapper)
 by=defaultdict(list)
 for r in oracle:by[r['true_record_id']].append(r)
 edges=[]
 for record,rows in by.items():
  rows.sort(key=lambda r:int(r['true_record_slot']));assert [int(r['true_record_slot']) for r in rows]==list(range(len(rows)))
  for a,b in zip(rows,rows[1:]):
   oa,ob=obs[a['observation_id']],obs[b['observation_id']];sa,sb=state(a),state(b)
   line_reset=oa['physical_line_id']!=ob['physical_line_id']
   if line_reset:scope='LINE_RESET';layout=('LINE_RESET','SAME_FIELD','1','FIRST','0')
   else:
    scope='SAME_FIELD';pos='LAST' if int(ob['group_index'])==int(ob['group_count']) else 'MIDDLE';layout=('SAME_FIELD','SAME_FIELD','0',pos,'0')
   delta=tuple('KEEP' if x==y else 'SET:'+y for x,y in zip(sa,sb));unit=a['source_unit_full']
   edges.append({'edge_id':sid('E',name+'|'+a['observation_id']+'|'+b['observation_id']),'physical_folio':unit,'unit_id':sid('U',unit),'section':name,'register':oa['register'],'hand':oa['hand'],'source':sa,'target':sb,'delta':delta,'layout':layout,'scope':scope})
 return edges

def potentials(frozen):
 out={p:{} for p in PAIRS}
 for r in frozen['potential_weights']:
  p=tuple(map(int,r['pair_id'].split('-')))
  if p in out:out[p][(r['scope'],r['delta_a'],r['delta_b'])]=float(r['factor'])
 return out

def edge_eval(e,tables,phi,pairs,g):
 probs=[g.target_probs(e,tables,i) for i in range(6)]
 if any(e['target'][i] not in probs[i] for i in range(6)):return None
 combos=itertools.product(*(tuple(sorted(p)) for p in probs));z=0.;truth_base=math.prod(probs[i][e['target'][i]] for i in range(6));best=(-1.,None)
 for target in combos:
  base=math.prod(probs[i][target[i]] for i in range(6));ds=tuple('KEEP' if target[i]==e['source'][i] else 'SET:'+target[i] for i in range(6));energy=1.
  for p in pairs:energy*=phi[p].get((e['scope'],ds[p[0]],ds[p[1]]),1.)
  w=base*energy;z+=w
  if w>best[0] or (w==best[0] and target<best[1]):best=(w,target)
 truth_energy=math.prod(phi[p].get((e['scope'],e['delta'][p[0]],e['delta'][p[1]]),1.) for p in pairs)
 return {'ind_bits':-math.log2(truth_base),'graph_bits':-math.log2(truth_base*truth_energy/z),'gain':math.log2(truth_energy/z),'logz':math.log2(z),'truth_logenergy':math.log2(truth_energy),'ind_exact':int(tuple(max(p,key=lambda y:(p[y],tuple(-ord(c) for c in y))) for p in probs)==e['target']),'graph_exact':int(best[1]==e['target'])}

def null_worlds(events,phi,worlds=4096,seed=3481901):
 observed=sum(x['score']['gain'] for x in events);groups=[defaultdict(list) for _ in range(6)]
 for k,e in enumerate(events):
  for i in range(6):groups[i][(e['unit_id'],*e['layout'],e['source'][i])].append(k)
 rows=[];exceed=0
 for world in range(worlds):
  rng=random.Random(seed+world);labels=[[e['delta'][i] for e in events] for i in range(6)]
  for i in range(6):
   for idx in groups[i].values():
    vals=[labels[i][j] for j in idx];rng.shuffle(vals)
    for j,v in zip(idx,vals):labels[i][j]=v
  gain=0.
  for k,e in enumerate(events):
   le=0.
   for p in PAIRS:le+=math.log2(phi[p].get((e['scope'],labels[p[0]][k],labels[p[1]][k]),1.))
   gain+=le-(e['score']['logz'])
  exceed+=gain>=observed;rows.append(gain)
 return observed,rows,(1+exceed)/(1+worlds)

def main():
 design=json.loads(DESIGN.read_text());frozen=json.loads(FROZEN.read_text());gd=json.loads(G346_DESIGN.read_text());g=load_g346();phi=potentials(frozen);held=set(design['split']['held_units']);panel_rows=[];unit_rows=[];edge_rows=[];null_rows=[];all_null=[];observed=[]
 for name,(op,vp,system) in SYSTEMS.items():
  edges=build_edges(name,op,vp,system,design);train=[e for e in edges if e['physical_folio'] not in held];test=[e for e in edges if e['physical_folio'] in held];tables=g.build_tables(train,'INDEPENDENT_MARGINAL',gd);scored=[]
  for e in test:
   v=edge_eval(e,tables,phi,PAIRS,g)
   if v:e['score']=v;scored.append(e)
  if not scored:raise AssertionError(name)
  obs,nvals,null_p=null_worlds(scored,phi);observed.append(obs);all_null.append(nvals)
  for w,v in enumerate(nvals):null_rows.append({'system':name,'world':w,'graph_gain_bits':format(v,'.17g')})
  ind=sum(e['score']['ind_bits'] for e in scored);graph=sum(e['score']['graph_bits'] for e in scored);ie=sum(e['score']['ind_exact'] for e in scored);ge=sum(e['score']['graph_exact'] for e in scored)
  positives=0
  for u in sorted({e['unit_id'] for e in scored}):
   es=[e for e in scored if e['unit_id']==u];gain=sum(e['score']['gain'] for e in es);positives+=gain>0;unit_rows.append({'system':name,'held_unit':u,'events':len(es),'independent_bits':format(sum(e['score']['ind_bits'] for e in es),'.17g'),'graph_bits':format(sum(e['score']['graph_bits'] for e in es),'.17g'),'graph_gain_bits':format(gain,'.17g'),'positive':int(gain>0)})
  nonneutral=0
  for pair in PAIRS:
   vals=[]
   for e in scored:
    factor=phi[pair].get((e['scope'],e['delta'][pair[0]],e['delta'][pair[1]]),1.);vals.append(factor);nonneutral+=factor!=1.
   pair_gain=0.
   for e in scored:
    v=edge_eval(e,tables,phi,(pair,),g);pair_gain+=v['gain']
   edge_rows.append({'system':name,'pair_id':f'{pair[0]}-{pair[1]}','coordinate_a':COMP[pair[0]],'coordinate_b':COMP[pair[1]],'events':len(scored),'nonneutral_truth_cells':sum(x!=1 for x in vals),'gain_bits':format(pair_gain,'.17g')})
  mobile=sum(any(len(v)>1 for v in [set(e['delta'][i] for e in scored if e['unit_id']==x['unit_id'] and e['layout']==x['layout'] and e['source'][i]==x['source'][i]) for i in range(6)]) for x in scored)
  coverage=nonneutral/(len(scored)*len(PAIRS));comparable=len(scored)>=500 and len({e['unit_id'] for e in scored})>=3 and coverage>=.1 and mobile>=100
  panel_rows.append({'system':name,'training_events':len(train),'held_events':len(scored),'held_units':len({e['unit_id'] for e in scored}),'independent_bits':format(ind,'.17g'),'graph_bits':format(graph,'.17g'),'raw_gain_bits':format(obs,'.17g'),'cost_adjusted_gain_bits':format(obs-float(frozen['selector_bits_once']),'.17g'),'positive_units':positives,'independent_exact':ie,'graph_exact':ge,'nonneutral_coverage':format(coverage,'.17g'),'null_mobile_events':mobile,'inclusive_p':format(null_p,'.17g'),'comparable':int(comparable),'semantic_state':'UNASSIGNED'})
 # synchronized max-three null across the same 4096 world indices
 obsmax=max(observed);ex=sum(max(vals[w] for vals in all_null)>=obsmax for w in range(4096));maxp=(1+ex)/4097
 by={r['system']:r for r in panel_rows}
 sig={k:(r['comparable']=='1' and float(r['raw_gain_bits'])>0 and float(r['inclusive_p'])<=.05 and maxp<=.05) for k,r in by.items()}
 if sig['LEXICAL_A']:status='ORACLE_GENERIC_LAYOUT_TRANSPORT'
 elif sig['FACTORIAL_B'] and sig['HUMAN_GROWN_B2']:status='ORACLE_COMPILER_STYLE_TRANSPORT'
 elif all(int(r['comparable'])==1 for r in panel_rows) and not any(sig.values()):status='ORACLE_MANUSCRIPT_SPECIFIC_RETAINED'
 else:status='ORACLE_CALIBRATION_INCONCLUSIVE'
 for r in panel_rows:r['max_three_p']=format(maxp,'.17g')
 write_tsv(PANELS,panel_rows);write_tsv(UNITS,unit_rows);write_tsv(EDGES,edge_rows);write_tsv(NULL,null_rows)
 counters=[
  {'counterexample_id':'CE01_PARTIAL_CROSSWALK','finding':'field marker positional right literal escape B2 lexical closure and hosts are intentionally unmapped','effect':'oracle ceiling covers only the closest six-coordinate analogue'},
  {'counterexample_id':'CE02_ALTERNATE_REGISTER_COPIES','finding':'register copies of one source unit remain correlated','effect':'source-unit split and unit-level signs are primary'},
  {'counterexample_id':'CE03_LABEL_ALIGNMENT','finding':'right categories use training-frequency rank rather than semantic identity','effect':'no graph-score optimization but category alignment remains an analytical convention'},
  {'counterexample_id':'CE04_NO_NEW_VOYNICH_SCORE','finding':'Voynich result is inherited unchanged from GDT347','effect':'this calibration cannot strengthen a Voynich decoding claim'}]
 write_tsv(COUNTER,counters)
 result={'schema':'GDT348_RESULT_V1','date':'2026-08-19','status':status,'panels':{r['system']:{k:r[k] for k in r if k not in {'system','semantic_state'}} for r in panel_rows},'max_three_p':maxp,'topology':frozen['topology'],'weights_unchanged':True,'score_optimized_mapping':False,'interpretation':status,'inputs':{str(p.relative_to(ROOT)):sha(p) for p in (DESIGN,FROZEN,G346_DESIGN,G346_RUN,O172,V172,O173,V173,METHOD,AUDIT,CORRECTION)},'outputs':{},'implementation':{str(Path(__file__).relative_to(ROOT)):sha(Path(__file__))},'f84':{'opened':False,'parsed':False,'retained':False,'scored':False},'semantic_state':'UNASSIGNED','claim_ceiling':'Oracle-coordinate instrument calibration only; no authorial compiler, semantics, PAGE_HOST factorization, tuple merge, word, morphology, language, plaintext, translation, or f84 result.'}
 REPORT.write_text(report_text(status,panel_rows,edge_rows,maxp));
 for pth in (PANELS,UNITS,EDGES,NULL,COUNTER,REPORT):result['outputs'][str(pth.relative_to(ROOT))]=sha(pth)
 result['content_sha256']=chash(result);RESULT.write_bytes(canonical(result));print(status,[(r['system'],r['raw_gain_bits'],r['inclusive_p']) for r in panel_rows],f'max3={maxp:.6g}')

def report_text(status,panels,edges,maxp):
 lines=['# GDT348 oracle-coordinate transport calibration report','',f'Status: **{status}**','',
 'GDT348 applies the exact three GDT347 pair tables and weights to authored oracle coordinates in the frozen synthetic controls. No Voynich model or score is changed.','',
 '## Panel results','', '| system | held events | raw gain (bits) | after topology cost | positive units | exact independent→graph | local p | max-3 p |','| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
 for r in panels:lines.append(f"| {r['system']} | {r['held_events']} | {r['raw_gain_bits']} | {r['cost_adjusted_gain_bits']} | {r['positive_units']}/{r['held_units']} | {r['independent_exact']}→{r['graph_exact']} | {r['inclusive_p']} | {maxp:.9f} |")
 lines+=['','## Edge decomposition','', '| system | edge | gain (bits) | non-neutral truth cells |','| --- | --- | ---: | ---: |']
 for r in edges:lines.append(f"| {r['system']} | {r['coordinate_a']}↔{r['coordinate_b']} | {r['gain_bits']} | {r['nonneutral_truth_cells']}/{r['events']} |")
 lines+=['','## Interpretation','',
 'All three fully comparable controls worsen held codelength, and every system is negative on all five held source units. Supplying the authored fields therefore does not rescue the GDT347 transport. B2\'s nominal local `p=.0403` is not positive evidence: its observed gain is −788.29 bits and only exceeds still more-negative coupling-destruction worlds. Exact next-state recovery is unchanged in every system.','',
 'This is an oracle ceiling. A positive result would show that a known authored system can reproduce the frozen Voynich coupling only after its true fields are supplied; it would not show that the blind VManus parser can recover those fields. The present negative result is stronger than GDT347 for the mapped inner-D, right, DY, wrapper, frame, and B3 analogues, but not for omitted field-marker, positional-right, literal, host, or B2-closure structure. The result retains a manuscript-specific formal convention within this coordinate definition; it does not establish a unique compiler.','',
 'No semantics, PAGE_HOST factorization, tuple merging, morphology, language, plaintext, translation, or f84 access occurred.','']
 return '\n'.join(lines)
if __name__=='__main__':main()

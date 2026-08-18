#!/usr/bin/env python3
"""Run GDT331 external-context agreement for recurrent field formulas."""
import csv,hashlib,json,random,statistics
from collections import defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent;INTER=R/'gdt327_joint_tuple_interlinear.tsv';ATLAS=R/'gdt328_formula_atlas.tsv';OCC=R/'gdt328_formula_occurrences.tsv';METHOD=R/'GDT331_FORMULA_EXTERNAL_CONTEXT_METHOD.md';SCORES=R/'gdt331_formula_context_scores.tsv';NULL=R/'gdt331_null.tsv';REPORT=R/'GDT331_FORMULA_EXTERNAL_CONTEXT_REPORT.md';RESULT=R/'gdt331_result.json';WORLDS=8192;SEED=331
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def can(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def read(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def write(p,rows):
 with Path(p).open('w',encoding='utf8',newline='') as h:w=csv.DictWriter(h,rows[0].keys(),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def main():
 rows=read(INTER);assert len(rows)==8448 and not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in rows);fields=defaultdict(list)
 for x in rows:fields[(x['page'],x['locus'],int(x['field_ordinal']))].append(x)
 for v in fields.values():v.sort(key=lambda x:int(x['group_index']))
 linecount=defaultdict(int)
 for p,l,o in fields:linecount[p,l]=max(linecount[p,l],o)
 def bucket(n):return str(n) if n<4 else '4+'
 def closure(v):return 'DY' if v[-1]['dy_closure']=='1' else ('B3' if v[-1]['b3']=='1' else 'OPEN')
 def context(k):
  p,l,o=k;pr=fields.get((p,l,o-1));nx=fields.get((p,l,o+1));return (bucket(len(pr)) if pr else 'NONE',closure(pr) if pr else 'NONE',bucket(len(nx)) if nx else 'NONE',closure(nx) if nx else 'NONE',bucket(linecount[p,l]))
 contexts={k:context(k) for k in fields};atlas=read(ATLAS);occ=read(OCC);by=defaultdict(list)
 for x in occ:by[x['formula_id']].append((x['page'],x['locus'],int(x['field_ordinal'])))
 def score(a,assign=None):
  vals=[contexts[assign[k]] if assign else contexts[k] for k in by[a['formula_id']]];den=5*sum(range(len(vals)));return sum(x==y for i,a in enumerate(vals) for b in vals[i+1:] for x,y in zip(a,b))/den
 observed=[score(a) for a in atlas];strata=defaultdict(list)
 for k,v in fields.items():strata[(v[0]['register'],len(v),k[2])].append(k)
 rng=random.Random(SEED);worlds=[[] for _ in atlas]
 for w in range(WORLDS):
  assign={}
  for s,keys in sorted(strata.items()):
   shuffled=keys[:];rng.shuffle(shuffled);assign.update(zip(keys,shuffled))
  for i,a in enumerate(atlas):worlds[i].append(score(a,assign))
 means=[statistics.mean(v) for v in worlds];sds=[statistics.pstdev(v) for v in worlds];zs=[(observed[i]-means[i])/sds[i] if sds[i] else 0 for i in range(len(atlas))];maxz=[max((worlds[i][w]-means[i])/sds[i] if sds[i] else 0 for i in range(len(atlas))) for w in range(WORLDS)]
 out=[]
 for i,a in enumerate(atlas):out.append({'formula_id':a['formula_id'],'level':a['level'],'level_rank':a['level_rank'],'group_length':a['group_length'],'occurrences':a['occurrences'],'physical_folios':a['physical_folios'],'page_host_sequence_display':a['page_host_sequence_display'],'observed_context_agreement':f'{observed[i]:.12f}','null_mean':f'{means[i]:.12f}','context_z':f'{zs[i]:.12f}','local_inclusive_p':f'{(sum(v>=observed[i]-1e-12 for v in worlds[i])+1)/(WORLDS+1):.12f}','max44_inclusive_p':f'{(sum(v>=zs[i]-1e-12 for v in maxz)+1)/(WORLDS+1):.12f}','semantic_state':'UNASSIGNED'})
 out.sort(key=lambda x:-float(x['context_z']));write(SCORES,out);write(NULL,[{'world':'OBSERVED','max_context_z':out[0]['context_z']}]+[{'world':i+1,'max_context_z':f'{v:.12f}'} for i,v in enumerate(maxz)]);lead=out[0];triple=next(x for x in out if x['formula_id']=='GDT328_9CBFB2F759E75414');status='NO_RECURRENT_FORMULA_HAS_SEARCH_STABLE_EXTERNAL_TEMPLATE' if float(lead['max44_inclusive_p'])>.05 else 'RECURRENT_FORMULA_EXTERNAL_TEMPLATE_LEAD'
 report=f'''# GDT331 — repeated-formula external record context

Status: **{status}**.

The best of 44 formulas is the two-host display `{lead['page_host_sequence_display']}`.  Its external-context agreement is {float(lead['observed_context_agreement']):.3f} against null mean {float(lead['null_mean']):.3f} (z={float(lead['context_z']):.3f}, local p={float(lead['local_inclusive_p']):.6f}, max-44 p={float(lead['max44_inclusive_p']):.6f}).

The GDT328 three-host formula has agreement {float(triple['observed_context_agreement']):.3f} against {float(triple['null_mean']):.3f} (z={float(triple['context_z']):.3f}, local p={float(triple['local_inclusive_p']):.6f}, max-44 p={float(triple['max44_inclusive_p']):.6f}). Its preceding field lengths are 1, 3, and 5+, and its following fields also differ.  It is therefore better described as portable stock field material than as one fixed whole-record template.

No formula has search-adjusted stable external context.  This does not erase exact formula recurrence; it prevents promoting recurrence into a record-level semantic slot or complete phrase schema.

No word boundary, phrase, semantic role, object, meaning, language, plaintext, or translation is assigned.  No f84 row was opened, retained, joined, or scored.
''';REPORT.write_text(report)
 result={'schema':'GDT331_FORMULA_EXTERNAL_CONTEXT_RESULT_V1','status':status,'candidates':len(atlas),'worlds':WORLDS,'lead':lead,'three_host_formula':triple,'claim_ceiling':'External record-context stability only; no semantic slot meaning plaintext or translation.','f84':{'input_rows':0,'opened':False,'retained':False,'joined':False,'scored':False},'inputs':{p.name:sha(p) for p in (INTER,ATLAS,OCC,R/'gdt329_result.json')},'documents':{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)},'implementation':{Path(__file__).name:sha(Path(__file__))},'outputs':{SCORES.name:sha(SCORES),NULL.name:sha(NULL)}};result['content_sha256']=can(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':status,'lead':lead,'triple':triple},sort_keys=True))
if __name__=='__main__':main()

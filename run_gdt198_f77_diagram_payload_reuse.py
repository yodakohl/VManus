#!/usr/bin/env python3
"""Score f77 diagram-internal opaque payload reuse."""
from __future__ import annotations
import csv,hashlib,itertools,json
from pathlib import Path
from run_gdt196_f77_structural_interlinear import read as read_rows, label_parser, tuple_key

R=Path(__file__).resolve().parent;SOURCE=R/'gdt062_right_family_inventory.tsv';STEPS=R/'gdt180_f77_process_steps.tsv';FIG=R/'gdt198_f77_figure_label_manifest.tsv';METHOD=R/'GDT198_F77_DIAGRAM_PAYLOAD_REUSE_METHOD.md';REPORT=R/'GDT198_F77_DIAGRAM_PAYLOAD_REUSE_REPORT.md';LINKS=R/'gdt198_f77_payload_links.tsv';NULL=R/'gdt198_assignment_null.tsv';COUNTER=R/'gdt198_counterexamples.tsv';RESULT=R/'gdt198_result.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def read(p):
 with Path(p).open(encoding='utf8',newline='')as h:return list(csv.DictReader(h,delimiter='\t'))
def write(p,rows,fields):
 with Path(p).open('w',encoding='utf8',newline='')as h:w=csv.DictWriter(h,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def payload(q):return'|'.join(str(q[k])for k in('page_host','right_family','dy_closure','b3'))
def main():
 source=[r for r in read_rows(SOURCE)if not r['page'].startswith('f84')];assert not any(r['page'].startswith('f84')for r in source);parse=label_parser(source)
 steps=read(STEPS);fig=read(FIG);assert len(steps)==6 and len(fig)==4
 items=[]
 for r in steps:
  q=parse(r['ZL3b_surface']);items.append({'locus':r['locus'],'visual_class':'TUBE_SEGMENT_STATE','surface':r['ZL3b_surface'],'payload':payload(q),'full_tuple':tuple_key(q),'reading_state':'ALL_READING_EXACT_SINGLE_GROUP'})
 for r in fig:
  if r['reading_state']!='ALL_READING_EXACT_SINGLE_GROUP':continue
  q=parse(r['ZL3b_surface']);items.append({'locus':r['locus'],'visual_class':'FIGURE_ASSOCIATED','surface':r['ZL3b_surface'],'payload':payload(q),'full_tuple':tuple_key(q),'reading_state':r['reading_state']})
 assert len(items)==9
 states=[x for x in items if x['visual_class']=='TUBE_SEGMENT_STATE'];figures=[x for x in items if x['visual_class']=='FIGURE_ASSOCIATED']
 links=[]
 for f in figures:
  matches=[s for s in states if s['payload']==f['payload']]
  links.append({'figure_locus':f['locus'],'figure_surface':f['surface'],'payload':f['payload'],'matching_tube_loci':';'.join(s['locus']for s in matches),'matching_tube_surfaces':';'.join(s['surface']for s in matches),'cross_class_payload_match':int(bool(matches)),'full_tuple_match':int(any(s['full_tuple']==f['full_tuple']for s in matches)),'interpretation':'OPAQUE_PAYLOAD_REUSE_DIFFERENT_RENDERER'if matches else'NO_TUBE_PAYLOAD_MATCH'})
 weak=fig[-1];links.append({'figure_locus':weak['locus'],'figure_surface':weak['ZL3b_surface'],'payload':'UNRESOLVED_READING_SEGMENTATION','matching_tube_loci':'f77r.5','matching_tube_surfaces':'otol','cross_class_payload_match':'NOT_SCORED','full_tuple_match':'NOT_SCORED','interpretation':'READING_SENSITIVE_OTOL_PREFIX_LEAD'})
 write(LINKS,links,list(links[0]))
 locs=[x['locus']for x in items];by={x['locus']:x for x in items}
 def score(chosen):
  F=set(chosen);S=set(locs)-F
  return sum(any(by[f]['payload']==by[s]['payload']for s in S)for f in F)
 actual=tuple(x['locus']for x in figures);observed=score(actual);worlds=[]
 for chosen in itertools.combinations(locs,3):worlds.append((chosen,score(chosen)))
 ge=sum(v>=observed for _,v in worlds);p=ge/len(worlds);dist={v:sum(x==v for _,x in worlds)for v in sorted({x for _,x in worlds})}
 null=[{'null':'ALL_3_OF_9_VISUAL_CLASS_ASSIGNMENTS','worlds':len(worlds),'observed_cross_class_matches':observed,'worlds_at_least_observed':ge,'inclusive_p':p,'score_distribution':json.dumps(dist,sort_keys=True),'preserves':'nine exact payloads;three versus six class sizes;single-group all-reading stability'}];write(NULL,null,list(null[0]))
 status='LOCAL_PAYLOAD_REUSE_LEAD_NOT_ABOVE_ROLE_ASSIGNMENT_NULL'
 counters=[{'id':'C01','finding':f'Exact assignment tail is {ge}/{len(worlds)} or p={p:.6f}.','impact':'Two matches are not rare under local role reassignment.'},{'id':'C02','finding':'Both matches require stripping wrapper and O/OT frame.','impact':'No exact whole surface or full HPR2 tuple is shared.'},{'id':'C03','finding':'All ownership evidence is proximity only.','impact':'The labels need not name their nearest figure or tube state.'},{'id':'C04','finding':'f77r.50 changes group segmentation across readings.','impact':'The otol prefix resemblance remains descriptive only.'},{'id':'C05','finding':'Payload definition was noticed after label exposure.','impact':'This is hypothesis generation, not confirmation.'}];write(COUNTER,counters,list(counters[0]))
 report=f'''# GDT198 — two local opaque payloads bridge f77 label classes

Status: **{status}**.

Two of the three all-reading-stable figure-associated labels share the same
renderer-stripped HPR2 payload as one of the six tube-state labels:

| figure label | tube label | shared payload | surface change |
|---|---|---|---|
| `dotedy` (`f77r.8`) | `otedy` (`f77r.3`) | `e|NONE|DY1|B30` | add outer `d` wrapper |
| `otchdy` (`f77r.49`) | `dchdy` (`f77r.6`) | `ch|NONE|DY1|B30` | `d` wrapper versus `OT` frame |

The southwest figure label supplies a weaker third resemblance: ZL3b writes
`otolaiin | o`, while IT2a/RF1b join `otolaiino`; its initial `otol` equals the
fourth tube label, but the reading-dependent boundary prevents an exact
payload comparison.

This is a coherent local compiler pattern: opaque payload can remain stable
while its left rendering changes with visual label class.  It is not strong
enough to identify a role.  Across all 84 assignments of three figure roles to
the nine stable labels, {ge} achieve at least the observed two cross-class
matches (**p={p:.6f}**).  Neither matched pair shares a complete surface or
full HPR2 tuple, and all human ownership is proximity-only.

The best abductive use is therefore narrow: retain `e+DY` and `ch+DY` as two
page-local opaque values reused across diagram contexts.  Do not call them
DRY, MOIST, figures, substances, or operations.  No word, sound, language,
plaintext, meaning, or translation is established. f84r and all f84 rows were
excluded.
''';REPORT.write_text(report,encoding='utf8')
 result={'schema':'GDT198_F77_DIAGRAM_PAYLOAD_REUSE_RESULT_V1','status':status,'stable_labels':9,'tube_labels':6,'figure_labels_primary':3,'reading_sensitive_figure_labels':1,'cross_class_payload_matches':observed,'exact_assignment_worlds':len(worlds),'worlds_at_least_observed':ge,'inclusive_p':p,'retained_local_payloads':['e|NONE|1|0','ch|NONE|1|0'],'interpretation':'Two renderer-stripped opaque payloads recur across tube-state and figure-associated label classes; the exposed local assignment is not rare under role reassignment.','claim_ceiling':'Local opaque payload reuse only; no ownership, quality, figure identity, tube function, word, sound, language, plaintext, meaning, or translation.','f84r':{'opened':False,'retained':False,'queried':False,'joined':False,'scored':False},'inputs':{SOURCE.name:sha(SOURCE),STEPS.name:sha(STEPS),FIG.name:sha(FIG),'gdt196_result.json':sha(R/'gdt196_result.json')},'implementation':{Path(__file__).name:sha(Path(__file__)),'run_gdt196_f77_structural_interlinear.py':sha(R/'run_gdt196_f77_structural_interlinear.py')},'outputs':{LINKS.name:sha(LINKS),NULL.name:sha(NULL),COUNTER.name:sha(COUNTER)},'documents':{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result['result_content_sha256']=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':status,'matches':observed,'p':p},sort_keys=True))
if __name__=='__main__':main()

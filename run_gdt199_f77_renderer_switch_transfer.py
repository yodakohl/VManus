#!/usr/bin/env python3
"""Test the two exact GDT198 renderer switches outside f77."""
from __future__ import annotations
import csv,hashlib,json
from pathlib import Path
from run_gdt196_f77_structural_interlinear import read as read_rows,label_parser

R=Path(__file__).resolve().parent
GROUPS=R/'gdt059_hpr2_external_inventory.tsv';ANN=R/'gdt012_annotated_core_inventory.tsv'
FULL=R/'gdt062_right_family_inventory.tsv';PARENT=R/'gdt198_result.json'
METHOD=R/'GDT199_F77_RENDERER_SWITCH_TRANSFER_METHOD.md';REPORT=R/'GDT199_F77_RENDERER_SWITCH_TRANSFER_REPORT.md'
INV=R/'gdt199_renderer_transfer_inventory.tsv';COUNTER=R/'gdt199_counterexamples.tsv';RESULT=R/'gdt199_result.json'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def read(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def write(p,rows,fields):
 with Path(p).open('w',encoding='utf8',newline='') as h:
  w=csv.DictWriter(h,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def payload(q):return f"{q['page_host']}|{q['right_family']}|DY{q['dy_closure']}|B3{q['b3']}"
def renderer(q):return f"{q['wrapper']}|D{q['inner_d']}|{q['local_frame']}"

FROZEN={
 'e|NONE|DY1|B30':{'APPARATUS_ONLY':'NONE|D0|OT','FIGURE_ONLY':'d|D0|OT'},
 'ch|NONE|DY1|B30':{'APPARATUS_ONLY':'d|D0|NONE','FIGURE_ONLY':'NONE|D0|OT'},
}

def main():
 groups=read(GROUPS);ann=read(ANN);full=[r for r in read_rows(FULL) if not r['page'].startswith('f84')]
 assert groups and ann and full and not any(r['page'].startswith('f84') for r in groups+ann+full)
 parse=label_parser(full);meta={r['locus']:r for r in ann};by={}
 for r in groups:by.setdefault(r['locus'],[]).append(r)
 out=[]
 for locus,z in sorted(by.items()):
  if locus.startswith('f77') or len(z)!=1:continue
  q=parse(z[0]['token']);p=payload(q)
  if p not in FROZEN:continue
  a=meta[locus];tags={x for x in (a['object_tags']+';'+a['relation_tags']).split(';') if x and x!='LABEL'}
  fig='FIGURE' in tags;app='WATER_OR_APPARATUS' in tags
  cls='FIGURE_ONLY' if fig and not app else 'APPARATUS_ONLY' if app and not fig else 'DUAL_OR_AMBIGUOUS' if fig and app else 'OTHER_CONTEXT'
  pred=FROZEN[p].get(cls,'NOT_SCORED');actual=renderer(q);scored=pred!='NOT_SCORED';correct=scored and pred==actual
  out.append({'locus':locus,'page':a['page'],'physical_folio':a['physical_folio'],'surface':z[0]['token'],'payload':p,'actual_renderer':actual,'archived_visual_class':cls,'prediction':pred,'scored':int(scored),'exact_prediction_correct':int(correct) if scored else 'NOT_SCORED','annotation_certainty':a['annotation_certainty'],'object_tags':a['object_tags'],'relation_tags':a['relation_tags'],'unit':a['unit'],'provenance':a['annotation_source']})
 assert len(out)==5 and not any(r['page'].startswith('f84') for r in out)
 write(INV,out,list(out[0]))
 eligible=[r for r in out if r['scored']==1];hits=sum(r['exact_prediction_correct']==1 for r in eligible)
 status='F77_RENDERER_SWITCH_DOES_NOT_TRANSFER_TO_ARCHIVED_LABELS' if hits<len(eligible) else 'F77_RENDERER_SWITCH_TRANSFERS_TO_ARCHIVED_LABELS'
 counters=[
  {'id':'C01','finding':'The sole FIGURE_ONLY target f73v.23 is otedy with the apparatus renderer, not frozen figure renderer d+otedy.','impact':'The cleanest cross-folio figure prediction fails.'},
  {'id':'C02','finding':'The two APPARATUS_ONLY targets are both on physical folio f75.','impact':'The one correct exact prediction is not independent replication.'},
  {'id':'C03','finding':'f75v.56 has qotedy rather than the frozen bare-OT apparatus renderer.','impact':'Even the apparatus proxy does not preserve the exact renderer.'},
  {'id':'C04','finding':'f82v.2 is tagged both FIGURE and WATER_OR_APPARATUS.','impact':'Its bare-OT renderer cannot adjudicate the two frozen classes.'},
  {'id':'C05','finding':'The archived WATER_OR_APPARATUS axis is broader than f77 tube-state ownership.','impact':'A positive result would still have had limited role specificity.'},
 ]
 write(COUNTER,counters,list(counters[0]))
 report=f'''# GDT199 — the f77 renderer switch does not transfer

Status: **{status}**.

The complete non-f77 annotated inventory contains five single-group labels
with either exact GDT198 payload.  {len(eligible)} have an unambiguous archived proxy
class and receive a frozen prediction; only **{hits}/{len(eligible)}** matches.

| locus | class | surface | frozen prediction | result |
|---|---|---|---|---|
'''+''.join(f"| `{r['locus']}` | {r['archived_visual_class']} | `{r['surface']}` | `{r['prediction']}` | {'HIT' if r['exact_prediction_correct']==1 else 'MISS'} |\n" for r in eligible)+f'''

The decisive miss is `f73v.23`: it is figure-only in the archived human
atlas, but its `e+DY` payload uses bare `OT` (`otedy`), not the f77-derived
figure renderer `d+OT` (`dotedy`).  The apparatus-only hit and miss are both
on f75, so they cannot supply independent replication.  The remaining row is
retained as an other context and is not forced into a class.

Thus GDT198 remains a real local surface relation but not a transferable
visual-class renderer rule.  The reusable fact is only that opaque `e+DY` and
`ch+DY` payloads recur under multiple outer forms.  No ownership, role, word,
sound, language, plaintext, meaning, or translation follows.  f84r and every
f84 row were excluded.
'''
 REPORT.write_text(report,encoding='utf8')
 result={'schema':'GDT199_F77_RENDERER_SWITCH_TRANSFER_RESULT_V1','status':status,'complete_target_inventory':len(out),'eligible_predictions':len(eligible),'exact_hits':hits,'exact_misses':len(eligible)-hits,'figure_only_hits':sum(r['exact_prediction_correct']==1 for r in eligible if r['archived_visual_class']=='FIGURE_ONLY'),'figure_only_total':sum(r['archived_visual_class']=='FIGURE_ONLY' for r in eligible),'interpretation':'The exact f77 visual-class renderer switch does not transfer to the complete archived non-f77 payload-matched label inventory.','claim_ceiling':'Opaque payload recurrence only; no ownership, role, word, sound, language, plaintext, meaning, or translation.','f84r':{'opened':False,'retained':False,'queried':False,'joined':False,'scored':False},'inputs':{GROUPS.name:sha(GROUPS),ANN.name:sha(ANN),FULL.name:sha(FULL),PARENT.name:sha(PARENT)},'implementation':{Path(__file__).name:sha(Path(__file__)),'run_gdt196_f77_structural_interlinear.py':sha(R/'run_gdt196_f77_structural_interlinear.py')},'outputs':{INV.name:sha(INV),COUNTER.name:sha(COUNTER)},'documents':{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result['result_content_sha256']=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':status,'targets':len(out),'eligible':len(eligible),'hits':hits},sort_keys=True))
if __name__=='__main__':main()

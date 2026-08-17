#!/usr/bin/env python3
"""Apply the frozen f77 upper-d/lower-ot rule to the f83r panel."""
import csv,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent;MAN=R/'gdt201_f83r_zone_transfer_manifest.tsv';PARENT=R/'gdt200_result.json';VIS=R/'gdt002_f83r_direct_visual_observations.tsv';MORPH=R/'gdt002_morphology_occurrences.tsv';METHOD=R/'GDT201_F77_ZONE_RENDERER_F83_TRANSFER_METHOD.md';REPORT=R/'GDT201_F77_ZONE_RENDERER_F83_TRANSFER_REPORT.md';PRED=R/'gdt201_f83r_zone_predictions.tsv';COUNTER=R/'gdt201_counterexamples.tsv';RESULT=R/'gdt201_result.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def read(p):
 with Path(p).open(encoding='utf8',newline='')as h:return list(csv.DictReader(h,delimiter='\t'))
def write(p,rows,fields):
 with Path(p).open('w',encoding='utf8',newline='')as h:w=csv.DictWriter(h,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def main():
 rows=read(MAN);assert len(rows)==4 and not any(r['locus'].startswith('f84') for r in rows)
 out=[]
 for r in rows:
  pred='STARTS_D' if r['zone']=='ARCH_END_NEAR_FIGURE_AND_TUBE' else 'STARTS_OT'
  vals=[]
  for e in ('ZL3b','IT2a','RF1b'):
   s=r[e+'_surface'];actual='STARTS_D' if s.startswith('d') else 'STARTS_OT' if s.startswith('ot') else 'OTHER';vals.append(actual)
  out.append({'locus':r['locus'],'zone':r['zone'],'prediction':pred,'ZL3b_surface':r['ZL3b_surface'],'IT2a_surface':r['IT2a_surface'],'RF1b_surface':r['RF1b_surface'],'ZL3b_actual':vals[0],'IT2a_actual':vals[1],'RF1b_actual':vals[2],'all_reading_prediction_correct':int(all(x==pred for x in vals)),'reading_agreement_on_renderer':int(len(set(vals))==1),'formal_exposure':r['formal_exposure']})
 write(PRED,out,list(out[0]));hits=sum(r['all_reading_prediction_correct'] for r in out);assert hits==0
 status='F77_ZONE_RENDERER_FAILS_COMPARABLE_F83_PANEL'
 counters=[{'id':'C01','finding':'Both f83 upper arch-end labels begin with neither d nor ot.','impact':'The exact f77 upper-zone renderer fails twice.'},{'id':'C02','finding':'The lower f83 labels begin s and d, not ot.','impact':'The exact f77 lower-zone renderer fails twice.'},{'id':'C03','finding':'f83r.50 differs internally across readings but every reading begins s.','impact':'Transcription sensitivity cannot rescue the prefix prediction.'},{'id':'C04','finding':'Both panels were already exposed before this comparison.','impact':'The transfer is a fixed-rule correction, not pristine validation.'},{'id':'C05','finding':'All target visual ownership remains proximity/ambiguous.','impact':'Failure or success would not assign referents.'}];write(COUNTER,counters,list(counters[0]))
 report=f'''# GDT201 — the f77 zone renderer fails on comparable f83r

Status: **{status}**.

The unmodified f77 rule makes four predictions on the previously fixed f83r
panel and gets **{hits}/4** correct:

| locus | visual zone | predicted | observed |
|---|---|---|---|
'''+''.join(f"| `{r['locus']}` | {r['zone']} | {r['prediction']} | `{r['ZL3b_surface']}` ({r['ZL3b_actual']}) |\n" for r in out)+'''

All three readings agree on the relevant initial class.  The internal
`sasoldal`/`saroldal` disagreement at `f83r.50` therefore does not affect the
failure.

GDT200 remains an exact description of four f77 labels, but not a transferable
upper/lower apparatus renderer.  Together with GDT199, this removes visual
class and panel zone as general explanations of the f77 `d`/`ot` split.  The
outer forms remain page/register-conditioned compiler material with no decoded
role.  No ownership, direction, stage, word, sound, language, plaintext,
meaning, or translation follows.  f84r and every f84 row were excluded.
''';REPORT.write_text(report,encoding='utf8')
 result={'schema':'GDT201_F77_ZONE_RENDERER_F83_TRANSFER_RESULT_V1','status':status,'target_rows':4,'exact_predictions':4,'exact_hits':hits,'exact_misses':4-hits,'all_reading_renderer_agreement':sum(r['reading_agreement_on_renderer'] for r in out),'interpretation':'The exact f77 upper-d/lower-ot renderer does not transfer to the comparable fixed f83r panel.','claim_ceiling':'Page-local f77 pattern only; no ownership, direction, stage, word, sound, language, plaintext, meaning, or translation.','f84r':{'opened':False,'retained':False,'queried':False,'joined':False,'scored':False},'inputs':{MAN.name:sha(MAN),PARENT.name:sha(PARENT),VIS.name:sha(VIS),MORPH.name:sha(MORPH)},'implementation':{Path(__file__).name:sha(Path(__file__))},'outputs':{PRED.name:sha(PRED),COUNTER.name:sha(COUNTER)},'documents':{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result['result_content_sha256']=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':status,'hits':hits,'predictions':4},sort_keys=True))
if __name__=='__main__':main()

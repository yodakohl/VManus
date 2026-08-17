#!/usr/bin/env python3
"""Enumerate the complete four-label f77 figure-zone renderer pattern."""
import csv,hashlib,itertools,json
from pathlib import Path
R=Path(__file__).resolve().parent;FIG=R/'gdt198_f77_figure_label_manifest.tsv';PARENT=R/'gdt199_result.json';METHOD=R/'GDT200_F77_FIGURE_ZONE_RENDERER_METHOD.md';REPORT=R/'GDT200_F77_FIGURE_ZONE_RENDERER_REPORT.md';INV=R/'gdt200_f77_figure_zone_inventory.tsv';NULL=R/'gdt200_zone_assignment_null.tsv';COUNTER=R/'gdt200_counterexamples.tsv';RESULT=R/'gdt200_result.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def read(p):
 with Path(p).open(encoding='utf8',newline='')as h:return list(csv.DictReader(h,delimiter='\t'))
def write(p,rows,fields):
 with Path(p).open('w',encoding='utf8',newline='')as h:w=csv.DictWriter(h,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def main():
 rows=read(FIG);assert [r['locus']for r in rows]==['f77r.1','f77r.8','f77r.49','f77r.50']
 zones={'f77r.1':'UPPER_TUBE_ENDPOINT','f77r.8':'UPPER_TUBE_ENDPOINT','f77r.49':'MIDDLE_LOWER_LEFT_APPARATUS','f77r.50':'MIDDLE_LOWER_LEFT_APPARATUS'}
 out=[]
 for r in rows:
  starts_d=all(r[e+'_surface'].startswith('d') for e in ('ZL3b','IT2a','RF1b'));starts_ot=all(r[e+'_surface'].startswith('ot') for e in ('ZL3b','IT2a','RF1b'));assert starts_d^starts_ot
  out.append({'locus':r['locus'],'zone':zones[r['locus']],'ZL3b_surface':r['ZL3b_surface'],'IT2a_surface':r['IT2a_surface'],'RF1b_surface':r['RF1b_surface'],'all_reading_renderer':'STARTS_D' if starts_d else 'STARTS_OT','ownership_evidence':r['ownership_evidence'],'geometry_provenance':'EXISTING_HUMAN_ANNOTATION_PLUS_AI_DIRECT_VISUAL_OBSERVATION','canvas_id':'1006212','canvas_sha256':'9ad387ccea37cd8a25ce9602817eb19af5105c545a238203715efe454e5b24ad'})
 write(INV,out,list(out[0]));locs=[r['locus']for r in out];rend={r['locus']:r['all_reading_renderer'] for r in out};actual={'f77r.1','f77r.8'}
 def oriented(U):return sum(rend[x]=='STARTS_D' for x in U)+sum(rend[x]=='STARTS_OT' for x in set(locs)-set(U))
 def free(U):return max(oriented(U),4-oriented(U))
 worlds=[]
 for U in itertools.combinations(locs,2):worlds.append((U,oriented(set(U)),free(set(U))))
 obs=oriented(actual);obsf=free(actual);ge=sum(o>=obs for _,o,_ in worlds);gef=sum(f>=obsf for _,_,f in worlds)
 null=[{'null':'ALL_TWO_OF_FOUR_UPPER_ZONE_ASSIGNMENTS','worlds':len(worlds),'observed_directional_score':obs,'directional_worlds_at_least_observed':ge,'directional_p':ge/len(worlds),'observed_orientation_free_score':obsf,'orientation_free_worlds_at_least_observed':gef,'orientation_free_p':gef/len(worlds),'disclosure':'POSTHOC_LABEL_AND_ZONE_EXPOSED'}];write(NULL,null,list(null[0]))
 status='PERFECT_LOCAL_ZONE_RENDERER_PATTERN_POSTHOC_ONE_FOLIO'
 counters=[{'id':'C01','finding':'The pattern contains four labels on one exposed folio.','impact':'It has no independent transfer.'},{'id':'C02','finding':'The directional exact tail is 1/6 and orientation-free tail is 2/6.','impact':'Perfect separation is not rare enough to establish a code.'},{'id':'C03','finding':'All four labels have proximity-only ownership.','impact':'Zone is geometry, not a proved referent class.'},{'id':'C04','finding':'GDT199 rejected the same f77 renderer as a general visual-class rule.','impact':'The finding must remain page-local.'},{'id':'C05','finding':'No arrow or authorial direction mark is used.','impact':'Upper tube endpoints are not source/destination values.'}];write(COUNTER,counters,list(counters[0]))
 report=f'''# GDT200 — f77 outer rendering follows panel zone perfectly, post hoc

Status: **{status}**.

The complete four-label figure inventory separates exactly:

| zone | loci | all-reading surface rule |
|---|---|---|
| upper tube endpoints | `f77r.1`, `f77r.8` | both start `d` |
| separate middle/lower left apparatuses | `f77r.49`, `f77r.50` | both start `ot` |

Direct inspection of official canvas 1006212 confirms the geometric split but
does not supply label ownership or direction.  Across all six assignments of
two labels to the upper zone, the directional tail is **{ge}/6 = {ge/6:.6f}**;
allowing either orientation gives **{gef}/6 = {gef/6:.6f}**.  The pattern was
noticed after exposure and has no second folio.

This supplies a better explanation of the GDT198 pairs than visual semantics:
outer `d` versus `ot` can be a local panel-zone renderer while the opaque inner
payload recurs.  GDT199 already shows that the renderer does not transfer as a
general figure/apparatus rule.  Retain the four-row pattern as a layout clue,
not a source/destination, quality, stage, word, sound, language, plaintext,
meaning, or translation.  f84r and all f84 rows were excluded.
''';REPORT.write_text(report,encoding='utf8')
 result={'schema':'GDT200_F77_FIGURE_ZONE_RENDERER_RESULT_V1','status':status,'labels':4,'upper_labels':2,'lower_labels':2,'all_reading_stable':4,'directional_score':obs,'directional_worlds':6,'directional_p':ge/6,'orientation_free_p':gef/6,'interpretation':'The f77 figure-label renderer is perfectly aligned with upper versus middle/lower panel zone, but only post hoc on one folio.','claim_ceiling':'Page-local panel-zone renderer only; no ownership, direction, stage, quality, word, sound, language, plaintext, meaning, or translation.','f84r':{'opened':False,'retained':False,'queried':False,'joined':False,'scored':False},'inputs':{FIG.name:sha(FIG),PARENT.name:sha(PARENT)},'implementation':{Path(__file__).name:sha(Path(__file__))},'outputs':{INV.name:sha(INV),NULL.name:sha(NULL),COUNTER.name:sha(COUNTER)},'documents':{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result['result_content_sha256']=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':status,'directional_p':ge/6,'orientation_free_p':gef/6},sort_keys=True))
if __name__=='__main__':main()

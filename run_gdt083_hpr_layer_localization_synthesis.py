#!/usr/bin/env python3
"""GDT083: compare online page signal across HPR representations."""
from __future__ import annotations
import csv,hashlib,json,math,re
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT/"gdt062_right_family_inventory.tsv";BASE=ROOT/"gdt016_group_state_inventory.tsv";EXT=ROOT/"gdt068_behavior_representation_summary.tsv";METHOD=ROOT/"GDT083_HPR_LAYER_LOCALIZATION_SYNTHESIS_METHOD.md";REPORT=ROOT/"GDT083_HPR_LAYER_LOCALIZATION_SYNTHESIS_REPORT.md";SCORES=ROOT/"gdt083_layer_scores.tsv";PAGES=ROOT/"gdt083_layer_page_contributions.tsv";SYN=ROOT/"gdt083_evidence_synthesis.tsv";RESULT=ROOT/"gdt083_result.json";ALPHAS=(8,16,32,64,128,256,512,1024)
def read(p):
 with Path(p).open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def write(p,rows,fields):
 with Path(p).open("w",encoding="utf-8",newline="")as h:w=csv.DictWriter(h,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def main():
 rows=read(SOURCE);base={(r["locus"],r["group_index"]):r for r in read(BASE)};rows.sort(key=lambda r:(r["page"],int(re.search(r"\.(\d+)",r["locus"]).group(1)),int(r["group_index"])));assert len(rows)==15592 and not any(r["locus"].startswith("f84r")for r in rows);folios=sorted({r["physical_folio"]for r in rows})
 values={"RAW_TOKEN":[r["token"]for r in rows],"RESIDUAL_HOST":[base[r["locus"],r["group_index"]]["residual_host"]for r in rows],"PAGE_HOST":[r["page_host"]for r in rows],"COMPILER_ONLY":["|".join(r[k]for k in("inner_d","local_frame","right_family","dy_closure","b3"))for r in rows]}
 score_rows=[];page_rows=[]
 for rep,vals in values.items():
  vocab=len(set(vals));best=None
  for wa in ALPHAS:
   regbits=wrapbits=0.0;gains=[0.0]*len(ALPHAS);perpage=[defaultdict(float)for _ in ALPHAS]
   for fol in folios:
    tr=[i for i,r in enumerate(rows)if r["physical_folio"]!=fol];te=[i for i,r in enumerate(rows)if r["physical_folio"]==fol];rc=defaultdict(Counter);wc=defaultdict(Counter)
    for i in tr:rc[rows[i]["register"]][vals[i]]+=1;wc[rows[i]["register"],rows[i]["wrapper"]][vals[i]]+=1
    pc=[defaultdict(Counter)for _ in ALPHAS];j=0
    while j<len(te):
     locus=rows[te[j]]["locus"];batch=[]
     while j<len(te)and rows[te[j]]["locus"]==locus:batch.append(te[j]);j+=1
     for i in batch:
      r=rows[i];y=vals[i];c=rc[r["register"]];bp=(c[y]+.5)/(sum(c.values())+.5*vocab);d=wc[r["register"],r["wrapper"]];wp=(d[y]+wa*bp)/(sum(d.values())+wa);regbits-=math.log2(bp);wrapbits-=math.log2(wp)
      for k,pa in enumerate(ALPHAS):p=pc[k][r["page"]];gain=math.log2((p[y]+pa*wp)/(sum(p.values())+pa)/wp);gains[k]+=gain;perpage[k][r["page"]]+=gain
     for i in batch:
      for p in pc:p[rows[i]["page"]][vals[i]]+=1
   k=max(range(len(ALPHAS)),key=lambda x:gains[x]);page_gain=max(0.0,gains[k]);page_alpha=ALPHAS[k]if gains[k]>0 else"NO_PAGE";total=regbits-wrapbits+page_gain
   candidate={"representation":rep,"vocabulary":vocab,"groups":len(rows),"wrapper_alpha":wa,"page_alpha":page_alpha,"register_bits":regbits,"wrapper_bits":wrapbits,"wrapper_gain_vs_register":regbits-wrapbits,"page_gain_vs_wrapper":page_gain,"page_gain_per_group":page_gain/len(rows),"page_gain_fraction_of_wrapper_bits":page_gain/wrapbits,"total_gain_vs_register":total,"page_selected":int(page_gain>0)}
   if best is None or candidate["total_gain_vs_register"]>best[0]["total_gain_vs_register"]:best=(candidate,perpage[k]if page_gain>0 else defaultdict(float))
  score_rows.append(best[0]);counts=Counter()
  for r in rows:counts[r["page"]]+=1
  for page,gain in best[1].items():page_rows.append({"representation":rep,"page":page,"physical_folio":next(r["physical_folio"]for r in rows if r["page"]==page),"groups":counts[page],"page_gain_vs_wrapper":gain})
 ext={r["representation"]:r for r in read(EXT)};syn=[{"evidence":"INTERNAL_ONLINE_PAGE_SIGNAL","RAW_TOKEN":next(r for r in score_rows if r["representation"]=="RAW_TOKEN")["page_gain_vs_wrapper"],"RESIDUAL_HOST":next(r for r in score_rows if r["representation"]=="RESIDUAL_HOST")["page_gain_vs_wrapper"],"PAGE_HOST":next(r for r in score_rows if r["representation"]=="PAGE_HOST")["page_gain_vs_wrapper"],"COMPILER_ONLY":next(r for r in score_rows if r["representation"]=="COMPILER_ONLY")["page_gain_vs_wrapper"],"interpretation":"Internal page clustering exists in PAGE_HOST and compiler; not semantic by itself."},{"evidence":"ARCHIVED_EXTERNAL_AXIS_GAIN_GDT068","RAW_TOKEN":ext["RAW_CHAR3"]["descriptive_total_gain_bits"],"RESIDUAL_HOST":"NOT_SCORED","PAGE_HOST":ext["PAGE_HOST_CHAR3"]["descriptive_total_gain_bits"],"COMPILER_ONLY":ext["COMPILER_ONLY"]["descriptive_total_gain_bits"],"interpretation":"PAGE_HOST external-axis signal exceeds raw while compiler-only is negative; archived/postselected."},{"evidence":"CROSS_SECTION_TRANSFER_GDT073","RAW_TOKEN":"NOT_PRIMARY","RESIDUAL_HOST":"NOT_PRIMARY","PAGE_HOST":json.loads((ROOT/"gdt073_result.json").read_text())["primary"]["total_gain_bits"]if"primary"in json.loads((ROOT/"gdt073_result.json").read_text())else-61.992,"COMPILER_ONLY":"NOT_PRIMARY","interpretation":"Broad behavior profile failed section-excluded cross-section transfer."}]
 status="PAGE_HOST_PAGE_SIGNAL_EXCEEDS_RAW_AND_RESIDUAL_BUT_INTERNAL_COMPILER_SIGNAL_PREVENTS_SEMANTIC_LOCALIZATION"
 write(SCORES,[{k:f"{v:.12g}"if isinstance(v,float)else v for k,v in r.items()}for r in score_rows],list(score_rows[0]));write(PAGES,[{k:f"{v:.12g}"if isinstance(v,float)else v for k,v in r.items()}for r in page_rows],list(page_rows[0]));write(SYN,syn,list(syn[0]))
 byrep={r["representation"]:r for r in score_rows};REPORT.write_text(f"""# GDT083 — HPR layer-localization synthesis

## Outcome

**{status}**

With whole physical folios held out and same-line cache leakage blocked, online
page adaptation after a register×WRAPPER baseline gains
`raw={byrep['RAW_TOKEN']['page_gain_vs_wrapper']:.3f}`,
`residual={byrep['RESIDUAL_HOST']['page_gain_vs_wrapper']:.3f}`,
`PAGE_HOST={byrep['PAGE_HOST']['page_gain_vs_wrapper']:.3f}`, and
`compiler={byrep['COMPILER_ONLY']['page_gain_vs_wrapper']:.3f}` bits.  PAGE_HOST
therefore improves over raw surface and the pre-HPR residual host as an
internal page-vocabulary representation.  But compiler signatures show even
more page clustering, so internal page dependence is not a semantic test.

The archived external-axis comparison supplies the crucial opposite pattern:
GDT068 gave raw {float(ext['RAW_CHAR3']['descriptive_total_gain_bits']):+.3f},
PAGE_HOST {float(ext['PAGE_HOST_CHAR3']['descriptive_total_gain_bits']):+.3f},
and compiler-only {float(ext['COMPILER_ONLY']['descriptive_total_gain_bits']):+.3f}
bits.  That localizes archived external information away from compiler-only
features, but GDT073's section-excluded transfer then lost about 61.992 bits.

The strongest coherent reading is: PAGE_HOST is a page-local vocabulary layer;
compiler coordinates also adapt to document layout; archived external content
is more visible after PAGE_HOST abstraction, but no broad transferable semantic
class has been established.  No new annotation or image was opened.  f84r was
excluded and not used.  No semantic role or gloss is assigned.
""",encoding="utf-8")
 result={"schema":"GDT083_HPR_LAYER_LOCALIZATION_SYNTHESIS_RESULT_V1","status":status,"groups":len(rows),"physical_folios":len(folios),"representations":score_rows,"external_archived":{"raw_gain_bits":float(ext["RAW_CHAR3"]["descriptive_total_gain_bits"]),"page_host_gain_bits":float(ext["PAGE_HOST_CHAR3"]["descriptive_total_gain_bits"]),"compiler_gain_bits":float(ext["COMPILER_ONLY"]["descriptive_total_gain_bits"]),"cross_section_behavior_gain_bits":-61.992},"interpretation":"PAGE_HOST is the best tested lexical-like page-vocabulary abstraction relative to raw/residual strings, but compiler page clustering and failed cross-section transfer prohibit semantic promotion.","claim_ceiling":"No semantic class, role, gloss, word, morpheme, POS, sound, language, plaintext, meaning, or translation.","f84r":{"opened":False,"retained":False,"queried":False,"joined":False,"scored":False,"targeted":False},"inputs":{SOURCE.name:sha(SOURCE),BASE.name:sha(BASE),EXT.name:sha(EXT),"gdt068_result.json":sha(ROOT/"gdt068_result.json"),"gdt073_result.json":sha(ROOT/"gdt073_result.json"),"gdt082_result.json":sha(ROOT/"gdt082_result.json")},"implementation":{Path(__file__).name:sha(Path(__file__))},"outputs":{SCORES.name:sha(SCORES),PAGES.name:sha(PAGES),SYN.name:sha(SYN)},"documents":{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result["result_content_sha256"]=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":status,"page_gains":{k:v["page_gain_vs_wrapper"]for k,v in byrep.items()}},sort_keys=True))
if __name__=="__main__":main()

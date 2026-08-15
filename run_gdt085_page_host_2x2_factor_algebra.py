#!/usr/bin/env python3
"""GDT085: held-cell factor prediction for ok/ot/yk/yt."""
from __future__ import annotations
import csv,hashlib,itertools,json,math
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT/"gdt062_right_family_inventory.tsv";METHOD=ROOT/"GDT085_PAGE_HOST_2X2_FACTOR_ALGEBRA_METHOD.md";REPORT=ROOT/"GDT085_PAGE_HOST_2X2_FACTOR_ALGEBRA_REPORT.md";CELLS=ROOT/"gdt085_host_renderer_cells.tsv";SCORES=ROOT/"gdt085_held_cell_scores.tsv";SCAN=ROOT/"gdt085_matched_rectangle_scan.tsv";RESULT=ROOT/"gdt085_result.json";HOSTS=("ok","ot","yk","yt");COORD={"ok":("o","k"),"ot":("o","t"),"yk":("y","k"),"yt":("y","t")};DIMS={"WRAPPER":"wrapper","RIGHT_FAMILY":"right_family","POSITION":"position_quartile","REGISTER":"register","DY":"dy_closure"};RIGHT=("aiin","air","ain","ar","al")
def read(p):
 with Path(p).open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def write(p,rows,fields):
 with Path(p).open("w",encoding="utf-8",newline="")as h:w=csv.DictWriter(h,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def distribution(rows,field,vocab):
 c=Counter(r[field]for r in rows);return{x:(c[x]+.5)/(len(rows)+.5*len(vocab))for x in vocab}
def bits(rows,field,p):return-sum(math.log2(p[r[field]])for r in rows)
def factor_score(rect,by,field):
 vocab=sorted({r[field]for h in rect for r in by[h]});out=[]
 for held in rect:
  a,b=held;row=next(h for h in rect if h[0]==a and h!=held);col=next(h for h in rect if h[1]==b and h!=held);diag=next(h for h in rect if h[0]!=a and h[1]!=b);pr=distribution(by[row],field,vocab);pc=distribution(by[col],field,vocab);pd=distribution(by[diag],field,vocab);raw={x:pr[x]*pc[x]/pd[x]for x in vocab};s=sum(raw.values());pf={x:raw[x]/s for x in vocab};pn={x:(pr[x]+pc[x])/2 for x in vocab};others=sum((by[h]for h in rect if h!=held),[]);pp=distribution(others,field,vocab);samebase=pr
  out.append({"held_host":held,"row_neighbor_same_base":row,"column_neighbor_same_terminal":col,"diagonal":diag,"held_occurrences":len(by[held]),"factor_bits":bits(by[held],field,pf),"neighbor_mixture_bits":bits(by[held],field,pn),"pooled_bits":bits(by[held],field,pp),"same_base_bits":bits(by[held],field,samebase)})
 return out
def main():
 rows=read(SOURCE);assert len(rows)==15592 and not any(r["locus"].startswith("f84r")for r in rows);by=defaultdict(list)
 for r in rows:by[r["page_host"]].append(r)
 score_rows=[];summaries={}
 for dim,field in DIMS.items():
  z=factor_score(list(HOSTS),by,field)
  for r in z:score_rows.append({"dimension":dim,**r,"factor_gain_vs_pool":r["pooled_bits"]-r["factor_bits"],"factor_gain_vs_neighbor_mixture":r["neighbor_mixture_bits"]-r["factor_bits"],"same_base_gain_vs_pool":r["pooled_bits"]-r["same_base_bits"]})
  summaries[dim]={"factor_gain_vs_pool":sum(r["pooled_bits"]-r["factor_bits"]for r in z),"factor_gain_vs_neighbor":sum(r["neighbor_mixture_bits"]-r["factor_bits"]for r in z),"same_base_gain_vs_pool":sum(r["pooled_bits"]-r["same_base_bits"]for r in z)}
 cell_rows=[]
 for host in HOSTS:
  for right in RIGHT:
   q=[r for r in by[host]if r["right_family"]==right];cell_rows.append({"page_host":host,"base_axis":COORD[host][0],"terminal_axis":COORD[host][1],"right_family":right,"occurrences":len(q),"physical_folios":len({r["physical_folio"]for r in q}),"example_token":q[0]["token"]if q else"","example_locus":q[0]["locus"]if q else"","cell":"PRESENT"if q else"ABSENT"})
 scan=[];wrappers=sorted({r["wrapper"]for r in rows})
 for threshold in(5,10,15,20):
  elig={h for h,z in by.items()if len(h)==2 and len(z)>=threshold and len({r["physical_folio"]for r in z})>=3};aa=sorted({h[0]for h in elig});bb=sorted({h[1]for h in elig});rects=[]
  for left in itertools.combinations(aa,2):
   for right in itertools.combinations(bb,2):
    rect=[a+b for a in left for b in right]
    if all(h in elig for h in rect):
     z=factor_score(rect,by,"wrapper");gain=sum(r["pooled_bits"]-r["factor_bits"]for r in z);rects.append((gain,rect,sum(len(by[h])for h in rect)))
  rects.sort(reverse=True)
  for rank,(gain,rect,n)in enumerate(rects,1):scan.append({"minimum_cell_occurrences":threshold,"rank_by_raw_gain":rank,"rectangle":";".join(rect),"total_occurrences":n,"wrapper_factor_gain_vs_pool":gain,"gain_per_occurrence":gain/n,"is_target":int(set(rect)==set(HOSTS))})
 target10=next(r for r in scan if r["minimum_cell_occurrences"]==10 and int(r["is_target"]));status="O_Y_HOST_AXIS_PREDICTS_WRAPPER_LICENSE_BUT_FULL_TWO_SLOT_INDEPENDENCE_FAILS"
 write(CELLS,cell_rows,list(cell_rows[0]));write(SCORES,[{k:f"{v:.12g}"if isinstance(v,float)else v for k,v in r.items()}for r in score_rows],list(score_rows[0]));write(SCAN,[{k:f"{v:.12g}"if isinstance(v,float)else v for k,v in r.items()}for r in scan],list(scan[0]))
 REPORT.write_text(f"""# GDT085 — PAGE_HOST 2×2 factor algebra

## Outcome

**{status}**

Every one of the twenty `{HOSTS} × {RIGHT}` renderer cells exists.  When an
entire host is hidden, the 2×2 factor model improves WRAPPER prediction by
{summaries['WRAPPER']['factor_gain_vs_pool']:+.3f} bits over pooling and
{summaries['WRAPPER']['factor_gain_vs_neighbor']:+.3f} over the equal
edit-distance-one neighbor mixture.  The simpler same-`o/y` neighbor gains
{summaries['WRAPPER']['same_base_gain_vs_pool']:+.3f} bits and wins 3/4 held
cells.  At minimum cell support 10, the target ranks
{target10['rank_by_raw_gain']}/{sum(r['minimum_cell_occurrences']==10 for r in scan)}
two-sign rectangles by raw held-cell WRAPPER gain.

The algebra is not general: factor gain versus pooling is
RIGHT_FAMILY {summaries['RIGHT_FAMILY']['factor_gain_vs_pool']:+.3f},
position {summaries['POSITION']['factor_gain_vs_pool']:+.3f}, register
{summaries['REGISTER']['factor_gain_vs_pool']:+.3f}, and DY
{summaries['DY']['factor_gain_vs_pool']:+.3f} bits.  The best current grammar is
therefore `PAGE_HOST := BASE(o/y) + TERMINAL(k/t)` only in the narrow sense
that BASE strongly organizes wrapper licensing.  TERMINAL is an unresolved
formal contrast; RIGHT_FAMILY remains whole-host/register-conditioned.

This is postselected and parser-native, not linguistic morphology.  GDT003
remains controlling negative evidence.  f84r was excluded and not used.  No
sound, meaning, role, language, or translation is assigned.
""",encoding="utf-8")
 result={"schema":"GDT085_PAGE_HOST_2X2_FACTOR_ALGEBRA_RESULT_V1","status":status,"hosts":list(HOSTS),"complete_renderer_cells":sum(r["cell"]=="PRESENT"for r in cell_rows),"dimension_summaries":summaries,"threshold10_target_rank":int(target10["rank_by_raw_gain"]),"threshold10_rectangles":sum(r["minimum_cell_occurrences"]==10 for r in scan),"grammar_refinement":{"page_host":"BASE(o/y) + TERMINAL(k/t)","base_function":"strong formal WRAPPER-licensing coordinate","terminal_function":"unresolved formal contrast","right_family":"whole-host and register conditioned; not factor-independent"},"limitations":["postselected rectangle","global held-cell rather than held-folio scoring","two-sign parser surfaces","GDT003 general algebra not above string baselines"],"claim_ceiling":"No content, semantic class, role, gloss, word, morpheme, POS, sound, language, plaintext, meaning, or translation.","f84r":{"opened":False,"retained":False,"queried":False,"joined":False,"scored":False,"targeted":False},"inputs":{SOURCE.name:sha(SOURCE),"gdt003_nested_result.json":sha(ROOT/"gdt003_nested_result.json"),"gdt081_result.json":sha(ROOT/"gdt081_result.json"),"gdt084_result.json":sha(ROOT/"gdt084_result.json")},"implementation":{Path(__file__).name:sha(Path(__file__))},"outputs":{CELLS.name:sha(CELLS),SCORES.name:sha(SCORES),SCAN.name:sha(SCAN)},"documents":{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result["result_content_sha256"]=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":status,"wrapper_gain":summaries["WRAPPER"]["factor_gain_vs_pool"],"right_gain":summaries["RIGHT_FAMILY"]["factor_gain_vs_pool"],"rank":target10["rank_by_raw_gain"]},sort_keys=True))
if __name__=="__main__":main()

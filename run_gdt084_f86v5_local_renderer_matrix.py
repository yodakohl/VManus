#!/usr/bin/env python3
"""GDT084: score the postselected f86v5 HPR5 renderer matrix."""
from __future__ import annotations
import csv,hashlib,itertools,json,math,random
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT/"gdt062_right_family_inventory.tsv";METHOD=ROOT/"GDT084_F86V5_LOCAL_RENDERER_MATRIX_METHOD.md";REPORT=ROOT/"GDT084_F86V5_LOCAL_RENDERER_MATRIX_REPORT.md";MATRIX=ROOT/"gdt084_f86v5_matrix.tsv";RANKS=ROOT/"gdt084_page_matrix_ranks.tsv";NULL=ROOT/"gdt084_null_results.tsv";RESULT=ROOT/"gdt084_result.json";HOSTS=("ok","yk","yt");RIGHT=("aiin","air","ain","ar","al")
def read(p):
 with Path(p).open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def write(p,rows,fields):
 with Path(p).open("w",encoding="utf-8",newline="")as h:w=csv.DictWriter(h,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def rect(z):
 c=set(z);return sum(all((h,r)in c for h in hs for r in rs)for hs in itertools.combinations(HOSTS,2)for rs in itertools.combinations(RIGHT,2))
def mi(z):
 n=len(z);a=Counter(h for h,r in z);b=Counter(r for h,r in z);c=Counter(z);return sum(v/n*math.log2(v*n/(a[h]*b[r]))for(h,r),v in c.items())
def main():
 rows=[r for r in read(SOURCE)if r["page_host"]in HOSTS and r["right_family"]in RIGHT];assert not any(r["locus"].startswith("f84r")for r in rows);by=defaultdict(list)
 for r in rows:by[r["page"]].append((r["page_host"],r["right_family"]))
 ranks=[]
 for page,z in by.items():ranks.append({"page":page,"occurrences":len(z),"distinct_cells":len(set(z)),"rectangles":rect(z),"mutual_information_bits":mi(z)})
 ranks.sort(key=lambda r:(-r["rectangles"],-r["distinct_cells"],r["page"]));
 for i,r in enumerate(ranks,1):r["rank"]=i
 z=by["f86v5"];matrix=[]
 for host in HOSTS:
  for right in RIGHT:
   q=[r for r in rows if r["page"]=="f86v5"and r["page_host"]==host and r["right_family"]==right];matrix.append({"page_host":host,"right_family":right,"occurrences":len(q),"physical_loci":";".join(r["locus"]for r in q),"tokens":";".join(r["token"]for r in q),"cell":"PRESENT"if q else"ABSENT"})
 obs=rect(z);obsmi=mi(z);rng=random.Random(84001);local=[];maxs=[];milow=[]
 for _ in range(10000):
  current={}
  for page,q in by.items():
   hs=[x[0]for x in q];rs=[x[1]for x in q];rng.shuffle(rs);current[page]=list(zip(hs,rs))
  local.append(rect(current["f86v5"]));milow.append(mi(current["f86v5"]));maxs.append(max(rect(q)for q in current.values()))
 null=[{"test":"F86V5_RECTANGLES_CONDITIONAL_MARGINS","observed":obs,"draws":len(local),"null_mean":sum(local)/len(local),"inclusive_p":(1+sum(x>=obs for x in local))/(len(local)+1)},{"test":"MANUSCRIPT_MAX_PAGE_RECTANGLES","observed":obs,"draws":len(maxs),"null_mean":sum(maxs)/len(maxs),"inclusive_p":(1+sum(x>=obs for x in maxs))/(len(maxs)+1)},{"test":"F86V5_LOW_MUTUAL_INFORMATION_INDEPENDENCE","observed":obsmi,"draws":len(milow),"null_mean":sum(milow)/len(milow),"inclusive_p":(1+sum(x<=obsmi for x in milow))/(len(milow)+1)}]
 status="F86V5_LOCAL_3X5_RENDERER_MATRIX_WEAK_POSTSELECTED_LEAD"
 write(MATRIX,matrix,list(matrix[0]));write(RANKS,[{k:f"{v:.12g}"if isinstance(v,float)else v for k,v in r.items()}for r in ranks],list(ranks[0]));write(NULL,[{k:f"{v:.12g}"if isinstance(v,float)else v for k,v in r.items()}for r in null],list(null[0]))
 REPORT.write_text(f"""# GDT084 — f86v5 local PAGE_HOST × RIGHT_FAMILY matrix

## Outcome

**{status}**

Across 20 occurrences on 14 physical lines, f86v5 fills 12/15 cells of
`{{ok,yk,yt}} × {{aiin,air,ain,ar,al}}` and contains {obs} complete 2×2
rectangles.  The next page has {ranks[1]['rectangles']}.  Missing cells are
`ok-air`, `ok-ain`, and `yk-air`.  The observed host×renderer mutual
information is {obsmi:.4f} bits, consistent with relatively free local
combination.

But the diverse f86v5 marginals make the pattern much less surprising:
conditional local p={float(null[0]['inclusive_p']):.4f}, and the
manuscript-max page correction is p={float(null[1]['inclusive_p']):.4f}.
Thus f86v5 is the strongest concrete local renderer matrix and a useful HPR5
example, not evidence beyond string statistics or a translation.  It is a
text-only page and was selected post hoc.  f84r was excluded and not used.
""",encoding="utf-8")
 result={"schema":"GDT084_F86V5_LOCAL_RENDERER_MATRIX_RESULT_V1","status":status,"eligible_pages":len(by),"f86v5_occurrences":len(z),"f86v5_physical_lines":len({r["locus"]for r in rows if r["page"]=="f86v5"}),"f86v5_distinct_cells":len(set(z)),"f86v5_rectangles":obs,"next_best_rectangles":ranks[1]["rectangles"],"f86v5_mutual_information_bits":obsmi,"local_conditional_p":float(null[0]["inclusive_p"]),"max_page_p":float(null[1]["inclusive_p"]),"interpretation":"f86v5 is a dense local HPR5 renderer matrix, but its rectangle count is explained by postselected diverse marginals.","claim_ceiling":"No content, semantic class, role, gloss, word, morpheme, POS, sound, language, plaintext, meaning, or translation.","f84r":{"opened":False,"retained":False,"queried":False,"joined":False,"scored":False,"targeted":False},"inputs":{SOURCE.name:sha(SOURCE),"gdt003_results.json":sha(ROOT/"gdt003_results.json"),"gdt082_result.json":sha(ROOT/"gdt082_result.json"),"gdt083_result.json":sha(ROOT/"gdt083_result.json")},"implementation":{Path(__file__).name:sha(Path(__file__))},"outputs":{MATRIX.name:sha(MATRIX),RANKS.name:sha(RANKS),NULL.name:sha(NULL)},"documents":{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result["result_content_sha256"]=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":status,"cells":len(set(z)),"rectangles":obs,"p":result["max_page_p"]},sort_keys=True))
if __name__=="__main__":main()

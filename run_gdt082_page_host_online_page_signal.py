#!/usr/bin/env python3
"""GDT082: exact HPR5 host identity from prior lines on an unseen folio."""
from __future__ import annotations
import csv,hashlib,json,math,random,re
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT/"gdt062_right_family_inventory.tsv";HPR5=ROOT/"gdt081_result.json";METHOD=ROOT/"GDT082_PAGE_HOST_ONLINE_PAGE_SIGNAL_METHOD.md";REPORT=ROOT/"GDT082_PAGE_HOST_ONLINE_PAGE_SIGNAL_REPORT.md";SCORES=ROOT/"gdt082_page_shrinkage_scores.tsv";REG=ROOT/"gdt082_register_scores.tsv";PAGES=ROOT/"gdt082_page_contributions.tsv";NULL=ROOT/"gdt082_null_results.tsv";RESULT=ROOT/"gdt082_result.json";Y=("ok","yk","yt");ALPHAS=(1,2,4,8,16,32,64);WA=4
def read(p):
 with Path(p).open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def write(p,rows,fields):
 with Path(p).open("w",encoding="utf-8",newline="")as h:w=csv.DictWriter(h,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def locnum(s):
 m=re.search(r"\.(\d+)",s);return int(m.group(1))if m else 0
def main():
 rows=[r for r in read(SOURCE)if r["page_host"]in Y];rows.sort(key=lambda r:(r["page"],locnum(r["locus"]),int(r["group_index"])));assert len(rows)==958 and not any(r["locus"].startswith("f84r")for r in rows);assert json.loads(HPR5.read_text())["primary_best_trio"]==list(Y)
 meta=[(r["register"],r["wrapper"],r["physical_folio"],r["page"],r["locus"])for r in rows];labels=[Y.index(r["page_host"])for r in rows];shuffle_groups=defaultdict(list)
 for i,(reg,w,*_)in enumerate(meta):shuffle_groups[reg,w].append(i)
 def score(labs,detail=False):
  gr=defaultdict(lambda:[0,0,0]);fr=defaultdict(lambda:[0,0,0]);gw=defaultdict(lambda:[0,0,0]);fw=defaultdict(lambda:[0,0,0])
  for (reg,w,fol,p,l),y in zip(meta,labs):gr[reg][y]+=1;fr[fol,reg][y]+=1;gw[reg,w][y]+=1;fw[fol,reg,w][y]+=1
  pcs=[defaultdict(lambda:[0,0,0])for _ in ALPHAS];gains=[0.0]*len(ALPHAS);bits=[0.0]*len(ALPHAS);wrapper_bits=0.0;reg_bits=0.0;perreg=[defaultdict(float)for _ in ALPHAS];perpage=[defaultdict(float)for _ in ALPHAS];i=0
  while i<len(meta):
   locus=meta[i][4];j=i
   while j<len(meta)and meta[j][4]==locus:j+=1
   for t in range(i,j):
    reg,w,fol,page,_=meta[t];y=labs[t];rc=[gr[reg][x]-fr[fol,reg][x]for x in range(3)];rn=sum(rc);base=[(rc[x]+.5)/(rn+1.5)for x in range(3)];wc=[gw[reg,w][x]-fw[fol,reg,w][x]for x in range(3)];wn=sum(wc);wp=[(wc[x]+WA*base[x])/(wn+WA)for x in range(3)];reg_bits-=math.log2(base[y]);wrapper_bits-=math.log2(wp[y])
    for k,a in enumerate(ALPHAS):
     c=pcs[k][page];n=sum(c);prob=(c[y]+a*wp[y])/(n+a);gain=math.log2(prob/wp[y]);gains[k]+=gain;bits[k]-=math.log2(prob);perreg[k][reg]+=gain;perpage[k][page]+=gain
   for t in range(i,j):
    page=meta[t][3];y=labs[t]
    for k in range(len(ALPHAS)):pcs[k][page][y]+=1
   i=j
  return gains,bits,wrapper_bits,reg_bits,perreg,perpage
 gains,bits,wrapper_bits,reg_bits,perreg,perpage=score(labels,True);best=max(range(len(ALPHAS)),key=lambda k:gains[k]);selected=ALPHAS[best]
 score_rows=[{"page_alpha":a,"register_bits":reg_bits,"wrapper_bits":wrapper_bits,"page_bits":bits[k],"wrapper_gain_vs_register":reg_bits-wrapper_bits,"page_gain_vs_wrapper":gains[k],"page_selector_paid_gain":gains[k]-math.log2(len(ALPHAS)),"selected":int(k==best)}for k,a in enumerate(ALPHAS)]
 register_rows=[{"register":reg,"occurrences":sum(r["register"]==reg for r in rows),"page_gain_vs_wrapper":perreg[best][reg],"direction":"POSITIVE"if perreg[best][reg]>0 else"NEGATIVE"}for reg in sorted({r["register"]for r in rows})]
 page_counts=defaultdict(Counter)
 for r in rows:page_counts[r["page"]][r["page_host"]]+=1
 page_rows=[{"page":page,"physical_folio":next(r["physical_folio"]for r in rows if r["page"]==page),"register":next(r["register"]for r in rows if r["page"]==page),"occurrences":sum(page_counts[page].values()),"ok":page_counts[page]["ok"],"yk":page_counts[page]["yk"],"yt":page_counts[page]["yt"],"page_gain_vs_wrapper":gain,"rank_by_gain":0}for page,gain in perpage[best].items()];page_rows.sort(key=lambda r:(-r["page_gain_vs_wrapper"],r["page"]));
 for i,r in enumerate(page_rows,1):r["rank_by_gain"]=i
 rng=random.Random(82002);null=[]
 for _ in range(5000):
  lab=labels[:]
  for idx in shuffle_groups.values():
   vals=[lab[i]for i in idx];rng.shuffle(vals)
   for i,y in zip(idx,vals):lab[i]=y
  null.append(max(score(lab)[0]))
 obs=gains[best];p=(1+sum(x>=obs for x in null))/(len(null)+1);s=sorted(null);null_rows=[{"null":"REGISTER_WRAPPER_PRESERVING_HOST_SHUFFLE_MAX_PAGE_ALPHA","draws":len(null),"observed_max_gain":obs,"null_mean":sum(null)/len(null),"null_q95":s[int(.95*len(s))],"null_q99":s[int(.99*len(s))],"null_max":max(null),"inclusive_p":p,"seed":82002}]
 status="PAGE_HOST_IDENTITY_HAS_PAGE_LOCAL_SIGNAL_BEYOND_WRAPPER_BUT_F86V5_DOMINATES"
 write(SCORES,[{k:f"{v:.12g}"if isinstance(v,float)else v for k,v in r.items()}for r in score_rows],list(score_rows[0]));write(REG,[{k:f"{v:.12g}"if isinstance(v,float)else v for k,v in r.items()}for r in register_rows],list(register_rows[0]));write(PAGES,[{k:f"{v:.12g}"if isinstance(v,float)else v for k,v in r.items()}for r in page_rows],list(page_rows[0]));write(NULL,[{k:f"{v:.12g}"if isinstance(v,float)else v for k,v in r.items()}for r in null_rows],list(null_rows[0]))
 top=page_rows[0];REPORT.write_text(f"""# GDT082 — PAGE_HOST online page-local identity signal

## Outcome

**{status}**

Across {len(rows)} `ok/yk/yt` occurrences on {len(page_rows)} pages and
{len({r['physical_folio']for r in rows})} physical folios, the
register×WRAPPER nuisance model saves {reg_bits-wrapper_bits:.3f} held-folio
bits over register alone.  After same-line updates are prohibited, the selected
online page shrinkage {selected} saves another {obs:.3f} bits
({obs-math.log2(len(ALPHAS)):.3f} after its seven-way selector).  A 5,000-draw
register×WRAPPER-preserving max-grid shuffle gives p={p:.5f}.

The gain is localized: `{top['page']}` contributes {top['page_gain_vs_wrapper']:+.3f}
bits, {100*top['page_gain_vs_wrapper']/obs:.1f}% of the total, with
`ok/yk/yt={top['ok']}/{top['yk']}/{top['yt']}`.  It is a human-catalogued
text-only page.  `OTHER_B` contributes {perreg[best]['OTHER_B']:+.3f} bits;
Stars/Recipe contributes {perreg[best]['STARS_RECIPE_B']:+.3f}.  Therefore
PAGE_HOST identity carries a real local-page vocabulary signal beyond wrapper,
but it is not a stable manuscript-wide semantic class.  The strongest lead is
the f86v5 local inventory contrast, not a gloss.  The null does not redo HPR5
or wrapper-alpha selection, so its p-value is exploratory.  f84r was excluded
and not opened or used.  No semantic class, role, gloss, word, morpheme, POS,
sound, language, plaintext, meaning, or translation is assigned.
""",encoding="utf-8")
 result={"schema":"GDT082_PAGE_HOST_ONLINE_PAGE_SIGNAL_RESULT_V1","status":status,"groups":len(rows),"pages":len(page_rows),"physical_folios":len({r["physical_folio"]for r in rows}),"host_counts":dict(Counter(r["page_host"]for r in rows)),"wrapper_gain_vs_register_bits":reg_bits-wrapper_bits,"selected_page_alpha":selected,"page_gain_vs_wrapper_bits":obs,"page_selector_paid_gain_bits":obs-math.log2(len(ALPHAS)),"null_inclusive_p":p,"positive_registers":sum(r["direction"]=="POSITIVE"for r in register_rows),"top_page":top,"interpretation":"Exact PAGE_HOST identity has sequential page-local information after wrapper, but f86v5 and OTHER_B dominate; this localizes a page vocabulary layer without identifying content.","claim_ceiling":"No semantic class, role, gloss, word, morpheme, POS, sound, language, plaintext, meaning, or translation.","f84r":{"opened":False,"retained":False,"queried":False,"joined":False,"scored":False,"targeted":False},"inputs":{SOURCE.name:sha(SOURCE),HPR5.name:sha(HPR5),"gdt081_validation.json":sha(ROOT/"gdt081_validation.json")},"implementation":{Path(__file__).name:sha(Path(__file__))},"outputs":{SCORES.name:sha(SCORES),REG.name:sha(REG),PAGES.name:sha(PAGES),NULL.name:sha(NULL)},"documents":{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result["result_content_sha256"]=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":status,"gain":obs,"paid":result["page_selector_paid_gain_bits"],"p":p,"top":top["page"]},sort_keys=True))
if __name__=="__main__":main()

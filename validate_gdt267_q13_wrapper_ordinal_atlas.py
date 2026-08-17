#!/usr/bin/env python3
"""Independent reconstruction for GDT267 wrapper/ordinal atlas."""
import csv,hashlib,itertools,json,math
from collections import Counter,defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent;SRC="gdt227_q13_abstract_interlinear.tsv";RES="gdt267_result.json";W=["NONE","ch","che","d","q","s","sh","t"]
def read(p):
 with (R/p).open(encoding="utf-8") as f:return list(csv.DictReader(f,delimiter="\t"))
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def corr(a,b):
 ma=sum(a)/len(a);mb=sum(b)/len(b);num=sum((x-ma)*(y-mb) for x,y in zip(a,b));den=math.sqrt(sum((x-ma)**2 for x in a)*sum((y-mb)**2 for y in b));return num/den if den else 0
def main():
 c=[]
 def ck(n,v):assert v,n;c.append(n)
 z=json.loads((R/RES).read_text())
 for g in ["inputs","documents","outputs","implementation"]:
  for p,h in z[g].items():ck("hash:"+p,sha(p)==h)
 q=dict(z);h=q.pop("content_hash");ck("content_hash",hashlib.sha256(json.dumps(q,sort_keys=True,separators=(",",":")).encode()).hexdigest()==h)
 src=read(SRC);ck("source_f84_free",src and all(not x["page"].startswith("f84") for x in src))
 rec=defaultdict(list);loc=defaultdict(set)
 for x in src:rec[(x["page"],x["record_id"])].append(x);loc[(x["page"],x["record_id"])].add(x["locus"])
 bp=defaultdict(list)
 for k,v in loc.items():
  if len(v)>=4:bp[k[0]].append(k[1])
 pages={p:sorted(v) for p,v in bp.items() if len(v)==2};ck("panel",len(pages)==9)
 counts={};diff={w:[] for w in W};lr=[];expected_detail={}
 for p,rs in sorted(pages.items()):
  cc=[]
  for role,rid in zip(["EARLIER","LATER"],rs):
   x=Counter(z.split(":")[0] for r in rec[(p,rid)] for z in r["compiler_cells"].split("|"));n=sum(x.values());ck("wrapper_vocab:"+p+role,set(x)<=set(W));cc.append((x,n))
   for w in W:expected_detail[(p,rid,w)]=(role,x[w],n,x[w]/n)
  counts[p]=cc;lr.append(math.log(cc[0][1]/cc[1][1]))
  for w in W:diff[w].append(cc[0][0][w]/cc[0][1]-cc[1][0][w]/cc[1][1])
 detail=read("gdt267_wrapper_page_rates.tsv");ck("detail_rows",len(detail)==144 and len({(x['page'],x['record_id'],x['wrapper']) for x in detail})==144)
 for x in detail:
  role,n,tot,rate=expected_detail[(x['page'],x['record_id'],x['wrapper'])];ck("detail:"+x['page']+x['record_id']+x['wrapper'],x['ordinal_class']==role and int(x['wrapper_count'])==n and int(x['group_count'])==tot and abs(float(x['rate_per_group'])-rate)<5e-10)
 def st(d):
  den=math.sqrt(sum(x*x for x in d));return abs(sum(d))/den if den else 0
 obs={w:st(diff[w]) for w in W};vals={w:[] for w in W};maxv=[]
 for bits in itertools.product([-1,1],repeat=9):
  x={w:st([s*v for s,v in zip(bits,diff[w])]) for w in W}
  for w in W:vals[w].append(x[w])
  maxv.append(max(x.values()))
 atlas={x['wrapper']:x for x in read("gdt267_wrapper_atlas.tsv")};ck("atlas_vocab",set(atlas)==set(W))
 for w in W:
  d=diff[w];x=atlas[w];loo=[sum(d[:i]+d[i+1:])/8 for i in range(9)];num=den=0
  for p in sorted(pages):
   (ce,ne),(cl,nl)=counts[p];a=ce[w];b=ne-a;cc=cl[w];dd=nl-cc;n=ne+nl;num+=a*dd/n;den+=b*cc/n
  held=sum((sum(d[:i]+d[i+1:])/8>0)==(d[i]>0) for i in range(9) if d[i]!=0);lp=(1+sum(v>=obs[w]-1e-15 for v in vals[w]))/513;mp=(1+sum(v>=obs[w]-1e-15 for v in maxv))/513
  ck("atlas:"+w,abs(float(x['mean_paired_rate_difference'])-sum(d)/9)<5e-10 and int(x['positive_pages'])==sum(v>0 for v in d) and int(x['negative_pages'])==sum(v<0 for v in d) and int(x['held_page_direction_correct'])==held and abs(float(x['leave_one_page_mean_min'])-min(loo))<5e-10 and abs(float(x['leave_one_page_mean_max'])-max(loo))<5e-10 and abs(float(x['mantel_haenszel_odds_ratio'])-num/den)<5e-10 and abs(float(x['correlation_with_log_group_count_ratio'])-corr(lr,d))<5e-10 and abs(float(x['local_two_sided_inclusive_p'])-lp)<5e-10 and abs(float(x['max_eight_inclusive_p'])-mp)<5e-10)
 ck("headline",z['status']=="Q13_Q_WRAPPER_EARLIER_BARE_RENDERING_LATER_RECORD_ASSOCIATION" and z['q']['positive_pages']==9 and z['bare']['negative_pages']==9 and z['semantic_assignments']==0)
 v={"experiment":"GDT267_Q13_WRAPPER_ORDINAL_ATLAS","status":"PASS_INDEPENDENT_RECONSTRUCTION","checks_passed":len(c),"checks_failed":0,"result_sha256":sha(RES),"result_content_hash":z['content_hash'],"f84r":{"new_access":False,"used":False,"scored":False},"checks":c};v['content_hash']=hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest();(R/'gdt267_validation.json').write_text(json.dumps(v,indent=2,sort_keys=True)+'\n');print(json.dumps({"status":v['status'],"checks":len(c)},sort_keys=True))
if __name__=='__main__':main()

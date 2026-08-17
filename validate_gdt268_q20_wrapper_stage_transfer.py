#!/usr/bin/env python3
"""Independent reconstruction for GDT268 Q20 wrapper-stage transfer."""
import csv,hashlib,itertools,json,math
from collections import Counter,defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent;SRC="gdt127_q20_field_inventory.tsv";RES="gdt268_result.json";EDS=["ZL3b","IT2a","RF1b"];W=["q","NONE"]
def read(p):
 with (R/p).open(encoding="utf-8") as f:return list(csv.DictReader(f,delimiter="\t"))
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def st(d):
 den=math.sqrt(sum(x*x for x in d));return abs(sum(d))/den if den else 0
def main():
 c=[]
 def ck(n,v):assert v,n;c.append(n)
 z=json.loads((R/RES).read_text())
 for g in ["inputs","documents","outputs","implementation"]:
  for p,h in z[g].items():ck("hash:"+p,sha(p)==h)
 q=dict(z);h=q.pop("content_hash");ck("content_hash",hashlib.sha256(json.dumps(q,sort_keys=True,separators=(",",":")).encode()).hexdigest()==h)
 src=read(SRC);ck("source_f84_free",src and all(not x['page'].startswith('f84') for x in src))
 scores={(x['edition'],x['wrapper']):x for x in read('gdt268_q20_stage_scores.tsv')};ck('scores6',len(scores)==6)
 detail={(x['edition'],x['page'],x['stage'],x['wrapper']):x for x in read('gdt268_q20_stage_rates.tsv')};ck('detail_unique',len(detail)==156)
 for ed in EDS:
  by=defaultdict(set)
  for x in src:
   if x['edition']==ed:by[x['page']].add(int(x['star_ordinal']))
  ck('capacity:'+ed,len(by)==13 and sum(map(len,by.values()))==170)
  diff={w:[] for w in W};counts={}
  for page,ss0 in sorted(by.items()):
   ss=sorted(ss0);k=len(ss)//2;cc=[]
   for stage,keep in zip(['EARLY_HALF','LATE_HALF'],[set(ss[:k]),set(ss[-k:])]):
    x=Counter(cell[0] for r in src if r['edition']==ed and r['page']==page and int(r['star_ordinal']) in keep for cell in json.loads(r['compiler_skeleton']));n=sum(x.values());cc.append((x,n))
    for w in W:
     a=detail[(ed,page,stage,w)];ck('detail:'+ed+page+stage+w,int(a['wrapper_count'])==x[w] and int(a['group_count'])==n and int(a['selected_record_count'])==k and abs(float(a['rate_per_group'])-x[w]/n)<5e-10)
   counts[page]=cc
   for w in W:diff[w].append(cc[0][0][w]/cc[0][1]-cc[1][0][w]/cc[1][1])
  obs={w:st(diff[w]) for w in W};vals={w:[] for w in W};maxv=[]
  for bits in itertools.product([-1,1],repeat=13):
   a={w:st([s*v for s,v in zip(bits,diff[w])]) for w in W}
   for w in W:vals[w].append(a[w])
   maxv.append(max(a.values()))
  for w in W:
   d=diff[w];num=den=0
   for page in sorted(by):
    (ce,ne),(cl,nl)=counts[page];a=ce[w];b=ne-a;cc=cl[w];dd=nl-cc;n=ne+nl;num+=a*dd/n;den+=b*cc/n
   x=scores[(ed,w)];lp=(1+sum(v>=obs[w]-1e-15 for v in vals[w]))/8193;mp=(1+sum(v>=obs[w]-1e-15 for v in maxv))/8193
   ck('score:'+ed+w,abs(float(x['mean_page_rate_difference'])-sum(d)/13)<5e-10 and int(x['positive_pages'])==sum(v>0 for v in d) and int(x['negative_pages'])==sum(v<0 for v in d) and abs(float(x['mantel_haenszel_odds_ratio'])-num/den)<5e-10 and abs(float(x['local_two_sided_inclusive_p'])-lp)<5e-10 and abs(float(x['max_two_inclusive_p'])-mp)<5e-10)
 ck('headline',z['status']=='Q13_WRAPPER_STAGE_SAME_DIRECTION_WEAK_NONCONFIRMING_IN_Q20' and z['semantic_assignments']==0 and z['zl']['q']['positive_pages']==9 and z['zl']['NONE']['negative_pages']==9)
 v={'experiment':'GDT268_Q20_WRAPPER_STAGE_TRANSFER','status':'PASS_INDEPENDENT_RECONSTRUCTION','checks_passed':len(c),'checks_failed':0,'result_sha256':sha(RES),'result_content_hash':z['content_hash'],'f84r':{'new_access':False,'used':False,'scored':False},'checks':c};v['content_hash']=hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest();(R/'gdt268_validation.json').write_text(json.dumps(v,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':v['status'],'checks':len(c)},sort_keys=True))
if __name__=='__main__':main()

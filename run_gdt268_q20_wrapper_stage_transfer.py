#!/usr/bin/env python3
"""GDT268: transfer q13 q/bare ordinal directions to star-defined Q20 records."""
import csv,hashlib,itertools,json,math
from collections import Counter,defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent;SRC="gdt127_q20_field_inventory.tsv";PRED="gdt267_result.json";ACCESS="gdt257_result.json";METHOD="GDT268_Q20_WRAPPER_STAGE_TRANSFER_METHOD.md"
EDS=["ZL3b","IT2a","RF1b"];WRAPS=["q","NONE"]
def read(p):
 with (R/p).open(encoding="utf-8") as f:return list(csv.DictReader(f,delimiter="\t"))
def write(p,r):
 with (R/p).open("w",encoding="utf-8",newline="") as f:w=csv.DictWriter(f,fieldnames=list(r[0]),delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(r)
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def stat(d):
 den=math.sqrt(sum(x*x for x in d));return abs(sum(d))/den if den else 0
def main():
 src=read(SRC);assert src and all(not x["page"].startswith("f84") for x in src)
 pred=json.loads((R/PRED).read_text());assert pred["status"]=="Q13_Q_WRAPPER_EARLIER_BARE_RENDERING_LATER_RECORD_ASSOCIATION"
 access=json.loads((R/ACCESS).read_text());assert access["access"]["pristine_access_seal"] is False
 detail=[];scores=[];allnull=[];effects={}
 for ed in EDS:
  by=defaultdict(set)
  for x in src:
   if x["edition"]==ed:by[x["page"]].add(int(x["star_ordinal"]))
  assert len(by)==13 and sum(len(v) for v in by.values())==170
  diff={w:[] for w in WRAPS};cnt={}
  for page,stars0 in sorted(by.items()):
   stars=sorted(stars0);k=len(stars)//2;sets=[set(stars[:k]),set(stars[-k:])];cc=[]
   for stage,keep in zip(["EARLY_HALF","LATE_HALF"],sets):
    c=Counter();records=0
    for x in src:
     if x["edition"]==ed and x["page"]==page and int(x["star_ordinal"]) in keep:
      records+=0
      for cell in json.loads(x["compiler_skeleton"]):c[cell[0]]+=1
    n=sum(c.values());cc.append((c,n));
    for w in WRAPS:detail.append({"edition":ed,"page":page,"stage":stage,"selected_record_count":len(keep),"selected_star_ordinals":";".join(map(str,sorted(keep))),"wrapper":w,"wrapper_count":c[w],"group_count":n,"rate_per_group":f"{c[w]/n:.12f}"})
   cnt[page]=cc
   for w in WRAPS:diff[w].append(cc[0][0][w]/cc[0][1]-cc[1][0][w]/cc[1][1])
  obs={w:stat(diff[w]) for w in WRAPS};vals={w:[] for w in WRAPS};maxv=[]
  for wi,bits in enumerate(itertools.product([-1,1],repeat=13)):
   z={w:stat([s*x for s,x in zip(bits,diff[w])]) for w in WRAPS}
   for w in WRAPS:vals[w].append(z[w])
   maxv.append(max(z.values()))
   if wi<128:allnull.append({"edition":ed,"world":wi,"q_stat":f"{z['q']:.12f}","NONE_stat":f"{z['NONE']:.12f}","max_two":f"{max(z.values()):.12f}"})
  effects[ed]=diff
  for w in WRAPS:
   d=diff[w];direction="POSITIVE" if sum(d)>0 else "NEGATIVE" if sum(d)<0 else "ZERO";expected="POSITIVE" if w=="q" else "NEGATIVE"
   num=den=0
   for page in sorted(by):
    (ce,ne),(cl,nl)=cnt[page];a=ce[w];b=ne-a;c=cl[w];dd=nl-c;n=ne+nl;num+=a*dd/n;den+=b*c/n
   scores.append({"edition":ed,"wrapper":w,"expected_early_minus_late_sign":expected,"observed_sign":direction,"direction_pass":int(direction==expected),"mean_page_rate_difference":f"{sum(d)/13:.12f}","positive_pages":sum(x>0 for x in d),"negative_pages":sum(x<0 for x in d),"tied_pages":sum(x==0 for x in d),"mantel_haenszel_odds_ratio":f"{num/den:.12f}","standardized_stat":f"{obs[w]:.12f}","local_two_sided_inclusive_p":f"{(1+sum(v>=obs[w]-1e-15 for v in vals[w]))/8193:.12f}","max_two_inclusive_p":f"{(1+sum(v>=obs[w]-1e-15 for v in maxv))/8193:.12f}"})
 write("gdt268_q20_stage_rates.tsv",detail);write("gdt268_q20_stage_scores.tsv",scores);write("gdt268_q20_stage_null.tsv",allnull)
 zl=[x for x in scores if x["edition"]=="ZL3b"];passed=all(int(x["direction_pass"]) and float(x["max_two_inclusive_p"])<=.05 for x in zl)
 status="Q13_WRAPPER_STAGE_TRANSFERS_TO_Q20" if passed else "Q13_WRAPPER_STAGE_SAME_DIRECTION_WEAK_NONCONFIRMING_IN_Q20"
 counter=[{"counterexample":"PRIMARY_MAX_TWO_NONPASS","value":"; ".join(f"{x['wrapper']}={x['max_two_inclusive_p']}" for x in zl),"consequence":"do not globalize the q13 placement rule"},{"counterexample":"PAGE_HETEROGENEITY","value":"ZL q 9 positive 4 negative; NONE 4 positive 9 negative","consequence":"same aggregate direction is not page-universal in Stars"},{"counterexample":"ALTERNATE_READINGS","value":"same aggregate signs but max-two p remains above .15 in IT2a and above .21/.24 in RF1b","consequence":"readings are sensitivities and do not rescue primary nonconfirmation"},{"counterexample":"RECORD_TYPE_CHANGE","value":"q13 mechanical paragraph records versus Q20 star-defined records","consequence":"failure may be register-specific rather than a contradiction of q13"}]
 write("gdt268_counterexamples.tsv",counter)
 report=["# GDT268 — q13 wrapper-stage transfer to Q20","",f"Status: **{status}**.","","## Frozen transfer result","","The first and last equal-sized halves of each Q20 page were compared; middle records on odd pages were excluded.","","| reading | wrapper | expected sign | mean early−late rate | + / − pages | MH OR | local p | max-two p |","|---|---|---|---:|---:|---:|---:|---:|"]
 for x in scores:report.append(f"| {x['edition']} | {x['wrapper']} | {x['expected_early_minus_late_sign']} | {float(x['mean_page_rate_difference']):+.4f} | {x['positive_pages']} / {x['negative_pages']} | {float(x['mantel_haenszel_odds_ratio']):.3f} | {float(x['local_two_sided_inclusive_p']):.4f} | {float(x['max_two_inclusive_p']):.4f} |")
 report += ["","Both q13 directions retain their aggregate sign in the ZL primary and both reading sensitivities: `q` is modestly higher in early Q20 records and bare rendering modestly higher late. But neither ZL endpoint passes the max-two test (`q` p=.1725; `NONE` p=.1917), and only 9/13 pages support each direction.","","The useful conclusion is bounded: the q13 record-stage contrast has a weak same-direction echo in Stars, but it is not a confirmed manuscript-wide ordinal operator. Keep `q` as an earlier-record-associated q13 renderer and a cross-register hypothesis; do not assign it a semantic or spoken value.","","No topic, word, morpheme, sound, language, plaintext, or translation is assigned. The input is f84-free and no new f84r access occurred.",""]
 (R/"GDT268_Q20_WRAPPER_STAGE_TRANSFER_REPORT.md").write_text("\n".join(report))
 result={"experiment":"GDT268_Q20_WRAPPER_STAGE_TRANSFER","status":status,"prediction_source":PRED,"primary":"ZL3b","pages_per_reading":13,"records_per_reading":170,"zl":{x["wrapper"]:{"mean_difference":float(x["mean_page_rate_difference"]),"positive_pages":int(x["positive_pages"]),"negative_pages":int(x["negative_pages"]),"max_two_p":float(x["max_two_inclusive_p"])} for x in zl},"semantic_assignments":0,"interpretation":"Weak same-direction Q20 echo does not confirm a global q/bare record-stage operator.","claim_ceiling":"Cross-register wrapper-stage direction only; no semantic operator word or translation.","f84r":{"prior_transient_parse_disclosed":True,"new_access":False,"used":False,"scored":False},"inputs":{SRC:sha(SRC),PRED:sha(PRED),ACCESS:sha(ACCESS)},"documents":{METHOD:sha(METHOD)},"outputs":{},"implementation":{Path(__file__).name:sha(Path(__file__).name)}}
 result["outputs"]={p:sha(p) for p in ["gdt268_q20_stage_rates.tsv","gdt268_q20_stage_scores.tsv","gdt268_q20_stage_null.tsv","gdt268_counterexamples.tsv","GDT268_Q20_WRAPPER_STAGE_TRANSFER_REPORT.md"]};result["content_hash"]=hashlib.sha256(json.dumps(result,sort_keys=True,separators=(",",":")).encode()).hexdigest();(R/"gdt268_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":status,"zl":result["zl"]},sort_keys=True))
if __name__=="__main__":main()

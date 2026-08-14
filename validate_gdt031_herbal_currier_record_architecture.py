#!/usr/bin/env python3
"""Independent nonimporting validation of GDT031."""
from __future__ import annotations
import csv,functools,hashlib,itertools,json
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parent;RES=ROOT/"gdt031_result.json";VAL=ROOT/"gdt031_validation.json"
FLAGS=("TEXT_WRAPS_GRAPHIC","TEXT_AVOIDS_GRAPHIC","TEXT_INSIDE_GRAPHIC","TEXT_BETWEEN_GRAPHICS");PRIMARY=("FIELDS_PER_LINE","DY_CHAIN_RATE","SINGLETON_CLOSED_RATE","OPEN_TAIL_AFTER_DY_RATE","DIRECT_MINUS_INSERTIONAL_QL_RATE")
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def read(n):
 with (ROOT/n).open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def guarded(path,pages):
 out=[]
 with path.open(encoding="utf-8",newline="")as h:
  header=h.readline();idx=header.rstrip("\n").split("\t").index("page")
  for line in h:
   if line.split("\t")[idx]in pages:out.extend(csv.DictReader([header,line],delimiter="\t"))
 return {r["page"]:r for r in out}
def profile(s):return"MIXED"if"α:"in s and"β:"in s else"ALPHA"if"α:"in s else"BETA"if"β:"in s else"UNCLASSIFIED"
def ql(f,p):return any(x in f for x in p)
def metrics(rows):
 lines=defaultdict(list)
 for r in rows:lines[r["locus"]].append(r)
 checkpoints=fields=dy_next=chains=single=closed=withdy=multi=open_tail=0;lens=[];direct=[];insert=[]
 for line in lines.values():
  line.sort(key=lambda r:int(r["group_index"]));states=[r["record_state"]for r in line];dy=[i for i,s in enumerate(states)if s=="DY_RESOLUTION"];checkpoints+=len(dy);fields+=len(dy)+int(not dy or states[-1]!="DY_RESOLUTION");withdy+=int(bool(dy));multi+=int(len(dy)>=2);dy_next+=sum(s=="DY_RESOLUTION"for s in states[:-1]);chains+=sum(a==b=="DY_RESOLUTION"for a,b in zip(states,states[1:]));open_tail+=int(bool(dy)and states[-1]!="DY_RESOLUTION");start=0
  for i in dy:closed+=1;lens.append(i-start+1);single+=int(i==start);start=i+1
  for i,r in enumerate(line):
   f=r["family_surface"]
   if ql(f,("QJB","QKB","LJB","LKB")):direct.append(("QJB"in f or"QKB"in f,i>0 and states[i-1]=="DY_RESOLUTION"))
   if ql(f,("QJAB","QKAB","LJAB","LKAB")):insert.append(("QJAB"in f or"QKAB"in f,i>0 and states[i-1]=="DY_RESOLUTION"))
 n=len(lines);groups=sum(len(v)for v in lines.values());rate=lambda a,b:a/b if b else 0.
 return {"LINES":n,"GROUPS":groups,"FIELDS_PER_LINE":fields/n,"DY_PER_LINE":checkpoints/n,"DY_LINE_RATE":withdy/n,"MULTI_DY_LINE_RATE":multi/n,"DY_CHAIN_RATE":rate(chains,dy_next),"SINGLETON_CLOSED_RATE":rate(single,closed),"MEAN_CLOSED_FIELD_LENGTH":rate(sum(lens),len(lens)),"OPEN_TAIL_AFTER_DY_RATE":rate(open_tail,withdy),"DIRECT_QL_RATE":len(direct)/groups,"INSERTIONAL_QL_RATE":len(insert)/groups,"DIRECT_MINUS_INSERTIONAL_QL_RATE":len(direct)/groups-len(insert)/groups,"DIRECT_Q_SHARE":rate(sum(q for q,p in direct),len(direct)),"INSERTIONAL_Q_SHARE":rate(sum(q for q,p in insert),len(insert)),"DIRECT_POST_DY_RATE":rate(sum(p for q,p in direct),len(direct)),"INSERTIONAL_POST_DY_RATE":rate(sum(p for q,p in insert),len(insert))}
def cost(a,b,role,ann):
 x,y=role[a],role[b];ta=set(ann[a]["source_tags"].split(";"));tb=set(ann[b]["source_tags"].split(";"));return abs(int(x["P_count"])-int(y["P_count"]))+2*abs(int(x["paragraph_start_count"])-int(y["paragraph_start_count"]))+4*int((int(x["L_count"])>0)!=(int(y["L_count"])>0))+2*sum((f in ta)!=(f in tb)for f in FLAGS)
def folio_match(pages,page_rows,profiles,role,ann):
 A=sorted(p for p in pages if page_rows[p][0]["currier"]=="A");B=sorted(p for p in pages if page_rows[p][0]["currier"]=="B");options=defaultdict(list)
 for b in B:
  for a in A:
   c=cost(a,b,role,ann)
   if profiles[a]==profiles[b]and profiles[b]!="BETA"and c<=4:options[page_rows[b][0]["physical_folio"]].append((page_rows[a][0]["physical_folio"],a,b,profiles[b],c))
 bfolios=sorted(options,key=lambda f:(len(options[f]),f))
 @functools.lru_cache(None)
 def solve(i,used):
  if i==len(bfolios):return(0,0,())
  best=solve(i+1,used)
  for af,a,b,p,c in options[bfolios[i]]:
   if af in used:continue
   z=solve(i+1,tuple(sorted(used+(af,))));candidate=(z[0]+1,z[1]+c,tuple(sorted(z[2]+((a,b,p,c),))))
   if(-candidate[0],candidate[1],candidate[2])<(-best[0],best[1],best[2]):best=candidate
  return best
 return sum(len(v)for v in options.values()),solve(0,())[2]
def signflip(v):
 obs=sum(v)/len(v);world=[sum(s*x for s,x in zip(z,v))/len(v)for z in itertools.product((-1,1),repeat=len(v))];return obs,sum(x>=obs-1e-15 for x in world)/len(world)
def close(a,b):return abs(float(a)-float(b))<7e-10
def main():
 checks=[];result=json.loads(RES.read_text());body=dict(result);digest=body.pop("result_content_sha256");checks +=[("schema",result["schema"]=="GDT031_HERBAL_CURRIER_RECORD_ARCHITECTURE_RESULT_V1"),("content",digest==csha(body)),("status",result["status"]=="HERBAL_B_RECORD_DENSITY_SUPPORTED_FULL_RECORD_ARCHITECTURE_NOT_SUPPORTED")]
 for section in("inputs","implementation","outputs"):
  for name,digest in result[section].items():checks.append((f"hash:{section}:{name}",sha(ROOT/name)==digest))
 inv=read("gdt016_group_state_inventory.tsv");checks +=[("inventory",len(inv)==15592),("f84r_inventory",not any(r["locus"].startswith("f84r")for r in inv))];page_rows=defaultdict(list)
 for r in inv:
  if r["section"]=="H":page_rows[r["page"]].append(r)
 pages=set(page_rows);base=ROOT/"experiments/semantic_assumptions/results";ann=guarded(base/"existing_human_page_annotations.tsv",pages);role=guarded(base/"existing_human_page_role_matrix.tsv",pages);checks +=[("guarded_sets",set(ann)==set(role)==pages and"f84r"not in pages),("guarded_hashes",result["guarded_source_subsets"]=={"existing_human_page_annotations_rows":len(ann),"existing_human_page_annotations_canonical_sha256":csha([ann[p]for p in sorted(ann)]),"existing_human_page_role_matrix_rows":len(role),"existing_human_page_role_matrix_canonical_sha256":csha([role[p]for p in sorted(role)])})]
 m={p:metrics(rows)for p,rows in page_rows.items()};profiles={p:profile(ann[p]["illustrations"])for p in pages};expected_pages=[]
 for p in sorted(pages):
  r=page_rows[p][0];x=role[p];row={"page":p,"physical_folio":r["physical_folio"],"currier":r["currier"],"hand":r["hand"],"illustration_profile":profiles[p],"catalogue_prose_lines":x["P_count"],"paragraph_starts":x["paragraph_start_count"],"catalogue_label_presence":str(int(int(x["L_count"])>0)),"special_layout_flags":"|".join(f for f in FLAGS if f in ann[p]["source_tags"].split(";"))};row.update({k:(str(v)if isinstance(v,int)else f"{v:.12f}")for k,v in m[p].items()});row["claim_state"]="HERBAL_PAGE_FORMAL_ARCHITECTURE_NOT_MEANING";expected_pages.append(row)
 checks.append(("page_inventory",expected_pages==read("gdt031_herbal_page_architecture.tsv")));eligible_edges,candidate=folio_match(pages,page_rows,profiles,role,ann)
 expected_match=[]
 for i,(a,b,pr,c) in enumerate(candidate,1):expected_match.append({"pair_id":f"HP{i:02d}","currier_a_page":a,"currier_a_folio":page_rows[a][0]["physical_folio"],"currier_b_page":b,"currier_b_folio":page_rows[b][0]["physical_folio"],"illustration_profile":pr,"match_cost":str(c),"a_prose_lines":role[a]["P_count"],"b_prose_lines":role[b]["P_count"],"a_paragraph_starts":role[a]["paragraph_start_count"],"b_paragraph_starts":role[b]["paragraph_start_count"],"classified_profile":str(int(pr!="UNCLASSIFIED")),"claim_state":"VISIBLE_PROFILE_LAYOUT_MATCH_NOT_IDENTICAL_IMAGE"})
 checks.append(("matches",expected_match==read("gdt031_matched_herbal_pages.tsv")and len({r["currier_a_folio"]for r in expected_match})==len({r["currier_b_folio"]for r in expected_match})==len(expected_match)));kept=expected_match;stored={r["feature"]:r for r in read("gdt031_matched_architecture_tests.tsv")}
 supplementary=("DY_PER_LINE","DY_LINE_RATE","MULTI_DY_LINE_RATE","MEAN_CLOSED_FIELD_LENGTH","DIRECT_QL_RATE","INSERTIONAL_QL_RATE","DIRECT_Q_SHARE","INSERTIONAL_Q_SHARE","DIRECT_POST_DY_RATE","INSERTIONAL_POST_DY_RATE")
 for feature in PRIMARY+supplementary:
  d=[m[r["currier_b_page"]][feature]-m[r["currier_a_page"]][feature]for r in kept];e,p=signflip(d);r=stored[feature];classified=[x for x,z in zip(d,kept)if z["classified_profile"]=="1"];ce,cp=signflip(classified);checks.append((f"test:{feature}",int(r["matched_pairs"])==len(kept)and close(r["b_minus_a_mean"],e)and int(r["positive_pairs"])==sum(x>0 for x in d)and int(r["zero_pairs"])==sum(x==0 for x in d)and close(r["one_sided_exact_p"],p)and(r["five_test_adjusted_p"]=="NOT_APPLICABLE"if feature not in PRIMARY else close(r["five_test_adjusted_p"],min(1,p*5)))and int(r["classified_only_pairs"])==len(classified)and close(r["classified_only_b_minus_a"],ce)and int(r["classified_only_positive_pairs"])==sum(x>0 for x in classified)and int(r["classified_only_zero_pairs"])==sum(x==0 for x in classified)and close(r["classified_only_exact_p"],cp)and(r["classified_only_five_test_adjusted_p"]=="NOT_APPLICABLE"if feature not in PRIMARY else close(r["classified_only_five_test_adjusted_p"],min(1,cp*5)))))
 def same(left,right):
  for k,v in right.items():
   if str(left[k])==v:continue
   try:
    if close(left[k],v):continue
   except (TypeError,ValueError):pass
   return False
  return True
 checks +=[("counts",result["herbal_pages"]=={"A":95,"B":32}and result["eligible_match_edges"]==eligible_edges==84 and result["matched_folio_pairs"]==len(kept)==8 and result["classified_pairs"]==4),("profiles",result["illustration_profiles"]=={"A":{"ALPHA":84,"MIXED":4,"UNCLASSIFIED":7},"B":{"ALPHA":2,"BETA":18,"MIXED":2,"UNCLASSIFIED":10}}),("hands",result["hand_confound"]=={"A":["1"],"B":["2","3","5"]}),("primary_snapshots",all(same(result["primary_tests"][k],stored[k])for k in PRIMARY)),("flags",result["f84r"]=={"input_contains_rows":False,"annotation_rows_retained":False,"opened":False,"retained":False,"joined":False,"scored":False})]
 report=" ".join((ROOT/"GDT031_HERBAL_CURRIER_RECORD_ARCHITECTURE_REPORT.md").read_text().lower().split());ledger=(ROOT/"GDT002_YOLO_LEDGER.tsv").read_text();checks +=[("claims",all(x in report for x in("not causal","full record architecture not supported","currier cannot be separated from hand","f84r was not opened","no role"))),("ledger",ledger.count("GDT031_CKPT001")==1)]
 failures=[n for n,ok in checks if not ok];validation={"schema":"GDT031_HERBAL_CURRIER_RECORD_ARCHITECTURE_VALIDATION_V1","status":"PASS"if not failures else"FAIL","checks":len(checks),"failures":failures,"result_sha256":sha(RES),"validator_sha256":sha(Path(__file__)),"scope":"Independent reconstruction of 127 Herbal page metrics, guarded human metadata subsets, optimal profile/layout matching, fifteen paired tests, hashes, f84r exclusion, ledger, and claim ceiling."};VAL.write_text(json.dumps(validation,indent=2,sort_keys=True)+"\n");print(json.dumps(validation,sort_keys=True));
 if failures:raise SystemExit(1)
if __name__=="__main__":main()

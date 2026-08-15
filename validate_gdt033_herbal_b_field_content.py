#!/usr/bin/env python3
"""Independent nonimporting reconstruction of GDT033."""
from __future__ import annotations
import csv,hashlib,json,random,re
from collections import Counter,defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parent
RES=ROOT/"gdt033_result.json";VAL=ROOT/"gdt033_validation.json";N=10000;SEED=330033
def read(name):
 with (ROOT/name).open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def close(a,b):return abs(float(a)-float(b))<7e-10
def guarded_rows(path,pages):
 out=[]
 with path.open(encoding="utf-8",newline="")as h:
  header=h.readline();idx=header.rstrip("\n").split("\t").index("page")
  for line in h:
   if line.split("\t")[idx]not in pages:continue
   out.append(next(csv.DictReader([header,line],delimiter="\t")))
 return out
def rules():
 return {
 "DAISY_CUP":lambda a:"β: 'daisy in a cup'"in a["illustrations"],
 "BROAD_CALYX":lambda a:"β: broad many-fingered calyx"in a["illustrations"],
 "FLOWER_HEAD_ARCHITECTURE":lambda a:"β: 'daisy in a cup'"in a["illustrations"]or"β: broad many-fingered calyx"in a["illustrations"],
 "GRASS":lambda a:"β: 'grass'"in a["illustrations"],
 "ROOT_PLATFORM":lambda a:"β: root platform"in a["illustrations"],
 "LEAVES_ONE_SIDE":lambda a:"β: all leaves point to one side"in a["illustrations"],
 "FUSED_PARALLEL_LEAVES":lambda a:"β: leaves parallel and fused together on one stalk"in a["illustrations"],
 "BULB_OR_TUBER_ROOT":lambda a:bool(re.search(r"\bbulb|\btuber",a["illustrations"],re.I)),
 "LARGE_OR_EXTENSIVE_ROOT":lambda a:bool(re.search(r"large root|large roots|extensive roots|huge[^.]{0,40}root",a["illustrations"],re.I)),
 "MULTIPLE_PLANTS":lambda a:bool(re.search(r"two plants|two different plants|two of the same plants|row of plants|many plants",a["illustrations"],re.I)),
 "BLUE_FLOWERS_OR_BUDS":lambda a:"blue"in a["illustrations"].lower()and bool(re.search(r"flower|bud",a["illustrations"],re.I)),
 "FINGERED_OR_FRILLED_LEAVES":lambda a:bool(re.search(r"fingered leaves|frilled fingered leaves|leaves (?:ending in|with)[^.]{0,20}(?:finger|figer)|leaves are similar, with many fingers",a["illustrations"],re.I)),
 "MULTIPLE_STEMS_OR_STALKS":lambda a:bool(re.search(r"(two|three|four|several) (stems|stalks)",a["illustrations"],re.I)),
 "TEXT_SPLIT_OR_INTERRUPTED":lambda a:bool(re.search(r"split by the plant|interrupted by the top of the plant|broken up by the plant",a["text_description"],re.I)),
 "TEXT_AVOIDS_DRAWING":lambda a:"avoid"in a["text_description"].lower(),
 "TEXT_ABOVE_PLANT":lambda a:bool(re.search(r"above the plant|above the drawing|above the dawing",a["text_description"],re.I))}
def difference(rate,state,pages):
 yes=[rate[p]for p in pages if state[p]];no=[rate[p]for p in pages if not state[p]]
 return sum(yes)/len(yes)-sum(no)/len(no)
def scan(hosts,features,rates,states,pages,arch):
 keys=[(h,f)for h in hosts for f in features]
 observed={k:difference(rates[k[0]],{p:states[p][k[1]]for p in pages},pages)for k in keys}
 strata=defaultdict(list)
 for p in pages:strata[(arch[p]["hand"],arch[p]["illustration_profile"])].append(p)
 for x in strata.values():x.sort()
 rng=random.Random(SEED+len(pages));null={k:[]for k in keys}
 for _ in range(N):
  shuffled={}
  for key in sorted(strata):
   source=strata[key];target=source[:];rng.shuffle(target)
   for p,q in zip(source,target):shuffled[p]=states[q]
  for h,f in keys:null[h,f].append(difference(rates[h],{p:shuffled[p][f]for p in pages},pages))
 stats={}
 for k in keys:
  mu=sum(null[k])/N;sd=(sum((x-mu)**2 for x in null[k])/N)**.5;z=(observed[k]-mu)/sd if sd else 0
  stats[k]={"effect":observed[k],"z":z,"local":(1+sum(abs(x-mu)>=abs(observed[k]-mu)-1e-15 for x in null[k]))/(N+1),"mu":mu,"sd":sd}
 maxz=[max(abs((null[k][i]-stats[k]["mu"])/stats[k]["sd"])if stats[k]["sd"]else 0 for k in keys)for i in range(N)]
 folios=sorted({arch[p]["physical_folio"]for p in pages})
 for k in keys:
  s=stats[k];s["maxT"]=(1+sum(x>=abs(s["z"])-1e-15 for x in maxz))/(N+1);loo=[]
  for folio in folios:
   keep=[p for p in pages if arch[p]["physical_folio"]!=folio]
   loo.append(difference(rates[k[0]],{p:states[p][k[1]]for p in pages},keep))
  s["lofo_min"]=min(loo);s["lofo_max"]=max(loo)
 return stats
def main():
 checks=[];result=json.loads(RES.read_text());body=dict(result);digest=body.pop("result_content_sha256")
 checks +=[("schema",result["schema"]=="GDT033_HERBAL_B_FIELD_CONTENT_RESULT_V1"),("content",digest==csha(body)),("status",result["status"]=="CKHY_FUSED_LEAF_CONFIGURATION_CORE_PROVISIONAL_POSTSELECTED")]
 for section in ("inputs","implementation","outputs"):
  for name,d in result[section].items():checks.append((f"hash:{section}:{name}",sha(ROOT/name)==d))
 inv=read("gdt016_group_state_inventory.tsv");checks +=[("inventory",len(inv)==15592),("f84_inventory",not any(r["locus"].startswith("f84r")for r in inv))]
 b=[r for r in inv if r["section"]=="H"and r["currier"]=="B"];pages=sorted({r["page"]for r in b});arch={r["page"]:r for r in read("gdt031_herbal_page_architecture.tsv")if r["currier"]=="B"}
 lines=defaultdict(list)
 for r in b:lines[r["locus"]].append(r)
 fields=[]
 for locus,rowset in lines.items():
  rowset.sort(key=lambda r:int(r["group_index"]));start=ordinal=0
  for i,r in enumerate(rowset):
   if r["record_state"]!="DY_RESOLUTION":continue
   if ordinal>=1:fields.append((locus,ordinal,rowset[start:i+1]))
   start=i+1;ordinal+=1
 stored_fields=read("gdt033_herbal_b_additional_fields.tsv");checks +=[("field_count",len(fields)==len(stored_fields)==160),("singleton",sum(len(x[2])==1 for x in fields)==88),("field_pages",len({x[2][-1]["page"]for x in fields})==26)]
 cluster=defaultdict(lambda:{"fields":set(),"occ":0,"close":0,"pages":set(),"folios":set(),"tokens":set(),"prefixes":set(),"states":set(),"templates":set()});page_total=Counter();page_host=Counter()
 for field_id,(locus,ordinal,segment)in enumerate(fields,1):
  saved=stored_fields[field_id-1];expected_tokens="|".join(r["token"]for r in segment);expected_hosts="|".join(r["residual_host"]for r in segment)
  checks.append((f"field:{field_id}",saved["field_id"]==f"HBF{field_id:03d}"and saved["locus"]==locus and int(saved["additional_field_index"])==ordinal and saved["tokens"]==expected_tokens and saved["residual_hosts"]==expected_hosts))
  page=segment[-1]["page"];page_total[page]+=1;seen=set();template=">".join(r["record_state"]for r in segment)
  for i,r in enumerate(segment):
   h=r["residual_host"];x=cluster[h];x["fields"].add(field_id);x["occ"]+=1;x["close"]+=i==len(segment)-1;x["pages"].add(page);x["folios"].add(r["physical_folio"]);x["tokens"].add(r["token"]);x["prefixes"].add(r["stripped_prefix"]);x["states"].add(r["record_state"]);x["templates"].add(template);seen.add(h)
  for h in seen:page_host[page,h]+=1
 stored_clusters={r["residual_host"]:r for r in read("gdt033_field_host_clusters.tsv")};eligible=[]
 for h,x in cluster.items():
  e=len(x["fields"])>=5 and len(x["pages"])>=4 and(len(x["tokens"])>=2 or len(x["prefixes"])>=2)
  if e:eligible.append(h)
  row=stored_clusters[h];checks.append((f"cluster:{h}",int(row["additional_field_occurrences"])==len(x["fields"])and int(row["raw_group_occurrences"])==x["occ"]and int(row["closing_occurrences"])==x["close"]and int(row["field_template_count"])==len(x["templates"])and int(row["eligible_candidate"])==e))
 eligible.sort();checks.append(("eligible",eligible==['aiin','ar','ckhy','dy','e','ke','o','okal','okar','okch','oke','okee','ol','otch','ote','y']))
 ann_rows=guarded_rows(ROOT/"experiments/semantic_assumptions/results/existing_human_page_annotations.tsv",set(pages)|{"f52r"});ann={r["page"]:r for r in ann_rows};exact=guarded_rows(ROOT/"experiments/semantic_assumptions/results/existing_human_exact_locus_annotations.tsv",set(pages));checks +=[("annotation_guard",set(ann)==set(pages)|{"f52r"}and"f84r"not in ann),("exact_label_capacity",len(exact)==4 and not any("LABEL"in r["object_tags"].split(";")for r in exact)),("guard_hashes",result["guarded_human_subsets"]["page_annotations"]=={"rows":33,"canonical_sha256":csha([ann[p]for p in sorted(ann)])}and result["guarded_human_subsets"]["exact_locus_annotations"]=={"rows":4,"canonical_sha256":csha(exact)})]
 rule=rules();states={p:{name:int(fn(ann[p]))for name,fn in rule.items()}for p in pages};feature="FUSED_PARALLEL_LEAVES";checks.append(("feature_capacity",sum(states[p][feature]for p in pages)==12 and rule[feature](ann["f52r"])))
 add_pages=sorted(page_total);add_rates={h:{p:page_host[p,h]/page_total[p]for p in add_pages}for h in eligible};full_total=Counter(r["page"]for r in b);full_count=Counter((r["page"],r["residual_host"])for r in b);full_rates={h:{p:full_count[p,h]/full_total[p]for p in pages}for h in eligible}
 astat=scan(eligible,sorted(rule),add_rates,states,add_pages,arch);fstat=scan(eligible,sorted(rule),full_rates,states,pages,arch);lead=next(r for r in read("gdt033_core_visual_associations.tsv")if r["host"]=="ckhy"and r["visual_feature"]==feature);a=astat["ckhy",feature];f=fstat["ckhy",feature]
 checks +=[("lead_additional",close(lead["additional_effect"],a["effect"])and close(lead["additional_local_p"],a["local"])and close(lead["additional_maxT_p"],a["maxT"])),("lead_full",close(lead["full_b_effect"],f["effect"])and close(lead["full_b_local_p"],f["local"])and close(lead["full_b_maxT_p"],f["maxT"])and close(lead["full_b_lofo_min"],f["lofo_min"])and close(lead["full_b_lofo_max"],f["lofo_max"])),("lead_counts",sum(full_count[p,"ckhy"]for p in pages)==23 and sum(full_count[p,"ckhy"]>0 for p in pages)==13 and int(lead["full_b_hit_pages"])==8 and int(lead["full_b_counterexample_pages"])==5 and int(lead["full_b_hit_folios"])==7),
 ("selected_snapshot",result["selected_core"]["host"]=="ckhy"and close(result["selected_core"]["full_b_maxT_p"],f["maxT"])and result["selected_core"]["feature_hit_folios"]==7),
 ("f52_counter",not any(r["residual_host"]=="ckhy"for r in inv if r["page"]=="f52r"))]
 report=" ".join((ROOT/"GDT033_HERBAL_B_FIELD_CONTENT_REPORT.md").read_text().lower().split());ledger=(ROOT/"GDT002_YOLO_LEDGER.tsv").read_text()
 checks +=[("claim_ceiling",all(x in report for x in("postselected-library maxt p=0.90691","not confirmation","no word, morpheme, pos, sound, language, plaintext, or translation","f84r was not opened"))),("ledger",ledger.count("GDT033_CKPT001")==1),("f84_result",result["f84r"]=={"formal_input_contains_rows":False,"opened":False,"retained":False,"joined":False,"scored":False})]
 failures=[name for name,ok in checks if not ok];validation={"schema":"GDT033_HERBAL_B_FIELD_CONTENT_VALIDATION_V1","status":"PASS"if not failures else"FAIL","checks":len(checks),"failures":failures,"result_sha256":sha(RES),"validator_sha256":sha(Path(__file__)),"scope":"Independent reconstruction of all 160 additional fields and host clusters, guarded human capacity, CKHY full/additional effects, 20,000 matched permutation worlds, LOFO robustness, hashes, ledger, f84r exclusion, and claim ceiling."};VAL.write_text(json.dumps(validation,indent=2,sort_keys=True)+"\n");print(json.dumps(validation,sort_keys=True))
 if failures:raise SystemExit(1)
if __name__=="__main__":main()

#!/usr/bin/env python3
"""Join frozen Q20 density predictors to the fixed GDT271 q page score."""
import csv,hashlib,json,math,random,statistics
from pathlib import Path
R=Path(__file__).resolve().parent;PRED="gdt272_frozen_prediction.json";XFILE="gdt272_frozen_density_predictors.tsv";YFILE="gdt271_page_scores.tsv";METHOD="GDT272_Q_DENSITY_MECHANISM_METHOD.md"
FEATURES=[("GROUP_COUNT_LOG_RATIO","group_count_log_ratio"),("FIELD_COUNT_LOG_RATIO","field_count_log_ratio"),("LINE_COUNT_LOG_RATIO","line_count_log_ratio")]
def read(name):
 with (R/name).open(encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def write(name,rows):
 with (R/name).open("w",encoding="utf-8",newline="") as h:w=csv.DictWriter(h,fieldnames=list(rows[0]),delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def sha(name):return hashlib.sha256((R/name).read_bytes()).hexdigest()
def chash(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def pearson(a,b):
 ma=sum(a)/len(a);mb=sum(b)/len(b);num=sum((x-ma)*(y-mb) for x,y in zip(a,b));den=math.sqrt(sum((x-ma)**2 for x in a)*sum((y-mb)**2 for y in b));return num/den if den else 0.0
def ranks(values):
 order=sorted(range(len(values)),key=lambda i:(values[i],i));out=[0.0]*len(values);i=0
 while i<len(order):
  j=i+1
  while j<len(order) and values[order[j]]==values[order[i]]:j+=1
  rank=(i+j-1)/2+1
  for k in range(i,j):out[order[k]]=rank
  i=j
 return out
def main():
 pred=json.loads((R/PRED).read_text());stored=pred.pop("content_hash");assert stored==chash(pred) and pred["freeze_status"]=="PREDICTORS_FROZEN_BEFORE_GDT271_PAGE_SCORE_JOIN";xrows=read(XFILE);yrows=[x for x in read(YFILE) if x["edition"]=="ZL3b" and x["variant"]=="PAGE_HOST_PAGE_OTHER_COMPILER"];ymap={x["page"]:float(x["conditional_score"]) for x in yrows};assert len(xrows)==len(ymap)==13 and {x["page"] for x in xrows}==set(ymap)
 pages=[x["page"] for x in xrows];y=[ymap[p] for p in pages];joined=[]
 for x in xrows:joined.append({**x,"q_conditional_score":f"{ymap[x['page']]:.12f}","outcome_source":"GDT271_ZL_PRIMARY_PAGE_SCORE"})
 write("gdt272_density_outcome_join.tsv",joined)
 seed=int(hashlib.sha256(pred["null_seed_literal"].encode()).hexdigest()[:16],16);rng=random.Random(seed);worlds=[]
 for _ in range(pred["null_worlds"]):
  perm=y[:];rng.shuffle(perm);worlds.append([pearson([float(x[col]) for x in xrows],perm) for _,col in FEATURES])
 maxima=[max(v) for v in worlds];tests=[]
 for index,(name,col) in enumerate(FEATURES):
  x=[float(row[col]) for row in xrows];r=pearson(x,y);rho=pearson(ranks(x),ranks(y));mx=sum(x)/len(x);my=sum(y)/len(y);slope=sum((a-mx)*(b-my) for a,b in zip(x,y))/sum((a-mx)**2 for a in x);agreement=sum(a*b>0 for a,b in zip(x,y));scored=sum(a!=0 and b!=0 for a,b in zip(x,y));loo=[pearson(x[:i]+x[i+1:],y[:i]+y[i+1:]) for i in range(13)];local=(1+sum(v[index]>=r-1e-15 for v in worlds))/(len(worlds)+1);maxp=(1+sum(v>=r-1e-15 for v in maxima))/(len(worlds)+1);values=sorted(v[index] for v in worlds)
  tests.append({"predictor":name,"pearson_r":f"{r:.12f}","spearman_rho":f"{rho:.12f}","linear_slope":f"{slope:.12f}","sign_agreements":agreement,"sign_scored":scored,"positive_leave_one_page":sum(v>0 for v in loo),"negative_leave_one_page":sum(v<0 for v in loo),"loo_min_r":f"{min(loo):.12f}","loo_max_r":f"{max(loo):.12f}","local_directional_p":f"{local:.12f}","max_three_directional_p":f"{maxp:.12f}","null_mean_r":f"{statistics.mean(v[index] for v in worlds):.12f}","null_q95_r":f"{values[int(.95*len(values))-1]:.12f}","semantic_value":"UNASSIGNED"})
 write("gdt272_density_tests.tsv",tests)
 primary=tests[0];gate=float(primary["pearson_r"])>0 and int(primary["sign_agreements"])>=pred["primary_gate"]["sign_agreement_min"] and int(primary["positive_leave_one_page"])>=pred["primary_gate"]["positive_leave_one_page_min"] and float(primary["max_three_directional_p"])<=pred["primary_gate"]["max_three_p_max"]
 status="Q_DENSITY_EXPANSION_MECHANISM_SUPPORTED_IN_Q20" if gate else "Q_DENSITY_EXPANSION_MECHANISM_NOT_SUPPORTED_IN_Q20"
 counter=[{"counterexample":"PRIMARY_GATE","value":f"r {primary['pearson_r']} signs {primary['sign_agreements']}/13 LOO+ {primary['positive_leave_one_page']}/13 max3 {primary['max_three_directional_p']}","consequence":"status follows the published group-density gate"},{"counterexample":"Q13_RATIONALE_EXPOSED","value":"GDT267 correlation .860","consequence":"direction was motivated by q13 and this is a cross-register mechanism test"},{"counterexample":"THIRTEEN_PAGES","value":"small page-level panel","consequence":"large single-page leverage is reported through all leave-one-page correlations"},{"counterexample":"FIELD_LINE_COLLINEARITY","value":"group field and line ratios are correlated document-size measures","consequence":"three predictors are sensitivities rather than independent evidence"},{"counterexample":"NO_SEMANTIC_OUTCOME","value":"q conditional record-stage score","consequence":"density association cannot identify q meaning"}];write("gdt272_counterexamples.tsv",counter)
 report=["# GDT272 — q density/expansion mechanism","",f"Status: **{status}**.","","## Frozen result","","| predictor | Pearson r | rank rho | slope | sign agreement | positive LOO | local p | max-3 p |","|---|---:|---:|---:|---:|---:|---:|---:|"]
 for x in tests:report.append(f"| {x['predictor']} | {float(x['pearson_r']):+.3f} | {float(x['spearman_rho']):+.3f} | {float(x['linear_slope']):+.3f} | {x['sign_agreements']}/{x['sign_scored']} | {x['positive_leave_one_page']}/13 | {float(x['local_directional_p']):.4f} | {float(x['max_three_directional_p']):.4f} |")
 report += ["",("The frozen group-density mechanism passes: the compiler-matched q score rises on pages whose early selected records contain more groups than their late records." if gate else "The frozen group-density mechanism does not pass. Q20 page heterogeneity is not explained reliably by the early/late density imbalance that accompanied q in q13."),"","This narrows q's current grammar only at the formal level. A supported density effect would make q an expansion/template renderer; a failure leaves its q13 record-stage association local. Neither outcome supplies a semantic or spoken value.","","No word, morpheme, sound, semantic operator, language, plaintext, meaning, or translation is assigned. No f84r material was opened, retained, queried, joined, or scored.",""];(R/"GDT272_Q_DENSITY_MECHANISM_REPORT.md").write_text("\n".join(report),encoding="utf-8")
 outputs=["gdt272_density_outcome_join.tsv","gdt272_density_tests.tsv","gdt272_counterexamples.tsv","GDT272_Q_DENSITY_MECHANISM_REPORT.md"]
 result={"experiment":"GDT272_Q_DENSITY_MECHANISM","status":status,"gate_pass":gate,"primary":{k:(int(primary[k]) if k in {"sign_agreements","sign_scored","positive_leave_one_page","negative_leave_one_page"} else float(primary[k])) for k in ("pearson_r","spearman_rho","linear_slope","sign_agreements","sign_scored","positive_leave_one_page","negative_leave_one_page","loo_min_r","loo_max_r","local_directional_p","max_three_directional_p")},"interpretation":"Frozen Q20 page-level test of whether q conditional stage scores track early-versus-late record density.","claim_ceiling":"Density-conditioned opaque renderer mechanism only; no q semantic value word meaning plaintext or translation.","semantic_assignments":0,"f84r":{"new_access":False,"used":False,"scored":False},"inputs":{PRED:sha(PRED),XFILE:sha(XFILE),YFILE:sha(YFILE)},"documents":{METHOD:sha(METHOD)},"implementation":{Path(__file__).name:sha(Path(__file__).name)},"outputs":{x:sha(x) for x in outputs}};result["content_hash"]=chash(result);(R/"gdt272_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":status,"gate":gate,"tests":tests},sort_keys=True))
if __name__=="__main__":main()

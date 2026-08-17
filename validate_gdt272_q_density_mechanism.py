#!/usr/bin/env python3
"""Independent reconstruction validator for GDT272."""
import csv,hashlib,json,math,random
from pathlib import Path
R=Path(__file__).resolve().parent;PRED="gdt272_frozen_prediction.json";XFILE="gdt272_frozen_density_predictors.tsv";YFILE="gdt271_page_scores.tsv";RESULT="gdt272_result.json";METHOD="GDT272_Q_DENSITY_MECHANISM_METHOD.md";RUNNER="run_gdt272_q_density_mechanism.py";FEATURES=[("GROUP_COUNT_LOG_RATIO","group_count_log_ratio"),("FIELD_COUNT_LOG_RATIO","field_count_log_ratio"),("LINE_COUNT_LOG_RATIO","line_count_log_ratio")]
def read(name):
 with (R/name).open(encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def sha(n):return hashlib.sha256((R/n).read_bytes()).hexdigest()
def corr(a,b):
 ma=sum(a)/len(a);mb=sum(b)/len(b);num=sum((x-ma)*(y-mb) for x,y in zip(a,b));den=math.sqrt(sum((x-ma)**2 for x in a)*sum((y-mb)**2 for y in b));return num/den if den else 0
def ranks(v):
 order=sorted(range(len(v)),key=lambda i:(v[i],i));out=[0.0]*len(v);i=0
 while i<len(order):
  j=i+1
  while j<len(order) and v[order[j]]==v[order[i]]:j+=1
  for k in range(i,j):out[order[k]]=(i+j-1)/2+1
  i=j
 return out
def close(a,b,t=8e-10):return abs(float(a)-float(b))<=t
def main():
 checks=[]
 def ck(n,v):assert v,n;checks.append(n)
 pred=json.loads((R/PRED).read_text());xrows=read(XFILE);ys={x["page"]:float(x["conditional_score"]) for x in read(YFILE) if x["edition"]=="ZL3b" and x["variant"]=="PAGE_HOST_PAGE_OTHER_COMPILER"};ck("join_keys",len(xrows)==len(ys)==13 and {x["page"] for x in xrows}==set(ys));ck("no_f84",all(not x["page"].startswith("f84") for x in xrows));y=[ys[x["page"]] for x in xrows];seed=int(hashlib.sha256(pred["null_seed_literal"].encode()).hexdigest()[:16],16);rng=random.Random(seed);world=[]
 for _ in range(pred["null_worlds"]):perm=y[:];rng.shuffle(perm);world.append([corr([float(x[col]) for x in xrows],perm) for _,col in FEATURES])
 maxima=[max(v) for v in world];tests={x["predictor"]:x for x in read("gdt272_density_tests.tsv")};vals=[]
 for i,(name,col) in enumerate(FEATURES):
  x=[float(z[col]) for z in xrows];r=corr(x,y);rho=corr(ranks(x),ranks(y));mx=sum(x)/13;my=sum(y)/13;slope=sum((a-mx)*(b-my) for a,b in zip(x,y))/sum((a-mx)**2 for a in x);agree=sum(a*b>0 for a,b in zip(x,y));scored=sum(a!=0 and b!=0 for a,b in zip(x,y));loo=[corr(x[:j]+x[j+1:],y[:j]+y[j+1:]) for j in range(13)];local=(1+sum(v[i]>=r-1e-15 for v in world))/(len(world)+1);maxp=(1+sum(v>=r-1e-15 for v in maxima))/(len(world)+1);row=tests[name];ck(name+"_effect",close(row["pearson_r"],r) and close(row["spearman_rho"],rho) and close(row["linear_slope"],slope));ck(name+"_stability",int(row["sign_agreements"])==agree and int(row["sign_scored"])==scored and int(row["positive_leave_one_page"])==sum(v>0 for v in loo) and close(row["loo_min_r"],min(loo)) and close(row["loo_max_r"],max(loo)));ck(name+"_null",close(row["local_directional_p"],local) and close(row["max_three_directional_p"],maxp));vals.append((r,agree,sum(v>0 for v in loo),maxp))
 res=json.loads((R/RESULT).read_text());stored=res.pop("content_hash");ck("content",stored==hashlib.sha256(json.dumps(res,sort_keys=True,separators=(",",":")).encode()).hexdigest());ck("inputs",all(sha(n)==v for n,v in res["inputs"].items()));ck("outputs",all(sha(n)==v for n,v in res["outputs"].items()));ck("method",res["documents"][METHOD]==sha(METHOD));ck("runner",res["implementation"][RUNNER]==sha(RUNNER));r,a,l,p=vals[0];gate=r>0 and a>=pred["primary_gate"]["sign_agreement_min"] and l>=pred["primary_gate"]["positive_leave_one_page_min"] and p<=pred["primary_gate"]["max_three_p_max"];ck("gate",res["gate_pass"]==gate);ck("status",res["status"]==("Q_DENSITY_EXPANSION_MECHANISM_SUPPORTED_IN_Q20" if gate else "Q_DENSITY_EXPANSION_MECHANISM_NOT_SUPPORTED_IN_Q20"));ck("claims",res["semantic_assignments"]==0 and not any(res["f84r"].values()));val={"experiment":"GDT272_Q_DENSITY_MECHANISM","status":"PASS","checks_passed":len(checks),"checks":checks,"independent_reconstruction":True,"result_sha256":sha(RESULT),"validator_sha256":sha(Path(__file__).name),"f84r_accessed":False};(R/"gdt272_validation.json").write_text(json.dumps(val,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":"PASS","checks":len(checks),"gate":gate,"primary":{"r":r,"signs":a,"loo":l,"max3":p}},sort_keys=True))
if __name__=="__main__":main()

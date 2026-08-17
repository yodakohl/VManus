#!/usr/bin/env python3
"""Independent GDT276 reconstruction from the published f84-free inventory."""
import csv,hashlib,json,math,random,statistics
from collections import Counter,defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent;MODELS=("COMPRESSED_NATURAL_LANGUAGE","ABBREVIATION_HEAVY_LANGUAGE","LOCAL_CODEBOOK","TECHNICAL_NOTATION","HYBRID")
def read(n):
 with (R/n).open(encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def sha(n):return hashlib.sha256((R/n).read_bytes()).hexdigest()
def ch(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def bkt(model,key,n=256):return int(hashlib.sha256(json.dumps([model,key],sort_keys=True,separators=(",",":")).encode()).hexdigest()[:16],16)%n
def chars(host):
 out=[];hist="^^";seq=list(host)+["<EOS>"]
 for i,c in enumerate(seq):
  z="EOS" if c=="<EOS>" else "FIRST_FINAL" if len(host)==1 else "INITIAL" if i==0 else "FINAL" if i==len(host)-1 else "INTERIOR";out.append((hist[-2:],c,z));hist+=c if c!="<EOS>" else "$"
 return out
def cp(counts,h,c,K,prior=0,base=None):
 q=counts.get(h,Counter());n=sum(q.values())
 return (q[c]+.5)/(n+.5*K) if base is None else (q[c]+prior*base)/(n+prior)
def literal(ev,d):
 K=len(d["alphabet"]);prior=d["capacity"]["character_context_prior_mass"];bf=defaultdict(list)
 for x in ev:bf[x["physical_folio"]].append(x)
 out={};fold={};components=defaultdict(float)
 for held,te in sorted(bf.items()):
  gl=defaultdict(Counter)
  for x in ev:
   if x["physical_folio"]!=held:
    for h,c,z in chars(x["page_host"]):gl[h][c]+=1
  pg=defaultdict(lambda:defaultdict(Counter));bits=0
  for x in te:
   p=1
   for h,c,z in chars(x["page_host"]):
    pb=cp(gl,h,c,K);pp=cp(pg[x["page"]],h,c,K,prior,pb);v=-math.log2(pp);bits+=v;components[z]+=v;p*=pp;pg[x["page"]][h][c]+=1
   out[x["observation_id"]]=p
  fold[held]=bits
 return out,fold,dict(components)
def schar(ev,buckets,d):
 K=len(d["alphabet"]);prior=d["capacity"]["character_context_prior_mass"];bf=defaultdict(list)
 for x in ev:bf[x["physical_folio"]].append(x)
 folds={};comps=defaultdict(float);occ=set();cells=set()
 for held,te in sorted(bf.items()):
  gl=defaultdict(Counter);ct=defaultdict(Counter)
  for x in ev:
   if x["physical_folio"]==held:continue
   b=buckets[x["observation_id"]];occ.add(b)
   for h,c,z in chars(x["page_host"]):gl[h][c]+=1;ct[(b,h)][c]+=1;cells.add((b,h,c))
  pg=defaultdict(lambda:defaultdict(Counter));bits=0
  for x in te:
   b=buckets[x["observation_id"]]
   for h,c,z in chars(x["page_host"]):
    pb=cp(gl,h,c,K);pp=cp(pg[x["page"]],h,c,K,prior,pb);q=ct.get((b,h),Counter());p=(q[c]+prior*pp)/(sum(q.values())+prior);v=-math.log2(p);bits+=v;comps[z]+=v;pg[x["page"]][h][c]+=1
  folds[held]=bits
 return {"bits":sum(folds.values()),"folds":folds,"components":dict(comps),"occupied":len(occ),"cells":len(cells)}
def stok(ev,buckets,lit,d,ctx):
 cap=d["capacity"];bf=defaultdict(list)
 for x in ev:bf[x["physical_folio"]].append(x)
 folds={};occ=set();cells=set()
 for held,te in sorted(bf.items()):
  gl=Counter();cc=defaultdict(Counter)
  for x in ev:
   if x["physical_folio"]==held:continue
   gl[x["page_host"]]+=1
   if ctx:b=buckets[x["observation_id"]];cc[b][x["page_host"]]+=1;occ.add(b);cells.add((b,x["page_host"]))
  pages=defaultdict(Counter);bits=0;N=sum(gl.values())
  for x in te:
   y=x["page_host"];p0=(gl[y]+cap["global_token_prior_mass"]*lit[x["observation_id"]])/(N+cap["global_token_prior_mass"]);q=pages[x["page"]];p1=(q[y]+cap["page_token_prior_mass"]*p0)/(sum(q.values())+cap["page_token_prior_mass"])
   if ctx:z=cc[buckets[x["observation_id"]]];p=(z[y]+cap["context_token_prior_mass"]*p1)/(sum(z.values())+cap["context_token_prior_mass"])
   else:p=p1
   bits-=math.log2(p);pages[x["page"]][y]+=1
  folds[held]=bits
 return {"bits":sum(folds.values()),"folds":folds,"components":{},"occupied":len(occ),"cells":len(cells)}
def base_buckets(ev):
 return {"COMPRESSED_NATURAL_LANGUAGE":{x["observation_id"]:int(x["nl_bucket"]) for x in ev},"ABBREVIATION_HEAVY_LANGUAGE":{x["observation_id"]:int(x["compiler_bucket"]) for x in ev},"TECHNICAL_NOTATION":{x["observation_id"]:int(x["compiler_bucket"]) for x in ev},"HYBRID":{x["observation_id"]:int(x["hybrid_bucket"]) for x in ev}}
def scoreall(ev,d,override=None):
 bb=base_buckets(ev)
 if override:bb.update(override)
 lit,lf,lc=literal(ev,d);return {"COMPRESSED_NATURAL_LANGUAGE":schar(ev,bb["COMPRESSED_NATURAL_LANGUAGE"],d),"ABBREVIATION_HEAVY_LANGUAGE":schar(ev,bb["ABBREVIATION_HEAVY_LANGUAGE"],d),"LOCAL_CODEBOOK":stok(ev,{},lit,d,False),"TECHNICAL_NOTATION":stok(ev,bb["TECHNICAL_NOTATION"],lit,d,True),"HYBRID":stok(ev,bb["HYBRID"],lit,d,True)},lc
def shuffled(ev,w):
 st=defaultdict(list)
 for x in ev:st[(x["register"],x["record_ordinal"],x["within_field_position"],x["host_length"])].append(x["observation_id"])
 old=base_buckets(ev);out={}
 for m,mm in old.items():
  rng=random.Random(int(hashlib.sha256(f"GDT276_MATCHED_CONTEXT_V1|{w}|{m}".encode()).hexdigest()[:16],16));z=dict(mm)
  for ids in st.values():
   v=[mm[i] for i in ids];rng.shuffle(v)
   for i,q in zip(ids,v):z[i]=q
  out[m]=z
 return out
def main():
 d=json.loads((R/"gdt276_design.json").read_text());ev=read("gdt276_event_inventory.tsv");checks=[]
 def ck(n,v):
  checks.append({"check":n,"pass":bool(v)})
  if not v:raise AssertionError(n)
 for x in ev:
  for k in ("record_ordinal","field_ordinal","line_close","paragraph_close","host_length"):x[k]=int(x[k])
 ck("groups_8448",len(ev)==8448);ck("lines_1143",len({x["locus"] for x in ev})==1143);ck("pages_180",len({x["page"] for x in ev})==180);ck("folios_91",len({x["physical_folio"] for x in ev})==91);ck("no_f84",all(not x["page"].startswith("f84") and not x["locus"].startswith("f84") for x in ev));ck("alphabet",set("".join(x["page_host"] for x in ev)).issubset(set(d["alphabet"])-{"<EOS>"}))
 for x in ev:
  compiler=json.loads(x["compiler_key"]);nl=(x["register"],x["record_ordinal"],x["field_ordinal"],x["within_field_position"],x["line_close"],x["previous_page_host"][-2:]);ck("bucket_"+x["observation_id"],int(x["nl_bucket"])==bkt("NL",nl) and int(x["compiler_bucket"])==bkt("COMPILER",compiler) and int(x["hybrid_bucket"])==bkt("HYBRID",(compiler,x["previous_page_host"])))
 tm=defaultdict(set)
 for x in ev:tm[(x["page_host"],x["wrapper"],x["local_frame"],x["inner_d"],x["right_family"],x["dy_closure"],x["b3"])].add(x["raw_token"])
 ck("tuple_types_2368",len(tm)==2368);ck("tuple_unambiguous",all(len(v)==1 for v in tm.values()))
 obs,components=scoreall(ev,d);export={x["world"]:x for x in read("gdt276_world_scores.tsv")};folds=read("gdt276_folio_scores.tsv")
 ck("five_worlds",set(export)==set(MODELS));ck("fold_rows_455",len(folds)==455)
 for m in MODELS:
  ck(m+"_bits",abs(obs[m]["bits"]-float(export[m]["held_bits"]))<1e-8);ck(m+"_contexts",obs[m]["occupied"]==int(export[m]["occupied_contexts"]));ck(m+"_cells",obs[m]["cells"]==int(export[m]["training_context_cells"]));ff={x["held_folio"]:float(x["held_bits"]) for x in folds if x["world"]==m};ck(m+"_folds",set(ff)==set(obs[m]["folds"]) and all(abs(ff[k]-v)<1e-8 for k,v in obs[m]["folds"].items()))
 ec={x["component"]:float(x["held_bits"]) for x in read("gdt276_residual_components.tsv")};ck("components",set(ec)==set(obs["ABBREVIATION_HEAVY_LANGUAGE"]["components"]) and all(abs(ec[k]-v)<1e-8 for k,v in obs["ABBREVIATION_HEAVY_LANGUAGE"]["components"].items()))
 retained=read("gdt276_null_worlds.tsv");ck("null_rows_256",len(retained)==256);ri={(int(x["world_index"]),x["model"]):float(x["held_bits"]) for x in retained};null={m:[] for m in MODELS if m!="LOCAL_CODEBOOK"}
 for w in range(64):
  z,_=scoreall(ev,d,shuffled(ev,w))
  for m in null:ck(f"null_{w}_{m}",abs(z[m]["bits"]-ri[(w,m)])<1e-8);null[m].append(z[m]["bits"])
 controls={x["world"]:x for x in read("gdt276_matched_controls.tsv")}
 for m in null:
  mean=statistics.mean(null[m]);sd=statistics.pstdev(null[m]);p=(1+sum(x<=obs[m]["bits"]+1e-12 for x in null[m]))/65;ck(m+"_null_mean",abs(mean-float(controls[m]["null_mean_bits"]))<1e-8);ck(m+"_null_sd",abs(sd-float(controls[m]["null_sd_bits"]))<1e-8);ck(m+"_null_p",abs(p-float(controls[m]["lower_tail_p"]))<1e-12)
 result=json.loads((R/"gdt276_result.json").read_text());h=result.pop("content_hash");ck("result_hash",h==ch(result));result["content_hash"]=h;ck("status",result["status"]=="RESIDUAL_CHANNEL_QUANTIFIED_ABBREVIATION_HEAVY_LANGUAGE_MDL_LEAD_EXPLORATORY");ck("lead",result["leading_world"]=="ABBREVIATION_HEAVY_LANGUAGE");ck("rank",result["world_rank"]==[x["world"] for x in sorted(export.values(),key=lambda q:int(q["rank"]))]);ck("no_semantics",result["semantic_assignments"]==0);ck("f84_flags",result["f84"]=={"rejected_before_formal_parse":True,"retained":False,"used":False,"scored":False,"tuned":False});ck("input_hashes",all(sha(k)==v for k,v in result["inputs"].items()));ck("docs",all(sha(k)==v for k,v in result["documents"].items()));ck("implementation",all(sha(k)==v for k,v in result["implementation"].items()));ck("outputs",all(sha(k)==v for k,v in result["outputs"].items()))
 p={"experiment":"GDT276_RESIDUAL_CHANNEL_WORLD_COMPARISON_VALIDATION","status":"PASS","checks_passed":len(checks),"checks_total":len(checks),"result_sha256":sha("gdt276_result.json"),"validator_sha256":sha(Path(__file__).name),"checks":checks};p["content_hash"]=ch(p);(R/"gdt276_validation.json").write_text(json.dumps(p,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":"PASS","checks":len(checks)},sort_keys=True))
if __name__=="__main__":main()

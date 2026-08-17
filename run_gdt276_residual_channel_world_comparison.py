#!/usr/bin/env python3
"""GDT276: compiler-conditioned residual entropy and five-world MDL comparison."""
from __future__ import annotations
import csv,hashlib,json,math,random,re,statistics
from collections import Counter,defaultdict
from pathlib import Path

R=Path(__file__).resolve().parent
HPR=R/"gdt062_right_family_inventory.tsv";FRAMES=R/"gdt046_line_frames.tsv";LABEL=R/"gdt237_predictions.tsv"
DESIGN=R/"gdt276_design.json";DESIGN_VALIDATION=R/"gdt276_design_validation.json";METHOD=R/"GDT276_RESIDUAL_CHANNEL_WORLD_COMPARISON_METHOD.md"
MODELS=("COMPRESSED_NATURAL_LANGUAGE","ABBREVIATION_HEAVY_LANGUAGE","LOCAL_CODEBOOK","TECHNICAL_NOTATION","HYBRID")

def sha(path:Path):return hashlib.sha256(path.read_bytes()).hexdigest()
def chash(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def write(path,rows):
 fields=[]
 for x in rows:
  for k in x:
   if k not in fields:fields.append(k)
 with path.open("w",encoding="utf-8",newline="") as h:w=csv.DictWriter(h,fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows([{k:x.get(k,"") for k in fields} for x in rows])
def guarded(path:Path):
 """Reject f84 using raw page/locus cells before constructing row dictionaries."""
 with path.open(encoding="utf-8",newline="") as h:
  header=h.readline().rstrip("\r\n").split("\t");pi=header.index("page");li=header.index("locus");assert (li,pi)==(0,1);rejected=0;kept=[]
  for raw in h:
   first=raw.split("\t",2);assert len(first)==3
   if first[pi].startswith("f84") or first[li].startswith("f84"):rejected+=1;continue
   vals=raw.rstrip("\r\n").split("\t");assert len(vals)==len(header)
   kept.append(dict(zip(header,vals)))
 return kept,rejected
def locus_number(x):
 m=re.search(r"\.(\d+)$",x);assert m;return int(m.group(1))
def bucket(model,key,n=256):
 raw=json.dumps([model,key],sort_keys=True,separators=(",",":")).encode();return int(hashlib.sha256(raw).hexdigest()[:16],16)%n
def build_events(design):
 frames,rf=guarded(FRAMES);hpr,rh=guarded(HPR);frame={x["locus"]:x for x in frames};by=defaultdict(list)
 for x in hpr:
  if x["locus"] in frame:by[x["locus"]].append(x)
 assert set(by)==set(frame)
 labels={}
 with LABEL.open(encoding="utf-8",newline="") as h:
  for x in csv.DictReader(h,delimiter="\t"):
   assert not x["page"].startswith("f84") and not x["locus"].startswith("f84");labels[x["locus"]]=x
 assert set(by).issubset(labels)
 pages=defaultdict(list)
 for locus,x in frame.items():pages[x["page"]].append(locus)
 paragraph_end=set();record_ordinal={}
 for page,ll in pages.items():
  ll.sort(key=locus_number);rec=1
  for i,locus in enumerate(ll):
   if i and int(frame[locus]["paragraph_start"]):rec+=1
   record_ordinal[locus]=rec
  paragraph_end.add(ll[-1])
  for a,b in zip(ll,ll[1:]):
   if int(frame[b]["paragraph_start"]):paragraph_end.add(a)
 events=[]
 for locus in sorted(by,key=lambda z:(frame[z]["page"],locus_number(z))):
  rr=sorted(by[locus],key=lambda z:int(z["group_index"]));assert len(rr)==int(rr[0]["group_count"]) and [int(x["group_index"]) for x in rr]==list(range(1,len(rr)+1))
  fields=[];cur=[]
  for i,x in enumerate(rr):
   cur.append(x)
   if x["dy_closure"]=="1" or i==len(rr)-1:fields.append(cur);cur=[]
  assert not cur
  prev="<LINE_BOS>"
  for fi,field in enumerate(fields,1):
   for wi,x in enumerate(field):
    pos="ONLY" if len(field)==1 else "FIRST" if wi==0 else "LAST" if wi==len(field)-1 else "MIDDLE"
    line_close=int(x["group_index"]==x["group_count"]);paragraph_close=int(line_close and locus in paragraph_end);lab=labels[locus]["matched_prefix"]
    compiler=(x["register"],record_ordinal[locus],fi,pos,x["wrapper"],int(x["wrapper"]=="q"),x["local_frame"],x["inner_d"],x["right_family"],x["dy_closure"],x["b3"],line_close,paragraph_close,lab)
    nl=(x["register"],record_ordinal[locus],fi,pos,line_close,prev[-2:])
    item={"observation_id":f"GDT276:{locus}:G{int(x['group_index']):03d}","page":x["page"],"physical_folio":x["physical_folio"],"locus":locus,"group_index":int(x["group_index"]),"group_count":int(x["group_count"]),"register":x["register"],"section":x["section"],"currier":x["currier"],"hand":x["hand"],"record_ordinal":record_ordinal[locus],"field_ordinal":fi,"within_field_position":pos,"wrapper":x["wrapper"],"q_flag":int(x["wrapper"]=="q"),"local_frame":x["local_frame"],"inner_d":x["inner_d"],"right_family":x["right_family"],"dy_closure":x["dy_closure"],"b3":x["b3"],"line_close":line_close,"paragraph_close":paragraph_close,"known_label_renderer":lab,"page_host":x["page_host"],"raw_token":x["token"],"previous_page_host":prev,"compiler_key":json.dumps(compiler,separators=(",",":")),"nl_bucket":bucket("NL",nl),"compiler_bucket":bucket("COMPILER",compiler),"hybrid_bucket":bucket("HYBRID",(compiler,prev)),"host_length":len(x["page_host"])}
    events.append(item);prev=x["page_host"]
 alphabet=set(design["alphabet"])-{"<EOS>"};assert set("".join(x["page_host"] for x in events)).issubset(alphabet)
 assert len(events)==8448 and len(by)==1143 and len(pages)==180 and len({x["physical_folio"] for x in events})==91
 return events,{"groups":len(events),"lines":len(by),"pages":len(pages),"folios":91,"f84_hpr_rows_rejected_before_formal_parse":rh,"f84_frame_rows_rejected_before_formal_parse":rf}

def chars(host):
 seq=list(host)+["<EOS>"];hist="^^";out=[]
 for i,c in enumerate(seq):
  comp="EOS" if c=="<EOS>" else "FIRST_FINAL" if len(host)==1 else "INITIAL" if i==0 else "FINAL" if i==len(host)-1 else "INTERIOR";out.append((hist[-2:],c,comp));hist+=c if c!="<EOS>" else "$"
 return out
def cprob(counts,hist,c,K,prior,base=None):
 q=counts.get(hist,Counter());n=sum(q.values())
 if base is None:return (q[c]+.5)/(n+.5*K)
 return (q[c]+prior*base)/(n+prior)

def literal_probabilities(events,alphabet,priors):
 K=len(alphabet);byfol=defaultdict(list)
 for x in events:byfol[x["physical_folio"]].append(x)
 out={};foldbits={};components=defaultdict(float)
 for held,te in sorted(byfol.items()):
  train=[x for x in events if x["physical_folio"]!=held];globalc=defaultdict(Counter)
  for x in train:
   for h,c,z in chars(x["page_host"]):globalc[h][c]+=1
  pagec=defaultdict(lambda:defaultdict(Counter));bits=0.0
  for x in te:
   p=1.0
   for h,c,z in chars(x["page_host"]):
    pb=cprob(globalc,h,c,K,0);pp=cprob(pagec[x["page"]],h,c,K,priors["char"],pb);v=-math.log2(pp);bits+=v;components[z]+=v;p*=pp;pagec[x["page"]][h][c]+=1
   out[x["observation_id"]]=p
  foldbits[held]=bits
 return out,foldbits,dict(components)

def score_char(events,model,buckets,alphabet,priors):
 K=len(alphabet);byfol=defaultdict(list)
 for x in events:byfol[x["physical_folio"]].append(x)
 fold={};components=defaultdict(float);occupied=set();cells=set()
 for held,te in sorted(byfol.items()):
  train=[x for x in events if x["physical_folio"]!=held];glob=defaultdict(Counter);ctx=defaultdict(Counter)
  for x in train:
   b=buckets[x["observation_id"]];occupied.add(b)
   for h,c,z in chars(x["page_host"]):glob[h][c]+=1;ctx[(b,h)][c]+=1;cells.add((b,h,c))
  pagec=defaultdict(lambda:defaultdict(Counter));bits=0.0
  for x in te:
   b=buckets[x["observation_id"]]
   for h,c,z in chars(x["page_host"]):
    pb=cprob(glob,h,c,K,0);pp=cprob(pagec[x["page"]],h,c,K,priors["char"],pb);q=ctx.get((b,h),Counter());pc=(q[c]+priors["char"]*pp)/(sum(q.values())+priors["char"]);v=-math.log2(pc);bits+=v;components[z]+=v;pagec[x["page"]][h][c]+=1
  fold[held]=bits
 return {"bits":sum(fold.values()),"folds":fold,"components":dict(components),"occupied_contexts":len(occupied),"training_cells":len(cells)}

def score_token(events,model,buckets,literal,priors,use_context):
 byfol=defaultdict(list)
 for x in events:byfol[x["physical_folio"]].append(x)
 fold={};occupied=set();cells=set()
 for held,te in sorted(byfol.items()):
  train=[x for x in events if x["physical_folio"]!=held];glob=Counter(x["page_host"] for x in train);ctx=defaultdict(Counter)
  if use_context:
   for x in train:b=buckets[x["observation_id"]];ctx[b][x["page_host"]]+=1;occupied.add(b);cells.add((b,x["page_host"]))
  pagec=defaultdict(Counter);bits=0.0;N=sum(glob.values())
  for x in te:
   y=x["page_host"];pl=literal[x["observation_id"]];pg=(glob[y]+priors["global_token"]*pl)/(N+priors["global_token"]);pc=pagec[x["page"]];pp=(pc[y]+priors["page_token"]*pg)/(sum(pc.values())+priors["page_token"])
   if use_context:
    q=ctx[buckets[x["observation_id"]]];p=(q[y]+priors["context_token"]*pp)/(sum(q.values())+priors["context_token"])
   else:p=pp
   bits-=math.log2(p);pagec[x["page"]][y]+=1
  fold[held]=bits
 return {"bits":sum(fold.values()),"folds":fold,"components":{},"occupied_contexts":len(occupied),"training_cells":len(cells)}

def score_models(events,design,bucket_overrides=None):
 cap=design["capacity"];priors={"char":cap["character_context_prior_mass"],"global_token":cap["global_token_prior_mass"],"page_token":cap["page_token_prior_mass"],"context_token":cap["context_token_prior_mass"]};alphabet=design["alphabet"];literal,litfold,litcomp=literal_probabilities(events,alphabet,priors)
 base={"COMPRESSED_NATURAL_LANGUAGE":{x["observation_id"]:x["nl_bucket"] for x in events},"ABBREVIATION_HEAVY_LANGUAGE":{x["observation_id"]:x["compiler_bucket"] for x in events},"TECHNICAL_NOTATION":{x["observation_id"]:x["compiler_bucket"] for x in events},"HYBRID":{x["observation_id"]:x["hybrid_bucket"] for x in events}}
 if bucket_overrides:
  for k,v in bucket_overrides.items():base[k]=v
 out={};out["COMPRESSED_NATURAL_LANGUAGE"]=score_char(events,"COMPRESSED_NATURAL_LANGUAGE",base["COMPRESSED_NATURAL_LANGUAGE"],alphabet,priors);out["ABBREVIATION_HEAVY_LANGUAGE"]=score_char(events,"ABBREVIATION_HEAVY_LANGUAGE",base["ABBREVIATION_HEAVY_LANGUAGE"],alphabet,priors);out["LOCAL_CODEBOOK"]=score_token(events,"LOCAL_CODEBOOK",{},literal,priors,False);out["TECHNICAL_NOTATION"]=score_token(events,"TECHNICAL_NOTATION",base["TECHNICAL_NOTATION"],literal,priors,True);out["HYBRID"]=score_token(events,"HYBRID",base["HYBRID"],literal,priors,True);out["LITERAL_CHAR3"]={"bits":sum(litfold.values()),"folds":litfold,"components":litcomp,"occupied_contexts":0,"training_cells":0};return out

def random_buckets(events,world):
 result={};strata=defaultdict(list)
 for x in events:strata[(x["register"],x["record_ordinal"],x["within_field_position"],x["host_length"])].append(x["observation_id"])
 originals={"COMPRESSED_NATURAL_LANGUAGE":{x["observation_id"]:x["nl_bucket"] for x in events},"ABBREVIATION_HEAVY_LANGUAGE":{x["observation_id"]:x["compiler_bucket"] for x in events},"TECHNICAL_NOTATION":{x["observation_id"]:x["compiler_bucket"] for x in events},"HYBRID":{x["observation_id"]:x["hybrid_bucket"] for x in events}}
 for model,m in originals.items():
  rng=random.Random(int(hashlib.sha256(f"GDT276_MATCHED_CONTEXT_V1|{world}|{model}".encode()).hexdigest()[:16],16));z=dict(m)
  for ids in strata.values():
   vals=[m[i] for i in ids];rng.shuffle(vals)
   for i,v in zip(ids,vals):z[i]=v
  result[model]=z
 return result

def main():
 design=json.loads(DESIGN.read_text());assert design["status"]=="FROZEN_BEFORE_GDT276_SCORING";events,census=build_events(design)
 observed=score_models(events,design);null={m:[] for m in MODELS if m!="LOCAL_CODEBOOK"};null_rows=[]
 for world in range(design["matched_control_worlds"]):
  z=score_models(events,design,random_buckets(events,world))
  for m in null:null[m].append(z[m]["bits"]);null_rows.append({"world_index":world,"model":m,"held_bits":f"{z[m]['bits']:.12f}"})
  if (world+1)%8==0:print(json.dumps({"matched_controls_completed":world+1}),flush=True)
 total_chars=sum(len(x["page_host"])+1 for x in events);selector=design["capacity"]["world_selector_bits"];world_rows=[];fold_rows=[]
 for m in MODELS:
  q=observed[m];vals=null.get(m,[]);mean=statistics.mean(vals) if vals else q["bits"];sd=statistics.pstdev(vals) if vals else 0.0;p=(1+sum(x<=q["bits"]+1e-12 for x in vals))/(len(vals)+1) if vals else 1.0
  world_rows.append({"rank":0,"world":m,"held_bits":f"{q['bits']:.12f}","selector_paid_mdl_bits":f"{q['bits']+selector:.12f}","bits_per_group":f"{q['bits']/len(events):.12f}","bits_per_host_symbol_including_eos":f"{q['bits']/total_chars:.12f}","positive_folio_wins_vs_abbreviation":"PENDING","occupied_contexts":q["occupied_contexts"],"training_context_cells":q["training_cells"],"matched_null_mean_bits":f"{mean:.12f}","matched_null_sd_bits":f"{sd:.12f}","matched_null_savings_bits":f"{mean-q['bits']:.12f}","matched_lower_tail_p":f"{p:.12f}","semantic_value":"UNASSIGNED"})
  for fol,bits in q["folds"].items():fold_rows.append({"world":m,"held_folio":fol,"held_bits":f"{bits:.12f}","groups":sum(x["physical_folio"]==fol for x in events),"bits_per_group":f"{bits/sum(x['physical_folio']==fol for x in events):.12f}"})
 abbrev=observed["ABBREVIATION_HEAVY_LANGUAGE"]["folds"]
 for row in world_rows:row["positive_folio_wins_vs_abbreviation"]=sum(observed[row["world"]]["folds"][f]<abbrev[f] for f in abbrev)
 world_rows.sort(key=lambda x:float(x["selector_paid_mdl_bits"]));
 for i,x in enumerate(world_rows,1):x["rank"]=i
 compiler_components=observed["ABBREVIATION_HEAVY_LANGUAGE"]["components"];component_rows=[{"component":k,"held_bits":f"{v:.12f}","fraction_of_abbreviation_bits":f"{v/observed['ABBREVIATION_HEAVY_LANGUAGE']['bits']:.12f}","interpretation":"OPAQUE_HOST_FORM_COMPONENT"} for k,v in sorted(compiler_components.items())]
 tuplemap=defaultdict(set)
 for x in events:tuplemap[(x["page_host"],x["wrapper"],x["local_frame"],x["inner_d"],x["right_family"],x["dy_closure"],x["b3"])].add(x["raw_token"])
 ambiguous=sum(len(v)>1 for v in tuplemap.values());assert ambiguous==0
 sequential=observed["TECHNICAL_NOTATION"]["bits"]-observed["HYBRID"]["bits"]
 residual=[{"channel":"COMPILER_CONDITIONED_CHARACTER_FORM","held_bits":f"{observed['ABBREVIATION_HEAVY_LANGUAGE']['bits']:.12f}","increment_bits_saved":"0.000000000000","statement":"host character entropy after joint renderer nuisance"},{"channel":"EXACT_PAGE_HOST_IDENTITY","held_bits":f"{observed['TECHNICAL_NOTATION']['bits']:.12f}","increment_bits_saved":f"{observed['ABBREVIATION_HEAVY_LANGUAGE']['bits']-observed['TECHNICAL_NOTATION']['bits']:.12f}","statement":"exact opaque identity beyond compiler-conditioned character form"},{"channel":"SEQUENTIAL_PREVIOUS_HOST","held_bits":f"{observed['HYBRID']['bits']:.12f}","increment_bits_saved":f"{sequential:.12f}","statement":"previous exact host beyond technical tuple"},{"channel":"PAGE_LOCAL_CODEBOOK","held_bits":f"{observed['LOCAL_CODEBOOK']['bits']:.12f}","increment_bits_saved":f"{observed['ABBREVIATION_HEAVY_LANGUAGE']['bits']-observed['LOCAL_CODEBOOK']['bits']:.12f}","statement":"prequential page-local exact identity versus compiler-conditioned characters"},{"channel":"RAW_GIVEN_FULL_TUPLE","held_bits":"0.000000000000","increment_bits_saved":"0.000000000000","statement":f"{len(tuplemap)} tuple types; {ambiguous} ambiguous; deterministic HPR2 reconstruction"}]
 write(R/"gdt276_event_inventory.tsv",events);write(R/"gdt276_world_scores.tsv",world_rows);write(R/"gdt276_folio_scores.tsv",fold_rows);write(R/"gdt276_residual_components.tsv",component_rows);write(R/"gdt276_residual_channels.tsv",residual)
 control_rows=[]
 for m in MODELS:
  row=next(x for x in world_rows if x["world"]==m);control_rows.append({"world":m,"observed_bits":row["held_bits"],"null_worlds":len(null.get(m,[])),"null_mean_bits":row["matched_null_mean_bits"],"null_sd_bits":row["matched_null_sd_bits"],"null_savings_bits":row["matched_null_savings_bits"],"lower_tail_p":row["matched_lower_tail_p"],"control_scope":"NOT_APPLICABLE_PAGE_LOCAL_BASE" if m=="LOCAL_CODEBOOK" else "FREQUENCY_AND_OPPORTUNITY_MATCHED_CONTEXT_BUCKET_PERMUTATION"})
 write(R/"gdt276_matched_controls.tsv",control_rows);write(R/"gdt276_null_worlds.tsv",null_rows)
 counter=[{"counterexample":"FULL_TUPLE_DETERMINISM","evidence":f"{len(tuplemap)} tuple types; zero raw-token ambiguity","impact":"raw reconstruction is guaranteed by the parser and is not independent evidence for a world"},{"counterexample":"EXPOSED_PANEL","evidence":"all five models frozen only before this scoring pass","impact":"ranking is exploratory model comparison, not confirmation"},{"counterexample":"LOCAL_CODEBOOK_CAPACITY","evidence":"prequential page counts start empty and use past held-page groups","impact":"page fit is honest sequential compression but not transfer of a global dictionary"},{"counterexample":"SEQUENTIAL_GDT175_PRIOR","evidence":"prior exact NEXT_HOST transfer was negative","impact":"HYBRID must earn held MDL rather than inherit a sequential claim"},{"counterexample":"LABEL_RENDERER_PARTIAL","evidence":"GDT237 transferred prefix or NONE is conditioned","impact":"known graphical renderer is partial and prose false positives remain"},{"counterexample":"NO_SEMANTIC_ENDPOINT","evidence":"target is opaque PAGE_HOST","impact":"best code cannot identify language notation role meaning plaintext or translation"}];write(R/"gdt276_counterexamples.tsv",counter)
 lead=world_rows[0];status="RESIDUAL_CHANNEL_QUANTIFIED_"+lead["world"]+"_MDL_LEAD_EXPLORATORY"
 report=["# GDT276 — residual channel and five-world comparison","",f"Status: **{status}**.","","## Held-folio world comparison","","| rank | world | bits | bits/group | bits/symbol | folio wins vs abbreviation | matched savings | matched p |","|---:|---|---:|---:|---:|---:|---:|---:|"]
 for x in world_rows:report.append(f"| {x['rank']} | {x['world']} | {float(x['held_bits']):.1f} | {float(x['bits_per_group']):.4f} | {float(x['bits_per_host_symbol_including_eos']):.4f} | {x['positive_folio_wins_vs_abbreviation']}/91 | {float(x['matched_null_savings_bits']):+.1f} | {float(x['matched_lower_tail_p']):.4f} |")
 report += ["","All worlds encode the same opaque PAGE_HOST target.  The selector charge is equal, so the ranking is unchanged by `log2(5)` bits.  Context models have the same 256-bucket ceiling; the page-local dictionary is prequential and begins empty on every held page.","","## Residual localization","",f"Compiler-conditioned host character form costs **{observed['ABBREVIATION_HEAVY_LANGUAGE']['bits']:.1f} bits**.  Switching to exact compiler-conditioned PAGE_HOST identities changes this by **{observed['ABBREVIATION_HEAVY_LANGUAGE']['bits']-observed['TECHNICAL_NOTATION']['bits']:+.1f} bits**.  Adding the previous exact host changes it by a further **{sequential:+.1f} bits**.  The page-local codebook costs **{observed['LOCAL_CODEBOOK']['bits']:.1f} bits**.","",f"The full HPR2 tuple reconstructs raw source groups deterministically on this panel ({len(tuplemap)} tuple types, zero ambiguous), so raw-given-host-plus-renderer residual entropy is zero by parser construction—not an empirical semantic result.","","## Interpretation","",f"The leading operational world is **{lead['world']}**.  This ranks residual coding architectures; it does not identify what PAGE_HOSTs denote.  Matched-control savings show whether the particular context alignment matters beyond bucket frequency and structural opportunity.","","No meaning, semantic role, language, plaintext, or translation is assigned.  All f84* source rows were rejected from raw page/locus fields before formal-column parsing; none was retained, joined, tuned on, or scored.",""];(R/"GDT276_RESIDUAL_CHANNEL_WORLD_COMPARISON_REPORT.md").write_text("\n".join(report),encoding="utf-8")
 outputs=["gdt276_event_inventory.tsv","gdt276_world_scores.tsv","gdt276_folio_scores.tsv","gdt276_residual_components.tsv","gdt276_residual_channels.tsv","gdt276_matched_controls.tsv","gdt276_null_worlds.tsv","gdt276_counterexamples.tsv","GDT276_RESIDUAL_CHANNEL_WORLD_COMPARISON_REPORT.md"]
 inherited=json.loads((R/"gdt174_result.json").read_text())["inputs"]
 result={"experiment":"GDT276_RESIDUAL_CHANNEL_WORLD_COMPARISON","status":status,"census":census,"world_rank":[x["world"] for x in world_rows],"leading_world":lead["world"],"world_scores":{x["world"]:{"bits":float(x["held_bits"]),"bits_per_group":float(x["bits_per_group"]),"matched_savings_bits":float(x["matched_null_savings_bits"]),"matched_p":float(x["matched_lower_tail_p"])} for x in world_rows},"residual":{"compiler_character_bits":observed["ABBREVIATION_HEAVY_LANGUAGE"]["bits"],"exact_identity_savings_vs_compiler_char":observed["ABBREVIATION_HEAVY_LANGUAGE"]["bits"]-observed["TECHNICAL_NOTATION"]["bits"],"sequential_savings_vs_technical":sequential,"raw_given_full_tuple_bits":0.0,"tuple_ambiguities":ambiguous},"semantic_assignments":0,"claim_ceiling":"Held-folio residual coding architecture only; no language notation identity semantic role meaning plaintext or translation.","f84":{"rejected_before_formal_parse":True,"retained":False,"used":False,"scored":False,"tuned":False},"source_bindings_inherited_from_gdt174":{"gdt046_line_frames.tsv":inherited["gdt046_line_frames.tsv"],"gdt062_right_family_inventory.tsv":inherited["gdt062_right_family_inventory.tsv"]},"inputs":{"gdt174_result.json":sha(R/"gdt174_result.json"),"gdt237_predictions.tsv":sha(LABEL),"gdt276_design.json":sha(DESIGN),"gdt276_design_validation.json":sha(DESIGN_VALIDATION)},"documents":{METHOD.name:sha(METHOD)},"implementation":{Path(__file__).name:sha(Path(__file__))},"outputs":{x:sha(R/x) for x in outputs}};result["content_hash"]=chash(result);(R/"gdt276_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":status,"lead":lead["world"],"bits":{x["world"]:float(x["held_bits"]) for x in world_rows}},sort_keys=True))
if __name__=="__main__":main()

#!/usr/bin/env python3
"""GDT273: held-folio q13 field-sequence prediction and record shuffles."""
import csv,hashlib,json,math,random,statistics
from collections import Counter,defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent;SRC="gdt227_q13_abstract_interlinear.tsv";METHOD="GDT273_Q13_FIELD_SEQUENCE_GRAMMAR_METHOD.md";CONTEXT=["gdt224_result.json","gdt226_result.json","gdt255_result.json","gdt271_result.json"]
REPS=("SIZE2","SIZE4","END2","JOINT4");WORLDS=4096;ALPHA=.5
def read(name):
 with (R/name).open(encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def write(name,rows):
 with (R/name).open("w",encoding="utf-8",newline="") as h:w=csv.DictWriter(h,fieldnames=list(rows[0]),delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def sha(name):return hashlib.sha256((R/name).read_bytes()).hexdigest()
def chash(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def state(row,rep):
 n=int(row["field_group_count"]);size2="S12" if n<=2 else "L3P";end=row["line_field_end"]
 if rep=="SIZE2":return size2
 if rep=="SIZE4":return "G1" if n==1 else "G2" if n==2 else "G3_5" if n<=5 else "G6P"
 if rep=="END2":return end
 return size2+"|"+end
def rbin(n):return "R1_10" if n<=10 else "R11_20" if n<=20 else "R21P"
def inventory():
 rows=read(SRC);assert rows and all(not x["page"].startswith("f84") for x in rows);seq=defaultdict(list)
 for x in rows:seq[x["record_id"]].append(x)
 for values in seq.values():values.sort(key=lambda x:int(x["field_ordinal"]));assert [int(x["field_ordinal"]) for x in values]==list(range(1,len(values)+1))
 assert len(rows)==701 and len(seq)==33 and len({x["physical_folio"] for x in rows})==9
 return rows,dict(seq)
def maps(seq,rep,permutations=None):
 out={}
 for rid,rows in seq.items():
  values=[state(x,rep) for x in rows]
  if permutations is not None:values=[values[i] for i in permutations[rid]]
  out[rid]=values
 return out
def score(seq,values,states):
 folios=sorted({rows[0]["physical_folio"] for rows in seq.values()});folds={}
 for held in folios:
  base=defaultdict(Counter);model=defaultdict(Counter)
  for rid,rows in seq.items():
   if rows[0]["physical_folio"]==held:continue
   n=len(rows);sv=values[rid]
   for i in range(1,n):
    q=min(3,int(((i+1)/n)*4));ctx=(rbin(n),q);base[ctx][sv[i]]+=1;model[ctx+(sv[i-1],)][sv[i]]+=1
  gain=0.0
  for rid,rows in seq.items():
   if rows[0]["physical_folio"]!=held:continue
   n=len(rows);sv=values[rid]
   for i in range(1,n):
    q=min(3,int(((i+1)/n)*4));ctx=(rbin(n),q);b=base[ctx];m=model[ctx+(sv[i-1],)];pb=(b[sv[i]]+ALPHA)/(sum(b.values())+ALPHA*len(states));pm=(m[sv[i]]+ALPHA)/(sum(m.values())+ALPHA*len(states));gain+=math.log2(pm/pb)
  folds[held]=gain
 return sum(folds.values()),folds
def repeats(values):return sum(sum(a==b for a,b in zip(v,v[1:])) for v in values.values())
def main():
 rows,seq=inventory();states={rep:sorted({state(x,rep) for x in rows}) for rep in REPS};observed={};fold_rows=[];transition=[]
 for rep in REPS:
  values=maps(seq,rep);gain,folds=score(seq,values,states[rep]);observed[rep]={"gain":gain,"folds":folds,"repeat":repeats(values)}
  for f,g in folds.items():fold_rows.append({"representation":rep,"held_folio":f,"gain_bits":f"{g:.12f}","positive":int(g>0)})
  counts=Counter()
  for v in values.values():counts.update(zip(v,v[1:]))
  for (left,right),n in sorted(counts.items()):transition.append({"representation":rep,"left_state":left,"right_state":right,"count":n})
 null_gain={rep:[] for rep in REPS};null_repeat={rep:[] for rep in REPS}
 for world in range(WORLDS):
  rng=random.Random(int(hashlib.sha256(f"GDT273_Q13_FIELD_SEQUENCE_NULL_V1|{world}".encode()).hexdigest()[:16],16));perm={}
  for rid,values in sorted(seq.items()):idx=list(range(len(values)));rng.shuffle(idx);perm[rid]=idx
  for rep in REPS:
   values=maps(seq,rep,perm);null_gain[rep].append(score(seq,values,states[rep])[0]);null_repeat[rep].append(repeats(values))
 gain_mean={r:statistics.mean(null_gain[r]) for r in REPS};gain_sd={r:statistics.pstdev(null_gain[r]) for r in REPS};rep_mean={r:statistics.mean(null_repeat[r]) for r in REPS};rep_sd={r:statistics.pstdev(null_repeat[r]) for r in REPS};gain_z={r:(observed[r]["gain"]-gain_mean[r])/gain_sd[r] for r in REPS};repeat_z={r:(observed[r]["repeat"]-rep_mean[r])/rep_sd[r] for r in REPS};max_gain=[max((null_gain[r][i]-gain_mean[r])/gain_sd[r] for r in REPS) for i in range(WORLDS)];max_repeat=[max(abs((null_repeat[r][i]-rep_mean[r])/rep_sd[r]) for r in REPS) for i in range(WORLDS)];tests=[]
 for rep in REPS:
  lg=(1+sum(v>=observed[rep]["gain"]-1e-12 for v in null_gain[rep]))/(WORLDS+1);mg=(1+sum(v>=gain_z[rep]-1e-12 for v in max_gain))/(WORLDS+1);lr=(1+sum(abs(v-rep_mean[rep])>=abs(observed[rep]["repeat"]-rep_mean[rep])-1e-12 for v in null_repeat[rep]))/(WORLDS+1);mr=(1+sum(v>=abs(repeat_z[rep])-1e-12 for v in max_repeat))/(WORLDS+1)
  tests.append({"representation":rep,"states":len(states[rep]),"transitions":sum(len(v)-1 for v in seq.values()),"held_gain_bits":f"{observed[rep]['gain']:.12f}","positive_folios":sum(v>0 for v in observed[rep]["folds"].values()),"negative_folios":sum(v<0 for v in observed[rep]["folds"].values()),"null_gain_mean":f"{gain_mean[rep]:.12f}","gain_z":f"{gain_z[rep]:.12f}","gain_local_p":f"{lg:.12f}","gain_max_four_p":f"{mg:.12f}","same_state_adjacencies":observed[rep]["repeat"],"null_repeat_mean":f"{rep_mean[rep]:.12f}","repeat_z":f"{repeat_z[rep]:.12f}","repeat_local_two_sided_p":f"{lr:.12f}","repeat_max_four_p":f"{mr:.12f}","semantic_value":"UNASSIGNED"})
 write("gdt273_lofo_folds.tsv",fold_rows);write("gdt273_transition_counts.tsv",transition);write("gdt273_tests.tsv",tests)
 gate_rows=[x for x in tests if float(x["held_gain_bits"])>0 and int(x["positive_folios"])>=6 and float(x["gain_max_four_p"])<=.05];status="Q13_TRANSFERABLE_FIRST_ORDER_FIELD_SYNTAX_SUPPORTED" if gate_rows else "Q13_FIELD_ORDER_NOT_PREDICTIVE_BEYOND_POSITION_AND_RECORD_SIZE"
 end=next(x for x in tests if x["representation"]=="END2");joint=next(x for x in tests if x["representation"]=="JOINT4")
 counter=[{"counterexample":"ALL_HELD_GAINS_NONPOSITIVE" if not gate_rows else "SOME_GAIN_PASS","value":"; ".join(f"{x['representation']}={x['held_gain_bits']}" for x in tests),"consequence":"first-order state does not improve held prediction unless a row passes the full gate"},{"counterexample":"ENDPOINT_REPEAT_EFFECT","value":f"END2 z {end['repeat_z']} max4 p {end['repeat_max_four_p']}","consequence":"endpoint alternation is real but mechanically coupled to DY field segmentation and line topology"},{"counterexample":"JOINT_NULL_RELATIVE_ONLY","value":f"gain {joint['held_gain_bits']} null mean {joint['null_gain_mean']}","consequence":"being less bad than shuffled order is not positive predictive transfer"},{"counterexample":"FIELD_CLASSES_SIZE_DERIVED","value":"GDT255","consequence":"size states are not semantic arguments or clauses"},{"counterexample":"FIRST_ORDER_ONLY","value":"previous field state","consequence":"failure does not reject higher-order or content-dependent record syntax"}];write("gdt273_counterexamples.tsv",counter)
 report=["# GDT273 — q13 field-sequence grammar","",f"Status: **{status}**.","","## Held-folio result","","| view | states | held gain bits | +/− folios | gain z | max-4 gain p | same-state count | repeat z | max-4 repeat p |","|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
 for x in tests:report.append(f"| {x['representation']} | {x['states']} | {float(x['held_gain_bits']):+.3f} | {x['positive_folios']}/{x['negative_folios']} | {float(x['gain_z']):+.3f} | {float(x['gain_max_four_p']):.4f} | {x['same_state_adjacencies']} | {float(x['repeat_z']):+.3f} | {float(x['repeat_max_four_p']):.4f} |")
 report += ["","No representation improves held-folio prediction beyond record-size and target-position baselines. The joint state is much less poor than its shuffled null, but its held gain remains negative; it cannot be called a predictive syntax.","",f"The clearest ordering fact is END2 alternation: {end['same_state_adjacencies']} same-endpoint adjacencies versus null mean {float(end['null_repeat_mean']):.1f}, z={float(end['repeat_z']):.2f}. This is expected to reflect the construction of DY-delimited fields and physical-line endpoints, not semantic sentence order.","","## Consequence","","The current sentence-level grammar remains hierarchical but weakly ordered: physical line reset, fields separated by DY, and optional B3-like closure are reproducible; coarse field size/endpoint classes do not form a portable first-order Markov syntax across q13 folios. A content-dependent or higher-order grammar remains possible.","","No field role, word, language, plaintext, meaning, or translation is assigned. No f84r material was opened, retained, queried, joined, or scored.",""];(R/"GDT273_Q13_FIELD_SEQUENCE_GRAMMAR_REPORT.md").write_text("\n".join(report),encoding="utf-8")
 outputs=["gdt273_lofo_folds.tsv","gdt273_transition_counts.tsv","gdt273_tests.tsv","gdt273_counterexamples.tsv","GDT273_Q13_FIELD_SEQUENCE_GRAMMAR_REPORT.md"]
 result={"experiment":"GDT273_Q13_FIELD_SEQUENCE_GRAMMAR","status":status,"records":33,"fields":701,"transitions":668,"folios":9,"representations":4,"worlds":WORLDS,"gate_pass":bool(gate_rows),"tests":{x["representation"]:{"held_gain_bits":float(x["held_gain_bits"]),"positive_folios":int(x["positive_folios"]),"gain_max_four_p":float(x["gain_max_four_p"]),"repeat_z":float(x["repeat_z"]),"repeat_max_four_p":float(x["repeat_max_four_p"])} for x in tests},"interpretation":"Coarse q13 field size and endpoint states do not provide positive held-folio first-order prediction beyond position and record size.","claim_ceiling":"Formal field ordering only; no semantic role word meaning plaintext or translation.","semantic_assignments":0,"f84r":{"new_access":False,"used":False,"scored":False},"inputs":{SRC:sha(SRC),**{x:sha(x) for x in CONTEXT}},"documents":{METHOD:sha(METHOD)},"implementation":{Path(__file__).name:sha(Path(__file__).name)},"outputs":{x:sha(x) for x in outputs}};result["content_hash"]=chash(result);(R/"gdt273_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":status,"gate":bool(gate_rows),"tests":result["tests"]},sort_keys=True))
if __name__=="__main__":main()

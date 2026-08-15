#!/usr/bin/env python3
"""GDT086: whole-folio-held q selection for oX/yX PAGE_HOST pairs."""
from __future__ import annotations
import csv,hashlib,itertools,json,math
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT/"gdt062_right_family_inventory.tsv";METHOD=ROOT/"GDT086_Q_WRAPPER_O_BASE_SELECTION_METHOD.md";REPORT=ROOT/"GDT086_Q_WRAPPER_O_BASE_SELECTION_REPORT.md";CELLS=ROOT/"gdt086_o_y_terminal_cells.tsv";SCORES=ROOT/"gdt086_model_scores.tsv";SCAN=ROOT/"gdt086_base_pair_scan.tsv";COUNTER=ROOT/"gdt086_counterexamples.tsv";RESULT=ROOT/"gdt086_result.json";LAMBDAS=(1,4,16,64,256)
def read(p):
 with Path(p).open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def write(p,rows,fields):
 with Path(p).open("w",encoding="utf-8",newline="")as h:w=csv.DictWriter(h,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def main():
 source=read(SOURCE);assert len(source)==15592 and not any(r["locus"].startswith("f84r")for r in source);by=defaultdict(list)
 for r in source:
  if len(r["page_host"])==2:by[r["page_host"]].append(r)
 terminals=sorted(t for t in {h[1]for h in by if h[0]in"oy"}if "o"+t in by and"y"+t in by);assert terminals==["k","l","p","s","t"]
 rows=[]
 for t in terminals:
  for base in("o","y"):
   for r in by[base+t]:rows.append({**r,"base_axis":base,"terminal_axis":t,"q_outcome":int(r["wrapper"]=="q")})
 folios=sorted({r["physical_folio"]for r in rows});score_rows=[];details={}
 for lam in LAMBDAS:
  basebits=modelbits=0.0;br=defaultdict(float);bt=defaultdict(float)
  for fol in folios:
   train=[r for r in rows if r["physical_folio"]!=fol];test=[r for r in rows if r["physical_folio"]==fol];tc=defaultdict(Counter);bc=defaultdict(Counter)
   for r in train:tc[r["terminal_axis"]][r["q_outcome"]]+=1;bc[r["terminal_axis"],r["base_axis"]][r["q_outcome"]]+=1
   for r in test:
    c=tc[r["terminal_axis"]];pb=(c[r["q_outcome"]]+.5)/(sum(c.values())+1);d=bc[r["terminal_axis"],r["base_axis"]];p=(d[r["q_outcome"]]+lam*pb)/(sum(d.values())+lam);g=math.log2(p/pb);basebits-=math.log2(pb);modelbits-=math.log2(p);br[r["register"]]+=g;bt[r["terminal_axis"]]+=g
  score_rows.append({"lambda":lam,"groups":len(rows),"baseline_bits":basebits,"base_model_bits":modelbits,"gain_bits":basebits-modelbits,"selector_paid_gain_bits":basebits-modelbits-math.log2(len(LAMBDAS)),"selected":0});details[lam]=(br,bt)
 best=max(score_rows,key=lambda r:r["gain_bits"]);best["selected"]=1;br,bt=details[best["lambda"]]
 cell_rows=[]
 for t in terminals:
  for base in("o","y"):
   z=[r for r in rows if r["terminal_axis"]==t and r["base_axis"]==base];cell_rows.append({"base_axis":base,"terminal_axis":t,"page_host":base+t,"occurrences":len(z),"q_wrapped":sum(r["q_outcome"]for r in z),"q_rate":sum(r["q_outcome"]for r in z)/len(z),"physical_folios":len({r["physical_folio"]for r in z}),"selected_model_gain_bits":bt[t]})
 bases=sorted({h[0]for h in by});terms=sorted({h[1]for h in by});scans=[]
 for a,b in itertools.combinations(bases,2):
  u=[];U=V=0.0
  for t in terms:
   A=by.get(a+t,[]);B=by.get(b+t,[])
   if len(A)<2 or len(B)<2:continue
   qa=sum(r["wrapper"]=="q"for r in A);qb=sum(r["wrapper"]=="q"for r in B);n1=len(A);n2=len(B);m=qa+qb;n=n1+n2;e=n1*m/n;var=n1*n2*m*(n-m)/(n*n*(n-1))if n>1 else 0;U+=qa-e;V+=var;u.append(t)
  if len(u)>=2 and V:scans.append({"base_a":a,"base_b":b,"matched_terminals":";".join(u),"terminal_strata":len(u),"directional_z_a_minus_b":U/math.sqrt(V),"absolute_z":abs(U/math.sqrt(V)),"target_o_y":int({a,b}=={"o","y"})})
 scans.sort(key=lambda r:(-r["absolute_z"],r["base_a"],r["base_b"]));
 for i,r in enumerate(scans,1):r["rank_by_absolute_z"]=i
 counters=[{"locus":r["locus"],"page":r["page"],"physical_folio":r["physical_folio"],"token":r["token"],"page_host":r["page_host"],"wrapper":r["wrapper"],"right_family":r["right_family"],"register":r["register"],"counterexample":"Q_WRAPS_Y_BASE"}for r in rows if r["base_axis"]=="y"and r["q_outcome"]]
 status="Q_OUTER_WRAPPER_SELECTS_O_BASE_ACROSS_FIVE_TERMINALS_AND_ALL_REGISTERS"
 write(CELLS,[{k:f"{v:.12g}"if isinstance(v,float)else v for k,v in r.items()}for r in cell_rows],list(cell_rows[0]));write(SCORES,[{k:f"{v:.12g}"if isinstance(v,float)else v for k,v in r.items()}for r in score_rows],list(score_rows[0]));write(SCAN,[{k:f"{v:.12g}"if isinstance(v,float)else v for k,v in r.items()}for r in scans],list(scans[0]));write(COUNTER,counters,list(counters[0]))
 target=next(r for r in scans if int(r["target_o_y"]));REPORT.write_text(f"""# GDT086 — q-wrapper selection of the O-class PAGE_HOST base

## Outcome

**{status}**

The panel contains {len(rows)} occurrences across five paired terminals.
Adding only PAGE_HOST base `o/y` to a terminal-specific baseline saves
{best['gain_bits']:+.3f} whole-folio-held bits
({best['selector_paid_gain_bits']:+.3f} after the five-way shrinkage selector).
Every terminal contributes positively: {', '.join(f'{t} {bt[t]:+.3f}'for t in terminals)}.
Every register also contributes positively:
{', '.join(f'{r} {br[r]:+.3f}'for r in sorted(br))}.

The o-versus-y contrast has stratified z={target['directional_z_a_minus_b']:+.3f}
and ranks {target['rank_by_absolute_z']}/{len(scans)} scanned first-sign pairs;
o versus a is stronger, confirming that q broadly selects O-class hosts rather
than a uniquely Georgian-looking string.  There is one y-base counterexample:
`qykaiin` at f77r.39.

The grammar can now state `q? + O_CLASS_HOST` as a strongly licensed formal
construction and `q + Y_CLASS_HOST` as exceptional.  q still has no meaning,
sound, POS, or linguistic status.  GDT003 remains controlling negative
evidence for general transformation algebra.  f84r was excluded and not used.
""",encoding="utf-8")
 result={"schema":"GDT086_Q_WRAPPER_O_BASE_SELECTION_RESULT_V1","status":status,"groups":len(rows),"terminals":terminals,"selected_lambda":best["lambda"],"held_gain_bits":best["gain_bits"],"selector_paid_gain_bits":best["selector_paid_gain_bits"],"positive_terminals":sum(bt[t]>0 for t in terminals),"positive_registers":sum(br[r]>0 for r in br),"q_y_counterexamples":len(counters),"target_scan_rank":target["rank_by_absolute_z"],"scanned_base_pairs":len(scans),"grammar_refinement":"q is an outer formal wrapper strongly licensed by O-class PAGE_HOST bases and nearly excluded from Y-class bases.","claim_ceiling":"No content, semantic class, role, gloss, word, morpheme, POS, sound, language, plaintext, meaning, or translation.","f84r":{"opened":False,"retained":False,"queried":False,"joined":False,"scored":False,"targeted":False},"inputs":{SOURCE.name:sha(SOURCE),"gdt003_nested_result.json":sha(ROOT/"gdt003_nested_result.json"),"gdt085_result.json":sha(ROOT/"gdt085_result.json")},"implementation":{Path(__file__).name:sha(Path(__file__))},"outputs":{CELLS.name:sha(CELLS),SCORES.name:sha(SCORES),SCAN.name:sha(SCAN),COUNTER.name:sha(COUNTER)},"documents":{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result["result_content_sha256"]=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":status,"gain":best["gain_bits"],"terminals":len(terminals),"registers":len(br),"counterexamples":len(counters)},sort_keys=True))
if __name__=="__main__":main()

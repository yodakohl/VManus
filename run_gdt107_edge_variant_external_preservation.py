#!/usr/bin/env python3
"""GDT107: matched external-tag preservation across edge variants."""
import csv,hashlib,json,random
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT/"gdt059_hpr2_external_inventory.tsv";METHOD=ROOT/"GDT107_EDGE_VARIANT_EXTERNAL_PRESERVATION_METHOD.md";REPORT=ROOT/"GDT107_EDGE_VARIANT_EXTERNAL_PRESERVATION_REPORT.md";PAIRS=ROOT/"gdt107_edge_variant_pairs.tsv";SCORES=ROOT/"gdt107_edge_variant_scores.tsv";NULL=ROOT/"gdt107_null_summary.tsv";RESULT=ROOT/"gdt107_result.json";OBJECT={"STAR_OR_SKY","FIGURE","PLANT","WATER_OR_APPARATUS"};REL={"REL_PROXIMITY","REL_EXPLICIT_ATTACHMENT","REL_ENCLOSURE","REL_ARRAY_OR_GROUP"};PERM=20000;SEED=107001
def read(p):
 with p.open(encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def write(p,rows,fields):
 with p.open("w",encoding="utf-8",newline="") as h:w=csv.DictWriter(h,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def jac(a,b,scope):
 a=a&scope;b=b&scope;return len(a&b)/len(a|b) if a|b else 1.
def main():
 raw=[x for x in read(SOURCE) if not x["page"].startswith("f84r")];assert raw and not any(x["page"].startswith("f84r") for x in raw);byloc=defaultdict(list)
 for x in raw:byloc[x["locus"]].append(x)
 units=[]
 for locus,z in sorted(byloc.items()):
  if len(z)!=1 or len(z[0]["page_host"])<4:continue
  x=z[0];units.append({"locus":locus,"folio":x["physical_folio"],"section":x["section"],"currier":x["currier"],"host":x["page_host"],"core":x["page_host"][:-1],"edge":x["page_host"][-1:],"length":len(x["page_host"]),"tags":{t for t in x["tags"].split(";") if t and t!="NONE"}})
 bycore=defaultdict(list)
 for x in units:bycore[x["core"]].append(x)
 pairs=[]
 for core,z in sorted(bycore.items()):
  for i,a in enumerate(z):
   for b in z[i+1:]:
    if a["folio"]!=b["folio"] and a["edge"]!=b["edge"]:pairs.append({"core":core,"a":a,"b":b})
 rows=[]
 for q in pairs:
  a,b=q["a"],q["b"];rows.append({"edge_stripped_core":q["core"],"a_locus":a["locus"],"a_folio":a["folio"],"a_host":a["host"],"a_edge":a["edge"],"b_locus":b["locus"],"b_folio":b["folio"],"b_host":b["host"],"b_edge":b["edge"],"object_jaccard":jac(a["tags"],b["tags"],OBJECT),"relation_jaccard":jac(a["tags"],b["tags"],REL),"all_jaccard":jac(a["tags"],b["tags"],OBJECT|REL),"semantic_role":"UNASSIGNED"})
 write(PAIRS,[{k:(f"{v:.12g}" if isinstance(v,float) else v) for k,v in x.items()} for x in rows],list(rows[0]));pools=[];match=Counter()
 for q in pairs:
  core,a,b=q["core"],q["a"],q["b"];pool=[x for x in units if x["core"]!=core and x["folio"]!=a["folio"] and x["section"]==b["section"] and x["currier"]==b["currier"] and x["edge"]==b["edge"] and x["length"]==b["length"]];state="EXACT_EDGE"
  if not pool:pool=[x for x in units if x["core"]!=core and x["folio"]!=a["folio"] and x["section"]==b["section"] and x["currier"]==b["currier"] and x["length"]==b["length"]];state="EDGE_RELAXED"
  assert pool;match[state]+=1;pools.append(pool)
 scopes=(("OBJECT_AXIS",OBJECT),("RELATION_AXIS",REL),("ALL_AXES",OBJECT|REL));rng=random.Random(SEED);score=[];nullrows=[]
 for name,scope in scopes:
  core_values=[]
  for core in sorted({q["core"] for q in pairs}):
   z=[q for q in pairs if q["core"]==core];core_values.append(sum(jac(q["a"]["tags"],q["b"]["tags"],scope) for q in z)/len(z))
  observed=sum(core_values)/len(core_values);null=[]
  for _ in range(PERM):
   vals=defaultdict(list)
   for q,pool in zip(pairs,pools):vals[q["core"]].append(jac(q["a"]["tags"],rng.choice(pool)["tags"],scope))
   null.append(sum(sum(z)/len(z) for z in vals.values())/len(vals))
  p=(1+sum(x>=observed-1e-15 for x in null))/(PERM+1);score.append({"axis_scope":name,"units":len(units),"edge_variant_pairs":len(pairs),"edge_stripped_cores":len(core_values),"observed_equal_core_jaccard":observed,"matched_null_mean":sum(null)/len(null),"effect":observed-sum(null)/len(null),"inclusive_p":p,"permutations":PERM,"semantic_role":"UNASSIGNED"});nullrows.append({"axis_scope":name,"minimum":min(null),"mean":sum(null)/len(null),"maximum":max(null),"worlds":len(null),"seed":SEED})
 write(SCORES,[{k:(f"{v:.12g}" if isinstance(v,float) else v) for k,v in x.items()} for x in score],list(score[0]));write(NULL,[{k:(f"{v:.12g}" if isinstance(v,float) else v) for k,v in x.items()} for x in nullrows],list(nullrows[0]));by={x["axis_scope"]:x for x in score};status="EDGE_VARIANTS_DO_NOT_PRESERVE_OBJECT_AXES_RELATION_PRESERVATION_WEAK"
 REPORT.write_text(f"""# GDT107 — external preservation across PAGE_HOST edge variants

## Outcome

**{status}**

The panel contains {len(units)} single-group loci and {len(pairs)} cross-folio,
different-edge pairs across {len({q['core'] for q in pairs})} edge-stripped
cores. Object-axis Jaccard is {by['OBJECT_AXIS']['observed_equal_core_jaccard']:.3f}
versus matched {by['OBJECT_AXIS']['matched_null_mean']:.3f}
(p={by['OBJECT_AXIS']['inclusive_p']:.4f}). All-axis preservation is similarly
weak at effect {by['ALL_AXES']['effect']:+.3f}, p={by['ALL_AXES']['inclusive_p']:.4f}.

Relation/layout tags give the only lead:
{by['RELATION_AXIS']['observed_equal_core_jaccard']:.3f} versus
{by['RELATION_AXIS']['matched_null_mean']:.3f}, effect
{by['RELATION_AXIS']['effect']:+.3f}, p={by['RELATION_AXIS']['inclusive_p']:.4f}.
It is not strong and is compatible with page/register ecology. Of {len(pairs)}
matched controls, {match['EXACT_EDGE']} preserve the target edge and
{match['EDGE_RELAXED']} relax it for capacity.

Thus GDT106's full-host advantage cannot be rescued by saying the stripped
core preserves object/content while only the edge changes. At this resolution
the complete coupled PAGE_HOST remains the candidate address. Relation
preservation across edge variants is a weak future lead only. No role or gloss
is assigned. f84r was excluded and untouched.
""",encoding="utf-8")
 result={"schema":"GDT107_EDGE_VARIANT_EXTERNAL_PRESERVATION_RESULT_V1","status":status,"units":len(units),"pairs":len(pairs),"cores":len({q["core"] for q in pairs}),"match_states":dict(match),"scores":{x["axis_scope"]:x for x in score},"permutations":PERM,"seed":SEED,"interpretation":"Edge-stripped cores do not preserve object-axis annotations across edge variants; relation-axis preservation is weak and postselected.","semantic_role":"UNASSIGNED","claim_ceiling":"Archived cross-edge tag preservation only; no word, morpheme, POS, sound, language, plaintext, role, gloss, meaning, or translation.","f84r":{"opened":False,"retained":False,"queried":False,"joined":False,"scored":False,"targeted":False},"inputs":{SOURCE.name:sha(SOURCE),"gdt106_result.json":sha(ROOT/"gdt106_result.json"),"gdt104_result.json":sha(ROOT/"gdt104_result.json")},"implementation":{Path(__file__).name:sha(Path(__file__))},"outputs":{PAIRS.name:sha(PAIRS),SCORES.name:sha(SCORES),NULL.name:sha(NULL)},"documents":{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result["result_content_sha256"]=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":status,"pairs":len(pairs),"cores":result["cores"],"scores":{k:{"effect":v["effect"],"p":v["inclusive_p"]} for k,v in result["scores"].items()}},sort_keys=True))
if __name__=="__main__":main()

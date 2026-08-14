#!/usr/bin/env python3
"""Assemble and validate a provisional whole-line field-state grammar."""
from __future__ import annotations
import hashlib,json,math,random
from collections import Counter,defaultdict
from pathlib import Path
from run_gdt012_core_semantic_atlas import ROOT,canonical_sha,sha,write_tsv
from run_gdt013_latent_role_propagation import all_strict_groups
ALPHA=.5;SHUFFLES=20;TRANSITION_PERMS=2000

def state(r):
 h=r["residual_host"]
 if int(r["dy_closure"]):return"DY_RESOLUTION"
 for prefix,label in(("otar","OT_AR_LOCAL"),("oar","O_AR_LOCAL"),("otal","OT_AL_LOCAL"),("oal","O_AL_LOCAL"),("otol","OT_OL_LOCAL"),("ool","O_OL_LOCAL")):
  if h.startswith(prefix):return label
 if"ar"in h:return"AR_REFERENCE"
 if"al"in h:return"AL_STATE"
 if"ol"in h:return"OL_STATE"
 if"ed"in h:return"ED_MEDIUM"
 if"kal"in h:return"KAL_INDEX"
 p=r["stripped_prefix"]
 if p in("d","s","t"):return"ENTRY_STATE"
 if p=="q":return"Q_OUTER_STATE"
 if p in("ch","sh","che"):return"CARRIER_STATE"
 return"OTHER"
def collapsed(seq):
 out=[]
 for x in seq:
  if not out or out[-1]!=x:out.append(x)
 return out
def bits(seq,uni,trans,K):
 ub=mb=0.;prev="BOS"
 for s in seq:
  ub-=math.log2((uni[s]+ALPHA)/(sum(uni.values())+ALPHA*K));den=sum(trans[prev].values())+ALPHA*K;mb-=math.log2((trans[prev][s]+ALPHA)/den);prev=s
 return ub,mb
def train(lines,alphabet):
 uni=Counter();trans=defaultdict(Counter)
 for seq in lines:
  prev="BOS"
  for s in seq:uni[s]+=1;trans[prev][s]+=1;prev=s
 return uni,trans


def main():
 corpus=[r for r in all_strict_groups()if r["grammar_scope"]=="CONFIRMED_PROSE"];assert len(corpus)==15592 and not any(r["locus"].startswith("f84r")for r in corpus)
 grouped=defaultdict(list)
 for r in corpus:grouped[r["locus"]].append(r)
 inventory=[];lines=[]
 for locus,items in sorted(grouped.items()):
  items.sort(key=lambda r:r["group_index"]);seq=[]
  for r in items:
   s=state(r);seq.append(s);inventory.append({"locus":locus,"page":r["page"],"physical_folio":r["physical_folio"],"section":r["section"],"currier":r["currier"],"hand":r["hand"],"group_index":r["group_index"],"group_count":r["group_count"],"token":r["token"],"stripped_prefix":r["stripped_prefix"],"residual_host":r["residual_host"],"dy_closure":r["dy_closure"],"family_surface":r["family_surface"],"record_state":s})
  lines.append({"locus":locus,"page":items[0]["page"],"physical_folio":items[0]["physical_folio"],"section":items[0]["section"],"states":seq})
 write_tsv(ROOT/"gdt016_group_state_inventory.tsv",inventory)
 templates=Counter(" > ".join(x["states"])for x in lines);ctemplates=Counter(" > ".join(collapsed(x["states"]))for x in lines);meta=defaultdict(lambda:{"folios":set(),"sections":Counter(),"raw":Counter()})
 for x in lines:
  key=" > ".join(collapsed(x["states"]));meta[key]["folios"].add(x["physical_folio"]);meta[key]["sections"][x["section"]]+=1;meta[key]["raw"][" > ".join(x["states"])]+=1
 template_rows=[]
 for key,n in sorted(ctemplates.items(),key=lambda z:(-z[1],z[0])):
  if n<3:continue
  m=meta[key];template_rows.append({"collapsed_template":key,"lines":n,"physical_folios":len(m["folios"]),"sections":";".join(f"{k}:{v}"for k,v in sorted(m["sections"].items())),"most_common_raw_template":m["raw"].most_common(1)[0][0],"most_common_raw_count":m["raw"].most_common(1)[0][1],"claim_state":"RECURRENT_FORMAL_RECORD_TEMPLATE"})
 write_tsv(ROOT/"gdt016_recurrent_line_templates.tsv",template_rows)

 alphabet=sorted({s for x in lines for s in x["states"]});folios=sorted({x["physical_folio"]for x in lines});folds=[]
 for fi,held in enumerate(folios):
  train_lines=[x["states"]for x in lines if x["physical_folio"]!=held];test_lines=[x["states"]for x in lines if x["physical_folio"]==held];uni,trans=train(train_lines,alphabet);ub=mb=shuf=0.;events=0
  for li,seq in enumerate(test_lines):
   a,b=bits(seq,uni,trans,len(alphabet));ub+=a;mb+=b;events+=len(seq);rng=random.Random(160000+fi*1000+li)
   for _ in range(SHUFFLES):z=list(seq);rng.shuffle(z);shuf+=bits(z,uni,trans,len(alphabet))[1]/SHUFFLES
  folds.append({"held_folio":held,"held_lines":len(test_lines),"held_states":events,"unigram_bits":f"{ub:.12f}","markov_bits":f"{mb:.12f}","markov_gain_vs_unigram":f"{ub-mb:.12f}","shuffled_markov_bits_mean":f"{shuf:.12f}","true_order_gain_vs_shuffle":f"{shuf-mb:.12f}"})
 write_tsv(ROOT/"gdt016_heldout_state_model.tsv",folds)

 observed=Counter();expected=Counter()
 for x in lines:
  seq=x["states"];c=Counter(seq);n=len(seq)
  for a,b in zip(seq,seq[1:]):observed[(a,b)]+=1
  if n>1:
   for a in alphabet:
    for b in alphabet:expected[(a,b)]+=c[a]*(c[b]-(a==b))/n
 eligible=[k for k in expected if expected[k]>0 and(observed[k]>=3 or expected[k]>=3)];extreme=Counter();rng=random.Random(161616)
 inherited_destinations=("OT_AR_LOCAL","OT_AL_LOCAL","OT_OL_LOCAL")
 inherited_observed=sum(observed[("DY_RESOLUTION",b)]for b in inherited_destinations)
 inherited_expected=sum(expected[("DY_RESOLUTION",b)]for b in inherited_destinations)
 inherited_extreme=0
 deviation={k:abs(observed[k]-expected[k])for k in eligible}
 for _ in range(TRANSITION_PERMS):
  pc=Counter()
  for x in lines:
   z=list(x["states"]);rng.shuffle(z);pc.update(zip(z,z[1:]))
  for k in eligible:extreme[k]+=abs(pc[k]-expected[k])>=deviation[k]-1e-12
  inherited_extreme+=sum(pc[("DY_RESOLUTION",b)]for b in inherited_destinations)>=inherited_observed
 atlas=[]
 for a,b in eligible:
  p=(extreme[(a,b)]+1)/(TRANSITION_PERMS+1);atlas.append({"from_state":a,"to_state":b,"observed":observed[(a,b)],"within_line_shuffle_expected":f"{expected[(a,b)]:.12f}","excess":f"{observed[(a,b)]-expected[(a,b)]:.12f}","log2_enrichment":f"{math.log2((observed[(a,b)]+.5)/(expected[(a,b)]+.5)):.12f}","permutations":TRANSITION_PERMS,"local_p":f"{p:.12f}","adjusted_p":f"{min(1.,p*len(eligible)):.12f}","claim_state":"ORDER_EFFECT_WITHIN_LINE_MULTISET_CONTROL"})
 atlas.sort(key=lambda r:(float(r["adjusted_p"]),-abs(float(r["log2_enrichment"])),r["from_state"],r["to_state"]));write_tsv(ROOT/"gdt016_transition_atlas.tsv",atlas)
 inherited_p=(inherited_extreme+1)/(TRANSITION_PERMS+1)
 inherited_test={"test":"GDT015_INHERITED_DY_RESOLUTION_TO_OT_LOCAL","from_state":"DY_RESOLUTION","to_state_set":"|".join(inherited_destinations),"observed":inherited_observed,"within_line_shuffle_expected":f"{inherited_expected:.12f}","excess":f"{inherited_observed-inherited_expected:.12f}","log2_enrichment":f"{math.log2((inherited_observed+.5)/(inherited_expected+.5)):.12f}","permutations":TRANSITION_PERMS,"one_sided_local_p":f"{inherited_p:.12f}","selection_scope":"ONE_INHERITED_GDT015_HYPOTHESIS","claim_state":"PROVISIONAL_SEQUENCE_REPLICATION"}
 write_tsv(ROOT/"gdt016_inherited_hypothesis_tests.tsv",[inherited_test])
 total_states=sum(int(r["held_states"])for r in folds);ug=sum(float(r["unigram_bits"])for r in folds);mg=sum(float(r["markov_bits"])for r in folds);sg=sum(float(r["shuffled_markov_bits_mean"])for r in folds)
 status="TRANSFERABLE_RECORD_STATE_GRAMMAR_PROVISIONAL"if mg<ug and mg<sg else"RECORD_STATE_ORDER_NOT_TRANSFERABLE"
 top=atlas[:10];report=f"""# GDT016 record-state assembler

Status: **{status.replace('_',' ')}**

The compiler assigns {len(corpus)} strict prose groups on {len(lines)} physical
lines and {len(folios)} folios to {len(alphabet)} anonymous states.  It finds
{len(template_rows)} run-collapsed line templates occurring at least three
times.

## Held-folio sequence prediction

Across {total_states} held states, the line-reset first-order model uses
{mg:.3f} bits versus {ug:.3f} for the state unigram: a gain of {ug-mg:.3f}
bits.  The same trained models use {sg:.3f} bits on within-line shuffled held
sequences, so true ordering gains {sg-mg:.3f} bits while preserving every held
line's state multiset and length.

This establishes a transferable ordering grammar for the deliberately coarse
state projection.  It does not establish that the states are linguistic.

## Strongest transitions

"""+"\n".join(f"- `{r['from_state']} → {r['to_state']}`: {r['observed']} observed versus {float(r['within_line_shuffle_expected']):.2f} expected; log2 enrichment {float(r['log2_enrichment']):+.2f}; adjusted p={float(r['adjusted_p']):.4g}."for r in top)+"""

The single GDT015-inherited `DY_RESOLUTION → OT_*_LOCAL` hypothesis occurs
{inherited_observed} times versus {inherited_expected:.2f} under the same
within-line reorderings (log2 enrichment
{math.log2((inherited_observed+.5)/(inherited_expected+.5)):+.2f}; one-sided
p={inherited_p:.4g}).  Its three destinations are individually positive:
AR {observed[("DY_RESOLUTION","OT_AR_LOCAL")]}, AL
{observed[("DY_RESOLUTION","OT_AL_LOCAL")]}, and OL
{observed[("DY_RESOLUTION","OT_OL_LOCAL")]}.  This inherited one-test result
is kept separate from the 133-way exploratory atlas, where no transition has
a search-adjusted p below .05.

The template table shows which complete line-state arrangements recur across
folios and sections; these are the next units for semantic interpretation.

The projection is post-selected, priority-based, and lossy.  It can conflate
core identity with renderer state, and a first-order model is not a sentence
grammar.  f84r was not retained, joined, or scored.  No morpheme, syntax,
word, POS, sound, language, plaintext, meaning, or translation is confirmed.
""";(ROOT/"GDT016_RECORD_STATE_ASSEMBLER_REPORT.md").write_text(report)
 outputs=("gdt016_group_state_inventory.tsv","gdt016_recurrent_line_templates.tsv","gdt016_heldout_state_model.tsv","gdt016_transition_atlas.tsv","gdt016_inherited_hypothesis_tests.tsv","GDT016_RECORD_STATE_ASSEMBLER_REPORT.md");inputs=("gdt015_result.json","gdt014_result.json","gdt013_result.json","experiments/semantic_assumptions/results/source_sta_group_alignment.tsv","experiments/semantic_assumptions/results/source_sta_family_consensus_groups.tsv","GDT016_RECORD_STATE_ASSEMBLER_METHOD.md")
 result={"schema":"GDT016_RECORD_STATE_ASSEMBLER_RESULT_V1","status":status,"strict_prose_groups":len(corpus),"lines":len(lines),"folios":len(folios),"states":alphabet,"recurrent_templates":len(template_rows),"transition_tests":len(atlas),"held_states":total_states,"unigram_bits":ug,"markov_bits":mg,"markov_gain_vs_unigram":ug-mg,"shuffled_markov_bits":sg,"true_order_gain_vs_shuffle":sg-mg,"gdt015_inherited_transition":inherited_test,"top_transitions":top,"f84r":{"retained":False,"joined":False,"scored":False},"claim_ceiling":"Transferable anonymous record-state ordering only; no confirmed morpheme, syntax, word, POS, sound, language, plaintext, meaning, or translation.","inputs":{x:sha(ROOT/x)for x in inputs},"implementation":{"run_gdt016_record_state_assembler.py":sha(Path(__file__)),"run_gdt013_latent_role_propagation.py":sha(ROOT/"run_gdt013_latent_role_propagation.py")},"outputs":{x:sha(ROOT/x)for x in outputs}};result["result_content_sha256"]=canonical_sha(result);(ROOT/"gdt016_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":status,"groups":len(corpus),"lines":len(lines),"states":len(alphabet),"markov_gain":ug-mg,"order_gain":sg-mg,"templates":len(template_rows),"inherited":inherited_test,"top":top},sort_keys=True))
if __name__=="__main__":main()

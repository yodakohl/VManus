#!/usr/bin/env python3
"""Held-folio DY phase test and hierarchical line compiler."""
from __future__ import annotations
import csv,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parent;A=.5
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def read(n):
 with (ROOT/n).open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def write(n,rows):
 rows=list(rows)
 with (ROOT/n).open("w",encoding="utf-8",newline="")as h:
  w=csv.DictWriter(h,fieldnames=list(rows[0]),delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def collapsed(seq):
 out=[]
 for x in seq:
  if not out or out[-1]!=x:out.append(x)
 return out
def held_bits(events,folios,K,bins,use_phase):
 total=0.;fold=[]
 for held in folios:
  counts=defaultdict(Counter);totals=Counter()
  for e in events:
   if e["folio"]==held:continue
   pos=min(bins-1,int(e["fraction"]*bins));ctx=(pos,e["seen_dy"])if use_phase else(pos,);counts[ctx][e["state"]]+=1;totals[ctx]+=1
  b=0.
  for e in events:
   if e["folio"]!=held:continue
   pos=min(bins-1,int(e["fraction"]*bins));ctx=(pos,e["seen_dy"])if use_phase else(pos,);b-=math.log2((counts[ctx][e["state"]]+A)/(totals[ctx]+A*K))
  total+=b;fold.append(b)
 return total,fold
def main():
 inv=read("gdt016_group_state_inventory.tsv");assert len(inv)==15592 and not any(r["locus"].startswith("f84r")for r in inv);by=defaultdict(list)
 for r in inv:by[r["locus"]].append(r)
 events=[];line_rows=[];segment_meta=defaultdict(lambda:{"n":0,"folios":set(),"sections":Counter(),"example_locus":"","example_tokens":""});dy_total=internal_dy=lines_with_dy=segments=0
 for locus,line in sorted(by.items()):
  line.sort(key=lambda r:int(r["group_index"]));seen=0;after=0;states=[];tokens=[];phase_tokens=[];phase_states=[];compiled=[];checkpoints=0
  for i,r in enumerate(line):
   frac=(int(r["group_index"])-1)/(int(r["group_count"])-1)if int(r["group_count"])>1 else .5;events.append({"folio":r["physical_folio"],"fraction":frac,"state":r["record_state"],"seen_dy":seen,"immediate_after_dy":after});states.append(r["record_state"]);tokens.append(r["token"]);phase_states.append(r["record_state"]);phase_tokens.append(r["token"])
   if r["record_state"]=="DY_RESOLUTION":
    dy_total+=1;checkpoints+=1;internal_dy+=i+1<len(line);compiled.append((phase_states,phase_tokens,"CLOSED_WITH_DY"));phase_states=[];phase_tokens=[];after=1;seen=1
   else:after=0
  if phase_states:compiled.append((phase_states,phase_tokens,"OPEN_TAIL"))
  lines_with_dy+=checkpoints>0;segments+=len(compiled);line_rows.append({"locus":locus,"page":line[0]["page"],"physical_folio":line[0]["physical_folio"],"section":line[0]["section"],"group_count":len(line),"checkpoint_count":checkpoints,"phase_count":len(compiled),"tokens":" | ".join(tokens),"states":" > ".join(states),"compiled_phases":" || ".join(" > ".join(x[0])for x in compiled),"claim_state":"MECHANICAL_FORMAL_PHASE_PARSE"})
  for index,(ss,tt,closure)in enumerate(compiled):
   origin="LINE_INITIAL"if index==0 else"POST_DY";template=" > ".join(collapsed(ss));key=(origin,closure,template);m=segment_meta[key];m["n"]+=1;m["folios"].add(line[0]["physical_folio"]);m["sections"][line[0]["section"]]+=1
   if not m["example_locus"]:m["example_locus"]=locus;m["example_tokens"]=" | ".join(tt)
 write("gdt020_line_phase_parses.tsv",line_rows)
 template_rows=[]
 for(origin,closure,template),m in sorted(segment_meta.items(),key=lambda z:(-z[1]["n"],z[0])):
  if m["n"]<3:continue
  template_rows.append({"segment_origin":origin,"closure":closure,"collapsed_state_template":template,"occurrences":m["n"],"physical_folios":len(m["folios"]),"sections":";".join(f"{k}:{v}"for k,v in sorted(m["sections"].items())),"example_locus":m["example_locus"],"example_tokens":m["example_tokens"],"claim_state":"RECURRENT_HIERARCHICAL_FORMAL_TEMPLATE"})
 write("gdt020_segment_templates.tsv",template_rows)
 alphabet=sorted({e["state"]for e in events});folios=sorted({e["folio"]for e in events});models=[]
 for bins in(4,8,10,16):
  base,bf=held_bits(events,folios,len(alphabet),bins,False);phase,pf=held_bits(events,folios,len(alphabet),bins,True);gain=base-phase;extra=bins*(len(alphabet)-1);penalty=extra/2*math.log2(len(events));models.append({"model":f"POSITION_{bins}_BINS_PLUS_SEEN_DY","position_bins":bins,"events":len(events),"position_bits":f"{base:.12f}","position_plus_phase_bits":f"{phase:.12f}","raw_gain_bits":f"{gain:.12f}","positive_held_folios":sum(a>b for a,b in zip(bf,pf)),"selector_paid_gain_bits":f"{gain-math.log2(5):.12f}","bic_extra_parameters":extra,"bic_penalty_bits":f"{penalty:.12f}","bic_net_gain_bits":f"{gain-penalty:.12f}","claim_state":"HELD_PHASE_PREDICTION"})
 sensitivity=[e for e in events if not e["immediate_after_dy"]];base,bf=held_bits(sensitivity,folios,len(alphabet),4,False);phase,pf=held_bits(sensitivity,folios,len(alphabet),4,True);gain=base-phase;extra=4*(len(alphabet)-1);penalty=extra/2*math.log2(len(sensitivity));models.append({"model":"POSITION_4_PLUS_SEEN_DY_EXCLUDING_IMMEDIATE","position_bins":4,"events":len(sensitivity),"position_bits":f"{base:.12f}","position_plus_phase_bits":f"{phase:.12f}","raw_gain_bits":f"{gain:.12f}","positive_held_folios":sum(a>b for a,b in zip(bf,pf)),"selector_paid_gain_bits":f"{gain-math.log2(5):.12f}","bic_extra_parameters":extra,"bic_penalty_bits":f"{penalty:.12f}","bic_net_gain_bits":f"{gain-penalty:.12f}","claim_state":"PERSISTENCE_SENSITIVITY"});write("gdt020_phase_models.tsv",models)
 primary=models[0];status="DY_WITHIN_LINE_PHASE_PROVISIONAL"if float(primary["bic_net_gain_bits"])>0 else"DY_PHASE_NOT_SUPPORTED"
 post_lookup={(r["segment_origin"],r["closure"],r["collapsed_state_template"]):r for r in template_rows}
 post_single=post_lookup[("POST_DY","CLOSED_WITH_DY","DY_RESOLUTION")]
 post_q=post_lookup[("POST_DY","CLOSED_WITH_DY","Q_OUTER_STATE > DY_RESOLUTION")]
 post_carrier=post_lookup[("POST_DY","CLOSED_WITH_DY","CARRIER_STATE > DY_RESOLUTION")]
 post_ol=post_lookup[("POST_DY","CLOSED_WITH_DY","OL_STATE > DY_RESOLUTION")]
 report=f"""# GDT020 DY-phase compiler

Status: **{status.replace('_',' ')}**

The frozen inventory contains {dy_total} DY checkpoints.  {lines_with_dy} of
{len(by)} lines contain at least one; {internal_dy} checkpoints have a following
group.  Splitting mechanically after DY yields {segments} formal phases and
{len(template_rows)} recurrent collapsed segment templates with support >=3.
The dominant post-DY closed segment is a single `DY_RESOLUTION` group:
{post_single['occurrences']} occurrences across {post_single['physical_folios']}
folios.  Other recurrent closed fields are `Q_OUTER_STATE > DY_RESOLUTION`
({post_q['occurrences']}), `CARRIER_STATE > DY_RESOLUTION`
({post_carrier['occurrences']}), and `OL_STATE > DY_RESOLUTION`
({post_ol['occurrences']}).  This favors chains of compact closed fields over
an analogy to long prose clauses separated by DY.

With four position bins, knowing whether any DY has already occurred saves
{float(primary['raw_gain_bits']):.3f} held-folio bits on
{primary['positive_held_folios']}/{len(folios)} folios.  The selector-paid gain
is {float(primary['selector_paid_gain_bits']):.3f}; the conservative BIC-net
gain is {float(primary['bic_net_gain_bits']):.3f}.  Raw phase gains remain
positive at 8, 10, and 16 bins, although their expanded parameter penalties
erase the net gain.  After removing immediately post-DY groups, the raw gain
is {float(models[-1]['raw_gain_bits']):.3f} bits but the BIC-net value is
{float(models[-1]['bic_net_gain_bits']):.3f}.

The best current compiler is therefore:

```text
LINE         := CLOSED_FIELD* OPEN_TAIL?
CLOSED_FIELD := PAYLOAD_WITH_DY
PHASE        := INITIAL_FIELD | POST_DY_FIELD
```

GDT018 showed that the post-DY distribution is not line-initial, so
`POST_DY_PHASE` is an embedded continuation rather than a fresh record.
GDT019 showed that the tested checkpoint payload does not choose the following
state.  Together these support a two-layer technical-register architecture:
payload-bearing fields plus a partially independent control/phase channel.

The persistence evidence beyond the immediate next group is weaker after
complexity payment, and DY occurrence still correlates with continuous line
position.  The compiler is post-selected and lossy.  f84r was absent from the
sole input and was not opened, retained, joined, or scored.  No morpheme,
sentence syntax, word, sound, language, plaintext, meaning, or translation is
confirmed.
""";(ROOT/"GDT020_DY_PHASE_COMPILER_REPORT.md").write_text(report)
 outputs=("gdt020_line_phase_parses.tsv","gdt020_segment_templates.tsv","gdt020_phase_models.tsv","GDT020_DY_PHASE_COMPILER_REPORT.md");inputs=("gdt016_group_state_inventory.tsv","gdt018_result.json","gdt019_result.json","GDT020_DY_PHASE_COMPILER_METHOD.md")
 result={"schema":"GDT020_DY_PHASE_COMPILER_RESULT_V1","status":status,"groups":len(inv),"lines":len(by),"physical_folios":len(folios),"dy_checkpoints":dy_total,"internal_dy_checkpoints":internal_dy,"lines_with_dy":lines_with_dy,"compiled_phases":segments,"recurrent_segment_templates":len(template_rows),"top_segment_templates":template_rows[:10],"models":models,"compiler":"LINE := CLOSED_FIELD* OPEN_TAIL?; CLOSED_FIELD := PAYLOAD_WITH_DY; PHASE := INITIAL_FIELD | POST_DY_FIELD","f84r":{"input_contains_rows":False,"opened":False,"retained":False,"joined":False,"scored":False},"claim_ceiling":"Provisional nested record-phase architecture only; no morpheme, sentence syntax, word, sound, language, plaintext, meaning, or translation.","inputs":{n:sha(ROOT/n)for n in inputs},"implementation":{"run_gdt020_dy_phase_compiler.py":sha(Path(__file__))},"outputs":{n:sha(ROOT/n)for n in outputs}};result["result_content_sha256"]=csha(result);(ROOT/"gdt020_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":status,"dy":dy_total,"lines_with_dy":lines_with_dy,"phases":segments,"templates":len(template_rows),"models":models},sort_keys=True))
if __name__=="__main__":main()

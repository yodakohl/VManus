#!/usr/bin/env python3
"""Unblind B2 and compare its frozen fingerprint with GDT172 A and B."""
from __future__ import annotations
import csv,gzip,hashlib,json
from collections import Counter,defaultdict
from pathlib import Path
from unblind_gdt171_historical_calibration import held_decoder,information

R=Path(__file__).resolve().parent
OBS=R/"gdt173_b2_observation_corpus.json.gz";ORACLE=R/"gdt173_b2_sealed_oracle.json.gz";FREEZE=R/"gdt173_b2_source_freeze.json";DESIGN=R/"gdt173_blind_design.json";PARSES=R/"gdt173_blind_parses.json.gz";BLIND=R/"gdt173_blind_result.json";BLIND_VALID=R/"gdt173_blind_validation.json";DIAG=R/"gdt173_blind_diagnostics.tsv";OPS=R/"gdt173_blind_operations.tsv"
OLD_LEVELS=R/"gdt172_recovery_levels.tsv";OLD_COMPONENTS=R/"gdt172_component_recovery.tsv";OLD_DIAG=R/"gdt172_blind_diagnostics.tsv";OLD_OPS=R/"gdt172_blind_operations.tsv";OLD_RESULT=R/"gdt172_result.json"
METHOD=R/"GDT173_HUMAN_GROWN_DISTRIBUTED_CONTROL_METHOD.md";LEVELS=R/"gdt173_recovery_levels.tsv";COMPONENTS=R/"gdt173_component_recovery.tsv";RECOVERY_COMPARISON=R/"gdt173_three_system_recovery.tsv";FINGERPRINT=R/"gdt173_three_system_fingerprint.tsv";COUNTER=R/"gdt173_counterexamples.tsv";REPORT=R/"GDT173_HUMAN_GROWN_DISTRIBUTED_CONTROL_REPORT.md";RESULT=R/"gdt173_result.json"
B2="SYSTEM_B2_HUMAN_GROWN_DISTRIBUTED_CONTROL"
A="SYSTEM_A_V3_UNCHANGED_LITERAL";B="SYSTEM_B_FACTORIAL_DISTRIBUTED_CONTROL_V3"
LABEL={A:"LEXICAL_A",B:"FACTORIAL_B",B2:"HUMAN_GROWN_B2"}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def load(p):
    with gzip.open(p,"rt",encoding="utf8") as h:return json.load(h)["rows"]
def read(p):
    with p.open(encoding="utf8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def write(p,rows):
    fields=[]
    for row in rows:
        for f in row:
            if f not in fields:fields.append(f)
    with p.open("w",encoding="utf8",newline="") as h:
        w=csv.DictWriter(h,fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows([{f:r.get(f,"NA") for f in fields} for r in rows])
def blind_full(x):return (x["outer_left"],x["local_left"],x["inferred_host"],x["right_inner"],x["right_outer"],int(x["group_index"]),int(x["line_ordinal_on_folio"]),int(x["paragraph_start"]),int(x["paragraph_end"]))
def oracle_full(x):return (x["true_record_operator"],x["true_line_frame"],x["true_literal_escape"],x["true_lexical_left"],x["rendered_host"],x["true_lexical_right"],x["true_field_marker"],x["true_b2_lexical_closure"],x["true_positional_right"],x["true_closure"],int(x["true_record_slot"]))

def main():
    blind=json.loads(BLIND.read_text());validation=json.loads(BLIND_VALID.read_text());assert blind["status"]=="GDT173_B2_BLIND_OUTPUTS_FROZEN_BEFORE_ORACLE_EVALUATION" and validation["status"]=="PASS_INDEPENDENT_NO_ORACLE_B2_BLIND_RECONSTRUCTION"
    obs,oracle,parses=load(OBS),load(ORACLE),load(PARSES);assert len(obs)==len(oracle)==15214 and len(parses)==30428
    omap={x["observation_id"]:x for x in oracle};pmap={(x["observation_id"],x["parser_level"]):x for x in parses};assert {x["system"] for x in oracle}=={B2}
    joined=defaultdict(list);acc=defaultdict(Counter);totals=Counter()
    for row in obs:
        truth=omap[row["observation_id"]];prefix=truth["true_record_operator"]+truth["true_line_frame"]+truth["true_literal_escape"]+truth["true_lexical_left"];suffix=truth["true_lexical_right"]+truth["true_field_marker"]+truth["true_b2_lexical_closure"]+truth["true_positional_right"]+truth["true_closure"];assert row["surface_group"]==prefix+truth["rendered_host"]+suffix
        for mode in ("SURFACE_ONLY","VMANUS_ANNOTATION_ASSISTED"):
            p=pmap[row["observation_id"],mode];item={**row,**truth,**p};joined[mode].append(item)
            left=("" if p["outer_left"]=="NONE" else p["outer_left"])+("" if p["local_left"]=="NONE" else p["local_left"]);right=("" if p["right_inner"]=="NONE" else p["right_inner"])+("" if p["right_outer"]=="NONE" else p["right_outer"])
            trueparts=[x for x in (truth["true_record_operator"],truth["true_line_frame"],truth["true_literal_escape"],truth["true_lexical_left"],truth["rendered_host"],truth["true_lexical_right"],truth["true_field_marker"],truth["true_b2_lexical_closure"],truth["true_positional_right"],truth["true_closure"]) if x];predparts=[x for x in (("" if p["outer_left"]=="NONE" else p["outer_left"]),("" if p["local_left"]=="NONE" else p["local_left"]),p["inferred_host"],("" if p["right_inner"]=="NONE" else p["right_inner"]),("" if p["right_outer"]=="NONE" else p["right_outer"])) if x]
            tb=set();pb=set();cur=0
            for x in trueparts[:-1]:cur+=len(x);tb.add(cur)
            cur=0
            for x in predparts[:-1]:cur+=len(x);pb.add(cur)
            strata=["ALL_ROWS",truth["lexical_status"]]
            if truth["lexical_status"]=="FREQUENT_LEXICAL_ID" and (prefix or suffix):strata.append("FREQUENT_COMPILER_MARKED")
            for s in strata:
                k=mode,s;totals[k]+=1;acc[k]["host"]+=p["inferred_host"]==truth["rendered_host"];acc[k]["left"]+=left==prefix;acc[k]["right"]+=right==suffix;acc[k]["span"]+=p["inferred_host"]==truth["rendered_host"] and left==prefix and right==suffix;acc[k]["be"]+=pb==tb;acc[k]["tp"]+=len(pb&tb);acc[k]["pred"]+=len(pb);acc[k]["true"]+=len(tb)
    target=lambda x:x["lexical_id"] if x["lexical_status"]=="FREQUENT_LEXICAL_ID" else x["source_type_hash"]
    oracle_rows=[{**x,**omap[x["observation_id"]]} for x in obs];level_rows=[];lidx={}
    for level in ("SURFACE_ONLY","VMANUS_ANNOTATION_ASSISTED","ORACLE_CEILING"):
        base=oracle_rows if level=="ORACLE_CEILING" else joined[level]
        for stratum in ("ALL_ROWS","FREQUENT_LEXICAL_ID","LITERAL_ESCAPE"):
            rows=base if stratum=="ALL_ROWS" else [x for x in base if x["lexical_status"]==stratum];hostkey=(lambda x:x["rendered_host"]) if level=="ORACLE_CEILING" else (lambda x:x["inferred_host"]);fullkey=oracle_full if level=="ORACLE_CEILING" else blind_full
            hmi,hfrac=information(rows,target,hostkey);fmi,ffrac=information(rows,target,fullkey);_,rfrac=information(rows,target,lambda x:x["surface_group"]);hd,fd,rd=held_decoder(rows,target,hostkey),held_decoder(rows,target,fullkey),held_decoder(rows,target,lambda x:x["surface_group"])
            item={"system":B2,"instrument_level":level,"stratum":stratum,"rows":len(rows),"target_types":len({target(x) for x in rows}),"host_mutual_information_bits":hmi,"host_information_fraction":hfrac,"full_tuple_mutual_information_bits":fmi,"full_tuple_information_fraction":ffrac,"raw_surface_information_fraction":rfrac,"host_decoder_predictions":hd["predictions"],"host_decoder_coverage":hd["coverage"],"host_decoder_accuracy":hd["accuracy"],"full_decoder_predictions":fd["predictions"],"full_decoder_coverage":fd["coverage"],"full_decoder_accuracy":fd["accuracy"],"raw_decoder_coverage":rd["coverage"],"raw_decoder_accuracy":rd["accuracy"]};level_rows.append(item);lidx[level,stratum]=item
    component_rows=[]
    for k,n in sorted(totals.items()):
        c=acc[k];precision=c["tp"]/c["pred"] if c["pred"] else 0;recall=c["tp"]/c["true"] if c["true"] else 0
        component_rows.append({"system":B2,"instrument_level":k[0],"stratum":k[1],"rows":n,"exact_true_host_rate":c["host"]/n,"exact_left_edge_rate":c["left"]/n,"exact_right_edge_rate":c["right"]/n,"exact_edge_span_decomposition_rate":c["span"]/n,"exact_component_boundary_set_rate":c["be"]/n,"component_boundary_precision":precision,"component_boundary_recall":recall,"component_boundary_f1":2*precision*recall/(precision+recall) if precision+recall else 0})
    for stratum in ("ALL_ROWS","FREQUENT_LEXICAL_ID","LITERAL_ESCAPE","FREQUENT_COMPILER_MARKED"):
        n=len([x for x in oracle if stratum=="ALL_ROWS" or x["lexical_status"]==stratum or (stratum=="FREQUENT_COMPILER_MARKED" and x["lexical_status"]=="FREQUENT_LEXICAL_ID" and any(x[k] for k in ("true_record_operator","true_line_frame","true_lexical_left","true_lexical_right","true_field_marker","true_b2_lexical_closure","true_positional_right","true_closure")))])
        component_rows.append({"system":B2,"instrument_level":"ORACLE_CEILING","stratum":stratum,"rows":n,"exact_true_host_rate":1.,"exact_left_edge_rate":1.,"exact_right_edge_rate":1.,"exact_edge_span_decomposition_rate":1.,"exact_component_boundary_set_rate":1.,"component_boundary_precision":1.,"component_boundary_recall":1.,"component_boundary_f1":1.})
    oldlevels=read(OLD_LEVELS);oldcomponents=read(OLD_COMPONENTS)
    recovery_comparison=[]
    for row in oldlevels+level_rows:
        if row["stratum"]!="FREQUENT_LEXICAL_ID":continue
        recovery_comparison.append({"system":LABEL[row["system"]],"instrument_level":row["instrument_level"],"rows":row["rows"],"host_information_fraction":row["host_information_fraction"],"host_decoder_accuracy":row["host_decoder_accuracy"],"host_decoder_coverage":row["host_decoder_coverage"],"full_decoder_accuracy":row["full_decoder_accuracy"],"full_decoder_coverage":row["full_decoder_coverage"],"raw_decoder_accuracy":row["raw_decoder_accuracy"],"raw_decoder_coverage":row["raw_decoder_coverage"]})
    for row in oldcomponents+component_rows:
        if row["stratum"] not in {"FREQUENT_LEXICAL_ID","FREQUENT_COMPILER_MARKED"}:continue
        recovery_comparison.append({"system":LABEL[row["system"]],"instrument_level":row["instrument_level"],"rows":row["rows"],"component_stratum":row["stratum"],"exact_true_host_rate":row["exact_true_host_rate"],"exact_left_edge_rate":row["exact_left_edge_rate"],"exact_right_edge_rate":row["exact_right_edge_rate"],"exact_edge_span_decomposition_rate":row["exact_edge_span_decomposition_rate"],"exact_component_boundary_set_rate":row["exact_component_boundary_set_rate"],"component_boundary_precision":row["component_boundary_precision"],"component_boundary_recall":row["component_boundary_recall"]})

    olddiag,newdiag=read(OLD_DIAG),read(DIAG);oldops,newops=read(OLD_OPS),read(OPS);fingerprint=[]
    for system,world,diagrows,oprows in ((A,"CONTROL_P",olddiag,oldops),(B,"CONTROL_Q",olddiag,oldops),(B2,"CONTROL_R",newdiag,newops)):
        for mode in ("SURFACE_ONLY","VMANUS_ANNOTATION_ASSISTED"):
            rows=[x for x in diagrows if x["world_view"]==world and x["parser_level"]==mode];allrows=[x for x in rows if x["scope"]=="ALL_PARTITIONED_REGISTERS"];by=defaultdict(list)
            for x in allrows:by[x["diagnostic"]].append(x)
            rec=by["RECORD_ARCHITECTURE"][0];comp=by["OPERATION_COMPATIBILITY"][0];short=by["SHORT_HOST_STRUCTURE"][0];same=by["SAME_GROUP_SUBSTITUTION"][0];external=by["EXTERNAL_CONTEXT_SUBSTITUTION"][0];nxt=next(x for x in by["HELD_CONTEXT"] if x["endpoint"]=="NEXT_HOST");line=next(x for x in by["HELD_CONTEXT"] if x["endpoint"]=="WHOLE_LINE");align=[float(x["greedy_matched_mean_cosine"]) for x in rows if x["diagnostic"]=="REGISTER_GEOMETRY_ALIGNMENT"]
            fingerprint.append({"system":LABEL[system],"instrument_level":mode,"selected_left_operations":sum(x["world_view"]==world and x["side"]=="LEFT" for x in oprows),"selected_right_operations":sum(x["world_view"]==world and x["side"]=="RIGHT" for x in oprows),"compatibility_density":comp["compatible_pair_density"],"compatibility_inclusive_p":comp["inclusive_p"],"next_host_gain_bits":nxt["gain_bits"],"next_host_positive_folios":nxt["positive_content_folios"],"whole_line_gain_bits":line["gain_bits"],"whole_line_positive_folios":line["positive_content_folios"],"right_marked_record_end_precision":rec["right_marked_record_end_precision"],"record_end_right_mark_recall":rec["record_end_right_mark_recall"],"short_host_mass":short["short_host_mass"],"same_group_substitution_cosine":same["mean_delta_cosine"],"external_substitution_cosine":external["mean_delta_cosine"],"register_alignment_mean":sum(align)/len(align)})
    counters=[{"counterexample":"HUMAN_GROWN_DISTRIBUTION_IMPLIES_DENSE_COMPATIBILITY","evidence":"B2 compatibility is high-null despite distributed lexical information.","impact":"Dense factorial-B compatibility is caused by its factorial table, not distributed coding in general."},{"counterexample":"FULL_LOOKUP_REVERSIBILITY_IMPLIES_BLIND_COMPONENT_RECOVERY","evidence":"The oracle tuple is injective but the blind parser need not recover its divisions.","impact":"Reversibility and surface identifiability are separate."},{"counterexample":"B2_IS_A_HISTORICAL_RECONSTRUCTION","evidence":"The table is hand-authored synthetic architecture over frozen lexical IDs.","impact":"Use only as an instrument control."},{"counterexample":"B2_SCORES_VOYNICH","evidence":"No Voynich or f84 input exists.","impact":"No Voynich inference follows."}]
    write(LEVELS,level_rows);write(COMPONENTS,component_rows);write(RECOVERY_COMPARISON,recovery_comparison);write(FINGERPRINT,fingerprint);write(COUNTER,counters)
    bs=lidx["SURFACE_ONLY","FREQUENT_LEXICAL_ID"];bv=lidx["VMANUS_ANNOTATION_ASSISTED","FREQUENT_LEXICAL_ID"];bcs=next(x for x in component_rows if x["instrument_level"]=="SURFACE_ONLY" and x["stratum"]=="FREQUENT_LEXICAL_ID");bcv=next(x for x in component_rows if x["instrument_level"]=="VMANUS_ANNOTATION_ASSISTED" and x["stratum"]=="FREQUENT_LEXICAL_ID");fps={x["system"]+"|"+x["instrument_level"]:x for x in fingerprint};b2s=fps["HUMAN_GROWN_B2|SURFACE_ONLY"];b2v=fps["HUMAN_GROWN_B2|VMANUS_ANNOTATION_ASSISTED"]
    old_component_index={(LABEL[x["system"]],x["instrument_level"],x["stratum"]):x for x in oldcomponents}
    acs=old_component_index["LEXICAL_A","SURFACE_ONLY","FREQUENT_LEXICAL_ID"]
    fbs=old_component_index["FACTORIAL_B","SURFACE_ONLY","FREQUENT_LEXICAL_ID"]
    status="B2_DISTRIBUTED_IDENTITY_PARTIALLY_RECOVERED_WITHOUT_FACTORIAL_COMPATIBILITY"
    report=f"""# GDT173 — B2 human-grown distributed control report

Status: **{status}**.

B2 alone was added. GDT172 lexical A and factorial B were not regenerated or
modified. B2 uses an explicit irregular 384-row reversible lookup with 32
unequal families, optional fields, 11 exceptions and six listed S2 family
variants on the exact GDT172 source/layout schedule.

## Recovery

| level | host information | held host accuracy / coverage | held full accuracy / coverage | exact true host |
|---|---:|---:|---:|---:|
| surface | {bs['host_information_fraction']:.3f} | {bs['host_decoder_accuracy']:.3f} / {bs['host_decoder_coverage']:.3f} | {bs['full_decoder_accuracy']:.3f} / {bs['full_decoder_coverage']:.3f} | {bcs['exact_true_host_rate']:.3f} |
| annotation | {bv['host_information_fraction']:.3f} | {bv['host_decoder_accuracy']:.3f} / {bv['host_decoder_coverage']:.3f} | {bv['full_decoder_accuracy']:.3f} / {bv['full_decoder_coverage']:.3f} | {bcv['exact_true_host_rate']:.3f} |

The sealed oracle is exactly reversible, but blind recovery is partial. Exact
component recovery on frequent lexical-ID rows is:

| system (surface) | exact host | exact left | exact right | exact boundary set |
|---|---:|---:|---:|---:|
| lexical A | {float(acs['exact_true_host_rate']):.3f} | {float(acs['exact_left_edge_rate']):.3f} | {float(acs['exact_right_edge_rate']):.3f} | {float(acs['exact_component_boundary_set_rate']):.3f} |
| factorial B | {float(fbs['exact_true_host_rate']):.3f} | {float(fbs['exact_left_edge_rate']):.3f} | {float(fbs['exact_right_edge_rate']):.3f} | {float(fbs['exact_component_boundary_set_rate']):.3f} |
| human-grown B2 | {bcs['exact_true_host_rate']:.3f} | {bcs['exact_left_edge_rate']:.3f} | {bcs['exact_right_edge_rate']:.3f} | {bcs['exact_component_boundary_set_rate']:.3f} |

Annotation-assisted B2 exact host/left/right/boundary-set recovery is
{bcv['exact_true_host_rate']:.3f} / {bcv['exact_left_edge_rate']:.3f} /
{bcv['exact_right_edge_rate']:.3f} / {bcv['exact_component_boundary_set_rate']:.3f}.
Full span and boundary precision/recall are retained in
`gdt173_component_recovery.tsv`; the complete A/B/B2 comparison is in
`gdt173_three_system_recovery.tsv`.

## Diagnostic fingerprint

| system (surface) | compatibility / p | NEXT gain | WHOLE_LINE gain | record-end precision |
|---|---:|---:|---:|---:|
| lexical A | {float(fps['LEXICAL_A|SURFACE_ONLY']['compatibility_density']):.3f} / {float(fps['LEXICAL_A|SURFACE_ONLY']['compatibility_inclusive_p']):.4f} | {float(fps['LEXICAL_A|SURFACE_ONLY']['next_host_gain_bits']):.0f} | {float(fps['LEXICAL_A|SURFACE_ONLY']['whole_line_gain_bits']):.0f} | {float(fps['LEXICAL_A|SURFACE_ONLY']['right_marked_record_end_precision']):.3f} |
| factorial B | {float(fps['FACTORIAL_B|SURFACE_ONLY']['compatibility_density']):.3f} / {float(fps['FACTORIAL_B|SURFACE_ONLY']['compatibility_inclusive_p']):.4f} | {float(fps['FACTORIAL_B|SURFACE_ONLY']['next_host_gain_bits']):.0f} | {float(fps['FACTORIAL_B|SURFACE_ONLY']['whole_line_gain_bits']):.0f} | {float(fps['FACTORIAL_B|SURFACE_ONLY']['right_marked_record_end_precision']):.3f} |
| human-grown B2 | {float(b2s['compatibility_density']):.3f} / {float(b2s['compatibility_inclusive_p']):.4f} | {float(b2s['next_host_gain_bits']):.0f} | {float(b2s['whole_line_gain_bits']):.0f} | {float(b2s['right_marked_record_end_precision']):.3f} |

B2 does **not** reproduce factorial B's dense, low-null compatibility graph.
It retains strong positive surface NEXT_HOST and positive surface WHOLE_LINE
context, while annotation assistance keeps NEXT_HOST positive but turns
WHOLE_LINE slightly negative ({float(b2v['whole_line_gain_bits']):.1f} bits).
The complete two-level fingerprint, including substitution, short-host and
register-alignment diagnostics, is in `gdt173_three_system_fingerprint.tsv`.

## Consequence

Distribution of identity across several explicit fields is insufficient by
itself to create factorial-B compatibility. The unchanged instrument recovers
some B2 identity and context, but not its full component architecture. B2 is a
synthetic human-grown control, not a historical reconstruction or Voynich
model. No Voynich source or image was scored and no f84 material was accessed.
""";REPORT.write_text(report)
    result={"schema":"GDT173_B2_CALIBRATION_RESULT_V1","status":status,"decision":"RETAIN_B2_AS_HUMAN_GROWN_DISTRIBUTED_INSTRUMENT_CONTROL","headline":{"surface_frequent":bs,"annotation_frequent":bv,"surface_component":bcs,"annotation_component":bcv,"surface_fingerprint":b2s,"annotation_fingerprint":b2v},"inputs":{p.name:sha(p) for p in (OBS,ORACLE,FREEZE,DESIGN,PARSES,BLIND,BLIND_VALID,DIAG,OPS,OLD_LEVELS,OLD_COMPONENTS,OLD_DIAG,OLD_OPS,OLD_RESULT)},"outputs":{p.name:sha(p) for p in (LEVELS,COMPONENTS,RECOVERY_COMPARISON,FINGERPRINT,COUNTER)},"documents":{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)},"implementation":{Path(__file__).name:sha(Path(__file__))},"commitments":{"levels":csha(level_rows),"components":csha(component_rows),"recovery_comparison":csha(recovery_comparison),"fingerprint":csha(fingerprint)},"chronology":{"b2_source_and_design_commit":"f11d14b","blind_outputs_commit":"63b778a","oracle_opened_only_after_blind_outputs_published":True},"system_a_frozen_unchanged":True,"factorial_b_frozen_unchanged":True,"no_voynich_tuning":True,"voynich_inputs":0,"f84_access":False,"claim_ceiling":"Synthetic B2 instrument calibration only; no Voynich architecture word code value language role meaning plaintext or translation."};result["result_content_sha256"]=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":status,"host_accuracy":bs["host_decoder_accuracy"],"host_coverage":bs["host_decoder_coverage"],"exact_host":bcs["exact_true_host_rate"],"compatibility":b2s["compatibility_density"],"compatibility_p":b2s["compatibility_inclusive_p"]},sort_keys=True))
if __name__=="__main__":main()

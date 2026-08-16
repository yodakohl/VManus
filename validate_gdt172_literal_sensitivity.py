#!/usr/bin/env python3
"""Independent recovery/delta validator for GDT172."""
from __future__ import annotations
import csv, gzip, hashlib, json, math
from collections import Counter, defaultdict
from pathlib import Path

R = Path(__file__).resolve().parent
OBS = R / "gdt172_observation_corpus.json.gz"; ORACLE = R / "gdt172_sealed_oracle.json.gz"
OLD_OBS = R / "gdt171_observation_corpus.json.gz"; PARSES = R / "gdt172_blind_parses.json.gz"
LEVELS = R / "gdt172_recovery_levels.tsv"; COMPONENTS = R / "gdt172_component_recovery.tsv"
CAL = R / "gdt172_diagnostic_calibration.tsv"; DELTAS = R / "gdt172_gdt171_delta.tsv"; COUNTER = R / "gdt172_counterexamples.tsv"
OLD_LEVELS = R / "gdt171_recovery_levels.tsv"; OLD_COMPONENTS = R / "gdt171_component_recovery.tsv"
OLD_OPS = R / "gdt171_blind_operations.tsv"; OPS = R / "gdt172_blind_operations.tsv"
REPORT = R / "GDT172_LITERAL_ESCAPE_CORRECTION_REPORT.md"; RESULT = R / "gdt172_result.json"
PRODUCER = R / "unblind_gdt172_literal_sensitivity.py"; OUT = R / "gdt172_validation.json"
A = "SYSTEM_A_V3_UNCHANGED_LITERAL"; B = "SYSTEM_B_FACTORIAL_DISTRIBUTED_CONTROL_V3"
OLD_SYSTEM = {A: "SYSTEM_A_V2", B: "SYSTEM_B_V2"}

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(x): return hashlib.sha256(json.dumps(x, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()
def load(p):
    with gzip.open(p, "rt", encoding="utf8") as h: return json.load(h)["rows"]
def read(p):
    with p.open(encoding="utf8", newline="") as h: return list(csv.DictReader(h, delimiter="\t"))
def check(v, label, checks):
    if not v: raise AssertionError(label)
    checks.append(label)
def entropy(c):
    n=sum(c.values()); return -sum(v/n*math.log2(v/n) for v in c.values() if v) if n else 0
def information(rows, target, key):
    h=entropy(Counter(target(x) for x in rows)); g=defaultdict(Counter)
    for x in rows: g[key(x)][target(x)]+=1
    cond=sum(sum(c.values())/len(rows)*entropy(c) for c in g.values())
    return (h-cond)/h if h else 0
def held(rows, target, key):
    covered=correct=total=0
    for fold in sorted({x["source_unit_full"] for x in rows}):
        maps=defaultdict(Counter)
        for x in rows:
            if x["source_unit_full"]!=fold: maps[key(x)][target(x)]+=1
        for x in rows:
            if x["source_unit_full"]!=fold: continue
            total+=1; k=key(x)
            if k in maps:
                covered+=1; pred=sorted(maps[k].items(),key=lambda z:(-z[1],str(z[0])))[0][0]; correct+=pred==target(x)
    return covered,correct,covered/total,correct/covered if covered else 0

def main():
    checks=[]; result=json.loads(RESULT.read_text())
    obs,old_obs,oracle,parses=load(OBS),load(OLD_OBS),load(ORACLE),load(PARSES)
    levels,components,cal,deltas,counters=read(LEVELS),read(COMPONENTS),read(CAL),read(DELTAS),read(COUNTER)
    check(result["status"]=="FREQUENT_ID_RECOVERY_STABLE_GLOBAL_DIAGNOSTICS_LITERAL_SENSITIVE", "status", checks)
    check(result["decision"]=="USE_UNCHANGED_GRAPHEMATIC_LITERAL_CONDITION_FOR_PRIMARY_HISTORICAL_PLAUSIBILITY_SENSITIVITY", "decision", checks)
    check(len(obs)==len(old_obs)==len(oracle)==30428 and len(parses)==60856, "input_counts", checks)
    check(len(levels)==18 and len(components)==24 and len(cal)==28 and len(counters)==4 and len(deltas)==194, "output_counts", checks)
    omap={x["observation_id"]:x for x in oracle}; pmap={(x["observation_id"],x["parser_level"]):x for x in parses}
    oldmap={x["observation_id"]:x for x in old_obs}
    check(len(omap)==30428 and len(pmap)==60856 and set(omap)==set(oldmap), "join_keys", checks)
    frequent=literal=0
    joined=defaultdict(list); accum=defaultdict(Counter); totals=Counter()
    for row in obs:
        truth=omap[row["observation_id"]]; system=truth["system"]
        prefix=truth["true_record_operator"]+truth["true_line_frame"]+truth["true_literal_escape"]+truth["true_lexical_left"]
        suffix=truth["true_lexical_right"]+truth["true_field_marker"]+truth["true_positional_right"]+truth["true_closure"]
        check(row["surface_group"]==prefix+truth["rendered_host"]+suffix,"surface_reconstruction",checks)
        if truth["lexical_status"]=="FREQUENT_LEXICAL_ID": frequent+=1; check(row["surface_group"]==oldmap[row["observation_id"]]["surface_group"],"frequent_surface_unchanged",checks)
        else: literal+=1; check(truth["canonical_host"]==truth["rendered_host"]==truth["source_form"] and truth["true_literal_escape"]=="w","literal_form_exact",checks)
        for mode in ("SURFACE_ONLY","VMANUS_ANNOTATION_ASSISTED"):
            p=pmap[row["observation_id"],mode]; item={**row,**truth,**p}; joined[system,mode].append(item)
            left=("" if p["outer_left"]=="NONE" else p["outer_left"])+("" if p["local_left"]=="NONE" else p["local_left"])
            right=("" if p["right_inner"]=="NONE" else p["right_inner"])+("" if p["right_outer"]=="NONE" else p["right_outer"])
            true_parts=[z for z in (truth["true_record_operator"],truth["true_line_frame"],truth["true_literal_escape"],truth["true_lexical_left"],truth["rendered_host"],truth["true_lexical_right"],truth["true_field_marker"],truth["true_positional_right"],truth["true_closure"]) if z]
            pred_parts=[z for z in (("" if p["outer_left"]=="NONE" else p["outer_left"]),("" if p["local_left"]=="NONE" else p["local_left"]),p["inferred_host"],("" if p["right_inner"]=="NONE" else p["right_inner"]),("" if p["right_outer"]=="NONE" else p["right_outer"])) if z]
            tb=set();pb=set();cur=0
            for z in true_parts[:-1]:cur+=len(z);tb.add(cur)
            cur=0
            for z in pred_parts[:-1]:cur+=len(z);pb.add(cur)
            strata=["ALL_ROWS",truth["lexical_status"]]
            if truth["lexical_status"]=="FREQUENT_LEXICAL_ID" and (prefix or suffix):strata.append("FREQUENT_COMPILER_MARKED")
            for s in strata:
                k=system,mode,s;totals[k]+=1;accum[k]["host"]+=p["inferred_host"]==truth["rendered_host"];accum[k]["left"]+=left==prefix;accum[k]["right"]+=right==suffix;accum[k]["span"]+=p["inferred_host"]==truth["rendered_host"] and left==prefix and right==suffix;accum[k]["be"]+=tb==pb;accum[k]["tp"]+=len(tb&pb);accum[k]["pred"]+=len(pb);accum[k]["true"]+=len(tb)
    checks=list(dict.fromkeys(checks)); check((frequent,literal)==(11422,19006),"lexical_literal_counts",checks)
    lmap={(x["system"],x["instrument_level"],x["stratum"]):x for x in levels}; cmap={(x["system"],x["instrument_level"],x["stratum"]):x for x in components}
    target=lambda x:x["lexical_id"] if x["lexical_status"]=="FREQUENT_LEXICAL_ID" else x["source_type_hash"]
    for system in (A,B):
        for mode in ("SURFACE_ONLY","VMANUS_ANNOTATION_ASSISTED"):
            rows=[x for x in joined[system,mode] if x["lexical_status"]=="FREQUENT_LEXICAL_ID"]
            row=lmap[system,mode,"FREQUENT_LEXICAL_ID"]; host_key=lambda z:z["inferred_host"]
            full_key=lambda z:(z["outer_left"],z["local_left"],z["inferred_host"],z["right_inner"],z["right_outer"],int(z["group_index"]),int(z["line_ordinal_on_folio"]),int(z["paragraph_start"]),int(z["paragraph_end"]))
            hc,hh,hcov,hacc=held(rows,target,host_key);fc,fh,fcov,facc=held(rows,target,full_key)
            check(abs(information(rows,target,host_key)-float(row["host_information_fraction"]))<1e-12,"frequent_information",checks)
            check((hc,hh)==(int(row["host_decoder_predictions"]),round(int(row["host_decoder_predictions"])*float(row["host_decoder_accuracy"]))),"frequent_held_counts",checks)
            check(abs(hcov-float(row["host_decoder_coverage"]))<1e-12 and abs(hacc-float(row["host_decoder_accuracy"]))<1e-12 and abs(fcov-float(row["full_decoder_coverage"]))<1e-12 and abs(facc-float(row["full_decoder_accuracy"]))<1e-12,"frequent_held_rates",checks)
    checks=list(dict.fromkeys(checks))
    for k,n in totals.items():
        row,a=cmap[k],accum[k];precision=a["tp"]/a["pred"] if a["pred"] else 0;recall=a["tp"]/a["true"] if a["true"] else 0
        check(abs(float(row["exact_true_host_rate"])-a["host"]/n)<1e-12 and abs(float(row["exact_component_boundary_set_rate"])-a["be"]/n)<1e-12,"component_rates",checks)
        check(abs(float(row["component_boundary_precision"])-precision)<1e-12 and abs(float(row["component_boundary_recall"])-recall)<1e-12,"component_pr",checks)
    checks=list(dict.fromkeys(checks))
    old_l={(x["system"],x["instrument_level"],x["stratum"]):x for x in read(OLD_LEVELS)}; old_c={(x["system"],x["instrument_level"],x["stratum"]):x for x in read(OLD_COMPONENTS)}
    frequent_delta=[x for x in deltas if x["scope"].startswith("FREQUENT_ID")]
    check(len(frequent_delta)==150 and all(x["material"]=="0" and abs(float(x["delta"]))<.05 for x in frequent_delta),"frequent_deltas_nonmaterial",checks)
    for x in frequent_delta:
        newmap,oldmap2=(lmap,old_l) if x["scope"]=="FREQUENT_ID_RECOVERY" else (cmap,old_c)
        newrow=newmap[x["system"],x["instrument_level"],x["stratum"]]
        oldrow=oldmap2[OLD_SYSTEM[x["system"]],x["instrument_level"],x["stratum"]]
        ov,nv=float(oldrow[x["metric"]]),float(newrow[x["metric"]])
        check(abs(ov-float(x["gdt171_value"]))<1e-12 and abs(nv-float(x["gdt172_value"]))<1e-12 and abs((nv-ov)-float(x["delta"]))<1e-12,"delta_values_exact",checks)
    checks=list(dict.fromkeys(checks))
    oldops,newops=read(OLD_OPS),read(OPS); opdelta=[x for x in deltas if x["scope"]=="GLOBAL_OPERATION_LIBRARY"]
    check(len(oldops)==35 and len(newops)==43 and len(opdelta)==4,"operation_counts",checks)
    for x in opdelta:
        a={r["operation"] for r in oldops if r["world_view"]==x["system"] and r["side"]==x["instrument_level"]};b={r["operation"] for r in newops if r["world_view"]==x["system"] and r["side"]==x["instrument_level"]};j=len(a&b)/len(a|b)
        check(abs(j-float(x["jaccard"]))<1e-12 and int(x["material"])==(j<.8),"operation_jaccard",checks)
    check(sum(int(x["material"]) for x in deltas if x["scope"].startswith("GLOBAL"))==12,"global_material_count",checks)
    check(all(sha(R/k)==v for k,v in result["inputs"].items()) and all(sha(R/k)==v for k,v in result["outputs"].items()),"artifact_hashes",checks)
    check(sha(REPORT)==result["documents"][REPORT.name] and sha(PRODUCER)==result["implementation"][PRODUCER.name],"doc_impl_hashes",checks)
    stored=result.pop("result_content_sha256");check(csha(result)==stored,"result_content_hash",checks)
    check(result["chronology"]=={"source_and_design_commit":"f374df8","blind_outputs_commit":"a9d472b","oracle_opened_only_after_blind_outputs_published":True},"chronology",checks)
    check(result["system_b_architecture"]=="EXPLICIT_FACTORIAL_DISTRIBUTED_CONTROL_NOT_HISTORICAL_NATURALISTIC" and result["b2_status"]=="NOT_BUILT_DEFERRED","system_b_label",checks)
    check(result["voynich_inputs"]==0 and not result["f84_access"] and result["no_voynich_tuning"],"no_voynich_f84",checks)
    out={"schema":"GDT172_LITERAL_SENSITIVITY_VALIDATION_V1","status":"PASS_INDEPENDENT_FREQUENT_AND_GLOBAL_DELTA_RECONSTRUCTION","checks_passed":len(checks),"checks_failed":0,"checks":checks,"frequent_rows":frequent,"literal_rows":literal,"delta_rows":len(deltas),"result_sha256":sha(RESULT),"validator_sha256":sha(Path(__file__)),"voynich_inputs":0,"f84_access":False}
    out["validation_content_sha256"]=csha(out);OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(f"PASS {len(checks)}/{len(checks)}")

if __name__=="__main__":main()

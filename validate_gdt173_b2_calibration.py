#!/usr/bin/env python3
"""Independent recovery and three-system fingerprint validator for GDT173."""
from __future__ import annotations
import csv,gzip,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent
OBS=R/"gdt173_b2_observation_corpus.json.gz";ORACLE=R/"gdt173_b2_sealed_oracle.json.gz";PARSES=R/"gdt173_blind_parses.json.gz";LEVELS=R/"gdt173_recovery_levels.tsv";COMPONENTS=R/"gdt173_component_recovery.tsv";RECOVERY=R/"gdt173_three_system_recovery.tsv";FINGERPRINT=R/"gdt173_three_system_fingerprint.tsv";COUNTER=R/"gdt173_counterexamples.tsv";OLD_LEVELS=R/"gdt172_recovery_levels.tsv";OLD_COMPONENTS=R/"gdt172_component_recovery.tsv";OLD_DIAG=R/"gdt172_blind_diagnostics.tsv";OLD_OPS=R/"gdt172_blind_operations.tsv";DIAG=R/"gdt173_blind_diagnostics.tsv";OPS=R/"gdt173_blind_operations.tsv";REPORT=R/"GDT173_HUMAN_GROWN_DISTRIBUTED_CONTROL_REPORT.md";RESULT=R/"gdt173_result.json";PRODUCER=R/"unblind_gdt173_b2_calibration.py";OUT=R/"gdt173_validation.json"
B2="SYSTEM_B2_HUMAN_GROWN_DISTRIBUTED_CONTROL"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def load(p):
    with gzip.open(p,"rt",encoding="utf8") as h:return json.load(h)["rows"]
def read(p):
    with p.open(encoding="utf8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def check(v,label,checks):
    if not v:raise AssertionError(label)
    checks.append(label)
def entropy(c):
    n=sum(c.values());return -sum(v/n*math.log2(v/n) for v in c.values() if v) if n else 0
def information(rows,target,key):
    h=entropy(Counter(target(x) for x in rows));g=defaultdict(Counter)
    for x in rows:g[key(x)][target(x)]+=1
    cond=sum(sum(c.values())/len(rows)*entropy(c) for c in g.values());return (h-cond)/h if h else 0
def held(rows,target,key):
    covered=correct=total=0
    for fold in sorted({x["source_unit_full"] for x in rows}):
        maps=defaultdict(Counter)
        for x in rows:
            if x["source_unit_full"]!=fold:maps[key(x)][target(x)]+=1
        for x in rows:
            if x["source_unit_full"]!=fold:continue
            total+=1;k=key(x)
            if k in maps:covered+=1;pred=sorted(maps[k].items(),key=lambda z:(-z[1],str(z[0])))[0][0];correct+=pred==target(x)
    return covered,correct,covered/total,correct/covered if covered else 0

def main():
    checks=[];result=json.loads(RESULT.read_text());obs,oracle,parses=load(OBS),load(ORACLE),load(PARSES);levels,components,recovery,fingerprint,counters=read(LEVELS),read(COMPONENTS),read(RECOVERY),read(FINGERPRINT),read(COUNTER)
    check(result["status"]=="B2_DISTRIBUTED_IDENTITY_PARTIALLY_RECOVERED_WITHOUT_FACTORIAL_COMPATIBILITY","status",checks);check(result["decision"]=="RETAIN_B2_AS_HUMAN_GROWN_DISTRIBUTED_INSTRUMENT_CONTROL","decision",checks);check(len(obs)==len(oracle)==15214 and len(parses)==30428,"input_counts",checks);check(len(levels)==9 and len(components)==12 and len(recovery)==27 and len(fingerprint)==6 and len(counters)==4,"output_counts",checks)
    omap={x["observation_id"]:x for x in oracle};pmap={(x["observation_id"],x["parser_level"]):x for x in parses};check(len(omap)==15214 and len(pmap)==30428 and {x["system"] for x in oracle}=={B2},"joins_system",checks)
    joined=defaultdict(list);acc=defaultdict(Counter);totals=Counter()
    for row in obs:
        truth=omap[row["observation_id"]];prefix=truth["true_record_operator"]+truth["true_line_frame"]+truth["true_literal_escape"]+truth["true_lexical_left"];suffix=truth["true_lexical_right"]+truth["true_field_marker"]+truth["true_b2_lexical_closure"]+truth["true_positional_right"]+truth["true_closure"];check(row["surface_group"]==prefix+truth["rendered_host"]+suffix,"surface_reconstructs",checks)
        for mode in ("SURFACE_ONLY","VMANUS_ANNOTATION_ASSISTED"):
            p=pmap[row["observation_id"],mode];x={**row,**truth,**p};joined[mode].append(x);left=("" if p["outer_left"]=="NONE" else p["outer_left"])+("" if p["local_left"]=="NONE" else p["local_left"]);right=("" if p["right_inner"]=="NONE" else p["right_inner"])+("" if p["right_outer"]=="NONE" else p["right_outer"])
            tp=[z for z in (truth["true_record_operator"],truth["true_line_frame"],truth["true_literal_escape"],truth["true_lexical_left"],truth["rendered_host"],truth["true_lexical_right"],truth["true_field_marker"],truth["true_b2_lexical_closure"],truth["true_positional_right"],truth["true_closure"]) if z];pp=[z for z in (("" if p["outer_left"]=="NONE" else p["outer_left"]),("" if p["local_left"]=="NONE" else p["local_left"]),p["inferred_host"],("" if p["right_inner"]=="NONE" else p["right_inner"]),("" if p["right_outer"]=="NONE" else p["right_outer"])) if z];tb=set();pb=set();cur=0
            for z in tp[:-1]:cur+=len(z);tb.add(cur)
            cur=0
            for z in pp[:-1]:cur+=len(z);pb.add(cur)
            strata=["ALL_ROWS",truth["lexical_status"]]
            if truth["lexical_status"]=="FREQUENT_LEXICAL_ID" and (prefix or suffix):strata.append("FREQUENT_COMPILER_MARKED")
            for s in strata:
                k=mode,s;totals[k]+=1;acc[k]["host"]+=p["inferred_host"]==truth["rendered_host"];acc[k]["left"]+=left==prefix;acc[k]["right"]+=right==suffix;acc[k]["span"]+=p["inferred_host"]==truth["rendered_host"] and left==prefix and right==suffix;acc[k]["be"]+=tb==pb;acc[k]["tp"]+=len(tb&pb);acc[k]["pred"]+=len(pb);acc[k]["true"]+=len(tb)
    checks=list(dict.fromkeys(checks));lmap={(x["instrument_level"],x["stratum"]):x for x in levels};cmap={(x["instrument_level"],x["stratum"]):x for x in components};target=lambda x:x["lexical_id"] if x["lexical_status"]=="FREQUENT_LEXICAL_ID" else x["source_type_hash"]
    for mode in ("SURFACE_ONLY","VMANUS_ANNOTATION_ASSISTED"):
        rows=[x for x in joined[mode] if x["lexical_status"]=="FREQUENT_LEXICAL_ID"];row=lmap[mode,"FREQUENT_LEXICAL_ID"];hk=lambda z:z["inferred_host"];fk=lambda z:(z["outer_left"],z["local_left"],z["inferred_host"],z["right_inner"],z["right_outer"],int(z["group_index"]),int(z["line_ordinal_on_folio"]),int(z["paragraph_start"]),int(z["paragraph_end"]));hc,hh,hcov,hacc=held(rows,target,hk);fc,fh,fcov,facc=held(rows,target,fk)
        check(abs(information(rows,target,hk)-float(row["host_information_fraction"]))<1e-12,"host_information",checks);check((hc,hh)==(int(row["host_decoder_predictions"]),round(int(row["host_decoder_predictions"])*float(row["host_decoder_accuracy"]))),"held_counts",checks);check(abs(hcov-float(row["host_decoder_coverage"]))<1e-12 and abs(hacc-float(row["host_decoder_accuracy"]))<1e-12 and abs(fcov-float(row["full_decoder_coverage"]))<1e-12 and abs(facc-float(row["full_decoder_accuracy"]))<1e-12,"held_rates",checks)
    checks=list(dict.fromkeys(checks))
    for k,n in totals.items():
        row,a=cmap[k],acc[k];precision=a["tp"]/a["pred"] if a["pred"] else 0;recall=a["tp"]/a["true"] if a["true"] else 0
        check(abs(float(row["exact_true_host_rate"])-a["host"]/n)<1e-12 and abs(float(row["exact_left_edge_rate"])-a["left"]/n)<1e-12 and abs(float(row["exact_right_edge_rate"])-a["right"]/n)<1e-12 and abs(float(row["exact_edge_span_decomposition_rate"])-a["span"]/n)<1e-12 and abs(float(row["exact_component_boundary_set_rate"])-a["be"]/n)<1e-12,"component_rates",checks);check(abs(float(row["component_boundary_precision"])-precision)<1e-12 and abs(float(row["component_boundary_recall"])-recall)<1e-12,"component_pr",checks)
    checks=list(dict.fromkeys(checks));oldlevels,oldcomponents=read(OLD_LEVELS),read(OLD_COMPONENTS)
    check(sum(x["component_stratum"]=="NA" for x in recovery)==9 and sum(x["component_stratum"]!="NA" for x in recovery)==18,"comparison_row_kinds",checks)
    old_level_keys={("LEXICAL_A" if x["system"].startswith("SYSTEM_A") else "FACTORIAL_B",x["instrument_level"]):x for x in oldlevels if x["stratum"]=="FREQUENT_LEXICAL_ID"};b2_level={("HUMAN_GROWN_B2",x["instrument_level"]):x for x in levels if x["stratum"]=="FREQUENT_LEXICAL_ID"}
    for x in recovery:
        if x["component_stratum"]!="NA":continue
        src={**old_level_keys,**b2_level}[x["system"],x["instrument_level"]];check(all(abs(float(x[f])-float(src[f]))<1e-12 for f in ("host_information_fraction","host_decoder_accuracy","host_decoder_coverage","full_decoder_accuracy","full_decoder_coverage","raw_decoder_accuracy","raw_decoder_coverage")),"recovery_comparison_exact",checks)
    checks=list(dict.fromkeys(checks));olddiag,newdiag=read(OLD_DIAG),read(DIAG);oldops,newops=read(OLD_OPS),read(OPS)
    source_map={"LEXICAL_A":("CONTROL_P",olddiag,oldops),"FACTORIAL_B":("CONTROL_Q",olddiag,oldops),"HUMAN_GROWN_B2":("CONTROL_R",newdiag,newops)}
    for row in fingerprint:
        world,drows,orows=source_map[row["system"]];mode=row["instrument_level"];sub=[x for x in drows if x["world_view"]==world and x["parser_level"]==mode];by=defaultdict(list)
        for x in sub:
            if x["scope"]=="ALL_PARTITIONED_REGISTERS":by[x["diagnostic"]].append(x)
        comp=by["OPERATION_COMPATIBILITY"][0];rec=by["RECORD_ARCHITECTURE"][0];nxt=next(x for x in by["HELD_CONTEXT"] if x["endpoint"]=="NEXT_HOST");line=next(x for x in by["HELD_CONTEXT"] if x["endpoint"]=="WHOLE_LINE");align=[float(x["greedy_matched_mean_cosine"]) for x in sub if x["diagnostic"]=="REGISTER_GEOMETRY_ALIGNMENT"]
        check(int(row["selected_left_operations"])==sum(x["world_view"]==world and x["side"]=="LEFT" for x in orows) and int(row["selected_right_operations"])==sum(x["world_view"]==world and x["side"]=="RIGHT" for x in orows),"fingerprint_operation_counts",checks);check(abs(float(row["compatibility_density"])-float(comp["compatible_pair_density"]))<1e-12 and abs(float(row["compatibility_inclusive_p"])-float(comp["inclusive_p"]))<1e-12 and abs(float(row["next_host_gain_bits"])-float(nxt["gain_bits"]))<1e-12 and abs(float(row["whole_line_gain_bits"])-float(line["gain_bits"]))<1e-12 and abs(float(row["right_marked_record_end_precision"])-float(rec["right_marked_record_end_precision"]))<1e-12 and abs(float(row["register_alignment_mean"])-sum(align)/len(align))<1e-12,"fingerprint_values",checks)
    checks=list(dict.fromkeys(checks));check(all(sha(R/k)==v for k,v in result["inputs"].items()) and all(sha(R/k)==v for k,v in result["outputs"].items()),"artifact_hashes",checks);check(sha(REPORT)==result["documents"][REPORT.name] and sha(PRODUCER)==result["implementation"][PRODUCER.name],"doc_impl_hashes",checks);stored=result.pop("result_content_sha256");check(csha(result)==stored,"result_content_hash",checks);check(result["chronology"]=={"b2_source_and_design_commit":"f11d14b","blind_outputs_commit":"63b778a","oracle_opened_only_after_blind_outputs_published":True},"chronology",checks);check(result["system_a_frozen_unchanged"] and result["factorial_b_frozen_unchanged"],"parent_systems_frozen",checks);check(result["voynich_inputs"]==0 and not result["f84_access"] and result["no_voynich_tuning"],"no_voynich_f84",checks)
    out={"schema":"GDT173_B2_CALIBRATION_VALIDATION_V1","status":"PASS_INDEPENDENT_B2_RECOVERY_AND_THREE_SYSTEM_FINGERPRINT_RECONSTRUCTION","checks_passed":len(checks),"checks_failed":0,"checks":checks,"observation_rows":len(obs),"parse_rows":len(parses),"fingerprint_rows":len(fingerprint),"result_sha256":sha(RESULT),"validator_sha256":sha(Path(__file__)),"voynich_inputs":0,"f84_access":False};out["validation_content_sha256"]=csha(out);OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(f"PASS {len(checks)}/{len(checks)}")
if __name__=="__main__":main()

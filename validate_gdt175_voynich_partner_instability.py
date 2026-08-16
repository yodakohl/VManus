#!/usr/bin/env python3
"""Independent, non-importing validation of GDT175 Voynich application."""
from __future__ import annotations

import csv
import hashlib
import itertools
import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

R = Path(__file__).resolve().parent
DESIGN = R / "gdt175_design.json"; CONTROL = R / "gdt175_control_result.json"
HPR2 = R / "gdt062_right_family_inventory.tsv"; FRAMES = R / "gdt046_line_frames.tsv"
HOSTS = R / "gdt175_voynich_host_metrics.tsv"; BINS = R / "gdt175_voynich_bin_summary.tsv"; SCOPES = R / "gdt175_voynich_scope_summary.tsv"
SIDE = R / "gdt175_side_by_side.tsv"; COUNTER = R / "gdt175_counterexamples.tsv"; REPORT = R / "GDT175_RECURRENCE_PARTNER_INSTABILITY_REPORT.md"
RESULT = R / "gdt175_result.json"; RUNNER = R / "run_gdt175_voynich_partner_instability.py"; CONTROL_RUNNER = R / "run_gdt175_control_partner_instability.py"; PANEL_RUNNER = R / "run_gdt174_voynich_calibrated_fingerprint.py"
OUT = R / "gdt175_validation.json"; ALPHA, BETA, WORLDS = 16.0, 8.0, 256


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def csha(value): return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()
def read(path):
    with path.open(encoding="utf8", newline="") as handle: return list(csv.DictReader(handle, delimiter="\t"))
def check(value, label, checks):
    if not value: raise AssertionError(label)
    checks.append(label)
def close(a, b, tolerance=1e-9): return abs(float(a)-float(b)) <= tolerance*max(1.0,abs(float(a)),abs(float(b)))
def locus_number(locus):
    match=re.search(r"\.(\d+)$",locus); assert match; return int(match.group(1))


def panel():
    frames={}; rejected_frames=0
    with FRAMES.open(encoding="utf8",newline="") as handle:
        for row in csv.DictReader(handle,delimiter="\t"):
            if row["page"].startswith("f84") or row["locus"].startswith("f84"): rejected_frames+=1; continue
            frames[row["locus"]]=row
    groups=defaultdict(list); rejected_hpr2=0
    with HPR2.open(encoding="utf8",newline="") as handle:
        for row in csv.DictReader(handle,delimiter="\t"):
            if row["page"].startswith("f84") or row["locus"].startswith("f84"): rejected_hpr2+=1; continue
            if row["locus"] in frames: groups[row["locus"]].append(row)
    assert set(groups)==set(frames)
    for locus, values in groups.items():
        assert len(values)==int(values[0]["group_count"])
        assert sorted(int(x["group_index"]) for x in values)==list(range(1,len(values)+1))
    folio_lines=defaultdict(list)
    for locus,row in frames.items(): folio_lines[row["physical_folio"]].append(locus)
    ordinals={}
    for folio, loci in folio_lines.items():
        loci.sort(key=lambda locus:(frames[locus]["page"],locus_number(locus)))
        for index,locus in enumerate(loci): ordinals[locus]=index
    rows=[]
    for locus in sorted(groups,key=lambda value:(frames[value]["page"],locus_number(value))):
        frame=frames[locus]
        for source in sorted(groups[locus],key=lambda value:int(value["group_index"])):
            rows.append({"line_id":locus,"page":source["page"],"locus":locus,"folio":source["physical_folio"],"register":source["register"],"section":source["section"],"host":source["page_host"],"group_index":int(source["group_index"]),"group_count":int(source["group_count"]),"line_ordinal":ordinals[locus]})
    assert not any(row["page"].startswith("f84") or row["locus"].startswith("f84") for row in rows)
    return rows,{"groups":len(rows),"lines":len(groups),"pages":len({row["page"] for row in rows}),"folios":len(folio_lines),"f84_hpr2_rows_rejected":rejected_hpr2,"f84_frame_rows_rejected":rejected_frames}


def make_events(rows):
    lines=defaultdict(list)
    for row in rows: lines[row["line_id"]].append(row)
    out=[]
    for line in lines.values():
        line.sort(key=lambda row:row["group_index"])
        for left,right in zip(line,line[1:]):
            assert right["group_index"]==left["group_index"]+1
            out.append({"folio":left["folio"],"register":left["register"],"section":left["section"],"host":left["host"],"target":right["host"],"nk":(left["group_index"],left["line_ordinal"]%3,left["group_count"])})
    return out


def entropy(counts):
    total=sum(counts.values()); return -sum(n/total*math.log2(n/total) for n in counts.values() if n) if total else 0.0


def pair_values(by_folio):
    support=sorted(set().union(*(set(counter) for counter in by_folio.values()))); values=[]
    for left,right in itertools.combinations(sorted(by_folio),2):
        a,b=by_folio[left],by_folio[right]; overlap=len(set(a)&set(b))/len(set(a)|set(b))
        da,db=sum(a.values())+.5*len(support),sum(b.values())+.5*len(support); divergence=0.0
        for target in support:
            pa,pb=(a.get(target,0)+.5)/da,(b.get(target,0)+.5)/db; middle=(pa+pb)/2
            divergence+=.5*pa*math.log2(pa/middle)+.5*pb*math.log2(pb/middle)
        values.append((overlap,divergence))
    return sum(x for x,_ in values)/len(values),sum(x for _,x in values)/len(values)


def held(values):
    vocab={x["target"] for x in values}; gt=Counter();gn=0;nt=Counter();nn=Counter();ht=Counter();hn=Counter();ft=defaultdict(Counter);fn=Counter();fnt=defaultdict(Counter);fnn=defaultdict(Counter);fht=defaultdict(Counter);fhn=defaultdict(Counter)
    for x in values:
        t,nk,h,f=x["target"],x["nk"],x["host"],x["folio"]
        gt[t]+=1;gn+=1;nt[nk,t]+=1;nn[nk]+=1;ht[h,t]+=1;hn[h]+=1;ft[f][t]+=1;fn[f]+=1;fnt[f][nk,t]+=1;fnn[f][nk]+=1;fht[f][h,t]+=1;fhn[f][h]+=1
    gains=Counter()
    for x in values:
        t,nk,h,f=x["target"],x["nk"],x["host"],x["folio"]
        q=(gt[t]-ft[f][t]+.5)/(gn-fn[f]+.5*len(vocab));base=(nt[nk,t]-fnt[f][nk,t]+ALPHA*q)/(nn[nk]-fnn[f][nk]+ALPHA);hp=(ht[h,t]-fht[f][h,t]+BETA*base)/(hn[h]-fhn[f][h]+BETA);gains[h]+=math.log2(hp/base)
    return gains


def null_values(host,by_folio,observed_overlap,observed_jsd):
    folios=sorted(by_folio);sizes=[sum(by_folio[x].values()) for x in folios];partners=[]
    for folio in folios: partners.extend(by_folio[folio].elements())
    value=int(hashlib.sha256("|".join(("GDT175","VOYNICH","GLOBAL:ALL",host)).encode()).hexdigest()[:16],16);rng=random.Random(value);overlaps=[];divergences=[]
    for _ in range(WORLDS):
        sample=list(partners);rng.shuffle(sample);cursor=0;rebuilt={}
        for folio,size in zip(folios,sizes): rebuilt[folio]=Counter(sample[cursor:cursor+size]);cursor+=size
        overlap,divergence=pair_values(rebuilt);overlaps.append(overlap);divergences.append(divergence)
    return sum(overlaps)/WORLDS,sum(divergences)/WORLDS,(1+sum(x<=observed_overlap+1e-15 for x in overlaps))/257,(1+sum(x>=observed_jsd-1e-15 for x in divergences))/257


def diagnose(global_row,bins,scopes,envelopes):
    bins=[row for row in bins if int(row["powered"])];inside=[];unstable=[]
    for row in bins:
        env=envelopes[row["occurrence_bin"]];inside.append(all(env[key][0]<=float(row[key])<=env[key][1] for key in ("held_bits_per_event","mean_overlap_excess","mean_jsd_excess")));unstable.append(float(row["held_bits_per_event"])<env["held_bits_per_event"][0] and (float(row["mean_overlap_excess"])<env["mean_overlap_excess"][0] or float(row["mean_jsd_excess"])>env["mean_jsd_excess"][1]))
    regs=[row for row in scopes if row["scope_type"]=="REGISTER" and int(row["powered"])];positive=sum(float(row["held_bits_per_event"])>0 for row in regs);negative=sum(float(row["held_bits_per_event"])<0 for row in regs);aggregate=sum(float(row["held_gain_bits"]) for row in regs)
    detail={"powered_bins":len(bins),"bins_inside_all_control_envelopes":sum(inside),"bins_meeting_instability_rule":sum(unstable),"powered_registers":len(regs),"positive_registers":positive,"negative_registers":negative,"aggregate_powered_register_gain_bits":aggregate}
    if len(bins)>=3 and all(inside): return "SAMPLING_FREQUENCY_SUFFICIENT",detail
    if float(global_row["held_gain_bits"])<0 and len(regs)>=3 and positive/len(regs)>=.75 and aggregate>0:return "REGISTER_MIXTURE_DOMINANT",detail
    if float(global_row["held_gain_bits"])<0 and len(bins)>=3 and sum(unstable)/len(bins)>=.75 and len(regs)>=3 and negative/len(regs)>=.75:return "FOLIO_CONDITIONED_INSTABILITY_SUPPORTED",detail
    return "MIXED_OR_UNRESOLVED",detail


def main():
    checks=[];design=json.loads(DESIGN.read_text());control=json.loads(CONTROL.read_text());result=json.loads(RESULT.read_text());host_rows=read(HOSTS);bin_rows=read(BINS);scope_rows=read(SCOPES);side=read(SIDE);counter=read(COUNTER);rows,census=panel();all_events=make_events(rows)
    check(design["status"]=="DIAGNOSTIC_FROZEN_BEFORE_CONTROL_CALIBRATION","design_status",checks);check(control["status"]=="CONTROL_CALIBRATION_FROZEN_BEFORE_VOYNICH_SCORING","control_status",checks);check(result["status"]=="MIXED_OR_UNRESOLVED","result_status",checks)
    check(census["groups"]==8448 and census["lines"]==1143 and census["folios"]==91 and len(all_events)==7305,"source_census",checks);check(result["census"]["f84_hpr2_rows_rejected"]==228 and result["census"]["f84_frame_rows_rejected"]==21 and result["f84_rows_retained"]==0 and not result["f84r_access"],"f84_filter",checks)
    exported={(row["scope_type"],row["scope_value"],row["host"]):row for row in host_rows};reconstructed={};audit=[]
    scopes=[("GLOBAL","ALL",rows,all_events)]
    for register in sorted({row["register"] for row in rows}):scopes.append(("REGISTER",register,[row for row in rows if row["register"]==register],[event for event in all_events if event["register"]==register]))
    for section in sorted({row["section"] for row in rows}):scopes.append(("SECTION",section,[row for row in rows if row["section"]==section],[event for event in all_events if event["section"]==section]))
    for scope_type,scope_value,subrows,subevents in scopes:
        grouped=defaultdict(list)
        for event in subevents:grouped[event["host"]].append(event)
        eligible={host for host,values in grouped.items() if len(values)>=2 and len({x["folio"] for x in values})>=2};gains=held(subevents);reconstructed[scope_type,scope_value]=(len(subrows),len(subevents),len(eligible),sum(len(grouped[h]) for h in eligible))
        for host in eligible:
            row=exported[scope_type,scope_value,host];values=grouped[host];by_folio=defaultdict(Counter);pooled=Counter()
            for x in values:by_folio[x["folio"]][x["target"]]+=1;pooled[x["target"]]+=1
            overlap,divergence=pair_values(by_folio);check(int(row["next_events"])==len(values) and int(row["physical_folios"])==len(by_folio) and int(row["partner_types"])==len(pooled),"host_counts",checks);check(close(row["held_gain_bits"],gains[host]) and close(row["partner_set_overlap"],overlap) and close(row["pairwise_jsd_bits"],divergence),"host_metrics",checks);check(close(row["pooled_target_entropy_bits"],entropy(pooled)) and close(row["mean_within_folio_entropy_bits"],sum(entropy(x) for x in by_folio.values())/len(by_folio)),"host_entropies",checks)
        if scope_type=="GLOBAL":
            for name in ("N2_4","N5_15","N16_63","N64_PLUS"):
                candidates=[h for h in eligible if exported[scope_type,scope_value,h]["occurrence_bin"]==name];chosen=min(candidates,key=lambda h:(len(grouped[h]),h));audit.append((chosen,grouped[chosen]))
    check(len(exported)==len(host_rows),"host_keys",checks)
    for summary in scope_rows:
        expected=reconstructed[summary["scope_type"],summary["scope_value"]];check(tuple(map(int,(summary["total_groups"],summary["total_next_events"],summary["eligible_hosts"],summary["eligible_next_events"])))==expected,"scope_counts",checks)
    for host,values in audit:
        row=exported["GLOBAL","ALL",host];by_folio=defaultdict(Counter)
        for x in values:by_folio[x["folio"]][x["target"]]+=1
        no,nj,po,pj=null_values(host,by_folio,float(row["partner_set_overlap"]),float(row["pairwise_jsd_bits"]));check(close(row["null_overlap_mean"],no) and close(row["null_jsd_mean"],nj) and close(row["overlap_lower_p"],po) and close(row["jsd_upper_p"],pj),"sampled_null_replay",checks)
    for summary in bin_rows+scope_rows:
        selected=[row for row in host_rows if row["scope_type"]==summary["scope_type"] and row["scope_value"]==summary["scope_value"] and (summary["occurrence_bin"]=="ALL_ELIGIBLE" or row["occurrence_bin"]==summary["occurrence_bin"])];gain=sum(float(row["held_gain_bits"]) for row in selected);events=sum(int(row["next_events"]) for row in selected);check(int(summary["eligible_hosts"])==len(selected) and int(summary["eligible_next_events"])==events and close(summary["held_gain_bits"],gain),"summary_arithmetic",checks)
    global_row=next(row for row in scope_rows if row["scope_type"]=="GLOBAL");global_bins=[row for row in bin_rows if row["scope_type"]=="GLOBAL"];status,detail=diagnose(global_row,global_bins,scope_rows,control["control_envelopes"]);check(status==result["status"] and detail==result["decision_details"],"decision_reconstruction",checks)
    check(len(side)==16 and sum(row["system"]=="VOYNICH" for row in side)==4 and len(counter)==4,"output_rows",checks);check(result["chronology"]=={"control_calibration_commit":"6817afd","design_commit":"f6fb14c","voynich_scored_after_both_public_freezes":True},"chronology",checks);check(not result["build_b3"] and result["no_rescaling"] and result["no_tuning_to_voynich"],"no_b3_tuning",checks)
    checks=list(dict.fromkeys(checks));check(all(sha(R/name)==value for name,value in result["inputs"].items()),"input_hashes",checks);check(all(sha(R/name)==value for name,value in result["outputs"].items()),"output_hashes",checks);check(sha(RUNNER)==result["implementation"][RUNNER.name] and sha(CONTROL_RUNNER)==result["implementation"][CONTROL_RUNNER.name] and sha(PANEL_RUNNER)==result["implementation"][PANEL_RUNNER.name],"implementation_hashes",checks);stored=result.pop("result_content_sha256");check(csha(result)==stored,"result_content_hash",checks)
    out={"schema":"GDT175_VOYNICH_PARTNER_INSTABILITY_VALIDATION_V1","status":"PASS_INDEPENDENT_F84_FILTERED_SOURCE_RECONSTRUCTION","checks_passed":len(checks),"checks_failed":0,"checks":checks,"eligible_groups":len(rows),"next_events":len(all_events),"host_metric_rows":len(host_rows),"sampled_null_hosts_replayed":len(audit),"result_sha256":sha(RESULT),"validator_sha256":sha(Path(__file__)),"build_b3":False,"f84_rows_retained":0,"f84r_access":False};out["validation_content_sha256"]=csha(out);OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(f"PASS {len(checks)}/{len(checks)}")


if __name__=="__main__":main()

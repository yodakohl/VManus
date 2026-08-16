#!/usr/bin/env python3
"""Independent no-oracle validator for GDT173 blind B2 outputs."""
from __future__ import annotations
import csv,gzip,hashlib,json
from collections import defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent
OBS=R/"gdt173_b2_observation_corpus.json.gz";PARSES=R/"gdt173_blind_parses.json.gz";OPS=R/"gdt173_blind_operations.tsv";DIAG=R/"gdt173_blind_diagnostics.tsv";DESIGN=R/"gdt173_blind_design.json";RESULT=R/"gdt173_blind_result.json";RUNNER=R/"run_gdt173_blind_instrument.py";CORE=R/"run_gdt170_blind_instrument.py";OUT=R/"gdt173_blind_validation.json"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def load(p):
    with gzip.open(p,"rt",encoding="utf8") as h:return json.load(h)["rows"]
def read(p):
    with p.open(encoding="utf8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def check(v,label,checks):
    if not v:raise AssertionError(label)
    checks.append(label)
def main():
    checks=[];design=json.loads(DESIGN.read_text());result=json.loads(RESULT.read_text());obs,parses,ops,diag=load(OBS),load(PARSES),read(OPS),read(DIAG)
    check(design["status"]=="FROZEN_UNCHANGED_GDT172_INSTRUMENT_BEFORE_B2_BLIND_PARSE","design_status",checks);check(result["status"]=="GDT173_B2_BLIND_OUTPUTS_FROZEN_BEFORE_ORACLE_EVALUATION","result_status",checks)
    check(len(obs)==15214 and len(parses)==30428 and len(diag)==26,"counts",checks);omap={x["observation_id"]:x for x in obs};check(len(omap)==len(obs) and len({(x["observation_id"],x["parser_level"]) for x in parses})==len(parses),"keys",checks)
    selected={"LEFT":set(),"RIGHT":set()}
    for x in ops:selected[x["side"]].add(x["operation"])
    check(len(selected["LEFT"])<=12 and len(selected["RIGHT"])<=12,"operation_caps",checks)
    for p in parses:
        src=omap[p["observation_id"]];check(p["surface_group"]==src["surface_group"] and p["world_view"]=="CONTROL_R","parse_join",checks)
        left=[x for x in (p["outer_left"],p["local_left"]) if x!="NONE"];right=[x for x in (p["right_outer"],p["right_inner"]) if x!="NONE"]
        check("".join(left)+p["inferred_host"]+"".join(reversed(right))==p["surface_group"],"parse_reconstructs",checks);check(all(x in selected["LEFT"] for x in left) and all(x in selected["RIGHT"] for x in right),"selected_ops",checks);check(int(p["operation_count"])==len(left)+len(right)<=3 and len(left)<=2 and len(right)<=2,"layer_caps",checks)
    checks=list(dict.fromkeys(checks));vocab={x["surface_group"] for x in obs};folios=defaultdict(set)
    for x in obs:folios[x["surface_group"]].add(x["folio_id"])
    for side in ("LEFT","RIGHT"):
        for op in selected[side]:
            hosts,fs=set(),set()
            for word in vocab:
                if side=="LEFT" and word.startswith(op) and len(word)>len(op) and word[len(op):] in vocab:host=word[len(op):];hosts.add(host);fs.update(folios[word]|folios[host])
                if side=="RIGHT" and word.endswith(op) and len(word)>len(op) and word[:-len(op)] in vocab:host=word[:-len(op)];hosts.add(host);fs.update(folios[word]|folios[host])
            check(1<=len(op)<=3 and len(hosts)>=8 and len(fs)>=5,"operation_eligibility",checks)
    checks=list(dict.fromkeys(checks));check(sum(x["diagnostic"]=="REGISTER_GEOMETRY_ALIGNMENT" for x in diag)==12,"alignment_count",checks);check(sum(x["diagnostic"]=="HELD_CONTEXT" for x in diag)==4,"held_count",checks);check(all(int(x["content_folios"])==176 for x in diag if x["diagnostic"]=="HELD_CONTEXT"),"held_folios",checks)
    for mode,summary in result["summary"].items():
        sub=[x for x in parses if x["parser_level"]==mode];check(len({x["inferred_host"] for x in sub})==int(summary["inferred_host_types"]),"summary_types",checks);check(abs(sum(int(x["operation_count"]) for x in sub)/len(sub)-float(summary["mean_operation_count"]))<1e-12,"summary_ops",checks)
    checks=list(dict.fromkeys(checks));check(csha(parses)==result["commitments"]["parse_content_sha256"],"parse_content_hash",checks);check(all(sha(R/k)==v for k,v in result["inputs"].items()) and all(sha(R/k)==v for k,v in result["outputs"].items()),"artifact_hashes",checks);check(sha(RUNNER)==result["implementation"][RUNNER.name] and sha(CORE)==design["core_runner_sha256"],"implementation_hashes",checks)
    stored=result.pop("result_content_sha256");check(csha(result)==stored,"result_content_hash",checks);check(not any(x in RUNNER.read_text() for x in design["forbidden_inputs"]),"firewall_source",checks);fw=result["blind_firewall"];check(not fw["forbidden_inputs_opened"] and not fw["oracle_fields_used"] and fw["voynich_inputs"]==0 and not fw["f84_access"],"firewall_result",checks)
    out={"schema":"GDT173_BLIND_VALIDATION_V1","status":"PASS_INDEPENDENT_NO_ORACLE_B2_BLIND_RECONSTRUCTION","checks_passed":len(checks),"checks_failed":0,"checks":checks,"observation_rows":len(obs),"parse_rows":len(parses),"operation_rows":len(ops),"diagnostic_rows":len(diag),"result_sha256":sha(RESULT),"validator_sha256":sha(Path(__file__)),"oracle_files_opened":0,"voynich_inputs":0,"f84_access":False};out["validation_content_sha256"]=csha(out);OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(f"PASS {len(checks)}/{len(checks)}")
if __name__=="__main__":main()

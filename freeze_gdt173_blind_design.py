#!/usr/bin/env python3
"""Freeze unchanged GDT172 blind instrument for anonymous B2."""
from __future__ import annotations
import hashlib,json
from pathlib import Path

R=Path(__file__).resolve().parent
FREEZE=R/"gdt173_b2_source_freeze.json";PARENT_DESIGN=R/"gdt172_blind_design.json"
CORE_RUNNER=R/"run_gdt170_blind_instrument.py";METHOD=R/"GDT173_HUMAN_GROWN_DISTRIBUTED_CONTROL_METHOD.md"
OUT=R/"gdt173_blind_design.json"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()

def main():
    p=json.loads(PARENT_DESIGN.read_text())
    d={"schema":"GDT173_BLIND_INSTRUMENT_DESIGN_V1","status":"FROZEN_UNCHANGED_GDT172_INSTRUMENT_BEFORE_B2_BLIND_PARSE",
       "source_freeze_sha256":sha(FREEZE),"parent_design_sha256":sha(PARENT_DESIGN),"core_runner_sha256":sha(CORE_RUNNER),"method_sha256":sha(METHOD),
       "parser_algorithm":"UNCHANGED_GDT170_GDT172_EXACT_SURFACE_CONTRAST_AND_LAYOUT_ASSISTED_RANKS",
       "blind_levels":p["blind_levels"],"operation_discovery":p["operation_discovery"],"surface_parse_rank":p["surface_parse_rank"],
       "annotation_assisted_rank":p["annotation_assisted_rank"],"diagnostics":p["diagnostics"],"context_smoothing":p["context_smoothing"],
       "operation_null_worlds":p["operation_null_worlds"],"alignment_host_panel":p["alignment_host_panel"],"corpus_adaptation":p["corpus_adaptation"],
       "forbidden_inputs":["gdt173_b2_sealed_oracle.json.gz","gdt173_b2_lookup.tsv","gdt173_b2_family_manifest.tsv","author_gdt173_b2_lookup.py","build_gdt173_b2_control.py"],
       "blind_output_freeze_before_oracle_unblinding":True,"no_voynich_tuning":True,"voynich_inputs":0,"f84_access":False,
       "implementation":{Path(__file__).name:sha(Path(__file__))},"claim_ceiling":"Blind synthetic B2 outputs only; no Voynich architecture word code value language meaning plaintext or translation."}
    d["design_content_sha256"]=csha(d);OUT.write_text(json.dumps(d,indent=2,sort_keys=True)+"\n");print(d["status"])
if __name__=="__main__":main()

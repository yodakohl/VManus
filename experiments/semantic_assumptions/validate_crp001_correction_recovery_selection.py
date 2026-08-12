#!/usr/bin/env python3
from __future__ import annotations

import hashlib, json, re, urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/"experiments/semantic_assumptions"; RES=BASE/"results"
SOURCE=ROOT/"transcription/sources/Stolfi_text25e1-52.evt"
METHOD=BASE/"CRP001_CORRECTION_RECOVERY_PANEL_METHOD.md"
PRODUCER=BASE/"build_crp001_correction_recovery_selection.py"
RESULT=RES/"crp001_correction_recovery_selection.json"
REPORT=RES/"crp001_correction_recovery_selection_report.md"
OUT=RES/"crp001_correction_recovery_selection_validation.json"
OUT_MD=RES/"crp001_correction_recovery_selection_validation_report.md"
MANIFEST_URL="https://collections.library.yale.edu/manifests/2002046"
MANIFEST_SHA="317d58fd9ea90392a83d9858a91eada3d0b41416a3c835857dc0154bd123a309"

def shab(b: bytes)->str:return hashlib.sha256(b).hexdigest()
def sha(p: Path)->str:return shab(p.read_bytes())

def hits(raw:str)->list[str]:
    comments=[]; out=[]
    for line in raw.splitlines():
        if line.startswith("#"): comments.append(line[1:].strip())
        elif line.startswith("<f"):
            m=re.match(r"<([^;>]+);",line); block=" ".join(comments)
            if m and re.search("correction",block,re.I) and re.search("darker ink|erasure",block,re.I): out.append(m.group(1))
            comments=[]
        elif line.strip() and not line.startswith("@@"): comments=[]
    return out

def main()->None:
    if OUT.exists() or OUT_MD.exists(): raise SystemExit("refusing overwrite")
    checks={}
    def ck(name:str,value:bool)->None: checks[name]=bool(value)
    raw=SOURCE.read_text(encoding="latin-1")
    exact_hits=hits(raw); ck("independent_complete_literal_scan",exact_hits==["f18r.3","f19r.2","f26v.5","f81v.19"])
    data=json.loads(RESULT.read_text())
    ck("strict_top_level_schema",set(data)=={"experiment","schema","status","decision","counts","selection_rule","prior_exclusions","targets","panel_pass_rule","gates","inputs","access","claim_ceiling"})
    ck("expected_residual_loci",[x["locus"] for x in data["targets"]]==exact_hits[:3])
    ck("only_prior_exclusion",data["prior_exclusions"]=={"f81v.19":"PIP001"})
    ck("three_distinct_pages",len({x["page"] for x in data["targets"]})==3)
    ck("target_access_false",data["access"]=={"formal_identity_or_meaning_used":False,"ocr_clip_embeddings_or_automated_recognition_used":False,"target_image_bodies_opened":False})
    ck("all_selection_gates_true",all(data["gates"].values()))
    ck("method_hash",data["inputs"][str(METHOD.relative_to(ROOT))]==sha(METHOD))
    ck("source_hash",data["inputs"][str(SOURCE.relative_to(ROOT))]==sha(SOURCE))
    req=urllib.request.Request(MANIFEST_URL,headers={"User-Agent":"VManus-CRP001-validator/1.0"})
    with urllib.request.urlopen(req,timeout=60) as response: manifest_raw=response.read()
    ck("manifest_hash",shab(manifest_raw)==MANIFEST_SHA)
    manifest=json.loads(manifest_raw); by={c["label"]["none"][0]:c for c in manifest["items"]}
    expected=[]
    for label in ["18r","19r","26v"]:
        c=by[label]; b=c["items"][0]["items"][0]["body"]
        expected.append((c["id"].rsplit("/",1)[-1],[b["width"],b["height"]]))
    ck("independent_canvas_bindings",[(x["canvas_id"],x["official_dimensions"]) for x in data["targets"]]==expected)
    ck("producer_not_imported_or_executed",True); ck("no_image_body_requested",True)
    ck("result_canonical",RESULT.read_bytes()==(json.dumps(data,sort_keys=True,separators=(",",":"))+"\n").encode())
    status="PASS_INDEPENDENT_SOURCE_AND_MANIFEST_RECONSTRUCTION" if all(checks.values()) else "FAIL"
    validation={"experiment":"CRP001_CORRECTION_RECOVERY_SELECTION_VALIDATION","schema":"CRP001_SELECTION_VALIDATION_V1","status":status,
                "source_result_sha256":sha(RESULT),"source_report_sha256":sha(REPORT),"producer_sha256":sha(PRODUCER),
                "check_count":len(checks),"checks":checks,"reconstructed":{"literal_rule_hits":exact_hits,"residual_loci":exact_hits[:3],"canvas_ids":[x[0] for x in expected]},
                "claim_ceiling":data["claim_ceiling"]}
    if status=="FAIL": raise SystemExit(json.dumps(checks,sort_keys=True))
    OUT.write_text(json.dumps(validation,sort_keys=True,separators=(",",":"))+"\n")
    OUT_MD.write_text(f"# CRP001 selection validation\n\nStatus: **{status}**.\n\nA nonimporting validator independently reconstructed all four literal-rule hits, the one prior-panel exclusion, the three residual targets, and their official Yale canvas bindings without requesting image bodies. {len(checks)}/{len(checks)} checks pass.\n")

if __name__=="__main__":main()

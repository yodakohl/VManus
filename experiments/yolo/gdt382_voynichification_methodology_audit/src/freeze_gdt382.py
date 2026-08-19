#!/usr/bin/env python3
"""Freeze an oracle-blind composite encoding and the GDT382 recovery design."""
from __future__ import annotations
import csv,gzip,hashlib,io,json,math
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
BASE=ROOT/"experiments/yolo/gdt382_voynichification_methodology_audit"
ART=BASE/"artifacts"
G378=ROOT/"experiments/yolo/gdt378_cross_corpus_construction_transfer/artifacts"
OBS=G378/"gdt378_comparator_observation_layer.tsv.gz"
ORACLE=G378/"gdt378_hidden_oracle.tsv.gz"
OUT=ART/"gdt382_voynichified_observation_layer.tsv.gz"
ENDPOINTS=["FUNCTION_WORD","ALTERNATIVE_OR","POLARITY_EXCLUSION","UNTIL_STATE_GATE","COORDINATOR","REF_ANAPHORA"]
REPS=["SOURCE_TOKEN_EQUALITY","DOMAIN_LOCAL_OPAQUE_ID","HOST_IDENTITY","COMPOSITE_JOINT_STATE","COMPLETE_RENDERED_GROUP","FIELD_CONSTRUCTION_SPAN"]
MODES=["BASE_ORACLE_BLIND","FREE_TOKEN","PREFIX","SUFFIX","WRAPPER_ALTERNATION","BOUNDARY_CHOICE","POSITIONAL_ALTERNATION","ZERO_SUPPLETIVE"]
VARS=["LINE_FIELD_POSITION","RECORD_RELATIVE_POSITION","BOUNDARY_CLOSURE","RECURRENCE","GLOBAL_LOCAL_FREQUENCY","RECORD_LENGTH","PREVIOUS_STATE","NEXT_STATE"]

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def h(*parts,n=12):return hashlib.sha256("\x1f".join(map(str,parts)).encode()).hexdigest()[:n]
def content(d):
    q=dict(d);q.pop("content_hash",None)
    return hashlib.sha256(json.dumps(q,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def read(p):
    with gzip.open(p,"rt",encoding="utf-8",newline="") as f:return list(csv.DictReader(f,delimiter="\t"))
def write_gz(p,rows,fields):
    p.parent.mkdir(parents=True,exist_ok=True)
    raw=p.open("wb");gz=gzip.GzipFile(filename="",mode="wb",fileobj=raw,mtime=0);f=io.TextIOWrapper(gz,encoding="utf-8",newline="")
    with f:w=csv.DictWriter(f,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)

def pos_state(j,m):
    if j==0:return "START"
    if j==m-1:return "END"
    q=j/max(1,m-1)
    return "EARLY" if q<.34 else "MIDDLE" if q<.67 else "LATE"
def size_state(m):return "R1_8" if m<=8 else "R9_16" if m<=16 else "R17_32" if m<=32 else "R33_PLUS"
def host_code(domain,form):
    alphabet="ABCDEFGHJKLMNPQRSTUVWXYZ23456789";v=int(h("host",domain,form,n=10),16)
    ln=2+(v%2);out=""
    for _ in range(ln):out+=alphabet[v%len(alphabet)];v//=len(alphabet)
    return out
def render(host,renderer):
    if renderer=="R0":return host.lower()
    if renderer=="R1":return host[0].lower()+host[1:]
    return host[:-1]+host[-1].lower()

def main():
    assert "f84" not in str(OBS).lower() and "f84" not in str(ORACLE).lower()
    rows=read(OBS);byrec=defaultdict(list)
    for r in rows:byrec[(r["domain"],r["collection_id"],r["record_id"])].append(r)
    out=[]
    for rec,rr in sorted(byrec.items()):
        rr.sort(key=lambda x:int(x["element_ordinal"]));m=len(rr);field=0;within=0
        hosts=[host_code(x["domain"],x["opaque_form_id"]) for x in rr]
        for j,r in enumerate(rr):
            host=hosts[j];renderer="R"+str(int(h("renderer",r["domain"],r["collection_id"],r["opaque_form_id"],int(r["record_ordinal"])%3,n=8),16)%3)
            wrapper="W"+str(int(h("wrapper",r["domain"],r["collection_id"],r["record_id"],r["opaque_form_id"],j%3,n=8),16)%6)
            ps=pos_state(j,m);boundary=("B"+r["boundary_before"]+r["boundary_after"]);rs=size_state(m)+"_"+("ODD" if int(r["record_ordinal"])%2 else "EVEN")
            opaque="O"+h("opaque",r["domain"],r["opaque_form_id"],n=14)
            joint="J"+h(host,wrapper,ps,boundary,rs,renderer,n=16)
            rendered=wrapper[-1]+render(host,renderer)+{"START":"s","EARLY":"e","MIDDLE":"m","LATE":"l","END":"z"}[ps]+boundary[-1]
            field_id=f"{r['domain']}:{r['collection_id']}:{r['record_id']}:F{field:03d}"
            prev=hosts[j-1] if j else "RECORD_START";nxt=hosts[j+1] if j+1<m else "RECORD_END"
            out.append({
                "element_key":r["element_key"],"domain":r["domain"],"collection_id":r["collection_id"],"record_id":r["record_id"],"record_ordinal":r["record_ordinal"],"element_ordinal":r["element_ordinal"],
                "source_token_equality":r["opaque_form_id"],"domain_local_opaque_id":opaque,"host_id":host,"wrapper_state":wrapper,"positional_state":ps,"boundary_state":boundary,"record_state":rs,"renderer_variant":renderer,
                "composite_joint_id":joint,"rendered_group":rendered,"field_id":field_id,"field_index":field,"within_field_index":within,"record_element_count":m,"relative_position":r["relative_position"],"surface_length":r["surface_length"],"within_record_frequency":r["within_record_frequency"],"previous_host":prev,"next_host":nxt,
                "encoder_used_oracle":"0","semantic_state":"HIDDEN_UNASSIGNED"})
            within+=1
            if within>=4 or r["boundary_after"]=="1":field+=1;within=0
    fields=list(out[0]);write_gz(OUT,out,fields)
    manifest={"schema":"GDT382_ENCODER_FREEZE_V1","status":"ORACLE_BLIND_ENCODER_FROZEN_BEFORE_RECOVERY","rows":len(out),"records":len(byrec),"domains":sorted({x["domain"] for x in out}),"encoder_seed":"SHA256_DOMAIN_SEPARATED_V1","field_width":4,"components":["HOST","WRAPPER","POSITIONAL_STATE","BOUNDARY_STATE","RECORD_STATE","RENDERER_VARIANT"],"oracle_used_to_build_base_layer":False,"observation_input":{str(OBS.relative_to(ROOT)):sha(OBS)},"hidden_oracle_commitment":{str(ORACLE.relative_to(ROOT)):sha(ORACLE)},"encoded_output":{str(OUT.relative_to(ROOT)):sha(OUT)},"f84":{"input":False,"opened":False,"parsed":False,"retained":False,"scored":False}}
    manifest["content_hash"]=content(manifest);(ART/"gdt382_encoder_freeze.json").write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n")
    design={"schema":"GDT382_RECOVERY_DESIGN_FREEZE_V1","status":"FROZEN_BEFORE_HIDDEN_ORACLE_EVALUATION","endpoints":ENDPOINTS,"representations":REPS,"encoding_modes":MODES,"overcontrol_variables":VARS,"overcontrol_treatments":["GRAMMAR_FEATURE","CONDITIONED_NUISANCE","REMOVED"],"recovery_regimes":["STRICT_UNIVERSAL_HELD_DOMAIN","DOMAIN_LOCAL_HIERARCHICAL_HELD_COLLECTION"],"primary_metrics":["held_logloss_gain_bits","auc","average_precision","positive_domains"],"exploration_gate":{"auc":.60,"gain_bits":0},"confirmation_gate":{"minimum_domains_auc_0_60_and_positive_gain":3,"requires_nonrecipe":True,"requires_procedural":True,"fixed_prediction_max_family_p":.05},"null":{"worlds":256,"preserve":["domain","collection","record_length_bin","position_bin","boundary_state"]},"prospective_split":{"development_domains":["COREMA","CURIOUS_CURES","PCEEC2"],"confirmation_domains":["HARLEIAN_COOKERY","QUINTE_ESSENCE"]},"ontology_inventories":{"NATURAL_LANGUAGE_LIKE":["COORDINATOR","ALTERNATIVE_OR","POLARITY_EXCLUSION","UNTIL_STATE_GATE","REF_ANAPHORA","FUNCTION_WORD"],"TECHNICAL_NOTATION_LIKE":{"ADD_ITEM":"COORDINATOR","ALTERNATIVE_SLOT":"ALTERNATIVE_OR","EXCEPTION":"POLARITY_EXCLUSION","NEXT_OR_GATE":"UNTIL_STATE_GATE","COPY_PREVIOUS":"REF_ANAPHORA","RELATION_OR_END":"FUNCTION_WORD"}},"gdt381_outcome_used_to_design":False,"voynich_scoring":False,"f84_accessed":False,"inputs":{"encoder_freeze":sha(ART/"gdt382_encoder_freeze.json"),"method":sha(BASE/"METHOD.md")}}
    design["content_hash"]=content(design);(ART/"gdt382_recovery_design_freeze.json").write_text(json.dumps(design,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"rows":len(out),"records":len(byrec),"encoder":manifest["content_hash"],"design":design["content_hash"]}))
if __name__=="__main__":main()

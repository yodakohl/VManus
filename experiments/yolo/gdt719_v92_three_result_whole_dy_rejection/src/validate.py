#!/usr/bin/env python3
"""Independent evidence, parity, confidence and renderer checks for GDT719."""
from __future__ import annotations
import csv, hashlib, json, sys
from collections import Counter
from pathlib import Path
sys.dont_write_bytecode = True

def root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists(): return candidate
    raise RuntimeError("repository root not found")

ROOT = root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt719_v92_three_result_whole_dy_rejection"
SRC, ART = EXP / "src", EXP / "artifacts"
G718 = ROOT / "experiments/yolo/gdt718_v91_three_result_whole_core_context_repair/artifacts"
PATHS = {
 "sl": G718/"V91_324_ACTIVE_LEXICAL_READINGS.tsv", "sc": G718/"V91_479_CONTEXT_REALIZATIONS.tsv",
 "sd": G718/"V91_COMPLETE_WORD_CONFIDENCE.tsv", "sq": G718/"V91_64_HELD_READING_AUDIT.tsv",
 "ss": G718/"V91_2_BOUND_SPAN_RENDERER.tsv", "spec": SRC/"V92_3_AUDIT_SPECS.tsv",
 "bind": SRC/"V92_34_PRIMARY_EVIDENCE_BINDINGS.tsv", "lex": ART/"V92_324_ACTIVE_LEXICAL_READINGS.tsv",
 "ctx": ART/"V92_479_CONTEXT_REALIZATIONS.tsv", "census": ART/"V92_61_HELD_READING_AUDIT.tsv",
 "delta": ART/"V92_3_RESULT_WHOLE_CORE_CONTEXT_DELTA.tsv", "evidence": ART/"V92_34_PRIMARY_EVIDENCE_BINDINGS.tsv",
 "reject": ART/"V92_1_REJECTED_SHARED_DY_DECOMPOSITION.tsv", "spans": ART/"V92_2_BOUND_SPAN_RENDERER.tsv",
 "directives": ART/"V92_2_ONE_SHOT_RENDER_DIRECTIVES.tsv", "render": ART/"V92_8_F7R2_RENDERED_UNITS.tsv",
 "complete": ART/"V92_COMPLETE_WORD_CONFIDENCE.tsv",
}
H0="H0_NONE"; IDS={"kchody#1","ochdy#1","oechedy#1"}
STATUS=("PASS_V92_3_RESULT_WHOLES_REVISED__SHARED_DY_DECOMPOSITION_REJECTED__"
        "3_POSITIONS_3_PAGES__58_WEAK_READINGS_REMAIN__NO_SCORE_CREDIT__ALL_H0_NONE")

def rd(path: Path) -> list[dict[str,str]]:
    with path.open(encoding="utf-8",newline="") as f:return list(csv.DictReader(f,delimiter="\t"))
def split(v:str)->list[str]:return [x for x in v.split("|") if x and x not in {"NONE","0"}]
def parse(v:str)->dict[str,str]:return dict(x.split("=",1) for x in v.split(";") if x)
def v92(k:str)->str:return k.replace("v91","v92").replace("V91","V92")
def lvl(n:int)->str:
    return "W0_PLACEHOLDER_OR_SEMANTICALLY_EMPTY" if n<20 else "W1_WEAK_WORKING" if n<40 else "W2_PROVISIONAL_WORKING" if n<60 else "W3_SOLID_WORKING_THEORY" if n<80 else "W4_STRONG_WORKING_THEORY"
def by_source(rows):
    out={}
    for row in rows:
        for key in split(row["source_reading_ids"]): assert key not in out; out[key]=row
    return out
class Audit:
    def __init__(self):self.n=0;self.groups=Counter()
    def check(self,ok,msg,group):
        self.n+=1;self.groups[group]+=1
        if not ok:raise AssertionError(msg)

def main()->int:
    a=Audit(); x={k:rd(v) for k,v in PATHS.items()}
    expected={"sl":324,"sc":479,"sd":1586,"sq":64,"ss":2,"spec":3,"bind":34,"lex":324,"ctx":479,"census":61,"delta":3,"evidence":34,"reject":1,"spans":2,"directives":2,"render":8,"complete":1586}
    for key,n in expected.items():a.check(len(x[key])==n,f"count {key}","counts")
    specs={r["source_reading_id"]:r for r in x["spec"]}
    a.check(set(specs)==IDS and len(specs)==3,"spec universe","spec")
    cores={"kchody#1":"heiß-trocken; abgeschlossen","ochdy#1":"trocken; abgeschlossen","oechedy#1":"bis Mittelstufe getrocknet; abgeschlossen"}
    for key,s in specs.items():
        a.check(s["v92_lexical_core_de"]==cores[key] and s["decision"]=="REVISE","core/decision "+key,"spec")
        a.check(s["family_ids"]==s["score_credit_family_ids"]=="NONE" and s["score_delta_lexical_core"]=="0","no credit "+key,"score")
        a.check(s["component_global_export_allowed"]=="0" and s["decomposition"]=="LEARNED_WHOLE_RESULT_NO_FREE_DY","scope "+key,"scope")
    a.check(len({r["expected_position_id"] for r in x["spec"]})==3 and len({r["expected_page"] for r in x["spec"]})==3,"position universe","spec")

    evidence={r["binding_id"]:r for r in x["evidence"]}
    a.check(len(evidence)==len({r["binding_id"] for r in x["bind"]})==34,"binding ids","evidence")
    occ=0
    for b in x["bind"]:
        a.check(b["source_reading_id"] in IDS and b["score_credit_family_ids"]=="NONE","binding scope "+b["binding_id"],"score")
        a.check("f84" not in b["evidence_path"].lower(),"sealed path","sealed")
        selector, assertions=parse(b["selector"]),parse(b["field_assertions"])
        a.check(all(not value.lower().startswith("f84") for value in selector.values()),"sealed selector","sealed")
        matches=[r for r in rd(ROOT/b["evidence_path"]) if all(r.get(k)==v for k,v in selector.items())]
        a.check(len(matches)==1,"selector "+b["binding_id"],"evidence")
        source=matches[0]
        for k,v in assertions.items():a.check(source.get(k)==v,f"assert {b['binding_id']}:{k}","assertions")
        fp=hashlib.sha256(json.dumps(source,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest(); out=evidence[b["binding_id"]]
        for k,v in b.items():a.check(out[k]==v,f"copy {b['binding_id']}:{k}","evidence_copy")
        a.check(out["matched_row_fingerprint_sha256"]==fp and out["source_row_match"]=="1","fingerprint "+b["binding_id"],"fingerprints")
        a.check(out["evidence_status"]=="BOUND_EXACT_PRIMARY_ROW" and out["historical_confirmation"]==H0,"status "+b["binding_id"],"evidence")
        occ+=b["evidence_role"].endswith("OCCURRENCE")
    a.check(occ==5,"five older occurrence controls","evidence")
    formal = {r["binding_id"]: parse(r["field_assertions"]) for r in x["bind"] if r["evidence_role"] == "CANONICAL_LATER_FORMAL_STATUS"}
    a.check(formal["G689_KCHODY_FORM"]["formal_dy_status"] == "NO_FORMAL_DY" and formal["G689_KCHODY_FORM"]["gdt515_recipes"] == "K+CH+O+D_ADDR+Y", "kchody later formal trace", "formal_status")
    a.check(formal["G689_OCHDY_FORM"]["formal_dy_status"] == "NO_FORMAL_DY" and formal["G689_OCHDY_FORM"]["gdt515_recipes"] == "O+CHD+Y", "ochdy later formal trace", "formal_status")
    a.check(formal["G689_OECHEDY_FORM"]["formal_dy_status"] == "UNRESOLVED" and formal["G689_OECHEDY_FORM"]["gdt515_recipes"] == "NONE" and formal["G689_OECHEDY_FORM"]["pair_status"] == "NO_REAL_SISTER", "oechedy unresolved no sister", "formal_status")

    sl,tl=by_source(x["sl"]),by_source(x["lex"])
    for key,s in specs.items():
        old,new=sl[key],tl[key]
        checks={"v92_lexical_core_de":s["v92_lexical_core_de"],"v92_context_realizations_de":s["v92_context_realization_de"],"family_ids":"NONE","decomposition":"LEARNED_WHOLE_RESULT_NO_FREE_DY","last_semantic_writer":"GDT719","base_score":"30","score_delta_lexical_core":"0","working_model_score_0_100_not_probability":"30","working_model_level":"W1_WEAK_WORKING","v92_audit_decision":"REVISE","v92_component_global_export_allowed":"0","historical_confirmation":H0}
        for f,v in checks.items():a.check(new[f]==v,f"lex {key}:{f}","target_lexical")
        a.check(old["v91_lexical_core_de"]==s["old_lexical_core_de"] and "GDT719" in split(new["source_gdts"]),"lex lineage "+key,"target_lexical")
        a.check(not any(w in new["v92_lexical_core_de"].lower() for w in ("masse","ansatz","zubereitung","extrakt","rückstand")),"head leak "+key,"head_boundary")
    skip={"v92_audit_decision","v92_evidence_class","v92_open_semantic_slots","v92_component_global_export_allowed","v92_prior_lexical_core_de"}; nonlex=0
    for old in x["sl"]:
        ids=split(old["source_reading_ids"])
        if len(ids)==1 and ids[0] in IDS:continue
        nonlex+=1;new=tl[ids[0]]
        for f,v in old.items():
            if v92(f) not in skip:a.check(new[v92(f)]==v,f"lex parity {old['surface']}:{f}","lexical_parity")
    a.check(nonlex==321,"nonlex count","lexical_parity")

    sc={r["position_id"]:r for r in x["sc"]};tc={r["position_id"]:r for r in x["ctx"]}; pos={s["expected_position_id"] for s in specs.values()}; lo={(r["locus"],int(r["token_ordinal"])):r for r in x["sc"]}
    for key,s in specs.items():
        old,new=sc[s["expected_position_id"]],tc[s["expected_position_id"]]
        a.check(lo[(old["locus"],int(old["token_ordinal"])-1)]["surface"]==s["expected_left_surface"],"left "+key,"context")
        a.check(new["v92_lexical_core_de"]==s["v92_lexical_core_de"] and new["v92_context_realization_de"]==s["v92_context_realization_de"],"context "+key,"context")
        a.check(new["v92_lexical_score"]==new["v92_context_score"]=="30","context score "+key,"score")
        a.check(old["v68_clause_type"]=="NOMINAL_BLOCK" and old["v68_action_license"]=="NOT_ACTION_LICENSED","nominality "+key,"context")
    skip={"v92_audit_decision","v92_evidence_class","v92_open_semantic_slots","v92_component_global_export_allowed","v92_local_context_hypothesis","v92_expected_left_surface"}; nonctx=0
    for old in x["sc"]:
        if old["position_id"] in pos:continue
        nonctx+=1;new=tc[old["position_id"]]
        for f,v in old.items():
            if v92(f) not in skip:a.check(new[v92(f)]==v,f"context parity {old['position_id']}:{f}","context_parity")
    a.check(nonctx==476,"nonctx count","context_parity")

    held={r["source_reading_id"] for r in x["sq"] if r["disposition"]=="HELD_FOR_LATER_REPAIR"}
    a.check(len(held)==61 and {r["source_reading_id"] for r in x["census"]}==held,"census universe","census")
    a.check(Counter(r["disposition"] for r in x["census"])==Counter({"HELD_FOR_LATER_REPAIR":58,"REVISED_IN_V92":3}),"census disposition","census")
    reject=x["reject"][0]
    a.check(reject["decision"]=="REJECT_NO_COMMON_LICENSED_WRITTEN_UNIT" and reject["score_credit_family_ids"]=="NONE" and reject["score_delta"]=="0","family reject","rejected_family")
    a.check(set(split(reject["selected_source_reading_ids"]))==IDS and reject["component_global_export_allowed"]=="0","family scope","rejected_family")

    a.check(x["spans"]==x["ss"],"span parity","renderer")
    f7=sorted((r for r in x["sc"] if r["locus"]=="f7r.2"),key=lambda r:int(r["token_ordinal"]));span=next(r for r in x["ss"] if r["locus"]=="f7r.2")
    expect=[]
    for r in f7:
        if r["position_id"]==span["right_position_id"]:continue
        expect.append(span["render_once_de"] if r["position_id"]==span["left_position_id"] else r["v91_context_realization_de"])
    a.check(len(f7)==9 and [r["rendered_text_de"] for r in x["render"]]==expect,"f7r2 parity","renderer")

    active={r["reading_id"]:r for r in x["complete"] if r["current_layer"]=="ACTIVE_V92_LEXICAL_CORE"};a.check(len(active)==324 and len({r["surface"] for r in x["complete"]})==1582,"complete universe","complete")
    for r in x["lex"]:
        d=active[r["v92_reading_id"]]
        for df,lf in (("working_meaning_de","v92_lexical_core_de"),("working_model_score_0_100_not_probability","working_model_score_0_100_not_probability"),("positive_evidence_de","positive_evidence_de"),("counterevidence_de","counterevidence_de")):a.check(d[df]==r[lf],f"active dictionary {r['surface']}:{df}","complete_parity")
    oldd={(r["surface"],r["reading_id"]):r for r in x["sd"]}; skip={"v92_audit_decision","v92_evidence_class","v92_open_semantic_slots","v92_component_global_export_allowed"}; nonactive=[r for r in x["complete"] if r["current_layer"]!="ACTIVE_V92_LEXICAL_CORE"]
    a.check(len(nonactive)==1262,"nonactive count","complete_parity")
    for new in nonactive:
        old=oldd[(new["surface"],new["reading_id"])]
        for f,v in old.items():
            if v92(f) not in skip:a.check(new[v92(f)]==v,f"complete parity {new['reading_id']}:{f}","complete_parity")
    for r in x["complete"]:
        a.check(bool(r["working_meaning_de"].strip()) and bool(r["positive_evidence_de"].strip()) and bool(r["counterevidence_de"].strip()),"dictionary evidence "+r["reading_id"],"dictionary")
        n=int(r["working_model_score_0_100_not_probability"]);a.check(r["working_model_level"]==lvl(n) and r["historical_confirmation"]==H0,"dictionary confidence "+r["reading_id"],"dictionary")
    levels=Counter(r["working_model_level"] for r in x["lex"]);a.check(levels==Counter({"W0_PLACEHOLDER_OR_SEMANTICALLY_EMPTY":7,"W1_WEAK_WORKING":135,"W2_PROVISIONAL_WORKING":163,"W3_SOLID_WORKING_THEORY":19}),"active levels","score")
    for r in x["delta"]:a.check(r["old_score"]==r["v92_score"]=="30" and r["score_credit_family_ids"]=="NONE","delta "+r["source_reading_id"],"score")

    result=json.loads((ART/"RESULT.json").read_text()); expected_result={"experiment_id":"GDT719","status":STATUS,"audited_readings":3,"primary_evidence_bindings":34,"remaining_unreviewed_weak_readings":58,"shared_free_dy_decomposition_accepted":0,"active_lexical_readings":324,"active_positions":479,"complete_readings":1586,"complete_surfaces":1582,"f7r2_rendered_units":8,"relation_word_credit_gdt719":0,"historical_confirmation":H0,"f84_or_f84r_used":0}
    for f,v in expected_result.items():a.check(result[f]==v,"result "+f,"result")
    report=(EXP/"REPORT.md").read_text()
    for word in (STATUS,"34","1586","58","einen Familien- oder Fluessigkeitsbonus"):a.check(word in report,"report "+word,"report")
    a.check(all(not r["page"].startswith("f84") and not r["locus"].startswith("f84") for r in x["ctx"]),"sealed contexts","sealed")
    out={"experiment_id":"GDT719","status":"PASS","checks_passed":a.n,"check_groups":dict(sorted(a.groups.items())),"target_readings":3,"primary_evidence_bindings_replayed":34,"dy_counterevidence_occurrence_rows_replayed":5,"score_credit_families":0,"score_delta_total":0,"non_target_lexical_rows_preserved":nonlex,"non_target_context_positions_preserved":nonctx,"complete_dictionary_rows_with_default_confidence_and_evidence":1586,"bound_spans_preserved":2,"f7r2_source_positions":9,"f7r2_output_units":8,"remaining_unreviewed_weak_readings":58,"f84_or_f84r_used":0}
    (ART/"VALIDATION.json").write_text(json.dumps(out,ensure_ascii=False,indent=2,sort_keys=True)+"\n");print(json.dumps(out,ensure_ascii=False,sort_keys=True));return 0
if __name__=="__main__":raise SystemExit(main())

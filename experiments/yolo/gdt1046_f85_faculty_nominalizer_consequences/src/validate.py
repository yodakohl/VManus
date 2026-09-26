#!/usr/bin/env python3
"""Independent literal replay for GDT1046. Does not import src/run.py."""
from __future__ import annotations
import csv, hashlib, json, sys
from collections import Counter
from pathlib import Path


def find_root(p: Path) -> Path:
    for q in (p, *p.parents):
        if (q / "AGENTS.md").is_file() and (q / ".git").exists():
            return q
    raise RuntimeError("VManus repository root not found")

ROOT = find_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt1046_f85_faculty_nominalizer_consequences"
SPEC = json.loads((EXP / "src/SPEC.json").read_text(encoding="utf-8"))
DRAFT_PATH = ROOT / "research_registry/proposals/laufenberg_f85r2_20260926/FRAME_FACULTY_WHOLE_DRAFT.json"
PARENT_S_PATH = ROOT / "research_registry/proposals/laufenberg_f85r2_20260926/until_s_draft/DRAFT.json"
PARENT_E_PATH = ROOT / "research_registry/proposals/laufenberg_f85r2_20260926/ideas/23_nourishment_requires_faculties.json"

def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def tsv(p: Path) -> list[dict[str, str]]:
    with p.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))

def main() -> int:
    errors=[]
    def ck(ok, msg):
        if not ok: errors.append(msg)

    # The package and all preregistered input files must still match the lock.
    lock=json.loads((EXP/"src/REGISTRATION_LOCK.json").read_text(encoding="utf-8"))
    prereg=EXP/"PREREGISTRATION.md"
    ck(sha(EXP/"src/SPEC.json")==lock["sha256"]["src/SPEC.json"],"SPEC hash mismatch")
    ck(sha(prereg)==lock["sha256"]["PREREGISTRATION.md"],"PREREGISTRATION hash mismatch")
    for name,item in SPEC["inputs"].items():
        p=ROOT/item["path"]
        ck(p.is_file() and sha(p)==item["sha256"],f"input hash missing/mismatch: {name}")

    ctx=tsv(ROOT/SPEC["inputs"]["projection"]["path"])
    draft=json.loads(DRAFT_PATH.read_text(encoding="utf-8"))
    ps=json.loads(PARENT_S_PATH.read_text(encoding="utf-8"))
    pe=json.loads(PARENT_E_PATH.read_text(encoding="utf-8"))
    ck(len(ctx)==473,"source projection does not have 473 rows")
    ck(len({r["source_group_id"] for r in ctx})==473,"source group IDs are not unique")
    byid={r["source_group_id"]:r for r in ctx}

    # Reconstitute the unchanged parent whole-form dictionaries from their source files.
    s_values={}
    for source_key in ("fixed_idea550_bindings","new_whole_form_values"):
        for form,item in ps[source_key].items():
            ck(form not in s_values,"duplicate form between frozen S dictionaries")
            s_values[form]={"type":item["type"],"meaning":item["meaning"]}
    e_values={form:{"type":item["type"],"meaning":item["meaning"]}
              for form,item in pe["design"]["assignments"].items()}
    parent=draft["parent_contracts_unchanged"]
    ck(len(s_values)==24 and parent["S_24"]==s_values,"parent S dictionary changed or is not 24 exact forms")
    ck(len(e_values)==6 and parent["E_6"]==e_values,"parent E six-form dictionary changed")
    all_parent={**s_values,**e_values}
    ck(len(all_parent)==30,"parent S/E dictionaries overlap or have wrong combined size")
    ck(parent["564_components"].keys()=={"qod","qok","ar"},"fixed RAW564 component inventory changed")
    ck("ProcessFrame→FacultySpec" in parent["564_components"]["ar"],"NOM domain/range is not fixed as ProcessFrame to FacultySpec")
    ck(len(parent["564_application_rules"])==4,"the two-reduction contract is not represented by the fixed four-rule list")
    rules=SPEC["reductions"]
    ck(rules=={"forward":["ProcessFrame","RecipientRef","EvaluatedProcessPredicate"],"backward":["ProcessFrame","NOM","FacultySpec"],"nom_domain":"ProcessFrame","nom_range":"FacultySpec","range_is_domain":False,"extra_reframing_or_casts":False},"SPEC reductions no longer express the exact two fixed rules")

    # Independently build the all-row E table by selecting the five E loci from the safe projection.
    e_rows=[r for r in ctx if r["block"]=="E"]
    ck(len(e_rows)==81,"literal E group coverage is not 81")
    e_expected=[]
    for r in e_rows:
        item=all_parent.get(r["ivtff_group_raw"])
        e_expected.append({**r,
            "parent_type": item["type"] if item else "",
            "parent_meaning": item["meaning"] if item else "",
            "assignment_status": "INHERITED_HYPOTHESIS" if item else "UNASSIGNED"})
    e_actual=tsv(EXP/"artifacts/E_GROUPS.tsv")
    ck(e_actual==e_expected,f"E_GROUPS differs from independent 81-row reconstruction ({len(e_actual)} actual)")
    cov={edition:sum(r["edition"]==edition and r["ivtff_group_raw"] in all_parent for r in e_rows)
         for edition in ("ZL3b","IT2a","RF1b")}
    ck(cov=={"ZL3b":8,"IT2a":7,"RF1b":7},f"inherited E membership counts differ: {cov}")

    # Verify the author draft's complete E inventory against source groups and the fixed dictionaries.
    authored_e=draft["all_E_occurrences"]
    ck(len(authored_e)==81,"draft E occurrence inventory does not have 81 rows")
    authored_e_byid={r["source_group_id"]:r for r in authored_e}
    ck(set(authored_e_byid)=={r["source_group_id"] for r in e_rows},"draft E inventory IDs differ from the source's complete E scope")
    for src in e_rows:
        a=authored_e_byid.get(src["source_group_id"],{})
        item=all_parent.get(src["ivtff_group_raw"])
        for key in ("edition","locus","source_group_index","source_group_count","left_separator","right_separator","paragraph_start","paragraph_end","ivtff_group_raw"):
            ck(str(a.get(key,""))==str(src[key]),f"author E source mismatch at {src['source_group_id']} field {key}")
        ck(a.get("inherited_binding")==item,f"author E parent binding mismatch at {src['source_group_id']}")
        expected_origin=("fixed550" if src["ivtff_group_raw"] in s_values else "RAW553") if item else None
        ck(a.get("binding_origin")==expected_origin,f"author E binding origin mismatch at {src['source_group_id']}")
        ck(a.get("status")==("INHERITED_VALUE_CONTEXT_NOT_COMPLETELY_PARSED" if item else "UNASSIGNED_LITERAL_GROUP"),f"author E parse status mismatch at {src['source_group_id']}")

    # Exact standalone ar census, neighbor rows, separators, and the adjacent-pair cases.
    bare=[r for r in ctx if r["ivtff_group_raw"]=="ar"]
    ck(len(bare)==16,"literal bare-ar selection is not 16")
    bare_expected=[]
    pair_first=set(); pair_second=set(); pair_records=[]
    for r in ctx:
        if r["ivtff_group_raw"]=="ar":
            same=[x for x in ctx if x["edition"]==r["edition"] and x["locus"]==r["locus"]]
            ix=next(i for i,x in enumerate(same) if x["source_group_id"]==r["source_group_id"])
            prev=same[ix-1] if ix else None; nxt=same[ix+1] if ix+1<len(same) else None
            if prev is None:
                status="UNRESOLVED_CROSS_LINE_SCOPE"
            elif prev["ivtff_group_raw"]=="ar":
                status="SECOND_NOM_DOMAIN_MISMATCH_UNDER_FIXED_REDUCTIONS"
                pair_second.add(r["source_group_id"])
            elif nxt is not None and nxt["ivtff_group_raw"]=="ar":
                status="FIRST_NOM_FRAME_GRANTED_CONDITIONALLY"
                pair_first.add(r["source_group_id"])
            else:
                status="UNBOUND_PRECEDING_FRAME"
            bare_expected.append({
                "edition":r["edition"],"locus":r["locus"],"source_group_id":r["source_group_id"],
                "source_group_index":r["source_group_index"],"ivtff_group_raw":r["ivtff_group_raw"],
                "left_separator":r["left_separator"],"right_separator":r["right_separator"],
                "previous_id":prev["source_group_id"] if prev else "","previous_raw":prev["ivtff_group_raw"] if prev else "",
                "next_id":nxt["source_group_id"] if nxt else "","next_raw":nxt["ivtff_group_raw"] if nxt else "","status":status})
            if nxt is not None and nxt["ivtff_group_raw"]=="ar":
                between=r["right_separator"]
                ck(between==nxt["left_separator"],f"pair separators disagree at {r['source_group_id']}")
                pair_records.append({"edition":r["edition"],"locus":r["locus"],"first_id":r["source_group_id"],
                    "second_id":nxt["source_group_id"],"between":between,"after_second":nxt["right_separator"],
                    "granted_left_type":"ProcessFrame","first_result_type":"FacultySpec",
                    "second_required_type":"ProcessFrame","result":"DOMAIN_MISMATCH"})
    ar_actual=tsv(EXP/"artifacts/BARE_AR.tsv")
    ck(ar_actual==bare_expected,f"BARE_AR differs from independent reconstruction ({len(ar_actual)} actual)")
    pair_expected=pair_records
    pair_actual=tsv(EXP/"artifacts/DOUBLE_AR.tsv")
    ck(pair_actual==pair_expected,f"DOUBLE_AR differs from independent adjacent-pair reconstruction ({len(pair_actual)} actual)")
    ck(Counter(r["edition"] for r in bare)==Counter({"ZL3b":4,"IT2a":6,"RF1b":6}),"bare ar counts by reader differ from 4/6/6")
    ck(Counter(r["edition"] for r in pair_records)==Counter({"IT2a":1,"RF1b":1}),"adjacent pair sets differ from exact IT/RF pairs, including empty ZL set")

    # The author's complete occurrence inventories must point to these same literal groups and neighbors.
    author_bare=draft["all_bare_ar_occurrences"]
    ck(len(author_bare)==16 and {x["source_group_id"] for x in author_bare}=={x["source_group_id"] for x in bare},"author's bare-ar occurrence IDs incomplete or expanded")
    actual_bare={x["source_group_id"]:x for x in author_bare}
    for x in bare_expected:
        a=actual_bare.get(x["source_group_id"],{})
        ck(a.get("fixed_type")=="ProcessFrame -> FacultySpec",f"bare ar type changed at {x['source_group_id']}")
        prev=a.get("immediately_previous_group") or {}; nxt=a.get("immediately_next_group") or {}
        ck((prev.get("source_group_id", ""),prev.get("ivtff_group_raw", ""),prev.get("right_separator", ""))==
           (x["previous_id"],x["previous_raw"], (byid[x["previous_id"]]["right_separator"] if x["previous_id"] else "")),
           f"author previous-group binding differs at {x['source_group_id']}")
        ck((nxt.get("source_group_id", ""),nxt.get("ivtff_group_raw", ""),nxt.get("left_separator", ""))==
           (x["next_id"],x["next_raw"], (byid[x["next_id"]]["left_separator"] if x["next_id"] else "")),
           f"author next-group binding differs at {x['source_group_id']}")
    traces=draft["adjacent_nom_inference_traces"]
    ck(len(traces)==2 and {x["case_id"] for x in traces}=={"IT2a_f85r2_24_adjacent_nom","RF1b_f85r2_24_adjacent_nom"},"draft does not enumerate exactly the two reader-pair traces, including empty ZL")
    for trace in traces:
        ck(trace["fixed_rule"]=="Backward(F:ProcessFrame, NOM:ProcessFrame->FacultySpec) = NOM(F):FacultySpec",f"trace rule differs: {trace['case_id']}")
        steps=trace["steps"]
        ck(len(steps)==2 and steps[0]["result_type"]=="FacultySpec" and steps[0]["outcome"]=="WELL_TYPED_IF_GRANTED_P_EXISTS",f"first NOM trace invalid: {trace['case_id']}")
        ck(steps[1]["actual_left_type"]=="FacultySpec" and steps[1]["required_left_type"]=="ProcessFrame" and steps[1]["outcome"]=="DOMAIN_MISMATCH",f"second NOM does not fail by fixed domain mismatch: {trace['case_id']}")

    # Verify 44 native line records against all original .24 rows and alignment coverage once.
    native_path=ROOT/SPEC["inputs"]["native_groups"]["path"]
    native=tsv(native_path)
    src24=[r for r in ctx if r["locus"]=="f85r2.24"]
    ck(len(src24)==44 and native==src24,"native .24 group packet differs from the 44 literal projection records")
    align=tsv(ROOT/SPEC["inputs"]["native_alignment"]["path"])
    usage=Counter(); align_errors=[]
    for row in align:
        for edition in ("ZL3b","IT2a","RF1b"):
            gids=row[edition+"_ids"].split(); raws=row[edition+"_literal"].split(" | ")
            if len(gids)!=len(raws):
                align_errors.append(row["alignment_unit"]+":"+edition+":span-length")
                continue
            for gid,raw in zip(gids,raws):
                usage[gid]+=1
                if gid not in byid or byid[gid]["locus"]!="f85r2.24" or byid[gid]["ivtff_group_raw"]!=raw:
                    align_errors.append(gid)
    ck(len(align)==13,"native alignment unit count not 13")
    ck(not align_errors,f"alignment points to wrong source group/literal: {align_errors[:3]}")
    ck(set(usage)=={r["source_group_id"] for r in src24} and all(n==1 for n in usage.values()),"native alignment does not cover all 44 source groups exactly once")
    # Freeze links must match their own B packet and the registered source bindings.
    bfreeze=json.loads((ROOT/"research_registry/proposals/laufenberg_f85r2_20260926/AR_DOUBLE_NATIVE_B_FREEZE.json").read_text(encoding="utf-8"))
    ck(bfreeze["files"].get("research_registry/proposals/laufenberg_f85r2_20260926/AR_DOUBLE_NATIVE_B.json")==SPEC["inputs"]["native_B"]["sha256"],"B observation freeze hash does not bind the preregistered bytes")
    bobs=json.loads((ROOT/"research_registry/proposals/laufenberg_f85r2_20260926/AR_DOUBLE_NATIVE_B.json").read_text(encoding="utf-8"))
    ck(bobs.get("status")=="INITIAL_OBSERVATIONS_FROZEN_BEFORE_PROJECTION_ROW_COMPARISON","B observations not frozen before row comparison")
    ck(bobs.get("informed_observation") is True,"native B exposure is not disclosed")

    # Compact output check reconstructed from the source census and fixed rules.
    expected_result={
      "experiment":"GDT1046","status":"STRICT_NOM_EXTENSION_FAILS_IT_RF_ZL_INCOMPLETE","source_rows":len(ctx),
      "counts":{},"E_total":len(e_rows),"bare_ar_total":len(bare),"adjacent_nom_reader_records":len(pair_records),
      "adjacent_nom_manuscript_loci":len({r["locus"] for r in pair_records}),
      "fixed_consequence":SPEC["conditional_trace"],"whole_E_complete":False,"ZL_impossibility_proved":False,
      "new_word_values_or_grammar_repairs":0,"native_line_records":len(native),"native_alignment_units":len(align),
      "native_decision":SPEC["native_decision"],"source_correction":SPEC["source_correction"],
      "confirmed_words":0,"independent_confirmation_folios":0,
      "claim_ceiling":"Literal census and fixed conditional construction only; no significance or selected meaning."
    }
    for edition in ("ZL3b","IT2a","RF1b"):
        erows=[r for r in e_rows if r["edition"]==edition]
        br=[r for r in bare if r["edition"]==edition]
        pp=[r for r in pair_records if r["edition"]==edition]
        expected_result["counts"][edition]={"E_groups":len(erows),"E_types":len({r["ivtff_group_raw"] for r in erows}),
            "inherited_assigned":cov[edition],"unassigned":len(erows)-cov[edition],"bare_ar":len(br),"adjacent_nom_pairs":len(pp)}
    result=json.loads((EXP/"artifacts/RESULT.json").read_text(encoding="utf-8"))
    ck(result==expected_result,"RESULT differs from independent census and fixed symbolic check")

    if errors:
        print("FAIL")
        for x in errors: print("- "+x)
        return 1
    print("PASS: registration/input hashes; unchanged 24 S and 6 E parent values; all 81 E groups with 8/7/7 inheritance; all 16 exact bare ar contexts with 4/6/6 counts; exact empty ZL and two IT/RF adjacent ar pairs and boundaries; fixed ProcessFrame→FacultySpec then second-domain mismatch; 44 native groups and 13 alignment units with each source group exactly once; RESULT.")
    print("Ceiling: literal census and conditional application under the exact two fixed rules. Not a full E parse, proof of whole-E impossibility, independent visual/meaning confirmation, or selected target meaning.")
    return 0

if __name__=="__main__":
    sys.exit(main())

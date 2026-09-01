#!/usr/bin/env python3
"""Independent validator for GDT730/V99R4."""
from __future__ import annotations
import csv, hashlib, json, re, sys
from collections import Counter
from pathlib import Path
sys.dont_write_bytecode = True

def root(p: Path) -> Path:
    for q in (p, *p.parents):
        if (q/"AGENTS.md").is_file() and (q/".git").exists(): return q
    raise RuntimeError("repository root not found")

ROOT=root(Path(__file__).resolve()); EXP=ROOT/"experiments/yolo/gdt730_v99r4_ninety_four_ambiguity_default_dispatch"
SRC=EXP/"src"; ART=EXP/"artifacts"
G727=ROOT/"experiments/yolo/gdt727_v99_six_meaning_debt_dispatch/artifacts"
G729=ROOT/"experiments/yolo/gdt729_v99r3_fourteen_indexed_quantity_dispatch"
BASE=G729/"artifacts/V99R3_COMPLETE_WORD_CONFIDENCE.tsv"
CURRENT=ART/"V99R4_COMPLETE_WORD_CONFIDENCE.tsv"
SURFACES=("ain","alkal","an","chcth","chcthy","chdal","chdaly","chedal","cheecthy","chocthy","choror","cth","cthal","cthar","ctharal","cthey","cthoiin","cthol","ctholy","cthom","cthor","cthory","daiil","dail","daldy","daly","dara","fshor","kol","laiin","lam","lchdy","lcheo","lchol","lolchedy","oaiin","oaiir","octhey","octhy","odal","okshor","paiin","paiir","pam","pchdy","pcheo","pchol","polchedy","pshedy","qodal","raiir","rchdy","rcheey","rcheo","rchey","rchol","rchy","roaiin","rodaiin","rody","roiin","rolchedy","saii","saiim","saiin","saiir","saim","sam","schdy","schedy","scheey","scheo","schey","schol","schy","shcthy","shecthy","shocthy","soaiin","sodaiin","sodal","sody","soiin","sol","sshedy","tchcthy","ychoy","yckhey","ycthar","ydy","ykchy","ykeedy","ysheey","ytal")
IDS=tuple(x+"#GLOBAL" for x in SURFACES); FP="cphol#GLOBAL"
PARITY=("V99_324_ACTIVE_LEXICAL_READINGS.tsv","V99_479_CONTEXT_REALIZATIONS.tsv","V99_471_PRACTICAL_RENDERED_UNITS.tsv","V99_51_PRACTICAL_LINE_READER.tsv","GDT727_V99_51_LINE_WORKING_READER.md")
ALLOWED={"working_meaning_de","source_gdts","relation_word_delta","v99_context_realizations_de","v99_audit_decision","v99_evidence_class","v99_open_semantic_slots","v99_lineage_class","v99_value_kind"}
PRESERVED=("surface","reading_id","current_layer","semantic_scope","semantic_applicability","form_level","occurrence_count","page_count","locus_count","working_model_score_0_100_not_probability","working_model_level","positive_evidence_de","counterevidence_de","historical_confirmation","historical_analogue","global_export_scope","bound_span_ids","unconditional_global_export_allowed","source_reading_ids","v99_component_global_export_allowed","v99_exact_whole_surface_default_allowed","v99_structural_tag","v99_action_default_allowed")

def tsv(p):
    with p.open(encoding="utf-8",newline="") as f:return list(csv.DictReader(f,delimiter="\t"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rsha(r):return hashlib.sha256(json.dumps(r,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def val(r,*ks):
    for k in ks:
        if k in r:return r[k]
    raise AssertionError(f"missing columns {ks}")
def technical(s):return "/" in s or re.search(r"\soder\s",s,re.I) is not None or "menge" in s.lower()
def ambiguous(s):
    # Avoid the known false friend zusamMENGEsetzt, but reject real quantity wording.
    s2=re.sub("zusammengesetzt","",s,flags=re.I)
    return "/" in s or re.search(r"\boder\b",s,re.I) is not None or "menge" in s2.lower()
def append_source(s,addition):
    values=[]
    for x in [*s.split("|"),addition]:
        if x and x not in {"0","NONE"} and x not in values:values.append(x)
    return "|".join(values) if values else "NONE"

def main():
    old=tsv(BASE); new=tsv(CURRENT); specs=tsv(SRC/"V99R4_94_AMBIGUITY_DEFAULT_SPECS.tsv")
    assert len(IDS)==len(set(IDS))==len(specs)==94
    assert tuple(val(x,"reading_id","source_reading_id") for x in specs)==IDS
    assert tuple(x["surface"] for x in specs)==SURFACES
    O={x["reading_id"]:x for x in old}; N={x["reading_id"]:x for x in new}; S={val(x,"reading_id","source_reading_id"):x for x in specs}
    assert len(old)==len(new)==1586 and list(old[0])==list(new[0])
    assert [(x["surface"],x["reading_id"]) for x in old]==[(x["surface"],x["reading_id"]) for x in new]
    glob=[x for x in old if x["current_layer"]=="GLOBAL_V48_DEFAULT"]
    tech={x["reading_id"] for x in glob if technical(x["working_meaning_de"])}
    sem={x["reading_id"] for x in glob if ambiguous(x["working_meaning_de"])}
    assert tech==set(IDS)|{FP} and len(tech)==95 and sum(int(O[x]["occurrence_count"]) for x in tech)==1050
    assert sem==set(IDS) and sum(int(O[x]["occurrence_count"]) for x in IDS)==1039
    active=other=0
    for a,b in zip(old,new,strict=True):
        rid=a["reading_id"]; changes={k for k in a if a[k]!=b[k]}
        if rid in S:
            sp=S[rid]; expected=val(sp,"expected_old_meaning_de","old_meaning_de"); replacement=val(sp,"new_meaning_de","v99r4_meaning_de")
            assert a["working_meaning_de"]==expected and changes==ALLOWED,(rid,changes)
            assert b["working_meaning_de"]==b["v99_context_realizations_de"]==replacement and replacement!=expected and not ambiguous(replacement)
            assert b["source_gdts"]==append_source(a["source_gdts"],"GDT730")
            assert b["relation_word_delta"]=="0_GDT696_TO_GDT730"
            assert b["v99_open_semantic_slots"]==sp["strongest_rival_de"]
            assert b["v99_value_kind"]==sp["family"]
            assert b["v99_audit_decision"]==f"GDT730_{sp['family']}_SINGLE_DEFAULT_DISPATCH"
            assert b["v99_evidence_class"]=="INHERITED_WHOLE_AMBIGUITY_DEFAULT_DISPATCH"
            assert b["v99_lineage_class"]=="INHERITED_GLOBAL_V48__GDT730_SINGLE_DEFAULT_DISPATCH"
            if "component_export_credit" in sp:assert sp["component_export_credit"]=="0"
        else:
            assert not changes,(rid,changes)
            active+=a["current_layer"]=="ACTIVE_V99_LEXICAL_CORE"
            other+=a["current_layer"]=="GLOBAL_V48_DEFAULT"
        for k in PRESERVED:assert a[k]==b[k],(rid,k)
        assert b["positive_evidence_de"] and b["counterevidence_de"]
        assert 0<=int(b["working_model_score_0_100_not_probability"])<=100
    assert active==324 and other==1168 and N[FP]==O[FP]
    assert Counter(x["current_layer"] for x in new)==Counter({"GLOBAL_V48_DEFAULT":1262,"ACTIVE_V99_LEXICAL_CORE":324})
    assert Counter(x["working_model_level"] for x in old)==Counter(x["working_model_level"] for x in new)
    prior={x["reading_id"] for x in tsv(G729/"src/V99R3_14_QUANTITY_DISPATCH_SPECS.tsv")}
    assert len(prior)==14 and not prior&set(IDS) and all(N[x]==O[x] for x in prior)
    for rid in ("rodaiin#GLOBAL","sodaiin#GLOBAL"):
        assert N[rid]["working_meaning_de"].startswith("drei Portionen")
        assert all(N[rid][k]==O[rid][k] for k in PRESERVED)

    audit=tsv(ART/"V99R4_94_AMBIGUITY_DEFAULT_AUDIT.tsv"); summary=tsv(ART/"V99R4_FAMILY_SUMMARY.tsv")
    fp=tsv(ART/"V99R4_SELECTOR_FALSE_POSITIVE_AUDIT.tsv"); evidence=tsv(ART/"V99R4_EVIDENCE_BINDINGS.tsv")
    parity=tsv(ART/"V99R4_ACTIVE_READER_PARITY.tsv")
    assert len(audit)==94 and [val(x,"reading_id","source_reading_id") for x in audit]==list(IDS)
    assert sum(int(val(x,"occurrence_count","observed_occurrence_count")) for x in audit)==1039
    for x in audit:
        rid=val(x,"reading_id","source_reading_id")
        if "base_row_sha256" in x:assert x["base_row_sha256"]==rsha(O[rid])
        if "new_row_sha256" in x:assert x["new_row_sha256"]==rsha(N[rid])
        if "changed_fields" in x:assert set(x["changed_fields"].split("|"))==ALLOWED
        if "component_export_credit" in x:assert x["component_export_credit"]=="0"
    expected_groups=Counter(x["family"] for x in audit)
    assert len(summary)==len(expected_groups)==8 and {x["family"]:int(x["target_rows"]) for x in summary}==dict(expected_groups)
    assert sum(int(val(x,"target_rows","rows")) for x in summary)==94
    assert sum(int(val(x,"summed_occurrence_count","occurrences")) for x in summary)==1039
    assert all(x["all_component_export_credit_zero"]=="1" and x["all_historical_confirmation_h0_none"]=="1" for x in summary)
    assert len(fp)==95 and Counter(x["classification"] for x in fp)==Counter({"TRUE_AMBIGUITY_TARGET":94,"LEXICAL_FALSE_POSITIVE":1})
    false_rows=[x for x in fp if x["classification"]=="LEXICAL_FALSE_POSITIVE"]
    assert len(false_rows)==1 and false_rows[0]["reading_id"]==FP and false_rows[0]["dispatch_allowed"]=="0"
    assert {x["reading_id"] for x in fp if x["classification"]=="TRUE_AMBIGUITY_TARGET"}==set(IDS)
    assert len(evidence)==94 and [x["reading_id"] for x in evidence]==list(IDS)
    bundle_keys=("working_model_score_0_100_not_probability","working_model_level",
      "positive_evidence_de","counterevidence_de","historical_confirmation",
      "historical_analogue","semantic_scope","global_export_scope",
      "unconditional_global_export_allowed","v99_component_global_export_allowed",
      "bound_span_ids","source_reading_ids","v99_structural_tag",
      "v99_action_default_allowed")
    for x in evidence:
        rid=x["reading_id"]; bundle={k:O[rid][k] for k in bundle_keys}
        assert x["bundle_sha256"]==hashlib.sha256(json.dumps(bundle,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
        assert x["all_preserved"]=="1" and x["component_relation_credit"]=="0"
    historical_copies=(
        (ART/"HISTORICAL_COMPOSITION_COMPARATORS.tsv",ROOT/"experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/HISTORICAL_COMPOSITION_COMPARATORS.tsv"),
        (ART/"HISTORICAL_HYBRID_COMPARATORS.tsv",ROOT/"experiments/yolo/gdt632_cth_interfix_lattice/artifacts/HISTORICAL_HYBRID_COMPARATORS.tsv"),
        (ART/"HISTORICAL_QUANTITY_COMPARATORS.tsv",ROOT/"experiments/yolo/gdt729_v99r3_fourteen_indexed_quantity_dispatch/artifacts/HISTORICAL_QUANTITY_COMPARATORS.tsv"),
    )
    for copied,source in historical_copies:
        assert copied.read_bytes()==source.read_bytes()
        assert tsv(copied)
    quantity_rows=tsv(historical_copies[2][0])
    assert all(x["voynich_relation_credit"]=="0" and x["historical_confirmation"]=="H0_NONE" for x in quantity_rows)
    assert len(parity)==5
    for name,x in zip(PARITY,parity,strict=True):
        assert val(x,"artifact","source_artifact").endswith(name) and val(x,"sha256","source_sha256")==sha(G727/name)
        if "parity_status" in x:assert x["parity_status"]=="BYTE_STABLE_INPUT_NOT_REWRITTEN"

    result=json.loads((ART/"RESULT.json").read_text())
    assert result["target_rows"]==94 and result["target_summed_occurrences"]==1039
    assert result["technical_selector_rows"]==95 and result["technical_selector_summed_occurrences"]==1050
    assert result["lexical_false_positive_rows"]==1 and result["lexical_false_positive_occurrences"]==11
    assert result["active_v99_rows_byte_stable"]==324
    assert result["non_target_global_rows_byte_stable"]==1168
    assert set(result["changed_fields"])==ALLOWED
    assert result["target_main_meanings_ambiguity_free"]==result["target_context_meanings_ambiguity_free"]==94
    assert result["historical_comparator_artifacts"]==3 and result["historical_comparator_relation_credit"]==0
    assert result["score_changes"]==result["confidence_level_changes"]==result["evidence_changes"]==0
    assert result["scope_changes"]==result["export_changes"]==result["component_relation_credit"]==0
    expected_outputs={"README.md","V99R4_COMPLETE_WORD_CONFIDENCE.tsv","V99R4_94_AMBIGUITY_DEFAULT_AUDIT.tsv","V99R4_FAMILY_SUMMARY.tsv","V99R4_SELECTOR_FALSE_POSITIVE_AUDIT.tsv","V99R4_ACTIVE_READER_PARITY.tsv","V99R4_EVIDENCE_BINDINGS.tsv","HISTORICAL_COMPOSITION_COMPARATORS.tsv","HISTORICAL_HYBRID_COMPARATORS.tsv","HISTORICAL_QUANTITY_COMPARATORS.tsv","RESULT.json"}
    assert {p.name for p in ART.iterdir() if p.is_file() and p.name!="VALIDATION.json"}==expected_outputs
    outputs=sorted(ART/name for name in expected_outputs)
    out={"experiment_id":"GDT730","status":"PASS","result_status":result["status"],"target_rows":94,"target_occurrences":1039,"technical_selector_rows":95,"technical_selector_occurrences":1050,"false_positive_control":FP,"active_rows_byte_stable":324,"non_target_global_rows_byte_stable":1168,"prior_gdt729_targets_byte_stable":14,"active_reader_artifacts_byte_stable":5,"score_evidence_scope_export_changes":0,"component_relation_credit":0,"validated_output_sha256":{str(p.relative_to(ROOT)):sha(p) for p in outputs}}
    payload=json.dumps(out,ensure_ascii=False,indent=2)+"\n"; target=ART/"VALIDATION.json"
    if target.exists():assert target.read_text()==payload
    else:target.write_text(payload)
    print(json.dumps(out,ensure_ascii=False,sort_keys=True));return 0

if __name__=="__main__":raise SystemExit(main())

#!/usr/bin/env python3
"""Independent scope and preservation validator for GDT732."""
from __future__ import annotations
import csv,hashlib,json,re,sys
from collections import Counter
from pathlib import Path
sys.dont_write_bytecode=True

def repo(p):
    for q in (p,*p.parents):
        if (q/"AGENTS.md").is_file() and (q/".git").exists():return q
    raise RuntimeError("repository root not found")
ROOT=repo(Path(__file__).resolve());EXP=ROOT/"experiments/yolo/gdt732_v99r5_grade_frame_spoken_renderer";ART=EXP/"artifacts"
G671=ROOT/"experiments/yolo/gdt671_fifteen_residual_family_completion/artifacts";G696=ROOT/"experiments/yolo/gdt696_v68_exact_local_object_carries/artifacts";G727=ROOT/"experiments/yolo/gdt727_v99_six_meaning_debt_dispatch/artifacts";G730=ROOT/"experiments/yolo/gdt730_v99r4_ninety_four_ambiguity_default_dispatch/artifacts"
BASE=G730/"V99R4_COMPLETE_WORD_CONFIDENCE.tsv";GRADE=re.compile(r"(?:Grades|Gradanfang|Gradmitte|Gradende)",re.I)
STAGE=re.compile(r"am Anfang des Grades|in der Mitte des Grades|am Ende des Grades|am Gradanfang|in der Gradmitte|am Gradende|Gradanfang|Gradmitte|Gradende",re.I)
MODS={"HEISS":re.compile(r"heiß",re.I),"KALT":re.compile(r"kalt",re.I),"TROCKEN":re.compile(r"trocken",re.I),"FEUCHT":re.compile(r"feucht",re.I)}
OUTMOD={"HEISS":re.compile(r"heiß|erhitz",re.I),"KALT":re.compile(r"kalt|abgekühl",re.I),"TROCKEN":re.compile(r"trocken|getrockn",re.I),"FEUCHT":re.compile(r"feucht|angefeucht",re.I)}
EXTRA=("v99r5_spoken_render_de","v99r5_formal_stage_sequence","v99r5_workflow_closure","v99r5_modality_class","v99r5_renderer_mode","v99r5_dispatch_scope","v99r5_policy_rule_ids")
STATUS=("PASS_175_GRADE_READINGS_2431_LICENSED_POSITIONS__162_GLOBAL_2401_PLUS_13_ACTIVE_30__1784_TARGET_ACTIVE_SURFACE_LEAK_CONTROLS__75_DIRECT_ROWS_1748_POSITIONS__100_NEUTRAL_ROWS_683_POSITIONS__ZERO_TARGET_GRADE_FRAMES__4752_V48_BASELINE_RESIDUALS_4692_ACTIVE_OUTSIDE_EXACT_PLUS_52_SUPERSEDED_EXACT_PLUS_8_ALIAS_MERGE__V99R4_SEMANTIC_DICTIONARY_BYTE_STABLE__NO_NEW_PAGE")

def tsv(p):
    with p.open(encoding="utf-8",newline="") as f:return list(csv.DictReader(f,delimiter="\t"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rsha(r):return hashlib.sha256(json.dumps(r,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def modalities(s,patterns):
    hits=[]
    for code,rx in patterns.items():hits += [(m.start(),code) for m in rx.finditer(s)]
    out=[]
    for _,code in sorted(hits):
        if code not in out:out.append(code)
    return out
def closure_counts(s):return (len(re.findall(r"(?<!\w)abgeschlossen(?!\w)",s,re.I)),len(re.findall(r"(?<!\w)fertig(?!\w)",s,re.I)))

def main():
    pages=[x["page"] for x in tsv(G671/"PAGE_ALLOWLIST.tsv")];lines=tsv(G671/"ALL_LINE_CONCRETE_COVERAGE_V48.tsv")
    assert len(pages)==len(set(pages))==179 and not any(re.match(r"^f84(?:r|v|$)",x) for x in pages)
    assert len(lines)==4128 and sum(int(x["token_count"]) for x in lines)==32339 and {x["page"] for x in lines}<=set(pages)
    base=tsv(BASE);overlay=tsv(ART/"V99R5_COMPLETE_SPOKEN_RENDERER.tsv");audit=tsv(ART/"V99R5_175_GRADE_FRAME_READING_AUDIT.tsv")
    assert len(base)==len(overlay)==1586 and list(overlay[0])==list(base[0])+list(EXTRA)
    assert [x["reading_id"] for x in base]==[x["reading_id"] for x in overlay]
    for a,b in zip(base,overlay,strict=True):assert {k:b[k] for k in a}==a
    targets=[x for x in base if GRADE.search(x["working_meaning_de"])];assert len(targets)==175 and sum(int(x["occurrence_count"]) for x in targets)==2431
    assert Counter(x["current_layer"] for x in targets)==Counter({"GLOBAL_V48_DEFAULT":162,"ACTIVE_V99_LEXICAL_CORE":13})
    assert sum(int(x["occurrence_count"]) for x in targets if x["current_layer"]=="GLOBAL_V48_DEFAULT")==2401
    assert sum(int(x["occurrence_count"]) for x in targets if x["current_layer"]=="ACTIVE_V99_LEXICAL_CORE")==30
    B={x["reading_id"]:x for x in base};O={x["reading_id"]:x for x in overlay};assert len(audit)==175
    for i,row in enumerate(audit,1):
        old=B[row["reading_id"]];new=O[row["reading_id"]]["v99r5_spoken_render_de"]
        assert row["audit_id"]==f"G732-R{i:03d}" and row["surface"]==old["surface"] and row["source_row_sha256"]==rsha(old)
        assert row["old_working_meaning_de"]==old["working_meaning_de"] and row["new_spoken_render_de"]==new and not GRADE.search(new)
        assert modalities(old["working_meaning_de"],MODS)==modalities(new,OUTMOD)
        assert closure_counts(old["working_meaning_de"])==closure_counts(new)
        assert row["working_model_score_0_100_not_probability"]==old["working_model_score_0_100_not_probability"] and row["working_model_level"]==old["working_model_level"]
        assert row["positive_evidence_de"]==old["positive_evidence_de"] and row["counterevidence_de"]==old["counterevidence_de"]
        assert row["semantic_scope"]==old["semantic_scope"] and row["global_export_scope"]==old["global_export_scope"] and row["historical_confirmation"]==old["historical_confirmation"]=="H0_NONE" and row["component_relation_credit"]=="0"
    modes=Counter(x["renderer_mode"] for x in audit);modeocc=Counter()
    for x in audit:modeocc[x["renderer_mode"]]+=int(x["occurrence_count"])
    assert modes==Counter({"MIXED_NEUTRAL_STAGE":82,"SINGLE_DIRECT":71,"SINGLE_COMPOSITE_NEUTRAL_STAGE":9,"NO_MODALITY_NEUTRAL_STAGE":9,"CLAUSE_LOCAL_MULTI_STAGE":4})
    assert modeocc==Counter({"MIXED_NEUTRAL_STAGE":604,"SINGLE_DIRECT":1710,"SINGLE_COMPOSITE_NEUTRAL_STAGE":21,"NO_MODALITY_NEUTRAL_STAGE":58,"CLAUSE_LOCAL_MULTI_STAGE":38})
    assert sum(modes[x] for x in ("SINGLE_DIRECT","CLAUSE_LOCAL_MULTI_STAGE"))==75 and sum(modeocc[x] for x in ("SINGLE_DIRECT","CLAUSE_LOCAL_MULTI_STAGE"))==1748

    contexts=tsv(G727/"V99_479_CONTEXT_REALIZATIONS.tsv");active_ids={x["reading_id"] for x in targets if x["current_layer"]=="ACTIVE_V99_LEXICAL_CORE"};active={}
    for x in contexts:
        if x["v99_reading_id"] in active_ids:
            key=(x["page"],x["locus"],int(x["token_ordinal"]),x["surface"]);assert key not in active;active[key]=x
    assert len(active)==30
    globals_={x["surface"]:x for x in targets if x["current_layer"]=="GLOBAL_V48_DEFAULT"};active_surfaces={x["surface"] for x in targets if x["current_layer"]=="ACTIVE_V99_LEXICAL_CORE"};assert len(globals_)==162 and not set(globals_)&active_surfaces
    expected=[];controls=[];global_counts=Counter();seen=set()
    for line in lines:
        tokens=line["zl3b_line"].split();glosses=line["token_glosses_de"].split(" | ");assert len(tokens)==len(glosses)==int(line["token_count"])
        for ordinal,(surface,gloss) in enumerate(zip(tokens,glosses,strict=True),1):
            key=(line["page"],line["locus"],ordinal,surface)
            if surface in globals_:rid=globals_[surface]["reading_id"];scope="GLOBAL_SURFACE";position="NONE";global_counts[rid]+=1
            elif key in active:rid=active[key]["v99_reading_id"];scope="ACTIVE_EXACT_POSITION";position=active[key]["position_id"];seen.add(key)
            elif surface in active_surfaces:controls.append(key);continue
            else:continue
            expected.append((key,rid,scope,position,gloss))
    assert len(expected)==2431 and len(seen)==30 and len(controls)==1784
    assert all(global_counts[x["reading_id"]]==int(x["occurrence_count"]) for x in targets if x["current_layer"]=="GLOBAL_V48_DEFAULT")
    occ=tsv(ART/"V99R5_2431_LICENSED_POSITION_OVERLAY.tsv");assert len(occ)==2431
    for row,(key,rid,scope,position,gloss) in zip(occ,expected,strict=True):
        assert (row["page"],row["locus"],int(row["token_ordinal"]),row["surface"])==key and row["reading_id"]==rid and row["dispatch_scope"]==scope and row["active_position_id"]==position
        assert row["inherited_v48_gloss_de"]==gloss and row["token_retained"]==row["ordinal_retained"]=="1" and row["component_relation_credit"]=="0"
        assert not GRADE.search(row["new_v99r5_spoken_render_de"]);assert closure_counts(row["old_v99r4_meaning_de"])==closure_counts(row["new_v99r5_spoken_render_de"])
        assert modalities(row["old_v99r4_meaning_de"],MODS)==modalities(row["new_v99r5_spoken_render_de"],OUTMOD)
    ctl=tsv(ART/"V99R5_1784_ACTIVE_SURFACE_SCOPE_CONTROLS.tsv");assert len(ctl)==1784
    assert [(x["page"],x["locus"],int(x["token_ordinal"]),x["surface"]) for x in ctl]==controls
    assert all(x["licensed_target"]=="0" and x["unchanged_in_overlay"]=="1" for x in ctl)

    comparisons=tsv(ART/"V99R5_1661_AFFECTED_LINE_COMPARISON.tsv");assert len(comparisons)==1661
    changed_lines={(x["page"],x["locus"]) for x in comparisons};assert sum(int(x["target_count"]) for x in comparisons)==2431
    residual=tsv(ART/"V99R5_4752_RESIDUAL_CACHE_GRADE_FRAME_CELLS.tsv");assert len(residual)==4752
    classes=Counter(x["residual_class"] for x in residual)
    assert classes==Counter({"TARGET_ACTIVE_SURFACE_OUTSIDE_30_EXACT_POSITIONS":1784,"OTHER_ACTIVE_SURFACE_OUTSIDE_EXACT_SCOPE":2908,"OTHER_ACTIVE_EXACT_POSITION_WITH_SUPERSEDED_V48_CELL":52,"LEGACY_CONTEXTUAL_ALIAS_OR_MERGE":8})
    affected=[x for x in residual if x["line_changed_by_gdt732"]=="1"]
    assert len(affected)==2494 and Counter(x["residual_class"] for x in affected)==Counter({"TARGET_ACTIVE_SURFACE_OUTSIDE_30_EXACT_POSITIONS":932,"OTHER_ACTIVE_SURFACE_OUTSIDE_EXACT_SCOPE":1538,"OTHER_ACTIVE_EXACT_POSITION_WITH_SUPERSEDED_V48_CELL":18,"LEGACY_CONTEXTUAL_ALIAS_OR_MERGE":6})
    assert all(GRADE.search(x["residual_gloss_de"]) and x["gdt732_rewrite_allowed"]=="0" for x in residual)
    active_all={x["surface"] for x in base if x["current_layer"]=="ACTIVE_V99_LEXICAL_CORE"}
    all_contexts={(x["page"],x["locus"],int(x["token_ordinal"]),x["surface"]):x for x in contexts};assert len(all_contexts)==479
    control_keys=set(controls);residual_keys=set()
    for x in residual:
        key=(x["page"],x["locus"],int(x["token_ordinal"]),x["surface"]);assert key not in residual_keys;residual_keys.add(key)
        expected_class=("TARGET_ACTIVE_SURFACE_OUTSIDE_30_EXACT_POSITIONS" if key in control_keys else "OTHER_ACTIVE_EXACT_POSITION_WITH_SUPERSEDED_V48_CELL" if key in all_contexts else "OTHER_ACTIVE_SURFACE_OUTSIDE_EXACT_SCOPE" if x["surface"] in active_all else "LEGACY_CONTEXTUAL_ALIAS_OR_MERGE")
        assert x["residual_class"]==expected_class
        if expected_class=="OTHER_ACTIVE_EXACT_POSITION_WITH_SUPERSEDED_V48_CELL":
            context=all_contexts[key]
            assert x["current_v99_position_id"]==context["position_id"] and x["current_v99_reading_id"]==context["v99_reading_id"] and x["current_v99_context_realization_de"]==context["v99_context_realization_de"]
        else:assert x["current_v99_position_id"]==x["current_v99_reading_id"]==x["current_v99_context_realization_de"]=="NONE"
    aliases=[x for x in residual if x["residual_class"]=="LEGACY_CONTEXTUAL_ALIAS_OR_MERGE"]
    assert Counter(x["surface"] for x in aliases)==Counter({"o":6,"ch":1,"dom":1})
    superseded=[x for x in residual if x["residual_class"]=="OTHER_ACTIVE_EXACT_POSITION_WITH_SUPERSEDED_V48_CELL"]
    still_grade=[x for x in superseded if GRADE.search(x["current_v99_context_realization_de"])]
    assert len(superseded)==52 and len(still_grade)==1
    assert (still_grade[0]["page"],still_grade[0]["locus"],still_grade[0]["token_ordinal"],still_grade[0]["surface"])==("f104v","f104v.2","3","chockhy")
    by_locus={}
    for x in residual:by_locus.setdefault(x["locus"],[]).append(x)
    dense=tsv(ART/"V99R5_50_TARGET_DENSE_PASSAGES.tsv")
    expected_dense=sorted(comparisons,key=lambda x:(-int(x["target_count"]),-int(x["complete_v48"]),x["locus"]))[:50]
    assert len(dense)==50
    for rank,(row,source) in enumerate(zip(dense,expected_dense,strict=True),1):
        assert row["rank"]==str(rank) and all(row[k]==source[k] for k in source)
        items=by_locus.get(row["locus"],[])
        expected_text=" | ".join(f"{x['token_ordinal']}:{x['residual_gloss_de']} [{x['residual_class']}]"+(f" => aktuelles V99: {x['current_v99_context_realization_de']}" if x["current_v99_context_realization_de"]!="NONE" else "") for x in items) or "NONE"
        assert int(row["residual_grade_cell_count"])==len(items) and row["residual_grade_cells_de"]==expected_text
    reader=["# GDT732 — 50 gradrahmendichteste Cache-Passagen","","Diese Rangliste misst nur die Zahl positionsgenau geänderter Gradrahmen. Sie ist keine Rangliste semantischer Wichtigkeit und keine Klartextübersetzung.","","Nur die 2.431 lizenzierten Zielpositionen werden geändert. Noch hörbare Gradformulierungen in der vollständigen Nachher-Zeile sind bewusst geschützte oder anderweitig geerbte V48-Zellen; GDT732 zählt sie separat.",""]
    for row in dense:
        reader += [f"## {row['rank']}. {row['locus']} ({row['target_count']} Gradrahmen)","",f"Voynich: `{row['zl3b_line']}`","",f"Formal: {row['formal_grade_tags']}","",f"Zielzellen vorher: {row['v99r4_target_glosses_de']}","",f"Zielzellen nachher: {row['v99r5_spoken_target_glosses_de']}","",f"Außerhalb des GDT732-Zielbereichs verbliebene Gradrahmen: {row['residual_grade_cells_de']}","",f"Vorher: {row['v99r4_render_de']}","",f"Nachher: {row['v99r5_spoken_render_de']}",""]
    assert (ART/"GDT732_V99R5_50_TARGET_DENSE_READER.md").read_text(encoding="utf-8")=="\n".join(reader).rstrip()+"\n"
    parity=tsv(ART/"V99R5_INHERITED_ARTIFACT_PARITY.tsv")
    paths=[G696/"V69_51_LINE_RELATION_OVERLAY.tsv",G696/"V69_479_TOKEN_RELATION_OVERLAY.tsv",G696/"GDT696_V69_LOCAL_OBJECT_CARRY_READER.md",G727/"V99_324_ACTIVE_LEXICAL_READINGS.tsv",G727/"V99_479_CONTEXT_REALIZATIONS.tsv",G727/"V99_471_PRACTICAL_RENDERED_UNITS.tsv",G727/"V99_51_PRACTICAL_LINE_READER.tsv",G727/"GDT727_V99_51_LINE_WORKING_READER.md"]
    assert len(parity)==len(paths)==8
    for row,path in zip(parity,paths,strict=True):assert row["source_artifact"]==str(path.relative_to(ROOT)) and row["sha256"]==sha(path) and row["gdt732_rewrite_count"]=="0" and row["parity_status"]=="BYTE_STABLE_INPUT_NOT_REWRITTEN"
    result=json.loads((ART/"RESULT.json").read_text());assert result["status"]==STATUS
    exact={"allowed_pages":179,"cached_lines":4128,"aligned_tokens":32339,"complete_dictionary_rows":1586,"target_reading_rows":175,"global_target_rows":162,"global_licensed_positions":2401,"active_target_rows":13,"active_licensed_positions":30,"active_surface_raw_positions":1814,"active_surface_scope_controls":1784,"licensed_target_positions":2431,"affected_lines":1661,"direct_spoken_rows":75,"direct_spoken_positions":1748,"neutral_stage_rows":100,"neutral_stage_positions":683,"target_audible_grade_frame_rows_after":0,"target_audible_grade_frame_occurrences_after":0,"residual_cache_grade_frame_cells_after":4752,"residual_affected_passage_grade_frame_cells_after":2494,"residual_target_active_surface_control_grade_cells":1784,"residual_other_active_surface_grade_cells":2908,"residual_other_active_superseded_exact_v48_grade_cells":52,"residual_legacy_alias_merge_grade_cells":8,"residual_affected_target_active_surface_control_grade_cells":932,"residual_affected_other_active_surface_grade_cells":1538,"residual_affected_other_active_superseded_exact_v48_grade_cells":18,"residual_affected_legacy_alias_merge_grade_cells":6,"workflow_closure_additions":0,"modality_additions":0,"action_default_changes":0,"score_changes":0,"confidence_changes":0,"evidence_changes":0,"scope_changes":0,"export_changes":0,"component_relation_credit":0,"inherited_artifacts_byte_stable":8,"new_pages":0}
    assert all(result[k]==v for k,v in exact.items()) and result["semantic_dictionary_sha256"]==sha(BASE)
    files={"README.md","RESULT.json","V99R5_COMPLETE_SPOKEN_RENDERER.tsv","V99R5_175_GRADE_FRAME_READING_AUDIT.tsv","V99R5_2431_LICENSED_POSITION_OVERLAY.tsv","V99R5_1784_ACTIVE_SURFACE_SCOPE_CONTROLS.tsv","V99R5_4752_RESIDUAL_CACHE_GRADE_FRAME_CELLS.tsv","V99R5_1661_AFFECTED_LINE_COMPARISON.tsv","V99R5_50_TARGET_DENSE_PASSAGES.tsv","V99R5_RENDERER_CLASS_SUMMARY.tsv","V99R5_BLOCKER_DELTA.tsv","V99R5_RENDER_QUALITY_SUMMARY.tsv","V99R5_INHERITED_ARTIFACT_PARITY.tsv","GDT732_V99R5_50_TARGET_DENSE_READER.md"}
    assert {x.name for x in ART.iterdir() if x.is_file() and x.name!="VALIDATION.json"}==files
    validation={"experiment_id":"GDT732","status":"PASS","result_status":STATUS,"target_reading_rows":175,"licensed_target_positions":2431,"global_rows_positions":[162,2401],"active_rows_positions":[13,30],"active_surface_scope_controls":1784,"direct_rows_positions":[75,1748],"neutral_rows_positions":[100,683],"target_grade_markers_after":0,"residual_cache_grade_cells":{"total":4752,"target_active_controls":1784,"other_active_scope":2908,"superseded_exact_v48":52,"legacy_alias_merge":8},"residual_affected_grade_cells":{"total":2494,"target_active_controls":932,"other_active_scope":1538,"superseded_exact_v48":18,"legacy_alias_merge":6},"superseded_exact_current_contexts_without_grade":51,"superseded_exact_current_contexts_with_grade":1,"semantic_dictionary_sha256":sha(BASE),"inherited_artifacts_byte_stable":8,"validated_output_sha256":{str((ART/x).relative_to(ROOT)):sha(ART/x) for x in sorted(files)}}
    payload=json.dumps(validation,ensure_ascii=False,indent=2)+"\n";target=ART/"VALIDATION.json"
    if target.exists():assert target.read_text()==payload
    else:target.write_text(payload)
    print(json.dumps(validation,ensure_ascii=False,sort_keys=True));return 0
if __name__=="__main__":raise SystemExit(main())

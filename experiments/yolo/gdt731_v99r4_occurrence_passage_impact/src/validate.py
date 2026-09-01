#!/usr/bin/env python3
"""Independent replay validator for GDT731's cached passage projection."""
from __future__ import annotations
import csv, hashlib, json, re, sys
from collections import Counter
from pathlib import Path
sys.dont_write_bytecode=True

def repo(p):
    for q in (p,*p.parents):
        if (q/"AGENTS.md").is_file() and (q/".git").exists():return q
    raise RuntimeError("repository root not found")
ROOT=repo(Path(__file__).resolve()); EXP=ROOT/"experiments/yolo/gdt731_v99r4_occurrence_passage_impact"; SRC=EXP/"src"; ART=EXP/"artifacts"
G671=ROOT/"experiments/yolo/gdt671_fifteen_residual_family_completion/artifacts"
G696=ROOT/"experiments/yolo/gdt696_v68_exact_local_object_carries/artifacts"
G729=ROOT/"experiments/yolo/gdt729_v99r3_fourteen_indexed_quantity_dispatch/artifacts"
G730=ROOT/"experiments/yolo/gdt730_v99r4_ninety_four_ambiguity_default_dispatch"
STATUS=("PASS_94_SURFACES_1039_POSITIONS_911_LINES__351_COMPLETE_LINES__50_TARGET_DENSE_"
        "PASSAGES__GDT696_OVERLAYS_BYTE_STABLE__CACHED_DEFAULT_IMPACT_ONLY__NO_POLISHED_"
        "TRANSLATION_OR_NEW_PAGE")
NAMES=("V99R3_V99R4_1039_OCCURRENCE_DELTA.tsv","V99R3_V99R4_911_LINE_RENDER_COMPARISON.tsv","V99R3_V99R4_351_COMPLETE_LINE_COMPARISON.tsv","V99R4_50_TARGET_DENSE_PASSAGES.tsv","V99R4_BLOCKER_CENSUS.tsv","V99R4_RENDER_QUALITY_SUMMARY.tsv","V99R4_GDT696_OVERLAY_PARITY.tsv","GDT731_V99R4_50_TARGET_DENSE_READER.md","RESULT.json")

def tsv(p):
    with p.open(encoding="utf-8",newline="") as f:return list(csv.DictReader(f,delimiter="\t"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def flags(s):return int("/" in s),int(re.search(r"(?i)(?<!\w)oder(?!\w)",s) is not None),int("menge" in s.casefold())
def practical(cells):
    cells=[re.sub(r"\s+"," ",x).strip(" ;") for x in cells]
    text="; ".join(cells);text=re.sub(r"\s+"," ",text).replace(".;",";").replace(":;",":")
    return re.sub(r";{2,}",";",text).strip()

def main():
    pages=[x["page"] for x in tsv(G671/"PAGE_ALLOWLIST.tsv")]
    assert len(pages)==len(set(pages))==179 and not any(re.match(r"^f84(?:r|v|$)",x) for x in pages)
    lines=tsv(G671/"ALL_LINE_CONCRETE_COVERAGE_V48.tsv")
    assert len(lines)==4128 and {x["page"] for x in lines}<=set(pages)
    assert sum(int(x["token_count"]) for x in lines)==32339
    old_rows=tsv(G729/"V99R3_COMPLETE_WORD_CONFIDENCE.tsv");new_rows=tsv(G730/"artifacts/V99R4_COMPLETE_WORD_CONFIDENCE.tsv");specs=tsv(G730/"src/V99R4_94_AMBIGUITY_DEFAULT_SPECS.tsv")
    old={x["surface"]:x for x in old_rows if x["current_layer"]=="GLOBAL_V48_DEFAULT"};new={x["surface"]:x for x in new_rows if x["current_layer"]=="GLOBAL_V48_DEFAULT"};spec={x["surface"]:x for x in specs}
    assert len(spec)==94 and set(spec)<=old.keys()&new.keys()
    for s,c in spec.items():
        assert old[s]["reading_id"]==new[s]["reading_id"]==c["reading_id"]
        assert old[s]["working_meaning_de"]==c["expected_old_meaning_de"]
        assert new[s]["working_meaning_de"]==new[s]["v99_context_realizations_de"]==c["new_meaning_de"]

    occ=[];comp=[];non=0
    surface_counts=Counter()
    for line in lines:
        tokens=line["zl3b_line"].split(); inherited=line["token_glosses_de"].split(" | ")
        assert len(tokens)==len(inherited)==int(line["token_count"])
        before=list(inherited);after=list(inherited);changed=[]
        for i,s in enumerate(tokens):
            if s not in spec:non+=1;continue
            c=spec[s];before[i]=old[s]["working_meaning_de"];after[i]=new[s]["working_meaning_de"]
            assert before[i]!=after[i];changed.append(i+1);surface_counts[s]+=1
            occ.append({"occurrence_id":f"G731-P{len(occ)+1:04d}","page":line["page"],"locus":line["locus"],"token_ordinal":str(i+1),"surface":s,"reading_id":c["reading_id"],"family":c["family"],"v99r3_meaning_de":before[i],"v99r4_meaning_de":after[i],"inherited_v48_gloss_de":inherited[i],"token_retained":"1","ordinal_retained":"1","strongest_rival_de":c["strongest_rival_de"],"source_evidence":c["source_evidence"],"working_model_score_0_100_not_probability":new[s]["working_model_score_0_100_not_probability"],"working_model_level":new[s]["working_model_level"],"positive_evidence_de":new[s]["positive_evidence_de"],"counterevidence_de":new[s]["counterevidence_de"],"semantic_scope":new[s]["semantic_scope"],"historical_confirmation":new[s]["historical_confirmation"],"component_relation_credit":"0"})
        if not changed:continue
        of=[sum(x) for x in zip(*(flags(before[i-1]) for i in changed))];nf=[sum(x) for x in zip(*(flags(after[i-1]) for i in changed))]
        comp.append({"page":line["page"],"locus":line["locus"],"section":line["section"],"language":line["language"],"hand":line["hand"],"token_count":line["token_count"],"unknown_tokens":line["unknown_tokens"],"complete_v48":str(int(line["unknown_tokens"]=="0")),"target_count":str(len(changed)),"target_ordinals":"|".join(map(str,changed)),"target_surfaces":"|".join(tokens[i-1] for i in changed),"zl3b_line":line["zl3b_line"],"v99r3_token_glosses_de":" | ".join(before),"v99r4_token_glosses_de":" | ".join(after),"v99r3_target_glosses_de":" | ".join(before[i-1] for i in changed),"v99r4_target_glosses_de":" | ".join(after[i-1] for i in changed),"v99r3_render_de":practical(before),"v99r4_render_de":practical(after),"old_slash_occurrences":str(of[0]),"new_slash_occurrences":str(nf[0]),"old_standalone_oder_occurrences":str(of[1]),"new_standalone_oder_occurrences":str(nf[1]),"old_casefold_menge_occurrences":str(of[2]),"new_casefold_menge_occurrences":str(nf[2]),"non_target_cells_unchanged":str(len(tokens)-len(changed)),"exact_tokens_and_ordinals_retained":"1"})
    assert len(occ)==1039 and len(comp)==911 and non==31300
    assert sum(surface_counts.values())==1039 and set(surface_counts)==set(spec)
    assert all(surface_counts[s]==int(new[s]["occurrence_count"]) for s in spec)
    complete=[x for x in comp if x["complete_v48"]=="1"]
    assert len(complete)==351 and sum(int(x["target_count"]) for x in complete)==409
    actual_occ=tsv(ART/NAMES[0]);actual_comp=tsv(ART/NAMES[1]);actual_complete=tsv(ART/NAMES[2])
    assert actual_occ==occ and actual_comp==comp and actual_complete==complete
    assert sum(int(x["non_target_cells_unchanged"]) for x in comp)==sum(int(x["token_count"])-int(x["target_count"]) for x in comp)
    assert all(x["token_retained"]==x["ordinal_retained"]=="1" for x in actual_occ)
    assert all(x["exact_tokens_and_ordinals_retained"]=="1" for x in actual_comp)
    for row in actual_occ:
        card=new[row["surface"]]
        assert row["working_model_score_0_100_not_probability"]==card["working_model_score_0_100_not_probability"]
        assert row["working_model_level"]==card["working_model_level"]
        assert row["positive_evidence_de"]==card["positive_evidence_de"] and row["counterevidence_de"]==card["counterevidence_de"]
        assert row["semantic_scope"]==card["semantic_scope"] and row["historical_confirmation"]==card["historical_confirmation"]=="H0_NONE"
        assert row["component_relation_credit"]=="0"
    for row in actual_comp:
        tokens=row["zl3b_line"].split();old_cells=row["v99r3_token_glosses_de"].split(" | ");new_cells=row["v99r4_token_glosses_de"].split(" | ")
        changed={int(x) for x in row["target_ordinals"].split("|")}
        assert len(tokens)==len(old_cells)==len(new_cells)==int(row["token_count"])
        assert sum(old_cells[i-1]==new_cells[i-1] for i in range(1,len(tokens)+1) if i not in changed)==int(row["non_target_cells_unchanged"])
        assert all(old_cells[i-1]!=new_cells[i-1] for i in changed)

    high=[{"rank":str(i),**x} for i,x in enumerate(sorted(comp,key=lambda x:(-int(x["target_count"]),-int(x["complete_v48"]),x["locus"]))[:50],1)]
    assert tsv(ART/NAMES[3])==high and [int(x["rank"]) for x in high]==list(range(1,51))
    md=["# GDT731 — 50 target-dense cached passages","","These are deterministic V99R3/V99R4 default projections, not polished translations or plaintext. The ranking measures changed target cells, not semantic importance.",""]
    for x in high:md += [f"## {x['rank']}. {x['locus']} ({x['target_count']} changes)","",f"Voynich: `{x['zl3b_line']}`","",f"Before: {x['v99r3_render_de']}","",f"After: {x['v99r4_render_de']}",""]
    assert (ART/NAMES[7]).read_text(encoding="utf-8")=="\n".join(md).rstrip()+"\n"

    oldmarks=tuple(sum(flags(x["v99r3_meaning_de"])[i] for x in occ) for i in range(3));newmarks=tuple(sum(flags(x["v99r4_meaning_de"])[i] for x in occ) for i in range(3))
    assert oldmarks==(823,76,251) and newmarks==(0,0,0)
    rules=tsv(SRC/"PRACTICAL_BLOCKER_RULES.tsv"); census=tsv(ART/NAMES[4]);assert len(census)==len(rules)
    passage_cells=[]
    for line in comp:
        tokens=line["zl3b_line"].split();cells=line["v99r4_token_glosses_de"].split(" | ")
        assert len(tokens)==len(cells)==int(line["token_count"])
        for i,(surface,cell) in enumerate(zip(tokens,cells,strict=True),1):
            status="UNKNOWN" if re.fullmatch(r"\[[^]]+:\?]",cell) else "RESOLVED"
            passage_cells.append((line["locus"],i,surface,cell,status))
    expected_census=[]
    for rule in rules:
        rx=re.compile(rule["regex"],re.I);scope=rule["field_scope"]
        assert scope in {"working_meaning_de","surface","passage_cell_status"}
        if scope=="working_meaning_de":ds=[x for x in new_rows if rx.search(x["working_meaning_de"])];ps=[x for x in passage_cells if rx.search(x[3])]
        elif scope=="surface":ds=[x for x in new_rows if rx.search(x["surface"])];ps=[x for x in passage_cells if rx.search(x[2])]
        else:ds=[];ps=[x for x in passage_cells if rx.search(x[4])]
        if scope!="passage_cell_status":
            assert len(ds)==int(rule["expected_dictionary_rows"]);assert sum(int(x["occurrence_count"]) for x in ds)==int(rule["expected_dictionary_occurrences"])
        expected_census.append({**rule,"matched_dictionary_rows":str(len(ds)),"matched_dictionary_occurrences":str(sum(int(x["occurrence_count"]) for x in ds)),"matched_affected_passage_cells":str(len(ps)),"matched_affected_passage_lines":str(len({x[0] for x in ps})),"sample_dictionary_surfaces":"|".join(x["surface"] for x in ds[:12]) or "NONE","sample_passage_loci":"|".join(dict.fromkeys(x[0] for x in ps[:12])) or "NONE","automatic_failure_triggered":str(int(rule["automatic_failure"]=="1" and bool(ps if scope=="passage_cell_status" else ds)))})
    assert census==expected_census

    quality=tsv(ART/NAMES[5]);Q={x["metric"]:x for x in quality};assert len(Q)==9
    exact={"target_surfaces":(94,94),"target_occurrences":(1039,1039),"affected_lines":(911,911),"affected_complete_v48_lines":(351,351),"slash_marker_occurrences":(823,0),"standalone_oder_occurrences":(76,0),"casefold_menge_occurrences":(251,0)}
    for k,(a,b) in exact.items():assert float(Q[k]["v99r3_before"])==a and float(Q[k]["v99r4_after"])==b and float(Q[k]["delta_after_minus_before"])==b-a
    assert Q["automatic_blocker_rules_triggered"]["v99r3_before"]=="NA"
    assert int(Q["automatic_blocker_rules_triggered"]["v99r4_after"])==sum(int(x["automatic_failure_triggered"]) for x in census)
    assert Q["automatic_blocker_rules_triggered"]["delta_after_minus_before"]=="NA"
    mb=sum(len(x["v99r3_meaning_de"].split()) for x in occ)/1039;ma=sum(len(x["v99r4_meaning_de"].split()) for x in occ)/1039
    assert float(Q["mean_target_words"]["v99r3_before"])==mb and float(Q["mean_target_words"]["v99r4_after"])==ma

    parity=tsv(ART/NAMES[6]);sources=((G696/"V69_51_LINE_RELATION_OVERLAY.tsv",51),(G696/"V69_479_TOKEN_RELATION_OVERLAY.tsv",479),(G696/"GDT696_V69_LOCAL_OBJECT_CARRY_READER.md",None));assert len(parity)==3
    for row,(p,count) in zip(parity,sources,strict=True):
        assert row["source_artifact"]==str(p.relative_to(ROOT)) and row["sha256"]==sha(p) and row["gdt731_rewrite_count"]=="0" and row["parity_status"]=="BYTE_STABLE_NOT_REWRITTEN"
        if count is not None:assert int(row["row_or_section_count"])==count
    result=json.loads((ART/"RESULT.json").read_text());assert result["status"]==STATUS
    expected={"allowed_pages":179,"cached_lines":4128,"aligned_tokens":32339,"target_surfaces":94,"target_positions":1039,"affected_lines":911,"affected_complete_v48_lines":351,"non_target_positions_unchanged":31300,"target_dense_passages":50,"old_slash_occurrences":823,"new_slash_occurrences":0,"old_standalone_oder_occurrences":76,"new_standalone_oder_occurrences":0,"old_casefold_menge_occurrences":251,"new_casefold_menge_occurrences":0,"blocker_rules":len(rules),"automatic_blocker_rules_triggered":sum(int(x["automatic_failure_triggered"]) for x in census),"gdt696_overlay_artifacts_byte_stable":3,"new_pages":0}
    assert all(result[k]==v for k,v in expected.items());assert result["mean_target_words_before"]==mb and result["mean_target_words_after"]==ma
    assert result["claim_ceiling"]=="cached whole-default impact; no polished translation or plaintext"
    expected_files={"README.md",*NAMES};assert {p.name for p in ART.iterdir() if p.is_file() and p.name!="VALIDATION.json"}==expected_files
    outputs=sorted(ART/x for x in expected_files)
    validation={"experiment_id":"GDT731","status":"PASS","result_status":STATUS,"allowed_pages":179,"cached_lines":4128,"aligned_tokens":32339,"target_surfaces":94,"target_positions":1039,"affected_lines":911,"affected_complete_v48_lines":351,"non_target_positions_unchanged":31300,"target_dense_passages":50,"ambiguity_marker_counts_before":{"slash":823,"standalone_oder":76,"casefold_menge":251},"ambiguity_marker_counts_after":{"slash":0,"standalone_oder":0,"casefold_menge":0},"gdt696_overlay_artifacts_byte_stable":3,"new_pages":0,"validated_output_sha256":{str(p.relative_to(ROOT)):sha(p) for p in outputs}}
    payload=json.dumps(validation,ensure_ascii=False,indent=2)+"\n";target=ART/"VALIDATION.json"
    if target.exists():assert target.read_text()==payload
    else:target.write_text(payload)
    print(json.dumps(validation,ensure_ascii=False,sort_keys=True));return 0
if __name__=="__main__":raise SystemExit(main())

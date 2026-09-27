#!/usr/bin/env python3
"""Independent literal/accounting replay for the frozen RAW572 partial.

Run from any directory with Python 3. The only target input is the owned,
meaning-neutral GDT1042 native_groups projection. This deliberately does not
import the author checker or parse mixed/sealed source files.
"""
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
PROJECTION = REPO / "experiments/yolo/gdt1042_f85r2_source_program_surface_census/artifacts/native_groups.tsv"
DRAFT = HERE / "PLANET_CHILD_AUTHOR_DRAFT.json"
READABLE_DRAFT = HERE / "PLANET_CHILD_AUTHOR_DRAFT.md"
AUTHOR_REPORT = HERE / "PLANET_CHILD_AUTHOR_REPORT.md"
CONTRACT = HERE / "PLANET_CHILD_AUTHOR_CONTRACT.md"
OUT = HERE / "PLANET_CHILD_REPLAY_B.json"
EXPECTED = {
    "projection": "e50307f834b04ff2ce17a97f14fd2c7b3f24b4818bc7fda3f57c372afc6b9d3c",
    "contract": "fc0092ad0792ea86aa26fdb24c3df3760a93425e8a17dda48cd63a5086f1e05f",
    "draft": "094bfbeef3d277a681e9650634cb8fdaa5183fa7e600a4a875a5687160565bed",
    "readable_draft": "1306e80676bf98767b64dbdc5fcd2d90009e9371155fb5ce756365323028718a",
    "author_report": "2ec5c28d41a9494e1c67ac8c3f0126553754b439f1501876fbbe16d9d53f81b0",
}
SOURCE_FIELDS = [
    "edition", "block", "locus", "source_group_id", "source_group_index",
    "source_group_count", "within_line_position", "paragraph_start",
    "paragraph_end", "left_separator", "right_separator", "ivtff_group_raw",
]
SELECTED_COUNTS = {"ZL3b": 108, "IT2a": 107, "RF1b": 109}


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def block_for(locus: str) -> str:
    n = int(locus.rsplit(".", 1)[1])
    if 2 <= n <= 6:
        return "N"
    if 7 <= n <= 11:
        return "E"
    if 12 <= n <= 17:
        return "S"
    if 18 <= n <= 23:
        return "W"
    return "OUTSIDE"


def main() -> None:
    hashes = {"projection": sha(PROJECTION), "contract": sha(CONTRACT), "draft": sha(DRAFT),
              "readable_draft": sha(READABLE_DRAFT), "author_report": sha(AUTHOR_REPORT)}
    with PROJECTION.open(newline="", encoding="utf-8") as f:
        source = list(csv.DictReader(f, delimiter="\t"))
    draft = json.loads(DRAFT.read_text(encoding="utf-8"))
    materialized = draft["all_occurrences"]
    checks: dict[str, object] = {}
    errors: list[str] = []

    checks["frozen_input_hashes_match"] = hashes == EXPECTED
    if hashes != EXPECTED:
        errors.append(f"input hash mismatch: {hashes}")
    checks["projection_rows"] = len(source)
    checks["draft_occurrence_rows"] = len(materialized)
    if len(source) != 473 or len(materialized) != 473:
        errors.append("expected exactly 473 projected and retained rows")

    source_by_id = {r["source_group_id"]: r for r in source}
    draft_by_id = {r["source_group_id"]: r for r in materialized}
    checks["unique_source_ids"] = len(source_by_id) == len(source)
    checks["unique_draft_ids"] = len(draft_by_id) == len(materialized)
    if len(source_by_id) != len(source) or len(draft_by_id) != len(materialized):
        errors.append("duplicate source_group_id in input or draft")

    missing = sorted(set(source_by_id) - set(draft_by_id))
    extra = sorted(set(draft_by_id) - set(source_by_id))
    field_diffs = []
    for gid in sorted(set(source_by_id) & set(draft_by_id)):
        for f in SOURCE_FIELDS:
            if source_by_id[gid].get(f) != draft_by_id[gid].get(f):
                field_diffs.append({"id": gid, "field": f,
                                    "source": source_by_id[gid].get(f),
                                    "draft": draft_by_id[gid].get(f)})
    checks["exact_projection_row_match"] = not missing and not extra and not field_diffs
    checks["projection_missing_from_draft"] = missing
    checks["draft_ids_not_in_projection"] = extra
    checks["projection_field_differences"] = field_diffs
    if missing or extra or field_diffs:
        errors.append("draft rows do not exactly replay the owned projection")

    expected_blocks = {r["source_group_id"]: block_for(r["locus"]) for r in source}
    wrong_block = [gid for gid, b in expected_blocks.items() if source_by_id[gid]["block"] != b]
    checks["projection_spatial_block_check"] = not wrong_block
    checks["wrong_projection_block_ids"] = wrong_block
    if wrong_block:
        errors.append("projection block labels disagree with fixed .2-.23 spatial boundaries")

    src_scope = [r for r in source if block_for(r["locus"]) != "OUTSIDE"]
    src_outside = [r for r in source if block_for(r["locus"]) == "OUTSIDE"]
    checks["scope_counts_by_edition"] = {
        ed: {
            "selected": sum(r["edition"] == ed for r in src_scope),
            "outside": sum(r["edition"] == ed for r in src_outside),
            "selected_by_block": {b: sum(r["edition"] == ed and block_for(r["locus"]) == b for r in src_scope)
                                  for b in ("N", "E", "S", "W")},
        } for ed in ("ZL3b", "IT2a", "RF1b")
    }
    if len(src_scope) != 324 or len(src_outside) != 149:
        errors.append("expected 324 selected reader rows and 149 outside rows")
    for ed in SELECTED_COUNTS:
        c = checks["scope_counts_by_edition"][ed]  # type: ignore[index]
        if c["selected"] != SELECTED_COUNTS[ed]:
            errors.append(f"selected scope count mismatch for {ed}: {c}")
    checks["only_f85r2_projection"] = all(r["locus"].startswith("f85r2.") for r in source)
    if not checks["only_f85r2_projection"]:
        errors.append("unexpected non-f85r2 projection row")

    selected_by_reader = Counter(r["edition"] for r in materialized if block_for(r["locus"]) != "OUTSIDE")
    outside_by_reader = Counter(r["edition"] for r in materialized if block_for(r["locus"]) == "OUTSIDE")
    assigned_by_reader = Counter(r["edition"] for r in materialized if r["lexical_status"] == "assigned_exact")
    selected_assigned = Counter(r["edition"] for r in materialized if block_for(r["locus"]) != "OUTSIDE" and r["lexical_status"] == "assigned_exact")
    outside_assigned = Counter(r["edition"] for r in materialized if block_for(r["locus"]) == "OUTSIDE" and r["lexical_status"] == "assigned_exact")
    selected_unassigned = Counter(r["edition"] for r in materialized if block_for(r["locus"]) != "OUTSIDE" and r["lexical_status"] == "unassigned")
    checks["assigned_unassigned_counts"] = {
        "selected_by_reader": dict(selected_by_reader),
        "outside_by_reader": dict(outside_by_reader),
        "selected_assigned_exact_by_reader": dict(selected_assigned),
        "selected_unassigned_by_reader": dict(selected_unassigned),
        "outside_assigned_exact_by_reader": dict(outside_assigned),
        "all_assigned_exact_by_reader": dict(assigned_by_reader),
    }
    if dict(selected_unassigned) != {"ZL3b": 4, "IT2a": 13, "RF1b": 21}:
        errors.append("selected alternate/primary unassigned row counts differ")
    if dict(outside_assigned) != {"ZL3b": 14, "IT2a": 18, "RF1b": 15}:
        errors.append("outside assigned row counts differ")

    lexicon = draft["lexicon"]
    lex_by_form = {x["form"]: x for x in lexicon}
    unique_zl_types = {r["ivtff_group_raw"] for r in materialized
                       if r["edition"] == "ZL3b" and block_for(r["locus"]) != "OUTSIDE"}
    checks["ZL_unique_types"] = len(unique_zl_types)
    checks["lexicon_type_count"] = len(lexicon)
    checks["lexicon_forms_equal_all_ZL_types"] = unique_zl_types == set(lex_by_form)
    if len(unique_zl_types) != 85 or unique_zl_types != set(lex_by_form):
        errors.append("lexicon is not exactly the 85 selected ZL whole types")

    lex_occurrence_diffs = []
    row_assignment_diffs = []
    for form, entry in lex_by_form.items():
        expected_ids = sorted(r["source_group_id"] for r in materialized if r["ivtff_group_raw"] == form)
        stated_ids = sorted(entry["all_owned_literal_occurrences"])
        if expected_ids != stated_ids:
            lex_occurrence_diffs.append({"form": form, "missing": sorted(set(expected_ids)-set(stated_ids)),
                                         "extra": sorted(set(stated_ids)-set(expected_ids))})
    for r in materialized:
        assigned = r["lexical_status"] == "assigned_exact"
        form = r["ivtff_group_raw"]
        entry = lex_by_form.get(form)
        if assigned and (entry is None or r.get("meaning") != entry.get("meaning") or r.get("type") != entry.get("type")):
            row_assignment_diffs.append({"id": r["source_group_id"], "form": form,
                                         "meaning": r.get("meaning"), "type": r.get("type"),
                                         "entry": entry})
        if not assigned and r.get("meaning") not in (None, "UNASSIGNED"):
            row_assignment_diffs.append({"id": r["source_group_id"], "issue": "unassigned row has meaning",
                                         "meaning": r.get("meaning")})
    checks["lexicon_occurrence_lists_exact"] = not lex_occurrence_diffs
    checks["lexicon_occurrence_differences"] = lex_occurrence_diffs
    checks["row_assignment_consistency"] = not row_assignment_diffs
    checks["row_assignment_differences"] = row_assignment_diffs
    if lex_occurrence_diffs or row_assignment_diffs:
        errors.append("lexicon/occurrence assignment mismatch")

    clauses = draft["clauses"]
    clause_ids = [gid for cl in clauses for gid in cl["source_ids"]]
    clause_counts = Counter(clause_ids)
    zl_selected_ids = {r["source_group_id"] for r in materialized
                       if r["edition"] == "ZL3b" and block_for(r["locus"]) != "OUTSIDE"}
    clause_coverage = {
        "clause_source_ids": len(clause_ids),
        "unique_clause_source_ids": len(clause_counts),
        "ids_not_primary_selected": sorted(set(clause_counts)-zl_selected_ids),
        "primary_selected_ids_missing_from_clauses": sorted(zl_selected_ids-set(clause_counts)),
        "multiple_clause_assignments": {gid:n for gid,n in clause_counts.items() if n != 1},
        "status_by_clause": {cl["id"]: cl["status"] for cl in clauses},
        "groups_by_clause": {cl["id"]: len(cl["source_ids"]) for cl in clauses},
    }
    checks["clause_coverage"] = clause_coverage
    if (len(clause_ids) != 108 or set(clause_counts) != zl_selected_ids or
            any(n != 1 for n in clause_counts.values())):
        errors.append("clause spans do not partition all 108 selected ZL groups exactly once")
    authored_slots = sum(len(cl["source_ids"]) for cl in clauses if cl["status"] != "UNRESOLVED")
    unresolved_slots = sum(len(cl["source_ids"]) for cl in clauses if cl["status"] == "UNRESOLVED")
    if authored_slots != 100 or unresolved_slots != 8:
        errors.append(f"partial slot counts differ: authored={authored_slots}, unresolved={unresolved_slots}")

    literal_diffs = []
    for cl in clauses:
        expected_words = [draft_by_id[gid]["ivtff_group_raw"] for gid in cl["source_ids"]]
        actual_words = cl["literal"].split()
        if actual_words != expected_words:
            literal_diffs.append({"clause": cl["id"], "expected": expected_words, "literal": actual_words})
    checks["clause_literals_match_source_ids"] = not literal_diffs
    checks["clause_literal_differences"] = literal_diffs

    form_counts = Counter(r["ivtff_group_raw"] for r in materialized)
    expected_component_meanings = {
        "dar": "d(POWER)", "daiin": "d(RECEIVED_PROPERTIES)",
        "qodar": "qo(d(POWER))", "qodaiin": "qo(d(RECEIVED_PROPERTIES))",
        "qodain": "qo(d(LAST_RESPECT))",
    }
    component_applications = {}
    for form, meaning in expected_component_meanings.items():
        rows = [r for r in materialized if r["ivtff_group_raw"] == form]
        component_applications[form] = {
            "occurrence_count_all_readers_scope": len(rows),
            "rows": [{"id": r["source_group_id"], "status": r["lexical_status"],
                      "meaning": r.get("meaning"), "clause": r.get("clause")} for r in rows],
            "meaning_consistent": all(r.get("meaning") == meaning for r in rows),
        }
        if not rows or not component_applications[form]["meaning_consistent"]:
            errors.append(f"fixed composition meaning mismatch for {form}")
    checks["actual_fixed_composition_rows"] = component_applications

    # Reconstruct the frozen LAST_RESPECT state independently from literal
    # standalone respects, in N,E,S,W line order for each reader.
    anaphors = []
    for ed in ("ZL3b", "IT2a", "RF1b"):
        rs = [r for r in materialized if r["edition"] == ed and block_for(r["locus"]) != "OUTSIDE"]
        rs.sort(key=lambda r: (int(r["locus"].rsplit(".",1)[1]), int(r["source_group_index"])))
        last = None
        for r in rs:
            raw = r["ivtff_group_raw"]
            if raw == "ar":
                last = "POWER"
            elif raw == "aiin":
                last = "RECEIVED_PROPERTIES"
            elif raw == "ain":
                anaphors.append({"id":r["source_group_id"], "kind":"standalone ain", "resolves":last,
                                 "row_meaning":r.get("meaning"), "clause":r.get("clause")})
                if last is None:
                    errors.append(f"standalone ain has no preceding register value: {r['source_group_id']}")
                last = last  # a resolved standalone anaphor repeats the current value
            elif raw == "qodain":
                anaphors.append({"id":r["source_group_id"], "kind":"internal qodain", "resolves":last,
                                 "row_meaning":r.get("meaning"), "clause":r.get("clause")})
                if last is None:
                    errors.append(f"qodain has no preceding register value: {r['source_group_id']}")
        # No update for respect components internal to d/qo compounds.
    checks["independent_ain_qodain_trace"] = anaphors
    checks["all_anaphor_traces_resolve_REC"] = all(x["resolves"] == "RECEIVED_PROPERTIES" for x in anaphors)
    if not checks["all_anaphor_traces_resolve_REC"]:
        errors.append("ain/qodain trace does not resolve uniformly to REC")

    clauses_by_id = {cl["id"]: cl for cl in clauses}
    actual_application_spans = {
        "d_REC": ("N2", "daiin"),
        "d_POWER": ("S4", "dar"),
        "qo_d_POWER": ("E4", "qodar"),
        "qo_d_REC": ("S5", "qodaiin"),
        "qo_d_LAST_RESPECT": ("W2", "qodain"),
        "repeated_qo_d_REC_W": ("W4", "qodaiin"),
    }
    app_check = {}
    for label,(cid,form) in actual_application_spans.items():
        clause = clauses_by_id[cid]
        hits = [gid for gid in clause["source_ids"] if draft_by_id[gid]["ivtff_group_raw"] == form]
        app_check[label] = {"clause":cid,"form":form,"matching_groups":hits,
                            "formula":clause.get("formula"),
                            "has_fixed_expected_meaning": bool(hits) and all(draft_by_id[g].get("meaning") == expected_component_meanings[form] for g in hits)}
        if not hits:
            errors.append(f"no literal {form} in claimed application clause {cid}")
    checks["claimed_application_locations"] = app_check

    coverage = draft["source_coverage"]
    checks["source_clause_statuses"] = {k:v["status"] for k,v in coverage.items()}
    checks["source_clause_count"] = len(coverage)
    checks["explicitly_unfulfilled_source_ids"] = [
        k for k,v in coverage.items() if "MISSING" in v["status"].upper() or "MISSING" in " ".join(v["where"]).upper()
    ]
    # Source coverage is manually reviewed against the fixed 28-line C01-18
    # inventory; this script does not claim semantic entailment.

    cost = draft["costs"]
    actual_origins = Counter(x["origin"] for x in lexicon)
    new_payloads = [x.get("semantic_payload_accounting",[]) for x in lexicon if x.get("origin") == "new"]
    payload_len = sum(len(x) if isinstance(x,list) else 1 for x in new_payloads)
    multi = sum((len(x) if isinstance(x,list) else 1) > 1 for x in new_payloads)
    grammar_ids = [g["id"] for g in draft["grammar"]]
    assumption_ids = [x.get("id") for x in draft["scope_and_input_assumptions"]]
    checks["independent_cost_reconstruction"] = {
        "origin_counts":dict(actual_origins),
        "lexicon_total":len(lexicon),
        "new_meaning_label_count":len({x["meaning"] for x in lexicon if x.get("origin")=="new"}),
        "new_payload_occurrence_count":payload_len,
        "new_multifeature_value_count":multi,
        "grammar_id_count":len(grammar_ids),
        "grammar_ids":grammar_ids,
        "assumption_id_count":len(assumption_ids),
        "assumption_ids":assumption_ids,
        "computed_cost_fields":cost,
    }
    if actual_origins != Counter({"new":73, "unassigned":4, "fixed atom":3, "computed":5}):
        errors.append(f"lexicon origin counts unexpected: {actual_origins}")
    if payload_len != cost.get("new_value_payload_occurrences") or multi != cost.get("multifeature_new_whole_values"):
        errors.append("new-value payload cost mismatch")
    if len(grammar_ids) != 24 or len(assumption_ids) != 14:
        errors.append("grammar or assumption bundle count mismatch")

    checks["outcome_scope"] = {
        "result": "PARTIAL_NOT_UNSAT_NOT_COMPLETE_TRANSLATION",
        "selected_primary_groups_authored": authored_slots,
        "selected_primary_groups_unresolved": unresolved_slots,
        "selected_ZL_forms_assigned": 81,
        "selected_ZL_forms_unassigned": 4,
        "source_obligations_missing_or_partial": ["C15", "C16", "first causal link C06->C07 in C17"],
        "earliest_exact_residue": draft["earliest_unowned_selected_span"],
    }
    checks["errors"] = errors
    checks["mechanical_bookkeeping_status"] = "PASS" if not errors else "FAIL"
    OUT.write_text(json.dumps({"schema":"independent-RAW572-replay-v1", "hashes":hashes, **checks},
                              ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status":checks["mechanical_bookkeeping_status"],
                      "selected":len(src_scope),"outside":len(src_outside),
                      "assigned_slots":authored_slots,"unresolved_slots":unresolved_slots,
                      "errors":errors,"output":OUT.name}, indent=2))


if __name__ == "__main__":
    main()

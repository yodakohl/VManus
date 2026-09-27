#!/usr/bin/env python3
"""Independent literal/type-obligation replay for the frozen RAW566 partial.

Reads only the frozen author draft and the already owned GDT1042 guarded
projection. It does not import author code or solve prose/semantic grammar.
Run from the repository root:
    python research_registry/proposals/laufenberg_f85r2_20260926/MEDIATED_COLD_REPLAY_B.py
"""
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path.cwd()
PROJECTION = Path("experiments/yolo/gdt1042_f85r2_source_program_surface_census/artifacts/guarded_projection.tsv")
DRAFT = Path("research_registry/proposals/laufenberg_f85r2_20260926/MEDIATED_COLD_AUTHOR_DRAFT.json")
OUT = Path("research_registry/proposals/laufenberg_f85r2_20260926/MEDIATED_COLD_REPLAY_B.json")
SELECTED = {f"f85r2.{n}" for n in (*range(12, 18), *range(18, 24))}
BLOCK = {f"f85r2.{n}": ("S" if n < 18 else "W") for n in (*range(12, 18), *range(18, 24))}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def main() -> None:
    src = load_tsv(PROJECTION)
    draft = json.loads(DRAFT.read_text(encoding="utf-8"))
    lex = draft["whole_lexicon"]
    src_by_id = {r["source_group_id"]: r for r in src}
    assert len(src_by_id) == len(src), "projection duplicate source_group_id"

    # Reconstruct complete physical lines from the projection's explicit
    # LINE_START/LINE_END separators, not from the authored row contexts.
    by_paragraph: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for r in src:
        by_paragraph[(r["edition"], r["locus"])].append(r)
    line_for_id: dict[str, str] = {}
    position_for_id: dict[str, str] = {}
    for key, rows in by_paragraph.items():
        rows.sort(key=lambda r: int(r["source_group_index"]))
        open_line: list[dict[str, str]] = []
        for row in rows:
            if row["left_separator"] == "LINE_START":
                assert not open_line, (key, "nested line start", row["source_group_id"])
                open_line = []
            assert open_line or row["left_separator"] == "LINE_START", (key, "line lacks start", row)
            open_line.append(row)
            if row["right_separator"] == "LINE_END":
                text = " ".join(x["ivtff_group_raw"] for x in open_line)
                for i, x in enumerate(open_line):
                    line_for_id[x["source_group_id"]] = text
                    position_for_id[x["source_group_id"]] = (
                        "single" if len(open_line) == 1 else
                        "first" if i == 0 else
                        "last" if i == len(open_line) - 1 else "interior"
                    )
                open_line = []
        assert not open_line, (key, "unterminated reconstructed line")

    selected_src = [r for r in src if r["locus"] in SELECTED]
    assert len(selected_src) == 186
    selected_draft = draft["selected_rows"]
    assert len(selected_draft) == 186
    selected_lookup = {r["source_group_id"]: r for r in selected_draft}
    assert len(selected_lookup) == 186
    projection_fields = (
        "source_group_id", "edition", "locus", "source_group_index",
        "source_group_count", "paragraph_start", "paragraph_end",
        "left_separator", "right_separator", "ivtff_group_raw",
    )
    row_errors = []
    for s in selected_src:
        d = selected_lookup.get(s["source_group_id"])
        if d is None:
            row_errors.append({"missing": s["source_group_id"]})
            continue
        for field in projection_fields:
            if str(d.get(field)) != str(s[field]):
                row_errors.append({"id": s["source_group_id"], "field": field,
                                   "projection": s[field], "draft": d.get(field)})
        if d.get("block") != BLOCK[s["locus"]]:
            row_errors.append({"id": s["source_group_id"], "field": "block"})
        sid = s["source_group_id"]
        if d.get("full_literal_line") != line_for_id.get(sid):
            row_errors.append({"id": sid, "field": "full_literal_line",
                               "projection_reconstructed": line_for_id.get(sid),
                               "draft": d.get("full_literal_line")})
        if d.get("within_line_position") != position_for_id.get(sid):
            row_errors.append({"id": sid, "field": "within_line_position",
                               "projection_reconstructed": position_for_id.get(sid),
                               "draft": d.get("within_line_position")})
        if d.get("lexically_assigned") != (s["ivtff_group_raw"] in lex):
            row_errors.append({"id": sid, "field": "lexically_assigned"})
    assert not row_errors, f"selected row/context mismatches: {row_errors[:3]}"
    assert set(selected_lookup) == {r["source_group_id"] for r in selected_src}

    selected_counts = {}
    for ed in ("ZL3b", "IT2a", "RF1b"):
        rows = [r for r in selected_src if r["edition"] == ed]
        selected_counts[ed] = {
            "rows": len(rows),
            "assigned": sum(r["ivtff_group_raw"] in lex for r in rows),
            "unassigned": sum(r["ivtff_group_raw"] not in lex for r in rows),
        }
    assert selected_counts == {
        "ZL3b": {"rows": 62, "assigned": 21, "unassigned": 41},
        "IT2a": {"rows": 61, "assigned": 20, "unassigned": 41},
        "RF1b": {"rows": 63, "assigned": 20, "unassigned": 43},
    }

    outside_src = [r for r in src if r["locus"] not in SELECTED and r["ivtff_group_raw"] in lex]
    outside_draft = draft["outside_assigned_rows"]
    outside_lookup = {r["source_group_id"]: r for r in outside_draft}
    assert len(outside_src) == 28 == len(outside_draft)
    assert len(outside_lookup) == 28
    outside_errors = []
    for s in outside_src:
        d = outside_lookup.get(s["source_group_id"])
        if d is None:
            outside_errors.append({"missing": s["source_group_id"]})
            continue
        for field in projection_fields:
            if str(d.get(field)) != str(s[field]):
                outside_errors.append({"id": s["source_group_id"], "field": field})
        if d.get("full_literal_line") != line_for_id.get(s["source_group_id"]):
            outside_errors.append({"id": s["source_group_id"], "field": "full_literal_line"})
        if d.get("lexically_assigned") is not True:
            outside_errors.append({"id": s["source_group_id"], "field": "lexically_assigned"})
    assert not outside_errors, outside_errors[:3]
    assert set(outside_lookup) == {r["source_group_id"] for r in outside_src}

    # Exact spelling census for the qod compounds and bare process roots over
    # all473 owned rows. These are literal equality checks, not a parser.
    focal = {"qodaiin", "qodain", "aiin", "ain"}
    focal_rows = [r for r in src if r["ivtff_group_raw"] in focal]
    focal_occurrences = []
    for r in focal_rows:
        focal_occurrences.append({
            "source_group_id": r["source_group_id"], "edition": r["edition"],
            "locus": r["locus"], "raw": r["ivtff_group_raw"],
            "block": BLOCK.get(r["locus"], "OUTSIDE"),
            "within_line_position": position_for_id[r["source_group_id"]],
            "left_separator": r["left_separator"], "right_separator": r["right_separator"],
            "full_literal_line": line_for_id[r["source_group_id"]],
            "lexical_type": lex[r["ivtff_group_raw"]]["type"],
        })
    qod_prefix_rows = [r for r in src if r["ivtff_group_raw"].startswith("qod")]
    unlicensed_qod_prefixes = [r for r in qod_prefix_rows
                               if r["ivtff_group_raw"] not in {"qodaiin", "qodain"}]

    # Verify each claimed ZL contiguous compound surface and its alternative.
    def by_locus(ed: str, locus: str) -> list[dict[str, str]]:
        return sorted((r for r in src if r["edition"] == ed and r["locus"] == locus),
                      key=lambda r: int(r["source_group_index"]))

    def raw_slice(ed: str, locus: str, start: int, end: int) -> list[str]:
        return [r["ivtff_group_raw"] for r in by_locus(ed, locus)
                if start <= int(r["source_group_index"]) <= end]

    required_spans = [
        ("K1_S16", "ZL3b", "f85r2.16", 2, 4, ["qodaiin", "odain", "an"]),
        ("K2_W19", "ZL3b", "f85r2.19", 2, 5, ["qodain", "chckhy", "ykeedy", "chedy"]),
    ]
    for name, ed, locus, first, last, expected in required_spans:
        assert raw_slice(ed, locus, first, last) == expected, name
    k3 = [by_locus("ZL3b", "f85r2.21")[4]["ivtff_group_raw"],
          by_locus("ZL3b", "f85r2.22")[0]["ivtff_group_raw"],
          by_locus("ZL3b", "f85r2.22")[1]["ivtff_group_raw"]]
    assert k3 == ["qodaiin", "los", "ar"]
    alt_it_k1 = raw_slice("IT2a", "f85r2.16", 2, 5)
    assert alt_it_k1 == ["qodain", "odain", "an", "chey"]
    alt_rf_k2 = by_locus("RF1b", "f85r2.19")[1]["ivtff_group_raw"]
    assert alt_rf_k2 == "qo@152;ain" and alt_rf_k2 not in lex

    # Fixed typed reasoning, stated as explicit checks rather than a general
    # grammar evaluator. References are type-compatible where noted but have
    # no completed Case/antecedent in this partial.
    bare_sources = [
        ("S14", "ZL3b", "f85r2.14", 3, "aiin", "RESOURCE_ASPECT",
         "right ar(a)rody or left chz[s:r] unknown; no type clash"),
        ("S17", "ZL3b", "f85r2.17", 3, "ain", "LOCATION_THEN_CARRIER",
         "no right arguments; left orar/oldar unassigned"),
        ("W20_aiin", "ZL3b", "f85r2.20", 2, "aiin", "RESOURCE_ASPECT",
         "right ckhed[a:y] unknown; left or is fixed ConditionKind and conflicts if postfix"),
        ("W20_ain", "ZL3b", "f85r2.20", 5, "ain", "LOCATION_THEN_CARRIER",
         "right olchey/qokal unassigned; postfix would take or as Carrier, a type mismatch"),
        ("W22", "ZL3b", "f85r2.22", 7, "aiin", "RESOURCE_ASPECT",
         "right og unknown; left or is fixed ConditionKind and conflicts if postfix"),
    ]
    bare_checks = []
    for name, ed, locus, ix, form, needs, finding in bare_sources:
        rows = by_locus(ed, locus)
        token = rows[ix - 1]["ivtff_group_raw"]
        assert token == form, (name, token, form)
        bare_checks.append({"id": name, "source_group_id": rows[ix - 1]["source_group_id"],
                            "raw": token, "required_argument_types": needs,
                            "independent_type_finding": finding})

    result = {
        "schema": "mediated_cold_literal_type_replay_b_v1",
        "status": "PASS_LITERAL_REPLAY; PARTIAL_TYPED_APPLICATIONS; NO_COMPLETE_CASES",
        "input_sha256": {str(PROJECTION): digest(PROJECTION), str(DRAFT): digest(DRAFT)},
        "selected_scope": sorted(SELECTED),
        "selected_row_replay": {"projection_rows": len(selected_src), "draft_rows": len(selected_draft),
                                "id_set_and_projected_fields_match": True,
                                "line_contexts_reconstructed_from_separators_match": True,
                                "counts": selected_counts},
        "outside_assignment_replay": {"projection_matching_rows": len(outside_src),
                                      "draft_rows": len(outside_draft),
                                      "id_set_and_projected_fields_match": True,
                                      "counts_by_reader": dict(Counter(r["edition"] for r in outside_src))},
        "exact_qod_bare_root_occurrences_all473_rows": {
            "counts": dict(Counter(r["ivtff_group_raw"] for r in focal_rows)),
            "rows": focal_occurrences,
        },
        "qod_initial_census_all473_rows": {
            "counts": dict(Counter(r["ivtff_group_raw"] for r in qod_prefix_rows)),
            "only_licensed_compounds": ["qodaiin", "qodain"],
            "other_qod_initials_unsegmented": [
                {"source_group_id": r["source_group_id"], "edition": r["edition"],
                 "locus": r["locus"], "raw": r["ivtff_group_raw"],
                 "status": "OPAQUE_WHOLE_NOT_ASSIGNED_OR_NORMALIZED"}
                for r in unlicensed_qod_prefixes
            ],
        },
        "manual_candidate_checks": {
            "compound_spans": [
                {"id": "K1_S16", "literal": "qodaiin odain an", "types": "ResourceAspect then Condition", "antecedents_case_scope": "UNRESOLVED"},
                {"id": "K2_W19", "literal": "qodain chckhy ykeedy chedy", "types": "Location, Carrier, Condition", "antecedents_case_scope": "UNRESOLVED"},
                {"id": "K3_W21_22", "literal": "qodaiin los ar", "types": "ResourceAspect then Condition", "antecedents_case_scope": "UNRESOLVED; no cross-paragraph S import"},
                {"id": "IT_S16", "literal": "qodain odain an chey",
                 "expected_arguments": ["Location", "Carrier", "Condition"],
                 "actual_arguments": ["Reference(ResourceAspect)", "Reference(Condition)", "UNASSIGNED"],
                 "type_result": "FAIL: first argument odain is ResourceAspect not Location; second an is Condition not Carrier; third chey is unassigned"},
                {"id": "RF_W19", "literal": alt_rf_k2, "type_result": "UNASSIGNED marked reading; not normalized to qodain"},
            ],
            "bare_root_obligations": bare_checks,
            "no_case_or_owner_completed": True,
            "no_path_derived": True,
        },
        "interpretive_limit": "Literal replay and local type consequences only. Unknown antecedents/owners/guards are not contradictions. No semantic confirmation, full case, source entailment, or full-block parse is tested.",
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "selected": result["selected_row_replay"],
                      "outside": result["outside_assignment_replay"],
                      "focal": result["exact_qod_bare_root_occurrences_all473_rows"]["counts"],
                      "result": str(OUT)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

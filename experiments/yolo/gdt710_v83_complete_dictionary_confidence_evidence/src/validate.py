#!/usr/bin/env python3
"""Independent validator for GDT710; does not import the builder."""

from __future__ import annotations

import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt710_v83_complete_dictionary_confidence_evidence"
ART = EXP / "artifacts"
G671 = ROOT / "experiments/yolo/gdt671_fifteen_residual_family_completion/artifacts"
G684 = ROOT / "experiments/yolo/gdt684_v57_complete_semantic_debt_census/artifacts"
G685 = ROOT / "experiments/yolo/gdt685_v58_ch_sh_t_ol_ansatz_dispatch/artifacts"
G686 = ROOT / "experiments/yolo/gdt686_v59_dain_daiin_qodaiin_value_head_dispatch/artifacts"
G687 = ROOT / "experiments/yolo/gdt687_v60_dchey_y_dy_action_result_boundary_dispatch/artifacts"
G689 = ROOT / "experiments/yolo/gdt689_v62_bound_dy_sister_endpoint_dispatch/artifacts"
G690 = ROOT / "experiments/yolo/gdt690_noun_ordinal_provenance_main_apparatus/artifacts"
G691 = ROOT / "experiments/yolo/gdt691_preparation_head_role_dispatch/artifacts"
G692 = ROOT / "experiments/yolo/gdt692_o_q_fraction_sister_compositor/artifacts"
G693 = ROOT / "experiments/yolo/gdt693_ar_head_semantic_tournament/artifacts"
G694 = ROOT / "experiments/yolo/gdt694_residual_fraction_share_migration/artifacts"
G695 = ROOT / "experiments/yolo/gdt695_fixed_v67_clause_realization/artifacts"
STATUS = (
    "PASS_V83_2115_MASTER_CARDS__1430_GLOBAL_SURFACES__"
    "1582_COMPLETE_WORD_SURFACES_1594_READINGS__"
    "320_LIVE_SURFACES_332_LIVE_READINGS_479_OCCURRENCES__"
    "ALL_H0_NONE__CONFIDENCE_IS_NOT_PLAINTEXT"
)


class Audit:
    def __init__(self) -> None:
        self.checks = 0

    def require(self, condition: bool, label: str) -> None:
        self.checks += 1
        if not condition:
            raise AssertionError(label)

    def equal(self, actual: Any, expected: Any, label: str) -> None:
        self.checks += 1
        if actual != expected:
            raise AssertionError(f"{label}: {actual!r} != {expected!r}")


def read_tsv(path: Path, audit: Audit) -> tuple[list[str], list[dict[str, str]]]:
    audit.require(path.is_file(), f"missing {path}")
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t"); fields = list(reader.fieldnames or []); rows = list(reader)
    audit.require(bool(fields), f"empty header {path}"); audit.equal(len(fields), len(set(fields)), f"unique fields {path}")
    for number, row in enumerate(rows, 2):
        audit.require(None not in row, f"extra cell {path}:{number}"); audit.equal(set(row), set(fields), f"schema {path}:{number}")
    return fields, rows


def key(row: dict[str, str]) -> tuple[str, str, int, str]:
    return row["page"], row["locus"], int(row.get("token_ordinal") or row.get("ordinal") or "0"), row["surface"]


def one(rows: list[dict[str, str]], audit: Audit, label: str, **wanted: str) -> dict[str, str]:
    hits = [row for row in rows if all(row.get(field) == value for field, value in wanted.items())]
    audit.equal(len(hits), 1, label)
    return hits[0]


def score_level(score: int) -> str:
    if score < 20: return "W0_PLACEHOLDER_OR_SEMANTICALLY_EMPTY"
    if score < 40: return "W1_WEAK_WORKING"
    if score < 60: return "W2_PROVISIONAL_WORKING"
    if score < 80: return "W3_SOLID_WORKING_THEORY"
    return "W4_STRONG_WORKING_THEORY"


def validate() -> dict[str, Any]:
    a = Audit()
    names = {
        "master": "V83_2115_MASTER_CARD_CONFIDENCE.tsv", "global": "V83_1430_GLOBAL_SURFACE_CONFIDENCE.tsv",
        "complete": "V83_COMPLETE_WORD_CONFIDENCE.tsv", "occurrence": "V83_479_LIVE_OCCURRENCE_EVIDENCE.tsv",
        "reading": "V83_332_LIVE_READING_CONFIDENCE.tsv", "surface": "V83_320_LIVE_SURFACE_CONFIDENCE.tsv",
        "rubric": "V83_CONFIDENCE_RUBRIC.tsv", "registry": "V83_EVIDENCE_SOURCE_REGISTRY.tsv",
    }
    loaded = {name: read_tsv(ART / filename, a)[1] for name, filename in names.items()}
    master, global_rows, complete = loaded["master"], loaded["global"], loaded["complete"]
    occurrences, readings, surfaces = loaded["occurrence"], loaded["reading"], loaded["surface"]
    a.equal((len(master), len(global_rows), len(complete), len(occurrences), len(readings), len(surfaces)), (2115, 1430, 1594, 479, 332, 320), "artifact populations")
    a.equal((len(loaded["rubric"]), len(loaded["registry"])), (20, 17), "method populations")

    source_master = read_tsv(G671 / "WORKING_DICTIONARY_V48.tsv", a)[1]
    source_global = read_tsv(G671 / "V48_WORKING_TOKEN_GLOSSARY.tsv", a)[1]
    coverage = read_tsv(G671 / "ALL_LINE_CONCRETE_COVERAGE_V48.tsv", a)[1]
    active = read_tsv(G695 / "V68_479_TOKEN_FREEZE.tsv", a)[1]
    a.equal(len({row["entry"] for row in source_master}), 2115, "source master unique")
    a.equal(len({row["surface"] for row in source_global}), 1430, "source global unique")
    a.equal({row["entry"] for row in master}, {row["entry"] for row in source_master}, "master entry parity")
    a.equal({(row["surface"], row["working_meaning_de"]) for row in global_rows}, {(row["surface"], row["working_meaning_de"]) for row in source_global}, "global semantic parity")
    for source, output in zip(source_master, master):
        a.equal(tuple(output[field] for field in ("entry", "kind", "working_meaning_de", "composition", "context_rule", "status")), tuple(source[field] for field in ("entry", "kind", "working_meaning_de", "composition", "context_rule", "status")), f"master row parity {source['entry']}")

    global_surfaces = {row["surface"] for row in source_global}; counts = Counter(); pages: dict[str, set[str]] = defaultdict(set); loci: dict[str, set[str]] = defaultdict(set)
    for row in coverage:
        a.require(not row["page"].startswith("f84") and not row["locus"].startswith("f84"), f"forbidden folio coverage {row['locus']}")
        for token in row["zl3b_line"].split():
            if token in global_surfaces:
                counts[token] += 1; pages[token].add(row["page"]); loci[token].add(row["locus"])
    for row in global_rows:
        a.equal((int(row["occurrence_count"]), int(row["page_count"]), int(row["locus_count"])), (counts[row["surface"]], len(pages[row["surface"]]), len(loci[row["surface"]])), f"global count {row['surface']}")
    a.equal([surface for surface in sorted(global_surfaces) if counts[surface] == 0], ["otaiiin"], "one zero exact occurrence")

    active_keys = {key(row) for row in active}; output_keys = {key(row) for row in occurrences}
    a.equal(output_keys, active_keys, "active occurrence keys")
    a.equal(len(active_keys), 479, "active unique keys")
    active_by_key = {key(row): row for row in active}
    for row in occurrences:
        source = active_by_key[key(row)]
        a.equal(row["working_meaning_de"], source["v68_token_gloss_de"], f"active gloss {key(row)}")
        a.equal((row["historical_confirmation"], row["relation_word_delta"]), ("H0_NONE", "0_GDT696_TO_GDT709"), f"active ceiling {key(row)}")
        a.require(row["positive_evidence_de"] if "positive_evidence_de" in row else row["last_writer_evidence_de"], f"active evidence {key(row)}")
    a.equal(sum(int(row["global_v48_semantic_match"]) for row in occurrences), 127, "only exact V48 surface-gloss matches inherit semantics")
    a.equal(sum(row["v68_action_license"] != "NOT_ACTION_LICENSED" for row in occurrences), 83, "live 83 action positions")
    a.equal(Counter(row["bound_span_id"] for row in occurrences), Counter({"NONE": 473, "B001": 2, "B002": 2, "B003": 2}), "three two-position bound spans")
    a.require(all(row["bound_span_global_export_allowed"] == "0" for row in occurrences if row["bound_span_id"] != "NONE"), "bound spans never globally export")

    source_pairs = Counter((row["surface"], row["v68_token_gloss_de"]) for row in active)
    a.equal(set(source_pairs), {(row["surface"], row["working_meaning_de"]) for row in readings}, "reading set")
    for row in readings:
        pair = row["surface"], row["working_meaning_de"]
        a.equal(int(row["occurrence_count"]), source_pairs[pair], f"reading count {pair}")
    sense_counts = Counter(surface for surface, _ in source_pairs)
    a.equal(Counter(sense_counts.values()), Counter({1: 314, 2: 4, 3: 1, 7: 1}), "sense-count partition")
    a.equal(sorted(surface for surface, count in sense_counts.items() if count > 1), ["daiin", "dain", "dchey", "dy", "ol", "y"], "polysemous surfaces")
    a.equal({row["surface"] for row in surfaces}, {row["surface"] for row in active}, "surface set")
    for row in surfaces:
        a.equal(int(row["reading_count"]), sense_counts[row["surface"]], f"surface reading count {row['surface']}")

    # Independent final semantic-writer replay from V57 to V68.
    v57 = read_tsv(G684 / "V57_479_POSITION_INFORMATION_AUDIT.tsv", a)[1]
    state = {key(row): {"gloss": row["literal_gloss_de"], "writer": "GDT684"} for row in v57}
    stages = [
        ("GDT685", G685 / "V58_TARGET_POSITION_DEBT_DELTA.tsv", "new_literal_gloss_de"),
        ("GDT686", G686 / "V59_TARGET_POSITION_DEBT_DELTA.tsv", "new_literal_gloss_de"),
        ("GDT687", G687 / "V60_95_POSITION_SCOPE_DISPATCH.tsv", "v60_literal_gloss_de"),
        ("GDT689", G689 / "V62_50_POSITION_REVISIONS.tsv", "v62_literal_gloss_de"),
        ("GDT690", G690 / "V63_479_TOKEN_NOUN_BINDING.tsv", "v63_main_token_gloss_de"),
        ("GDT691", G691 / "V64_479_TOKEN_READER.tsv", "v64_token_gloss_de"),
        ("GDT692", G692 / "V65_479_TOKEN_READER.tsv", "v65_token_gloss_de"),
        ("GDT693", G693 / "V66_479_TOKEN_SELECTED_SHARE_READER.tsv", "v66_selected_gloss_de"),
        ("GDT694", G694 / "V67_479_TOKEN_ZERO_FRACTION_READER.tsv", "v67_token_gloss_de"),
        ("GDT695", G695 / "V68_479_TOKEN_FREEZE.tsv", "v68_token_gloss_de"),
    ]
    for gdt, path, field in stages:
        for row in read_tsv(path, a)[1]:
            position = key(row); a.require(position in state, f"known stage key {gdt} {position}")
            if row[field] != state[position]["gloss"]:
                state[position] = {"gloss": row[field], "writer": gdt}
    expected_writers = Counter({"GDT684": 201, "GDT685": 8, "GDT686": 8, "GDT687": 32, "GDT689": 36, "GDT690": 64, "GDT691": 50, "GDT692": 1, "GDT693": 57, "GDT694": 22})
    a.equal(Counter(cell["writer"] for cell in state.values()), expected_writers, "last writer distribution")
    occurrence_by_key = {key(row): row for row in occurrences}
    for position, cell in state.items():
        a.equal((cell["gloss"], cell["writer"]), (occurrence_by_key[position]["working_meaning_de"], occurrence_by_key[position]["last_semantic_writer"]), f"last writer replay {position}")
    expected_pre_v57_writers = Counter({"GDT676": 141, "GDT677": 2, "GDT678": 13, "GDT679": 12, "GDT680": 13, "GDT681": 13, "GDT683": 7})
    a.equal(Counter(row["position_assignment_writer_gdt"] for row in occurrences if row["last_semantic_writer"] == "GDT684"), expected_pre_v57_writers, "pre-V57 assignment writers for 201 survivors")

    active_surface_set = {row["surface"] for row in readings}
    expected_complete = {(row["surface"], row["working_meaning_de"]) for row in global_rows if row["surface"] not in active_surface_set} | {(row["surface"], row["working_meaning_de"]) for row in readings}
    a.equal({(row["surface"], row["working_meaning_de"]) for row in complete}, expected_complete, "complete current union")
    a.equal(len({row["surface"] for row in complete}), 1582, "complete surface population")

    score_fields = ("score_attestation", "score_invariance", "score_rule", "score_provenance", "score_specificity", "score_stress_survival")
    for group_name, rows in (("master", master), ("global", global_rows), ("reading", readings)):
        for row in rows:
            raw = sum(int(row[field]) for field in score_fields); score = int(row["working_model_score_0_100_not_probability"])
            a.equal(int(row["raw_score"]), raw, f"raw score {group_name} {row.get('entity_id')}")
            a.require(0 <= score <= 79, f"bounded score {group_name} {row.get('entity_id')}")
            a.equal(row["working_model_level"], score_level(score), f"level mapping {group_name} {row.get('entity_id')}")
            a.equal(row["historical_confirmation"], "H0_NONE", f"historical H0 {group_name} {row.get('entity_id')}")
            a.equal(row["relation_word_delta"], "0_GDT696_TO_GDT709", f"relation zero {group_name} {row.get('entity_id')}")
            a.require(bool(row["positive_evidence_de"] and row["counterevidence_de"]), f"two-sided evidence {group_name} {row.get('entity_id')}")

    # Hard reality controls guard against frequency- or renderer-driven nonsense.
    global_daiin = one(global_rows, a, "global daiin", surface="daiin")
    global_dain = one(global_rows, a, "global dain", surface="dain")
    a.require(int(global_daiin["working_model_score_0_100_not_probability"]) >= 60 and int(global_dain["working_model_score_0_100_not_probability"]) >= 60, "abstract value cells outrank concrete axes")
    for surface in ("daiin", "dain"):
        a.require(all(int(row["working_model_score_0_100_not_probability"]) <= 39 for row in readings if row["surface"] == surface), f"concrete {surface} capped W1")
    for surface in ("dy", "y"):
        a.require(all(int(row["working_model_score_0_100_not_probability"]) <= 19 for row in readings if row["surface"] == surface), f"structural {surface} semantic cap")
    for surface in ("shx", "oidal", "yey"):
        a.require(all(int(row["working_model_score_0_100_not_probability"]) <= 19 for row in readings if row["surface"] == surface), f"weak identity cap {surface}")
    olkar = one(readings, a, "olkar reading", surface="olkar")
    qokaiin = one(readings, a, "qokaiin reading", surface="qokaiin")
    chol = one(readings, a, "chol reading", surface="chol")
    a.require(int(olkar["working_model_score_0_100_not_probability"]) <= 39 < int(qokaiin["working_model_score_0_100_not_probability"]), "olkar below qokaiin")
    a.require(int(olkar["working_model_score_0_100_not_probability"]) < int(chol["working_model_score_0_100_not_probability"]), "olkar below chol")
    for surface in ("pchedaiin", "ldy", "olpchedy", "sheky"):
        row = one(readings, a, f"manual medium {surface}", surface=surface)
        a.require(40 <= int(row["working_model_score_0_100_not_probability"]) <= 59, f"manual W2 {surface}")
    dchey = [row for row in readings if row["surface"] == "dchey"]
    a.equal(len(dchey), 2, "two dchey senses"); a.require(all(row["working_model_level"].startswith("W3_") for row in dchey), "both dchey scope readings W3")
    a.equal(sorted(int(row["action_licensed_positions"]) for row in dchey), [0, 9], "dchey result/action license split")
    renderer_cards = [row for row in master if row["entry_scope"] == "RENDERER_CARD_NOT_WORD"]
    a.equal(len(renderer_cards), 563, "563 renderer cards")
    a.require(all(int(row["working_model_score_0_100_not_probability"]) <= 19 for row in renderer_cards), "renderer semantic cap")
    a.require(all(row["historical_confirmation"] == "H0_NONE" for row in complete), "complete H0")

    result_source = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))
    a.equal(result_source["status"], STATUS, "result status")
    a.equal(result_source["active_last_semantic_writer_positions"], dict(sorted(expected_writers.items())), "result writers")
    a.equal(result_source["historically_confirmed_words"], 0, "zero historical words")
    a.equal(result_source["relation_word_delta"], 0, "zero relation delta")
    a.equal(result_source["score_is_probability"], False, "not probability")
    return {"experiment_id": "GDT710", "status": "PASS", "experiment_status": STATUS, "checks": a.checks, "populations": {"master_cards": 2115, "global_surfaces": 1430, "complete_word_surfaces": 1582, "complete_word_readings": 1594, "active_surfaces": 320, "active_readings": 332, "active_occurrences": 479}, "historical_confirmation": "H0_NONE", "relation_word_delta": 0}


def main() -> int:
    result = validate()
    (ART / "VALIDATION.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True)); return 0


if __name__ == "__main__":
    raise SystemExit(main())

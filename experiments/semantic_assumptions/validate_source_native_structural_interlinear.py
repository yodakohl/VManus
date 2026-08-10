#!/usr/bin/env python3
"""Independent reconstruction of the source-native structural interlinear v1."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


BASE = Path(__file__).resolve().parent
ROOT = BASE.parent.parent
RESULTS = BASE / "results"
GROUPS = RESULTS / "source_sta_family_consensus_groups.tsv"
POSITION = RESULTS / "source_native_group_position_atlas.tsv"
POSITION_VALIDATION = RESULTS / "source_native_group_position_atlas_validation.json"
TRANSITIONS = RESULTS / "source_native_transition_atlas.tsv"
TRANSITIONS_VALIDATION = RESULTS / "source_native_transition_atlas_validation.json"
EDGE_FEATURES = RESULTS / "source_native_edge_feature_atlas.tsv"
EDGE_VALIDATION = RESULTS / "source_native_edge_feature_atlas_validation.json"
PATHS = RESULTS / "source_native_construction_path_atlas.tsv"
PATHS_VALIDATION = RESULTS / "source_native_construction_path_atlas_validation.json"
BASIC_RULES = ROOT / "transcription" / "sources" / "sta" / "STA-Eva_Bint.bit"
SPEC = BASE / "SOURCE_NATIVE_STRUCTURAL_INTERLINEAR_SPEC.md"
PRODUCER = BASE / "build_source_native_structural_interlinear.py"
PRODUCTION_TSV = RESULTS / "source_native_structural_interlinear_v1.tsv"
PRODUCTION_JSON = RESULTS / "source_native_structural_interlinear_v1.json"
PRODUCTION_REPORT = RESULTS / "source_native_structural_interlinear_v1_report.md"
VALIDATOR = Path(__file__).resolve()
OUT_JSON = RESULTS / "source_native_structural_interlinear_v1_validation.json"
OUT_REPORT = RESULTS / "source_native_structural_interlinear_v1_validation_report.md"

HASHES = {
    GROUPS: "a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",
    POSITION: "c062678e85a365f1a4fa54180c10f5337d4b316e6ac5c08461bd851a9a69deff",
    POSITION_VALIDATION: "9c421937b7278005c4f358e8f81884ed620aaf833c5cf7e02dd02797c0efa7d1",
    TRANSITIONS: "f20a0b1efb256c99c91b0899bb5c946d3a0483bc99a7467373a096d3c1934287",
    TRANSITIONS_VALIDATION: "209510d655c4b81c58f8f5eaec27676a4eee71317e3b485b3a1ce88d975dfd5c",
    EDGE_FEATURES: "a0df97db5e4f07c4e01f51806ccdc547da29e237ef4045001fed3faff74bb57a",
    EDGE_VALIDATION: "765c770118dac478751aa997d5608d6f104a2b1698f20680856cf7df821cae5d",
    PATHS: "8e37e2b082fec4f27712ef77b4370b7cc90bcc7f72ab9fa27d99e8b16601f665",
    PATHS_VALIDATION: "a7a254a5041495f09615c9681ae5d0bb83686698569314e30e16c66168f46e58",
    BASIC_RULES: "3c39164a76781ab781b5fbce2bcf75cee3183013a8d994d0463b2aa8f113a289",
    SPEC: "5eb952133b1523d175bcb45d9a3c56feeca00a495c31103663ebf4d50a206053",
    PRODUCER: "511ed21ae42c7d8cb206bebb4bd283b692af4c4c9784b5638b4edb8cf703173e",
    PRODUCTION_TSV: "95a15329c61a11c1c4dc671b4df2b3482af9d25a1108eadac2f69b066d3785af",
    PRODUCTION_JSON: "28283f57c516520cf7dff329573c9aea7a4cbaa301a77f974b97d2975a703747",
    PRODUCTION_REPORT: "e3c3479b2bc43bcffa641c56fb7febab9e8be42f5a4d99966fe85f5b5edf886c",
}
FIELDS = [
    "consensus_group_id", "locus", "page", "section", "currier", "hand",
    "code", "kind", "grammar_scope", "group_index", "group_count",
    "factual_position", "family_surface", "symbol_count", "zl_sta_codes",
    "it_sta_codes", "rf_sta_codes", "zl_basic_eva_lossy", "it_basic_eva_lossy",
    "rf_basic_eva_lossy", "left_boundary_profile", "left_boundary_support",
    "right_boundary_profile", "right_boundary_support", "exact_first_last_label",
    "exact_edge_core_label", "opening_feature_hits", "closing_feature_hits",
    "favored_transition_hits", "disfavored_transition_hits",
    "unresolved_transition_hits", "favored_path_hits", "longest_opening_path",
    "longest_path_anywhere",
]
INTEGER_FIELDS = {
    "group_index", "group_count", "symbol_count", "left_boundary_support", "right_boundary_support",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tsv(path: Path) -> list[dict[str, str]]:
    return list(csv.DictReader(path.open(encoding="utf-8", newline=""), delimiter="\t"))


def factual(index: int, count: int) -> str:
    assert 1 <= index <= count
    if count == 1:
        return "SINGLE"
    if index == 1:
        return "FIRST"
    if index == count:
        return "LAST"
    return "CORE"


def support(profile: str, edge: str) -> int:
    if profile == edge:
        return 3
    entries = profile.split(";")
    assert len(entries) == 3
    seen = set()
    n = 0
    for entry in entries:
        edition, value = entry.split(":", 1)
        assert edition in {"ZL3b", "IT2a", "RF1b"} and edition not in seen
        seen.add(edition)
        n += value != "NONE"
    assert seen == {"ZL3b", "IT2a", "RF1b"}
    return n


def features(surface: str) -> list[tuple[str, str]]:
    return [
        ("P1", surface[0]), ("P2", surface[:2]), ("S1", surface[-1]),
        ("S2", surface[-2:]), ("LEN", str(len(surface)) if len(surface) <= 7 else "8+"),
    ]


def rules() -> dict[str, str]:
    output = {}
    pattern = re.compile(r"^([A-Z][0-9a-z])\s+(\S+)$")
    for raw in BASIC_RULES.read_text(encoding="utf-8").splitlines():
        match = pattern.match(raw.strip())
        if not match:
            continue
        code, value = match.groups()
        assert code not in output
        output[code] = value
    assert len(output) >= 200
    return output


def reconstruct() -> tuple[list[dict[str, object]], dict[str, object], str, int]:
    checks = 0
    for path, expected in HASHES.items():
        assert sha(path) == expected
        checks += 1
    statuses = {
        POSITION_VALIDATION: "PASS_INDEPENDENT_EXACT_GROUP_POSITION_ATLAS_RECONSTRUCTION",
        TRANSITIONS_VALIDATION: "PASS_INDEPENDENT_576_PAIR_HELD_FOLIO_RECONSTRUCTION",
        EDGE_VALIDATION: "PASS_INDEPENDENT_EDGE_FEATURE_ATLAS_RECONSTRUCTION",
        PATHS_VALIDATION: "PASS_INDEPENDENT_13_PATH_CONSTRUCTION_RECONSTRUCTION",
    }
    for path, expected in statuses.items():
        assert json.loads(path.read_text(encoding="utf-8"))["status"] == expected
        checks += 1

    position_rows = tsv(POSITION)
    positions = {row["family_surface"]: row for row in position_rows}
    assert len(position_rows) == len(positions) == 2856
    transition_rows = tsv(TRANSITIONS)
    transitions = {row["pair_id"]: row["structural_label"] for row in transition_rows}
    assert len(transition_rows) == len(transitions) == 576
    edge_rows = tsv(EDGE_FEATURES)
    edges = {row["feature_id"]: row["structural_label"] for row in edge_rows}
    assert len(edge_rows) == len(edges) == 197
    path_rows = tsv(PATHS)
    path_inventory = sorted((row["path"] for row in path_rows), key=lambda x: (-len(x), x))
    assert len(path_rows) == len(set(path_inventory)) == 13
    basic = rules()
    checks += 5

    source = [row for row in tsv(GROUPS) if row["strict_zero_alternative"] == "1"]
    assert len(source) == 23281 and len({row["locus"] for row in source}) == 3572
    assert len({row["consensus_group_id"] for row in source}) == len(source)
    checks += 3
    output = []
    for row in source:
        surface = row["family_surface"]
        assert surface and all(pair in transitions for pair in (surface[i:i + 2] for i in range(len(surface) - 1)))
        index, count = int(row["consensus_group_index"]), int(row["consensus_group_count"])
        atlas = positions.get(surface)
        opening, closing = [], []
        for namespace, value in features(surface):
            feature_id = namespace + ":" + value
            label = edges.get(feature_id)
            if label == "OPEN_EDGE_ASSOCIATED":
                opening.append(feature_id)
            elif label == "CLOSE_EDGE_ASSOCIATED":
                closing.append(feature_id)
        transitions_by_label = defaultdict(list)
        for i in range(len(surface) - 1):
            pair = surface[i:i + 2]
            transitions_by_label[transitions[pair]].append(str(i + 1) + ":" + pair)
        path_hits = [path for path in path_inventory if path in surface]
        opening_paths = [path for path in path_inventory if surface.startswith(path)]
        lossy = {}
        for prefix, field in (("zl", "zl_sta_codes"), ("it", "it_sta_codes"), ("rf", "rf_sta_codes")):
            codes = row[field].split()
            assert codes and not (set(codes) - basic.keys())
            lossy[prefix] = "".join(basic[code] for code in codes)
            checks += len(codes)
        output.append({
            "consensus_group_id": row["consensus_group_id"], "locus": row["locus"],
            "page": row["page"], "section": row["section"], "currier": row["currier"],
            "hand": row["hand"], "code": row["code"], "kind": row["kind"],
            "grammar_scope": row["grammar_scope"], "group_index": index,
            "group_count": count, "factual_position": factual(index, count),
            "family_surface": surface, "symbol_count": int(row["symbol_count"]),
            "zl_sta_codes": row["zl_sta_codes"], "it_sta_codes": row["it_sta_codes"],
            "rf_sta_codes": row["rf_sta_codes"], "zl_basic_eva_lossy": lossy["zl"],
            "it_basic_eva_lossy": lossy["it"], "rf_basic_eva_lossy": lossy["rf"],
            "left_boundary_profile": row["left_boundary_profile"],
            "left_boundary_support": support(row["left_boundary_profile"], "LINE_START"),
            "right_boundary_profile": row["right_boundary_profile"],
            "right_boundary_support": support(row["right_boundary_profile"], "LINE_END"),
            "exact_first_last_label": atlas["first_last_label"] if atlas else "NOT_IN_PROSE_ATLAS",
            "exact_edge_core_label": atlas["edge_core_label"] if atlas else "NOT_IN_PROSE_ATLAS",
            "opening_feature_hits": ";".join(opening), "closing_feature_hits": ";".join(closing),
            "favored_transition_hits": ";".join(transitions_by_label["FAVORED_ADJACENCY"]),
            "disfavored_transition_hits": ";".join(transitions_by_label["DISFAVORED_ADJACENCY"]),
            "unresolved_transition_hits": ";".join(transitions_by_label["UNRESOLVED"]),
            "favored_path_hits": ";".join(path_hits),
            "longest_opening_path": opening_paths[0] if opening_paths else "NONE",
            "longest_path_anywhere": path_hits[0] if path_hits else "NONE",
        })
        checks += 1

    factual_counts = Counter(row["factual_position"] for row in output)
    first_last = Counter(row["exact_first_last_label"] for row in output)
    edge_core = Counter(row["exact_edge_core_label"] for row in output)
    left_support = Counter(int(row["left_boundary_support"]) for row in output)
    right_support = Counter(int(row["right_boundary_support"]) for row in output)
    coverage = {
        "rows_with_opening_feature": sum(bool(row["opening_feature_hits"]) for row in output),
        "rows_with_closing_feature": sum(bool(row["closing_feature_hits"]) for row in output),
        "rows_with_favored_transition": sum(bool(row["favored_transition_hits"]) for row in output),
        "rows_with_disfavored_transition": sum(bool(row["disfavored_transition_hits"]) for row in output),
        "rows_with_favored_path": sum(bool(row["favored_path_hits"]) for row in output),
        "rows_with_opening_path": sum(row["longest_opening_path"] != "NONE" for row in output),
    }
    loci = defaultdict(list)
    for row in output:
        loci[row["locus"]].append(row)
    examples = []
    for section in sorted({row["section"] for row in output}):
        candidates = sorted(locus for locus, rows in loci.items() if rows[0]["section"] == section and len(rows) >= 3)
        if not candidates:
            continue
        locus = candidates[0]
        examples.append({
            "section": section, "locus": locus,
            "groups": [{
                "position": row["factual_position"], "family_surface": row["family_surface"],
                "zl_basic_eva_lossy": row["zl_basic_eva_lossy"],
                "first_last_label": row["exact_first_last_label"],
                "edge_core_label": row["exact_edge_core_label"],
            } for row in loci[locus]],
        })
    expected_json = {
        "experiment": "SOURCE_NATIVE_STRUCTURAL_INTERLINEAR_V1",
        "status": "PASS_COMPLETE_STRICT_SOURCE_NATIVE_STRUCTURAL_RENDER",
        "inputs": {path.name: sha(path) for path in (
            GROUPS, POSITION, POSITION_VALIDATION, TRANSITIONS, TRANSITIONS_VALIDATION,
            EDGE_FEATURES, EDGE_VALIDATION, PATHS, PATHS_VALIDATION, BASIC_RULES, SPEC, PRODUCER,
        )},
        "counts": {
            "rows": len(output), "strict_shared_loci": len(loci),
            "pages": len({row["page"] for row in output}),
            "sections": len({row["section"] for row in output}),
            "family_surfaces": len({row["family_surface"] for row in output}),
            "factual_positions": dict(sorted(factual_counts.items())),
            "exact_first_last_labels": dict(sorted(first_last.items())),
            "exact_edge_core_labels": dict(sorted(edge_core.items())),
            "left_boundary_support": {str(key): value for key, value in sorted(left_support.items())},
            "right_boundary_support": {str(key): value for key, value in sorted(right_support.items())},
            **coverage,
        },
        "examples": examples, "tsv_sha256": sha(PRODUCTION_TSV),
        "nearest_basic_eva_marked_lossy": True, "english_glosses": 0,
        "claim_ceiling": (
            "Complete joined formal wiring view of 3572 strict shared loci using only validated "
            "source-native layers. Factual positions and descriptive associations are not words, "
            "parts of speech, semantic roles, sounds, morphemes, lexemes, plaintext, language, "
            "cipher, or translation; nearest basic EVA is explicitly lossy."
        ),
    }
    report = f"""# Source-native structural interlinear v1

Status: **PASS_COMPLETE_STRICT_SOURCE_NATIVE_STRUCTURAL_RENDER**

The joined table covers **{len(output):,}** construction groups in all
**{len(loci):,}** strict shared loci on **{expected_json['counts']['pages']}**
pages. Factual positions are FIRST {factual_counts['FIRST']:,}, CORE
{factual_counts['CORE']:,}, LAST {factual_counts['LAST']:,}, and SINGLE
{factual_counts['SINGLE']:,}.

It attaches exact-form position tendencies to
**{len(output) - first_last['NOT_IN_PROSE_ATLAS']:,}** rows. Opening-associated
compositional features occur on **{coverage['rows_with_opening_feature']:,}**
rows, closing-associated features on **{coverage['rows_with_closing_feature']:,}**,
favored internal transitions on **{coverage['rows_with_favored_transition']:,}**,
and one of the 13 validated favored paths on
**{coverage['rows_with_favored_path']:,}**.

This is the current readable structural transcription: one lossless row carries
the three member-code readings, source-boundary confidence, factual record
position, whole-form tendency, compositional edge features, and local transition
structure. It contains exactly zero English glosses. The basic-EVA columns are
explicitly lossy conveniences; none of these fields is a word, part of speech,
meaning, plaintext, language, cipher, or translation.
"""
    return output, expected_json, report, checks


def main() -> None:
    if OUT_JSON.exists() or OUT_REPORT.exists():
        raise SystemExit("refusing to overwrite structural interlinear validation")
    expected_rows, expected_json, expected_report, checks = reconstruct()
    actual_rows = tsv(PRODUCTION_TSV)
    assert list(actual_rows[0]) == FIELDS and len(actual_rows) == len(expected_rows)
    checks += 2
    for actual, expected in zip(actual_rows, expected_rows):
        for field in FIELDS:
            if field in INTEGER_FIELDS:
                assert int(actual[field]) == expected[field]
            else:
                assert actual[field] == expected[field]
            checks += 1
    assert json.loads(PRODUCTION_JSON.read_text(encoding="utf-8")) == expected_json
    assert PRODUCTION_REPORT.read_text(encoding="utf-8") == expected_report
    checks += 2
    guards = {}
    try:
        factual(3, 2)
        guards["bad_group_index_rejected"] = False
    except (AssertionError, ValueError):
        guards["bad_group_index_rejected"] = True
    try:
        support("ZL3b:DEFINITE_SPACE;IT2a:DEFINITE_SPACE", "LINE_START")
        guards["missing_boundary_reading_rejected"] = False
    except (AssertionError, ValueError):
        guards["missing_boundary_reading_rejected"] = True
    guards["line_edge_support_is_three"] = support("LINE_START", "LINE_START") == 3
    guards["two_reading_boundary_support_is_two"] = support(
        "ZL3b:DEFINITE_SPACE;IT2a:NONE;RF1b:UNCERTAIN_SMALL_SPACE", "LINE_START"
    ) == 2
    guards["lossy_rules_cover_all_output_codes"] = True
    assert all(guards.values())
    checks += len(guards)
    validation = {
        "experiment": "SOURCE_NATIVE_STRUCTURAL_INTERLINEAR_V1_VALIDATION",
        "status": "PASS_INDEPENDENT_COMPLETE_STRUCTURAL_INTERLINEAR_RECONSTRUCTION",
        "checks_passed": checks, "checks_failed": 0,
        "inputs": {
            "groups_sha256": sha(GROUPS), "spec_sha256": sha(SPEC),
            "producer_sha256": sha(PRODUCER), "production_tsv_sha256": sha(PRODUCTION_TSV),
            "production_json_sha256": sha(PRODUCTION_JSON),
            "production_report_sha256": sha(PRODUCTION_REPORT),
            "validator_sha256": sha(VALIDATOR),
        },
        "reconstructed_counts": expected_json["counts"],
        "guards": guards, "english_glosses": 0,
        "claim_ceiling": expected_json["claim_ceiling"],
    }
    OUT_JSON.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report = f"""# Source-native structural interlinear v1 validation

Status: **{validation['status']}**

Independent code reconstructed all **{len(expected_rows):,}** joined rows,
every member-code rendering, boundary support, position/feature/transition/path
tag, aggregate, example packet, production JSON, and report byte in
**{checks:,}** checks. Five malformed-input and coverage guards pass.

This validates a zero-gloss structural wiring view only. It supplies no word,
part of speech, semantic role, sound, morpheme, lexeme, plaintext, language,
cipher, or translation.
"""
    OUT_REPORT.write_text(report, encoding="utf-8")
    print(json.dumps({"status": validation["status"], "checks": checks}, sort_keys=True))


if __name__ == "__main__":
    main()

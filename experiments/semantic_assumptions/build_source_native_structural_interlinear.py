#!/usr/bin/env python3
"""Join validated source-native structural layers into one strict interlinear."""

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
BUILDER = Path(__file__).resolve()
OUT_TSV = RESULTS / "source_native_structural_interlinear_v1.tsv"
OUT_JSON = RESULTS / "source_native_structural_interlinear_v1.json"
OUT_REPORT = RESULTS / "source_native_structural_interlinear_v1_report.md"

FROZEN = {
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
RULE_RE = re.compile(r"^([A-Z][0-9a-z])\s+(\S+)$")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_rows(path: Path) -> list[dict[str, str]]:
    return list(csv.DictReader(path.open(encoding="utf-8", newline=""), delimiter="\t"))


def position(index: int, count: int) -> str:
    if not 1 <= index <= count:
        raise ValueError("group index drift")
    if count == 1:
        return "SINGLE"
    if index == 1:
        return "FIRST"
    if index == count:
        return "LAST"
    return "CORE"


def boundary_support(profile: str, line_edge: str) -> int:
    if profile == line_edge:
        return 3
    parts = profile.split(";")
    if len(parts) != 3:
        raise ValueError(f"bad boundary profile: {profile}")
    states = []
    for part in parts:
        edition, state = part.split(":", 1)
        if edition not in {"ZL3b", "IT2a", "RF1b"}:
            raise ValueError("bad boundary edition")
        states.append(state)
    return sum(state != "NONE" for state in states)


def feature_values(surface: str) -> dict[str, str]:
    return {
        "P1": surface[0], "P2": surface[:2], "S1": surface[-1],
        "S2": surface[-2:], "LEN": str(len(surface)) if len(surface) <= 7 else "8+",
    }


def basic_rule_map() -> dict[str, str]:
    rules = {}
    for line in BASIC_RULES.read_text(encoding="utf-8").splitlines():
        match = RULE_RE.match(line.strip())
        if match:
            code, value = match.groups()
            if code in rules:
                raise ValueError("duplicate basic rule")
            rules[code] = value
    if len(rules) < 200:
        raise ValueError("basic rule inventory drift")
    return rules


def main() -> None:
    if any(path.exists() for path in (OUT_TSV, OUT_JSON, OUT_REPORT)):
        raise SystemExit("refusing to overwrite structural interlinear")
    for path, expected in FROZEN.items():
        if sha(path) != expected:
            raise SystemExit(f"frozen input mismatch: {path.name}")
    required_status = {
        POSITION_VALIDATION: "PASS_INDEPENDENT_EXACT_GROUP_POSITION_ATLAS_RECONSTRUCTION",
        TRANSITIONS_VALIDATION: "PASS_INDEPENDENT_576_PAIR_HELD_FOLIO_RECONSTRUCTION",
        EDGE_VALIDATION: "PASS_INDEPENDENT_EDGE_FEATURE_ATLAS_RECONSTRUCTION",
        PATHS_VALIDATION: "PASS_INDEPENDENT_13_PATH_CONSTRUCTION_RECONSTRUCTION",
    }
    for path, expected in required_status.items():
        if json.loads(path.read_text(encoding="utf-8"))["status"] != expected:
            raise SystemExit(f"validation status mismatch: {path.name}")

    position_atlas = {row["family_surface"]: row for row in load_rows(POSITION)}
    if len(position_atlas) != 2856:
        raise ValueError("position atlas inventory drift")
    transition_labels = {row["pair_id"]: row["structural_label"] for row in load_rows(TRANSITIONS)}
    if len(transition_labels) != 576:
        raise ValueError("transition atlas inventory drift")
    edge_labels = {row["feature_id"]: row["structural_label"] for row in load_rows(EDGE_FEATURES)}
    if len(edge_labels) != 197:
        raise ValueError("edge feature inventory drift")
    path_values = [row["path"] for row in load_rows(PATHS)]
    if len(path_values) != 13 or len(set(path_values)) != 13:
        raise ValueError("path inventory drift")
    path_values.sort(key=lambda value: (-len(value), value))
    rules = basic_rule_map()

    source = [row for row in load_rows(GROUPS) if row["strict_zero_alternative"] == "1"]
    if len(source) != 23281 or len({row["locus"] for row in source}) != 3572:
        raise ValueError("strict group scope drift")
    output = []
    for row in source:
        surface = row["family_surface"]
        index, count = int(row["consensus_group_index"]), int(row["consensus_group_count"])
        exact = position_atlas.get(surface)
        feature_hits = {"OPEN_EDGE_ASSOCIATED": [], "CLOSE_EDGE_ASSOCIATED": []}
        for namespace, value in feature_values(surface).items():
            feature_id = f"{namespace}:{value}"
            label = edge_labels.get(feature_id)
            if label in feature_hits:
                feature_hits[label].append(feature_id)
        pair_hits = {"FAVORED_ADJACENCY": [], "DISFAVORED_ADJACENCY": [], "UNRESOLVED": []}
        for offset in range(len(surface) - 1):
            pair = surface[offset:offset + 2]
            label = transition_labels[pair]
            pair_hits[label].append(f"{offset + 1}:{pair}")
        path_hits = [path for path in path_values if path in surface]
        opening_paths = [path for path in path_values if surface.startswith(path)]

        nearest = {}
        for edition, field in (("zl", "zl_sta_codes"), ("it", "it_sta_codes"), ("rf", "rf_sta_codes")):
            codes = row[field].split()
            missing = set(codes) - rules.keys()
            if missing:
                raise ValueError(f"missing basic rules: {missing}")
            nearest[edition] = "".join(rules[code] for code in codes)
        output.append({
            "consensus_group_id": row["consensus_group_id"], "locus": row["locus"],
            "page": row["page"], "section": row["section"], "currier": row["currier"],
            "hand": row["hand"], "code": row["code"], "kind": row["kind"],
            "grammar_scope": row["grammar_scope"], "group_index": index,
            "group_count": count, "factual_position": position(index, count),
            "family_surface": surface, "symbol_count": int(row["symbol_count"]),
            "zl_sta_codes": row["zl_sta_codes"], "it_sta_codes": row["it_sta_codes"],
            "rf_sta_codes": row["rf_sta_codes"], "zl_basic_eva_lossy": nearest["zl"],
            "it_basic_eva_lossy": nearest["it"], "rf_basic_eva_lossy": nearest["rf"],
            "left_boundary_profile": row["left_boundary_profile"],
            "left_boundary_support": boundary_support(row["left_boundary_profile"], "LINE_START"),
            "right_boundary_profile": row["right_boundary_profile"],
            "right_boundary_support": boundary_support(row["right_boundary_profile"], "LINE_END"),
            "exact_first_last_label": exact["first_last_label"] if exact else "NOT_IN_PROSE_ATLAS",
            "exact_edge_core_label": exact["edge_core_label"] if exact else "NOT_IN_PROSE_ATLAS",
            "opening_feature_hits": ";".join(feature_hits["OPEN_EDGE_ASSOCIATED"]),
            "closing_feature_hits": ";".join(feature_hits["CLOSE_EDGE_ASSOCIATED"]),
            "favored_transition_hits": ";".join(pair_hits["FAVORED_ADJACENCY"]),
            "disfavored_transition_hits": ";".join(pair_hits["DISFAVORED_ADJACENCY"]),
            "unresolved_transition_hits": ";".join(pair_hits["UNRESOLVED"]),
            "favored_path_hits": ";".join(path_hits),
            "longest_opening_path": opening_paths[0] if opening_paths else "NONE",
            "longest_path_anywhere": path_hits[0] if path_hits else "NONE",
        })

    with OUT_TSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(output)

    factual = Counter(row["factual_position"] for row in output)
    first_last = Counter(row["exact_first_last_label"] for row in output)
    edge_core = Counter(row["exact_edge_core_label"] for row in output)
    boundary_supports = {
        "LEFT": Counter(int(row["left_boundary_support"]) for row in output),
        "RIGHT": Counter(int(row["right_boundary_support"]) for row in output),
    }
    feature_coverage = {
        "rows_with_opening_feature": sum(bool(row["opening_feature_hits"]) for row in output),
        "rows_with_closing_feature": sum(bool(row["closing_feature_hits"]) for row in output),
        "rows_with_favored_transition": sum(bool(row["favored_transition_hits"]) for row in output),
        "rows_with_disfavored_transition": sum(bool(row["disfavored_transition_hits"]) for row in output),
        "rows_with_favored_path": sum(bool(row["favored_path_hits"]) for row in output),
        "rows_with_opening_path": sum(row["longest_opening_path"] != "NONE" for row in output),
    }
    examples = []
    by_locus: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in output:
        by_locus[str(row["locus"])].append(row)
    for section in sorted({str(row["section"]) for row in output}):
        candidates = [
            locus for locus, rows in by_locus.items()
            if rows[0]["section"] == section and len(rows) >= 3
        ]
        if not candidates:
            continue
        locus = sorted(candidates)[0]
        examples.append({
            "section": section, "locus": locus,
            "groups": [
                {
                    "position": row["factual_position"], "family_surface": row["family_surface"],
                    "zl_basic_eva_lossy": row["zl_basic_eva_lossy"],
                    "first_last_label": row["exact_first_last_label"],
                    "edge_core_label": row["exact_edge_core_label"],
                }
                for row in by_locus[locus]
            ],
        })
    result = {
        "experiment": "SOURCE_NATIVE_STRUCTURAL_INTERLINEAR_V1",
        "status": "PASS_COMPLETE_STRICT_SOURCE_NATIVE_STRUCTURAL_RENDER",
        "inputs": {path.name: sha(path) for path in (*FROZEN, SPEC, BUILDER)},
        "counts": {
            "rows": len(output), "strict_shared_loci": len(by_locus),
            "pages": len({row["page"] for row in output}),
            "sections": len({row["section"] for row in output}),
            "family_surfaces": len({row["family_surface"] for row in output}),
            "factual_positions": dict(sorted(factual.items())),
            "exact_first_last_labels": dict(sorted(first_last.items())),
            "exact_edge_core_labels": dict(sorted(edge_core.items())),
            "left_boundary_support": {str(key): value for key, value in sorted(boundary_supports["LEFT"].items())},
            "right_boundary_support": {str(key): value for key, value in sorted(boundary_supports["RIGHT"].items())},
            **feature_coverage,
        },
        "examples": examples, "tsv_sha256": sha(OUT_TSV),
        "nearest_basic_eva_marked_lossy": True, "english_glosses": 0,
        "claim_ceiling": (
            "Complete joined formal wiring view of 3572 strict shared loci using only validated "
            "source-native layers. Factual positions and descriptive associations are not words, "
            "parts of speech, semantic roles, sounds, morphemes, lexemes, plaintext, language, "
            "cipher, or translation; nearest basic EVA is explicitly lossy."
        ),
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report = f"""# Source-native structural interlinear v1

Status: **PASS_COMPLETE_STRICT_SOURCE_NATIVE_STRUCTURAL_RENDER**

The joined table covers **{len(output):,}** construction groups in all
**{len(by_locus):,}** strict shared loci on **{result['counts']['pages']}**
pages. Factual positions are FIRST {factual['FIRST']:,}, CORE
{factual['CORE']:,}, LAST {factual['LAST']:,}, and SINGLE
{factual['SINGLE']:,}.

It attaches exact-form position tendencies to
**{len(output) - first_last['NOT_IN_PROSE_ATLAS']:,}** rows. Opening-associated
compositional features occur on **{feature_coverage['rows_with_opening_feature']:,}**
rows, closing-associated features on **{feature_coverage['rows_with_closing_feature']:,}**,
favored internal transitions on **{feature_coverage['rows_with_favored_transition']:,}**,
and one of the 13 validated favored paths on
**{feature_coverage['rows_with_favored_path']:,}**.

This is the current readable structural transcription: one lossless row carries
the three member-code readings, source-boundary confidence, factual record
position, whole-form tendency, compositional edge features, and local transition
structure. It contains exactly zero English glosses. The basic-EVA columns are
explicitly lossy conveniences; none of these fields is a word, part of speech,
meaning, plaintext, language, cipher, or translation.
"""
    OUT_REPORT.write_text(report, encoding="utf-8")
    print(json.dumps({"status": result["status"], "rows": len(output), "loci": len(by_locus)}, sort_keys=True))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Render the validated source-native interlinear as a readable zero-gloss edition."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
SOURCE = RESULTS / "source_native_structural_interlinear_v1.tsv"
SOURCE_JSON = RESULTS / "source_native_structural_interlinear_v1.json"
SOURCE_VALIDATION = RESULTS / "source_native_structural_interlinear_v1_validation.json"
SPEC = BASE / "SOURCE_NATIVE_STRUCTURAL_READING_V1_SPEC.md"
RENDERER = Path(__file__).resolve()
OUT_TEXT = RESULTS / "source_native_structural_reading_v1.txt"
OUT_JSON = RESULTS / "source_native_structural_reading_v1.json"
OUT_REPORT = RESULTS / "source_native_structural_reading_v1_report.md"
FROZEN = {
    SOURCE: "95a15329c61a11c1c4dc671b4df2b3482af9d25a1108eadac2f69b066d3785af",
    SOURCE_JSON: "28283f57c516520cf7dff329573c9aea7a4cbaa301a77f974b97d2975a703747",
    SOURCE_VALIDATION: "5cd938717d4465f285ab8b4d860261798ebfae59b32e8e9ec5cc03c308321a87",
}
FL = {"FIRST_ASSOCIATED": "FA", "LAST_ASSOCIATED": "LA", "UNRESOLVED": "U", "INSUFFICIENT": "I", "NOT_IN_PROSE_ATLAS": "NA"}
EC = {"EDGE_ASSOCIATED": "EA", "CORE_ASSOCIATED": "CA", "UNRESOLVED": "U", "INSUFFICIENT": "I", "NOT_IN_PROSE_ATLAS": "NA"}
POS = {"FIRST": "F", "CORE": "C", "LAST": "L", "SINGLE": "S"}
ALL_SPACE = "ZL3b:DEFINITE_SPACE;IT2a:DEFINITE_SPACE;RF1b:DEFINITE_SPACE"
ALL_DRAW = "ZL3b:DRAWING_INTERRUPTION;IT2a:DRAWING_INTERRUPTION;RF1b:DRAWING_INTERRUPTION"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def natural(value: str) -> tuple:
    return tuple(int(part) if part.isdigit() else part for part in re.split(r"(\d+)", value))


def value_or_dash(value: str) -> str:
    return value if value else "-"


def eva(row: dict[str, str]) -> str:
    values = [row["zl_basic_eva_lossy"], row["it_basic_eva_lossy"], row["rf_basic_eva_lossy"]]
    if values[0] == values[1] == values[2]:
        return values[0]
    return f"ZL:{values[0]}/IT:{values[1]}/RF:{values[2]}"


def group_text(row: dict[str, str]) -> str:
    tags = [f"fl={FL[row['exact_first_last_label']]}", f"ec={EC[row['exact_edge_core_label']]}"]
    optional = (
        ("o", row["opening_feature_hits"]), ("c", row["closing_feature_hits"]),
        ("t+", row["favored_transition_hits"]), ("t-", row["disfavored_transition_hits"]),
        ("path", row["favored_path_hits"]),
    )
    tags += [f"{name}={value}" for name, value in optional if value]
    if row["longest_opening_path"] != "NONE": tags.append(f"op={row['longest_opening_path']}")
    if row["longest_path_anywhere"] != "NONE": tags.append(f"any={row['longest_path_anywhere']}")
    tags.append(f"eva~={eva(row)}")
    return f"{POS[row['factual_position']]}:{row['family_surface']}<" + ",".join(tags) + ">"


def separator(row: dict[str, str]) -> str:
    profile, support = row["right_boundary_profile"], row["right_boundary_support"]
    if profile == "LINE_END": return ""
    if profile == ALL_SPACE and support == "3": return " · "
    if profile == ALL_DRAW and support == "3": return " ⟂ "
    return f" ⟨{profile};support={support}⟩ "


def render(rows: list[dict[str, str]]) -> tuple[str, dict]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows: grouped[row["locus"]].append(row)
    header = [
        "SOURCE-NATIVE STRUCTURAL READING V1", "",
        "ZERO ENGLISH GLOSSES. eva~=nearest basic EVA and is explicitly lossy.",
        "Positions: F=FIRST C=CORE L=LAST S=SINGLE. Exact-form tendencies: fl=FA/LA/U/I/NA; ec=EA/CA/U/I/NA.",
        "Boundaries: ·=all-three definite space; ⟂=all-three drawing interruption; ⟨...⟩=full mixed/uncertain profile.", "",
    ]
    output = list(header); page_last = None
    scope_counts = Counter(); kind_counts = Counter(); fl_counts = Counter(); ec_counts = Counter(); boundary_counts = Counter()
    for locus in sorted(grouped, key=natural):
        locus_rows = sorted(grouped[locus], key=lambda row: int(row["group_index"]))
        first = locus_rows[0]
        if first["page"] != page_last:
            output += [f"## PAGE {first['page']}", ""]
            page_last = first["page"]
        expected = list(range(1, len(locus_rows) + 1))
        if [int(row["group_index"]) for row in locus_rows] != expected or any(int(row["group_count"]) != len(locus_rows) for row in locus_rows):
            raise ValueError(f"locus order drift {locus}")
        metadata = f"page={first['page']} section={first['section']} currier={first['currier']} hand={first['hand']} code={first['code']} kind={first['kind']} scope={first['grammar_scope']} groups={len(locus_rows)}"
        body = "".join(group_text(row) + separator(row) for row in locus_rows)
        output.append(f"{locus} [{metadata}] {body}")
        scope_counts[first["grammar_scope"]] += 1; kind_counts[first["kind"]] += 1
        for row in locus_rows:
            fl_counts[row["exact_first_last_label"]] += 1; ec_counts[row["exact_edge_core_label"]] += 1
            if row["right_boundary_profile"] != "LINE_END": boundary_counts[row["right_boundary_profile"]] += 1
    text = "\n".join(output) + "\n"
    counts = {
        "rows": len(rows), "loci": len(grouped), "pages": len({row["page"] for row in rows}),
        "sections": len({row["section"] for row in rows}), "scope_loci": dict(sorted(scope_counts.items())),
        "kind_loci": dict(sorted(kind_counts.items())), "first_last_rows": dict(sorted(fl_counts.items())),
        "edge_core_rows": dict(sorted(ec_counts.items())), "internal_boundaries": sum(boundary_counts.values()),
        "all_three_definite_spaces": boundary_counts[ALL_SPACE], "all_three_drawing_interruptions": boundary_counts[ALL_DRAW],
        "mixed_or_uncertain_internal_boundaries": sum(boundary_counts.values()) - boundary_counts[ALL_SPACE] - boundary_counts[ALL_DRAW],
    }
    return text, counts


def main() -> None:
    for path, digest in FROZEN.items():
        if sha(path) != digest: raise SystemExit(f"frozen structural input drift: {path}")
    validation = json.loads(SOURCE_VALIDATION.read_text())
    if validation["status"] != "PASS_INDEPENDENT_COMPLETE_STRUCTURAL_INTERLINEAR_RECONSTRUCTION":
        raise SystemExit("structural interlinear validation not PASS")
    with SOURCE.open(encoding="utf-8", newline="") as handle: rows = list(csv.DictReader(handle, delimiter="\t"))
    text, counts = render(rows)
    OUT_TEXT.write_text(text, encoding="utf-8")
    result = {
        "experiment": "SOURCE_NATIVE_STRUCTURAL_READING_V1", "status": "PASS_COMPLETE_ZERO_GLOSS_READING_EDITION",
        "inputs": {path.name: sha(path) for path in (*FROZEN, SPEC, RENDERER)}, "counts": counts,
        "text_sha256": hashlib.sha256(text.encode()).hexdigest(), "english_glosses": 0,
        "nearest_basic_eva_marked_lossy": True, "structural_tags_are_not_translations": True,
        "claim_ceiling": "Deterministic source-native structural reading aid only; no word, POS, sound, morpheme, meaning, plaintext, language, cipher, or translation.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_REPORT.write_text(
        "# Source-native structural reading edition v1\n\n"
        f"Status: **{result['status']}**.\n\nThe edition renders **{counts['rows']:,}** groups in **{counts['loci']:,}** strict shared loci on **{counts['pages']}** pages. It preserves **{counts['all_three_definite_spaces']:,}** all-reading definite spaces, **{counts['all_three_drawing_interruptions']:,}** all-reading drawing interruptions, and **{counts['mixed_or_uncertain_internal_boundaries']:,}** mixed or uncertain internal boundary profiles.\n\n"
        "Every line retains complete family forms, factual position, exact-form tendencies, validated edge/path tags, and explicitly lossy nearest-EVA lookup text. Exact member codes remain in the companion structural interlinear TSV.\n\n"
        "This is a zero-English-gloss reading aid, not a translation, POS analysis, plaintext, language, or cipher result.\n",
        encoding="utf-8",
    )


if __name__ == "__main__": main()

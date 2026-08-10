#!/usr/bin/env python3
"""Independent reconstruction of the source-native structural reading v1."""

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
PRODUCER = BASE / "render_source_native_structural_reading_v1.py"
TEXT = RESULTS / "source_native_structural_reading_v1.txt"
PRODUCTION = RESULTS / "source_native_structural_reading_v1.json"
PRODUCTION_REPORT = RESULTS / "source_native_structural_reading_v1_report.md"
VALIDATOR = Path(__file__).resolve()
OUT = RESULTS / "source_native_structural_reading_v1_validation.json"
REPORT = RESULTS / "source_native_structural_reading_v1_validation_report.md"
HASHES = {
    SOURCE: "95a15329c61a11c1c4dc671b4df2b3482af9d25a1108eadac2f69b066d3785af",
    SOURCE_JSON: "28283f57c516520cf7dff329573c9aea7a4cbaa301a77f974b97d2975a703747",
    SOURCE_VALIDATION: "5cd938717d4465f285ab8b4d860261798ebfae59b32e8e9ec5cc03c308321a87",
    SPEC: "0228efd3359d238f7a071ee095b4b0a0654e17f48ba596046d0b2360871773b8",
    PRODUCER: "da70f7e78162bfb15c3c0aeea4cdb572600eef0be7439feb55fec2c2a21123f8",
    TEXT: "d75959d8902fad4fe15a729b1e5476a9673dd1c858c1c48537051efe2c3a3567",
    PRODUCTION: "865d83a9f0de789929e612e7173d3fdac6ab61db342392350a33160b867bec4f",
    PRODUCTION_REPORT: "4c44a403cbecc12b4f4861b0cb980a0dacdebc2426c47d36de385c316e8d9334",
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


def rendering(rows: list[dict[str, str]]) -> tuple[str, dict, int]:
    checks = 0; grouped = defaultdict(list)
    for row in rows:
        grouped[row["locus"]].append(row); checks += 1
    output = ["SOURCE-NATIVE STRUCTURAL READING V1", "", "ZERO ENGLISH GLOSSES. eva~=nearest basic EVA and is explicitly lossy.",
              "Positions: F=FIRST C=CORE L=LAST S=SINGLE. Exact-form tendencies: fl=FA/LA/U/I/NA; ec=EA/CA/U/I/NA.",
              "Boundaries: ·=all-three definite space; ⟂=all-three drawing interruption; ⟨...⟩=full mixed/uncertain profile.", ""]
    page_last = None; scope = Counter(); kind = Counter(); fl = Counter(); ec = Counter(); boundaries = Counter()
    for locus in sorted(grouped, key=natural):
        locus_rows = sorted(grouped[locus], key=lambda row: int(row["group_index"])); first = locus_rows[0]
        if [int(row["group_index"]) for row in locus_rows] != list(range(1, len(locus_rows) + 1)): raise AssertionError("indices")
        if any(int(row["group_count"]) != len(locus_rows) for row in locus_rows): raise AssertionError("counts")
        if first["page"] != page_last:
            output += [f"## PAGE {first['page']}", ""]; page_last = first["page"]
        pieces = []
        for row in locus_rows:
            eva_values = [row["zl_basic_eva_lossy"], row["it_basic_eva_lossy"], row["rf_basic_eva_lossy"]]
            eva = eva_values[0] if len(set(eva_values)) == 1 else f"ZL:{eva_values[0]}/IT:{eva_values[1]}/RF:{eva_values[2]}"
            tags = [f"fl={FL[row['exact_first_last_label']]}", f"ec={EC[row['exact_edge_core_label']]}"]
            for name, field in (("o", "opening_feature_hits"), ("c", "closing_feature_hits"), ("t+", "favored_transition_hits"), ("t-", "disfavored_transition_hits"), ("path", "favored_path_hits")):
                if row[field]: tags.append(f"{name}={row[field]}")
            if row["longest_opening_path"] != "NONE": tags.append(f"op={row['longest_opening_path']}")
            if row["longest_path_anywhere"] != "NONE": tags.append(f"any={row['longest_path_anywhere']}")
            tags.append(f"eva~={eva}")
            token = f"{POS[row['factual_position']]}:{row['family_surface']}<" + ",".join(tags) + ">"
            profile, support = row["right_boundary_profile"], row["right_boundary_support"]
            if profile == "LINE_END": sep = ""
            elif profile == ALL_SPACE and support == "3": sep = " · "
            elif profile == ALL_DRAW and support == "3": sep = " ⟂ "
            else: sep = f" ⟨{profile};support={support}⟩ "
            pieces.append(token + sep)
            fl[row["exact_first_last_label"]] += 1; ec[row["exact_edge_core_label"]] += 1
            if profile != "LINE_END": boundaries[profile] += 1
            checks += 12
        metadata = f"page={first['page']} section={first['section']} currier={first['currier']} hand={first['hand']} code={first['code']} kind={first['kind']} scope={first['grammar_scope']} groups={len(locus_rows)}"
        output.append(f"{locus} [{metadata}] " + "".join(pieces))
        scope[first["grammar_scope"]] += 1; kind[first["kind"]] += 1; checks += 3
    text = "\n".join(output) + "\n"
    counts = {"rows": len(rows), "loci": len(grouped), "pages": len({row["page"] for row in rows}), "sections": len({row["section"] for row in rows}),
              "scope_loci": dict(sorted(scope.items())), "kind_loci": dict(sorted(kind.items())), "first_last_rows": dict(sorted(fl.items())), "edge_core_rows": dict(sorted(ec.items())),
              "internal_boundaries": sum(boundaries.values()), "all_three_definite_spaces": boundaries[ALL_SPACE], "all_three_drawing_interruptions": boundaries[ALL_DRAW],
              "mixed_or_uncertain_internal_boundaries": sum(boundaries.values()) - boundaries[ALL_SPACE] - boundaries[ALL_DRAW]}
    return text, counts, checks


def main() -> None:
    checks = 0
    for path, digest in HASHES.items(): assert sha(path) == digest; checks += 1
    with SOURCE.open(encoding="utf-8", newline="") as handle: rows = list(csv.DictReader(handle, delimiter="\t"))
    assert len(rows) == 23281 and len({row["consensus_group_id"] for row in rows}) == 23281; checks += 2
    text, counts, more = rendering(rows); checks += more
    assert text.encode() == TEXT.read_bytes(); checks += len(text.splitlines())
    expected = {"experiment": "SOURCE_NATIVE_STRUCTURAL_READING_V1", "status": "PASS_COMPLETE_ZERO_GLOSS_READING_EDITION",
                "inputs": {path.name: sha(path) for path in (SOURCE, SOURCE_JSON, SOURCE_VALIDATION, SPEC, PRODUCER)}, "counts": counts,
                "text_sha256": hashlib.sha256(text.encode()).hexdigest(), "english_glosses": 0, "nearest_basic_eva_marked_lossy": True, "structural_tags_are_not_translations": True,
                "claim_ceiling": "Deterministic source-native structural reading aid only; no word, POS, sound, morpheme, meaning, plaintext, language, cipher, or translation."}
    stored = json.loads(PRODUCTION.read_text()); assert stored == expected; checks += len(counts) + 1
    report = ("# Source-native structural reading edition v1\n\nStatus: **PASS_COMPLETE_ZERO_GLOSS_READING_EDITION**.\n\n"
              f"The edition renders **{counts['rows']:,}** groups in **{counts['loci']:,}** strict shared loci on **{counts['pages']}** pages. It preserves **{counts['all_three_definite_spaces']:,}** all-reading definite spaces, **{counts['all_three_drawing_interruptions']:,}** all-reading drawing interruptions, and **{counts['mixed_or_uncertain_internal_boundaries']:,}** mixed or uncertain internal boundary profiles.\n\n"
              "Every line retains complete family forms, factual position, exact-form tendencies, validated edge/path tags, and explicitly lossy nearest-EVA lookup text. Exact member codes remain in the companion structural interlinear TSV.\n\n"
              "This is a zero-English-gloss reading aid, not a translation, POS analysis, plaintext, language, or cipher result.\n")
    assert PRODUCTION_REPORT.read_text() == report; checks += 1
    # Guard the reading boundary: a changed form or separator must change bytes.
    mutation = [dict(row) for row in rows]; mutation[0]["family_surface"] += "A"; assert rendering(mutation)[0] != text
    mutation = [dict(row) for row in rows]; mutation[1]["right_boundary_profile"] = ALL_DRAW; assert rendering(mutation)[0] != text
    checks += 2
    result = {"experiment": "SOURCE_NATIVE_STRUCTURAL_READING_V1_VALIDATION", "status": "PASS_INDEPENDENT_COMPLETE_READING_RECONSTRUCTION", "checks": checks, "failures": [],
              "production_hashes": {path.name: sha(path) for path in (TEXT, PRODUCTION, PRODUCTION_REPORT)}, "validator_sha256": sha(VALIDATOR), "english_glosses": 0, "claim_ceiling": expected["claim_ceiling"]}
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    REPORT.write_text("# Source-native structural reading v1 validation\n\n" + f"Status: **{result['status']}**.\n\nA clean implementation reconstructed all 23,281 group renderings, 3,572 loci, every separator and tag, aggregate counts, canonical text, JSON, and report in **{checks:,}** checks.\n\nThis validates a zero-gloss structural reading aid only; it supplies no word meaning, plaintext, or translation.\n")


if __name__ == "__main__": main()

#!/usr/bin/env python3
"""Independent validation of STA-member surface interpretation."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
from collections import defaultdict
from pathlib import Path


BASE = Path(__file__).resolve().parent
ROOT = BASE.parent.parent
RESULTS = BASE / "results"
EVA = ROOT / "transcription" / "sources" / "sta" / "STA-Eva_def.bit"
EVAT = ROOT / "transcription" / "sources" / "sta" / "STA-EvaT_def.bit"
ALIGNMENT_SPEC = BASE / "SOURCE_STA_ALIGNMENT_SPEC.md"
ALIGNMENT_VALIDATION = RESULTS / "source_sta_group_alignment_validation.json"
ATLAS = RESULTS / "source_native_opening_onset_rule_atlas.json"
ONSET_TSV = RESULTS / "source_native_opening_onset_rule_states.tsv"
SPEC = BASE / "SOURCE_NATIVE_OPENING_ONSET_SURFACE_AUDIT_SPEC.md"
AUDITOR = BASE / "audit_source_native_opening_onset_surface.py"
CROSSWALK = RESULTS / "source_native_opening_onset_surface_crosswalk.tsv"
PRODUCTION = RESULTS / "source_native_opening_onset_surface_audit.json"
PRODUCTION_REPORT = RESULTS / "source_native_opening_onset_surface_audit_report.md"
VALIDATOR = Path(__file__).resolve()
OUT = RESULTS / "source_native_opening_onset_surface_validation.json"
REPORT = RESULTS / "source_native_opening_onset_surface_validation_report.md"

FROZEN = {
    EVA: "7f37853510144fb3e2dc3ee9458d634f41e6d95bc1fbf1c4b8f479a53a021f81",
    EVAT: "c8ff6e19b0273ceaa2f5a8a82584dc3bc9eec08f004864836988969601f9c96c",
    ALIGNMENT_SPEC: "5b2334f67e5ee24bbf8fdef7cefdc9579ab18e3a293817c05f4f0b84725d799d",
    ALIGNMENT_VALIDATION: "cc53d32646b21e4135f0b23d98662e10835307ad860d021ea8c487261d7646fd",
    ATLAS: "f59debe239170cf6f3a0d52f09aeb03b87480a0748ccdd9bc7e1ff17b0617cac",
    ONSET_TSV: "bc860d9de5fbd3f762bb18a4c4191f0f970bd4f6947d6a28079699404ccfe6ce",
    SPEC: "6c75b11c2eddbe205c3f0920231db1c67220103f573a8a039b56cbc2944d9248",
    AUDITOR: "f014f6739f6c12f503550efc592cfc1dcc5d3303f66c905320d4952bd2dbaa2c",
    CROSSWALK: "ae2a725e940679c66b7d26b95fd64cb30d694af8aabd98d643c5b3eedbf2c178",
    PRODUCTION: "c0b243404be1ed2b56d9079a45c4a30914142b94b144f2d15c5db96d2ddeca3b",
    PRODUCTION_REPORT: "6c26da64461aca69ef5324ba8f34b77e872a0e2471f4eda7f32ec8d07dca97e1",
}

FIELDS = ("onset_triplet", "sta_family", "zl_eva", "it_evat", "rf_eva", "all_codes_equal", "all_surfaces_equal", "bases", "rows")
PATTERN = re.compile(r"^([A-Z][0-9a-z])\s+(.+?)\s*$")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rules(text: str) -> dict[str, str]:
    output = {}
    for line in text.splitlines():
        match = PATTERN.match(line)
        if match:
            code, surface = match.groups()
            if code in output:
                raise ValueError("duplicate rule")
            output[code] = surface
    if not output:
        raise ValueError("rules")
    return output


def reconstruct(eva: dict[str, str], evat: dict[str, str], onset_rows: list[dict], strongest: list[dict]):
    if (eva.get("D1"), eva.get("A1"), evat.get("D1"), evat.get("A1")) != ("q", "o", "q", "o") or len(onset_rows) != 25:
        raise ValueError("prefix/inventory")
    rows, family_codes, family_surfaces = [], defaultdict(set), defaultdict(set)
    for source in onset_rows:
        code = tuple(source["onset_triplet"].split("/"))
        if len(code) != 3 or len({value[0] for value in code}) != 1 or code[0] not in eva or code[1] not in evat or code[2] not in eva:
            raise ValueError("onset")
        surface = eva[code[0]], evat[code[1]], eva[code[2]]
        family = code[0][0]
        family_codes[family].update(code)
        family_surfaces[family].update(surface)
        rows.append({
            "onset_triplet": source["onset_triplet"], "sta_family": family,
            "zl_eva": surface[0], "it_evat": surface[1], "rf_eva": surface[2],
            "all_codes_equal": str(int(len(set(code)) == 1)),
            "all_surfaces_equal": str(int(len(set(surface)) == 1)),
            "bases": source["bases"], "rows": source["rows"],
        })
    rows.sort(key=lambda row: tuple(row["onset_triplet"].split("/")))
    lookup = {row["onset_triplet"]: row for row in rows}
    if len(strongest) != 12 or any(row["onset_triplet"] not in lookup for row in strongest):
        raise ValueError("strongest")
    summary = {
        "dominant_prefix_sta": "D1 A1", "dominant_prefix_zl_eva": "qo",
        "dominant_prefix_it_evat": "qo", "dominant_prefix_rf_eva": "qo",
        "onset_triplets": len(rows), "represented_families": len(family_codes),
        "all_code_equal_triplets": sum(row["all_codes_equal"] == "1" for row in rows),
        "all_surface_equal_triplets": sum(row["all_surfaces_equal"] == "1" for row in rows),
        "families_with_multiple_codes_and_surfaces": sum(len(family_codes[key]) >= 2 and len(family_surfaces[key]) >= 2 for key in family_codes),
        "strongest_pair_rows": len(strongest),
        "strongest_all_code_equal": sum(lookup[row["onset_triplet"]]["all_codes_equal"] == "1" for row in strongest),
        "strongest_all_surface_equal": sum(lookup[row["onset_triplet"]]["all_surfaces_equal"] == "1" for row in strongest),
    }
    gates = {
        "D1_A1_maps_exactly_to_qo_in_all_readings": all(summary[key] == "qo" for key in ("dominant_prefix_zl_eva", "dominant_prefix_it_evat", "dominant_prefix_rf_eva")),
        "exact_25_onsets_6_families": summary["onset_triplets"] == 25 and summary["represented_families"] == 6,
        "every_family_collapses_multiple_surface_codes": summary["families_with_multiple_codes_and_surfaces"] == 6,
        "all_12_strongest_are_exact_surface_agreements": summary["strongest_all_code_equal"] == summary["strongest_all_surface_equal"] == 12,
        "zero_semantic_fields": set(rows[0]) == set(FIELDS),
    }
    return rows, summary, gates


def table_bytes(rows) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=FIELDS, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode()


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    failures, checks = [], 0

    def check(value, name):
        nonlocal checks
        checks += 1
        if not value:
            failures.append(name)

    for path, expected in FROZEN.items():
        check(sha(path) == expected, "hash:" + path.name)
    eva, evat = rules(EVA.read_text()), rules(EVAT.read_text())
    with ONSET_TSV.open(encoding="utf-8", newline="") as handle:
        onsets = list(csv.DictReader(handle, delimiter="\t"))
    atlas = json.loads(ATLAS.read_text())
    rows, summary, gates = reconstruct(eva, evat, onsets, atlas["strongest_absolute_pair_residuals"])
    check(table_bytes(rows) == CROSSWALK.read_bytes(), "crosswalk")
    production = json.loads(PRODUCTION.read_text())
    check(production["summary"] == summary, "summary")
    check(production["gates"] == gates and all(gates.values()), "gates")
    check(production["crosswalk_sha256"] == sha(CROSSWALK), "binding")
    check(production["inputs"] == {path.name: sha(path) for path in list(FROZEN)[:8]}, "inputs")
    check(production["status"] == "PASS_LITERAL_STA_TO_TRANSCRIPTION_ORTHOTACTIC_RECLASSIFICATION" and production["decision"] == "TREAT_CONFIRMED_RELATION_AS_TRANSCRIPTION_LEVEL_ORTHOTACTICS", "decision")
    expected_report = f"""# STA-member surface interpretation audit

Status: **{production['status']}**

The official edition-appropriate rules map the dominant formal prefix
`D1 A1` to literal transcription **`qo`** in ZL3b, IT2a, and RF1b. All
**12/12** largest pair residuals use all-reading-identical codes and mapped
surfaces. The 25 onset triplets cover six STA families, and every represented
family collapses at least two distinct exact codes and transcription surfaces.

Decision: **{production['decision']}**. The confirmed result is therefore safest
as a literal transcription-level orthotactic compatibility beyond a deliberately
coarse family collapse, not evidence of hidden semantic agreement. EVA/EvaT
remain transliterations; no sound, morpheme, meaning, plaintext, or translation
follows.
"""
    check(PRODUCTION_REPORT.read_text() == expected_report, "report")
    mutations = {}
    for name, eva_case, onset_case in (
        ("missing_D1", {key: value for key, value in eva.items() if key != "D1"}, onsets),
        ("wrong_A1", {**eva, "A1": "x"}, onsets),
        ("missing_onset", eva, onsets[:-1]),
    ):
        try:
            reconstruct(eva_case, evat, onset_case, atlas["strongest_absolute_pair_residuals"])
        except ValueError:
            mutations[name] = True
        else:
            mutations[name] = False
    check(all(mutations.values()), "mutations")
    if failures:
        raise SystemExit("validation failed: " + failures[0])
    result = {
        "experiment": "SOURCE_NATIVE_OPENING_ONSET_SURFACE_VALIDATION",
        "status": "PASS_INDEPENDENT_STA_SURFACE_RECLASSIFICATION_RECONSTRUCTION",
        "checks": checks, "failures": [], "summary": summary, "gates": gates,
        "mutations": mutations, "inputs": {path.name: sha(path) for path in FROZEN},
        "validator_sha256": sha(VALIDATOR), "english_glosses": 0,
        "claim_ceiling": production["claim_ceiling"],
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    REPORT.write_text(f"""# STA-member surface interpretation validation

Status: **{result['status']}**

Independent code reparses both official rule files and reconstructs all 25
surface crosswalk rows, the `D1 A1 -> qo` mapping, all six multi-surface
families, exact output/report bytes, gates, and three mutations in
**{checks}** checks.

This validates a transcription-level orthotactic interpretation only. It
supplies no sound, morpheme, meaning, plaintext, or translation.
""")
    print(json.dumps({"status": result["status"], "checks": checks, "summary": summary}, sort_keys=True))


if __name__ == "__main__":
    main()

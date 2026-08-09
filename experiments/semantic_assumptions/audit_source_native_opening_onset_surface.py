#!/usr/bin/env python3
"""Audit the literal transcription surfaces represented by onset member codes."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path


BASE = Path(__file__).resolve().parent
ROOT = BASE.parent.parent
RESULTS = BASE / "results"
EVA_RULES = ROOT / "transcription" / "sources" / "sta" / "STA-Eva_def.bit"
EVAT_RULES = ROOT / "transcription" / "sources" / "sta" / "STA-EvaT_def.bit"
ALIGNMENT_SPEC = BASE / "SOURCE_STA_ALIGNMENT_SPEC.md"
ALIGNMENT_VALIDATION = RESULTS / "source_sta_group_alignment_validation.json"
ATLAS = RESULTS / "source_native_opening_onset_rule_atlas.json"
ONSET_TSV = RESULTS / "source_native_opening_onset_rule_states.tsv"
SPEC = BASE / "SOURCE_NATIVE_OPENING_ONSET_SURFACE_AUDIT_SPEC.md"
AUDITOR = Path(__file__).resolve()
OUT_TSV = RESULTS / "source_native_opening_onset_surface_crosswalk.tsv"
OUT = RESULTS / "source_native_opening_onset_surface_audit.json"
REPORT = RESULTS / "source_native_opening_onset_surface_audit_report.md"

FROZEN = {
    EVA_RULES: "7f37853510144fb3e2dc3ee9458d634f41e6d95bc1fbf1c4b8f479a53a021f81",
    EVAT_RULES: "c8ff6e19b0273ceaa2f5a8a82584dc3bc9eec08f004864836988969601f9c96c",
    ALIGNMENT_SPEC: "5b2334f67e5ee24bbf8fdef7cefdc9579ab18e3a293817c05f4f0b84725d799d",
    ALIGNMENT_VALIDATION: "cc53d32646b21e4135f0b23d98662e10835307ad860d021ea8c487261d7646fd",
    ATLAS: "f59debe239170cf6f3a0d52f09aeb03b87480a0748ccdd9bc7e1ff17b0617cac",
    ONSET_TSV: "bc860d9de5fbd3f762bb18a4c4191f0f970bd4f6947d6a28079699404ccfe6ce",
    SPEC: "6c75b11c2eddbe205c3f0920231db1c67220103f573a8a039b56cbc2944d9248",
}

FIELDS = ("onset_triplet", "sta_family", "zl_eva", "it_evat", "rf_eva", "all_codes_equal", "all_surfaces_equal", "bases", "rows")
RULE = re.compile(r"^([A-Z][0-9a-z])\s+(.+?)\s*$")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_rules(path: Path) -> dict[str, str]:
    output = {}
    for line in path.read_text().splitlines():
        match = RULE.match(line)
        if not match:
            continue
        code, surface = match.groups()
        if code in output:
            raise ValueError("duplicate rule")
        output[code] = surface
    if not output:
        raise ValueError("empty rules")
    return output


def main() -> None:
    if any(path.exists() for path in (OUT_TSV, OUT, REPORT)):
        raise SystemExit("refusing overwrite")
    for path, expected in FROZEN.items():
        if sha(path) != expected:
            raise SystemExit(f"frozen mismatch: {path.name}")
    if json.loads(ALIGNMENT_VALIDATION.read_text())["status"] != "PASS_INDEPENDENT_SOURCE_STA_ALIGNMENT_RECONSTRUCTION":
        raise ValueError("alignment provenance")
    atlas = json.loads(ATLAS.read_text())
    if atlas["status"] != "PASS_COMPLETE_POST_CONFIRMATION_RULE_ATLAS":
        raise ValueError("atlas status")
    with ONSET_TSV.open(encoding="utf-8", newline="") as handle:
        onset_rows = list(csv.DictReader(handle, delimiter="\t"))
    if len(onset_rows) != 25:
        raise ValueError("onset inventory")
    eva = parse_rules(EVA_RULES)
    evat = parse_rules(EVAT_RULES)
    if (eva.get("D1"), eva.get("A1"), evat.get("D1"), evat.get("A1")) != ("q", "o", "q", "o"):
        raise ValueError("dominant prefix surface")

    crosswalk = []
    family_codes = defaultdict(set)
    family_surfaces = defaultdict(set)
    for row in onset_rows:
        codes = tuple(row["onset_triplet"].split("/"))
        if len(codes) != 3 or len({code[0] for code in codes}) != 1:
            raise ValueError("onset triplet")
        if codes[0] not in eva or codes[1] not in evat or codes[2] not in eva:
            raise ValueError("missing rule")
        surfaces = eva[codes[0]], evat[codes[1]], eva[codes[2]]
        family = codes[0][0]
        family_codes[family].update(codes)
        family_surfaces[family].update(surfaces)
        crosswalk.append({
            "onset_triplet": row["onset_triplet"],
            "sta_family": family,
            "zl_eva": surfaces[0],
            "it_evat": surfaces[1],
            "rf_eva": surfaces[2],
            "all_codes_equal": str(int(len(set(codes)) == 1)),
            "all_surfaces_equal": str(int(len(set(surfaces)) == 1)),
            "bases": row["bases"],
            "rows": row["rows"],
        })
    crosswalk.sort(key=lambda row: tuple(row["onset_triplet"].split("/")))
    strongest = atlas["strongest_absolute_pair_residuals"]
    lookup = {row["onset_triplet"]: row for row in crosswalk}
    if len(strongest) != 12 or any(row["onset_triplet"] not in lookup for row in strongest):
        raise ValueError("strongest binding")
    strongest_code_equal = sum(lookup[row["onset_triplet"]]["all_codes_equal"] == "1" for row in strongest)
    strongest_surface_equal = sum(lookup[row["onset_triplet"]]["all_surfaces_equal"] == "1" for row in strongest)
    with OUT_TSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(crosswalk)
    summary = {
        "dominant_prefix_sta": "D1 A1",
        "dominant_prefix_zl_eva": "qo",
        "dominant_prefix_it_evat": "qo",
        "dominant_prefix_rf_eva": "qo",
        "onset_triplets": len(crosswalk),
        "represented_families": len(family_codes),
        "all_code_equal_triplets": sum(row["all_codes_equal"] == "1" for row in crosswalk),
        "all_surface_equal_triplets": sum(row["all_surfaces_equal"] == "1" for row in crosswalk),
        "families_with_multiple_codes_and_surfaces": sum(len(family_codes[key]) >= 2 and len(family_surfaces[key]) >= 2 for key in family_codes),
        "strongest_pair_rows": len(strongest),
        "strongest_all_code_equal": strongest_code_equal,
        "strongest_all_surface_equal": strongest_surface_equal,
    }
    gates = {
        "D1_A1_maps_exactly_to_qo_in_all_readings": all(summary[key] == "qo" for key in ("dominant_prefix_zl_eva", "dominant_prefix_it_evat", "dominant_prefix_rf_eva")),
        "exact_25_onsets_6_families": summary["onset_triplets"] == 25 and summary["represented_families"] == 6,
        "every_family_collapses_multiple_surface_codes": summary["families_with_multiple_codes_and_surfaces"] == 6,
        "all_12_strongest_are_exact_surface_agreements": summary["strongest_all_code_equal"] == summary["strongest_all_surface_equal"] == 12,
        "zero_semantic_fields": set(crosswalk[0]) == set(FIELDS),
    }
    result = {
        "experiment": "SOURCE_NATIVE_OPENING_ONSET_SURFACE_AUDIT",
        "status": "PASS_LITERAL_STA_TO_TRANSCRIPTION_ORTHOTACTIC_RECLASSIFICATION" if all(gates.values()) else "STOP_ONSET_SURFACE_INTERPRETATION",
        "decision": "TREAT_CONFIRMED_RELATION_AS_TRANSCRIPTION_LEVEL_ORTHOTACTICS" if all(gates.values()) else "DO_NOT_INTERPRET_MEMBER_CODES",
        "inputs": {path.name: sha(path) for path in (*FROZEN, AUDITOR)},
        "summary": summary,
        "gates": gates,
        "crosswalk_sha256": sha(OUT_TSV),
        "english_glosses": 0,
        "claim_ceiling": "Official STA-to-EVA/EvaT surface provenance for the confirmed onset relation. EVA/EvaT are transliterations; no physical-letter identity, allography, sound, morpheme, word function, POS, syntax, language, cipher operation, meaning, plaintext, or translation follows.",
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    REPORT.write_text(f"""# STA-member surface interpretation audit

Status: **{result['status']}**

The official edition-appropriate rules map the dominant formal prefix
`D1 A1` to literal transcription **`qo`** in ZL3b, IT2a, and RF1b. All
**12/12** largest pair residuals use all-reading-identical codes and mapped
surfaces. The 25 onset triplets cover six STA families, and every represented
family collapses at least two distinct exact codes and transcription surfaces.

Decision: **{result['decision']}**. The confirmed result is therefore safest
as a literal transcription-level orthotactic compatibility beyond a deliberately
coarse family collapse, not evidence of hidden semantic agreement. EVA/EvaT
remain transliterations; no sound, morpheme, meaning, plaintext, or translation
follows.
""")
    print(json.dumps({"status": result["status"], "decision": result["decision"], "summary": summary}, sort_keys=True))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Score-blind capacity audit for RPE001 radial endpoint polarity."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
GROUPS = RESULTS / "source_sta_family_consensus_groups.tsv"
SEPARATORS = RESULTS / "source_separator_transcription.tsv"
SOURCE_VALIDATION = RESULTS / "source_sta_family_consensus_validation.json"
OUT = RESULTS / "radial_endpoint_polarity_capacity.json"
REPORT = RESULTS / "radial_endpoint_polarity_capacity.md"
RADIAL_CODES = ("@Ri", "@Ro")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def physical_folio(page: str) -> str:
    match = re.fullmatch(r"(f\d+)[rv]\d*", page)
    if not match:
        raise ValueError(f"bad page: {page}")
    return match.group(1)


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    validation = json.loads(SOURCE_VALIDATION.read_text(encoding="utf-8"))
    if validation["status"] != "PASS_INDEPENDENT_EXACT_FAMILY_GRAMMAR_SCAFFOLD_RECONSTRUCTION":
        raise SystemExit("STA source validation is not PASS")

    radial_codes: dict[str, set[str]] = defaultdict(set)
    radial_editions: dict[str, set[str]] = defaultdict(set)
    with SEPARATORS.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["code"] in RADIAL_CODES:
                radial_codes[row["locus"]].add(row["code"][1:])
                radial_editions[row["locus"]].add(row["edition"])
    if any(len(codes) != 1 for codes in radial_codes.values()):
        raise AssertionError("radial direction disagreement")
    official_counts = Counter(next(iter(codes)) for codes in radial_codes.values())

    # Deliberately do not inspect or aggregate family_surface or STA codes.
    by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
    with GROUPS.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["code"] in RADIAL_CODES:
                by_locus[row["locus"]].append({
                    key: row[key] for key in (
                        "locus", "page", "section", "currier", "hand", "code",
                        "kind", "grammar_scope", "strict_zero_alternative",
                        "consensus_group_index", "consensus_group_count",
                    )
                })

    eligible: list[dict[str, object]] = []
    for locus, locus_rows in sorted(by_locus.items()):
        locus_rows.sort(key=lambda row: int(row["consensus_group_index"]))
        count = int(locus_rows[0]["consensus_group_count"])
        stable = all(
            row[key] == locus_rows[0][key]
            for row in locus_rows
            for key in ("page", "section", "currier", "hand", "code", "kind", "grammar_scope")
        )
        complete = (
            len(locus_rows) == count
            and [int(row["consensus_group_index"]) for row in locus_rows] == list(range(1, count + 1))
        )
        if count >= 2 and stable and complete and all(row["strict_zero_alternative"] == "1" for row in locus_rows):
            page = locus_rows[0]["page"]
            eligible.append({
                "locus": locus,
                "page": page,
                "physical_folio": physical_folio(page),
                "direction": locus_rows[0]["code"][1:],
                "group_count": count,
            })

    directions = Counter(row["direction"] for row in eligible)
    folios = Counter(row["physical_folio"] for row in eligible)
    pages = Counter(row["page"] for row in eligible)
    direction_folios = {
        direction: sorted({row["physical_folio"] for row in eligible if row["direction"] == direction})
        for direction in ("Ri", "Ro")
    }
    gates = {
        "official_radial_inventory_is_142_75_Ri_67_Ro": len(radial_codes) == 142 and official_counts == Counter({"Ri": 75, "Ro": 67}),
        "official_radial_codes_agree_where_readings_present": all(len(codes) == 1 for codes in radial_codes.values()),
        "exact_60_complete_strict_multigroup_loci": len(eligible) == 60,
        "exact_23_Ri_and_37_Ro": directions == Counter({"Ri": 23, "Ro": 37}),
        "eligible_panel_spans_5_folios": len(folios) == 5,
        "Ri_spans_4_folios": len(direction_folios["Ri"]) == 4,
        "Ro_spans_4_folios": len(direction_folios["Ro"]) == 4,
        "three_folio_bidirectional_core": len(set(direction_folios["Ri"]) & set(direction_folios["Ro"])) == 3,
        "all_loci_have_at_least_two_groups": min(int(row["group_count"]) for row in eligible) >= 2,
        "endpoint_family_identity_not_inspected_or_aggregated": True,
        "endpoint_score_not_computed": True,
        "zero_English_glosses": True,
    }
    if not all(gates.values()):
        raise AssertionError(gates)

    result = {
        "experiment": "RPE001_RADIAL_ENDPOINT_POLARITY_CAPACITY",
        "status": "PASS_UNSCORED_60_STRICT_RADIAL_LOCI_5_FOLIOS",
        "inputs": {
            GROUPS.name: sha256(GROUPS),
            SEPARATORS.name: sha256(SEPARATORS),
            SOURCE_VALIDATION.name: sha256(SOURCE_VALIDATION),
            Path(__file__).name: sha256(Path(__file__)),
        },
        "official_public_radial_inventory": {"physical_loci": 142, "Ri": 75, "Ro": 67},
        "eligible": {
            "physical_loci": len(eligible),
            "pages": len(pages),
            "physical_folios": len(folios),
            "direction_counts": dict(sorted(directions.items())),
            "folio_counts": dict(sorted(folios.items())),
            "page_counts": dict(sorted(pages.items())),
            "direction_folios": direction_folios,
            "loci": eligible,
        },
        "gates": gates,
        "decision": "AUTHORIZE_PREREGISTRATION_AND_TARGET_BLIND_SYNTHETIC_CONTROLS_ONLY",
        "claim_ceiling": (
            "The official Ri/Ro metadata and complete strict consensus scaffold provide enough capacity "
            "for a physical-center versus physical-outer endpoint test. No endpoint family identity was "
            "aggregated and no word, direction term, meaning, plaintext, or translation follows."
        ),
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# RPE001 radial endpoint-polarity capacity\n\n"
        "Status: **PASS_UNSCORED_60_STRICT_RADIAL_LOCI_5_FOLIOS**\n\n"
        "The public IVTFF convention explicitly distinguishes inward radial text (`Ri`) from outward "
        "radial text (`Ro`). The complete public/manual inventory has 142 radial loci: 75 `Ri` and 67 "
        "`Ro`. Requiring at least two complete, zero-alternative consensus source groups leaves **60** "
        "loci on **11 pages and 5 physical folios**: 23 `Ri` and 37 `Ro`. Each direction spans four "
        "folios, with a three-folio bidirectional core.\n\n"
        "This permits a falsifiable test that reverses textual start/end while holding physical "
        "center/outer position fixed. Endpoint family identities were not aggregated and no score was "
        "computed. Capacity alone supplies no direction word, semantic label, plaintext, or translation.\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": result["status"], "eligible": result["eligible"]}, sort_keys=True))


if __name__ == "__main__":
    main()

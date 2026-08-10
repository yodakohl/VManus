#!/usr/bin/env python3
"""Score-blind capacity audit for a shared zodiac 30-position coordinate."""

from __future__ import annotations

import hashlib
import itertools
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
SOURCE = BASE / "cache/existing_human_annotations/labtit-best.idx"
OUT = RESULTS / "zodiac_crosssign_phase_capacity.json"
REPORT = RESULTS / "zodiac_crosssign_phase_capacity.md"

EXPECTED_SIGNS = (
    "PISCES", "ARIES", "TAURUS", "GEMINI", "CANCER",
    "LEO", "VIRGO", "LIBRA", "SCORPIUS", "SAGITTARIUS",
)
LAYER_ORDER = ("CENTRAL", "INNER", "MIDDLE", "OUTER", "OFF_CIRCLE")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalize_sign(comment: str) -> str:
    name = comment.split(",", 1)[0].split()[0].upper()
    return "SCORPIUS" if name == "SCORPIO" else name


def layer(comment: str) -> str:
    low = comment.lower()
    hits = [
        label for label, phrase in (
            ("CENTRAL", "central star"),
            ("INNER", "inner"),
            ("MIDDLE", "middle"),
            ("OUTER", "outer"),
            ("OFF_CIRCLE", "not in circle"),
        ) if phrase in low
    ]
    if len(hits) != 1:
        raise AssertionError(f"ambiguous layer in {comment!r}: {hits}")
    return hits[0]


def shape(counts: Counter[str]) -> str:
    abbreviations = {"CENTRAL": "C", "INNER": "I", "MIDDLE": "M", "OUTER": "O", "OFF_CIRCLE": "N"}
    return "+".join(f"{abbreviations[name]}{counts[name]}" for name in LAYER_ORDER if counts[name])


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    records = []
    for raw in SOURCE.read_text(encoding="utf-8").splitlines():
        if not raw or raw.startswith("#"):
            continue
        fields = raw.split("|")
        if len(fields) != 11:
            raise AssertionError("source field count drift")
        if fields[1] != "zodiac":
            continue
        comment = fields[10]
        records.append({
            "id": fields[0],
            "page": fields[2],
            "folio": re.match(r"^f\d+", fields[2]).group(0),
            "sign": normalize_sign(comment),
            "layer": layer(comment),
            "label_present": fields[6] != "-",
        })
    if len(records) != 300 or len({row["id"] for row in records}) != 300:
        raise AssertionError("expected exact 300-slot public inventory")
    if set(row["sign"] for row in records) != set(EXPECTED_SIGNS):
        raise AssertionError("zodiac sign inventory drift")

    panel_counts: dict[tuple[str, str], Counter[str]] = defaultdict(Counter)
    sign_folios: dict[str, set[str]] = defaultdict(set)
    sign_present = Counter()
    for row in records:
        panel_counts[(row["sign"], row["page"])][row["layer"]] += 1
        sign_folios[row["sign"]].add(row["folio"])
        sign_present[row["sign"]] += int(row["label_present"])

    sign_rows = []
    topology_groups: dict[str, list[str]] = defaultdict(list)
    for sign in EXPECTED_SIGNS:
        panels = [
            {
                "page": page,
                "shape": shape(counts),
                "counts": {name: counts[name] for name in LAYER_ORDER},
            }
            for (row_sign, page), counts in panel_counts.items() if row_sign == sign
        ]
        panels.sort(key=lambda row: row["page"])
        topology = " / ".join(sorted(row["shape"] for row in panels))
        topology_groups[topology].append(sign)
        sign_rows.append({
            "sign": sign,
            "slot_count": sum(sum(row["counts"].values()) for row in panels),
            "label_count": sign_present[sign],
            "physical_folios": sorted(sign_folios[sign]),
            "panel_topology": panels,
            "topology_signature_ignoring_page_identity": topology,
        })

    repeated = {key: signs for key, signs in topology_groups.items() if len(signs) > 1}
    repeated_pairs = []
    for topology, signs in repeated.items():
        for left, right in itertools.combinations(signs, 2):
            overlap = sorted(sign_folios[left] & sign_folios[right])
            repeated_pairs.append({
                "topology": topology,
                "left": left,
                "right": right,
                "shared_physical_folios": overlap,
                "disjoint_physical_folios": not overlap,
            })
    disjoint_pairs = [row for row in repeated_pairs if row["disjoint_physical_folios"]]
    all_layer_counts = Counter(row["layer"] for row in records)
    per_sign_layer_counts = {
        row["sign"]: dict(Counter(r["layer"] for r in records if r["sign"] == row["sign"]))
        for row in sign_rows
    }
    gates = {
        "exact_300_expected_slots": len(records) == 300,
        "exact_299_present_labels": sum(row["label_present"] for row in records) == 299,
        "exact_10_extant_signs": len(sign_rows) == 10,
        "exact_4_physical_folios": len({row["folio"] for row in records}) == 4,
        "seven_distinct_panel_topologies": len(topology_groups) == 7,
        "no_universal_equal_band_partition": len({
            tuple(sorted(counts.items())) for counts in per_sign_layer_counts.values()
        }) > 1,
        "no_same_topology_pair_on_disjoint_folios": len(disjoint_pairs) == 0,
        "zero_Voynich_string_score": True,
        "zero_phase_selected": True,
        "zero_interband_continuation_selected": True,
    }
    if not all(gates.values()):
        raise AssertionError(gates)
    result = {
        "experiment": "ZODIAC_CROSSSIGN_PHASE_CAPACITY",
        "status": "STOP_UNSCORED_NO_IDENTIFIABLE_SHARED_30_POSITION_COORDINATE",
        "input": {str(SOURCE.relative_to(BASE)): sha(SOURCE)},
        "public_source": "https://www.ic.unicamp.br/~stolfi/EXPORT/00-EXPORT/98-02-01-lotsa-labels/",
        "counts": {
            "expected_slots": len(records),
            "present_labels": sum(row["label_present"] for row in records),
            "signs": len(sign_rows),
            "physical_folios": len({row["folio"] for row in records}),
            "distinct_panel_topologies": len(topology_groups),
            "repeated_topology_pairs": len(repeated_pairs),
            "disjoint_folio_repeated_topology_pairs": len(disjoint_pairs),
        },
        "all_layer_counts": dict(all_layer_counts),
        "signs": sign_rows,
        "topology_groups": dict(sorted(topology_groups.items())),
        "repeated_topology_pairs": repeated_pairs,
        "gates": gates,
        "decision": "DO_NOT_FIT_CROSSSIGN_DEGREE_PHASE_WITHOUT_EXTERNAL_BAND_AND_START_KEY",
        "claim_ceiling": (
            "The public 300-slot inventory has seven incompatible panel topologies. Every repeated topology "
            "pair shares a physical folio, so there is no disjoint-folio train/test replication of a topology. "
            "A universal 30-position degree coordinate is not identified without choosing starts, directions, "
            "and inter-band/off-circle continuation. This capacity stop does not exclude degree records or "
            "other position-free zodiac structure and supplies no number, degree, word, meaning, or translation."
        ),
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    groups = "; ".join(f"{key}: {', '.join(value)}" for key, value in sorted(topology_groups.items()))
    REPORT.write_text(
        "# Cross-sign zodiac 30-position capacity audit\n\n"
        "Status: **STOP_UNSCORED_NO_IDENTIFIABLE_SHARED_30_POSITION_COORDINATE**\n\n"
        "This is a score-blind check of the public Stolfi/Grove 300-slot catalogue, not a rerun of a "
        "Voynich-string experiment. It reconstructs 299 present labels for ten extant signs on only four "
        "physical folios. The panels do not share one ring partition: they realize seven distinct topologies.\n\n"
        f"Topologies are: {groups}. The three repeated-topology pairs are Aries--Taurus, Leo--Virgo, and "
        "Scorpius--Sagittarius; every pair shares a physical folio. There is therefore no disjoint-folio "
        "same-topology replication from which to learn a band continuation and predict it on held material.\n\n"
        "A latent cross-sign 30-degree model would have to choose starts, directions, and how inner, middle, "
        "outer, central, off-circle, and split-page slots continue. Those choices are the missing answer, not "
        "nuisance parameters justified by the data. Decision: **DO_NOT_FIT_CROSSSIGN_DEGREE_PHASE_WITHOUT_EXTERNAL_BAND_AND_START_KEY**. "
        "This does not reject a degree-record interpretation or position-free zodiac structure, and it supplies "
        "no number, degree, word, meaning, plaintext, or translation.\n\n"
        "Public source: [Stolfi/Grove zodiac label catalogue](https://www.ic.unicamp.br/~stolfi/EXPORT/00-EXPORT/98-02-01-lotsa-labels/).\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": result["status"], **result["counts"]}, sort_keys=True))


if __name__ == "__main__":
    main()

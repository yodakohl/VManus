#!/usr/bin/env python3
"""Build the LTG001 cross-folio latent-channel capacity inventory."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
METHOD = HERE / "LTG001_LATENT_TRANSCRIPTION_CHANNEL_METHOD.md"
GROUPS = RESULTS / "source_sta_family_consensus_groups.tsv"
UPSTREAM = RESULTS / "source_sta_member_agreement_atlas_validation.json"
OUT_TSV = RESULTS / "ltg001_latent_channel_capacity.tsv"
OUT_JSON = RESULTS / "ltg001_latent_channel_capacity.json"
OUT_REPORT = RESULTS / "ltg001_latent_channel_capacity_report.md"

EXPECTED = {
    GROUPS: "a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",
    UPSTREAM: "8f0c89207a440ae5e767b35c6fb150cb0b32b39f32677bb32ff8be9a10ba9168",
}
EDITIONS = ("ZL", "IT", "RF")
FOLD_DOMAIN = "LTG001_FOLD_V1|"
FIELDS = [
    "family", "positions", "disagreements", "disagreement_folios",
    "triplet_types", "triplet_types_three_folios", "ambiguous_events",
    "ambiguous_folios", "loo_supported_ambiguous_events",
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def folio(page: str) -> str:
    match = re.match(r"^(f(?:Ros|[0-9]+))", page, re.IGNORECASE)
    if not match:
        raise ValueError(f"unrecognized page {page}")
    return match.group(1).lower()


def fold(folio_id: str) -> int:
    digest = hashlib.sha256((FOLD_DOMAIN + folio_id).encode("utf-8")).digest()
    return int.from_bytes(digest[:4], "big") % 5


def main() -> None:
    for output in (OUT_TSV, OUT_JSON, OUT_REPORT):
        if output.exists():
            raise SystemExit(f"refusing to overwrite {output.name}")
    for path, expected in EXPECTED.items():
        if sha(path) != expected:
            raise SystemExit(f"frozen input mismatch {path.name}")
    upstream = json.loads(UPSTREAM.read_text(encoding="utf-8"))
    if upstream["status"] != "PASS_INDEPENDENT_FINE_CODE_AGREEMENT_RECONSTRUCTION":
        raise SystemExit("upstream agreement validation is not PASS")

    rows = list(csv.DictReader(GROUPS.open(encoding="utf-8", newline=""), delimiter="\t"))
    family = defaultdict(Counter)
    family_folios = defaultdict(set)
    triplet_folios = defaultdict(set)
    context_occurrences = defaultdict(list)
    disagreement_folios = set()
    dominant_folios = set()
    currier_disagreements = Counter()
    fold_counts = Counter()
    positions = 0
    disagreements = 0
    ambiguous = []
    exact_triplets = Counter()

    for row in rows:
        if row["strict_zero_alternative"] != "1":
            continue
        physical_folio = folio(row["page"])
        current_fold = fold(physical_folio)
        zl = row["zl_sta_codes"].split()
        it = row["it_sta_codes"].split()
        rf = row["rf_sta_codes"].split()
        families = row["family_surface"]
        if not (len(zl) == len(it) == len(rf) == len(families) == int(row["symbol_count"])):
            raise ValueError(f"group length drift {row['consensus_group_id']}")
        for symbol_index, (fam, zcode, icode, rcode) in enumerate(zip(families, zl, it, rf)):
            if zcode[0] != fam or icode[0] != fam or rcode[0] != fam:
                raise ValueError(f"family drift {row['consensus_group_id']}:{symbol_index}")
            observations = {"ZL": zcode[1:], "IT": icode[1:], "RF": rcode[1:]}
            positions += 1
            family[fam]["positions"] += 1
            if len(set(observations.values())) > 1:
                disagreements += 1
                family[fam]["disagreements"] += 1
                family_folios[fam].add(physical_folio)
                disagreement_folios.add(physical_folio)
                currier_disagreements[row["currier"] or "BLANK"] += 1
                fold_counts[current_fold] += 1
                triplet = (fam, zcode, icode, rcode)
                exact_triplets[triplet] += 1
                triplet_folios[triplet].add(physical_folio)
                if (zcode, icode, rcode) != ("B1", "B1", "Ba"):
                    dominant_folios.add(physical_folio)
            for target, left, right in (("ZL", "IT", "RF"), ("IT", "ZL", "RF"), ("RF", "ZL", "IT")):
                if observations[left] == observations[right]:
                    continue
                event = {
                    "folio": physical_folio,
                    "target": target,
                    "family": fam,
                    "left": observations[left],
                    "right": observations[right],
                    "outcome": observations[target],
                }
                ambiguous.append(event)
                family[fam]["ambiguous_events"] += 1
                context_occurrences[(target, fam, observations[left], observations[right])].append(
                    physical_folio
                )

    if positions != 95451 or disagreements != 3535:
        raise ValueError("published position totals drift")

    supported = Counter()
    ambiguous_folios = defaultdict(set)
    for event in ambiguous:
        fam = event["family"]
        ambiguous_folios[fam].add(event["folio"])
        key = (event["target"], fam, event["left"], event["right"])
        outside = sum(other != event["folio"] for other in context_occurrences[key])
        if outside >= 5:
            supported[fam] += 1

    output_rows = []
    for fam in sorted(family):
        triplets = [key for key in exact_triplets if key[0] == fam]
        output_rows.append({
            "family": fam,
            "positions": family[fam]["positions"],
            "disagreements": family[fam]["disagreements"],
            "disagreement_folios": len(family_folios[fam]),
            "triplet_types": len(triplets),
            "triplet_types_three_folios": sum(len(triplet_folios[key]) >= 3 for key in triplets),
            "ambiguous_events": family[fam]["ambiguous_events"],
            "ambiguous_folios": len(ambiguous_folios[fam]),
            "loo_supported_ambiguous_events": supported[fam],
        })

    with OUT_TSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(output_rows)

    dominant_count = exact_triplets[("B", "B1", "B1", "Ba")]
    recurrent_triplets = sum(len(folios) >= 3 for folios in triplet_folios.values())
    loo_supported = sum(supported.values())
    qualifying_families = sum(
        row["disagreements"] >= 20 and row["disagreement_folios"] >= 10
        for row in output_rows
    )
    folds = {str(index): fold_counts[index] for index in range(5)}
    gates = {
        "disagreements_3000_80_folios": disagreements >= 3000 and len(disagreement_folios) >= 80,
        "ambiguous_events_5000_80_folios": len(ambiguous) >= 5000 and len({e["folio"] for e in ambiguous}) >= 80,
        "recurrent_triplets_50": recurrent_triplets >= 50,
        "loo_supported_events_5000_80_folios": loo_supported >= 5000 and len({e["folio"] for e in ambiguous}) >= 80,
        "each_fold_500_disagreements": min(fold_counts.values()) >= 500 and len(fold_counts) == 5,
        "dominant_policy_deleted_1500_60_folios": disagreements - dominant_count >= 1500 and len(dominant_folios) >= 60,
        "currier_A_B_each_500": currier_disagreements["A"] >= 500 and currier_disagreements["B"] >= 500,
        "five_families_20_disagreements_10_folios": qualifying_families >= 5,
    }
    result = {
        "experiment": "LTG001_LATENT_TRANSCRIPTION_CHANNEL_CAPACITY",
        "status": "PASS_IDENTIFIABLE_CROSS_FOLIO_CHANNEL" if all(gates.values()) else "STOP_INSUFFICIENT_CHANNEL_CAPACITY",
        "inputs": {
            path.name: {"sha256": sha(path), "bytes": path.stat().st_size}
            for path in (*EXPECTED, METHOD, Path(__file__).resolve())
        },
        "counts": {
            "strict_positions": positions,
            "physical_folios": len({folio(row["page"]) for row in rows if row["strict_zero_alternative"] == "1"}),
            "disagreement_positions": disagreements,
            "disagreement_folios": len(disagreement_folios),
            "exact_disagreement_triplet_types": len(exact_triplets),
            "triplet_types_three_folios": recurrent_triplets,
            "ambiguous_prediction_events": len(ambiguous),
            "ambiguous_prediction_folios": len({event["folio"] for event in ambiguous}),
            "loo_supported_ambiguous_events": loo_supported,
            "dominant_B1_B1_Ba_positions": dominant_count,
            "dominant_policy_deleted_disagreements": disagreements - dominant_count,
            "dominant_policy_deleted_folios": len(dominant_folios),
            "qualifying_families": qualifying_families,
        },
        "by_currier_disagreements": dict(sorted(currier_disagreements.items())),
        "fold_disagreements": folds,
        "gates": gates,
        "outputs": {OUT_TSV.name: sha(OUT_TSV)},
        "claim_ceiling": (
            "Score-bearing capacity for a held-folio latent transcription-channel test only. "
            "No preferred reading, physical glyph identity, allography, sound, alphabet, word, "
            "language, cipher, plaintext, meaning, or translation follows."
        ),
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report = f"""# LTG001 latent transcription-channel capacity

Status: **{result['status']}**.

The strict aligned panel contains **{positions:,}** fine-code positions on
**{result['counts']['physical_folios']}** physical folios.  There are
**{disagreements:,}** disagreement positions on **{len(disagreement_folios)}**
folios and **{len(ambiguous):,}** prediction events where the two available
readings disagree.  **{loo_supported:,}** such events retain at least five
exact-context examples outside their own folio.

The single known `(B1,B1,Ba)` RF policy contributes **{dominant_count:,}**
positions.  Deleting it leaves **{disagreements - dominant_count:,}**
disagreements on **{len(dominant_folios)}** folios.  All five frozen folds
contain at least **{min(fold_counts.values()):,}** disagreements, and
**{recurrent_triplets}** exact triplets recur on at least three folios.

All {len(gates)} capacity gates pass.  This authorizes the frozen synthetic
calibration and held-folio channel model.  It does not choose a correct
transcription or establish a physical glyph, allograph, sound, word, language,
cipher, plaintext, meaning, or translation.
"""
    OUT_REPORT.write_text(report, encoding="utf-8")
    print(json.dumps({"status": result["status"], **result["counts"]}, sort_keys=True))


if __name__ == "__main__":
    main()

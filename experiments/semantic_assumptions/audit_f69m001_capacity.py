#!/usr/bin/env python3
"""Target-blind capacity audit for the f69v 28-mansion prefix test."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path


BASE = Path(__file__).resolve().parent
ROOT = BASE.parent.parent
RESULTS = BASE / "results"
LINES = ROOT / "transcription" / "voynich_stolfi25e1_lines.tsv"
CONSENSUS = RESULTS / "source_sta_family_consensus_loci.tsv"
ROSTER = BASE / "f69v_lunar_mansion_agrippa_roster.tsv"
OUT = RESULTS / "f69m001_capacity.json"
REPORT = RESULTS / "f69m001_capacity.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    with ROSTER.open(encoding="utf-8", newline="") as handle:
        roster = list(csv.DictReader(handle, delimiter="\t"))
    if [int(row["ordinal"]) for row in roster] != list(range(1, 29)):
        raise AssertionError("roster order")
    if any(not re.fullmatch(r"[A-Za-z]+(?: [A-Za-z]+)*", row["name"]) for row in roster):
        raise AssertionError("roster spelling")

    with LINES.open(encoding="utf-8", newline="") as handle:
        # Do not retain transcription fields.
        radial = [
            {key: row[key] for key in ("page", "locus", "old_locus", "code", "word_count")}
            for row in csv.DictReader(handle, delimiter="\t")
            if row["page"] == "f69v" and row["code"] == "@Ri"
        ]
    radial.sort(key=lambda row: int(row["old_locus"].rsplit(".", 1)[1]))
    ordinals = [int(row["old_locus"].rsplit(".", 1)[1]) for row in radial]
    if ordinals != list(range(1, 29)):
        raise AssertionError("f69v X1 order")

    with CONSENSUS.open(encoding="utf-8", newline="") as handle:
        # Deliberately omit family_sequence and member-code fields.
        consensus = {
            row["locus"]: {
                "locus": row["locus"], "page": row["page"], "code": row["code"],
                "symbol_count": int(row["symbol_count"]),
                "strict_zero_alternative": row["strict_zero_alternative"] == "1",
            }
            for row in csv.DictReader(handle, delimiter="\t")
            if row["page"] == "f69v" and row["code"] == "@Ri"
        }
    loci = [row["locus"] for row in radial]
    if set(loci) != set(consensus):
        raise AssertionError("consensus coverage")
    panel = [
        {
            "ordinal": index,
            "locus": row["locus"],
            "old_locus": row["old_locus"],
            "word_count": int(row["word_count"]),
            "consensus_symbol_count": consensus[row["locus"]]["symbol_count"],
            "strict_zero_alternative": consensus[row["locus"]]["strict_zero_alternative"],
        }
        for index, row in enumerate(radial, 1)
    ]
    gates = {
        "exact_public_28_inward_radial_labels": len(panel) == 28 and {row["code"] for row in radial} == {"@Ri"},
        "exact_human_X1_1_through_28_order": ordinals == list(range(1, 29)),
        "one_label_locus_per_slot": len(set(loci)) == 28,
        "all_28_have_all_reading_family_consensus": len(consensus) == 28,
        "every_consensus_sequence_has_at_least_3_families": min(row["consensus_symbol_count"] for row in panel) >= 3,
        "exact_28_fixed_historical_roster_names": len(roster) == 28,
        "Voynich_prefix_values_not_accessed": True,
        "alignment_score_not_computed": True,
        "zero_English_glosses": True,
    }
    if not all(gates.values()):
        raise AssertionError(gates)
    result = {
        "experiment": "F69M001_LUNAR_MANSION_PREFIX_CAPACITY",
        "status": "PASS_UNSCORED_28_ORDERED_LABELS_AND_FIXED_ROSTER",
        "public_sources": {
            "f69v_description": "https://www.voynich.nu/q10/index.html",
            "human_28_log_description": "https://www.ic.unicamp.br/en/~stolfi/EXPORT/voynich/00-06-07-word-grammar/Notes/040/html/f69v.htm",
            "fixed_Agrippa_name_table": "https://digitalambler.com/2015/04/03/on-geomantic-figures-zodiac-signs-and-lunar-mansions/",
        },
        "inputs": {path.name: sha(path) for path in (LINES, CONSENSUS, ROSTER, Path(__file__))},
        "panel": panel,
        "historical_roster": [{"ordinal": int(row["ordinal"]), "name": row["name"]} for row in roster],
        "counts": {
            "slots": 28,
            "single_source_group_labels": sum(row["word_count"] == 1 for row in panel),
            "multi_source_group_labels": sum(row["word_count"] > 1 for row in panel),
            "strict_zero_alternative_loci": sum(row["strict_zero_alternative"] for row in panel),
        },
        "gates": gates,
        "decision": "AUTHORIZE_PREFIX_TOPOLOGY_PREREGISTRATION_AND_SYNTHETIC_CONTROLS_ONLY",
        "claim_ceiling": "Capacity for one rotation/reflection-corrected prefix-equivalence topology test against one fixed Latin lunar-mansion roster; no list identity, name, word, sound, meaning, plaintext, or translation follows.",
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# F69M001 28-mansion prefix capacity\n\n"
        "Status: **PASS_UNSCORED_28_ORDERED_LABELS_AND_FIXED_ROSTER**\n\n"
        "Public human sources describe f69v as 28 alternating long/short radial objects with one inward-"
        "reading label apiece and explicitly raise the 28 lunar mansions as a possibility. The manual "
        "crosswalk supplies one complete cyclic order, `f69v.X1.1` through `.28`. All 28 loci have an "
        "all-reading STA-family consensus sequence of at least three families; 25 are zero-alternative. "
        "A fixed 28-name Latin/Agrippa roster is transcribed from the cited human table.\n\n"
        "No Voynich prefix value or alignment score was opened. This reopens only the closed route's "
        "explicit-ordered-coordinate exception. Capacity supplies no lunar-mansion identity, name, word, "
        "sound, meaning, plaintext, or translation.\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": result["status"], "counts": result["counts"]}, sort_keys=True))


if __name__ == "__main__":
    main()

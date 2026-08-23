#!/usr/bin/env python3
"""Paraphrase blocked fused meanings with only already observed cards."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
BLOCKED = ROOT / "experiments/yolo/sidequest_semantic_surface_realization_forty_eighth_edition/FORTY_EIGHTH_17_BLOCKED_COMPOUNDS.tsv"
LEDGER = ROOT / "experiments/yolo/sidequest_semantic_final_productive_cards_nineteenth_edition/NINETEENTH_776_SPEAKABLE_LEDGER.tsv"

PROFILES = ("S1_BARE_MASTER", "S2_Q_CELL_SCRIBE", "S3_S_LINE_SCRIBE", "S4_MIXED_COMPACT")

PARAPHRASES = {
    "OK+CLOSE": (("OK+E+CLOSE",), "EXTRA_BRIEF_GRADE", "ansetzen, kurz ausführen und schließen"),
    "OT+E+Y": (("OT+Y", "OK+E+Y"), "EXTRA_SET_OPERATION", "zum folgenden Posten gehen und ihn kurz ansetzen"),
    "SHED+Y": (("Y", "SHED+E+CLOSE"), "EXTRA_BRIEF_GRADE_AND_CLOSE", "den aktuellen Posten kurz absetzen lassen und schließen"),
    "SOLK+Y": (("SOLK+E+Y",), "EXTRA_BRIEF_GRADE", "den aktuellen Posten kurz auffangen"),
    "CHD+E+Y": (("CHD+Y", "OK+E+Y"), "EXTRA_SET_OPERATION", "den aktuellen Posten umsetzen und kurz neu ansetzen"),
    "CHK+Y": (("CHK+E+Y",), "EXTRA_BRIEF_GRADE", "den aktuellen Posten kurz wärmen"),
    "CHD+EE+CLOSE": (("CHD+Y", "OK+EE+CLOSE"), "EXTRA_SET_OPERATION", "umsetzen, länger neu ansetzen und schließen"),
    "OT+CLOSE": (("OT+Y", "OK+E+CLOSE"), "EXTRA_SET_AND_BRIEF_GRADE", "zum folgenden Posten gehen, kurz ansetzen und schließen"),
    "CKHE+Y": (("Y", "CKHE+AR"), "EXTRA_SOURCE_ADDRESS", "den aktuellen Posten an der Quellenadresse trennen"),
    "SHED+AR": (("AR", "SHED+E+CLOSE"), "EXTRA_BRIEF_GRADE_AND_CLOSE", "aus der Quelle nehmen, kurz absetzen lassen und schließen"),
    "SHED+E+Y": (("Y", "SHED+E+CLOSE"), "EXTRA_CLOSE", "den aktuellen Posten kurz absetzen lassen und schließen"),
    "CHK+AIIN": (("AIIN", "CHK+E+Y"), "EXTRA_BRIEF_GRADE_AND_CURRENT", "nach Sollwert kurz wärmen"),
    "SOLK+AL": (("AL", "SOLK+E+Y"), "EXTRA_BRIEF_GRADE_AND_CURRENT", "am Ziel kurz auffangen"),
    "SOLK+AR": (("AR", "SOLK+E+Y"), "EXTRA_BRIEF_GRADE_AND_CURRENT", "aus der Quelle kurz auffangen"),
    "OL+E+Y": (("OL", "OK+E+Y"), "EXTRA_SET_OPERATION", "fortsetzen und den aktuellen Posten kurz neu ansetzen"),
    "CHD+E+CLOSE": (("CHD+Y", "OK+E+CLOSE"), "EXTRA_SET_OPERATION", "umsetzen, kurz neu ansetzen und schließen"),
    "SHED+EE+Y": (("Y", "SHED+EE+CLOSE"), "EXTRA_CLOSE", "den aktuellen Posten länger absetzen lassen und schließen"),
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def choose(surfaces: list[str], profile: str, offset: int) -> str:
    unique = sorted(set(surfaces), key=lambda value: (len(value), value))
    preferences = {
        "S1_BARE_MASTER": lambda value: not value.startswith(("q", "s")),
        "S2_Q_CELL_SCRIBE": lambda value: value.startswith("q"),
        "S3_S_LINE_SCRIBE": lambda value: value.startswith("s"),
        "S4_MIXED_COMPACT": lambda value: value.startswith(("o", "d", "a")),
    }
    candidates = [value for value in unique if preferences[profile](value)] or unique
    return candidates[offset % len(candidates)]


def main() -> None:
    blocked = read_tsv(BLOCKED)
    ledger = read_tsv(LEDGER)
    observed: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in ledger:
        observed[row["atom_sequence"]].append(row)
    if set(PARAPHRASES) != {row["predicted_fused_atom_sequence"] for row in blocked}:
        raise RuntimeError("paraphrase map does not cover the blocked inventory exactly")

    paraphrase_rows = []
    copy_rows = []
    for row in blocked:
        desired = row["predicted_fused_atom_sequence"]
        components, drift, spoken = PARAPHRASES[desired]
        for component in components:
            if component not in observed:
                raise RuntimeError(f"unobserved paraphrase card: {component}")
        representative = []
        for component in components:
            representative.append(sorted({card["visible_surface"] for card in observed[component]}, key=lambda value: (len(value), value))[0])
        paraphrase_rows.append({
            "prediction_rank": row["prediction_rank"],
            "cell_id": row["cell_id"],
            "blocked_fused_atom_sequence": desired,
            "intended_reading_de": row["predicted_reading_de"],
            "paraphrase_atom_sequence": " | ".join(components),
            "paraphrase_card_count": len(components),
            "representative_observed_surfaces": " ".join(representative),
            "spoken_paraphrase_de": spoken,
            "controlled_meaning_drift": drift,
            "exact_semantic_equivalence": "NO_NEAREST_WORKSHOP_PARAPHRASE",
            "all_cards_individually_observed": "YES",
            "complete_chain_observed": "NO",
            "new_surface_invented": "NO",
            "master_warning_de": "Zusatzinformation laut mitsprechen; nicht so tun, als sei die blockierte Fusionskarte vorhanden.",
        })
        for offset, profile in enumerate(PROFILES):
            surfaces = [choose([card["visible_surface"] for card in observed[component]], profile, offset) for component in components]
            copy_rows.append({
                "prediction_rank": row["prediction_rank"],
                "cell_id": row["cell_id"],
                "scribe_profile": profile,
                "blocked_fused_atom_sequence": desired,
                "paraphrase_atom_sequence": " | ".join(components),
                "scribe_surface_sequence": " ".join(surfaces),
                "spoken_paraphrase_de": spoken,
                "controlled_meaning_drift": drift,
                "all_surfaces_observed": "YES",
                "new_surface_invented": "NO",
                "status": "CONTROLLED_PARAPHRASE_NOT_FUSED_WORD",
            })
    write_tsv(OUT / "FORTY_NINTH_17_CONTROLLED_PARAPHRASES.tsv", paraphrase_rows)
    write_tsv(OUT / "FORTY_NINTH_68_SCRIBE_COPIES.tsv", copy_rows)

    lines = [
        "# Umschreibebuch für siebzehn blockierte Befehle",
        "",
        "Jede blockierte Fusionsbedeutung wird mit einer oder zwei vorhandenen Karten",
        "umschrieben. Die Umschreibung ist nie als exakt gleich ausgegeben: zusätzlicher",
        "Kurzgrad, Schluss, Quellenadresse oder erneutes Ansetzen wird laut genannt. Das ist",
        "besser als eine neue Voynich-Form zu erfinden.",
        "",
    ]
    for row in paraphrase_rows:
        lines.extend([
            f"## {row['blocked_fused_atom_sequence']}",
            "",
            f"Gewünscht: {row['intended_reading_de']}.",
            "",
            f"Schreibe: `{row['paraphrase_atom_sequence']}` → `{row['representative_observed_surfaces']}`.",
            "",
            f"Sprich: **{row['spoken_paraphrase_de']}**. Zusatz: `{row['controlled_meaning_drift']}`.",
            "",
        ])
    (OUT / "FORTY_NINTH_CONTROLLED_PARAPHRASE_BOOK.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    summary = {
        "status": "CONSISTENT",
        "counts": {
            "blocked_meanings_covered": len(paraphrase_rows),
            "scribe_copies": len(copy_rows),
            "one_card_paraphrases": sum(int(row["paraphrase_card_count"]) == 1 for row in paraphrase_rows),
            "two_card_paraphrases": sum(int(row["paraphrase_card_count"]) == 2 for row in paraphrase_rows),
            "exact_equivalences_claimed": sum(row["exact_semantic_equivalence"] == "YES" for row in paraphrase_rows),
            "new_surfaces": sum(row["new_surface_invented"] == "YES" for row in paraphrase_rows),
        },
        "sources": {str(path.relative_to(ROOT)): sha256(path) for path in (BLOCKED, LEDGER)},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

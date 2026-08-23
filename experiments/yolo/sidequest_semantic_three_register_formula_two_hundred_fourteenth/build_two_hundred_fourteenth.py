#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
BASE = ROOT / "experiments/yolo/sidequest_semantic_astro_prose_bridge_two_hundred_thirteenth"
DICT = BASE / "TWO_HUNDRED_THIRTEENTH_173_CARD_CROSS_REGISTER_DICTIONARY.tsv"
ASTRO = BASE / "TWO_HUNDRED_THIRTEENTH_395_ASTRO_SURFACE_BRIDGE.tsv"

FIELDS = [
    ("T01", "PF03", [("MC123", "chey"), ("MC039", "aiin"), ("MC026", "choky")],
     "Diesen Pflanzenposten auf den Sollwert bringen und einsetzen.",
     "Diesen Stationsposten auf den Sollwert bringen und einsetzen.",
     "Diesen Diagrammposten auf den Sollwert bringen und setzen."),
    ("T02", "PF07", [("MC055", "dar"), ("MC039", "daiin"), ("MC154", "dal")],
     "Davon das Sollmaß nehmen und an die nächste Pflanzenzubereitung bringen.",
     "Davon den Sollwert nehmen und an die nächste Station bringen.",
     "Vom Bezugssektor den Sollwert nehmen und zum Zielsektor führen."),
    ("T03", "CROSS_REGISTER_END_FRAME", [("MC039", "aiin"), ("MC040", "okal"), ("MC019", "oldy")],
     "Den Sollwert an der Zielzubereitung einsetzen und fertigstellen.",
     "Den Sollwert an der Zielstation einsetzen und fertigstellen.",
     "Den Sollwert im Zielfeld setzen und den Eintrag fertigstellen."),
    ("T04", "WHOLE_CARD_BRIDGE", [("MC119", "cheey")],
     "Den Freigabewert als klaren Pflanzenauszug ablesen.",
     "Den Freigabewert als klaren Stationsablauf ablesen.",
     "Den Freigabewert am Diagrammplatz ablesen."),
]


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    dictionary = {row["master_card_id"]: row for row in read(DICT)}
    astro = read(ASTRO)
    astro_surface_counts = Counter(row["visible_surface"] for row in astro)
    token_rows: list[dict[str, object]] = []
    field_rows: list[dict[str, object]] = []
    sequence = 0
    for field_id, license_id, tokens, herbal, bio, astro_reading in FIELDS:
        for position, (card_id, surface) in enumerate(tokens, 1):
            sequence += 1
            card = dictionary[card_id]
            token_rows.append({
                "sequence": sequence,
                "field_id": field_id,
                "position": position,
                "license_id": license_id,
                "master_card_id": card_id,
                "selected_surface": surface,
                "registered_surfaces": card["registered_surfaces"],
                "portable_value_de": card["current_value_de"],
                "astro_exact_surface_occurrences": astro_surface_counts[surface],
                "herbal_value_de": card["current_value_de"],
                "bio_value_de": card["current_value_de"],
                "astro_value_de": card["current_value_de"],
                "value_changed": "NO",
            })
        field_rows.append({
            "field_id": field_id,
            "license_id": license_id,
            "surface_text": " ".join(surface for _, surface in tokens),
            "portable_literal_de": " | ".join(dictionary[card_id]["current_value_de"] for card_id, _ in tokens),
            "herbal_owner": "Bildpflanze",
            "herbal_expansion_de": herbal,
            "bio_owner": "lokale Becken-/Gerätestation",
            "bio_expansion_de": bio,
            "astro_owner": "lokaler Sektor/Stern-/Ringplatz",
            "astro_expansion_de": astro_reading,
        })
    write(OUT / "TWO_HUNDRED_FOURTEENTH_10_THREE_REGISTER_TOKENS.tsv", token_rows)
    write(OUT / "TWO_HUNDRED_FOURTEENTH_FOUR_PARALLEL_FIELDS.tsv", field_rows)
    summary = {
        "dictionary_source_sha256": hashlib.sha256(DICT.read_bytes()).hexdigest(),
        "astro_source_sha256": hashlib.sha256(ASTRO.read_bytes()).hexdigest(),
        "fields": len(field_rows),
        "tokens": len(token_rows),
        "unique_cards": len({row["master_card_id"] for row in token_rows}),
        "all_selected_surfaces_seen_in_astro": all(int(row["astro_exact_surface_occurrences"]) > 0 for row in token_rows),
        "changed_values": sum(row["value_changed"] == "YES" for row in token_rows),
        "owner_expansions": len(field_rows) * 3,
        "sealed_pages_accessed": False,
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
TIERED = ROOT / "experiments/yolo/sidequest_semantic_tiered_119_plus_3_codebook_nine_hundred_sixty_fourth/PASS964_TIERED_122_ENTRY_CODEBOOK.tsv"
FORMULAS = ROOT / "experiments/yolo/sidequest_semantic_cross_register_core_normalization_nine_hundred_sixty_second/PASS962_66_REGISTER_INVARIANT_FORMULAS.tsv"
FAMILY_META = ROOT / "experiments/yolo/sidequest_semantic_deduplicated_root_formula_codebook_nine_hundred_fifty_seventh/PASS957_66_TRUE_MULTICOMPONENT_FORMULAS.tsv"
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_cross_register_core_normalization_nine_hundred_sixty_second/PASS962_2511_REGISTER_NORMALIZED_EVENTS.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    tiered = read_tsv(TIERED)
    formulas = {row["formula_card_id"]: row for row in read_tsv(FORMULAS)}
    meta = read_tsv(FAMILY_META)
    events = read_tsv(EVENTS)
    keep = {
        row["formula_card_id"]
        for row in meta
        if int(row["events_including_local"]) >= 10 and len(row["physical_pages"].split("|")) >= 3
    }

    deck_rows: list[dict[str, object]] = []
    demoted_rows: list[dict[str, object]] = []
    for row in meta:
        formula_id = row["formula_card_id"]
        normalized = formulas[formula_id]
        target = deck_rows if formula_id in keep else demoted_rows
        target.append({
            "formula_card_id": formula_id,
            "component_recipe": row["component_recipe"],
            "portable_atomic_core_de": normalized["portable_atomic_core_de"],
            "surface_variants": row["surface_variants"],
            "surface_variant_count": row["surface_variant_count"],
            "events_including_local": row["events_including_local"],
            "physical_pages": row["physical_pages"],
            "decision": "KEEP_AS_COMMON_LEARNED_CARD" if formula_id in keep else "READ_PRODUCTIVELY_FROM_ROOTS",
            "teaching_rule_de": "Als Karte erkennen und im Ganzen sprechen." if formula_id in keep else "Nicht auswendig lernen; Stammfolge sichtbar zusammensetzen.",
        })
    write_tsv(OUT / "PASS965_30_COMMON_FORMULA_CARDS.tsv", deck_rows)
    write_tsv(OUT / "PASS965_36_PRODUCTIVE_FORMER_FORMULAS.tsv", demoted_rows)

    event_rows: list[dict[str, object]] = []
    demoted_events = 0
    for row in events:
        old_layer = row["codebook_layer"]
        formula_id = next((candidate for candidate, value in formulas.items() if value["component_recipe"] == row["component_recipe"]), "NONE")
        demote = old_layer == "LEARNED_FORMULA_CARD" and formula_id not in keep
        demoted_events += int(demote)
        new_layer = "PRODUCTIVE_ABBREVIATION_COMPOSITION" if demote else old_layer
        event_rows.append({
            "event_id": row["event_id"], "physical_page": row["physical_page"], "locus": row["locus"],
            "surface": row["surface"], "component_recipe": row["component_recipe"],
            "old_layer": old_layer, "compact_layer": new_layer,
            "formula_card_id": formula_id if new_layer == "LEARNED_FORMULA_CARD" else "NONE",
            "portable_atomic_reading_de": row["portable_atomic_reading_de"],
            "register_expansion_de": row["register_expansion_de"],
            "revision": "FORMULA_DEMOTED_TO_PRODUCTIVE_COMPOSITION" if demote else "UNCHANGED",
        })
    write_tsv(OUT / "PASS965_2511_COMPACT_DECK_EDITION.tsv", event_rows)

    compact_entries: list[dict[str, object]] = []
    for row in tiered:
        if row["entry_type"] == "FORMULA_CARD" and row["entry_id"] not in keep:
            continue
        portable_value = (
            formulas[row["entry_id"]]["portable_atomic_core_de"]
            if row["entry_type"] == "FORMULA_CARD"
            else row["portable_value_de"]
        )
        compact_entries.append({
            "entry_id": row["entry_id"], "entry_tier": row["entry_tier"], "entry_type": row["entry_type"],
            "recognition_form": row["recognition_form"], "portable_value_de": portable_value,
            "teaching_rule_de": row["teaching_rule_de"],
        })
    write_tsv(OUT / "PASS965_COMPACT_86_ENTRY_CODEBOOK.tsv", compact_entries)

    counts = Counter(row["compact_layer"] for row in event_rows)
    report = f"""# Pass 965 — nur 30 echte gelernte Ganzkarten

Die 66er-Formelliste war noch zu großzügig. Eine Mehrteilfolge wird jetzt nur
als gemeinsame gelernte Karte behandelt, wenn sie mindestens zehnmal und auf
mindestens drei physischen Seiten vorkommt. Das lässt **30 häufige Karten**
übrig. Die übrigen **36 Folgen** verlieren keine Bedeutung; sie werden einfach
aus ihren sichtbaren Stämmen gelesen.

Dadurch wechseln {demoted_events} Ereignisse von der Ganzkartenschublade zurück
zur produktiven Komposition. Die neue Ereignisbilanz ist {dict(counts)}.

## Das kleinere Werkstattinventar

- 37 häufige Stämme,
- 16 seltene produktive Erweiterungen,
- 30 gelernte Ganzkarten,
- 3 lokale Diagrammzeichen.

Das sind **83 gemeinsame Einträge plus drei lokale Zeichen = 86** statt 122
auswendig zu lernender Positionen. Die demotierten Formen bleiben vollständig
lesbar, weil jedes ihrer Teile bereits einen Kernwert besitzt. Das trifft die
gesuchte historische Mischung besser: ein kleiner produktiver Kürzelvorrat,
ein wirklich häufiges Nomenklatordeck und ein schmaler lokaler Rand.
"""
    (OUT / "PASS965_REPORT.md").write_text(report, encoding="utf-8")

    outputs = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(OUT.glob("PASS965_*"))
        if "BUILD_SUMMARY" not in path.name and "VALIDATION" not in path.name
    }
    summary = {
        "common_formula_cards": len(deck_rows), "productive_former_formulas": len(demoted_rows),
        "demoted_events": demoted_events, "compact_entries": len(compact_entries),
        "layer_counts": counts, "outputs": outputs,
    }
    (OUT / "PASS965_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

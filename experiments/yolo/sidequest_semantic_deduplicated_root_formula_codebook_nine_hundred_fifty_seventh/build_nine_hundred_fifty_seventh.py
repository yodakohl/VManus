#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
ROOTS = ROOT / "experiments/yolo/sidequest_semantic_concrete_root_lemmas_nine_hundred_fifty_fifth/PASS955_56_CONCRETE_ROOT_LEMMAS.tsv"
FAMILIES = ROOT / "experiments/yolo/sidequest_semantic_long_formula_deck_nine_hundred_fifty_second/PASS952_79_LEARNED_CARD_FAMILIES.tsv"
VARIANTS = ROOT / "experiments/yolo/sidequest_semantic_long_formula_deck_nine_hundred_fifty_second/PASS952_155_SURFACE_VARIANTS.tsv"
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_long_formula_deck_nine_hundred_fifty_second/PASS952_2511_LONG_FORMULA_EDITION.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    roots = read_tsv(ROOTS)
    families = read_tsv(FAMILIES)
    variants = read_tsv(VARIANTS)
    events = read_tsv(EVENTS)
    root_values = {row["component"]: row["concrete_root_lemma_de"] for row in roots}

    kept = [row for row in families if "+" in row["component_recipe"]]
    removed = [row for row in families if "+" not in row["component_recipe"]]
    compact_id_by_old: dict[str, str] = {}
    compact_families: list[dict[str, object]] = []
    for index, row in enumerate(kept, 1):
        compact_id = f"F{index:03d}"
        compact_id_by_old[row["learned_card_id"]] = compact_id
        compact_families.append({
            "formula_card_id": compact_id,
            "source_family_id": row["learned_card_id"],
            "component_recipe": row["component_recipe"],
            "workshop_formula_de": row["workshop_learned_value_de"],
            "image_formula_de": row["image_register_value_de"],
            "surface_variants": row["surface_variants"],
            "surface_variant_count": row["surface_variant_count"],
            "events_including_local": row["events"],
            "physical_pages": row["physical_pages"],
            "registers": row["registers"],
        })
    write_tsv(OUT / "PASS957_66_TRUE_MULTICOMPONENT_FORMULAS.tsv", compact_families)

    kept_ids = set(compact_id_by_old)
    compact_variants: list[dict[str, object]] = []
    for row in variants:
        if row["learned_card_id"] not in kept_ids:
            continue
        compact_variants.append({
            "surface": row["surface"],
            "formula_card_id": compact_id_by_old[row["learned_card_id"]],
            "component_recipe": row["component_recipe"],
            "workshop_formula_de": row["workshop_learned_value_de"],
            "image_formula_de": row["image_register_value_de"],
            "events": row["events"],
            "physical_pages": row["physical_pages"],
            "channel_class": row["channel_class"],
            "surface_role": row["surface_role"],
        })
    write_tsv(OUT / "PASS957_126_FORMULA_SURFACE_VARIANTS.tsv", compact_variants)

    removed_recipes = {row["component_recipe"] for row in removed}
    event_rows: list[dict[str, object]] = []
    demoted = 0
    for row in events:
        old_id = row["learned_card_id"]
        demote = row["codebook_layer"] == "LEARNED_FORMULA_CARD" and row["component_recipe"] in removed_recipes
        demoted += int(demote)
        if demote:
            layer = "PRODUCTIVE_ABBREVIATION_COMPOSITION"
            card_id = "NONE"
            value = root_values[row["component_recipe"]]
            revision = "SINGLE_ROOT_DEDUPLICATED"
        else:
            layer = row["codebook_layer"]
            card_id = compact_id_by_old[old_id] if layer == "LEARNED_FORMULA_CARD" else "NONE"
            value = row["current_value_de"]
            revision = "UNCHANGED"
        event_rows.append({
            "event_id": row["event_id"], "physical_page": row["physical_page"], "locus": row["locus"], "channel": row["channel"],
            "surface": row["surface"], "component_recipe": row["component_recipe"], "codebook_layer": layer,
            "current_value_de": value, "formula_card_id": card_id, "pass957_revision": revision,
        })
    write_tsv(OUT / "PASS957_2511_DEDUPLICATED_THREE_LAYER_EDITION.tsv", event_rows)

    removed_rows: list[dict[str, object]] = []
    for row in removed:
        removed_rows.append({
            "removed_source_family_id": row["learned_card_id"],
            "component": row["component_recipe"],
            "root_lemma_de": root_values[row["component_recipe"]],
            "former_formula_value_de": row["workshop_learned_value_de"],
            "surface_variants": row["surface_variants"],
            "events_including_local": row["events"],
            "decision_de": "Kein Ganzwort: exakt ein bereits gelehrter Stamm.",
        })
    write_tsv(OUT / "PASS957_13_REMOVED_SINGLE_ROOT_FORMULAS.tsv", removed_rows)

    entries: list[dict[str, object]] = []
    for index, row in enumerate(roots, 1):
        entries.append({"codebook_entry_id": f"R{index:03d}", "entry_type": "PRODUCTIVE_ROOT", "recognition_form": row["component"], "short_value_de": row["concrete_root_lemma_de"], "surface_variants": "PRODUCTIVE", "events_or_uses": row["atom_uses"]})
    for row in compact_families:
        entries.append({"codebook_entry_id": row["formula_card_id"], "entry_type": "LEARNED_FORMULA", "recognition_form": row["component_recipe"], "short_value_de": row["workshop_formula_de"], "surface_variants": row["surface_variants"], "events_or_uses": row["events_including_local"]})
    write_tsv(OUT / "PASS957_122_ENTRY_CODEBOOK.tsv", entries)

    counts = Counter(row["codebook_layer"] for row in event_rows)
    report = f"""# Pass 957 — 122 echte Lehreinträge statt 135 Doppelzählungen

Dreizehn angebliche Formelkarten bestanden aus genau einem bereits vorhandenen
Stamm. `Y`, `OL`, `AIIN`, `AL`, `S`, `AR`, `AIN`, `OR`, `AM_ADDR`, `O`, `R`,
`D_ADDR` und `HO` werden daher nur einmal gelehrt. {demoted} Ereignisse wechseln
von der Formelschublade zurück zur produktiven Stammschublade.

Das bereinigte Inventar besteht aus **56 Stämmen + 66 echten mehrteiligen
Formelkarten = 122 Lehreinträgen**. Die Ereignisbilanz lautet {dict(counts)}.
"""
    (OUT / "PASS957_REPORT.md").write_text(report, encoding="utf-8")
    outputs = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(OUT.glob("PASS957_*")) if "BUILD_SUMMARY" not in path.name and "VALIDATION" not in path.name}
    summary = {"roots": 56, "formulas": len(compact_families), "entries": len(entries), "variants": len(compact_variants), "demoted_events": demoted, "layer_counts": counts, "outputs": outputs}
    (OUT / "PASS957_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

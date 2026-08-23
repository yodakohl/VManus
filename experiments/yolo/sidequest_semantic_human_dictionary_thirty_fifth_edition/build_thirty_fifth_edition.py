#!/usr/bin/env python3
"""Build one human-readable teaching dictionary for all fixed-page surfaces."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import textwrap
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
SURFACES = ROOT / "experiments/yolo/sidequest_semantic_final_productive_cards_nineteenth_edition/NINETEENTH_RECLASSIFIED_487_SURFACES.tsv"
LEDGER = ROOT / "experiments/yolo/sidequest_semantic_final_productive_cards_nineteenth_edition/NINETEENTH_776_SPEAKABLE_LEDGER.tsv"
DECK = ROOT / "experiments/yolo/sidequest_semantic_apprentice_roundtrip_twenty_third_edition/TWENTY_THIRD_COMPONENT_DECK.tsv"
VERDICTS = ROOT / "experiments/yolo/sidequest_semantic_minimal_pairs_thirty_third_edition/THIRTY_THIRD_STEM_VERDICTS.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atom_tokens(sequence: str) -> set[str]:
    return {token for token in re.split(r"[+|:]", sequence) if token and token not in {"PROSE", "ASTRO"}}


def burden(row: dict[str, str]) -> str:
    classification = row["classification"]
    historical = row["historical_layer"]
    autonomy = row["composition_autonomy"]
    if autonomy == "REGISTER_SPLIT":
        return "REGISTER_SPLIT"
    if autonomy == "NONE" or classification in {"NOMENCLATOR_WHOLE_SIGN", "MEMORIZED_WHOLE_COMMAND"}:
        return "MEMORIZED_WHOLE_CARD"
    if "COMPOSED_LEARNED" in classification or "FINAL_PRODUCTIVE_BODY" in classification or "TECHNICAL_NOMENCLATOR" in historical:
        return "LEARNED_TECHNICAL_BODY"
    if "ASTRO_LOCAL" in classification or "MICROCODE" in classification or "TABLE_" in historical or "LOCAL_TABLE" in historical:
        return "TABLE_LOCAL_CODE"
    if "RENDERER" in classification or autonomy == "FULL_AFTER_RENDERER_NORMALIZATION" or "SCRIBAL_FRAME" in historical:
        return "REGISTERED_RENDERER_ALLOGRAPH"
    if "BOUND" in classification or "GRADE" in classification or "BOUND_" in historical:
        return "BOUND_MODIFIER_COMPOSITION"
    return "PRODUCTIVE_COMMON_COMPOSITION"


BURDEN_ACTION = {
    "PRODUCTIVE_COMMON_COMPOSITION": "gemeinsame Kerne in Reihenfolge lesen",
    "BOUND_MODIFIER_COMPOSITION": "nur innerhalb der lizenzierten Familie auswerten",
    "REGISTERED_RENDERER_ALLOGRAPH": "Schreiberrahmen normalisieren und Kern lesen",
    "TABLE_LOCAL_CODE": "lokalen Tafelwert am sichtbaren Besitzer nachschlagen",
    "LEARNED_TECHNICAL_BODY": "Fachkörper als Einheit lernen und Argumente anhängen",
    "MEMORIZED_WHOLE_CARD": "gesamte Karte auswendig aus dem Exemplar lernen",
    "REGISTER_SPLIT": "Register zuerst bestimmen und dann getrennte Lesung wählen",
}


def owner_rule(row: dict[str, str]) -> str:
    register = row["register_status"]
    if register == "ASTRO_ONLY":
        return "sichtbare Diagrammadresse liefert den konkreten Tabellengegenstand"
    if register == "PROSE_ONLY":
        return "Bildbesitzer und laufender Record liefern Stoff, Gerät oder Stelle"
    return "gemeinsamer Kern bleibt; Bild oder Diagramm konkretisiert den Gegenstand"


def chunks(values: list[str], width: int = 100) -> list[str]:
    text = ", ".join(f"`{value}`" for value in values)
    return textwrap.wrap(text, width=width, break_long_words=False, break_on_hyphens=False)


def main() -> None:
    surfaces = read_tsv(SURFACES)
    ledger = read_tsv(LEDGER)
    deck = read_tsv(DECK)
    verdicts = {r["symbol"]: r for r in read_tsv(VERDICTS)}
    events_by_surface: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in ledger:
        events_by_surface[event["surface_id"]].append(event)

    enriched = []
    for row in surfaces:
        events = events_by_surface[row["surface_id"]]
        if not events:
            raise RuntimeError(f"surface has no event: {row['surface_id']}")
        teaching_class = burden(row)
        example = events[0]
        enriched.append({
            "surface_id": row["surface_id"],
            "visible_surface": row["visible_surface"],
            "register_status": row["register_status"],
            "observed_groups": len(events),
            "pages": "|".join(sorted({e["page"] for e in events})),
            "atom_sequence": row["common_atom_sequences"],
            "teaching_class": teaching_class,
            "short_spoken_value_de": row["short_spoken_value_de"],
            "owner_rule_de": owner_rule(row),
            "apprentice_action_de": BURDEN_ACTION[teaching_class],
            "memorized_body_or_residue": row["memorized_body_or_residue"],
            "example_group": example["source_group_id"],
            "example_owner": example["visible_owner"],
            "example_value_de": example["short_value_de"],
            "original_classification": row["classification"],
        })
    write_tsv(OUT / "THIRTY_FIFTH_487_SURFACE_TEACHING_DICTIONARY.tsv", enriched, list(enriched[0]))

    surface_tokens = {row["surface_id"]: atom_tokens(row["common_atom_sequences"]) for row in surfaces}
    event_tokens = [atom_tokens(row["atom_sequence"]) for row in ledger]
    deck_rows = []
    for entry in deck:
        symbol = entry["symbol"]
        if entry["layer"] == "WHOLE_CARD":
            surface_hits = [row for row in surfaces if row["visible_surface"].upper() == symbol]
            whole_surface_ids = {row["surface_id"] for row in surface_hits}
            event_hits = [row for row in ledger if row["surface_id"] in whole_surface_ids]
        else:
            surface_hits = [row for row in surfaces if symbol in surface_tokens[row["surface_id"]]]
            event_hits = [row for row, tokens in zip(ledger, event_tokens) if symbol in tokens]
        verdict = verdicts.get(symbol)
        if verdict:
            status = verdict["status"]
            caution = verdict["caution_de"]
            pair_ids = verdict["pair_ids"]
        elif entry["layer"] == "BOUND":
            status = "GEBUNDEN"
            caution = "nur in einer registrierten Familie abtrennen"
            pair_ids = "NONE"
        elif entry["layer"] == "TABLE_LOCAL":
            status = "TAFELLOKAL"
            caution = "nicht in Prosa oder eine andere Tafel exportieren"
            pair_ids = "NONE"
        elif entry["layer"] == "LEARNED_BODY":
            status = "GELERNTER_FACHKÖRPER"
            caution = "nicht weiter in Einzelbuchstaben zerlegen"
            pair_ids = "NONE"
        elif entry["layer"] == "WHOLE_CARD":
            status = "GANZKARTE"
            caution = "nur als vollständige Karte lernen"
            pair_ids = "NONE"
        else:
            status = "AKTIVER_KERN"
            caution = "konkretes Nomen weiterhin vom Besitzer beziehen"
            pair_ids = "NONE"
        deck_rows.append({
            "teaching_order": entry["teaching_order"],
            "symbol": symbol,
            "layer": entry["layer"],
            "atomic_value_de": entry["atomic_value_de"],
            "owner_expansion_de": entry["owner_expansion_de"],
            "status": status,
            "surface_type_count": len(surface_hits),
            "visible_group_count": len(event_hits),
            "registers": "|".join(sorted({row["register"] for row in event_hits})) or "NONE",
            "pages": "|".join(sorted({row["page"] for row in event_hits})) or "NONE",
            "example_surfaces": "|".join(sorted({row["visible_surface"] for row in event_hits})[:12]) or "NONE",
            "minimal_pair_ids": pair_ids,
            "caution_de": caution,
        })
    write_tsv(OUT / "THIRTY_FIFTH_56_TEACHING_ENTRIES.tsv", deck_rows, list(deck_rows[0]))

    by_burden = Counter(row["teaching_class"] for row in enriched)
    groups_by_burden = Counter()
    for row in enriched:
        groups_by_burden[row["teaching_class"]] += int(row["observed_groups"])
    summary_rows = []
    for category in BURDEN_ACTION:
        members = [row for row in enriched if row["teaching_class"] == category]
        summary_rows.append({
            "teaching_class": category,
            "surface_type_count": by_burden[category],
            "visible_group_count": groups_by_burden[category],
            "apprentice_action_de": BURDEN_ACTION[category],
            "example_surfaces": "|".join(row["visible_surface"] for row in members[:12]) or "NONE",
        })
    write_tsv(
        OUT / "THIRTY_FIFTH_TEACHING_BURDEN.tsv",
        summary_rows,
        ["teaching_class", "surface_type_count", "visible_group_count", "apprentice_action_de", "example_surfaces"],
    )

    lines = [
        "# Gesamtes aktuelles Werkstattwörterbuch",
        "",
        "## Wie man die Tabellen benutzt",
        "",
        "Die 56 Lehrkasteneinträge sind keine 56 behaupteten deutschen Wörter. Sie bestehen",
        "aus portablen Kernen, gebundenen Graden, lokalen Tafelcodes, gelernten Fachkörpern",
        "und zwei Ganzkarten. Die 487 sichtbaren Formen zeigen, wie diese Einträge zusammen",
        "mit Schreiberrahmen und lokalen Resten tatsächlich erscheinen.",
        "",
        "## 56 Lehrkasteneinträge",
        "",
        "| Nr. | Zeichen | Schicht | Kurzlesung | Status | Formen / Gruppen |",
        "|---:|---|---|---|---|---:|",
    ]
    for row in deck_rows:
        lines.append(
            f"| {row['teaching_order']} | `{row['symbol']}` | {row['layer']} | {row['atomic_value_de']} | {row['status']} | {row['surface_type_count']} / {row['visible_group_count']} |"
        )
    lines.extend(["", "## Lernlast der 487 sichtbaren Formen", ""])
    for row in summary_rows:
        lines.append(
            f"- **{row['teaching_class']}**: {row['surface_type_count']} Formen / {row['visible_group_count']} Gruppen — {row['apprentice_action_de']}."
        )
    lines.extend(["", "## Alle sichtbaren Formen nach Lehrklasse", ""])
    for category in BURDEN_ACTION:
        members = sorted(row["visible_surface"] for row in enriched if row["teaching_class"] == category)
        lines.append(f"### {category}")
        lines.append("")
        lines.extend(chunks(members) or ["Keine."])
        lines.append("")
    lines.extend([
        "## Praktische Leseregel",
        "",
        "1. Register und sichtbaren Besitzer feststellen. 2. Ganzkarte oder gelernten Fachkörper",
        "vor einer Einzelzerlegung prüfen. 3. Portable Kerne und gebundene Grade lesen.",
        "4. q/s/ch/d/t-Rahmen nur nach registrierter Regel normalisieren. 5. Das konkrete",
        "Pflanzen-, Geräte- oder Himmelsnomen aus Bild und lokalem Exemplar ergänzen.",
    ])
    (OUT / "THIRTY_FIFTH_COMPLETE_HUMAN_DICTIONARY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    summary = {
        "status": "PASS",
        "counts": {
            "teaching_entries": len(deck_rows),
            "visible_surface_types": len(enriched),
            "visible_groups": sum(int(row["observed_groups"]) for row in enriched),
            "teaching_classes": len(summary_rows),
            "register_splits": by_burden["REGISTER_SPLIT"],
            "memorized_whole_cards": by_burden["MEMORIZED_WHOLE_CARD"],
        },
        "sources": {str(path.relative_to(ROOT)): sha256(path) for path in (SURFACES, LEDGER, DECK, VERDICTS)},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

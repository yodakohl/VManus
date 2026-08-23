#!/usr/bin/env python3
"""Build a compact productivity chart from the fixed-page literal parses."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
PARSES = ROOT / "experiments/yolo/sidequest_semantic_surface_compiler/COMPLETE_173_LITERAL_PARSE.tsv"
SURFACES = ROOT / "experiments/yolo/sidequest_semantic_surface_compiler/COMPLETE_230_SURFACE_PARSE.tsv"
OLD_GAPS = ROOT / "experiments/yolo/sidequest_semantic_surface_compiler/FORWARD_PREDICTIONS.tsv"
R96 = ROOT / "experiments/yolo/sidequest_semantic_compound_predictions_ninety_sixth_edition/NINETY_SIXTH_36_COMPOUND_PREDICTIONS.tsv"


HEADS = ["OK", "OT", "OL", "L", "CHD", "CTH", "CKH", "CHK", "SHED", "SOLK", "HO", "CHEO", "KCH", "TY", "SH"]
TAILS = ["BARE", "Y", "CLOSE", "AIIN", "AIN", "IIN", "AL", "AR", "AIR", "OR", "GRADED_Y", "GRADED_CLOSE"]
VALUES = {
    "OK": "ansetzen", "OT": "danach", "OL": "weiter", "L": "abführen",
    "CHD": "umsetzen", "CTH": "bereit", "CKH": "Durchlass", "CHK": "wärmen",
    "SHED": "absetzen", "SOLK": "sammeln", "HO": "Zutat", "CHEO": "Auszug",
    "KCH": "bearbeiten", "TY": "Teil", "SH": "halten", "Y": "dies",
    "CLOSE": "Schluss", "AIIN": "Sollmaß", "AIN": "Anteil", "IIN": "Stufe",
    "AL": "Ziel", "AR": "Quelle", "AIR": "Lauf", "OR": "Ansatz",
    "GRADED_Y": "kurz/länger/voll und offen", "GRADED_CLOSE": "kurz/länger/voll und Schluss",
    "BARE": "",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def collapse_tail(parts: list[str]) -> str | None:
    if not parts:
        return "BARE"
    joined = "+".join(parts)
    if joined in {"Y", "CLOSE", "AIIN", "AIN", "IIN", "AL", "AR", "AIR", "OR"}:
        return joined
    if len(parts) == 2 and parts[0] in {"E", "EE", "EEE"} and parts[1] == "Y":
        return "GRADED_Y"
    if len(parts) == 2 and parts[0] in {"E", "EE", "EEE"} and parts[1] == "CLOSE":
        return "GRADED_CLOSE"
    return None


def ordered_subsequence(needle: list[str], haystack: list[str]) -> bool:
    pos = 0
    for atom in haystack:
        if pos < len(needle) and needle[pos] == atom:
            pos += 1
    return pos == len(needle)


def main() -> None:
    parsed = read_tsv(PARSES)
    observed: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    other_complex: Counter[str] = Counter()
    for row in parsed:
        atoms = row["corrected_semantic_atoms"].split("+")
        if atoms[0] not in HEADS:
            continue
        tail = collapse_tail(atoms[1:])
        if tail is None:
            other_complex[atoms[0]] += 1
        else:
            observed[(atoms[0], tail)].append(row)

    predicted: dict[tuple[str, str], list[str]] = defaultdict(list)
    prediction_sequences: dict[tuple[str, str], set[str]] = defaultdict(set)
    for row in read_tsv(OLD_GAPS):
        seq = row["predicted_atom_sequence"].split("+")
        if seq[0] not in HEADS:
            continue
        tail = collapse_tail(seq[1:])
        if tail:
            predicted[(seq[0], tail)].append(row["predicted_short_reading_de"])
            prediction_sequences[(seq[0], tail)].add(row["predicted_atom_sequence"])
    for row in read_tsv(R96):
        seq = row["components"].split("+")
        if seq[0] not in HEADS:
            continue
        tail = collapse_tail(seq[1:])
        if tail and row["matched_surfaces"] == "NONE":
            predicted[(seq[0], tail)].append(row["predicted_workshop_meaning_de"])
            prediction_sequences[(seq[0], tail)].add(row["components"])

    cells: list[dict[str, object]] = []
    for head in HEADS:
        for tail in TAILS:
            hits = observed.get((head, tail), [])
            surfaces = sorted({surface for row in hits for surface in row["registered_surface_family"].split("|")})
            events = sum(int(row["prose_events"]) for row in hits)
            if hits:
                status = "FILLED_VISIBLE_CELL"
            elif (head, tail) in predicted:
                status = "FORWARD_PRODUCTIVE_GAP"
            else:
                status = "NO_LICENSED_COMBINATION_YET"
            meaning = " ".join(part for part in (VALUES[head], VALUES[tail]) if part)
            cells.append({
                "head": head,
                "head_value_de": VALUES[head],
                "tail_class": tail,
                "tail_value_de": VALUES[tail] or "NONE",
                "cell_status": status,
                "observed_master_cards": len(hits),
                "observed_events": events,
                "observed_surfaces": "|".join(surfaces) if surfaces else "NONE",
                "forward_sequences": "|".join(sorted(prediction_sequences.get((head, tail), set()))) or "NONE",
                "economical_reading_de": meaning,
            })

    families: list[dict[str, object]] = []
    for head in HEADS:
        subset = [row for row in cells if row["head"] == head]
        filled = sum(row["cell_status"] == "FILLED_VISIBLE_CELL" for row in subset)
        gaps = sum(row["cell_status"] == "FORWARD_PRODUCTIVE_GAP" for row in subset)
        cards = sum(int(row["observed_master_cards"]) for row in subset) + other_complex[head]
        events = sum(int(row["observed_events"]) for row in subset)
        if filled >= 7:
            tier = "BROAD_PRODUCTIVE_PARADIGM"
            apprentice_rule = "compose routinely; check long-card collisions"
        elif filled >= 4:
            tier = "BOUNDED_PRODUCTIVE_PARADIGM"
            apprentice_rule = "compose only listed tail classes"
        elif filled >= 2:
            tier = "NARROW_RECURRENT_PATTERN"
            apprentice_rule = "learn the attested mini-family; predict cautiously"
        else:
            tier = "WHOLE_CARD_FIRST"
            apprentice_rule = "memorize exact cards; component value is only a hint"
        families.append({
            "head": head,
            "minimal_value_de": VALUES[head],
            "filled_grid_cells": filled,
            "forward_gap_cells": gaps,
            "other_complex_card_types": other_complex[head],
            "grid_master_card_types": cards - other_complex[head],
            "grid_events": events,
            "productivity_tier": tier,
            "apprentice_rule": apprentice_rule,
        })

    collisions: list[dict[str, object]] = []
    for row in read_tsv(OLD_GAPS):
        if row["loose_surface_hits_in_230"] != "NONE":
            collisions.append({
                "predicted_atoms": row["predicted_atom_sequence"],
                "predicted_meaning_de": row["predicted_short_reading_de"],
                "surface_collision": row["loose_surface_hits_in_230"],
                "resolution": "LONGEST_REGISTERED_CARD_WINS",
                "workshop_consequence": "do not infer the shorter compound inside an existing longer card",
            })

    surface_atoms = {row["visible_surface"]: row["corrected_semantic_atoms"] for row in read_tsv(SURFACES)}
    corrections: list[dict[str, object]] = []
    for row in read_tsv(R96):
        if row["matched_surfaces"] == "NONE":
            continue
        wanted = row["components"].split("+")
        actual = sorted({surface_atoms[surface] for surface in row["matched_surfaces"].split(",")})
        support = [ordered_subsequence(wanted, atoms.split("+")) for atoms in actual]
        if all(atoms == row["components"] for atoms in actual):
            verdict = "SUPPORTED_EXACT_COMPONENT_SEQUENCE"
        elif all(support):
            verdict = "SUPPORTED_INSIDE_LICENSED_OUTER_FRAME"
        elif any(support):
            verdict = "MIXED_SURFACE_FAMILY_REQUIRES_WHOLE_CARD_CHECK"
        else:
            verdict = "WITHDRAW_MATCH__RENDERER_ALIAS_NOT_COMPOUND"
        corrections.append({
            "prediction_id": row["prediction_id"],
            "predicted_components": row["components"],
            "matched_surfaces": row["matched_surfaces"],
            "registered_actual_atoms": "|".join(actual),
            "reconciliation_verdict": verdict,
            "revised_workshop_use": "retain composition" if verdict.startswith("SUPPORTED") else "use registered whole-card/allograph value",
        })

    write_tsv(OUT / "NINETY_SEVENTH_180_CELL_PARADIGM.tsv", list(cells[0]), cells)
    write_tsv(OUT / "NINETY_SEVENTH_15_FAMILY_ECONOMY.tsv", list(families[0]), families)
    write_tsv(OUT / "NINETY_SEVENTH_COLLISION_LEDGER.tsv", list(collisions[0]), collisions)
    write_tsv(OUT / "NINETY_SEVENTH_R96_COMPOSITION_CORRECTIONS.tsv", list(corrections[0]), corrections)

    tiers = Counter(row["productivity_tier"] for row in families)
    status = Counter(row["cell_status"] for row in cells)
    broad = [row["head"] for row in families if row["productivity_tier"] == "BROAD_PRODUCTIVE_PARADIGM"]
    bounded = [row["head"] for row in families if row["productivity_tier"] == "BOUNDED_PRODUCTIVE_PARADIGM"]
    narrow = [row["head"] for row in families if row["productivity_tier"] == "NARROW_RECURRENT_PATTERN"]
    whole = [row["head"] for row in families if row["productivity_tier"] == "WHOLE_CARD_FIRST"]
    correction_counts = Counter(row["reconciliation_verdict"] for row in corrections)
    doc = [
        "# Siebenundneunzigste Runde: Wie produktiv sind die Stämme wirklich?", "",
        "## Werkstattergebnis", "",
        f"Breit produktiv: **{', '.join(broad) or 'keiner'}**.",
        f"Begrenzt produktiv: **{', '.join(bounded) or 'keiner'}**.",
        f"Schmale wiederkehrende Reihen: **{', '.join(narrow) or 'keine'}**.",
        f"Vorerst als Ganzkarten lernen: **{', '.join(whole) or 'keine'}**.", "",
        f"Die 15×12-Tafel enthält {status['FILLED_VISIBLE_CELL']} sichtbar gefüllte",
        f"Zellen, {status['FORWARD_PRODUCTIVE_GAP']} echte Vorwärtslücken und",
        f"{status['NO_LICENSED_COMBINATION_YET']} Kombinationen, die das aktuelle",
        "Werkstattsystem gar nicht verlangt. Eine leere Zelle ist also nicht automatisch",
        "ein noch unbekanntes Wort.", "",
        "Die erneute Kartenprüfung korrigiert außerdem vier zu großzügige Familien der",
        "sechsundneunzigsten Runde. Von 27 sichtbaren Regex-Treffern sind 23 echte",
        "Kompositionen, zwei gemischte Oberflächenfamilien und zwei Fehlzuordnungen.",
        "`taiin` ist AIIN-Allographie statt `TY+AIIN`; `lcheckhedy/shckhedy` enthalten",
        "CKHE statt CKH+E; `schedy` mischt CHD mit echten SHED-Formen, und",
        "`chckhal/kchal` mischt CKH+AL mit KCH+AL. TY wird daher vorerst als Ganzkarte",
        "gelernt und die drei anderen Familien werden beim längsten Kartenkörper geteilt.", "",
        "## Praktische Lehrregel", "",
        "Ein Schreiber darf breite Familien frei mit den gelisteten Enden verbinden.",
        "Bei begrenzten Familien darf er nur belegte Endklassen benutzen. Schmale Reihen",
        "werden als kleine Paradigmen gelernt; Ganzwortfamilien werden kopiert. Immer gilt",
        "die längste registrierte Karte vor einer kürzeren scheinbaren Zerlegung.", "",
        "Das wichtigste Ergebnis ist daher nicht mehr ‘alles ist kompositionell’, sondern",
        "eine glaubhafte Mischung aus produktivem Fachkürzel und gelerntem Nomenklator.",
        "Die feste `HO+AR`-Kollision zeigt den Nutzen: sichtbares `kchoar` bleibt",
        "`CHEO+AR` (aus dem Auszug) und wird nicht nachträglich zu `HO+AR` umgedeutet.", "",
        "Nur die festen Prosaseiten wurden verwendet; f84 und f84r blieben versiegelt.",
    ]
    (OUT / "NINETY_SEVENTH_PARADIGM_ECONOMY_REPORT.md").write_text("\n".join(doc) + "\n", encoding="utf-8")
    summary = {
        "status": "CONSISTENT", "families": len(families), "cells": len(cells),
        "cell_status": dict(status), "tiers": dict(tiers), "collisions": len(collisions),
        "r96_reconciliation": dict(correction_counts),
        "source_master_cards": len(parsed), "source_events": sum(int(row["prose_events"]) for row in parsed),
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

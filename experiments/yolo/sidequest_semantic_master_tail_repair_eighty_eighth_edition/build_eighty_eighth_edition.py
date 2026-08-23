#!/usr/bin/env python3
"""Replace unsupported exact recipe nouns with predictable workshop classes."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R86 = ROOT / "experiments/yolo/sidequest_semantic_concrete_codex_eighty_sixth_edition"
R87 = ROOT / "experiments/yolo/sidequest_semantic_textual_anchor_eighty_seventh_edition"


REPAIRS = {
    "H_R02": ("Wein", "Auszugsflüssigkeit", "CHEO/OR/AR beschreiben Auszug und Ansatz, aber keine bestimmte Flüssigkeit."),
    "H_R03": ("Öl", "Trägerstoff", "Ansetzen und äußerliche Verwendung bestimmen eine Trägerklasse, nicht Öl als Wort."),
    "H_R04": ("Honig", "Bindestoff", "Binden und Halten bestimmen die Funktion, nicht den Stoffnamen Honig."),
    "H_R05": ("Satz", "Restteil", "TY/Teil und der kleine Restposten tragen Rest, nicht Sediment als Substanz."),
    "H_R06": ("Trank", "dosiertes Mittel", "AIIN/AIN und Verwenden liefern Dosis plus Mittel, nicht die Einnahmeart."),
    "H_R07": ("Salbe", "streichfähiges Mittel", "Ansatz plus Auftragen liefert Konsistenz/Funktion, nicht die Gattung Salbe."),
    "H_R08": ("Einreibung", "äußerliche Anwendung", "AL/DAN und Halten liefern äußere Anwendung, nicht zwingend Reiben."),
    "H_R10": ("Auflage", "gebundene Anwendung", "Ziel plus Befestigen/Halten liefert gebundene Anwendung, nicht das Objektwort."),
}


UNIT_WORDS = {
    "H_R02": {"H3", "H4", "H5"}, "H_R03": {"H2", "H3"},
    "H_R04": {"H4", "H5"}, "H_R05": {"H1"},
    "H_R06": {"H1", "H3", "H5"}, "H_R07": {"H2"},
    "H_R08": {"H3"}, "H_R10": {"H2", "H4", "H5"},
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def replace_text(text: str) -> str:
    phrase_repairs = {
        "zur Salbe": "zu einem streichfähigen Mittel",
        "als Einreibung": "als äußerliche Anwendung",
        "als Auflage": "als gebundene Anwendung",
        "als Trank": "als dosiertes Mittel",
        "den Satz": "den Restteil",
    }
    for old, new in phrase_repairs.items():
        text = text.replace(old, new)
    for old, new, _ in REPAIRS.values():
        text = text.replace(old, new)
    return text


def main() -> None:
    audit = read_tsv(R87 / "EIGHTY_SEVENTH_44_WORD_ANCHOR_AUDIT.tsv")
    units = read_tsv(R86 / "EIGHTY_SIXTH_14_CONCRETE_CODEX_UNITS.tsv")
    binding = read_tsv(R86 / "EIGHTY_SIXTH_776_CONCRETE_CODEX_BINDING.tsv")

    repairs = []
    revised_lexicon = []
    for row in audit:
        out = dict(row)
        if row["codex_word_id"] in REPAIRS:
            old, new, reason = REPAIRS[row["codex_word_id"]]
            out["selected_word_de"] = new
            out["primary_anchor"] = "WORKSHOP_FUNCTION_CLASS"
            out["secondary_support"] = "EXACT_MATERIAL_OR_PRODUCT_REMAINS_CREATIVE_RIVAL"
            out["working_status"] = "REVISED_TO_PREDICTABLE_FUNCTION_CLASS"
            out["meaning_scope_de"] = reason
            repairs.append({
                "codex_word_id": row["codex_word_id"], "old_exact_guess_de": old,
                "selected_function_class_de": new, "used_units": row["used_units"],
                "card_slot_bridge": row["bridged_card_slots"],
                "candidate_dictionary_entries": row["licensing_dictionary_entries"],
                "why_de": reason, "exact_guess_status": "KEEP_AS_SECONDARY_CONTENT_RIVAL",
            })
        revised_lexicon.append(out)
    write_tsv(OUT / "EIGHTY_EIGHTH_8_MASTER_WORD_REPAIRS.tsv", repairs)
    write_tsv(OUT / "EIGHTY_EIGHTH_REVISED_44_SOURCE_WORDS.tsv", revised_lexicon)

    # Rank recurring visible identities by association with each repaired source program.
    prose = [row for row in binding if row["domain"] != "CELESTIAL_ALMANAC"]
    candidates = []
    for word_id, target_units in UNIT_WORDS.items():
        old, new, _ = REPAIRS[word_id]
        cards: dict[str, dict[str, object]] = defaultdict(lambda: {
            "target_events": 0, "outside_events": 0, "target_units": set(),
            "outside_units": set(), "reading": "",
        })
        for event in prose:
            card = cards[event["visible_identity"]]
            key = "target" if event["unit_id"] in target_units else "outside"
            card[f"{key}_events"] = int(card[f"{key}_events"]) + 1
            cast_set = card[f"{key}_units"]
            assert isinstance(cast_set, set)
            cast_set.add(event["unit_id"])
            card["reading"] = event["short_form_reading"]
        ranked = sorted(
            ((identity, data) for identity, data in cards.items() if int(data["target_events"])),
            key=lambda item: (
                len(item[1]["target_units"]),
                int(item[1]["target_events"]) / (int(item[1]["target_events"]) + int(item[1]["outside_events"])),
                int(item[1]["target_events"]),
            ), reverse=True,
        )[:8]
        for rank, (identity, data) in enumerate(ranked, 1):
            candidates.append({
                "codex_word_id": word_id, "old_guess_de": old,
                "selected_class_de": new, "rank": rank, "visible_identity": identity,
                "target_events": data["target_events"], "outside_events": data["outside_events"],
                "target_unit_coverage": ",".join(sorted(data["target_units"])),
                "outside_unit_coverage": ",".join(sorted(data["outside_units"])) or "NONE",
                "current_short_reading": data["reading"],
                "decision": "NO_EXACT_NOUN_PROMOTION__ASSOCIATION_ONLY",
            })
    write_tsv(OUT / "EIGHTY_EIGHTH_CARD_NEIGHBOR_CANDIDATES.tsv", candidates)

    revised_units = []
    unit_readings = {}
    for row in units:
        out = dict(row)
        out["concrete_reading_de"] = replace_text(row["concrete_reading_de"])
        out["lexical_revision"] = "FUNCTION_CLASS_REPAIR" if out["concrete_reading_de"] != row["concrete_reading_de"] else "UNCHANGED"
        revised_units.append(out)
        unit_readings[row["unit_id"]] = out["concrete_reading_de"]
    write_tsv(OUT / "EIGHTY_EIGHTH_14_REPAIRED_CODEX_UNITS.tsv", revised_units)

    revised_binding = []
    for row in binding:
        out = dict(row)
        out["concrete_unit_reading_de"] = unit_readings[row["unit_id"]]
        out["content_precision"] = "FUNCTION_CLASS_PRIMARY__EXACT_RECIPE_NOUN_SECONDARY" if row["unit_id"].startswith("H") else "UNCHANGED"
        revised_binding.append(out)
    write_tsv(OUT / "EIGHTY_EIGHTH_776_REPAIRED_BINDING.tsv", revised_binding)

    doc = [
        "# Achtundachtzigste Werkstattfassung: Reparatur des Rezeptwortschwanzes", "",
        "## Hauptentscheidung", "",
        "Die wiederkehrenden Karten liefern Prozess- und Funktionsklassen, aber keinen",
        "sauberen Schlüssel für Wein, Öl, Honig oder die vier modernen Produktnamen.",
        "Darum steht in der primären Rücklesung jetzt:", "",
    ]
    for row in repairs:
        doc.append(f"- {row['old_exact_guess_de']} → **{row['selected_function_class_de']}**")
    doc.extend([
        "", "Die alten konkreten Wörter bleiben als anschauliche zweite Lesung. Ein Schreiber",
        "kann also weiterhin Wein oder Öl gemeint haben; die Karte selbst verpflichtet ihn",
        "nur auf Auszugsflüssigkeit oder Trägerstoff. Das macht die Komposition lernbarer.", "",
        "## Fünf reparierte Pflanzenartikel", "",
    ])
    for row in revised_units[:5]:
        doc.extend([f"### {row['unit_id']} · {row['page']}", "", row["concrete_reading_de"], ""])
    doc.extend([
        "## Ergebnis der Nachbarschaftssuche", "",
        "Keines der acht alten Wörter besitzt eine exakte wiederkehrende Karte, die alle",
        "zugehörigen Artikel abdeckt und zugleich die übrigen Artikel meidet. Wiederkehrend",
        "sind vor allem Maß, Ansatz, Auszug, Ziel und Anwendungsoperation. Genau diese",
        "gemeinsamen Teile bilden nun die primären Funktionsklassen.", "",
        "Nur die festen zehn Seiten wurden verwendet; f84 und f84r blieben versiegelt.",
    ])
    (OUT / "EIGHTY_EIGHTH_EDITION_REPORT.md").write_text("\n".join(doc) + "\n", encoding="utf-8")

    summary = {
        "status": "CONSISTENT", "repaired_master_words": len(repairs),
        "candidate_rows": len(candidates), "source_words": len(revised_lexicon),
        "units": len(revised_units), "bound_groups": len(revised_binding),
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

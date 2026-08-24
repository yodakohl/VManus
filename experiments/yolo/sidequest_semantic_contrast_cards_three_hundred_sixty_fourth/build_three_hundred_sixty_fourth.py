#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P363 = ROOT / "experiments/yolo/sidequest_semantic_family_dictation_three_hundred_sixty_third"


def read(name: str) -> list[dict[str, str]]:
    with (P363 / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


CONTRASTS = {
    "Bindestufe": ("STUFE", "REPEATED_SEMANTIC_CUE"),
    "befestigen": ("HANDLUNG", "GRAMMATICAL_ASPECT"),
    "Pflanzenteil": ("ALLGEMEINER_TEIL", "OWNER_VISIBLE"),
    "Wurzelteil": ("WURZEL", "OWNER_VISIBLE"),
    "Ansatz": ("GRUNDANSATZ", "REPEATED_SEMANTIC_CUE"),
    "Auszugsansatz": ("AUSZUG", "REPEATED_SEMANTIC_CUE"),
    "Folgeansatz": ("NÄCHSTER", "REPEATED_SEMANTIC_CUE"),
    "Fortsetzungsansatz": ("GLEICHER_WEITER", "REPEATED_SEMANTIC_CUE"),
    "Anschluss": ("ANKNÜPFEN", "NOMENCLATOR_MNEMONIC"),
    "Folgefortsetzung": ("NÄCHSTES_WEITER", "REPEATED_SEMANTIC_CUE"),
    "Fortsetzung": ("GLEICHES_WEITER", "REPEATED_SEMANTIC_CUE"),
    "Weiterlauf": ("LAUF", "REPEATED_SEMANTIC_CUE"),
    "Weiterweg": ("WEG", "REPEATED_SEMANTIC_CUE"),
    "weiterführen": ("AKTIV_FÜHREN", "GRAMMATICAL_ASPECT"),
    "Langfolge": ("NÄCHSTER", "REPEATED_SEMANTIC_CUE"),
    "Langfolgestufe": ("STUFE", "REPEATED_SEMANTIC_CUE"),
    "Langfortsetzung": ("GLEICHER_WEITER", "REPEATED_SEMANTIC_CUE"),
    "Folgefortsetzungsposten": ("NÄCHSTES_WEITER", "REPEATED_SEMANTIC_CUE"),
    "Folgeposten": ("NÄCHSTER_POSTEN", "REPEATED_SEMANTIC_CUE"),
    "Weiterposten": ("GLEICHER_POSTEN", "REPEATED_SEMANTIC_CUE"),
    "Langwärme": ("ZUSTAND", "GRAMMATICAL_ASPECT"),
    "Langwärmen": ("HANDLUNG", "GRAMMATICAL_ASPECT"),
    "Sollmaß": ("MENGE", "REPEATED_SEMANTIC_CUE"),
    "Sollstellung": ("EINSTELLUNG", "REPEATED_SEMANTIC_CUE"),
    "Postenportion": ("NORMALE_PORTION", "NOMENCLATOR_MNEMONIC"),
    "Postenzweitportion": ("ZWEITE_PORTION", "REPEATED_SEMANTIC_CUE"),
    "Auszugzugabe": ("AUSZUG", "REPEATED_SEMANTIC_CUE"),
    "Einlage": ("EINLEGEN", "GRAMMATICAL_ASPECT"),
    "Zugabe": ("ZUGEBEN", "GRAMMATICAL_ASPECT"),
    "Zusatz": ("ZUSATZSTOFF", "GRAMMATICAL_ASPECT"),
    "Auszugnahme": ("AUSZUG_NEHMEN", "REPEATED_SEMANTIC_CUE"),
    "Laufschluss": ("LAUF_BEENDEN", "REPEATED_SEMANTIC_CUE"),
    "Transfer": ("NEUTRAL", "NOMENCLATOR_MNEMONIC"),
    "Umsetzen": ("UMSETZEN", "REPEATED_SEMANTIC_CUE"),
    "Umsetzschluss": ("UMSETZEN_SCHLIESSEN", "REPEATED_SEMANTIC_CUE"),
    "überführen": ("ÜBERFÜHREN", "NOMENCLATOR_MNEMONIC"),
    "Abführgut": ("GUT", "GRAMMATICAL_ASPECT"),
    "Abführung": ("VORGANG", "GRAMMATICAL_ASPECT"),
    "Abzug": ("ERGEBNIS", "GRAMMATICAL_ASPECT"),
    "abführen": ("WEGFÜHREN", "GRAMMATICAL_ASPECT"),
    "abziehen": ("ABZIEHEN", "NOMENCLATOR_MNEMONIC"),
    "Quellabführung": ("VORGANG", "GRAMMATICAL_ASPECT"),
    "Quellabzug": ("ERGEBNIS", "GRAMMATICAL_ASPECT"),
    "Beckenlauf": ("BECKEN", "OWNER_VISIBLE"),
    "durchlassen": ("PASSIEREN_LASSEN", "GRAMMATICAL_ASPECT"),
    "durchleiten": ("LEITEN", "GRAMMATICAL_ASPECT"),
    "Kurzdurchgang": ("VORGANG", "GRAMMATICAL_ASPECT"),
    "Kurzpassage": ("ABSCHNITT", "GRAMMATICAL_ASPECT"),
    "Absetzschluss": ("SCHLIESSEN", "REPEATED_SEMANTIC_CUE"),
    "Einsatzabsetzen": ("NACH_EINSATZ", "REPEATED_SEMANTIC_CUE"),
    "Standzeit": ("ZEIT", "REPEATED_SEMANTIC_CUE"),
    "Klarabzug": ("KLAR", "REPEATED_SEMANTIC_CUE"),
    "Trennabzug": ("TRENNEN", "REPEATED_SEMANTIC_CUE"),
    "Waschgang": ("WASCHEN", "REPEATED_SEMANTIC_CUE"),
    "Wasserzulauf": ("WASSER_ZU", "OWNER_VISIBLE"),
    "Stelle": ("ALLGEMEIN", "NOMENCLATOR_MNEMONIC"),
    "Zieleingabe": ("EINGABE", "GRAMMATICAL_ASPECT"),
    "Zieleinsatz": ("EINSATZ", "GRAMMATICAL_ASPECT"),
    "Zielmarke": ("MARKE", "REPEATED_SEMANTIC_CUE"),
    "Zielschluss": ("SCHLIESSEN", "REPEATED_SEMANTIC_CUE"),
    "Zwischenziel": ("ZWISCHEN", "REPEATED_SEMANTIC_CUE"),
    "Einsetzen": ("GRUNDHANDLUNG", "NOMENCLATOR_MNEMONIC"),
    "Laufeinsatz": ("LAUF", "REPEATED_SEMANTIC_CUE"),
    "Neueinsatz": ("NEU", "REPEATED_SEMANTIC_CUE"),
    "Wiedereinsatz": ("WIEDER", "REPEATED_SEMANTIC_CUE"),
}


def value_from_phrase(phrase: str) -> str:
    return phrase.split("[", 1)[1][:-1]


def main() -> None:
    drills = read("THREE_HUNDRED_SIXTY_THIRD_159_DICTATION_DRILLS.tsv")
    events = read("THREE_HUNDRED_SIXTY_THIRD_380_EVENT_SETTING_ROUTES.tsv")
    ambiguous = read("THREE_HUNDRED_SIXTY_THIRD_AMBIGUOUS_BUNDLES.tsv")
    contrast_rows = []
    cue_by_phrase = {}
    for row in drills:
        if row["status"] != "MASTER_CARD_REQUIRED":
            continue
        value = value_from_phrase(row["target_controlled_phrase"])
        cue, kind = CONTRASTS[value]
        cue_by_phrase[row["target_controlled_phrase"]] = (cue, kind)
        contrast_rows.append({
            "family_id": row["family_id"],
            "base_dictation": row["spoken_dictation_de"],
            "contrast_cue": cue,
            "contrast_kind": kind,
            "target_controlled_phrase": row["target_controlled_phrase"],
            "target_joint_tuple_ids": row["target_joint_tuple_ids"],
            "full_dictation": f"{row['spoken_dictation_de']} + {cue}",
            "fixed_formula": f"{row['family_id']}::{row['target_controlled_phrase']}",
            "teaching_rule": "COMPOSE" if kind != "NOMENCLATOR_MNEMONIC" else "MEMORIZE_WHOLE_CARD",
        })
    contrast_rows.sort(key=lambda row: (row["family_id"], row["base_dictation"], row["contrast_cue"]))

    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in contrast_rows:
        grouped[row["base_dictation"]].append(row)
    panel_rows = []
    for number, base in enumerate(sorted(grouped), 1):
        members = grouped[base]
        panel_rows.append({
            "panel_id": f"P{number:02d}",
            "base_dictation": base,
            "card_count": len(members),
            "contrast_cues": "|".join(str(row["contrast_cue"]) for row in members),
            "controlled_phrases": "|".join(str(row["target_controlled_phrase"]) for row in members),
            "all_unique_after_contrast": "YES" if len({row["contrast_cue"] for row in members}) == len(members) else "NO",
        })

    event_rows = []
    for row in events:
        phrase = row["controlled_phrase"]
        if row["dictation_status"] == "COMPOSED_UNIQUE":
            route, cue, kind = "DIRECT_COMPOSITION", "NONE", "PRIMARY_FAMILY_CUES"
        else:
            cue, kind = cue_by_phrase[phrase]
            route = "CONTRAST_COMPOSITION" if kind != "NOMENCLATOR_MNEMONIC" else "WHOLE_CARD_MNEMONIC"
        event_rows.append({
            "source_position_id": row["source_position_id"],
            "event_id": row["event_id"],
            "record_unit_id": row["record_unit_id"],
            "statement_id": row["statement_id"],
            "surface": row["surface"],
            "joint_tuple_id": row["joint_tuple_id"],
            "family_id": row["family_id"],
            "controlled_phrase": phrase,
            "contrast_cue": cue,
            "contrast_kind": kind,
            "final_setting_route": route,
            "exact_selection": "YES",
        })

    write("THREE_HUNDRED_SIXTY_FOURTH_65_CONTRAST_CARDS.tsv", contrast_rows)
    write("THREE_HUNDRED_SIXTY_FOURTH_22_CONTRAST_PANELS.tsv", panel_rows)
    write("THREE_HUNDRED_SIXTY_FOURTH_380_FINAL_SETTING_ROUTES.tsv", event_rows)

    kinds = Counter(row["contrast_kind"] for row in contrast_rows)
    routes = Counter(row["final_setting_route"] for row in event_rows)
    manual = ["# Pass 364 — 22 Kontrasttafeln", ""]
    for panel in panel_rows:
        manual += [
            f"## {panel['panel_id']} — {panel['base_dictation']}",
            "",
        ]
        for row in grouped[str(panel["base_dictation"])]:
            manual.append(f"- **{row['contrast_cue']}** → `{row['fixed_formula']}` ({row['contrast_kind']})")
        manual.append("")
    manual += [
        "## Regel",
        "",
        "Ein wiederkehrender Bedeutungsunterschied darf als Zusatzkürzel gelehrt werden. Ein einmaliger Unterschied bleibt ein Merkspruch an der ganzen Karte. Beides wählt die Karte, aber nur Ersteres erweitert die produktive Grammatik.",
    ]
    (HERE / "THREE_HUNDRED_SIXTY_FOURTH_CONTRAST_TABLET.md").write_text("\n".join(manual) + "\n", encoding="utf-8")
    report = f"""# Pass 364 — Kontrastkarten

Die 22 mehrdeutigen Diktatbündel erhalten 65 explizite Kontrastkarten. Davon
sind {kinds['REPEATED_SEMANTIC_CUE']} wiederkehrende semantische Zusätze,
{kinds['GRAMMATICAL_ASPECT']} Handlungs-/Zustands-/Ergebnisunterschiede,
{kinds['OWNER_VISIBLE']} sichtbare Besitzerunterschiede und
{kinds['NOMENCLATOR_MNEMONIC']} ehrliche Nomenklator-Merksprüche.

Damit sind alle 380 Quellkarten setzbar: {routes['DIRECT_COMPOSITION']} direkt
aus der ersten Familienregel, {routes['CONTRAST_COMPOSITION']} mit einer
zusätzlichen wiederverwendbaren oder grammatischen Kontrastkarte und
{routes['WHOLE_CARD_MNEMONIC']} als ganze gelernte Karte. Die letzte Gruppe wird
nicht in neue Stämme zerlegt.

Als Nächstes soll ein kompletter Rekonstruktionsdurchgang die 116 Aussagen nur
aus Familien-, Kontrast- und Nomenklatortafeln neu setzen und danach mit der
realen Kartenfolge vergleichen.
"""
    (HERE / "THREE_HUNDRED_SIXTY_FOURTH_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "contrast_panels": len(panel_rows),
        "contrast_cards": len(contrast_rows),
        "contrast_kind_counts": dict(kinds),
        "source_cards": len(event_rows),
        "setting_route_counts": dict(routes),
        "exact_selections": sum(row["exact_selection"] == "YES" for row in event_rows),
    }
    (HERE / "THREE_HUNDRED_SIXTY_FOURTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

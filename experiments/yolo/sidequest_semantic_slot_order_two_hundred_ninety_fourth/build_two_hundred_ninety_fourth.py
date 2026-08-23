#!/usr/bin/env python3
"""Recover the visible left-to-right slot order of the 64 prose frame cards."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
CLASSIFIED = ROOT / "experiments/yolo/sidequest_semantic_full_prose_morphology_two_hundred_ninety_third/TWO_HUNDRED_NINETY_THIRD_149_CARD_PRODUCTION_CLASSIFICATION.tsv"
DICTIONARY = ROOT / "experiments/yolo/sidequest_semantic_two_layer_prose_two_hundred_seventy_ninth/TWO_HUNDRED_SEVENTY_NINTH_173_TWO_LAYER_DICTIONARY.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


FRAMES = {"Q_FRAME", "D_SIDE_FRAME", "D_TERMINAL_FRAME", "R_FRAME", "OLS_BELOW"}
RANK = {"PREFIX_SELECTOR": 1, "PROCESS_BODY": 2, "ADDRESS": 3, "VALUE_STAGE": 4, "CURRENT_REFERENT": 5, "COMMIT": 6}


def macro_slot(atom: str) -> str:
    atom = atom.strip()
    if atom in FRAMES:
        return "RENDERER_FRAME"
    if atom.startswith(("OK", "OT", "L_OUT", "LCH_WITHDRAW", "LD_END")):
        return "PREFIX_SELECTOR"
    if atom.startswith("OL") or atom == "OL":
        return "MOBILE_CONTINUATION"
    if atom.startswith(("AR", "AL")):
        return "ADDRESS"
    if atom.startswith(("AIIN", "AIN", "IIN")):
        return "VALUE_STAGE"
    if atom.startswith("Y") or atom == "Y":
        return "CURRENT_REFERENT"
    if atom.startswith(("DY", "CLOSE", "TERMINAL")) or atom == "DY":
        return "COMMIT"
    return "PROCESS_BODY"


def main() -> None:
    classified = read_tsv(CLASSIFIED)
    dictionary = {row["master_card_id"]: row for row in read_tsv(DICTIONARY)}
    slot_cards = [row for row in classified if row["production_mechanic"] == "ORDERED_SLOT_FRAME_ASSEMBLY"]
    output = []
    pairwise: Counter[tuple[str, str]] = Counter()
    ol_position = Counter()
    exceptions = []

    for row in slot_cards:
        source = dictionary[row["master_card_id"]]
        atoms = [part.strip() for part in source["old_component_parse"].split("+")]
        macros = [macro_slot(atom) for atom in atoms]
        ranked = [slot for slot in macros if slot not in {"RENDERER_FRAME", "MOBILE_CONTINUATION"}]
        ranks = [RANK[slot] for slot in ranked]
        fits = ranks == sorted(ranks)
        for left_index, left in enumerate(ranked):
            for right in ranked[left_index + 1:]:
                if left != right:
                    pairwise[(left, right)] += 1

        if "MOBILE_CONTINUATION" not in macros:
            ol_place = "NO_OL"
        else:
            ol_index = macros.index("MOBILE_CONTINUATION")
            content_indices = [i for i, value in enumerate(macros) if value in {"PROCESS_BODY", "ADDRESS", "VALUE_STAGE", "CURRENT_REFERENT"}]
            ol_place = "POSTPOSED_AFTER_CONTENT" if content_indices and ol_index > min(content_indices) else "PREFIX_OR_SELECTOR_CHAIN"
            ol_position[ol_place] += 1

        output.append({
            "master_card_id": row["master_card_id"],
            "canonical_surface": row["canonical_surface"],
            "canonical_value_de": row["canonical_value_de"],
            "semantic_recipe": row["final_recipe"],
            "visible_component_order": ">".join(atoms),
            "visible_macro_order": ">".join(macros),
            "default_order_without_renderer_and_ol": ">".join(ranked),
            "fits_default_slot_order": "YES" if fits else "NO",
            "ol_placement": ol_place,
            "renderer_frames": "|".join(atom for atom in atoms if atom in FRAMES) or "NONE",
            "event_support": row["event_support"],
            "writer_instruction_de": "Schreibe Rahmen/Selektor, dann Prozesskörper, Adresse, Wert/Stufe, aktuellen Posten und Schluss; OL darf als Fortsetzungszeichen vor- oder nachgestellt werden.",
        })
        if not fits:
            exceptions.append({
                "master_card_id": row["master_card_id"],
                "canonical_surface": row["canonical_surface"],
                "visible_component_order": ">".join(atoms),
                "visible_macro_order": ">".join(macros),
                "canonical_value_de": row["canonical_value_de"],
                "exception_type": "FRONTED_REFERENT" if macros[0] == "CURRENT_REFERENT" else "FRONTED_ADDRESS_WITH_RENDERER",
                "apprentice_treatment_de": "Als gelernte invertierte Karte behalten; nicht zur allgemeinen Wortfolge machen.",
            })

    slot_path = HERE / "TWO_HUNDRED_NINETY_FOURTH_64_SLOT_ORDER_CARDS.tsv"
    exception_path = HERE / "TWO_HUNDRED_NINETY_FOURTH_2_FRONTED_EXCEPTIONS.tsv"
    write_tsv(slot_path, output)
    write_tsv(exception_path, exceptions)

    pair_rows = []
    for (left, right), count in sorted(pairwise.items(), key=lambda item: (-item[1], item[0])):
        reverse = pairwise[(right, left)]
        pair_rows.append({
            "left_slot": left,
            "right_slot": right,
            "left_before_right_cards": count,
            "right_before_left_cards": reverse,
            "workshop_rule": "DEFAULT_LEFT_BEFORE_RIGHT" if reverse == 0 else "TWO_LEARNED_FRONTING_EXCEPTIONS_EXIST",
        })
    pair_path = HERE / "TWO_HUNDRED_NINETY_FOURTH_PAIRWISE_SLOT_ORDER.tsv"
    write_tsv(pair_path, pair_rows)

    manual = """# Linksläufige Schreibtafel für Slotkarten

## Die Grundzeile

Der Lehrling schreibt eine zusammengesetzte Slotkarte in dieser sichtbaren Ordnung:

`[RENDERERRAHMEN] [OK/OT/L-SELEKTOR] [PROZESSKÖRPER] [AR/AL-ADRESSE] [AIIN/AIN/IIN-WERT] [Y-POSTEN] [DY-SCHLUSS]`

Nicht jede Karte besitzt jeden Platz. Leere Plätze werden übersprungen.

Beispiele:

- `ok-aiin` → `okaiin`: einsetzen + Sollwert;
- `ot-al` → `otal`: Folgeposten + Ziel;
- `shed-al` → `shedal`: absetzen + Ziel;
- `cho-aiin` → `chodaiin`: Eingabe + Sollwert;
- `ar-y` → `chary`: Quelle + aktueller Posten;
- `air-y-dy` → `dairydy`: Lauf + Posten + Schluss, mit gelerntem D-Rahmen.

## Das bewegliche OL

OL ist kein gewöhnlicher Sachstamm, sondern ein Fortsetzungszeichen. In elf Karten steht es im Präfix-/Selektorzug; in zwei Karten folgt es einem bereits geschriebenen Körper oder Posten. Darum darf der Schreiber OL voranstellen oder nachtragen, ohne die übrige Slotordnung zu ändern. Die zwei echten Nachträge sind `octheol` und `otytchol`; `lol` bleibt eine L+OL-Selektorkette.

## Nur zwei invertierte Karten

- `ycheor`: Y steht vor CHEO+OR; die Karte bedeutet den aktuell gemeinten Auszugsansatz.
- `chealror`: AL steht vor dem OR-Körper und trägt zusätzlich einen R-Rahmen.

Beide werden als gelernte Inversionen kopiert. Sie erzeugen keine alternative Allgemeinsyntax.

## Reichweite

62 von 64 Slotkarten folgen der Grundzeile, sobald reine Rendererrahmen ignoriert und OL als bewegliches Fortsetzungszeichen behandelt wird. Das ist ausreichend einfach für mehrere Schreiber: eine Zeile, ein mobiles Fortsetzungszeichen, zwei bekannte Ausnahmen.
"""
    manual_path = HERE / "TWO_HUNDRED_NINETY_FOURTH_SLOT_ORDER_MANUAL.md"
    manual_path.write_text(manual, encoding="utf-8")

    report = """# Sidequest-Pass 294: die sichtbare Reihenfolge der Slotkarten

## Ergebnis

Die alte sichtbare Komponentenzerlegung und die neue Bedeutungsgrammatik lassen sich auf eine gemeinsame Schreibrichtung bringen. Nach Abzug reiner Rendererrahmen und Behandlung von OL als mobilem Fortsetzungszeichen folgen 62 der 64 Slotkarten derselben Ordnung:

**Selektor → Prozesskörper → Adresse → Wert/Stufe → aktueller Posten → Schluss.**

Die Daten erzwingen nicht jede mögliche Nachbarschaft; insbesondere stehen Adresse und Wert selten gemeinsam in derselben Slotkarte. Aber jede tatsächlich sichtbare Kombination außer zwei gelernten Inversionen ist mit dieser Zeile vereinbar.

Die zwei Ausnahmen sind `ycheor` und `chealror`. Sie werden nicht wegnormalisiert, sondern als frontierte Ganzformen im Lehrdeck behalten. OL ist in elf Karten prä- oder selektornah und in zwei nach einem Inhaltsplatz; seine Beweglichkeit erklärt `octheol` und `otytchol` ohne neue Bedeutung.

## Nächster Angriff

Die 20 CHD/CHED-Überlagerungen bekommen nun dieselbe buchstabennahe Behandlung. Wir suchen ihre linken und rechten Slots, die Bedingungen für CHD gegen CHED und die Stellung von DY, damit `pchedain` nicht nur semantisch, sondern auch graphisch zwingend wird.
"""
    report_path = HERE / "TWO_HUNDRED_NINETY_FOURTH_REPORT.md"
    report_path.write_text(report, encoding="utf-8")

    summary = {
        "status": "PASS",
        "slot_cards": len(output),
        "slot_events": sum(int(row["event_support"]) for row in output),
        "default_order_fit": sum(row["fits_default_slot_order"] == "YES" for row in output),
        "fronted_exceptions": len(exceptions),
        "ol_mobile_cards": sum(ol_position.values()),
        "ol_prefix_or_selector_chain": ol_position["PREFIX_OR_SELECTOR_CHAIN"],
        "ol_postposed_after_content": ol_position["POSTPOSED_AFTER_CONTENT"],
        "renderer_framed_cards": sum(row["renderer_frames"] != "NONE" for row in output),
        "source_hashes": {str(path.relative_to(ROOT)): sha(path) for path in [CLASSIFIED, DICTIONARY]},
        "outputs": {path.name: sha(path) for path in [slot_path, exception_path, pair_path, manual_path, report_path]},
    }
    (HERE / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

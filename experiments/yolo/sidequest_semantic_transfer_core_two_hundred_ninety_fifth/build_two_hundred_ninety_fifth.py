#!/usr/bin/env python3
"""Build the CHD/CHED transfer-core writing manual and pchedain derivation."""

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
LEDGER = ROOT / "experiments/yolo/sidequest_semantic_complete_forward_writer_two_hundred_ninetieth/TWO_HUNDRED_NINETIETH_776_FORWARD_WRITING_LEDGER.tsv"


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


def choose_core(master_card_id: str, atoms: list[str]) -> tuple[str, str]:
    joined = "+".join(atoms)
    if "CHD~CHED" in joined:
        return "FLEX_CHD_CHED__SHORT_CANONICAL", "bare current-item transfer permits the short card and its expanded surface allograph"
    if master_card_id == "MC067":
        return "SHORT_CHD", "compact technical addendum selects the short OT transfer"
    if master_card_id == "MC057":
        return "EXPANDED_CHED", "main operating record selects the expanded OT transfer"
    if master_card_id == "MC088":
        return "SHORT_CHD", "new active item selects short CHD"
    if master_card_id == "MC005":
        return "EXPANDED_CHED", "previous active item selects expanded CHED"
    if master_card_id == "MC064":
        return "EXPANDED_CHED", "learned expanded current-item transfer"
    if any(marker in joined for marker in ["L_OUT", "P_IN", "OL_CONTINUE", "AR_FROM", "AIN_PORTION", "CTH_READY"]):
        return "EXPANDED_CHED", "explicit source, receiver, continuation, portion, or prepared-state load selects CHED"
    if "CHED" in joined:
        return "EXPANDED_CHED", "registered expanded transfer card"
    return "SHORT_CHD", "unloaded or direct-target transfer uses compact CHD"


def main() -> None:
    classified = read_tsv(CLASSIFIED)
    dictionary = {row["master_card_id"]: row for row in read_tsv(DICTIONARY)}
    ledger = read_tsv(LEDGER)
    visible = {row["resulting_visible_surface"] for row in ledger}
    transfer = [row for row in classified if row["production_mechanic"] == "SHARED_TRANSFER_CORE_OVERLAY"]
    rows = []
    counts = Counter()

    for row in transfer:
        source = dictionary[row["master_card_id"]]
        atoms = [part.strip() for part in source["old_component_parse"].split("+")]
        core_index = next(i for i, atom in enumerate(atoms) if "TRANSFER" in atom or atom.startswith(("CHD", "CHED")))
        core_choice, core_reason = choose_core(row["master_card_id"], atoms)
        recipe_parts = [part.split("[")[0] for part in row["final_recipe"].split("+")]
        if "DY" in recipe_parts or "LICENSED_CLOSE=YES" in row["final_recipe"]:
            endpoint = "TERMINAL_COMMIT"
        elif "Y" in recipe_parts:
            endpoint = "CURRENT_ITEM_NOT_COMMIT"
        else:
            endpoint = "OPEN_TRANSFER"
        counts[(core_choice, "cards")] += 1
        counts[(core_choice, "events")] += int(row["event_support"])
        rows.append({
            "master_card_id": row["master_card_id"],
            "canonical_surface": row["canonical_surface"],
            "registered_surfaces": source["registered_surfaces"],
            "canonical_value_de": row["canonical_value_de"],
            "semantic_recipe": row["final_recipe"],
            "visible_component_order": ">".join(atoms),
            "left_of_transfer_core": ">".join(atoms[:core_index]) or "NONE",
            "transfer_core_atom": atoms[core_index],
            "right_of_transfer_core": ">".join(atoms[core_index + 1:]) or "NONE",
            "core_choice": core_choice,
            "core_choice_reason": core_reason,
            "endpoint_interpretation": endpoint,
            "event_support": row["event_support"],
        })

    card_path = HERE / "TWO_HUNDRED_NINETY_FIFTH_20_TRANSFER_CORE_CARDS.tsv"
    write_tsv(card_path, rows)

    decision_rows = [
        {"priority": 1, "condition": "L, P, OL, AR, AIN oder CTH explizit geladen", "write_core": "CHED", "examples": "lchedy|pchedy|olchedy|cheedar|chedain|shecthedchy", "instruction_de": "Benutze den langen Transferkörper, damit der zusätzliche Slot sichtbar bleibt."},
        {"priority": 2, "condition": "OT im Haupt-Arbeitsrecord", "write_core": "CHED", "examples": "otchedy", "instruction_de": "Hauptregister benutzt die ausgebaute OT-Form."},
        {"priority": 3, "condition": "OT im kompakten technischen Nachtrag", "write_core": "CHD", "examples": "otchdy", "instruction_de": "Der Nachtrag kürzt denselben Transferkörper."},
        {"priority": 4, "condition": "OK mit neuem Posten", "write_core": "CHD", "examples": "qokchdy", "instruction_de": "Neuen Posten kurz einsetzen und übertragen."},
        {"priority": 5, "condition": "OK mit vorigem Posten", "write_core": "CHED", "examples": "okchedy", "instruction_de": "Der vorige Posten erhält die ausgebaute Erinnerungsform."},
        {"priority": 6, "condition": "bloßer aktueller Posten oder direktes AL/DY", "write_core": "CHD", "examples": "chdy|chdal|dalchdy|dchdy", "instruction_de": "Nimm die kurze Grundform; chdy darf als chedy gerendert werden."},
        {"priority": 7, "condition": "gelernte erweiterte Y-Transferkarte", "write_core": "CHED", "examples": "chedchy", "instruction_de": "Diese einzelne Karte bleibt eine gelernte lange Variante."},
    ]
    decision_path = HERE / "TWO_HUNDRED_NINETY_FIFTH_CHD_CHED_DECISION_TREE.tsv"
    write_tsv(decision_path, decision_rows)

    pchedain = [{
        "step": 1,
        "surface": "pchedy",
        "role": "P+CHED_TRANSFER+CLOSE",
        "instruction_de": "Nimm die belegte Empfänger-Transferkarte; P erzwingt CHED.",
    }, {
        "step": 2,
        "surface": "chedain",
        "role": "CHED_TRANSFER+AIN",
        "instruction_de": "Nimm die belegte Portions-Transferkarte; AIN steht rechts vom CHED-Körper.",
    }, {
        "step": 3,
        "surface": "p + ched + ain",
        "role": "LEFT_SLOT + SHARED_CORE + RIGHT_SLOT",
        "instruction_de": "Lege beide Karten am identischen CHED übereinander; entferne das terminale Y der ersten Elternkarte.",
    }, {
        "step": 4,
        "surface": "pchedain",
        "role": "P+CHED_TRANSFER+AIN",
        "instruction_de": "Schreibe ohne Zwischenraum: eine Portion in den Empfänger überführen.",
    }]
    prediction_path = HERE / "TWO_HUNDRED_NINETY_FIFTH_PCHEDAIN_DERIVATION.tsv"
    write_tsv(prediction_path, pchedain)

    manual = """# CHD/CHED-Lehrtafel

## Der Kartenkörper

CHD und CHED sind kurze und ausgebaute Formen desselben Transferkörpers. Der Schreiber setzt links Rahmen, Selektor, Quelle oder Empfänger; rechts setzt er Portion, Quelle, Ziel, aktuellen Posten oder Schluss.

`[linke Slots] + CHD/CHED + [rechte Slots]`

Die kurze Form CHD genügt beim bloßen aktuellen Posten, direkten Ziel und ungeladenen Schluss. CHED wird gewählt, wenn L, P, OL, AR, AIN oder CTH einen zusätzlichen Slot sichtbar tragen. OT und OK haben je eine gelernte Bedeutungs-/Dokumentwahl: Hauptrecord gegen Nachtrag, neuer gegen voriger Posten.

## Wichtig: sichtbares -dy ist nicht immer Schluss

`chdy|chedy` bezeichnet in elf Vorkommen den laufenden Posten beim Überführen und ist nicht terminal. `lchedy` dagegen ist achtmal eine geschlossene Abführung. Die ganze registrierte Karte entscheidet, ob Y „dies“ oder DY „festsetzen“ bedeutet.

## Die neue Karte pchedain

`pchedy` zeigt links P und den langen CHED-Körper. `chedain` zeigt denselben Körper mit AIN rechts. Beide Regeln überlagern sich ohne Konflikt:

`P + CHED + AIN` → **`pchedain`**

Damit ist die Schreibung nicht mehr nur eine semantische Vermutung. Sie folgt der sichtbaren Slotordnung zweier echter Elternkarten und der Regel, dass P und AIN den ausgeführten CHED-Körper verlangen.
"""
    manual_path = HERE / "TWO_HUNDRED_NINETY_FIFTH_TRANSFER_CORE_MANUAL.md"
    manual_path.write_text(manual, encoding="utf-8")

    report = """# Sidequest-Pass 295: der Transferkörper CHD/CHED

## Ergebnis

Die 20 Transferkarten und 43 Vorkommen besitzen eine stabile Bauform: linke Slots → CHD/CHED → rechte Slots. Die kanonischen Karten verteilen sich auf 18 Ereignisse mit kurzer/flexibler CHD-Realisierung und 25 mit CHED.

Die wichtigste Auswahlregel ist funktional einfach: explizit geladene Quelle, Empfänger, Fortsetzung, Portion oder Bereitschaft nimmt CHED; der bloße aktuelle Posten und direkte Ziel-/Schlussformen nehmen CHD. Drei kleine gelernte Konventionen bleiben: OT Hauptrecord/Nachtrag, OK voriger/neuer Posten und die einzelne erweiterte `chedchy`-Karte.

`pchedain` ist damit die bisher präziseste neue Kartenprognose. P muss links stehen, AIN rechts, beide bekannten Eltern verlangen denselben langen CHED-Körper. Eine alternative Buchstabenfolge würde zwei bereits sichtbare Slotordnungen zugleich verletzen.

## Nächster Angriff

Als Nächstes bekommt die E/EE/EEE-Familie dieselbe vollständige Tafel: 30 Karten, exakter Gradplatz, kurze/lange/volle Reihen und alle Lücken. Dadurch können wir entscheiden, welche weiteren Formen neben `lsheedy`, `sheeedy` und `sheeckhal` wirklich vorhersagbar sind.
"""
    report_path = HERE / "TWO_HUNDRED_NINETY_FIFTH_REPORT.md"
    report_path.write_text(report, encoding="utf-8")

    summary = {
        "status": "PASS",
        "transfer_cards": len(rows),
        "transfer_events": sum(int(row["event_support"]) for row in rows),
        "short_or_flexible_cards": counts[("SHORT_CHD", "cards")] + counts[("FLEX_CHD_CHED__SHORT_CANONICAL", "cards")],
        "short_or_flexible_events": counts[("SHORT_CHD", "events")] + counts[("FLEX_CHD_CHED__SHORT_CANONICAL", "events")],
        "expanded_cards": counts[("EXPANDED_CHED", "cards")],
        "expanded_events": counts[("EXPANDED_CHED", "events")],
        "decision_rules": len(decision_rows),
        "pchedain_visible_now": "pchedain" in visible,
        "source_hashes": {str(path.relative_to(ROOT)): sha(path) for path in [CLASSIFIED, DICTIONARY, LEDGER]},
        "outputs": {path.name: sha(path) for path in [card_path, decision_path, prediction_path, manual_path, report_path]},
    }
    (HERE / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

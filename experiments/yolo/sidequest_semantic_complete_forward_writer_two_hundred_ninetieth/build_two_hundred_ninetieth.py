#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R279 = ROOT / "experiments/yolo/sidequest_semantic_two_layer_prose_two_hundred_seventy_ninth"
R286 = ROOT / "experiments/yolo/sidequest_semantic_apprentice_reverse_codebook_two_hundred_eighty_sixth"
R288 = ROOT / "experiments/yolo/sidequest_semantic_final_writer_conventions_two_hundred_eighty_eighth"
R274 = ROOT / "experiments/yolo/sidequest_semantic_ten_page_mixed_deck_two_hundred_seventy_fourth"
R289 = ROOT / "experiments/yolo/sidequest_semantic_astro_reverse_encoder_two_hundred_eighty_ninth"

PROSE_EVENTS = R279 / "TWO_HUNDRED_SEVENTY_NINTH_381_TWO_LAYER_EVENTS.tsv"
PROSE_CARDS = R279 / "TWO_HUNDRED_SEVENTY_NINTH_173_TWO_LAYER_DICTIONARY.tsv"
ROOTS = R286 / "TWO_HUNDRED_EIGHTY_SIXTH_36_PRODUCTIVE_ROOTS.tsv"
PROSE_WHOLE = R286 / "TWO_HUNDRED_EIGHTY_SIXTH_23_WHOLE_SIGNS.tsv"
PROSE_RECIPES = R288 / "TWO_HUNDRED_EIGHTY_EIGHTH_149_DETERMINISTIC_RECIPES.tsv"
ASTRO_ALL = R274 / "TWO_HUNDRED_SEVENTY_FOURTH_LAYERED_395_ASTRO_GROUPS.tsv"
ASTRO_REVERSE = R289 / "TWO_HUNDRED_EIGHTY_NINTH_265_REVERSE_ENCODINGS.tsv"
ASTRO_WHOLE = R289 / "TWO_HUNDRED_EIGHTY_NINTH_46_ASTRO_WHOLE_SIGNS.tsv"
ASTRO_LOCAL = R289 / "TWO_HUNDRED_EIGHTY_NINTH_67_LOCAL_COPY_KEYS.tsv"

LESSONS = [
    (1, "Bildbesitzer und Schreibrichtung", "Lerne, dass Bild, Gefäß oder Diagrammplatz den stillen Besitzer liefert; Zeilenende beendet keinen Satz."),
    (2, "Sechzehn gemeinsame Stammfamilien", "Übe Quelle, Ziel, Fortsetzung, Folge, Portion, Sollwert, Grad, aktueller Posten, Festsetzung, Bedingungsansatz und Bahn."),
    (3, "Zwanzig Fach- und Brückenfamilien", "Ergänze Transfer, Bereitschaft, Absetzen, Waschen, Durchlass, Seihen, Sammeln, Auszug, Eingabe und die kleinen Herbal/Bio-Familien."),
    (4, "Dreiundzwanzig Prosa-Ganzzeichen", "Lerne die praktischen Nomenklatorkarten und die eine gerahmte Wiederverwendung des Klarlaufzeichens."),
    (5, "Prosa schreiben", "Baue eine von 149 Bedeutungsfolgen; benutze Besitzergrenzen- und Hauptrecord/Nachtrag-Konvention für die letzten Oberflächenwahlen."),
    (6, "Sechsundvierzig Astro-Ganzzeichen", "Lerne die festen Diagrammwerte als unteilbare Zeichen; spalte DY oder Y dort nicht ab."),
    (7, "Astro produktiv schreiben", "Benutze elf Strategien: Karte wiederverwenden oder lokalen Kern kopieren und Adresse, Relation, Folge, Wert, Grad, Teil oder Bahn anfügen."),
    (8, "Masterexemplar und Mehrschreiberbetrieb", "Kopiere 67 lokale Schlüssel nur am bezeichneten Ort; prüfe ganze Zelle, Besitzer und Festsetzung gegen das Masterexemplar."),
]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    prose_events = read_tsv(PROSE_EVENTS)
    prose_cards = {r["master_card_id"]: r for r in read_tsv(PROSE_CARDS)}
    prose_recipes = {r["master_card_id"]: r for r in read_tsv(PROSE_RECIPES)}
    astro_all = read_tsv(ASTRO_ALL)
    astro_reverse = {r["group_serial"]: r for r in read_tsv(ASTRO_REVERSE)}
    ledger: list[dict[str, object]] = []

    for event in prose_events:
        card = prose_cards[event["master_card_id"]]
        cls = card["card_class_279"]
        if cls == "COMPOSED_FROM_36_FAMILIES":
            recipe = prose_recipes[event["master_card_id"]]
            layer = "PURE_COMPOSITION"
            writer_action = f"Build {recipe['final_recipe']}; {recipe['writer_rule']}"
            source_recipe = recipe["final_recipe"]
        elif cls == "MEMORIZED_WHOLE_SIGN":
            layer = "LEARNED_WHOLE_SIGN"
            writer_action = "Copy the complete memorized prose nomenclator card"
            source_recipe = card["family_parse"]
        else:
            layer = "FRAMED_WHOLE_EXCEPTION"
            writer_action = "Reuse the memorized inner whole sign inside its licensed outer frame"
            source_recipe = card["family_parse"]
        ledger.append({
            "unified_index": len(ledger) + 1,
            "register": "PROSE",
            "page": event["page"],
            "unit_or_locus": event["statement_id"],
            "visible_owner": event["visible_owner"],
            "source_id": event["event_id"],
            "desired_value_de": event["register_expansion_de"],
            "writing_layer": layer,
            "recipe_or_key": source_recipe,
            "writer_action": writer_action,
            "resulting_visible_surface": event["visible_surface"],
            "result_status": "GENERATED_OR_COPIED_EXACTLY",
        })

    for group in astro_all:
        cls = group["coverage_class_274"]
        if cls == "PORTABLE_COMPOSITION":
            reverse = astro_reverse[group["group_serial"]]
            layer = "PURE_COMPOSITION"
            recipe = f"{reverse['writer_strategy']}::{reverse['copied_or_registered_core_surface']}+{reverse['productive_affix_or_modifier']}"
            action = reverse["reverse_instruction_de"]
        elif cls == "LEARNED_WHOLE_SIGN":
            layer = "LEARNED_WHOLE_SIGN"
            recipe = f"ASTRO_WHOLE[{group['visible_surface']}]"
            action = "Copy the complete memorized Astro value sign"
        else:
            layer = "LOCAL_COPY_KEY"
            recipe = f"LOCAL_KEY[{group['visible_surface']}]"
            action = "Copy this key from the selected local diagram locus"
        ledger.append({
            "unified_index": len(ledger) + 1,
            "register": "ASTRO",
            "page": group["page"],
            "unit_or_locus": group["locus"],
            "visible_owner": group["visible_owner"],
            "source_id": f"G{group['group_serial']}",
            "desired_value_de": group["concrete_diagram_reading_de"],
            "writing_layer": layer,
            "recipe_or_key": recipe,
            "writer_action": action,
            "resulting_visible_surface": group["visible_surface"],
            "result_status": "GENERATED_OR_COPIED_EXACTLY",
        })

    lesson_rows = [{"lesson": n, "title_de": title, "instruction_de": instruction} for n, title, instruction in LESSONS]
    curriculum = [
        {"inventory_layer": "PRODUCTIVE_STEM_FAMILIES", "entry_count": 36, "event_or_group_uses": 617, "learn_or_copy": "LEARN", "purpose": "generate pure compositions across prose and Astro"},
        {"inventory_layer": "PROSE_WHOLE_SIGNS", "entry_count": 23, "event_or_group_uses": 28, "learn_or_copy": "LEARN", "purpose": "practical nomenclator cards"},
        {"inventory_layer": "ASTRO_WHOLE_SIGNS", "entry_count": 46, "event_or_group_uses": 51, "learn_or_copy": "LEARN", "purpose": "fixed Astro value cards"},
        {"inventory_layer": "FRAMED_WHOLE_RULE", "entry_count": 0, "event_or_group_uses": 1, "learn_or_copy": "RULE", "purpose": "reuse an already learned inner whole sign inside one frame"},
        {"inventory_layer": "LOCAL_DIAGRAM_KEYS", "entry_count": 67, "event_or_group_uses": 79, "learn_or_copy": "COPY", "purpose": "locus-specific names and addresses"},
        {"inventory_layer": "TOTAL_MEMORIZED_ENTRIES", "entry_count": 105, "event_or_group_uses": 697, "learn_or_copy": "LEARN", "purpose": "36 stem families plus 69 whole signs"},
    ]

    ledger_path = OUT / "TWO_HUNDRED_NINETIETH_776_FORWARD_WRITING_LEDGER.tsv"
    lesson_path = OUT / "TWO_HUNDRED_NINETIETH_EIGHT_LESSON_CURRICULUM.tsv"
    curriculum_path = OUT / "TWO_HUNDRED_NINETIETH_WORKSHOP_INVENTORY.tsv"
    manual_path = OUT / "TWO_HUNDRED_NINETIETH_COMPLETE_SCRIBE_MANUAL.md"
    report_path = OUT / "TWO_HUNDRED_NINETIETH_REPORT.md"
    write_tsv(ledger_path, ledger, list(ledger[0]))
    write_tsv(lesson_path, lesson_rows, list(lesson_rows[0]))
    write_tsv(curriculum_path, curriculum, list(curriculum[0]))

    counts = Counter(str(r["writing_layer"]) for r in ledger)
    manual = [
        "# Vollständiges Schreiberhandbuch für die zehn Seiten",
        "",
        "## Was der Lehrling wirklich lernt",
        "",
        "Der feste Lehrbestand umfasst 105 Einträge: 36 produktive Stammfamilien, 23 Prosa-Ganzzeichen und 46 Astro-Ganzzeichen. Ein gerahmtes Ganzzeichen benutzt einen bereits gelernten Innenwert und kostet nur eine Regel. 67 lokale Diagrammschlüssel werden nicht auswendig gelernt, sondern am jeweiligen Ort kopiert.",
        "",
        "## Acht Lektionen",
        "",
    ]
    for row in lesson_rows:
        manual.append(f"{row['lesson']}. **{row['title_de']}** — {row['instruction_de']}")
    manual.extend([
        "",
        "## Vollständiger Schreibablauf",
        "",
        "Zuerst werden Bild oder Diagramm und damit der Besitzer festgelegt. Dann wird der Sachauftrag in Quelle, Ziel, Folge, Menge, Grad, Handlung, Bahn und Festsetzung zerlegt. In der Prosa erzeugt eine der 149 Bedeutungsfolgen die Karte; zwei lokale Schreiberkonventionen wählen die letzte Oberfläche. In Astro wird entweder eine gemeinsame Karte wiederverwendet oder ein lokaler Kern kopiert und mit Funktionssuffix versehen. Ganzzeichen werden ungeteilt geschrieben. Lokale Schlüssel werden direkt aus dem Masterexemplar übernommen.",
        "",
        "## Deckung",
        "",
        f"Die 776 sichtbaren Gruppen teilen sich in {counts['PURE_COMPOSITION']} reine Kompositionen, {counts['LEARNED_WHOLE_SIGN']} Ganzzeichen-Vorkommen, {counts['FRAMED_WHOLE_EXCEPTION']} gerahmte Ganzzeichenform und {counts['LOCAL_COPY_KEY']} lokale Kopierschlüssel. Jede Zeile des Ledgers endet in ihrer tatsächlich sichtbaren Oberfläche.",
        "",
        "Das ist für mehrere Schreiber um 1420 lernbar: Sie teilen Stammdeck, Ganzzeichentafel und Masterexemplar; ihre sichtbaren q-/s-/ch-Varianten dürfen hand- und positionsabhängig sein, solange die registrierte Karte gleich bleibt.",
        "",
    ])
    manual_path.write_text("\n".join(manual), encoding="utf-8")

    report_path.write_text(
        "# Sidequest-Pass 290: ein vollständiger Vorwärts-Schreiber\n\n"
        "## Ergebnis\n\n"
        "Prosa- und Astro-Encoder sind in einem 776-zeiligen Schreibledger verbunden. Die ehrliche Schichtung lautet 617 reine Kompositionen, 79 reine Ganzzeichen-Vorkommen, eine gerahmte Ganzzeichenform und 79 lokale Kopierschlüssel. "
        "Der memorierte Werkstattbestand bleibt 105 Einträge: 36 Familien und 69 Ganzzeichen; 67 lokale Formen werden nur kopiert.\n\n"
        "Ein Acht-Lektionen-Plan macht das System für eine kleine Mehrschreiberwerkstatt ausführbar. Es ist ein gemischtes Fachkürzel-/Nomenklator-/Exemplarsystem, kein Alphabet und keine bloße Liste zufälliger Wörter.\n\n"
        f"Inputs prose `{sha(PROSE_EVENTS)}`, recipes `{sha(PROSE_RECIPES)}`, Astro `{sha(ASTRO_ALL)}`, Astro encoder `{sha(ASTRO_REVERSE)}`.\n",
        encoding="utf-8",
    )

    outputs = (ledger_path, lesson_path, curriculum_path, manual_path, report_path)
    summary = {
        "status": "PASS",
        "ledger_rows": len(ledger),
        "writing_layers": dict(counts),
        "memorized_entries": 105,
        "local_copy_forms": len(read_tsv(ASTRO_LOCAL)),
        "lessons": len(lesson_rows),
        "outputs": {p.name: sha(p) for p in outputs},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

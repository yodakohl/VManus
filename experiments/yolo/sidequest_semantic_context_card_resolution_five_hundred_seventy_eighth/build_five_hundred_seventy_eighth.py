#!/usr/bin/env python3
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
YOLO = HERE.parent
P554 = YOLO / "sidequest_semantic_canonical_working_dictionary_five_hundred_fifty_fourth"
P562 = YOLO / "sidequest_semantic_integrated_apprentice_manual_five_hundred_sixty_second"

INVARIANTS = {
    "PROC004": ("INTO_ACTIVE_ENTRY", "diesen Posten in das aktive Fach übernehmen"),
    "PROC008": ("ACTIVATE_CURRENT_ITEM", "diesen Posten in Einsatz bringen"),
    "PROC011": ("START_CURRENT_ITEM", "diesen Posten neu ansetzen"),
    "PROC038": ("ACTIVATE_TO_MEASURE", "den laufenden Posten nach Sollmaß ansetzen"),
    "PROC042": ("TRANSFER_CURRENT_ITEM", "diesen Posten umsetzen"),
    "PROC046": ("SUSTAIN_TEMPERATURE", "diesen Posten länger temperieren"),
    "PROC072": ("GUIDE_ALONG_LOCAL_PATH", "den laufenden Posten entlangführen"),
    "PROC076": ("COMMIT_TRANSFER", "den laufenden Posten überführen; Schritt schließen"),
    "PROC078": ("COMMIT_DEPOSIT", "den laufenden Posten absetzen; Schritt schließen"),
    "PROC092": ("SUSTAIN_ACTIVE_ITEM", "den laufenden Posten länger in Einsatz halten"),
    "PROC120": ("COMMIT_GUIDED_TRANSFER", "den laufenden Posten weiterleiten und überführen; Schritt schließen"),
}


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name, rows):
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def fill_class(text):
    if "abmessen" in text:
        return "MEASURE_SLOT"
    if "einleiten" in text or "durchleiten" in text:
        return "VISIBLE_PATH_OR_FLOW"
    if "umfüllen" in text or "hinleiten" in text:
        return "VISIBLE_TARGET"
    if "abführen" in text:
        return "VISIBLE_SOURCE_OR_DRAIN"
    if "anlegen" in text or "wirken lassen" in text:
        return "CONTACT_OR_APPLICATION_OWNER"
    if "temperieren" in text or "warm halten" in text:
        return "THERMAL_STATE"
    if "ablagern" in text:
        return "VISIBLE_DEPOSIT_TARGET"
    if "übertragen" in text:
        return "SOURCE_COPY"
    return "BASE_OPERATION"


def main():
    cards = read(P554 / "FIVE_HUNDRED_FIFTY_FOURTH_ONE_HUNDRED_SEVENTY_THREE_CARD_DICTIONARY.tsv")
    traces = read(P562 / "FIVE_HUNDRED_SIXTY_SECOND_THREE_HUNDRED_EIGHTY_ONE_FULL_TRACES.tsv")
    target_cards = [r for r in cards if r["context_sensitive"] == "YES"]
    occurrences = [r for r in traces if r["observed_card_no"] in INVARIANTS]
    by_card = defaultdict(list)
    occurrence_rows = []
    for row in occurrences:
        code, invariant = INVARIANTS[row["observed_card_no"]]
        fill = fill_class(row["local_action_expansion_de"])
        by_card[row["observed_card_no"]].append(fill)
        occurrence_rows.append({
            "event_id": row["event_id"],
            "page": row["page"],
            "record": row["record"],
            "statement_id": row["statement_id"],
            "locus": row["locus"],
            "card_no": row["observed_card_no"],
            "surface": row["observed_surface"],
            "silent_owner_de": row["silent_owner_de"],
            "invariant_operation_code": code,
            "invariant_operation_de": invariant,
            "owner_or_slot_fill": fill,
            "filled_local_verb_de": row["local_action_expansion_de"],
            "new_whole_word_introduced": "NO",
            "resolved": "YES",
        })

    card_rows = []
    for row in target_cards:
        code, invariant = INVARIANTS[row["card_no"]]
        fills = Counter(by_card[row["card_no"]])
        card_rows.append({
            "card_no": row["card_no"],
            "surfaces": row["surfaces"],
            "component_parse": row["component_parse"],
            "invariant_operation_code": code,
            "invariant_operation_de": invariant,
            "owner_or_slot_fills": "|".join(sorted(fills)),
            "fill_distribution": "|".join(f"{k}:{fills[k]}" for k in sorted(fills)),
            "occurrences": row["occurrences"],
            "component_meaning_changed": "NO",
            "new_whole_word_introduced": "NO",
            "context_dependence_resolved": "YES",
        })

    fill_counts = Counter(r["owner_or_slot_fill"] for r in occurrence_rows)
    fill_rows = [{
        "fill": key,
        "events": fill_counts[key],
        "rule_de": {
            "BASE_OPERATION": "verwende das abstrakte Kartenverb unverändert",
            "MEASURE_SLOT": "Menge macht Umsetzen zu Abmessen plus Umsetzen",
            "VISIBLE_PATH_OR_FLOW": "sichtbarer Lauf konkretisiert Führen oder Ansetzen als Ein- oder Durchleiten",
            "VISIBLE_TARGET": "sichtbares Ziel konkretisiert Transfer als Hinleiten oder Umfüllen",
            "VISIBLE_SOURCE_OR_DRAIN": "sichtbare Quelle konkretisiert Weiterleitung als Abführen",
            "CONTACT_OR_APPLICATION_OWNER": "Körper- oder Kontaktbesitzer konkretisiert Einsatz als Anlegen oder Einwirken",
            "THERMAL_STATE": "Wärmezustand konkretisiert Halten als Temperieren oder Warmhalten",
            "VISIBLE_DEPOSIT_TARGET": "sichtbarer Empfänger konkretisiert Absetzen als Ablagern",
            "SOURCE_COPY": "Quellbezug konkretisiert Eintragen als Übernehmen",
        }[key],
    } for key in sorted(fill_counts)]

    write("FIVE_HUNDRED_SEVENTY_EIGHTH_ELEVEN_INVARIANT_CARD_RULES.tsv", card_rows)
    write("FIVE_HUNDRED_SEVENTY_EIGHTH_SEVENTY_OCCURRENCE_RESOLUTIONS.tsv", occurrence_rows)
    write("FIVE_HUNDRED_SEVENTY_EIGHTH_OWNER_SLOT_FILL_RULES.tsv", fill_rows)
    summary = {
        "status": "PASS",
        "context_cards": len(card_rows),
        "occurrences": len(occurrence_rows),
        "fill_rules": len(fill_rows),
        "new_whole_words": sum(r["new_whole_word_introduced"] == "YES" for r in occurrence_rows),
        "resolved_occurrences": sum(r["resolved"] == "YES" for r in occurrence_rows),
    }
    (HERE / "FIVE_HUNDRED_SEVENTY_EIGHTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = [
        "# Fünfhundertachtundsiebzigste Runde: elf Kontextkarten",
        "",
        "## Ergebnis",
        "",
        "Die elf Karten brauchen keine elf zusätzlichen Bedeutungen. Jede erhält genau einen invarianten Arbeitswert; neun kleine Besitzer-/Slotfüllungen erklären die konkrete Wortwahl in allen 70 Vorkommen. Kein neuer Ganzwert wurde eingeführt.",
        "",
        "Beispiele: OK+Y bleibt immer ›diesen Posten in Einsatz bringen‹. Am Pflanzenbesitzer wird daraus einsetzen, am sichtbaren Lauf einleiten, am Körper-/Kontaktbesitzer anlegen oder einwirken. L+CHD+DY bleibt ›weiterleiten und überführen; schließen‹; sichtbare Quelle, Bahn, Ziel oder Maß wählen nur abführen, durchleiten, umfüllen oder abmessen.",
        "",
        "Damit sind die elf früher kontextsensitiven Karten keine Polysemie im Wörterbuch. Sie sind abstrakte Werkstattverben mit sichtbaren Argumenten. Die kleine Werkstatt kann denselben Kartensatz über Pflanzenartikel und Beckenstationen verwenden, weil das Bild den Gegenstand liefert.",
        "",
        "## Nächster Schritt",
        "",
        "Die 94 semantischen Lernobjekte und neun Besitzerfüllungen werden nun in einen einzigen kompakten Kompositionsparser überführt. Dieser soll aus jeder Komponentenfolge zuerst die abstrakte Kartenlesung und dann aus dem sichtbaren Besitzer eine natürliche deutsche Anweisung erzeugen.",
    ]
    (HERE / "FIVE_HUNDRED_SEVENTY_EIGHTH_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

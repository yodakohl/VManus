#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P361 = ROOT / "experiments/yolo/sidequest_semantic_controlled_reverse_language_three_hundred_sixty_first"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


FAMILIES = {
    "B01": ("MATERIAL", "Material", "Stoff|Teil|Zutat", "niemals Pflanzenart oder Heilwirkung"),
    "B02": ("SOURCE", "Quelle", "Quelle|Vorrat|daraus", "niemals konkrete Herkunft erfinden"),
    "B03": ("PREPARATION", "Ansatz", "Ansatz|Zubereitung|Vorbereitung", "nicht mit fertigem Produkt gleichsetzen"),
    "B04": ("CONTINUE", "Fortsetzung", "weiter|danach|fortsetzen", "keine neue Operation hinzudichten"),
    "B05": ("CURRENT", "Diesposten", "dies|es|laufender Posten", "nur recordlokaler Referent"),
    "B06": ("VESSEL", "Gefäß", "Gefäß|Behälter", "keine Gefäßart ohne Bild"),
    "B07": ("BIND_THREAD", "Bindefortsetzung", "weiter binden|Bindegang", "nicht automatisch Körperverband"),
    "M01": ("MEASURE", "Sollmaß", "Maß|Vorgabe|Sollwert", "keine moderne Einheit einsetzen"),
    "M02": ("PORTION", "Portion", "Teil|Portion|Menge", "nicht mit Materialart gleichsetzen"),
    "M03": ("ADDITION", "Zugabe", "zugeben|Zusatz|Einlage", "Zusatzstoff bleibt lokal"),
    "M04": ("STAGE", "Arbeitsstufe", "Stufe|Stand|Einstellung", "keine absolute Zeitstufe behaupten"),
    "M05": ("DIVIDE", "Teilen", "teilen|zerkleinern", "keine Werkzeugart erfinden"),
    "T01": ("TRANSFER", "Transfer", "führen|überführen|umsetzen", "Richtung nur aus Quelle und Ziel"),
    "T02": ("SUPPLY", "Zuführung", "zuführen|zugießen|eingeben", "Medium nicht ohne Stoffkarte benennen"),
    "T03": ("DRAIN", "Abführung", "abführen|abziehen|ablassen", "kein sichtbares Rohr voraussetzen"),
    "T04": ("PASSAGE", "Durchgang", "durchführen|durchleiten|Passage", "Durchlass ist nicht automatisch Filter"),
    "T05": ("SETTLE", "Absetzen", "absetzen|stehen lassen|ruhen", "Dauer nur mit Gradkarte"),
    "T06": ("COLLECT", "Sammeln", "auffangen|sammeln|zurücknehmen", "Gefäßart bleibt bildabhängig"),
    "T07": ("CLARIFY", "Klären", "seihen|klären|Klarauszug", "nicht zwingend sichtbares Tuch"),
    "T08": ("PRESS", "Auswringen", "pressen|auswringen", "Werkzeug nicht ergänzen"),
    "T09": ("WASH", "Waschgang", "waschen|spülen", "Körper oder Anlage kommt vom Besitzer"),
    "D01": ("SHORT_PROCESS", "Kurzprozess", "kurz|direkt|einmal", "keine genaue Zeitdauer"),
    "D02": ("LONG_HOLD", "Langhalten", "länger|anhalten|halten", "keine genaue Zeitdauer"),
    "D03": ("LONG_CONTACT", "Langkontakt", "länger anlegen|einwirken", "Anwendungsobjekt bleibt lokal"),
    "D04": ("HEAT", "Wärmen", "wärmen|warm halten", "keine Temperaturzahl"),
    "Z01": ("PLACE", "Zielstelle", "an|zur Stelle|zum Ziel", "Zielreferent nicht erraten"),
    "Z02": ("SET", "Einsetzen", "einsetzen|ansetzen|eingeben", "keinen Stoff hinzuerfinden"),
    "Z03": ("USE", "Gebrauchen", "gebrauchen|anwenden", "keine medizinische Indikation"),
    "Z04": ("BIND", "Binden", "binden|befestigen", "Körperverband nur bei sichtbarem Besitzer"),
    "A01": ("READY", "Bereit", "bereit|fertig|einsatzbereit", "kein Qualitätsurteil darüber hinaus"),
    "A02": ("FASTEN", "Festmachen", "befestigen|binden|festsetzen", "Ziel bleibt lokal"),
    "A03": ("STORE", "Verwahren", "verwahren|beiseitestellen", "keine Lagerdauer"),
    "A04": ("REMAINDER", "Rest", "Rest|Endposten|Rückstand", "nicht automatisch Abfall"),
}


def family(slot: str, value: str) -> str:
    low = value.lower()
    if slot == "S1_BEZUG_FOLGE":
        if value == "Gefäß": return "B06"
        if value == "Diesposten": return "B05"
        if "bind" in low: return "B07"
        if "quelle" in low or "quell" in low: return "B02"
        if any(x in low for x in ("ansatz", "vorbereitung", "zubereitung")): return "B03"
        if any(x in low for x in ("blüten", "wurzel", "pflanze", "zutat")): return "B01"
        return "B04"
    if slot == "S2_MATERIAL_MASS":
        if any(x in low for x in ("maß", "sollstellung")): return "M01"
        if any(x in low for x in ("zugabe", "zusatz", "einlage")): return "M03"
        if "stufe" in low: return "M04"
        if value in {"teilen", "Zerkleinern"}: return "M05"
        return "M02"
    if slot == "S3_PROZESS_TRANSFER":
        if "auswring" in low: return "T08"
        if any(x in low for x in ("klar", "seih", "trenn")): return "T07"
        if any(x in low for x in ("wasser", "wasch")): return "T09"
        if any(x in low for x in ("absetz", "standzeit")): return "T05"
        if any(x in low for x in ("samml", "auffang", "rücknahme")): return "T06"
        if any(x in low for x in ("zuführ", "ausguss")): return "T02"
        if any(x in low for x in ("abführ", "abzug", "abzieh")): return "T03"
        if any(x in low for x in ("passage", "durchgang", "durchlass", "durchleit", "auslass", "beckenlauf")): return "T04"
        return "T01"
    if slot == "S4_DAUER_ZUSTAND":
        if "wärm" in low: return "D04"
        if "kontakt" in low: return "D03"
        if "lang" in low or "halt" in low: return "D02"
        return "D01"
    if slot == "S5_ZIEL_ANWENDUNG":
        if "gebrauch" in low: return "Z03"
        if "bind" in low: return "Z04"
        if any(x in low for x in ("stelle", "ziel", "marke")): return "Z01"
        return "Z02"
    if slot == "S6_BEREIT_ABSCHLUSS":
        if value == "Verwahren": return "A03"
        if any(x in low for x in ("befest", "binde")): return "A02"
        if "bereit" in low: return "A01"
        return "A04"
    raise ValueError((slot, value))


def main() -> None:
    phrases = read_tsv(P361 / "THREE_HUNDRED_SIXTY_FIRST_159_CONTROLLED_PHRASES.tsv")
    cards = read_tsv(P361 / "THREE_HUNDRED_SIXTY_FIRST_380_CONTROLLED_SOURCE_CARDS.tsv")
    statements = read_tsv(P361 / "THREE_HUNDRED_SIXTY_FIRST_116_REVERSE_PARSED_STATEMENTS.tsv")
    phrase_by_controlled = {row["controlled_phrase"]: row for row in phrases}

    phrase_rows = []
    family_members: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in phrases:
        fid = family(row["slot_code"], row["atomic_value_de"])
        family_members[fid].append(row)
        phrase_rows.append({
            "family_id": fid,
            "family_head_de": FAMILIES[fid][1],
            "controlled_phrase": row["controlled_phrase"],
            "atomic_value_de": row["atomic_value_de"],
            "slot_code": row["slot_code"],
            "event_count": row["event_count"],
            "card_types": row["card_types"],
            "joint_tuple_ids": row["joint_tuple_ids"],
            "allowed_free_synonyms_de": FAMILIES[fid][2],
            "drift_boundary_de": FAMILIES[fid][3],
            "fixed_reverse_formula": f"{fid}::{row['controlled_phrase']}",
        })
    phrase_rows.sort(key=lambda row: (row["family_id"], row["controlled_phrase"]))

    family_rows = []
    for fid in sorted(family_members):
        members = family_members[fid]
        slot_counts = Counter(row["slot_code"] for row in members)
        family_rows.append({
            "family_id": fid,
            "family_code": FAMILIES[fid][0],
            "family_head_de": FAMILIES[fid][1],
            "allowed_free_synonyms_de": FAMILIES[fid][2],
            "drift_boundary_de": FAMILIES[fid][3],
            "controlled_phrases": len(members),
            "source_events": sum(int(row["event_count"]) for row in members),
            "slot_codes": "|".join(sorted(slot_counts)),
            "member_values_de": "|".join(sorted(row["atomic_value_de"] for row in members)),
        })

    card_rows = []
    card_lookup = {}
    for row in cards:
        phrase = phrase_by_controlled[row["controlled_phrase"]]
        fid = family(phrase["slot_code"], phrase["atomic_value_de"])
        out = {
            "source_position_id": row["source_position_id"],
            "event_id": row["event_id"],
            "record_unit_id": row["record_unit_id"],
            "statement_id": row["statement_id"],
            "surface": row["surface"],
            "joint_tuple_id": row["joint_tuple_id"],
            "family_id": fid,
            "family_head_de": FAMILIES[fid][1],
            "controlled_phrase": row["controlled_phrase"],
            "fixed_reverse_formula": f"{fid}::{row['controlled_phrase']}",
            "exact_card_value_de": row["atomic_value_de"],
        }
        card_rows.append(out)
        card_lookup[row["event_id"]] = out

    statement_rows = []
    for row in statements:
        ids = row["source_event_ids"].split("|")
        selected = [card_lookup[event_id] for event_id in ids]
        statement_rows.append({
            "statement_id": row["statement_id"],
            "record_unit_id": row["record_unit_id"],
            "free_fluent_german": row["free_fluent_german"],
            "family_chain": " → ".join(item["family_id"] for item in selected),
            "family_heads_de": " → ".join(item["family_head_de"] for item in selected),
            "fixed_formula_chain": " · ".join(item["fixed_reverse_formula"] for item in selected),
            "recovered_values_de": " → ".join(item["exact_card_value_de"] for item in selected),
            "source_event_ids": "|".join(ids),
            "reverse_status": "EXACT",
        })

    write_tsv(HERE / "THREE_HUNDRED_SIXTY_SECOND_33_FAMILY_THESAURUS.tsv", family_rows, list(family_rows[0]))
    write_tsv(HERE / "THREE_HUNDRED_SIXTY_SECOND_159_PHRASE_INDEX.tsv", phrase_rows, list(phrase_rows[0]))
    write_tsv(HERE / "THREE_HUNDRED_SIXTY_SECOND_380_FAMILY_TAGGED_CARDS.tsv", card_rows, list(card_rows[0]))
    write_tsv(HERE / "THREE_HUNDRED_SIXTY_SECOND_116_FAMILY_PARSES.tsv", statement_rows, list(statement_rows[0]))

    lessons = defaultdict(list)
    for row in family_rows:
        lesson = row["family_id"][0]
        lessons[lesson].append(row)
    manual = ["# Pass 362 — Werkstatt-Thesaurus", ""]
    for lesson, title in (("B", "Bezug"), ("M", "Maß und Material"), ("T", "Transfer"), ("D", "Dauer und Zustand"), ("Z", "Ziel und Anwendung"), ("A", "Abschluss")):
        manual += [f"## {title}", ""]
        for row in lessons[lesson]:
            manual.append(f"- `{row['family_id']}` **{row['family_head_de']}**: {row['allowed_free_synonyms_de']}. Grenze: {row['drift_boundary_de']}. ({row['controlled_phrases']} Phrasen/{row['source_events']} Karten)")
        manual.append("")
    manual += [
        "## Lehrregel",
        "",
        "Im freien Deutsch darf der Schreiber ein Synonym aus der Familie benutzen. Auf der Korrekturtafel steht jedoch immer die vollständige Formel `FAMILIE::SLOT[Wert]`. Nur diese Formel wählt die konkrete Kartenbedeutung; der Familienkopf allein reicht nie.",
        "",
        "Beispiel: `T03::TRANSFER[Abführung]` darf frei als *abführen*, *abziehen* oder *ablassen* gelesen werden. `T03` allein darf weder eine Richtung noch ein Medium erfinden.",
    ]
    (HERE / "THREE_HUNDRED_SIXTY_SECOND_WORKSHOP_THESAURUS.md").write_text("\n".join(manual) + "\n", encoding="utf-8")

    report = f"""# Pass 362 — kompakter Werkstatt-Thesaurus

Die 159 exakten Kontrollphrasen fallen in {len(family_rows)} lehrbare Familien.
Der Thesaurus gestattet natürliche Synonyme, hält aber unter jeder freien
Formulierung genau eine Formel `FAMILIE::SLOT[Wert]`. So bleiben alle 380
Quellkarten und 116 Aussagen exakt rücklesbar.

Die Familien sind keine neuen Voynich-Wörter. Sie sind das kleine deutsche
Lehrgerüst, mit dem ein Meister Varianten wie *abführen*, *abziehen* und
*ablassen* zusammen erklären kann, ohne die Karten selbst zu verwechseln. Jede
Familie besitzt deshalb auch eine ausdrückliche Driftgrenze.

Als nächster Schritt eignet sich ein Blinddiktat im handwerklichen Sinn: Der
Meister spricht nur freie Familienphrasen; der Lehrling muss die vollständige
kontrollierte Formel auswählen und daraus die Karte setzen. Fehler zeigen dann,
welche Familien noch zu breit sind.
"""
    (HERE / "THREE_HUNDRED_SIXTY_SECOND_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "families": len(family_rows),
        "controlled_phrases": len(phrase_rows),
        "source_cards": len(card_rows),
        "statements": len(statement_rows),
        "family_event_distribution": {row["family_id"]: int(row["source_events"]) for row in family_rows},
    }
    (HERE / "THREE_HUNDRED_SIXTY_SECOND_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

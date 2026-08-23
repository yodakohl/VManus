#!/usr/bin/env python3
"""Build the practical exact-form selector for the sixteen-headword codebook."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
APPRENTICE = HERE.parent / "sidequest_semantic_apprentice_codebook"
COMPACT = HERE.parent / "sidequest_semantic_nomenclator_family_completion"

CARDS_IN = APPRENTICE / "WHOLE_CARD_22_CODEBOOK.tsv"
HEADS_IN = APPRENTICE / "WHOLE_HEADWORD_16.tsv"
COPYBOOK_IN = APPRENTICE / "COPYBOOK_116_STATEMENTS.tsv"
EVENTS_IN = COMPACT / "COMPACT_381_EVENT_INTERLINEAR.tsv"

RULES_OUT = HERE / "WHOLE_16_VARIANT_RULES.tsv"
OCCURRENCES_OUT = HERE / "WHOLE_28_VARIANT_OCCURRENCES.tsv"
ENCODER_OUT = HERE / "ENCODER_116_STATEMENTS.tsv"
DRILLS_OUT = HERE / "VARIANT_7_DRILLS.tsv"
MANUAL_OUT = HERE / "VARIANT_SELECTOR_LEAF.md"
SUMMARY_OUT = HERE / "BUILD_SUMMARY.json"


# Nine headwords have one visible exact family, five select a semantic subtype,
# and two keep one exact tuple but copy a local surface allograph.
HEAD_RULES = {
    "W01_ZUSATZ": ("ONLY_FORM", "Schreibe die einzige Karte dl.", "dl = allgemeiner Zusatz"),
    "W02_GEFAESS": ("SEMANTIC_VARIANT_MENU", "Welche Gefaessaufgabe hat der Posten?", "os = Mischgefaess; oykchor = Zubereitungsgefaess; ly = Auffang-/Haltegefaess"),
    "W03_KUEHLEN": ("SEMANTIC_VARIANT_MENU", "Wird ein Fertigprodukt oder eine Portion gekuehlt?", "tchody = Fertigprodukt kaltstellen; ody = Portion abkuehlen"),
    "W04_ROH": ("ONLY_FORM", "Schreibe die einzige Karte qekey.", "qekey = roher Posten"),
    "W05_TUCH": ("ONLY_FORM", "Schreibe die einzige Karte dain.", "dain = Arbeitstuch"),
    "W06_SCHWENKEN": ("ONLY_FORM", "Schreibe die einzige Karte sshkchdy.", "sshkchdy = einmal schwenken und schliessen"),
    "W07_PFLANZENTEIL": ("SEMANTIC_VARIANT_MENU", "Welchen Teil zeigt der Bildbesitzer?", "dchey = Wurzel; sh = Staengel"),
    "W08_WASCHEN": ("SEMANTIC_VARIANT_MENU", "Ist dies der ganze Waschgang oder ein Nachwaschen?", "rshedy = Waschgang; lkedy = nachwaschen"),
    "W09_AUFTRAGEN": ("ONLY_FORM", "Schreibe die einzige Karte cheeckhody.", "cheeckhody = auftragen und schliessen"),
    "W10_FUELLEN": ("ONLY_FORM", "Schreibe die einzige Karte ytey.", "ytey = Empfaenger fuellen"),
    "W11_KLARLAUF": ("RENDERER_ALLOGRAPH", "Bedeutung gleich lassen und die lokale Handform kopieren.", "cheey und shey = dieselbe exakte Klarlaufkarte"),
    "W12_TRENNEN": ("SEMANTIC_VARIANT_MENU", "Liegt die grobe oder die feine Trennstufe vor?", "cfhy = auswringen; cphy = nachseihen"),
    "W13_FRISCHWASSER": ("ONLY_FORM", "Schreibe die einzige Karte dshedy.", "dshedy = Frischwasser zugeben und schliessen"),
    "W14_VORIGES": ("RENDERER_ALLOGRAPH", "Bedeutung gleich lassen und die lokale Handform kopieren.", "dchol und schol = dieselbe exakte Voriges-Karte"),
    "W15_TEILEN": ("ONLY_FORM", "Schreibe die einzige Karte ches.", "ches = aktuellen Posten teilen"),
    "W16_BEFESTIGEN": ("ONLY_FORM", "Schreibe die einzige Karte qokylddy.", "qokylddy = befestigen und schliessen"),
}


# surface family -> semantic subtype, exact-form selection rule
CARD_VARIANTS = {
    "dl": ("ALLGEMEINER_ZUSATZ", "Bei einem unbenannten Zusatz zum laufenden Ansatz dl nehmen."),
    "os": ("MISCHGEFAESS", "Fuer frischen Pflanzenstoff mit folgendem Fluessigkeitszulauf os nehmen."),
    "oykchor": ("ZUBEREITUNGSGEFAESS", "Fuer einen fortgefuehrten Folgeansatz vor weiterer Bearbeitung oykchor nehmen."),
    "ly": ("AUFFANG_ODER_HALTEGEFAESS", "Fuer eine Bio-Station, in der der Posten ruht oder gesammelt wird, ly nehmen."),
    "tchody": ("FERTIGPRODUKT_KALTSTELLEN", "Nach dem Klarlauf das fertige Produkt mit tchody kaltstellen."),
    "ody": ("PORTION_ABKUEHLEN", "Eine bereits abgemessene Postenportion mit ody abkuehlen."),
    "qekey": ("ROHER_AUSGANGSPOSTEN", "Fuer den unbehandelten Ausgangsposten qekey nehmen."),
    "dain": ("ARBEITSTUCH", "Fuer das eingelegte Arbeitstuch dain nehmen."),
    "sshkchdy": ("EINMAL_SCHWENKEN", "Fuer einen einzelnen abgeschlossenen Schwenkgang sshkchdy nehmen."),
    "dchey": ("WURZEL", "Wenn der Bildbesitzer die Wurzel vorgibt, dchey nehmen."),
    "sh": ("STAENGEL", "Wenn der Bildbesitzer den Staengel vorgibt, sh nehmen."),
    "rshedy": ("VOLLSTAENDIGER_WASCHGANG", "Fuer eine eigenstaendige geschlossene Waschzelle rshedy nehmen."),
    "lkedy": ("NACHWASCHEN", "Nach vorausgehenden Bearbeitungsschritten fuer den letzten Waschgang lkedy nehmen."),
    "cheeckhody": ("AUFTRAGEN", "Fuer den abgeschlossenen Auftrag des bereiteten Postens cheeckhody nehmen."),
    "ytey": ("EMPFANGER_FUELLEN", "Fuer das Fuellen des sichtbaren Empfaengers ytey nehmen."),
    "cheey|shey": ("KLARLAUF", "Die exakte Karte bleibt gleich; cheey oder shey aus der lokalen Handvorlage kopieren."),
    "cfhy": ("GROB_TRENNEN_ODER_AUSWRINGEN", "Vor der Standzeit die grobe Trennung mit cfhy schreiben."),
    "cphy": ("FEIN_TRENNEN_ODER_NACHSEIHEN", "Nach der Standzeit vor dem Klarlauf die feine Trennung mit cphy schreiben."),
    "dshedy": ("FRISCHWASSER_ZUGEBEN", "Fuer Frischwasserzugabe mit Zellschluss dshedy nehmen."),
    "dchol|schol": ("VORIGEN_POSTEN_AUFNEHMEN", "Die exakte Karte bleibt gleich; dchol oder schol aus der lokalen Handvorlage kopieren."),
    "ches": ("AKTUELLEN_POSTEN_TEILEN", "Fuer die Teilung des laufenden Postens ches nehmen."),
    "qokylddy": ("POSTEN_BEFESTIGEN", "Fuer Befestigen mit Zellschluss qokylddy nehmen."),
}


EVENT_CUES = {
    "E001": "Die Pflanzenzeichnung liefert WURZEL; daher dchey.",
    "E005": "Der frische Wurzelposten erhaelt danach Wasser; daher Mischgefaess os.",
    "E032": "Ein fortgefuehrter Folgeansatz geht in weitere Bearbeitung; daher Zubereitungsgefaess oykchor.",
    "E041": "Erste grobe Trennung vor der Standzeit; daher cfhy.",
    "E043": "Zweite feine Trennung nach der Standzeit und vor Klarlauf; daher cphy.",
    "E044": "Klarlaufkopf; auf H3 wird die lokale Form shey kopiert.",
    "E045": "Der eben gewonnene Klarlauf ist Fertigprodukt; daher tchody.",
    "E047": "Voriges-Kopf; auf H3 wird die lokale Form dchol kopiert.",
    "E060": "Eine abgemessene Portion wird abgekuehlt; daher ody.",
    "E083": "Voriges-Kopf; auf H5 wird die lokale Form schol kopiert.",
    "E086": "Bereiteten Posten auftragen und Zelle schliessen; daher cheeckhody.",
    "E087": "Die Pflanzenzeichnung liefert STAENGEL; daher sh.",
    "E112": "Unbenannter Zusatz zum laufenden Ansatz; daher dl.",
    "E122": "Ein einzelner geschlossener Schwenkgang; daher sshkchdy.",
    "E129": "Unbenannter Zusatz zum laufenden Ansatz; daher dl.",
    "E150": "Der sichtbare Empfaenger wird gefuellt; daher ytey.",
    "E159": "Bio-Empfangsstation zum Ruhen und Sammeln; daher ly.",
    "E189": "Frischwasserzugabe als eigene Schlusszelle; daher dshedy.",
    "E197": "Klarlaufkopf; in B2 wird die lokale Form cheey kopiert.",
    "E203": "Klarlaufkopf; in B2 wird die lokale Form cheey kopiert.",
    "E216": "Der laufende Posten wird geteilt; daher ches.",
    "E225": "Eigenstaendige vollstaendige Waschzelle; daher rshedy.",
    "E326": "Posten befestigen und Zelle schliessen; daher qokylddy.",
    "E327": "Arbeitstuch in die laufende Station einlegen; daher dain.",
    "E344": "Waschen nach mehreren vorausgehenden Arbeitsschritten; daher lkedy.",
    "E353": "Klarlaufkopf; in B4 wird die lokale Form shey kopiert.",
    "E374": "Der Ausgangsposten wird ausdruecklich roh gefuehrt; daher qekey.",
    "E379": "Arbeitstuch in die laufende Station einlegen; daher dain.",
}


DRILL_HEADS = [
    "W02_GEFAESS",
    "W03_KUEHLEN",
    "W07_PFLANZENTEIL",
    "W08_WASCHEN",
    "W12_TRENNEN",
    "W11_KLARLAUF",
    "W14_VORIGES",
]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        raise ValueError(f"empty output: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict[str, object]:
    cards = read_tsv(CARDS_IN)
    heads = read_tsv(HEADS_IN)
    copybook = read_tsv(COPYBOOK_IN)
    events = read_tsv(EVENTS_IN)
    assert (len(cards), len(heads), len(copybook), len(events)) == (22, 16, 116, 381)
    assert set(HEAD_RULES) == {row["headword_id"] for row in heads}
    assert set(CARD_VARIANTS) == {row["surface_family"] for row in cards}

    cards_by_id = {row["joint_tuple_id"]: row for row in cards}
    whole_events = [row for row in events if row["joint_tuple_id"] in cards_by_id]
    whole_events.sort(key=lambda row: int(row["event_serial"]))
    assert len(whole_events) == 28
    assert set(EVENT_CUES) == {row["event_id"] for row in whole_events}

    events_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        events_by_statement[event["statement_id"]].append(event)
    copy_by_statement = {row["statement_id"]: row for row in copybook}

    head_rows: list[dict[str, str]] = []
    for head in heads:
        mode, question, choice_map = HEAD_RULES[head["headword_id"]]
        head_rows.append({
            "headword_id": head["headword_id"],
            "headword_de": head["headword_de"],
            "selection_mode": mode,
            "exact_card_types": head["exact_card_types"],
            "occurrences": head["occurrences"],
            "surface_families": head["surface_families"],
            "encoder_question_de": question,
            "choice_map_de": choice_map,
            "apprentice_rule_de": head["apprentice_mnemonic_de"],
        })

    occurrence_rows: list[dict[str, str]] = []
    for event in whole_events:
        card = cards_by_id[event["joint_tuple_id"]]
        mode, question, choice_map = HEAD_RULES[card["headword_id"]]
        subtype, exact_rule = CARD_VARIANTS[card["surface_family"]]
        statement_events = events_by_statement[event["statement_id"]]
        position = statement_events.index(event)
        previous = statement_events[position - 1]["surface_display"] if position else "STATEMENT_START"
        following = statement_events[position + 1]["surface_display"] if position + 1 < len(statement_events) else "STATEMENT_END"
        renderer_rule = (
            f"Gleiche exakte Karte; lokale Oberflaeche {event['surface_display']} kopieren, ohne Bedeutungswechsel."
            if mode == "RENDERER_ALLOGRAPH"
            else "Die exakte Kartenfamilie folgt der Bedeutungsunterart; zusaetzliche Huelle nicht neu uebersetzen."
        )
        occurrence_rows.append({
            "event_serial": event["event_serial"],
            "event_id": event["event_id"],
            "record_unit_id": event["record_unit_id"],
            "page": event["page"],
            "locus": event["locus"],
            "field_id": event["field_id"],
            "statement_id": event["statement_id"],
            "headword_id": card["headword_id"],
            "headword_de": card["headword_de"],
            "selection_mode": mode,
            "semantic_variant_de": subtype,
            "joint_tuple_id": event["joint_tuple_id"],
            "surface_family": card["surface_family"],
            "visible_surface": event["surface_display"],
            "previous_surface": previous,
            "following_surface": following,
            "source_trigger_de": EVENT_CUES[event["event_id"]],
            "exact_card_rule_de": exact_rule,
            "renderer_rule_de": renderer_rule,
            "readback_de": event["compact_contextual_event_de"],
            "statement_instruction_de": copy_by_statement[event["statement_id"]]["source_instruction_de"],
        })

    occurrence_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in occurrence_rows:
        occurrence_by_statement[row["statement_id"]].append(row)

    encoder_rows: list[dict[str, str]] = []
    for row in copybook:
        selected = occurrence_by_statement[row["statement_id"]]
        plan = " || ".join(
            f"{item['event_id']}:{item['headword_de']}->{item['visible_surface']} [{item['semantic_variant_de']}]"
            for item in selected
        ) or "KEIN_CODEBUCHGRIFF"
        cues = " || ".join(item["source_trigger_de"] for item in selected) or "Nur P/p-Bauteile verwenden."
        encoder_rows.append({
            "statement_id": row["statement_id"],
            "record_unit_id": row["record_unit_id"],
            "page": row["page"],
            "loci": row["loci"],
            "lesson_level": row["lesson_level"],
            "source_instruction_de": row["source_instruction_de"],
            "whole_variant_count": str(len(selected)),
            "whole_variant_plan_de": plan,
            "whole_variant_cues_de": cues,
            "target_surface_sequence": row["surface_sequence"],
            "target_architecture_sequence": row["architecture_sequence"],
            "readback_de": row["source_instruction_de"],
        })

    drill_rows: list[dict[str, str]] = []
    for ordinal, headword_id in enumerate(DRILL_HEADS, start=1):
        head = next(row for row in head_rows if row["headword_id"] == headword_id)
        selected = [row for row in occurrence_rows if row["headword_id"] == headword_id]
        drill_rows.append({
            "drill_id": f"V{ordinal:02d}",
            "headword_id": headword_id,
            "headword_de": head["headword_de"],
            "selection_mode": head["selection_mode"],
            "encoder_question_de": head["encoder_question_de"],
            "choice_map_de": head["choice_map_de"],
            "example_event_ids": "|".join(row["event_id"] for row in selected),
            "example_statement_ids": "|".join(dict.fromkeys(row["statement_id"] for row in selected)),
            "actual_surfaces": "|".join(row["visible_surface"] for row in selected),
            "exercise_de": "Decke die sichtbaren Formen ab, entscheide aus Besitzer und Arbeitsstufe und vergleiche erst danach mit der Kartenfolge.",
        })

    manual_lines = [
        "# Variantenblatt fuer die sechzehn Kopfwoerter",
        "",
        "## Drei Auswahlarten",
        "",
        "- `ONLY_FORM`: Bedeutung erkannt, einzige Ganzkarte schreiben.",
        "- `SEMANTIC_VARIANT_MENU`: die konkrete Arbeitsunterart waehlt eine exakte Karte.",
        "- `RENDERER_ALLOGRAPH`: die exakte Karte und Bedeutung bleiben gleich; die lokale Handform wird kopiert.",
        "",
        "## Die sieben wirklichen Auswahlfragen",
        "",
        "| Kopfwort | Frage | Auswahl |",
        "|---|---|---|",
    ]
    for headword_id in DRILL_HEADS:
        row = next(item for item in head_rows if item["headword_id"] == headword_id)
        manual_lines.append(f"| {row['headword_de']} | {row['encoder_question_de']} | {row['choice_map_de']} |")
    manual_lines.extend([
        "",
        "## Schreibgang",
        "",
        "1. Kopfwort aus der Arbeitsanweisung bestimmen.",
        "2. Bei einer Form sofort schreiben.",
        "3. Bei einem Variantenmenue Bildbesitzer, Prozessstufe und Ziel lesen.",
        "4. Bei Klarlauf und Voriges nur die lokale Handform aus dem Exemplar kopieren.",
        "5. Danach die produktiven P/p-Karten ergaenzen.",
        "6. Den ganzen Satz ruecklesen; eine physische Zeile ist kein erzwungenes Satzende.",
        "",
        "> Bedeutung waehlt die Kartenfamilie; Besitzer und Arbeitsstufe waehlen die Unterart; die Hand waehlt nur die Oberflaeche.",
    ])

    write_tsv(RULES_OUT, head_rows)
    write_tsv(OCCURRENCES_OUT, occurrence_rows)
    write_tsv(ENCODER_OUT, encoder_rows)
    write_tsv(DRILLS_OUT, drill_rows)
    MANUAL_OUT.write_text("\n".join(manual_lines).rstrip() + "\n", encoding="utf-8")

    modes = Counter(row["selection_mode"] for row in head_rows)
    summary = {
        "status": "PASS",
        "headwords": len(head_rows),
        "exact_whole_cards": len(cards),
        "whole_occurrences": len(occurrence_rows),
        "statements": len(encoder_rows),
        "variant_drills": len(drill_rows),
        "selection_modes": dict(modes),
        "files": {},
    }
    for path in [RULES_OUT, OCCURRENCES_OUT, ENCODER_OUT, DRILLS_OUT, MANUAL_OUT]:
        summary["files"][path.name] = {"sha256": sha256(path), "bytes": path.stat().st_size}
    SUMMARY_OUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return summary


if __name__ == "__main__":
    print(json.dumps(build(), ensure_ascii=False, indent=2))

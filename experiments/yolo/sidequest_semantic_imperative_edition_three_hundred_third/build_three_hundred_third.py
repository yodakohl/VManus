#!/usr/bin/env python3
"""Turn every fixed-page prose card into a short executable German clause."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
DICTIONARY = ROOT / "experiments/yolo/sidequest_semantic_two_layer_prose_two_hundred_seventy_ninth/TWO_HUNDRED_SEVENTY_NINTH_173_TWO_LAYER_DICTIONARY.tsv"
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_two_layer_prose_two_hundred_seventy_ninth/TWO_HUNDRED_SEVENTY_NINTH_381_TWO_LAYER_EVENTS.tsv"
PUNCTUATED = ROOT / "experiments/yolo/sidequest_semantic_punctuated_edition_three_hundred_second/THREE_HUNDRED_SECOND_116_PUNCTUATED_STATEMENTS.tsv"
SCOPE = ROOT / "experiments/yolo/sidequest_semantic_endpoint_scope_three_hundred_first/THREE_HUNDRED_FIRST_381_EVENT_SCOPE.tsv"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


SPECIAL = {
    "Wurzel": "Nimm die Wurzel",
    "Stängel": "Nimm den Stängel",
    "Teil": "Nimm den bezeichneten Teil",
    "Vollteil": "Nimm den ganzen bezeichneten Teil",
    "Kurzteil": "Nimm einen kleinen Teil",
    "Folgeteil": "Nimm danach den folgenden Teil",
    "Zugabeteil": "Nimm den Teil für die Zugabe",
    "Portion": "Nimm eine Portion",
    "erste Portion": "Nimm die erste Portion",
    "zweite Portion": "Nimm die zweite Portion",
    "Sollportion": "Nimm die vorgeschriebene Portion",
    "Sollmaß": "Arbeite nach dem vorgeschriebenen Maß",
    "Folgemaß": "Arbeite danach nach dem nächsten Maß",
    "Zugabemaß": "Gib die vorgeschriebene Menge zu",
    "Kurzsoll": "Halte die kurze Sollstufe ein",
    "Arbeitsstufe": "Stelle die Arbeitsstufe ein",
    "Endstufe": "Stelle die Endstufe ein",
    "Ansatz": "Verwende den Ansatz",
    "Folgeansatz": "Wechsle zum folgenden Ansatz",
    "derselbe Ansatz": "Verwende denselben Ansatz weiter",
    "Sudansatz": "Bereite den Sudansatz",
    "Zugabeansatz": "Bereite den Zugabeansatz",
    "aktueller Auszugsansatz": "Verwende den laufenden Auszugsansatz",
    "Bereitungsanteil": "Nimm einen Anteil der Bereitung",
    "Kochgut": "Setze das Kochgut an",
    "Klarlauf": "Nimm den klaren Ablauf",
    "Folgeklarlauf": "Nimm danach den klaren Ablauf",
    "Klarabzug": "Ziehe den klaren Anteil ab",
    "Abführgut": "Nimm das abzuführende Gut",
    "Auszug aus der Quelle": "Nimm den Auszug aus der Quelle",
    "bearbeiteter Quellauszug": "Nimm den bearbeiteten Quellauszug",
    "Quellposten": "Nimm den Posten aus der Quelle",
    "Quelleinsatz": "Setze den Quellposten ein",
    "Folgequelle": "Wechsle zur folgenden Quelle",
    "Zusatz": "Gib den Zusatz zu",
    "weitere Zutat": "Nimm die nächste Zutat",
    "aktuelle Zutat": "Nimm die aktuelle Zutat",
    "Einlage": "Lege die Einlage ein",
    "Aufnahmegefäß": "Stelle das Aufnahmegefäß bereit",
    "Auffanggefäß": "Stelle das Auffanggefäß bereit",
    "Gefäß für den Ansatz": "Stelle das Ansatzgefäß bereit",
    "Beckenlauf": "Führe durch den Beckenlauf",
    "Auslass": "Führe zum Auslass",
    "Anschluss": "Schließe am nächsten Abschnitt an",
    "Weiterweg": "Führe auf dem Weg weiter",
    "Endziel": "Führe bis zum Endziel",
    "Endposten": "Nimm den Endposten",
    "Zwischenziel": "Führe zum Zwischenziel",
    "Zielmarke": "Halte die Zielmarke ein",
    "dies": "Halte diesen Posten aktiv",
    "davon": "Nimm davon",
    "dorthin": "Führe ihn dorthin",
    "bereit": "Halte ihn bereit",
    "weiter": "Arbeite weiter",
    "das nächste": "Nimm das nächste",
    "kleiner Rest": "Nimm den kleinen Rest",
    "weiterer Anteil": "Nimm einen weiteren Anteil",
    "bemessen": "Messe den Posten ab",
    "teilen": "Teile den Posten",
    "einsetzen": "Setze den Posten ein",
    "überführen": "Führe den Posten über",
    "durchleiten": "Leite den Posten hindurch",
    "auswringen": "Wringe den Posten aus",
    "nachseihen": "Seihe ihn danach erneut",
    "kurz bearbeiten": "Bearbeite ihn kurz",
    "länger bearbeiten": "Bearbeite ihn länger",
    "weiter bearbeiten": "Bearbeite ihn weiter",
    "kurz weiterbearbeiten": "Bearbeite ihn kurz weiter",
    "kurz weiterführen": "Führe ihn kurz weiter",
    "länger einwirken lassen": "Lass ihn länger einwirken",
    "kurz einwirken lassen": "Lass ihn kurz einwirken",
    "kurz vorbereiten": "Bereite ihn kurz vor",
    "kurz wärmen": "Wärme ihn kurz",
    "eine vorgeschriebene Stehzeit einhalten": "Lass ihn die vorgeschriebene Zeit stehen",
    "vom vorigen Arbeitsgang nehmen": "Nimm ihn aus dem vorigen Arbeitsgang",
    "den Ansatz bereitstellen": "Stelle den Ansatz bereit",
    "die Arbeitsstufe setzen": "Stelle die Arbeitsstufe ein",
    "die Fortsetzung einsetzen": "Setze die Fortsetzung ein",
    "die Sollvorbereitung setzen": "Stelle die vorgeschriebene Vorbereitung ein",
    "die laufende Bereitung fortsetzen": "Führe die laufende Bereitung fort",
    "den laufenden Posten bearbeiten": "Bearbeite den laufenden Posten",
    "den laufenden Posten kurz bearbeiten": "Bearbeite den laufenden Posten kurz",
    "den laufenden Posten einsetzen und weiterbearbeiten": "Setze den laufenden Posten ein und bearbeite ihn weiter",
    "denselben Posten erneut einsetzen": "Setze denselben Posten erneut ein",
    "zum nächsten Posten wechseln": "Wechsle zum nächsten Posten",
    "zum Folgegang wechseln": "Wechsle zum Folgegang",
    "danach im selben Gang weiter": "Arbeite danach im selben Gang weiter",
    "danach mit diesem Posten weiter": "Arbeite danach mit diesem Posten weiter",
    "danach dorthin": "Führe ihn danach dorthin",
    "zur Folgeanwendung weiterführen": "Führe ihn zur folgenden Anwendung weiter",
    "laufendes Medium zugießen": "Gieße das laufende Medium zu",
    "Anteil zugeben": "Gib einen Anteil zu",
    "Zugabe am aktuellen Ziel": "Gib ihn an der aktuellen Stelle zu",
    "Auszug einsetzen": "Setze den Auszug ein",
    "am Ziel absetzen": "Lass ihn am Ziel absetzen",
    "an der Zielstelle bearbeiten": "Bearbeite ihn an der Zielstelle",
}

COMPOUND_SPECIAL = {
    "Zieltransfer": "Führe ihn zum Ziel über",
    "Langabsetzen": "Lass ihn lange absetzen",
    "Quellabführung": "Führe ihn von der Quelle ab",
    "Langsammlung": "Sammle ihn lange",
    "Zielpassage": "Führe ihn durch die Zielpassage",
    "Quellabzug": "Ziehe ihn aus der Quelle ab",
    "Abzug": "Ziehe ihn ab",
    "Sollsammlung": "Sammle ihn bis zur Sollmenge",
    "Waschgang": "Führe einen Waschgang aus",
    "Quelltransfer": "Führe ihn von der Quelle über",
    "Vorbereitungstransfer": "Führe die vorbereitete Portion über",
    "Kurzsammlung": "Sammle ihn kurz",
    "Zielabführung": "Führe ihn am Ziel ab",
    "Zieleinsatz": "Setze ihn am Ziel ein",
    "Folgetransfer": "Führe danach den nächsten Posten über",
    "Kurze Zielpassage": "Führe ihn kurz durch die Zielpassage",
    "Postentransfer": "Führe den aktuellen Posten über",
    "Nachtransfer": "Führe ihn danach über",
    "Zuführung": "Führe ihn zu",
    "Kurzhalt": "Halte ihn kurz",
    "Zielschluss": "Schließe den Schritt am Ziel ab",
    "Laufeinsatz": "Setze ihn in den Lauf ein",
    "Vollwaschung": "Wasche ihn vollständig",
    "Laufschluss": "Schließe den Lauf ab",
    "Weiterabzug": "Ziehe ihn weiter ab",
    "Langhalt": "Halte ihn lange",
    "Langer Zieleinsatz": "Setze ihn lange am Ziel ein",
    "Langwärmen": "Wärme ihn lange",
    "Weiterlauf": "Führe ihn im Lauf weiter",
    "Zielzuführung": "Führe ihn dem Ziel zu",
    "Abführung": "Führe ihn ab",
    "kurz absetzen": "Lass ihn kurz absetzen",
    "Kurzpassage": "Führe ihn kurz hindurch",
    "Trennabzug": "Ziehe die getrennte Fraktion ab",
    "Kurzvorbereitung": "Bereite ihn kurz vor",
    "Transfer": "Führe ihn über",
    "Volleinsatz": "Setze ihn vollständig ein",
    "Anteilstransfer": "Führe einen Anteil über",
    "Folgeabsetzen": "Lass danach den nächsten Posten absetzen",
    "Langfortsetzung": "Setze den Gang lange fort",
    "Einsatzabsetzen": "Lass ihn nach dem Einsatz absetzen",
    "Kurzdurchgang": "Führe ihn kurz hindurch",
    "Abführpassage": "Führe ihn durch die Abführpassage",
}

CLAUSE_SPECIAL = {
    "abziehen": "Ziehe ihn ab",
    "vorigen Posten überführen": "Führe den vorigen Posten über",
    "fertig": "Beende den Arbeitsschritt",
    "weiterführen": "Führe ihn weiter",
    "kalt stellen": "Stelle ihn kalt",
    "dorthin einsetzen": "Setze ihn dort ein",
    "lange sammeln": "Sammle ihn lange",
    "übertragen": "Übertrage ihn",
    "lange einwirken": "Lass ihn lange einwirken",
    "kurz einwirken": "Lass ihn kurz einwirken",
    "neuen Posten einsetzen": "Setze einen neuen Posten ein",
    "auftragen": "Trage ihn auf",
    "aus der Wärme nehmen und abkühlen": "Nimm ihn aus der Wärme und lass ihn abkühlen",
    "weiter abziehen": "Ziehe ihn weiter ab",
    "durchlassen": "Lass ihn hindurch",
    "abführen": "Führe ihn ab",
    "verwahren": "Verwahre ihn",
    "befestigen": "Befestige ihn",
    "lange Folgestufe": "Führe die lange Folgestufe aus",
}

NAMED_SPECIAL = {
    "Weiter einsetzen": "Setze den Posten weiter ein",
    "Langfolge": "Führe die lange Folge aus",
    "Quellausguss": "Gieße ihn aus der Quelle zu",
    "Kurzhalt am Ziel": "Halte ihn kurz am Ziel",
    "Fortsetzung vorbereiten": "Bereite die Fortsetzung vor",
    "Kurzfolge": "Führe die kurze Folge aus",
    "Frischwasser zugeben": "Gib frisches Wasser zu",
    "Sollabsetzung": "Lass ihn bis zum Sollzustand absetzen",
    "Zielbereitung": "Bereite ihn am Ziel",
    "Weiterposten": "Nimm den nächsten Posten zur Fortsetzung",
}


def strip_close(text: str) -> str:
    return re.sub(r"; (?:Schluss(?:; Arbeitsschritt festsetzen)?|Arbeitsschritt festsetzen)$", "", text.strip())


def imperative(gloss: str) -> tuple[str, str]:
    core = strip_close(gloss)
    if core in SPECIAL:
        return SPECIAL[core], "CURATED_IMPERATIVE"
    if core in COMPOUND_SPECIAL:
        return COMPOUND_SPECIAL[core], "PRODUCTIVE_NOUN_TO_IMPERATIVE"
    if core in CLAUSE_SPECIAL:
        return CLAUSE_SPECIAL[core], "RECIPE_INFINITIVE_OR_CLAUSE"
    if core in NAMED_SPECIAL:
        return NAMED_SPECIAL[core], "NAMED_WORKSTEP_IMPERATIVE"
    lower = core.lower()
    # Productive operation nouns. These retain every semantic qualifier.
    patterns = [
        ("abführung", "Führe {x} ab"),
        ("abzug", "Ziehe {x} ab"),
        ("transfer", "Führe {x} über"),
        ("zuführung", "Führe {x} zu"),
        ("einsatz", "Setze {x} ein"),
        ("passage", "Führe {x} durch"),
        ("durchgang", "Führe {x} durch"),
        ("sammlung", "Sammle {x}"),
        ("absetzen", "Lass {x} absetzen"),
        ("vorbereitung", "Bereite {x} vor"),
        ("fortsetzung", "Setze {x} fort"),
        ("halt", "Halte {x}"),
        ("wärmen", "Wärme {x}"),
        ("waschung", "Wasche {x}"),
        ("waschgang", "Führe {x} als Waschgang aus"),
        ("lauf", "Führe {x} im Lauf"),
        ("schluss", "Schließe {x} ab"),
    ]
    for ending, template in patterns:
        if lower.endswith(ending):
            qualifier = core[: -len(ending)].strip()
            object_text = "den Posten" if not qualifier else "den " + qualifier.lower() + "en Posten"
            return template.format(x=object_text), "PRODUCTIVE_NOUN_TO_IMPERATIVE"
    if core and core[0].islower():
        return core[0].upper() + core[1:], "RECIPE_INFINITIVE_OR_CLAUSE"
    return f"Führe den Schritt {core.lower()} aus", "NAMED_WORKSTEP_IMPERATIVE"


def main() -> None:
    dictionary = read(DICTIONARY)
    events = read(EVENTS)
    punct = {r["statement_id"]: r for r in read(PUNCTUATED)}
    scope = {r["event_id"]: r for r in read(SCOPE)}
    by_card: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_record: dict[str, list[str]] = defaultdict(list)
    for event in events:
        by_card[event["master_card_id"]].append(event)
        by_statement[event["statement_id"]].append(event)
        if event["statement_id"] not in by_record[event["record_unit_id"]]:
            by_record[event["record_unit_id"]].append(event["statement_id"])

    lexicon = []
    imperative_by_card = {}
    for card in dictionary:
        observed = by_card[card["master_card_id"]]
        source_glosses = {r["register_expansion_de"] for r in observed}
        assert len(source_glosses) == 1
        source_gloss = source_glosses.pop()
        clause, method = imperative(source_gloss)
        imperative_by_card[card["master_card_id"]] = clause
        lexicon.append({
            "master_card_id": card["master_card_id"],
            "master_form": card["master_form"],
            "registered_surfaces": card["registered_surfaces"],
            "family_parse": card["family_parse"],
            "source_short_value_de": strip_close(source_gloss),
            "imperative_clause_de": clause,
            "conversion_method": method,
            "event_count": len(observed),
        })
    lexicon_path = HERE / "THREE_HUNDRED_THIRD_173_IMPERATIVE_CARD_LEXICON.tsv"
    write(lexicon_path, lexicon)

    event_rows = []
    for event in events:
        s = scope[event["event_id"]]
        clause = imperative_by_card[event["master_card_id"]]
        if event["event_id"] == "E180":
            clause += " [am Zeilenrand einmal lesen]"
        if event["event_id"] == "E181":
            clause = "[sichtbare Wiederholung; nicht nochmals ausführen]"
        event_rows.append({
            "event_id": event["event_id"],
            "source_token_id": s["source_token_id"],
            "statement_id": event["statement_id"],
            "record_unit_id": event["record_unit_id"],
            "page": event["page"],
            "field_id": event["field_id"],
            "visible_owner": event["visible_owner"],
            "visible_surface": event["visible_surface"],
            "master_card_id": event["master_card_id"],
            "source_short_value_de": strip_close(event["register_expansion_de"]),
            "imperative_clause_de": clause,
            "terminal_status": event["terminal_status"],
        })
    event_path = HERE / "THREE_HUNDRED_THIRD_381_IMPERATIVE_EVENTS.tsv"
    write(event_path, event_rows)

    statement_rows = []
    for statement_id, selected in by_statement.items():
        p = punct[statement_id]
        clauses = []
        previous_field = None
        read_tokens = []
        for event in selected:
            if event["event_id"] == "E181":
                continue
            if previous_field is not None and previous_field != event["field_id"]:
                clauses.append("Öffne das nächste Feld")
            if event["event_id"] in {"E203", "E264", "E291", "E356"}:
                clauses.append("Setze den sichtbaren Besitzer neu")
            clause = imperative_by_card[event["master_card_id"]]
            if event["event_id"] == "E180":
                clause += " und lies die Randwiederholung nur einmal"
            clauses.append(clause)
            read_tokens.append(scope[event["event_id"]]["source_token_id"])
            previous_field = event["field_id"]
        ending = ";" if p["punctuation_class"] == "COMMIT_SEMICOLON" else (" …" if p["punctuation_class"] == "OPEN_RECORD_RELEASE" else " ↪")
        continuous = clauses[0] + "".join("; dann " + clause[0].lower() + clause[1:] for clause in clauses[1:]) + ending
        continuous = continuous[0].upper() + continuous[1:]
        statement_rows.append({
            "statement_id": statement_id,
            "record_unit_id": p["record_unit_id"],
            "page": p["page"],
            "owner_slot": p["owner_slot"],
            "field_path": p["field_path"],
            "visible_event_count": len(selected),
            "read_source_token_count": len(set(read_tokens)),
            "surface_punctuated": p["surface_punctuated"],
            "fluent_imperative_de": continuous,
            "punctuation_class": p["punctuation_class"],
            "trace_rule_de": "Jede Klausel entspricht genau einer gelesenen Karte; Feld- und Besitzerwechsel sind ausgeschrieben.",
        })
    statement_path = HERE / "THREE_HUNDRED_THIRD_116_FLUENT_IMPERATIVE_STATEMENTS.tsv"
    write(statement_path, statement_rows)

    headings = {
        "H1": "f10r · Pflanzenartikel I", "H2": "f10r · Pflanzenartikel II",
        "H3": "f11r · Pflanzenartikel", "H4": "f55v · Pflanzenartikel",
        "H5": "f56r · Pflanzenartikel", "B1": "f81v · Bad-/Waschregister",
        "B2": "f82r · lokale Bad-/Gefäßstationen", "B3": "f83r · Stationsregister I",
        "B4": "f83r · Stationsregister II", "B5": "f83r · technischer Nachtrag I",
        "B6": "f83r · technischer Nachtrag II",
    }
    row_by_statement = {r["statement_id"]: r for r in statement_rows}
    lines = ["# Vollständige flüssige Werkstattausgabe der sieben Prosaseiten", "", "Jede durch Semikolon getrennte Teilklausel geht auf genau eine gelesene Ganzkarte zurück. Die Form ist moderne deutsche Arbeitsprosa; der Inhalt bleibt die aktuelle kreative Werkstatttheorie.", ""]
    for record_id, statement_ids in by_record.items():
        owner = row_by_statement[statement_ids[0]]["owner_slot"]
        lines += [f"## {record_id} — {headings[record_id]}", "", f"**Stiller Besitzer:** {owner}.", ""]
        for statement_id in statement_ids:
            row = row_by_statement[statement_id]
            lines += [f"**{statement_id}:** {row['fluent_imperative_de']}", ""]
    edition_path = HERE / "THREE_HUNDRED_THIRD_ELEVEN_RECORD_FLUENT_EDITION.md"
    edition_path.write_text("\n".join(lines), encoding="utf-8")

    method_counts = Counter(r["conversion_method"] for r in lexicon)
    report_path = HERE / "THREE_HUNDRED_THIRD_REPORT.md"
    report_path.write_text(
        "# Sidequest-Pass 303: jede Karte als ausführbare Klausel\n\n"
        "Alle 173 Prosakarten und 381 sichtbaren Ereignisse besitzen jetzt neben dem kurzen Kartenwert eine vollständige deutsche Imperativklausel. Dadurch lassen sich alle 116 Aussagen und elf Records ohne Nominalzettel oder leere Platzhalter lesen. "
        f"{method_counts['CURATED_IMPERATIVE']} Karten erhielten eine gezielt formulierte Klausel, {method_counts['PRODUCTIVE_NOUN_TO_IMPERATIVE']} folgen einem produktiven Operationsmuster, {method_counts['RECIPE_INFINITIVE_OR_CLAUSE']} waren bereits ausführbare Rezeptklauseln und {method_counts['NAMED_WORKSTEP_IMPERATIVE']} seltene gelehrte Schritte bleiben als benannte Werkstattoperationen lesbar.\n\n"
        "Die neue Ausgabe ist nicht eine Lautentschlüsselung, sondern die bislang vollständigste Ausführung unserer Schreibertheorie: keine Karte fällt semantisch heraus, und jede flüssige Klausel bleibt auf Karten-ID und Ereignis zurückführbar. Als nächstes sollten die generischen benannten Arbeitsschritte einzeln durch konkrete Verben ersetzt und die wiederkehrenden Satzketten zu einem kleinen historischen Rezeptstil geglättet werden.\n",
        encoding="utf-8",
    )
    summary = {
        "status": "PASS", "cards": len(lexicon), "events": len(event_rows), "statements": len(statement_rows), "records": len(by_record),
        "visible_events": sum(int(r["visible_event_count"]) for r in statement_rows),
        "read_source_tokens": sum(int(r["read_source_token_count"]) for r in statement_rows),
        "conversion_methods": dict(method_counts),
        "source_hashes": {str(p.relative_to(ROOT)): sha(p) for p in [DICTIONARY, EVENTS, PUNCTUATED, SCOPE]},
        "output_hashes": {p.name: sha(p) for p in [lexicon_path, event_path, statement_path, edition_path, report_path]},
    }
    (HERE / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

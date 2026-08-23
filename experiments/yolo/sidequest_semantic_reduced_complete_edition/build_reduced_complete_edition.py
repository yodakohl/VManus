#!/usr/bin/env python3
"""Build a complete 116-statement and eleven-record creative translation."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
GRAMMAR = ROOT / "experiments/yolo/sidequest_semantic_second_ring_grammar"
UNIQUE = ROOT / "experiments/yolo/sidequest_semantic_unique_master_glosses"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: str(row.get(field, "")) for field in fields})


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


LOCAL_IMPERATIVES = {
    "dchol": "Nimm das Vorige",
    "dl": "Gib den Zusatz zu",
    "cfhy": "Wringe aus",
    "cheeckhody": "Trage auf und schließe",
    "cphy": "Seihe nach",
    "dchey": "Nimm die Wurzel",
    "dshedy": "Gib Frischwasser zu und schließe",
    "lkedy": "Wasche nach und schließe",
    "ly": "Nimm das Sammelgefäß",
    "oykchor": "Nimm das Ansatzgefäß",
    "qekey": "Verwende roh",
    "qokylddy": "Befestige und schließe",
    "sh": "Nimm den Stängel",
    "skar": "Gieße vom Ausgang aus",
    "sotodan": "Wende danach an",
    "sshkchdy": "Schwenke und schließe",
    "talam": "Verwahre am Ziel",
    "tchody": "Stelle kalt und schließe",
    "ytey": "Fülle",
}


EXACT_NUCLEUS_IMPERATIVES = {
    "VORGABEWERT": "Stelle den Vorgabewert ein",
    "ANTEIL": "Nimm einen Anteil",
    "VOM AUSGANG": "Nimm vom Ausgang",
    "ZUM ZIEL": "Führe zum Ziel",
    "AKTUELLER POSTEN": "Nimm den aktuellen Posten",
    "FREIGEGEBENER WERT": "Lies den freigegebenen Wert",
    "EINGANGSPOSTEN": "Nimm den Eingangsposten",
    "FORTSETZEN": "Führe fort",
    "ABDECKTRÄGER": "Nimm den Abdeckträger",
    "BEARBEITEN": "Bearbeite den aktuellen Posten",
    "ZURÜCKNEHMEN": "Nimm zurück",
    "ANSATZ": "Bereite den Ansatz",
    "UMSCHLIESSENDER TRÄGER": "Gib in den umschließenden Träger",
    "FOLGEPOSTEN": "Nimm den Folgeposten",
    "STUFE": "Stelle die Stufe ein",
    "WASSERLAUF": "Nutze den Wasserlauf",
    "AUSLASS": "Nutze den Auslass",
    "WASCHGANG": "Führe den Waschgang aus",
    "TRENNEN": "Trenne",
    "AUSZUGSANSATZ": "Bereite den Auszugsansatz",
    "ENDZIEL": "Führe zum Endziel",
    "HALTEWERT": "Halte bis zum Vorgabewert",
    "ABFÜHREN": "Führe ab",
    "ABSEIHEN": "Seihe ab",
    "AKTUELLEN POSTEN ABZIEHEN": "Ziehe den aktuellen Posten ab",
    "AKTUELLEN POSTEN ZUM ZIEL": "Führe den aktuellen Posten zum Ziel",
    "AKTUELLER EINGANGSPOSTEN": "Nimm den aktuellen Eingangsposten",
    "ANSATZ ZUM ZIEL": "Führe den Ansatz zum Ziel",
    "EINFÜHREN": "Führe ein",
    "EINGANGSPOSTEN ZUM ZIEL": "Führe den Eingangsposten zum Ziel",
    "EINGANGSWERT": "Stelle den Eingangswert ein",
    "FOLGEANSATZ": "Bereite den Folgeansatz",
    "FORTGESETZTER ANSATZ": "Führe den Ansatz weiter",
    "GANZER TEIL": "Nimm den ganzen Teil",
    "GEZÄHLTEN TEIL ZUGEBEN": "Gib einen gezählten Anteil zu",
    "KURZ BEREITHALTEN": "Halte kurz bereit",
    "KURZE FOLGE": "Führe die kurze Folge aus",
    "KURZER TEIL": "Nimm einen kurzen Teil",
    "LANGE FOLGE": "Führe die lange Folge aus",
    "NÄCHSTER POSTEN": "Nimm den nächsten Posten",
    "NÄCHSTER POSTEN; LANGE STUFE": "Nimm den nächsten Posten in langer Stufe",
    "POSTEN DURCH AUSGANG FÜHREN": "Führe den Posten durch den Ausgang",
    "POSTEN VOM AUSGANG": "Nimm den Posten vom Ausgang",
    "POSTEN ZUR UNTEREN ZIELSTELLE": "Führe den Posten zur unteren Zielstelle",
    "SEIHEN": "Seihe",
    "TEIL ABTRENNEN": "Trenne einen Teil ab",
    "TEIL DES EINGANGSPOSTENS": "Nimm einen Teil des Eingangspostens",
    "WASCHEN": "Wasche",
    "WASSERLAUF SCHLIESSEN": "Schließe den Wasserlauf",
    "ZIEL SCHLIESSEN": "Schließe das Ziel",
    "ÜBERTRAGEN": "Übertrage",
    "ZUM ZIEL ÜBERTRAGEN": "Übertrage zum Ziel",
    "SETZEN UND ÜBERTRAGEN": "Setze an, übertrage",
    "VOM AUSGANG ABFÜHREN": "Führe vom Ausgang ab",
    "AKTUELLEN POSTEN ERNEUT SETZEN": "Setze den aktuellen Posten erneut",
    "ZUM ZIEL DURCHLEITEN": "Leite zum Ziel durch",
    "VOM AUSGANG ÜBERTRAGEN": "Übertrage vom Ausgang",
    "VOM AUSGANG SETZEN": "Setze vom Ausgang aus an",
    "AKTUELLEN POSTEN AM ZIEL SETZEN": "Setze den aktuellen Posten am Ziel",
    "KURZ ZUM ZIEL DURCHLEITEN": "Leite kurz zum Ziel durch",
    "NÄCHSTEN TEIL FORTSETZEN": "Führe den nächsten Teil fort",
    "KURZ HALTEN UND FORTSETZEN": "Halte kurz und führe fort",
    "AM ZIEL BEARBEITEN": "Bearbeite am Ziel",
    "ABFÜHRUNG FORTSETZEN": "Führe die Abführung fort",
    "LÄNGER AM ZIEL HALTEN": "Halte länger am Ziel",
    "KURZ AM ZIEL HALTEN": "Halte kurz am Ziel",
    "AUF VORGABEWERT SETZEN": "Stelle auf den Vorgabewert ein",
    "DANACH VOM AUSGANG": "Nimm danach vom Ausgang",
    "ZUM ZIEL EINFÜHREN": "Führe zum Ziel ein",
    "AUF DEM ARBEITSWEG FORTSETZEN": "Führe auf dem Arbeitsweg fort",
    "REST ABFÜHREN": "Führe den Rest ab",
    "BIS VORGABEWERT SAMMELN": "Sammle bis zum Vorgabewert",
    "AM ZIEL ABSETZEN": "Lass am Ziel absetzen",
    "ZUM ZIEL ABFÜHREN": "Führe zum Ziel ab",
    "BEREITEN POSTEN ÜBERTRAGEN": "Übertrage den bereiten Posten",
    "BEREIT FORTSETZEN": "Führe den bereiten Posten fort",
    "WASSERLAUF SETZEN": "Öffne den Wasserlauf",
    "DANACH ZUM ZIEL": "Führe danach zum Ziel",
    "ABSETZGANG SETZEN": "Beginne den Absetzgang",
}


OBJECT_FORMS = {
    "AKTUELLEN POSTEN": "den aktuellen Posten",
    "POSTEN VOM AUSGANG": "den Posten vom Ausgang",
    "FOLGEPOSTEN": "den Folgeposten",
    "FOLGENDEN POSTEN": "den Folgeposten",
    "EINGANGSPOSTEN": "den Eingangsposten",
    "EINGANGSPOSTEN ZUM ZIEL": "den Eingangsposten zum Ziel",
    "ANTEIL": "einen Anteil",
    "GANZER TEIL": "den ganzen Teil",
    "KURZER TEIL": "einen kurzen Teil",
    "TEIL DES EINGANGSPOSTENS": "einen Teil des Eingangspostens",
    "BEREITER POSTEN": "den bereiten Posten",
    "BEREITEN POSTEN": "den bereiten Posten",
    "AUSZUG": "den Auszug",
    "FREIGEGEBENEN WERT": "den freigegebenen Wert",
    "WASSERLAUF": "den Wasserlauf",
    "ANSATZ": "den Ansatz",
    "FORTSETZUNG": "die Fortsetzung",
    "ZIEL": "das Ziel",
}


def object_form(text: str) -> str:
    return OBJECT_FORMS.get(text, text.lower())


def imperative_from_nucleus(head: str, nucleus: str) -> str:
    if head in LOCAL_IMPERATIVES:
        return LOCAL_IMPERATIVES[head]
    close = nucleus.endswith("; SCHLUSS")
    core = nucleus.removesuffix("; SCHLUSS").strip()
    if core in EXACT_NUCLEUS_IMPERATIVES:
        phrase = EXACT_NUCLEUS_IMPERATIVES[core]
    elif core.startswith("DANACH "):
        rest = imperative_from_nucleus("", core.removeprefix("DANACH "))
        phrase = "Danach " + rest[:1].lower() + rest[1:]
    elif core.endswith(" ÜBERTRAGEN"):
        obj = core.removesuffix(" ÜBERTRAGEN")
        phrase = "Übertrage " + object_form(obj)
    elif core.endswith(" SETZEN"):
        obj = core.removesuffix(" SETZEN")
        replacements = {
            "AKTUELLEN POSTEN": "den aktuellen Posten",
            "KURZE STUFE": "die kurze Stufe",
            "LANGE STUFE": "die lange Stufe",
            "VOLLSTÄNDIG": "vollständig",
            "AM ZIEL": "am Ziel",
            "FORTSETZUNG": "die Fortsetzung",
            "WASSERLAUF": "den Wasserlauf",
            "AUSZUG": "den Auszug",
            "KURZEN DURCHLAUF": "den kurzen Durchlauf",
            "ABSETZGANG": "den Absetzgang",
        }
        phrase = "Setze " + replacements.get(obj, obj.lower())
    elif core.endswith(" FORTSETZEN"):
        obj = core.removesuffix(" FORTSETZEN")
        phrase = "Führe " + (object_form(obj) + " " if obj else "") + "fort"
    elif core.endswith(" ABFÜHREN"):
        obj = core.removesuffix(" ABFÜHREN")
        phrase = "Führe " + (object_form(obj) + " " if obj else "") + "ab"
    elif core.endswith(" DURCHLEITEN"):
        obj = core.removesuffix(" DURCHLEITEN")
        phrase = "Leite " + (object_form(obj) + " " if obj else "") + "durch"
    elif core.endswith(" EINFÜHREN"):
        obj = core.removesuffix(" EINFÜHREN")
        phrase = "Führe " + (object_form(obj) + " " if obj else "") + "ein"
    elif core.endswith(" WÄRMEN"):
        grade = core.removesuffix(" WÄRMEN").lower()
        phrase = "Wärme " + grade
    elif core.endswith(" ABSETZEN"):
        modifier = core.removesuffix(" ABSETZEN").lower()
        phrase = "Lass " + (modifier + " " if modifier else "") + "absetzen"
    elif core.endswith(" SAMMELN"):
        modifier = core.removesuffix(" SAMMELN").lower()
        phrase = "Sammle " + modifier
    elif core.endswith(" SEIHEN"):
        modifier = core.removesuffix(" SEIHEN").lower()
        phrase = ("Seihe " + modifier).strip()
    elif core.endswith(" WASCHEN"):
        modifier = core.removesuffix(" WASCHEN").lower()
        phrase = ("Wasche " + modifier).strip()
    elif core.endswith(" HALTEN"):
        modifier = core.removesuffix(" HALTEN").lower()
        phrase = "Halte " + modifier
    elif core.endswith(" BEARBEITEN"):
        modifier = core.removesuffix(" BEARBEITEN").lower()
        phrase = "Bearbeite " + modifier
    elif core.endswith(" ENTNEHMEN"):
        obj = core.removesuffix(" ENTNEHMEN")
        phrase = "Entnimm " + object_form(obj)
    elif core == "BEREITER ANSATZ":
        phrase = "Halte den Ansatz bereit"
    elif core == "BEREITER POSTEN":
        phrase = "Halte den Posten bereit"
    elif core == "BEREIT FORTSETZEN":
        phrase = "Führe bereit fort"
    elif core == "BEREITWERT":
        phrase = "Stelle den Bereitwert ein"
    elif core == "ABSETZWERT":
        phrase = "Stelle den Absetzwert ein"
    elif core == "FOLGEWERT":
        phrase = "Stelle den Folgewert ein"
    elif core == "KURZER FOLGEWERT":
        phrase = "Stelle den kurzen Folgewert ein"
    elif core == "EINGANGSANSATZ":
        phrase = "Bereite den Eingangsansatz"
    elif core == "ANSATZANTEIL":
        phrase = "Nimm einen Anteil des Ansatzes"
    elif core == "WEITERER ANTEIL":
        phrase = "Nimm einen weiteren Anteil"
    elif core == "POSTENWERT":
        phrase = "Stelle den Postenwert ein"
    elif core == "POSTENANTEIL":
        phrase = "Nimm einen Anteil des Postens"
    elif core == "AKTUELLER ANTEIL":
        phrase = "Nimm den aktuellen Anteil"
    elif core == "AUSZUG VOM AUSGANG":
        phrase = "Nimm den Auszug vom Ausgang"
    elif core == "FREIGEGEBENER WERT":
        phrase = "Lies den freigegebenen Wert"
    else:
        phrase = "Führe aus: " + core.lower()
    if close and "schließe" not in phrase.lower():
        phrase += " und schließe"
    return phrase[:1].upper() + phrase[1:]


FLUENT_REPLACEMENTS = [
    ("sein Sollmass", "seinen Vorgabewert"), ("sein Sollmaß", "seinen Vorgabewert"),
    ("das Sollmass", "den Vorgabewert"), ("das Sollmaß", "den Vorgabewert"),
    ("das Folgemass", "den Folgewert"), ("das Folgemaß", "den Folgewert"),
    ("das Zutatenmass", "den Eingangswert"), ("das Zutatenmaß", "den Eingangswert"),
    ("Sollmass", "Vorgabewert"), ("Sollmaß", "Vorgabewert"),
    ("Sollstufe", "Stufe"), ("Folgemass", "Folgewert"), ("Folgemaß", "Folgewert"),
    ("Fertigmass", "Bereitwert"), ("Fertigmaß", "Bereitwert"),
    ("Standmass", "Haltewert"), ("Standmaß", "Haltewert"),
    ("Absetzmass", "Absetzwert"), ("Absetzmaß", "Absetzwert"),
    ("Postenmass", "Postenwert"), ("Postenmaß", "Postenwert"),
    ("weitere Portionen", "weitere Anteile"), ("weitere Portion", "weiteren Anteil"),
    ("eine Portion", "einen Anteil"), ("einer Portion", "einem Anteil"),
    ("Portionen", "Anteile"), ("Portion", "Anteil"),
    ("Klarlauf", "freigegebenen Auszug"),
    ("sein Vorgabewert", "seinen Vorgabewert"), ("das Vorgabewert", "den Vorgabewert"),
    ("das Folgewert", "den Folgewert"), ("eine weiteren Anteil", "einen weiteren Anteil"),
    ("die Anteil", "den Anteil"), ("eine Postenportion", "einen Postenanteil"),
    ("Postenportion", "Postenanteil"), ("Zutatenmass", "Eingangswert"),
    ("Fuehre", "Führe"), ("fuehre", "führe"), ("laenger", "länger"),
    ("waerme", "wärme"), ("Waerme", "Wärme"), ("schliesse", "schließe"),
    ("Schliesse", "Schließe"), ("naechsten", "nächsten"), ("Gefaess", "Gefäß"),
    ("weitergefuehrten", "weitergeführten"), ("zurueck", "zurück"),
    ("Staengel", "Stängel"), ("uebergib", "übergib"),
    ("vollstaendig", "vollständig"), ("Nebenoeffnung", "Nebenöffnung"),
    ("Oeffnung", "Öffnung"), ("oeffnung", "öffnung"),
    ("abgekuehlt", "abgekühlt"), ("gekuehlt", "gekühlt"),
    ("giesse", "gieße"), ("Giesse", "Gieße"),
    ("setze um", "übertrage"), ("Setze um", "Übertrage"),
]


FLUENT_OVERRIDES = {
    "H1-S001": "Nimm die Wurzel, halte den Ansatz bereit, nimm vom Ausgang, trenne einen Teil, gib ihn in den Träger, öffne den Wasserlauf, führe den nächsten Teil weiter und setze den aktuellen Posten auf den Vorgabewert.",
    "H2-S002": "Nimm den Folgeansatz, führe Ansatz und Fortsetzungsansatz weiter, stelle den Vorgabewert ein und entnimm ihn vom Ausgang.",
    "H5-S001": "Setze einen Eingangsansatz an, bringe den Eingangsposten zum Ziel, nimm den Vorgabewert, bearbeite weiter, beginne den Folgeansatz und setze den aktuellen Posten am Ziel.",
    "H4-S002": "Stelle den Vorgabewert ein, übertrage den Posten und verwahre ihn am Ziel.",
    "H4-S003": "Stelle den Postenwert ein, nimm den Auszug vom Ausgang, wärme länger, führe fort und schließe.",
    "B1-S002": "Setze den Vorgabewert, setze das Beckenwasser am Ziel an, nimm vom Ausgang, führe weiter, gib Anteil und weiteren Anteil zum Ziel, halte dort länger, übertrage und schließe.",
    "B1-S006": "Gib einen gezählten Anteil und den Zusatz zu, leite den Posten durch und führe ihn zum Ziel.",
    "B1-S007": "Setze den Posten an, übertrage und schließe.",
    "B1-S015": "Fülle das Gefäß, setze den Inhalt an, übertrage und schließe.",
    "B1-S018": "Nimm das Sammelgefäß, halte den Posten kurz, führe fort, stelle die Stufe ein, sammle länger und schließe.",
    "B2-S005": "Setze den aktuellen Posten am Ziel, sammle bis zum Vorgabewert, leite durch, setze zweimal auf Vorgabewert, führe bereit fort, wärme länger, führe ab und schließe.",
    "B2-S011": "Gib einen gezählten Anteil zu, nimm vom Ausgang einen weiteren Anteil, setze länger an und schließe.",
    "B2-S015": "Nimm den freigegebenen Auszug, setze länger an und schließe.",
    "B2-S016": "Führe zum Ziel und vom Ausgang ab, trenne, setze den Vorgabewert, nimm den langen Folgeposten, setze kurz, führe ein und schließe.",
    "B2-S017": "Halte den Posten kurz am Ziel, schließe das Ziel und beende den Schritt.",
    "B3-S003": "Nimm den aktuellen Posten, stelle den Vorgabewert ein, nimm ihn wieder auf, führe ab und schließe.",
    "B3-S005": "Übertrage und schließe.",
    "B3-S006": "Übertrage den aktuellen Posten, setze ihn am Ziel an, führe weiter und schließe.",
    "B3-S011": "Übertrage den bereiten Posten, setze ihn an, übertrage den aktuellen Posten und nimm ihn vom Ausgang.",
    "B3-S012": "Bereite den Ansatz, lass ihn absetzen und schließe.",
    "B3-S022": "Übertrage den Folgeposten und schließe.",
    "B3-S026": "Übertrage vom Ausgang, stelle den Absetzwert ein, übertrage den aktuellen Posten, gib einen Anteil zu, halte den Posten bereit, führe den Ansatz zum Ziel, sammle länger und schließe.",
    "B3-S030": "Setze den Posten an, stelle den Vorgabewert ein, nutze den Wasserlauf, übertrage den Folgeposten und schließe.",
    "B3-S032": "Übertrage einen Anteil und den aktuellen Posten, setze den kurzen Folgewert und den Folgewert, führe die kurze Folge aus und schließe.",
    "B3-S034": "Setze die Stufe, halte bereit, trenne einen Teil, setze den Folgewert, führe zur unteren Zielstelle, setze kurz ab und schließe.",
}


RECORD_TITLES = {
    "H1": "Wurzelansatz",
    "H2": "Fortgesetzter Pflanzenansatz",
    "H3": "Auswringen, Stehenlassen und Nachseihen",
    "H4": "Verwahrter Auszug",
    "H5": "Frische Pflanzenfolge",
    "B1": "Gemeinsamer Beckenweg",
    "B2": "Stations- und Durchlaufweg",
    "B3": "Hauptfolge der Anwendungen",
    "B4": "Tuch-, Halte- und Nachwaschfolge",
    "B5": "Nachtrag: Ziel- und Öffnungsfolge",
    "B6": "Nachtrag: Abschlussfolge",
}


def revise_fluent(statement_id: str, text: str) -> str:
    if statement_id in FLUENT_OVERRIDES:
        return FLUENT_OVERRIDES[statement_id]
    revised = text.strip()
    for old, new in FLUENT_REPLACEMENTS:
        revised = revised.replace(old, new)
    if revised and revised[-1] not in ".!?":
        revised += "."
    return revised


def main() -> None:
    dictionary = read_tsv(GRAMMAR / "COMPLETE_173_EXTENDED_CARD_DICTIONARY.tsv")
    events = read_tsv(GRAMMAR / "PROSE_381_EXTENDED_COMPONENT_READER.tsv")
    statements = read_tsv(UNIQUE / "UNIQUE_116_STATEMENT_EDITION.tsv")

    card_rows = []
    for card in dictionary:
        imperative = imperative_from_nucleus(card["master_head_form"], card["portable_nucleus_de"])
        card_rows.append({
            **card,
            "imperative_phrase_de": imperative,
            "apprentice_reading_rule_de": "Atomfolge lesen, Lehrimperativ bilden, danach konkreten Besitzerwert einsetzen",
        })
    write_tsv(
        OUT / "IMPERATIVE_173_CARD_DICTIONARY.tsv",
        card_rows,
        list(dictionary[0]) + ["imperative_phrase_de", "apprentice_reading_rule_de"],
    )

    card_by_mc = {row["master_card_id"]: row for row in card_rows}
    event_rows = []
    events_by_statement: dict[str, list[dict[str, object]]] = defaultdict(list)
    for event in events:
        card = card_by_mc[event["master_card_id"]]
        row = {
            **event,
            "imperative_phrase_de": card["imperative_phrase_de"],
            "reading_source": card["composition_layer"],
        }
        event_rows.append(row)
        events_by_statement[event["statement_id"]].append(row)
    write_tsv(
        OUT / "IMPERATIVE_381_EVENT_TRACE.tsv",
        event_rows,
        list(events[0]) + ["imperative_phrase_de", "reading_source"],
    )

    statement_rows = []
    for statement in statements:
        sid = statement["statement_id"]
        statement_events = events_by_statement[sid]
        atom_chain = " | ".join(str(row["atom_sequence"]) for row in statement_events)
        nucleus_chain = " → ".join(str(row["portable_nucleus_de"]) for row in statement_events)
        imperative_chain = "; ".join(str(row["imperative_phrase_de"]) for row in statement_events)
        reduced = revise_fluent(sid, statement["fluent_workshop_sentence_de"])
        local_count = sum(row["composition_layer"] == "LEARNED_LOCAL_WHOLE" for row in statement_events)
        status = "FULLY_COMPOSED" if local_count == 0 else "COMPOSED_WITH_LOCAL_WHOLE_WORDS"
        statement_rows.append({
            "statement_id": sid,
            "record_unit_id": statement["record_unit_id"],
            "page": statement["page"],
            "loci": statement["loci"],
            "event_count": statement["event_count"],
            "surface_sequence": statement["surface_sequence"],
            "atom_sequence_chain": atom_chain,
            "portable_nucleus_chain_de": nucleus_chain,
            "card_imperative_chain_de": imperative_chain,
            "previous_fluent_reading_de": statement["fluent_workshop_sentence_de"],
            "reduced_fluent_reading_de": reduced,
            "local_whole_word_events": local_count,
            "composition_status": status,
            "crosses_physical_line": "YES" if "|" in statement["loci"] else "NO",
            "revision_status": "REPHRASED" if reduced != statement["fluent_workshop_sentence_de"] else "RETAINED_ALREADY_CONCISE",
        })
    statement_fields = [
        "statement_id", "record_unit_id", "page", "loci", "event_count", "surface_sequence",
        "atom_sequence_chain", "portable_nucleus_chain_de", "card_imperative_chain_de",
        "previous_fluent_reading_de", "reduced_fluent_reading_de", "local_whole_word_events",
        "composition_status", "crosses_physical_line", "revision_status",
    ]
    write_tsv(OUT / "COMPLETE_116_RETRANSLATED_STATEMENTS.tsv", statement_rows, statement_fields)

    statement_groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in statement_rows:
        statement_groups[str(row["record_unit_id"])].append(row)
    record_rows = []
    record_lines = [
        "# Vollständige reduzierte Ausgabe der elf Prosa-Records", "",
        "Jede Aussage folgt ihrer tatsächlichen Aussagegrenze; ein physischer Zeilenwechsel beendet den Satz nicht automatisch.", "",
    ]
    for record_id in RECORD_TITLES:
        rows = statement_groups[record_id]
        record_events = sum(int(row["event_count"]) for row in rows)
        local_events = sum(int(row["local_whole_word_events"]) for row in rows)
        pages = ";".join(dict.fromkeys(str(row["page"]) for row in rows))
        continuous = " ".join(str(row["reduced_fluent_reading_de"]) for row in rows)
        record_rows.append({
            "record_unit_id": record_id,
            "title_de": RECORD_TITLES[record_id],
            "pages": pages,
            "statement_count": len(rows),
            "event_count": record_events,
            "composed_event_count": record_events - local_events,
            "local_whole_word_events": local_events,
            "line_spanning_statements": sum(row["crosses_physical_line"] == "YES" for row in rows),
            "continuous_reduced_reading_de": continuous,
        })
        record_lines += [f"## {record_id} — {RECORD_TITLES[record_id]} · {pages}", "", f"**Durchgehende Lesung:** {continuous}", "", "**Aussagen:**", ""]
        for row in rows:
            record_lines.append(f"- **{row['statement_id']} · {row['loci']}** — `{row['surface_sequence']}`")
            record_lines.append(f"  {row['reduced_fluent_reading_de']}")
        record_lines.append("")
    write_tsv(
        OUT / "ELEVEN_RECORD_REDUCED_SUMMARY.tsv",
        record_rows,
        ["record_unit_id", "title_de", "pages", "statement_count", "event_count", "composed_event_count", "local_whole_word_events", "line_spanning_statements", "continuous_reduced_reading_de"],
    )
    (OUT / "ELEVEN_RECORD_COMPLETE_READING.md").write_text("\n".join(record_lines).rstrip() + "\n", encoding="utf-8")

    rephrased = sum(row["revision_status"] == "REPHRASED" for row in statement_rows)
    fully_composed = sum(row["composition_status"] == "FULLY_COMPOSED" for row in statement_rows)
    line_spanning = sum(row["crosses_physical_line"] == "YES" for row in statement_rows)
    report = f"""# Vollständige reduzierte Prosa-Ausgabe

## Ergebnis

Die 31 produktiven Atome und 19 lokalen Ganzkarten sind jetzt nicht mehr nur Wörterbuchmaterial. Alle 173 Meisterkarten besitzen einen kurzen Lehrimperativ, alle 381 sichtbaren Prosaereignisse eine Atom- und Imperativspur, alle 116 Aussagen eine reduzierte flüssige Lesung und alle elf Records einen durchgehenden Werkstatttext.

{fully_composed} der 116 Aussagen bestehen vollständig aus produktiven Karten. Die übrigen {116 - fully_composed} Aussagen enthalten mindestens eine der 21 lokalen Ganzkarten-Vorkommen, behalten dafür aber ihre konkrete Bedeutung. {rephrased} Aussagen wurden gegenüber der bisherigen Ausgabe sprachlich neu gefasst; die übrigen waren bereits kurz genug. {line_spanning} Aussagen überschreiten mindestens eine physische Zeile und bleiben trotzdem genau eine Anweisung.

## Was sich sprachlich geändert hat

- `Sollmaß` wird konsequent **Vorgabewert**, `Folgemaß` **Folgewert**, `Portion` **Anteil**.
- Allgemeines `umsetzen` wird dort, wo `CHD` trägt, als **übertragen** gelesen.
- `AIR` heißt im atomaren Kern Wasserlauf; Zulauf, Beckenwasser oder Weiterleitung kommt erst aus der lokalen Karte.
- `CHEEY` bleibt freigegebener Wert; der praktische Besitzer konkretisiert ihn zum klaren Auszug.
- Kurze, lange und vollständige Grade stehen nie allein für ganze Arbeitsanweisungen.
- Die 19 Ganzkarten bleiben sichtbar: Wurzel, Zusatz, Gefäße, Auswringen, Nachseihen, Auftragen, Befestigen, Kaltstellen, Ausgießen, Verwahren, Anwenden, Füllen und einige lokale Zustände.

## Lesebeispiele

`H2-S002` ist jetzt eine fast reine Reihenfolge aus Folgeansatz, Fortsetzung, Vorgabewert und Ausgang. `B2-S005` führt Zielsetzung, Sammeln, Durchleiten, Vorgabewert, Bereitschaft, Wärme und Abführung zusammen. `B3-S032` bleibt die kompakteste Karte: Anteil übertragen, aktuellen Posten übertragen, kurzer Folgewert, Folgewert, kurze Folge schließen.

## Werkstattgebrauch

Der Lehrling liest zunächst die Kartenimperative einzeln. Danach verbindet er sie innerhalb der registrierten Aussagegrenze und setzt Bildbesitzer, Gefäß, Pflanzenteil oder Station ein. Eine Manuskriptzeile ist dabei nur Schreibraum; die Aussage darf über sie hinweggehen. Die durchgehenden Recordtexte sind die aktuelle kreative Übersetzung dieser zehn Seiten.
"""
    (OUT / "REDUCED_COMPLETE_EDITION_REPORT.md").write_text(report, encoding="utf-8")

    content_names = [
        "IMPERATIVE_173_CARD_DICTIONARY.tsv", "IMPERATIVE_381_EVENT_TRACE.tsv",
        "COMPLETE_116_RETRANSLATED_STATEMENTS.tsv", "ELEVEN_RECORD_REDUCED_SUMMARY.tsv",
        "ELEVEN_RECORD_COMPLETE_READING.md", "REDUCED_COMPLETE_EDITION_REPORT.md",
    ]
    summary = {
        "status": "BUILT",
        "master_cards": len(card_rows),
        "prose_events": len(event_rows),
        "statements": len(statement_rows),
        "records": len(record_rows),
        "composed_events": sum(row["composition_layer"] != "LEARNED_LOCAL_WHOLE" for row in event_rows),
        "local_whole_word_events": sum(row["composition_layer"] == "LEARNED_LOCAL_WHOLE" for row in event_rows),
        "fully_composed_statements": fully_composed,
        "mixed_statements": len(statement_rows) - fully_composed,
        "rephrased_statements": rephrased,
        "retained_concise_statements": len(statement_rows) - rephrased,
        "line_spanning_statements": line_spanning,
        "source_sha256": {
            "extended_173_dictionary": sha256(GRAMMAR / "COMPLETE_173_EXTENDED_CARD_DICTIONARY.tsv"),
            "extended_381_events": sha256(GRAMMAR / "PROSE_381_EXTENDED_COMPONENT_READER.tsv"),
            "source_116_statements": sha256(UNIQUE / "UNIQUE_116_STATEMENT_EDITION.tsv"),
        },
        "output_sha256": {name: sha256(OUT / name) for name in content_names},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

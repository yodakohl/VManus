#!/usr/bin/env python3
"""Build the R1 Biological second edition from the selected V60--V63 ledgers.

The builder deliberately keeps three layers apart:

* copied formal/card anchors;
* copied V61/V62/V63 discourse, register, and template structure;
* explicitly marked medical and apparatus exemplars.

No exemplar noun or action is written back into the card deck.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
ALLOWED_PAGES = ("f81v", "f82r", "f83r")
ALLOWED_RECORDS = ("B1", "B2", "B3", "B4", "B5", "B6")

P60 = ROOT / "experiments/yolo/sidequest_theory_candidates_v60"
P61 = ROOT / "experiments/yolo/sidequest_theory_candidates_v61"
P62 = ROOT / "experiments/yolo/sidequest_theory_candidates_v62"
P63 = ROOT / "experiments/yolo/sidequest_theory_candidates_v63"
P54 = ROOT / "experiments/yolo/sidequest_theory_candidates_v54"


RECORD_META = {
    "B1": {
        "title": "Gemeinsames Grundbad und erster Stationslauf",
        "owner": "B1:O01 = [EXEMPLAR] bebildertes Grundbad beziehungsweise die dort behandelte Gruppe",
        "medical_fill": "B1:Ixxx = Kräuterzusatz oder medizinische Badportion; B1:Txxx = Mischbecken, Lauf oder erste Badestelle",
        "apparatus_fill": "B1:Ixxx = Betriebscharge; B1:Txxx = Mischbecken, Leitung oder Übergabeanschluss",
        "picture": "Becken- und Laufzone; das Bild lizenziert einen lokalen Owner, aber weder Becken noch Bad als Kartenwort.",
        "genre": "Grundrezept und Ablaufzettel für ein gemeinsames medizinisches Bad",
        "rival": "Beschickungs-, Spül- und Übergabeplan eines kleinen Wasserwerks",
        "contradiction": "43/66 Ereignisse sind V63-UNPARSED_EXEMPLAR; Rücklauf, Öl, Becken und Badestelle stammen aus der Exemplarwelt.",
        "revision": "V54s einen Grundkreislauf ersetzt V65 durch 21 Aussagen und fünf Phasen; offene Übergabe und Registerwechsel bleiben sichtbar.",
        "workflow": "Owner B1:O01 setzen; Grundcharge anlegen; S001--S006 beschicken; S007--S011 temperieren/prüfen; S012--S016 nachspülen/absetzen; S017--S021 klären und offen übergeben.",
        "unsupported_med": "Grundbad|Behandlungsgruppe|Kräuterzusatz|Öl|Badestelle|Wasser",
        "unsupported_app": "Betriebscharge|Mischbecken|Leitung|Anschluss|Wasserwerk",
        "phases": [
            (1, 1, "P1_REINIGEN", "die markierte Badestelle vor dem Grundansatz spülen", "den ersten Anschluss des Hauptlaufs spülen"),
            (2, 6, "P2_GRUNDANSATZ", "den Heilzusatz dosieren, mit dem recordlokal vorigen Posten verbinden und im Grundbad mischen", "die Grundcharge dosieren, rückführen und in das Mischbecken leiten"),
            (7, 11, "P3_TEMPERIEREN", "eine Teilportion erwärmen, prüfen, spülen und zur Anwendung bereitstellen", "eine Teilcharge temperieren und die Arbeitsanschlüsse prüfen"),
            (12, 16, "P4_NACHSPUELEN", "mit warmem Wasser nachspülen, mischen, absetzen und erneut temperieren", "eine Reinigungscharge einlassen, mischen, absetzen und konditionieren"),
            (17, 21, "P5_KLAEREN_UEBERGEBEN", "die geklärte Badportion filtern und an die erste Behandlungsstelle übergeben", "die geklärte Charge filtern und an den nächsten Anschluss übergeben"),
        ],
    },
    "B2": {
        "title": "Einzelne temperierte Bad- oder Anwendungsstation",
        "owner": "B2:O01 = [EXEMPLAR] einzelne bebilderte Badperson beziehungsweise ihre Station",
        "medical_fill": "B2:Ixxx = temperierte Bad-, Wasch- oder Auflagenportion; B2:Txxx = Teilbad, Körperstelle, Öffnung oder Auffanggefäß",
        "apparatus_fill": "B2:Ixxx = Prüfcharge; B2:Txxx = Kammer, Filter, Anschluss oder Auffangbehälter",
        "picture": "Figuren und Formen stehen nebeneinander; Nähe liefert nur den Owner-Rahmen, keine Patientensemantik der Karten.",
        "genre": "individueller Bade- und Nachbehandlungszettel mit mehreren Gebrauchsmöglichkeiten",
        "rival": "Prüf- und Reinigungsfolge einer mehrkammerigen Beckenanlage",
        "contradiction": "S010→S011 bleibt UNRESOLVED; Trinken, Auflage, Körperziel und Tuch sind austauschbare medizinische Exemplare, keine Ankerwerte.",
        "revision": "V65 macht den f82r.3→4-Carry in B2-S005 explizit, hält die spätere Grenze verzweigt und behandelt S019--S022 als lokale Gebrauchsexemplare statt codierte Diagnosen.",
        "workflow": "Owner B2:O01 setzen; S001--S005 Station reinigen/beschicken; S006--S010 erste Anwendung; an S010→S011 beide Lesepfade merken; S011--S014 klären/ablassen; S015--S018 zweiten Gang; S019--S022 Varianten getrennt buchen.",
        "unsupported_med": "Badperson|Teilbad|Körperstelle|Waschung|Auflage|Trank|Öl|Wasser|Tuch",
        "unsupported_app": "Prüfcharge|Mehrkammerbecken|Filter|Anschluss|Auffangbehälter|Wasser",
        "phases": [
            (1, 5, "P1_STATION_VORBEREITEN", "Gefäß und Einzelbad reinigen, eine Portion einlassen, temperieren und durch Tuch klären", "Kammer und Lauf reinigen, eine Prüfcharge einlassen, temperieren und filtern"),
            (6, 10, "P2_ERSTE_ANWENDUNG", "die temperierte Portion an der gewählten Bad- oder Körperstelle anwenden und bis zum klaren Zustand führen", "die temperierte Charge am gewählten Anschluss fahren und den Endzustand prüfen"),
            (11, 14, "P3_KLAEREN_ABLASSEN", "eine neue Teilbadportion dosieren, vollständig eintauchen, ablassen und den Ablauf schließen", "eine neue Prüfcharge dosieren, die Kammer füllen, ablassen und den Ablauf schließen"),
            (15, 18, "P4_ZWEITER_GANG", "einen zweiten warmen Bade- oder Spülgang am Ziel ausführen", "einen zweiten Füll-, Spül- und Übergabegang ausführen"),
            (19, 22, "P5_GEBRAUCHSVARIANTEN", "Trank, Auflage, Bad und Mischabschluss als getrennte lokale Anwendungsvarianten buchen", "Entnahme, Filterbefestigung, Kammergang und Mischabschluss als parallele Prüfzellen buchen"),
        ],
    },
    "B3": {
        "title": "Langer Irrigations- und Mehrstationszyklus",
        "owner": "B3:O01 = [EXEMPLAR] bebilderte Behandlungsfolge beziehungsweise Mehrstationsanlage",
        "medical_fill": "B3:Ixxx = temperierte Bad- oder Irrigationsflüssigkeit; B3:Txxx = Badestelle, Körperziel, Öffnung, Becken oder Ablauf",
        "apparatus_fill": "B3:Ixxx = Umlaufcharge; B3:Txxx = Becken, Ventil, Öffnung, Filter oder Ablauf",
        "picture": "Figuren, Becken und offene Ausläufe bilden einen gemischten Owner-Rahmen; zwei Auslasslabels ohne lokale Figur halten den Apparaterivalen stark.",
        "genre": "wiederholbarer Bade-/Irrigationsgang mit Absetzen, Temperieren, Anwenden und Ablassen",
        "rival": "Mehrbecken-, Rücklauf- und Filterzyklus ohne Patientensemantik",
        "contradiction": "57/86 Ereignisse sind unparsed; der lange Ablauf ist ausführbar, doch keine Karte benennt Patient, Körperöffnung, Wasser, Becken oder Leitung.",
        "revision": "V54s langer Zyklus wird in 34 Aussagen mit drei RESUME-Kanten, paralleler Zelle und sechs Phasen zerlegt; ein geschlossener Kreislauf wird nicht vorausgesetzt.",
        "workflow": "Owner B3:O01 setzen; S001--S005 absetzen/ablassen; S006--S012 warmen Anwendungsgang führen; S013--S020 spülen/schalten; S021--S026 Station wechseln; S027--S030 lokal nachbehandeln; S031--S034 Schlussgang ausführen.",
        "unsupported_med": "Patient|Bad|Irrigation|Körperziel|Öffnung|Wasser|Tuch|Auflage",
        "unsupported_app": "Umlaufcharge|Mehrbeckenanlage|Ventil|Leitung|Filter|Rücklauf|Wasser",
        "phases": [
            (1, 5, "P1_ABSETZEN_ABLASSEN", "die medizinische Flüssigkeit absetzen, eine Portion eintauchen und verbrauchten Anteil ablassen", "die Umlaufcharge absetzen, die Kammer füllen und zum unteren Ablauf entleeren"),
            (6, 12, "P2_WARMER_ANWENDUNGSGANG", "warm nachfüllen, mischen, baden oder irrigieren, klären und am markierten Ziel anwenden", "warm nachfüllen, mischen, die Kammer fahren, klären und am markierten Anschluss einsetzen"),
            (13, 20, "P3_SPUELEN_SCHALTEN", "neue Portion ansetzen, die Stelle spülen, oberen und unteren Lauf schalten und erneut baden", "neue Charge ansetzen, Anschlüsse spülen, Zu- und Ablauf schalten und die Kammer fahren"),
            (21, 26, "P4_STATIONSWECHSEL", "gebrauchsfertige Portion bemessen, Ziel und Dauer wechseln, Rückstand halten und nächsten Gang vorbereiten", "freigegebene Charge bemessen, Anschluss und Takt wechseln, Rückstand halten und Nebenstation vorbereiten"),
            (27, 30, "P5_LOKALE_NACHANWENDUNG", "Auflage oder Waschung ausführen, lauwarm spülen und eine bemessene Portion klären", "Filterauflage befestigen, lauwarm spülen und eine bemessene Prüfcharge klären"),
            (31, 34, "P6_SCHLUSSGANG", "abschließend baden, mischen, klären, abziehen und Bereitschaft prüfen", "abschließend die Kammer fahren, mischen, klären, abziehen und den Endzustand prüfen"),
        ],
    },
    "B4": {
        "title": "Warmer Nachgang, Filterung und Neuansatz",
        "owner": "B4:O01 = [EXEMPLAR] eigene Nachbehandlungsstation im f83r-Bildfeld",
        "medical_fill": "B4:Ixxx = warme Wasch-, Auflagen- oder Spülportion; B4:Txxx = bezeichnete Stelle, Tuch, Gefäß oder unterer Lauf",
        "apparatus_fill": "B4:Ixxx = warme Reinigungscharge; B4:Txxx = Filtertuch, Anschluss, Gefäß oder Ablauf",
        "picture": "Der Ausschnitt kann Person und Station zugleich besitzen; der Owner bleibt daher anonym, und ein Körper wird nur im medizinischen Exemplar eingesetzt.",
        "genre": "warmer medizinischer Nachgang mit Auswahl, Filterung, Anwendung und Reinigung",
        "rival": "Filter-, Spül- und Neuansatzroutine eines Nebenlaufs",
        "contradiction": "32/47 Ereignisse sind unparsed; insbesondere Binden/Auflegen setzt einen Körper voraus, obwohl der sichtbare Owner auch eine Station sein kann.",
        "revision": "V65 isoliert in B4-S003 die lizenzierte Folge ANTEIL?→TEMPERIEREN?→ANWENDEN? und trennt sie von den exemplarischen Nomen; spätere START-Kanten eröffnen Reinigung und Neuansatz.",
        "workflow": "Owner B4:O01 neu setzen; S001--S004 warmen Nachgang; S005--S009 filtern/spülen; S010--S013 kochen, reinigen und ablassen; S014--S016 neuen Ansatz sofort verwenden, klären und nachfüllen.",
        "unsupported_med": "Patient|Körperstelle|Auflage|Waschung|Tuch|Wasser|Gefäß",
        "unsupported_app": "Reinigungscharge|Nebenlauf|Filtertuch|Anschluss|Ablauf|Wasser",
        "phases": [
            (1, 4, "P1_WARMER_NACHGANG", "eine warme Teilportion spülen, auswählen, temperieren und als lokale Waschung oder Auflage anwenden", "eine warme Teilcharge spülen, auswählen, temperieren und am Anschluss einsetzen"),
            (5, 9, "P2_FILTERN_SPUELEN", "Rückstand durch Tuch klären und die erste Stelle noch warm spülen", "Rückstand durch Filtertuch führen und den ersten Anschluss noch warm spülen"),
            (10, 13, "P3_REINIGEN_ABLASSEN", "eine Reinigungsportion sanft erhitzen, zweimal waschen und unten ablassen", "eine Reinigungscharge sanft erhitzen, den Lauf zweimal spülen und unten ablassen"),
            (14, 16, "P4_NEUANSETZEN", "frische Arbeitsflüssigkeit sofort anwenden, bis zur Klarheit führen, ablassen und warm nachfüllen", "frische Charge sofort in den Lauf geben, klären, ablassen und warm nachfüllen"),
        ],
    },
    "B5": {
        "title": "Kurzer Wärme- und Übergabenachtrag",
        "owner": "B5:O01 = [EXEMPLAR] neuer lokaler Nachtragsowner; keine Fortsetzung des B4-Owners",
        "medical_fill": "B5:Ixxx = Restportion dieses Nachtrags; B5:Txxx = nächste Behandlungsstation dieses Records",
        "apparatus_fill": "B5:Ixxx = Restcharge dieses Nachtrags; B5:Txxx = nächster Übergabeanschluss dieses Records",
        "picture": "Kurzer f83r-Nachtrag mit wenig direkter Bildbindung; die Recordgrenze erzwingt einen neuen anonymen Owner.",
        "genre": "Übergabezettel für eine noch warme medizinische Restportion",
        "rival": "technischer Restchargen- und Wartungsstummel",
        "contradiction": "7/11 Ereignisse sind unparsed, drei Felder offen; der interne VORBEZUG wird nur exemplarisch rekonstruiert.",
        "revision": "V54s fünf Feldschritte werden zu drei V61-Aussagen; S003 trägt drei Felder über zwei Zeilengrenzen. PREVIOUS darf niemals aus B4 übernommen werden.",
        "workflow": "Owner und aktive Restportion bei B5 neu anlegen; S001 abziehen; S002 einmal erwärmen; S003 Dauer, internes Voriges, Maß und Übergabe in einer fortgesetzten Klausel lesen.",
        "unsupported_med": "Restportion|Wärmefrist|Behandlungsstation",
        "unsupported_app": "Restcharge|Wartung|Übergabeanschluss",
        "phases": [
            (1, 1, "P1_ABZIEHEN", "die Restportion dieses Nachtrags abziehen", "die Restcharge dieses Nachtrags abziehen"),
            (2, 2, "P2_ERWAERMEN", "die Restportion einmal erwärmen", "die Restcharge einmal temperieren"),
            (3, 3, "P3_HALTEN_UEBERGEBEN", "für die lokale Frist halten, mit dem recordintern vorigen Posten bemessen und zur nächsten Behandlungsstation geben", "für den lokalen Takt halten, mit der recordintern vorigen Charge bemessen und zum nächsten Anschluss geben"),
        ],
    },
    "B6": {
        "title": "Kalter offener Filtergang",
        "owner": "B6:O01 = [EXEMPLAR] neuer lokaler Kaltgang-Owner; keine Fortsetzung von B5",
        "medical_fill": "B6:Ixxx = ungekochte kalte Waschportion; B6:Txxx = Tuch, erste Öffnung oder bezeichnete Behandlungsstelle",
        "apparatus_fill": "B6:Ixxx = kalte Vorlaufcharge; B6:Txxx = Filter, erste Öffnung oder Zielanschluss",
        "picture": "Eine Figur und eine offene Station können denselben kurzen Record rahmen; beide Felder bleiben formal offen.",
        "genre": "ungekochter kurzer Wasch- oder Irrigationsgang",
        "rival": "kalte Vorlauf-, Filter- und Übergabenotiz",
        "contradiction": "6/9 Ereignisse sind unparsed, beide Felder offen; Person, Kochen, Tuch und Ziel sind vollständig exemplarische Füllungen.",
        "revision": "V65 liest beide Felder und zwei loci als genau eine V61-Aussage, setzt alle Register am B6-Anfang neu und vermeidet jeden B5→B6-Carry.",
        "workflow": "Owner B6:O01 und kalte aktive Portion neu setzen; beide offenen Felder als eine fortgesetzte Aussage lesen; Maß ausführen; Filter und Ziel nur im Exemplar einsetzen; offen enden.",
        "unsupported_med": "Person|ungekochte Waschportion|Tuch|Körperstelle|Wasser",
        "unsupported_app": "Vorlaufcharge|Filter|Öffnung|Zielanschluss",
        "phases": [
            (1, 1, "P1_KALTER_FILTERGANG", "eine ungekochte bemessene Waschportion durch Tuch an die bezeichnete Behandlungsstelle führen", "eine kalte bemessene Vorlaufcharge durch den Filter zum Zielanschluss führen"),
        ],
    },
}


def read_header(path: Path) -> list[str]:
    with path.open(encoding="utf-8", newline="") as handle:
        return next(csv.reader(handle, delimiter="\t"))


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_bio_guarded(path: Path, selector: str = "page") -> list[dict[str, str]]:
    """Materialize only the three allowed pages through the guarded query."""
    columns = read_header(path)
    cmd = [
        str(ROOT / "vmanus-exp"),
        "query-tsv",
        str(path),
        "--selector",
        selector,
    ]
    for page in ALLOWED_PAGES:
        cmd.extend(("--allow", page))
    cmd.extend(("--columns", ",".join(columns), "--forbid-prefix", "f84"))
    result = subprocess.run(cmd, cwd=ROOT, check=True, capture_output=True, text=True)
    return list(csv.DictReader(io.StringIO(result.stdout), delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], columns: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in columns})


def phase_for(record: str, statement_ordinal: int) -> tuple[str, str, str]:
    for lo, hi, phase, medical, apparatus in RECORD_META[record]["phases"]:
        if lo <= statement_ordinal <= hi:
            return phase, medical, apparatus
    raise ValueError(f"no phase for {record} statement {statement_ordinal}")


def apparatus_transform(text: str) -> str:
    """Create a concrete apparatus exemplar without changing a card value."""
    replacements = [
        ("setze die Person an das Becken", "stelle die Prüfcharge am Beckenanschluss bereit"),
        ("bade oder tauche in der temperierten warmen Flüssigkeit", "führe die Prüfcharge durch das temperierte Becken"),
        ("tauche vollständig ein", "fülle die Kammer bis zur Markierung"),
        ("trinke den angegebenen Anteil", "entnimm den angegebenen Anteil am Prüfanschluss"),
        ("binde es auf die Stelle", "befestige das Filtertuch am markierten Anschluss"),
        ("wende es an der markierten Stelle an", "führe die Charge am markierten Anschluss ein"),
        ("Die aktive Portion verwenden", "die aktive Charge in den Arbeitslauf geben"),
        ("über der örtlich bezeichneten Stelle", "am örtlich bezeichneten Anschluss"),
        ("an der bezeichneten Stelle", "am bezeichneten Anschluss"),
        ("die betroffene Stelle", "der markierte Anschluss"),
        ("spüle die bezeichnete Stelle", "spüle den bezeichneten Anschluss"),
        ("wasche zweimal", "spüle den Lauf zweimal"),
        ("wasche einmal", "spüle den Lauf einmal"),
        ("das bereitete Öl", "das bereitete Arbeitsmedium"),
        ("der eingetauchte Teil", "die gefüllte Kammer"),
        ("die erste Öffnung", "der erste Anschluss"),
        ("die zweite Öffnung", "der zweite Anschluss"),
        ("bezeichnete Zielstelle", "bezeichneten Zielanschluss"),
        ("Zubereitung", "Charge"),
        ("Mischung", "Charge"),
        ("aktive Portion", "aktive Charge"),
        ("Person", "Prüfcharge"),
    ]
    transformed = text
    for old, new in replacements:
        transformed = transformed.replace(old, new)
    return transformed


def marker(layer: str, phase_text: str, local_text: str) -> str:
    return f"[EXEMPLAR_{layer}; KEIN_KARTENWERT] {phase_text}. Einzelposition: {local_text}"


def graph_operation(boundary: str) -> str:
    return {
        "RECORD_START": "RESET_ALL;INTRODUCE_OWNER_ACTIVE_AS_NEEDED;EXECUTE_TARGET_NODE",
        "WITHIN_LOCUS_FIELD_BOUNDARY": "KEEP_RECORD;EXECUTE_NEXT_CLAUSE_CELL",
        "CONTINUE_SAME_CLAUSE": "KEEP_OWNER_ACTIVE_TARGET_PREVIOUS;APPEND_SAME_CLAUSE",
        "RESUME_ACTIVE_ITEM": "KEEP_OWNER;RESUME_ACTIVE;UPDATE_TARGET_AS_LOGGED",
        "NEXT_PARALLEL_CELL": "KEEP_OWNER;SAVE_PREVIOUS;INTRODUCE_PARALLEL_ACTIVE;RESET_TARGET",
        "START_NEW_CLAUSE": "KEEP_OWNER;SAVE_PREVIOUS;INTRODUCE_NEW_ACTIVE;RESET_TARGET",
        "UNRESOLVED": "BRANCH_SELECTED_CONTINUE_OR_ALTERNATIVE_NEW_CELL;PRESERVE_BOTH_IN_AUDIT",
        "RECORD_END": "COMMIT_VISIBLE_TERMINALS;KEEP_OPEN_FIELDS_OPEN;RESET_BEFORE_NEXT_RECORD",
    }.get(boundary, f"EXECUTE_BOUNDARY({boundary})")


def main() -> None:
    event60 = read_bio_guarded(P60 / "V60_SELECTED_381_EVENT_LEDGER.tsv")
    statements61 = read_bio_guarded(P61 / "V61_SELECTED_116_SOURCE_STATEMENTS.tsv")
    records61 = read_bio_guarded(P61 / "V61_SELECTED_11_RECORD_CONTINUATIONS.tsv")
    transitions62 = read_bio_guarded(P62 / "V62_SELECTED_116_REGISTER_TRANSITIONS.tsv")
    event63 = read_bio_guarded(P63 / "V63_SELECTED_381_EVENT_TEMPLATE_LEDGER.tsv")
    field63 = read_bio_guarded(P63 / "V63_SELECTED_135_FIELD_SLOT_PARSE.tsv")
    statement63 = read_bio_guarded(P63 / "V63_SELECTED_116_STATEMENT_SLOT_PARSE.tsv")
    records54 = read_bio_guarded(P54 / "V54_SELECTED_SIX_BIO_RECORDS.tsv", selector="folio")
    deck = read_tsv(P60 / "V60_SELECTED_EXACT_CARD_DECISIONS.tsv")

    assert len(event60) == len(event63) == 281
    assert len(field63) == 115
    assert len(statements61) == len(transitions62) == len(statement63) == 97
    assert len(records61) == len(records54) == 6

    event63_by_id = {row["event_serial"]: row for row in event63}
    statement61_by_id = {row["statement_id"]: row for row in statements61}
    transition_by_id = {row["statement_id"]: row for row in transitions62}
    statement63_by_id = {row["statement_id"]: row for row in statement63}
    record61_by_id = {row["record_unit_id"]: row for row in records61}
    record54_by_id = {row["record_id"]: row for row in records54}

    statements_by_record: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in statements61:
        statements_by_record[row["record_unit_id"]].append(row)
    for rows in statements_by_record.values():
        rows.sort(key=lambda r: int(r["statement_ordinal_in_record"]))

    fields_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in field63:
        fields_by_statement[row["statement_id"]].append(row)
    for rows in fields_by_statement.values():
        rows.sort(key=lambda r: int(r["field_id"][1:]))

    events_by_field: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in event60:
        events_by_field[row["field_id"]].append(row)
    for rows in events_by_field.values():
        rows.sort(key=lambda r: int(r["event_serial"]))

    event_rows: list[dict[str, object]] = []
    for source in sorted(event60, key=lambda r: int(r["event_serial"])):
        parsed = event63_by_id[source["event_serial"]]
        statement = statement61_by_id[parsed["statement_id"]]
        ordinal = int(statement["statement_ordinal_in_record"])
        phase, medical_focus, apparatus_focus = phase_for(source["record_unit_id"], ordinal)
        medical_local = source["LOCAL_IATROMEDICAL_EXPANSION"].strip() or "lokalen Arbeitsschritt ausführen"
        apparatus_local = apparatus_transform(medical_local)
        semantic_accounting = (
            "EXEMPLAR_ONLY_COMPLETE"
            if parsed["event_template"] == "EXEMPLAR_ONLY"
            else "LICENSED_ANCHOR_PLUS_EXEMPLAR_FILL"
        )
        event_rows.append(
            {
                "event_serial": source["event_serial"],
                "page": source["page"],
                "locus": source["locus"],
                "record_unit_id": source["record_unit_id"],
                "field_id": source["field_id"],
                "statement_id": parsed["statement_id"],
                "event_index_in_record": source["event_index_in_record"],
                "surface_display_only": source["surface"],
                "joint_tuple_id": source["joint_tuple_id"],
                "formal_value": source["FORMAL_VALUE"],
                "terminal_status": source["terminal_status"],
                "strict_control_prompt": source["strict_control_prompt"],
                "v60_exact_mnemonic": source["ATOMIC_OR_WHOLE_CARD_MNEMONIC"],
                "v63_event_template": parsed["event_template"],
                "v63_event_parse_status": parsed["event_parse_status"],
                "trigger_origin": parsed["trigger_origin"],
                "required_registers": parsed["required_registers"],
                "symbolic_register_effect": parsed["symbolic_register_effect"],
                "process_phase": phase,
                "medical_exemplar_expansion": marker("MED", medical_focus, medical_local),
                "apparative_exemplar_expansion": marker("APPARAT", apparatus_focus, apparatus_local),
                "semantic_accounting": semantic_accounting,
                "unknown_exemplar_status": source["UNKNOWN_EXEMPLAR_STATUS"],
                "layer_contract": "EXACT_TUPLE_ATOMIC;SURFACE_COMPONENTS_PAGE_HOST_NONSEMANTIC;EXEMPLARS_NO_DICTIONARY_FEEDBACK",
                "source_lineage": "V60_SELECTED_EVENT+V63_SELECTED_EVENT_TEMPLATE+V65_R1_MARKED_EXEMPLAR",
            }
        )

    event_columns = list(event_rows[0])
    write_tsv(OUT / "V65_R1_281_EVENT_INTERLINEAR.tsv", event_rows, event_columns)

    field_rows: list[dict[str, object]] = []
    for field in sorted(field63, key=lambda r: int(r["field_id"][1:])):
        statement = statement61_by_id[field["statement_id"]]
        ordinal = int(statement["statement_ordinal_in_record"])
        phase, medical_focus, apparatus_focus = phase_for(field["record_unit_id"], ordinal)
        source_events = events_by_field[field["field_id"]]
        medical_units = [row["LOCAL_IATROMEDICAL_EXPANSION"].strip() or "lokalen Arbeitsschritt ausführen" for row in source_events]
        apparatus_units = [apparatus_transform(unit) for unit in medical_units]
        field_rows.append(
            {
                "field_id": field["field_id"],
                "record_unit_id": field["record_unit_id"],
                "page": field["page"],
                "locus": field["locus"],
                "statement_id": field["statement_id"],
                "field_position_in_statement": field["field_position_in_statement"],
                "event_count": field["event_count"],
                "event_serials": field["event_serials"],
                "primary_template": field["primary_template"],
                "licensed_primitive_sequence": field["licensed_primitive_sequence"],
                "v63_parse_status": field["parse_status"],
                "v63_parse_reason": field["parse_reason"],
                "recognized_event_count": field["recognized_event_count"],
                "exemplar_only_event_count": field["exemplar_only_event_count"],
                "process_phase": phase,
                "medical_field_default": marker("MED", medical_focus, " ; ".join(medical_units)),
                "apparative_field_default": marker("APPARAT", apparatus_focus, " ; ".join(apparatus_units)),
                "register_pre_state_statement_envelope": field["register_pre_state_statement_envelope"],
                "register_update_trace": field["register_update_trace"],
                "register_post_state_statement_envelope": field["register_post_state_statement_envelope"],
                "roundtrip_status": field["roundtrip_status"],
                "exemplar_contract": "LOCAL_COMPLETE;ALL_UNSUPPORTED_NOUNS_AND_ACTIONS_MARKED;NO_CARD_FEEDBACK",
                "source_lineage": "V63_SELECTED_FIELD+V60_SELECTED_EVENT_EXPANSIONS+V65_R1",
            }
        )

    field_columns = list(field_rows[0])
    write_tsv(OUT / "V65_R1_115_FIELD_EDITION.tsv", field_rows, field_columns)

    statement_rows: list[dict[str, object]] = []
    for source in sorted(
        statements61,
        key=lambda r: (ALLOWED_RECORDS.index(r["record_unit_id"]), int(r["statement_ordinal_in_record"])),
    ):
        transition = transition_by_id[source["statement_id"]]
        parsed = statement63_by_id[source["statement_id"]]
        ordinal = int(source["statement_ordinal_in_record"])
        phase, medical_focus, apparatus_focus = phase_for(source["record_unit_id"], ordinal)
        medical_text = marker("MED", medical_focus, source["concrete_workshop_reading"])
        apparatus_text = marker("APPARAT", apparatus_focus, apparatus_transform(source["concrete_workshop_reading"]))
        reflow_highlight = ""
        if source["statement_id"] == "B2-S005":
            reflow_highlight = "f82r.3→f82r.4=CONTINUE_SAME_CLAUSE; qokaiin-Wiederholung ist Carry-Evidenz, keine neue Bedeutung"
        elif source["internal_cross_line_boundaries"]:
            reflow_highlight = f"V61_INTERNAL_REFLOW={source['internal_cross_line_boundaries']}"
        statement_rows.append(
            {
                "statement_id": source["statement_id"],
                "record_unit_id": source["record_unit_id"],
                "page": source["page"],
                "statement_ordinal_in_record": source["statement_ordinal_in_record"],
                "start_locus": source["start_locus"],
                "start_field": source["start_field"],
                "end_locus": source["end_locus"],
                "end_field": source["end_field"],
                "constituent_loci": source["constituent_loci"],
                "constituent_fields": source["constituent_fields"],
                "physical_line_count": source["physical_line_count"],
                "event_count": source["event_count"],
                "event_serials": source["event_serials"],
                "closure_sequence": source["closure_sequence"],
                "entry_boundary_class": source["entry_boundary_class"],
                "exit_boundary_class": source["exit_boundary_class"],
                "internal_cross_line_boundaries": source["internal_cross_line_boundaries"],
                "reflow_highlight": reflow_highlight,
                "selected_short_card_skeleton": source["selected_short_card_skeleton"],
                "primary_template": parsed["primary_template"],
                "licensed_primitive_sequence": parsed["licensed_primitive_sequence"],
                "v63_parse_status": parsed["parse_status"],
                "v63_parse_reason": parsed["parse_reason"],
                "recognized_event_count": parsed["recognized_event_count"],
                "exemplar_only_event_count": parsed["exemplar_only_event_count"],
                "process_phase": phase,
                "register_pre_state": transition["pre_state"],
                "owner_operation": transition["owner_operation"],
                "active_operation": transition["active_item_preparation_operation"],
                "target_operation": transition["target_station_operation"],
                "previous_operation": transition["previous_item_operation"],
                "register_operation_trace": transition["operation_trace"],
                "register_post_state": transition["post_state"],
                "irreducible_ambiguity_codes": transition["irreducible_ambiguity_codes"],
                "medical_default_clause": medical_text,
                "apparative_default_clause": apparatus_text,
                "strongest_alternative": source["strongest_alternative"],
                "apprentice_reading_rule": source["apprentice_reading_rule"],
                "layer_contract": "V61_REFLOW+V62_ANONYMOUS_REGISTERS+V63_STATUS;EXEMPLARS_NO_DICTIONARY_FEEDBACK",
                "source_lineage": "V61_SELECTED_STATEMENT+V62_SELECTED_TRANSITION+V63_SELECTED_STATEMENT_PARSE+V65_R1",
            }
        )

    statement_columns = list(statement_rows[0])
    write_tsv(OUT / "V65_R1_97_STATEMENT_EDITION.tsv", statement_rows, statement_columns)

    statement_output_by_record: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in statement_rows:
        statement_output_by_record[str(row["record_unit_id"])].append(row)

    graph_rows: list[dict[str, object]] = []
    for record in ALLOWED_RECORDS:
        rows = statement_output_by_record[record]
        for index, row in enumerate(rows):
            from_node = "START" if index == 0 else str(rows[index - 1]["statement_id"])
            boundary = str(row["entry_boundary_class"])
            graph_rows.append(
                {
                    "record_unit_id": record,
                    "edge_ordinal": index + 1,
                    "from_node": from_node,
                    "to_node": row["statement_id"],
                    "boundary_class": boundary,
                    "selected_graph_operation": graph_operation(boundary),
                    "target_statement_phase": row["process_phase"],
                    "target_statement_parse_status": row["v63_parse_status"],
                    "pre_state": row["register_pre_state"],
                    "post_state": row["register_post_state"],
                    "medical_execution": row["medical_default_clause"],
                    "apparative_execution": row["apparative_default_clause"],
                    "branch_or_alternative": row["strongest_alternative"],
                    "execution_contract": "SELECTED_EDGE_EXECUTABLE;UNRESOLVED_EDGE_RETAINS_EXPLICIT_ALTERNATIVE",
                }
            )
        graph_rows.append(
            {
                "record_unit_id": record,
                "edge_ordinal": len(rows) + 1,
                "from_node": rows[-1]["statement_id"],
                "to_node": "END",
                "boundary_class": "RECORD_END",
                "selected_graph_operation": graph_operation("RECORD_END"),
                "target_statement_phase": "END",
                "target_statement_parse_status": "N/A",
                "pre_state": rows[-1]["register_post_state"],
                "post_state": "RESET_BEFORE_NEXT_RECORD",
                "medical_execution": "[EXEMPLAR_MED; KEIN_KARTENWERT] Record mit sichtbaren offenen Feldern offen beenden.",
                "apparative_execution": "[EXEMPLAR_APPARAT; KEIN_KARTENWERT] Record mit sichtbaren offenen Feldern offen beenden.",
                "branch_or_alternative": record61_by_id[record]["strongest_segmentation_pressure"],
                "execution_contract": "RECORD_LOCAL_REGISTERS_NEVER_CROSS_END",
            }
        )

    graph_columns = list(graph_rows[0])
    write_tsv(OUT / "V65_R1_PROCESS_GRAPH_EDGES.tsv", graph_rows, graph_columns)

    event_counts = Counter(row["record_unit_id"] for row in event60)
    field_counts = Counter(row["record_unit_id"] for row in field63)
    statement_counts = Counter(row["record_unit_id"] for row in statements61)
    event_status_counts: dict[str, Counter[str]] = defaultdict(Counter)
    field_status_counts: dict[str, Counter[str]] = defaultdict(Counter)
    statement_status_counts: dict[str, Counter[str]] = defaultdict(Counter)
    for row in event63:
        event_status_counts[row["record_unit_id"]][row["event_parse_status"]] += 1
    for row in field63:
        field_status_counts[row["record_unit_id"]][row["parse_status"]] += 1
    for row in statement63:
        statement_status_counts[row["record_unit_id"]][row["parse_status"]] += 1

    record_rows: list[dict[str, object]] = []
    for record in ALLOWED_RECORDS:
        meta = RECORD_META[record]
        rows = statement_output_by_record[record]
        phase_graph = "START → " + " → ".join(
            f"{phase}[S{lo:03d}–S{hi:03d}]" if lo != hi else f"{phase}[S{lo:03d}]"
            for lo, hi, phase, _, _ in meta["phases"]
        ) + " → END"
        medical_full = " ".join(f"[{row['statement_id']}] {row['medical_default_clause']}" for row in rows)
        apparatus_full = " ".join(f"[{row['statement_id']}] {row['apparative_default_clause']}" for row in rows)
        first_transition = transition_by_id[str(rows[0]["statement_id"])]
        last_transition = transition_by_id[str(rows[-1]["statement_id"])]
        r61 = record61_by_id[record]
        r54 = record54_by_id[record]
        record_rows.append(
            {
                "record_unit_id": record,
                "page": r61["page"],
                "title": meta["title"],
                "picture_owner_description": meta["picture"],
                "proposed_article_genre": meta["genre"],
                "field_count": field_counts[record],
                "event_count": event_counts[record],
                "statement_count": statement_counts[record],
                "open_fields": r61["open_fields"],
                "terminal_fields": r61["terminal_fields"],
                "event_parse_counts": "|".join(f"{key}:{value}" for key, value in sorted(event_status_counts[record].items())),
                "field_parse_counts": "|".join(f"{key}:{value}" for key, value in sorted(field_status_counts[record].items())),
                "statement_parse_counts": "|".join(f"{key}:{value}" for key, value in sorted(statement_status_counts[record].items())),
                "v60_short_card_skeleton": r61["selected_short_card_skeleton"],
                "record_local_owner_fill": meta["owner"],
                "medical_register_fill": f"[EXEMPLAR_MED; KEIN_KARTENWERT] {meta['medical_fill']}",
                "apparative_register_fill": f"[EXEMPLAR_APPARAT; KEIN_KARTENWERT] {meta['apparatus_fill']}",
                "initial_register_state": first_transition["pre_state"],
                "final_register_state": last_transition["post_state"],
                "executable_process_graph": phase_graph,
                "complete_medical_default_text": medical_full,
                "complete_apparative_rival_text": apparatus_full,
                "apprentice_workflow": meta["workflow"],
                "strongest_contradiction": meta["contradiction"],
                "revision_against_v54": meta["revision"],
                "v54_baseline_text": r54["complete_working_translation_German"],
                "strongest_nonmedical_rival": meta["rival"],
                "unsupported_medical_nouns": meta["unsupported_med"],
                "unsupported_apparative_nouns": meta["unsupported_app"],
                "teaching_contract": "Owner einmal setzen; V61-Reflow ausführen; V62-Register nur recordlokal tragen; V63 UNIQUE/AMBIGUOUS/UNPARSED anzeigen; CLOSE nicht sprechen; Exemplar nie ins Deck zurückschreiben.",
                "edition_status": "COMPLETE_CREATIVE_SECOND_EDITION;NOT_DECRYPTION;DICTIONARY_DELTA_ZERO",
            }
        )

    record_columns = list(record_rows[0])
    write_tsv(OUT / "V65_R1_6_RECORD_EDITION.tsv", record_rows, record_columns)

    deck_rows: list[dict[str, object]] = []
    for row in deck:
        deck_rows.append(
            {
                "card": row["card"],
                "joint_tuple_id": row["joint_tuple_id"],
                "v60_selected_short_mnemonic": row["selected_short_mnemonic"],
                "v65_selected_short_mnemonic": row["selected_short_mnemonic"],
                "source_class": row["source_class"],
                "binding": row["binding"],
                "v65_action": "UNCHANGED",
            }
        )
    write_tsv(OUT / "V65_R1_V60_DECK_FREEZE.tsv", deck_rows, list(deck_rows[0]))

    write_tsv(
        OUT / "V65_R1_DICTIONARY_DELTA.tsv",
        [],
        ["joint_tuple_id", "v60_value", "v65_value", "decision", "reason"],
    )

    deck_hash = hashlib.sha256(
        "\n".join(f"{row['joint_tuple_id']}\t{row['selected_short_mnemonic']}" for row in deck).encode("utf-8")
    ).hexdigest()
    build_summary = {
        "status": "BUILT",
        "allowed_pages": list(ALLOWED_PAGES),
        "records": len(record_rows),
        "fields": len(field_rows),
        "events": len(event_rows),
        "statements": len(statement_rows),
        "process_graph_edges": len(graph_rows),
        "v60_deck_rows": len(deck_rows),
        "dictionary_delta_rows": 0,
        "event_parse_counts": dict(Counter(row["event_parse_status"] for row in event63)),
        "field_parse_counts": dict(Counter(row["parse_status"] for row in field63)),
        "statement_parse_counts": dict(Counter(row["parse_status"] for row in statement63)),
        "v60_deck_sha256": deck_hash,
        "exemplar_contract": "ALL_CREATIVE_NOUNS_AND_ACTIONS_MARKED;NO_DICTIONARY_FEEDBACK",
    }
    (OUT / "V65_R1_BUILD_SUMMARY.json").write_text(
        json.dumps(build_summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()

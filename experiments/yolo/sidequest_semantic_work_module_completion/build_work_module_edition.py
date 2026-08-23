#!/usr/bin/env python3
"""Group the 116 creative ten-page instructions into practical work modules."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
BASE = HERE.parent / "sidequest_semantic_handoff_resolution_completion"
OWNER_BASE = HERE.parent / "sidequest_theory_candidates_v71"

DICT_IN = BASE / "SELECTED_173_HANDOFF_DICTIONARY.tsv"
EVENT_IN = BASE / "SELECTED_381_HANDOFF_INTERLINEAR.tsv"
SENTENCE_IN = BASE / "SELECTED_116_HANDOFF_SENTENCES.tsv"
HANDOFF_IN = BASE / "HANDOFF_REGISTER.tsv"
OWNER_IN = OWNER_BASE / "V71_SELECTED_OWNER_LEDGER.tsv"

DICT_OUT = HERE / "SELECTED_173_WORK_MODULE_DICTIONARY.tsv"
EVENT_OUT = HERE / "SELECTED_381_WORK_MODULE_INTERLINEAR.tsv"
SENTENCE_OUT = HERE / "SELECTED_116_WORK_MODULE_SENTENCES.tsv"
RECORD_OUT = HERE / "SELECTED_11_WORK_MODULE_RECORDS.md"
MODULE_OUT = HERE / "WORK_MODULE_REGISTER.tsv"
EDGE_OUT = HERE / "STATEMENT_RELATION_REGISTER.tsv"
CHECK_OUT = HERE / "BUILD_CHECK.json"
SUMMARY_OUT = HERE / "BUILD_SUMMARY.json"

RECORD_ORDER = ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"]
ALLOWED_PAGES = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def statement_ids(record: str, first: int, last: int) -> list[str]:
    return [f"{record}-S{number:03d}" for number in range(first, last + 1)]


TYPE_RULES = {
    "CONTINUOUS_MATERIAL_CHAIN": "Chronologisch lesen: jede innere Kante ist eine ausdrücklich offene Material- oder Reserveübergabe.",
    "SELF_CONTAINED_ROUTINE": "Als eigenständige Routine lesen; die Nachbarzelle ist nicht automatisch ihr nächster Arbeitsschritt.",
    "LOCAL_STATION_VARIANTS": "Als parallele Stationsvarianten oder einzelne Checklistenposten lesen; die Schreibreihenfolge allein erzeugt keine Chronologie.",
    "LOCAL_ROUTINE_WITH_HANDOFF": "Nur die ausdrücklich offene Kante ist chronologisch; die übrigen Einträge sind lokale Varianten oder Kontrollposten.",
    "CROSS_STATION_HANDOFF": "Nur die ausdrücklich offene Kante chronologisch lesen; dabei keine unsichtbare Rohrverbindung zwischen den Bildstationen ergänzen.",
    "OWNER_BREAK_COMPOSITE": "Eine Textanweisung berührt zwei Bildbesitzer; ohne sichtbare Verbindung bleibt der Übergang ein redaktioneller Sprung.",
}


def module(
    module_id: str,
    record: str,
    first: int,
    last: int,
    module_type: str,
    title: str,
    reading: str,
    visible_basis: str,
    rival: str,
) -> dict[str, object]:
    return {
        "module_id": module_id,
        "record_unit_id": record,
        "statement_ids": statement_ids(record, first, last),
        "module_type": module_type,
        "workshop_title_de": title,
        "workshop_module_reading_de": reading,
        "chronology_rule_de": TYPE_RULES[module_type],
        "visible_basis_de": visible_basis,
        "strongest_rival_de": rival,
    }


MODULES = [
    module("WM01", "H1", 1, 2, "CONTINUOUS_MATERIAL_CHAIN", "Wurzelauszug", "Wurzel entnehmen, zerkleinern, mit Wasser ausziehen, bemessen, anwärmen und bereit halten.", "Eine offene Übergabe trägt den bemessenen Auszug in die zweite Anweisung.", "Zwei selbständige Verwendungsnotizen zur abgebildeten Pflanze."),
    module("WM02", "H2", 1, 3, "CONTINUOUS_MATERIAL_CHAIN", "Pflanzenansatz zur Folgeportion", "Pflanzenansatz auspressen, bemessen, als Folgeansatz weiterführen und im Topf bis zur Weichstufe bearbeiten.", "Zwei aufeinanderfolgende offene Übergaben benennen denselben fortgeführten Ansatz.", "Drei Rezeptvarianten, die nur denselben Pflanzenbesitzer teilen."),
    module("WM03", "H3", 1, 1, "SELF_CONTAINED_ROUTINE", "Klarauszug aus Blütenkraut", "Blütenkraut auskochen, auswringen, stehen lassen, nachseihen, Klarflüssigkeit nehmen und abkühlen.", "Die Anweisung schließt ihre eigene Zelle vollständig.", "Eine bloße Liste verschiedener Verwendungen."),
    module("WM04", "H3", 2, 4, "CONTINUOUS_MATERIAL_CHAIN", "Blütenreserve", "Blütenreserve zurücklegen, daraus einen Trank bemessen und die restliche Reserve als Folgeposten bereit halten.", "Zwei offene Reserveübergaben halten ausdrücklich denselben Nebenposten aktiv.", "Drei unabhängige Blütennotizen."),
    module("WM05", "H4", 1, 1, "SELF_CONTAINED_ROUTINE", "Abgekühlte Portion", "Sollmaß einstellen, eine Portion nehmen und abkühlen.", "Eigene geschlossene Zelle am Pflanzenbesitzer.", "Ein kurzer Eigenschaftseintrag statt Handlung."),
    module("WM06", "H4", 2, 3, "CONTINUOUS_MATERIAL_CHAIN", "Verwahrter Ansatz", "Ansatz nach Sollmaß umsetzen und verwahren; daraus den Auszug entnehmen, länger wärmen und abschließen.", "Die offene erste Zelle liefert ausdrücklich den verwahrten Ansatz.", "Zwei getrennte Zubereitungsvarianten."),
    module("WM07", "H4", 4, 4, "SELF_CONTAINED_ROUTINE", "Ansatzportion am Ziel", "Eine Ansatzportion nach Sollmaß zum Ziel geben, anwärmen und halten.", "Recordfinale selbständige Arbeitszelle.", "Eine alternative Dosisangabe ohne zeitliche Stellung."),
    module("WM08", "H5", 1, 2, "CONTINUOUS_MATERIAL_CHAIN", "Zutatenansatz auftragen", "Zutatenansatz bereiten und bemessen, die Stelle waschen und den vorbereiteten Ansatz dort auftragen.", "Die offene Zubereitung wird in der nächsten Zelle als Anwendungsposten übernommen.", "Zubereitung und Anwendung gehören zu zwei getrennten Verwendungsfällen."),
    module("WM09", "H5", 3, 6, "CONTINUOUS_MATERIAL_CHAIN", "Stängel zum Anwendungsauszug", "Stängel zerreiben, Auszug zugeben, seihen, den Anwendungsauszug gewinnen und die nächste Gabe vormerken.", "Drei offene Materialübergaben bilden eine geschlossene Herstellungs- und Gebrauchskette.", "Vier nebeneinander kopierte Pflanzenteilnotizen."),

    module("WM10", "B1", 1, 5, "LOCAL_STATION_VARIANTS", "Grundprogramme des gemeinsamen Pools", "Fünf abgeschlossene Einstell-, Misch-, Wärme- und Absetzprogramme desselben zweireihigen Poolfelds.", "Gleicher Bildbesitzer, aber zwischen den Zellen keine offene Übergabe.", "Ein einziger langer Badeablauf."),
    module("WM11", "B1", 6, 7, "CONTINUOUS_MATERIAL_CHAIN", "Abgekühlte Badmischung", "Badzusatz und Portion durchleiten, abkühlen und die erhaltene Mischung umsetzen.", "Die erste Zelle bleibt offen und benennt die abgekühlte Badmischung der zweiten.", "Zwei unabhängige Poolprogramme."),
    module("WM12", "B1", 8, 10, "LOCAL_STATION_VARIANTS", "Kurze Haltevarianten", "Drei kurze Varianten: fortführen und absetzen, kurz ansetzen oder den nächsten Posten kurz ansetzen.", "Derselbe Poolbesitzer; jede Zelle schließt separat.", "Drei aufeinanderfolgende Phasen eines einzigen Postens."),
    module("WM13", "B1", 11, 13, "LOCAL_ROUTINE_WITH_HANDOFF", "Durchlauf und Waschgang", "Einen Waschposten durchleiten, damit den Waschgang beginnen; daneben steht eine selbständige Wiederholungswäsche.", "Nur S011→S012 ist offen; S013 ist eine weitere abgeschlossene Waschvariante.", "Alle drei Sätze bilden zwingend einen dreifachen Waschgang."),
    module("WM14", "B1", 14, 17, "LOCAL_ROUTINE_WITH_HANDOFF", "Auslass und Auffanggefäß", "Arbeitsflüssigkeit am Auslass abführen und im Gefäß auffangen; weitere Zellen geben Halte- und Hahnvarianten.", "Nur S014→S015 trägt Material; S016 und S017 schließen eigenständig.", "Ein gezeichneter Kreislauf zwischen Auslass, Gefäß und Hahn."),
    module("WM15", "B1", 18, 21, "LOCAL_STATION_VARIANTS", "Sammeln, Seihen und Zielposten", "Vier Abschlussvarianten des Poolfelds: sammeln/einreiben, absetzen, wärmen/seihen und einen Folgeposten zum Ziel führen.", "Gleicher Besitzer, vier separat geschlossene oder recordfinale Einträge.", "Die letzten vier Phasen einer einzigen Behandlung."),

    module("WM16", "B2", 1, 5, "LOCAL_STATION_VARIANTS", "Obere Paarbecken", "Fünf Varianten für Umsetzen, Portionieren, Durchleiten, Seihen und beidseitiges Angleichen an den oberen Becken.", "Alle Felder gehören zum oberen Paarbeckenbesitzer; keine innere Zelle bleibt offen.", "Eine lineare Maschinenstrecke durch beide Becken."),
    module("WM17", "B2", 6, 7, "CROSS_STATION_HANDOFF", "Überlaufposten zur Mittelstation", "Einen langen Folgeposten am Überlauf offen weiterführen und an der nächsten Station mit Frischwasser ergänzen.", "Explizite Materialübergabe, aber sichtbarer Besitzerwechsel vom oberen Becken zum linken Mittelgerät.", "Eine reale verdeckte Rohrleitung zwischen beiden Zeichnungen."),
    module("WM18", "B2", 8, 9, "LOCAL_STATION_VARIANTS", "Absetzvarianten am linken Mittelgerät", "Folgemaß einstellen und absetzen oder den vorigen Posten weiter absetzen.", "Gleicher Besitzer; beide Zellen schließen separat.", "Zwingend erster und zweiter Absetzschritt."),
    module("WM19", "B2", 10, 11, "CROSS_STATION_HANDOFF", "Klarflüssigkeit zur unklaren Mittelstation", "Klarflüssigkeit an der Düse gewinnen und an der unklaren Nachbarstation portionieren und halten.", "Explizite Materialübergabe trifft auf einen ungelösten Bildbesitzer ohne sichtbare Verbindung.", "Ein durchgezeichneter Klarlauf."),
    module("WM20", "B2", 12, 12, "OWNER_BREAK_COMPOSITE", "Sprung zum unteren Mehrfigurenpool", "Klarflüssigkeit abziehen und an einer Nassstelle nach Sollmaß vollständig ausführen.", "Die eine Textanweisung überspannt die ungelöste Mittelstation und den unteren grünen Pool.", "Ein ununterbrochener sichtbarer Stoffweg."),
    module("WM21", "B2", 13, 15, "CROSS_STATION_HANDOFF", "Bodenablauf und Randstation", "Am unteren Pool abführen, den Bodenablauf schließen und diesen Gerätezustand in den Spülgang der Randstation übernehmen.", "Die offene Zustandsübergabe kreuzt vom unteren Pool zu den Randstationen; sie überträgt eine Stellung, keinen Stoff.", "Eine sichtbare mechanische Kupplung beider Stationen."),
    module("WM22", "B2", 16, 22, "LOCAL_STATION_VARIANTS", "Programme der unteren Randstationen", "Sieben abgeschlossene Randprogramme für Teilen, Einführen, Warmwasser, Waschen, Halten und Restablauf.", "Gleicher lokaler Besitzer; jede Zelle ist einzeln abgeschlossen.", "Sieben zwingend chronologische Takte einer Maschine."),

    module("WM23", "B3", 1, 3, "LOCAL_STATION_VARIANTS", "Obere Fächerstation", "Drei Varianten zum Sammeln, Wärmen und Abführen an der oberen offenen Fächerstation.", "Gleicher Besitzer, drei geschlossene Zellen.", "Eine dreistufige Vorbehandlung."),
    module("WM24", "B3", 4, 5, "CROSS_STATION_HANDOFF", "Sollmaßportion zum Rundgefäß", "Eine Sollmaßportion an der oberen Station entnehmen und am mittleren Rundgefäß umsetzen.", "Explizite Materialübergabe kreuzt den sichtbaren Stationswechsel.", "Eine unsichtbare Leitung vom Fächer zum Rundgefäß."),
    module("WM25", "B3", 6, 8, "LOCAL_STATION_VARIANTS", "Programme des Rundgefäßes", "Drei Umsetz-, Halte- und Ablaufvarianten am mittleren Rundgefäß.", "Gleicher Besitzer; alle Zellen schließen separat.", "Drei feste aufeinanderfolgende Gefäßphasen."),
    module("WM26", "B3", 9, 10, "CROSS_STATION_HANDOFF", "Ansatz zur unteren Korbstation", "Einen Posten am Rundgefäß ansetzen und an der unteren Korb-/Gefäßstation zuführen.", "Explizite Übergabe bei Besitzerwechsel; die Zeichnung liefert keine Leitung.", "Ein sichtbarer Einlass vom Rundgefäß zur Korbstation."),
    module("WM27", "B3", 11, 15, "LOCAL_ROUTINE_WITH_HANDOFF", "Aufstreichen, Absetzen und Wasserzugabe", "Einen aufgestrichenen Posten abkühlen und absetzen; daneben drei lokale Maß-, Wasser- und Ablaufvarianten.", "Nur S011→S012 ist chronologisch offen; S013–S015 schließen einzeln.", "Eine zwingende fünfstufige Behandlung."),
    module("WM28", "B3", 16, 16, "OWNER_BREAK_COMPOSITE", "Bodenablauf über die Bildlücke", "Den Bodenablauf schließen und den Posten umsetzen.", "Die eine Textanweisung schneidet von der Korbstation in die ungelöste Bildlücke.", "Ein sichtbarer Anschluss über die Lücke."),
    module("WM29", "B3", 17, 25, "LOCAL_STATION_VARIANTS", "Ungedeutete Zwischenstation", "Neun eigenständige Halte-, Absetz-, Ziel- und Umsetzprogramme im ungelösten Zwischenbereich.", "Ein bewusst ungelöster Besitzer; neun geschlossene Zellen ohne offene Übergabe.", "Eine versteckte, durchlaufende Mittelmaschine."),
    module("WM30", "B3", 26, 26, "OWNER_BREAK_COMPOSITE", "Sprung zum Hauptbogenpaar", "Sammelbecken bereitstellen, bis zum Klarstand arbeiten und länger sammeln.", "Die Aussage beginnt im ungelösten Zwischenbereich und endet am sichtbaren Hauptbogenpaar.", "Ein realer Stofflauf über die Bildlücke."),
    module("WM31", "B3", 27, 34, "LOCAL_STATION_VARIANTS", "Programme des Hauptbogenpaars", "Acht lokale Varianten für Halten, Waschen, Wasserweitergabe, Wanne, Abziehen und unteres Ziel.", "Gleicher Hauptbogenbesitzer; jede Zelle schließt separat.", "Ein einziger achtstufiger Kreislauf."),

    module("WM32", "B4", 1, 10, "LOCAL_STATION_VARIANTS", "Anwendungs- und Filterprogramme am Hauptpaar", "Zehn abgeschlossene Varianten zum Halten, Befestigen, Tuch einlegen, Seihen, Wärmen und Fortführen.", "Gleicher Hauptpaarbesitzer; keine offene Materialübergabe zwischen den Zellen.", "Ein langer Verband- oder Filterablauf."),
    module("WM33", "B4", 11, 14, "LOCAL_STATION_VARIANTS", "Linker Fransenposten", "Vier lokale Programme für Erwärmen, Waschen, Abführen, Absetzen und Wasserlauf schließen.", "Eigener linker Besitzer; jede Zelle schließt separat.", "Fortsetzung des Hauptpaars über eine unsichtbare Verbindung."),
    module("WM34", "B4", 15, 15, "OWNER_BREAK_COMPOSITE", "Klarflüssigkeit zum rechten Mehrarmknoten", "Klarflüssigkeit portionieren, halten, sammeln und abführen.", "Die Textanweisung wechselt intern vom linken Fransenposten zum rechten S-Lauf-/Mehrarmknoten.", "Ein sichtbarer Querfluss zwischen beiden Seiten."),
    module("WM35", "B4", 16, 16, "SELF_CONTAINED_ROUTINE", "Warmer Ausguss am rechten Knoten", "Eine weitere Portion zum rechten Knoten geben, warm ausgießen und absetzen.", "Eigene geschlossene Zelle am rechten Besitzer.", "Letzte Phase des linken Klarlaufs."),
    module("WM36", "B5", 1, 3, "LOCAL_STATION_VARIANTS", "Linker Stationsnachtrag", "Drei kurze Nachträge zum Umsetzen, Absetzen, Wärmen und Einstellen an der linken offenen Station.", "Eigener Record und Besitzer; keine offene Übergabe zwischen den drei Einträgen.", "Chronologische Fortsetzung von B4."),
    module("WM37", "B6", 1, 1, "SELF_CONTAINED_ROUTINE", "Rechter Stationsnachtrag", "Rohen Posten sammeln, Seitenarm öffnen, nach Sollmaß weiterführen, Tuch einlegen und zum Endziel bringen.", "Eigener Record und rechter Mehrarmbesitzer.", "Chronologische Fortsetzung von B5 oder B4."),
]


def unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))


def build() -> dict[str, object]:
    dictionary = read_tsv(DICT_IN)
    events = read_tsv(EVENT_IN)
    sentences = read_tsv(SENTENCE_IN)
    handoffs = read_tsv(HANDOFF_IN)
    owners = [row for row in read_tsv(OWNER_IN) if row["unit_kind"] == "PROSE_FIELD"]
    if (len(dictionary), len(events), len(sentences), len(handoffs), len(owners)) != (173, 381, 116, 19, 135):
        raise AssertionError("unexpected input dimensions")

    sentence_map = {row["statement_id"]: row for row in sentences}
    field_owner = {row["unit_id"]: row for row in owners}
    handoff_by_source = {row["source_statement_id"]: row for row in handoffs}
    handoff_by_target = {row["target_statement_id"]: row for row in handoffs}
    module_by_statement: dict[str, dict[str, object]] = {}
    for spec in MODULES:
        for statement_id in spec["statement_ids"]:
            if statement_id in module_by_statement:
                raise AssertionError(f"duplicate module assignment {statement_id}")
            module_by_statement[statement_id] = spec
    if set(module_by_statement) != set(sentence_map):
        raise AssertionError("module coverage does not match 116 statements")

    statement_owners: dict[str, list[str]] = {}
    statement_owner_statuses: dict[str, list[str]] = {}
    for row in sentences:
        fields = row["field_ids"].split("|")
        if not all(field in field_owner for field in fields):
            raise AssertionError(f"missing owner for {row['statement_id']}")
        statement_owners[row["statement_id"]] = unique([field_owner[field]["selected_visible_owner"] for field in fields])
        statement_owner_statuses[row["statement_id"]] = unique([field_owner[field]["owner_status"] for field in fields])

    module_rows: list[dict[str, str]] = []
    module_row_map: dict[str, dict[str, str]] = {}
    for spec in MODULES:
        module_sentences = [sentence_map[statement_id] for statement_id in spec["statement_ids"]]
        fields = [field for row in module_sentences for field in row["field_ids"].split("|")]
        event_ids = [event for row in module_sentences for event in row["event_ids"].split("|")]
        owner_sequence = unique([owner for statement_id in spec["statement_ids"] for owner in statement_owners[statement_id]])
        handoff_edges = [
            f"{source}->{item['target_statement_id']}"
            for source, item in handoff_by_source.items()
            if source in spec["statement_ids"] and item["target_statement_id"] in spec["statement_ids"]
        ]
        owner_breaks = [statement_id for statement_id in spec["statement_ids"] if len(statement_owners[statement_id]) > 1]
        internal_edges = len(spec["statement_ids"]) - 1
        row = {
            "module_id": str(spec["module_id"]),
            "section": "HERBAL" if str(spec["record_unit_id"]).startswith("H") else "BIOLOGICAL",
            "record_unit_id": str(spec["record_unit_id"]),
            "page": module_sentences[0]["page"],
            "module_type": str(spec["module_type"]),
            "workshop_title_de": str(spec["workshop_title_de"]),
            "statement_ids": "|".join(str(item) for item in spec["statement_ids"]),
            "statement_count": str(len(module_sentences)),
            "field_ids": "|".join(fields),
            "field_count": str(len(fields)),
            "event_ids": "|".join(event_ids),
            "event_count": str(len(event_ids)),
            "owner_sequence": "|".join(owner_sequence),
            "owner_count": str(len(owner_sequence)),
            "owner_break_statement_ids": "|".join(owner_breaks),
            "explicit_handoff_edges": "|".join(handoff_edges),
            "explicit_handoff_count": str(len(handoff_edges)),
            "internal_unsequenced_edge_count": str(internal_edges - len(handoff_edges)),
            "workshop_module_reading_de": str(spec["workshop_module_reading_de"]),
            "chronology_rule_de": str(spec["chronology_rule_de"]),
            "visible_basis_de": str(spec["visible_basis_de"]),
            "strongest_rival_de": str(spec["strongest_rival_de"]),
        }
        module_rows.append(row)
        module_row_map[row["module_id"]] = row

    # Classify all 105 adjacent statement edges. Only explicit handoffs license chronology.
    edge_rows: list[dict[str, str]] = []
    by_record: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in sentences:
        by_record[row["record_unit_id"]].append(row)
    for record in RECORD_ORDER:
        record_rows = by_record[record]
        for edge_index, (source, target) in enumerate(zip(record_rows, record_rows[1:]), 1):
            source_module = module_by_statement[source["statement_id"]]
            target_module = module_by_statement[target["statement_id"]]
            same_module = source_module["module_id"] == target_module["module_id"]
            same_owner = statement_owners[source["statement_id"]][-1] == statement_owners[target["statement_id"]][0]
            handoff = handoff_by_source.get(source["statement_id"])
            is_explicit = bool(handoff and handoff["target_statement_id"] == target["statement_id"])
            if is_explicit:
                edge_class = "EXPLICIT_HANDOFF_SAME_OWNER" if same_owner else "EXPLICIT_HANDOFF_CROSS_OWNER"
                chronology = "SEQUENTIAL"
                carried = handoff["carried_register_de"]
                interpretation = (
                    "Offener Posten wird an derselben Bildstation weitergeführt."
                    if same_owner
                    else "Offener Posten wechselt die Bildstation; Rezeptfolge ja, unsichtbare Rohrleitung nein."
                )
            elif same_module:
                edge_class = "PARALLEL_OR_EDITORIAL_WITHIN_MODULE"
                chronology = "NOT_FORCED"
                carried = ""
                interpretation = "Benachbarte abgeschlossene Einträge gehören zum selben Arbeitsmodul, sind aber Varianten oder Kontrollposten."
            else:
                edge_class = "NEW_MODULE_BOUNDARY_SAME_OWNER" if same_owner else "NEW_MODULE_BOUNDARY_OWNER_CHANGE"
                chronology = "RESET_MODULE"
                carried = ""
                interpretation = (
                    "Neuer Teilvorgang unter demselben Bildbesitzer."
                    if same_owner
                    else "Neuer Teilvorgang und neuer Bildbesitzer; alle lokalen Stoff- und Richtungsannahmen zurücksetzen."
                )
            edge_rows.append({
                "edge_id": f"{record}-E{edge_index:03d}",
                "record_unit_id": record,
                "page": source["page"],
                "source_statement_id": source["statement_id"],
                "target_statement_id": target["statement_id"],
                "source_module_id": str(source_module["module_id"]),
                "target_module_id": str(target_module["module_id"]),
                "source_owner": statement_owners[source["statement_id"]][-1],
                "target_owner": statement_owners[target["statement_id"]][0],
                "edge_class": edge_class,
                "chronology": chronology,
                "carried_register_de": carried,
                "workshop_interpretation_de": interpretation,
            })

    incoming_relation = {row["target_statement_id"]: row["edge_class"] for row in edge_rows}
    out_dictionary: list[dict[str, str]] = []
    for original in dictionary:
        row = dict(original)
        row["work_module_layer"] = "CARD_VALUE_UNCHANGED__MODULE_IS_STATEMENT_AND_OWNER_LEVEL"
        out_dictionary.append(row)

    out_sentences: list[dict[str, str]] = []
    for original in sentences:
        row = dict(original)
        statement_id = row["statement_id"]
        spec = module_by_statement[statement_id]
        module_row = module_row_map[str(spec["module_id"])]
        incoming = handoff_by_target.get(statement_id)
        outgoing = handoff_by_source.get(statement_id)
        if len(statement_owners[statement_id]) > 1:
            role = "COMPOSITE_OWNER_BREAK"
        elif incoming and outgoing:
            role = "SEQUENCE_MIDDLE"
        elif outgoing:
            role = "SEQUENCE_SOURCE"
        elif incoming:
            role = "SEQUENCE_TARGET"
        elif spec["module_type"] == "LOCAL_STATION_VARIANTS":
            role = "PARALLEL_VARIANT_ENTRY"
        elif spec["module_type"] == "LOCAL_ROUTINE_WITH_HANDOFF":
            role = "PARALLEL_LOCAL_ENTRY"
        else:
            role = "SELF_CONTAINED_ENTRY"
        row["work_module_id"] = str(spec["module_id"])
        row["work_module_type"] = str(spec["module_type"])
        row["work_module_title_de"] = str(spec["workshop_title_de"])
        row["work_module_role"] = role
        row["work_module_owner_sequence"] = "|".join(statement_owners[statement_id])
        row["work_module_owner_statuses"] = "|".join(statement_owner_statuses[statement_id])
        row["work_module_owner_break"] = "YES" if len(statement_owners[statement_id]) > 1 else "NO"
        row["relation_from_previous_statement"] = incoming_relation.get(statement_id, "RECORD_START")
        row["work_module_chronology_de"] = module_row["chronology_rule_de"]
        row["work_module_reading_de"] = module_row["workshop_module_reading_de"]
        out_sentences.append(row)

    sentence_out_map = {row["statement_id"]: row for row in out_sentences}
    out_events: list[dict[str, str]] = []
    for original in events:
        row = dict(original)
        statement = sentence_out_map[row["statement_id"]]
        row["work_module_id"] = statement["work_module_id"]
        row["work_module_type"] = statement["work_module_type"]
        row["work_module_role"] = statement["work_module_role"]
        row["work_module_owner_sequence"] = statement["work_module_owner_sequence"]
        row["work_module_layer_note"] = "EVENT_VALUE_UNCHANGED__MODULE_ORDER_FROM_STATEMENT_EDGE"
        out_events.append(row)

    write_tsv(DICT_OUT, out_dictionary)
    write_tsv(EVENT_OUT, out_events)
    write_tsv(SENTENCE_OUT, out_sentences)
    write_tsv(MODULE_OUT, module_rows)
    write_tsv(EDGE_OUT, edge_rows)

    record_lines = [
        "# Elf Records als Werkstattmodule",
        "",
        "Pfeile stehen nur bei ausdrücklich offenen Übergaben. Aufzählungspunkte innerhalb eines Variantenmoduls sind nicht automatisch chronologisch.",
        "",
    ]
    for record in RECORD_ORDER:
        record_lines.extend([f"## {record} — {by_record[record][0]['page']}", ""])
        record_modules = [row for row in module_rows if row["record_unit_id"] == record]
        for module_row in record_modules:
            record_lines.extend([
                f"### {module_row['module_id']} — {module_row['workshop_title_de']}",
                "",
                f"**Lesung:** {module_row['workshop_module_reading_de']}",
                "",
                f"**Ordnungsregel:** {module_row['chronology_rule_de']}",
                "",
            ])
            module_statement_ids = module_row["statement_ids"].split("|")
            for index, statement_id in enumerate(module_statement_ids, 1):
                statement = sentence_out_map[statement_id]
                prefix = "→" if statement["handoff_in_category"] else "•"
                owner_note = (
                    f" **[BESITZERBRUCH: {statement['work_module_owner_sequence']}]**"
                    if statement["work_module_owner_break"] == "YES"
                    else ""
                )
                carry_note = (
                    f" **[ÜBERNIMMT: {statement['handoff_in_register_de']}]**"
                    if statement["handoff_in_register_de"]
                    else ""
                )
                record_lines.append(
                    f"{prefix} **{statement_id}** — {statement['workshop_sentence_de'].rstrip('.')} "
                    f"{statement['step_editor_label']}{carry_note}{owner_note}"
                )
            record_lines.append("")
    RECORD_OUT.write_text("\n".join(record_lines), encoding="utf-8")

    edge_counts = Counter(row["edge_class"] for row in edge_rows)
    module_type_counts = Counter(row["module_type"] for row in module_rows)
    owner_break_ids = {
        row["statement_id"] for row in out_sentences if row["work_module_owner_break"] == "YES"
    }
    checks = {
        "cards_173": len(out_dictionary) == 173,
        "events_381": len(out_events) == 381,
        "sentences_116": len(out_sentences) == 116,
        "records_11": set(by_record) == set(RECORD_ORDER),
        "modules_37": len(module_rows) == 37,
        "adjacent_edges_105": len(edge_rows) == 105,
        "explicit_handoffs_19": sum(row["chronology"] == "SEQUENTIAL" for row in edge_rows) == 19,
        "same_owner_handoffs_14": edge_counts["EXPLICIT_HANDOFF_SAME_OWNER"] == 14,
        "cross_owner_handoffs_5": edge_counts["EXPLICIT_HANDOFF_CROSS_OWNER"] == 5,
        "parallel_editorial_edges_60": edge_counts["PARALLEL_OR_EDITORIAL_WITHIN_MODULE"] == 60,
        "module_boundaries_26": sum(key.startswith("NEW_MODULE_BOUNDARY") for key in edge_counts for _ in range(edge_counts[key])) == 26,
        "owner_break_statements_exact": owner_break_ids == {"B2-S012", "B3-S016", "B3-S026", "B4-S015"},
        "module_statement_counts_116": sum(int(row["statement_count"]) for row in module_rows) == 116,
        "module_event_counts_381": sum(int(row["event_count"]) for row in module_rows) == 381,
        "dictionary_values_unchanged": all(
            row["concrete_word_reading_de"] == original["concrete_word_reading_de"]
            for row, original in zip(out_dictionary, dictionary)
        ),
        "event_values_unchanged": all(
            row["concrete_word_reading_de"] == original["concrete_word_reading_de"]
            and row["contextual_event_reading_de"] == original["contextual_event_reading_de"]
            for row, original in zip(out_events, events)
        ),
        "sentence_readings_unchanged": all(
            row["workshop_sentence_de"] == original["workshop_sentence_de"]
            for row, original in zip(out_sentences, sentences)
        ),
        "all_statements_one_module": len({row["statement_id"] for row in out_sentences}) == 116,
        "all_events_module_agree": all(
            row["work_module_id"] == sentence_out_map[row["statement_id"]]["work_module_id"] for row in out_events
        ),
        "fixed_pages_only": {row["page"] for row in out_events} == ALLOWED_PAGES,
        "sealed_absent": not any(row["page"].startswith("f84") for row in out_events),
    }
    result = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "counts": {
            "cards": len(out_dictionary),
            "events": len(out_events),
            "sentences": len(out_sentences),
            "records": len(by_record),
            "modules": len(module_rows),
            "adjacent_statement_edges": len(edge_rows),
            "module_types": dict(sorted(module_type_counts.items())),
            "edge_classes": dict(sorted(edge_counts.items())),
            "owner_break_statements": len(owner_break_ids),
        },
        "working_rule": "OPEN HANDOFFS SEQUENCE; CLOSED CELLS MAY BE PARALLEL VARIANTS; OWNER CHANGE STARTS A NEW STATION",
        "sealed": {"f84": True, "f84r": True},
    }
    CHECK_OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    outputs = [DICT_OUT, EVENT_OUT, SENTENCE_OUT, RECORD_OUT, MODULE_OUT, EDGE_OUT, CHECK_OUT]
    summary = {
        "status": result["status"],
        "counts": result["counts"],
        "input_hashes": {path.name: sha256(path) for path in [DICT_IN, EVENT_IN, SENTENCE_IN, HANDOFF_IN, OWNER_IN]},
        "output_hashes": {path.name: sha256(path) for path in outputs},
        "sealed": result["sealed"],
    }
    SUMMARY_OUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise AssertionError(json.dumps(result, ensure_ascii=False, indent=2))
    return result


if __name__ == "__main__":
    print(json.dumps(build(), ensure_ascii=False, indent=2, sort_keys=True))

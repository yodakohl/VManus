#!/usr/bin/env python3
"""Build the blinded V61 R2 historical clause/reflow edition.

This is a creative source-structure exercise.  It preserves the selected V60
exact-card mnemonics and the canonical V59 field expansions; it assigns no new
card meaning.  Mixed page-bearing sources are materialised only through the
guarded allow-list query.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
from collections import Counter, OrderedDict, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
ALLOWED_PAGES = ("f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r")

FIELD_SOURCE = ROOT / "experiments/yolo/sidequest_theory_candidates_v59/V59_R1_FINAL_135_FIELD_EDITION.tsv"
RECORD_SOURCE = ROOT / "experiments/yolo/sidequest_theory_candidates_v59/V59_R1_FINAL_14_RECORD_DIAGRAM_TEXTS.tsv"
EVENT_SOURCE = ROOT / "experiments/yolo/sidequest_theory_candidates_v60/V60_SELECTED_381_EVENT_LEDGER.tsv"
DECISION_SOURCE = ROOT / "experiments/yolo/sidequest_theory_candidates_v60/V60_SELECTED_EXACT_CARD_DECISIONS.tsv"

FIELD_COLUMNS = [
    "field_serial", "field_id", "page", "record", "record_unit_id", "locus",
    "field_ordinal_in_locus", "field_ordinal_in_record", "event_count",
    "surface_sequence", "formal_sequence_opaque", "FORMAL_VALUE",
    "ATOMIC_OR_WHOLE_CARD_MNEMONIC", "LOCAL_IATROMEDICAL_EXPANSION",
    "NONMEDICAL_RIVAL", "UNKNOWN_EXEMPLAR_STATUS", "closure_status",
    "source_lineage",
]

EVENT_COLUMNS = [
    "event_serial", "page", "locus", "record", "record_unit_id", "field_id",
    "field_ordinal_in_locus", "event_index_in_locus", "event_index_in_record",
    "surface", "joint_tuple_id", "formal_formula_opaque", "FORMAL_VALUE",
    "terminal_status", "strict_control_prompt", "ATOMIC_OR_WHOLE_CARD_MNEMONIC",
    "mnemonic_scope", "LOCAL_IATROMEDICAL_EXPANSION", "NONMEDICAL_RIVAL",
    "UNKNOWN_EXEMPLAR_STATUS", "source_lineage",
]

RECORD_COLUMNS = [
    "unit_id", "page", "module", "fields_or_loci", "events_or_groups",
    "FORMAL_VALUE", "ATOMIC_OR_WHOLE_CARD_MNEMONIC",
    "LOCAL_IATROMEDICAL_EXPANSION", "NONMEDICAL_RIVAL",
    "UNKNOWN_EXEMPLAR_STATUS", "strongest_contradiction", "teaching_rule",
    "source_lineage",
]

VALID_BOUNDARY_CLASSES = {
    "CONTINUE_SAME_CLAUSE",
    "START_NEW_CLAUSE",
    "RESUME_ACTIVE_ITEM",
    "NEXT_PARALLEL_CELL",
    "UNRESOLVED",
}

# Exact boundary decisions are keyed by the last field of one physical line and
# the first field of the next physical line.  No surface or substring rule is
# used to generate them.
BOUNDARY_SPECS = [
    ("F001", "F002", "RESUME_ACTIVE_ITEM", "Die zweite Zeile setzt die bereits bereitete Arznei als stilles Objekt voraus.", "IMPLICIT_ACTIVE_PREPARATION", ".53"),
    ("F003", "F004", "CONTINUE_SAME_CLAUSE", "Beide Felder bleiben offen; Erntezeit, Ansatz und Mass können dieselbe Simplex-Bereitung fortsetzen.", "NONE", ".42"),
    ("F004", "F005", "START_NEW_CLAUSE", "Der Wechsel von vor der Blüte zu geöffneter Blüte und neuer Aufbewahrung spricht für einen neuen parataktischen Satz.", "NONE", ".45"),
    ("F007", "F008", "RESUME_ACTIVE_ITEM", "Die zurückbehaltene Blütenkrone kann als aktiver Teil in die folgende Anwendung übernommen werden.", "IMPLICIT_RETAINED_PART", ".48"),
    ("F008", "F009", "START_NEW_CLAUSE", "Der Blätterumschlag ist ein neuer Gebrauch und nicht die sichere Fortsetzung der zuvor gebundenen Portion.", "NONE", ".55"),
    ("F011", "F012", "START_NEW_CLAUSE", "Die Waschhandlung ist terminal; die nächste Zeile bezeichnet ausdrücklich einen zweiten Arzneigebrauch.", "SECOND_USE_RUBRIC", ".72"),
    ("F014", "F015", "CONTINUE_SAME_CLAUSE", "Wurzel und Mass erhalten im Folgefeld Medium, Anwendung und Ziel.", "NONE", ".61"),
    ("F015", "F016", "CONTINUE_SAME_CLAUSE", "Der folgende Simplex-Bezug und das Trocknen des Pflasters schließen die offene Anwendung ab.", "SAME_SIMPLEX", ".56"),
    ("F016", "F017", "NEXT_PARALLEL_CELL", "Nach der terminalen Pflasterhandlung beginnt ein anderer Samen-, Knospen- oder Blattposten.", "NEW_PLANT_PART", ".69"),
    ("F017", "F018", "RESUME_ACTIVE_ITEM", "Der getrocknete Pflanzenteil wird in der Folgezeile gebraucht und verwahrt.", "IMPLICIT_DRIED_PART", ".58"),
    ("F018", "F019", "NEXT_PARALLEL_CELL", "Der Honigansatz ist besser als neuer Gebrauchsposten denn als notwendige Satzfortsetzung gelesen.", "NONE", ".46"),
    ("F019", "F020", "NEXT_PARALLEL_CELL", "Der feldinitiale Anteil mit Blüte und Mass bildet einen neuen kurzen Artikelposten.", "NEW_SELECTED_PORTION", ".51"),
    ("F022", "F023", "RESUME_ACTIVE_ITEM", "Das exakte VORIGES? am Anfang der Folgezeile greift den offenen Arbeitsbestand auf.", "EXACT_VORIGES_AT_LINE_ENTRY", ".76"),
    ("F024", "F025", "CONTINUE_SAME_CLAUSE", "Der bloße Verweis auf die vorige Zubereitung erhält erst mit warm halten eine ausführbare Handlung.", "IMPLICIT_PREVIOUS_PREPARATION", ".68"),
    ("F028", "F029", "NEXT_PARALLEL_CELL", "Abkühlen und erneutes einmaliges Erwärmen sind als parallele Operationszellen glatter als eine einzige Klausel.", "NONE", ".60"),
    ("F033", "F034", "START_NEW_CLAUSE", "Auf Anwendung durch die Läufe folgt eine neue Spülrubrik mit Wasser.", "NONE", ".57"),
    ("F036", "F037", "START_NEW_CLAUSE", "Der Gebrauch des unteren Ablaufs wird von einer neuen Füll- und Kühlhandlung gefolgt.", "NONE", ".49"),
    ("F040", "F041", "CONTINUE_SAME_CLAUSE", "Das offene Füllen des Gefäßes nimmt Anwendung, Klärung und Absetzen der nächsten Zeile auf.", "IMPLICIT_FILLED_VESSEL", ".52"),
    ("F048", "F049", "CONTINUE_SAME_CLAUSE", "Der Gang zum nächsten Becken wird dort durch Temperieren und Klären vollendet.", "NEXT_BASIN_CARRY", ".63"),
    ("F050", "F051", "UNRESOLVED", "Die Formel nächster abgemessener Posten steht beidseits der Grenze; Catchword, Dittographie und echter Neustart sind untrennbar.", "DUPLICATED_BATCH_OPENING", ".18"),
    ("F052", "F053", "START_NEW_CLAUSE", "Nach Anwendung der Ölmischung ist die Zugabe sauberen Wassers ein eigener Folgeschritt.", "NONE", ".47"),
    ("F056", "F057", "NEXT_PARALLEL_CELL", "Nach der Klarheitszelle und großem Locus-Sprung beginnt eine neue gemessene Badezelle.", "NONE", ".62"),
    ("F058", "F059", "RESUME_ACTIVE_ITEM", "Die abgezogene klare Flüssigkeit bleibt aktiver Gegenstand für Temperieren und Eintauchen.", "IMPLICIT_CLEAR_LIQUID", ".64"),
    ("F061", "F062", "START_NEW_CLAUSE", "Auf das Schließen des Ablaufs folgt eine neue Spül- oder Badeanweisung.", "NONE", ".58"),
    ("F063", "F064", "CONTINUE_SAME_CLAUSE", "Die offene Zutaten-, Mass- und Warmwasserfolge endet plausibel erst mit dem Abziehen.", "OPEN_BATCH_CARRY", ".55"),
    ("F074", "F075", "CONTINUE_SAME_CLAUSE", "Der neue Posten zum unteren Ablauf wird durch Spülen und Abschluss vollendet.", "OPEN_BATCH_CARRY", ".50"),
    ("F079", "F080", "NEXT_PARALLEL_CELL", "Auf die nackte Anwendungszelle folgt eine selbständige Füll- und Klärzelle.", "NONE", ".55"),
    ("F081", "F082", "RESUME_ACTIVE_ITEM", "Die angewandte, gemischte und gekühlte Flüssigkeit wird als bereiteter Ansatz weitergeführt.", "IMPLICIT_PREPARED_FLUID", ".46"),
    ("F086", "F087", "START_NEW_CLAUSE", "Nach dem Schließen des unteren Ablaufs beginnt eine getrennte Kühlhandlung.", "NONE", ".51"),
    ("F092", "F093", "CONTINUE_SAME_CLAUSE", "Der offene Posten mit Ziel und aktiver Portion erhält Mass, Zeit, Warmwasser und terminales Zurückbehalten.", "TARGET_AND_ACTIVE_PORTION_RECUR", ".66"),
    ("F095", "F096", "NEXT_PARALLEL_CELL", "Ablassen und Spülen sind zwei jeweils terminale Nachbarzellen.", "NONE", ".76"),
    ("F098", "F099", "CONTINUE_SAME_CLAUSE", "Die offene Folge bis der Strom klar wird wird durch Absetzen abgeschlossen.", "CLEAR_STREAM_CARRY", ".62"),
    ("F103", "F104", "RESUME_ACTIVE_ITEM", "Die aktive gemessene Portion bleibt Gegenstand des Abziehens und Mischens.", "IMPLICIT_ACTIVE_PORTION", ".43"),
    ("F107", "F108", "NEXT_PARALLEL_CELL", "Nach terminalem Abziehen beginnt eine neue Status- und Bearbeitungszelle.", "NONE", ".64"),
    ("F111", "F112", "NEXT_PARALLEL_CELL", "Ablaufgerichtetes Mischen und ausgewähltes Temperieren/Anwenden sind als Nachbarzellen sparsamer.", "NONE", ".42"),
    ("F113", "F114", "NEXT_PARALLEL_CELL", "Auf abgeschlossene Bindung folgt eine eigenständige Filter-, Misch- und Badezelle.", "NONE", ".67"),
    ("F116", "F117", "NEXT_PARALLEL_CELL", "Eine abgeschlossene Filterzelle wird von einer gemessenen warmen Spülzelle gefolgt.", "NONE", ".71"),
    ("F119", "F120", "START_NEW_CLAUSE", "Der Kochschritt ist terminal; danach beginnt ein neuer gemessener Gefäßposten.", "NONE", ".71"),
    ("F120", "F121", "RESUME_ACTIVE_ITEM", "Der offene gemischte Posten wird mit der Formel vorige Zubereitung wieder aufgenommen.", "PREVIOUS_PREPARATION_FORMULA", ".59"),
    ("F123", "F124", "START_NEW_CLAUSE", "Nach terminalem Einlaufen/Stehen folgt eine neue Zubereitung zum sofortigen Gebrauch.", "NONE", ".54"),
    ("F124", "F125", "START_NEW_CLAUSE", "Der sofortige Gebrauch endet; die nächste Zeile beginnt eine neue Mass-, Klarheits- und Dauerangabe.", "NONE", ".58"),
    ("F125", "F126", "CONTINUE_SAME_CLAUSE", "Die offene Dauerangabe wird durch Öffnen und Ablassen terminal abgeschlossen.", "OPEN_DURATION_CARRY", ".61"),
    ("F127", "F128", "CONTINUE_SAME_CLAUSE", "Der offene Zielbezug erhält erwärmtes Wasser und einen Bereitschaftsschluss.", "OPEN_TARGET_CARRY", ".58"),
    ("F131", "F132", "CONTINUE_SAME_CLAUSE", "Das isolierte Zeitfragment verlangt die folgende Ziel-, Vorposten- und Massfolge als Ergänzung.", "FRAGMENT_CARRY", ".73"),
    ("F132", "F133", "RESUME_ACTIVE_ITEM", "Die vorige Mischung/Zubereitung wird wiederholt und an der zweiten Öffnung weiterbearbeitet.", "REPEATED_PREVIOUS_MIXTURE_FORMULA", ".61"),
    ("F134", "F135", "CONTINUE_SAME_CLAUSE", "Die offene Ohne-Kochen-/erste-Öffnung-Folge wird durch Mass, Tuch und Ziel vervollständigt.", "PREVIOUS_PREPARATION_RECURS", ".60"),
]

SILENT_COMPLEMENTS = {
    "MASS?": "Artikel, Vorgeschriebenheitsgrad, Einheit und gemessener Stoff",
    "ANWENDEN?": "Objekt, Ziel und Flexion des Gebrauchsverbs",
    "BEREIT?": "Subjekt, Kopula und zeitliche Schwellenkonstruktion",
    "ANSATZ?": "Artikel, Materialart und Herstellungszustand",
    "ZIEL?": "Bewegungsverb, Deixis und konkreter Ort oder Körperteil",
    "KLAR?": "Trägerflüssigkeit, Zustandsverb und gegebenenfalls Ablauf",
    "VORIGES?": "Antezedent, Entnahmeverb und Stoffklasse",
    "ANTEIL?": "Imperativ, Artikel und Auswahlmerkmal",
    "TEMPERIEREN?": "Arbeitsflüssigkeit, Temperaturgrad und Dauer",
    "SPÜLEN?": "Objekt oder Ort, Wiederholungszahl und Zellschluss",
    "ABLASSEN?": "verbrauchte Flüssigkeit, Zielgefäß und Zellschluss",
}

BOUNDARY_RIVALS = {
    "CONTINUE_SAME_CLAUSE": "ZWEI_SELBSTÄNDIGE_LISTENPUNKTE_TROTZ_OFFENHEIT",
    "START_NEW_CLAUSE": "BLOSSER_ZEILENRESET_IN_FORTLAUFENDER_PROSA",
    "RESUME_ACTIVE_ITEM": "NEUER_POSTEN_MIT_NUR_FORMELHAFT_GLEICHEM_WORTLAUT",
    "NEXT_PARALLEL_CELL": "FORTLAUFENDE_PROSA_OHNE_ECHTE_ZELLENGRENZE",
    "UNRESOLVED": "CATCHWORD_ODER_DITTOGRAPHIE_ODER_ECHTER_NEUSTART",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def guarded_query(path: Path, columns: list[str]) -> tuple[list[dict[str, str]], dict]:
    command = [
        str(ROOT / "vmanus-exp"), "query-tsv", str(path),
        "--selector", "page",
    ]
    for page in ALLOWED_PAGES:
        command.extend(["--allow", page])
    command.extend(["--columns", ",".join(columns), "--forbid-prefix", "f84"])
    result = subprocess.run(command, cwd=ROOT, check=True, text=True, capture_output=True)
    match = re.search(r"GUARD_STATS\s+(\{.*\})", result.stderr)
    if not match:
        raise RuntimeError(f"Missing guarded-query statistics for {path}")
    stats = json.loads(match.group(1))
    rows = list(csv.DictReader(result.stdout.splitlines(), delimiter="\t"))
    return rows, stats


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def unique(values):
    return list(dict.fromkeys(value for value in values if value))


def segments(expansion: str) -> list[str]:
    return [part.strip() for part in expansion.split(" ; ") if part.strip()]


def source_expansion(field_rows: list[dict[str, str]]) -> str:
    parts: list[str] = []
    for field in field_rows:
        parts.extend(segments(field["LOCAL_IATROMEDICAL_EXPANSION"]))
    text = "; ".join(parts)
    if text and not text.endswith("."):
        text += "."
    return text


def context_tail(expansion: str) -> str:
    parts = segments(expansion)
    return parts[-1] if parts else expansion


def context_head(expansion: str) -> str:
    parts = segments(expansion)
    return parts[0] if parts else expansion


def reflow_preview(decision: str, before: str, after: str) -> str:
    if decision == "CONTINUE_SAME_CLAUSE":
        return f"{before}; {after} …"
    if decision == "START_NEW_CLAUSE":
        return f"{before}. Item: {after} …"
    if decision == "RESUME_ACTIVE_ITEM":
        return f"{before}. [stiller aktiver Gegenstand:] {after} …"
    if decision == "NEXT_PARALLEL_CELL":
        return f"{before}. [nächste Parallelzelle:] {after} …"
    return f"{before} | {after} …"


def main() -> None:
    fields, field_guard = guarded_query(FIELD_SOURCE, FIELD_COLUMNS)
    events, event_guard = guarded_query(EVENT_SOURCE, EVENT_COLUMNS)
    records, record_guard = guarded_query(RECORD_SOURCE, RECORD_COLUMNS)
    decisions = read_tsv(DECISION_SOURCE)

    fields.sort(key=lambda row: int(row["field_serial"]))
    events.sort(key=lambda row: int(row["event_serial"]))
    record_order = ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"]
    record_rank = {record: rank for rank, record in enumerate(record_order)}
    records.sort(key=lambda row: record_rank[row["unit_id"]])

    decision_by_id = {row["joint_tuple_id"]: row for row in decisions}
    card_by_id = {row["joint_tuple_id"]: row["card"] for row in decisions}
    selected_by_id = {row["joint_tuple_id"]: row["selected_short_mnemonic"] for row in decisions}
    boundary_spec = {
        (left, right): {
            "decision": decision,
            "evidence": evidence,
            "catchword_signal": catchword,
            "confidence": confidence,
        }
        for left, right, decision, evidence, catchword, confidence in BOUNDARY_SPECS
    }

    events_by_field: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        events_by_field[event["field_id"]].append(event)

    field_by_id = {row["field_id"]: row for row in fields}
    actual_boundary_pairs: list[tuple[str, str]] = []
    previous = None
    for field in fields:
        if previous and previous["record_unit_id"] == field["record_unit_id"] and previous["locus"] != field["locus"]:
            actual_boundary_pairs.append((previous["field_id"], field["field_id"]))
        previous = field

    if set(actual_boundary_pairs) != set(boundary_spec):
        missing = sorted(set(actual_boundary_pairs) - set(boundary_spec))
        extra = sorted(set(boundary_spec) - set(actual_boundary_pairs))
        raise AssertionError(f"Boundary specification mismatch; missing={missing}, extra={extra}")

    field_assignment: dict[str, dict[str, str]] = {}
    statement_groups: OrderedDict[str, list[dict[str, str]]] = OrderedDict()
    statement_ordinals: Counter = Counter()
    previous = None
    current_statement = ""
    for field in fields:
        record = field["record_unit_id"]
        if previous is None or previous["record_unit_id"] != record:
            relation_before = "RECORD_START"
            new_statement = True
        elif previous["locus"] == field["locus"]:
            relation_before = "INTRA_LINE_FIELD_BREAK"
            new_statement = True
        else:
            relation_before = boundary_spec[(previous["field_id"], field["field_id"])]["decision"]
            new_statement = relation_before != "CONTINUE_SAME_CLAUSE"

        if new_statement:
            statement_ordinals[record] += 1
            current_statement = f"{record}_S{statement_ordinals[record]:03d}"
            statement_groups[current_statement] = []
        statement_groups[current_statement].append(field)
        field_assignment[field["field_id"]] = {
            "statement_id": current_statement,
            "relation_before": relation_before,
        }
        previous = field

    def event_trace(event: dict[str, str]) -> str:
        tuple_id = event["joint_tuple_id"]
        mnemonic = event["ATOMIC_OR_WHOLE_CARD_MNEMONIC"]
        if tuple_id in decision_by_id:
            return (
                f"{{{event['surface']}/{card_by_id[tuple_id]}={mnemonic}}}"
                f"[STILL_GRAMMAR:{SILENT_COMPLEMENTS[mnemonic]}]"
            )
        return f"[EXEMPLAR:{event['LOCAL_IATROMEDICAL_EXPANSION']}]"

    def field_trace(field_id: str) -> str:
        return " | ".join(event_trace(event) for event in events_by_field[field_id])

    def anchors_for(field_rows: list[dict[str, str]]) -> list[str]:
        anchors = []
        for field in field_rows:
            for event in events_by_field[field["field_id"]]:
                tuple_id = event["joint_tuple_id"]
                if tuple_id in decision_by_id:
                    anchors.append(f"{card_by_id[tuple_id]}={event['ATOMIC_OR_WHOLE_CARD_MNEMONIC']}")
        return anchors

    def unknown_expansions_for(field_rows: list[dict[str, str]]) -> list[str]:
        expansions = []
        for field in field_rows:
            for event in events_by_field[field["field_id"]]:
                if event["joint_tuple_id"] not in decision_by_id:
                    expansions.append(event["LOCAL_IATROMEDICAL_EXPANSION"])
        return expansions

    statement_rows: list[dict[str, object]] = []
    statement_by_id: dict[str, dict[str, object]] = {}
    for statement_id, group in statement_groups.items():
        record = group[0]["record_unit_id"]
        group_events = [event for field in group for event in events_by_field[field["field_id"]]]
        anchors = anchors_for(group)
        unknown_expansions = unknown_expansions_for(group)
        internal_relations = []
        for left, right in zip(group, group[1:]):
            if left["locus"] != right["locus"]:
                internal_relations.append(boundary_spec[(left["field_id"], right["field_id"])]["decision"])
        entry_relation = field_assignment[group[0]["field_id"]]["relation_before"]
        spans_lines = len(unique(field["locus"] for field in group)) > 1
        if record.startswith("H"):
            if spans_lines:
                clause_type = "HERBAL_REFLOWED_RECIPE_CLAUSE"
                mechanism = "Simplex oder Ansatz bleibt über den physischen Zeilenwechsel aktiv; parataktische Rezeptglieder werden im selben Aussageschritt gelesen."
            elif entry_relation == "RESUME_ACTIVE_ITEM":
                clause_type = "HERBAL_ACTIVE_ITEM_RESUMPTION"
                mechanism = "Ein stiller Bildbesitzer oder zuvor genannter Pflanzenteil wird wie de eodem/praedictum wieder aufgenommen; nur Funktionsvergleich."
            else:
                clause_type = "HERBAL_PARATACTIC_ITEM"
                mechanism = "Kurzer Herbal- oder Rezeptposten im Recipe/Item-Stil; Feldtrenner ordnet, ohne einen modernen Satz zu behaupten."
        else:
            if spans_lines:
                clause_type = "BIO_REFLOWED_WORKCELL_CLAUSE"
                mechanism = "Ein offener Bade-, Gefäß- oder Leitungsprozess läuft in der nächsten physischen Zeile bis zur lokalen Operation oder Terminalformel weiter."
            elif entry_relation == "RESUME_ACTIVE_ITEM":
                clause_type = "BIO_ACTIVE_FLUID_OR_STATION_RESUMPTION"
                mechanism = "Arbeitsflüssigkeit, Gefäß oder Station bleibt als aktiver Registerposten still und wird in einer neuen Kurzklausel wieder aufgenommen."
            elif entry_relation == "NEXT_PARALLEL_CELL":
                clause_type = "BIO_PARALLEL_WORKCELL"
                mechanism = "Benachbarte kurze Zellen werden als parallele Bade-/Gefäßanweisungen gelesen, nicht als durchlaufender grammatischer Satz."
            else:
                clause_type = "BIO_PARATACTIC_WORKCELL"
                mechanism = "Kurze imperative Arbeitszelle eines Bade- oder Gefäßregimens; Terminalwert schließt die Zelle, nicht notwendig die physische Zeile."

        silent_anchor_grammar = unique(
            SILENT_COMPLEMENTS[event["ATOMIC_OR_WHOLE_CARD_MNEMONIC"]]
            for event in group_events
            if event["joint_tuple_id"] in decision_by_id
        )
        row = {
            "statement_id": statement_id,
            "record_unit_id": record,
            "page": group[0]["page"],
            "field_ids": "|".join(field["field_id"] for field in group),
            "loci": "|".join(unique(field["locus"] for field in group)),
            "field_count": len(group),
            "event_count": len(group_events),
            "spans_physical_lines": "YES" if spans_lines else "NO",
            "entry_relation": entry_relation,
            "interline_relations_inside_statement": "|".join(internal_relations) if internal_relations else "NONE",
            "final_closure_status": group[-1]["closure_status"],
            "exact_short_mnemonic_sequence": " | ".join(anchors) if anchors else "NONE",
            "exact_anchor_count": len(anchors),
            "unknown_exemplar_event_count": len(unknown_expansions),
            "anchor_silent_trace": " || ".join(field_trace(field["field_id"]) for field in group),
            "silent_anchor_grammar": " | ".join(silent_anchor_grammar) if silent_anchor_grammar else "NONE",
            "silent_unknown_event_expansions": " | ".join(unknown_expansions) if unknown_expansions else "NONE",
            "german_source_expansion": source_expansion(group),
            "source_clause_type": clause_type,
            "historical_mechanism": mechanism,
            "strongest_historical_rival": " | ".join(unique(field["NONMEDICAL_RIVAL"] for field in group)),
            "interpretation_status": "CREATIVE_LOCAL_SOURCE_EXPANSION_NOT_CARD_COMPOSITION_OR_TRANSLATION",
            "source_lineage": "V59_R1_CANONICAL_FIELDS+V60_SELECTED_EXACT_DECK>V61_R2",
        }
        statement_rows.append(row)
        statement_by_id[statement_id] = row

    field_map_rows: list[dict[str, object]] = []
    for field in fields:
        statement_id = field_assignment[field["field_id"]]["statement_id"]
        statement = statement_by_id[statement_id]
        group = statement_groups[statement_id]
        field_events = events_by_field[field["field_id"]]
        field_anchors = anchors_for([field])
        field_unknowns = [event for event in field_events if event["joint_tuple_id"] not in decision_by_id]
        field_map_rows.append({
            "field_serial": field["field_serial"],
            "field_id": field["field_id"],
            "page": field["page"],
            "record_unit_id": field["record_unit_id"],
            "locus": field["locus"],
            "field_ordinal_in_locus": field["field_ordinal_in_locus"],
            "field_ordinal_in_record": field["field_ordinal_in_record"],
            "event_count": field["event_count"],
            "surface_sequence": field["surface_sequence"],
            "formal_sequence_opaque": field["formal_sequence_opaque"],
            "FORMAL_VALUE": field["FORMAL_VALUE"],
            "source_closure_status": field["closure_status"],
            "boundary_before": field_assignment[field["field_id"]]["relation_before"],
            "statement_id": statement_id,
            "field_position_in_statement": f"{group.index(field) + 1}/{len(group)}",
            "statement_spans_physical_lines": statement["spans_physical_lines"],
            "exact_short_mnemonics_in_field": " | ".join(field_anchors) if field_anchors else "NONE",
            "exact_anchor_count_in_field": len(field_anchors),
            "unknown_exemplar_events_in_field": len(field_unknowns),
            "anchor_silent_trace_in_field": field_trace(field["field_id"]),
            "canonical_local_expansion_unchanged": field["LOCAL_IATROMEDICAL_EXPANSION"],
            "statement_german_source_expansion": statement["german_source_expansion"],
            "silent_additions_rule": "ONLY_BRACED_CARD=MNEMONIC_IS_EXACT;ALL_GRAMMAR_OBJECTS_OWNERS_AND_EXEMPLAR_TEXT_ARE_SILENT_LOCAL_EXPANSION",
            "source_clause_type": statement["source_clause_type"],
            "strongest_historical_rival": field["NONMEDICAL_RIVAL"],
            "interpretation_status": statement["interpretation_status"],
            "source_lineage": "V59_R1_CANONICAL_FIELD+V60_SELECTED_EXACT_DECK>V61_R2",
        })

    boundary_rows: list[dict[str, object]] = []
    for serial, (left_id, right_id) in enumerate(actual_boundary_pairs, start=1):
        left = field_by_id[left_id]
        right = field_by_id[right_id]
        spec = boundary_spec[(left_id, right_id)]
        decision = spec["decision"]
        left_statement = field_assignment[left_id]["statement_id"]
        right_statement = field_assignment[right_id]["statement_id"]
        before = context_tail(left["LOCAL_IATROMEDICAL_EXPANSION"])
        after = context_head(right["LOCAL_IATROMEDICAL_EXPANSION"])
        boundary_rows.append({
            "boundary_id": f"IB{serial:03d}",
            "page": left["page"],
            "record_unit_id": left["record_unit_id"],
            "from_locus": left["locus"],
            "to_locus": right["locus"],
            "from_field_id": left_id,
            "to_field_id": right_id,
            "from_closure_status": left["closure_status"],
            "to_closure_status": right["closure_status"],
            "decision": decision,
            "from_statement_id": left_statement,
            "to_statement_id": right_statement,
            "same_statement_after_reflow": "YES" if left_statement == right_statement else "NO",
            "boundary_context": f"{before} || {after}",
            "german_reflow_preview": reflow_preview(decision, before, after),
            "historical_evidence": spec["evidence"],
            "catchword_or_carry_signal": spec["catchword_signal"],
            "strongest_historical_rival": BOUNDARY_RIVALS[decision],
            "confidence": spec["confidence"],
            "interpretation_status": "BOUNDARY_HYPOTHESIS_NOT_SYNTAX_DECIPHERMENT",
            "source_lineage": "V59_R1_PHYSICAL_LOCI+FIELDS>V61_R2",
        })

    record_by_unit = {row["unit_id"]: row for row in records}
    fields_by_record: dict[str, list[dict[str, str]]] = defaultdict(list)
    events_by_record: dict[str, list[dict[str, str]]] = defaultdict(list)
    boundaries_by_record: dict[str, list[dict[str, object]]] = defaultdict(list)
    for field in fields:
        fields_by_record[field["record_unit_id"]].append(field)
    for event in events:
        events_by_record[event["record_unit_id"]].append(event)
    for boundary in boundary_rows:
        boundaries_by_record[str(boundary["record_unit_id"])].append(boundary)

    record_rows: list[dict[str, object]] = []
    for record in record_order:
        canonical = record_by_unit[record]
        record_fields = fields_by_record[record]
        record_events = events_by_record[record]
        record_statements = [row for row in statement_rows if row["record_unit_id"] == record]
        record_boundaries = boundaries_by_record[record]
        anchor_counter = Counter(
            event["ATOMIC_OR_WHOLE_CARD_MNEMONIC"]
            for event in record_events
            if event["joint_tuple_id"] in decision_by_id
        )
        anchor_inventory = ";".join(
            f"{row['selected_short_mnemonic']}={anchor_counter[row['selected_short_mnemonic']]}"
            for row in decisions
            if anchor_counter[row["selected_short_mnemonic"]]
        ) or "NONE"
        boundary_profile = Counter(str(row["decision"]) for row in record_boundaries)
        if record.startswith("H"):
            source_structure = "BILDLEMMA_PLUS_HERBAL_ARTICLE_PLUS_PARATACTIC_RECIPE"
            historical_analogy = "Kompilierter Simplexartikel mit still erhaltenem Bildbesitzer, Recipe/Item-Fortsetzungen und de-eodem-artiger Wiederaufnahme; nur Strukturvergleich."
            silent_inventory = "Bildbesitzer; konkrete Pflanze und Teile; Habitat und Sammelzeit; Wasser/Wein/Öl/Honig; Indikation; Artikel, Pronomen und Flexion."
        else:
            source_structure = "PICTURED_BATH_OR_VESSEL_OWNER_PLUS_PARALLEL_SHORT_WORKCELLS"
            historical_analogy = "Bade-, Wasch- oder Gefäßregimen mit kurzen Arbeitszellen, fortgeltender Flüssigkeit/Station und parataktischen Item-Folgen; Körper und Apparat bleiben Rivalen."
            silent_inventory = "Bildbesitzer Apparat oder Patient; Gefäß, Lauf und Öffnung; konkrete Flüssigkeit; Reihenfolge, Wiederholung und Körperziel; Artikel, Pronomen und Flexion."
        record_rows.append({
            "record_unit_id": record,
            "page": canonical["page"],
            "module": canonical["module"],
            "field_count": len(record_fields),
            "event_count": len(record_events),
            "physical_line_count": len(unique(field["locus"] for field in record_fields)),
            "statement_count": len(record_statements),
            "line_spanning_statement_count": sum(row["spans_physical_lines"] == "YES" for row in record_statements),
            "interline_boundary_count": len(record_boundaries),
            "boundary_profile": ";".join(f"{key}={boundary_profile[key]}" for key in sorted(boundary_profile)) or "NONE",
            "statement_ids": "|".join(str(row["statement_id"]) for row in record_statements),
            "formal_source_skeleton": canonical["FORMAL_VALUE"],
            "exact_short_mnemonic_inventory": anchor_inventory,
            "historical_source_structure": source_structure,
            "reconstructed_german_source_text": canonical["LOCAL_IATROMEDICAL_EXPANSION"],
            "silent_local_expansion_inventory": silent_inventory,
            "strongest_historical_analogy": historical_analogy,
            "strongest_historical_rival": canonical["NONMEDICAL_RIVAL"],
            "strongest_counterevidence": canonical["strongest_contradiction"],
            "interpretation_status": "COMPLETE_RECORD_SOURCE_RECONSTRUCTION_NOT_ATOM_BY_ATOM_TRANSLATION",
            "source_lineage": "V59_R1_CANONICAL_RECORD+FIELDS+V60_SELECTED_EXACT_DECK>V61_R2",
        })

    field_map_path = OUT / "V61_R2_135_FIELD_STATEMENT_MAP.tsv"
    statement_path = OUT / "V61_R2_121_STATEMENTS.tsv"
    boundary_path = OUT / "V61_R2_46_INTERLINE_BOUNDARIES.tsv"
    record_path = OUT / "V61_R2_11_RECORD_RECONSTRUCTIONS.tsv"
    validation_path = OUT / "V61_R2_VALIDATION.json"

    write_tsv(field_map_path, list(field_map_rows[0]), field_map_rows)
    write_tsv(statement_path, list(statement_rows[0]), statement_rows)
    write_tsv(boundary_path, list(boundary_rows[0]), boundary_rows)
    write_tsv(record_path, list(record_rows[0]), record_rows)

    boundary_counts = Counter(row["decision"] for row in boundary_rows)
    physical_lines = sum(len(unique(field["locus"] for field in fields_by_record[record])) for record in record_order)
    exact_events = [event for event in events if event["joint_tuple_id"] in decision_by_id]
    unknown_events = [event for event in events if event["joint_tuple_id"] not in decision_by_id]
    selected_values_seen = {event["ATOMIC_OR_WHOLE_CARD_MNEMONIC"] for event in exact_events}
    selected_values_expected = set(selected_by_id.values())
    source_field_expansions = {row["field_id"]: row["LOCAL_IATROMEDICAL_EXPANSION"] for row in fields}

    assertions = {
        "all_11_prose_records_present": [row["record_unit_id"] for row in record_rows] == record_order,
        "all_135_fields_mapped_once": len(field_map_rows) == 135 and len({row["field_id"] for row in field_map_rows}) == 135,
        "all_381_events_preserved": len(events) == 381 and sum(int(row["event_count"]) for row in fields) == 381,
        "all_46_interline_boundaries_catalogued": len(boundary_rows) == 46 and len(boundary_spec) == 46,
        "boundary_vocabulary_exact": set(boundary_counts) <= VALID_BOUNDARY_CLASSES,
        "physical_lines_count_57": physical_lines == 57,
        "statement_count_121": len(statement_rows) == 121,
        "line_spanning_statements_exist": any(row["spans_physical_lines"] == "YES" for row in statement_rows),
        "every_statement_has_concrete_expansion": all(row["german_source_expansion"] for row in statement_rows),
        "every_statement_has_historical_rival": all(row["strongest_historical_rival"] for row in statement_rows),
        "exact_85_vs_unknown_296_separated": len(exact_events) == 85 and len(unknown_events) == 296,
        "selected_short_mnemonics_unchanged": all(event["ATOMIC_OR_WHOLE_CARD_MNEMONIC"] == selected_by_id[event["joint_tuple_id"]] for event in exact_events),
        "no_new_short_mnemonic": selected_values_seen == selected_values_expected,
        "canonical_field_expansions_unchanged": all(row["canonical_local_expansion_unchanged"] == source_field_expansions[row["field_id"]] for row in field_map_rows),
        "same_clause_boundaries_share_statement": all((row["decision"] == "CONTINUE_SAME_CLAUSE") == (row["same_statement_after_reflow"] == "YES") for row in boundary_rows),
        "all_pages_allowlisted": all(row["page"] in ALLOWED_PAGES for row in fields + events + records),
        "guarded_sources_have_no_forbidden_rows": all(stats["skipped_forbidden"] == 0 for stats in (field_guard, event_guard, record_guard)),
        "exact_and_silent_layers_explicit": all("ONLY_BRACED_CARD=MNEMONIC_IS_EXACT" in row["silent_additions_rule"] for row in field_map_rows),
    }

    validation = {
        "status": "PASS" if all(assertions.values()) else "FAIL",
        "role": "R2_HISTORICAL_MEDICAL_HERBAL_SCRIBE",
        "decision": "PHYSICAL_LINE_IS_REFLOW_OR_CELL_BOUNDARY_NOT_AUTOMATIC_SENTENCE_END",
        "scope": {
            "allowed_pages": list(ALLOWED_PAGES),
            "prose_records": 11,
            "physical_lines": physical_lines,
            "fields": len(fields),
            "events": len(events),
            "selected_exact_cards": len(decisions),
        },
        "counts": {
            "record_reconstructions": len(record_rows),
            "field_map_rows": len(field_map_rows),
            "statement_rows": len(statement_rows),
            "interline_boundaries": len(boundary_rows),
            "intraline_field_breaks": len(fields) - physical_lines,
            "line_spanning_statements": sum(row["spans_physical_lines"] == "YES" for row in statement_rows),
            "records_with_line_spanning_statement": len({row["record_unit_id"] for row in statement_rows if row["spans_physical_lines"] == "YES"}),
            "exact_mnemonic_events": len(exact_events),
            "silent_unknown_events": len(unknown_events),
        },
        "boundary_class_counts": {key: boundary_counts[key] for key in sorted(VALID_BOUNDARY_CLASSES)},
        "per_record": {
            row["record_unit_id"]: {
                "fields": row["field_count"],
                "events": row["event_count"],
                "physical_lines": row["physical_line_count"],
                "statements": row["statement_count"],
                "interline_boundaries": row["interline_boundary_count"],
            }
            for row in record_rows
        },
        "assertions": assertions,
        "guards": {
            "field_query": field_guard,
            "event_query": event_guard,
            "record_query": record_guard,
            "forbidden_prefix": "f84",
            "f84_accessed": False,
            "f84r_accessed": False,
            "new_voynich_pages_opened": 0,
            "v61_sibling_files_read": 0,
            "sound_or_language_assignment": False,
            "page_host_or_substring_semantics": False,
        },
        "source_sha256": {
            "v59_r1_fields": sha256(FIELD_SOURCE),
            "v59_r1_records": sha256(RECORD_SOURCE),
            "v60_selected_events": sha256(EVENT_SOURCE),
            "v60_selected_decisions": sha256(DECISION_SOURCE),
        },
        "output_sha256": {
            "field_map": sha256(field_map_path),
            "statements": sha256(statement_path),
            "boundaries": sha256(boundary_path),
            "records": sha256(record_path),
        },
    }
    validation_path.write_text(json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if validation["status"] != "PASS":
        raise AssertionError(json.dumps(assertions, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

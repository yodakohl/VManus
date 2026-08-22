#!/usr/bin/env python3
"""Build the complete V73 R1 Herbal third edition.

The builder binds the frozen V69 Herbal event inventory to the central V70
image revision, V71 whole-plant owners, and V72 selected statements.  Concrete
German values are occurrence-specific master-exemplar defaults; they never
become meanings of a surface string, tuple, card component, or stem.
"""

from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
V69 = ROOT / "experiments/yolo/sidequest_theory_candidates_v69"
V70 = ROOT / "experiments/yolo/sidequest_theory_candidates_v70"
V71 = ROOT / "experiments/yolo/sidequest_theory_candidates_v71"
V72 = ROOT / "experiments/yolo/sidequest_theory_candidates_v72"
OUT = Path(__file__).resolve().parent

CARD_PATH = V69 / "V69_R4_FINAL_173_CARD_DICTIONARY.tsv"
EVENT_PATH = V69 / "V69_R4_FINAL_381_PROSE_EVENT_INTERLINEAR.tsv"
FIELD_PATH = V69 / "V69_R4_FINAL_135_FIELD_EDITION.tsv"
IMAGE_PATH = V70 / "V70_SELECTED_TEN_PAGE_IMAGE_REVISION.tsv"
OWNER_PATH = V71 / "V71_SELECTED_OWNER_LEDGER.tsv"
STATEMENT_PATH = V72 / "V72_SELECTED_116_STATEMENTS.tsv"

EVENT_OUT = OUT / "V73_R1_100_EVENT_INTERLINEAR.tsv"
FIELD_OUT = OUT / "V73_R1_20_FIELD_EDITION.tsv"
ARTICLE_OUT = OUT / "V73_R1_FIVE_RECORD_ARTICLES.md"
VALIDATION_OUT = OUT / "V73_R1_VALIDATION.json"

HERBAL_PAGES = ("f10r", "f11r", "f55v", "f56r")
EXPECTED_OWNERS = {
    "f10r": "WHOLE_BROAD_TOOTHED_RADIAL_FLOWERED_HERB",
    "f11r": "WHOLE_DENSE_BLUE_FLOWERED_CROWN_PLANT",
    "f55v": "WHOLE_BROAD_LEAF_PANICLED_PLANT_WITH_MNEMONIC_ROOT",
    "f56r": "WHOLE_MULTIHEAD_SPINY_OR_EMBLEMATIC_HERB",
}

V70_CONSTRAINT_LABELS = {
    "f10r": "NARROW_SPECIES_AND_IMAGE_BASED_WATER_DEFAULT_WITHDRAWN",
    "f11r": "NARROW_SPECIES_DEFAULT_WITHDRAWN",
    "f55v": "NARROW_SPECIES_VISIBLE_WOUND_AND_VISIBLE_PROCESS_DEFAULTS_WITHDRAWN",
    "f56r": "NARROW_SPECIES_AND_IMAGE_BASED_REMEDY_DEFAULT_WITHDRAWN",
}


# One explicitly typed, occurrence-specific default for every frozen event.
# These are not dictionary entries.  The field lists make accidental omissions
# or reordering impossible to hide.
DEFAULTS_BY_FIELD: dict[str, list[tuple[str, str]]] = {
    "F001": [
        ("PART_ARGUMENT", "Nimm vom ganzen abgebildeten Kraut den kräftigen unteren Wurzelstock."),
        ("PREPARATION_ACTION", "Säubere ihn vollständig von Erde."),
        ("MEDIUM_ACTION", "Wasche ihn mit frischem Quellwasser."),
        ("PREPARATION_ACTION", "Schneide ihn in kleine Stücke."),
        ("VESSEL_ACTION", "Gib die Stücke in einen irdenen Topf."),
        ("MEDIUM_ACTION", "Bedecke sie mit Quellwasser."),
        ("PREPARATION_ACTION", "Koche sie gelinde und fange den ersten Auszug gesondert auf."),
        ("USE_ACTION", "Gebrauche den frischen Auszug innerlich."),
        ("MEASURE_ARGUMENT", "Nimm davon das im Exemplar vorgeschriebene kleine Maß."),
        ("INDICATION_AND_STORAGE", "Gib es bei stechendem Leibschmerz und bewahre den übrigen Wurzelstock trocken verschlossen auf."),
    ],
    "F002": [
        ("ACTIVE_ITEM_ARGUMENT", "Nimm für den zweiten Gebrauch einen frischen Anteil des ersten Auszugs."),
        ("PREPARATION_ACTION", "Erwärme ihn gelinde bis handwarm."),
        ("STATE_LINK", "Führe ihn als Fortsetzung derselben Wurzelbereitung weiter."),
        ("READINESS_CONDITION", "Gebrauche ihn, sobald der im Exemplar bezeichnete Bereitschaftszustand erreicht ist."),
    ],
    "F003": [
        ("PART_ARGUMENT", "Nimm Blütenköpfe und junge Blätter der ganzen abgebildeten Pflanze."),
        ("HARVEST_CONDITION", "Ernte sie, wenn die ersten Köpfe sich eben öffnen."),
        ("ACTIVE_ITEM_STATE", "Führe diese Ernte als ersten frischen Ansatz."),
        ("PREPARATION_ACTION", "Zerstoße das Kraut grob."),
        ("PREPARATION_ACTION", "Presse die Pflanzenflüssigkeit durch ein Leinentuch aus."),
        ("FRACTION_ARGUMENT", "Fange die erste Flüssigkeitsfraktion getrennt auf."),
        ("MEDIUM_ACTION", "Gib etwas Olivenöl hinzu."),
        ("MEASURE_ARGUMENT", "Nimm das im Exemplar vorgeschriebene Maß."),
        ("PREPARATION_ACTION", "Erwärme den Ansatz gelinde."),
    ],
    "F004": [
        ("PART_ARGUMENT", "Nimm vor voller Blüte eine zweite Portion der Spitzen."),
        ("ACTIVE_ITEM_STATE", "Halte den ersten Presssaft als laufenden Ansatz bereit."),
        ("MEASURE_ARGUMENT", "Nimm von der zweiten Ernte eine Handvoll."),
        ("STATE_LINK", "Verknüpfe diese Portion im Register mit dem laufenden Ansatz."),
        ("PREVIOUS_ITEM_STATE", "Nimm den vorigen Ansatz zum Vergleich wieder auf."),
        ("STATE_LINK", "Führe beide Ansätze im Register als zusammengehöriges Vergleichspaar."),
        ("MEASURE_ARGUMENT", "Bemesse beide mit demselben im Exemplar vorgeschriebenen Maß."),
        ("PREPARATION_ACTION", "Verarbeite beide getrennt auf dieselbe Weise."),
    ],
    "F005": [
        ("VESSEL_ACTION", "Gib die beiden Fraktionen in zwei getrennte glasierte Gefäße."),
        ("ACTIVE_ITEM_STATE", "Führe die frühere Fraktion als ersten aktiven Ansatz."),
        ("ACTIVE_ITEM_STATE", "Führe die spätere Fraktion als zweiten aktiven Ansatz."),
        ("PREPARATION_ACTION", "Rühre beide bei kleinem Feuer."),
        ("ENDPOINT_CONDITION", "Lasse beide eindicken, bis eine weiche Salbe entsteht."),
        ("STORAGE_ACTION", "Bewahre beide bedeckt auf."),
        ("USE_ACTION", "Lege die passendere Salbe äußerlich auf ein Geschwür oder eine harte Schwellung."),
    ],
    "F006": [
        ("HARVEST_ARGUMENT", "Nimm im zeitigen Frühjahr Blüten und junge Blätter der ganzen abgebildeten Pflanze."),
        ("MEDIUM_ACTION", "Koche sie in mildem Weißwein."),
        ("PREPARATION_ACTION", "Wringe den Sud durch feines Leinentuch."),
        ("PREPARATION_ACTION", "Lasse den Auszug ruhig stehen."),
        ("PREPARATION_ACTION", "Seihe ihn ein zweites Mal."),
        ("ENDPOINT_CONDITION", "Prüfe ihn, bis der im Exemplar bezeichnete klare Zustand erreicht ist."),
        ("CLOSURE_ACTION", "Lasse ihn abkühlen und schließe diesen Zubereitungsposten."),
    ],
    "F007": [
        ("RESERVE_ARGUMENT", "Behalte einen Teil der frischen Blüten für die zweite Zubereitung zurück."),
    ],
    "F008": [
        ("ACTIVE_ITEM_ARGUMENT", "Nimm den ersten klaren Auszug wieder auf."),
        ("PORTION_ACTION", "Nimm davon einen Anteil."),
        ("USE_ACTION", "Gib ihn als Trank."),
        ("INDICATION_ARGUMENT", "Verwende ihn bei bedrücktem Gemüt und beschwerter Brust."),
        ("MEASURE_ARGUMENT", "Gib nur das im Exemplar vorgeschriebene kleine Maß."),
    ],
    "F009": [
        ("RESERVE_ARGUMENT", "Nimm die zurückbehaltenen Blüten."),
        ("MEDIUM_ACTION", "Erwärme sie in Olivenöl."),
        ("READINESS_CONDITION", "Halte das Öl, bis der im Exemplar bezeichnete Bereitschaftszustand erreicht ist."),
        ("USE_ACTION", "Streiche es äußerlich um die Lider, ohne das Auge zu berühren."),
    ],
    "F010": [
        ("REGISTER_ACTION", "Setze für die ganze Pflanze einen ersten Zubereitungsposten im Register an."),
        ("MEASURE_ARGUMENT", "Nimm das vorgeschriebene Maß der breiten Blätter."),
        ("PREPARATION_ACTION", "Wasche und zerstoße die Blätter grob."),
        ("MEDIUM_ACTION", "Gib milden Weißwein hinzu."),
        ("CLOSURE_ACTION", "Verschließe das Gefäß, lasse es kühl ziehen und schließe den Posten."),
    ],
    "F011": [
        ("MEASURE_ARGUMENT", "Miss eine Portion des Ansatzes ab."),
        ("PREPARATION_ACTION", "Wringe sie durch Leinentuch und lasse den Auszug klar absetzen."),
        ("CLOSURE_ACTION", "Verwahre den klaren Auszug und schließe die getrennten Restfraktionen."),
    ],
    "F012": [
        ("USE_ACTION", "Wasche eine unreine äußere Wunde."),
        ("ACTIVE_ITEM_ARGUMENT", "Verwende dafür den klaren Auszug."),
        ("FREQUENCY_ARGUMENT", "Wasche einmal oder so oft, wie das örtliche Exemplar vorschreibt."),
        ("CLOSURE_ACTION", "Beende diesen Gebrauch und schließe den Posten."),
    ],
    "F013": [
        ("MEASURE_ARGUMENT", "Nimm ein vorgeschriebenes Maß der zurückbehaltenen Blätter."),
        ("TARGET_ARGUMENT", "Lege sie an die im Exemplar bezeichnete äußere Stelle."),
        ("PREPARATION_ACTION", "Erwärme sie gelinde."),
        ("ACTIVE_ITEM_STATE", "Führe diese Bereitung als zweiten Ansatz."),
        ("MEDIUM_ACTION", "Mische sie mit Honig."),
        ("USE_ACTION", "Lege den warmen Umschlag frisch auf."),
    ],
    "F014": [
        ("WHOLE_PLANT_ARGUMENT", "Nimm die ganze abgebildete Pflanze, deren Art hier unbenannt bleibt."),
        ("HABITAT_AND_HARVEST", "Sammle das oberirdische Kraut an einem feuchten Standort."),
        ("HARVEST_CONDITION", "Nimm es zu Beginn der Blüte."),
        ("MEASURE_ARGUMENT", "Verwende nur ein kleines, im Exemplar vorgeschriebenes Maß."),
    ],
    "F015": [
        ("PREPARATION_ACTION", "Zerstoße die frischen klebrigen Blätter."),
        ("USE_ACTION", "Lege die Masse auf die bezeichnete Stelle."),
        ("INDICATION_ARGUMENT", "Behandle damit eine einzelne Warze oder ein Hühnerauge."),
        ("USE_DURATION", "Lasse die Masse nur kurz einwirken."),
        ("TARGET_ARGUMENT", "Bestätige die örtlich bezeichnete Hautstelle als Ziel."),
    ],
    "F016": [
        ("USE_ACTION", "Nimm die Auflage wieder ab."),
        ("MEDIUM_ACTION", "Wasche die Stelle mit Wasser."),
        ("USE_CONDITION", "Wiederhole den Gebrauch nur, wenn die Haut ihn verträgt."),
        ("CLOSURE_ACTION", "Beende die äußere Anwendung und schließe den Posten."),
    ],
    "F017": [
        ("PART_ARGUMENT", "Nimm vom übrigen Kraut die blühenden Stiele."),
        ("DRYING_ACTION", "Trockne sie im Schatten."),
        ("PREPARATION_ACTION", "Zerreibe sie grob."),
        ("STORAGE_ACTION", "Verwahre sie trocken."),
    ],
    "F018": [
        ("PREPARATION_ACTION", "Setze daraus einen schwachen Auszug an."),
        ("MEDIUM_ARGUMENT", "Verwende milden Wein als Medium."),
        ("PREPARATION_ACTION", "Seihe den Auszug durch ein Tuch."),
    ],
    "F019": [
        ("MEDIUM_ACTION", "Füge dem Auszug Honig hinzu."),
        ("PREPARATION_ACTION", "Erwärme den Auszug gelinde."),
        ("USE_ACTION", "Gib ihn als Brusttrank."),
        ("INDICATION_ARGUMENT", "Verwende ihn bei trockenem Husten."),
    ],
    "F020": [
        ("SELECTED_PART_STATE", "Wähle den im Exemplar bezeichneten geöffneten Blütenteil."),
        ("DOSE_ARGUMENT", "Nimm davon je Gabe einen Anteil."),
        ("MEASURE_ARGUMENT", "Bemesse jede Gabe mit dem vorgeschriebenen kleinen Maß."),
    ],
}


FIELD_LEADS = {
    "F001": "Erste Wurzelbereitung.",
    "F002": "Zweiter Gebrauch desselben Wurzelansatzes.",
    "F003": "Erster Posten aus oberirdischen Teilen.",
    "F004": "Frühere Vergleichsernte.",
    "F005": "Parallele Salbenbereitung.",
    "F006": "Erster geklärter Auszug.",
    "F007": "Zurückbehaltene Blütenfraktion.",
    "F008": "Innerlicher Gebrauch des klaren Auszugs.",
    "F009": "Zweite äußere Bereitung.",
    "F010": "Erster Blattposten.",
    "F011": "Klärung und Verwahrung.",
    "F012": "Äußere Waschung.",
    "F013": "Zweiter Blattumschlag.",
    "F014": "Ernte und Maß.",
    "F015": "Kurze äußere Auflage.",
    "F016": "Abnahme und Nachwäsche.",
    "F017": "Trockenvorrat.",
    "F018": "Schwacher Weinauszug.",
    "F019": "Honigtrank.",
    "F020": "Einzeldosis der Blütenfraktion.",
}

FIELD_ROLES = {
    "F001": "ROOT_EXTRACTION_AND_FIRST_USE", "F002": "SECOND_WARM_USE",
    "F003": "FIRST_AERIAL_HARVEST", "F004": "EARLY_HARVEST_COMPARISON",
    "F005": "PARALLEL_SALVE_AND_USE", "F006": "WINE_EXTRACTION_AND_CLARIFICATION",
    "F007": "RESERVED_FLOWER_PORTION", "F008": "INTERNAL_DOSE",
    "F009": "OIL_PREPARATION_AND_EXTERNAL_USE", "F010": "FIRST_LEAF_MACERATION",
    "F011": "CLARIFY_AND_STORE", "F012": "EXTERNAL_WASH",
    "F013": "HONEY_LEAF_POULTICE", "F014": "HARVEST_AND_MEASURE",
    "F015": "SHORT_SKIN_APPLICATION", "F016": "APPLICATION_AFTERCARE",
    "F017": "DRIED_RESERVE", "F018": "WEAK_WINE_EXTRACT",
    "F019": "HONEY_CHEST_DRINK", "F020": "FLOWER_PORTION_DOSE",
}

ARTICLE_TITLES = {
    "H1": "Unbenannte f10r-Pflanze — Wurzelbereitung",
    "H2": "Unbenannte f10r-Pflanze — zwei Erntezustände der oberirdischen Teile",
    "H3": "Unbenannte f11r-Pflanze — geklärter Auszug und zurückbehaltene Blüten",
    "H4": "Unbenannte f55v-Pflanze — Blattansatz, Waschung und Umschlag",
    "H5": "Unbenannte f56r-Pflanze — äußere Kurzauflage und getrockneter Vorrat",
}

ARTICLE_RIVALS = {
    "H1": "Pflanzenmaterial-Protokoll: Wurzelmaterial waschen, mazerieren, eine Prüfportion abnehmen und den Rest als Charge lagern.",
    "H2": "Vergleichsprotokoll zweier Erntechargen: frühe und späte Fraktion gleich bearbeiten, vergleichen und getrennt verwahren.",
    "H3": "Extrakt- und Musterprotokoll: Pflanzenmaterial zweimal seihen, Referenzfraktion zurücklegen und Flüssigkeitsproben bemessen.",
    "H4": "Blattfraktions-Protokoll: zwei Flotten herstellen, klären, vergleichen und als Wasch- oder Materialposten lagern.",
    "H5": "Beschichtungs-/Materialprotokoll: klebrige Pflanzenfraktion prüfen, Trockenmaterial lagern und eine gebundene Masse herstellen.",
}

ARTICLE_CONTRADICTIONS = {
    "H1": "Das Bild bezeichnet weder Wurzelteil, Quellwasser, Topf, innerlichen Gebrauch, Leibschmerz noch Maß.",
    "H2": "Das Bild bezeichnet weder Erntezeit, Presssaft, Öl, Vergleichspaar, Salbe noch Schwellung.",
    "H3": "Das Bild bezeichnet weder Frühjahr, Wein, Tuch, Trank, Gemüts-/Brustbeschwerde, Öl noch Lidbereich.",
    "H4": "Das Bild bezeichnet weder Blattwahl, Wein, Gefäß, Wunde, Honig noch äußere Zielstelle; die Texttaschen sind keine sichtbaren Teiletiquetten.",
    "H5": "Das Bild identifiziert weder Art, feuchten Standort, klebrige Blätter, Hautziel, Wein, Honig, Husten noch Dosis.",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t",
                                lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def unique(items: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for item in items:
        if item and item not in seen:
            seen.add(item)
            out.append(item)
    return out


def local_rival(text: str) -> str:
    values = re.findall(r"\bLOCAL\[([^\]]+)\]", text)
    value = values[-1] if values else text
    value = re.sub(r"\s+", " ", value).strip(" ;.")
    return value + "."


def source_layer(event: dict[str, str]) -> str:
    card = event["selected_exact_mnemonic"] not in {"", "NONE", "UNKNOWN"}
    formal = event["strict_formal_prompt"] not in {"", "NONE", "UNKNOWN"}
    terminal = event["terminal_status"] == "TERMINAL"
    if card and formal:
        return "KNOWN_CARD_AND_FORMAL_WITH_EXEMPLAR_FILL"
    if card:
        return "KNOWN_CARD_WITH_EXEMPLAR_FILL"
    if formal:
        return "KNOWN_FORMAL_WITH_EXEMPLAR_FILL"
    if terminal:
        return "FORMAL_CLOSURE_MARKER_WITH_EXEMPLAR_FILL"
    return "EXEMPLAR_ONLY"


def confidence(event: dict[str, str], slot: str, default: str) -> tuple[str, str]:
    score = 0.45
    if event["parse_status"] != "UNPARSED_EXEMPLAR":
        score = 0.62
    if event["strict_formal_prompt"] not in {"", "NONE", "UNKNOWN"}:
        score += 0.04
    if event["terminal_status"] == "TERMINAL":
        score = max(score, 0.55)
    if slot in {"MEDIUM_ACTION", "MEDIUM_ARGUMENT", "HABITAT_AND_HARVEST",
                "INDICATION_ARGUMENT", "INDICATION_AND_STORAGE", "USE_ACTION"}:
        score -= 0.10
    if slot in {"PART_ARGUMENT", "HARVEST_ARGUMENT", "RESERVE_ARGUMENT",
                "WHOLE_PLANT_ARGUMENT", "SELECTED_PART_STATE"}:
        score -= 0.06
    score = min(0.70, max(0.28, round(score, 2)))
    label = ("MEDIUM_HIGH_INTERNAL" if score >= 0.62 else
             "MEDIUM_INTERNAL" if score >= 0.50 else
             "LOW_MEDIUM_INTERNAL" if score >= 0.38 else "LOW_INTERNAL")
    return f"{score:.2f}", label


def contradiction(event: dict[str, str], slot: str) -> str:
    notes: list[str] = []
    card = event["selected_exact_mnemonic"]
    prompt = event["strict_formal_prompt"]
    if card not in {"", "NONE", "UNKNOWN"}:
        notes.append(f"{card} ist nur der bestehende unsichere Ganzkarten-Merksatz, keine bestätigte Wortbedeutung")
    if prompt not in {"", "NONE", "UNKNOWN"}:
        notes.append(f"{prompt} ist eine formale Slotanweisung, keine Übersetzung")
    if event["terminal_status"] == "TERMINAL":
        notes.append("der Schlussmarker stützt nur Feldabschluss, nicht die konkrete Schlussaktion")
    if slot in {"PART_ARGUMENT", "HARVEST_ARGUMENT", "RESERVE_ARGUMENT", "SELECTED_PART_STATE"}:
        notes.append("keine Leiterlinie weist diesem Feld den genannten Pflanzenteil sichtbar zu")
    if slot in {"MEDIUM_ACTION", "MEDIUM_ARGUMENT", "VESSEL_ACTION"}:
        notes.append("Medium, Wasser, Wein, Öl, Honig, Tuch oder Gefäß sind nicht abgebildet")
    if slot in {"INDICATION_ARGUMENT", "INDICATION_AND_STORAGE", "USE_ACTION",
                "TARGET_ARGUMENT", "USE_DURATION", "USE_CONDITION"}:
        notes.append("Indikation, Gebrauch und Zielstelle sind nicht abgebildet")
    if slot == "HABITAT_AND_HARVEST":
        notes.append("Standort und Erntezeit sind nicht abgebildet")
    if not notes:
        notes.append("der konkrete Wert ist ein occurrence-spezifischer Masterexemplar-Default; das Bild stützt nur den Ganzpflanzenartikel")
    return "; ".join(unique(notes)) + "."


def literal_layer(event: dict[str, str], card_row: dict[str, str]) -> str:
    card = event["selected_exact_mnemonic"]
    prompt = event["strict_formal_prompt"]
    return " | ".join([
        f"EXACT_CARD_ID={event['joint_tuple_id']}",
        f"SURFACE_DISPLAY_ONLY={event['surface_display_only']}",
        f"OPAQUE_FORMULA={event['formal_formula_opaque']}",
        f"KNOWN_CARD={card if card not in {'', 'NONE', 'UNKNOWN'} else 'NONE'}",
        f"KNOWN_FORMAL={prompt if prompt not in {'', 'NONE', 'UNKNOWN'} else 'NONE'}",
        f"TERMINAL={event['terminal_status']}",
        f"V69_CONTROL_CLASS={card_row['V69_FINAL_CONTROL_CLASS']}",
    ])


def build() -> dict[str, object]:
    cards = read_tsv(CARD_PATH)
    all_events = read_tsv(EVENT_PATH)
    all_fields = read_tsv(FIELD_PATH)
    images = read_tsv(IMAGE_PATH)
    all_owners = read_tsv(OWNER_PATH)
    all_statements = read_tsv(STATEMENT_PATH)

    events = [r for r in all_events if r["page"] in HERBAL_PAGES]
    fields = [r for r in all_fields if r["page"] in HERBAL_PAGES]
    owner_rows = [r for r in all_owners if r["unit_kind"] == "PROSE_FIELD" and r["page"] in HERBAL_PAGES]
    statements = [r for r in all_statements if r["page"] in HERBAL_PAGES]
    image_rows = [r for r in images if r["page"] in HERBAL_PAGES]

    card_by_id = {r["joint_tuple_id"]: r for r in cards}
    owner_by_field = {r["unit_id"]: r for r in owner_rows}
    statement_by_id = {r["statement_id"]: r for r in statements}
    image_by_page = {r["page"]: r for r in image_rows}
    events_by_field: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        events_by_field[event["field_id"]].append(event)
    for values in events_by_field.values():
        values.sort(key=lambda r: int(r["event_serial"]))

    event_rows: list[dict[str, object]] = []
    for field in fields:
        field_id = field["field_id"]
        field_events = events_by_field[field_id]
        defaults = DEFAULTS_BY_FIELD[field_id]
        if len(field_events) != len(defaults):
            raise ValueError(f"default/event mismatch in {field_id}: {len(defaults)} != {len(field_events)}")
        owner = owner_by_field[field_id]
        for event, (slot, default) in zip(field_events, defaults):
            card_row = card_by_id[event["joint_tuple_id"]]
            score, label = confidence(event, slot, default)
            event_rows.append({
                "event_serial": event["event_serial"],
                "page": event["page"],
                "locus": event["locus"],
                "record_unit_id": event["record_unit_id"],
                "field_id": field_id,
                "statement_id": event["statement_id"],
                "exact_card_id": event["joint_tuple_id"],
                "surface_display_only": event["surface_display_only"],
                "literal_exact_card_layer": literal_layer(event, card_row),
                "v71_whole_plant_owner": owner["selected_visible_owner"],
                "owner_status": owner["owner_status"],
                "default_slot_type": slot,
                "concrete_german_default": default,
                "source_layer": source_layer(event),
                "known_card": event["selected_exact_mnemonic"] if event["selected_exact_mnemonic"] not in {"", "NONE", "UNKNOWN"} else "NONE",
                "known_formal_prompt": event["strict_formal_prompt"] if event["strict_formal_prompt"] not in {"", "NONE", "UNKNOWN"} else "NONE",
                "parse_status": event["parse_status"],
                "terminal_status": event["terminal_status"],
                "working_confidence": score,
                "confidence_label": label,
                "confidence_scope": "INTERNAL_THIRD_EDITION_COHERENCE_NOT_DECIPHERMENT_PROBABILITY",
                "strongest_alternative": local_rival(event["practical_source_segment"]),
                "contradiction": contradiction(event, slot),
                "v70_image_constraint": V70_CONSTRAINT_LABELS[event["page"]],
                "semantic_ceiling": "OCCURRENCE_SPECIFIC_EXEMPLAR_DEFAULT_NOT_CARD_STEM_WORD_OR_SPECIES_MEANING",
            })

    event_fields = [
        "event_serial", "page", "locus", "record_unit_id", "field_id", "statement_id",
        "exact_card_id", "surface_display_only", "literal_exact_card_layer",
        "v71_whole_plant_owner", "owner_status", "default_slot_type",
        "concrete_german_default", "source_layer", "known_card", "known_formal_prompt",
        "parse_status", "terminal_status", "working_confidence", "confidence_label",
        "confidence_scope", "strongest_alternative", "contradiction",
        "v70_image_constraint", "semantic_ceiling",
    ]
    write_tsv(EVENT_OUT, event_rows, event_fields)

    event_out_by_field: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in event_rows:
        event_out_by_field[str(row["field_id"])].append(row)

    field_rows: list[dict[str, object]] = []
    for index, field in enumerate(fields, start=1):
        field_id = field["field_id"]
        values = event_out_by_field[field_id]
        owner = owner_by_field[field_id]
        readable = FIELD_LEADS[field_id] + " " + " ".join(str(r["concrete_german_default"]) for r in values)
        exact_sequence = " > ".join(
            f"E{int(r['event_serial']):03d}:{r['exact_card_id']}"
            + (f"[CARD:{r['known_card']}]" if r["known_card"] != "NONE" else "")
            + (f"[FORMAL:{r['known_formal_prompt']}]" if r["known_formal_prompt"] != "NONE" else "")
            for r in values
        )
        rivals = " ".join(str(r["strongest_alternative"]) for r in values)
        field_rows.append({
            "field_row": index,
            "field_id": field_id,
            "record_unit_id": field["record_unit_id"],
            "page": field["page"],
            "locus": field["locus"],
            "statement_id": field["statement_id"],
            "event_count": field["event_count"],
            "event_serials": field["event_serials"],
            "v71_whole_plant_owner": owner["selected_visible_owner"],
            "owner_status": owner["owner_status"],
            "field_role": FIELD_ROLES[field_id],
            "literal_exact_card_sequence": exact_sequence,
            "complete_event_default_sequence": " | ".join(
                f"E{int(r['event_serial']):03d}={r['concrete_german_default']}" for r in values
            ),
            "readable_field_text": readable,
            "source_layer_counts": json.dumps(dict(sorted(Counter(str(r["source_layer"]) for r in values).items())), ensure_ascii=False, sort_keys=True),
            "minimum_working_confidence": min(float(r["working_confidence"]) for r in values),
            "mean_working_confidence": f"{sum(float(r['working_confidence']) for r in values)/len(values):.3f}",
            "strongest_alternative": rivals,
            "contradiction": " ".join(unique([str(r["contradiction"]) for r in values])),
            "v72_selected_statement_paraphrase": statement_by_id[field["statement_id"]]["selected_concrete_paraphrase"],
            "semantic_ceiling": "COMPLETE_READABLE_FIELD_IS_EXEMPLAR_EXPANSION_NOT_TRANSLATION",
        })

    field_fields = [
        "field_row", "field_id", "record_unit_id", "page", "locus", "statement_id",
        "event_count", "event_serials", "v71_whole_plant_owner", "owner_status",
        "field_role", "literal_exact_card_sequence", "complete_event_default_sequence",
        "readable_field_text", "source_layer_counts", "minimum_working_confidence",
        "mean_working_confidence", "strongest_alternative", "contradiction",
        "v72_selected_statement_paraphrase", "semantic_ceiling",
    ]
    write_tsv(FIELD_OUT, field_rows, field_fields)

    fields_by_record: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in field_rows:
        fields_by_record[str(row["record_unit_id"])].append(row)
    events_by_record: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in event_rows:
        events_by_record[str(row["record_unit_id"])].append(row)

    article_lines = [
        "# V73 R1 — fünf vollständige Herbal-Recordartikel",
        "",
        "Status: kreative dritte Herbal-Ausgabe über den festgelegten Vierseitenbestand; keine Übersetzung.",
        "",
        "Jeder Artikel trägt ausschließlich den V71-Ganzpflanzenbesitzer. Konkrete Teile, Medien, Standorte, Zubereitungen und Verwendungen sind occurrence-spezifische Werte des angenommenen Masterexemplars. Die fünf Lesefassungen enthalten gemeinsam jedes der 100 Ereignisse genau einmal.",
        "",
        "## Lehrbare Artikelschablone",
        "",
        "```text",
        "GANZPFLANZENBILD SETZEN",
        "→ unbenannten Pflanzenartikel/Record eröffnen",
        "→ Teil, Standort und Erntezeit aus dem Masterexemplar einsetzen",
        "→ Zubereitung in Ereignisreihenfolge ausschreiben",
        "→ bekannte Ganzkarte oder formalen Slot unverändert übernehmen",
        "→ Dosis/Ziel/Gebrauch/Lagerung aus dem Masterexemplar einsetzen",
        "→ CLOSE beendet nur den Feldposten",
        "→ beim nächsten Record alle Arbeitsregister zurücksetzen",
        "```",
        "",
    ]
    for record in ("H1", "H2", "H3", "H4", "H5"):
        rr = fields_by_record[record]
        er = sorted(events_by_record[record], key=lambda r: int(r["event_serial"]))
        pages = unique([str(r["page"]) for r in rr])
        owners = unique([str(r["v71_whole_plant_owner"]) for r in rr])
        controls = []
        for row in er:
            if row["known_card"] != "NONE" or row["known_formal_prompt"] != "NONE":
                bits = [f"E{int(row['event_serial']):03d}"]
                if row["known_card"] != "NONE":
                    bits.append(f"CARD:{row['known_card']}")
                if row["known_formal_prompt"] != "NONE":
                    bits.append(f"FORMAL:{row['known_formal_prompt']}")
                controls.append("/".join(bits))
        article_lines.extend([
            f"## {record} — {ARTICLE_TITLES[record]}",
            "",
            f"**Seite:** {', '.join(pages)}  ",
            f"**Besitzer:** `{owners[0]}` (`PAGE_OWNER_ONLY`)  ",
            f"**Abdeckung:** {len(rr)} Felder; {len(er)} Ereignisse; E{int(er[0]['event_serial']):03d}–E{int(er[-1]['event_serial']):03d}.",
            "",
            "### Vollständige Lesefassung",
            "",
        ])
        article_lines.extend(str(row["readable_field_text"]) + "\n" for row in rr)
        article_lines.extend([
            "### Literal erhaltene Kontrollfolge",
            "",
            (" → ".join(controls) if controls else "Keine erkannte Kontrollkarte; nur occurrence-spezifische Exemplarwerte."),
            "",
            "### Stärkste konkrete Alternative",
            "",
            ARTICLE_RIVALS[record],
            "",
            "### Härtester Widerspruch",
            "",
            ARTICLE_CONTRADICTIONS[record],
            "",
        ])
    article_lines.extend([
        "## Rückleseregel für den Lehrling",
        "",
        "Der Lehrling kann Besitzer, Ereignisfolge, bekannte Karten, Feldschluss und Recordreset zurücklesen. Er kann ohne Masterexemplar weder die unbenannte Art noch Teilwahl, Medium, Standort, Zubereitung, Indikation oder Dosis zurückgewinnen. Wiederholte Oberflächen oder Karten erben deshalb niemals automatisch den occurrence-spezifischen deutschen Satzwert.",
        "",
    ])
    ARTICLE_OUT.write_text("\n".join(article_lines), encoding="utf-8")

    banned_species = ["teufelsabbiss", "veilchen", "bärlauch", "sonnentau", "allium", "wegerich", "plantain"]
    event_text = "\n".join("\t".join(str(v) for v in r.values()) for r in event_rows).lower()
    field_text = "\n".join(str(r["readable_field_text"]) for r in field_rows).lower()
    article_text = ARTICLE_OUT.read_text(encoding="utf-8").lower()
    event_serials = [int(r["event_serial"]) for r in event_rows]
    field_ids = [str(r["field_id"]) for r in field_rows]
    statement_ids = {str(r["statement_id"]) for r in event_rows}
    recognized = [r for r in event_rows if r["parse_status"] != "UNPARSED_EXEMPLAR"]
    checks = {
        "exactly_100_events": len(event_rows) == 100,
        "event_serials_exact_1_to_100": event_serials == list(range(1, 101)),
        "exactly_20_fields": len(field_rows) == 20,
        "field_ids_exact_F001_to_F020": field_ids == [f"F{i:03d}" for i in range(1, 21)],
        "exactly_19_statements": len(statement_ids) == 19,
        "exactly_5_records": {str(r["record_unit_id"]) for r in event_rows} == {"H1", "H2", "H3", "H4", "H5"},
        "pages_exactly_fixed_four_herbal": {str(r["page"]) for r in event_rows} == set(HERBAL_PAGES),
        "all_exact_cards_in_frozen_173_dictionary": all(str(r["exact_card_id"]) in card_by_id for r in event_rows),
        "all_owners_match_central_v71_whole_plants": all(str(r["v71_whole_plant_owner"]) == EXPECTED_OWNERS[str(r["page"])] for r in event_rows),
        "all_owners_page_owner_only": all(str(r["owner_status"]) == "PAGE_OWNER_ONLY" for r in event_rows),
        "all_event_defaults_nonempty_and_concrete": all(len(str(r["concrete_german_default"])) >= 18 and str(r["concrete_german_default"]).endswith(".") for r in event_rows),
        "all_events_have_source_confidence_alternative_contradiction": all(
            all(str(r[k]) for k in ("source_layer", "working_confidence", "strongest_alternative", "contradiction")) for r in event_rows
        ),
        "recognized_parser_events_remain_29": len(recognized) == 29,
        "exemplar_only_parser_events_remain_71": len(event_rows) - len(recognized) == 71,
        "field_event_counts_match": all(int(r["event_count"]) == len(event_out_by_field[str(r["field_id"])]) for r in field_rows),
        "every_default_verbatim_in_its_field": all(
            str(event["concrete_german_default"]) in str(next(f for f in field_rows if f["field_id"] == event["field_id"])["readable_field_text"])
            for event in event_rows
        ),
        "every_field_verbatim_in_its_article": all(str(r["readable_field_text"]) in ARTICLE_OUT.read_text(encoding="utf-8") for r in field_rows),
        "five_article_headings": sum(ARTICLE_OUT.read_text(encoding="utf-8").count(f"## {r} —") for r in ("H1", "H2", "H3", "H4", "H5")) == 5,
        "species_names_absent_from_defaults_fields_articles": not any(x in event_text + field_text + article_text for x in banned_species),
        "no_new_card_labels": all(
            str(r["known_card"]) == "NONE" or str(r["known_card"]) == next(e for e in events if e["event_serial"] == r["event_serial"])["selected_exact_mnemonic"]
            for r in event_rows
        ),
    }
    validation: dict[str, object] = {
        "experiment": "V73_R1_COMPLETE_HERBAL_THIRD_EDITION",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "inputs": {
            "v69_cards": str(CARD_PATH.relative_to(ROOT)),
            "v69_events": str(EVENT_PATH.relative_to(ROOT)),
            "v69_fields": str(FIELD_PATH.relative_to(ROOT)),
            "v70_selected_image_revision": str(IMAGE_PATH.relative_to(ROOT)),
            "v71_selected_owners": str(OWNER_PATH.relative_to(ROOT)),
            "v72_selected_statements": str(STATEMENT_PATH.relative_to(ROOT)),
        },
        "counts": {
            "events": len(event_rows), "fields": len(field_rows),
            "statements": len(statement_ids), "records": len({r["record_unit_id"] for r in event_rows}),
            "recognized_parser_events": len(recognized),
            "exemplar_only_parser_events": len(event_rows) - len(recognized),
            "source_layers": dict(sorted(Counter(str(r["source_layer"]) for r in event_rows).items())),
            "known_card_occurrences": sum(r["known_card"] != "NONE" for r in event_rows),
            "known_formal_occurrences": sum(r["known_formal_prompt"] != "NONE" for r in event_rows),
            "terminal_occurrences": sum(r["terminal_status"] == "TERMINAL" for r in event_rows),
        },
        "checks": checks,
        "constraints": {
            "species_identified": False,
            "new_card_or_stem_meaning": False,
            "new_pages_read": False,
            "sealed_pages_opened": False,
            "active_v73_sibling_outputs_read": False,
            "commit_or_push": False,
        },
    }
    VALIDATION_OUT.write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return validation


if __name__ == "__main__":
    print(json.dumps(build(), ensure_ascii=False, indent=2))

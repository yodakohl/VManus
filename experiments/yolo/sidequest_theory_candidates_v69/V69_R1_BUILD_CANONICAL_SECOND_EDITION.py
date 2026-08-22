#!/usr/bin/env python3
"""Build the final R1 V69 ten-page second edition.

No semantics are induced here.  The script freezes the V60 control deck,
V61--V63 structure, V66 page-local Astro groups, and the coequal V68 content
fork, then republishes complete deterministic ledgers.
"""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent

V60_DICT = ROOT / "experiments/yolo/sidequest_theory_candidates_v60/V60_SELECTED_173_CARD_DICTIONARY.tsv"
V60_EVENTS = ROOT / "experiments/yolo/sidequest_theory_candidates_v60/V60_SELECTED_381_EVENT_LEDGER.tsv"
V60_DECISIONS = ROOT / "experiments/yolo/sidequest_theory_candidates_v60/V60_SELECTED_EXACT_CARD_DECISIONS.tsv"
V61_STATEMENTS = ROOT / "experiments/yolo/sidequest_theory_candidates_v61/V61_SELECTED_116_SOURCE_STATEMENTS.tsv"
V62_TRANSITIONS = ROOT / "experiments/yolo/sidequest_theory_candidates_v62/V62_SELECTED_116_REGISTER_TRANSITIONS.tsv"
V63_FIELDS = ROOT / "experiments/yolo/sidequest_theory_candidates_v63/V63_SELECTED_135_FIELD_SLOT_PARSE.tsv"
V63_STATEMENTS = ROOT / "experiments/yolo/sidequest_theory_candidates_v63/V63_SELECTED_116_STATEMENT_SLOT_PARSE.tsv"
V66_ASTRO = ROOT / "experiments/yolo/sidequest_theory_candidates_v66/V66_R2_395_GROUP_ASTRO_INTERLINEAR.tsv"
V67_LEDGER = ROOT / "experiments/yolo/sidequest_theory_candidates_v67/V67_R1_776_COVERAGE_LEDGER.tsv"
V67_UNITS = ROOT / "experiments/yolo/sidequest_theory_candidates_v67/V67_R1_14_UNIT_ROUNDTRIP.tsv"
V68_LEDGER = ROOT / "experiments/yolo/sidequest_theory_candidates_v68/V68_R1_776_GROUP_NONMEDICAL_LEDGER.tsv"
V68_UNITS = ROOT / "experiments/yolo/sidequest_theory_candidates_v68/V68_R1_14_UNIT_ADVERSARIAL_EDITION.tsv"
V68_CONTRADICTIONS = ROOT / "experiments/yolo/sidequest_theory_candidates_v68/V68_R1_CONTRADICTION_LEDGER.tsv"

UNIT_ORDER = ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6", "A1", "A2", "A3"]
EXPECTED_UNIT_COUNTS = {"H1": 14, "H2": 24, "H3": 17, "H4": 18, "H5": 27, "B1": 66, "B2": 62, "B3": 86, "B4": 47, "B5": 11, "B6": 9, "A1": 190, "A2": 65, "A3": 140}
ALLOWED_PAGES = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"}
PROSE_PAGES = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}
ASTRO_PAGES = {"f67r2", "f68r1", "f69v"}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if not rows:
        raise AssertionError(f"empty input {path}")
    if "page" in rows[0]:
        bad = sorted({row["page"] for row in rows if row["page"] not in ALLOWED_PAGES})
        if bad:
            raise AssertionError(f"out-of-scope page in {path.name}: {bad}")
    return rows


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str] | None = None) -> None:
    if not rows:
        raise AssertionError(f"empty output {path}")
    names = fields or list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=names, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def norm(text: str) -> str:
    return " ".join(text.split())


def short_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:20]


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ids(serials: str) -> list[int]:
    return [int(value) for value in serials.split("|") if value]


def content_classes(unit: str) -> tuple[str, str]:
    if unit.startswith("H"):
        return "SIMPLE", "MATERIAL"
    if unit.startswith("B"):
        return "BATH", "PROCESS"
    return "ELECTION", "SCHEDULE"


CONCISE = {
    "H1": (
        "Nimm den Wurzelstock der abgebildeten Simple, reinige und zerkleinere ihn, gewinne einen ersten wässrigen Lauf, verwende ihn in kleiner bemessener Gabe und erwärme den zurückbehaltenen Posten für einen zweiten Gebrauch.",
        "Ziehe aus dem abgebildeten Wurzelkraut eine milde Lauge, kläre und bemesse sie, prüfe sie an Leinen, reinige damit Tücher und Wannen und lagere einen zweiten Lauf getrennt.",
    ),
    "H2": (
        "Verarbeite frühe und spätere Blüten-/Blattfraktionen derselben Simple, verbinde sie recordlokal mit Öl zu einem warm gerührten äußeren Ansatz und verwahre ihn bedeckt.",
        "Gewinne zwei Pflanzenfarbfraktionen, gleiche sie am Probestreifen ab und teile sie zwischen kleinem Färbebad und einer Öl-/Wachspaste für Holz oder Leder.",
    ),
    "H3": (
        "Bereite aus der abgebildeten Duftsimple einen zweimal geklärten Wein-Auszug als kleine Gabe und aus zurückbehaltenen Blüten ein gelinde erwärmtes äußeres Öl.",
        "Bereite einen klaren Duftauszug für das letzte Wäschespülwasser und ein getrenntes Blütenöl für Kämme, Lederzeug und Badhausbänke.",
    ),
    "H4": (
        "Setze aus breiten Blättern einen geklärten Auszug zur äußeren Wäsche an und bereite aus dem Rest mit Honig einen warmen Blattumschlag.",
        "Nutze den geklärten Breitblatt-Auszug zum Reinigen von Tuch und Becken und binde den erwärmten Rest mit Honig zu einer dünnen Holz-/Lederpaste.",
    ),
    "H5": (
        "Wende wenig frisches klebriges Kraut kurz an einer bezeichneten Hautstelle an, wasche nach, trockne den Rest und gib einen kleinen bemessenen Anteil eines Wein-Honig-Auszuges als Brusttrank.",
        "Prüfe wenig Klebkraut kurz an Stoff oder Leder, wasche nach, trockne den Rest und bereite daraus portionsweise Etikettenleim oder Gefäßmarkierpaste.",
    ),
    "B1": (
        "Setze und temperiere eine Kräuter-Badeflotte, verteile sie auf Becken, halte Teilposten aktiv, prüfe Zustand und Füllung und beende den Behandlungsgang mit Spülen und Ablassen.",
        "Beschicke morgens den Badhauskreislauf, setze und filtere Pflanzenwasser, temperiere und verteile es, fülle nach und reinige, entleere und buche die Anlage nach dem Dienst.",
    ),
    "B2": (
        "Bereite ein temperiertes Teil- oder Sitzbad, filtriere die Charge, führe sie an den bezeichneten Körperbereich, gib eine warme Waschung oder Tuchauflage und lasse anschließend ab.",
        "Reinige ein Einzelbecken, bereite gefiltertes Duftwasser, halte Füllung und Wärme für den Badgast, reiche ein Reinigungstuch und spüle und trockne die Station danach.",
    ),
    "B3": (
        "Führe einen langen warmen Bad-/Lavagezyklus: setzen, klare Fraktion abziehen, warm nachspeisen, verteilen, unten fangen, erneut klären, rückführen und abschließend spülen und ablassen.",
        "Führe den langen Badhaus-Wartungszyklus: Strang isolieren, gebraucht ablassen, setzen, klar abziehen, frisch nachfüllen, filtern, verteilen, einmal rückspülen und Leitungen trocknen.",
    ),
    "B4": (
        "Temperiere einen Anteil, führe ihn durch Tuch, wasche die bezeichnete äußere Haut- oder Wundstelle, lege warm auf und reinige und entleere danach den Arbeitsgang.",
        "Reinige Filtertuch, Beckenrand, Sitzbrett und Zulauf mit einem temperierten Anteil, löse Ablagerungen, spüle und entleere die Leitung und trockne die Tücher getrennt.",
    ),
    "B5": (
        "Ziehe den Restposten ab, erwärme ihn einmal, halte ihn für die örtliche Frist, verbinde ihn mit dem vorigen B5-Posten und übergib ihn bemessen an die nächste Station.",
        "Ziehe die Servicecharge ab, erwärme sie genau einmal, prüfe sie nach der Haltefrist, verbinde sie nur bei gleicher Qualität und notiere die bemessene Übergabe.",
    ),
    "B6": (
        "Eröffne recordlokal einen kalten gefilterten Posten, bemesse ihn und übergib ihn an die bezeichnete Behandlungsstation; greife nicht auf B5 zurück.",
        "Eröffne nach vollständigem Reset eine kalte Spülreserve, miss und filtere sie, leite sie zum Zielkasten und lasse sie dort offen für den nächsten Dienst bereit.",
    ),
    "A1": (
        "Wähle aus sieben Planeten, zwölf Tierkreis-/Körpersektoren und acht Bedingungen, ob ein bereits bestimmtes Bad, eine Gabe, Anwendung, Ruhe oder Entleerung erlaubt, gemildert oder verschoben wird.",
        "Wähle einen von sieben Werkstatttagen, eine von zwölf Arbeitsklassen und eine von acht Material-/Wasser-/Wetterbedingungen; erlaube, verkleinere oder verschiebe die Arbeit.",
    ),
    "A2": (
        "Lies das Zentrum als Mondkatalog-Besitzer und jede der 28 äußeren Sternstellen als eigene Mondhausadresse; Namen, Start und Richtung kommen nur aus dem lokalen Exemplar.",
        "Lies das Zentrum als Monatsdienstblatt und jede der 28 äußeren Stellen als eigene Arbeitsadresse für Brunnen, Feuer, Kräuter, Filter, Becken, Wäsche, Vorrat oder Rechnung.",
    ),
    "A3": (
        "Lies die Kreisrubriken als Anleitung und die 28 Radialeinträge als unabhängige Wahlregeln für Bad, Waschung, Salbung, Ruhe, Maß, Entleerung oder Verschiebung.",
        "Lies die Kreisrubriken als Anleitung und die 28 Radialeinträge als unabhängige Regeln für Ernte, Trocknung, Färben, Filtern, Heizen, Badedienst, Reinigung und Vorrat.",
    ),
}

IATRO_WORKFLOW = {
    "H1": "Bildowner > Wurzel reinigen/zerkleinern > wässrigen Lauf gewinnen > MASS/ANWENDEN > Rest halten > LINK/BEREIT",
    "H2": "Frühfraktion > pressen > Öl/MASS > Spätfraktion > H2-PREVIOUS > verbinden > warm rühren > äußerlich anwenden/lagern",
    "H3": "Blütenauszug > zweimal klären > Teil als kleine Gabe > Restblüten in Öl > BEREIT prüfen > äußerlich anwenden",
    "H4": "Blattauszug > filtern > äußere Wäsche > Restanteil temperieren > Honigansatz > warmer Umschlag",
    "H5": "kleine Frischmenge > kurze Zielanwendung > abwaschen/abbrechen > Rest trocknen > Wein-Honig-Auszug > Anteil/MASS",
    "B1": "Badeflotte setzen > messen/linken > temperieren/prüfen > Becken verteilen > nachfüllen > spülen/ablassen",
    "B2": "Teilbadcharge > filtern/temperieren > Zielbereich > warme Waschung/Tuch > kühler Schluss > ablassen",
    "B3": "setzen > klare Fraktion > warm nachspeisen > verteilen > fangen > erneut klären/rückführen > spülen/ablassen",
    "B4": "Anteil temperieren > Tuchfilter > Haut-/Wundwäsche > warme Auflage > spülen/ablassen/nachfüllen",
    "B5": "Rest abziehen > einmal erwärmen > halten > PREVIOUS verbinden > bemessen > nächste Station",
    "B6": "Recordreset > kalten Posten > MASS > einfach filtern > TARGET übergeben > offen enden",
    "A1": "Planet > Zeichen/Körpersektor > acht Bedingungen > Eingriff erlauben, mildern oder verschieben",
    "A2": "Mondzentrum > eine räumliche 28er-Adresse > lokalen Hauswert nachschlagen; Rotation exemplarabhängig",
    "A3": "Rubrik > eine unabhängige 28er-Wahlregel > medizinische Arbeit ausführen; kein A2-Paarindex",
}


def main() -> None:
    dictionary_source = read_tsv(V60_DICT)
    event_source = read_tsv(V60_EVENTS)
    decisions = read_tsv(V60_DECISIONS)
    statement_source = read_tsv(V61_STATEMENTS)
    transitions = read_tsv(V62_TRANSITIONS)
    field_source = read_tsv(V63_FIELDS)
    statement_parses = read_tsv(V63_STATEMENTS)
    astro_source = read_tsv(V66_ASTRO)
    v67_ledger = read_tsv(V67_LEDGER)
    v67_units = read_tsv(V67_UNITS)
    v68_ledger = read_tsv(V68_LEDGER)
    v68_units = read_tsv(V68_UNITS)
    v68_contradictions = read_tsv(V68_CONTRADICTIONS)

    assert len(dictionary_source) == 173 and len(event_source) == 381
    assert len(statement_source) == len(transitions) == len(statement_parses) == 116
    assert len(field_source) == 135 and len(astro_source) == 395
    assert len(v67_ledger) == len(v68_ledger) == 776
    assert len(v67_units) == len(v68_units) == len(v68_contradictions) == 14

    event_by_serial = {int(row["event_serial"]): row for row in event_source}
    v67_by_global = {int(row["universal_group_serial"]): row for row in v67_ledger}
    v68_by_global = {int(row["universal_group_serial"]): row for row in v68_ledger}
    mnemonic_by_id = {row["joint_tuple_id"]: row for row in decisions}
    assert len(mnemonic_by_id) == 11

    formal_events = [row for row in event_source if row["strict_control_prompt"] != "NONE"]
    formal_prompts_by_id: dict[str, set[str]] = defaultdict(set)
    for row in formal_events:
        formal_prompts_by_id[row["joint_tuple_id"]].add(row["strict_control_prompt"])
    assert len(formal_prompts_by_id) == 4 and all(len(values) == 1 for values in formal_prompts_by_id.values())
    formal_count_by_id = Counter(row["joint_tuple_id"] for row in formal_events)

    dictionary_rows: list[dict[str, object]] = []
    dictionary_status_by_id: dict[str, str] = {}
    mnemonic_value_by_id: dict[str, str] = {}
    formal_value_by_id: dict[str, str] = {}
    for source in sorted(dictionary_source, key=lambda row: row["joint_tuple_id"]):
        card_id = source["joint_tuple_id"]
        decision = mnemonic_by_id.get(card_id)
        mnemonic = decision["selected_short_mnemonic"] if decision else "UNKNOWN_EXEMPLAR"
        formal_control = next(iter(formal_prompts_by_id[card_id])) if card_id in formal_prompts_by_id else "NONE"
        if decision and formal_control != "NONE":
            status = "MNEMONIC_AND_FORMAL_CONTROL"
        elif decision:
            status = "MNEMONIC_ONLY"
        elif formal_control != "NONE":
            status = "FORMAL_CONTROL_ONLY"
        else:
            status = "UNKNOWN_EXEMPLAR"
        dictionary_status_by_id[card_id] = status
        mnemonic_value_by_id[card_id] = mnemonic
        formal_value_by_id[card_id] = formal_control
        dictionary_rows.append({
            "joint_tuple_id": card_id,
            "surface_examples_display_only": source["surface_examples"],
            "occurrences": source["occurrences"],
            "pages": source["pages"],
            "observed_formal_formula_opaque": source["formal_formula_opaque"],
            "FORMAL_CONTROL": formal_control,
            "formal_control_event_count": formal_count_by_id.get(card_id, 0),
            "ATOMIC_OR_WHOLE_CARD_MNEMONIC": mnemonic,
            "mnemonic_occurrence_count": int(decision["occurrences"]) if decision else 0,
            "mnemonic_source_class": decision["source_class"] if decision else "UNKNOWN",
            "strongest_mnemonic_rival": decision["strongest_live_rival"] if decision else "NONE_EXEMPLAR_REQUIRED",
            "dictionary_status": status,
            "local_content_binding": "EXCLUDED_FROM_DICTIONARY; SEE_OCCURRENCE_EXEMPLARS",
            "identity_contract": "EXACT_JOINT_TUPLE_ATOMIC; NO_PAGE_HOST_STRING_COMPONENT_OR_SURFACE_INHERITANCE",
            "interpretation_status": "CREATIVE_CONTROL_NOT_TRANSLATION" if status != "UNKNOWN_EXEMPLAR" else "UNKNOWN_EXEMPLAR",
        })
    write_tsv(OUT / "V69_R1_173_EXACT_CARD_DICTIONARY.tsv", dictionary_rows)

    prose_events: list[dict[str, object]] = []
    for serial in range(1, 382):
        source = event_by_serial[serial]
        v67 = v67_by_global[serial]
        v68 = v68_by_global[serial]
        assert v67["register"] != "ASTRO" and v68["register"] != "ASTRO"
        assert source["joint_tuple_id"] == v67["exact_card_or_local_group_id"] == v68["exact_card_or_local_group_id"]
        assert source["page"] == v67["page"] == v68["page"]
        card_id = source["joint_tuple_id"]
        iatro_class, practical_class = content_classes(source["record_unit_id"])
        prose_events.append({
            "event_serial": serial,
            "page": source["page"],
            "locus": source["locus"],
            "record_unit_id": source["record_unit_id"],
            "field_id": source["field_id"],
            "statement_id": v67["statement_or_station"],
            "event_index_in_record": source["event_index_in_record"],
            "joint_tuple_id": card_id,
            "surface_display_only": source["surface"],
            "formal_formula_opaque": source["formal_formula_opaque"],
            "FORMAL_VALUE": source["FORMAL_VALUE"],
            "FORMAL_CONTROL_AT_THIS_EVENT": source["strict_control_prompt"],
            "ATOMIC_OR_WHOLE_CARD_MNEMONIC": mnemonic_value_by_id[card_id],
            "dictionary_status": dictionary_status_by_id[card_id],
            "terminal_status": source["terminal_status"],
            "v63_source_order_slot": v67["source_order_slot"],
            "v63_parse_status": v67["selected_parse_status"],
            "register_state_before": v67["register_state_before"],
            "register_update": v67["register_update"],
            "register_state_after": v67["register_state_after"],
            "iatromedical_content_class": iatro_class,
            "IATROMEDICAL_SIMPLE_BATH_ELECTION": v68["iatromedical_selected_local_expansion"],
            "practical_content_class": practical_class,
            "PRACTICAL_MATERIAL_PROCESS_SCHEDULE": v68["nonmedical_rival_local_expansion"],
            "content_preference": "COEQUAL",
            "content_status": "BOTH_RECORD_LOCAL_EXEMPLARS; NOT_CARD_VALUES",
            "renderer_instruction": v68["renderer_instruction"],
            "semantic_contract": "EXACT_ID_FORMAL_MNEMONIC_LOCAL_CONTENT_SEPARATE; NO_NEW_SEMANTICS",
        })
    write_tsv(OUT / "V69_R1_381_PROSE_EVENT_INTERLINEAR.tsv", prose_events)

    prose_by_serial = {int(row["event_serial"]): row for row in prose_events}
    fields: list[dict[str, object]] = []
    for source in field_source:
        event_rows = [prose_by_serial[value] for value in ids(source["event_serials"])]
        skeleton = []
        for row in event_rows:
            parts = []
            if row["FORMAL_CONTROL_AT_THIS_EVENT"] != "NONE":
                parts.append(f"FORMAL:{row['FORMAL_CONTROL_AT_THIS_EVENT']}")
            if row["ATOMIC_OR_WHOLE_CARD_MNEMONIC"] != "UNKNOWN_EXEMPLAR":
                parts.append(f"MNEMONIC:{row['ATOMIC_OR_WHOLE_CARD_MNEMONIC']}")
            skeleton.append("+".join(parts) if parts else "UNKNOWN_EXEMPLAR")
        fields.append({
            "field_id": source["field_id"], "record_unit_id": source["record_unit_id"], "page": source["page"],
            "locus": source["locus"], "statement_id": source["statement_id"],
            "field_position_in_statement": source["field_position_in_statement"], "event_count": source["event_count"],
            "event_serials": source["event_serials"],
            "exact_joint_tuple_sequence": "|".join(str(row["joint_tuple_id"]) for row in event_rows),
            "selected_control_skeleton": " > ".join(skeleton),
            "primary_template": source["primary_template"], "parse_status": source["parse_status"],
            "recognized_event_count": source["recognized_event_count"], "exemplar_only_event_count": source["exemplar_only_event_count"],
            "register_pre_state": source["register_pre_state_statement_envelope"],
            "register_update_trace": source["register_update_trace"],
            "register_post_state": source["register_post_state_statement_envelope"],
            "IATROMEDICAL_SIMPLE_BATH": " ; ".join(str(row["IATROMEDICAL_SIMPLE_BATH_ELECTION"]) for row in event_rows),
            "PRACTICAL_MATERIAL_PROCESS": " ; ".join(str(row["PRACTICAL_MATERIAL_PROCESS_SCHEDULE"]) for row in event_rows),
            "content_preference": "COEQUAL", "opaque_roundtrip_status": source["roundtrip_status"],
            "semantic_contract": "FIELD_STRUCTURE_SELECTED; BOTH_CONTENTS_LOCAL_EXEMPLARS",
        })
    write_tsv(OUT / "V69_R1_135_FIELD_DUAL_EDITION.tsv", fields)

    transition_by_id = {row["statement_id"]: row for row in transitions}
    parse_by_id = {row["statement_id"]: row for row in statement_parses}
    statements: list[dict[str, object]] = []
    for source in statement_source:
        sid = source["statement_id"]
        transition = transition_by_id[sid]
        parse = parse_by_id[sid]
        event_rows = [prose_by_serial[value] for value in ids(source["event_serials"])]
        statements.append({
            "statement_id": sid, "record_unit_id": source["record_unit_id"], "page": source["page"],
            "statement_ordinal_in_record": source["statement_ordinal_in_record"],
            "start_locus": source["start_locus"], "start_field": source["start_field"],
            "end_locus": source["end_locus"], "end_field": source["end_field"],
            "constituent_loci": source["constituent_loci"], "constituent_fields": source["constituent_fields"],
            "physical_line_count": source["physical_line_count"], "event_count": source["event_count"],
            "event_serials": source["event_serials"],
            "exact_joint_tuple_sequence": "|".join(str(row["joint_tuple_id"]) for row in event_rows),
            "entry_boundary_class": source["entry_boundary_class"], "exit_boundary_class": source["exit_boundary_class"],
            "internal_cross_line_boundaries": source["internal_cross_line_boundaries"],
            "selected_short_card_skeleton": source["selected_short_card_skeleton"],
            "v63_primary_template": parse["primary_template"], "v63_parse_status": parse["parse_status"],
            "recognized_event_count": parse["recognized_event_count"], "exemplar_only_event_count": parse["exemplar_only_event_count"],
            "register_pre_state": transition["pre_state"], "register_operation_trace": transition["operation_trace"],
            "register_post_state": transition["post_state"], "irreducible_ambiguity_codes": transition["irreducible_ambiguity_codes"],
            "IATROMEDICAL_SIMPLE_BATH": " ; ".join(str(row["IATROMEDICAL_SIMPLE_BATH_ELECTION"]) for row in event_rows),
            "PRACTICAL_MATERIAL_PROCESS": " ; ".join(str(row["PRACTICAL_MATERIAL_PROCESS_SCHEDULE"]) for row in event_rows),
            "strongest_segmentation_alternative": source["strongest_alternative"],
            "apprentice_reading_rule": source["apprentice_reading_rule"],
            "content_preference": "COEQUAL", "opaque_roundtrip_status": parse["roundtrip_status"],
            "semantic_contract": "PHYSICAL_LINE_NOT_SENTENCE; BOTH_CONTENTS_LOCAL_EXEMPLARS",
        })
    write_tsv(OUT / "V69_R1_116_STATEMENT_DUAL_EDITION.tsv", statements)

    astro_by_serial = {int(row["group_serial"]): row for row in astro_source}
    astro_groups: list[dict[str, object]] = []
    for group_serial in range(1, 396):
        source = astro_by_serial[group_serial]
        v68 = v68_by_global[381 + group_serial]
        assert v68["register"] == "ASTRO" and source["surface_ZL3b"] == v68["rendered_surface"]
        iatro_class, practical_class = content_classes(v68["unit_id"])
        astro_groups.append({
            "group_serial": group_serial, "page": source["page"], "unit_id": v68["unit_id"],
            "locus": source["locus"], "event_index": source["event_index"], "source_event_serial": source["source_event_serial"],
            "astro_local_group_identity": v68["exact_card_or_local_group_id"], "surface_ZL3b": source["surface_ZL3b"],
            "locus_role": source["locus_role"], "inventory_item": source["inventory_item"],
            "formal_value": "PAGE_LOCAL_ASTRO_ADDRESS_ONLY; NO_PROSE_FORMAL_IMPORT",
            "mnemonic": "NOT_APPLICABLE_ASTRO",
            "iatromedical_content_class": iatro_class,
            "IATROMEDICAL_ELECTION": v68["iatromedical_selected_local_expansion"],
            "practical_content_class": practical_class,
            "PRACTICAL_SCHEDULE": v68["nonmedical_rival_local_expansion"],
            "content_preference": "COEQUAL", "external_label_status": source["external_label_status"],
            "rotation_start_status": source["rotation_start_status"], "direct_f68_f69_mapping": source["f68_f69_mapping"],
            "content_status": "BOTH_PAGE_LOCAL_EXEMPLARS; NO_PORTABLE_CARD_VALUE",
        })
    write_tsv(OUT / "V69_R1_395_ASTRO_GROUP_DUAL_EDITION.tsv", astro_groups)

    unified: list[dict[str, object]] = []
    for row in prose_events:
        unified.append({
            "global_group_serial": row["event_serial"], "source_kind": "PROSE_EXACT_CARD", "register": "HERBAL" if row["record_unit_id"].startswith("H") else "BIO",
            "unit_id": row["record_unit_id"], "page": row["page"], "local_serial": row["event_serial"],
            "locus": row["locus"], "field_or_address": row["field_id"], "statement_or_station": row["statement_id"],
            "exact_identity": row["joint_tuple_id"], "surface_display_only": row["surface_display_only"],
            "formal_control": row["FORMAL_CONTROL_AT_THIS_EVENT"], "mnemonic_or_status": row["ATOMIC_OR_WHOLE_CARD_MNEMONIC"],
            "structural_status": row["v63_parse_status"], "iatromedical_content_class": row["iatromedical_content_class"],
            "IATROMEDICAL_SIMPLE_BATH_ELECTION": row["IATROMEDICAL_SIMPLE_BATH_ELECTION"],
            "practical_content_class": row["practical_content_class"],
            "PRACTICAL_MATERIAL_PROCESS_SCHEDULE": row["PRACTICAL_MATERIAL_PROCESS_SCHEDULE"],
            "content_preference": "COEQUAL", "content_status": row["content_status"],
            "roundtrip_status": "PASS_EXACT_PROSE_ID_AND_CONTEXT",
        })
    for row in astro_groups:
        unified.append({
            "global_group_serial": 381 + int(row["group_serial"]), "source_kind": "ASTRO_PAGE_LOCAL_GROUP", "register": "ASTRO",
            "unit_id": row["unit_id"], "page": row["page"], "local_serial": row["group_serial"],
            "locus": row["locus"], "field_or_address": f"{row['locus']}:{row['event_index']}", "statement_or_station": row["inventory_item"],
            "exact_identity": row["astro_local_group_identity"], "surface_display_only": row["surface_ZL3b"],
            "formal_control": "NOT_APPLICABLE_ASTRO", "mnemonic_or_status": "NOT_APPLICABLE_ASTRO",
            "structural_status": row["locus_role"], "iatromedical_content_class": row["iatromedical_content_class"],
            "IATROMEDICAL_SIMPLE_BATH_ELECTION": row["IATROMEDICAL_ELECTION"],
            "practical_content_class": row["practical_content_class"],
            "PRACTICAL_MATERIAL_PROCESS_SCHEDULE": row["PRACTICAL_SCHEDULE"],
            "content_preference": "COEQUAL", "content_status": row["content_status"],
            "roundtrip_status": "PASS_EXACT_ASTRO_LOCAL_ADDRESS_AND_CONTEXT",
        })
    write_tsv(OUT / "V69_R1_776_UNIFIED_DUAL_LEDGER.tsv", unified)

    v67_unit_by_id = {row["unit_id"]: row for row in v67_units}
    v68_unit_by_id = {row["unit_id"]: row for row in v68_units}
    contradiction_by_id = {row["unit_id"]: row for row in v68_contradictions}
    unit_rows: list[dict[str, object]] = []
    for unit in UNIT_ORDER:
        v67 = v67_unit_by_id[unit]
        v68 = v68_unit_by_id[unit]
        contradiction = contradiction_by_id[unit]
        iatro_class, practical_class = content_classes(unit)
        iatro_short, practical_short = CONCISE[unit]
        unit_rows.append({
            "unit_id": unit, "page": v67["page"], "register": v67["register"],
            "group_count": v67["group_count"], "field_or_locus_count": v67["field_or_locus_count"], "statement_count": v67["statement_count"],
            "iatromedical_content_class": iatro_class, "iatromedical_title": v67["unit_title_or_system"],
            "complete_IATROMEDICAL_SIMPLE_BATH_ELECTION_text": v67["complete_selected_source_or_diagram_reading"],
            "readable_concise_iatromedical_translation": iatro_short, "iatromedical_workflow": IATRO_WORKFLOW[unit],
            "practical_content_class": practical_class, "practical_title": v68["nonmedical_article_or_diagram_title"],
            "complete_PRACTICAL_MATERIAL_PROCESS_SCHEDULE_text": v68["complete_nonmedical_German_text"],
            "readable_concise_practical_translation": practical_short, "practical_workflow": v68["executable_workflow"],
            "explicit_iconography": v68["explicit_iconographic_argument"], "explicit_history": v68["explicit_historical_argument"],
            "strongest_iatromedical_contradiction": contradiction["strongest_contradiction_to_iatromedical"],
            "strongest_practical_contradiction": contradiction["strongest_contradiction_to_nonmedical"],
            "content_preference": "COEQUAL", "uncertainty": "HIGH_LOCAL_EXEMPLAR_DEPENDENCE",
            "semantic_contract": "COMPLETE_DUAL_CREATIVE_EDITION; NOT_TRANSLATION; NO_NEW_CARD_MEANING",
        })
    write_tsv(OUT / "V69_R1_14_COMPLETE_UNIT_DUAL_EDITION.tsv", unit_rows)

    uncertainty_rows: list[dict[str, object]] = [
        {"scope": "GLOBAL", "unit_id": "ALL", "layer": "LEXICON", "uncertainty_or_contradiction": "Confirmed historical lexemes and plaintext clauses are zero.", "strongest_rival_or_counterpressure": "All short values are creative prompts.", "release_action": "Keep question marks and UNKNOWN_EXEMPLAR.", "status": "OPEN_FINAL"},
        {"scope": "GLOBAL", "unit_id": "ALL", "layer": "IDENTITY", "uncertainty_or_contradiction": "Exact joint tuples are executable identities, not proven words.", "strongest_rival_or_counterpressure": "A tuple can be a code state, formula card or copied exemplar address.", "release_action": "Never segment by surface or PAGE_HOST.", "status": "FROZEN"},
        {"scope": "GLOBAL", "unit_id": "ALL", "layer": "CONTROL_DECK", "uncertainty_or_contradiction": "Only 119/381 events have mnemonic or formal control; 262 are EXEMPLAR_ONLY.", "strongest_rival_or_counterpressure": "Formal preservation does not establish source semantics.", "release_action": "No posthoc gloss for the tail.", "status": "FROZEN"},
        {"scope": "GLOBAL", "unit_id": "ALL", "layer": "REGISTER", "uncertainty_or_contradiction": "Four anonymous registers are minimal only for the selected creative clauses.", "strongest_rival_or_counterpressure": "Pure form copying needs no semantic register.", "release_action": "Keep IDs record-local and never as card meanings.", "status": "OPEN_FINAL"},
        {"scope": "GLOBAL", "unit_id": "ALL", "layer": "LAYOUT", "uncertainty_or_contradiction": "A physical line is not a sentence; 18 statements cross loci.", "strongest_rival_or_counterpressure": "Some carries may be repetition or scribal repair.", "release_action": "Use the selected 116-statement map and retain alternatives.", "status": "FROZEN"},
        {"scope": "GLOBAL", "unit_id": "ALL", "layer": "CLOSURE", "uncertainty_or_contradiction": "Terminal families are formally real but their individual lexical actions remain confounded.", "strongest_rival_or_counterpressure": "SPÜLEN?/ABLASSEN? may be anonymous terminal steps.", "release_action": "Close commits fields and supplies no silent object.", "status": "OPEN_FINAL"},
        {"scope": "GLOBAL", "unit_id": "ALL", "layer": "CONTENT", "uncertainty_or_contradiction": "Iatromedical and practical editions reach parity.", "strongest_rival_or_counterpressure": "No exact card discriminates SIMPLE/BATH/ELECTION from MATERIAL/PROCESS/SCHEDULE.", "release_action": "Publish both columns coequally.", "status": "FINAL_COEQUAL"},
        {"scope": "GLOBAL", "unit_id": "A1-A3", "layer": "ASTRO", "uncertainty_or_contradiction": "All 395 meanings are page-local exemplars; start and rotation remain unproven.", "strongest_rival_or_counterpressure": "Generic lookup and historical astrology both fit topology.", "release_action": "No prose import and no portable surface gloss.", "status": "FROZEN"},
        {"scope": "GLOBAL", "unit_id": "A2/A3", "layer": "CROSS_PAGE", "uncertainty_or_contradiction": "No visible f68r1-to-f69v key exists.", "strongest_rival_or_counterpressure": "An external user could know a relation not written here.", "release_action": "Do not join the pages.", "status": "FROZEN"},
        {"scope": "GLOBAL", "unit_id": "ALL", "layer": "ROUNDTRIP", "uncertainty_or_contradiction": "776/776 content roundtrips require the master exemplar; surface alone recovers 0/776 full intentions.", "strongest_rival_or_counterpressure": "The same machine carries unrelated content worlds.", "release_action": "Treat roundtrip as preservation, not decipherment evidence.", "status": "FINAL"},
    ]
    for unit in UNIT_ORDER:
        contradiction = contradiction_by_id[unit]
        uncertainty_rows.append({
            "scope": "UNIT", "unit_id": unit, "layer": "CONTENT_FORK",
            "uncertainty_or_contradiction": contradiction["strongest_contradiction_to_iatromedical"],
            "strongest_rival_or_counterpressure": contradiction["strongest_contradiction_to_nonmedical"],
            "release_action": "Retain both complete local texts; no dictionary feedback.", "status": "COEQUAL_LOCAL_DEFAULTS",
        })
    write_tsv(OUT / "V69_R1_UNCERTAINTIES_AND_CONTRADICTIONS.tsv", uncertainty_rows)

    generated = [
        "V69_R1_173_EXACT_CARD_DICTIONARY.tsv", "V69_R1_381_PROSE_EVENT_INTERLINEAR.tsv",
        "V69_R1_135_FIELD_DUAL_EDITION.tsv", "V69_R1_116_STATEMENT_DUAL_EDITION.tsv",
        "V69_R1_395_ASTRO_GROUP_DUAL_EDITION.tsv", "V69_R1_776_UNIFIED_DUAL_LEDGER.tsv",
        "V69_R1_14_COMPLETE_UNIT_DUAL_EDITION.tsv", "V69_R1_UNCERTAINTIES_AND_CONTRADICTIONS.tsv",
    ]
    hashes = {name: file_hash(OUT / name) for name in generated}
    (OUT / "V69_R1_ARTIFACT_SHA256.json").write_text(json.dumps(hashes, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    summary = {
        "status": "PASS", "pages": 10, "dictionary_cards": 173,
        "mnemonic_cards": 11, "formal_control_cards": 4, "active_control_card_union": 14,
        "unknown_exemplar_cards": 159, "prose_events": 381, "fields": 135,
        "statements": 116, "astro_groups": 395, "unified_groups": 776, "units": 14,
        "prose_recognized_control_events": 119, "prose_exemplar_only_events": 262,
        "content_columns": ["IATROMEDICAL_SIMPLE_BATH_ELECTION", "PRACTICAL_MATERIAL_PROCESS_SCHEDULE"],
        "content_preference": "COEQUAL", "new_semantics": 0, "direct_f68_f69_join": False,
        "phonetic_or_letter_claim": False, "next_iteration": "STOP_NO_V70",
    }
    (OUT / "V69_R1_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Build the constrained Pass-1012 semantic contract on the current 22 pages."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
CODEBOOK = (
    ROOT
    / "experiments/yolo/sidequest_semantic_ot_grade_and_concept_review_one_thousand_tenth"
    / "PASS1010_175_GRADE_REVISED_CODEBOOK.tsv"
)
STATEMENTS = (
    ROOT
    / "experiments/yolo/sidequest_semantic_manual_optical_passage_audit_one_thousand_eleventh"
    / "PASS1011_627_OPTICALLY_REPAIRED_STATEMENTS.tsv"
)

PORTABLE = "PORTABLE_CORE_MEANING"
FORMAL = "FORMAL_CONTROL_NOT_CONTENT_WORD"
SPECIALIST = "SPECIALIST_MEANING_CANDIDATE"
LOCAL = "LOCAL_ADDRESS_OR_MEMORIZED_SIGN"

CONTENT_CORES = {"OK", "CH", "SH", "K", "AIIN", "S", "CHD", "OR", "T", "AIN", "R", "P"}
RELATION_CORES = {"Y", "OL", "OT", "AL", "AR", "L"}


def c(status: str, value: str, allowed: str, forbidden: str) -> tuple[str, str, str, str]:
    return status, value, allowed, forbidden


# One value per visible teaching sign.  Context may instantiate that value but
# may not replace it with an unrelated material, device, direction, or action.
CONTRACTS: dict[str, tuple[str, str, str, str]] = {
    "Y": c(PORTABLE, "AKTIVER POSTEN", "dieses Material, diese Station oder dieser Eintrag", "kein Satzschluss, keine Qualität und kein Stoffname"),
    "OK": c(PORTABLE, "SETZEN", "ansetzen, platzieren oder aktiv setzen", "nicht automatisch erhitzen, mischen, waschen oder anwenden"),
    "OL": c(PORTABLE, "FORTSETZEN", "denselben Gang, Posten oder Eintrag fortführen", "kein warm, vorig, Gefäß oder Richtung"),
    "OT": c(PORTABLE, "DANACH", "nächster lokaler Schritt oder Platz", "kein eigenes Aktionsverb und keine automatische Wiederholung"),
    "AL": c(PORTABLE, "ZIELORT", "Zielgefäß, Gebrauchsstelle oder Diagrammplatz", "kein Körperteil, Becken oder unten ohne sichtbaren Besitzer"),
    "CH": c(PORTABLE, "NEHMEN", "Teil, Portion oder Eintrag entnehmen", "kein Pflanzenname, Mahlen, Erhitzen oder Trennen"),
    "SH": c(PORTABLE, "HALTEN", "halten, stehen lassen oder einen Zustand bewahren", "kein Stängel, Wasser oder Absetzen ohne weitere Karte"),
    "AR": c(PORTABLE, "AUSGANG", "Vorrat, Ausgangsstelle oder Ausgangsplatz", "kein Wasser, Wurzel oder Quelle als Stoffname"),
    "K": c(PORTABLE, "GEBEN", "zugeben, zuweisen oder an eine Stelle geben", "kein spezieller Zusatz, Trank oder Guss ohne Besitzer"),
    "AIIN": c(PORTABLE, "MASS", "vorgeschriebene Menge, Wert oder Einstellung", "keine Zahl, Zeitdauer oder Einheit ohne separate Angabe"),
    "S": c(PORTABLE, "WÄHLEN", "Material, Station oder Diagrammplatz auswählen", "kein bestimmtes Objekt und keine Probe ohne Zusatzkarte"),
    "CHD": c(PORTABLE, "UMSETZEN", "Posten zwischen zwei lokalen Zuständen oder Stellen versetzen", "keine Richtung, Wärme oder Flüssigkeit ohne Anker"),
    "OR": c(PORTABLE, "ANSATZ", "laufende Zubereitung, Arbeitskonfiguration oder Eintragsverband", "kein Wein, Öl, Sud oder Gefäß"),
    "L": c(PORTABLE, "VERBINDUNG", "über eine sichtbare oder textlich gesetzte Verbindung weitergeben", "keine Flussrichtung und kein Rohr ohne Bildanker"),
    "T": c(PORTABLE, "EINSTELLEN", "Menge, Stufe, Stellung oder Arbeitswert einstellen", "kein Erhitzen, Füllen oder Körperteil"),
    "AIN": c(PORTABLE, "PORTION", "Teilmenge, Füllung oder einzelne Zelle", "kein Tuch, Gefäß oder feste Maßeinheit"),
    "R": c(PORTABLE, "MARKIEREN", "Zustand, Stelle oder Eintrag kennzeichnen", "kein Kühlen, Wärme oder Prüfergebnis"),
    "P": c(PORTABLE, "EINSETZEN", "Material, Einsatz oder Eintrag in einen lokalen Rahmen setzen", "kein Beginnmarker, Gefäß oder Richtung allein"),

    "E": c(FORMAL, "GRAD I", "erste oder niedrige Stufe der aktiven Handlung", "kein universelles kurz, kalt, einmal oder leicht"),
    "EE": c(FORMAL, "GRAD II", "zweite oder höhere Stufe derselben aktiven Handlung", "kein universelles lang, warm oder stark"),
    "EEE": c(FORMAL, "GRAD III", "dritte oder volle Stufe derselben aktiven Handlung", "kein automatischer Abschluss und kein vollständig als eigenes Verb"),
    "DY": c(FORMAL, "SCHLUSS", "nur in der lizenzierten Endkonstruktion den Teilgang schließen", "sichtbares dy nicht global zerlegen und nicht als Stoffwort lesen"),
    "O": c(FORMAL, "AUSFÜHRUNG", "die lokal aktive Handlung ausführen", "kein selbständiges konkretes Verb und insbesondere nicht Wasser oder Öl"),
    "CARRIER_Q": c(FORMAL, "BEGINNMARKER", "neuen lokalen Eintrag oder Gang eröffnen", "kein Lautwert, Stoff oder eigenes Aktionsverb"),
    "IIN": c(FORMAL, "STUFE", "benannte Arbeits- oder Diagrammstufe", "nicht mit AIIN=MASS verschmelzen und keine konkrete Zahl erfinden"),
    "DA": c(FORMAL, "ZWEITE STUFE", "zweiten lokalen Gang oder zweite Position anzeigen", "kein bestimmtes Gefäß, Material oder zeitliches danach"),

    "CTH": c(SPECIALIST, "BEREIT", "einen erreichten Arbeitszustand als bereit kennzeichnen", "kein gebrauchsfertig, klar oder gekocht ohne lokale Stütze"),
    "SHED": c(SPECIALIST, "ABSETZEN", "einen Posten stehen und sich setzen lassen", "kein allgemeiner Schluss, Bad oder Waschgang"),
    "CKH": c(SPECIALIST, "DURCHLASS", "lokaler Durchgang, Anschluss oder Passage", "kein Filtertuch, Auslass oder Richtung ohne Bildanker"),
    "CHEO": c(SPECIALIST, "AUSZUG", "gewonnener oder weitergeführter Arbeitsauszug", "kein Wasser, Wein, Öl oder Diagrammwort; bei Labels nur lokale Adresse"),
    "AIR": c(SPECIALIST, "LAUF", "Flüssigkeits-, Arbeits- oder Ringlauf mit gemeinsamem Wegkern", "nicht universal Wasser und nicht Rücklauf, Einlass oder Richtung"),
    "CHK": c(SPECIALIST, "BEARBEITEN", "unspezifizierte Fachbearbeitung des aktiven Postens", "nicht frei zu Wärme, Mischen, Mahlen, Waschen oder Baden ausbauen"),
    "SOLK": c(SPECIALIST, "AUFFANGEN", "an einer lokalen Sammel- oder Empfangsstelle aufnehmen", "kein bestimmtes Becken, Gefäß, Sieb oder Ergebnis"),
    "LSH": c(SPECIALIST, "SPÜLEN", "mit einem vorhandenen Arbeitsmedium durchwaschen", "kein Wasserstoffwort, Körperwäsche oder Ringlauf ohne Besitzer"),
    "CPH": c(SPECIALIST, "UMLEITEN", "auf einen alternativen lokalen Weg oder Empfänger setzen", "keine Richtung und kein Nachseihen ohne sichtbare Alternative"),
    "CFH": c(SPECIALIST, "TRENNEN", "Teil, Fraktion oder Lauf voneinander trennen", "kein Auswringen, Pressen oder Filtern ohne weitere Karte"),
    "LD": c(SPECIALIST, "BEFESTIGEN", "einen Einsatz oder Posten an Ort halten", "keine Binde, Auflage oder Körperanwendung ohne Bildbesitzer"),

    "D_ADDR": c(LOCAL, "TEILADRESSE", "lokalen Teil des sichtbaren Besitzers adressieren", "kein portables Wort TEIL und kein bestimmtes Pflanzenorgan"),
    "AM_ADDR": c(LOCAL, "INNENADRESSE", "inneren lokalen Platz markieren", "kein universelles in, Gefäß oder Innenbecken"),
    "A_ADDR": c(LOCAL, "ORTSADRESSE", "eine lokale Bild- oder Diagrammstelle adressieren", "kein portables Wort ORT und kein Zieloperator"),
    "S_ADDR": c(LOCAL, "SONDERADRESSE", "besonders bezeichneten lokalen Platz markieren", "kein Stern-, Material- oder Stationswort außerhalb des Besitzers"),
    "LOCAL_CHAR_F": c(LOCAL, "NEBENADRESSE", "lokalen Nebenplatz oder Zweig markieren", "kein portabler Nebenweg und keine Flussrichtung"),
    "HO": c(LOCAL, "STOFFKLASSE", "lokale Material- oder Unterklasse aus dem Besitzer übernehmen", "kein universeller Teilstoff, Pflanze oder Badezusatz"),
    "AN": c(LOCAL, "ZUSATZKLASSE", "lokalen Zusatztyp aus dem Exemplar übernehmen", "kein portables Zusatzwort und keine konkrete Zutat"),
    "G_LABEL": c(LOCAL, "PRÜFZEICHEN", "lokale Prüf- oder Kennzeichnungsstelle markieren", "kein universelles prüfen, klar oder Farbe"),
    "LOCAL_CHAR_G": c(LOCAL, "EINER-MARKE", "lokalen Einzelplatz oder einfachen Durchgang markieren", "kein portables einmal und keine Zahl Eins"),
    "LOCAL_CHAR_I": c(LOCAL, "UNTERSTUFENMARKE", "lokale untere oder zweite Stufe markieren", "kein portables unten oder zweiter Arbeitsgang"),
    "OS": c(LOCAL, "ZUSATZBEZUG", "lokalen Bezug zum laufenden Besitzer herstellen", "kein Gefäß und kein portables dazu"),
    "D_LABEL": c(LOCAL, "RANDADRESSE", "lokalen Rand- oder Außenplatz markieren", "kein portables Randwort"),
    "S_LABEL": c(LOCAL, "RAHMENZEICHEN", "lokalen Bild- oder Diagrammrahmen anzeigen", "kein portables Rahmenwort"),
    "LOCAL_CHAR_B": c(LOCAL, "PAARMARKE", "lokales Paar oder Doppelobjekt anzeigen", "kein portables Paar und keine Menge Zwei"),
    "M_LOCAL": c(LOCAL, "MITTENADRESSE", "lokalen Mittelpunkt oder Mittelplatz markieren", "kein portables Mittewort"),
    "Z_ADDR": c(LOCAL, "AUSSENADRESSE", "lokalen Außenplatz markieren", "kein portables außen"),
    "LOCAL_CHAR_J": c(LOCAL, "VERBINDUNGSMARKE", "lokal gezeichnete Zusammengehörigkeit anzeigen", "kein portables verbinden und keine Richtung"),
    "LOCAL_CHAR_Z": c(LOCAL, "ZWISCHENMARKE", "lokalen Zwischenplatz markieren", "kein portables zwischen"),
    "RESUME_CARD": c(LOCAL, "WIEDERAUFNAHMEKARTE", "lokalen Besitzer oder Gang erneut aufnehmen", "kein universelles wieder und keine Wiederholungszahl"),
}


def read_tsv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        return list(reader.fieldnames or []), list(reader)


def write_tsv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def split_components(value: str) -> list[list[str]]:
    return [part.split("+") for part in value.split(" | ")]


def main() -> None:
    _, codebook = read_tsv(CODEBOOK)
    source_fields, statements = read_tsv(STATEMENTS)
    root_rows = [row for row in codebook if row["teaching_unit_id"].startswith("R-")]
    codebook_tokens = {row["recognition_forms"] for row in root_rows}
    if codebook_tokens != set(CONTRACTS):
        missing = sorted(codebook_tokens - set(CONTRACTS))
        extra = sorted(set(CONTRACTS) - codebook_tokens)
        raise SystemExit(f"contract inventory mismatch missing={missing} extra={extra}")

    usage = {
        token: {
            "root_mentions": 0,
            "event_occurrences": 0,
            "statements": set(),
            "pages": set(),
            "registers": set(),
            "surfaces": Counter(),
        }
        for token in CONTRACTS
    }
    event_index: dict[str, list[tuple[str, str, str, str]]] = defaultdict(list)
    unknown_tokens: Counter[str] = Counter()
    pressure_rows: list[dict[str, str]] = []
    statement_class_counts: Counter[str] = Counter()
    event_class_counts: Counter[str] = Counter()

    for statement in statements:
        surfaces = statement["surface_sequence"].split()
        components = split_components(statement["component_sequence"])
        if len(surfaces) != len(components):
            raise SystemExit(f"surface/component mismatch {statement['statement_id']}")
        mention_counts = Counter()
        per_event_classes = Counter()
        contract_events: list[str] = []
        for surface, tokens in zip(surfaces, components):
            for token in tokens:
                if token not in CONTRACTS:
                    unknown_tokens[token] += 1
                    continue
                mention_counts[token] += 1
                info = usage[token]
                info["root_mentions"] += 1
                info["statements"].add(statement["statement_id"])
                info["pages"].add(statement["physical_page"])
                info["registers"].add(statement["register"])
                info["surfaces"][surface] += 1
            for token in set(tokens) & set(CONTRACTS):
                usage[token]["event_occurrences"] += 1
            classes = {CONTRACTS[token][0] for token in tokens if token in CONTRACTS}
            if LOCAL in classes:
                event_class = "LOCAL_OWNER_DEPENDENT"
            elif SPECIALIST in classes:
                event_class = "SPECIALIST_CANDIDATE_DEPENDENT"
            elif PORTABLE in classes:
                event_class = "PORTABLE_CORE_COMPOSITION"
            else:
                event_class = "FORMAL_CONTROL_ONLY"
            per_event_classes[event_class] += 1
            event_class_counts[event_class] += 1
            contract_events.append(" + ".join(CONTRACTS[token][1] for token in tokens))
            event_index[surface].append(
                (
                    "+".join(tokens),
                    statement["physical_page"],
                    statement["statement_id"],
                    statement["register"],
                )
            )

        if per_event_classes["LOCAL_OWNER_DEPENDENT"]:
            status = "LOCAL_OWNER_REQUIRED"
        elif per_event_classes["SPECIALIST_CANDIDATE_DEPENDENT"]:
            status = "SPECIALIST_CANDIDATE_REQUIRED"
        elif per_event_classes["PORTABLE_CORE_COMPOSITION"]:
            status = "PORTABLE_CORE_READABLE"
        else:
            status = "FORMAL_CONTROL_ONLY"
        statement_class_counts[status] += 1
        pressure_rows.append(
            {
                **statement,
                "pass1012_statement_status": status,
                "portable_core_mentions": str(
                    sum(mention_counts[token] for token in CONTRACTS if CONTRACTS[token][0] == PORTABLE)
                ),
                "content_or_operation_core_mentions": str(
                    sum(mention_counts[token] for token in CONTENT_CORES)
                ),
                "referent_sequence_relation_mentions": str(
                    sum(mention_counts[token] for token in RELATION_CORES)
                ),
                "formal_control_mentions": str(
                    sum(mention_counts[token] for token in CONTRACTS if CONTRACTS[token][0] == FORMAL)
                ),
                "specialist_candidate_mentions": str(
                    sum(mention_counts[token] for token in CONTRACTS if CONTRACTS[token][0] == SPECIALIST)
                ),
                "local_sign_mentions": str(
                    sum(mention_counts[token] for token in CONTRACTS if CONTRACTS[token][0] == LOCAL)
                ),
                "portable_event_count": str(per_event_classes["PORTABLE_CORE_COMPOSITION"]),
                "formal_only_event_count": str(per_event_classes["FORMAL_CONTROL_ONLY"]),
                "specialist_event_count": str(per_event_classes["SPECIALIST_CANDIDATE_DEPENDENT"]),
                "local_event_count": str(per_event_classes["LOCAL_OWNER_DEPENDENT"]),
                "contract_literal_de": " | ".join(contract_events),
                "pass1012_working_translation_de": statement["optically_revised_translation"],
                "working_translation_status": (
                    "MANUAL_IMAGE_REPAIR" if statement["optical_review_status"] == "MANUALLY_REVIEWED_ORIGINAL_IMAGE"
                    else "LEGACY_FLUENT_READING_NOT_YET_MANUALLY_REPAIRED"
                ),
            }
        )

    if unknown_tokens:
        raise SystemExit(f"unknown component tokens: {dict(unknown_tokens)}")

    contract_rows: list[dict[str, str]] = []
    row_by_token = {row["recognition_forms"]: row for row in root_rows}
    for token in [row["recognition_forms"] for row in root_rows]:
        status, value, allowed, forbidden = CONTRACTS[token]
        info = usage[token]
        examples = [surface for surface, _ in info["surfaces"].most_common(8)]
        if token in CONTENT_CORES:
            semantic_kind = "CONTENT_OR_OPERATION_CORE"
        elif token in RELATION_CORES:
            semantic_kind = "REFERENT_SEQUENCE_OR_RELATION_CORE"
        elif status == FORMAL:
            semantic_kind = "GRADE_BOUNDARY_OR_ENTRY_CONTROL"
        elif status == SPECIALIST:
            semantic_kind = "SPECIALIST_OPERATION_CANDIDATE"
        else:
            semantic_kind = "LOCAL_SIGN_OR_ADDRESS"
        contract_rows.append(
            {
                "teaching_unit_id": row_by_token[token]["teaching_unit_id"],
                "sign": token,
                "pass1010_value_de": row_by_token[token]["spoken_value_de"],
                "pass1012_class": status,
                "semantic_kind": semantic_kind,
                "single_core_value_de": value,
                "allowed_contextual_realization_de": allowed,
                "forbidden_rescue_de": forbidden,
                "root_mentions": str(info["root_mentions"]),
                "event_occurrences": str(info["event_occurrences"]),
                "statement_count": str(len(info["statements"])),
                "page_count": str(len(info["pages"])),
                "register_count": str(len(info["registers"])),
                "pages": "|".join(sorted(info["pages"])),
                "registers": "|".join(sorted(info["registers"])),
                "surface_examples": "|".join(examples),
                "forward_rule_de": (
                    "Neues Kompositum wörtlich mit diesem Kern lesen; bei Konflikt die Gesamtkarte aussondern, nicht den Kern ändern."
                    if status in {PORTABLE, SPECIALIST}
                    else "Nur als Steuer- oder Lokalzeichen verwenden; daraus kein neues Inhaltswort erzeugen."
                ),
            }
        )

    contract_fields = [
        "teaching_unit_id",
        "sign",
        "pass1010_value_de",
        "pass1012_class",
        "semantic_kind",
        "single_core_value_de",
        "allowed_contextual_realization_de",
        "forbidden_rescue_de",
        "root_mentions",
        "event_occurrences",
        "statement_count",
        "page_count",
        "register_count",
        "pages",
        "registers",
        "surface_examples",
        "forward_rule_de",
    ]
    contract_path = HERE / "PASS1012_56_SIGN_SEMANTIC_CONTRACT.tsv"
    write_tsv(contract_path, contract_fields, contract_rows)

    composition_rows: list[dict[str, str]] = []
    composition_units = [
        row
        for row in codebook
        if row["unit_type"] in {"FORMULA_CARD", "CONTEXTUAL_COMPOSITION_NOT_NEW_WORD"}
    ]
    for unit in composition_units:
        if unit["unit_type"] == "FORMULA_CARD":
            recipes = {unit["recognition_forms"]}
            matches = [
                (surface, page, statement_id, register)
                for surface, events in event_index.items()
                for recipe, page, statement_id, register in events
                if recipe == unit["recognition_forms"]
            ]
        else:
            target_surfaces = set((unit["specialist_surface_forms"] or unit["recognition_forms"]).split("|"))
            events = [event for surface in target_surfaces for event in event_index.get(surface, [])]
            recipes = {recipe for recipe, _, _, _ in events}
            matches = [
                (surface, page, statement_id, register)
                for surface in target_surfaces
                for recipe, page, statement_id, register in event_index.get(surface, [])
            ]
        tokens = sorted({token for recipe in recipes for token in recipe.split("+")})
        classes = {CONTRACTS[token][0] for token in tokens}
        if LOCAL in classes:
            decision = "LOCAL_COMPOSITION_ONLY"
        elif SPECIALIST in classes:
            decision = "SPECIALIST_COMPOSITION_CANDIDATE"
        elif PORTABLE in classes:
            decision = "PORTABLE_COMPOSITION"
        else:
            decision = "FORMAL_COMPOSITION_ONLY"
        readings = {
            " + ".join(CONTRACTS[token][1] for token in recipe.split("+")) for recipe in recipes
        }
        composition_rows.append(
            {
                "teaching_unit_id": unit["teaching_unit_id"],
                "unit_type": unit["unit_type"],
                "surface_forms": "|".join(sorted({surface for surface, _, _, _ in matches})),
                "observed_events_in_627": str(len(matches)),
                "pages": "|".join(sorted({page for _, page, _, _ in matches})),
                "component_recipes": "|".join(sorted(recipes)),
                "pass1012_contract_reading_de": " || ".join(sorted(readings)),
                "composition_decision": decision,
                "content_core_count": str(sum(token in CONTENT_CORES for token in tokens)),
                "relation_core_count": str(sum(token in RELATION_CORES for token in tokens)),
                "formal_control_count": str(sum(CONTRACTS[token][0] == FORMAL for token in tokens)),
                "specialist_candidate_count": str(sum(CONTRACTS[token][0] == SPECIALIST for token in tokens)),
                "local_sign_count": str(sum(CONTRACTS[token][0] == LOCAL for token in tokens)),
                "pass1010_spoken_value_de": unit["spoken_value_de"],
                "pass1010_local_expansion_de": unit["concrete_context_values_de"],
                "local_expansion_status": (
                    "WITHDRAW_AS_PORTABLE_MEANING_KEEP_ONLY_OWNER_BOUND_PARAPHRASE"
                    if unit["unit_type"] == "CONTEXTUAL_COMPOSITION_NOT_NEW_WORD"
                    else "ROOT_SUM_ONLY"
                ),
                "forward_prediction_de": (
                    "Auf neuer Seite zuerst exakt diese Kernsumme lesen; ein konkreteres Nomen oder Verfahren braucht einen sichtbaren Besitzer."
                ),
            }
        )

    composition_fields = [
        "teaching_unit_id",
        "unit_type",
        "surface_forms",
        "observed_events_in_627",
        "pages",
        "component_recipes",
        "pass1012_contract_reading_de",
        "composition_decision",
        "content_core_count",
        "relation_core_count",
        "formal_control_count",
        "specialist_candidate_count",
        "local_sign_count",
        "pass1010_spoken_value_de",
        "pass1010_local_expansion_de",
        "local_expansion_status",
        "forward_prediction_de",
    ]
    composition_path = HERE / "PASS1012_102_COMPOSITION_CONTRACTS.tsv"
    write_tsv(composition_path, composition_fields, composition_rows)

    pressure_fields = source_fields + [
        "pass1012_statement_status",
        "portable_core_mentions",
        "content_or_operation_core_mentions",
        "referent_sequence_relation_mentions",
        "formal_control_mentions",
        "specialist_candidate_mentions",
        "local_sign_mentions",
        "portable_event_count",
        "formal_only_event_count",
        "specialist_event_count",
        "local_event_count",
        "contract_literal_de",
        "pass1012_working_translation_de",
        "working_translation_status",
    ]
    pressure_path = HERE / "PASS1012_627_SEMANTIC_PRESSURE_MAP.tsv"
    write_tsv(pressure_path, pressure_fields, pressure_rows)

    class_counts = Counter(row["pass1012_class"] for row in contract_rows)
    kind_counts = Counter(row["semantic_kind"] for row in contract_rows)
    composition_counts = Counter(row["composition_decision"] for row in composition_rows)
    summary = {
        "pass": 1012,
        "pages_unchanged": 22,
        "statements": len(statements),
        "visible_sign_entries": len(contract_rows),
        "semantic_contract_classes": dict(sorted(class_counts.items())),
        "semantic_kinds": dict(sorted(kind_counts.items())),
        "composition_units": len(composition_rows),
        "composition_decisions": dict(sorted(composition_counts.items())),
        "statement_statuses": dict(sorted(statement_class_counts.items())),
        "event_statuses": dict(sorted(event_class_counts.items())),
        "contextual_local_expansions_withdrawn_as_portable_meanings": sum(
            row["local_expansion_status"].startswith("WITHDRAW") for row in composition_rows
        ),
        "manual_image_repaired_statements_carried": sum(
            row["working_translation_status"] == "MANUAL_IMAGE_REPAIR" for row in pressure_rows
        ),
    }
    for path in (contract_path, composition_path, pressure_path):
        summary.setdefault("outputs_sha256", {})[str(path.relative_to(ROOT))] = sha256(path)
    (HERE / "PASS1012_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()

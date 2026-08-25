#!/usr/bin/env python3
"""Build the Pass-912 fourteen-page handbook after ordering the local drawer."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
P910 = ROOT / "experiments/yolo/sidequest_semantic_three_layer_master_handbook_nine_hundred_tenth"
P911 = ROOT / "experiments/yolo/sidequest_semantic_local_drawer_ordering_nine_hundred_eleventh"

SOURCE_EVENTS = P910 / "PASS910_2511_EVENT_INTERLINEAR.tsv"
SOURCE_EXPANSIONS = P910 / "PASS910_REGISTER_EXPANSIONS.tsv"
SOURCE_ORDERED = P911 / "PASS911_ORDERED_LOCAL_DRAWER.tsv"

EVENTS_OUT = BASE / "PASS912_2511_EVENT_INTERLINEAR.tsv"
DICTIONARY_OUT = BASE / "PASS912_CARD_DICTIONARY.tsv"
LOCI_OUT = BASE / "PASS912_464_LOCUS_EDITION.tsv"
PAGES_OUT = BASE / "PASS912_FOURTEEN_PAGE_SUMMARY.tsv"
OWNER_OUT = BASE / "PASS912_OWNER_BOUND_LABELS.tsv"
COMPONENTS_OUT = BASE / "PASS912_COMPONENTS.tsv"
RULES_OUT = BASE / "PASS912_SCRIBAL_RULES.tsv"
EDITION_OUT = BASE / "PASS912_FOURTEEN_PAGE_EDITION.md"
HANDBOOK_OUT = BASE / "PASS912_APPRENTICE_HANDBOOK.md"
REPORT_OUT = BASE / "PASS912_REPORT.md"
SUMMARY_OUT = BASE / "PASS912_BUILD_SUMMARY.json"


PAGE_ORDER = [
    "f10r", "f11r", "f13r", "f55v", "f56r", "f75r", "f81v", "f82r", "f83r",
    "f67r2", "f68r1", "f69v", "f70v", "f88r",
]


SHORT = {
    "AIIN": "SOLL-MASS", "AIN": "PORTION", "AIR": "LAUF", "AL": "ZIELSTELLE",
    "AR": "QUELLSTELLE", "CKH": "DURCHLASS", "CPH": "GEGEN-/EMPFANGSGANG",
    "DY": "SCHLUSS", "E": "KURZ", "EE": "LANG", "EEE": "VOLL", "IIN": "STUFE",
    "L": "LEITEN", "OL": "FORTSETZEN", "OT": "DANACH", "Y": "DIESER POSTEN",
    "O": "GANG", "OK": "ANSETZEN", "CH": "ENTNEHMEN/ABLESEN", "CHD": "UMSETZEN",
    "CHK": "ZUSTAND BEHANDELN", "CTH": "STATUS", "K": "ZUORDNEN/ZUGEBEN",
    "P": "BEGINNEN/EINSETZEN", "R": "MARKIERTER ZUSTAND", "S": "KONTEXT/PROBE",
    "SH": "HALTEN", "SHED": "RUHESTUFE", "T": "BEARBEITEN/MARKIEREN",
    "OR": "ANSATZ/EINTRAG", "DA": "ZWEITE STUFE", "A_ADDR": "LOKALE ADRESSE",
    "AM_ADDR": "GEGEN-/INNENFELD", "D_ADDR": "TEILADRESSE", "S_ADDR": "S-ADRESSE",
    "D_LABEL": "D-KENNZEICHEN", "G_LABEL": "G-KENNZEICHEN", "M_LOCAL": "M-KENNZEICHEN",
    "Z_ADDR": "Z-BEZUG", "CARRIER_Q": "Q-TRAEGER", "AN": "ZUSATZ", "OS": "AUCH",
    "RESUME_CARD": "WIEDERAUFNAHME", "CFH": "TRENNEN/PRESSEN", "CHEO": "REGISTER-EINTRAG",
    "HO": "OBJEKTTEIL", "LD": "BEFESTIGEN", "LSH": "WASCHEN/SPUELEN",
    "SOLK": "SAMMELSTELLE", "S_LABEL": "S-KENNZEICHEN",
}


COMMON_FLUENT = {
    "AIIN": "nach Sollmaß", "AIN": "eine Portion", "AIR": "entlang des Laufs",
    "AL": "zur Zielstelle", "AR": "von der Quellstelle", "CKH": "durch den Durchlass",
    "DY": "den Schritt schließen", "E": "kurz", "EE": "länger", "EEE": "vollständig",
    "IIN": "auf der Stufe", "L": "weiterleiten", "OL": "fortsetzen", "OT": "danach",
    "Y": "diesen Posten", "DA": "auf der zweiten Stufe", "A_ADDR": "an der lokalen Adresse",
    "AM_ADDR": "am Gegen-/Innenfeld", "D_ADDR": "an der Teiladresse", "S_ADDR": "an der S-Adresse",
    "D_LABEL": "mit D-Kennzeichen", "G_LABEL": "mit G-Kennzeichen", "M_LOCAL": "mit M-Kennzeichen",
    "Z_ADDR": "am Z-Bezug", "AN": "mit einem Zusatz", "OS": "ebenfalls",
    "RESUME_CARD": "den vorigen Posten wiederaufnehmen", "LD": "befestigen",
}


REGISTER_FLUENT = {
    "HERBAL": {
        "O": "den Verarbeitungsgang ausführen", "OK": "die Zubereitung ansetzen",
        "CH": "den Pflanzenteil entnehmen", "CHD": "das Material umsetzen",
        "CPH": "in den Nachlauf oder zweiten Durchgang geben", "CHK": "den Ansatz behandeln",
        "CTH": "den Zubereitungsstatus prüfen", "K": "Material zugeben", "P": "den Teil einsetzen",
        "R": "den Zustand markieren", "S": "prüfen oder weitergehen", "SH": "den Ansatz halten",
        "SHED": "den Ansatz ruhen lassen", "T": "den Teil bearbeiten", "OR": "mit dem Pflanzenansatz",
        "CFH": "auspressen oder trennen", "CHEO": "den Auszug verwenden", "HO": "den Objektteil nehmen",
        "LSH": "waschen oder spülen", "SOLK": "im Gefäß sammeln",
    },
    "BIOLOGICAL": {
        "O": "den Stationsgang ausführen", "OK": "die Station ansetzen", "CH": "den Posten abnehmen",
        "CHD": "den Posten umsetzen", "CPH": "zum Gegenlauf oder Empfänger zurückführen",
        "CHK": "den Stationszustand behandeln", "CTH": "den Stationsstatus prüfen",
        "K": "den Posten einsetzen", "P": "die Station beginnen", "R": "den Zustand markieren",
        "S": "die Station prüfen", "SH": "den Posten halten", "SHED": "an der Station halten",
        "T": "den Abschnitt bedienen", "OR": "mit dem Arbeitsansatz", "CFH": "pressen oder trennen",
        "CHEO": "den Arbeitsinhalt verwenden", "HO": "den Anlagenabschnitt verwenden",
        "LSH": "die Station spülen", "SOLK": "an der Auffangstelle sammeln",
    },
    "ZODIAC": {
        "O": "den Ringgang lesen", "OK": "die Ringstelle setzen", "CH": "die Kennung ablesen",
        "CHD": "die Bezugsstelle wechseln", "CPH": "zur Gegen- oder Rückstelle wechseln",
        "CHK": "den Kennungszustand setzen", "CTH": "den Stellenstatus prüfen", "K": "den Wert zuordnen",
        "P": "den Eintrag beginnen", "R": "den Kennungszustand markieren", "S": "die Sternkennung lesen",
        "SH": "den Bezug halten", "SHED": "den Ringstatus halten", "T": "die Stelle markieren",
        "OR": "mit dem lokalen Eintrag", "CFH": "die Trennkennung lesen", "CHEO": "den lokalen Eintrag lesen",
        "HO": "den Figurenteil verwenden", "LSH": "den Ringgang markieren", "SOLK": "an die Sammelstelle binden",
    },
    "PHARMA": {
        "O": "den Zubereitungsgang ausführen", "OK": "den Ansatz beginnen", "CH": "die Zutat entnehmen",
        "CHD": "den Ansatz umsetzen", "CPH": "den Auszug auffangen oder nachführen",
        "CHK": "den Ansatz behandeln", "CTH": "den Ansatzstatus prüfen", "K": "die Zutat zugeben",
        "P": "die Zutat einsetzen", "R": "den Zustand markieren", "S": "und dann",
        "SH": "den Ansatz halten", "SHED": "den Ansatz ruhen lassen", "T": "die Zutat bearbeiten",
        "OR": "mit dem Gefäßansatz", "CFH": "die Zutat abpressen", "CHEO": "den Auszug verwenden",
        "HO": "den Zutatenteil nehmen", "LSH": "das Gefäß spülen", "SOLK": "im Gefäß sammeln",
    },
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def recipe_parts(recipe: str) -> list[str]:
    return [part for part in recipe.split("+") if part]


def atomic(recipe: str) -> str:
    values = []
    for component in recipe_parts(recipe):
        if component == "CARRIER_Q":
            continue
        if component.startswith("LOCAL_CHAR_"):
            values.append(component.removeprefix("LOCAL_CHAR_") + "-KENNZEICHEN")
        else:
            values.append(SHORT.get(component, component))
    return " · ".join(values)


def fluent(recipe: str, register: str) -> str:
    values = []
    for component in recipe_parts(recipe):
        if component == "CARRIER_Q":
            continue
        if component.startswith("LOCAL_CHAR_"):
            values.append("mit lokalem " + component.removeprefix("LOCAL_CHAR_") + "-Kennzeichen")
            continue
        value = COMMON_FLUENT.get(component) or REGISTER_FLUENT[register].get(component)
        values.append(value or SHORT.get(component, component).lower())
    return "; ".join(values)


def main() -> None:
    source_events = read_tsv(SOURCE_EVENTS)
    ordered = read_tsv(SOURCE_ORDERED)
    if len(source_events) != 2511 or len(ordered) != 240:
        raise RuntimeError("unexpected source inventory")
    by_code = {row["local_code"]: row for row in ordered}

    event_rows: list[dict[str, object]] = []
    owner_rows: list[dict[str, object]] = []
    for number, source in enumerate(source_events, start=1):
        old_code = source["local_code"]
        repair_origin = "UNCHANGED"
        owner_binding = "NO"
        owner_description = source["visible_owner_de"]
        recipe = source["component_recipe"]
        mode = source["meaning_mode"]
        analysis_source = source["form_analysis_source"]

        if old_code:
            repair = by_code[old_code]
            recipe = repair["revised_recipe"]
            owner_description = repair["visible_owner_or_default_de"]
            if repair["old_drawer"] == "PICTURED_NAME_OR_CLASS":
                mode = "OWNER_BOUND_COMPOUND_LABEL"
                repair_origin = "PASS911_OWNER_LABEL"
                owner_binding = "YES"
            else:
                mode = "CPH_COMPONENT_COMPOSITION" if "CPH" in recipe_parts(recipe) else "REPAIRED_COMPONENT_COMPOSITION"
                repair_origin = "PASS911_WORKSHOP_CARD"
            analysis_source = "PASS911_LOCAL_DRAWER_REPAIR"
        elif source["surface"] == "cphy":
            recipe = "CPH+Y"
            mode = "CPH_COMPONENT_COMPOSITION"
            repair_origin = "PASS911_CPH_EXTERNAL"
            analysis_source = "PASS911_CPH_FAMILY_REPAIR"

        literal = atomic(recipe)
        fluent_value = fluent(recipe, source["register"])
        if owner_binding == "YES":
            fluent_value = f"Bild-/Musterwert: {owner_description}"
            owner_rows.append({
                "event_id": f"P912-E{number:04d}",
                "prior_local_code": old_code,
                "surface": source["surface"],
                "register": source["register"],
                "physical_page": source["physical_page"],
                "source_page": source["source_page"],
                "locus": source["locus"],
                "owner_description_de": owner_description,
                "component_recipe": recipe,
                "atomic_reading_de": literal,
                "owner_bound_reading_de": fluent_value,
            })

        event_rows.append({
            "event_id": f"P912-E{number:04d}",
            "pass910_event_id": source["event_id"],
            "dictionary_entry_id": "",
            "physical_page": source["physical_page"],
            "source_page": source["source_page"],
            "register": source["register"],
            "locus": source["locus"],
            "source_kind": source["source_kind"],
            "usage_class": source["usage_class"],
            "line_order": source["line_order"],
            "token_index": source["token_index"],
            "surface": source["surface"],
            "visible_owner_de": source["visible_owner_de"],
            "owner_binding_required": owner_binding,
            "owner_description_de": owner_description,
            "component_recipe": recipe,
            "meaning_mode": mode,
            "repair_origin": repair_origin,
            "prior_local_code": old_code or "NONE",
            "atomic_reading_de": literal,
            "fluent_token_de": fluent_value,
            "line_is_sentence_end": source["line_is_sentence_end"],
            "analysis_source": analysis_source,
        })

    dictionary_groups: dict[tuple[str, ...], list[dict[str, object]]] = defaultdict(list)
    for row in event_rows:
        key = tuple(str(row[field]) for field in (
            "surface", "register", "usage_class", "component_recipe", "meaning_mode", "owner_binding_required"
        ))
        dictionary_groups[key].append(row)

    dictionary_rows = []
    for number, (key, members) in enumerate(sorted(dictionary_groups.items()), start=1):
        dictionary_id = f"P912-D{number:04d}"
        for member in members:
            member["dictionary_entry_id"] = dictionary_id
        first = members[0]
        dictionary_rows.append({
            "dictionary_entry_id": dictionary_id,
            "surface": first["surface"],
            "register": first["register"],
            "usage_class": first["usage_class"],
            "component_recipe": first["component_recipe"],
            "meaning_mode": first["meaning_mode"],
            "owner_binding_required": first["owner_binding_required"],
            "events": len(members),
            "physical_pages": "|".join(sorted({str(row["physical_page"]) for row in members})),
            "loci": "|".join(sorted({str(row["locus"]) for row in members})),
            "atomic_default_de": first["atomic_reading_de"],
            "fluent_default_de": (
                "sichtbaren Besitzer als Namen/Klasse lesen; Komponenten nur als Klassifikator-Hypothese"
                if first["owner_binding_required"] == "YES" else first["fluent_token_de"]
            ),
        })

    event_fields = [
        "event_id", "pass910_event_id", "dictionary_entry_id", "physical_page", "source_page", "register",
        "locus", "source_kind", "usage_class", "line_order", "token_index", "surface", "visible_owner_de",
        "owner_binding_required", "owner_description_de", "component_recipe", "meaning_mode", "repair_origin",
        "prior_local_code", "atomic_reading_de", "fluent_token_de", "line_is_sentence_end", "analysis_source",
    ]
    write_tsv(EVENTS_OUT, event_rows, event_fields)
    write_tsv(DICTIONARY_OUT, dictionary_rows, [
        "dictionary_entry_id", "surface", "register", "usage_class", "component_recipe", "meaning_mode",
        "owner_binding_required", "events", "physical_pages", "loci", "atomic_default_de", "fluent_default_de",
    ])
    write_tsv(OWNER_OUT, owner_rows, [
        "event_id", "prior_local_code", "surface", "register", "physical_page", "source_page", "locus",
        "owner_description_de", "component_recipe", "atomic_reading_de", "owner_bound_reading_de",
    ])

    locus_groups: dict[tuple[str, str, str, str], list[dict[str, object]]] = defaultdict(list)
    for row in event_rows:
        locus_groups[(str(row["physical_page"]), str(row["source_page"]), str(row["register"]), str(row["locus"]))].append(row)
    locus_rows = []
    for number, ((page, source_page, register, locus), members) in enumerate(locus_groups.items(), start=1):
        locus_rows.append({
            "locus_order": number,
            "physical_page": page,
            "source_page": source_page,
            "register": register,
            "locus": locus,
            "source_kind": members[0]["source_kind"],
            "events": len(members),
            "owner_bound_events": sum(row["owner_binding_required"] == "YES" for row in members),
            "repaired_events": sum(row["repair_origin"] != "UNCHANGED" for row in members),
            "surface_sequence": " · ".join(str(row["surface"]) for row in members),
            "atomic_sequence_de": " | ".join(str(row["atomic_reading_de"]) for row in members),
            "continuous_reading_de": "; ".join(str(row["fluent_token_de"]) for row in members),
            "physical_line_is_sentence_end": "NO",
        })
    write_tsv(LOCI_OUT, locus_rows, [
        "locus_order", "physical_page", "source_page", "register", "locus", "source_kind", "events",
        "owner_bound_events", "repaired_events", "surface_sequence", "atomic_sequence_de",
        "continuous_reading_de", "physical_line_is_sentence_end",
    ])

    page_rows = []
    for page in PAGE_ORDER:
        members = [row for row in event_rows if row["physical_page"] == page]
        loci = [row for row in locus_rows if row["physical_page"] == page]
        page_rows.append({
            "page_order": PAGE_ORDER.index(page) + 1,
            "physical_page": page,
            "register": "|".join(sorted({str(row["register"]) for row in members})),
            "source_pages": "|".join(sorted({str(row["source_page"]) for row in members})),
            "loci": len(loci),
            "events": len(members),
            "surface_types": len({str(row["surface"]) for row in members}),
            "dictionary_entries": len({str(row["dictionary_entry_id"]) for row in members}),
            "owner_bound_labels": sum(row["owner_binding_required"] == "YES" for row in members),
            "repaired_workshop_events": sum(row["repair_origin"] == "PASS911_WORKSHOP_CARD" for row in members),
            "cph_events": sum("CPH" in recipe_parts(str(row["component_recipe"])) for row in members),
        })
    write_tsv(PAGES_OUT, page_rows, [
        "page_order", "physical_page", "register", "source_pages", "loci", "events", "surface_types",
        "dictionary_entries", "owner_bound_labels", "repaired_workshop_events", "cph_events",
    ])

    components = read_tsv(SOURCE_EXPANSIONS)
    components.append({
        "component": "CPH", "layer": "B_REGISTER_OPERATOR", "portable_value_de": "GEGEN- ODER EMPFANGSGANG",
        "herbal_de": "Nachlauf oder zweiter Durchgang", "biological_de": "Rücklauf zur Empfangsstation",
        "zodiac_de": "Gegen- oder Rückstelle im Rad", "pharma_de": "Auszug auffangen oder nachführen",
        "pass909_decision": "PASS911_NEW_REGISTER_ROOT",
    })
    components.sort(key=lambda row: row["component"])
    write_tsv(COMPONENTS_OUT, components, [
        "component", "layer", "portable_value_de", "herbal_de", "biological_de", "zodiac_de",
        "pharma_de", "pass909_decision",
    ])

    rules = [
        {"rule": "OWNER_ARGUMENT", "trigger": "LABEL OR DIAGRAM_TEXT", "reading": "Setze den sichtbaren Besitzer als Argument der Komponentenformel ein.", "examples": "otar; otal; ykchy"},
        {"rule": "CPH_TOPOLOGY", "trigger": "cph inside a licensed card", "reading": "Lies einen Gegen-/Empfangsgang; wähle erst im Register Nachlauf, Rücklauf, Gegenstelle oder Auffangen.", "examples": "cphy; cphedy; cphal; cphol"},
        {"rule": "N_ELISION_BEFORE_R", "trigger": "aiir or oiir before final R", "reading": "Lies IIN/AIIN + R ohne ausgeschriebenes Schluss-n.", "examples": "doiir; saiir; soraiir"},
        {"rule": "DY_LICENSE", "trigger": "licensed recipe ending in DY", "reading": "Schließe den Schritt; nacktes sichtbares dy kann weiterhin Y sein.", "examples": "kedy; ytody; cphedy"},
        {"rule": "Q_CARRIER", "trigger": "initial q in licensed family", "reading": "Q trägt die Karte und fügt keinen eigenen Sachwert hinzu.", "examples": "qedy; qody; qop"},
        {"rule": "LINE_CONTINUATION", "trigger": "physical locus boundary", "reading": "Eine physische Zeile beendet die Aussage nicht automatisch.", "examples": "all 464 loci"},
    ]
    write_tsv(RULES_OUT, rules, ["rule", "trigger", "reading", "examples"])

    edition = ["# Pass 912 — vollständige Vierzehn-Seiten-Ausgabe", ""]
    for page in PAGE_ORDER:
        page_row = next(row for row in page_rows if row["physical_page"] == page)
        edition += [
            f"## {page}", "",
            f"{page_row['events']} Gruppen in {page_row['loci']} Loci; "
            f"{page_row['owner_bound_labels']} Besitzeretiketten; {page_row['repaired_workshop_events']} reparierte Arbeitskarten.",
            "",
        ]
        for row in [row for row in locus_rows if row["physical_page"] == page]:
            edition.append(f"- **{row['locus']}** — `{row['surface_sequence']}` → {row['continuous_reading_de']}")
        edition.append("")
    EDITION_OUT.write_text("\n".join(edition).rstrip() + "\n", encoding="utf-8")

    handbook = [
        "# Pass 912 — Lehrlingshandbuch", "",
        "1. Erkenne zuerst Register und sichtbaren Besitzer.",
        "2. Lies die fünfzehn portablen Kerne und die kurze Registeroperation.",
        "3. Bei `CPH` lies zuerst Gegen-/Empfangsgang, erst dann den Registerwert.",
        "4. Eine Bildkennung bleibt ein gelernter Name/Klassenwert; ihre Komponenten dürfen nur als Adress- oder Klassifikator-Hypothese mitgelesen werden.",
        "5. `E/EE/EEE` staffeln kurz/länger/voll; `IIN` setzt die Stufe.",
        "6. `Y` hält den aktuellen Posten; nur eine lizenzierte `DY`-Karte schließt.",
        "7. Vor `R` darf das n von `IIN/AIIN` fehlen.",
        "8. Physische Zeilen werden beim Lesen weitergeführt, sofern kein Kartenabschluss vorliegt.",
        "", "## Neue Arbeitsbeispiele", "",
        "- `Y–CH–O–CPH–Y`: diesen Pflanzenposten entnehmen, in den Nachlauf geben und als aktuellen Posten halten.",
        "- `CPH–E–DY`: den Empfangsgang kurz ausführen und schließen.",
        "- `Y–T–E–DY`: diesen Posten kurz bearbeiten/markieren und schließen.",
        "- `S–AM`: den Kontextwert am Gegen-/Innenfeld lesen.",
        "- `D–O–IIN–R`: den Teilgang auf der markierten Stufe lesen.",
    ]
    HANDBOOK_OUT.write_text("\n".join(handbook) + "\n", encoding="utf-8")

    modes = Counter(str(row["meaning_mode"]) for row in event_rows)
    origins = Counter(str(row["repair_origin"]) for row in event_rows)
    report = [
        "# Pass 912 — revidiertes Vierzehn-Seiten-Handbuch", "",
        "## Ergebnis", "",
        "Alle 2511 Gruppen und 464 Loci sind mit der Pass-911-Ordnung neu ausgegeben.",
        "Die früheren 63 Ganzkartenereignisse sind nun Kompositionen; 198 Bildetiketten",
        "bleiben Besitzer-gebundene Namen/Klassen mit einer zusätzlichen Formzerlegung. Zusätzlich wurde das ältere `cphy`",
        "in die neue CPH-Familie aufgenommen. Keine Ereigniszeile trägt mehr `WHOLE[...]`,",
        "`LOCAL_WORKSHOP_CARD` oder `LOCAL_NOMENCLATOR`.", "",
        "## Bilanz", "",
        f"- Ereignisse: {len(event_rows)}",
        f"- Wörterbucheinträge: {len(dictionary_rows)}",
        f"- Loci: {len(locus_rows)}",
        f"- Besitzer-gebundene Etiketten: {len(owner_rows)}",
        f"- CPH-Ereignisse: {sum('CPH' in recipe_parts(str(row['component_recipe'])) for row in event_rows)}",
        f"- Komponenten: {len(components)}",
        "", "## Leseschlüssel", "",
        "Der sichtbare Besitzer liefert den konkreten Namen/Klassenwert. Die Kartenform kann",
        "zusätzlich Auswahl, Adresse, Reihenfolge, Grad, Lauf oder Abschluss tragen. Eine",
        "Figurbeischrift mit `OT + AL + Y` wird daher als sichtbarer Figurenwert plus mögliche",
        "Klassenform DANACH–ZIELSTELLE–POSTEN gelesen, nicht als sicherer Arbeitssatz.", "",
        "## Nächster Hebel", "",
        "Die nächste Runde soll nicht wieder das Inventar vergrößern. Sie soll innerhalb der",
        "198 Besitzeretiketten prüfen, welche Formeln wiederholt dieselbe räumliche Rolle",
        "tragen: Zentrum, Außenfigur, obere/untere Beckenstation, Zutatenplatz oder Ringsektor.",
        "Daraus kann eine kleine konkrete Adresssyntax entstehen.",
    ]
    REPORT_OUT.write_text("\n".join(report) + "\n", encoding="utf-8")

    summary = {
        "pass": 912,
        "decision": "FOURTEEN_PAGE_REVISED_HANDBOOK__NO_OPAQUE_WORKSHOP_CARD__OWNER_NAMES_RETAINED",
        "events": len(event_rows),
        "dictionary_entries": len(dictionary_rows),
        "loci": len(locus_rows),
        "physical_pages": len(page_rows),
        "source_pages": len({str(row["source_page"]) for row in event_rows}),
        "owner_bound_label_events": len(owner_rows),
        "cph_events": sum("CPH" in recipe_parts(str(row["component_recipe"])) for row in event_rows),
        "meaning_modes": dict(sorted(modes.items())),
        "repair_origins": dict(sorted(origins.items())),
        "source_hashes": {path.name: sha(path) for path in (SOURCE_EVENTS, SOURCE_EXPANSIONS, SOURCE_ORDERED)},
        "output_hashes": {path.name: sha(path) for path in (
            EVENTS_OUT, DICTIONARY_OUT, LOCI_OUT, PAGES_OUT, OWNER_OUT, COMPONENTS_OUT,
            RULES_OUT, EDITION_OUT, HANDBOOK_OUT, REPORT_OUT,
        )},
    }
    SUMMARY_OUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

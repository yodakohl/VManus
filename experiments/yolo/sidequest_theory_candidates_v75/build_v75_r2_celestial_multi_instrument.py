#!/usr/bin/env python3
"""Build V75 R2: a complete, image-repaired celestial multi-instrument edition.

The algorithm binds opaque Astro groups to V71 local visible owners and gives
each occurrence a copied local exemplar-label context. It never reads surface
spelling, imports prose cards, or assigns a common orientation or cross-page
key. Content is a historical working edition, not decipherment.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
V66 = ROOT / "experiments/yolo/sidequest_theory_candidates_v66"
V69 = ROOT / "experiments/yolo/sidequest_theory_candidates_v69"
V70 = ROOT / "experiments/yolo/sidequest_theory_candidates_v70"
V71 = ROOT / "experiments/yolo/sidequest_theory_candidates_v71"
OUT = ROOT / "experiments/yolo/sidequest_theory_candidates_v75"

GROUPS_IN = V69 / "V69_R4_FINAL_395_ASTRO_GROUPS.tsv"
OWNERS_IN = V71 / "V71_SELECTED_OWNER_LEDGER.tsv"
IMAGES_IN = V70 / "V70_SELECTED_TEN_PAGE_IMAGE_REVISION.tsv"
SOURCES_IN = V66 / "V66_R2_HISTORICAL_SOURCES.tsv"

GROUPS_OUT = OUT / "V75_R2_395_ASTRO_GROUPS.tsv"
LOCI_OUT = OUT / "V75_R2_142_ASTRO_LOCI.tsv"
INSTRUMENTS_OUT = OUT / "V75_R2_THREE_CELESTIAL_INSTRUMENTS.tsv"
SOURCES_OUT = OUT / "V75_R2_HISTORICAL_SOURCE_AUDIT.tsv"
ORIENTATION_OUT = OUT / "V75_R2_ORIENTATION_ALTERNATIVES.tsv"
UNSUPPORTED_OUT = OUT / "V75_R2_UNSUPPORTED_LABELS.tsv"
REPORT_OUT = OUT / "V75_R2_CELESTIAL_MULTI_INSTRUMENT_REPORT.md"


R2_BACKGROUND = [
    "Du kennst zeitgenössische Herbarien, Materia medica, Rezeptbücher, Abkürzungen und kompilierte Sammelhandschriften.",
    "Du vergleichst Namen, Beschreibungen, Qualitäten, Habitate, Zubereitungen, Anwendungen und Rezeptfortsetzungen.",
    "Du unterscheidest überlieferte Textpraxis von modernen Tabellen-, Datenbank- oder Übersetzungsannahmen.",
    "Du darfst historische Quellen recherchieren, aber niemals Voynich-Formen über Klang oder Buchstabenähnlichkeit zuordnen.",
    "Du lieferst die historisch plausibelste Quelltextstruktur samt Gegenbelegen und eng begrenzter Pseudoübersetzung.",
]


PAGE_SYSTEM = {
    "f67r2": "PAIRED_BUT_DISCONNECTED_CELESTIAL_REFERENCE_WHEELS",
    "f68r1": "MULTIPANEL_STAR_FIELD_ATLAS_WITH_SEVERAL_CENTRES",
    "f69v": "THREE_DISCONNECTED_HETEROGENEOUS_CELESTIAL_WHEELS",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def numeric_suffix(owner: str) -> int | None:
    match = re.search(r"_(\d+)$", owner)
    return int(match.group(1)) if match else None


def copied_locus_reading(owner: str) -> str:
    number = numeric_suffix(owner)
    if owner.startswith("A1_RIGHT_SECTOR_SLOT_"):
        return (
            f"Rechtes f67r2-Rad, lokaler Zeichen- oder Kalendersektor R{number:02d}: "
            "Ein einzelner Himmelsabschnitt wird aus dem Werkstattexemplar kopiert und nur mit den Ringangaben dieses rechten Rades gelesen; "
            "die Sektornummer ist eine editoriale Adresse, kein festgelegter Tierkreis- oder Monatsname."
        )
    if owner.startswith("A1_RIGHT_RING_BAND_"):
        return (
            f"Rechtes f67r2-Rad, Ringband R{number:02d}: Örtliche Rubrik für die Zeichen-, Kalender- oder Sektorordnung dieses Rades; "
            "sie erläutert ausschließlich den eigenen Ring und stellt keine Verbindung zum linken Rad her."
        )
    if owner.startswith("A1_LEFT_LOCAL_FIELD_"):
        return (
            f"Linkes f67r2-Rad, lokales Radial- oder Ringfeld L{number:02d}: Ein Stern-, Strahlen- oder Aspektvermerk wird an dieser Stelle "
            "aus dem Exemplar kopiert und nur im linken Rad nachgeschlagen; genauer Himmelsname und Gebrauchswert bleiben unbekannt."
        )
    if owner.startswith("A1_LEFT_OUTER_STAR_STATION_"):
        return (
            f"Linkes f67r2-Rad, äußerer Sternplatz L{number:02d}: Lokales Stern- oder Himmelspositionsetikett mit eigenem Begleitvermerk; "
            "der sichtbare Stern macht weder seine astronomische Identität noch eine Reihenfolge kenntlich."
        )
    if owner.startswith("A1_RIGHT_PHASE_STATION_"):
        return (
            f"Rechtes f67r2-Rad, Scheiben- oder Bedingungsplatz R{number:02d}: Lokale Phasen-, Licht- oder Kalenderbedingung für dieses Rad; "
            "die genaue Bedingung wird nur als Exemplarwert kopiert und nicht aus ihrer Lage berechnet."
        )
    if owner == "A1_LEFT_OUTER_RING_TEXT":
        return (
            "Linkes f67r2-Rad, äußeres Textband: Selbständige Gebrauchsrubrik für die Stern-, Strahlen- und Randplätze des linken Rades; "
            "sie definiert weder einen Startpunkt noch eine Laufrichtung und reicht nicht in das rechte Rad."
        )
    if owner == "A1_RIGHT_OUTER_RING_TEXT":
        return (
            "Rechtes f67r2-Rad, äußeres Textband: Selbständige Zeichen-, Kalender- oder Phasenrubrik des rechten Rades; "
            "sie definiert weder einen Startpunkt noch eine Laufrichtung und reicht nicht in das linke Rad."
        )
    if owner == "A1_PAIRED_WHEEL_LEGEND_UNRESOLVED":
        return (
            "f67r2, unaufgelöste Seitenlegende: Der Text wird als lokaler Hinweis für eines der beiden sichtbaren Räder kopiert, "
            "doch das Bild entscheidet seinen Besitzer nicht; daraus wird keine Konkordanz zwischen den Rädern gebaut."
        )

    panel = {
        "A2_LEFT_PANEL_HEADER": "linken offenen Sternfeldes",
        "A2_MIDDLE_PANEL_HEADER": "mittleren Stern-/Zentralfeldes",
        "A2_RIGHT_PANEL_HEADER": "rechten sektorierten Teilbildes",
    }
    if owner in panel:
        return (
            f"f68r1, Rubrik des {panel[owner]}: Lokale Himmelsregion, Sternfeld- oder Kalendergruppe dieses einen Paneels; "
            "die Rubrik darf nicht auf die anderen Paneele oder Gesichtszentren vererbt werden."
        )
    if owner.startswith("A2_MULTIPANEL_HEADER_FRAGMENT_"):
        return (
            "f68r1, unaufgelöstes Fragment einer mehrpaneeligen Randrubrik: Der vollständige Hinweis wird aus dem Exemplar kopiert, "
            "doch sein genaues Sternfeld oder Zentrum bleibt unbestimmt; er liefert keinen seitenweiten Besitzer."
        )
    if owner == "A2_CENTRE_KEY_UNRESOLVED":
        return (
            "f68r1, unaufgelöste Zentrumsangabe: Lokales Etikett eines der sichtbaren Gesichtsmedaillons; welches Zentrum und welcher Himmelskörper gemeint sind, "
            "kann nur das Exemplar bestimmen, nicht die Textlage."
        )
    if owner.startswith("A2_STAR_STATION_"):
        return (
            f"f68r1, sichtbarer Sternplatz S{number:02d}: Lokales Stern-, Asterismus- oder Stationsetikett innerhalb seines Bildfeldes; "
            f"S{number:02d} ist nur eine editoriale Adresse, und die 28 gezählten Sternplätze bilden weder eine bewiesene Folge noch ein gemeinsames Rad."
        )
    if owner == "A2_CENTRAL_LEGEND_UNRESOLVED":
        return (
            "f68r1, unaufgelöste Zentrallegende eines Teilbildes: Ein lokaler Himmels- oder Kalenderhinweis wird aus dem Exemplar kopiert, "
            "aber weder Zentrum noch Paneel noch Lesereihenfolge sind sichtbar eindeutig."
        )

    if owner == "A3_LEFT_WHEEL_RING_TEXT":
        return (
            "f69v, Ringtext des linken Rades: Rubrik eines örtlichen 28-Platz-Inventars für Mondstationen oder vergleichbare Kalenderabschnitte; "
            "jeder Radialplatz ist ein eigener Nachschlageposten, doch Namen, Anfang, Richtung und zyklische Folge werden nicht aus der Zeichnung ergänzt."
        )
    if owner == "A3_MIDDLE_WHEEL_RING_TEXT":
        return (
            "f69v, Ringtext des mittleren Wolken- oder Wellenrades: Eigenständige Rubrik für örtliche Himmels-, Witterungs- oder Prognosezustände; "
            "das Wolkenmotiv trägt nur diese Arbeitslesung und beweist weder Wettersemantik noch eine Verbindung zu den Nachbarrädern."
        )
    if owner == "A3_RIGHT_WHEEL_RING_TEXT":
        return (
            "f69v, Ringtext des rechten Gesicht- oder Strahlenrades: Eigenständige Rubrik für eine örtliche Licht-, Planeten- oder Komplexionsangabe; "
            "das Gesicht identifiziert keinen bestimmten Himmelskörper und schafft keine Kante zu den beiden anderen Rädern."
        )
    if owner.startswith("A3_LEFT_RADIAL_SLOT_"):
        return (
            f"f69v, linker Radialplatz L{number:02d}: Lokales Mondstations- oder Kalenderabschnittsetikett aus dem Exemplar; "
            f"L{number:02d} ist nur eine editoriale Adresse, kein behaupteter Name, Rang, Startpunkt oder Handlungsschritt."
        )
    raise KeyError(owner)


def content_class(owner: str) -> str:
    rules = (
        ("A1_RIGHT_SECTOR_SLOT_", "RIGHT_WHEEL_CELESTIAL_OR_CALENDAR_SECTOR"),
        ("A1_RIGHT_RING_BAND_", "RIGHT_WHEEL_LOCAL_RING_RUBRIC"),
        ("A1_LEFT_LOCAL_FIELD_", "LEFT_WHEEL_STAR_RAY_OR_ASPECT_FIELD"),
        ("A1_LEFT_OUTER_STAR_STATION_", "LEFT_WHEEL_OUTER_STAR_POSITION"),
        ("A1_RIGHT_PHASE_STATION_", "RIGHT_WHEEL_PHASE_LIGHT_OR_CALENDAR_CONDITION"),
        ("A2_MULTIPANEL_HEADER_FRAGMENT_", "MULTIPANEL_HEADER_OWNER_UNRESOLVED"),
        ("A2_STAR_STATION_", "LOCAL_STAR_OR_ASTERISM_STATION"),
        ("A3_LEFT_RADIAL_SLOT_", "LEFT_WHEEL_LOCAL_28_PLACE_INVENTORY_ENTRY"),
    )
    for prefix, value in rules:
        if owner.startswith(prefix):
            return value
    exact = {
        "A1_LEFT_OUTER_RING_TEXT": "LEFT_WHEEL_LOCAL_RING_RUBRIC",
        "A1_RIGHT_OUTER_RING_TEXT": "RIGHT_WHEEL_LOCAL_RING_RUBRIC",
        "A1_PAIRED_WHEEL_LEGEND_UNRESOLVED": "PAIRED_PAGE_LEGEND_OWNER_UNRESOLVED",
        "A2_LEFT_PANEL_HEADER": "LEFT_STAR_PANEL_RUBRIC",
        "A2_MIDDLE_PANEL_HEADER": "MIDDLE_STAR_PANEL_RUBRIC",
        "A2_RIGHT_PANEL_HEADER": "RIGHT_SECTORIZED_PANEL_RUBRIC",
        "A2_CENTRE_KEY_UNRESOLVED": "FACE_CENTRE_IDENTITY_UNRESOLVED",
        "A2_CENTRAL_LEGEND_UNRESOLVED": "CENTRAL_PANEL_LEGEND_UNRESOLVED",
        "A3_LEFT_WHEEL_RING_TEXT": "LEFT_28_PLACE_WHEEL_RUBRIC",
        "A3_MIDDLE_WHEEL_RING_TEXT": "MIDDLE_SKY_WEATHER_PROGNOSTIC_RUBRIC",
        "A3_RIGHT_WHEEL_RING_TEXT": "RIGHT_LIGHT_PLANET_COMPLEXION_RUBRIC",
    }
    return exact[owner]


def local_namespace(owner: str) -> str:
    if owner.startswith("A1_RIGHT_"):
        return "A1_RIGHT_WHEEL_ONLY"
    if owner.startswith("A1_LEFT_"):
        return "A1_LEFT_WHEEL_ONLY"
    if owner == "A1_PAIRED_WHEEL_LEGEND_UNRESOLVED":
        return "A1_OWNER_UNRESOLVED_NO_JOIN"
    if owner.startswith("A2_LEFT_"):
        return "A2_LEFT_PANEL_ONLY"
    if owner.startswith("A2_MIDDLE_"):
        return "A2_MIDDLE_PANEL_ONLY"
    if owner.startswith("A2_RIGHT_"):
        return "A2_RIGHT_PANEL_ONLY"
    if owner.startswith("A2_STAR_STATION_"):
        return "A2_LOCAL_STAR_FIELD_ONLY__PANEL_NOT_INFERRED"
    if owner.startswith("A2_"):
        return "A2_LOCAL_OWNER_UNRESOLVED"
    if owner.startswith("A3_LEFT_"):
        return "A3_LEFT_WHEEL_ONLY"
    if owner.startswith("A3_MIDDLE_"):
        return "A3_MIDDLE_WHEEL_ONLY"
    if owner.startswith("A3_RIGHT_"):
        return "A3_RIGHT_WHEEL_ONLY"
    raise KeyError(owner)


def rival(owner: str) -> str:
    if owner.startswith("A1_RIGHT_SECTOR_SLOT_"):
        return "Astronomisch-kalendarischer Rivale: zwölf bloße Lehr-, Farb- oder Teilungssektoren ohne Auswahlfunktion."
    if owner.startswith("A1_LEFT_"):
        return "Astronomischer Rivale: dekorative Stern-/Strahlenposition oder kopierte Lehrliste ohne Aspekt- oder Gebrauchsfunktion."
    if owner.startswith("A1_RIGHT_"):
        return "Kalenderischer Rivale: selbständige Phasen-, Monats- oder Lehrscheibe ohne Bezug zum linken Rad."
    if owner.startswith("A1_"):
        return "Formaler Rivale: seitenlokale Legende, deren Bildbesitzer und Funktion nicht auflösbar sind."
    if owner.startswith("A2_STAR_STATION_"):
        return "Astronomischer Rivale: dekorativer Sternplatz oder unverbundene Sternnamensammlung ohne Stationssystem."
    if owner.startswith("A2_"):
        return "Formaler Rivale: unabhängige Paneel- oder Zentrumslegende ohne gemeinsamen Atlasalgorithmus."
    if owner.startswith("A3_LEFT_RADIAL_SLOT_") or owner == "A3_LEFT_WHEEL_RING_TEXT":
        return "Kalenderischer Rivale: 28 Grad-, Teilungs- oder Gedächtnisplätze ohne Mondhausnamen, Ordnung oder Operation."
    if owner == "A3_MIDDLE_WHEEL_RING_TEXT":
        return "Astronomisch-formaler Rivale: selbständiger Qualitäts-, Wolken- oder Schmuckring ohne Wetterprognose."
    if owner == "A3_RIGHT_WHEEL_RING_TEXT":
        return "Astronomisch-formaler Rivale: selbständiger Sonnen-, Mond-, Planeten- oder Schmuckring ohne Komplexionsfunktion."
    raise KeyError(owner)


def contradiction(owner: str) -> str:
    clauses = ["kein sichtbarer Textanker identifiziert den konkreten externen Himmels- oder Kalenderwert"]
    if owner.startswith("A1_"):
        clauses.append("zwischen linkem und rechtem Rad fehlt jede gezeichnete Kante")
    if owner.startswith("A2_"):
        clauses.append("mehrere Paneele und Gesichtszentren widerlegen einen einzigen Seitenmittelpunkt")
    if owner.startswith("A3_"):
        clauses.append("die drei Räder sind heterogen und voneinander getrennt")
    if "RADIAL_SLOT" in owner or "SECTOR_SLOT" in owner or "STAR_STATION" in owner:
        clauses.append("Adresse und Zählrichtung sind editorisch")
    if owner.startswith("A2_") and ("UNRESOLVED" in owner or "HEADER_FRAGMENT" in owner):
        clauses.append("selbst der genaue lokale Bildbesitzer bleibt unaufgelöst")
    if owner == "A1_PAIRED_WHEEL_LEGEND_UNRESOLVED":
        clauses.append("selbst der genaue lokale Bildbesitzer bleibt unaufgelöst")
    text = "; ".join(clauses)
    return text[0].upper() + text[1:] + "."


def source_status(owner_status: str) -> str:
    return {
        "DIRECT_VISIBLE": "VISIBLE_LOCAL_OWNER__HISTORICAL_CONTENT_CLASS_EXEMPLAR_ONLY",
        "INHERITED_VISIBLE": "INHERITED_LOCAL_OWNER__HISTORICAL_CONTENT_CLASS_EXEMPLAR_ONLY",
        "PAGE_OWNER_ONLY": "PANEL_OWNER_ONLY__HISTORICAL_CONTENT_CLASS_EXEMPLAR_ONLY",
        "UNRESOLVED": "VISIBLE_CONTEXT_BUT_OWNER_UNRESOLVED__FORMAL_COPY_DEFAULT",
    }[owner_status]


def content_confidence(page: str, owner_status: str, owner_confidence: str) -> float:
    if owner_status == "UNRESOLVED":
        return 0.18
    if owner_status == "INHERITED_VISIBLE" and owner_confidence == "LOW":
        return 0.24
    if owner_status == "PAGE_OWNER_ONLY":
        return 0.30
    if page == "f69v":
        return 0.38
    if owner_confidence == "HIGH":
        return 0.40
    return 0.32


def unsupported_for_owner(owner: str) -> list[str]:
    values: list[str] = []
    if owner.startswith("A1_RIGHT_SECTOR_SLOT_"):
        values += ["A1_RIGHT_EXACT_SIGN_OR_MONTH", "AUTHORIAL_START_AND_DIRECTION"]
    elif owner.startswith("A1_LEFT_"):
        values += ["A1_LEFT_EXACT_STAR_ASPECT_OR_CALENDAR_VALUE", "AUTHORIAL_START_AND_DIRECTION"]
    elif owner.startswith("A1_RIGHT_"):
        values += ["A1_RIGHT_EXACT_PHASE_OR_CONDITION_VALUE", "AUTHORIAL_START_AND_DIRECTION"]
    elif owner.startswith("A1_"):
        values += ["A1_LEGEND_OWNER"]
    if owner.startswith("A1_"):
        values += ["A1_INTERWHEEL_RELATION"]
    if owner.startswith("A2_STAR_STATION_"):
        values += ["A2_EXACT_STAR_OR_ASTERISM_IDENTITY", "A2_UNIFIED_28_OBJECT"]
    elif owner.startswith("A2_"):
        values += ["A2_PANEL_OR_CENTRE_IDENTITY", "A2_COMMON_CENTRE_OR_ORDER"]
    if owner.startswith("A3_LEFT_"):
        values += ["A3_LEFT_EXACT_28_PLACE_NAMES", "AUTHORIAL_START_AND_DIRECTION"]
    elif owner.startswith("A3_MIDDLE_"):
        values += ["A3_MIDDLE_WEATHER_OR_PROGNOSTIC_FUNCTION", "AUTHORIAL_START_AND_DIRECTION"]
    elif owner.startswith("A3_RIGHT_"):
        values += ["A3_RIGHT_PLANET_LIGHT_OR_COMPLEXION_IDENTITY", "AUTHORIAL_START_AND_DIRECTION"]
    if owner.startswith("A3_"):
        values += ["A3_INTERWHEEL_RELATION"]
    values += ["IATROMEDICAL_APPLICATION"]
    if owner.startswith(("A2_", "A3_")):
        values += ["F68_F69_DIRECT_KEY"]
    return list(dict.fromkeys(values))


def aggregate(values: list[str]) -> str:
    return "|".join(dict.fromkeys(values))


def build() -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]], list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    source_groups = read_tsv(GROUPS_IN)
    owners = {
        r["unit_id"]: r for r in read_tsv(OWNERS_IN)
        if r["unit_kind"] == "ASTRO_LOCUS"
    }
    images = {
        r["page"]: r for r in read_tsv(IMAGES_IN) if r["section"] == "ASTRO"
    }

    locus_members: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in source_groups:
        locus_members[row["locus"]].append(row)

    group_rows: list[dict[str, str]] = []
    for source in source_groups:
        owner_row = owners[source["locus"]]
        owner = owner_row["selected_visible_owner"]
        members = locus_members[source["locus"]]
        full = copied_locus_reading(owner)
        index = int(source["event_index"])
        count = len(members)
        segment = (
            f"Vollständiges lokales Etikett: {full}"
            if count == 1
            else f"Kopiersegment {index:02d}/{count:02d} derselben lokalen Etikette; Einzelwortwert unbekannt. Vollständige Etikette: {full}"
        )
        group_rows.append({
            "group_serial": source["group_serial"],
            "diagram_id": source["diagram_id"],
            "page": source["page"],
            "locus": source["locus"],
            "event_index": source["event_index"],
            "opaque_local_id": source["opaque_local_id"],
            "local_image_owner": owner,
            "owner_status": owner_row["owner_status"],
            "owner_confidence": owner_row["confidence"],
            "local_namespace": local_namespace(owner),
            "local_content_class": content_class(owner),
            "copied_local_meaning_or_label": segment,
            "copied_label_source_status": source_status(owner_row["owner_status"]),
            "meaning_confidence": f"{content_confidence(source['page'], owner_row['owner_status'], owner_row['confidence']):.2f}",
            "strongest_astronomical_calendar_or_formal_rival": rival(owner),
            "strongest_contradiction": contradiction(owner),
            "unsupported_labels": "|".join(unsupported_for_owner(owner)),
            "orientation_status": "LOCAL_EDITORIAL_ADDRESS_ONLY__NO_AUTHORIAL_START_ROTATION_OR_DIRECTION",
            "f68_f69_mapping": "NONE__NO_VISIBLE_KEY",
            "prose_card_import": "NONE",
            "semantic_ceiling": "LOCAL_COPIED_EXEMPLAR_LABEL_NOT_WORD_SOUND_CARD_STEM_POS_OR_TRANSLATION",
        })

    by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_page: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in group_rows:
        by_locus[row["locus"]].append(row)
        by_page[row["page"]].append(row)

    locus_rows: list[dict[str, str]] = []
    for locus, members in by_locus.items():
        owner_row = owners[locus]
        owner = owner_row["selected_visible_owner"]
        locus_rows.append({
            "page": members[0]["page"],
            "diagram_id": members[0]["diagram_id"],
            "locus": locus,
            "group_count": str(len(members)),
            "group_serials": "|".join(r["group_serial"] for r in members),
            "opaque_group_ids": "|".join(r["opaque_local_id"] for r in members),
            "local_image_owner": owner,
            "owner_status": owner_row["owner_status"],
            "owner_confidence": owner_row["confidence"],
            "silent_argument_default": owner_row["silent_argument_default"],
            "local_namespace": members[0]["local_namespace"],
            "local_content_class": members[0]["local_content_class"],
            "complete_copied_local_meaning_or_label": copied_locus_reading(owner),
            "source_status": members[0]["copied_label_source_status"],
            "meaning_confidence": members[0]["meaning_confidence"],
            "strongest_rival": members[0]["strongest_astronomical_calendar_or_formal_rival"],
            "strongest_contradiction": members[0]["strongest_contradiction"],
            "unsupported_labels": members[0]["unsupported_labels"],
            "orientation_status": members[0]["orientation_status"],
            "f68_f69_mapping": "NONE__NO_VISIBLE_KEY",
            "image_geometry_guard": images[members[0]["page"]]["selected_geometry"],
            "semantic_ceiling": "LOCUS_BOUND_CELESTIAL_WORKING_LABEL_NOT_TRANSLATION",
        })

    instrument_summary = {
        "f67r2": (
            "Zwei getrennte Himmelsräder: rechts ein zwölfteiliger Zeichen-/Kalenderrahmen mit eigenen Ring- und Bedingungsfeldern, links ein Stern-/Strahlenrad mit lokalen Innen- und Außenplätzen. Beide werden nebeneinander kopiert, aber nicht miteinander verrechnet.",
            "Zwei unabhängige Lehr- oder Schmuckscheiben ohne Wahl-/Konkordanzfunktion.",
            "Keine Kante verbindet die Räder; Zeichen, Sterne, Start und Richtung sind nicht identifiziert.",
        ),
        "f68r1": (
            "Ein mehrpaneeliger Sternatlas aus zwei offenen Sternfeldern, einem sektorierten Teilbild und mehreren Gesichtszentren. Jede Rubrik und jeder Sternplatz bleibt im eigenen lokalen Bildfeld; die editorisch gezählten 28 Sternplätze sind kein einheitlicher Zyklus.",
            "Mehrere unabhängige Sternbilder, Lehrskizzen oder dekorative Himmelsfelder ohne gemeinsamen Atlasalgorithmus.",
            "Mehrere Zentren und unaufgelöste Rubriken verhindern einen seitenweiten Besitzer und eine gemeinsame Ordnung.",
        ),
        "f69v": (
            "Drei getrennte Instrumente: links ein lokales, ungeordnetes 28-Platz-Mondstations-/Kalenderinventar; mittig ein möglicher Himmels-/Witterungsring; rechts ein möglicher Licht-/Planeten-/Komplexionsring. Kein Wert wandert zwischen den Rädern.",
            "Drei unabhängige Kalender-, Qualitäts- oder bloße Formalräder; die linke 28er-Teilung kann ohne Mondhaussemantik bestehen.",
            "Nur links sind etwa 28 Radialplätze sichtbar; Namen, Reihenfolge, Start, Richtung und Funktionen aller drei Räder fehlen.",
        ),
    }
    instrument_rows: list[dict[str, str]] = []
    for page in ("f67r2", "f68r1", "f69v"):
        loci = [r for r in locus_rows if r["page"] == page]
        description, competing, counter = instrument_summary[page]
        continuous = " ".join(
            f"[{r['locus']} | {r['local_namespace']}] {r['complete_copied_local_meaning_or_label']}"
            for r in loci
        )
        instrument_rows.append({
            "diagram_id": loci[0]["diagram_id"],
            "page": page,
            "locus_count": str(len(loci)),
            "group_count": str(sum(int(r["group_count"]) for r in loci)),
            "repaired_visual_system": PAGE_SYSTEM[page],
            "continuous_instrument_description": continuous,
            "compact_historical_working_reading": description,
            "strongest_competing_instrument": competing,
            "strongest_counterevidence": counter,
            "orientation_status": "NO_COMMON_START_ROTATION_OR_DIRECTION",
            "crosspage_mapping": "NONE__F68_F69_KEY_ABSENT",
            "prose_card_import": "NONE",
            "semantic_ceiling": "THREE_PAGE_LOCAL_INSTRUMENT_EDITIONS_NOT_DECIPHERMENT",
        })

    source_application = {
        "S1": ("GENERAL_MIXED_ALMANAC_GENRE_ONLY", "Stützt die gemeinsame Buchökologie von Planeten, Medizin und Tabellen, aber kein einzelnes Rad oder Etikett."),
        "S2": ("GENERAL_IATROMATHEMATICAL_USE_ONLY", "Stützt einen praktischen medizinischen Almanachgebrauch, aber weder f67-Anordnung noch Voynich-Werte."),
        "S3": ("ZODIAC_TIMING_MECHANISM_ONLY", "Stützt Zeichen-/Mondzeit als medizinischen Auswahlrahmen, nicht die Identität eines f67-Sektors."),
        "S4": ("GENERAL_COMPOSITE_MANUSCRIPT_GENRE_ONLY", "Stützt astrologisch-medizinische Sammelhandschriften, nicht die Diagrammbelegung."),
        "S5": ("LOCAL_28_COMPARATOR_FOR_F69_LEFT_ONLY", "Stützt 28 Mondhausplätze als historische Möglichkeit; Namen, Start, Richtung, Operation und medizinische Spezialisierung bleiben unübertragen."),
        "S6": ("LOCAL_28_AND_SEVEN_ECOLOGY_ONLY", "Stützt das Nebeneinander von 28er- und 7er-Inventaren, aber keine sichtbare Verbindung der Voynich-Räder."),
        "S7": ("THIRTY_DAY_COUNTEREXAMPLE", "Das 30-Tage-Lunarium schwächt eine Gleichsetzung der linken 28 Plätze mit gewöhnlichen Mondtagen."),
        "S8": ("LATE_GENERAL_IATROMATHEMATICAL_COMPARATOR", "Stützt den Gattungsrahmen, ist aber später und identifiziert keinen lokalen Wert."),
    }
    source_rows: list[dict[str, str]] = []
    for source in read_tsv(SOURCES_IN):
        applicability, conclusion = source_application[source["source_id"]]
        source_rows.append({
            **source,
            "v75_applicability": applicability,
            "v75_audit_conclusion": conclusion,
            "permitted_target_scope": "GENRE_OR_LOCAL_COUNT_COMPARATOR_ONLY__NEVER_STRING_OR_LABEL_IDENTITY",
        })

    orientation_specs = [
        ("A1_RIGHT_WHEEL", "EDITORIAL_LOCUS_ORDER", "ADMITTED_NOT_SELECTED", "Ablageordnung der Transkription; kein Autorenanfang."),
        ("A1_RIGHT_WHEEL", "CLOCKWISE_ANY_ROTATIONAL_OFFSET", "ADMITTED_NOT_SELECTED", "Sichtbares Rad erlaubt diese Leseform, fixiert aber keinen Offset."),
        ("A1_RIGHT_WHEEL", "COUNTERCLOCKWISE_ANY_ROTATIONAL_OFFSET", "ADMITTED_NOT_SELECTED", "Ebenso bildverträglich; nicht zur Etikettvergabe benutzt."),
        ("A1_LEFT_WHEEL", "CLOCKWISE_OR_COUNTERCLOCKWISE_ANY_OFFSET", "ADMITTED_NOT_SELECTED", "Stern-/Strahlenrad ohne sichtbaren Startmarker."),
        ("A1_PAIRED_WHEELS", "INDEPENDENT_LOCAL_NAMESPACES", "SELECTED_VISUAL_GUARD", "Zwischen beiden Rädern fehlt eine Kante."),
        ("A2_MULTIPANEL", "LEFT_TO_RIGHT_COPY_ORDER", "ADMITTED_LAYOUT_ONLY", "Kann Schreiberreihenfolge sein, aber keine Himmelsfolge."),
        ("A2_MULTIPANEL", "INDEPENDENT_PANELS_NO_COMMON_ORDER", "SELECTED_VISUAL_GUARD", "Mehrere offene Felder, sektoriertes Teilbild und mehrere Zentren."),
        ("A2_STAR_STATIONS", "EDITORIAL_01_TO_28", "ADDRESS_ONLY_NOT_SEQUENCE", "Zählung dient ausschließlich der Edition."),
        ("A3_LEFT_28_WHEEL", "EDITORIAL_LOCUS_4_TO_31", "ADDRESS_ONLY_NOT_SEQUENCE", "28 Adressen, aber kein Autorenanfang."),
        ("A3_LEFT_28_WHEEL", "CLOCKWISE_ANY_ROTATIONAL_OFFSET", "ADMITTED_NOT_SELECTED", "Keine sichtbare Nullposition."),
        ("A3_LEFT_28_WHEEL", "COUNTERCLOCKWISE_ANY_ROTATIONAL_OFFSET", "ADMITTED_NOT_SELECTED", "Keine sichtbare Laufrichtung."),
        ("A3_MIDDLE_WHEEL", "EITHER_RING_DIRECTION_ANY_OFFSET", "UNRESOLVED_NOT_USED", "Ringtext ohne gerichtete Kante."),
        ("A3_RIGHT_WHEEL", "EITHER_RING_DIRECTION_ANY_OFFSET", "UNRESOLVED_NOT_USED", "Strahlen und Gesicht liefern keine Leserichtung."),
        ("A3_THREE_WHEELS", "INDEPENDENT_LOCAL_NAMESPACES", "SELECTED_VISUAL_GUARD", "Heterogene Räder ohne Verbindung."),
        ("A2_TO_A3", "NO_DIRECT_INDEX_OR_LOOKUP_KEY", "SELECTED_HARD_GUARD", "Gleiche oder ähnliche Anzahlen ersetzen keinen sichtbaren Schlüssel."),
    ]
    orientation_rows = [
        {
            "component": component,
            "orientation_or_mapping_alternative": alternative,
            "status": status,
            "visible_reason": reason,
            "used_to_assign_content": "NO",
            "semantic_ceiling": "ORIENTATION_ALTERNATIVE_NOT_VALUE_MAPPING",
        }
        for component, alternative, status, reason in orientation_specs
    ]

    audit_rationale = {
        "A1_RIGHT_EXACT_SIGN_OR_MONTH": "Zwölf sichtbare Sektoren lizenzieren weder Tierkreisnamen noch Monate oder deren Zuordnung.",
        "A1_LEFT_EXACT_STAR_ASPECT_OR_CALENDAR_VALUE": "Sterne und Strahlen tragen keinen extern identifizierten Stern-, Aspekt- oder Kalendernamen.",
        "A1_RIGHT_EXACT_PHASE_OR_CONDITION_VALUE": "Scheiben-/Bedingungsplätze besitzen keinen extern verankerten Phasen- oder Wahlwert.",
        "A1_LEGEND_OWNER": "Die Seitenlegende lässt sich keinem der beiden Räder sicher zuweisen.",
        "A1_INTERWHEEL_RELATION": "Zwischen linkem und rechtem Rad fehlt eine sichtbare Kante.",
        "A2_EXACT_STAR_OR_ASTERISM_IDENTITY": "Kein Sternplatz ist extern benannt oder mit einem bekannten Asterismus verankert.",
        "A2_UNIFIED_28_OBJECT": "Die 28 editorisch gezählten Sternplätze liegen in einer Mehrpaneelseite und bilden kein bewiesenes gemeinsames Objekt.",
        "A2_PANEL_OR_CENTRE_IDENTITY": "Paneel- und Gesichtsmedaillonidentitäten sind lokal sichtbar, aber inhaltlich unbekannt.",
        "A2_COMMON_CENTRE_OR_ORDER": "Mehrere Zentren verhindern eine einzige seitenweite Mitte oder Reihenfolge.",
        "A3_LEFT_EXACT_28_PLACE_NAMES": "Die lokale 28er-Teilung stützt eine Inventargröße, aber keine Mondhausnamen oder Einzelwerte.",
        "A3_MIDDLE_WEATHER_OR_PROGNOSTIC_FUNCTION": "Wolken-/Wellenikonographie macht eine Wetterlesung plausibel, beweist sie aber nicht.",
        "A3_RIGHT_PLANET_LIGHT_OR_COMPLEXION_IDENTITY": "Gesicht und Strahlen identifizieren weder Sonne, Mond, Planet noch medizinische Komplexion.",
        "A3_INTERWHEEL_RELATION": "Zwischen den drei heterogenen f69v-Rädern fehlt jede sichtbare Kante oder gemeinsame Adresse.",
        "AUTHORIAL_START_AND_DIRECTION": "Kein untersuchtes Rad besitzt einen sicher erkannten Autorenanfang oder Pfeil.",
        "IATROMEDICAL_APPLICATION": "Historische Gattung macht medizinische Nutzung möglich; kein lokales Label nennt sichtbar eine Behandlung.",
        "F68_F69_DIRECT_KEY": "Zwischen f68r1 und f69v ist kein sichtbarer Index, Anschluss oder gleichläufiger Schlüssel vorhanden.",
    }
    label_members: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in group_rows:
        for label in row["unsupported_labels"].split("|"):
            label_members[label].append(row)
    unsupported_rows: list[dict[str, str]] = []
    for label, members in sorted(label_members.items()):
        unsupported_rows.append({
            "unsupported_label_or_relation": label,
            "group_count": str(len(members)),
            "locus_count": str(len({r['locus'] for r in members})),
            "pages": aggregate([r["page"] for r in members]),
            "loci": aggregate([r["locus"] for r in members]),
            "rationale": audit_rationale[label],
            "working_edition_treatment": "KEEP_AS_EXEMPLAR_CLASS_OR_REMOVE_RELATION__NEVER_ASSIGN_EXACT_NAME",
            "semantic_ceiling": "UNSUPPORTED_EXTERNAL_LABEL_NOT_VOYNICH_MEANING",
        })
    return group_rows, locus_rows, instrument_rows, source_rows, orientation_rows, unsupported_rows


def build_report(
    groups: list[dict[str, str]],
    loci: list[dict[str, str]],
    instruments: list[dict[str, str]],
    sources: list[dict[str, str]],
    orientations: list[dict[str, str]],
    unsupported: list[dict[str, str]],
) -> str:
    owner_status = Counter(r["owner_status"] for r in loci)
    out = [
        "# V75 R2 — celestial multi-instrument third edition",
        "",
        "Status: vollständige historische Arbeitsedition; keine Entzifferung oder Übersetzung.",
        "",
        "## Unveränderter R2-Hintergrund",
        "",
    ]
    out += [f"{i}. {line}" for i, line in enumerate(R2_BACKGROUND, 1)]
    out += [
        "",
        "## Ergebnis",
        "",
        "Alle 395 Astro-Gruppen und 142 Loci besitzen nun ein lokales kopiertes Bedeutungs-/Etikettumfeld. Kein sichtbares Gruppenbild erhält eine portable Wortglosse: bei mehrgliedrigen Loci ist jede Gruppe nur `Kopiersegment i/n` derselben vollständigen lokalen Etikette.",
        "",
        f"Ownerstatus der 142 Loci: " + ", ".join(f"{k}={v}" for k, v in sorted(owner_status.items())) + ".",
        "",
        "Die f67-, f68- und f69-Seitenwerte leben in getrennten lokalen Namespaces. Es gibt keinen gemeinsamen Start, keine Rotation oder Richtung, keinen f68↔f69-Schlüssel, keinen Import aus dem Prosakartensatz und keine Zuordnung durch Oberflächenähnlichkeit.",
        "",
        "## Drei kontinuierliche Instrumentbeschreibungen",
        "",
    ]
    for row in instruments:
        out += [
            f"### {row['page']} — {row['repaired_visual_system']}",
            "",
            f"**Arbeitslesung:** {row['compact_historical_working_reading']}",
            "",
            f"**Vollständige locusgebundene Beschreibung:** {row['continuous_instrument_description']}",
            "",
            f"**Stärkster Rivale:** {row['strongest_competing_instrument']}",
            "",
            f"**Härtester Gegenbeleg:** {row['strongest_counterevidence']}",
            "",
        ]
    out += [
        "## Historische Quellenprüfung",
        "",
        "Die Vergleichsquellen kalibrieren nur Gattung oder lokale Inventargröße. Besonders S5/S6 machen ein 28-Platz-Inventar historisch möglich, jedoch ausschließlich für das linke f69v-Rad. S7s 30-Tage-Lunarium bleibt der konkrete Gegenbeleg gegen eine simple 28-Mondtage-Lesung.",
        "",
        "| ID | Datum | Vergleich | V75-Reichweite | Grenze |",
        "|---|---|---|---|---|",
    ]
    for row in sources:
        out.append(f"| {row['source_id']} | {row['date']} | [{row['institution_item']}]({row['url']}) | {row['v75_applicability']} | {row['v75_audit_conclusion']} |")
    out += [
        "",
        "## Orientierungs- und Verbindungsgrenze",
        "",
        f"Der Audit enthält {len(orientations)} explizite Alternativen. Uhrzeigersinn, Gegenuhrzeigersinn, beliebiger Rotationsversatz und Transkriptionsreihenfolge bleiben für die Räder offen. Ausgewählt werden nur die negativen Bildguards `INDEPENDENT_LOCAL_NAMESPACES` und `NO_DIRECT_INDEX_OR_LOOKUP_KEY`.",
        "",
        "Die Nummern R01, L01 oder S01 sind editoriale Adressen. Sie behaupten weder einen Autorstart noch Widder, Januar, ein bestimmtes Mondhaus oder einen Rang. f68r1s 28 Sternplätze werden nicht als ein Zyklus behandelt; f69v.4–.31 bleiben ein lokales, ungeordnetes 28er-Inventar des linken Rades.",
        "",
        "## Unsupported-label audit",
        "",
        f"{len(unsupported)} ungestützte externe Identitäten, Funktionen oder Relationen werden getrennt ausgewiesen. Dazu gehören konkrete Zeichen-/Monatsnamen, Stern- und Planetenidentitäten, Mondhausnamen, Wetter- und Komplexionsfunktion, medizinische Anwendung, Start/Richtung und ein f68↔f69-Schlüssel.",
        "",
        "Ein sichtbarer Stern, ein Gesicht, Wolkenlinien oder 28 Stäbe dürfen die lokale Quellklasse motivieren; sie lesen den externen Namen oder Zweck nicht aus. Der rein astronomisch-kalendarische und der rein formale Rivale bleiben an jedem Locus erhalten.",
        "",
        "## Interpretation ceiling",
        "",
        "Die Ausgabe etabliert höchstens eine vollständige, historisch mögliche Masterexemplar-Lesung für lokale Himmelsinstrumente. Sie bestätigt weder Tierkreiszeichen, Monate, Sterne, Planeten, Mondhäuser, Wetter, Komplexion, medizinische Wahlregeln noch irgendeinen Voynich-Gruppenwert. Oberfläche, Laut, Stamm, Karte, POS, Sprache und Übersetzung bleiben unbestimmt. f84 und f84r blieben versiegelt.",
        "",
        "## Reproduzierbarkeit",
        "",
        "```bash",
        "python experiments/yolo/sidequest_theory_candidates_v75/build_v75_r2_celestial_multi_instrument.py",
        "python experiments/yolo/sidequest_theory_candidates_v75/validate_v75_r2_celestial_multi_instrument.py",
        "```",
        "",
    ]
    return "\n".join(out)


def main() -> None:
    groups, loci, instruments, sources, orientations, unsupported = build()
    write_tsv(GROUPS_OUT, groups)
    write_tsv(LOCI_OUT, loci)
    write_tsv(INSTRUMENTS_OUT, instruments)
    write_tsv(SOURCES_OUT, sources)
    write_tsv(ORIENTATION_OUT, orientations)
    write_tsv(UNSUPPORTED_OUT, unsupported)
    REPORT_OUT.write_text(build_report(groups, loci, instruments, sources, orientations, unsupported), encoding="utf-8")
    print(json.dumps({
        "groups": len(groups),
        "loci": len(loci),
        "instruments": len(instruments),
        "historical_sources": len(sources),
        "orientation_alternatives": len(orientations),
        "unsupported_label_classes": len(unsupported),
        "groups_sha256": hashlib.sha256(GROUPS_OUT.read_bytes()).hexdigest(),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Build the frozen V71 R3 image-to-text owner ledger.

This is a creative sidequest compiler, not a semantic decoder.  Exact V69
field/locus identities are retained; V70 supplies only visible owner geometry.
"""

from __future__ import annotations

import csv
import json
from collections import OrderedDict, Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
FIELD_SOURCE = ROOT / "experiments/yolo/sidequest_theory_candidates_v69/V69_R4_FINAL_135_FIELD_EDITION.tsv"
ASTRO_SOURCE = ROOT / "experiments/yolo/sidequest_theory_candidates_v69/V69_R4_FINAL_395_ASTRO_GROUPS.tsv"
V70_SELECTED = ROOT / "experiments/yolo/sidequest_theory_candidates_v70/V70_SELECTED_TEN_PAGE_IMAGE_REVISION.tsv"
OWNER_OUT = OUT / "V71_R3_OWNER_LEDGER.tsv"
REVISION_OUT = OUT / "V71_R3_REVISIONS.tsv"
REPORT_OUT = OUT / "V71_R3_TECHNICAL_REPORT.md"

ALLOWED_PAGES = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"}
ALLOWED_STATUS = {"DIRECT_VISIBLE", "INHERITED_VISIBLE", "PAGE_OWNER_ONLY", "UNRESOLVED"}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], columns: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


PROSE_OWNER_DATA = {
    "H1_ROOT_AXIS_AND_RED_SWELLINGS": (
        "PICTURED_PART",
        "sichtbarer Wurzelachsen- und Speicherorganposten dieser Pflanze",
        "durchgehende braune Wurzelachse mit zwei geschlossenen roten Endkörpern",
        "ganze f10r-Pflanze statt eines gesonderten Wurzelpostens",
    ),
    "H2_UPPER_STEM_FLOWER_BUD_LEAF_SET": (
        "PICTURED_PART",
        "sichtbarer oberer Sprossposten derselben f10r-Pflanze",
        "Blüte, Knospe und Blattgruppen treffen sichtbar den oberen Stängel",
        "ganze f10r-Pflanze ohne Teiltrennung",
    ),
    "H3_WHOLE_DENSE_CROWN_PLANT": (
        "WHOLE_PLANT",
        "gesamte dichtkronige f11r-Pflanze des laufenden Artikels",
        "eine zusammenhängende Krone über mehreren Stielen und einem gekreuzten Wurzelkomplex",
        "ein einzelner Kronen-, Stiel- oder Wurzelteil",
    ),
    "H4_WHOLE_BROAD_LEAF_PLANT": (
        "WHOLE_PLANT",
        "gesamte breitblättrige f55v-Pflanze des laufenden Artikels",
        "Mittelstängel verbindet Wurzel, große Blattmasse und Endfächer",
        "oberer Endfächer oder unterer Wurzelast als gesonderter Posten",
    ),
    "H5_WHOLE_MULTIHEAD_COILED_PLANT": (
        "WHOLE_PLANT",
        "gesamte mehrköpfige f56r-Pflanze des laufenden Artikels",
        "Blüten, Stachelorgane und eingerollter Zweig hängen am selben sichtbaren Stängel",
        "Spiralzweig als selbständiger Besitzer",
    ),
    "B1_SHARED_TWO_ROW_POOL": (
        "SHARED_POOL",
        "gemeinsame zweireihige Figuren-/Beckenstation auf f81v",
        "ungefähr sechzehn Figuren liegen innerhalb einer gemeinsamen grünen Umgrenzung",
        "zwei unabhängige Reihen oder ein rein allegorisches Feld",
    ),
    "B2_UPPER_PAIRED_BASINS_AND_CYLINDER": (
        "LOCAL_APPARATUS",
        "obere f82r-Konfiguration aus zwei Figurengefäßen, Bögen und Mittelzylinder",
        "Bögen treffen den Zylinder; eine Hand hält ein Bogenende; der Text liegt im oberen Konfigurationsraum",
        "mehrere bloß benachbarte Einzelvignetten ohne gemeinsame Bedienung",
    ),
    "B2_MIDDLE_LEFT_DEVICE_AND_INLINE_NODE": (
        "LOCAL_APPARATUS",
        "mittlere linke Ring-/Fächerstation samt horizontalem Inline-Knoten",
        "Wellenlinien entspringen am Handgerät; der Doppelstrich läuft durch den Sternknoten",
        "ikonographischer Strahl und Stern auf einem Schmuckband",
    ),
    "B2_MIDDLE_RIGHT_AMBIGUOUS_STATION": (
        "UNRESOLVED_LOCAL_STATION",
        "örtliche mittlere f82r-Station, die nur das Exemplar zwischen Linie und Liegepodest entscheidet",
        "horizontale Linie liegt nahe über dem Liegepodest, berührt es aber nicht sicher",
        "Inline-Knotenstation oder unabhängiges Liegepodest",
    ),
    "B2_LOWER_GREEN_MULTI_FIGURE_POOL": (
        "SHARED_POOL",
        "unteres grünes Mehrfigurenfeld auf f82r",
        "zahlreiche Figuren schneiden dieselbe unregelmäßige grüne Fläche; zwei Vertikalformen reichen an den Rand",
        "mehrere getrennte allegorische Figurenplätze",
    ),
    "B2_LOWER_POOL_EDGE_STATIONS": (
        "FIGURE_STATION_SET",
        "lokale Figurenplätze am Rand des unteren f82r-Feldes",
        "kleine Gefäße und Figuren sind am gemeinsamen Feldrand wiederholt, aber nicht durch Leitungen gekoppelt",
        "das gesamte grüne Feld als ungeteilter Besitzer",
    ),
    "B3_UPPER_MARGIN_OPEN_FAN_STATION": (
        "FIGURE_STATION",
        "oberste f83r-Randstation mit offenem Punkt-/Fächerende",
        "oberste Randfigur steht unmittelbar unter offenem Ende und Fächermotiv",
        "rein ikonographischer Strahlenbesitzer",
    ),
    "B3_MIDDLE_MARGIN_ROUND_VESSEL_STATION": (
        "FIGURE_STATION",
        "mittlere f83r-Randfigur in rundem Gefäß",
        "zweite Randfigur ist sichtbar in einer eigenen rund eingefassten Station",
        "gesamter dreiteiliger Randstapel",
    ),
    "B3_LOWER_MARGIN_BASKET_VESSEL_STATION": (
        "FIGURE_STATION",
        "untere f83r-Randfigur im korbartigen Gefäß",
        "dritte Randfigur sitzt in eigener Schuppen-/Korbform mit freien unteren Strichen",
        "gesamter dreiteiliger Randstapel",
    ),
    "B3_MARGIN_TO_MAIN_GAP_UNRESOLVED": (
        "UNRESOLVED_LOCAL_STATION",
        "örtlicher f83r-Posten laut Exemplar; keine Bildvererbung über die Lücke",
        "zwischen Randstapel und unterer Paarstation besteht keine gezeichnete Kante",
        "untere Randstation oder obere Seite der Hauptpaarstation",
    ),
    "B3_MAIN_ARCH_LINKED_PAIR": (
        "LINKED_FIGURE_PAIR",
        "untere f83r-Paarstation mit gemeinsamem ungerichtetem Bogen",
        "breiter blau gefüllter Bogen verbindet die zwei Hauptfiguren tatsächlich",
        "Regenbogen-/Himmelsband ohne technische Kopplung",
    ),
    "B4_MAIN_ARCH_LINKED_PAIR": (
        "LINKED_FIGURE_PAIR",
        "untere f83r-Paarstation als gemeinsamer Besitzer dieses Records",
        "beide Endstationen teilen einen sichtbaren Bogen, aber keinen Pfeil",
        "zwei getrennte Figuren mit dekorativem Bogen",
    ),
    "B4_MAIN_LEFT_OPEN_FRINGE_STATION": (
        "LOCAL_APPARATUS",
        "linke Hauptstation mit blauem Unterlauf und offenen Fransen",
        "gefüllter Unterlauf setzt am linken Gefäß an und endet mehrfach offen",
        "ornamentaler Schweif statt Auslass",
    ),
    "B4_MAIN_RIGHT_S_RUN_MULTIPORT_STATION": (
        "LOCAL_APPARATUS",
        "rechte Hauptstation mit S-Lauf und blauem Mehrarmknoten",
        "S-Kontur läuft vom Figurenbecken sichtbar in den mehrarmigen Knoten",
        "Band-/Rosettenornament ohne technische Funktion",
    ),
    "B5_LEFT_OPEN_FRINGE_STATION": (
        "LOCAL_APPARATUS",
        "linker offener Endposten der f83r-Hauptstation",
        "blauer Lauf und mehrere freie Enden bilden eine lokal geschlossene Besitzerfigur",
        "gesamte Paarstation statt linker Endposten",
    ),
    "B6_RIGHT_S_RUN_MULTIPORT_STATION": (
        "LOCAL_APPARATUS",
        "rechter S-Lauf-/Mehrarmknotenposten der f83r-Hauptstation",
        "durchgehender S-Lauf tritt in blauen Knoten mit freien Armen ein",
        "gesamte Paarstation statt rechter Endposten",
    ),
}


def locus_number(locus: str) -> int:
    return int(locus.rsplit(".", 1)[1])


def prose_owner(field: dict[str, str]) -> tuple[str, str]:
    """Return owner ID and anchor mode: PAGE, DIRECT or UNRESOLVED."""
    record = field["record_unit_id"]
    n = locus_number(field["locus"])
    if record == "H1":
        return "H1_ROOT_AXIS_AND_RED_SWELLINGS", "PAGE"
    if record == "H2":
        return "H2_UPPER_STEM_FLOWER_BUD_LEAF_SET", "PAGE"
    if record == "H3":
        return "H3_WHOLE_DENSE_CROWN_PLANT", "PAGE"
    if record == "H4":
        return "H4_WHOLE_BROAD_LEAF_PLANT", "PAGE"
    if record == "H5":
        return "H5_WHOLE_MULTIHEAD_COILED_PLANT", "PAGE"
    if record == "B1":
        return "B1_SHARED_TWO_ROW_POOL", "PAGE"
    if record == "B2":
        if n <= 4:
            return "B2_UPPER_PAIRED_BASINS_AND_CYLINDER", "DIRECT"
        if n == 7:
            return "B2_MIDDLE_LEFT_DEVICE_AND_INLINE_NODE", "DIRECT"
        if n == 19:
            return "B2_MIDDLE_RIGHT_AMBIGUOUS_STATION", "UNRESOLVED"
        if n == 23:
            return "B2_LOWER_GREEN_MULTI_FIGURE_POOL", "DIRECT"
        return "B2_LOWER_POOL_EDGE_STATIONS", "DIRECT"
    if record == "B3":
        if n <= 3:
            return "B3_UPPER_MARGIN_OPEN_FAN_STATION", "DIRECT"
        if n <= 6:
            return "B3_MIDDLE_MARGIN_ROUND_VESSEL_STATION", "DIRECT"
        if n <= 11:
            return "B3_LOWER_MARGIN_BASKET_VESSEL_STATION", "DIRECT"
        if n <= 16:
            return "B3_MARGIN_TO_MAIN_GAP_UNRESOLVED", "UNRESOLVED"
        return "B3_MAIN_ARCH_LINKED_PAIR", "DIRECT"
    if record == "B4":
        if n <= 28:
            return "B4_MAIN_ARCH_LINKED_PAIR", "DIRECT"
        if n <= 39:
            return "B4_MAIN_LEFT_OPEN_FRINGE_STATION", "DIRECT"
        return "B4_MAIN_RIGHT_S_RUN_MULTIPORT_STATION", "DIRECT"
    if record == "B5":
        return "B5_LEFT_OPEN_FRINGE_STATION", "DIRECT"
    if record == "B6":
        return "B6_RIGHT_S_RUN_MULTIPORT_STATION", "DIRECT"
    raise ValueError(f"unmapped record {record}")


def prose_change(record: str) -> str:
    if record.startswith("H"):
        return "SPECIES_AND_PREPARATION_IMAGE_DEFAULT_REMOVED; VISIBLE_PLANT_OWNER_ONLY"
    if record == "B1":
        return "SEVEN_STAGE_CIRCULATION_REMOVED; SHARED_POOL_OWNER"
    if record == "B2":
        return "ONE_LINEAR_MACHINE_REMOVED; DISCONNECTED_LOCAL_STATION_OWNERS"
    return "GLOBAL_F83R_CYCLE_REMOVED; LOCAL_CONTACT_BOUNDED_OWNER"


def aggregate_astro(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    grouped: OrderedDict[tuple[str, str, str], list[dict[str, str]]] = OrderedDict()
    for row in rows:
        grouped.setdefault((row["diagram_id"], row["page"], row["locus"]), []).append(row)
    result = []
    for (diagram, page, locus), members in grouped.items():
        roles = []
        for member in members:
            if member["local_formal_role"] not in roles:
                roles.append(member["local_formal_role"])
        result.append({
            "diagram_id": diagram,
            "page": page,
            "locus": locus,
            "group_count": len(members),
            "member_group_serials": "|".join(member["group_serial"] for member in members),
            "v69_roles": "|".join(roles),
        })
    return result


def astro_owner(row: dict[str, object]) -> tuple[str, str, str, str, str, str, str, str]:
    """Return namespace, owner class/id, status, default, basis, rival, confidence."""
    page = str(row["page"])
    n = locus_number(str(row["locus"]))
    if page == "f67r2":
        if 1 <= n <= 12:
            return (
                "A1_RIGHT_WHEEL", "DIAGRAM_SECTOR", f"A1_RIGHT_SECTOR_SLOT_{n:02d}", "DIRECT_VISIBLE",
                f"dieser lokale Sektorplatz {n:02d} des rechten f67r2-Rades",
                "zwölfteilige lokale Sektor-/Scheibenordnung im rechten Rad; keine Kante zum linken Rad",
                "bloße farbige Himmelsposition ohne Auswahlfunktion", "MEDIUM",
            )
        if 13 <= n <= 14:
            return (
                "A1_RIGHT_WHEEL", "RING_TEXT_BAND", f"A1_RIGHT_RING_BAND_{n-12:02d}", "INHERITED_VISIBLE",
                "gegenwärtiges Ringband des rechten f67r2-Rades",
                "Schrift folgt einem vorgezeichneten Ringraum des rechten Rades",
                "allgemeine Seitenlegende", "MEDIUM",
            )
        if 15 <= n <= 51:
            return (
                "A1_LEFT_WHEEL", "LOCAL_WHEEL_FIELD", f"A1_LEFT_LOCAL_FIELD_{n:02d}", "INHERITED_VISIBLE",
                f"gegenwärtiges lokales Radial-/Ringfeld {n:02d} des linken f67r2-Rades",
                "V70 trennt das strahlen-/sterngefüllte linke Rad als eigenen Bildbesitzer; die alte Zeilenrolle liefert keine Semantik",
                "lokaler Text des rechten Rades oder seitenweite Legende", "LOW",
            )
        if 52 <= n <= 63:
            return (
                "A1_LEFT_WHEEL", "STAR_STATION", f"A1_LEFT_OUTER_STAR_STATION_{n-51:02d}", "DIRECT_VISIBLE",
                f"äußerer Sternplatz {n-51:02d} des linken f67r2-Rades",
                "wiederholte sichtbare Sternplätze liegen in der äußeren Zone des linken Rades",
                "dekorativer Stern ohne technische Adresse", "MEDIUM",
            )
        if 64 <= n <= 71:
            return (
                "A1_RIGHT_WHEEL", "PHASE_OR_CONDITION_STATION", f"A1_RIGHT_PHASE_STATION_{n-63:02d}", "DIRECT_VISIBLE",
                f"lokaler Scheiben-/Bedingungsplatz {n-63:02d} des rechten f67r2-Rades",
                "farbige kleine Scheiben liegen in getrennten Feldern des rechten Rades",
                "rein ikonographische Himmelskörperscheibe", "MEDIUM",
            )
        if n == 72:
            return (
                "A1_LEFT_WHEEL", "RING_TEXT_BAND", "A1_LEFT_OUTER_RING_TEXT", "DIRECT_VISIBLE",
                "äußeres Textband des linken f67r2-Rades",
                "konzentrische Schrift umschließt nur das linke Kreisbild",
                "allgemeine Seitenprosa", "MEDIUM",
            )
        if n == 73:
            return (
                "A1_RIGHT_WHEEL", "RING_TEXT_BAND", "A1_RIGHT_OUTER_RING_TEXT", "DIRECT_VISIBLE",
                "äußeres Textband des rechten f67r2-Rades",
                "konzentrische Schrift umschließt nur das rechte Kreisbild",
                "allgemeine Seitenprosa", "MEDIUM",
            )
        return (
            "A1_PAGE", "UNRESOLVED_PAGE_LEGEND", "A1_PAIRED_WHEEL_LEGEND_UNRESOLVED", "UNRESOLVED",
            "seitenlokale Legende; das Exemplar entscheidet linkes oder rechtes Rad",
            "der verbleibende Textblock ist keinem der zwei Räder durch eine Kante zugewiesen",
            "linke oder rechte Radlegende", "LOW",
        )
    if page == "f68r1":
        if n == 1:
            owner = "A2_LEFT_PANEL_HEADER"
            namespace = "A2_LEFT_STAR_FIELD"
            basis = "oberer Textblock steht im linken freien Sternfeldpaneel"
        elif n == 2:
            owner = "A2_MIDDLE_PANEL_HEADER"
            namespace = "A2_MIDDLE_STAR_FIELD"
            basis = "oberer Textblock steht im mittleren freien Sternfeldpaneel"
        elif n == 3:
            owner = "A2_RIGHT_PANEL_HEADER"
            namespace = "A2_RIGHT_SECTORIZED_MAP"
            basis = "Text folgt dem rechten sektorgegliederten Kreisfeld"
        else:
            owner = f"A2_MULTIPANEL_HEADER_FRAGMENT_{n:02d}"
            namespace = "A2_MULTIPANEL_PAGE"
            basis = "Headerfragment gehört zum manifestierten Mehrpaneelfeld, besitzt aber keine sichtbare Objektkante"
        if 1 <= n <= 7:
            status = "PAGE_OWNER_ONLY" if n <= 3 else "UNRESOLVED"
            return (
                namespace, "PANEL_HEADER", owner, status,
                "lokale Kopf-/Legendenangabe des zugeordneten f68r1-Paneels" if n <= 3 else "mehrpaneelige Seitenlegende laut Exemplar",
                basis, "Legende eines benachbarten Paneels", "MEDIUM" if n <= 3 else "LOW",
            )
        if n == 8:
            return (
                "A2_MULTIPANEL_PAGE", "FACE_MEDALLION_SET", "A2_CENTRE_KEY_UNRESOLVED", "UNRESOLVED",
                "eines der sichtbaren Gesichtmedaillons; genaue Wahl nur aus dem Exemplar",
                "das Querfeld besitzt mindestens fünf Zentren statt eines eindeutigen Gesamtzentrums",
                "jedes der anderen Gesichtmedaillons", "LOW",
            )
        if 9 <= n <= 36:
            slot = n - 8
            return (
                "A2_LOCAL_STAR_CATALOGUE", "STAR_STATION", f"A2_STAR_STATION_{slot:02d}", "DIRECT_VISIBLE",
                f"sichtbarer lokal beschrifteter Sternplatz {slot:02d} im f68r1-Atlas",
                "das lokale Label sitzt bei einem einzelnen Stern; zwischen Sternen gibt es keine Kante",
                "bloße dekorative Sternposition ohne gemeinsame Semantik", "HIGH",
            )
        return (
            "A2_MULTIPANEL_PAGE", "FACE_MEDALLION_OR_CENTRAL_LEGEND", "A2_CENTRAL_LEGEND_UNRESOLVED", "UNRESOLVED",
            "lokale Zentrallegende eines f68r1-Teilbildes laut Exemplar",
            "mehrere Gesichtzentren verhindern die alte seitenweite Zentralvererbung",
            "Legende eines anderen Teilzentrums", "LOW",
        )
    if page == "f69v":
        if 1 <= n <= 3:
            names = {1: ("LEFT", "linken 28-Platz-Rades"), 2: ("MIDDLE", "mittleren Wolken-/Wellenrades"), 3: ("RIGHT", "rechten Gesicht-Strahlenrades")}
            code, label = names[n]
            return (
                f"A3_{code}_WHEEL", "RING_TEXT_BAND", f"A3_{code}_WHEEL_RING_TEXT", "DIRECT_VISIBLE",
                f"Ringtext des {label}",
                "jedes Textband umschließt nur sein eigenes Kreisbild; zwischen Rädern fehlt jede Kante",
                "allgemeine Seitenlegende", "HIGH",
            )
        slot = n - 3
        return (
            "A3_LEFT_WHEEL", "RADIAL_SLOT", f"A3_LEFT_RADIAL_SLOT_{slot:02d}", "DIRECT_VISIBLE",
            f"lokaler Radialplatz {slot:02d} des linken f69v-Rades; Nummer nur editoriale Adresse",
            "ungefähr 28 sichtbare Stäbe teilen die linke Mitte; kein Start und keine Richtung",
            "dekorativer Strahl ohne Regel- oder Terminwert", "HIGH",
        )
    raise ValueError(f"unmapped astro page {page}")


def astro_change(page: str) -> str:
    return {
        "f67r2": "LITERAL_7X12_PAGE_MATRIX_REMOVED; TWO_PAGE_LOCAL_WHEEL_NAMESPACES",
        "f68r1": "SINGLE_CENTRE_PLUS_28_PAGE_OBJECT_REMOVED; MULTIPANEL_LOCAL_OWNERS",
        "f69v": "ORDERED_28_RULE_SEQUENCE_REMOVED; THREE_WHEELS_WITH_LOCAL_LEFT_28_SLOTS",
    }[page]


def build_rows() -> list[dict[str, object]]:
    fields = read_tsv(FIELD_SOURCE)
    astro_groups = read_tsv(ASTRO_SOURCE)
    v70 = read_tsv(V70_SELECTED)
    assert len(fields) == 135
    assert len(astro_groups) == 395
    assert len(v70) == 10
    assert {r["page"] for r in v70} == ALLOWED_PAGES

    output: list[dict[str, object]] = []
    seen_anchor: set[tuple[str, str]] = set()
    for serial, field in enumerate(fields, 1):
        owner_id, mode = prose_owner(field)
        owner_class, default, basis, rival = PROSE_OWNER_DATA[owner_id]
        anchor_key = (field["record_unit_id"], owner_id)
        if mode == "UNRESOLVED":
            status = "UNRESOLVED"
        elif anchor_key in seen_anchor:
            status = "INHERITED_VISIBLE"
        else:
            status = "DIRECT_VISIBLE" if mode == "DIRECT" else "PAGE_OWNER_ONLY"
            seen_anchor.add(anchor_key)
        confidence = "LOW" if status == "UNRESOLVED" else ("HIGH" if owner_class in {"WHOLE_PLANT", "SHARED_POOL"} else "MEDIUM")
        output.append({
            "owner_row_id": f"P{serial:03d}",
            "source_level": "PROSE_FIELD",
            "source_id": field["field_id"],
            "page": field["page"],
            "section": "HERBAL" if field["record_unit_id"].startswith("H") else "BIOLOGICAL",
            "record_or_diagram": field["record_unit_id"],
            "locus": field["locus"],
            "member_count": field["event_count"],
            "member_ids": field["event_serials"],
            "v69_formal_role": f"{field['primary_template']}|{field['licensed_primitive_sequence']}",
            "image_namespace": field["record_unit_id"],
            "owner_class": owner_class,
            "owner_id": owner_id,
            "ownership_status": status,
            "technical_silent_argument_default": default,
            "visible_geometric_basis": basis,
            "strongest_rival": rival,
            "confidence": confidence,
            "v69_change": prose_change(field["record_unit_id"]),
            "direction_policy": "NO_DIRECTION_FROM_IMAGE",
            "semantic_ceiling": "VISIBLE_OWNER_NOT_WORD_CARD_STEM_OR_MEANING",
        })

    for serial, locus in enumerate(aggregate_astro(astro_groups), 1):
        namespace, owner_class, owner_id, status, default, basis, rival, confidence = astro_owner(locus)
        output.append({
            "owner_row_id": f"A{serial:03d}",
            "source_level": "ASTRO_LOCUS",
            "source_id": locus["locus"],
            "page": locus["page"],
            "section": "ASTRO",
            "record_or_diagram": locus["diagram_id"],
            "locus": locus["locus"],
            "member_count": locus["group_count"],
            "member_ids": locus["member_group_serials"],
            "v69_formal_role": locus["v69_roles"],
            "image_namespace": namespace,
            "owner_class": owner_class,
            "owner_id": owner_id,
            "ownership_status": status,
            "technical_silent_argument_default": default,
            "visible_geometric_basis": basis,
            "strongest_rival": rival,
            "confidence": confidence,
            "v69_change": astro_change(str(locus["page"])),
            "direction_policy": "NO_START_ROTATION_OR_CROSS_WHEEL_JOIN_FROM_IMAGE",
            "semantic_ceiling": "VISIBLE_OWNER_NOT_WORD_CARD_STEM_OR_MEANING",
        })
    return output


REVISIONS = [
    ("R001", "ALL_PROSE", "ein OWNER konnte implizit über die ganze Seite fortlaufen", "OWNER wird am Recordbeginn gesetzt und am Recordende gelöscht", "kein H1→H2- oder B3→B4-Übertrag", "sichtbare Seitenbesitzer plus V69-Recordgrenzen", "HIGH"),
    ("R002", "HERBAL", "Pflanzenname und Zubereitung konnten als Bildargument erscheinen", "nur ganze Pflanze oder sichtbarer Teil wird still getragen", "Art, Wasser und Verfahren bleiben Exemplarwerte", "vier Bilder ohne Gefäß oder Flüssigkeit", "HIGH"),
    ("R003", "f10r", "beide Artikel konnten denselben ungeteilten Besitzer nutzen", "H1 erhält Wurzelachsenposten; H2 oberen Sprossposten; beide resetten", "keine inhaltliche Teilbedeutung einer Karte", "sichtbar unterscheidbare Wurzel- und Oberteile", "MEDIUM"),
    ("R004", "f81v", "gerichteter siebenstufiger Grundkreislauf", "ein gemeinsames zweireihiges Figuren-/Beckenfeld", "alle B1-Felder erben nur das gemeinsame Feld", "eine Umgrenzung; keine Pfeile", "HIGH"),
    ("R005", "f82r_TOP", "eine lineare Einzelmaschine", "oberer Figuren-/Zylinderraum und mittlere Ring-/Knotenstation sind getrennte Owner", "Owner-Reset am visuellen Stationswechsel", "lokale Kontakte, aber keine durchgehende Seitekante", "HIGH"),
    ("R006", "f82r_MIDDLE", "Linie und Liegepodest wurden als angeschlossen behandelt", "locus 19 bleibt UNRESOLVED", "keine Vererbung über den sichtbaren Spalt", "V70 R3 E022 PROXIMITY_ONLY", "HIGH"),
    ("R007", "f82r_BOTTOM", "unteres Feld war Endstation derselben Maschine", "unteres Mehrfigurenfeld und Randstationen bilden neue lokale Owner", "kein Ober→Unter-Fluss", "V70 R3 E026 NO_CONTINUOUS_EDGE", "HIGH"),
    ("R008", "f83r_B3", "langer Irrigationszyklus", "drei Randstationen, eine ungelöste Lücke und die Hauptpaarstation", "B3 darf Richtung oder Zyklus nicht erben", "Randstationen ohne Kante; Hauptpaar mit ungerichtetem Bogen", "HIGH"),
    ("R009", "f83r_B4_B6", "ein gemeinsamer Rücklauf", "B4 Paar/Endstationen, B5 linker offener Lauf und B6 rechter Knoten sind lokal getrennt", "Recordreset bleibt trotz gemeinsamer Seite", "zwei verschiedene Unterläufe und offene Enden", "HIGH"),
    ("R010", "f67r2", "sichtbar wörtliche 7×12-Seitenmatrix", "linkes und rechtes Rad erhalten getrennte Namensräume", "kein Locus verbindet beide ohne sichtbare Legende", "zwei heterogene, unverbundene Kreisfelder", "HIGH"),
    ("R011", "f68r1", "ein seitenweites Zentrum plus 28", "28 lokale Sternstationen bleiben, ein Gesamtzentrum nicht", "Zentralfelder bleiben UNRESOLVED", "mindestens fünf Gesichtmedaillons und drei Paneele", "HIGH"),
    ("R012", "f69v", "eine geordnete 28-Regelfolge", "drei Radnamensräume; 28 lokale Slots nur links", "Editorennummer ist keine Drehrichtung", "drei Kreise ohne Kante, Start oder Zeiger", "HIGH"),
    ("R013", "ALL_ASTRO", "gleiche Locusnummer konnte radübergreifend wirken", "Namespace ist page- und wheel-lokal", "keine f68↔f69- oder f69-internen Joins", "V70 Kontaktcensus", "HIGH"),
    ("R014", "SEMANTIC_CEILING", "Owner konnte wie ein Textwert klingen", "Owner ist nur stilles sichtbares Argument", "keine Wort-, Karten-, Stamm- oder Operatorbedeutung", "Bildkontakt bestimmt nur Geometrie", "HIGH"),
]


def write_revisions() -> None:
    cols = ["revision_id", "scope", "v69_default", "v71_r3_revision", "executable_effect", "visible_basis", "confidence"]
    rows = [dict(zip(cols, row)) for row in REVISIONS]
    write_tsv(REVISION_OUT, rows, cols)


def make_report(rows: list[dict[str, object]]) -> str:
    status_counts = Counter(str(r["ownership_status"]) for r in rows)
    section_counts = Counter(str(r["section"]) for r in rows)
    prose = [r for r in rows if r["source_level"] == "PROSE_FIELD"]
    astro = [r for r in rows if r["source_level"] == "ASTRO_LOCUS"]
    lines = [
        "# V71 R3 — ausführbarer Bildbesitzer-Compiler",
        "",
        "Status: kreative technische Rekonstruktion, keine Entzifferung oder Übersetzung.",
        "Alle Besitzer sind sichtbare Argumentträger; sie sind keine Wörter, Kartenwerte,",
        "Stämme, Referenten oder Bedeutungen.",
        "",
        "## Ergebnis",
        "",
        f"Der Ledger bindet **{len(prose)} Prosa-Felder** und **{len(astro)} Astro-Loci**",
        f"in insgesamt **{len(rows)}** Zeilen. Die 135 Felder decken 381 Ereignisse,",
        "die 142 Astro-Loci 395 Gruppen. Jede Bindung bleibt record- oder radlokal.",
        "",
        "Statuszählung:",
        "",
        "| Status | Zeilen |",
        "|---|---:|",
    ]
    for status in ("DIRECT_VISIBLE", "INHERITED_VISIBLE", "PAGE_OWNER_ONLY", "UNRESOLVED"):
        lines.append(f"| `{status}` | {status_counts[status]} |")
    lines += [
        "",
        "## Ausführbare OWNER-Registerregeln",
        "",
        "1. `RESET_RECORD`: Am Beginn jedes H-/B-Records wird OWNER gelöscht; am Ende darf nichts in den nächsten Record gelangen.",
        "2. `ANCHOR_DIRECT`: Berührt/umschließt ein Bildobjekt den lokalen Schreibraum eindeutig, setze OWNER auf dieses kleinste Objekt.",
        "3. `ANCHOR_PAGE`: Gibt es nur eine dominante Seitenfigur, darf der erste Recordposten sie als `PAGE_OWNER_ONLY` setzen.",
        "4. `INHERIT_LOCAL`: Folgende Felder dürfen denselben OWNER nur im selben Record und ohne sichtbare Trennkante erben.",
        "5. `BREAK_AT_GAP`: Eine sichtbare Unterbrechung oder ein neues Gefäß löscht OWNER; bloße Nähe ist keine Verbindung.",
        "6. `ASTRO_NAMESPACE`: Jeder Kreis, jedes Paneel und jede Sternstation hat einen eigenen lokalen Namensraum.",
        "7. `NO_DIRECTION`: Bogen, Ring und Rad geben ohne Pfeil weder Fluss, Start noch Rotation vor.",
        "8. `UNRESOLVED`: Sind mehrere kleinste Besitzer möglich, wird nicht seitenweit vererbt; das Masterexemplar muss wählen.",
        "9. `NO_SEMANTIC_LIFT`: Ein sichtbarer Besitzer ergänzt nur 'dieses Bildobjekt'; er benennt kein Material, Heilmittel, Gestirn oder Verfahren.",
        "",
        "## Wichtigste Revisionen",
        "",
        "- Herbal trägt sichtbare Pflanzenbesitzer, nicht bildsichtbare Arten oder Zubereitungen.",
        "- f81v trägt ein gemeinsames Feld, aber keinen siebenstufigen Kreislauf.",
        "- f82r wird bei jedem Stationswechsel zurückgesetzt; die Linie über dem Liegepodest bleibt ausdrücklich ungelöst.",
        "- f83r bindet nur die wirklich gekoppelte Paarstation; B5 und B6 erhalten getrennte offene Endbesitzer.",
        "- f67r2, f68r1 und f69v besitzen wheel-/panel-lokale Namensräume; die 28 f69v-Slots gelten ausschließlich links und ungeordnet.",
        "",
        "## Vollständige Herbal-Spur (20/20)",
        "",
        "| Feld | Record | Locus | Status | OWNER | stilles technisches Argument |",
        "|---|---|---|---|---|---|",
    ]
    for row in prose:
        if row["section"] != "HERBAL":
            continue
        lines.append(f"| {row['source_id']} | {row['record_or_diagram']} | {row['locus']} | {row['ownership_status']} | `{row['owner_id']}` | {row['technical_silent_argument_default']} |")
    lines += [
        "",
        "## Vollständige Biological-Spur (115/115)",
        "",
        "| Feld | Record | Locus | Status | OWNER | stilles technisches Argument |",
        "|---|---|---|---|---|---|",
    ]
    for row in prose:
        if row["section"] != "BIOLOGICAL":
            continue
        lines.append(f"| {row['source_id']} | {row['record_or_diagram']} | {row['locus']} | {row['ownership_status']} | `{row['owner_id']}` | {row['technical_silent_argument_default']} |")
    lines += [
        "",
        "## Vollständige Astro-Spur (142/142)",
        "",
        "| Locus | Diagramm | Gruppen | Namespace | Status | OWNER | stilles technisches Argument |",
        "|---|---|---:|---|---|---|---|",
    ]
    for row in astro:
        lines.append(f"| {row['source_id']} | {row['record_or_diagram']} | {row['member_count']} | `{row['image_namespace']}` | {row['ownership_status']} | `{row['owner_id']}` | {row['technical_silent_argument_default']} |")
    lines += [
        "",
        "## Vollständige Beispielausführung vorwärts/rückwärts",
        "",
        "### Herbal H1→H2",
        "",
        "`RESET H1 → PAGE_OWNER(root axis) → F001 → inherit F002 → RESET → PAGE_OWNER(upper shoot) → F003 → inherit F004–F005 → RESET`.",
        "Rückwärts darf F003 nie den H1-Wurzelposten liefern; das H2-Record setzt einen neuen sichtbaren Teilbesitzer.",
        "",
        "### Biological f82r",
        "",
        "`upper station(F045–F052) → BREAK → middle-left(F053–F056) → BREAK → UNRESOLVED gap(F057–F058) → BREAK → lower pool(F059–F061) → BREAK → edge stations(F062–F070)`.",
        "Kein Rückwärtslauf darf F057/F058 über die sichtbare Lücke mit dem Podest oder dem Inline-Knoten gleichsetzen.",
        "",
        "### Astro f69v",
        "",
        "`LEFT_RING(f69v.1) | MIDDLE_RING(f69v.2) | RIGHT_RING(f69v.3) | LEFT_SLOT_01..28(f69v.4..31)`.",
        "Die senkrechten Striche bedeuten parallele lokale Namensräume. Weder Vorwärts- noch Rückwärtslesen erzeugt Start, Rotation oder einen Join.",
        "",
        "## Grenze",
        "",
        "Das Resultat etabliert höchstens eine ausführbare Bildellipsis: Ein Schreiber kann",
        "ein sichtbares Objekt auslassen, wenn Record und Bildraum den Besitzer erhalten.",
        "Es bestätigt kein Voynich-Wort und keine konkrete Quellenoperation. f84 und f84r",
        "blieben versiegelt; keine andere Seite wurde verwendet.",
    ]
    assert section_counts == {"HERBAL": 20, "BIOLOGICAL": 115, "ASTRO": 142}
    return "\n".join(lines) + "\n"


def main() -> None:
    rows = build_rows()
    columns = [
        "owner_row_id", "source_level", "source_id", "page", "section",
        "record_or_diagram", "locus", "member_count", "member_ids",
        "v69_formal_role", "image_namespace", "owner_class", "owner_id",
        "ownership_status", "technical_silent_argument_default",
        "visible_geometric_basis", "strongest_rival", "confidence",
        "v69_change", "direction_policy", "semantic_ceiling",
    ]
    assert len(rows) == 277
    assert all(str(row["ownership_status"]) in ALLOWED_STATUS for row in rows)
    assert {str(row["page"]) for row in rows} == ALLOWED_PAGES
    write_tsv(OWNER_OUT, rows, columns)
    write_revisions()
    REPORT_OUT.write_text(make_report(rows), encoding="utf-8")
    summary = {
        "status": "BUILT",
        "owner_rows": len(rows),
        "prose_fields": sum(row["source_level"] == "PROSE_FIELD" for row in rows),
        "astro_loci": sum(row["source_level"] == "ASTRO_LOCUS" for row in rows),
        "status_counts": dict(sorted(Counter(str(row["ownership_status"]) for row in rows).items())),
        "section_counts": dict(sorted(Counter(str(row["section"]) for row in rows).items())),
        "prose_member_events": sum(int(row["member_count"]) for row in rows if row["source_level"] == "PROSE_FIELD"),
        "astro_member_groups": sum(int(row["member_count"]) for row in rows if row["source_level"] == "ASTRO_LOCUS"),
        "semantic_ceiling": "VISIBLE_OWNER_NOT_WORD_CARD_STEM_OR_MEANING",
        "sealed": ["f84", "f84r"],
    }
    (OUT / "V71_R3_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

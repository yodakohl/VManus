#!/usr/bin/env python3
"""Build V75 R1: complete local celestial multi-instrument third edition."""

from __future__ import annotations

import csv
import json
from collections import Counter, OrderedDict, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
V69 = ROOT / "experiments/yolo/sidequest_theory_candidates_v69"
V71 = ROOT / "experiments/yolo/sidequest_theory_candidates_v71"

GROUP_SOURCE = V69 / "V69_R4_FINAL_395_ASTRO_GROUPS.tsv"
OWNER_SOURCE = V71 / "V71_SELECTED_OWNER_LEDGER.tsv"

GROUP_OUT = OUT / "V75_R1_395_GROUP_CELESTIAL_INTERLINEAR.tsv"
LOCUS_OUT = OUT / "V75_R1_142_LOCUS_CELESTIAL_EDITION.tsv"
READING_OUT = OUT / "V75_R1_THREE_COMPLETE_INSTRUMENT_READINGS.md"
ORIENTATION_OUT = OUT / "V75_R1_ORIENTATION_AUDIT.tsv"
BUILD_OUT = OUT / "V75_R1_BUILD_SUMMARY.json"

PAGES = ("f67r2", "f68r1", "f69v")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=fields, delimiter="\t", lineterminator="\n",
            extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def owner_namespace(owner: str) -> str:
    if owner.startswith("A1_RIGHT_"):
        return "A67_RIGHT_CELESTIAL_WHEEL"
    if owner.startswith("A1_LEFT_"):
        return "A67_LEFT_CELESTIAL_WHEEL"
    if owner == "A1_PAIRED_WHEEL_LEGEND_UNRESOLVED":
        return "A67_PAIRED_WHEEL_PAGE_LEGEND_UNRESOLVED"
    if owner == "A2_LEFT_PANEL_HEADER":
        return "A68_LEFT_STAR_PANEL"
    if owner == "A2_MIDDLE_PANEL_HEADER":
        return "A68_MIDDLE_STAR_PANEL"
    if owner == "A2_RIGHT_PANEL_HEADER":
        return "A68_RIGHT_STAR_PANEL"
    if owner.startswith("A2_"):
        return "A68_MULTIPANEL_STAR_ATLAS"
    if owner.startswith("A3_LEFT_"):
        return "A69_LEFT_28_PLACE_WHEEL"
    if owner.startswith("A3_MIDDLE_"):
        return "A69_MIDDLE_CLOUD_WAVE_WHEEL"
    if owner.startswith("A3_RIGHT_"):
        return "A69_RIGHT_FACE_RAY_WHEEL"
    raise ValueError(f"unhandled owner: {owner}")


def owner_kind(owner: str) -> str:
    if "SECTOR_SLOT" in owner:
        return "RIGHT_WHEEL_SECTOR_LABEL"
    if "RING_BAND" in owner:
        return "RIGHT_WHEEL_RING_BAND"
    if "LOCAL_FIELD" in owner:
        return "LEFT_WHEEL_LOCAL_FIELD_LABEL"
    if "OUTER_STAR_STATION" in owner:
        return "LEFT_WHEEL_OUTER_STAR_LABEL"
    if "PHASE_STATION" in owner:
        return "RIGHT_WHEEL_DISC_CONDITION_LABEL"
    if owner == "A1_LEFT_OUTER_RING_TEXT":
        return "LEFT_WHEEL_RING_LEGEND"
    if owner == "A1_RIGHT_OUTER_RING_TEXT":
        return "RIGHT_WHEEL_RING_LEGEND"
    if owner == "A1_PAIRED_WHEEL_LEGEND_UNRESOLVED":
        return "PAIRED_WHEEL_LEGEND_UNRESOLVED"
    if "PANEL_HEADER" in owner:
        return "STAR_PANEL_HEADER"
    if "HEADER_FRAGMENT" in owner:
        return "MULTIPANEL_HEADER_FRAGMENT"
    if "CENTRE_KEY" in owner:
        return "FACE_CENTRE_KEY_UNRESOLVED"
    if "STAR_STATION" in owner:
        return "MULTIPANEL_STAR_LABEL"
    if "CENTRAL_LEGEND" in owner:
        return "SUBPANEL_CENTRAL_LEGEND_UNRESOLVED"
    if owner == "A3_LEFT_WHEEL_RING_TEXT":
        return "LEFT_WHEEL_RING_LEGEND"
    if owner == "A3_MIDDLE_WHEEL_RING_TEXT":
        return "MIDDLE_WHEEL_RING_LEGEND"
    if owner == "A3_RIGHT_WHEEL_RING_TEXT":
        return "RIGHT_WHEEL_RING_LEGEND"
    if "LEFT_RADIAL_SLOT" in owner:
        return "LEFT_WHEEL_UNORDERED_RADIAL_SLOT_LABEL"
    raise ValueError(f"unhandled owner kind: {owner}")


def use_rule(kind: str) -> str:
    rules = {
        "RIGHT_WHEEL_SECTOR_LABEL":
            "Zeige den Sektor im rechten Rad, kopiere sein örtliches Etikett und schlage nur den rechtsradlokalen Exemplareintrag nach.",
        "RIGHT_WHEEL_RING_BAND":
            "Kopiere dieses Ringband als eigene rechtsradlokale Legende; verknüpfe es nicht mit dem linken Rad.",
        "LEFT_WHEEL_LOCAL_FIELD_LABEL":
            "Zeige das Feld im linken Rad, kopiere sein örtliches Etikett und schlage nur den linksradlokalen Exemplareintrag nach.",
        "LEFT_WHEEL_OUTER_STAR_LABEL":
            "Setze das Etikett an den sichtbaren äußeren Sternplatz des linken Rades und lies es nur über diesen Bildort zurück.",
        "RIGHT_WHEEL_DISC_CONDITION_LABEL":
            "Setze das Etikett an den sichtbaren Scheiben-/Bedingungsplatz des rechten Rades; seine Funktion liefert nur das lokale Exemplar.",
        "LEFT_WHEEL_RING_LEGEND":
            "Kopiere diese Legende vollständig in das Ringband des linken Rades und lies sie nur in diesem Rad zurück.",
        "RIGHT_WHEEL_RING_LEGEND":
            "Kopiere diese Legende vollständig in das Ringband des rechten Rades und lies sie nur in diesem Rad zurück.",
        "PAIRED_WHEEL_LEGEND_UNRESOLVED":
            "Kopiere die seitenlokale Legende exakt; das Masterexemplar entscheidet, welchem der zwei Räder sie dient.",
        "STAR_PANEL_HEADER":
            "Kopiere diese vollständige Kopfzeile in das sichtbare lokale Sternpaneel; übertrage sie auf kein anderes Paneel.",
        "MULTIPANEL_HEADER_FRAGMENT":
            "Kopiere dieses Legendenstück an seiner sichtbaren Seitenposition; seine Paneelzuweisung bleibt exemplarabhängig.",
        "FACE_CENTRE_KEY_UNRESOLVED":
            "Kopiere den Zentralschlüssel beim sichtbaren Gesichtsmedaillon; welches der mehreren Zentren gemeint ist, entscheidet das Exemplar.",
        "MULTIPANEL_STAR_LABEL":
            "Setze das vollständige Etikett an genau diesen sichtbaren Sternplatz und schlage seinen Eintrag in dessen lokalem Paneel nach.",
        "SUBPANEL_CENTRAL_LEGEND_UNRESOLVED":
            "Kopiere die Zentrallegende in das gezeigte Teilbild; keine ganze Seite erbt automatisch ihren Wert.",
        "MIDDLE_WHEEL_RING_LEGEND":
            "Kopiere diese Legende vollständig in das mittlere Wolken-/Wellenrad und lies sie nur dort zurück.",
        "LEFT_WHEEL_UNORDERED_RADIAL_SLOT_LABEL":
            "Setze das Etikett an genau diesen radialen Platz des linken Rades und schlage ihn nach Bildlage nach; die Nummer ist nur editoriale Adresse.",
    }
    return rules[kind]


def historical_rival(owner: str) -> str:
    ns = owner_namespace(owner)
    if ns == "A67_RIGHT_CELESTIAL_WHEEL":
        return "zodiakal-, kalender- oder iatromathematisch gegliedertes Sektor-/Scheibenrad"
    if ns == "A67_LEFT_CELESTIAL_WHEEL":
        return "eigenständiges Stern-, Kalender- oder Prognostikrad mit äußeren Sternplätzen"
    if ns == "A67_PAIRED_WHEEL_PAGE_LEGEND_UNRESOLVED":
        return "gemeinsame Rubrik zweier astronomischer Konkordanzräder"
    if ns.startswith("A68_"):
        return "mehrpaneeliger Sternatlas, Konstellationskatalog oder Mondstations-Merktafel"
    if ns == "A69_LEFT_28_PLACE_WHEEL":
        return "örtliches 28-Platz-Inventar für Mondstationen, Wahlen oder Kalendergebrauch ohne bekannte Reihenfolge"
    if ns == "A69_MIDDLE_CLOUD_WAVE_WHEEL":
        return "eigenständiges Himmels-, Wetter- oder Zustandsrad"
    if ns == "A69_RIGHT_FACE_RAY_WHEEL":
        return "eigenständiges Sonnen-, Planeten- oder Prognostikrad"
    raise ValueError(ns)


def technical_rival(owner: str) -> str:
    ns = owner_namespace(owner)
    if ns.startswith("A67_"):
        return "zwei unabhängige formale Merk- und Lookup-Räder; Etiketten sind nur Bildadressen"
    if ns.startswith("A68_"):
        return "dekorative Stern-/Gesichtspaneele oder ein formaler Kopieratlas ohne bestimmbaren Kataloginhalt"
    if ns == "A69_LEFT_28_PLACE_WHEEL":
        return "ungeordnetes 28-Platz-Arbeitsregister oder bloße Radialbeschriftung"
    return "eigenständige formale Ringrubrik oder Kopiervorlage ohne nachweisbare Bedienfunktion"


def contradiction(owner: str) -> str:
    ns = owner_namespace(owner)
    if ns == "A67_RIGHT_CELESTIAL_WHEEL":
        return "Kein Etikett ist identifiziert; das zweite Rad ist unverbunden, und eine seitenweite 7×12-Komposition ist nicht sichtbar."
    if ns == "A67_LEFT_CELESTIAL_WHEEL":
        return "Lokale Felder und Sterne sind sichtbar, doch weder ihr Himmelswert noch ein Schlüssel zum rechten Rad ist gegeben."
    if ns == "A67_PAIRED_WHEEL_PAGE_LEGEND_UNRESOLVED":
        return "Die sichtbare Nähe entscheidet nicht, ob die Legende links, rechts oder der ganzen Seite gehört."
    if ns.startswith("A68_"):
        return "Mehrere Paneele und mindestens fünf Zentren widersprechen einem einzigen ganzen Zentrum-plus-28-Kreis; kein Sternname ist identifiziert."
    if ns == "A69_LEFT_28_PLACE_WHEEL":
        return "Nur ungefähr 28 lokale Plätze sind sichtbar; Start, Richtung, Rotation, Reihenfolge und Wert bleiben unbelegt."
    if ns == "A69_MIDDLE_CLOUD_WAVE_WHEEL":
        return "Das mittlere Rad besitzt keinen sichtbaren Schlüssel zum linken 28-Platz-Rad und keine sicher abgetrennten 28 Einträge."
    if ns == "A69_RIGHT_FACE_RAY_WHEEL":
        return "Das rechte Rad besitzt keinen sichtbaren Schlüssel zu den anderen Rädern und keine sicher abgetrennten 28 Einträge."
    raise ValueError(ns)


def source_status(status: str) -> str:
    return {
        "DIRECT_VISIBLE": "VISIBLE_GROUP_AND_DIRECT_OWNER; FUNCTION_FROM_MASTER_EXEMPLAR",
        "INHERITED_VISIBLE": "VISIBLE_GROUP_AND_LOCAL_INHERITED_OWNER; FUNCTION_FROM_MASTER_EXEMPLAR",
        "PAGE_OWNER_ONLY": "VISIBLE_GROUP_AND_PAGE_LOCAL_OWNER; FUNCTION_FROM_MASTER_EXEMPLAR",
        "UNRESOLVED": "VISIBLE_GROUP; OWNER_ASSIGNMENT_REQUIRES_MASTER_EXEMPLAR",
    }[status]


def group_instruction(owner_row: dict[str, str], group: dict[str, str]) -> str:
    kind = owner_kind(owner_row["selected_visible_owner"])
    idx = int(group["event_index"])
    total = int(owner_row["member_count"])
    surface = group["surface_display_only"]
    if total == 1:
        copy = (f"Kopiere das vollständige opake Etikett «{surface}» für den Bildbesitzer "
                f"«{owner_row['silent_argument_default']}».")
    else:
        copy = (f"Kopiere Segment {idx}/{total} «{surface}» in Quellordnung für den Bildbesitzer "
                f"«{owner_row['silent_argument_default']}»; das Segment erhält keinen Einzelwert.")
    return f"{copy} {use_rule(kind)}"


def locus_reading(owner_row: dict[str, str], groups: list[dict[str, str]]) -> str:
    owner = owner_row["selected_visible_owner"]
    label = " ".join(g["surface_display_only"] for g in groups)
    return (f"Am Besitzer [{owner}] setze das vollständige opake Lokaletikett «{label}». "
            f"{use_rule(owner_kind(owner))} Das Etikett bleibt eine abschreibbare lokale Identität, keine Wort- oder Kartenbedeutung.")


def orientation_rows() -> list[dict[str, str]]:
    raw = [
        ("O01", "f67r2", "beide Räder", "zwei getrennte sichtbare Räder", "UNKNOWN", "UNKNOWN", "UNLICENSED", "jedes Rad separat zeigen und kopieren", "keine Rad-zu-Rad-Konkordanz", "NONE", "kein gezeichneter Verbinder"),
        ("O02", "f67r2", "rechtes Sektorinventar", "zwölf editoriale lokale Sektoradressen", "UNKNOWN", "UNKNOWN", "UNLICENSED", "Sektor nach Bildlage wählen", "keine Zeichen-, Monats- oder Körperreihenfolge", "NONE", "zwölf Plätze identifizieren keinen Start"),
        ("O03", "f67r2", "rechtes Scheibeninventar", "acht editoriale lokale Scheibenadressen", "UNKNOWN", "UNKNOWN", "UNLICENSED", "Scheibenplatz nach Bildlage wählen", "keine Phasenfolge", "NONE", "acht Plätze identifizieren keine Funktion"),
        ("O04", "f67r2", "linke lokale Felder", "editoriale Quellorte 15–51", "UNKNOWN", "UNKNOWN", "UNLICENSED", "Feld nach Bildlage wählen", "keine lineare oder zyklische Feldfolge", "NONE", "Feldzahl ist keine sichtbare Skala"),
        ("O05", "f67r2", "linke äußere Sterne", "zwölf editoriale Sternadressen", "UNKNOWN", "UNKNOWN", "UNLICENSED", "Stern nach Bildlage wählen", "keine gemeinsame Ordnung mit rechten Sektoren", "NONE", "gleiche Kardinalität ist kein Schlüssel"),
        ("O06", "f67r2", "globale 7×12-Annahme", "NONE", "NONE", "NONE", "FORBIDDEN", "zwei lokale Räder getrennt halten", "keine 84 Zellen oder produktive 7×12-Komposition", "NONE", "keine rechteckige Matrix sichtbar"),
        ("O07", "f68r1", "gesamter Sternatlas", "mehrere Paneele/Felder und mindestens fünf Zentren", "NOT_APPLICABLE", "NOT_APPLICABLE", "UNLICENSED", "Paneel und Stern räumlich zeigen", "kein ganzseitiges Zentrum-plus-28-System", "NONE", "Mehrzentren-Geometrie"),
        ("O08", "f68r1", "28 Sternetiketten", "28 editoriale Atlasadressen, nicht ein Kreis", "NOT_APPLICABLE", "NOT_APPLICABLE", "UNLICENSED", "Sternplatz nach Bildlage wählen", "keine Mondhausfolge oder Kreisrotation", "NONE", "Paneelzuordnung bleibt teilweise offen"),
        ("O09", "f68r1", "Gesichtsmedaillons/Zentren", "mehrere sichtbare Zentren", "NOT_APPLICABLE", "NOT_APPLICABLE", "UNLICENSED", "Zentrum nur laut Exemplar zuweisen", "kein einziges Seitenzentrum", "NONE", "genauer Besitzer von Zentrumsschlüsseln ungelöst"),
        ("O10", "f69v", "gesamte Dreiradseite", "drei unverbundene heterogene Räder", "UNKNOWN", "UNKNOWN", "UNLICENSED", "jedes Rad separat zeigen und kopieren", "keine gemeinsame Startlage oder Drehung", "NONE", "keine gezeichneten Verbinder"),
        ("O11", "f69v", "linkes 28-Platz-Rad", "ungeordnetes lokales Inventar von 28 editorischen Adressen", "UNKNOWN", "UNKNOWN", "UNLICENSED", "Platz nach Bildlage wählen", "keine geordnete 28-Regelfolge", "NONE", "ungefähre Kardinalität beweist weder Reihenfolge noch Inhalt"),
        ("O12", "f69v", "mittleres Wolken-/Wellenrad", "ein eigener Ringtext ohne 28-Teilung", "UNKNOWN", "UNKNOWN", "UNLICENSED", "Ringtext im mittleren Rad halten", "keine 28 Plätze aus dem linken Rad erben", "NONE", "keine sichtbare lokale 28-Teilung"),
        ("O13", "f69v", "rechtes Gesicht-Strahlenrad", "ein eigener Ringtext ohne 28-Teilung", "UNKNOWN", "UNKNOWN", "UNLICENSED", "Ringtext im rechten Rad halten", "keine 28 Plätze aus dem linken Rad erben", "NONE", "keine sichtbare lokale 28-Teilung"),
        ("O14", "f68r1↔f69v", "seitenübergreifender Schlüssel", "NONE", "NONE", "NONE", "FORBIDDEN", "beide Seiten unabhängig rücklesen", "kein Sxx↔Rxx oder Stern↔Radialplatz", "NONE", "kein sichtbarer Join"),
        ("O15", "alle Astro-Seiten", "Prosa-/Kartenimport", "NONE", "NONE", "NONE", "FORBIDDEN", "nur lokale sichtbare Gruppen kopieren", "keine Prosa-Karte, kein Stamm, kein Klangwert", "NONE", "keine externe Stringverankerung"),
    ]
    fields = ("audit_id", "page_scope", "instrument_scope", "frozen_address_convention",
              "authorial_start", "authorial_direction", "rotation_status", "allowed_operation",
              "forbidden_inference", "cross_namespace_join", "contradiction")
    return [dict(zip(fields, row)) for row in raw]


def reading_sort_key(row: dict[str, str]) -> tuple[int, int]:
    page = row["page"]
    locus_num = int(row["locus"].split(".")[-1])
    owner = row["selected_visible_owner"]
    if page == "f67r2":
        if owner.startswith("A1_RIGHT_"):
            return (0, locus_num)
        if owner.startswith("A1_LEFT_"):
            return (1, locus_num)
        return (2, locus_num)
    if page == "f68r1":
        return (0, locus_num)
    if owner.startswith("A3_LEFT_"):
        return (0, locus_num)
    if owner.startswith("A3_MIDDLE_"):
        return (1, locus_num)
    return (2, locus_num)


def build() -> None:
    source_groups = read_tsv(GROUP_SOURCE)
    if len(source_groups) != 395 or {r["page"] for r in source_groups} != set(PAGES):
        raise ValueError("frozen Astro group source is not exactly the fixed three-page panel")
    owners = [r for r in read_tsv(OWNER_SOURCE)
              if r["unit_kind"] == "ASTRO_LOCUS" and r["page"] in PAGES]
    if len(owners) != 142:
        raise ValueError(f"expected 142 Astro owners, got {len(owners)}")
    owner_by_locus = {r["locus"]: r for r in owners}
    if len(owner_by_locus) != 142:
        raise ValueError("duplicate V71 Astro owner")
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in source_groups:
        grouped[row["locus"]].append(row)
    if set(grouped) != set(owner_by_locus):
        raise ValueError("V69/V71 locus mismatch")
    for locus, rows in grouped.items():
        rows.sort(key=lambda r: int(r["event_index"]))
        if len(rows) != int(owner_by_locus[locus]["member_count"]):
            raise ValueError(f"member count mismatch at {locus}")

    group_rows: list[dict[str, object]] = []
    locus_rows: list[dict[str, object]] = []
    for locus in sorted(grouped, key=lambda x: (PAGES.index(x.split(".")[0]), int(x.split(".")[-1]))):
        rows = grouped[locus]
        own = owner_by_locus[locus]
        owner = own["selected_visible_owner"]
        ns = owner_namespace(owner)
        kind = owner_kind(owner)
        for group in rows:
            group_rows.append({
                "group_serial": group["group_serial"],
                "diagram_id": group["diagram_id"],
                "page": group["page"],
                "locus": group["locus"],
                "event_index": group["event_index"],
                "opaque_local_id": group["opaque_local_id"],
                "surface_display_only": group["surface_display_only"],
                "exact_visible_identity_layer":
                    f"{group['opaque_local_id']}@{group['locus']}#{group['event_index']}=«{group['surface_display_only']}»",
                "v69_local_formal_role": group["local_formal_role"],
                "v71_owner_status": own["owner_status"],
                "v71_visible_owner": owner,
                "local_namespace": ns,
                "local_owner_kind": kind,
                "silent_argument_default": own["silent_argument_default"],
                "concrete_copied_label_or_instruction": group_instruction(own, group),
                "source_status": source_status(own["owner_status"]),
                "confidence": own["confidence"],
                "historical_celestial_rival": historical_rival(owner),
                "technical_formal_rival": technical_rival(owner),
                "contradiction": contradiction(owner),
                "authorial_start": "UNKNOWN_OR_NOT_APPLICABLE",
                "authorial_direction": "UNKNOWN_OR_NOT_APPLICABLE",
                "rotation_status": "UNLICENSED",
                "f68_f69_mapping": "NONE",
                "cross_wheel_join": "NONE",
                "prose_card_import": "NONE",
                "global_7x12": "NONE",
                "semantic_ceiling": "LOCAL_VISIBLE_IDENTITY_AND_EXEMPLAR_INSTRUCTION_NOT_WORD_CARD_STEM_SOUND_LANGUAGE_OR_MEANING",
            })
        locus_rows.append({
            "locus_row": len(locus_rows) + 1,
            "diagram_id": rows[0]["diagram_id"],
            "page": rows[0]["page"],
            "locus": locus,
            "group_count": len(rows),
            "group_serials": "|".join(r["group_serial"] for r in rows),
            "opaque_local_ids": "|".join(r["opaque_local_id"] for r in rows),
            "surface_sequence": "|".join(r["surface_display_only"] for r in rows),
            "complete_visible_label": " ".join(r["surface_display_only"] for r in rows),
            "v71_owner_status": own["owner_status"],
            "selected_visible_owner": owner,
            "local_namespace": ns,
            "local_owner_kind": kind,
            "silent_argument_default": own["silent_argument_default"],
            "visible_basis": own["visible_basis"],
            "continuous_local_reading": locus_reading(own, rows),
            "source_status": source_status(own["owner_status"]),
            "confidence": own["confidence"],
            "historical_celestial_rival": historical_rival(owner),
            "technical_formal_rival": technical_rival(owner),
            "contradiction": contradiction(owner),
            "orientation_status": "SOURCE_LOCUS_ADDRESS_ONLY; AUTHORIAL_START_DIRECTION_ROTATION_UNPROVEN",
            "cross_namespace_join": "NONE",
            "prose_card_import": "NONE",
            "global_7x12": "NONE",
            "semantic_ceiling": "LOCAL_CELESTIAL_OR_FORMAL_OWNER_WITH_EXEMPLAR_VALUE; NO_LEXEME_OR_TRANSLATION",
        })

    write_tsv(GROUP_OUT, group_rows, list(group_rows[0]))
    write_tsv(LOCUS_OUT, locus_rows, list(locus_rows[0]))
    audit = orientation_rows()
    write_tsv(ORIENTATION_OUT, audit, list(audit[0]))

    by_page = defaultdict(list)
    for row in locus_rows:
        by_page[row["page"]].append(row)
    lines = [
        "# V75 R1 — drei vollständige lokale Instrumentrücklesungen", "",
        "Status: konkrete Werkstattfassung eines himmlischen Mehrinstrumentblatts; keine Übersetzung.", "",
        "Jede sichtbare Gruppe bleibt ein opakes abschreibbares Stück. Der deutsche Satz beschreibt, wie ein Lehrling das lokale Etikett setzt und benutzt; er ist keine Glosse der Oberfläche.", "",
        "## Lehrbare Grundregel", "", "```text",
        "SEITE UND INSTRUMENT AUSRUFEN",
        "→ kleinsten sichtbaren Locus zeigen",
        "→ alle Oberflächengruppen in Quellordnung kopieren",
        "→ vollständiges Etikett nur an diesem Bildort rücklesen",
        "→ exemplarischen Himmels-/Kalenderwert nur innerhalb dieses Instruments nachschlagen",
        "→ bei Rad-, Paneel- oder Seitengrenze alle lokalen Schlüssel löschen",
        "→ niemals Start, Richtung, Rotation oder Seitenjoin ergänzen",
        "```", "",
    ]
    page_intro = {
        "f67r2": (
            "## f67r2 — zwei getrennte Himmelsräder",
            "Das rechte Rad besitzt zwölf lokale Sektorplätze, zwei Ringbänder, acht Scheiben-/Bedingungsplätze und eigenen Ringtext. Das linke Rad besitzt lokale Radial-/Ringfelder, zwölf äußere Sternplätze und eigenen Ringtext. Die folgende Reihenfolge gruppiert zur Werkstattkontrolle nach Rad; sie behauptet keine Kreisrichtung und keine 7×12-Komposition."),
        "f68r1": (
            "## f68r1 — mehrpaneeliger Sternatlas",
            "Drei paneellokale Kopfbereiche, weitere ungelöste Legendenstücke, mehrere sichtbare Gesichtsmedaillons/Zentren und 28 räumliche Sternetiketten werden als Atlasbestand kopiert. Die 28 Etiketten sind keine geordnete Kreisfolge und gehören nicht automatisch zu einem einzigen Zentrum."),
        "f69v": (
            "## f69v — drei unverbundene heterogene Räder",
            "Das linke Rad besitzt einen Ringtext und 28 nur editorisch nummerierte, ungeordnete Radialplätze. Das mittlere Wolken-/Wellenrad und das rechte Gesicht-Strahlenrad besitzen je eigenen Ringtext, aber keine geerbte 28-Teilung. Alle drei Instrumente werden getrennt rückgelesen."),
    }
    last_ns = None
    for page in PAGES:
        title, intro = page_intro[page]
        lines.extend([title, "", intro, ""])
        last_ns = None
        for row in sorted(by_page[page], key=reading_sort_key):
            if row["local_namespace"] != last_ns:
                lines.extend([f"### `{row['local_namespace']}`", ""])
                last_ns = row["local_namespace"]
            lines.extend([
                f"- **{row['locus']}** · Besitzer `{row['selected_visible_owner']}` · "
                f"Etikett «{row['complete_visible_label']}»: {row['continuous_local_reading']}",
                f"  - Historisch-himmlischer Rivale: {row['historical_celestial_rival']}.",
                f"  - Technisch/formaler Rivale: {row['technical_formal_rival']}.",
                f"  - Widerspruch: {row['contradiction']}",
            ])
        lines.extend(["", "### Instrumentgrenze", "",
                      "Alle lokalen Besitzer, exemplarischen Werte und möglichen Orientierungen werden gelöscht; die nächste Seite oder das nächste unverbundene Rad beginnt neu.", ""])
    lines.extend([
        "## Rückleseprobe", "",
        "Ein Korrektor muss aus jeder Zeile wieder Seite, Instrument, Locus, komplette sichtbare Oberfläche und Besitzer zeigen können. Er darf aus zwei gleichen Oberflächen keine gleiche Bedeutung ableiten. Er darf auf f69v nur am linken Rad 28 lokale Plätze zählen und muss sie als ungeordnet behandeln. Er darf f68r1 weder zu einem einzigen Zentrum-plus-28-Kreis zusammenziehen noch einen f68-Sternplatz mit einem f69-Radialplatz verbinden.", "",
        "## Typische Lehrlingsfehler", "",
        "- die beiden f67r2-Räder zu einer 7×12-Tabelle multiplizieren;",
        "- die zwölf äußeren Sterne links mit den zwölf Sektoren rechts paaren;",
        "- f68r1 trotz mehrerer Paneele und Zentren als einen einzigen 28er-Kreis lesen;",
        "- den editorischen Locus 01 als sichtbaren Startpunkt behandeln;",
        "- aus Schreibrichtung eine Kreisrichtung oder Rotation ableiten;",
        "- die 28 linken f69v-Plätze auf Mittel- und Rechtsrad übertragen;",
        "- f68- und f69-Adressen wegen ähnlicher Kardinalität verbinden;",
        "- ein konkretes historisches Instrument zur Bedeutung einer sichtbaren Gruppe erklären.", "",
    ])
    READING_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    summary = {
        "status": "BUILT",
        "experiment": "V75_R1_CELESTIAL_MULTI_INSTRUMENT_THIRD_EDITION",
        "counts": {
            "groups": len(group_rows),
            "loci": len(locus_rows),
            "pages": len(by_page),
            "orientation_audit_rows": len(audit),
            "groups_by_page": dict(Counter(r["page"] for r in group_rows)),
            "loci_by_page": dict(Counter(r["page"] for r in locus_rows)),
            "owner_status_loci": dict(Counter(r["v71_owner_status"] for r in locus_rows)),
            "namespaces": len({r["local_namespace"] for r in locus_rows}),
            "f69_left_radial_slots": sum("LEFT_RADIAL_SLOT" in r["selected_visible_owner"] for r in locus_rows),
        },
        "constraints": {
            "authorial_start_assigned": False,
            "authorial_direction_assigned": False,
            "rotation_assigned": False,
            "f68_f69_key_created": False,
            "prose_card_imported": False,
            "global_7x12_created": False,
            "new_card_stem_sound_language_meaning": False,
            "f84_or_f84r_opened": False,
        },
    }
    BUILD_OUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    build()

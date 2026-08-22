#!/usr/bin/env python3
"""Build V75 R3's complete local celestial lookup edition.

Every surface group remains opaque.  The executable layer addresses only the
smallest V71 page-local owner, enumerates orientation alternatives, and never
joins f68 to f69 or imports prose-card values.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
V66 = ROOT / "experiments/yolo/sidequest_theory_candidates_v66"
V69 = ROOT / "experiments/yolo/sidequest_theory_candidates_v69"
V70 = ROOT / "experiments/yolo/sidequest_theory_candidates_v70"
V71 = ROOT / "experiments/yolo/sidequest_theory_candidates_v71"
V74 = ROOT / "experiments/yolo/sidequest_theory_candidates_v74"

GROUP_SOURCE = V69 / "V69_R3_395_ASTRO_GROUP_LEDGER.tsv"
FINAL_GROUP_SOURCE = V69 / "V69_R4_FINAL_395_ASTRO_GROUPS.tsv"
LOCUS_SOURCE = V66 / "V66_R3_142_LOCUS_FUNCTIONS.tsv"
OWNER_SOURCE = V71 / "V71_SELECTED_OWNER_LEDGER.tsv"
IMAGE_SOURCE = V70 / "V70_SELECTED_TEN_PAGE_IMAGE_REVISION.tsv"
CONTINUITY_SOURCE = V74 / "V74_FOUR_ROLE_SELECTION.md"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], columns: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row[column] for column in columns})


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


NAMESPACE_DEFINITIONS: dict[str, dict[str, str]] = {
    "F67_RIGHT_WHEEL_NS": {
        "page": "f67r2", "instrument": "F67_RIGHT_WHEEL", "kind": "RIGHT_CELESTIAL_WHEEL",
        "entry": "address the visible right-wheel sector, phase, band, or ring-text owner directly",
        "orientation": "DIRECT_LOCAL_ADDRESS|ARBITRARY_START_CLOCKWISE|ARBITRARY_START_COUNTERCLOCKWISE|REFLECTED_LAYOUT;SELECTED=NONE",
        "rival_medical": "right-hand astrological or iatromathematical election wheel",
        "rival_formal": "celestial diagram labels or decorative radial text without executable content",
    },
    "F67_LEFT_WHEEL_NS": {
        "page": "f67r2", "instrument": "F67_LEFT_WHEEL", "kind": "LEFT_CELESTIAL_WHEEL",
        "entry": "address the visible left-wheel radial field, star station, band, or ring text directly",
        "orientation": "DIRECT_LOCAL_ADDRESS|ARBITRARY_START_CLOCKWISE|ARBITRARY_START_COUNTERCLOCKWISE|REFLECTED_LAYOUT;SELECTED=NONE",
        "rival_medical": "left-hand astrological or iatromathematical election wheel",
        "rival_formal": "celestial diagram labels or decorative stellar text without executable content",
    },
    "F67_PAIRED_LEGEND_QUARANTINE_NS": {
        "page": "f67r2", "instrument": "F67_PAIRED_WHEEL_LEGEND", "kind": "UNRESOLVED_PAGE_LEGEND",
        "entry": "copy the legend to quarantine until the exemplar chooses left or right wheel",
        "orientation": "LEFT_OWNER|RIGHT_OWNER|PAGE_LEGEND;SELECTED=NONE",
        "rival_medical": "shared medical-election legend for both wheels",
        "rival_formal": "page caption unrelated to either wheel's operational use",
    },
    "F68_LEFT_PANEL_HEADER_NS": {
        "page": "f68r1", "instrument": "F68_LEFT_OPEN_STAR_FIELD", "kind": "LEFT_PANEL_HEADER",
        "entry": "copy only the left-panel header fragments; star-slot membership remains unresolved",
        "orientation": "DIRECT_DRAWN_LOCUS|CENTRE_OUTWARD|EDGE_INWARD|EDITORIAL_SOURCE_ORDER;SELECTED=NONE",
        "rival_medical": "header of a medical-election star field",
        "rival_formal": "panel caption or decorative star-map legend",
    },
    "F68_MIDDLE_PANEL_HEADER_NS": {
        "page": "f68r1", "instrument": "F68_MIDDLE_SECTORIZED_SUBMAP", "kind": "MIDDLE_PANEL_HEADER",
        "entry": "copy only the middle-panel header fragments; no page-wide centre is inferred",
        "orientation": "DIRECT_DRAWN_LOCUS|ARBITRARY_START_CLOCKWISE|ARBITRARY_START_COUNTERCLOCKWISE|UNORDERED_SECTORS;SELECTED=NONE",
        "rival_medical": "header of a sectorized medical-election submap",
        "rival_formal": "circular diagram caption without recoverable lookup values",
    },
    "F68_RIGHT_PANEL_HEADER_NS": {
        "page": "f68r1", "instrument": "F68_RIGHT_OPEN_STAR_FIELD", "kind": "RIGHT_PANEL_HEADER",
        "entry": "copy only the right-panel header fragments; star-slot membership remains unresolved",
        "orientation": "DIRECT_DRAWN_LOCUS|CENTRE_OUTWARD|EDGE_INWARD|EDITORIAL_SOURCE_ORDER;SELECTED=NONE",
        "rival_medical": "header of a second medical-election star field",
        "rival_formal": "panel caption or decorative star-map legend",
    },
    "F68_MULTIPANEL_HEADER_QUARANTINE_NS": {
        "page": "f68r1", "instrument": "F68_MULTIPANEL_HEADER", "kind": "UNRESOLVED_MULTIPANEL_HEADER",
        "entry": "retain the header fragment without assigning it to left, middle, or right panel",
        "orientation": "LEFT_PANEL|MIDDLE_PANEL|RIGHT_PANEL|PAGE_HEADER;SELECTED=NONE",
        "rival_medical": "shared rubric for several election panels",
        "rival_formal": "page-level decorative or catalogue header",
    },
    "F68_CENTRE_KEY_QUARANTINE_NS": {
        "page": "f68r1", "instrument": "F68_FACE_CENTRE_SET", "kind": "UNRESOLVED_FACE_CENTRE_KEY",
        "entry": "copy the key while leaving the choice among at least five visible face centres to the exemplar",
        "orientation": "DIRECT_MEDALLION_ADDRESS|PANEL_LOCAL_CENTRE|NEAREST_STAR_BINDING|EDITORIAL_SOURCE_ORDER;SELECTED=NONE",
        "rival_medical": "planetary, temporal, or bodily owner medallion for a local election panel",
        "rival_formal": "portrait medallion or decorative centre without lookup semantics",
    },
    "F68_LOCAL_STAR_SLOT_NS": {
        "page": "f68r1", "instrument": "F68_UNASSIGNED_LOCAL_STAR_STATIONS", "kind": "LOCAL_STAR_SLOT_POOL",
        "entry": "address the drawn star locus directly; do not bind it to one common centre or panel",
        "orientation": "DIRECT_DRAWN_LOCUS|PANEL_LOCAL_RADIAL|CENTRE_OUTWARD|EDITORIAL_SOURCE_ORDER;SELECTED=NONE",
        "rival_medical": "local lunar, stellar, or election station under an unresolved panel owner",
        "rival_formal": "independent star label or spatial catalogue item",
    },
    "F68_CENTRAL_LEGEND_QUARANTINE_NS": {
        "page": "f68r1", "instrument": "F68_CENTRAL_LEGEND", "kind": "UNRESOLVED_CENTRAL_LEGEND",
        "entry": "copy the central legend without making it owner of all star stations",
        "orientation": "LOCAL_PANEL_LEGEND|CENTRE_SET_LEGEND|PAGE_LEGEND;SELECTED=NONE",
        "rival_medical": "central rubric for a medical-election submap",
        "rival_formal": "free legend or decorative centre text",
    },
    "F69_LEFT_WHEEL_NS": {
        "page": "f69v", "instrument": "F69_LEFT_28_SLOT_WHEEL", "kind": "LEFT_WHEEL_WITH_28_UNORDERED_SLOTS",
        "entry": "address ring text or one of the 28 editorial source slots directly",
        "orientation": "UNORDERED_DIRECT_SLOT|ARBITRARY_START_CLOCKWISE|ARBITRARY_START_COUNTERCLOCKWISE|OPPOSED_PAIRING;SELECTED=NONE",
        "rival_medical": "28-place iatromathematical or prognostic election wheel",
        "rival_formal": "radial catalogue or celestial ornament with local labels",
    },
    "F69_MIDDLE_WHEEL_NS": {
        "page": "f69v", "instrument": "F69_MIDDLE_WAVE_WHEEL", "kind": "MIDDLE_WAVE_OR_CLOUD_WHEEL",
        "entry": "copy only the middle wheel's own ring text; no 28-slot inventory is licensed",
        "orientation": "DIRECT_RING_ADDRESS|ARBITRARY_START_CLOCKWISE|ARBITRARY_START_COUNTERCLOCKWISE|STATIC_UNORDERED_RING;SELECTED=NONE",
        "rival_medical": "middle prognostic or meteorological election wheel",
        "rival_formal": "cloud- or wave-rosette caption",
    },
    "F69_RIGHT_WHEEL_NS": {
        "page": "f69v", "instrument": "F69_RIGHT_FACE_RAY_WHEEL", "kind": "RIGHT_FACE_RAY_WHEEL",
        "entry": "copy only the right wheel's own ring text; no 28-slot inventory is licensed",
        "orientation": "DIRECT_RING_ADDRESS|ARBITRARY_START_CLOCKWISE|ARBITRARY_START_COUNTERCLOCKWISE|STATIC_UNORDERED_RING;SELECTED=NONE",
        "rival_medical": "right prognostic or election wheel centred on a face",
        "rival_formal": "face-and-ray emblem with a local caption",
    },
}


INSTRUMENTS: dict[str, dict[str, str]] = {
    "F67_LEFT_WHEEL": {
        "page": "f67r2", "kind": "RADIAL_CELESTIAL_WHEEL", "namespaces": "F67_LEFT_WHEEL_NS",
        "assignment": "left radial fields, outer stars and left ring text are local; no connector to the right wheel",
        "technical": "direct-address lookup over left-wheel fields and star stations without an origin",
        "medical": "astrological or iatromathematical selector wheel",
        "formal": "static celestial wheel with labels",
        "basis": "V70 sees one of two differently organized wheels and no drawn connector.",
    },
    "F67_RIGHT_WHEEL": {
        "page": "f67r2", "kind": "RADIAL_CELESTIAL_WHEEL", "namespaces": "F67_RIGHT_WHEEL_NS",
        "assignment": "right sector, phase, band and ring owners remain local to the right wheel",
        "technical": "direct-address lookup over right-wheel sectors and conditions without an origin",
        "medical": "second astrological or iatromathematical selector wheel",
        "formal": "static celestial wheel with labels",
        "basis": "V70 sees a second differently organized wheel and no drawn connector.",
    },
    "F68_LEFT_OPEN_STAR_FIELD": {
        "page": "f68r1", "kind": "OPEN_STAR_FIELD", "namespaces": "F68_LEFT_PANEL_HEADER_NS|F68_LOCAL_STAR_SLOT_NS[SUBSET_UNRESOLVED]",
        "assignment": "left header is bound; membership of the 28 editorial star loci is not",
        "technical": "local spatial catalogue addressed by drawn star position",
        "medical": "stellar or lunar election field",
        "formal": "decorative or descriptive star panel",
        "basis": "V70 sees one open star field among several panels and centres.",
    },
    "F68_MIDDLE_SECTORIZED_SUBMAP": {
        "page": "f68r1", "kind": "SECTORIZED_CIRCULAR_SUBMAP", "namespaces": "F68_MIDDLE_PANEL_HEADER_NS|F68_LOCAL_STAR_SLOT_NS[SUBSET_UNRESOLVED]",
        "assignment": "middle header is bound; its sector labels are not separable from the local star-slot pool",
        "technical": "sector-local direct lookup without page-wide centre or direction",
        "medical": "sectorized election or calendrical submap",
        "formal": "circular celestial diagram with local labels",
        "basis": "V70 distinguishes a sectorized circular submap from the open fields.",
    },
    "F68_RIGHT_OPEN_STAR_FIELD": {
        "page": "f68r1", "kind": "OPEN_STAR_FIELD", "namespaces": "F68_RIGHT_PANEL_HEADER_NS|F68_LOCAL_STAR_SLOT_NS[SUBSET_UNRESOLVED]",
        "assignment": "right header is bound; membership of the 28 editorial star loci is not",
        "technical": "second local spatial catalogue addressed by drawn star position",
        "medical": "second stellar or lunar election field",
        "formal": "decorative or descriptive star panel",
        "basis": "V70 sees a second open star field among several panels and centres.",
    },
    "F68_FACE_CENTRE_SET": {
        "page": "f68r1", "kind": "MULTIPLE_FACE_CENTRES", "namespaces": "F68_CENTRE_KEY_QUARANTINE_NS|F68_CENTRAL_LEGEND_QUARANTINE_NS",
        "assignment": "at least five face centres exist; the key and legend cannot choose one without the exemplar",
        "technical": "owner-key register with centre choice quarantined",
        "medical": "planetary, temporal, bodily, or prognostic centre owners",
        "formal": "portrait medallions or ornamental centres",
        "basis": "V70 records at least five centres and rejects one page-wide centre.",
    },
    "F69_LEFT_28_SLOT_WHEEL": {
        "page": "f69v", "kind": "LEFT_RADIAL_WHEEL", "namespaces": "F69_LEFT_WHEEL_NS",
        "assignment": "ring text plus exactly 28 editorial radial slots, all local to the left wheel",
        "technical": "unordered 28-slot direct-address inventory; cyclic traversal remains only an alternative",
        "medical": "28-place prognostic or election wheel",
        "formal": "radial celestial catalogue or ornament",
        "basis": "V70 sees approximately 28 places on the left wheel only.",
    },
    "F69_MIDDLE_WAVE_WHEEL": {
        "page": "f69v", "kind": "MIDDLE_WAVE_OR_CLOUD_WHEEL", "namespaces": "F69_MIDDLE_WHEEL_NS",
        "assignment": "only its own ring-text locus is bound; no left-wheel slots are inherited",
        "technical": "independent ring-header lookup with unknown local body values",
        "medical": "meteorological, prognostic, or election wheel",
        "formal": "cloud- or wave-rosette",
        "basis": "V70 sees a heterogeneous middle wheel disconnected from the other two.",
    },
    "F69_RIGHT_FACE_RAY_WHEEL": {
        "page": "f69v", "kind": "RIGHT_FACE_RAY_WHEEL", "namespaces": "F69_RIGHT_WHEEL_NS",
        "assignment": "only its own ring-text locus is bound; no left-wheel slots are inherited",
        "technical": "independent face/ray ring lookup with unknown local body values",
        "medical": "prognostic or election wheel",
        "formal": "face-and-ray emblem",
        "basis": "V70 sees a heterogeneous right wheel disconnected from the other two.",
    },
}


def locus_number(source_locus: str) -> int:
    return int(source_locus.rsplit(".", 1)[1])


def namespace_for(page: str, source_locus: str) -> str:
    number = locus_number(source_locus)
    if page == "f67r2":
        if number == 74:
            return "F67_PAIRED_LEGEND_QUARANTINE_NS"
        if number in range(1, 15) or number in range(64, 72) or number == 73:
            return "F67_RIGHT_WHEEL_NS"
        return "F67_LEFT_WHEEL_NS"
    if page == "f68r1":
        if number == 1:
            return "F68_LEFT_PANEL_HEADER_NS"
        if number == 2:
            return "F68_MIDDLE_PANEL_HEADER_NS"
        if number == 3:
            return "F68_RIGHT_PANEL_HEADER_NS"
        if number in range(4, 8):
            return "F68_MULTIPANEL_HEADER_QUARANTINE_NS"
        if number == 8:
            return "F68_CENTRE_KEY_QUARANTINE_NS"
        if number in range(9, 37):
            return "F68_LOCAL_STAR_SLOT_NS"
        return "F68_CENTRAL_LEGEND_QUARANTINE_NS"
    if number == 1 or number in range(4, 32):
        return "F69_LEFT_WHEEL_NS"
    if number == 2:
        return "F69_MIDDLE_WHEEL_NS"
    return "F69_RIGHT_WHEEL_NS"


def source_class(owner: dict[str, str]) -> str:
    owner_id = owner["selected_visible_owner"]
    status = owner["owner_status"]
    if status == "UNRESOLVED":
        return "OPAQUE_GROUP_IN_UNRESOLVED_LEGEND_OR_CENTRE_QUARANTINE"
    if "STAR_STATION" in owner_id or "RADIAL_SLOT" in owner_id or "SECTOR_SLOT" in owner_id or "PHASE_STATION" in owner_id:
        return "OPAQUE_GROUP_AT_DIRECT_VISIBLE_LOCAL_SLOT"
    if "RING_TEXT" in owner_id or "RING_BAND" in owner_id:
        return "OPAQUE_GROUP_IN_LOCAL_RING_OR_BAND_TEXT"
    if status == "PAGE_OWNER_ONLY":
        return "OPAQUE_GROUP_IN_PANEL_HEADER"
    return "OPAQUE_GROUP_AT_INHERITED_LOCAL_FIELD"


def confidence(owner_status: str, group_index: int) -> str:
    base = {"DIRECT_VISIBLE": 0.43, "INHERITED_VISIBLE": 0.32, "PAGE_OWNER_ONLY": 0.24, "UNRESOLVED": 0.10}[owner_status]
    if group_index > 1:
        base -= 0.02
    return f"{base:.2f}"


def local_address(namespace: str, owner_id: str, group_index: int) -> str:
    return f"{namespace}/{owner_id}/FRAGMENT_{group_index:02d}"


def technical_default(group: dict[str, str], owner: dict[str, str], namespace: str, group_count: int) -> str:
    number = locus_number(group["source_locus"])
    index = int(group["group_index_within_locus"])
    surface = group["surface_display_only"]
    fragment = f"Kopiere die sichtbare Gruppe „{surface}“ als Fragment {index}/{group_count} in den örtlichen Ergebnisposten."
    if namespace == "F67_RIGHT_WHEEL_NS":
        return f"Öffne am rechten f67r2-Rad ausschließlich den Besitzer „{owner['selected_visible_owner']}“. {fragment} Wähle weder Anfang noch Drehsinn und rufe kein linkes Radfeld auf."
    if namespace == "F67_LEFT_WHEEL_NS":
        return f"Öffne am linken f67r2-Rad ausschließlich den Besitzer „{owner['selected_visible_owner']}“. {fragment} Wähle weder Anfang noch Drehsinn und rufe kein rechtes Radfeld auf."
    if namespace == "F67_PAIRED_LEGEND_QUARANTINE_NS":
        return f"Lege die gemeinsame f67r2-Legende in einen ungelösten Seitenposten. {fragment} Weise sie ohne Exemplar weder dem linken noch dem rechten Rad zu."
    if namespace in {"F68_LEFT_PANEL_HEADER_NS", "F68_MIDDLE_PANEL_HEADER_NS", "F68_RIGHT_PANEL_HEADER_NS"}:
        panel = {"F68_LEFT_PANEL_HEADER_NS": "linken", "F68_MIDDLE_PANEL_HEADER_NS": "mittleren", "F68_RIGHT_PANEL_HEADER_NS": "rechten"}[namespace]
        return f"Öffne nur den {panel} f68r1-Paneelkopf. {fragment} Binde daraus keinen Sternplatz und kein fremdes Zentrum automatisch an."
    if namespace == "F68_MULTIPANEL_HEADER_QUARANTINE_NS":
        return f"Lege das mehrpaneelige f68r1-Kopffragment in den Quarantäneposten {number:02d}. {fragment} Entscheide ohne Exemplar kein Paneel."
    if namespace == "F68_CENTRE_KEY_QUARANTINE_NS":
        return f"Öffne den ungelösten f68r1-Zentrumschlüssel. {fragment} Halte die Wahl unter mindestens fünf Gesichtsmedaillons offen und erzeuge kein Seitenzentrum."
    if namespace == "F68_LOCAL_STAR_SLOT_NS":
        slot = number - 8
        return f"Öffne den direkt gezeichneten f68r1-Sternplatz S{slot:02d}. {fragment} Halte Paneel und Gesichtszentrum lokal unbestimmt und rufe niemals f69v auf."
    if namespace == "F68_CENTRAL_LEGEND_QUARANTINE_NS":
        return f"Lege die f68r1-Zentrallegende in einen lokalen Quarantäneposten. {fragment} Mache sie weder zum Besitzer aller Paneele noch zum Schlüssel für f69v."
    if namespace == "F69_LEFT_WHEEL_NS" and number >= 4:
        slot = number - 3
        return f"Öffne am linken f69v-Rad den editorialen Radialslot U{slot:02d} direkt, ohne Vorgänger oder Nachfolger. {fragment} Behalte alle 28 Slots ungeordnet und wähle keinen Start oder Drehsinn."
    if namespace == "F69_LEFT_WHEEL_NS":
        return f"Öffne ausschließlich den Ringtext des linken f69v-Rades. {fragment} Verwende ihn nicht als Startmarke für die 28 Slots."
    if namespace == "F69_MIDDLE_WHEEL_NS":
        return f"Öffne ausschließlich den Ringtext des mittleren f69v-Wolken-/Wellenrades. {fragment} Übernimm weder 28 Slots noch Richtung vom linken Rad."
    return f"Öffne ausschließlich den Ringtext des rechten f69v-Gesicht-/Strahlenrades. {fragment} Übernimm weder 28 Slots noch Richtung vom linken Rad."


def contradiction(page: str, namespace: str, owner: dict[str, str]) -> str:
    page_issue = {
        "f67r2": "Die Seite zeigt zwei verschieden organisierte Räder ohne Verbindung und keine sichtbare 7×12-Matrix.",
        "f68r1": "Die Seite zeigt mehrere Paneele und mindestens fünf Zentren; ein gemeinsames Zentrum-plus-28-Objekt ist nicht sichtbar.",
        "f69v": "Die Seite zeigt drei unverbundene heterogene Räder; nur das linke trägt ungefähr 28 radiale Plätze.",
    }[page]
    return f"{owner['visible_basis']}. {page_issue} Start, Richtung und der konkrete Exemplarwert bleiben unbestimmt; {namespace} ist nur eine lokale Werkstattadresse."


def orientation_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    circular = {
        "F67_LEFT_WHEEL", "F67_RIGHT_WHEEL", "F68_MIDDLE_SECTORIZED_SUBMAP",
        "F69_LEFT_28_SLOT_WHEEL", "F69_MIDDLE_WAVE_WHEEL", "F69_RIGHT_FACE_RAY_WHEEL",
    }
    for instrument_id, instrument in INSTRUMENTS.items():
        if instrument_id in circular:
            alternatives = [
                ("DIRECT_UNORDERED", "NO_AUTHORIAL_START", "DIRECT_LOCAL_ADDRESS_WITHOUT_TRAVERSAL", "ADMISSIBLE_UNSELECTED"),
                ("CW_ARBITRARY_START", "ANY_VISIBLE_SLOT", "CLOCKWISE", "ADMISSIBLE_UNSELECTED"),
                ("CCW_ARBITRARY_START", "ANY_VISIBLE_SLOT", "COUNTERCLOCKWISE", "ADMISSIBLE_UNSELECTED"),
                ("REFLECTED_OR_OPPOSED", "ANY_VISIBLE_SLOT_OR_PAIR", "REFLECTED_OR_OPPOSED_PAIRING", "POSSIBLE_UNSELECTED"),
            ]
        elif instrument_id == "F68_FACE_CENTRE_SET":
            alternatives = [
                ("DIRECT_MEDALLION", "EXEMPLAR_CHOSEN_MEDALLION", "NO_TRAVERSAL", "ADMISSIBLE_UNSELECTED"),
                ("PANEL_LOCAL_CENTRE", "EXEMPLAR_CHOSEN_PANEL", "CENTRE_TO_LOCAL_SLOTS", "ADMISSIBLE_UNSELECTED"),
                ("NEAREST_STAR_BINDING", "EXEMPLAR_CHOSEN_MEDALLION", "NEAREST_DRAWN_STARS", "POSSIBLE_UNSELECTED"),
                ("PAGE_WIDE_CENTRE", "ONE_PAGE_CENTRE", "ALL_STAR_SLOTS", "REJECTED_BY_MULTICENTRE_GEOMETRY"),
            ]
        else:
            alternatives = [
                ("DIRECT_DRAWN_LOCUS", "NO_AUTHORIAL_START", "NO_TRAVERSAL", "ADMISSIBLE_UNSELECTED"),
                ("CENTRE_OUTWARD", "EXEMPLAR_CHOSEN_LOCAL_CENTRE", "RADIAL_OUTWARD", "POSSIBLE_UNSELECTED"),
                ("EDGE_INWARD", "EXEMPLAR_CHOSEN_EDGE", "RADIAL_INWARD", "POSSIBLE_UNSELECTED"),
                ("EDITORIAL_SOURCE_ORDER", "FIRST_TRANSCRIBED_LOCUS", "SOURCE_ORDER_ONLY", "AUDIT_ONLY_NOT_AUTHORIAL"),
            ]
        for ordinal, (alternative, start, traversal, status) in enumerate(alternatives, 1):
            rows.append({
                "orientation_alternative_id": f"{instrument_id}:O{ordinal}",
                "instrument_id": instrument_id,
                "page": instrument["page"],
                "alternative": alternative,
                "start_rule": start,
                "traversal_rule": traversal,
                "admissibility": status,
                "selected_orientation": "NONE",
                "required_external_information": "MASTER_EXEMPLAR_OR_EXTERNAL_ANCHOR",
                "cross_instrument_effect": "NONE;NEVER_ALIGNS_F68_WITH_F69",
            })
    return rows


def build() -> None:
    groups = read_tsv(GROUP_SOURCE)
    final_groups = {row["group_serial"]: row for row in read_tsv(FINAL_GROUP_SOURCE)}
    loci = read_tsv(LOCUS_SOURCE)
    owners = {
        row["locus"]: row for row in read_tsv(OWNER_SOURCE)
        if row["section"] == "ASTRO" and row["unit_kind"] == "ASTRO_LOCUS"
    }
    image_rows = [row for row in read_tsv(IMAGE_SOURCE) if row["page"] in {"f67r2", "f68r1", "f69v"}]
    assert len(groups) == 395 and len(final_groups) == 395 and len(loci) == 142 and len(owners) == 142 and len(image_rows) == 3

    locus_group_count = {row["source_locus"]: int(row["group_count"]) for row in loci}
    group_rows: list[dict[str, object]] = []
    groups_by_locus: dict[str, list[dict[str, object]]] = defaultdict(list)
    for group in groups:
        serial = group["astro_group_serial"]
        final = final_groups[serial]
        assert final["opaque_local_id"] == group["local_group_id"]
        assert final["surface_display_only"] == group["surface_display_only"]
        assert final["locus"] == group["source_locus"]
        owner = owners[group["source_locus"]]
        namespace = namespace_for(group["page"], group["source_locus"])
        definition = NAMESPACE_DEFINITIONS[namespace]
        group_index = int(group["group_index_within_locus"])
        group_count = locus_group_count[group["source_locus"]]
        row: dict[str, object] = {
            "astro_group_serial": serial,
            "unified_group_ordinal": group["unified_group_ordinal"],
            "diagram_id": group["diagram_id"],
            "page": group["page"],
            "source_locus": group["source_locus"],
            "local_locus_id": group["local_locus_id"],
            "local_group_id": group["local_group_id"],
            "group_index_within_locus": group_index,
            "surface_display_only_exact": group["surface_display_only"],
            "frozen_v69_editorial_address": group["local_lookup_address"],
            "frozen_v69_formal_role_address_only": group["formal_local_role"],
            "v75_local_namespace": namespace,
            "v75_instrument_id": definition["instrument"],
            "v75_local_namespace_address": local_address(namespace, owner["selected_visible_owner"], group_index),
            "owner_status": owner["owner_status"],
            "smallest_visible_owner": owner["selected_visible_owner"],
            "concrete_technical_lookup_default": technical_default(group, owner, namespace, group_count),
            "lookup_effect": "OPEN_LOCAL_NAMESPACE>COPY_OPAQUE_FRAGMENT>PRESERVE_SOURCE_LOCUS>CLOSE_LOCUS_IF_FINAL_FRAGMENT",
            "source_class": source_class(owner),
            "confidence": confidence(owner["owner_status"], group_index),
            "orientation_and_start_alternatives": definition["orientation"],
            "crosspage_contract": "PAGE_LOCAL_ONLY;NO_F68_F69_JOIN;NO_COMMON_DIRECTION;NO_PROSE_CARD_VALUE",
            "iatromedical_rival": "IATROMEDICAL_RIVAL: " + definition["rival_medical"] + ".",
            "formal_iconographic_rival": "FORMAL_RIVAL: " + definition["rival_formal"] + ".",
            "contradiction": contradiction(group["page"], namespace, owner),
            "legacy_model_correction": "V66_FORMAL_ADDRESS_RETAINED_ONLY;NO_PAGEWIDE_7X12;NO_SINGLE_CENTER_PLUS_28;NO_ORDERED_PAGEWIDE_28_RULES",
            "semantic_ceiling": "OPAQUE_LOCAL_GROUP_NOT_PROSE_CARD_WORD_STEM_SOUND_LANGUAGE_MEANING_OR_TRANSLATION",
        }
        group_rows.append(row)
        groups_by_locus[group["source_locus"]].append(row)

    group_columns = [
        "astro_group_serial", "unified_group_ordinal", "diagram_id", "page", "source_locus",
        "local_locus_id", "local_group_id", "group_index_within_locus",
        "surface_display_only_exact", "frozen_v69_editorial_address",
        "frozen_v69_formal_role_address_only", "v75_local_namespace", "v75_instrument_id",
        "v75_local_namespace_address", "owner_status", "smallest_visible_owner",
        "concrete_technical_lookup_default", "lookup_effect", "source_class", "confidence",
        "orientation_and_start_alternatives", "crosspage_contract", "iatromedical_rival",
        "formal_iconographic_rival", "contradiction", "legacy_model_correction", "semantic_ceiling",
    ]
    group_path = OUT / "V75_R3_395_GROUP_LOOKUP_EDITION.tsv"
    write_tsv(group_path, group_rows, group_columns)

    locus_rows: list[dict[str, object]] = []
    for locus in loci:
        owner = owners[locus["source_locus"]]
        namespace = namespace_for(locus["page"], locus["source_locus"])
        definition = NAMESPACE_DEFINITIONS[namespace]
        rows = groups_by_locus[locus["source_locus"]]
        locus_rows.append({
            "local_locus_id": locus["local_locus_id"],
            "diagram_id": locus["diagram_id"],
            "page": locus["page"],
            "source_locus": locus["source_locus"],
            "locus_ordinal_editorial": locus["locus_ordinal_editorial"],
            "group_count": locus["group_count"],
            "local_group_ids": locus["local_group_ids"],
            "surface_sequence_display_only_exact": locus["surface_sequence_display_only"],
            "v75_local_namespace": namespace,
            "v75_instrument_id": definition["instrument"],
            "smallest_visible_owner": owner["selected_visible_owner"],
            "owner_status": owner["owner_status"],
            "local_lookup_address": f"{namespace}/{owner['selected_visible_owner']}",
            "source_class": source_class(owner),
            "formal_role_sequence_address_only": " > ".join(str(row["frozen_v69_formal_role_address_only"]) for row in rows),
            "complete_concrete_technical_locus_reading": " ".join(str(row["concrete_technical_lookup_default"]) for row in rows),
            "orientation_and_start_alternatives": definition["orientation"],
            "crosspage_contract": "PAGE_LOCAL_ONLY;NO_F68_F69_JOIN;NO_COMMON_DIRECTION;NO_PROSE_CARD_VALUE",
            "confidence": confidence(owner["owner_status"], 1),
            "iatromedical_rival": "IATROMEDICAL_RIVAL: " + definition["rival_medical"] + ".",
            "formal_iconographic_rival": "FORMAL_RIVAL: " + definition["rival_formal"] + ".",
            "visible_basis": owner["visible_basis"],
            "contradiction": contradiction(locus["page"], namespace, owner),
            "semantic_ceiling": "LOCAL_LOOKUP_LOCUS_NOT_WORD_CARD_MEANING_OR_TRANSLATION",
        })
    locus_columns = [
        "local_locus_id", "diagram_id", "page", "source_locus", "locus_ordinal_editorial",
        "group_count", "local_group_ids", "surface_sequence_display_only_exact",
        "v75_local_namespace", "v75_instrument_id", "smallest_visible_owner", "owner_status",
        "local_lookup_address", "source_class", "formal_role_sequence_address_only",
        "complete_concrete_technical_locus_reading", "orientation_and_start_alternatives",
        "crosspage_contract", "confidence", "iatromedical_rival", "formal_iconographic_rival",
        "visible_basis", "contradiction", "semantic_ceiling",
    ]
    locus_path = OUT / "V75_R3_142_LOCUS_LOOKUP_EDITION.tsv"
    write_tsv(locus_path, locus_rows, locus_columns)

    namespace_loci: dict[str, list[dict[str, object]]] = defaultdict(list)
    namespace_groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in locus_rows:
        namespace_loci[str(row["v75_local_namespace"])].append(row)
    for row in group_rows:
        namespace_groups[str(row["v75_local_namespace"])].append(row)
    namespace_rows: list[dict[str, object]] = []
    for namespace, definition in NAMESPACE_DEFINITIONS.items():
        ns_loci = namespace_loci[namespace]
        ns_groups = namespace_groups[namespace]
        namespace_rows.append({
            "namespace_id": namespace,
            "page": definition["page"],
            "instrument_id": definition["instrument"],
            "visible_kind": definition["kind"],
            "locus_count": len(ns_loci),
            "group_count": len(ns_groups),
            "source_loci": "|".join(str(row["source_locus"]) for row in ns_loci),
            "entry_rule": definition["entry"],
            "orientation_and_start_alternatives": definition["orientation"],
            "selected_orientation": "NONE",
            "cross_namespace_rule": "RESET_ON_NAMESPACE_CHANGE;NO_IMPLICIT_OWNER_INHERITANCE",
            "crosspage_rule": "NO_CROSSPAGE_JOIN;F68_AND_F69_KEYS_INCOMPATIBLE",
            "prohibited_models": "PAGEWIDE_7X12|SINGLE_F68_CENTER_PLUS_28|ORDERED_PAGEWIDE_F69_28|PROSE_CARD_VALUES",
            "semantic_ceiling": "EXECUTABLE_LOCAL_NAMESPACE_NOT_SEMANTIC_IDENTIFICATION",
        })
    namespace_path = OUT / "V75_R3_NAMESPACE_REGISTRY.tsv"
    write_tsv(namespace_path, namespace_rows, [
        "namespace_id", "page", "instrument_id", "visible_kind", "locus_count", "group_count",
        "source_loci", "entry_rule", "orientation_and_start_alternatives", "selected_orientation",
        "cross_namespace_rule", "crosspage_rule", "prohibited_models", "semantic_ceiling",
    ])

    orientation = orientation_rows()
    orientation_path = OUT / "V75_R3_ORIENTATION_ALTERNATIVES.tsv"
    write_tsv(orientation_path, orientation, [
        "orientation_alternative_id", "instrument_id", "page", "alternative", "start_rule",
        "traversal_rule", "admissibility", "selected_orientation",
        "required_external_information", "cross_instrument_effect",
    ])

    instrument_rows: list[dict[str, object]] = []
    for instrument_id, instrument in INSTRUMENTS.items():
        instrument_rows.append({
            "instrument_id": instrument_id,
            "page": instrument["page"],
            "visible_instrument_kind": instrument["kind"],
            "bound_or_unresolved_namespaces": instrument["namespaces"],
            "group_assignment_status": instrument["assignment"],
            "technical_lookup_reading": instrument["technical"],
            "iatromedical_rival": instrument["medical"],
            "formal_iconographic_rival": instrument["formal"],
            "visible_basis": instrument["basis"],
            "orientation_alternatives": "|".join(row["alternative"] for row in orientation if row["instrument_id"] == instrument_id),
            "selected_start_or_direction": "NONE",
            "cross_instrument_join": "NONE",
            "hardest_contradiction": "No surface group supplies an externally anchored value; assignment, start, orientation, and content require the master exemplar.",
            "semantic_ceiling": "INSTRUMENT_CLASS_WORKING_MODEL_NOT_MEANING_OR_TRANSLATION",
        })
    instrument_path = OUT / "V75_R3_INSTRUMENT_COMPARISON.tsv"
    write_tsv(instrument_path, instrument_rows, [
        "instrument_id", "page", "visible_instrument_kind", "bound_or_unresolved_namespaces",
        "group_assignment_status", "technical_lookup_reading", "iatromedical_rival",
        "formal_iconographic_rival", "visible_basis", "orientation_alternatives",
        "selected_start_or_direction", "cross_instrument_join", "hardest_contradiction",
        "semantic_ceiling",
    ])

    report_path = OUT / "V75_R3_TECHNICAL_REPORT.md"
    lines = [
        "# V75 R3 — celestial multi-instrument third edition",
        "",
        "Status: kreative lokale Nachschlageedition, keine Entzifferung oder Übersetzung.",
        "",
        "## Ergebnis",
        "",
        "Alle **395 Astro-Gruppen** in **142 Loci** besitzen jetzt exakte Oberflächen-/Adressbindung, kleinsten V71-Besitzer, lokale Namespace, konkrete technische Lookuphandlung, Konfidenz, Quellenklasse, iatromedizinischen und formal-ikonographischen Rivalen sowie einen Widerspruch.",
        "",
        "Die Ausgabe ersetzt drei überholte V66-Abstraktionen: keine virtuelle seitenweite 7×12-Matrix auf f67r2, kein einziges Zentrum-plus-28-Objekt auf f68r1 und keine geordnete seitenweite 28-Regelfolge auf f69v. Die alten V69-Adressen bleiben nur als Auditkoordinaten erhalten.",
        "",
        "## Ausführbare Regel",
        "",
        "```text",
        "READ exact page + source locus + opaque surface group",
        "SET the smallest V71 local owner",
        "MAP owner to one page-local namespace",
        "OPEN only that namespace and copy the group as an opaque fragment",
        "IF owner unresolved: quarantine; do not select panel, centre, wheel, start or direction",
        "IF orientation requested: return every listed admissible alternative; select NONE",
        "ON namespace change: reset local lookup context",
        "REJECT f68<->f69 join, common direction, prose-card lookup and external semantic value",
        "```",
        "",
        "## f67r2 — zwei Räder, keine Matrix",
        "",
        "Die 74 Loci und 190 Gruppen werden auf ein linkes und ein rechtes Rad verteilt. Das rechte Rad besitzt lokale Sektor-, Scheiben-/Bedingungs-, Band- und Ringtextadressen. Das linke besitzt lokale Ring-/Radialfelder, zwölf äußere Sternplätze und eigenen Ringtext. Locus f67r2.74 bleibt eine quarantänisierte gemeinsame Legende. Kein gezeichneter Connector erlaubt eine Zelle aus einem linken und rechten Schlüssel; die alte virtuelle 7×12-Tafel ist damit vollständig zurückgezogen.",
        "",
        "## f68r1 — mehrere Paneele und Zentren",
        "",
        "Die 37 Loci und 65 Gruppen gehören zu drei Paneelköpfen, vier ungelösten Mehrpaneel-Fragmenten, einem ungelösten Zentrumsschlüssel, 28 direkt adressierten Sternloci und einer ungelösten Zentrallegende. Die Sternloci bilden einen editorischen lokalen Slotpool; ihre Zuordnung zu linkem, mittlerem oder rechtem Teilbild und zu mindestens fünf Gesichtsmedaillons bleibt offen. Es gibt kein page-weites Zentrum und keinen f69-Schlüssel.",
        "",
        "## f69v — drei Räder; 28 nur links",
        "",
        "Die 31 Loci und 140 Gruppen teilen sich in drei unverbundene Namespaces. Nur der linke enthält neben seinem Ringtext die 28 Loci f69v.4–f69v.31. Diese werden als ungeordnete direkt adressierte Slots U01–U28 geführt. Uhrzeigersinn, Gegenuhrzeigersinn, beliebiger Ursprung und Gegenüberpaarung sind ungewählte Alternativen. Das mittlere Wolken-/Wellenrad und das rechte Gesicht-/Strahlenrad besitzen ausschließlich ihre eigenen lokalen Ringtexte und erben keine 28er-Struktur.",
        "",
        "## Instrument- und Rivalenvergleich",
        "",
        "Neun sichtbare Instrumentklassen werden getrennt geführt: zwei f67-Räder, zwei offene f68-Sternfelder, eine sektorisierte f68-Teilkarte, eine Mehrzentrenmenge und drei f69-Räder. Die technische Lesung behandelt sie als direkte lokale Arbeits-, Kalender- oder Beobachtungsadressen. Der iatromedizinische Rivale liest Wahl-, Prognose- oder Sternstationen. Der formal-ikonographische Rivale liest statische Diagramme, Embleme und Legenden ohne ausführbare Quellwerte.",
        "",
        "## Orientierung bleibt offen",
        "",
        f"Die Orientierungstabelle enthält {len(orientation)} explizite Alternativen. Keine ist ausgewählt. Moderne Slotnummern sind ausschließlich editorische Auditadressen; sie sind weder Handschriftenanfang noch Nachbarschaftsbehauptung. Auch ein zulässiger Uhrzeigersinn erzeugt keine Ausrichtung zu einem anderen Instrument.",
        "",
        "## Grenze",
        "",
        "Die Edition macht die 395 Gruppen lokal ausführbar, weil ein Werkstattschreiber nur Bildbesitzer, Quelllocus und Exemplarfragment braucht. Sie gewinnt dadurch keine konkrete Himmelsbedeutung. Weder Sternname, Planet, Tierkreiszeichen, Datum, Körperteil, Prognose, Arbeitsregel noch Kartenwert wird aus einer Oberfläche gelesen.",
        "",
        "Keine Prosa-Karte, kein Stamm, Laut, Wort, POS, Sprache oder Klartext wurde ergänzt. f84 und f84r blieben versiegelt.",
        "",
    ]
    report_path.write_text("\n".join(lines), encoding="utf-8")

    source_paths = [GROUP_SOURCE, FINAL_GROUP_SOURCE, LOCUS_SOURCE, OWNER_SOURCE, IMAGE_SOURCE, CONTINUITY_SOURCE]
    output_paths = [group_path, locus_path, namespace_path, orientation_path, instrument_path, report_path]
    summary = {
        "experiment": "V75_R3_CELESTIAL_MULTI_INSTRUMENT_THIRD_EDITION",
        "status": "CREATIVE_EXECUTABLE_LOCAL_LOOKUP_NOT_DECIPHERMENT",
        "counts": {
            "groups": len(group_rows),
            "loci": len(locus_rows),
            "namespaces": len(namespace_rows),
            "orientation_alternatives": len(orientation),
            "instruments": len(instrument_rows),
            "f67_groups": sum(row["page"] == "f67r2" for row in group_rows),
            "f68_groups": sum(row["page"] == "f68r1" for row in group_rows),
            "f69_groups": sum(row["page"] == "f69v" for row in group_rows),
            "f69_left_unordered_slots": sum(row["page"] == "f69v" and 4 <= locus_number(str(row["source_locus"])) <= 31 for row in locus_rows),
        },
        "pages": sorted({str(row["page"]) for row in group_rows}),
        "source_hashes": {str(path.relative_to(ROOT)): sha256(path) for path in source_paths},
        "output_hashes": {path.name: sha256(path) for path in output_paths},
        "selected_orientation": "NONE",
        "crosspage_mapping": "NONE",
        "prose_card_values": "NONE",
        "sealed": ["f84", "f84r"],
        "semantic_ceiling": "NO_CARD_STEM_SOUND_LANGUAGE_MEANING_OR_TRANSLATION_PROMOTION",
    }
    (OUT / "V75_R3_BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    build()

#!/usr/bin/env python3
"""Build the complete V71 R1 image-to-text owner ledger.

This bounded creative sidequest tool consumes only the frozen V69 field/Astro
ledgers and writes anonymous visible-owner defaults. It does not inspect image
files, infer card semantics, or touch material outside the ten-page panel.
"""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUTDIR = Path(__file__).resolve().parent
FIELD_SOURCE = ROOT / "experiments/yolo/sidequest_theory_candidates_v69/V69_R4_FINAL_135_FIELD_EDITION.tsv"
ASTRO_SOURCE = ROOT / "experiments/yolo/sidequest_theory_candidates_v69/V69_R4_FINAL_395_ASTRO_GROUPS.tsv"
OWNER_OUT = OUTDIR / "V71_R1_OWNER_LEDGER.tsv"
REVISION_OUT = OUTDIR / "V71_R1_REVISIONS.tsv"
VALIDATION_OUT = OUTDIR / "V71_R1_VALIDATION.json"

PAGES = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"}
ALLOWED_STATUS = {"DIRECT_VISIBLE", "INHERITED_VISIBLE", "PAGE_OWNER_ONLY", "UNRESOLVED"}
FIELDNAMES = [
    "owner_row",
    "unit_kind",
    "unit_id",
    "page",
    "section",
    "record_or_diagram",
    "source_locus",
    "member_count",
    "v69_formal_role",
    "ownership_status",
    "smallest_visible_owner",
    "silent_argument_default",
    "strongest_rival",
    "confidence",
    "v69_must_change",
    "change_reason",
    "revision_family",
    "semantic_ceiling",
]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def field_spec(row: dict[str, str]) -> dict[str, str]:
    fid = row["field_id"]
    num = int(fid[1:])
    page = row["page"]
    locus = row["locus"]

    herbal: dict[str, tuple[str, str, str, str, str, str]] = {
        "F001": ("DIRECT_VISIBLE", "PLANT_10_ROOTSTOCK", "Der ausgelassene Besitzer ist der sichtbare untere Wurzelstock von PLANT_10; das Verfahren bleibt EXEMPLAR_VALUE_UNKNOWN.", "PLANT_10_WHOLE_PLANT", "MEDIUM", "H_ROOT"),
        "F002": ("INHERITED_VISIBLE", "PLANT_10_ROOTSTOCK", "Führe denselben recordlokalen Wurzelstockbesitzer aus F001 fort; ein Rest oder Auszug ist nur Exemplarinhalt.", "PLANT_10_WHOLE_PLANT", "MEDIUM", "H_ROOT"),
        "F003": ("DIRECT_VISIBLE", "PLANT_10_OPEN_HEAD_AND_UPPER_LEAF_TIER", "Der neue H2-Posten nimmt den offenen Kopf samt oberem Blattbereich als sichtbaren Teilbesitzer.", "PLANT_10_WHOLE_PLANT", "MEDIUM", "H_HEADS"),
        "F004": ("DIRECT_VISIBLE", "PLANT_10_CLOSED_BUD_OR_UPPER_TIP", "Der zweite H2-Posten nimmt die sichtbar geschlossene Knospe beziehungsweise obere Spitze als Gegenstück.", "PLANT_10_OPEN_HEAD", "MEDIUM", "H_HEADS"),
        "F005": ("INHERITED_VISIBLE", "PLANT_10_TWO_HEAD_STAGE_SET", "Der Abschluss führt die beiden zuvor gesetzten sichtbaren Kopf- oder Stufenbesitzer gemeinsam; Mischung und Produkt bleiben unbekannt.", "PLANT_10_WHOLE_PLANT", "LOW", "H_HEADS"),
        "F006": ("DIRECT_VISIBLE", "PLANT_11_FLOWERLET_SET_AND_CANOPY", "Der Artikel eröffnet die sichtbare blaue Blütenkopfmenge mit ihrer dichten Krone als Teilbesitzer.", "PLANT_11_WHOLE_PLANT", "MEDIUM", "H_CANOPY"),
        "F007": ("DIRECT_VISIBLE", "PLANT_11_FLOWERLET_SET", "Eine nicht weiter identifizierte Teilmenge der sichtbaren blauen Köpfe wird zurückgestellt.", "PLANT_11_CANOPY", "MEDIUM", "H_CANOPY"),
        "F008": ("INHERITED_VISIBLE", "PLANT_11_CANOPY_DERIVED_PORTION", "Nimm den im selben Record eröffneten Kronenposten wieder auf; Gefäß und Produkt bleiben exemplarabhängig.", "PLANT_11_FLOWERLET_SET", "LOW", "H_CANOPY"),
        "F009": ("INHERITED_VISIBLE", "PLANT_11_RESERVED_FLOWERLET_PORTION", "Führe die in F007 reservierte sichtbare Blütenkopfportion als stilles Argument fort.", "PLANT_11_CANOPY", "MEDIUM", "H_CANOPY"),
        "F010": ("DIRECT_VISIBLE", "PLANT_55_BROAD_LEAF_MASS", "Der erste Posten gehört der großen sichtbaren Blattmasse; Medium und Verarbeitung bleiben unbekannt.", "PLANT_55_WHOLE_PLANT", "HIGH", "H_LEAF"),
        "F011": ("INHERITED_VISIBLE", "PLANT_55_BROAD_LEAF_MASS", "Führe den Blattmassenposten aus F010 als aktuelles stilles Argument fort.", "PLANT_55_INFLORESCENCE", "MEDIUM", "H_LEAF"),
        "F012": ("INHERITED_VISIBLE", "PLANT_55_PREVIOUS_LEAF_PORTION", "Der Gebrauch bezieht sich auf die zuvor eröffnete Blattportion; Ziel und Zweck sind nicht sichtbar.", "PLANT_55_WHOLE_PLANT", "LOW", "H_LEAF"),
        "F013": ("UNRESOLVED", "UNRESOLVED_PLANT_55_PART_RELATION", "Das Masterexemplar muss entscheiden, ob Blattmasse, obere Krone oder beide gemeint sind.", "PLANT_55_WHOLE_PLANT", "LOW", "H_LEAF"),
        "F014": ("DIRECT_VISIBLE", "PLANT_56_WHOLE_PLANT", "Der Artikelbesitzer ist die ganze schematische Pflanze PLANT_56.", "PLANT_56_DOMINANT_HEAD", "HIGH", "H_SCHEMATIC"),
        "F015": ("PAGE_OWNER_ONLY", "PLANT_56_WHOLE_PLANT", "Ohne Bildzeiger gilt die aktuelle unbekannte Portion der ganzen PLANT_56 als stilles Argument.", "PLANT_56_LOWER_RADIAL_HEAD", "LOW", "H_SCHEMATIC"),
        "F016": ("INHERITED_VISIBLE", "PLANT_56_CURRENT_PORTION", "Führe die in F015 recordlokal gesetzte Pflanzenportion fort; Anwendung und Ziel bleiben unbekannt.", "PLANT_56_WHOLE_PLANT", "LOW", "H_SCHEMATIC"),
        "F017": ("DIRECT_VISIBLE", "PLANT_56_SECONDARY_HEAD_SET", "Der neue Posten nimmt die sichtbar kleineren Seitenköpfe als Besitzergruppe.", "PLANT_56_DOMINANT_SPIRAL_HEAD", "MEDIUM", "H_SCHEMATIC"),
        "F018": ("INHERITED_VISIBLE", "PLANT_56_SECONDARY_HEAD_SET", "Führe die Seitenkopfportion aus F017 fort; Lagerung oder Medium bleiben unbekannt.", "PLANT_56_BASAL_SHOOT", "LOW", "H_SCHEMATIC"),
        "F019": ("INHERITED_VISIBLE", "PLANT_56_SECONDARY_HEAD_DERIVED_PORTION", "Der aktuelle Posten stammt recordlokal aus F017/F018; Produkt und Gebrauch bleiben exemplarabhängig.", "PLANT_56_WHOLE_PLANT", "LOW", "H_SCHEMATIC"),
        "F020": ("DIRECT_VISIBLE", "PLANT_56_SELECTED_HEAD_SET", "Wähle eine im Masterexemplar bezeichnete sichtbare Kopfportion; der dominante Spiral- oder ein Nebenkopf bleibt die stärkste Alternative.", "PLANT_56_DOMINANT_SPIRAL_HEAD", "MEDIUM", "H_SCHEMATIC"),
    }
    if page in {"f10r", "f11r", "f55v", "f56r"}:
        status, owner, default, rival, confidence, family = herbal[fid]
        return make_spec(status, owner, default, rival, confidence, family, "YES", "V70 zieht enge Art-, Zubereitungs- und Gebrauchswerte auf sichtbare Pflanzenteile oder Exemplarinhalt zurück.")

    if page == "f81v":
        status = "PAGE_OWNER_ONLY" if fid == "F021" else "INHERITED_VISIBLE"
        return make_spec(
            status,
            "F81V_SHARED_TWO_TIER_FIGURE_POOL",
            "Das ausgelassene Argument ist die gemeinsame zweireihige Figuren-Einfassung; die aktuelle Figurstation wird nur aus dem Masterexemplar gewählt, Stoff und Richtung bleiben unbekannt.",
            "F81V_TWO_TIER_FORMAL_TABLEAU",
            "HIGH" if fid == "F021" else "MEDIUM",
            "B81_SHARED",
            "YES",
            "V69s globaler Wärmestellen-, Rinnen- und Rücklaufbesitzer wird durch einen einzigen sichtbaren gemeinsamen Figurenpool ersetzt.",
        )

    if page == "f82r":
        mapping = {
            "f82r.2": ("F82R_UPPER_PAIRED_ARC_AND_CYLINDER_ASSEMBLY", "B82_UPPER", "F045"),
            "f82r.3": ("F82R_UPPER_PAIRED_ARC_AND_CYLINDER_ASSEMBLY", "B82_UPPER", None),
            "f82r.4": ("F82R_UPPER_PAIRED_ARC_AND_CYLINDER_ASSEMBLY", "B82_UPPER", None),
            "f82r.7": ("F82R_MIDLEFT_HAND_DEVICE_AND_WAVY_STRANDS", "B82_MIDLEFT", "F053"),
            "f82r.19": ("F82R_RECLINING_FIGURE_FUNNEL_VESSEL", "B82_RECLINING", "F057"),
            "f82r.23": ("F82R_LOWER_IRREGULAR_FIGURE_POOL", "B82_LOWER", "F059"),
            "f82r.26": ("F82R_LOWER_IRREGULAR_FIGURE_POOL", "B82_LOWER", None),
            "f82r.27": ("F82R_LOWER_IRREGULAR_FIGURE_POOL", "B82_LOWER", None),
        }
        owner, family, direct_fid = mapping[locus]
        status = "DIRECT_VISIBLE" if fid == direct_fid else "INHERITED_VISIBLE"
        return make_spec(
            status,
            owner,
            f"Das aktuelle Feld führt {owner} als lokalen Szenenbesitzer; nur seine sichtbaren Kontakte gelten, eine Fließrichtung oder Verbindung zu anderen Vignetten nicht.",
            "F82R_PAGE_LEVEL_STATION_ATLAS",
            "MEDIUM",
            family,
            "YES",
            "V69s lineare Filter-Abfluss-Maschine wird in voneinander getrennte Bildstationen zerlegt.",
        )

    if page == "f83r":
        unresolved_loci = {"f83r.47", "f83r.48", "f83r.49", "f83r.52", "f83r.54"}
        if locus in unresolved_loci:
            family = "B83_TAIL_B5" if row["record_unit_id"] == "B5" else "B83_TAIL_B6"
            return make_spec(
                "UNRESOLVED",
                "UNRESOLVED_AMONG_F83R_LOCAL_FIGURE_VESSELS",
                "Das Masterexemplar benennt eine lokale f83r-Szene; aus dem Bild allein ist für diesen Nachtrag keine einzelne Szene auswählbar.",
                "F83R_RIGHT_S_CONDUIT_AND_HUB_ASSEMBLY",
                "LOW",
                family,
                "YES",
                "Die B5/B6-Nachträge besitzen keinen belastbaren eigenen Bildanker; V69s Übergabe- und Kaltbecken sind erfunden.",
            )
        chunks = [
            ({"f83r.3", "f83r.6", "f83r.8"}, "F83R_UPPER_MARGIN_FIGURE_VESSEL_SERIES", "B83_UPPER", "F071", "PAGE_OWNER_ONLY"),
            ({"f83r.11", "f83r.14", "f83r.15", "f83r.16"}, "F83R_MIDDLE_LOCAL_FIGURE_VESSEL_SERIES", "B83_MIDDLE", "F082", "PAGE_OWNER_ONLY"),
            ({"f83r.20", "f83r.22", "f83r.24"}, "F83R_ARCH_LINKED_LOWER_PAIR", "B83_ARCH", "F099", "DIRECT_VISIBLE"),
            ({"f83r.25", "f83r.26", "f83r.27", "f83r.28"}, "F83R_LEFT_DESCENDING_BLUE_CHANNEL_ASSEMBLY", "B83_LEFT", "F109", "DIRECT_VISIBLE"),
            ({"f83r.35", "f83r.37", "f83r.38", "f83r.39", "f83r.41", "f83r.44"}, "F83R_RIGHT_S_CONDUIT_AND_MULTIENDED_HUB", "B83_RIGHT", "F120", "DIRECT_VISIBLE"),
        ]
        for loci, owner, family, first_fid, first_status in chunks:
            if locus in loci:
                status = first_status if fid == first_fid else "INHERITED_VISIBLE"
                return make_spec(
                    status,
                    owner,
                    f"Führe {owner} als aktuellen lokalen Besitzer; nutze nur gezeichnete Berührung, nie Wärme, Filter oder Richtung als Bildwert.",
                    "F83R_MULTISCENE_PAGE_OWNER",
                    "MEDIUM" if "SERIES" not in owner else "LOW",
                    family,
                    "YES",
                    "V69s einheitliches C/W/L/F/U/R-Netz wird durch die kleinste sichtbare lokale Verbindung ersetzt.",
                )
        raise AssertionError((fid, locus))

    raise AssertionError((fid, page, num))


def astro_spec(page: str, locus: str) -> dict[str, str]:
    n = int(locus.rsplit(".", 1)[1])
    if page == "f67r2":
        if 1 <= n <= 12:
            return make_spec("INHERITED_VISIBLE", f"F67_LEFT_RADIAL_OUTER_SECTOR_{n:02d}", "Der opake Eintrag gehört dem gleich nummerierten sichtbaren Außensektor des linken Rades; sein Inhalt bleibt unbekannt.", "F67_RIGHT_CONCENTRIC_RING_STATION", "MEDIUM", "A67_LEFT_SECTORS", "YES", "Die 12er-Serie bleibt lokal am linken Rad statt Teil einer behaupteten 7-mal-12-Matrix zu sein.")
        if n in {13, 14}:
            return make_spec("DIRECT_VISIBLE", "F67_LEFT_UPPER_PROSE_BLOCK", "Der Eintrag gehört zum sichtbaren oberen Prosablock und gilt als Gebrauchshinweis für das linke oder das gepaarte Rad.", "F67_LEFT_RADIAL_RING_TEXT", "MEDIUM", "A67_LEFT_PROSE", "YES", "Der Text wird als lokaler Prosabesitzer statt als semantisch gelesene Lookup-Anweisung geführt.")
        if 15 <= n <= 51:
            row_keys = {15: 1, 22: 2, 28: 3, 31: 4, 34: 5, 37: 6, 47: 7}
            if n in row_keys:
                idx = row_keys[n]
                return make_spec("INHERITED_VISIBLE", f"F67_LEFT_RADIAL_INNER_STATION_{idx:02d}", "Der kurze Eintrag gehört einer wiederholten inneren Station des linken Rades; der Stationswert ist EXEMPLAR_VALUE_UNKNOWN.", "F67_PAIRED_WHEELS_PAGE_OWNER", "LOW", "A67_LEFT_INNER", "YES", "Der alte Planetenreihenwert wird durch eine anonyme lokale Radstation ersetzt.")
            return make_spec("PAGE_OWNER_ONLY", "F67_PAIRED_CELESTIAL_WHEELS", "Der Text ist ein seitenlokaler Gebrauch- oder Ringtext; das Masterexemplar entscheidet, welchem der beiden Räder er im Detail gehört.", "F67_LEFT_RADIAL_DIAGRAM", "LOW", "A67_PAGE_TEXT", "YES", "Die alte 7-mal-12-Instruktionssemantik besitzt keine eindeutige sichtbare Teilzuweisung.")
        if 52 <= n <= 63:
            idx = n - 51
            return make_spec("INHERITED_VISIBLE", f"F67_RIGHT_CONCENTRIC_OUTER_SECTOR_{idx:02d}", "Der opake Eintrag gehört dem entsprechenden Außensektor des rechten konzentrischen Rades.", "F67_LEFT_RADIAL_OUTER_SECTOR", "MEDIUM", "A67_RIGHT_SECTORS", "YES", "Die alte Häuserliste wird als anonyme 12er-Sektorserie im rechten Rad geführt.")
        if 64 <= n <= 71:
            idx = n - 63
            return make_spec("INHERITED_VISIBLE", f"F67_RIGHT_DISK_OR_CRESCENT_STATION_{idx:02d}", "Der opake Eintrag gehört einer sichtbaren Scheiben- oder Sichelstation des rechten Rades; keine Bedingungsbedeutung wird übernommen.", "F67_RIGHT_RING_TEXT", "MEDIUM", "A67_RIGHT_STATIONS", "YES", "Die alten acht Wahlbedingungen werden zu anonymen sichtbaren Stationen.")
        if 72 <= n <= 74:
            idx = n - 71
            return make_spec("DIRECT_VISIBLE", f"F67_RIGHT_LOWER_PROSE_LINE_{idx:02d}", "Der Eintrag gehört zum sichtbaren dreizeiligen Prosablock unter dem rechten Rad und trägt einen lokalen Gebrauchshinweis unbekannten Inhalts.", "F67_RIGHT_OUTER_RING_TEXT", "HIGH", "A67_RIGHT_PROSE", "YES", "Die lange medizinische Anweisung wird nur noch als sichtbarer Prosaort geführt.")

    if page == "f68r1":
        if 1 <= n <= 3:
            return make_spec("DIRECT_VISIBLE", "F68_LEFT_STAR_FIELD_HEADER", "Der Eintrag gehört zum sichtbaren Kopfblock über dem linken offenen Sternfeld.", "F68_CENTRE_STAR_FIELD_HEADER", "MEDIUM", "A68_HEADERS", "YES", "Der alte einheitliche Katalogkopf wird panel-lokal gebunden.")
        if 4 <= n <= 7:
            return make_spec("DIRECT_VISIBLE", "F68_CENTRE_STAR_FIELD_HEADER", "Der Eintrag gehört zum sichtbaren Kopfblock über dem mittleren offenen Sternfeld.", "F68_LEFT_STAR_FIELD_HEADER", "MEDIUM", "A68_HEADERS", "YES", "Der alte einheitliche Katalogkopf wird panel-lokal gebunden.")
        if n == 8:
            return make_spec("UNRESOLVED", "UNRESOLVED_FACE_DISK_AMONG_F68_FIVE_CENTRES", "Das Masterexemplar muss den gemeinten Gesichtsmittelpunkt wählen; das Bild besitzt mehrere gleichartige Zentren.", "F68_RIGHT_RADIAL_FACE_DISK", "LOW", "A68_CENTRE_AMBIG", "YES", "Ein einziger Mondbesitzer ist auf der Multipanel-Seite nicht sichtbar.")
        if 9 <= n <= 36:
            idx = n - 8
            return make_spec("DIRECT_VISIBLE", f"F68_STAR_STATION_AT_SOURCE_POSITION_{idx:02d}", "Das lokale Label übernimmt die unmittelbar bei seiner Quellposition gezeichnete Sternstation als stillen Adressbesitzer; Panel und Bedeutung bleiben im Exemplar.", "F68_PANEL_LEVEL_STAR_FIELD", "MEDIUM", "A68_STATIONS", "YES", "Die 28 alten Mondhauswerte werden zu 28 anonymen quellpositionsgebundenen Sternadressen ohne behauptetes Ein-Zentrum-System.")
        if n == 37:
            return make_spec("PAGE_OWNER_ONLY", "F68_MULTIPANEL_STAR_ATLAS_LEGEND", "Der Legendentext gehört dem Multipanel-Sternatlas; welcher Gesichtsmittelpunkt ihn lokal besitzt, bleibt offen.", "F68_RIGHT_RADIAL_DIAGRAM_RING", "LOW", "A68_LEGEND", "YES", "Die alte zentrale Mondlegende wird als seitenweite anonyme Legende geführt.")

    if page == "f69v":
        if n == 1:
            return make_spec("DIRECT_VISIBLE", "F69_UPPER_RIGHT_PROSE_BLOCK", "Der Eintrag ist der sichtbare Prosahinweis für die Drei-Räder-Tafel; seine genaue Reichweite bleibt seitenlokal.", "F69_LEFT_SPOKE_DIAGRAM_OUTER_RING", "MEDIUM", "A69_PROSE", "YES", "Das erste alte Regelband wird an den separaten Prosablock statt an eine 28er-Regelkette gebunden.")
        if n == 2:
            return make_spec("DIRECT_VISIBLE", "F69_MIDDLE_LOBED_DIAGRAM_RING_TEXT", "Der Eintrag gehört dem Ringtext des mittleren Lappenrades.", "F69_RIGHT_FACE_PETAL_RING_TEXT", "MEDIUM", "A69_MIDDLE_RING", "YES", "Das zweite alte Regelband wird ein anonymer lokaler Ringtext.")
        if n == 3:
            return make_spec("DIRECT_VISIBLE", "F69_RIGHT_FACE_PETAL_DIAGRAM_RING_TEXT", "Der Eintrag gehört dem Ringtext des rechten Gesicht-Blatt-Rades.", "F69_MIDDLE_LOBED_RING_TEXT", "MEDIUM", "A69_RIGHT_RING", "YES", "Das dritte alte Regelband wird ein anonymer lokaler Ringtext.")
        if 4 <= n <= 31:
            idx = n - 3
            return make_spec("DIRECT_VISIBLE", f"F69_LEFT_SPOKE_RADIAL_PLACE_{idx:02d}", "Der Eintrag gehört genau dem lokalen radialen Platz am linken Speichenrad; Karten-, Medizin- und Operationswert bleiben unbekannt.", "F69_LOCAL_ANNOTATION_WITHOUT_RULE_STATUS", "HIGH", "A69_LEFT_28", "YES", "Die 28 alten medizinischen Regeln werden zu einer lokalen anonymen 28-Platz-Inventur ohne gemeinsamen Start oder Richtung.")

    raise AssertionError((page, locus, n))


def make_spec(status: str, owner: str, default: str, rival: str, confidence: str, family: str, must_change: str, reason: str) -> dict[str, str]:
    return {
        "ownership_status": status,
        "smallest_visible_owner": owner,
        "silent_argument_default": default,
        "strongest_rival": rival,
        "confidence": confidence,
        "revision_family": family,
        "v69_must_change": must_change,
        "change_reason": reason,
    }


REVISION_TEXT = {
    "H_ROOT": ("specific plant name plus distilled root-water process", "anonymous PLANT_10 rootstock owner", "The root is visible; plant name, water and apparatus are not."),
    "H_HEADS": ("two named therapeutic flower fractions", "open-head versus closed-bud visible part set", "The two visible stages are economical owners, but product and use remain exemplar values."),
    "H_CANOPY": ("violet remedies and products", "PLANT_11 flowerlet/canopy portions", "A flower-rich canopy is visible; species and remedy are not."),
    "H_LEAF": ("Allium-like leaf processing and wound use", "PLANT_55 leaf mass with unresolved part relation", "Broad leaves and crown are visible; medium and use are not."),
    "H_SCHEMATIC": ("sundew skin and chest preparations", "PLANT_56 whole plant and head sets", "The schematic plant supports parts but no named species or therapy."),
    "B81_SHARED": ("one directed thermal circulation network", "shared two-tier figure pool or tableau", "One dominant common enclosure is visible; flow and substance are absent."),
    "B82_UPPER": ("fields in one global f82 process", "upper paired arc/cylinder assembly", "This local assembly is connected internally but not to the lower page."),
    "B82_MIDLEFT": ("global machine continuation", "middle-left hand/device station", "A local contact and strand device exists without page-wide pipe continuity."),
    "B82_RECLINING": ("global machine continuation", "reclining figure funnel-vessel", "The reclining scene is separately bounded."),
    "B82_LOWER": ("global filter/drain/refill network", "lower irregular shared figure pool", "The lower green field is a local owner and is not connected to every upper vignette."),
    "B83_UPPER": ("global C/W/L/F/U/R network", "upper marginal figure-vessel series", "Several local scenes exist; precise field-to-scene binding is weak."),
    "B83_MIDDLE": ("global C/W/L/F/U/R network", "middle figure-vessel series", "Several local scenes exist; precise field-to-scene binding is weak."),
    "B83_ARCH": ("directed main-basin cycle", "arch-linked lower pair", "The pair is visibly connected, but direction and contents are not."),
    "B83_LEFT": ("filter/return subsystem", "left descending blue-channel assembly", "The channel is visible; filter and direction are not."),
    "B83_RIGHT": ("filter/return subsystem", "right S-conduit and multi-ended hub", "The connection is visible; inlet, outlet and use are not."),
    "B83_TAIL_B5": ("warm transfer basin E", "unresolved local f83 scene", "No unique B5 image anchor survives."),
    "B83_TAIL_B6": ("cold filter basin F", "unresolved local f83 scene", "No unique B6 image anchor survives."),
    "A67_LEFT_SECTORS": ("12 semantic zodiac columns", "12 anonymous left-wheel sectors", "The local sector series is visible; zodiac values are not."),
    "A67_LEFT_PROSE": ("medical lookup instructions", "left upper prose block", "Prose placement is visible; instruction meaning is not."),
    "A67_LEFT_INNER": ("seven named planetary rows", "seven anonymous inner stations", "Repeated stations may be retained without planetary labels."),
    "A67_PAGE_TEXT": ("medical lookup clauses", "paired-wheel page text", "The exact subwheel owner cannot be reconstructed from the frozen table."),
    "A67_RIGHT_SECTORS": ("12 named astrological houses", "12 anonymous right-wheel sectors", "The sector series is visible; house meanings are not."),
    "A67_RIGHT_STATIONS": ("eight named election checks", "eight anonymous disk/crescent stations", "Visible station topology does not identify conditions."),
    "A67_RIGHT_PROSE": ("medical election instruction", "right lower prose block", "The three prose lines are visible; their semantics are not."),
    "A68_HEADERS": ("one catalogue header", "panel-local star-field headers", "The sheet has multiple panels and header blocks."),
    "A68_CENTRE_AMBIG": ("one lunar centre", "unresolved among five face centres", "The visible sheet has multiple face disks."),
    "A68_STATIONS": ("28 named lunar mansions around one centre", "28 anonymous source-position star stations", "Addresses survive, names and one-centre geometry do not."),
    "A68_LEGEND": ("one central lunar legend", "multipanel atlas legend", "No unique centre owns the legend visibly."),
    "A69_PROSE": ("first rule band", "separate upper-right prose block", "The prose is outside the three wheels."),
    "A69_MIDDLE_RING": ("second rule band", "middle lobed-wheel ring text", "The wheel is a local namespace."),
    "A69_RIGHT_RING": ("third rule band", "right face-petal-wheel ring text", "The wheel is a local namespace."),
    "A69_LEFT_28": ("28 ordered medical or technical rules", "28 anonymous places on the left spoke wheel", "Only a local 28-place inventory survives the image."),
}


def build() -> dict[str, object]:
    fields = read_tsv(FIELD_SOURCE)
    astro_groups = read_tsv(ASTRO_SOURCE)
    rows: list[dict[str, str]] = []

    for source in fields:
        spec = field_spec(source)
        rows.append({
            "unit_kind": "PROSE_FIELD",
            "unit_id": source["field_id"],
            "page": source["page"],
            "section": "HERBAL" if source["page"] in {"f10r", "f11r", "f55v", "f56r"} else "BIOLOGICAL",
            "record_or_diagram": source["record_unit_id"],
            "source_locus": source["locus"],
            "member_count": source["event_count"],
            "v69_formal_role": source["primary_template"] or source["parse_status"],
            **spec,
            "semantic_ceiling": "VISIBLE_OWNER_DEFAULT_NOT_CARD_OR_STEM_MEANING",
        })

    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    order: list[tuple[str, str]] = []
    for source in astro_groups:
        key = (source["page"], source["locus"])
        if key not in grouped:
            order.append(key)
        grouped[key].append(source)
    for page, locus in order:
        members = grouped[(page, locus)]
        spec = astro_spec(page, locus)
        roles = sorted({m["local_formal_role"] for m in members})
        rows.append({
            "unit_kind": "ASTRO_LOCUS",
            "unit_id": f"ASTRO:{page}:{locus}",
            "page": page,
            "section": "ASTRO",
            "record_or_diagram": members[0]["diagram_id"],
            "source_locus": locus,
            "member_count": str(len(members)),
            "v69_formal_role": "|".join(roles),
            **spec,
            "semantic_ceiling": "VISIBLE_OWNER_DEFAULT_NOT_CARD_OR_STEM_MEANING",
        })

    for index, row in enumerate(rows, 1):
        row["owner_row"] = f"OWN{index:03d}"

    with OWNER_OUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    family_counts = Counter(row["revision_family"] for row in rows)
    revision_fields = ["revision_id", "revision_family", "affected_units", "v69_owner_or_default", "v71_visible_owner_or_default", "reason", "formal_ids_changed", "semantic_status"]
    with REVISION_OUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=revision_fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for index, family in enumerate(sorted(family_counts), 1):
            old, new, reason = REVISION_TEXT[family]
            writer.writerow({
                "revision_id": f"REV{index:02d}",
                "revision_family": family,
                "affected_units": family_counts[family],
                "v69_owner_or_default": old,
                "v71_visible_owner_or_default": new,
                "reason": reason,
                "formal_ids_changed": "NO",
                "semantic_status": "CREATIVE_VISIBLE_OWNER_ONLY",
            })

    status_counts = Counter(row["ownership_status"] for row in rows)
    page_counts = Counter(row["page"] for row in rows)
    checks = {
        "owner_rows_277": len(rows) == 277,
        "prose_fields_135": sum(r["unit_kind"] == "PROSE_FIELD" for r in rows) == 135,
        "astro_loci_142": sum(r["unit_kind"] == "ASTRO_LOCUS" for r in rows) == 142,
        "prose_events_381": sum(int(r["member_count"]) for r in rows if r["unit_kind"] == "PROSE_FIELD") == 381,
        "astro_groups_395": sum(int(r["member_count"]) for r in rows if r["unit_kind"] == "ASTRO_LOCUS") == 395,
        "unit_ids_unique": len({r["unit_id"] for r in rows}) == len(rows),
        "owner_rows_unique": len({r["owner_row"] for r in rows}) == len(rows),
        "exact_fixed_pages": set(page_counts) == PAGES,
        "statuses_allowed": set(status_counts) <= ALLOWED_STATUS,
        "required_text_nonempty": all(r["smallest_visible_owner"] and r["silent_argument_default"] and r["strongest_rival"] and r["confidence"] for r in rows),
        "all_v69_creative_defaults_audited": all(r["v69_must_change"] in {"YES", "NO"} for r in rows),
        "herbal_trace_h2_complete": {r["unit_id"] for r in rows if r["record_or_diagram"] == "H2"} == {"F003", "F004", "F005"},
        "bio_trace_b2_complete": len([r for r in rows if r["record_or_diagram"] == "B2"]) == 26,
        "astro_trace_f69_complete": len([r for r in rows if r["page"] == "f69v" and r["unit_kind"] == "ASTRO_LOCUS"]) == 31,
        "no_sealed_page": not any(r["page"].lower().startswith("f84") for r in rows),
    }
    validation = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "counts": {
            "owner_rows": len(rows),
            "unit_kind": dict(sorted(Counter(r["unit_kind"] for r in rows).items())),
            "ownership_status": dict(sorted(status_counts.items())),
            "page": dict(sorted(page_counts.items())),
            "revision_families": len(family_counts),
        },
        "source_sha256": {FIELD_SOURCE.name: digest(FIELD_SOURCE), ASTRO_SOURCE.name: digest(ASTRO_SOURCE)},
        "output_sha256": {OWNER_OUT.name: digest(OWNER_OUT), REVISION_OUT.name: digest(REVISION_OUT)},
        "ceiling": "Complete creative visible-owner map; no card, stem, word, language, or translation value established.",
    }
    VALIDATION_OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return validation


if __name__ == "__main__":
    result = build()
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["status"] == "PASS" else 1)

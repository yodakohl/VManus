#!/usr/bin/env python3
"""Build the score-blind GDT337 external-homologue census.

This program deliberately reads no Voynich transcription, PAGE_HOST, HPR2,
joint-tuple, source-member, or source-family value.  Voynich inputs are limited
to previously published text-blind topology/capacity artifacts.
"""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
sys.path.insert(0, str(ROOT))

from tools.vmanus_experiment import GuardedTSV, canonical_json_bytes, sha256_file  # noqa: E402


EXP = ROOT / "experiments/yolo/gdt337_external_homologue_census"
ART = EXP / "artifacts"
SC = ROOT / "experiments/semantic_assumptions/results/special_circle_text_blind_array_inventory.tsv"
ZODIAC = ROOT / "experiments/semantic_assumptions/results/zodiac_crosssign_phase_capacity.json"
F69 = ROOT / "experiments/semantic_assumptions/results/f69vsd001_start_direction_result.json"
PAIR105 = ROOT / "experiments/semantic_assumptions/results/special_circle_10_to_5_pairing_worth.json"
KART_MANIFEST = ROOT / "kart001_a65_comparator_manifest.tsv"
KART_GENERIC = ROOT / "kart001_generic_medieval_comparators.tsv"
FDTW = ROOT / "experiments/semantic_assumptions/results/fdtw_f57_homologue_metadata_prescreen.tsv"


INPUTS = [SC, ZODIAC, F69, PAIR105, KART_MANIFEST, KART_GENERIC, FDTW]


EXTERNAL_SOURCES = [
    {
        "source_id": "EXT001_BL_ADD_MS_25435",
        "manuscript_id": "London, British Library, Add MS 25435",
        "date_region": "1345-1355; German",
        "source_type": "OFFICIAL_LIBRARY_CATALOGUE",
        "source_url": "https://searcharchives.bl.uk/catalog/032-002029758",
        "bibliographic_reference": "British Library Archives and Manuscripts Catalogue, Add MS 25435",
        "supporting_statement": "A wheel on the upper cover has Roman numerals I-XXVIII for 28 lunar mansions and a movable pointing figure; 28 named prophet records occupy ff.3r-16v.",
        "readable_slot_values": "YES",
        "fixed_start": "YES_NUMERALS",
        "fixed_order": "YES_I_TO_XXVIII",
        "one_to_one_ownership": "YES_WHEEL_NUMBER_TO_RECORD",
        "topology": "NUMBERED_CIRCULAR_28_WITH_POINTER",
        "voynich_target_family": "F69V_28;F68R1_28_NONCENTRAL",
        "source_status": "SOURCE_VERIFIED",
    },
    {
        "source_id": "EXT002_A65_28_NIGHTS",
        "manuscript_id": "Tbilisi, National Centre of Manuscripts, A-65",
        "date_region": "1188-1210; Georgian translation of Arabic astrological tract",
        "source_type": "SCHOLARLY_EDITION_AND_CATALOGUE",
        "source_url": "https://titus.uni-frankfurt.de/texte/etcs/cauc/ageo/etlta/etltat.htm",
        "bibliographic_reference": "A. Shanidze (ed.), Eṭlta da šwdta mnatobtatws (1975), TITUS electronic edition",
        "supporting_statement": "The edition gives an ordered 1-28 lunar-night schedule and reports odd entries red and even entries black; no homologous A-65 circular topology is documented.",
        "readable_slot_values": "YES",
        "fixed_start": "YES_TEXTUAL_NIGHT_1",
        "fixed_order": "YES_TEXTUAL_1_TO_28",
        "one_to_one_ownership": "YES_TEXTUAL_RECORD",
        "topology": "TEXTUAL_ORDERED_28_ALTERNATING_RENDERING",
        "voynich_target_family": "F69V_28",
        "source_status": "SOURCE_VERIFIED_NOT_DIAGRAM_HOMOLOGUE",
    },
    {
        "source_id": "EXT003_W73_WINDS_12",
        "manuscript_id": "Baltimore, Walters Art Museum, W.73, f.1v",
        "date_region": "late 12th century; England",
        "source_type": "OFFICIAL_MUSEUM_CATALOGUE",
        "source_url": "https://t.thedigitalwalters.org/Data/WaltersManuscripts/html/W73/description.html",
        "bibliographic_reference": "Walters Ms. W.73, Cosmography, description of f.1v",
        "supporting_statement": "Twelve profile winds have Latin and Greek names in concentric bands, owned spokes, four cardinal directions, East at top, and a catalogue-given clockwise reading.",
        "readable_slot_values": "YES",
        "fixed_start": "YES_EAST_TOP_AND_NORTH_REFERENCE",
        "fixed_order": "YES_CATALOGUED_CLOCKWISE",
        "one_to_one_ownership": "YES_SPOKES_AND_NAMES",
        "topology": "OWNED_12_SPOKE_WHEEL",
        "voynich_target_family": "SPECIAL_CIRCLE_12_SECTOR_RINGS",
        "source_status": "SOURCE_VERIFIED",
    },
    {
        "source_id": "EXT004_W73_PLANETS_ZODIAC",
        "manuscript_id": "Baltimore, Walters Art Museum, W.73, f.2v",
        "date_region": "late 12th century; England",
        "source_type": "OFFICIAL_MUSEUM_CATALOGUE",
        "source_url": "https://art.thewalters.org/object/W.73.2V/",
        "bibliographic_reference": "Walters W.73.2V, Diagram of the Planetary Orbits and Zodiac",
        "supporting_statement": "Earth is central, seven named heavenly bodies occupy ordered concentric rings, and twelve named zodiac signs occupy the frame.",
        "readable_slot_values": "YES",
        "fixed_start": "YES_CATALOGUED_TOP_SIGN",
        "fixed_order": "YES_CONCENTRIC_AND_ZODIAC_ORDER",
        "one_to_one_ownership": "YES_RING_AND_FRAME_LABELS",
        "topology": "CENTER_PLUS_7_CONCENTRIC_PLUS_12_FRAME",
        "voynich_target_family": "F67R2_7_AND_12",
        "source_status": "SOURCE_VERIFIED",
    },
    {
        "source_id": "EXT005_W73_LUNAR_30_ZODIAC_12",
        "manuscript_id": "Baltimore, Walters Art Museum, W.73, f.6v",
        "date_region": "late 12th century; England",
        "source_type": "OFFICIAL_MUSEUM_CATALOGUE",
        "source_url": "https://t.thedigitalwalters.org/Data/WaltersManuscripts/html/W73/description.html",
        "bibliographic_reference": "Walters Ms. W.73, description of f.6v",
        "supporting_statement": "A lunar-course rota numbers days I-XXX counterclockwise from the top and gives twelve zodiac names beginning with Aries.",
        "readable_slot_values": "YES",
        "fixed_start": "YES_TOP_AND_ARIES",
        "fixed_order": "YES_COUNTERCLOCKWISE_I_TO_XXX",
        "one_to_one_ownership": "YES_NUMBERED_RINGS",
        "topology": "ORDERED_30_DAY_RING_PLUS_12_ZODIAC",
        "voynich_target_family": "ZODIAC_30;F68R1_29",
        "source_status": "SOURCE_VERIFIED",
    },
    {
        "source_id": "EXT006_W73_FOURFOLD",
        "manuscript_id": "Baltimore, Walters Art Museum, W.73, f.7v",
        "date_region": "late 12th century; England",
        "source_type": "OFFICIAL_MUSEUM_CATALOGUE",
        "source_url": "https://t.thedigitalwalters.org/Data/WaltersManuscripts/html/W73/description.html",
        "bibliographic_reference": "Walters Ms. W.73, four elements/seasons/qualities diagram",
        "supporting_statement": "The diagram explicitly names and orders four elements with qualities, seasons and humours through interlocking arcs.",
        "readable_slot_values": "YES",
        "fixed_start": "YES_CATALOGUED_TOP",
        "fixed_order": "YES_CLOCKWISE_CATALOGUE",
        "one_to_one_ownership": "YES_NAMED_ARCS",
        "topology": "INTERLOCKED_FOURFOLD_CORRESPONDENCE",
        "voynich_target_family": "F67V2_FOURFOLD",
        "source_status": "SOURCE_VERIFIED_PRIOR_ROUTE_EXPOSED",
    },
    {
        "source_id": "EXT007_ST_JOHNS_17_TIDAL_ROTA",
        "manuscript_id": "Oxford, St John's College, MS 17",
        "date_region": "ca.1110; England",
        "source_type": "OFFICIAL_FACSIMILE_PLUS_SCHOLARLY_AUDIT",
        "source_url": "https://digital.bodleian.ox.ac.uk/objects/cca30c56-0751-4f52-a952-bbffcb7b64e9/",
        "bibliographic_reference": "St John's College MS 17; L. Teresi, Anglia 138 (2020)",
        "supporting_statement": "The source-audited tidal rota uses explicit ordered wedges with 30 sectors, with 29-sector variants documented in the tradition.",
        "readable_slot_values": "YES_NUMERALS",
        "fixed_start": "YES_IN_SOURCE_TRADITION",
        "fixed_order": "YES_ORDERED_WEDGES",
        "one_to_one_ownership": "YES_WEDGE_NUMERALS",
        "topology": "ORDERED_29_OR_30_WEDGE_ROTA",
        "voynich_target_family": "F68R1_29;ZODIAC_30",
        "source_status": "SOURCE_VERIFIED",
    },
    {
        "source_id": "EXT008_NYPL_MA069_MODULES",
        "manuscript_id": "New York Public Library, MA 069 / MssCol 2557",
        "date_region": "1240-1260; Paris",
        "source_type": "OFFICIAL_LIBRARY_CATALOGUE_PLUS_SOURCE_AUDIT",
        "source_url": "https://digitalcollections.nypl.org/items/1fbe4680-28ab-013b-27fe-0242ac110002",
        "bibliographic_reference": "NYPL MA 069, Computus, Text 3",
        "supporting_statement": "One codex combines zodiac, letter-number, fourfold, Sun-Moon and nineteen-year circular modules, but audited cardinalities and ownership differ from Voynich panels.",
        "readable_slot_values": "PARTIAL",
        "fixed_start": "MIXED_BY_DIAGRAM",
        "fixed_order": "MIXED_BY_DIAGRAM",
        "one_to_one_ownership": "NO_EXACT_VOYNICH_HOMOLOGUE",
        "topology": "MULTIPLE_COMPUTUS_COSMOGRAPHY_WHEELS",
        "voynich_target_family": "SPECIAL_CIRCLE_BLOCK",
        "source_status": "SYSTEM_FAMILY_ONLY",
    },
    {
        "source_id": "EXT009_WELLCOME_MS202_MODULES",
        "manuscript_id": "London, Wellcome Collection, MS.202",
        "date_region": "1443; German",
        "source_type": "OFFICIAL_LIBRARY_CATALOGUE_PLUS_SOURCE_AUDIT",
        "source_url": "https://wellcomecollection.org/works/aeb73uat",
        "bibliographic_reference": "Wellcome MS.202, computistical miscellany",
        "supporting_statement": "A chronologically close computistical miscellany combines coloured fourfold and Sun-Moon diagrams but supplies no matching one-to-one Voynich slot map.",
        "readable_slot_values": "PARTIAL",
        "fixed_start": "MIXED_BY_DIAGRAM",
        "fixed_order": "MIXED_BY_DIAGRAM",
        "one_to_one_ownership": "NO_EXACT_VOYNICH_HOMOLOGUE",
        "topology": "COMPUTUS_COSMOGRAPHY_MODULE_SET",
        "voynich_target_family": "SPECIAL_CIRCLE_BLOCK",
        "source_status": "SYSTEM_FAMILY_ONLY",
    },
    {
        "source_id": "EXT010_OXFORD_ARAB_C90",
        "manuscript_id": "Oxford, Bodleian Libraries, MS. Arab. c. 90, ff.2b-3a",
        "date_region": "ca.1200; Arabic",
        "source_type": "HUMAN_CURATED_FDTW_METADATA",
        "source_url": "https://www.oraedes.fr/Medias/Details/a9a0e134-9a21-47b7-818b-c7058cd6b425",
        "bibliographic_reference": "FDTW/ORAEDES record 'Earth and the Heavens'",
        "supporting_statement": "The catalogue describes Earth and seven climates centrally, 28 star/image sections, 36 constellations, and an outer twelve-zodiac layer with east/west axis.",
        "readable_slot_values": "PARTIAL_MARGINAL_TEXT",
        "fixed_start": "AXIS_ONLY",
        "fixed_order": "NOT_FULLY_DOCUMENTED",
        "one_to_one_ownership": "PARTIAL",
        "topology": "CENTER_7_PLUS_28_PLUS_36_PLUS_12",
        "voynich_target_family": "F67R2_7_AND_12;F68R1_28_NONCENTRAL",
        "source_status": "METADATA_NEAR_HOMOLOGUE_ORDER_UNVERIFIED",
    },
    {
        "source_id": "EXT011_PARANATELLONTA_30",
        "manuscript_id": "Vatican BAV Reg. lat. 1283 / Astrolabium planum tradition",
        "date_region": "13th-century Iberian witness; later Latin witnesses",
        "source_type": "SCHOLARLY_PUBLIC_SOURCE_AUDIT",
        "source_url": "http://digi.vatlib.it/view/MSS_Reg.lat.1283.pt.A",
        "bibliographic_reference": "Libro de astromagia / Book of Paranatellonta; Astrolabium planum tradition",
        "supporting_statement": "The tradition supplies degree-specific images and fate descriptions in a fixed 1-30 order per sign, but the Vatican witness is incomplete and does not supply the missing Voynich phase/band key.",
        "readable_slot_values": "YES_FOR_EXTANT_DEGREES",
        "fixed_start": "YES_DEGREE_1",
        "fixed_order": "YES_1_TO_30_PER_SIGN",
        "one_to_one_ownership": "YES_EXTERNAL_DEGREE_RECORD",
        "topology": "ORDERED_30_RECORDS_PER_ZODIAC_SIGN",
        "voynich_target_family": "ZODIAC_30",
        "source_status": "SOURCE_VERIFIED_TARGET_PHASE_MISSING",
    },
    {
        "source_id": "EXT012_FENDULUS_DECANS",
        "manuscript_id": "London, British Library, Sloane MS 3983 / Morgan MS M.785 tradition",
        "date_region": "1350-1374 Sloane witness; ca.1403 Morgan witness",
        "source_type": "OFFICIAL_LIBRARY_AND_MUSEUM_CATALOGUES",
        "source_url": "https://searcharchives.bl.uk/catalog/040-002116376",
        "bibliographic_reference": "British Library Sloane MS 3983 catalogue; Morgan Library M.785 Astrological Treatises catalogue",
        "supporting_statement": "The official catalogues document a zodiac/paranatellonta cycle organized as one sign image plus three decan folios per sign; this is a 3x10 conceptual hierarchy, not a 30-slot circular one-to-one donor.",
        "readable_slot_values": "YES_CHAPTER_AND_DECAN_LEVEL",
        "fixed_start": "YES_SIGN_AND_DECAN_ORDER",
        "fixed_order": "YES_3_BY_10_TEXTUAL",
        "one_to_one_ownership": "NO_30_INDIVIDUAL_CIRCLE_SLOTS",
        "topology": "TWELVE_SIGNS_TIMES_THREE_DECANS",
        "voynich_target_family": "ZODIAC_30",
        "source_status": "SYSTEM_FAMILY_ONLY",
    },
    {
        "source_id": "EXT013_GOTHA_CHART_A472",
        "manuscript_id": "Gotha Research Library, Chart. A 472",
        "date_region": "ca.1460; German",
        "source_type": "OFFICIAL_CATALOGUE_PLUS_SCHOLARLY_AUDIT",
        "source_url": "https://bilder.manuscripta-mediaevalia.de/hs//projekt-Gotha-pdfs/Chart_A_472.pdf",
        "bibliographic_reference": "Official Gotha catalogue, Chart. A 472",
        "supporting_statement": "A consecutive seven-diagram run includes zodiac, year, four individual planets and apsides; it is not a one-to-one seven-planet donor.",
        "readable_slot_values": "YES_DIAGRAM_TITLES",
        "fixed_start": "YES_CODEX_ORDER",
        "fixed_order": "YES_CODEX_ORDER",
        "one_to_one_ownership": "NO_SEVEN_PLANET_MAPPING",
        "topology": "SEVEN_DIAGRAM_RUN_NOT_SEVEN_LUMINARIES",
        "voynich_target_family": "SPECIAL_CIRCLE_SEVEN_ARRAYS",
        "source_status": "REJECTED_ONE_TO_ONE_DONOR",
    },
    {
        "source_id": "EXT014_LANDSBERG_SPHAERA_7_IN_12",
        "manuscript_id": "Leipzig, Martin Landsberg Sphaera frontispiece",
        "date_region": "ca.1494; Leipzig",
        "source_type": "SCHOLARLY_STUDY_PLUS_OFFICIAL_DIGITIZATION",
        "source_url": "https://doi.org/10.1007/978-3-030-86600-6_12",
        "bibliographic_reference": "Richard L. Kremer, Printing Sacrobosco in Leipzig, 1488-ca.1521 (2022), fig.10; BSB 4 Inc.s.a.1607, urn:nbn:de:bvb:12-bsb00029417-1",
        "supporting_statement": "The reproduced 1494 frontispiece yields a human-audited seven-body-in-twelve-sign binary pattern 111101010100. Kremer identifies the design as newly Christianized and explicitly warns that its zodiac signs are incorrectly placed; no earlier exact witness is established here.",
        "readable_slot_values": "YES",
        "fixed_start": "YES_IN_PRINT",
        "fixed_order": "YES_IN_PRINT",
        "one_to_one_ownership": "YES_LATE_PRINT",
        "topology": "SEVEN_OCCUPIED_OF_TWELVE_111101010100",
        "voynich_target_family": "F67R2_7_IN_12",
        "source_status": "LATE_COMPARATOR_NO_EARLY_DONOR",
    },
]


CANDIDATES = [
    {
        "candidate_id": "C001_BL28_TO_F69V",
        "external_source_ids": "EXT001_BL_ADD_MS_25435;EXT002_A65_28_NIGHTS",
        "voynich_target": "f69v|X1",
        "geometry_match": "CIRCULAR_28_VS_NUMBERED_OR_ORDERED_28",
        "external_slots_readable": "YES",
        "external_order_fixed": "YES",
        "external_ownership_fixed": "YES",
        "voynich_order_authorial": "NO_EDITORIAL_ONLY",
        "voynich_phase_text_blind": "NO",
        "voynich_physical_folios": "1",
        "independent_discovery_held_capacity": "NO",
        "prior_route": "F69VSD001_NO_START_DIRECTION;KART001_DIRECT_TRANSFER_FALSIFIED",
        "viable": "NO",
        "exclusion_reason": "External donor is excellent, but f69v has no authorial origin/direction and no independent held folio.",
    },
    {
        "candidate_id": "C002_BL28_TO_F68R1",
        "external_source_ids": "EXT001_BL_ADD_MS_25435",
        "voynich_target": "f68r1|S1",
        "geometry_match": "28_NONCENTRAL_PLUS_ONE_CENTER_VS_NUMBERED_28",
        "external_slots_readable": "YES",
        "external_order_fixed": "YES",
        "external_ownership_fixed": "YES",
        "voynich_order_authorial": "NO_SCATTERED_STARS",
        "voynich_phase_text_blind": "NO",
        "voynich_physical_folios": "1",
        "independent_discovery_held_capacity": "NO",
        "prior_route": "COMPUTUS_CIRCLE_AUDIT_COUNT_ONLY",
        "viable": "NO",
        "exclusion_reason": "The 28 noncentral stars have neither an authorial sequence nor an independent-folio replication.",
    },
    {
        "candidate_id": "C003_W73_7_12_TO_F67R2",
        "external_source_ids": "EXT004_W73_PLANETS_ZODIAC;EXT014_LANDSBERG_SPHAERA_7_IN_12",
        "voynich_target": "f67r2|M1+M2",
        "geometry_match": "SEVEN_AND_TWELVE_COUNTS",
        "external_slots_readable": "YES",
        "external_order_fixed": "YES",
        "external_ownership_fixed": "YES",
        "voynich_order_authorial": "PARTIAL_CIRCULAR",
        "voynich_phase_text_blind": "NO",
        "voynich_physical_folios": "1",
        "independent_discovery_held_capacity": "NO",
        "prior_route": "F67_F72_SEVEN_SPECIFICITY_FAILED;SACROBOSCO_LATE_ONLY",
        "viable": "NO",
        "exclusion_reason": "The counts coexist, but the external seven are concentric or late binary occupants rather than the Voynich local topology; only one target folio exists.",
    },
    {
        "candidate_id": "C004_W73_WINDS_TO_12_SECTORS",
        "external_source_ids": "EXT003_W73_WINDS_12",
        "voynich_target": "f67r1|D1;f67r2|M2;f67v1|X1",
        "geometry_match": "TWELVE_CIRCULAR_SECTORS",
        "external_slots_readable": "YES",
        "external_order_fixed": "YES",
        "external_ownership_fixed": "YES",
        "voynich_order_authorial": "YES_WITHIN_EACH_RING",
        "voynich_phase_text_blind": "NO_SHARED_MARKER",
        "voynich_physical_folios": "1",
        "independent_discovery_held_capacity": "NO",
        "prior_route": "WARBURG_WIND_HOMOLOGUE_PRESCREEN_NO_EXACT_OWNED_TOPOLOGY",
        "viable": "NO",
        "exclusion_reason": "All three twelve-slot target rings are on physical folio f67 and lack a shared text-blind phase/ownership key.",
    },
    {
        "candidate_id": "C005_PARANATELLONTA_TO_ZODIAC30",
        "external_source_ids": "EXT005_W73_LUNAR_30_ZODIAC_12;EXT011_PARANATELLONTA_30;EXT012_FENDULUS_DECANS",
        "voynich_target": "ten extant zodiac signs f70v2-f73v",
        "geometry_match": "THIRTY_POSITIONS_PER_SIGN",
        "external_slots_readable": "YES",
        "external_order_fixed": "YES",
        "external_ownership_fixed": "YES_EXTERNAL_RECORDS",
        "voynich_order_authorial": "NO_COMMON_PHASE",
        "voynich_phase_text_blind": "NO_SEVEN_TOPOLOGIES",
        "voynich_physical_folios": "4",
        "independent_discovery_held_capacity": "NO_SAME_TOPOLOGY_ACROSS_DISJOINT_FOLIOS",
        "prior_route": "ZODIAC_CROSSSIGN_PHASE_CAPACITY_STOP",
        "viable": "NO",
        "exclusion_reason": "Target count is strong, but seven panel topologies lack a common start, direction, and band continuation; every repeated topology pair shares a folio.",
    },
    {
        "candidate_id": "C006_A65_FORTUNATE_DEGREES_TO_ZODIAC",
        "external_source_ids": "EXT002_A65_28_NIGHTS",
        "voynich_target": "ten extant zodiac signs f70v2-f73v",
        "geometry_match": "SIGN_SPECIFIC_SUBSETS_OF_30",
        "external_slots_readable": "YES_EXTERNAL_DEGREE_SETS",
        "external_order_fixed": "YES",
        "external_ownership_fixed": "YES_EXTERNAL_TEXT",
        "voynich_order_authorial": "NO_COMMON_PHASE",
        "voynich_phase_text_blind": "NO",
        "voynich_physical_folios": "4",
        "independent_discovery_held_capacity": "NO_CAPACITY_VALID_FROZEN_VISUAL_SUBSET",
        "prior_route": "KART001_T5_UNSCORED_NO_CAPACITY",
        "viable": "NO",
        "exclusion_reason": "No complete independently annotated Voynich binary/subset state with singular slot ownership survives across signs.",
    },
    {
        "candidate_id": "C007_W73_FOURFOLD_TO_F67V2",
        "external_source_ids": "EXT006_W73_FOURFOLD",
        "voynich_target": "f67v2|M1+E1",
        "geometry_match": "FOURFOLD_CORNERS_AND_RADIAL_TITLES",
        "external_slots_readable": "YES",
        "external_order_fixed": "YES",
        "external_ownership_fixed": "YES",
        "voynich_order_authorial": "FOUR_CORNERS_ONLY",
        "voynich_phase_text_blind": "NO_EXTERNAL_CORNER_KEY",
        "voynich_physical_folios": "1",
        "independent_discovery_held_capacity": "NO",
        "prior_route": "F57_F67_SEMANTIC_TRANSFER_EXPOSED_AND_WITHDRAWN",
        "viable": "NO",
        "exclusion_reason": "One target folio and no independent corner phase; prior element/direction semantics are exposed and withdrawn.",
    },
    {
        "candidate_id": "C008_TIDAL29_TO_F68R1",
        "external_source_ids": "EXT007_ST_JOHNS_17_TIDAL_ROTA",
        "voynich_target": "f68r1|S1",
        "geometry_match": "TWENTY_NINE_TOTAL",
        "external_slots_readable": "YES",
        "external_order_fixed": "YES",
        "external_ownership_fixed": "YES",
        "voynich_order_authorial": "NO",
        "voynich_phase_text_blind": "NO",
        "voynich_physical_folios": "1",
        "independent_discovery_held_capacity": "NO",
        "prior_route": "COMPUTUS_CIRCLE_AUDIT_COUNT_ANALOGUE_ONLY",
        "viable": "NO",
        "exclusion_reason": "The donor is a numbered wedge rota; the target is a scattered 29-star field with one centre and no authorial cycle.",
    },
    {
        "candidate_id": "C009_10_PLUS_5_ZODIAC_SPLITS",
        "external_source_ids": "EXT011_PARANATELLONTA_30;EXT012_FENDULUS_DECANS",
        "voynich_target": "f70v1;f71r;f71v;f72r1",
        "geometry_match": "TWO_PANELS_EACH_10_PLUS_5_EQUALS_30",
        "external_slots_readable": "YES_EXTERNAL_30",
        "external_order_fixed": "YES_EXTERNAL_30",
        "external_ownership_fixed": "YES_EXTERNAL_RECORDS",
        "voynich_order_authorial": "NO_INTERPANEL_CONTINUATION",
        "voynich_phase_text_blind": "NO_TWO_TO_ONE_PAIRING_OR_BAND_KEY",
        "voynich_physical_folios": "3",
        "independent_discovery_held_capacity": "NO_AUTHOR_VISIBLE_PAIRING",
        "prior_route": "SPECIAL_CIRCLE_10_TO_5_PAIRING_STOP",
        "viable": "NO",
        "exclusion_reason": "Four panels offer nominal folio capacity, but no spokes, cells, leaders, or continuation rule identify the 30 external positions.",
    },
    {
        "candidate_id": "C010_ARAB_C90_COMPOSITE",
        "external_source_ids": "EXT010_OXFORD_ARAB_C90",
        "voynich_target": "f67r2 plus f68r1",
        "geometry_match": "7_CENTER_CONTEXT_PLUS_28_PLUS_12",
        "external_slots_readable": "PARTIAL",
        "external_order_fixed": "NO",
        "external_ownership_fixed": "PARTIAL",
        "voynich_order_authorial": "NO_COMPOSITE_AUTHORIAL_UNIT",
        "voynich_phase_text_blind": "NO",
        "voynich_physical_folios": "2",
        "independent_discovery_held_capacity": "NO",
        "prior_route": "FDTW_METADATA_PRESCREEN_ONLY",
        "viable": "NO",
        "exclusion_reason": "The resemblance exists only by combining different Voynich pages/folios; the external 28-slot order is not documented in the metadata.",
    },
    {
        "candidate_id": "C011_GOTHA_SEVEN_DIAGRAMS",
        "external_source_ids": "EXT013_GOTHA_CHART_A472",
        "voynich_target": "special-circle seven-size arrays",
        "geometry_match": "SEVEN_COUNT_ONLY",
        "external_slots_readable": "YES_TITLES",
        "external_order_fixed": "YES_CODEX_ORDER",
        "external_ownership_fixed": "NO_SEVEN_PLANETS",
        "voynich_order_authorial": "NO_CROSS_PAGE_SEQUENCE_KEY",
        "voynich_phase_text_blind": "NO",
        "voynich_physical_folios": "2",
        "independent_discovery_held_capacity": "NO",
        "prior_route": "TPQ001_NO_ONE_TO_ONE_DONOR",
        "viable": "NO",
        "exclusion_reason": "The seven external titles are not seven luminaries and target seven-size arrays are not a matched page sequence.",
    },
]


def write_tsv(path: Path, rows: list[dict[str, str]], fieldnames: list[str] | None = None) -> None:
    if fieldnames is None:
        if not rows:
            raise ValueError("fieldnames required for empty table")
        fieldnames = list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def input_hashes() -> dict[str, str]:
    return {str(path.relative_to(ROOT)): sha256_file(path) for path in INPUTS}


def load_special_circle_summary() -> tuple[list[dict[str, str]], dict[str, object]]:
    arrays: dict[str, dict[str, str]] = {}
    slots = 0
    guard = GuardedTSV(SC, selector_column="page", forbidden_action="error")
    for row in guard:
        slots += 1
        arrays.setdefault(row["array_id"], row)
    folios = sorted({row["physical_folio"] for row in arrays.values()})
    if slots != 504 or len(arrays) != 45 or len(folios) != 7:
        raise AssertionError((slots, len(arrays), folios))
    sizes = Counter(int(row["slot_count"]) for row in arrays.values())
    rows = []
    for array_id, row in sorted(arrays.items(), key=lambda item: int(item[1]["array_index"])):
        rows.append(
            {
                "target_id": f"SC_{int(row['array_index']):03d}",
                "scope": "SPECIAL_CIRCLE_ARRAY",
                "physical_folios": row["physical_folio"],
                "pages": row["page"],
                "unit_ids": row["unit"],
                "instance_count": "1",
                "slot_structure": row["slot_count"],
                "authorial_order_state": "LOCAL_ARRAY_ORDER_ONLY",
                "phase_state": "NO_EXTERNAL_VALUE_KEY",
                "ownership_state": "HUMAN_UNIT_LEVEL_ONLY",
                "independent_folio_capacity": "NO_SINGLE_ARRAY",
                "source_artifact": str(SC.relative_to(ROOT)),
                "neutral_description": row["unit_description"],
            }
        )
    summary = {
        "array_count": len(arrays),
        "slot_count": slots,
        "folio_count": len(folios),
        "folios": folios,
        "size_histogram": {str(k): sizes[k] for k in sorted(sizes)},
        "guard": guard.stats.__dict__,
    }
    return rows, summary


def add_composite_targets(rows: list[dict[str, str]]) -> dict[str, object]:
    zodiac = json.loads(ZODIAC.read_text(encoding="utf-8"))
    f69 = json.loads(F69.read_text(encoding="utf-8"))
    pair105 = json.loads(PAIR105.read_text(encoding="utf-8"))
    if zodiac["counts"] != {
        "disjoint_folio_repeated_topology_pairs": 0,
        "distinct_panel_topologies": 7,
        "expected_slots": 300,
        "physical_folios": 4,
        "present_labels": 299,
        "repeated_topology_pairs": 3,
        "signs": 10,
    }:
        raise AssertionError("zodiac capacity artifact changed")
    if f69["counts"]["author_visible_start_devices"] != 0 or f69["counts"]["author_visible_direction_devices"] != 0:
        raise AssertionError("f69 start/direction artifact changed")
    if pair105["counts"]["pages_with_pairing_device"] != 0:
        raise AssertionError("10-to-5 pairing artifact changed")
    rows.extend(
        [
            {
                "target_id": "COMPOSITE_ZODIAC_30",
                "scope": "TEN_EXTANT_ZODIAC_SIGNS",
                "physical_folios": "f70;f71;f72;f73",
                "pages": "f70v2-f73v",
                "unit_ids": "10 signs; 7 topology classes",
                "instance_count": "10",
                "slot_structure": "30 per sign; 300 expected; 299 labels",
                "authorial_order_state": "NO_COMMON_BAND_CONTINUATION",
                "phase_state": "NO_SHARED_START_OR_DIRECTION",
                "ownership_state": "SIGN_LEVEL_HUMAN_INVENTORY",
                "independent_folio_capacity": "FAIL_ZERO_DISJOINT_FOLIO_REPEATED_TOPOLOGY_PAIRS",
                "source_artifact": str(ZODIAC.relative_to(ROOT)),
                "neutral_description": "Ten public zodiac sign inventories use seven incompatible panel topologies.",
            },
            {
                "target_id": "COMPOSITE_F69V_28",
                "scope": "F69V_RADIAL_ARRAY",
                "physical_folios": "f69",
                "pages": "f69v",
                "unit_ids": "X1",
                "instance_count": "1",
                "slot_structure": "28 alternating radial entries",
                "authorial_order_state": "CYCLIC_RELATIVE_ORDER_ONLY",
                "phase_state": "NO_AUTHOR_VISIBLE_START_OR_DIRECTION",
                "ownership_state": "HUMAN_ARRAY_LEVEL",
                "independent_folio_capacity": "FAIL_ONE_FOLIO",
                "source_artifact": str(F69.relative_to(ROOT)),
                "neutral_description": "Twenty-eight radial entries with no author-visible origin or traversal direction.",
            },
            {
                "target_id": "COMPOSITE_ZODIAC_10_PLUS_5",
                "scope": "FOUR_SPLIT_ZODIAC_PANELS",
                "physical_folios": "f70;f71;f72",
                "pages": "f70v1;f71r;f71v;f72r1",
                "unit_ids": "outer10+inner5 per panel",
                "instance_count": "4",
                "slot_structure": "10+5 repeated panels",
                "authorial_order_state": "LOCAL_RING_ORDER_ONLY",
                "phase_state": "NO_TWO_TO_ONE_OR_INTERPANEL_KEY",
                "ownership_state": "BAND_LEVEL_ONLY",
                "independent_folio_capacity": "FAIL_NO_AUTHOR_VISIBLE_PAIRING_DEVICE",
                "source_artifact": str(PAIR105.relative_to(ROOT)),
                "neutral_description": "Four panels have no spokes, cells, leaders or exact two-to-one pairing.",
            },
        ]
    )
    return {"zodiac": zodiac["counts"], "f69": f69["counts"], "pair105": pair105["counts"]}


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    topology_rows, special_summary = load_special_circle_summary()
    composite_summary = add_composite_targets(topology_rows)
    source_rows = [dict(row) for row in EXTERNAL_SOURCES]
    candidate_rows = [dict(row) for row in CANDIDATES]
    viable = [row for row in candidate_rows if row["viable"] == "YES"]

    write_tsv(ART / "gdt337_external_source_manifest.tsv", source_rows)
    write_tsv(ART / "gdt337_voynich_topology_capacity.tsv", topology_rows)
    write_tsv(ART / "gdt337_candidate_correspondences.tsv", candidate_rows)
    write_tsv(
        ART / "gdt337_viable_endpoint_freeze.tsv",
        viable,
        fieldnames=list(candidate_rows[0]),
    )

    outputs = [
        ART / "gdt337_external_source_manifest.tsv",
        ART / "gdt337_voynich_topology_capacity.tsv",
        ART / "gdt337_candidate_correspondences.tsv",
        ART / "gdt337_viable_endpoint_freeze.tsv",
    ]
    output_hashes = {str(path.relative_to(ROOT)): sha256_file(path) for path in outputs}
    result = {
        "schema": "GDT337_EXTERNAL_HOMOLOGUE_CENSUS_V1",
        "experiment": "GDT337",
        "status": "NO_VIABLE_FROZEN_ENDPOINT",
        "decision": "NO_EXTERNAL_EXACT_TOPOLOGICAL_HOMOLOGUE_HAS_TEXT_BLIND_PHASE_AND_INDEPENDENT_FOLIO_TRANSFER_CAPACITY",
        "question": "Does the provenance-clean external manuscript census supply a readable exact/topological endpoint that can be frozen before any Voynich joint-tuple scoring?",
        "counts": {
            "external_sources": len(source_rows),
            "candidate_correspondences": len(candidate_rows),
            "viable_endpoints": len(viable),
            "special_circle_arrays": special_summary["array_count"],
            "special_circle_slots": special_summary["slot_count"],
            "special_circle_folios": special_summary["folio_count"],
            "zodiac_signs": composite_summary["zodiac"]["signs"],
            "zodiac_expected_slots": composite_summary["zodiac"]["expected_slots"],
            "zodiac_panel_topologies": composite_summary["zodiac"]["distinct_panel_topologies"],
        },
        "eligibility_rule": {
            "external_slots_readable": True,
            "external_order_and_start_fixed": True,
            "external_one_to_one_ownership": True,
            "voynich_candidate_selected_without_text_identity": True,
            "voynich_phase_or_slot_correspondence_fixed_without_text": True,
            "disjoint_physical_folio_discovery_and_holdout": True,
            "no_closed_route_repair_by_relabeling": True,
        },
        "strongest_external_donor": {
            "source_id": "EXT001_BL_ADD_MS_25435",
            "strength": "NUMBERED_I_TO_XXVIII_WHEEL_WITH_POINTER_AND_28_READABLE_RECORDS",
            "target_blocker": "F69V_HAS_NO_AUTHORIAL_START_DIRECTION_AND_ONE_FOLIO;F68R1_HAS_NO_AUTHORIAL_ORDER_AND_ONE_FOLIO",
        },
        "special_circle_summary": special_summary,
        "source_access": {
            "external_catalogue_or_scholarly_text_reviewed": True,
            "voynich_images_opened": False,
            "voynich_transcription_or_tuple_identity_opened": False,
            "f84_material_opened_retained_joined_or_scored": False,
        },
        "next_acquisition_requirements": [
            "A second independently ordered 28-slot Voynich array or author-visible start/direction on a new 28-slot folio",
            "A text-blind start/direction/band key for the 30-position zodiac panels plus a disjoint-folio repeated topology",
            "At least two discovery folios and one disjoint held folio sharing singularly owned homologous slots",
        ],
        "inputs": input_hashes(),
        "outputs": output_hashes,
        "implementation": {
            str(Path(__file__).resolve().relative_to(ROOT)): sha256_file(Path(__file__).resolve())
        },
        "claim_ceiling": "This score-blind census can freeze or reject candidate external endpoints only. It assigns no diagram identity, external slot value, Voynich word, tuple, semantic role, language, plaintext, or translation.",
    }
    content = dict(result)
    result["result_content_sha256"] = hashlib.sha256(canonical_json_bytes(content)).hexdigest()
    (ART / "gdt337_result.json").write_bytes(canonical_json_bytes(result))
    print(json.dumps({"status": result["status"], "counts": result["counts"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

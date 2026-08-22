#!/usr/bin/env python3
"""Build the frozen V71 R2 image-to-text ownership ledger.

The mapping is deliberately image-first.  It consumes only the two frozen V69
unit ledgers and assigns owners from the frozen V70 R2 visual inventory.  It
never consumes surface spelling, card values, stems, or semantic glosses.
"""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
FIELD_SOURCE = ROOT / "experiments/yolo/sidequest_theory_candidates_v69/V69_R4_FINAL_135_FIELD_EDITION.tsv"
ASTRO_SOURCE = ROOT / "experiments/yolo/sidequest_theory_candidates_v69/V69_R4_FINAL_395_ASTRO_GROUPS.tsv"
LEDGER_OUT = HERE / "V71_R2_OWNER_LEDGER.tsv"
REVISIONS_OUT = HERE / "V71_R2_REVISIONS.tsv"
BUILD_OUT = HERE / "V71_R2_BUILD_SUMMARY.json"


LEDGER_COLUMNS = [
    "unit_type",
    "unit_id",
    "page",
    "section",
    "source_record",
    "locus",
    "source_statement",
    "source_group_count",
    "source_group_ids",
    "ownership_status",
    "smallest_visible_owner",
    "silent_argument_or_source_default",
    "strongest_rival",
    "confidence",
    "v69_revision_id",
    "v69_revision",
    "image_basis",
    "historical_constraint",
]


REVISION_META = {
    "H10_WHOLE": (
        "f10r/F001-F005",
        "Two operational records and possible part-specific defaults.",
        "One whole broad-toothed, radial-flowered herb owns the article.",
        "REPLACE_OWNER; RETAIN_FIELD_ORDER_ONLY",
        "Illustrated simple/herbal article practice; an unpictured recipe may follow the plant.",
        "Flower-, leaf-, and underground-part subarticles.",
        "0.76",
    ),
    "H11_WHOLE": (
        "f11r/F006-F009",
        "A narrow named plant and operation-bearing record.",
        "One whole dense blue-flowered crown plant owns the article.",
        "REPLACE_OWNER; RETAIN_FIELD_ORDER_ONLY",
        "A whole illustrated simple can govern several prose fields without one field per part.",
        "Several compressed shoots or specimens.",
        "0.72",
    ),
    "H55_WHOLE": (
        "f55v/F010-F013",
        "Four text pockets read as distinct plant-part/process slots.",
        "One uninterrupted broad-leaf panicled plant, including mnemonic root, owns all pockets.",
        "REPLACE_OWNER; BLOCK_POCKETS_NOT_PART_LABELS",
        "Image-first layout around a central plant is ordinary in illustrated herbals.",
        "Root grotesque as an independently named creature or plant identity.",
        "0.81",
    ),
    "H56_WHOLE": (
        "f56r/F014-F020",
        "Individual heads assigned separate preparation meanings.",
        "One multihead spiny or emblematic herb owns the article.",
        "REPLACE_OWNER; RETAIN_FIELD_ORDER_ONLY",
        "Schematic growth stages may coexist in one herbal image without defining separate entries.",
        "Several specimens or a sequence of growth stages.",
        "0.70",
    ),
    "B81_PAGE": (
        "f81v loci 2/7",
        "A seven-stage preparation/cycle owner.",
        "The shared enclosure and figure group own the page-level prose.",
        "WITHDRAW_CYCLE; REPLACE_WITH_SHARED_VISIBLE_OWNER",
        "Late-medieval bath manuscripts place grouped nude bathers inside one basin.",
        "Two separate figure-row episodes.",
        "0.63",
    ),
    "B81_POOL": (
        "f81v loci 17-27",
        "Successive process stations or named individual participants.",
        "The prose inherits the one shared pool/enclosure; the final local locus may attach to its edge.",
        "WITHDRAW_INDIVIDUAL_STAGE_NAMES; KEEP_SHARED_ASSEMBLY",
        "A basin can own a regimen while individual users remain silent arguments.",
        "Before/after rows or personified stages.",
        "0.67",
    ),
    "B82_UPPER": (
        "f82r loci 2-4",
        "One page-wide impersonal circuit.",
        "Upper paired arches, perforated cylinder, and two figure stations form one local assembly.",
        "SPLIT_PAGE_OWNER_INTO_LOCAL_ASSEMBLIES; NO_FLOW_DIRECTION",
        "Bath books and device books both permit locally bounded station scenes.",
        "One abstract pipe network.",
        "0.68",
    ),
    "B82_CROSS": (
        "f82r locus 7",
        "A continuation of the same page-wide station.",
        "The four-arm crosspiece and its horizontal support line are the nearest local owner.",
        "LOCALIZE_OWNER; NO_SOURCE_OR_SINK",
        "Technical diagrams can isolate fittings, but their direction requires arrows or level evidence.",
        "Decorative or cosmological emblem rather than fitting.",
        "0.58",
    ),
    "B82_RECLINED": (
        "f82r locus 19",
        "A generic bath/process step in one circuit.",
        "The reclined figure in a distinct funnel-footed vessel owns the nearby prose pocket.",
        "LOCALIZE_OWNER_TO_FIGURE_VESSEL",
        "Illustrated bath regimens can bind a text unit to a particular posture or vessel scene.",
        "Personified state rather than patient/user.",
        "0.72",
    ),
    "B82_TRANSITION": (
        "f82r locus 23",
        "A determinate station in one circuit.",
        "No smallest owner is resolved between the reclined vessel and lower enclosure.",
        "MARK_OWNER_UNRESOLVED",
        "Text fitted into inter-image space need not label the closest contour.",
        "Either adjacent local assembly.",
        "0.38",
    ),
    "B82_LOWER": (
        "f82r loci 26-27",
        "A lower stage of one directional cycle.",
        "The large irregular green enclosure, its figures, and terminating vertical marks form the owner.",
        "LOCALIZE_OWNER; WITHDRAW_STAGE_NUMBER_AND_DIRECTION",
        "A collective basin scene is historically simpler than an unseen modern closed circuit.",
        "Allegorical region with personified states.",
        "0.69",
    ),
    "B83_MARGIN": (
        "f83r loci 3-16",
        "One main basin/circuit owner.",
        "The vertical left-margin sequence of small figure stations owns adjacent prose by inheritance.",
        "SPLIT_SINGLE_CIRCUIT; LOCAL_MARGIN_OWNER",
        "Marginal station series can organize exempla without implying hydraulic continuity.",
        "Pure page ornament or one continuous process stage series.",
        "0.62",
    ),
    "B83_LEFT": (
        "f83r loci 20-24",
        "One directed return/irrigation circuit.",
        "The left vessel, over-arch, blue lower channel, and second figure station form one connected owner.",
        "KEEP_CONNECTIVITY; WITHDRAW_DIRECTION_AND_FLUID",
        "Taccola-type hydraulic drawing calibrates apparatus, not the identity or direction of contents.",
        "A therapeutic posture scene rather than a device.",
        "0.67",
    ),
    "B83_GAP": (
        "f83r loci 25-28",
        "Continuation of one page-wide circuit.",
        "The text lies between two visibly disconnected lower assemblies; no owner is resolved.",
        "MARK_DISCONNECTION_AND_OWNER_UNRESOLVED",
        "Separate vignette ownership is normal in illustrated compilations.",
        "Left assembly or right S-tube assembly.",
        "0.36",
    ),
    "B83_RIGHT": (
        "f83r loci 35-54",
        "A continuation/return stage of the left apparatus.",
        "The right figure cup, S-tube, and blue lobed terminal node form a separate local owner.",
        "SPLIT_FROM_LEFT_ASSEMBLY; KEEP_LOCAL_CONNECTIVITY_ONLY",
        "Visible tubing supports a formal apparatus relation but no source, sink, or medical gloss.",
        "A personified state chain.",
        "0.71",
    ),
    "A67_INNER12": (
        "f67r2 loci 1-12",
        "Twelve named sign/body columns in a 7x12 lookup matrix.",
        "Each locus owns only a local radial sector/address in the paired-wheel page.",
        "KEEP_LOCAL_SLOT; WITHDRAW_SIGN_NAME_BODY_NAME_AND_MATRIX",
        "Twelvefold rings are period-plausible, but the drawing does not expose a rectangular cross-product.",
        "Circumferential prose fragments rather than discrete sector labels.",
        "0.61",
    ),
    "A67_BANDS": (
        "f67r2 non-key loci 13-51",
        "Lookup instructions mapped to one semantic matrix.",
        "The source-to-side crosswalk is absent; owner remains unresolved between the two wheels.",
        "WITHDRAW_LOOKUP_PROSE; MARK_WHEEL_OWNER_UNRESOLVED",
        "Concentric bands can carry legends or rules, but adjacency alone does not choose a wheel or sector.",
        "A page-level legend applying to both wheels.",
        "0.34",
    ),
    "A67_SEVEN": (
        "f67r2 loci 15/22/28/31/34/37/47",
        "Seven named planetary rows in a 7x12 matrix.",
        "At most seven spaced local anchors/emblem slots survive as a formal inventory.",
        "KEEP_SEVEN_LOCATION_CANDIDATE; WITHDRAW_PLANET_NAMES_AND_CROSS_PRODUCT",
        "A sevenfold astrological series is historical context, not an image identification.",
        "Ordinary ring labels with no coherent sevenfold owner.",
        "0.52",
    ),
    "A67_OUTER12": (
        "f67r2 loci 52-63",
        "Twelve named auxiliary houses.",
        "Each locus owns only one outer radial/emblem slot of the right rosette wheel.",
        "KEEP_OUTER_LOCAL_SLOT; WITHDRAW_HOUSE_LABELS",
        "Nested rings are historically plausible; house meanings require an external legend.",
        "Outer circumferential text divided by available space.",
        "0.62",
    ),
    "A67_OUTER_BAND": (
        "f67r2 loci 64-71",
        "Eight semantic conditions in a lookup algorithm.",
        "The red outer circumferential band of the right wheel is the inherited owner.",
        "KEEP_BAND_PLACEMENT; WITHDRAW_CONDITION_MEANINGS",
        "Rubric rings can be legends, instructions, or labels; their syntax is not visible.",
        "Independent page rubric rather than wheel legend.",
        "0.60",
    ),
    "A67_PAGE": (
        "f67r2 loci 72-74",
        "Long lookup and medical instruction blocks.",
        "Only the paired celestial-wheel page can own these prose blocks.",
        "WITHDRAW_PROSE_CONTENT; KEEP_PAGE_OWNER",
        "Period diagrams commonly coexist with explanatory prose, but the image cannot supply its wording.",
        "A continuation unrelated to either wheel.",
        "0.79",
    ),
    "A68_HEADER": (
        "f68r1 loci 1-7",
        "A single 28-house catalogue header and instructions.",
        "The multipanel star atlas, not one universal 28-item route, owns the prose heads.",
        "WITHDRAW_SINGLE_CATALOGUE_AND_ROUTE; KEEP_MULTIPANEL_PAGE_OWNER",
        "Star catalogues and lunar-station diagrams are period-plausible, but no inter-panel route is drawn.",
        "Independent captions for the two open fields.",
        "0.70",
    ),
    "A68_CENTER": (
        "f68r1 locus 8",
        "One central lunar catalogue owner.",
        "The label cannot be assigned among five face medallions from the frozen crosswalk.",
        "WITHDRAW_LUNAR_NAME; MARK_CENTRE_OWNER_UNRESOLVED",
        "Face medallions can mark celestial owners, winds, or mnemonic centres without fixing identity.",
        "The centre of the right circular field specifically.",
        "0.38",
    ),
    "A68_STARS": (
        "f68r1 loci 9-36",
        "Twenty-eight named lunar houses with imported operations.",
        "Each locus owns only its adjacent drawn star station or compact star cluster.",
        "KEEP_SPATIAL_ADDRESS; WITHDRAW_NAMES_OPERATIONS_AND_SEQUENCE",
        "Local star labels are a normal catalogue device; route, start, and meaning remain external.",
        "Sector address rather than individual star station.",
        "0.84",
    ),
    "A68_RIGHT_CENTER": (
        "f68r1 locus 37",
        "A legend proving a complete 28-house lunar circle.",
        "The central face and right circular star field jointly own the local central legend.",
        "LOCALIZE_LEGEND; WITHDRAW_NUMBER_NAME_AND_DIRECTION",
        "A centre-plus-surrounding-stars catalogue is visually plausible only for the right panel.",
        "Page-wide legend covering all three panels.",
        "0.67",
    ),
    "A69_PAGE": (
        "f69v loci 1-3",
        "One ordered 28-rule schedule header.",
        "The three separate rosettes and far-right prose block provide only a page owner.",
        "WITHDRAW_ONE_SCHEDULE; KEEP_THREE_DEVICE_PAGE_OWNER",
        "Multiple independent circular devices can coexist on one foldout without a crosswalk.",
        "One shared rubric applying to all three rosettes.",
        "0.75",
    ),
    "A69_LEFT_SLOTS": (
        "f69v loci 4-31",
        "Twenty-eight ordered rules with medical or workshop content.",
        "Each locus owns one local club-ended radial place in the left rosette only.",
        "KEEP_LOCAL_28_PLACE_INVENTORY; WITHDRAW_RULE_MEANING_START_AND_DIRECTION",
        "A 28-place lunar wheel is historically possible, but only the visible local carrier survives.",
        "Circumferential label fragments not individually attached to spokes.",
        "0.73",
    ),
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def page_section(page: str) -> str:
    if page in {"f10r", "f11r", "f55v", "f56r"}:
        return "HERBAL"
    if page in {"f81v", "f82r", "f83r"}:
        return "BIOLOGICAL"
    return "ASTRO"


def locus_number(locus: str) -> int:
    return int(locus.rsplit(".", 1)[1])


def assignment(
    status: str,
    owner: str,
    silent: str,
    rival: str,
    confidence: float,
    revision_id: str,
    image_basis: str,
    historical: str,
) -> dict[str, str]:
    return {
        "ownership_status": status,
        "smallest_visible_owner": owner,
        "silent_argument_or_source_default": silent,
        "strongest_rival": rival,
        "confidence": f"{confidence:.2f}",
        "v69_revision_id": revision_id,
        "v69_revision": REVISION_META[revision_id][3],
        "image_basis": image_basis,
        "historical_constraint": historical,
    }


def prose_assignment(row: dict[str, str]) -> dict[str, str]:
    page = row["page"]
    n = locus_number(row["locus"])

    herbal = {
        "f10r": (
            "WHOLE_BROAD_TOOTHED_RADIAL_FLOWERED_HERB",
            "The same whole illustrated plant remains the article subject; water, preparation, or application may be supplied only as an unpictured source argument.",
            "A flower-, leaf-, or underground-part-specific subarticle.",
            0.76,
            "H10_WHOLE",
            "One continuous axis joins leaves, flower, terminal form, and underground swellings; no water or implement is visible.",
        ),
        "f11r": (
            "WHOLE_DENSE_BLUE_FLOWERED_CROWN_PLANT",
            "The same whole illustrated plant remains the article subject; any preparation or use is unpictured source matter.",
            "Several compressed shoots or separate specimens.",
            0.72,
            "H11_WHOLE",
            "Crown, blooms, pale axes, and crossed root complex form one continuous specimen.",
        ),
        "f55v": (
            "WHOLE_BROAD_LEAF_PANICLED_PLANT_WITH_MNEMONIC_ROOT",
            "The uninterrupted whole plant remains the subject across all four text pockets; a source recipe may silently supply an unpictured material or use.",
            "One pocket per leaf, inflorescence, root, or independent grotesque creature.",
            0.81,
            "H55_WHOLE",
            "The central stem continuously joins spray, leaf mass, and root; text pockets are contour-shaped leftovers.",
        ),
        "f56r": (
            "WHOLE_MULTIHEAD_SPINY_OR_EMBLEMATIC_HERB",
            "The whole illustrated specimen remains the article subject; growth state, preparation medium, and use must come from an external source tradition if present.",
            "Each head is a separate specimen or growth-stage entry.",
            0.70,
            "H56_WHOLE",
            "All heads attach to one pale branching axis and no pictured liquid, person, vessel, or tool intervenes.",
        ),
    }
    if page in herbal:
        owner, silent, rival, conf, revision, basis = herbal[page]
        return assignment(
            "PAGE_OWNER_ONLY",
            owner,
            silent,
            rival,
            conf,
            revision,
            basis,
            "Illustrated herbal articles permit one plant image to govern several prose fields; they do not license a word or part gloss.",
        )

    if page == "f81v":
        if n in {2, 7}:
            return assignment(
                "PAGE_OWNER_ONLY",
                "SHARED_GREEN_POOL_OR_ENCLOSURE_WITH_FIGURE_GROUP",
                "The shared illustrated enclosure/group is the article owner; no individual figure, row, fluid identity, or stage is supplied.",
                "The two visible figure rows own separate episodes.",
                0.63,
                "B81_PAGE",
                "Two large prose blocks stand above one continuous green enclosure containing the whole figure group.",
                "Grouped nude bathers inside one basin are a direct late-medieval bath-manuscript motif, but gender and therapy remain open.",
            )
        if n == 27:
            return assignment(
                "DIRECT_VISIBLE",
                "LOWER_LEFT_APPENDAGE_AND_EDGE_OF_SHARED_FIGURE_ENCLOSURE",
                "The local lower-left writing can name or qualify the enclosure edge/appendage only; it does not identify one bather.",
                "The whole pool and figure group rather than its edge.",
                0.55,
                "B81_POOL",
                "The only short local writing lies at the lower-left boundary; no leader singles out a person.",
                "A caption may attach to a basin part or regimen, but proximity alone cannot produce a personal or medical name.",
            )
        return assignment(
            "INHERITED_VISIBLE",
            "SHARED_GREEN_POOL_OR_ENCLOSURE_WITH_FIGURE_GROUP",
            "The nearest prose pocket inherits the single shared enclosure; an individual participant or before/after stage is not supplied.",
            "Sequential upper/lower figure stages.",
            0.68,
            "B81_POOL",
            "All lower bodies enter the same continuous field and no boundary separates the two rows into stages.",
            "Bath regimens may describe a shared place while leaving the individual user implicit.",
        )

    if page == "f82r":
        if n in {2, 3, 4}:
            return assignment(
                "INHERITED_VISIBLE",
                "UPPER_PAIRED_ARCH_PERFORATED_CYLINDER_AND_TWO_FIGURE_STATIONS",
                "The upper station complex is the local owner; which end is source or sink and what passes through it remain silent.",
                "One page-wide abstract pipe network.",
                0.68,
                "B82_UPPER",
                "Both arches meet the perforated cylinder and extend toward two distinct figure stations.",
                "Bath and device manuscripts both support bounded station scenes; neither supplies flow direction here.",
            )
        if n == 7:
            return assignment(
                "INHERITED_VISIBLE",
                "MIDPAGE_FOUR_ARM_CROSSPIECE_ON_HORIZONTAL_LINE",
                "The crosspiece/line is the local formal subject; direction, material, and function are unpictured.",
                "A decorative or cosmological emblem rather than a fitting.",
                0.58,
                "B82_CROSS",
                "The four cup-ended arms form one local object on a horizontal line, isolated from a demonstrated source or sink.",
                "Contemporary device drawing makes a fitting possible but cannot choose it over an emblem without functional marks.",
            )
        if n == 19:
            return assignment(
                "INHERITED_VISIBLE",
                "RECLINED_FIGURE_IN_FUNNEL_FOOTED_VESSEL",
                "The distinct figure/vessel vignette is the local owner; patient identity, treatment, and vessel contents remain absent.",
                "A personified state or non-medical user station.",
                0.72,
                "B82_RECLINED",
                "The covered or clothed reclining figure occupies a separate funnel-footed container.",
                "Illustrated bath regimens can bind posture and container, but the same geometry can personify a process state.",
            )
        if n == 23:
            return assignment(
                "UNRESOLVED",
                "UNRESOLVED_BETWEEN_RECLINED_FIGURE_VESSEL_AND_LOWER_GREEN_FIGURE_ENCLOSURE",
                "No local owner is silently supplied; preserve both adjacent assemblies as alternatives.",
                "Either the reclined vessel alone or the lower collective enclosure.",
                0.38,
                "B82_TRANSITION",
                "The prose occupies an interstation pocket without a leader or enclosing contour.",
                "Image-first reflow can place prose between vignettes without making proximity a label relation.",
            )
        return assignment(
            "INHERITED_VISIBLE",
            "LOWER_IRREGULAR_GREEN_FIGURE_ENCLOSURE_AND_VERTICAL_TERMINALS",
            "The lower collective enclosure is the local owner; no numbered stage, medium identity, or direction is supplied.",
            "An allegorical region populated by personified states.",
            0.69,
            "B82_LOWER",
            "Many figures intersect one irregular green boundary and several patterned vertical marks terminate at or above it.",
            "Collective bathing and personified-process readings remain historically possible; a modern closed loop does not follow.",
        )

    if page == "f83r":
        if n <= 16:
            return assignment(
                "INHERITED_VISIBLE",
                "LEFT_MARGIN_SEQUENCE_OF_SMALL_FIGURE_STATIONS",
                "The adjacent station sequence is the local owner; each figure's identity and any temporal ordering remain silent.",
                "Page ornament or one continuous stage series.",
                0.62,
                "B83_MARGIN",
                "Small nude figures recur vertically in separate scalloped supports along the prose margin.",
                "Marginal station series occur in compilations without proving a hydraulic or therapeutic sequence.",
            )
        if n <= 24:
            return assignment(
                "INHERITED_VISIBLE",
                "LOWER_LEFT_VESSEL_OVERARCH_BLUE_CHANNEL_AND_SECOND_FIGURE_STATION",
                "The connected left assembly is the local owner; flow direction, fluid, source, and destination remain silent.",
                "A therapeutic posture scene rather than a device.",
                0.67,
                "B83_LEFT",
                "Vessel, blue lower curve, large overhead arch, and second figure station are contour-connected.",
                "Contemporary hydraulic diagrams validate apparatus as a genre option, not a directional reading.",
            )
        if n <= 28:
            return assignment(
                "UNRESOLVED",
                "UNRESOLVED_BETWEEN_DISCONNECTED_LOWER_LEFT_AND_LOWER_RIGHT_ASSEMBLIES",
                "No cross-assembly argument is supplied; retain the left and right devices as separate alternatives.",
                "The left over-arch assembly or the right S-tube assembly.",
                0.36,
                "B83_GAP",
                "No contour joins the two lower assemblies; intervening prose follows available space.",
                "Separate vignette ownership is historically ordinary and blocks an inferred single circuit.",
            )
        return assignment(
            "INHERITED_VISIBLE",
            "RIGHT_FIGURE_CUP_S_TUBE_AND_BLUE_LOBED_TERMINAL_NODE",
            "The right connected assembly is the local owner; the endpoint's function, contents, and direction remain silent.",
            "A personified-state chain rather than a device.",
            0.71 if n < 47 else 0.73,
            "B83_RIGHT",
            "The figure cup joins one S-shaped tube, which joins the blue lobed node; the nearby prose follows that contour.",
            "Visible connectivity supports a formal relation only; neither a medical nor workshop interpretation is forced.",
        )

    raise ValueError(f"Unexpected prose page: {page}")


def astro_assignment(page: str, n: int) -> dict[str, str]:
    if page == "f67r2":
        seven = {15, 22, 28, 31, 34, 37, 47}
        if 1 <= n <= 12:
            return assignment(
                "DIRECT_VISIBLE",
                f"LOCAL_RADIAL_SECTOR_ADDRESS_{n:02d}_WITHIN_PAIRED_WHEEL_PAGE",
                "The locally adjacent sector/star-field slot is the only owner; no sign, body part, or cross-table coordinate is supplied.",
                "A circumferential prose fragment rather than a sector label.",
                0.61,
                "A67_INNER12",
                "The page contains radial partitions and star/emblem fields, not a visible rectangular matrix.",
                "Twelvefold and sevenfold astrological relations are period-plausible comparanda, not readable labels here.",
            )
        if n in seven:
            return assignment(
                "INHERITED_VISIBLE",
                f"LOCAL_SPACED_RING_ANCHOR_OR_EMBLEM_SLOT_AT_{n:02d}",
                "Only a member of a seven-location formal candidate inventory is supplied; no planetary identity or row relation is inherited.",
                "An ordinary ring label with no coherent sevenfold owner.",
                0.52,
                "A67_SEVEN",
                "Seven source loci are spaced as formal keys, but the image shows two independent radial devices.",
                "A seven-planet series existed in period practice; this does not name these anchors.",
            )
        if 52 <= n <= 63:
            return assignment(
                "DIRECT_VISIBLE",
                f"OUTER_RADIAL_OR_EMBLEM_SLOT_{n - 51:02d}_OF_RIGHT_ROSETTE_WHEEL",
                "The adjacent outer slot/emblem is the only owner; no house, question, or semantic category is supplied.",
                "A circumferential text segment divided by available space.",
                0.62,
                "A67_OUTER12",
                "The right wheel has sector spokes, disc/crescent emblems, concentric writing, and an outer ring.",
                "Nested twelvefold rings are possible in medieval practice, but their labels require an external key.",
            )
        if 64 <= n <= 71:
            return assignment(
                "INHERITED_VISIBLE",
                "OUTER_RED_CIRCUMFERENTIAL_BAND_OF_RIGHT_ROSETTE_WHEEL",
                "The entire local band is inherited as owner; no condition, polarity, or rule sequence is supplied.",
                "An independent page rubric rather than a wheel legend.",
                0.60,
                "A67_OUTER_BAND",
                "Red writing forms an outer circular band around the right radial device.",
                "Rubric rings may be legends or instructions, but the visible form alone does not determine content.",
            )
        if 72 <= n <= 74:
            return assignment(
                "PAGE_OWNER_ONLY",
                "PAIRED_CELESTIAL_REFERENCE_WHEELS",
                "Both independent wheels provide the page context; no single sector, side, medical rule, or lookup path is supplied.",
                "A prose continuation unrelated to the diagrams.",
                0.79,
                "A67_PAGE",
                "Long prose occupies residual page space around two unconnected circular devices.",
                "Explanatory prose beside wheels is historically normal, but its wording is not pictorially recoverable.",
            )
        return assignment(
            "UNRESOLVED",
            "UNRESOLVED_BETWEEN_LEFT_FACE_WHEEL_AND_RIGHT_ROSETTE_WHEEL",
            "No wheel, sector, or instruction owner is silently supplied; the source-to-side crosswalk is absent.",
            "A page-level legend applying to both wheels.",
            0.34,
            "A67_BANDS",
            "Two independent concentric devices have separate centres and no connecting line.",
            "Concentric legends are historical, but proximity and source order do not select one device.",
        )

    if page == "f68r1":
        if 1 <= n <= 7:
            return assignment(
                "PAGE_OWNER_ONLY" if n >= 3 else "INHERITED_VISIBLE",
                "MULTIPANEL_STAR_ATLAS_WITH_TWO_OPEN_FIELDS_AND_ONE_RIGHT_CIRCULAR_FIELD",
                "The visible atlas or nearest open field is the owner; no route, house name, or universal 28-item sequence is supplied.",
                "Independent captions for the first and second open star fields.",
                0.70 if n >= 3 else 0.64,
                "A68_HEADER",
                "Short prose heads the open fields, while the full foldout contains three unconnected star panels.",
                "Star catalogues and lunar-station wheels are historical genres; a cross-panel itinerary is not visible.",
            )
        if n == 8:
            return assignment(
                "UNRESOLVED",
                "UNRESOLVED_AMONG_FIVE_FACE_MEDALLIONS",
                "No named central owner is supplied; retain all five medallions until a source-to-panel crosswalk exists.",
                "The central face of the right circular star field alone.",
                0.38,
                "A68_CENTER",
                "Five face medallions occur across three panels and the frozen inventory has no leader from this source locus.",
                "Celestial, wind, or mnemonic face-centres are all historically possible without fixing identity.",
            )
        if 9 <= n <= 36:
            return assignment(
                "DIRECT_VISIBLE",
                f"INDIVIDUAL_STAR_STATION_OR_COMPACT_STAR_CLUSTER_AT_{n:02d}",
                "The immediately adjacent drawn star/station is the owner; no name, operation, route, start, or direction is supplied.",
                "A sector address rather than an individual star station.",
                0.84,
                "A68_STARS",
                "Numerous short labels sit beside individual stars or compact groups across the fields.",
                "Local star labels are historically plausible catalogue practice; imported lunar-house names are not image evidence.",
            )
        return assignment(
            "INHERITED_VISIBLE",
            "CENTRAL_FACE_AND_RIGHT_CIRCULAR_STAR_FIELD",
            "The right circular panel owns the central legend; no lunar name, count, or reading direction is supplied.",
            "A page-wide legend covering all three star panels.",
            0.67,
            "A68_RIGHT_CENTER",
            "Only the right panel has a centre-plus-circular-star-field geometry.",
            "A local circular catalogue is plausible, but it does not account for the two open fields.",
        )

    if page == "f69v":
        if 1 <= n <= 3:
            return assignment(
                "PAGE_OWNER_ONLY",
                "THREE_SEPARATE_CELESTIAL_ROSETTES_AND_FAR_RIGHT_PROSE_BLOCK",
                "The foldout context is the only owner; no common start, direction, schedule, or cross-rosette rule is supplied.",
                "One shared rubric applying to all three rosettes.",
                0.75,
                "A69_PAGE",
                "Three differently constructed rosettes have separate centres and bands with no connecting line.",
                "Multiple circular lookup devices can share a foldout without forming one ordered table.",
            )
        slot = n - 3
        return assignment(
            "DIRECT_VISIBLE",
            f"LEFT_ROSETTE_CLUB_ENDED_RADIAL_PLACE_{slot:02d}",
            "The single local spoke/place carrying or adjoining the locus is the owner; rule content, start, direction, and semantic value remain absent.",
            "A circumferential text fragment not individually attached to one spoke.",
            0.73,
            "A69_LEFT_SLOTS",
            "The left rosette supplies approximately twenty-eight club-ended local radial places; the other two rosettes are disconnected.",
            "A 28-place lunar wheel is period-plausible, but calling a local place a lunar house or rule requires an external key.",
        )

    raise ValueError(f"Unexpected astro page: {page}")


def build_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for source in read_tsv(FIELD_SOURCE):
        base = {
            "unit_type": "PROSE_FIELD",
            "unit_id": source["field_id"],
            "page": source["page"],
            "section": page_section(source["page"]),
            "source_record": source["record_unit_id"],
            "locus": source["locus"],
            "source_statement": source["statement_id"],
            "source_group_count": source["event_count"],
            "source_group_ids": source["event_serials"],
        }
        base.update(prose_assignment(source))
        rows.append(base)

    grouped: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for source in read_tsv(ASTRO_SOURCE):
        grouped[(source["diagram_id"], source["page"], source["locus"])].append(source)
    for diagram, page, locus in sorted(
        grouped,
        key=lambda key: (int(key[0][1:]), locus_number(key[2])),
    ):
        sources = sorted(grouped[(diagram, page, locus)], key=lambda row: int(row["event_index"]))
        base = {
            "unit_type": "ASTRO_LOCUS",
            "unit_id": locus,
            "page": page,
            "section": "ASTRO",
            "source_record": diagram,
            "locus": locus,
            "source_statement": "NONE",
            "source_group_count": str(len(sources)),
            "source_group_ids": "|".join(row["opaque_local_id"] for row in sources),
        }
        base.update(astro_assignment(page, locus_number(locus)))
        rows.append(base)
    return rows


def write_tsv(path: Path, columns: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    rows = build_rows()
    write_tsv(LEDGER_OUT, LEDGER_COLUMNS, rows)

    revision_columns = [
        "revision_id",
        "unit_scope",
        "prior_v69_default",
        "v71_image_owner",
        "revision_action",
        "historical_basis",
        "strongest_rival",
        "confidence",
        "mapped_unit_count",
    ]
    revision_counts = Counter(row["v69_revision_id"] for row in rows)
    revision_rows = []
    for revision_id, values in REVISION_META.items():
        revision_rows.append(
            dict(zip(revision_columns[:-1], (revision_id, *values), strict=True))
            | {"mapped_unit_count": str(revision_counts[revision_id])}
        )
    write_tsv(REVISIONS_OUT, revision_columns, revision_rows)

    summary = {
        "experiment": "V71_R2_IMAGE_TO_TEXT_OWNER_MAP",
        "builder": Path(__file__).name,
        "source_files": [FIELD_SOURCE.name, ASTRO_SOURCE.name],
        "rows": len(rows),
        "unit_type_counts": dict(Counter(row["unit_type"] for row in rows)),
        "page_counts": dict(Counter(row["page"] for row in rows)),
        "ownership_status_counts": dict(Counter(row["ownership_status"] for row in rows)),
        "source_group_totals": {
            kind: sum(int(row["source_group_count"]) for row in rows if row["unit_type"] == kind)
            for kind in {"PROSE_FIELD", "ASTRO_LOCUS"}
        },
        "revision_count": len(revision_rows),
        "output_sha256": {
            LEDGER_OUT.name: sha256(LEDGER_OUT),
            REVISIONS_OUT.name: sha256(REVISIONS_OUT),
        },
        "sealed_data_accessed": False,
        "surface_or_card_semantics_used": False,
    }
    BUILD_OUT.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

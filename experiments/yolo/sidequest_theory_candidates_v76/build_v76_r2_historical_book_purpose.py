#!/usr/bin/env python3
"""Build the bounded V76 R2 historical book-purpose competition.

This builder only binds the frozen central V73--V75 selected occurrence
editions to two book-level historical purpose models.  It does not assign a
new value to any opaque form and it does not inspect any manuscript page.
"""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "experiments/yolo/sidequest_theory_candidates_v76"

H_EVENTS = ROOT / "experiments/yolo/sidequest_theory_candidates_v73/V73_SELECTED_100_EVENT_INTERLINEAR.tsv"
H_UNITS = ROOT / "experiments/yolo/sidequest_theory_candidates_v73/V73_SELECTED_FIVE_ARTICLES.tsv"
B_EVENTS = ROOT / "experiments/yolo/sidequest_theory_candidates_v74/V74_SELECTED_281_EVENT_INTERLINEAR.tsv"
B_UNITS = ROOT / "experiments/yolo/sidequest_theory_candidates_v74/V74_SELECTED_SIX_RECORD_EDITION.tsv"
A_EVENTS = ROOT / "experiments/yolo/sidequest_theory_candidates_v75/V75_SELECTED_395_GROUP_CELESTIAL_EDITION.tsv"
A_UNITS = ROOT / "experiments/yolo/sidequest_theory_candidates_v75/V75_SELECTED_THREE_INSTRUMENTS.tsv"


PURPOSE_A = "A_PRACTITIONER_THERAPEUTIC_IATROMATHEMATICAL_COMPENDIUM"
PURPOSE_B = "B_NATURAL_ARTIFICIAL_CELESTIAL_IMAGE_ATLAS_MODELBOOK"


UNITS = {
    "H1": {
        "section": "HERBAL", "page": "f10r", "count": 14,
        "range": "H:E001-H:E014",
        "a_role": "Illustrated simple-drug article: root/water preparation, use, and storage.",
        "b_role": "Natural-specimen/material sheet: root fraction, wet processing, and storage assay.",
        "a": (4, 4, 4, 4, 3), "b": (4, 3, 4, 2, 3),
        "discriminator": "An explicit therapeutic indication would favor A; a nonmedical material endpoint would favor B.",
    },
    "H2": {
        "section": "HERBAL", "page": "f10r", "count": 24,
        "range": "H:E015-H:E038",
        "a_role": "Illustrated simple-drug article: two harvest-state fractions composed as an external salve.",
        "b_role": "Seasonal specimen/material protocol: two harvest fractions combined and conserved.",
        "a": (4, 4, 4, 4, 3), "b": (4, 3, 4, 2, 3),
        "discriminator": "A bodily application or disease target would favor A; a durable reference sample would favor B.",
    },
    "H3": {
        "section": "HERBAL", "page": "f11r", "count": 17,
        "range": "H:E039-H:E055",
        "a_role": "Illustrated simple-drug article: wine extraction/internal administration plus a flower-oil preparation.",
        "b_role": "Natural-material sheet: two plant fractions preserved in different media.",
        "a": (4, 4, 4, 4, 3), "b": (4, 3, 4, 2, 3),
        "discriminator": "Administration language would favor A; comparison or storage language without a patient would favor B.",
    },
    "H4": {
        "section": "HERBAL", "page": "f55v", "count": 18,
        "range": "H:E056-H:E073",
        "a_role": "Illustrated simple-drug article: clarified leaf wash and a honey-bound poultice.",
        "b_role": "Natural-material sheet: clarified leaf liquid and an adhesive plant preparation.",
        "a": (4, 4, 4, 3, 3), "b": (4, 3, 4, 2, 3),
        "discriminator": "A named body site would favor A; a craft/material destination would favor B.",
    },
    "H5": {
        "section": "HERBAL", "page": "f56r", "count": 27,
        "range": "H:E074-H:E100",
        "a_role": "Illustrated simple-drug article: fresh topical material and a dried wine/honey extract.",
        "b_role": "Natural-material sheet: fresh-versus-dry plant handling and preservation.",
        "a": (4, 4, 4, 3, 3), "b": (4, 3, 4, 2, 3),
        "discriminator": "A treatment course would favor A; a shelf-life or material-quality test would favor B.",
    },
    "B1": {
        "section": "BIO", "page": "f81v", "count": 66,
        "range": "B:E101-B:E166",
        "a_role": "One shared therapeutic bathing field with a local regimen, not a chronological two-row sequence.",
        "b_role": "One illustrated bath/hydraulic installation sheet with local operating annotations.",
        "a": (4, 4, 4, 4, 3), "b": (3, 3, 4, 2, 3),
        "discriminator": "Patient indication and regimen duration favor A; construction/maintenance instructions favor B.",
    },
    "B2": {
        "section": "BIO", "page": "f82r", "count": 62,
        "range": "B:E167-B:E228",
        "a_role": "A local atlas of separate therapeutic bathing/application stations.",
        "b_role": "A modelbook of separate bathhouse, vessel, and conduit installations.",
        "a": (3, 3, 4, 4, 3), "b": (4, 4, 4, 2, 4),
        "discriminator": "Local ailments or prescribed exposure favor A; materials, dimensions, or repairs favor B.",
    },
    "B3": {
        "section": "BIO", "page": "f83r", "count": 86,
        "range": "B:E229-B:E314",
        "a_role": "Several independent treatment stations plus one genuine locally linked arch pair.",
        "b_role": "Several independent technical station drawings plus one genuinely connected installation pair.",
        "a": (3, 2, 3, 4, 3), "b": (4, 4, 4, 2, 4),
        "discriminator": "Repeated patient-state outcomes favor A; explicit mechanical interfaces favor B.",
    },
    "B4": {
        "section": "BIO", "page": "f83r", "count": 47,
        "range": "B:E315-B:E361",
        "a_role": "A main paired treatment station with disconnected left and right local stations.",
        "b_role": "A main apparatus pair with disconnected marginal installation studies.",
        "a": (3, 3, 3, 4, 3), "b": (4, 4, 4, 2, 4),
        "discriminator": "Therapeutic sequencing within the true pair favors A; component interaction favors B.",
    },
    "B5": {
        "section": "BIO", "page": "f83r", "count": 11,
        "range": "B:E362-B:E372",
        "a_role": "Independent left-tail therapeutic station article.",
        "b_role": "Independent left-tail technical station note.",
        "a": (2, 2, 3, 3, 3), "b": (3, 4, 3, 2, 4),
        "discriminator": "A bodily outcome favors A; a local assembly or service action favors B.",
    },
    "B6": {
        "section": "BIO", "page": "f83r", "count": 9,
        "range": "B:E373-B:E381",
        "a_role": "Independent right-tail therapeutic station article.",
        "b_role": "Independent right-tail technical station note.",
        "a": (2, 2, 3, 3, 3), "b": (3, 4, 3, 2, 4),
        "discriminator": "A bodily outcome favors A; a local assembly or service action favors B.",
    },
    "A1": {
        "section": "ASTRO", "page": "f67r2", "count": 190,
        "range": "A:G001-A:G190",
        "a_role": "Two independent celestial lookup instruments usable within a medical-calendar reference section.",
        "b_role": "Two independent cosmographic/calendar teaching or exemplar wheels.",
        "a": (4, 3, 4, 4, 3), "b": (4, 4, 4, 2, 4),
        "discriminator": "A stated diagnostic/timing operation favors A; copying, teaching, or ornament without use favors B.",
    },
    "A2": {
        "section": "ASTRO", "page": "f68r1", "count": 65,
        "range": "A:G191-A:G255",
        "a_role": "A multipanel star-field reference within an iatromathematical/calendrical section.",
        "b_role": "A multipanel celestial atlas or model sheet with local labels.",
        "a": (3, 3, 3, 4, 3), "b": (4, 4, 4, 2, 4),
        "discriminator": "A treatment/prognosis lookup rule favors A; independent descriptive labels favor B.",
    },
    "A3": {
        "section": "ASTRO", "page": "f69v", "count": 140,
        "range": "A:G256-A:G395",
        "a_role": "Three disconnected celestial reference wheels, only one with a local unordered 28-slot inventory.",
        "b_role": "Three independent celestial exemplar/model wheels, only one with a local 28-slot inventory.",
        "a": (3, 3, 3, 4, 3), "b": (4, 4, 4, 2, 4),
        "discriminator": "A practical computation or prognosis instruction favors A; autonomous copying/teaching labels favor B.",
    },
}


SOURCES = [
    {
        "source_id": "S01", "institution": "British Library", "shelfmark": "Egerton MS 2020",
        "date_place": "c.1390-1404; Padua/Italy", "genre": "illustrated medicinal herbal",
        "official_url": "https://searcharchives.bl.uk/catalog/032-001982947",
        "verified_features": "Italian Serapion herbal; numerous coloured plant miniatures; index; numerous reserved miniature spaces.",
        "supports_A": "Strong Herbal-section and learned-practical materia-medica mechanism.",
        "supports_B": "Illustrated natural-reference object and exemplar copying.",
        "production_evidence": "Reserved but unfilled miniature spaces prove planned image zones and an incomplete/mixed production campaign.",
        "limit": "Reserved spaces contradict any universal rule that pictures always preceded text; it is not a bath or celestial compendium.",
    },
    {
        "source_id": "S02", "institution": "British Library", "shelfmark": "Sloane MS 4016",
        "date_place": "c.1440; Lombardy", "genre": "image-dominant herbal",
        "official_url": "https://searcharchives.bl.uk/catalog/040-002116409",
        "verified_features": "Full-page plant miniatures on every folio with captions, sometimes with animals or people.",
        "supports_A": "An illustrated plant reference could serve materia medica.",
        "supports_B": "Especially strong for picture-led atlas/modelbook organization.",
        "production_evidence": "Image-dominant folio design with short dependent captions.",
        "limit": "No demonstrated bathing or celestial section and no proof of the target's exact production order.",
    },
    {
        "source_id": "S03", "institution": "Biblioteca Casanatense", "shelfmark": "MS 459 Historia Plantarum",
        "date_place": "late 14th century; Lombard court", "genre": "illustrated natural-science encyclopedia",
        "official_url": "https://casanatense.cultura.gov.it/en/activities/editorials/historia-plantarum-ms-459/",
        "verified_features": "Descriptions of plants, animals, and minerals with medical properties; over 500 illustrations and daily-life scenes.",
        "supports_A": "Natural substances and health knowledge could coexist in a learned medical reference.",
        "supports_B": "Strong courtly encyclopedic and image-atlas comparator.",
        "production_evidence": "Large coordinated illustrative campaign attributed in part to more than one artist.",
        "limit": "Does not supply the target's bathing-station or multiwheel celestial architecture.",
    },
    {
        "source_id": "S04", "institution": "Morgan Library & Museum", "shelfmark": "MS G.74 De balneis Puteolanis",
        "date_place": "c.1400; southern Italy", "genre": "illustrated therapeutic-baths catalogue",
        "official_url": "https://www.themorgan.org/manuscript/77063",
        "verified_features": "36 vellum leaves, 31 large and 6 small miniatures; local bath buildings, nude bathers, water handling, and individual bath scenes.",
        "supports_A": "Direct period mechanism for a sequence of locally distinct therapeutic bathing sites.",
        "supports_B": "The same site-by-site images can function as an architectural/topographic atlas.",
        "production_evidence": "Large image-and-text programme organized by distinct local baths.",
        "limit": "Its identifiable sites and conventional Latin text do not establish target meanings or a hydraulic network.",
    },
    {
        "source_id": "S05", "institution": "Wellcome Collection", "shelfmark": "MS.8515",
        "date_place": "c.1425; southern England", "genre": "practical computational science and astrological medicine manual",
        "official_url": "https://wellcomecollection.org/works/w9nkm98w",
        "verified_features": "Calendar, computus, planets, zodiacal administration of medicine, eclipse tables; later recipes in several hands.",
        "supports_A": "Very strong direct evidence that celestial/calendar material served medicine and later accumulated recipes.",
        "supports_B": "Also demonstrates a formal computational reference book with reusable diagrams/tables.",
        "production_evidence": "Core in one hand; recipes added by later hands and generations.",
        "limit": "No plant-picture series or bathing atlas and no correspondence to target wheel labels.",
    },
    {
        "source_id": "S06", "institution": "Wellcome Collection", "shelfmark": "MS.8932",
        "date_place": "c.1415-1420; England", "genre": "folding medical/astrological almanac",
        "official_url": "https://wellcomecollection.org/works/a2y8zd6x",
        "verified_features": "Calendar, astrological tables and diagrams, Zodiac Man, eclipse data; information usable for medical diagnosis and prognosis.",
        "supports_A": "Direct period evidence for a portable celestial/calendrical medical instrument.",
        "supports_B": "Luxurious diagrammatic object also compatible with display and learned consultation.",
        "production_evidence": "Compartmental folding design and coordinated multi-colour diagram programme.",
        "limit": "Different physical format; no Herbal or bath-station sequence.",
    },
    {
        "source_id": "S07", "institution": "British Library", "shelfmark": "Royal MS 17 A XVI",
        "date_place": "calendar for 1420; England", "genre": "pictorial astronomical almanac",
        "official_url": "https://searcharchives.bl.uk/catalog/040-002107247",
        "verified_features": "Pictorial calendar, zodiac signs, Zodiac Man, planetary/day volvelle, astronomical data, and later additions.",
        "supports_A": "Supports practical calendar/astrological consultation adjacent to bodily medicine.",
        "supports_B": "Strong comparator for autonomous illustrated celestial teaching/reference instruments.",
        "production_evidence": "Core pictorial calendar plus heterogeneous additions over time.",
        "limit": "No evidence that the target diagrams calculate the same quantities.",
    },
    {
        "source_id": "S08", "institution": "Bayerische Staatsbibliothek", "shelfmark": "Cod.icon. 242",
        "date_place": "1420-1430; Venice", "genre": "illustrated technical/artificialia book",
        "official_url": "https://www.digitale-sammlungen.de/de/details/bsb00013084",
        "verified_features": "72 vellum leaves; image-centred technical collection including hydraulic machines, fountains, vessels, instruments, and constructions.",
        "supports_A": "Only weakly: shows period technical apparatus that a practitioner might consult.",
        "supports_B": "Very strong mechanism for a heterogeneous image/modelbook of artificial works.",
        "production_evidence": "BSB classifies it among image manuscripts with little or explanatory text.",
        "limit": "A technical modelbook is not evidence that the target nude figures are machines, nor that plants or wheels belong to it.",
    },
    {
        "source_id": "S09", "institution": "Bayerische Staatsbibliothek", "shelfmark": "Clm 197,II, Taccola De ingeneis",
        "date_place": "c.1427-1441; Siena", "genre": "technical drawing/copy workshop book",
        "official_url": "https://www.digitale-sammlungen.de/de/details/bsb00113809",
        "verified_features": "136 paper leaves; Taccola among the scribes; pen drawings by Taccola and later sketches by Francesco di Giorgio.",
        "supports_A": "Weak general evidence for practitioner compilation and later reuse.",
        "supports_B": "Strong evidence for technical images, workshop copying, and multi-stage hands.",
        "production_evidence": "Author/scribe drawings plus later hand's sketches in the same physical object.",
        "limit": "Its engineering subject does not identify the target Bio or celestial content.",
    },
    {
        "source_id": "S10", "institution": "Wellcome Collection", "shelfmark": "MS.MSL.139",
        "date_place": "14th century; Europe", "genre": "modular medical compendium",
        "official_url": "https://wellcomecollection.org/works/ypdjvvqn",
        "verified_features": "Assembly of seven booklets containing health tables, antidotary commentary, simples lists, regimen, experiments, and fever text.",
        "supports_A": "Strong evidence that practical medical books were assembled from heterogeneous textual booklets.",
        "supports_B": "Some evidence for composite rather than authorially unified book structure.",
        "production_evidence": "Physically separate booklets and several hands in listed components.",
        "limit": "Date is broad; little support for image-first production or the specific three target sections.",
    },
    {
        "source_id": "S11", "institution": "Wellcome Collection", "shelfmark": "MS.105",
        "date_place": "before 1435; Germany", "genre": "medical and pharmacological compendium",
        "official_url": "https://wellcomecollection.org/works/abzgsvax",
        "verified_features": "General medical rules, food/drink, disease treatment, and preparation/properties of simple and compound drugs, preceded by contents.",
        "supports_A": "Direct period mechanism for a structured practitioner compendium spanning materia and treatment.",
        "supports_B": "Only general evidence for selective compilation from transmitted exemplars.",
        "production_evidence": "Copied as an organized sequence in a cursive Gothic hand.",
        "limit": "No illustrated bathing atlas or celestial wheel section.",
    },
    {
        "source_id": "S12", "institution": "British Library", "shelfmark": "Add MS 82946",
        "date_place": "1409-1431; England/Flanders", "genre": "Book of Hours with calendars and astronomical tables",
        "official_url": "https://searcharchives.bl.uk/catalog/032-000200122",
        "verified_features": "Devotional core, calendars, eclipse tables, circular astrological calendar, diagrams, and later texts in another campaign.",
        "supports_A": "Shows celestial reference matter could coexist with an otherwise different practical/devotional book.",
        "supports_B": "Shows heterogeneous image/text blocks can accumulate without one narrow workflow purpose.",
        "production_evidence": "Astronomical and textual additions belong to distinct stages/hands.",
        "limit": "Co-binding does not prove functional unity and gives no Herbal or baths analogue.",
    },
]


CONTRADICTIONS = [
    ("A01", PURPOSE_A, "ALL", "No verified period witness in the audit combines an illustrated Herbal, a local bath-station atlas, and several celestial instruments in this exact architecture.", "HIGH", "Treat A as a composite period-purpose model, never as a located source manuscript.", "OPEN"),
    ("A02", PURPOSE_A, "H1-H5", "Species, recipe media, doses, diseases, and exact actions remain unsupported source-class exemplars.", "HIGH", "Retain whole-plant owners and occurrence exemplars; add no portable form value.", "OPEN"),
    ("A03", PURPOSE_A, "B2-B6", "Disconnected Bio scenes and owner breaks resist a continuous treatment flow.", "HIGH", "Model a station atlas with local articles, not one page-wide regimen or substance.", "CONTAINED"),
    ("A04", PURPOSE_A, "A1-A3", "No visible rule connects the celestial instruments to diagnosis, treatment timing, or prognosis.", "HIGH", "Medical use is book-purpose context only; each wheel remains an anonymous local instrument.", "OPEN"),
    ("A05", PURPOSE_A, "ALL", "A physician, apothecary, bath practitioner, and calendar specialist may be too broad a single user.", "MEDIUM", "Prefer an institutional/household workshop or practitioner network over a lone polymath owner.", "OPEN"),
    ("A06", PURPOSE_A, "ALL", "Multiple hands could record copying history rather than specialist division of labor.", "MEDIUM", "Keep multi-scribe production compatible with both specialist and sequential copying models.", "OPEN"),
    ("B01", PURPOSE_B, "H1-H5", "The selected Herbal source-class articles are more recipe-like than captions or specimen labels.", "HIGH", "B must treat the recipe layer as a rival material protocol, not erase it.", "OPEN"),
    ("B02", PURPOSE_B, "B1-B6", "Nude figures actively bathing fit therapeutic/topographic bath literature better than a pure machine modelbook.", "HIGH", "B is an image atlas of natural/artificial stations, not a claim that bodies are machine parts.", "OPEN"),
    ("B03", PURPOSE_B, "ALL", "No visible natural/artificial/celestial taxonomy or section rubric proves an encyclopedic programme.", "HIGH", "Use the triad only as a purpose hypothesis explaining coexistence.", "OPEN"),
    ("B04", PURPOSE_B, "H1-B6", "Long local text groups are costlier than the short-caption economy of the strongest image-modelbook comparators.", "MEDIUM", "Allow operational annotations or copied exemplars rather than simple picture names.", "OPEN"),
    ("B05", PURPOSE_B, "B2-B6", "No visible arrows, dimensions, material labels, or stable hydraulic direction proves apparatus construction.", "HIGH", "Keep technical readings as local rivals only.", "OPEN"),
    ("B06", PURPOSE_B, "A1-A3", "Celestial diagrams can be working instruments rather than teaching/model sheets.", "MEDIUM", "Do not infer decorative or pedagogic use from geometry alone.", "OPEN"),
    ("S01", "SHARED", "ALL", "The target pages provide no verified readable source text, donor manuscript, codebook, nomenclator, or dictionary entry.", "CRITICAL", "No dictionary gloss was added anywhere in V76 R2.", "SEALED"),
    ("S02", "SHARED", "ALL", "The ten-page sample cannot establish original binding order or the purpose of the complete book.", "HIGH", "Limit conclusions to the fixed ten-page workshop sample.", "OPEN"),
    ("S03", "SHARED", "ALL", "Local text fitting around drawings supports target image-first planning but does not prove the order for every folio or section.", "HIGH", "State picture-first as a target working inference; period comparators show mixed production orders.", "CONTAINED"),
    ("S04", "SHARED", "A1-A3", "No common start, direction, rotation, f68-f69 key, or prose-card import is visible.", "CRITICAL", "Preserve three local instrument namespaces and no cross-page calculation.", "SEALED"),
]


WORKFLOW = [
    (1, "SOURCE_ACQUISITION", "Acquire separate Herbal/receptarium, baths/topographic-treatment, and calendar/astronomical exemplars.", "Acquire natural-specimen, bath/apparatus, and celestial model sheets from a workshop or patron's collection.", "Both models require more than one exemplar family; no direct donor is identified."),
    (2, "SECTION_PLANNING", "Plan three practitioner-reference blocks: materials, local treatment stations, and timing/prognostic instruments.", "Plan three image-atlas blocks: natural things, artificial/bathing works, and heavens.", "The fixed sample cannot recover original quire or binding order."),
    (3, "IMAGE_GEOMETRY", "Copy whole plants, local bathing scenes, and each celestial instrument as an independent visual owner before fitting its local text.", "Copy specimen, station/apparatus, and diagram exemplars first as reusable model images.", "This is the target-side picture-first working inference; it is not universalized to all medieval production."),
    (4, "LOCAL_TEXT_COPY", "Fit plant articles, station articles, and local instrument labels to the already allocated image geometry.", "Add operational notes, exemplar labels, and local captions to the already allocated image geometry.", "No opaque form receives a dictionary value; all content remains occurrence/source-class paraphrase."),
    (5, "HAND_DIVISION", "Different hands may divide section copying, diagram labeling, or later continuation within a practitioner workshop.", "Different hands may copy distinct model batches or revise/extend an atlas over time.", "Wellcome MS.8515, Taccola, and Add MS 82946 calibrate multi-stage use; they do not identify target hands' jobs."),
    (6, "ASSEMBLY", "Assemble fascicles as one therapeutic reference collection for an institution, household, or practitioner network.", "Assemble visual dossiers as a learned natural/artificial/celestial collection for teaching, copying, or consultation.", "A composite codex need not have one author or one moment of manufacture."),
    (7, "USE_AND_ADDITION", "Consult sections independently; later users could add recipes or corrections without creating cross-section keys.", "Consult/copy sections independently; later workshop users could add sketches or local annotations.", "No later-addition claim is made for a specific target event."),
]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def score_columns(values: tuple[int, int, int, int, int], prefix: str) -> dict[str, int]:
    visual, section, period, coexistence, production = values
    return {
        f"{prefix}_visual_fit_0_4": visual,
        f"{prefix}_selected_section_fit_0_4": section,
        f"{prefix}_period_mechanism_support_0_4": period,
        f"{prefix}_book_coexistence_fit_0_4": coexistence,
        f"{prefix}_production_fit_0_4": production,
        f"{prefix}_total_0_20": sum(values),
    }


def redact_unattested_mnemonics(literal: str) -> str:
    """Retain the opaque/formal provenance layer but never reprint old word mnemonics."""
    return re.sub(
        r"(?<!OPAQUE_)\[CARD:[^\]]+\]",
        "[PROVISIONAL_UNATTESTED_MNEMONIC_REDACTED]",
        literal,
    )


def normalize_old_status(status: str) -> str:
    if "MNEMONIC" in status:
        return "PROVISIONAL_UNATTESTED_MNEMONIC__SOURCE_STATUS_RETAINED_ONLY_AS_PROVENANCE"
    return status


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    h_events, b_events, a_events = read_tsv(H_EVENTS), read_tsv(B_EVENTS), read_tsv(A_EVENTS)
    h_units, b_units, a_units = read_tsv(H_UNITS), read_tsv(B_UNITS), read_tsv(A_UNITS)
    assert (len(h_events), len(b_events), len(a_events)) == (100, 281, 395)

    unit_source = {}
    for row in h_units:
        unit_source[row["record_unit_id"]] = {
            "selected_reading": row["fluent_article"],
            "source_rival": row["strongest_alternative_article"],
            "source_contradiction": row["strongest_contradiction"],
        }
    for row in b_units:
        unit_source[row["record_unit_id"]] = {
            "selected_reading": row["fluent_record_synopsis"],
            "source_rival": row["strongest_global_rival"],
            "source_contradiction": row["strongest_contradiction"],
        }
    for row in a_units:
        unit_source[row["diagram_id"]] = {
            "selected_reading": row["compact_historical_working_reading"],
            "source_rival": row["strongest_competing_instrument"],
            "source_contradiction": row["strongest_counterevidence"],
        }
    assert set(unit_source) == set(UNITS)

    bindings: list[dict[str, object]] = []
    serial = 0
    for section, rows in (("HERBAL", h_events), ("BIO", b_events), ("ASTRO", a_events)):
        for row in rows:
            serial += 1
            if section == "HERBAL":
                unit = row["record_unit_id"]
                source_row = f"E{int(row['event_serial']):03d}"
                opaque = row["joint_tuple_id"]
                owner = row["whole_plant_owner"]
                literal = redact_unattested_mnemonics(row["exact_literal_card_formal_exemplar_layer"])
                selected = row["concrete_german_meaning_in_context"]
                status = normalize_old_status(row["v69_support_class"])
                ceiling = row["semantic_ceiling"]
            elif section == "BIO":
                unit = row["record_unit_id"]
                source_row = f"E{int(row['event_serial']):03d}"
                opaque = row["joint_tuple_id"]
                owner = row["local_image_owner"]
                literal = redact_unattested_mnemonics(row["exact_literal_card_formal_exemplar_layer"])
                selected = row["concrete_german_meaning_in_context"]
                status = normalize_old_status(row["v69_source_status"])
                ceiling = row["semantic_ceiling"]
            else:
                unit = row["diagram_id"]
                source_row = f"G{int(row['group_serial']):03d}"
                opaque = row["opaque_local_id"]
                owner = row["local_image_owner"]
                literal = f"[LOCAL_CONTENT_CLASS:{row['local_content_class']}] [NAMESPACE:{row['local_namespace']}]"
                selected = row["copied_local_meaning_or_label"]
                status = row["copied_label_source_status"]
                ceiling = row["semantic_ceiling"]
            spec = UNITS[unit]
            bindings.append({
                "binding_serial": serial,
                "binding_id": f"V76R2:{section[0]}:{source_row}",
                "unit_id": unit,
                "section": section,
                "page": row["page"],
                "source_artifact": {"HERBAL": H_EVENTS.name, "BIO": B_EVENTS.name, "ASTRO": A_EVENTS.name}[section],
                "source_row_id": source_row,
                "opaque_identity": opaque,
                "local_image_owner": owner,
                "inherited_literal_or_formal_layer": literal,
                "inherited_selected_occurrence_context": selected,
                "inherited_source_status": status,
                "purpose_A_unit_role": spec["a_role"],
                "purpose_B_unit_role": spec["b_role"],
                "binding_status": "INHERITED_FROM_FROZEN_SELECTED_SECTION__NO_NEW_GROUP_VALUE",
                "codebook_attestation_status": "NO_DICTIONARY_GLOSS_ADDED",
                "cross_unit_inference_status": "BOOK_PURPOSE_LEVEL_ONLY__NO_GROUP_VALUE_TRANSFER",
                "source_semantic_ceiling": ceiling,
                "v76_semantic_ceiling": "BOOK_PURPOSE_BINDING_NOT_WORD_STEM_SOUND_LANGUAGE_OR_DECIPHERMENT",
            })
    assert serial == 776

    binding_fields = list(bindings[0])
    write_tsv(OUT / "V76_R2_776_GROUP_PURPOSE_BINDING.tsv", bindings, binding_fields)

    score_rows = []
    for unit_id, spec in UNITS.items():
        row: dict[str, object] = {
            "unit_id": unit_id, "section": spec["section"], "page": spec["page"],
            "group_count": spec["count"], "bound_group_range": spec["range"],
            "frozen_selected_section_reading": unit_source[unit_id]["selected_reading"],
            "purpose_A_unit_role": spec["a_role"],
            "purpose_B_unit_role": spec["b_role"],
        }
        row.update(score_columns(spec["a"], "A"))
        row.update(score_columns(spec["b"], "B"))
        row.update({
            "A_minus_B": sum(spec["a"]) - sum(spec["b"]),
            "unit_lead": "A" if sum(spec["a"]) > sum(spec["b"]) else "B" if sum(spec["b"]) > sum(spec["a"]) else "TIE",
            "strongest_discriminator": spec["discriminator"],
            "frozen_section_rival": unit_source[unit_id]["source_rival"],
            "frozen_section_contradiction": unit_source[unit_id]["source_contradiction"],
            "scoring_status": "TRANSPARENT_ORDINAL_HISTORICAL_DIAGNOSTIC_NOT_STATISTICAL_EVIDENCE",
        })
        score_rows.append(row)
    score_fields = list(score_rows[0])
    write_tsv(OUT / "V76_R2_14_UNIT_PURPOSE_SCORECARD.tsv", score_rows, score_fields)

    a_total = sum(int(r["A_total_0_20"]) for r in score_rows)
    b_total = sum(int(r["B_total_0_20"]) for r in score_rows)
    assert (a_total, b_total) == (236, 235)
    purpose_rows = [
        {
            "purpose_id": PURPOSE_A,
            "period_purpose": "Composite working reference for a medical household, institutional infirmary, or practitioner network: simples and preparations; locally distinct baths/applications; celestial/calendar consultation for timing or prognosis.",
            "practical_use": "Consult each block independently during identification/preparation, local treatment planning, and calendrical/iatromathematical consultation.",
            "compilation_order": "Separate Herbal, balneological, and celestial source fascicles or exemplar batches, then workshop assembly; no required cross-page key.",
            "picture_first_production": "On the target pages, image geometry is the working prior owner and text is fitted locally; this remains a target inference, not a universal medieval rule.",
            "multiple_scribes": "Plausibly section-specialized copying or sequential additions within a workshop/institution; not evidence for several authors or professions.",
            "source_exemplar_families": "Illustrated Herbal/receptarium; local bath-site or bathing regimen book; medical almanac/computus/astronomical reference.",
            "probable_user": "A physician/apothecary/bath practitioner network or learned household/infirmary, not necessarily one omniscient individual.",
            "why_sections_coexist": "Materials, treatment environments, and timing/prognosis form a historically coherent medical reference ecology.",
            "best_period_support": "S01/S04/S05/S06/S10/S11",
            "largest_forced_assumption": "No target-visible link makes the celestial instruments medical, and no exact three-section period witness was found.",
            "ordinal_total": a_total,
            "competition_result": "MARGINAL_ONE_POINT_LEAD__NOT_DECISIVE",
        },
        {
            "purpose_id": PURPOSE_B,
            "period_purpose": "Learned image atlas/modelbook of natural things, bathing/artificial works, and celestial diagrams for copying, teaching, classification, or consultation rather than a patient workflow.",
            "practical_use": "Reuse images and local annotations as specimen, station/apparatus, and celestial exemplars; sections need not share one algorithm.",
            "compilation_order": "Independent image batches gathered by a workshop or patron, locally annotated, and assembled as a broad visual dossier.",
            "picture_first_production": "Image exemplars are copied first and explanatory/local text is fitted into available space.",
            "multiple_scribes": "Distinct exemplar batches and later workshop reuse naturally admit multiple hands and stages.",
            "source_exemplar_families": "Image-dominant Herbal/natural encyclopedia; bath-site or technical/artificialia modelbook; celestial teaching/almanac diagrams.",
            "probable_user": "Courtly or urban learned household, artisan-engineer, teaching workshop, or collector of useful images.",
            "why_sections_coexist": "A broad natural/artificial/celestial survey explains heterogeneity without requiring clinical cross-links.",
            "best_period_support": "S02/S03/S04/S07/S08/S09/S12",
            "largest_forced_assumption": "No visible taxonomy labels the three blocks, and nude bathing scenes are more directly paralleled by therapeutic bath books than by pure machine books.",
            "ordinal_total": b_total,
            "competition_result": "NEAR_TIE__STRONGER_VISIBLE_AND_PRODUCTION_ECONOMY_IN_BIO_ASTRO",
        },
    ]
    write_tsv(OUT / "V76_R2_BOOK_PURPOSE_COMPETITION.tsv", purpose_rows, list(purpose_rows[0]))

    source_rows = []
    for src in SOURCES:
        source_rows.append({
            **src,
            "date_window_status": "BROAD_14C_TRANSMISSION_BACKGROUND" if src["source_id"] == "S10" else "WITHIN_OR_OVERLAPPING_C1370_1450",
            "codebook_or_lexical_use": "NONE__MECHANISM_CALIBRATION_ONLY",
            "audit_status": (
                "BROAD_DATE_BACKGROUND__NOT_DONOR_AND_NOT_IDENTITY_MATCH"
                if src["source_id"] == "S10"
                else "PERIOD_COMPARATOR__NOT_DONOR_AND_NOT_IDENTITY_MATCH"
            ),
        })
    write_tsv(OUT / "V76_R2_HISTORICAL_SOURCE_AUDIT.tsv", source_rows, list(source_rows[0]))

    workflow_rows = [
        {"stage": n, "stage_id": sid, "purpose_A_workflow": a, "purpose_B_workflow": b, "shared_guard": g}
        for n, sid, a, b, g in WORKFLOW
    ]
    write_tsv(OUT / "V76_R2_PRODUCTION_WORKFLOW.tsv", workflow_rows, list(workflow_rows[0]))

    contradiction_rows = [
        {
            "contradiction_id": cid, "model": model, "affected_units": units,
            "contradiction": issue, "severity": severity, "containment": containment,
            "status": status,
        }
        for cid, model, units, issue, severity, containment, status in CONTRADICTIONS
    ]
    write_tsv(OUT / "V76_R2_CONTRADICTIONS.tsv", contradiction_rows, list(contradiction_rows[0]))

    summary = {
        "status": "BUILT",
        "role": "R2_HISTORICAL_MEDICAL_HERBAL_SCRIBE",
        "fixed_pages": ["f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"],
        "units": len(UNITS),
        "groups_bound": len(bindings),
        "section_counts": {"HERBAL": len(h_events), "BIO": len(b_events), "ASTRO": len(a_events)},
        "purpose_A_ordinal_total": a_total,
        "purpose_B_ordinal_total": b_total,
        "competition": "NEAR_TIE__A_236__B_235__ORDINAL_DIAGNOSTIC_ONLY",
        "historical_sources": len(source_rows),
        "contradictions": len(contradiction_rows),
        "dictionary_glosses_added": 0,
        "codebook_entries_claimed": 0,
        "f84_access": False,
        "f84r_access": False,
    }
    (OUT / "V76_R2_BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

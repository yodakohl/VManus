#!/usr/bin/env python3
"""Independent live reconstruction of the Warburg circle metadata screen."""

from __future__ import annotations

import hashlib
import html
import json
import re
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
SPEC = ROOT / "WARBURG_SPECIAL_CIRCLE_METADATA_PRESCREEN_SPEC.md"
PRODUCER = ROOT / "check_warburg_special_circle_metadata_prescreen.py"
RESULT = RESULTS / "warburg_special_circle_metadata_prescreen.json"
REPORT = RESULTS / "warburg_special_circle_metadata_prescreen_report.md"
OUT = RESULTS / "warburg_special_circle_metadata_prescreen_validation.json"
OUT_MD = RESULTS / "warburg_special_circle_metadata_prescreen_validation_report.md"
SEARCH = "https://iconographic.warburg.sas.ac.uk/results"
OBJECT = "https://iconographic.warburg.sas.ac.uk/"
DURHAM = "https://reed.dur.ac.uk/xtf/view?docId=ark%2F32150_s28g84mm25j.xml"
FROZEN = {
    SPEC: "308f12fd1f53d8b3e1c18e7111d9e9f7f686c0c9f0a8a458842ee9fdd443bdd5",
    PRODUCER: "f01076de5cb2ecd3da6d6faaaad15d6032acda090d12a585e370f9cce696903e",
    RESULT: "2e4b7f15c397ac106498f06610937c321bc35b8538fca1684721ccc53b03c858",
    REPORT: "c5019f408100e843ba643bb785989fc770571eee3a4bd7b32a889a9060b38a4c",
}
COUNTS = {
    '"four seasons"': 24,
    '"four elements"': 9,
    "four seasons elements": 1,
    "four seasons figures": 2,
    "four seasons elements figures": 0,
    "Sun Moon stars": 30,
    "Sun Moon stars circle": 0,
    "Sun Moon stars ring": 0,
    "Sun Moon stars medallions": 0,
    "twelve winds": 18,
    "twelve winds circle": 0,
    "winds faces circle": 0,
    "winds personifications circle": 0,
    "wind heads circle": 0,
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def encoded(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def strict_result() -> dict[str, object]:
    raw = RESULT.read_bytes()

    def unique(pairs: list[tuple[str, object]]) -> dict[str, object]:
        keys = [key for key, _ in pairs]
        if len(keys) != len(set(keys)):
            raise ValueError("duplicate result key")
        return dict(pairs)

    value = json.loads(
        raw.decode("utf-8"),
        object_pairs_hook=unique,
        parse_constant=lambda token: (_ for _ in ()).throw(ValueError(token)),
    )
    if not isinstance(value, dict) or encoded(value) != raw:
        raise ValueError("noncanonical result")
    return value


def get(request: urllib.request.Request, url: str) -> str:
    with urllib.request.urlopen(request, timeout=60) as response:
        if response.status != 200 or response.geturl() != url or response.headers.get("Location") is not None:
            raise ValueError(f"unexpected response for {url}")
        return response.read().decode("utf-8")


def plain(markup: str) -> str:
    without = re.sub(r"<[^>]*>", " ", markup)
    return " ".join(html.unescape(without).split())


def run_query(query: str) -> dict[str, object]:
    payload = urllib.parse.urlencode(
        {"simple_search": query, "mi_adv_search": "no", "mi_search_type": "simple"}
    ).encode("ascii")
    request = urllib.request.Request(
        SEARCH,
        data=payload,
        method="POST",
        headers={"User-Agent": "VManus-Warburg-independent-validator/1"},
    )
    page = get(request, SEARCH)
    match = re.search(r'class="items-found">\s*([0-9,]+)&nbsp;items? found<', page)
    if match is None:
        raise ValueError(f"missing search total: {query}")
    count = int(match.group(1).replace(",", ""))
    cards = [
        {"object_id": object_id, "title": plain(title)}
        for object_id, title in re.findall(
            r'href="(object-wpc-wid-[a-z]+)"[^>]*>.*?class="card-header card-header-wrap">(.*?)</h2>',
            page,
            flags=re.DOTALL,
        )
    ]
    cards.sort(key=lambda row: str(row["object_id"]))
    if len(cards) != count or len({row["object_id"] for row in cards}) != count:
        raise ValueError(f"card orbit mismatch: {query}")
    return {"count": count, "records": cards}


def read_object(object_id: str) -> dict[str, object]:
    if re.fullmatch(r"object-wpc-wid-[a-z]+", object_id) is None:
        raise ValueError("bad object identifier")
    url = OBJECT + object_id
    page = get(
        urllib.request.Request(url, method="GET", headers={"User-Agent": "VManus-Warburg-independent-validator/1"}),
        url,
    )
    page = re.sub(r"<(?:script|style|form)\b[^>]*>.*?</(?:script|style|form)>", "", page, flags=re.I | re.S)
    title = re.search(r"<h1[^>]*>(.*?)</h1>", page, flags=re.I | re.S)
    if title is None:
        raise ValueError("missing object title")
    values = [plain(value) for value in re.findall(r'class="full_record_data_value"[^>]*>(.*?)</div>', page, flags=re.I | re.S)]
    values = [
        value for value in values
        if value and "licensed under a Creative Commons" not in value and not value.startswith("For comments or queries")
    ]
    if not values:
        raise ValueError("empty human catalogue projection")
    return {"object_id": object_id, "title": plain(title.group(1)), "public_url": url, "human_metadata_values": values}


def words(record: dict[str, object]) -> str:
    values = record["human_metadata_values"]
    if not isinstance(values, list):
        raise ValueError("human metadata type drift")
    return " ".join([str(record["title"]), *map(str, values)]).lower()


def found(text: str, expression: str) -> bool:
    return re.search(expression, text, flags=re.I) is not None


def gate67(record: dict[str, object]) -> dict[str, bool]:
    text = words(record)
    return {
        "explicit_twelve_wind_system": found(text, r"\btwelve winds\b|\btwelve-part wind\b"),
        "ring_circle_wheel_rota_or_rose": found(text, r"\bring\b|\bcircle\b|\bcircular\b|\bwheel\b|\brota\b|\bwind rose\b"),
        "explicit_readable_owned_text_sequence": found(text, r"\blabel|\bname[ds]?\b|\bcaption|\binscription|\btext sequence\b|\bowned\b"),
    }


def gate57(record: dict[str, object]) -> dict[str, bool]:
    text = words(record)
    return {
        "season_element_or_quality_relation": found(text, r"season") and found(text, r"element|qualit"),
        "four_human_figures": found(text, r"four (human )?(figures|portraits|philosophers|heads|faces)"),
        "explicit_owned_slot_or_register_relation": found(text, r"owned|slot|register|caption|inscription|labelled|labeled"),
    }


def gate68(record: dict[str, object]) -> dict[str, bool]:
    text = words(record)
    return {
        "sun_moon_stars": found(text, r"\bsun\b") and found(text, r"\bmoon\b") and found(text, r"\bstars?\b"),
        "ring_circle_or_annulus": found(text, r"\bring\b|\bcircle\b|\bcircular\b|\bannulus\b"),
        "explicit_text_ownership": found(text, r"\blabel|\bcaption|\binscription|\btext\b"),
        "upper_lower_relation": found(text, r"\bupper\b|\blower\b|\babove\b|\bbelow\b|\btop\b|\bbottom\b"),
    }


def durham() -> dict[str, object]:
    page = get(
        urllib.request.Request(DURHAM, method="GET", headers={"User-Agent": "VManus-Warburg-independent-validator/1"}),
        DURHAM,
    )
    page = re.sub(r"<(?:script|style)\b[^>]*>.*?</(?:script|style)>", "", page, flags=re.I | re.S)
    text = plain(page)
    facts = {
        "shelfmark_hunter_100": "Durham Cathedral Library MS. Hunter 100" in text,
        "durham_early_twelfth_century": "Written in England, Durham, early 12th century." in text,
        "four_element_quality_season_diagram": "Diagram of the harmony of the four elements, qualities, and seasons" in text,
    }
    if not all(facts.values()):
        raise ValueError("Durham record drift")
    return {"url": DURHAM, "facts": facts}


def main() -> None:
    if OUT.exists() or OUT_MD.exists():
        raise SystemExit("refusing to overwrite Warburg validation outputs")
    checks: list[str] = []
    for path, expected_hash in FROZEN.items():
        if digest(path.read_bytes()) != expected_hash:
            raise ValueError(f"frozen file mismatch: {path.name}")
        checks.append(f"sha256:{path.name}")
    source_result = strict_result()
    checks.append("canonical_duplicate_free_result")
    searches = {query: run_query(query) for query in COUNTS}
    observed_counts = {query: searches[query]["count"] for query in COUNTS}
    if observed_counts != COUNTS:
        raise ValueError("query-count drift")
    checks.extend(("fourteen_query_counts", "singular_and_plural_count_grammar", "result_card_orbits"))
    hunter_rows = searches["four seasons elements"]["records"]
    if not isinstance(hunter_rows, list) or [row["object_id"] for row in hunter_rows] != ["object-wpc-wid-aeeg"]:
        raise ValueError("Hunter query orbit drift")
    wind_rows = searches["twelve winds"]["records"]
    solar_rows = searches["Sun Moon stars"]["records"]
    if not isinstance(wind_rows, list) or not isinstance(solar_rows, list):
        raise ValueError("broad panel type drift")
    identifiers = sorted({str(row["object_id"]) for row in [*wind_rows, *solar_rows]})
    with ThreadPoolExecutor(max_workers=8) as workers:
        fetched = list(workers.map(read_object, identifiers))
    by_id = {str(row["object_id"]): row for row in fetched}
    if len(by_id) != len(identifiers):
        raise ValueError("object projection collision")
    wind = sorted((by_id[str(row["object_id"])] for row in wind_rows), key=lambda row: str(row["object_id"]))
    solar = sorted((by_id[str(row["object_id"])] for row in solar_rows), key=lambda row: str(row["object_id"]))
    hunter = read_object("object-wpc-wid-aeeg")
    checks.extend(("forty_eight_broad_object_records", "hunter_object_record", "human_metadata_values_only"))
    wind_classes = {"TWELVE_WIND_COSMOGRAPHY": [], "HOMERIC_WIND_SKINS": [], "OTHER": []}
    for record in wind:
        text = words(record)
        category = (
            "TWELVE_WIND_COSMOGRAPHY" if "geography / weather / winds / the twelve winds" in text
            else "HOMERIC_WIND_SKINS" if "twelve skins containing winds" in text
            else "OTHER"
        )
        wind_classes[category].append(record["object_id"])
    solar_classes = {"COSMOLOGICAL_SPHERES": [], "GENESIS_CREATION": [], "OTHER": []}
    for record in solar:
        text = words(record)
        category = (
            "COSMOLOGICAL_SPHERES" if "spheres with stars, sun and moon" in text
            else "GENESIS_CREATION" if "creation of sun, moon and stars" in text
            else "OTHER"
        )
        solar_classes[category].append(record["object_id"])
    if {key: len(value) for key, value in wind_classes.items()} != {"TWELVE_WIND_COSMOGRAPHY": 12, "HOMERIC_WIND_SKINS": 6, "OTHER": 0}:
        raise ValueError("wind class drift")
    if {key: len(value) for key, value in solar_classes.items()} != {"COSMOLOGICAL_SPHERES": 3, "GENESIS_CREATION": 26, "OTHER": 1}:
        raise ValueError("solar class drift")
    checks.extend(("wind_classes_12_6_0", "solar_classes_3_26_1"))
    wind_candidates = [record["object_id"] for record in wind if all(gate67(record).values())]
    solar_candidates = [record["object_id"] for record in solar if all(gate68(record).values())]
    hunter_gates = gate57(hunter)
    if wind_candidates or solar_candidates or all(hunter_gates.values()):
        raise ValueError("owned-topology candidate drift")
    checks.extend(("f67_zero_owned_candidates", "f57_incomplete_gate_vector", "f68_zero_owned_candidates"))
    durham_record = durham()
    checks.extend(("durham_shelfmark", "durham_date", "durham_diagram_description"))
    projection = {"searches": searches, "hunter": hunter, "f67_records": wind, "f68_records": solar, "durham": durham_record}
    expected = {
        "experiment": "WARBURG_SPECIAL_CIRCLE_METADATA_PRESCREEN",
        "status": "PASS_49_RECORD_HUMAN_METADATA_WORTH_SCREEN",
        "decision": "STOP_BEFORE_IMAGE_OR_PAPER_REVIEW_NO_EXACT_F67_F57_OR_F68_OWNED_TOPOLOGY",
        "source": {"publisher": "The Warburg Institute Iconographic Database", "search_url": SEARCH, "durham_catalogue_url": DURHAM, "stable_projection_sha256": digest(encoded(projection))},
        "query_counts": observed_counts,
        "f67": {"broad_record_count": len(wind), "class_counts": {key: len(value) for key, value in wind_classes.items()}, "class_object_ids": wind_classes, "exact_owned_topology_candidate_ids": wind_candidates},
        "f57": {"combined_query_object": {"object_id": hunter["object_id"], "title": hunter["title"], "public_url": hunter["public_url"]}, "gates": hunter_gates, "durham_confirmation": durham_record["facts"], "exact_owned_topology_candidate": False},
        "f68": {"broad_record_count": len(solar), "class_counts": {key: len(value) for key, value in solar_classes.items()}, "class_object_ids": solar_classes, "exact_owned_topology_candidate_ids": solar_candidates},
        "gates": {"human_catalogue_metadata_only": True, "f67_complete_owned_homologue_found": False, "f57_complete_owned_homologue_found": False, "f68_complete_owned_homologue_found": False, "escalate_to_image_manuscript_or_paper": False},
        "source_access": {"warburg_search_and_object_html_opened": True, "durham_catalogue_html_opened": True, "asset_thumbnail_zoom_iiif_or_image_opened": False, "manuscript_pdf_or_paper_body_opened": False, "ocr_or_automated_visual_output_used": False, "decoder_claims_opened": False},
        "inputs": {SPEC.name: FROZEN[SPEC]},
        "claim_ceiling": "At current human catalogue-metadata resolution, Warburg's complete 18-record twelve-winds result supplies no readable owned circular sequence, Warburg supplies one broad f57 diagram-family comparator (Durham Hunter 100) but no four-person owned two-register homologue, and its complete 30-record Sun-Moon-stars result supplies no f68r2 owned topology; no person, direction, season, element, quality, object, label, word, sound, language, cipher, plaintext, meaning, or translation follows.",
    }
    if source_result != expected:
        raise ValueError("exact result reconstruction mismatch")
    checks.extend(("stable_projection_digest", "exact_result_object", "exact_gate_vector"))
    expected_report = (
        "# Warburg special-circle metadata prescreen\n\n"
        "Decision: **STOP_BEFORE_IMAGE_OR_PAPER_REVIEW_NO_EXACT_F67_F57_OR_F68_OWNED_TOPOLOGY**.\n\n"
        "The complete `twelve winds` result contains 18 human catalogue records: 12 winds/cosmography records and six Homeric winds-in-skins records. None states both a circular arrangement and a readable owned label/name sequence; the narrower wind-circle, wind-face, wind-personification-circle, and wind-head-circle searches all return zero.\n\n"
        "The public Warburg simple-search catalogue returns 24 records for `four seasons`, nine for `four elements`, and one for the combined `four seasons elements` query. The sole combined record is Durham Cathedral Library Hunter 100, f.16v. Warburg describes correspondences among elements, seasons, humours, and four ages of man; Durham independently catalogues a diagram of the harmony of the four elements, qualities, and seasons. Neither record states four human figures or an owned two-register slot relation.\n\n"
        "The complete `Sun Moon stars` result contains 30 human catalogue records: three ordinary cosmological-sphere records, 26 Creation records, and one other emblem record. None states the required ring/circle, text ownership, and upper/lower relation together; the narrower circle, ring, and medallions searches all return zero.\n\n"
        "No asset, thumbnail, zoom image, IIIF manifest, manuscript, PDF, paper body, OCR, automated visual output, or decoder claim entered this screen. This is a catalogue-description stop, not proof that no undescribed image exists, and it supplies no person, direction, season, element, quality, astronomical object, label, word, sound, language, cipher, plaintext, meaning, or translation.\n"
    )
    if REPORT.read_text(encoding="utf-8") != expected_report:
        raise ValueError("exact report reconstruction mismatch")
    checks.append("exact_report_bytes")
    validation = {
        "experiment": "WARBURG_SPECIAL_CIRCLE_METADATA_PRESCREEN_VALIDATION",
        "status": "PASS_INDEPENDENT_49_RECORD_LIVE_METADATA_RECONSTRUCTION",
        "decision": source_result["decision"],
        "source_result_sha256": FROZEN[RESULT],
        "source_report_sha256": FROZEN[REPORT],
        "validator_sha256": digest(Path(__file__).read_bytes()),
        "check_count": len(checks),
        "checks": checks,
        "counts": {"queries": 14, "wind_records": 18, "hunter_records": 1, "sun_moon_star_records": 30, "exact_candidates": 0},
        "claim_ceiling": source_result["claim_ceiling"],
    }
    OUT.write_bytes(encoded(validation))
    OUT_MD.write_text(
        "# Warburg special-circle metadata prescreen — independent validation\n\n"
        f"Status: **{validation['status']}**.\n\n"
        f"All **{len(checks)}** checks pass. The validator independently repeats all 14 public catalogue queries, "
        "reconstructs the complete 18-record winds and 30-record Sun–Moon–stars panels plus Hunter 100, verifies the "
        "official Durham description, and reproduces the result and report exactly.\n\n"
        "This validates only the metadata stop before image or paper review. It supplies no person, direction, season, "
        "element, quality, astronomical object, label, word, sound, language, cipher, plaintext, meaning, or translation.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()

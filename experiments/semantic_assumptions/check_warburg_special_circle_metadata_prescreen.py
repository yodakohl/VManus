#!/usr/bin/env python3
"""Text-only Warburg metadata worth screen for f67, f57v, and f68r2."""

from __future__ import annotations

import hashlib
import html
import json
import re
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
SPEC = BASE / "WARBURG_SPECIAL_CIRCLE_METADATA_PRESCREEN_SPEC.md"
SEARCH_URL = "https://iconographic.warburg.sas.ac.uk/results"
OBJECT_BASE = "https://iconographic.warburg.sas.ac.uk/"
DURHAM_URL = "https://reed.dur.ac.uk/xtf/view?docId=ark%2F32150_s28g84mm25j.xml"
OUT_JSON = RESULTS / "warburg_special_circle_metadata_prescreen.json"
OUT_REPORT = RESULTS / "warburg_special_circle_metadata_prescreen_report.md"
QUERIES = (
    '"four seasons"',
    '"four elements"',
    "four seasons elements",
    "four seasons figures",
    "four seasons elements figures",
    "Sun Moon stars",
    "Sun Moon stars circle",
    "Sun Moon stars ring",
    "Sun Moon stars medallions",
    "twelve winds",
    "twelve winds circle",
    "winds faces circle",
    "winds personifications circle",
    "wind heads circle",
)
EXPECTED_COUNTS = {
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
HUNTER_ID = "object-wpc-wid-aeeg"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def fetch(request: urllib.request.Request, expected_url: str) -> bytes:
    with urllib.request.urlopen(request, timeout=60) as response:
        if response.status != 200 or response.geturl() != expected_url or response.headers.get("Location"):
            raise ValueError(f"unexpected response: {expected_url}")
        return response.read()


def normalize_markup(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", value))).strip()


def search(query: str) -> dict[str, object]:
    body = urllib.parse.urlencode({
        "simple_search": query,
        "mi_adv_search": "no",
        "mi_search_type": "simple",
    }).encode("ascii")
    request = urllib.request.Request(
        SEARCH_URL,
        data=body,
        method="POST",
        headers={"User-Agent": "VManus-Warburg-metadata-prescreen/1"},
    )
    page = fetch(request, SEARCH_URL).decode("utf-8")
    count_match = re.search(r'<div class="items-found">\s*([0-9,]+)&nbsp;items? found</div>', page)
    if count_match is None:
        raise ValueError(f"missing result count: {query}")
    count = int(count_match.group(1).replace(",", ""))
    rows = []
    for object_id, title in re.findall(
        r'<a href="(object-[^"]+)">.*?<h2 class="card-header card-header-wrap">(.*?)</h2>',
        page,
        re.DOTALL,
    ):
        rows.append({"object_id": object_id, "title": normalize_markup(title)})
    rows.sort(key=lambda row: str(row["object_id"]))
    if len(rows) != count or len({row["object_id"] for row in rows}) != count:
        raise ValueError(f"result-card orbit mismatch: {query}")
    return {"count": count, "records": rows}


def object_record(object_id: str) -> dict[str, object]:
    if not re.fullmatch(r"object-wpc-wid-[a-z]+", object_id):
        raise ValueError("unexpected Warburg object ID")
    url = OBJECT_BASE + object_id
    request = urllib.request.Request(url, method="GET", headers={"User-Agent": "VManus-Warburg-metadata-prescreen/1"})
    page = fetch(request, url).decode("utf-8")
    page = re.sub(r"<(script|style|form)\b.*?</\1>", "", page, flags=re.DOTALL | re.IGNORECASE)
    title_match = re.search(r"<h1>(.*?)</h1>", page, re.DOTALL | re.IGNORECASE)
    if not title_match:
        raise ValueError(f"missing object title: {object_id}")
    values = []
    for match in re.finditer(r'<div class="full_record_data_value"[^>]*>(.*?)</div>', page, re.DOTALL | re.IGNORECASE):
        value = normalize_markup(match.group(1))
        if not value or "licensed under a Creative Commons" in value or value.startswith("For comments or queries"):
            continue
        values.append(value)
    if not values:
        raise ValueError(f"missing human metadata: {object_id}")
    return {
        "object_id": object_id,
        "title": normalize_markup(title_match.group(1)),
        "public_url": url,
        "human_metadata_values": values,
    }


def record_text(record: dict[str, object]) -> str:
    values = record["human_metadata_values"]
    if not isinstance(values, list):
        raise ValueError("record metadata schema drift")
    return " ".join([str(record["title"]), *[str(value) for value in values]]).lower()


def term(text: str, pattern: str) -> bool:
    return bool(re.search(pattern, text, re.IGNORECASE))


def f57_gates(record: dict[str, object]) -> dict[str, bool]:
    text = record_text(record)
    return {
        "season_element_or_quality_relation": term(text, r"season") and term(text, r"element|qualit"),
        "four_human_figures": term(text, r"four (human )?(figures|portraits|philosophers|heads|faces)"),
        "explicit_owned_slot_or_register_relation": term(text, r"owned|slot|register|caption|inscription|labelled|labeled"),
    }


def f67_gates(record: dict[str, object]) -> dict[str, bool]:
    text = record_text(record)
    return {
        "explicit_twelve_wind_system": term(text, r"\btwelve winds\b|\btwelve-part wind\b"),
        "ring_circle_wheel_rota_or_rose": term(text, r"\bring\b|\bcircle\b|\bcircular\b|\bwheel\b|\brota\b|\bwind rose\b"),
        "explicit_readable_owned_text_sequence": term(text, r"\blabel|\bname[ds]?\b|\bcaption|\binscription|\btext sequence\b|\bowned\b"),
    }


def f68_gates(record: dict[str, object]) -> dict[str, bool]:
    text = record_text(record)
    return {
        "sun_moon_stars": term(text, r"\bsun\b") and term(text, r"\bmoon\b") and term(text, r"\bstars?\b"),
        "ring_circle_or_annulus": term(text, r"\bring\b|\bcircle\b|\bcircular\b|\bannulus\b"),
        "explicit_text_ownership": term(text, r"\blabel|\bcaption|\binscription|\btext\b"),
        "upper_lower_relation": term(text, r"\bupper\b|\blower\b|\babove\b|\bbelow\b|\btop\b|\bbottom\b"),
    }


def f68_class(record: dict[str, object]) -> str:
    text = record_text(record)
    if "spheres with stars, sun and moon" in text:
        return "COSMOLOGICAL_SPHERES"
    if "creation of sun, moon and stars" in text:
        return "GENESIS_CREATION"
    return "OTHER"


def f67_class(record: dict[str, object]) -> str:
    text = record_text(record)
    if "geography / weather / winds / the twelve winds" in text:
        return "TWELVE_WIND_COSMOGRAPHY"
    if "twelve skins containing winds" in text:
        return "HOMERIC_WIND_SKINS"
    return "OTHER"


def durham_confirmation() -> dict[str, object]:
    request = urllib.request.Request(DURHAM_URL, method="GET", headers={"User-Agent": "VManus-Warburg-metadata-prescreen/1"})
    page = fetch(request, DURHAM_URL).decode("utf-8")
    page = re.sub(r"<(script|style)\b.*?</\1>", "", page, flags=re.DOTALL | re.IGNORECASE)
    text = normalize_markup(page)
    facts = {
        "shelfmark_hunter_100": "Durham Cathedral Library MS. Hunter 100" in text,
        "durham_early_twelfth_century": "Written in England, Durham, early 12th century." in text,
        "four_element_quality_season_diagram": "Diagram of the harmony of the four elements, qualities, and seasons" in text,
    }
    if not all(facts.values()):
        raise ValueError("Durham catalogue confirmation drift")
    return {"url": DURHAM_URL, "facts": facts}


def main() -> None:
    if OUT_JSON.exists() or OUT_REPORT.exists():
        raise SystemExit("refusing to overwrite Warburg prescreen outputs")
    searches = {query: search(query) for query in QUERIES}
    counts = {query: searches[query]["count"] for query in QUERIES}
    if counts != EXPECTED_COUNTS:
        raise ValueError(f"Warburg query count drift: {counts}")
    combined_rows = searches["four seasons elements"]["records"]
    if not isinstance(combined_rows, list) or [row["object_id"] for row in combined_rows] != [HUNTER_ID]:
        raise ValueError("unexpected f57 combined-query result")
    broad_rows = searches["Sun Moon stars"]["records"]
    if not isinstance(broad_rows, list):
        raise ValueError("unexpected f68 result schema")
    wind_rows = searches["twelve winds"]["records"]
    if not isinstance(wind_rows, list):
        raise ValueError("unexpected f67 result schema")
    ids = sorted({str(row["object_id"]) for row in [*broad_rows, *wind_rows]})
    with ThreadPoolExecutor(max_workers=8) as pool:
        fetched_records = list(pool.map(object_record, ids))
    fetched_by_id = {str(row["object_id"]): row for row in fetched_records}
    if len(fetched_by_id) != len(ids):
        raise ValueError("duplicate fetched Warburg object")
    f68_records = [fetched_by_id[str(row["object_id"])] for row in broad_rows]
    f68_records.sort(key=lambda row: str(row["object_id"]))
    f67_records = [fetched_by_id[str(row["object_id"])] for row in wind_rows]
    f67_records.sort(key=lambda row: str(row["object_id"]))
    hunter = object_record(HUNTER_ID)
    f67_gate_rows = [{"object_id": row["object_id"], "gates": f67_gates(row)} for row in f67_records]
    f67_candidates = [row["object_id"] for row in f67_gate_rows if all(row["gates"].values())]
    f67_classes = {name: [] for name in ("TWELVE_WIND_COSMOGRAPHY", "HOMERIC_WIND_SKINS", "OTHER")}
    for record in f67_records:
        f67_classes[f67_class(record)].append(record["object_id"])
    if {name: len(value) for name, value in f67_classes.items()} != {"TWELVE_WIND_COSMOGRAPHY": 12, "HOMERIC_WIND_SKINS": 6, "OTHER": 0}:
        raise ValueError("f67 broad-panel classification drift")
    hunter_gates = f57_gates(hunter)
    f68_gate_rows = [{"object_id": row["object_id"], "gates": f68_gates(row)} for row in f68_records]
    f68_candidates = [row["object_id"] for row in f68_gate_rows if all(row["gates"].values())]
    classes = {name: [] for name in ("COSMOLOGICAL_SPHERES", "GENESIS_CREATION", "OTHER")}
    for record in f68_records:
        classes[f68_class(record)].append(record["object_id"])
    if {name: len(value) for name, value in classes.items()} != {"COSMOLOGICAL_SPHERES": 3, "GENESIS_CREATION": 26, "OTHER": 1}:
        raise ValueError("f68 broad-panel classification drift")
    if f67_candidates or f68_candidates or all(hunter_gates.values()):
        raise ValueError("metadata target unexpectedly passed")
    durham = durham_confirmation()
    stable_projection = {
        "searches": searches,
        "hunter": hunter,
        "f67_records": f67_records,
        "f68_records": f68_records,
        "durham": durham,
    }
    result = {
        "experiment": "WARBURG_SPECIAL_CIRCLE_METADATA_PRESCREEN",
        "status": "PASS_49_RECORD_HUMAN_METADATA_WORTH_SCREEN",
        "decision": "STOP_BEFORE_IMAGE_OR_PAPER_REVIEW_NO_EXACT_F67_F57_OR_F68_OWNED_TOPOLOGY",
        "source": {
            "publisher": "The Warburg Institute Iconographic Database",
            "search_url": SEARCH_URL,
            "durham_catalogue_url": DURHAM_URL,
            "stable_projection_sha256": sha(canonical(stable_projection)),
        },
        "query_counts": counts,
        "f67": {
            "broad_record_count": len(f67_records),
            "class_counts": {name: len(value) for name, value in f67_classes.items()},
            "class_object_ids": f67_classes,
            "exact_owned_topology_candidate_ids": f67_candidates,
        },
        "f57": {
            "combined_query_object": {"object_id": hunter["object_id"], "title": hunter["title"], "public_url": hunter["public_url"]},
            "gates": hunter_gates,
            "durham_confirmation": durham["facts"],
            "exact_owned_topology_candidate": False,
        },
        "f68": {
            "broad_record_count": len(f68_records),
            "class_counts": {name: len(value) for name, value in classes.items()},
            "class_object_ids": classes,
            "exact_owned_topology_candidate_ids": f68_candidates,
        },
        "gates": {
            "human_catalogue_metadata_only": True,
            "f67_complete_owned_homologue_found": False,
            "f57_complete_owned_homologue_found": False,
            "f68_complete_owned_homologue_found": False,
            "escalate_to_image_manuscript_or_paper": False,
        },
        "source_access": {
            "warburg_search_and_object_html_opened": True,
            "durham_catalogue_html_opened": True,
            "asset_thumbnail_zoom_iiif_or_image_opened": False,
            "manuscript_pdf_or_paper_body_opened": False,
            "ocr_or_automated_visual_output_used": False,
            "decoder_claims_opened": False,
        },
        "inputs": {SPEC.name: sha(SPEC.read_bytes())},
        "claim_ceiling": "At current human catalogue-metadata resolution, Warburg's complete 18-record twelve-winds result supplies no readable owned circular sequence, Warburg supplies one broad f57 diagram-family comparator (Durham Hunter 100) but no four-person owned two-register homologue, and its complete 30-record Sun-Moon-stars result supplies no f68r2 owned topology; no person, direction, season, element, quality, object, label, word, sound, language, cipher, plaintext, meaning, or translation follows.",
    }
    OUT_JSON.write_bytes(canonical(result))
    OUT_REPORT.write_text(
        "# Warburg special-circle metadata prescreen\n\n"
        "Decision: **STOP_BEFORE_IMAGE_OR_PAPER_REVIEW_NO_EXACT_F67_F57_OR_F68_OWNED_TOPOLOGY**.\n\n"
        "The complete `twelve winds` result contains 18 human catalogue records: 12 winds/cosmography records and "
        "six Homeric winds-in-skins records. None states both a circular arrangement and a readable owned label/name "
        "sequence; the narrower wind-circle, wind-face, wind-personification-circle, and wind-head-circle searches all "
        "return zero.\n\n"
        "The public Warburg simple-search catalogue returns 24 records for `four seasons`, nine for `four elements`, "
        "and one for the combined `four seasons elements` query. The sole combined record is Durham Cathedral Library "
        "Hunter 100, f.16v. Warburg describes correspondences among elements, seasons, humours, and four ages of man; "
        "Durham independently catalogues a diagram of the harmony of the four elements, qualities, and seasons. Neither "
        "record states four human figures or an owned two-register slot relation.\n\n"
        "The complete `Sun Moon stars` result contains 30 human catalogue records: three ordinary cosmological-sphere "
        "records, 26 Creation records, and one other emblem record. None states the required ring/circle, text ownership, "
        "and upper/lower relation together; the narrower circle, ring, and medallions searches all return zero.\n\n"
        "No asset, thumbnail, zoom image, IIIF manifest, manuscript, PDF, paper body, OCR, automated visual output, or "
        "decoder claim entered this screen. This is a catalogue-description stop, not proof that no undescribed image "
        "exists, and it supplies no person, direction, season, element, quality, astronomical object, label, word, sound, language, "
        "cipher, plaintext, meaning, or translation.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()

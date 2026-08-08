#!/usr/bin/env python3
"""Build an active atlas from existing human Voynich annotations.

Inputs are cached human prose and manual transcription comments only.  The
builder opens no manuscript image, uses no OCR, and performs no automated
vision.  It preserves source assertions and marks rule-extracted tags as
indexes rather than as authorial truth.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import time
import urllib.request
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
ARCHIVE = ROOT / "archive_pre_reset_2026-08-06" / "semantic_assumptions"

CATALOGUE_CACHE = ARCHIVE / "cache" / "gheuens_rapaport_traits"
EVT_SOURCE = ROOT / "transcription" / "sources" / "Stolfi_text25e1-52.evt"
STOLFI_LINES = ROOT / "transcription" / "voynich_stolfi25e1_lines.tsv"
STRUCTURAL_LINES = ROOT / "transcription" / "voynich_zl3b_lines.tsv"
ZL_SOURCE = ROOT / "transcription" / "sources" / "ZL3b-n.txt"
RF_SOURCE = ROOT / "transcription" / "sources" / "RF1b-e.txt"
IT_SOURCE = ROOT / "transcription" / "sources" / "IT2a-n.txt"
PAGE_CENSUS = RESULTS / "document_role_page_census.tsv"
LABEL_INDEX_CACHE = HERE / "cache" / "existing_human_annotations" / "labtit-best.idx"

PAGE_OUT = RESULTS / "existing_human_page_annotations.tsv"
LOCUS_ROLE_OUT = RESULTS / "existing_human_locus_roles.tsv"
LOCUS_OUT = RESULTS / "existing_human_exact_locus_annotations.tsv"
LABEL_OUT = RESULTS / "existing_human_label_annotations.tsv"
MANIFEST_OUT = RESULTS / "existing_human_annotation_atlas.json"
REPORT_OUT = RESULTS / "existing_human_annotation_atlas_report.md"

CATALOGUE_URLS = {
    path.stem: f"https://www.voynich.nu/{path.stem}/index.html"
    for path in sorted(CATALOGUE_CACHE.glob("q*.html"))
}
STOLFI_BEST_LABEL_URL = (
    "https://www.ic.unicamp.br/~stolfi/PUB/EXPORT/voynich/Notes/107/"
    "work/Notes/614/labtit-best.idx"
)

PAGE_RE = re.compile(r"f\d+[rv]\d*", re.I)
UNIT_RE = re.compile(r"^# Unit <(f\d+[rv]\d*)\.([^>]+)>:\s*(.*)$")
LOCUS_RE = re.compile(r"^<(f\d+[rv]\d*)\.([^;>]+);([^>]+)>\s*(.*)$")
IVTFF_LOCUS_CODE_RE = re.compile(r"^<([^,>]+),([^>]+)>")
LEGACY_LABEL_PAGE_IDS = {"f101v1", "f101v2", "f86r4"}

SECTION_FIELDS = {
    "general description": "general_description",
    "illustration(s)": "illustrations",
    "text": "text_description",
    "tentative identifications": "tentative_identifications",
    "other information": "other_information",
}

PAGE_TAG_PATTERNS = {
    "SOURCE_TEXT_ONLY_PAGE": re.compile(r"\btext[- ]only page\b|\bno illustrations\b", re.I),
    "SOURCE_HERBAL_PAGE": re.compile(r"\bherbal page\b", re.I),
    "SOURCE_COSMOLOGICAL_PAGE": re.compile(r"\bcosmological page\b", re.I),
    "SOURCE_ZODIAC_PAGE": re.compile(r"\bzodiac\b", re.I),
    "SOURCE_BIOLOGICAL_OR_BATH_PAGE": re.compile(r"\bbiological\b|\bbalneological\b|\bbath", re.I),
    "SOURCE_PHARMACEUTICAL_PAGE": re.compile(r"\bpharmaceutical page\b", re.I),
    "SOURCE_RECIPE_OR_STAR_ENTRY_PAGE": re.compile(r"\brecipes? section\b|\bstarred paragraphs?\b", re.I),
    "TEXT_PARAGRAPHS": re.compile(r"\bparagraphs?\b", re.I),
    "TEXT_LABELS": re.compile(r"\blabels?\b", re.I),
    "TEXT_TITLES": re.compile(r"\btitles?\b", re.I),
    "TEXT_CIRCULAR": re.compile(r"\bcircular text\b|\btext .* circle\b|\btext .* ring\b", re.I),
    "TEXT_RADIAL": re.compile(r"\bradial text\b|\bradially\b", re.I),
    "TEXT_LIST_OR_SEQUENCE": re.compile(r"\blists?\b|\bsequence of\b|\bseries of\b", re.I),
    "TEXT_AVOIDS_GRAPHIC": re.compile(r"\btext (?:carefully )?avoids?\b|\bwriting avoids?\b", re.I),
    "TEXT_WRAPS_GRAPHIC": re.compile(r"\btext (?:wraps?|runs?) around\b|\bwritten around\b", re.I),
    "TEXT_INSIDE_GRAPHIC": re.compile(r"\btext (?:is )?(?:inside|within)\b|\bwritten inside\b", re.I),
    "TEXT_BETWEEN_GRAPHICS": re.compile(r"\btext .* between\b|\bblock .* between\b", re.I),
}

OBJECT_TAG_PATTERNS = {
    "FIGURE": re.compile(r"\b(?:nymphs?|women|woman|female|male|men|man|persons?|figures?)\b", re.I),
    "PLANT": re.compile(r"\b(?:plants?|roots?|leaves|leaf|flowers?|stems?|tubers?|bulbs?|berries)\b", re.I),
    "WATER_OR_APPARATUS": re.compile(
        r"\b(?:water|pools?|ponds?|tubs?|tubes?|tubing|barrels?|funnels?|"
        r"waterfalls?|channels?|streams?|pipes?|pipelines?|rivulets?)\b",
        re.I,
    ),
    "STAR_OR_SKY": re.compile(r"\b(?:stars?|moons?|suns?|zodiac|constellations?|planets?)\b", re.I),
    "ROSETTE_OR_MAP": re.compile(r"\b(?:rosettes?|towers?|roads?|doorways?|castles?|bridges?)\b", re.I),
    "ANIMAL": re.compile(r"\b(?:animals?|rams?|armadillos?|birds?|fish)\b", re.I),
    "LABEL": re.compile(r"\blabels?\b", re.I),
}

RELATION_TAG_PATTERNS = {
    "REL_EXPLICIT_ATTACHMENT": re.compile(r"\b(?:attached to|label on|labels on|written on)\b", re.I),
    "REL_ENCLOSURE": re.compile(r"\b(?:inside|within|enclosed by|in the circle|in circle)\b", re.I),
    "REL_OVERLAP_OR_CONTACT": re.compile(r"\b(?:covered by|runs? into|touch(?:es|ing)?|cross(?:es|ing))\b", re.I),
    "REL_TEXT_WRAP_OR_INTERRUPTION": re.compile(r"\b(?:wraps? around|written around|separated by the plant|interrupted by)\b", re.I),
    "REL_ARRAY_OR_GROUP": re.compile(r"\b(?:row of labels|group of labels|labels near|labels associated|set of labels|words?.*nymphs?)\b", re.I),
    "REL_PROXIMITY": re.compile(r"\b(?:near|next to|above|below|left of|right of|east of|west of|between)\b", re.I),
}

HEDGE_RE = re.compile(
    r"\?|\b(?:may|might|could|possibly|perhaps|probably|probable|likely|"
    r"seems?|appears?|presum(?:e|ed|ably)|assum(?:e|ed)|tentative|"
    r"ambiguous|uncertain|unclear|unsure)\b|\bnot clear\b",
    re.I,
)

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def normalized_text(parts: Iterable[str]) -> str:
    return re.sub(r"\s+", " ", " ".join(parts).replace("\xa0", " ")).strip()


def certainty(text: str) -> str:
    return "HEDGED" if HEDGE_RE.search(text) else "UNHEDGED"


def tags(text: str, patterns: dict[str, re.Pattern[str]]) -> list[str]:
    return [name for name, pattern in patterns.items() if pattern.search(text)]


def write_tsv(path: Path, fields: list[str], rows: Iterable[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def fetch_bytes(url: str) -> bytes:
    request = urllib.request.Request(
        url, headers={"User-Agent": "VManus human-annotation provenance audit"}
    )
    with urllib.request.urlopen(request, timeout=45) as response:
        return response.read()


def ensure_label_index(refresh: bool) -> bytes:
    if refresh or not LABEL_INDEX_CACHE.exists():
        data = fetch_bytes(STOLFI_BEST_LABEL_URL)
        LABEL_INDEX_CACHE.parent.mkdir(parents=True, exist_ok=True)
        LABEL_INDEX_CACHE.write_bytes(data)
    return LABEL_INDEX_CACHE.read_bytes()


class FolioCatalogueParser(HTMLParser):
    def __init__(self, quire: str) -> None:
        super().__init__(convert_charrefs=True)
        self.quire = quire
        self.page = ""
        self.heading = ""
        self.capture = ""
        self.parts: list[str] = []
        self.records: dict[str, dict[str, Any]] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key.lower(): value for key, value in attrs}
        lowered = tag.lower()
        if lowered == "th" and values.get("id"):
            candidate = str(values["id"]).lower()
            if PAGE_RE.fullmatch(candidate):
                self.page = candidate
                self.records.setdefault(candidate, {
                    "page": candidate, "quire": self.quire,
                    **{field: [] for field in SECTION_FIELDS.values()},
                })
        if lowered in {"h4", "p"}:
            self.capture = lowered
            self.parts = []
        elif lowered == "br" and self.capture:
            self.parts.append(" ")

    def handle_data(self, data: str) -> None:
        if self.capture:
            self.parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        lowered = tag.lower()
        if lowered != self.capture:
            return
        text = normalized_text(self.parts)
        self.capture = ""
        self.parts = []
        if lowered == "h4":
            self.heading = text.lower()
            return
        field = SECTION_FIELDS.get(self.heading)
        if field and self.page and text and text.lower() not in {"&nbsp;", "none"}:
            self.records[self.page][field].append(text)


def folio_sort_key(page: str) -> tuple[int, str]:
    match = re.match(r"f(\d+)", page)
    return (int(match.group(1)) if match else 10**9, page)


def parse_catalogue() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    records: dict[str, dict[str, Any]] = {}
    sources = []
    for path in sorted(CATALOGUE_CACHE.glob("q*.html")):
        data = path.read_bytes()
        parser = FolioCatalogueParser(path.stem)
        parser.feed(data.decode("utf-8", errors="replace"))
        for page, record in parser.records.items():
            target = records.setdefault(page, {
                "page": page, "quire": record["quire"],
                **{field: [] for field in SECTION_FIELDS.values()},
            })
            for field in SECTION_FIELDS.values():
                target[field].extend(record[field])
        sources.append({
            "source_id": path.stem, "url": CATALOGUE_URLS[path.stem],
            "path": str(path.relative_to(ROOT)), "bytes": len(data),
            "sha256": sha256_bytes(data), "pages": len(parser.records),
        })
    output = []
    for page in sorted(records, key=folio_sort_key):
        source = records[page]
        row = {
            "page": page, "quire": source["quire"],
            **{
                field: " || ".join(dict.fromkeys(source[field]))
                for field in SECTION_FIELDS.values()
            },
        }
        role_text = normalized_text([
            row["general_description"], row["illustrations"], row["text_description"],
        ])
        row["source_tags"] = ";".join(tags(role_text, PAGE_TAG_PATTERNS))
        row["source_url"] = f"{CATALOGUE_URLS[source['quire']]}#{page}"
        row["tentative_identifications_are_role_evidence"] = 0
        output.append(row)
    return output, sources


def line_crosswalk() -> dict[str, dict[str, str]]:
    with STOLFI_LINES.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    return {row["source_locus"].lower(): row for row in rows}


def parse_structural_locus_roles() -> list[dict[str, Any]]:
    """Copy only human editorial locus metadata, never Voynich strings."""
    with STRUCTURAL_LINES.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    fields = [
        "page_order", "page", "locus", "line_number", "code", "relation",
        "kind", "subtype", "section", "language", "hand", "quire",
        "folio_type", "paragraph_start", "paragraph_end", "token_count",
    ]
    source_path = str(STRUCTURAL_LINES.relative_to(ROOT))
    return [
        {**{field: row[field] for field in fields}, "source_path": source_path}
        for row in rows
    ]


def ivtff_locus_codes(path: Path) -> dict[str, str]:
    output = {}
    for raw_line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        match = IVTFF_LOCUS_CODE_RE.match(raw_line)
        if match:
            output[match.group(1).lower()] = match.group(2)
    return output


def parse_evt_comments() -> list[dict[str, Any]]:
    crosswalk = line_crosswalk()
    output = []
    page = unit = unit_description = ""
    pending: list[str] = []
    for line in EVT_SOURCE.read_text(encoding="utf-8", errors="replace").splitlines():
        page_match = re.match(r"^@@\s+(f\d+[rv]\d*)\s*$", line)
        if page_match:
            page = page_match.group(1).lower()
            pending = []
            continue
        unit_match = UNIT_RE.match(line)
        if unit_match:
            page = unit_match.group(1).lower()
            unit = unit_match.group(2)
            unit_description = unit_match.group(3).strip()
            pending = []
            continue
        if line.startswith("#"):
            value = line[1:].strip()
            if value and not value.startswith("===") and value != "[ONE-LEG GALLOWS CHECKED]":
                pending.append(value)
            continue
        match = LOCUS_RE.match(line)
        if not match:
            continue
        local_comment = normalized_text(pending)
        pending = []
        source_locus = f"{match.group(1)}.{match.group(2)}".lower()
        active = crosswalk.get(source_locus, {})
        combined = normalized_text([unit_description, local_comment])
        object_tags = tags(combined, OBJECT_TAG_PATTERNS)
        if not object_tags:
            continue
        local_relation_tags = tags(local_comment, RELATION_TAG_PATTERNS)
        unit_relation_tags = tags(unit_description, RELATION_TAG_PATTERNS)
        relation_scope = (
            "EXACT_LOCAL_COMMENT" if local_relation_tags
            else "UNIT_DESCRIPTION" if unit_relation_tags
            else "OBJECT_CONTEXT_ONLY"
        )
        output.append({
            "page": page,
            "locus": active.get("locus", source_locus),
            "source_locus": source_locus,
            "old_locus": active.get("old_locus", ""),
            "unit": unit,
            "normalized_code": active.get("code", ""),
            "unit_description": unit_description,
            "local_comment": local_comment,
            "object_tags": ";".join(object_tags),
            "context_class": (
                "OBJECT_BEARING"
                if any(tag != "LABEL" for tag in object_tags)
                else "LABEL_ONLY"
            ),
            "local_relation_tags": ";".join(local_relation_tags),
            "unit_relation_tags": ";".join(unit_relation_tags),
            "relation_scope": relation_scope,
            "certainty": certainty(local_comment if local_relation_tags else combined),
            "source_path": str(EVT_SOURCE.relative_to(ROOT)),
        })
    return output


def label_attribute_tags(text: str) -> list[str]:
    patterns = {
        "FACING_LEFT": r"\bfacing left\b", "FACING_RIGHT": r"\bfacing right\b",
        "FACING_FORWARD": r"\bfacing forward\b", "FACING_AWAY": r"\bfacing away\b",
        "MALE": r"\bmale\??\b", "FEMALE": r"\bfemale\??\b|\bwoman\b|\bwomen\b",
        "CROWN": r"\b(?:crown|crowned)\b", "HAT": r"\bhat\b",
        "DRESSED": r"\bdressed\??\b", "STAR_TAIL": r"\bstar with tail\b|\btailed star\b",
        "COLORED_STAR": r"\bcolou?red star\b", "VERTICAL_BARREL": r"\bvert\.? barrel\b",
        "HORIZONTAL_BARREL": r"\bhor\.? barrel\b",
        "HOLDING_PROP": r"\b(?:holding|holds?|with (?:a )?(?:towel|keyring|ring|object))\b",
        "NYMPH": r"\bnymph\??\b", "DUCT": r"\bduct\??\b|\btubes?\b|\bpipes?\b",
        "FLOW": r"\bflow\??\b|\bwaterfalls?|waterflows?|streams?\b",
        "ORGAN": r"\borgan\??\b", "PLANT": r"\bplants?\??\b|\broots?\??\b|\bleaves|leaf\b",
        "STAR": r"\bstars?\b", "MOON": r"\bmoons?\b", "DARK": r"\bdark\b",
        "LIGHT": r"\blight\b",
    }
    return [name for name, pattern in patterns.items() if re.search(pattern, text, re.I)]


def parse_best_label_index(data: bytes) -> list[dict[str, Any]]:
    """Parse Stolfi's one-best-reading machine-readable label/title index."""
    output = []
    for line_number, raw_line in enumerate(
        data.decode("utf-8", errors="replace").splitlines(), 1
    ):
        fields = raw_line.split("|")
        if len(fields) != 11:
            raise ValueError(f"label index line {line_number}: expected 11 fields")
        (
            source_id, section, page, unit, item, transcriber_code, _voynich_text,
            _alternate_text, object_class, object_guess, comments,
        ) = fields
        description = normalized_text([object_guess, comments])
        output.append({
            "source_record_id": f"STOLFI_BEST_{source_id}",
            "section": section,
            "page": page.lower(),
            "legacy_page_id_needs_alias": int(page.lower() in LEGACY_LABEL_PAGE_IDS),
            "location": f"{page}.{unit}.{item}".lower(),
            "transcriber_code": transcriber_code,
            "object_guess": object_guess,
            "object_class": object_class,
            "comments": comments,
            "attribute_tags": ";".join(label_attribute_tags(description)),
            "certainty": certainty(description),
            "source_url": STOLFI_BEST_LABEL_URL,
        })
    return output


def live_check(source_id: str, url: str, expected_hash: str) -> dict[str, Any]:
    request = urllib.request.Request(url, headers={"User-Agent": "VManus human-annotation provenance audit"})
    try:
        data = fetch_bytes(url)
        live_hash = sha256_bytes(data)
        return {"source_id": source_id, "url": url, "status": "MATCH" if live_hash == expected_hash else "DIFF", "cached_sha256": expected_hash, "live_sha256": live_hash}
    except Exception as error:  # network failure is explicit, never silently a match
        return {"source_id": source_id, "url": url, "status": "FETCH_ERROR", "cached_sha256": expected_hash, "error": f"{type(error).__name__}: {error}"}


def verify_live(
    catalogue_sources: list[dict[str, Any]], label_index_hash: str
) -> list[dict[str, Any]]:
    jobs = [
        (source["source_id"], source["url"], source["sha256"])
        for source in catalogue_sources
    ]
    jobs.append((
        "stolfi_best_label_index", STOLFI_BEST_LABEL_URL, label_index_hash
    ))
    results = []
    with ThreadPoolExecutor(max_workers=min(32, len(jobs))) as executor:
        futures = {executor.submit(live_check, *job): job[0] for job in jobs}
        for future in as_completed(futures):
            results.append(future.result())
    return sorted(results, key=lambda row: row["source_id"])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify-live", action="store_true")
    parser.add_argument("--refresh-label-index", action="store_true")
    args = parser.parse_args()
    started = time.perf_counter()
    label_index_data = ensure_label_index(args.refresh_label_index)
    pages, catalogue_sources = parse_catalogue()
    locus_roles = parse_structural_locus_roles()
    loci = parse_evt_comments()
    labels = parse_best_label_index(label_index_data)
    zl_codes = ivtff_locus_codes(ZL_SOURCE)
    rf_codes = ivtff_locus_codes(RF_SOURCE)
    it_codes = ivtff_locus_codes(IT_SOURCE)
    with PAGE_CENSUS.open(encoding="utf-8", newline="") as handle:
        census = list(csv.DictReader(handle, delimiter="\t"))
    active_pages = {row["page"] for row in census}
    catalogue_pages = {row["page"] for row in pages}
    exact_active_coverage = active_pages & catalogue_pages

    page_fields = [
        "page", "quire", "general_description", "illustrations", "text_description",
        "tentative_identifications", "other_information", "source_tags", "source_url",
        "tentative_identifications_are_role_evidence",
    ]
    locus_fields = [
        "page", "locus", "source_locus", "old_locus", "unit", "normalized_code",
        "unit_description", "local_comment", "object_tags", "context_class",
        "local_relation_tags", "unit_relation_tags", "relation_scope", "certainty",
        "source_path",
    ]
    locus_role_fields = [
        "page_order", "page", "locus", "line_number", "code", "relation",
        "kind", "subtype", "section", "language", "hand", "quire",
        "folio_type", "paragraph_start", "paragraph_end", "token_count",
        "source_path",
    ]
    label_fields = [
        "source_record_id", "section", "page", "legacy_page_id_needs_alias",
        "location", "transcriber_code", "object_guess", "object_class", "comments",
        "attribute_tags", "certainty", "source_url",
    ]
    write_tsv(PAGE_OUT, page_fields, pages)
    write_tsv(LOCUS_ROLE_OUT, locus_role_fields, locus_roles)
    write_tsv(LOCUS_OUT, locus_fields, loci)
    write_tsv(LABEL_OUT, label_fields, labels)

    label_index_hash = sha256_bytes(label_index_data)
    live = verify_live(catalogue_sources, label_index_hash) if args.verify_live else []
    exact_local_relations = [
        row for row in loci
        if row["relation_scope"] == "EXACT_LOCAL_COMMENT" and row["certainty"] == "UNHEDGED"
    ]
    tag_counts = Counter(
        tag for row in pages for tag in row["source_tags"].split(";") if tag
    )
    structural_kind_counts = Counter(row["kind"] for row in locus_roles)
    local_relation_row_counts = Counter()
    for row in exact_local_relations:
        for relation_tag in row["local_relation_tags"].split(";"):
            if relation_tag:
                local_relation_row_counts[relation_tag] += 1
    strong_local_tags = {
        "REL_EXPLICIT_ATTACHMENT", "REL_ENCLOSURE", "REL_OVERLAP_OR_CONTACT",
        "REL_TEXT_WRAP_OR_INTERRUPTION", "REL_ARRAY_OR_GROUP",
    }
    exact_unhedged_strong_rows = [
        row for row in exact_local_relations
        if strong_local_tags.intersection(row["local_relation_tags"].split(";"))
    ]
    result = {
        "status": "PASS_EXISTING_HUMAN_ANNOTATION_REUSE_SCOPED",
        "correction": (
            "new manual labeling is not the next action for the source-only role pass; "
            "existing public annotation was overlooked"
        ),
        "coverage": {
            "active_page_records": len(active_pages),
            "catalogue_page_records": len(pages),
            "exact_active_page_matches": len(exact_active_coverage),
            "active_pages_without_exact_catalogue_id": sorted(active_pages - catalogue_pages),
            "catalogue_wrapper_ids_not_active_pages": sorted(catalogue_pages - active_pages),
            "pages_with_general_description": sum(bool(row["general_description"]) for row in pages),
            "pages_with_illustration_description": sum(bool(row["illustrations"]) for row in pages),
            "pages_with_text_description": sum(bool(row["text_description"]) for row in pages),
            "page_source_tag_counts": dict(sorted(tag_counts.items())),
            "structural_locus_rows": len(locus_roles),
            "structural_locus_pages": len({row["page"] for row in locus_roles}),
            "structural_locus_kind_counts": dict(sorted(structural_kind_counts.items())),
            "zl_rf_exact_locus_code_matches": sum(
                zl_codes[locus] == rf_codes[locus]
                for locus in zl_codes.keys() & rf_codes.keys()
            ),
            "zl_rf_locus_code_differences": sum(
                zl_codes[locus] != rf_codes[locus]
                for locus in zl_codes.keys() & rf_codes.keys()
            ),
            "zl_it_shared_loci": len(zl_codes.keys() & it_codes.keys()),
            "zl_it_exact_locus_code_matches": sum(
                zl_codes[locus] == it_codes[locus]
                for locus in zl_codes.keys() & it_codes.keys()
            ),
            "evt_indexed_context_rows": len(loci),
            "evt_object_bearing_context_rows": sum(
                row["context_class"] == "OBJECT_BEARING" for row in loci
            ),
            "evt_label_only_context_rows": sum(
                row["context_class"] == "LABEL_ONLY" for row in loci
            ),
            "exact_locus_pages": len({row["page"] for row in loci}),
            "exact_unhedged_local_relation_rows": len(exact_local_relations),
            "exact_unhedged_local_relation_pages": len({row["page"] for row in exact_local_relations}),
            "exact_unhedged_local_relation_tag_row_counts": dict(
                sorted(local_relation_row_counts.items())
            ),
            "exact_unhedged_strong_local_relation_rows": len(exact_unhedged_strong_rows),
            "exact_unhedged_strong_local_relation_pages": len({
                row["page"] for row in exact_unhedged_strong_rows
            }),
            "best_label_title_records": len(labels),
            "best_label_title_pages": len({row["page"] for row in labels}),
            "best_label_title_tagged_records": sum(bool(row["attribute_tags"]) for row in labels),
            "best_label_title_proposed_title_records": sum(
                "title" in row["object_guess"].lower() for row in labels
            ),
            "best_label_title_legacy_page_ids_needing_alias": sorted(
                {row["page"] for row in labels if row["legacy_page_id_needs_alias"]}
            ),
        },
        "sources": {
            "voynich_nu_catalogue": catalogue_sources,
            "stolfi_evt": {"path": str(EVT_SOURCE.relative_to(ROOT)), "sha256": sha256_file(EVT_SOURCE)},
            "stolfi_line_crosswalk": {"path": str(STOLFI_LINES.relative_to(ROOT)), "sha256": sha256_file(STOLFI_LINES)},
            "zl3b_structural_loci": {"path": str(STRUCTURAL_LINES.relative_to(ROOT)), "sha256": sha256_file(STRUCTURAL_LINES)},
            "zl3b_ivtff": {"path": str(ZL_SOURCE.relative_to(ROOT)), "sha256": sha256_file(ZL_SOURCE)},
            "rf1b_ivtff": {"path": str(RF_SOURCE.relative_to(ROOT)), "sha256": sha256_file(RF_SOURCE)},
            "it2a_ivtff": {"path": str(IT_SOURCE.relative_to(ROOT)), "sha256": sha256_file(IT_SOURCE)},
            "stolfi_best_label_index": {"url": STOLFI_BEST_LABEL_URL, "path": str(LABEL_INDEX_CACHE.relative_to(ROOT)), "sha256": label_index_hash},
        },
        "live_verification": live,
        "live_all_match": bool(live) and all(row["status"] == "MATCH" for row in live),
        "evidence_rules": [
            "P/L/C/R is a complete ZL3b/RF1b editorial locus-role layer, not object ownership or authorial semantics",
            "page and text-layout prose is source-level human description, not authorial semantics",
            "tentative identifications are preserved but excluded from document-role evidence",
            "page and relation tags are nonexhaustive regex indexes into retained source prose",
            "exact unhedged local comments outrank unit descriptions",
            "proximity remains distinct from attachment",
            "the 1998 best label/title index is a described legacy subset, not the current 1029-L-locus inventory",
            "legacy split-page identifiers remain flagged until an explicit current-locus crosswalk is applied",
            "VIB is a renderer of the same Stolfi archive and is not an independent witness",
        ],
        "manual_reannotation_required_for_current_source_only_role_pass": False,
        "best_label_title_index_asserted_complete_or_current": False,
        "complete_author_independent_object_ownership": False,
        "image_pixels_or_automated_vision_used": False,
        "ocr_used": False,
        "semantic_or_grammar_score_computed": False,
        "runtime_seconds": time.perf_counter() - started,
    }
    result["artifact_hashes"] = {
        str(path.relative_to(ROOT)): sha256_file(path)
        for path in (PAGE_OUT, LOCUS_ROLE_OUT, LOCUS_OUT, LABEL_OUT)
    }
    MANIFEST_OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    coverage = result["coverage"]
    report = "\n".join([
        "# Existing human-annotation atlas", "",
        "Decision: **PASS_EXISTING_HUMAN_ANNOTATION_REUSE_SCOPED**.", "",
        "Creating a new 47-page annotation set before using the public metadata was unnecessary. Existing human work supplies manuscript-wide editorial locus roles, a near-complete page catalogue, page-level text-layout descriptions, and useful but incomplete label/comment layers.", "",
        "| human source layer | coverage | admissible use |",
        "|---|---:|---|",
        f"| voynich.nu categorized folio prose | {coverage['exact_active_page_matches']}/{coverage['active_page_records']} exact active page IDs | page type, illustration description, and text-layout assertions |",
        f"| current IVTFF metadata | {coverage['structural_locus_rows']} loci on {coverage['structural_locus_pages']} pages | complete editorial P/L/C/R locus role; ZL3b and RF1b codes match at every locus |",
        f"| Stolfi 25e1 exact comments | {coverage['evt_object_bearing_context_rows']} object-bearing plus {coverage['evt_label_only_context_rows']} label-only regex-indexed loci on {coverage['exact_locus_pages']} pages | exact or unit-scoped source comments with hedging retained; absence is unknown |",
        f"| Stolfi 1998 best label/title index | {coverage['best_label_title_records']} legacy records on {coverage['best_label_title_pages']} source page IDs | described subset with human class/guess/attributes; not the current complete label inventory |",
        "", f"Text-layout prose is present for **{coverage['pages_with_text_description']}** catalogue records; the older local inventory had accidentally omitted this entire named source field.", "",
        f"Of **{coverage['exact_unhedged_local_relation_rows']}** unhedged exact-local relation rows, **{coverage['exact_unhedged_local_relation_tag_row_counts'].get('REL_PROXIMITY', 0)}** use proximity language and only **{coverage['exact_unhedged_strong_local_relation_rows']}** contain a stronger attachment, enclosure, contact, wrap, or grouping assertion; these tag counts overlap. They remain source assertions, not automatic ownership truth.", "",
        f"The current metadata has **{coverage['structural_locus_kind_counts']['L']}** `L` loci. The older Stolfi file's **{coverage['best_label_title_records']}** records are a different labels-plus-proposed-titles inventory (including **{coverage['best_label_title_proposed_title_records']}** title guesses), so the totals must not be subtracted or treated as one-to-one coverage. Legacy page IDs `{', '.join(coverage['best_label_title_legacy_page_ids_needing_alias'])}` remain explicitly flagged.", "",
        f"Live verification: **{'all cached human sources match their canonical live bytes' if result['live_all_match'] else 'not all sources were live-verified'}**.", "",
        "The sole active page ID without a literal catalogue counterpart is `fRos`; the catalogue describes the compound 85/86 foldout through its component/wrapper entries, so that mapping must be explicit rather than silently duplicated.", "",
        "This atlas replaces new labeling only as the immediate source-gathering action. It does not provide complete paragraph-to-object ownership; missing ownership remains unknown because the user has ruled out a new manual pass. Modern descriptions are not authorial meanings.", "",
        "No manuscript image, OCR, automated vision, excluded old-scan coordinate, grammar feature, or semantic score was used.", "",
    ])
    REPORT_OUT.write_text(report, encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

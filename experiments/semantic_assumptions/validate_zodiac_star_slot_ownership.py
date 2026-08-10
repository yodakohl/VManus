#!/usr/bin/env python3
"""Clean-room validation of the public zodiac star-slot ownership audit."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path

BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
CACHE = BASE / "cache" / "public_voynich_nu_catalogue"
PRODUCER = BASE / "audit_zodiac_star_slot_ownership.py"
PUBLIC = RESULTS / "public_voynich_nu_page_annotations_v2.tsv"
ROLE_ATLAS = RESULTS / "public_circle_block_role_atlas.tsv"
ROLE_ATLAS_JSON = RESULTS / "public_circle_block_role_atlas.json"
ROLE_ATLAS_VALIDATION = RESULTS / "public_circle_block_role_atlas_validation.json"
META = RESULTS / "source_separator_transcription.tsv"
STOLFI = BASE / "cache" / "existing_human_annotations" / "labtit-best.idx"
TARGET_TSV = RESULTS / "zodiac_star_slot_ownership.tsv"
TARGET_JSON = RESULTS / "zodiac_star_slot_ownership.json"
TARGET_REPORT = RESULTS / "zodiac_star_slot_ownership_report.md"
OUT = RESULTS / "zodiac_star_slot_ownership_validation.json"
OUT_REPORT = RESULTS / "zodiac_star_slot_ownership_validation.md"

PAGES = (
    "f70v2", "f70v1", "f71r", "f71v", "f72r1", "f72r2",
    "f72r3", "f72v3", "f72v2", "f72v1", "f73r", "f73v",
)
READINGS = ("ZL3b", "IT2a", "RF1b")
SIGN_RE = re.compile(
    r"\bemblem of (Pisces|Aries|Taurus|Gemini|Cancer|Leo|Virgo|Libra|Scorpius|Sagittarius)\b",
    re.I,
)
FIGURE_RE = re.compile(r"\bThere are (\d+)(?: figures)? in total\b", re.I)
LABEL_RE = re.compile(r"\b(\d+) zodiac labels\b", re.I)
NEAR_RE = re.compile(r"\b(\d+) of the zodiac labels are near the small human figures\b", re.I)
PAGE_RE = re.compile(r"f\d+[rv]\d*", re.I)
FOLIO_RE = re.compile(r"f\d+", re.I)
FIELDS = {
    "general description": "general_description",
    "illustration(s)": "illustrations",
    "text": "text_description",
    "tentative identifications": "tentative_identifications",
    "other information": "other_information",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tsv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def normalized(parts: list[str]) -> str:
    return re.sub(r"\s+", " ", " ".join(parts).replace("\xa0", " ")).strip()


class PublicParser(HTMLParser):
    def __init__(self, quire: str) -> None:
        super().__init__(convert_charrefs=True)
        self.quire = quire
        self.page = ""
        self.heading = ""
        self.container = ""
        self.text: list[str] = []
        self.records: dict[str, dict[str, object]] = {}

    def handle_starttag(self, tag: str, attrs) -> None:
        tag = tag.lower()
        values = {key.lower(): value for key, value in attrs}
        identifier = str(values.get("id") or "").lower()
        if tag == "th" and identifier:
            if PAGE_RE.fullmatch(identifier):
                self.page = identifier
                self.records.setdefault(
                    identifier,
                    {"page": identifier, "quire": self.quire, **{field: [] for field in FIELDS.values()}},
                )
            elif FOLIO_RE.fullmatch(identifier):
                self.page = ""
        if tag in ("h4", "p"):
            self.container = tag
            self.text = []
        elif tag == "br" and self.container:
            self.text.append(" ")

    def handle_data(self, data: str) -> None:
        if self.container:
            self.text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() != self.container:
            return
        value = normalized(self.text)
        container = self.container
        self.container = ""
        self.text = []
        if container == "h4":
            self.heading = value.lower()
            return
        field = FIELDS.get(self.heading)
        if field and self.page and value and value.lower() not in ("&nbsp;", "none"):
            self.records[self.page][field].append(value)


def star_figure_count(text: str, count: int) -> int:
    lower = text.lower()
    if "with one exception" in lower and "all holding a star" in lower:
        return count - 1
    if "each one is holding a star" in lower or "they are all holding a star" in lower:
        return count
    raise AssertionError("star grammar")


def main() -> None:
    if OUT.exists() or OUT_REPORT.exists():
        raise SystemExit("refusing overwrite")
    checks = 0

    def check(value: bool, name: str) -> None:
        nonlocal checks
        checks += 1
        if not value:
            raise AssertionError(name)

    public_stored = {row["page"]: row for row in tsv_rows(PUBLIC)}
    raw_public: dict[str, dict[str, object]] = {}
    raw_sources = [CACHE / name for name in ("q10.html", "q11.html", "q12.html")]
    for path in raw_sources:
        parser = PublicParser(path.stem)
        parser.feed(path.read_text(encoding="utf-8", errors="replace"))
        raw_public.update(parser.records)
    check(all(page in raw_public and page in public_stored for page in PAGES), "public page coverage")
    for page in PAGES:
        raw = raw_public[page]
        for field in FIELDS.values():
            value = " || ".join(dict.fromkeys(raw[field]))
            check(value == public_stored[page][field], f"raw public {page} {field}")

    meta_rows = tsv_rows(META)
    distinct_loci: dict[tuple[str, str], set[str]] = {
        (page, reading): set() for page in PAGES for reading in READINGS
    }
    for row in meta_rows:
        if row["page"] in PAGES and row["edition"] in READINGS and row["kind"] == "L":
            distinct_loci[(row["page"], row["edition"])].add(row["locus"])
    role_atlas_rows = tsv_rows(ROLE_ATLAS)
    atlas_l = {
        (row["page"], row["reading"]): int(row["locus_count"])
        for row in role_atlas_rows
        if row["page"] in PAGES and row["ivtff_role"] == "L"
    }
    check(set(atlas_l) == set(distinct_loci), "L cell universe")
    for key in sorted(atlas_l):
        check(atlas_l[key] == len(distinct_loci[key]), "raw L count " + "|".join(key))

    raw_stolfi = []
    for line in STOLFI.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        fields = line.split("|")
        check(len(fields) == 11, "Stolfi field count")
        raw_stolfi.append(fields)
    missing_zodiac = [row for row in raw_stolfi if row[1] == "zodiac" and "not labeled" in row[10].lower()]
    check(len(missing_zodiac) == 1, "one zodiac missing label")
    check(missing_zodiac[0][:10] == ["0606", "zodiac", "f72r2", "S", "23", "V", "-", "-", "Z", "day?"], "missing identity")
    check("outer, #14" in missing_zodiac[0][10], "missing position")

    reconstructed = []
    label_counts = {}
    for page in PAGES:
        row = public_stored[page]
        sign = SIGN_RE.search(row["illustrations"])
        figure = FIGURE_RE.search(row["illustrations"])
        label = LABEL_RE.search(row["text_description"])
        check(bool(sign and figure and label), "parsed " + page)
        figures = int(figure.group(1))
        star_figures = star_figure_count(row["illustrations"], figures)
        labels = int(label.group(1))
        label_counts[page] = labels
        extra = int("The 30th is near one of the central stars" in row["text_description"])
        near = NEAR_RE.search(row["text_description"])
        reconstructed.append({
            "page": page,
            "physical_folio": re.match(r"f\d+", page).group(0),
            "public_sign": sign.group(1).upper(),
            "public_figure_count": figures,
            "public_star_holding_figure_count": star_figures,
            "public_label_count": labels,
            "explicit_near_figure_label_count": int(near.group(1)) if near else "",
            "explicit_nonfigure_star_label_count": extra,
            "star_slot_prediction": star_figures + extra,
            "figure_count_residual_labels_minus_figures": labels - figures,
            "star_slot_residual_labels_minus_prediction": labels - star_figures - extra,
            "all_reading_ivtff_L_count": labels,
            "explicit_unlabelled_nonstar_figure": int(page == "f72r2"),
        })
        for reading in READINGS:
            check(len(distinct_loci[(page, reading)]) == labels, f"label/L {page} {reading}")

    stored_tsv = tsv_rows(TARGET_TSV)
    check(len(stored_tsv) == len(reconstructed), "stored rows")
    check(list(stored_tsv[0]) == list(reconstructed[0]), "stored header")
    for stored, expected in zip(stored_tsv, reconstructed, strict=True):
        check(stored == {key: str(value) for key, value in expected.items()}, "stored row " + expected["page"])

    figure_matches = sum(row["figure_count_residual_labels_minus_figures"] == 0 for row in reconstructed)
    star_matches = sum(row["star_slot_residual_labels_minus_prediction"] == 0 for row in reconstructed)
    exceptions = [row for row in reconstructed if row["figure_count_residual_labels_minus_figures"] != 0]
    check(figure_matches == 10, "figure 10/12")
    check(star_matches == 12, "star 12/12")
    check([(row["page"], row["figure_count_residual_labels_minus_figures"]) for row in exceptions] == [("f70v2", 1), ("f72r2", -1)], "opposite exceptions")
    check(len({row["physical_folio"] for row in exceptions}) == 2, "different folios")

    gates = {
        "all_12_public_zodiac_pages_present": len(reconstructed) == 12,
        "all_36_ivtff_L_counts_equal_public_label_counts": all(
            len(distinct_loci[(page, reading)]) == label_counts[page]
            for page in PAGES for reading in READINGS
        ),
        "figure_count_model_has_two_opposite_exceptions": figure_matches == 10 and [
            row["figure_count_residual_labels_minus_figures"] for row in exceptions
        ] == [1, -1],
        "star_slot_model_matches_all_pages": star_matches == 12,
        "f70v2_has_explicit_label_near_nonfigure_central_star": reconstructed[0]["explicit_nonfigure_star_label_count"] == 1,
        "f72r2_has_exact_public_unlabelled_nonstar_figure": next(row for row in reconstructed if row["page"] == "f72r2")["explicit_unlabelled_nonstar_figure"] == 1,
        "two_exception_pages_are_different_physical_folios": len({row["physical_folio"] for row in exceptions}) == 2,
        "zero_lexical_glosses": True,
    }
    expected_json = {
        "experiment": "ZODIAC_STAR_SLOT_OWNERSHIP_AUDIT",
        "status": "PASS_PUBLIC_STAR_BEARING_SLOT_OWNERSHIP_LEAD",
        "inputs": {path.name: sha(path) for path in (PUBLIC, ROLE_ATLAS, ROLE_ATLAS_JSON, ROLE_ATLAS_VALIDATION, STOLFI)},
        "counts": {"pages": 12, "physical_folios": 4, "reading_specific_L_count_cells": 36, "figure_model_matching_pages": 10, "star_slot_model_matching_pages": 12, "opposite_exception_pages": 2},
        "opposite_exceptions": exceptions,
        "gates": gates,
        "output_tsv_sha256": sha(TARGET_TSV),
        "decision": "RETAIN_STAR_BEARING_SLOT_AS_AGGREGATE_L_RECORD_OWNER",
        "claim_ceiling": "The public zodiac L inventory follows selected star-bearing slots rather than figures across the two separating exceptions. This does not establish whether a label names a star, day, degree, person, property, or anything else, and supplies no Voynich word, meaning, plaintext, or translation.",
    }
    check(all(gates.values()), "all gates")
    check(json.loads(TARGET_JSON.read_text(encoding="utf-8")) == expected_json, "target JSON")
    expected_report = (
        "# Public zodiac star-slot ownership audit\n\n"
        "Status: **PASS_PUBLIC_STAR_BEARING_SLOT_OWNERSHIP_LEAD**\n\n"
        "Across all twelve public zodiac panels, the manual IVTFF `L` count equals the public catalogue's label count in all 36 page-reading cells. A simple figure-count model matches 10/12 pages. The two failures point in opposite directions: f70v2 has 29 figures but 30 labels, with the 30th explicitly beside a central star; f72r2 has 30 figures but only 29 star-holding figures and 29 labels, while the independent human label index explicitly records the non-star figure as `Not labeled`. The two exceptions lie on different physical folios.\n\n"
        "Counting star-holding figures plus the explicitly labelled non-figure central star matches 12/12 pages. This supports `STAR-BEARING SLOT` as the aggregate owner of the zodiac `L` inventory more strongly than `FIGURE`. It does not show what any label says: STAR, DAY, DEGREE, PERSON, a property, a name, and every lexical translation remain unestablished.\n"
    )
    check(TARGET_REPORT.read_text(encoding="utf-8") == expected_report, "target report")
    # Live falsifiers: either exception must break the 12/12 star-slot identity.
    check(star_figure_count(public_stored["f72r2"]["illustrations"].replace("with one exception", ""), 30) != 29, "f72 exception mutation")
    check(29 + 0 != label_counts["f70v2"], "f70 central-star mutation")

    validation = {
        "experiment": "ZODIAC_STAR_SLOT_OWNERSHIP_VALIDATION",
        "status": "PASS_INDEPENDENT_PUBLIC_SOURCE_STAR_SLOT_RECONSTRUCTION",
        "checks": checks,
        "bindings": {path.name: sha(path) for path in (*raw_sources, META, STOLFI, PUBLIC, ROLE_ATLAS, TARGET_TSV, TARGET_JSON, TARGET_REPORT, PRODUCER)},
        "reconstructed": {"pages": 12, "L_cells": 36, "figure_matches": 10, "star_slot_matches": 12, "exceptions": [["f70v2", 1], ["f72r2", -1]]},
        "production_module_imported": False,
        "decision": expected_json["decision"],
        "claim_ceiling": "Validates only the aggregate public star-bearing-slot ownership lead; no label content, word, meaning, plaintext, or translation follows.",
    }
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_REPORT.write_text(
        "# Public zodiac star-slot ownership validation\n\n"
        f"Status: **{validation['status']}** ({checks} checks). Raw public catalogue HTML, the manual source-separator inventory, and the raw human label index independently reproduce all twelve rows, both opposite exceptions, exact artifacts, and the 10/12 versus 12/12 comparison.\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": validation["status"], "checks": checks}, sort_keys=True))


if __name__ == "__main__":
    main()

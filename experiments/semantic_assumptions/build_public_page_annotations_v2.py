#!/usr/bin/env python3
"""Build a folio-boundary-safe version of the cached public page catalogue."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
CACHE = BASE / "cache" / "public_voynich_nu_catalogue"
OLD = BASE / "results" / "existing_human_page_annotations.tsv"
METHOD = BASE / "PUBLIC_PAGE_ANNOTATION_BOUNDARY_CORRECTION_METHOD.md"
OUT = BASE / "results" / "public_voynich_nu_page_annotations_v2.tsv"
RESULT = BASE / "results" / "public_page_annotation_boundary_correction.json"
REPORT = BASE / "results" / "public_page_annotation_boundary_correction_report.md"

FIELDS = {
    "general description": "general_description",
    "illustration(s)": "illustrations",
    "text": "text_description",
    "tentative identifications": "tentative_identifications",
    "other information": "other_information",
}
OUTPUT_FIELDS = [
    "page", "quire", "general_description", "illustrations",
    "text_description", "tentative_identifications", "other_information",
    "source_tags", "source_url", "tentative_identifications_are_role_evidence",
]
PAGE_RE = re.compile(r"f\d+[rv]\d*", re.I)
FOLIO_RE = re.compile(r"f\d+", re.I)
SIGN_RE = re.compile(r"\bemblem of (Pisces|Aries|Taurus|Gemini|Cancer|Leo|Virgo|Libra|Scorpius|Sagittarius)\b", re.I)
TENTATIVE_RE = re.compile(r"\bzodiac sign of (Pisces|Aries|Taurus|Gemini|Cancer|Leo|Virgo|Libra|Scorpius|Sagittarius)\b", re.I)
MONTH_RE = re.compile(r"\bmonth name (March|April|May|June|July|August|September|October|November|December)\b", re.I)
MONTH_SIGN = {
    "march": "pisces", "april": "aries", "may": "taurus",
    "june": "gemini", "july": "cancer", "august": "leo",
    "september": "virgo", "october": "libra", "november": "scorpius",
    "december": "sagittarius",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalized(parts: list[str]) -> str:
    return re.sub(r"\s+", " ", " ".join(parts).replace("\xa0", " ")).strip()


class CatalogueParser(HTMLParser):
    def __init__(self, quire: str) -> None:
        super().__init__(convert_charrefs=True)
        self.quire = quire
        self.page = ""
        self.heading = ""
        self.capture = ""
        self.parts: list[str] = []
        self.records: dict[str, dict[str, object]] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        lowered = tag.lower()
        values = {key.lower(): value for key, value in attrs}
        candidate = str(values.get("id") or "").lower()
        if lowered == "th" and candidate:
            if PAGE_RE.fullmatch(candidate):
                self.page = candidate
                self.records.setdefault(candidate, {
                    "page": candidate,
                    "quire": self.quire,
                    **{field: [] for field in FIELDS.values()},
                })
            elif FOLIO_RE.fullmatch(candidate):
                self.page = ""
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
        text = normalized(self.parts)
        captured = self.capture
        self.capture = ""
        self.parts = []
        if captured == "h4":
            self.heading = text.lower()
            return
        field = FIELDS.get(self.heading)
        if field and self.page and text and text.lower() not in {"&nbsp;", "none"}:
            self.records[self.page][field].append(text)  # type: ignore[index,union-attr]


def parse_sources() -> tuple[dict[str, dict[str, str]], list[dict[str, object]]]:
    records: dict[str, dict[str, object]] = {}
    sources: list[dict[str, object]] = []
    paths = sorted(CACHE.glob("q*.html"))
    if len(paths) != 18:
        raise RuntimeError("expected exactly 18 cached public quire files")
    for path in paths:
        parser = CatalogueParser(path.stem)
        parser.feed(path.read_text(encoding="utf-8", errors="replace"))
        sources.append({
            "source_id": path.stem,
            "bytes": path.stat().st_size,
            "sha256": sha(path),
            "pages": len(parser.records),
        })
        for page, raw in parser.records.items():
            target = records.setdefault(page, {
                "page": page,
                "quire": path.stem,
                **{field: [] for field in FIELDS.values()},
            })
            for field in FIELDS.values():
                target[field].extend(raw[field])  # type: ignore[union-attr]
    output: dict[str, dict[str, str]] = {}
    for page, raw in records.items():
        output[page] = {
            "page": page,
            "quire": str(raw["quire"]),
            **{
                field: " || ".join(dict.fromkeys(raw[field]))
                for field in FIELDS.values()
            },
        }
    return output, sources


def main() -> None:
    if any(path.exists() for path in (OUT, RESULT, REPORT)):
        raise SystemExit("refusing overwrite")
    with OLD.open(encoding="utf-8", newline="") as handle:
        old = {row["page"]: row for row in csv.DictReader(handle, delimiter="\t")}
    parsed, sources = parse_sources()
    if len(parsed) != len(old) or set(parsed) != set(old):
        raise AssertionError("page universe changed")

    changes: list[dict[str, str]] = []
    fixed_fields = ("quire", "general_description", "illustrations", "text_description", "tentative_identifications")
    for page in sorted(parsed):
        for field in fixed_fields:
            if parsed[page][field] != old[page][field]:
                raise AssertionError(f"unexpected field drift: {page} {field}")
        if parsed[page]["other_information"] != old[page]["other_information"]:
            if not old[page]["other_information"].startswith(parsed[page]["other_information"]):
                raise AssertionError(f"non-removal other-information drift: {page}")
            changes.append({
                "page": page,
                "removed_suffix": old[page]["other_information"][len(parsed[page]["other_information"]):].removeprefix(" || "),
            })
        for field in ("source_tags", "source_url", "tentative_identifications_are_role_evidence"):
            parsed[page][field] = old[page][field]

    contradictions = []
    zodiac_rows = []
    for page in sorted(parsed):
        row = parsed[page]
        image = SIGN_RE.search(row["illustrations"])
        tentative = TENTATIVE_RE.search(row["tentative_identifications"])
        month = MONTH_RE.search(row["text_description"])
        if not image and not tentative and not month:
            continue
        if not (image and tentative and month):
            raise AssertionError(f"incomplete zodiac identity fields: {page}")
        item = {
            "page": page,
            "illustration_sign": image.group(1).lower(),
            "tentative_sign": tentative.group(1).lower(),
            "month": month.group(1).lower(),
        }
        item["month_sign"] = MONTH_SIGN[item["month"]]
        zodiac_rows.append(item)
        if item["illustration_sign"] != item["tentative_sign"]:
            contradictions.append(item)
        if item["illustration_sign"] != item["month_sign"]:
            raise AssertionError(f"illustration/month contradiction: {page}")

    with OUT.open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(parsed[page] for page in sorted(parsed, key=lambda p: (int(re.match(r"f(\d+)", p).group(1)), p)))

    semantic_other_consumers = []
    excluded_names = {
        "build_existing_human_annotation_atlas.py",
        "refresh_public_voynich_nu_catalogue.py",
        "validate_public_voynich_nu_catalogue_refresh.py",
        Path(__file__).name,
        "validate_public_page_annotations_v2.py",
    }
    for path in BASE.rglob("*.py"):
        text = path.read_text(encoding="utf-8", errors="replace")
        if "existing_human_page_annotations.tsv" in text and "other_information" in text and path.name not in excluded_names:
            semantic_other_consumers.append(str(path.relative_to(ROOT)))

    circle_pages = [
        page for page in parsed
        if 67 <= int(re.match(r"f(\d+)", page).group(1)) <= 73
    ]
    gates = {
        "exact_18_cached_public_sources": len(sources) == 18,
        "exact_228_page_records": len(parsed) == 228,
        "only_other_information_changed": True,
        "exact_84_boundary_leak_corrections": len(changes) == 84,
        "source_tags_unchanged": all(parsed[p]["source_tags"] == old[p]["source_tags"] for p in parsed),
        "tentative_identity_never_role_evidence": all(parsed[p]["tentative_identifications_are_role_evidence"] == "0" for p in parsed),
        "exact_one_zodiac_source_contradiction": len(contradictions) == 1 and contradictions[0]["page"] == "f73v",
        "f73v_illustration_and_month_agree_sagittarius": contradictions[0]["illustration_sign"] == contradictions[0]["month_sign"] == "sagittarius",
        "no_semantic_consumer_reads_other_information": not semantic_other_consumers,
        "public_f67_f73_scope_retains_26_pages": len(circle_pages) == 26,
    }
    if not all(gates.values()):
        raise AssertionError(gates)
    result = {
        "experiment": "PUBLIC_PAGE_ANNOTATION_BOUNDARY_CORRECTION",
        "status": "PASS_84_CROSS_FOLIO_LEAKS_REMOVED_ONE_ZODIAC_SOURCE_CONTRADICTION",
        "decision": "USE_V2_FOR_FUTURE_PUBLIC_PAGE_WORK_KEEP_TENTATIVE_IDENTITIES_NONAUTHORITATIVE",
        "inputs": {
            "old_page_table": sha(OLD),
            "method": sha(METHOD),
            "builder": sha(Path(__file__)),
            "sources": {item["source_id"]: item["sha256"] for item in sources},
        },
        "counts": {
            "sources": len(sources), "pages": len(parsed),
            "corrected_other_information_pages": len(changes),
            "zodiac_pages": len(zodiac_rows), "zodiac_contradictions": len(contradictions),
            "f67_through_f73_pages": len(circle_pages),
        },
        "corrections": changes,
        "zodiac_contradictions": contradictions,
        "semantic_other_information_consumers": semantic_other_consumers,
        "gates": gates,
        "output_tsv_sha256": sha(OUT),
        "claim_ceiling": "Corrects public catalogue record ownership and exposes one internal source contradiction; no Voynich label ownership, lexeme, plaintext, or translation follows.",
    }
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# Public page-annotation boundary correction\n\n"
        f"Status: **{result['status']}**\n\n"
        "A folio-aware reparse of 18 cached public quire pages retains all 228 "
        "page IDs and every general, illustration, text, and tentative-identification "
        "field, but removes next-folio prose from **84** `other_information` records. "
        "All derived source tags are unchanged, and no semantic consumer reads the "
        "affected field.\n\n"
        "The same audit exposes one public-source contradiction: f73v's illustration "
        "and December month label identify Sagittarius, while the tentative field says "
        "Scorpius. Tentative identifications were already excluded from role evidence; "
        "the independent label catalogue also calls f73v Sagittarius.\n\n"
        "The public f67--f73 scope remains 26 page panels. This is a data-boundary "
        "correction, not a lexical or translation result.\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": result["status"], "corrections": len(changes)}, sort_keys=True))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Validate P source preservation and textual inventory; no target-data reads."""
from collections import Counter
import csv
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re


class TextOnly(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.skip += 1
        if tag in ("br", "p", "div", "h1", "h2", "h3"):
            self.parts.append(" ")

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.skip -= 1
        if tag in ("p", "div", "h1", "h2", "h3"):
            self.parts.append(" ")

    def handle_data(self, text):
        if not self.skip:
            self.parts.append(text)


def norm(text):
    return re.sub(r"\s+", " ", text).strip()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    base = Path(__file__).parent
    receipt = json.loads((base / "P_ACQUISITION_RECEIPTS.json").read_text())
    acquired = []
    for item in receipt:
        if item.get("status") != 200:
            assert "error" in item
            continue
        path = base / item["file"]
        assert len(path.read_bytes()) == item["bytes"], item["file"]
        assert digest(path) == item["sha256"], item["file"]
        acquired.append(item["file"])

    parser = TextOnly()
    parser.feed((base / "P_CLERUS_LATIN.html").read_bytes().decode("iso-8859-1"))
    source = norm("".join(parser.parts))
    complete = norm((base / "P_COMPLETE_VISIO_II_1_LATIN.txt").read_text())
    assert complete in source
    assert complete.startswith("[Col. 0751A] Descriptio sphaerae totius mundi")
    assert complete.endswith("in praecedentibus, et subsequentibus verbis suis manifestatur.")
    after = source[source.index(complete) + len(complete):]
    assert after.lstrip().startswith("[Col. 0755B]")
    assert "II." in after[:1800]
    assert len(complete.split()) == 1789
    assert "non autem signum capitis ursi tangebat" in complete
    assert "radios suos tantum ad nigrum ignem dirigebant" in complete
    assert "flatusque qui ex ore capitis cervi usque ad medietatem spatii inter capita leopardi et leonis" in complete
    excerpts = []
    for path in sorted(base.glob("P_EXEGESIS_*_WITH_NEXT_HEADING.txt")):
        assert norm(path.read_text()) in source, path.name
        excerpts.append(path.name)
    assert len(excerpts) == 3

    with (base / "P_SIXTEEN_STAR_SLOTS.tsv").open() as stream:
        stars = list(csv.DictReader(stream, delimiter="\t"))
    assert len(stars) == 16
    assert [row["editorial_id"] for row in stars] == [f"S{i:02d}" for i in range(1, 17)]
    assert Counter(row["terminal"] for row in stars) == {"thin_air": 8, "black_fire": 8}
    assert Counter((row["interval_first_head"], row["interval_second_head"]) for row in stars) == {
        ("leopard", "lion"): 4, ("lion", "wolf"): 4,
        ("wolf", "bear"): 4, ("bear", "leopard"): 4,
    }
    for row in stars:
        assert (row["restriction"] == "only") == (row["terminal"] == "black_fire")
        assert row["image_endpoint_collated"] == "no"
        assert row["target_assignment"] == "none"

    proposal = json.loads((base / "P_RAW_STELLAR_WIND_TYPED_RELATIONS.json").read_text())
    assert "RAW_UNREVIEWED_NOT_SELECTED_NOT_TESTED" in proposal["summary"]
    assert "Conditional on selecting this exact source account" in proposal["design"]["prediction"]
    report = (base / "P_SOURCE_REVIEW.md").read_text()
    assert "Unrepaired text problem" in report
    assert "not a critical edition or a diplomatic transcription" in report
    hashes = {
        path.name: {"sha256": digest(path), "bytes": path.stat().st_size}
        for path in sorted(base.glob("P_*"))
        if path.is_file() and path.name != "P_INTEGRITY_RECEIPT.json"
    }
    result = {
        "status": "PASS_SOURCE_ARTIFACT_INTEGRITY_ONLY",
        "idea_id": "IDEA000770",
        "successful_acquisitions": acquired,
        "failed_acquisitions_retained": sum("error" in item for item in receipt),
        "complete_section_words": len(complete.split()),
        "complete_section_and_three_exegeses_contiguous_in_acquired_html": True,
        "textual_star_slots": 16,
        "terminal_counts": {"thin_air": 8, "black_fire_only": 8},
        "individual_image_endpoint_collation_complete": False,
        "new_target_reads": 0,
        "meaning_test": "none",
        "files": hashes,
    }
    (base / "P_INTEGRITY_RECEIPT.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({key: value for key, value in result.items() if key != "files"}, indent=2))


if __name__ == "__main__":
    main()

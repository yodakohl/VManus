#!/usr/bin/env python3
"""Replay the bounded source witnesses; this is not a semantic compiler."""
import argparse
import hashlib
import html
import json
from pathlib import Path
import re

EXPECTED = {
    "pantry": "423b5c768884da4c624c78056e5c4cfe592ba4b06ea0c6ce8a7ca1515a29c669",
    "recipes": "a61ba433da1779a727d144c70fe89836be83d76a8c23ad37c8f69f879bc34a4a",
}


def plain(value):
    return html.unescape(re.sub(r"<[^>]*>", "", value))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_directory", type=Path,
                        help="Directory containing the byte-bound pantry.html and recipes.html")
    args = parser.parse_args()
    sources = {}
    for name, digest in EXPECTED.items():
        raw = (args.source_directory / (name + ".html")).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == digest, (name, "source_hash")
        sources[name] = raw.decode("utf-8")

    pantry = re.findall(r"<h3>(.*?)</h3>", sources["pantry"], re.S)
    assert len(pantry) == 7
    assert plain(pantry[-1]).strip() == "Haec omnia in loco sicco pone, ne odorem et virtutem perdant."
    records = [("PANTRY" + str(i + 1), plain(t)) for i, t in enumerate(pantry[:6])]
    src = sources["recipes"]
    headings = list(re.finditer(r"<h4>([IVXL]+)\. (.*?)</h4>", src, re.S))
    expected_roman = "I II III IV V VI VII VIII IX X XI XII XIII XIV XV XVI XVII XVIII XIX XX XXI XXII XXIII XXIV XXV XXVI XXVII XXVIII XXIX XXX XXXI".split()
    assert [h.group(1) for h in headings] == expected_roman
    recovered = 0
    for i, heading in enumerate(headings):
        end = headings[i + 1].start() if i + 1 < len(headings) else src.index("<!--  finis contentus", heading.end())
        body = src[heading.end():end]
        # Recover exactly the known malformed opener, before any generic tag removal.
        if "<h3<2. Alias:" in body:
            assert i == 0 and body.count("<h3<2. Alias:") == 1
            body = body.replace("<h3<2. Alias:", "<h3>2. Alias:")
            recovered += 1
        chunks = re.findall(r"<h3>(.*?)</h3>", body, re.S)
        assert len(chunks) == (2 if i == 0 else 1), (i, "body_count")
        assert len(re.findall(r"<h3", body)) == len(chunks), (i, "unparsed_body")
        records.append(("RECIPE" + str(i + 1), plain(heading.group(2) + " " + " ".join(chunks))))
    assert len(records) == 37 and recovered == 1
    stems = {"malva": "malv", "beta": "bet", "coliclos": "colicl", "amygdala": "amygdal", "aballana": "aballan"}
    columns, surfaces = {}, {}
    for name, stem in stems.items():
        columns[name], surfaces[name] = [], []
        for record, content in records:
            hits = [t for t in re.findall(r"[A-Za-z]+", content) if t.lower().startswith(stem)]
            columns[name].append(len(hits))
            surfaces[name].extend({"record": record, "surface": t} for t in hits)
        assert sum(columns[name]) == 1, (name, "complete_occurrence_count")
    assert columns["malva"] == columns["beta"] == columns["coliclos"]
    assert columns["amygdala"] == columns["aballana"]
    assert surfaces["malva"] == [{"record": "RECIPE2", "surface": "Malvas"}]
    assert surfaces["beta"] == [{"record": "RECIPE2", "surface": "betas"}]
    assert surfaces["amygdala"][0]["record"] == surfaces["aballana"][0]["record"] == "PANTRY5"
    phrase = "betas sive coliclos"
    assert src.count(phrase) == 1 and phrase in dict(records)["RECIPE2"]
    result = {
        "status": "PASS_RAW_SOURCE_COUNTS_AND_LITERAL_ALTERNATIVE",
        "source_hashes": EXPECTED,
        "records": 37,
        "recovered_recipe_I_continuations": recovered,
        "source_occurrences": surfaces,
        "weighted_columns": columns,
        "literal_alternative": phrase,
        "interpretation": "Binding the adjacent sive phrase to beta/coliclos breaks the malva/beta weighted-incidence symmetry. Amygdala/aballana remain interchangeable under unordered pantry incidence and recipe-derived relations.",
        "not_certified": "Complete semantic annotation, all automorphism orbits, unique named ingredients, target fit, historical source identity or meanings. Alternative operand interpretation requires independent source reading.",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

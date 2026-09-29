"""Replay W packet integrity and whole-paragraph exact comparisons; no semantics."""
import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(name):
    return json.loads((HERE / name).read_text())


def main(check=False):
    receipt = read("W_OKO_CONTEXT.json")
    boundary = read("W_OKO_BOUNDARIES.json")
    locators = read("W_OKO_LOCATORS.json")
    freeze = read("W_FIRST_FREEZE.json")
    checks = []

    def require(condition, name):
        assert condition, name
        checks.append(name)

    require(digest(ROOT / freeze["proposal"]) == freeze["sha256"], "frozen proposal unchanged")
    require(receipt["opened_utc"].replace("T", " ")[:19] > freeze["frozen_utc"][:19], "opening after freeze")
    for path, expected in receipt["inputs"].items():
        require(digest(ROOT / path) == expected, "context input " + path)
    for item in read("W_INPUT_RECEIPTS.json")["inputs"]:
        require(digest(ROOT / item["path"]) == item["sha256"], "author input " + item["path"])
    source = ROOT / locators["cache_receipt"]["inputs"]["source"]
    require(digest(source) == boundary["source_sha256"] == receipt["source_sha256"], "opaque source digest unchanged")
    require(digest(HERE / "W_OKO_BOUNDARY_METADATA.tsv") == boundary["metadata_sha256"], "metadata digest")
    require(digest(HERE / "W_OKO_CONTEXT.tsv") == receipt["source_tsv_sha256"], "raw packet digest")
    with (HERE / "W_OKO_CONTEXT.tsv").open() as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    require(len(rows) == receipt["rows"] == 667, "all 667 acquired groups")
    require(not any(r["page"].startswith("f84") for r in rows), "sealed pages absent")
    require(len({r["source_group_id"] for r in rows}) == len(rows), "unique source groups")
    lines = defaultdict(list)
    for r in rows:
        lines[(r["edition"], r["locus"])].append(r)
    for key, line in lines.items():
        line.sort(key=lambda r: int(r["source_group_index"]))
        require([int(r["source_group_index"]) for r in line] == list(range(1, int(line[0]["source_group_count"]) + 1)), "complete line " + repr(key))
    require({r["source_group_id"] for r in rows if r["ivtff_group_raw"] == "oko"} == {r["source_group_id"] for r in locators["rows"]}, "all twelve exact bare-oko locators")
    outside = [[r for locus in b["loci"] for r in lines[(b["edition"], locus)]] for b in boundary["units"]]
    require(Counter(r["source_group_id"] for unit in outside for r in unit) == Counter(r["source_group_id"] for r in rows), "whole units partition acquired rows")
    for b, unit in zip(boundary["units"], outside):
        if b["edition"] != "RF1b":
            require(unit[0]["paragraph_start"] == unit[-1]["paragraph_end"] == "1", "marked paragraph " + b["edition"] + b["page"])
        else:
            require(not b["missing_corresponding_loci"], "complete borrowed RF window " + b["page"])
    ring = json.loads((HERE.parent / "F68R_PAIRED_OPENINGS_SOURCE_20260927.json").read_text())
    ring_rows = next(q["rows"] for q in ring["queries"] if q["id"] == "groups")
    prose = json.loads((HERE.parent / "F89V1_OKOAIIN_CONTEXT_SOURCE_20260927.json").read_text())["query"]["rows"]
    comparisons = defaultdict(list)
    for r in ring_rows:
        comparisons[("ring", r["edition"], r["locus"])].append(r)
    for r in prose:
        comparisons[("f89", r["edition"], "whole paragraph")].append(r)
    matches = []
    # Independently enumerate OLD n-grams, then search whole OUTSIDE paragraphs.
    # Cross-line candidates are included, with original boundary flags retained.
    for key, old in comparisons.items():
        old.sort(key=lambda r: (int(r["locus"].split(".")[-1]), int(r["source_group_index"])))
        for start in range(len(old)):
            for end in range(start + 2, len(old) + 1):
                fragment = old[start:end]
                tokens = [r["ivtff_group_raw"] for r in fragment]
                if "oko" not in tokens:
                    continue
                for unit in outside:
                    literal = [r["ivtff_group_raw"] for r in unit]
                    for at in range(len(unit) - len(tokens) + 1):
                        if literal[at:at + len(tokens)] != tokens:
                            continue
                        segment = unit[at:at + len(tokens)]
                        def gaps(part):
                            return all(a["right_separator"] == b["left_separator"] == "DEFINITE_SPACE" for a, b in zip(part, part[1:]))
                        matches.append({"outside_reader": unit[0]["edition"], "outside_locus": segment[0]["locus"],
                                        "outside_start": int(segment[0]["source_group_index"]), "outside_end": int(segment[-1]["source_group_index"]),
                                        "comparison_kind": key[0], "comparison_reader": key[1], "comparison_locus": fragment[0]["locus"],
                                        "comparison_start": int(fragment[0]["source_group_index"]), "same_reader": unit[0]["edition"] == key[1],
                                        "groups": tokens, "definite_both": gaps(segment) and gaps(fragment),
                                        "cross_line": len({r["locus"] for r in segment}) > 1 or len({r["locus"] for r in fragment}) > 1})
    require(not any(m["cross_line"] for m in matches), "no additional cross-line matches")
    normal = lambda items: sorted(json.dumps(x, sort_keys=True) for x in items)
    require(normal([{k: v for k, v in m.items() if k != "cross_line"} for m in matches]) == normal(receipt["all_matches_containing_bare_oko_length_at_least_two"]), "whole-paragraph replay matches original within-line output")
    counts = {ed: dict(Counter(r["ivtff_group_raw"] for r in rows if r["edition"] == ed)) for ed in ("ZL3b", "IT2a", "RF1b")}
    forms = ("oko", "ok", "okaiin", "okoaiin", "qokaiin", "chokaiin")
    report = {"status": "PASS_PACKET_AND_LITERAL_REPLAY_ONLY", "checks": checks,
              "rows_per_reader": dict(Counter(r["edition"] for r in rows)), "whole_unit_matches": matches,
              "counts_of_declared_forms": {ed: {w: c.get(w, 0) for w in forms} for ed, c in counts.items()},
              "meaning_test": False, "independent_confirmation_leaves": 0}
    target = HERE / "W_ROOT_VALIDATION.json"
    if check:
        require(json.loads(target.read_text()) == report, "saved validation replay")
    else:
        target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"status": report["status"], "checks": len(checks), "matches": len(matches), "counts": report["counts_of_declared_forms"]}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    main(parser.parse_args().check)

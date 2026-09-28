#!/usr/bin/env python3
"""Fixed same-base versus other-base p/y follower comparison."""
import csv
import hashlib
import io
import json
import re
import subprocess
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
ART = Path(__file__).resolve().parents[1] / "artifacts"
SOURCE = ROOT / "experiments/semantic_assumptions/results/source_separator_transcription.tsv"
ALLOW = ROOT / "experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv"
FROZEN = ROOT / "experiments/yolo/gdt1075_py_section_hand_confound/artifacts/EVENTS.tsv"
FROZEN_HASH = "6c0b9fd422054a7ece186506d06aa3fa4558a77ac75eefa40424a5b4560a594d"
PRIMARY = {("chedy", "B", "2"), ("cheol", "H", "1"), ("chor", "H", "1")}


def read(path):
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path, data, fields):
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(data)


def similarity(a, b):
    x, y = set(a), set(b)
    return len(x & y) / len(x | y) if x | y else 0.0


def main():
    assert hashlib.sha256(FROZEN.read_bytes()).hexdigest() == FROZEN_HASH
    events = read(FROZEN)
    assert len(events) == 214
    pages = [r["page"] for r in read(ALLOW)]
    assert len(pages) == 179 and not any(p.startswith("f84") for p in pages)
    cmd = [str(ROOT / "vmanus-exp"), "query-tsv", str(SOURCE), "--selector", "page",
           "--columns", "edition,page,locus,kind,source_group_index,left_separator,right_separator,ivtff_group_raw",
           "--forbid-prefix", "f84"]
    for page in pages:
        cmd.extend(["--allow", page])
    got = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=True)
    by_line = defaultdict(dict)
    for row in csv.DictReader(io.StringIO(got.stdout), delimiter="\t"):
        if row["kind"] == "P" and row["source_group_index"] in {"2", "3", "4", "5"}:
            key = (row["edition"], row["locus"])
            pos = row["source_group_index"]
            if pos in by_line[key]:
                raise ValueError("duplicate group index")
            by_line[key][pos] = row
    follows = []
    for event in events:
        exact = []
        raw = by_line[(event["edition"], event["locus"])]
        for pos in ("2", "3", "4", "5"):
            row = raw.get(pos)
            if row is None:
                break
            if (row["left_separator"] in {"DEFINITE_SPACE", "LINE_START"}
                    and row["right_separator"] in {"DEFINITE_SPACE", "LINE_END"}
                    and re.fullmatch(r"[a-z]+", row["ivtff_group_raw"])):
                exact.append(row["ivtff_group_raw"])
        follows.append({**event, "followers": " ".join(exact), "usable_n": str(len(exact))})
    assert len(follows) == 214
    groups = defaultdict(list)
    for r in follows:
        groups[(r["edition"], r["section"], r["hand"])].append(r)
    p_scores = []
    all_strata = []
    for key, cohort in sorted(groups.items()):
        bases = sorted({r["base"] for r in cohort})
        for base in bases:
            p_events = [r for r in cohort if r["base"] == base and r["lead"] == "p"]
            y_events = [r for r in cohort if r["base"] == base and r["lead"] == "y"]
            eligible = []
            for p in p_events:
                same = [y for y in y_events if y["folio"] != p["folio"]]
                control_by_base = defaultdict(list)
                for y in cohort:
                    if y["lead"] == "y" and y["base"] != base and y["folio"] != p["folio"]:
                        control_by_base[y["base"]].append(y)
                other = [y for ys in control_by_base.values() for y in ys]
                other_folios = {y["folio"] for y in other}
                if not same or len(other_folios) < 2:
                    continue
                x = p["followers"].split()
                sm = sum(similarity(x, y["followers"].split()) for y in same) / len(same)
                om = sum(sum(similarity(x, y["followers"].split()) for y in ys) / len(ys)
                         for ys in control_by_base.values()) / len(control_by_base)
                score = dict(edition=p["edition"], section=p["section"], hand=p["hand"],
                             base=base, p_locus=p["locus"], same_y_n=len(same),
                             other_y_n=len(other), other_y_bases=len(control_by_base),
                             same_mean=f"{sm:.9f}", other_mean=f"{om:.9f}", delta=f"{sm-om:.9f}")
                p_scores.append(score)
                eligible.append(score)
            mean = sum(float(x["delta"]) for x in eligible) / len(eligible) if eligible else 0.0
            all_strata.append(dict(edition=key[0], section=key[1], hand=key[2], base=base,
                                   p_n=len(p_events), y_n=len(y_events), eligible_p_n=len(eligible),
                                   mean_delta=f"{mean:.9f}", direction="SAME_GREATER" if mean>0
                                   else "OTHER_GREATER" if mean<0 else "TIE_OR_NO_CAPACITY",
                                   primary=int(key[0] == "ZL3b" and (base,key[1],key[2]) in PRIMARY)))
    ART.mkdir(exist_ok=True)
    write(ART / "FOLLOWERS.tsv", follows, list(follows[0]))
    write(ART / "P_SCORES.tsv", p_scores, list(p_scores[0]))
    write(ART / "STRATA.tsv", all_strata, list(all_strata[0]))
    primary = [r for r in all_strata if r["primary"] == 1]
    assert len(primary) == 3
    status = "NO_CAPACITY" if any(r["eligible_p_n"] < 2 for r in primary) else (
        "COMMON_BASE_FOLLOWER_LEAD" if all(r["direction"] == "SAME_GREATER" for r in primary)
        else "COMMON_BASE_FOLLOWER_GATE_FAIL")
    result = {"guard": got.stderr.strip(), "fixed_events":len(follows), "scored_p_events":len(p_scores),
              "strata":len(all_strata), "primary_strata":primary, "decision":status,
              "claim_ceiling":"Descriptive follower similarity only; no allograph identity, meaning, significance or translation."}
    (ART / "RESULT.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))


if __name__ == "__main__":
    main()

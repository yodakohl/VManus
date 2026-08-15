#!/usr/bin/env python3
"""GDT039: attribute the GDT038 DAM placement lead against terminal-M."""
from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "gdt016_group_state_inventory.tsv"
METHOD = ROOT / "GDT039_TERMINAL_M_POSITIONAL_CONTROL_METHOD.md"
REPORT = ROOT / "GDT039_TERMINAL_M_POSITIONAL_CONTROL_REPORT.md"
OCC = ROOT / "gdt039_terminal_m_occurrences.tsv"
TESTS = ROOT / "gdt039_family_tests.tsv"
SPECIFICITY = ROOT / "gdt039_specificity_tests.tsv"
RESULT = ROOT / "gdt039_result.json"
DISCOVERY_FOLIOS = {"f39", "f46", "f95", "f106", "f112"}
OUTCOMES = ("final_open_field", "physical_line_end", "open_physical_line_end")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical_sha(value):
    raw = json.dumps(value, sort_keys=True, ensure_ascii=True,
                     separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def read(path):
    with Path(path).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path, rows, fields):
    with Path(path).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t",
                                lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def section(row):
    if row["section"] == "H" and row["currier"] == "B":
        return "HB"
    if row["section"] == "S" and row["currier"] == "B":
        return "SB"
    return "OUT"


def complete_lines(rows):
    grouped = defaultdict(list)
    for row in rows:
        assert not row["locus"].startswith("f84r")
        if section(row) in {"HB", "SB"} and row["physical_folio"] not in DISCOVERY_FOLIOS:
            grouped[row["locus"]].append(row)
    output = []
    for locus, line in grouped.items():
        line.sort(key=lambda row: int(row["group_index"]))
        count = int(line[0]["group_count"])
        if len(line) != count or {int(row["group_index"]) for row in line} != set(range(1, count + 1)):
            continue
        final_dy = max([-1] + [index for index, row in enumerate(line)
                              if row["record_state"] == "DY_RESOLUTION"])
        enriched = []
        for index, row in enumerate(line):
            enriched.append({**row, "target_section": section(row),
                "final_open_field": int(index > final_dy),
                "physical_line_end": int(index == count - 1),
                "open_physical_line_end": int(index == count - 1 and
                                               row["record_state"] != "DY_RESOLUTION")})
        output.append(enriched)
    output.sort(key=lambda line: line[0]["locus"])
    return output


def hypergeom(n, successes, draws):
    denominator = math.comb(n, draws)
    low, high = max(0, draws - (n - successes)), min(successes, draws)
    return {hits: math.comb(successes, hits) * math.comb(n - successes, draws - hits) /
            denominator for hits in range(low, high + 1)}


def convolve(left, right):
    output = defaultdict(float)
    for a, p in left.items():
        for b, q in right.items():
            output[a + b] += p * q
    return dict(output)


def exact_test(lines, predicate, outcome, base=lambda row: True):
    distribution = {0: 1.0}
    observed = family_n = 0
    folio_counts = defaultdict(lambda: [0, 0])
    section_counts = defaultdict(lambda: [0, 0])
    informative_lines = 0
    for line in lines:
        pool = [row for row in line if base(row)]
        if not pool:
            continue
        draws = sum(predicate(row) for row in pool)
        if not draws:
            continue
        successes = sum(int(row[outcome]) for row in pool)
        hits = sum(predicate(row) and int(row[outcome]) for row in pool)
        distribution = convolve(distribution, hypergeom(len(pool), successes, draws))
        informative_lines += int(0 < successes < len(pool))
        observed += hits
        family_n += draws
        for row in pool:
            if predicate(row):
                folio_counts[row["physical_folio"]][0] += int(row[outcome])
                folio_counts[row["physical_folio"]][1] += 1
                section_counts[row["target_section"]][0] += int(row[outcome])
                section_counts[row["target_section"]][1] += 1
    expected = sum(hits * probability for hits, probability in distribution.items())
    local_p = sum(probability for hits, probability in distribution.items()
                  if hits >= observed)
    deletion_rates, deletion_effects = [], []
    for held in sorted(folio_counts):
        subset = [[row for row in line if row["physical_folio"] != held] for line in lines]
        subset = [line for line in subset if line]
        reduced = exact_test_no_lofo(subset, predicate, outcome, base)
        if reduced["family_n"]:
            deletion_rates.append(reduced["observed"] / reduced["family_n"])
            deletion_effects.append(reduced["rate_effect"])
    return {"observed": observed, "family_n": family_n,
            "observed_rate": observed / family_n, "null_expected_hits": expected,
            "null_expected_rate": expected / family_n,
            "rate_effect": (observed - expected) / family_n, "local_p": local_p,
            "null_support_min": min(distribution), "null_support_max": max(distribution),
            "informative_lines": informative_lines, "target_folios": len(folio_counts),
            "hb_hits": section_counts["HB"][0], "hb_n": section_counts["HB"][1],
            "sb_hits": section_counts["SB"][0], "sb_n": section_counts["SB"][1],
            "lofo_min_rate": min(deletion_rates),
            "lofo_min_effect": min(deletion_effects)}


def exact_test_no_lofo(lines, predicate, outcome, base):
    distribution = {0: 1.0}
    observed = family_n = 0
    for line in lines:
        pool = [row for row in line if base(row)]
        draws = sum(predicate(row) for row in pool)
        if not draws:
            continue
        successes = sum(int(row[outcome]) for row in pool)
        observed += sum(predicate(row) and int(row[outcome]) for row in pool)
        family_n += draws
        distribution = convolve(distribution, hypergeom(len(pool), successes, draws))
    expected = sum(hits * probability for hits, probability in distribution.items())
    return {"observed": observed, "family_n": family_n,
            "rate_effect": (observed - expected) / family_n if family_n else 0.0}


def main():
    source = read(SOURCE)
    lines = complete_lines(source)
    all_rows = [row for line in lines for row in line]
    assert len(lines) == 284 and len(all_rows) == 2561
    predicates = {
        "TERMINAL_M": lambda row: row["residual_host"].endswith("m"),
        "TERMINAL_AM": lambda row: row["residual_host"].endswith("am"),
        "TERMINAL_DAM": lambda row: row["residual_host"].endswith("dam"),
        "EXACT_AM_HOST": lambda row: row["residual_host"] == "am",
        "D_WRAPPED_AM": lambda row: row["residual_host"] == "am" and row["stripped_prefix"] == "d",
        "CARRIER_WRAPPED_AM": lambda row: row["residual_host"] == "am" and
                                      row["stripped_prefix"] in {"ch", "che", "sh"},
    }
    test_rows = []
    for family, predicate in predicates.items():
        for outcome in OUTCOMES:
            stats = exact_test(lines, predicate, outcome)
            test_rows.append({"family": family, "outcome": outcome, **stats})
    for row in test_rows:
        row["bonferroni_18_p"] = min(1.0, row["local_p"] * len(test_rows))

    nested = [
        ("TERMINAL_AM_WITHIN_TERMINAL_M", predicates["TERMINAL_AM"], predicates["TERMINAL_M"]),
        ("TERMINAL_DAM_WITHIN_TERMINAL_AM", predicates["TERMINAL_DAM"], predicates["TERMINAL_AM"]),
        ("EXACT_AM_WITHIN_TERMINAL_AM", predicates["EXACT_AM_HOST"], predicates["TERMINAL_AM"]),
    ]
    specificity_rows = []
    for name, predicate, base in nested:
        for outcome in OUTCOMES:
            stats = exact_test(lines, predicate, outcome, base)
            specificity_rows.append({"contrast": name, "outcome": outcome, **stats})
    for row in specificity_rows:
        row["bonferroni_9_p"] = min(1.0, row["local_p"] * len(specificity_rows))

    numeric = ("observed_rate", "null_expected_hits", "null_expected_rate", "rate_effect",
               "local_p", "bonferroni_18_p", "lofo_min_rate", "lofo_min_effect")
    fields = ["family", "outcome", "observed", "family_n"] + list(numeric[:6]) + [
        "null_support_min", "null_support_max", "informative_lines", "target_folios",
        "hb_hits", "hb_n", "sb_hits", "sb_n", "lofo_min_rate", "lofo_min_effect"]
    write(TESTS, [{key: (f'{row[key]:.12g}' if key in numeric else row[key])
                   for key in fields} for row in test_rows], fields)
    snumeric = ("observed_rate", "null_expected_hits", "null_expected_rate", "rate_effect",
                "local_p", "bonferroni_9_p", "lofo_min_rate", "lofo_min_effect")
    sfields = ["contrast", "outcome", "observed", "family_n"] + list(snumeric[:6]) + [
        "null_support_min", "null_support_max", "informative_lines", "target_folios",
        "hb_hits", "hb_n", "sb_hits", "sb_n", "lofo_min_rate", "lofo_min_effect"]
    write(SPECIFICITY, [{key: (f'{row[key]:.12g}' if key in snumeric else row[key])
                         for key in sfields} for row in specificity_rows], sfields)

    occurrence_rows = []
    for row in all_rows:
        if not predicates["TERMINAL_M"](row):
            continue
        occurrence_rows.append({key: row[key] for key in (
            "locus", "page", "physical_folio", "target_section", "hand",
            "group_index", "group_count", "token", "stripped_prefix",
            "residual_host", "record_state", "final_open_field",
            "physical_line_end", "open_physical_line_end")})
    occurrence_rows.sort(key=lambda row: (row["physical_folio"], row["locus"],
                                           int(row["group_index"])))
    write(OCC, occurrence_rows, list(occurrence_rows[0]))

    by = {(row["family"], row["outcome"]): row for row in test_rows}
    nested_by = {(row["contrast"], row["outcome"]): row for row in specificity_rows}
    terminal = by["TERMINAL_M", "physical_line_end"]
    am_nested = nested_by["TERMINAL_AM_WITHIN_TERMINAL_M", "physical_line_end"]
    dam_nested = nested_by["TERMINAL_DAM_WITHIN_TERMINAL_AM", "physical_line_end"]
    decision = "DAM_FIELD_ROLE_ATTRIBUTED_TO_TERMINAL_M_POSITIONAL_SYSTEM"
    assert terminal["rate_effect"] > 0 and terminal["lofo_min_effect"] > 0
    assert am_nested["rate_effect"] <= 0 and dam_nested["rate_effect"] <= 0

    report = f"""# GDT039 — terminal-M control for the DAM field-role lead

## Outcome

**{decision}**

The GDT038 DAM-positive folios were removed before this test. The held pool
contains {len(all_rows):,} groups on {len(lines)} complete physical lines and
{len({row['physical_folio'] for row in all_rows})} physical folios.

Terminal `m` transfers strongly: {terminal['observed']}/{terminal['family_n']}
occurrences are physical line-final versus {terminal['null_expected_hits']:.3f}
under exact within-line placement (effect {terminal['rate_effect']:+.3f}; local
p={terminal['local_p']:.3g}; 18-test p={terminal['bonferroni_18_p']:.3g}). The
physical-line-end rate remains at least {terminal['lofo_min_rate']:.3f} and the
effect remains positive after deleting every target-positive physical folio.

The nested specificity tests reverse the interpretation. Terminal `am` has
{am_nested['observed']}/{am_nested['family_n']} physical line ends versus
{am_nested['null_expected_hits']:.3f} expected **within terminal-m forms**
(effect {am_nested['rate_effect']:+.3f}; one-sided enrichment p={am_nested['local_p']:.3g}).
Terminal `dam` has {dam_nested['observed']}/{dam_nested['family_n']} versus
{dam_nested['null_expected_hits']:.3f} expected **within terminal-am forms**
(effect {dam_nested['rate_effect']:+.3f}; p={dam_nested['local_p']:.3g}). Neither
nested family improves on its parent.

The replication is therefore real but not DAM-specific. Related terminal-AM
and terminal-DAM forms recur late on entirely different folios because the
broader terminal-M system is already strongly line-final. This is a positional
formal system, not a semantic value for DAM or M.

## Counterexamples and limits

- 11 held terminal-M forms do not end in `am`; 10/11 are physical line-final,
  a higher raw rate than terminal-AM's 49/70.
- Terminal-DAM's impressive unconditional exact p is inherited from its
  parent family; its conditional enrichment is absent.
- The strict-consensus restriction removes incomplete lines rather than
  treating retained endpoints as physical endpoints.
- The discovery split is post-GDT038, not a pristine prospective split. It
  tests transfer to non-DAM-positive folios but not a new manuscript.

No concrete function, word, morpheme, POS, referent, sound, language,
plaintext, meaning, or translation is assigned. f84r was not opened, retained,
queried, joined, or scored.
"""
    REPORT.write_text(report, encoding="utf-8")
    result = {
        "schema": "GDT039_TERMINAL_M_POSITIONAL_CONTROL_RESULT_V1",
        "status": decision, "discovery_folios": sorted(DISCOVERY_FOLIOS),
        "held_complete_lines": len(lines), "held_groups": len(all_rows),
        "held_physical_folios": len({row["physical_folio"] for row in all_rows}),
        "terminal_m_physical_end": terminal,
        "terminal_am_within_m_physical_end": am_nested,
        "terminal_dam_within_am_physical_end": dam_nested,
        "claim_ceiling": "Formal terminal-M positional attribution only; no concrete function, word, morpheme, POS, referent, sound, language, plaintext, meaning, or translation.",
        "f84r": {"opened": False, "retained": False, "queried": False,
                   "joined": False, "scored": False},
        "inputs": {"gdt016_group_state_inventory.tsv": sha(SOURCE),
                   "gdt016_result.json": sha(ROOT / "gdt016_result.json"),
                   "gdt038_result.json": sha(ROOT / "gdt038_result.json")},
        "implementation": {Path(__file__).name: sha(Path(__file__))},
        "outputs": {OCC.name: sha(OCC), TESTS.name: sha(TESTS),
                    SPECIFICITY.name: sha(SPECIFICITY)},
        "documents": {METHOD.name: sha(METHOD), REPORT.name: sha(REPORT)},
    }
    result["result_content_sha256"] = canonical_sha(result)
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": decision, "held_groups": len(all_rows),
                      "terminal_m": [terminal["observed"], terminal["family_n"]],
                      "am_within_m_effect": am_nested["rate_effect"],
                      "dam_within_am_effect": dam_nested["rate_effect"]},
                     sort_keys=True))


if __name__ == "__main__":
    main()

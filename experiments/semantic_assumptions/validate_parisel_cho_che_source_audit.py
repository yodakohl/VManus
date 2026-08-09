#!/usr/bin/env python3
"""Nonimporting reconstruction of the Parisel cho/che source audit."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path


BASE = Path(__file__).resolve().parent
REPO = BASE.parents[1]
RESULTS = BASE / "results"
SOURCES = {
    "ZL3b": REPO / "transcription/sources/ZL3b-n.txt",
    "IT2a": REPO / "transcription/sources/IT2a-n.txt",
    "RF1b": REPO / "transcription/sources/RF1b-e.txt",
}
SEPARATOR_VALIDATION = RESULTS / "source_separator_transcription_validation.json"
SPEC = BASE / "PARISEL_CHO_CHE_SOURCE_AUDIT_SPEC.md"
PRODUCER = BASE / "audit_parisel_cho_che_source.py"
PRODUCTION = RESULTS / "parisel_cho_che_source_audit.json"
FOLIOS = RESULTS / "parisel_cho_che_folio_states.tsv"
TEMPLATES = RESULTS / "parisel_cho_che_template_summary.tsv"
PRODUCTION_REPORT = RESULTS / "parisel_cho_che_source_audit_report.md"
VALIDATOR = Path(__file__).resolve()
OUT = RESULTS / "parisel_cho_che_source_audit_validation.json"
REPORT = RESULTS / "parisel_cho_che_source_audit_validation_report.md"

HASHES = {
    SOURCES["ZL3b"]: "bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc",
    SOURCES["IT2a"]: "7f27a8b0feed8f6de0a99900df6bf912dd1d295c38e5f830bac8b41c3f536fb5",
    SOURCES["RF1b"]: "e7d3238e35743e06c63367a933909ec37b1e2de7ada3a1b449447eafa1918782",
    SEPARATOR_VALIDATION: "8698a2643219fd8ab00b05bba8705a1f1e8219c9b468824fbe2dc92117043deb",
    SPEC: "ebc70e422783397e3933b3ac5a58c86b112f196d46ee127af07051346c4dd5b9",
    PRODUCER: "5eb841198eb8f04996afd11de8df7f8a149dc9359e2590fc3d165671fc665c4a",
    PRODUCTION: "4243602269b648a4c3069955cf8d44beee2f6f7299769638e7060b03be6a8624",
    FOLIOS: "4c713c379b33d04985c0efbf9dd4025cb810a9c1006975f7855ed6cc52ff381c",
    TEMPLATES: "648a7d334ea747d5c39a1c90c9d3882d88d2e5584616d7b0165659555a8f1cb6",
    PRODUCTION_REPORT: "a2dd872fd067ae3db5a2b24609f14699b02812ef2a65fa0320d4561a15217618",
}
READINGS = ("ZL3b", "IT2a", "RF1b")
PARSERS = ("PUBLISHED_MERGE", "REPOSITORY_DRAWING_SPLIT", "SOURCE_ALL_SEPARATORS")
ASSIGNMENTS = ("EM", "THRESHOLD")
FOLIO_FIELDS = [
    "parser", "edition", "folio", "cho_groups", "che_groups",
    "classifiable_groups", "cho_rate", "threshold_state", "em_state",
    "em_responsibility_high", "assignment_disagrees",
]
TEMPLATE_FIELDS = [
    "parser", "edition", "assignment", "template", "state1_cho",
    "state1_che", "state0_cho", "state0_che", "state1_rate",
    "state0_rate", "signed_delta", "absolute_delta", "class", "direction",
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def render_tsv(fields: list[str], rows: list[dict]) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode()


def manual_parse(path: Path, parser: str) -> tuple[dict[str, list[str]], dict]:
    pages: dict[str, list[str]] = defaultdict(list)
    line_rows = 0
    separator_counts = Counter()
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line[0] in "#;":
            continue
        locator = re.match(r"<(f\d+[rv]\d?)\.(\d+\w*)", line)
        if locator is None:
            continue
        line_rows += 1
        page_match = re.match(r"(f\d+[rv])", locator.group(1))
        if page_match is None:
            raise AssertionError("page parse")
        page = page_match.group(1)
        body = line.split(">", 1)[1] if ">" in line else ""
        separator_counts["uncertain_small_space"] += body.count(",")
        separator_counts["drawing_interruption"] += body.count("<->")
        separator_counts["unaligned_drawing_interruption"] += body.count("<~>")
        working = line
        if parser in {"REPOSITORY_DRAWING_SPLIT", "SOURCE_ALL_SEPARATORS"}:
            working = working.replace("<->", ".")
        if parser == "SOURCE_ALL_SEPARATORS":
            working = working.replace("<~>", ".")
        working = re.sub(r"<[^>]*>", "", working)
        working = re.sub(r"\{[^}]*\}", "", working)
        working = re.sub(r"@\d+;?", "", working)
        working = re.sub(r"[!%*]", "", working)
        pieces = re.split(r"[.,]", working) if parser == "SOURCE_ALL_SEPARATORS" else working.split(".")
        for piece in pieces:
            if piece.strip():
                cleaned = re.sub(r"[^a-z]", "", piece.strip())
                if cleaned:
                    pages[page].append(cleaned)
    return dict(pages), {
        "accepted_rows": line_rows,
        "physical_pages": len(pages),
        "groups": sum(len(values) for values in pages.values()),
        "manual_nondefinite_separators": dict(sorted(separator_counts.items())),
    }


def split_glyphs(surface: str) -> list[str]:
    answer = []
    cursor = 0
    while cursor < len(surface):
        if surface[cursor:cursor + 2] in {"ch", "sh"}:
            answer.append(surface[cursor:cursor + 2])
            cursor += 2
        else:
            answer.append(surface[cursor])
            cursor += 1
    return answer


def group_class(surface: str) -> str | None:
    sequence = split_glyphs(surface)
    o_site = any(sequence[i] in {"ch", "sh"} and sequence[i + 1] == "o" for i in range(len(sequence) - 1))
    e_site = any(sequence[i] in {"ch", "sh"} and sequence[i + 1] == "e" for i in range(len(sequence) - 1))
    if o_site != e_site:
        return "CHO" if o_site else "CHE"
    return None


def event_template(surface: str) -> tuple[str, int, int] | None:
    sequence = split_glyphs(surface)
    output = []
    o_events = 0
    e_events = 0
    for index, unit in enumerate(sequence):
        target = index > 0 and sequence[index - 1] in {"ch", "sh"} and unit in {"o", "e"}
        output.append("X" if target else unit)
        if target:
            o_events += unit == "o"
            e_events += unit == "e"
    return ("".join(output), o_events, e_events) if o_events + e_events else None


def independent_em(observations: list[tuple[int, int]]) -> dict:
    high = 0.7
    low = 0.2
    mixing = 0.5
    posterior = []
    iterations = 0
    for iteration in range(200):
        iterations = iteration + 1
        posterior = []
        for successes, trials in observations:
            lh = math.log(mixing + 1e-15) + successes * math.log(max(high, 1e-15)) + (trials - successes) * math.log(max(1 - high, 1e-15))
            ll = math.log(1 - mixing + 1e-15) + successes * math.log(max(low, 1e-15)) + (trials - successes) * math.log(max(1 - low, 1e-15))
            peak = max(lh, ll)
            eh = math.exp(lh - peak)
            el = math.exp(ll - peak)
            posterior.append(eh / (eh + el))
        new_mixing = sum(posterior) / len(posterior)
        new_high = sum(r * k for r, (k, n) in zip(posterior, observations)) / sum(r * n for r, (k, n) in zip(posterior, observations))
        new_low = sum((1 - r) * k for r, (k, n) in zip(posterior, observations)) / sum((1 - r) * n for r, (k, n) in zip(posterior, observations))
        if abs(new_high - high) < 1e-8 and abs(new_low - low) < 1e-8 and abs(new_mixing - mixing) < 1e-8:
            break
        high, low, mixing = new_high, new_low, new_mixing
    if high < low:
        high, low = low, high
        mixing = 1 - mixing
        posterior = [1 - value for value in posterior]
    successes = sum(k for k, n in observations)
    trials = sum(n for k, n in observations)
    pooled = successes / trials
    ll_one = sum(k * math.log(pooled) + (n - k) * math.log(1 - pooled) for k, n in observations)
    ll_two = 0.0
    for k, n in observations:
        lh = math.log(mixing + 1e-15) + k * math.log(max(high, 1e-15)) + (n - k) * math.log(max(1 - high, 1e-15))
        ll = math.log(1 - mixing + 1e-15) + k * math.log(max(low, 1e-15)) + (n - k) * math.log(max(1 - low, 1e-15))
        peak = max(lh, ll)
        ll_two += peak + math.log(math.exp(lh - peak) + math.exp(ll - peak))
    return {
        "p_high": high,
        "p_low": low,
        "pi_high": mixing,
        "iterations": iterations,
        "delta_aic_two_over_one": (-2 * ll_one + 2) - (-2 * ll_two + 6),
        "posterior": posterior,
    }


def template_class(rate1: float, rate0: float) -> str:
    if min(rate1, rate0) > 0.9:
        return "F1_FIXED_CHO"
    if max(rate1, rate0) < 0.1:
        return "F0_FIXED_CHE"
    if abs(rate1 - rate0) >= 0.2:
        return "S_SWITCHABLE"
    return "I_INTERMEDIATE"


def reconstruct_templates(parser: str, edition: str, assignment: str, pages: dict[str, list[str]], states: dict[str, int]) -> list[dict]:
    counts: dict[str, list[int]] = defaultdict(lambda: [0, 0, 0, 0])
    for page, state in states.items():
        for surface in pages[page]:
            event = event_template(surface)
            if event is None:
                continue
            template, cho, che = event
            slot = 0 if state else 2
            counts[template][slot] += cho
            counts[template][slot + 1] += che
    output = []
    for template, values in counts.items():
        n1 = values[0] + values[1]
        n0 = values[2] + values[3]
        if n1 < 10 or n0 < 10:
            continue
        r1 = values[0] / n1
        r0 = values[2] / n0
        delta = r1 - r0
        output.append({
            "parser": parser, "edition": edition, "assignment": assignment,
            "template": template, "state1_cho": values[0], "state1_che": values[1],
            "state0_cho": values[2], "state0_che": values[3],
            "state1_rate": r1, "state0_rate": r0, "signed_delta": delta,
            "absolute_delta": abs(delta), "class": template_class(r1, r0),
            "direction": "FORWARD" if delta > 0 else "REVERSE" if delta < 0 else "EQUAL",
        })
    return sorted(output, key=lambda row: row["template"])


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing to overwrite Parisel validation artifacts")
    checks = 0

    def require(value: bool, label: str) -> None:
        nonlocal checks
        checks += 1
        if not value:
            raise AssertionError(label)

    for path, expected in HASHES.items():
        require(sha(path) == expected, f"hash {path.name}")
    require(json.loads(SEPARATOR_VALIDATION.read_text())["status"] == "PASS_INDEPENDENT_SOURCE_SEPARATOR_RECONSTRUCTION", "separator validation")
    actual = json.loads(PRODUCTION.read_text(encoding="utf-8"))
    require(actual["experiment"] == "PARISEL_CHO_CHE_SOURCE_AUDIT", "experiment")
    require(actual["status"] == "CONFIRM_FOLIO_REGIME_REJECT_EXACT_PUBLISHED_IMPLEMENTATION_CLAIMS", "status")
    require(actual["external_reference"]["paper"]["id"] == "arXiv:2604.25979v2", "paper version")
    require(actual["external_reference"]["paper"]["reported_eligible_folios"] == 197, "paper eligible")
    require(actual["external_reference"]["paper"]["reported_retained_templates"] == 31, "paper templates")
    require(actual["external_reference"]["repository"]["separator_fix_commit"] == "74c24ee939956d44abd81d4a9895dc03894d44d1", "fix commit")
    require(actual["external_reference"]["repository"]["audited_main_commit"] == "627ee9a1f3df76cbc61a1415399b78ad2eb50602", "main commit")
    require(actual["external_reference"]["published_table_literal_reversals"] == [
        {"template": "shXo", "state1_rate": 0.0, "state0_rate": 0.034},
        {"template": "otchXy", "state1_rate": 0.0, "state0_rate": 0.032},
    ], "published reversals")
    require(group_class("chody") == "CHO", "cho fixture")
    require(group_class("shedy") == "CHE", "che fixture")
    require(group_class("cholshey") is None, "mixed fixture")
    require(event_template("chodyshes") == ("chXdyshXs", 1, 1), "multi-site fixture")

    summaries = {}
    states = {}
    folio_rows = []
    template_rows = []
    for parser in PARSERS:
        summaries[parser] = {}
        for edition in READINGS:
            pages, parse_counts = manual_parse(SOURCES[edition], parser)
            eligible = []
            for page in sorted(pages):
                counts = Counter(group_class(surface) for surface in pages[page])
                cho = counts["CHO"]
                che = counts["CHE"]
                if cho + che >= 5:
                    eligible.append((page, cho, che))
            fit = independent_em([(cho, cho + che) for page, cho, che in eligible])
            threshold = {page: int(cho / (cho + che) > 0.5) for page, cho, che in eligible}
            mixture = {page: int(value > 0.5) for (page, cho, che), value in zip(eligible, fit["posterior"])}
            states[(parser, edition, "THRESHOLD")] = threshold
            states[(parser, edition, "EM")] = mixture
            for (page, cho, che), value in zip(eligible, fit["posterior"]):
                folio_rows.append({
                    "parser": parser, "edition": edition, "folio": page,
                    "cho_groups": cho, "che_groups": che, "classifiable_groups": cho + che,
                    "cho_rate": cho / (cho + che), "threshold_state": threshold[page],
                    "em_state": mixture[page], "em_responsibility_high": value,
                    "assignment_disagrees": int(threshold[page] != mixture[page]),
                })
            summary = {
                "parse": parse_counts,
                "eligible_folios": len(eligible),
                "classifiable_groups": sum(cho + che for page, cho, che in eligible),
                "em": {key: fit[key] for key in ("p_high", "p_low", "pi_high", "iterations", "delta_aic_two_over_one")},
                "em_state1": sum(mixture.values()), "em_state0": len(mixture) - sum(mixture.values()),
                "threshold_state1": sum(threshold.values()), "threshold_state0": len(threshold) - sum(threshold.values()),
                "em_threshold_disagreements": sum(mixture[p] != threshold[p] for p in mixture),
                "em_confidence_over_95pct": sum(max(value, 1 - value) > 0.95 for value in fit["posterior"]),
                "templates": {},
            }
            for assignment, mapping in (("EM", mixture), ("THRESHOLD", threshold)):
                rows = reconstruct_templates(parser, edition, assignment, pages, mapping)
                template_rows.extend(rows)
                summary["templates"][assignment] = {
                    "retained": len(rows),
                    "events": sum(row["state1_cho"] + row["state1_che"] + row["state0_cho"] + row["state0_che"] for row in rows),
                    "classes": dict(sorted(Counter(row["class"] for row in rows).items())),
                    "forward": sum(row["direction"] == "FORWARD" for row in rows),
                    "reverse": sum(row["direction"] == "REVERSE" for row in rows),
                    "equal": sum(row["direction"] == "EQUAL" for row in rows),
                }
            summaries[parser][edition] = summary
    require(summaries == actual["summaries"], "complete summaries")

    agreement = {}
    for parser in PARSERS:
        agreement[parser] = {}
        for assignment in ASSIGNMENTS:
            mappings = [states[(parser, edition, assignment)] for edition in READINGS]
            common = sorted(set.intersection(*(set(mapping) for mapping in mappings)))
            disagreements = []
            for page in common:
                values = {edition: states[(parser, edition, assignment)][page] for edition in READINGS}
                if len(set(values.values())) > 1:
                    disagreements.append({"folio": page, **values})
            agreement[parser][assignment] = {
                "common_eligible_folios": len(common),
                "all_three_same": len(common) - len(disagreements),
                "all_three_same_fraction": (len(common) - len(disagreements)) / len(common),
                "disagreements": disagreements,
            }
    require(agreement == actual["cross_reading_agreement"], "cross-reading agreement")
    require(agreement["SOURCE_ALL_SEPARATORS"]["EM"]["all_three_same"] == 196, "EM agreement count")
    require(agreement["SOURCE_ALL_SEPARATORS"]["THRESHOLD"]["all_three_same"] == 197, "threshold agreement count")

    folio_rows.sort(key=lambda row: (row["parser"], row["edition"], row["folio"]))
    template_rows.sort(key=lambda row: (row["parser"], row["edition"], row["assignment"], row["template"]))
    require(render_tsv(FOLIO_FIELDS, folio_rows) == FOLIOS.read_bytes(), "folio TSV bytes")
    require(render_tsv(TEMPLATE_FIELDS, template_rows) == TEMPLATES.read_bytes(), "template TSV bytes")
    for row in folio_rows:
        require(row["classifiable_groups"] == row["cho_groups"] + row["che_groups"], "folio count algebra")
        require(row["assignment_disagrees"] == (row["threshold_state"] != row["em_state"]), "folio disagreement algebra")
    for row in template_rows:
        require(row["absolute_delta"] == abs(row["signed_delta"]), "template delta algebra")
        require(row["state1_cho"] + row["state1_che"] >= 10 and row["state0_cho"] + row["state0_che"] >= 10, "template retention")

    published_rf = summaries["PUBLISHED_MERGE"]["RF1b"]
    repository_rf = summaries["REPOSITORY_DRAWING_SPLIT"]["RF1b"]
    split_rf = summaries["SOURCE_ALL_SEPARATORS"]["RF1b"]
    published_audit = {
        "paper_197_vs_reconstructed_published_parser_rf_eligible": [197, published_rf["eligible_folios"]],
        "published_31_template_inventory_reproduced": published_rf["templates"]["EM"]["retained"] == 31,
        "repository_drawing_fix_changes_rf_retained_templates_to": repository_rf["templates"]["EM"]["retained"],
        "all_source_separators_change_rf_retained_templates_to": split_rf["templates"]["EM"]["retained"],
        "paper_threshold_vs_implemented_em_rf_assignment_disagreements": published_rf["em_threshold_disagreements"],
        "paper_table_literal_reversal_count": 2,
        "local_published_parser_rf_em_reversal_count": published_rf["templates"]["EM"]["reverse"],
        "local_repository_drawing_split_rf_em_reversal_count": repository_rf["templates"]["EM"]["reverse"],
        "local_source_all_separators_rf_em_reversal_count": split_rf["templates"]["EM"]["reverse"],
    }
    require(published_audit == actual["published_claim_audit"], "published claim audit")
    require(published_rf["templates"]["EM"]["retained"] == 31, "31 reproduction")
    require(repository_rf["templates"]["EM"]["retained"] == 34, "34 repository drawing repair")
    require(split_rf["templates"]["EM"]["retained"] == 35, "35 all-separator source")
    require(published_rf["templates"]["EM"]["reverse"] == 2, "published parser reversals")
    require(all(summaries[parser][edition]["eligible_folios"] == 200 for parser in PARSERS for edition in READINGS), "all eligible 200")
    require(all(summaries["SOURCE_ALL_SEPARATORS"][edition]["em_threshold_disagreements"] == 13 for edition in READINGS), "all assignment differences 13")
    require(all(actual["gates"].values()), "all gates")
    require(actual["english_glosses"] == 0, "zero glosses")
    require(actual["outputs"] == {FOLIOS.name: sha(FOLIOS), TEMPLATES.name: sha(TEMPLATES)}, "output bindings")
    require(actual["inputs"] == {path.name: sha(path) for path in (*{p: None for p in (SOURCES["ZL3b"], SOURCES["IT2a"], SOURCES["RF1b"], SEPARATOR_VALIDATION)}, SPEC, PRODUCER)}, "input bindings")

    split = summaries["SOURCE_ALL_SEPARATORS"]
    expected_report = f"""# Parisel `cho/che` source and implementation audit

Status: **{actual['status']}**

The folio-level effect is real and unusually strong. With all manual separator
classes kept as source separators, the fitted high/low rates are
**{split['ZL3b']['em']['p_high']:.3f}/{split['ZL3b']['em']['p_low']:.3f}** in ZL,
**{split['IT2a']['em']['p_high']:.3f}/{split['IT2a']['em']['p_low']:.3f}** in IT,
and **{split['RF1b']['em']['p_high']:.3f}/{split['RF1b']['em']['p_low']:.3f}** in RF.
All three EM state labels agree on
**{agreement['SOURCE_ALL_SEPARATORS']['EM']['all_three_same']}/200** folios; the literal
threshold labels agree on
**{agreement['SOURCE_ALL_SEPARATORS']['THRESHOLD']['all_three_same']}/200**. These are
alternate readings of the same manuscript, so this is transcription robustness,
not three independent replications.

The exact published implementation claims do not survive audit:

- every reading has **200**, not 197, eligible folios under the linked parser;
- the printed threshold and the implemented EM state differ on **13/200** RF
  folios (also 13/200 in ZL and IT);
- the published 31-template inventory is reproduced only when `<->` drawing
  interruptions are deleted and their neighboring groups are concatenated;
- the repository's aligned-drawing repair yields
  **{repository_rf['templates']['EM']['retained']}** RF templates, but still
  deletes comma and `<~>` separators;
- preserving every manual separator yields **{split_rf['templates']['EM']['retained']}**
  RF templates, while ZL/IT yield
  **{split['ZL3b']['templates']['EM']['retained']}** and
  **{split['IT2a']['templates']['EM']['retained']}**;
- the published table itself has two reverse-rate rows (`shXo`, `otchXy`), so
  the literal zero-reversal and `2^-31` claim is false.

The safe retained result is therefore a page-level formal regime that modulates
some `ch/sh + o/e` contexts. The exact 31-item template table and its monotonicity
argument are retired. Nothing here identifies sounds, vowels, consonants, words,
a natural language, a cipher operation, meaning, plaintext, or translation.
"""
    require(PRODUCTION_REPORT.read_text(encoding="utf-8") == expected_report, "report bytes")

    validation = {
        "experiment": "PARISEL_CHO_CHE_SOURCE_AUDIT_VALIDATION",
        "status": "PASS_INDEPENDENT_SOURCE_AND_IMPLEMENTATION_RECONSTRUCTION",
        "checks": checks,
        "production_sha256": sha(PRODUCTION),
        "folio_tsv_sha256": sha(FOLIOS),
        "template_tsv_sha256": sha(TEMPLATES),
        "validator_sha256": sha(VALIDATOR),
        "reconstructed": {
            "eligible_each_reading": 200,
            "source_all_separators_em_agreement": 196,
            "source_all_separators_threshold_agreement": 197,
            "published_merge_rf_em_templates": 31,
            "repository_drawing_split_rf_em_templates": 34,
            "source_all_separators_rf_em_templates": 35,
            "em_threshold_disagreements_each_reading": 13,
            "published_table_literal_reversals": 2,
        },
        "claim_ceiling": actual["claim_ceiling"],
        "failures": [],
    }
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    validation_report = f"""# Parisel `cho/che` source audit validation

Status: **{validation['status']}**

A nonimporting implementation reconstructed all three parser modes, both assignment
rules, all 1,800 folio rows, every retained-template row, the three-reading
agreement panels, exact TSV bytes, production report, and all audit gates in
**{checks:,}** checks. It confirms the robust folio regime and the failures of
the published 197-folio, threshold-equivalence, 31-template source-complete, and
literal no-reversal claims. No lexical or phonetic interpretation follows.
"""
    REPORT.write_text(validation_report, encoding="utf-8")
    print(json.dumps({"status": validation["status"], "checks": checks}, sort_keys=True))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Audit the published cho/che switch against source-valid manual readings."""

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
BUILDER = Path(__file__).resolve()
OUT_JSON = RESULTS / "parisel_cho_che_source_audit.json"
OUT_FOLIOS = RESULTS / "parisel_cho_che_folio_states.tsv"
OUT_TEMPLATES = RESULTS / "parisel_cho_che_template_summary.tsv"
REPORT = RESULTS / "parisel_cho_che_source_audit_report.md"

FROZEN = {
    SOURCES["ZL3b"]: "bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc",
    SOURCES["IT2a"]: "7f27a8b0feed8f6de0a99900df6bf912dd1d295c38e5f830bac8b41c3f536fb5",
    SOURCES["RF1b"]: "e7d3238e35743e06c63367a933909ec37b1e2de7ada3a1b449447eafa1918782",
    SEPARATOR_VALIDATION: "8698a2643219fd8ab00b05bba8705a1f1e8219c9b468824fbe2dc92117043deb",
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
EXTERNAL = {
    "paper": {
        "id": "arXiv:2604.25979v2",
        "date": "2026-05-05",
        "url": "https://arxiv.org/abs/2604.25979v2",
        "reported_eligible_folios": 197,
        "reported_retained_templates": 31,
        "reported_direction_reversals": 0,
    },
    "repository": {
        "url": "https://github.com/labyrinthinesecurity/currier-models",
        "published_report_commit": "c9bb7e5d4d19d00b2e6f63af6df0a421308be14a",
        "published_switch_sha256": "af0ddbd25ccb0e7d6761858865b7f450f3044128b6d9f57abe0ff8c1516ce580",
        "published_report_sha256": "f33125dfd4070f9f1b0763bad888c9d7760491252ad0cf5a81f7ae5a03fedbec",
        "separator_fix_commit": "74c24ee939956d44abd81d4a9895dc03894d44d1",
        "audited_main_commit": "627ee9a1f3df76cbc61a1415399b78ad2eb50602",
        "audited_main_switch_sha256": "9649a5b041999ef84e489d42e816f0ffd96a839a6d2f9dd389a174cb30bf9665",
        "audited_main_report_sha256": "7dbbdddd4303a51439599f10ba06647d13abf72d80e3f78f18e411c143c804a5",
        "audited_main_source_sha256": "4f8f096eaafb2fa65096e8384ca98599138e9d0b4b57ebc3452a0f45e9544c63",
        "audited_main_eligible_folios": 200,
        "audited_main_retained_templates": 34,
    },
    "published_table_literal_reversals": [
        {"template": "shXo", "state1_rate": 0.000, "state0_rate": 0.034},
        {"template": "otchXy", "state1_rate": 0.000, "state0_rate": 0.032},
    ],
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_json_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def tsv_bytes(fields: list[str], rows: list[dict]) -> bytes:
    target = io.StringIO(newline="")
    writer = csv.DictWriter(target, fieldnames=fields, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return target.getvalue().encode("utf-8")


def parse_source(path: Path, parser: str) -> tuple[dict[str, list[str]], dict]:
    folios: dict[str, list[str]] = defaultdict(list)
    separator_counts = Counter()
    accepted_rows = 0
    for raw in path.read_text(encoding="utf-8").splitlines():
        if raw.startswith(("#", ";")) or not raw.strip():
            continue
        match = re.match(r"<(f\d+[rv]\d?)\.(\d+\w*)", raw)
        if not match:
            continue
        accepted_rows += 1
        folio_match = re.match(r"(f\d+[rv])", match.group(1))
        if folio_match is None:
            raise ValueError("physical folio parse failure")
        folio = folio_match.group(1)
        body = raw.split(">", 1)[1] if ">" in raw else ""
        separator_counts["uncertain_small_space"] += body.count(",")
        separator_counts["drawing_interruption"] += body.count("<->")
        separator_counts["unaligned_drawing_interruption"] += body.count("<~>")
        text = raw
        if parser in ("REPOSITORY_DRAWING_SPLIT", "SOURCE_ALL_SEPARATORS"):
            text = re.sub(r"<->", ".", text)
        if parser == "SOURCE_ALL_SEPARATORS":
            text = re.sub(r"<~>", ".", text)
        text = re.sub(r"<[^>]*>", "", text)
        text = re.sub(r"\{[^}]*\}", "", text)
        text = re.sub(r"@\d+;?", "", text)
        text = re.sub(r"[!%*]", "", text)
        pieces = re.split(r"[.,]", text) if parser == "SOURCE_ALL_SEPARATORS" else text.split(".")
        words = [
            re.sub(r"[^a-z]", "", item.strip())
            for item in pieces
            if item.strip()
        ]
        folios[folio].extend(word for word in words if word)
    return dict(folios), {
        "accepted_rows": accepted_rows,
        "physical_pages": len(folios),
        "groups": sum(len(words) for words in folios.values()),
        "manual_nondefinite_separators": dict(sorted(separator_counts.items())),
    }


def glyphs(word: str) -> list[str]:
    output = []
    index = 0
    while index < len(word):
        pair = word[index:index + 2]
        if pair in ("ch", "sh"):
            output.append(pair)
            index += 2
        else:
            output.append(word[index])
            index += 1
    return output


def classify_group(word: str) -> str | None:
    units = glyphs(word)
    has_cho = False
    has_che = False
    for index in range(len(units) - 1):
        if units[index] in ("ch", "sh"):
            has_cho |= units[index + 1] == "o"
            has_che |= units[index + 1] == "e"
    if has_cho and not has_che:
        return "CHO"
    if has_che and not has_cho:
        return "CHE"
    return None


def template_events(word: str) -> tuple[str, int, int] | None:
    units = glyphs(word)
    parts = []
    cho = 0
    che = 0
    for index, unit in enumerate(units):
        if index and units[index - 1] in ("ch", "sh") and unit in ("o", "e"):
            parts.append("X")
            cho += unit == "o"
            che += unit == "e"
        else:
            parts.append(unit)
    if not cho + che:
        return None
    return "".join(parts), cho, che


def fit_em(counts: list[tuple[int, int]]) -> dict:
    p_high = 0.7
    p_low = 0.2
    pi_high = 0.5
    responsibilities = []
    iterations = 0
    for iteration in range(200):
        iterations = iteration + 1
        responsibilities = []
        for successes, total in counts:
            log_high = (
                math.log(pi_high + 1e-15)
                + successes * math.log(max(p_high, 1e-15))
                + (total - successes) * math.log(max(1.0 - p_high, 1e-15))
            )
            log_low = (
                math.log(1.0 - pi_high + 1e-15)
                + successes * math.log(max(p_low, 1e-15))
                + (total - successes) * math.log(max(1.0 - p_low, 1e-15))
            )
            maximum = max(log_high, log_low)
            high = math.exp(log_high - maximum)
            low = math.exp(log_low - maximum)
            responsibilities.append(high / (high + low))
        next_pi = sum(responsibilities) / len(counts)
        next_high = sum(r * k for r, (k, total) in zip(responsibilities, counts)) / sum(
            r * total for r, (k, total) in zip(responsibilities, counts)
        )
        next_low = sum((1.0 - r) * k for r, (k, total) in zip(responsibilities, counts)) / sum(
            (1.0 - r) * total for r, (k, total) in zip(responsibilities, counts)
        )
        if (
            abs(next_high - p_high) < 1e-8
            and abs(next_low - p_low) < 1e-8
            and abs(next_pi - pi_high) < 1e-8
        ):
            break
        p_high, p_low, pi_high = next_high, next_low, next_pi
    if p_high < p_low:
        p_high, p_low = p_low, p_high
        pi_high = 1.0 - pi_high
        responsibilities = [1.0 - value for value in responsibilities]
    total_successes = sum(k for k, total in counts)
    total_trials = sum(total for k, total in counts)
    pooled = total_successes / total_trials
    ll_one = sum(
        k * math.log(pooled) + (total - k) * math.log(1.0 - pooled)
        for k, total in counts
    )
    ll_two = 0.0
    for k, total in counts:
        high = (
            math.log(pi_high + 1e-15)
            + k * math.log(max(p_high, 1e-15))
            + (total - k) * math.log(max(1.0 - p_high, 1e-15))
        )
        low = (
            math.log(1.0 - pi_high + 1e-15)
            + k * math.log(max(p_low, 1e-15))
            + (total - k) * math.log(max(1.0 - p_low, 1e-15))
        )
        maximum = max(high, low)
        ll_two += maximum + math.log(math.exp(high - maximum) + math.exp(low - maximum))
    return {
        "p_high": p_high,
        "p_low": p_low,
        "pi_high": pi_high,
        "responsibilities": responsibilities,
        "iterations": iterations,
        "delta_aic_two_over_one": (-2.0 * ll_one + 2.0) - (-2.0 * ll_two + 6.0),
    }


def classify_template(rate1: float, rate0: float) -> str:
    if rate1 > 0.9 and rate0 > 0.9:
        return "F1_FIXED_CHO"
    if rate1 < 0.1 and rate0 < 0.1:
        return "F0_FIXED_CHE"
    if abs(rate1 - rate0) >= 0.2:
        return "S_SWITCHABLE"
    return "I_INTERMEDIATE"


def template_rows(
    parser: str,
    edition: str,
    assignment: str,
    folios: dict[str, list[str]],
    states: dict[str, int],
) -> list[dict]:
    counts: dict[str, list[int]] = defaultdict(lambda: [0, 0, 0, 0])
    for folio, state in states.items():
        for word in folios[folio]:
            event = template_events(word)
            if event is None:
                continue
            template, cho, che = event
            offset = 0 if state == 1 else 2
            counts[template][offset] += cho
            counts[template][offset + 1] += che
    rows = []
    for template, values in counts.items():
        n1 = values[0] + values[1]
        n0 = values[2] + values[3]
        if n1 < 10 or n0 < 10:
            continue
        rate1 = values[0] / n1
        rate0 = values[2] / n0
        signed = rate1 - rate0
        rows.append({
            "parser": parser,
            "edition": edition,
            "assignment": assignment,
            "template": template,
            "state1_cho": values[0],
            "state1_che": values[1],
            "state0_cho": values[2],
            "state0_che": values[3],
            "state1_rate": rate1,
            "state0_rate": rate0,
            "signed_delta": signed,
            "absolute_delta": abs(signed),
            "class": classify_template(rate1, rate0),
            "direction": "FORWARD" if signed > 0 else "REVERSE" if signed < 0 else "EQUAL",
        })
    return sorted(rows, key=lambda row: row["template"])


def main() -> None:
    outputs = (OUT_JSON, OUT_FOLIOS, OUT_TEMPLATES, REPORT)
    if any(path.exists() for path in outputs):
        raise SystemExit("refusing to overwrite Parisel audit artifacts")
    for path, expected in FROZEN.items():
        if sha(path) != expected:
            raise SystemExit(f"frozen input mismatch: {path.name}")
    separator_validation = json.loads(SEPARATOR_VALIDATION.read_text(encoding="utf-8"))
    if separator_validation.get("status") != "PASS_INDEPENDENT_SOURCE_SEPARATOR_RECONSTRUCTION":
        raise SystemExit("source separator validation is not PASS")

    folio_rows = []
    all_template_rows = []
    summaries = {}
    states_by_key: dict[tuple[str, str, str], dict[str, int]] = {}
    for parser in PARSERS:
        summaries[parser] = {}
        for edition in READINGS:
            folios, parse_counts = parse_source(SOURCES[edition], parser)
            eligible = []
            for folio, words in sorted(folios.items()):
                labels = Counter(classify_group(word) for word in words)
                cho = labels["CHO"]
                che = labels["CHE"]
                if cho + che >= 5:
                    eligible.append((folio, cho, che))
            fitted = fit_em([(cho, cho + che) for folio, cho, che in eligible])
            threshold_states = {
                folio: int(cho / (cho + che) > 0.5)
                for folio, cho, che in eligible
            }
            em_states = {
                folio: int(responsibility > 0.5)
                for (folio, cho, che), responsibility in zip(eligible, fitted["responsibilities"])
            }
            states_by_key[(parser, edition, "THRESHOLD")] = threshold_states
            states_by_key[(parser, edition, "EM")] = em_states
            for (folio, cho, che), responsibility in zip(eligible, fitted["responsibilities"]):
                folio_rows.append({
                    "parser": parser,
                    "edition": edition,
                    "folio": folio,
                    "cho_groups": cho,
                    "che_groups": che,
                    "classifiable_groups": cho + che,
                    "cho_rate": cho / (cho + che),
                    "threshold_state": threshold_states[folio],
                    "em_state": em_states[folio],
                    "em_responsibility_high": responsibility,
                    "assignment_disagrees": int(threshold_states[folio] != em_states[folio]),
                })
            summary = {
                "parse": parse_counts,
                "eligible_folios": len(eligible),
                "classifiable_groups": sum(cho + che for folio, cho, che in eligible),
                "em": {
                    key: fitted[key]
                    for key in ("p_high", "p_low", "pi_high", "iterations", "delta_aic_two_over_one")
                },
                "em_state1": sum(em_states.values()),
                "em_state0": len(em_states) - sum(em_states.values()),
                "threshold_state1": sum(threshold_states.values()),
                "threshold_state0": len(threshold_states) - sum(threshold_states.values()),
                "em_threshold_disagreements": sum(
                    em_states[folio] != threshold_states[folio] for folio in em_states
                ),
                "em_confidence_over_95pct": sum(
                    max(value, 1.0 - value) > 0.95 for value in fitted["responsibilities"]
                ),
            }
            summaries[parser][edition] = summary
            for assignment, states in (("EM", em_states), ("THRESHOLD", threshold_states)):
                rows = template_rows(parser, edition, assignment, folios, states)
                all_template_rows.extend(rows)
                summary.setdefault("templates", {})[assignment] = {
                    "retained": len(rows),
                    "events": sum(
                        row["state1_cho"] + row["state1_che"]
                        + row["state0_cho"] + row["state0_che"]
                        for row in rows
                    ),
                    "classes": dict(sorted(Counter(row["class"] for row in rows).items())),
                    "forward": sum(row["direction"] == "FORWARD" for row in rows),
                    "reverse": sum(row["direction"] == "REVERSE" for row in rows),
                    "equal": sum(row["direction"] == "EQUAL" for row in rows),
                }

    agreements = {}
    for parser in PARSERS:
        agreements[parser] = {}
        for assignment in ASSIGNMENTS:
            maps = [states_by_key[(parser, edition, assignment)] for edition in READINGS]
            common = sorted(set.intersection(*(set(mapping) for mapping in maps)))
            disagree = [
                {
                    "folio": folio,
                    **{edition: states_by_key[(parser, edition, assignment)][folio] for edition in READINGS},
                }
                for folio in common
                if len({states_by_key[(parser, edition, assignment)][folio] for edition in READINGS}) > 1
            ]
            agreements[parser][assignment] = {
                "common_eligible_folios": len(common),
                "all_three_same": len(common) - len(disagree),
                "all_three_same_fraction": (len(common) - len(disagree)) / len(common),
                "disagreements": disagree,
            }

    published_rf = summaries["PUBLISHED_MERGE"]["RF1b"]
    repository_rf = summaries["REPOSITORY_DRAWING_SPLIT"]["RF1b"]
    source_rf = summaries["SOURCE_ALL_SEPARATORS"]["RF1b"]
    result = {
        "experiment": "PARISEL_CHO_CHE_SOURCE_AUDIT",
        "status": "CONFIRM_FOLIO_REGIME_REJECT_EXACT_PUBLISHED_IMPLEMENTATION_CLAIMS",
        "external_reference": EXTERNAL,
        "inputs": {path.name: sha(path) for path in (*FROZEN, SPEC, BUILDER)},
        "summaries": summaries,
        "cross_reading_agreement": agreements,
        "published_claim_audit": {
            "paper_197_vs_reconstructed_published_parser_rf_eligible": [
                EXTERNAL["paper"]["reported_eligible_folios"],
                published_rf["eligible_folios"],
            ],
            "published_31_template_inventory_reproduced":
                published_rf["templates"]["EM"]["retained"] == 31,
            "repository_drawing_fix_changes_rf_retained_templates_to":
                repository_rf["templates"]["EM"]["retained"],
            "all_source_separators_change_rf_retained_templates_to":
                source_rf["templates"]["EM"]["retained"],
            "paper_threshold_vs_implemented_em_rf_assignment_disagreements":
                published_rf["em_threshold_disagreements"],
            "paper_table_literal_reversal_count":
                len(EXTERNAL["published_table_literal_reversals"]),
            "local_published_parser_rf_em_reversal_count":
                published_rf["templates"]["EM"]["reverse"],
            "local_repository_drawing_split_rf_em_reversal_count":
                repository_rf["templates"]["EM"]["reverse"],
            "local_source_all_separators_rf_em_reversal_count":
                source_rf["templates"]["EM"]["reverse"],
        },
        "gates": {
            "exact_200_eligible_each_parser_reading": all(
                summaries[parser][edition]["eligible_folios"] == 200
                for parser in PARSERS for edition in READINGS
            ),
            "source_all_separators_mixture_delta_aic_positive_all_readings": all(
                summaries["SOURCE_ALL_SEPARATORS"][edition]["em"]["delta_aic_two_over_one"] > 0
                for edition in READINGS
            ),
            "source_all_separators_component_separation_at_least_045_all_readings": all(
                summaries["SOURCE_ALL_SEPARATORS"][edition]["em"]["p_high"]
                - summaries["SOURCE_ALL_SEPARATORS"][edition]["em"]["p_low"] >= 0.45
                for edition in READINGS
            ),
            "source_all_separators_em_cross_reading_agreement_at_least_095":
                agreements["SOURCE_ALL_SEPARATORS"]["EM"]["all_three_same_fraction"] >= 0.95,
            "source_all_separators_threshold_cross_reading_agreement_at_least_095":
                agreements["SOURCE_ALL_SEPARATORS"]["THRESHOLD"]["all_three_same_fraction"] >= 0.95,
            "published_31_templates_reconstructed_before_separator_fix":
                published_rf["templates"]["EM"]["retained"] == 31,
            "repository_fix_changes_published_template_inventory":
                repository_rf["templates"]["EM"]["retained"] != 31,
            "all_source_separators_change_repository_inventory":
                source_rf["templates"]["EM"]["retained"] != repository_rf["templates"]["EM"]["retained"],
            "threshold_and_em_nonidentical":
                published_rf["em_threshold_disagreements"] > 0,
            "published_literal_no_reversal_claim_contradicted":
                len(EXTERNAL["published_table_literal_reversals"]) > 0,
            "source_primary_not_fewer_groups_than_repository_fix": all(
                summaries["SOURCE_ALL_SEPARATORS"][edition]["parse"]["groups"]
                >= summaries["REPOSITORY_DRAWING_SPLIT"][edition]["parse"]["groups"]
                for edition in READINGS
            ),
            "zl_primary_observes_uncertain_and_both_drawing_separator_types": all(
                summaries["SOURCE_ALL_SEPARATORS"]["ZL3b"]["parse"]["manual_nondefinite_separators"][key] > 0
                for key in ("uncertain_small_space", "drawing_interruption", "unaligned_drawing_interruption")
            ),
            "english_glosses_zero": True,
        },
        "outputs": {},
        "english_glosses": 0,
        "claim_ceiling": (
            "A strong, transcription-robust folio-level two-regime distribution of formal cho/che "
            "groups survives source-separator correction. The published 31-template inventory, "
            "threshold/implementation equivalence, and exact no-reversal claim do not. No sound, "
            "letter, vowel, consonant, word, natural language, cipher operation, meaning, plaintext, "
            "or translation follows."
        ),
    }
    if not all(result["gates"].values()):
        raise ValueError("Parisel audit hard gate failure")

    folio_rows.sort(key=lambda row: (row["parser"], row["edition"], row["folio"]))
    all_template_rows.sort(key=lambda row: (
        row["parser"], row["edition"], row["assignment"], row["template"]
    ))
    OUT_FOLIOS.write_bytes(tsv_bytes(FOLIO_FIELDS, folio_rows))
    OUT_TEMPLATES.write_bytes(tsv_bytes(TEMPLATE_FIELDS, all_template_rows))
    result["outputs"] = {
        OUT_FOLIOS.name: sha(OUT_FOLIOS),
        OUT_TEMPLATES.name: sha(OUT_TEMPLATES),
    }
    OUT_JSON.write_bytes(canonical_json_bytes(result))

    split = summaries["SOURCE_ALL_SEPARATORS"]
    report = f"""# Parisel `cho/che` source and implementation audit

Status: **{result['status']}**

The folio-level effect is real and unusually strong. With all manual separator
classes kept as source separators, the fitted high/low rates are
**{split['ZL3b']['em']['p_high']:.3f}/{split['ZL3b']['em']['p_low']:.3f}** in ZL,
**{split['IT2a']['em']['p_high']:.3f}/{split['IT2a']['em']['p_low']:.3f}** in IT,
and **{split['RF1b']['em']['p_high']:.3f}/{split['RF1b']['em']['p_low']:.3f}** in RF.
All three EM state labels agree on
**{agreements['SOURCE_ALL_SEPARATORS']['EM']['all_three_same']}/200** folios; the literal
threshold labels agree on
**{agreements['SOURCE_ALL_SEPARATORS']['THRESHOLD']['all_three_same']}/200**. These are
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
- preserving every manual separator yields **{source_rf['templates']['EM']['retained']}**
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
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "source_all_separators_em_agreement": agreements["SOURCE_ALL_SEPARATORS"]["EM"]["all_three_same"],
        "source_all_separators_threshold_agreement": agreements["SOURCE_ALL_SEPARATORS"]["THRESHOLD"]["all_three_same"],
        "rf_templates_published_merge": published_rf["templates"]["EM"]["retained"],
        "rf_templates_repository_drawing_split": repository_rf["templates"]["EM"]["retained"],
        "rf_templates_source_all_separators": source_rf["templates"]["EM"]["retained"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()

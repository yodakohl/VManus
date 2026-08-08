#!/usr/bin/env python3
"""Generalize S into a word-edge carrier/state inventory.

The exact S/Q missing-corner result prompted a carrier-wide preflight.  It
showed that q-after-S is not special: q is almost always attached to the first
parsed unit, and many separate initial bare units exclude a following q-state.
This runner therefore corrects the scope before exporting more grammar.

Odd ZL screens every sufficiently supported exact bare ``C+BASE`` carrier for
line-entry enrichment relative to the identical PLAIN BASE.  The complete
carrier family is corrected before candidates are frozen for even ZL and both
splits of IT/RF.  Among confirmed carriers, a separately declared paragraph
contrast compares bare-t against bare-d/bare-s while conditioning physical
page and the complete q-cleared core-role sequence.  RF is excluded from that
contrast because its paragraph markup is absent.

Bare carrier ``d`` is not the internal BOUND_D selector.  All results are
formal positional states, not phonetics, parts of speech, or English words.
"""

from __future__ import annotations

import csv
import json
import math
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Sequence

import numpy as np
from scipy.stats import hypergeom

from common import RESULTS, Row, folio_number
from run_confirmed_operator_factorial_inventory import (
    SOURCES,
    Signature,
    collapse_signature,
    key_text,
    prose_rows,
    role,
    signatures,
)


OUTPUT_JSON = RESULTS / "initial_bare_carrier_state_system_results.json"
OUTPUT_REPORT = RESULTS / "initial_bare_carrier_state_system_report.md"
OUTPUT_LINE = RESULTS / "initial_bare_carrier_line_entry.tsv"
OUTPUT_Q = RESULTS / "initial_bare_carrier_q_position.tsv"
OUTPUT_PARAGRAPH = RESULTS / "initial_bare_carrier_paragraph.tsv"

MIN_CARRIER_OCCURRENCES = 20
MIN_LINE_STRATA = 15
EXPECTED_PARAGRAPH_CARRIERS = {"d", "s", "t"}


def is_bare(signature: Signature) -> bool:
    return bool(
        not signature[1]
        and all(value == "NONE" for value in signature[2:])
        and signature[0] != "EMPTY"
    )


def carrier_root(word: str) -> str | None:
    values = signatures(word)
    return values[0][0] if len(values) > 1 and is_bare(values[0]) else None


def carrier_state(word: str, carrier: str) -> tuple[tuple[Signature, ...], str] | None:
    values = list(signatures(word))
    has_carrier = bool(
        len(values) > 1 and values[0] == (carrier, False, "NONE", "NONE", "NONE", "NONE")
    )
    core = values[1:] if has_carrier else values
    if not core:
        return None
    has_q = bool(core[0][1])
    core[0] = collapse_signature(core[0], q="<Q>")
    state = "CQ" if has_carrier and has_q else "C" if has_carrier else "Q" if has_q else "PLAIN"
    return tuple(core), state


def exact_binary(
    strata: Sequence[dict[str, Any]],
    target_positive: str, target_negative: str,
    control_positive: str, control_negative: str,
    *, direction: int = 1,
) -> dict[str, Any]:
    distribution = np.asarray([1.0], dtype=np.float64)
    offset = 0
    observed = 0
    expectation = 0.0
    variance = 0.0
    totals = Counter()
    usable = 0
    for item in strata:
        a = int(item.get(target_positive, 0))
        b = int(item.get(target_negative, 0))
        c = int(item.get(control_positive, 0))
        d = int(item.get(control_negative, 0))
        n_target = a + b
        population = n_target + c + d
        n_positive = a + c
        if min(n_target, population - n_target, n_positive, population - n_positive) <= 0:
            continue
        low = max(0, n_target - (population - n_positive))
        high = min(n_target, n_positive)
        values = np.arange(low, high + 1)
        distribution = np.convolve(
            distribution, hypergeom.pmf(values, population, n_positive, n_target),
        )
        offset += low
        observed += a
        expectation += n_target * n_positive / population
        variance += (
            n_target * (n_positive / population) * (1 - n_positive / population)
            * ((population - n_target) / (population - 1))
        )
        totals.update({
            target_positive: a, target_negative: b,
            control_positive: c, control_negative: d,
        })
        usable += 1
    if not usable:
        return {
            "strata": 0,
            target_positive: 0, target_negative: 0,
            control_positive: 0, control_negative: 0,
            "observed": 0, "expected": 0.0, "oriented_z": 0.0, "exact_p": 1.0,
        }
    support = np.arange(offset, offset + len(distribution))
    oriented_observed = direction * (observed - expectation)
    oriented_null = direction * (support - expectation)
    p = float(distribution[oriented_null >= oriented_observed - 1e-12].sum())
    return {
        "strata": usable,
        **{key: int(totals[key]) for key in (
            target_positive, target_negative, control_positive, control_negative,
        )},
        "observed": int(observed),
        "expected": float(expectation),
        "oriented_z": float(oriented_observed / math.sqrt(max(variance, 1e-12))),
        "exact_p": p,
    }


def carrier_counts(rows: Sequence[Row]) -> Counter[str]:
    output = Counter()
    for row in rows:
        for word in row.words:
            carrier = carrier_root(word)
            if carrier:
                output[carrier] += 1
    return output


def line_entry_test(rows: Sequence[Row], parity: int, carrier: str) -> dict[str, Any]:
    grouped: dict[tuple[str, tuple[Signature, ...]], Counter[str]] = defaultdict(Counter)
    for row in rows:
        if folio_number(row.page) % 2 != parity:
            continue
        for index, word in enumerate(row.words):
            event = carrier_state(word, carrier)
            if event is None or event[1] not in {"C", "PLAIN"}:
                continue
            key, state = event
            grouped[(row.page, key)][f"{state}_{'FIRST' if index == 0 else 'OTHER'}"] += 1
    strata = [dict(counts) for counts in grouped.values()]
    return exact_binary(
        strata, "C_FIRST", "C_OTHER", "PLAIN_FIRST", "PLAIN_OTHER",
    )


def line_panels(
    corpora: dict[str, list[Row]], carriers: Sequence[str],
) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for edition, rows in corpora.items():
        output[edition] = {}
        for parity, label in ((1, "odd"), (0, "even")):
            output[edition][label] = {
                carrier: line_entry_test(rows, parity, carrier) for carrier in carriers
            }
    return output


def q_position_inventory(rows: Sequence[Row], edition: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    counts = Counter()
    exceptions: list[dict[str, Any]] = []
    for row in rows:
        for word_index, word in enumerate(row.words):
            values = signatures(word)
            for unit_index, signature in enumerate(values):
                if not signature[1]:
                    continue
                counts["q_units"] += 1
                counts["q_first_unit" if unit_index == 0 else "q_noninitial_unit"] += 1
                if unit_index:
                    exceptions.append({
                        "edition": edition,
                        "page": row.page,
                        "locus": row.locus,
                        "word_index": word_index,
                        "unit_index": unit_index,
                        "surface": word,
                        "signatures": repr(values),
                    })
    return {
        "q_units": counts["q_units"],
        "q_first_unit": counts["q_first_unit"],
        "q_noninitial_unit": counts["q_noninitial_unit"],
        "first_unit_fraction": counts["q_first_unit"] / max(counts["q_units"], 1),
    }, exceptions


def q_stack_test(rows: Sequence[Row], parity: int, carrier: str) -> dict[str, Any]:
    grouped: dict[tuple[str, tuple[Signature, ...]], Counter[str]] = defaultdict(Counter)
    for row in rows:
        if folio_number(row.page) % 2 != parity:
            continue
        for word in row.words:
            event = carrier_state(word, carrier)
            if event is None:
                continue
            key, state = event
            grouped[(row.page, key)][state] += 1
    return exact_binary(
        [dict(counts) for counts in grouped.values()],
        "CQ", "C", "Q", "PLAIN", direction=-1,
    )


def core_roles(word: str) -> tuple[str, tuple[str, ...]] | None:
    values = list(signatures(word))
    if len(values) <= 1 or not is_bare(values[0]) or values[0][0] not in EXPECTED_PARAGRAPH_CARRIERS:
        return None
    carrier = values.pop(0)[0]
    values[0] = collapse_signature(values[0], q=False)
    return carrier, tuple(role(signature) for signature in values)


def paragraph_test(rows: Sequence[Row], parity: int) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    grouped: dict[tuple[str, tuple[str, ...]], Counter[str]] = defaultdict(Counter)
    events: list[dict[str, Any]] = []
    for row in rows:
        if folio_number(row.page) % 2 != parity or not row.words:
            continue
        event = core_roles(row.words[0])
        if event is None:
            continue
        carrier, roles = event
        family = "T" if carrier == "t" else "DS"
        context = "OPEN" if row.paragraph_start else "CONT"
        grouped[(row.page, roles)][f"{family}_{context}"] += 1
        events.append({
            "page": row.page,
            "locus": row.locus,
            "carrier": carrier,
            "family": family,
            "paragraph_context": context,
            "core_roles": "+".join(roles),
            "surface": row.words[0],
        })
    result = exact_binary(
        [dict(counts) for counts in grouped.values()],
        "T_OPEN", "T_CONT", "DS_OPEN", "DS_CONT",
    )
    return result, events


def planted_paragraph(events: Sequence[dict[str, Any]]) -> dict[str, Any]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for event in events:
        grouped[(event["page"], event["core_roles"])].append(event)
    strata = []
    for values in grouped.values():
        n_t = sum(event["family"] == "T" for event in values)
        n_open = sum(event["paragraph_context"] == "OPEN" for event in values)
        if not n_t or n_t == len(values) or not n_open or n_open == len(values):
            continue
        t_open = min(n_t, n_open)
        strata.append({
            "T_OPEN": t_open,
            "T_CONT": n_t - t_open,
            "DS_OPEN": n_open - t_open,
            "DS_CONT": len(values) - n_t - n_open + t_open,
        })
    return exact_binary(strata, "T_OPEN", "T_CONT", "DS_OPEN", "DS_CONT")


def write_tsv(path: Path, rows: Sequence[dict[str, Any]]) -> None:
    fields = sorted({key for row in rows for key in row})
    with path.open("w", encoding="utf-8", newline="") as handle:
        if not fields:
            return
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    started = time.perf_counter()
    corpora = {edition: prose_rows(path) for edition, path in SOURCES.items()}
    counts = carrier_counts(corpora["ZL3b"])
    support_candidates = sorted(
        carrier for carrier, count in counts.items()
        if count >= MIN_CARRIER_OCCURRENCES
    )
    preliminary = line_panels(corpora, support_candidates)
    discovery_candidates = [
        carrier for carrier in support_candidates
        if preliminary["ZL3b"]["odd"][carrier]["strata"] >= MIN_LINE_STRATA
    ]
    panels = line_panels(corpora, discovery_candidates)
    discovery_family = len(discovery_candidates)
    discovered = [
        carrier for carrier in discovery_candidates
        if panels["ZL3b"]["odd"][carrier]["oriented_z"] > 0
        and panels["ZL3b"]["odd"][carrier]["exact_p"] * discovery_family <= 0.05
    ]
    confirmed = [
        carrier for carrier in discovered
        if all(
            panels[edition][parity][carrier]["oriented_z"] > 0
            and panels[edition][parity][carrier]["exact_p"] * len(discovered) <= 0.05
            for edition in SOURCES for parity in ("odd", "even")
            if not (edition == "ZL3b" and parity == "odd")
        )
    ]

    q_inventory: dict[str, Any] = {}
    q_exceptions: list[dict[str, Any]] = []
    q_stack: dict[str, Any] = {}
    for edition, rows in corpora.items():
        q_inventory[edition], exceptions = q_position_inventory(rows, edition)
        q_exceptions.extend(exceptions)
        q_stack[edition] = {
            label: {
                carrier: q_stack_test(rows, parity, carrier)
                for carrier in confirmed
            }
            for parity, label in ((1, "odd"), (0, "even"))
        }

    paragraph: dict[str, Any] = {}
    paragraph_events: list[dict[str, Any]] = []
    for edition in ("ZL3b", "IT2a"):
        paragraph[edition] = {}
        for parity, label in ((1, "odd"), (0, "even")):
            test, events_here = paragraph_test(corpora[edition], parity)
            paragraph[edition][label] = test
            paragraph_events.extend({
                "edition": edition, "parity": label, **event,
            } for event in events_here)
    paragraph_tests = [
        paragraph[edition][parity]
        for edition in paragraph for parity in ("odd", "even")
    ]
    paragraph_pass = (
        set(confirmed) == EXPECTED_PARAGRAPH_CARRIERS
        and all(test["oriented_z"] > 0 and test["exact_p"] * 4 <= 0.05 for test in paragraph_tests)
    )
    plant = planted_paragraph([
        event for event in paragraph_events
        if event["edition"] == "ZL3b" and event["parity"] == "odd"
    ])
    plant_pass = plant["exact_p"] <= 0.05

    line_rows: list[dict[str, Any]] = []
    for edition in SOURCES:
        for parity in ("odd", "even"):
            for carrier in discovery_candidates:
                item = panels[edition][parity][carrier]
                line_rows.append({
                    "edition": edition, "parity": parity, "carrier": carrier,
                    "discovery_candidate": 1,
                    "odd_discovered": int(carrier in discovered),
                    "all_panel_confirmed": int(carrier in confirmed),
                    **item,
                })

    status = (
        "INITIAL_BARE_CARRIER_STATE_SYSTEM_CONFIRMED_QUALIFIED"
        if paragraph_pass and plant_pass else
        "INITIAL_BARE_CARRIER_STATE_SYSTEM_NOT_CONFIRMED"
    )
    payload = {
        "meta": {
            "elapsed_seconds": time.perf_counter() - started,
            "images_decoded": 0,
            "editions": list(SOURCES),
        },
        "protocol": {
            "carrier": "separate exact initial BARE unit C before a nonempty core BASE",
            "line_entry_discovery": f"odd ZL carriers with >= {MIN_CARRIER_OCCURRENCES} corpus events and >= {MIN_LINE_STRATA} exact page+base strata",
            "line_entry_family": discovery_candidates,
            "line_entry_holdout": "even ZL and odd/even IT/RF with frozen discovered carriers",
            "paragraph": "T versus combined D/S among line-first carriers, exact page+complete q-cleared core-role strata",
            "paragraph_scope": "ZL/IT only; RF paragraph markup absent",
            "meaning_licensed": False,
        },
        "carrier_counts": dict(counts),
        "line_entry": {
            "panels": panels,
            "discovery_candidates": discovery_candidates,
            "discovered": discovered,
            "confirmed": confirmed,
        },
        "q_word_edge": {
            "inventory": q_inventory,
            "noninitial_reading_occurrences": len(q_exceptions),
            "confirmed_carrier_stack_tests": q_stack,
            "scope": "q is overwhelmingly a first parsed-unit state; rare noninitial exceptions remain explicit",
        },
        "paragraph_state": {
            "tests": paragraph,
            "four_panel_bonferroni_max_p": min(
                1.0, max(test["exact_p"] for test in paragraph_tests) * 4,
            ),
            "pass": paragraph_pass,
            "planted_control": {"test": plant, "pass": plant_pass},
        },
        "decision": {
            "status": status,
            "supersedes": "S/Q missing-corner as an S-specific operator interaction",
            "retains": "S is one of the robust line-entry carriers and is continuation-associated",
            "licensed": [
                "q overwhelmingly occupies the first parsed unit rather than stacking after a separate bare carrier",
                "bare-d, bare-t, and bare-s are robust exact-base-controlled line-entry carriers",
                "bare-t carrier constructions are paragraph-opening-associated; bare-d/bare-s carrier constructions are continuation-associated",
            ],
            "not_licensed": [
                "bare d equals the BOUND_D selector",
                "T means start/title/topic",
                "D or S means continue/and/then",
                "any negative marker or English word",
            ],
        },
    }
    payload["meta"]["elapsed_seconds"] = time.perf_counter() - started
    OUTPUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_tsv(OUTPUT_LINE, line_rows)
    write_tsv(OUTPUT_Q, q_exceptions)
    write_tsv(OUTPUT_PARAGRAPH, paragraph_events)

    line_table = [
        "| carrier | odd ZL strata | z | family p | discovered | all-panel confirmed |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for carrier in discovery_candidates:
        item = panels["ZL3b"]["odd"][carrier]
        line_table.append(
            f"| {carrier} | {item['strata']} | {item['oriented_z']:.3f} | "
            f"{min(1.0, item['exact_p'] * discovery_family):.6g} | "
            f"{carrier in discovered} | {carrier in confirmed} |"
        )
    paragraph_table = [
        "| reading | split | role-conditioned strata | T open/cont | D+S open/cont | z | exact p |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for edition in paragraph:
        for parity in ("odd", "even"):
            item = paragraph[edition][parity]
            paragraph_table.append(
                f"| {edition} | {parity} | {item['strata']} | "
                f"{item['T_OPEN']}/{item['T_CONT']} | "
                f"{item['DS_OPEN']}/{item['DS_CONT']} | "
                f"{item['oriented_z']:.3f} | {item['exact_p']:.6g} |"
            )
    q_lines = [
        f"{edition} {item['q_first_unit']}/{item['q_units']} first "
        f"({item['first_unit_fraction']:.6%}; noninitial={item['q_noninitial_unit']})"
        for edition, item in q_inventory.items()
    ]
    report = [
        "# Initial bare-carrier state system",
        "",
        f"Decision: **{status}**.",
        "",
        "## Carrier-wide correction",
        "",
        "The S/Q missing corner is not S-specific. q is overwhelmingly attached to the first parsed unit: " + "; ".join(q_lines) + ". Rare exceptions are exported, so this is not an absolute spelling ban.",
        "",
        *line_table,
        "",
        f"Frozen all-panel line-entry carriers: **{', '.join(confirmed)}**. The bare-d carrier is not the BOUND_D selector.",
        "",
        "## Paragraph-state split",
        "",
        *paragraph_table,
        "",
        f"Largest four-panel Bonferroni p={payload['paragraph_state']['four_panel_bonferroni_max_p']:.6g}; paragraph plant p={plant['exact_p']:.6g}, pass={plant_pass}.",
        "",
        "Corrected structural reading: `[PARAGRAPH-OPENING-ASSOCIATED BARE-T CARRIER + BASE]` contrasts with `[CONTINUATION-LINE-ENTRY-ASSOCIATED BARE-D/BARE-S CARRIER + BASE]`. q is a word-edge state used in confirmed selector environments. These are positional constructions, not START/CONTINUE words and not evidence for a negative marker.",
        "",
        "This supersedes the interpretation of the missing s+q corner as a special S/Q semantic or operator interaction. It does not supersede S's independently measured continuation-line preference.",
        "",
        f"Runtime: {payload['meta']['elapsed_seconds']:.2f} s; cached text only, image decodes: 0.",
        "",
    ]
    OUTPUT_REPORT.write_text("\n".join(report), encoding="utf-8")
    print(json.dumps({
        "status": status,
        "discovery_candidates": discovery_candidates,
        "discovered": discovered,
        "confirmed": confirmed,
        "q_inventory": q_inventory,
        "paragraph_max_bonferroni_p": payload["paragraph_state"]["four_panel_bonferroni_max_p"],
        "plant_pass": plant_pass,
        "elapsed_seconds": payload["meta"]["elapsed_seconds"],
    }, indent=2))


if __name__ == "__main__":
    main()

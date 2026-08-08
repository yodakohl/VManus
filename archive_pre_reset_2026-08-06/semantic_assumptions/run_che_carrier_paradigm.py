#!/usr/bin/env python3
"""Assemble the first exact four-form carrier paradigm around ``che``.

This runner does not search for an English gloss.  It combines three effects
that were established independently:

* plain BASE versus initial ``l+BASE``;
* plain BASE versus final ``BASE+od``; and
* the exact-base final switch ``BASE+ol`` versus ``BASE+od``.

It asks which canonical base has all four literal forms in every
ZL3b/IT2a/RF1b x odd/even Currier-B/hand-2 panel.  It also inventories every
E-bound frame followed internally by a final BARE value across the manuscript,
to determine whether the surviving base is an isolated curiosity or a
productive construction frame.
"""

from __future__ import annotations

import csv
import json
import math
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Sequence

from common import RESULTS, folio_number, parse_rows
from run_bath_ol_same_hand_falsifier import HAND, LANGUAGE, NEGATIVE, POSITIVE
from run_internal_utterance_grammar import SPACE_RULES, line_nodes
from run_section_content_bridge import SOURCES
from run_star_entry_label_gradient import label_corpus
from run_typology_neutral_structure import canonical_units, normalized_root, unit_role
import voynich_paradigm_decoder as paradigm


FIELD_OPERATOR_JSON = RESULTS / "residual_field_same_base_operators_results.json"
FIELD_SWITCH_JSON = RESULTS / "od_ol_exact_base_field_switch_results.json"
OUTPUT_JSON = RESULTS / "che_carrier_paradigm_results.json"
OUTPUT_REPORT = RESULTS / "che_carrier_paradigm_report.md"
OUTPUT_TSV = RESULTS / "che_carrier_paradigm_translation.tsv"
FORM_NAMES = ("PLAIN", "L_PREFIX", "OL_FINAL", "OD_FINAL")


def eligible_nodes(corpus: Any, parity: int):
    for row in corpus.rows:
        if (
            row.kind != "P" or row.section not in {POSITIVE, NEGATIVE}
            or row.language != LANGUAGE or row.hand != HAND
            or folio_number(row.page) % 2 != parity
        ):
            continue
        nodes = line_nodes(row)
        excluded = {
            index + 1
            for index, (left, right) in enumerate(zip(nodes, nodes[1:]))
            if SPACE_RULES["D_SELECT_Q"](left.last_role, right.first_role)
        }
        for word_index, node in enumerate(nodes):
            if word_index not in excluded:
                yield row, word_index, node


def panel_counts(corpus: Any, parity: int) -> dict[tuple[str, ...], Counter[str]]:
    counts: dict[tuple[str, ...], Counter[str]] = defaultdict(Counter)
    for row, _word_index, node in eligible_nodes(corpus, parity):
        counts[tuple(node.units)][row.section] += 1
    return counts


def form_units(base: tuple[str, ...]) -> dict[str, tuple[str, ...]]:
    return {
        "PLAIN": base,
        "L_PREFIX": ("l",) + base,
        "OL_FINAL": base + ("ol",),
        "OD_FINAL": base + ("od",),
    }


def complete_bases(
    counts: dict[tuple[str, ...], Counter[str]],
) -> set[tuple[str, ...]]:
    candidates = set(counts)
    return {
        base for base in candidates
        if base and all(sum(counts[units].values()) for units in form_units(base).values())
    }


def carrier_inventory(path: Path) -> dict[str, Any]:
    frames: dict[tuple[str, ...], Counter[str]] = defaultdict(Counter)
    for row in parse_rows(path):
        for surface in row.words:
            units = canonical_units(surface)
            if (
                len(units) < 2 or unit_role(units[-1]) != "BARE"
                or unit_role(units[-2]) not in {"BOUND_E", "Q_BOUND_E"}
            ):
                continue
            root = normalized_root(paradigm.strict_parse(units[-1])[0])
            frames[tuple(units[:-1])][root] += 1
    ranked = []
    for base, values in frames.items():
        events = sum(values.values())
        entropy = -sum(
            count / events * math.log2(count / events)
            for count in values.values()
        )
        ranked.append({
            "base": list(base), "events": events,
            "distinct_final_roots": len(values), "entropy_bits": entropy,
            "top_values": values.most_common(12),
        })
    ranked.sort(
        key=lambda row: (row["distinct_final_roots"], row["events"]), reverse=True,
    )
    for rank, row in enumerate(ranked, 1):
        row["diversity_rank"] = rank
    event_ranked = sorted(ranked, key=lambda row: row["events"], reverse=True)
    event_rank = {
        tuple(row["base"]): rank for rank, row in enumerate(event_ranked, 1)
    }
    for row in ranked:
        row["event_rank"] = event_rank[tuple(row["base"])]
    che = next(row for row in ranked if row["base"] == ["che"])
    return {"frame_count": len(ranked), "che": che, "top_frames": ranked[:12]}


def export_zl_occurrences(corpus: Any, base: tuple[str, ...]) -> list[dict[str, str]]:
    patterns = {units: form for form, units in form_units(base).items()}
    readings = {
        "PLAIN": "[E-BOUND CARRIER BASE=che; VALUE/ENGLISH LEXEME UNKNOWN]",
        "L_PREFIX": "[LINKED/DEPENDENT l+che CARRIER FORM; BATHING-ENRICHED]",
        "OL_FINAL": "[che CARRIER + BATHING-SIDE CLASS/STATE VALUE ol]",
        "OD_FINAL": "[che CARRIER + HERBAL-SIDE CLASS/STATE VALUE od]",
    }
    output = []
    for parity in (1, 0):
        for row, word_index, node in eligible_nodes(corpus, parity):
            form = patterns.get(tuple(node.units))
            if form is None:
                continue
            output.append({
                "page": row.page, "section": row.section, "locus": row.locus,
                "word_index": str(word_index + 1), "surface": node.surface,
                "canonical_units": "+".join(node.units), "form": form,
                "reading": readings[form],
            })
    return output


def write_tsv(rows: Sequence[dict[str, str]]) -> None:
    fields = (
        "page", "section", "locus", "word_index", "surface",
        "canonical_units", "form", "reading",
    )
    with OUTPUT_TSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def render_report(payload: dict[str, Any]) -> str:
    lines = [
        "# Exact four-form `che` carrier paradigm", "",
        f"Decision: **{payload['status']}**", "",
        "Holding canonical form literally fixed, only `che` has all four forms "
        "in every ZL3b/IT2a/RF1b x odd/even Currier-B/hand-2 panel:", "",
        "> `che` = `[E-BOUND CARRIER BASE; VALUE/LEX=?]`  ",
        "> `l+che` = `[LINKED/DEPENDENT CARRIER FORM; BATHING-ENRICHED]`  ",
        "> `che+ol` = `[CARRIER + BATHING-SIDE CLASS/STATE]`  ",
        "> `che+od` = `[CARRIER + HERBAL-SIDE CLASS/STATE]`", "",
        "| panel | plain B/H | l+che B/H | che+ol B/H | che+od B/H |",
        "|---|---:|---:|---:|---:|",
    ]
    for panel, row in payload["panels"].items():
        cells = []
        for form in FORM_NAMES:
            value = row["forms"][form]
            cells.append(f"{value.get(POSITIVE, 0)}/{value.get(NEGATIVE, 0)}")
        lines.append(f"| {panel} | " + " | ".join(cells) + " |")
    lines += [
        "", "## Why `che` looks like a frame, not a decoded noun", "",
        "Across the complete manuscript, `che` is the most productive exact "
        "E-bound frame before a final BARE value in every reading:", "",
        "| reading | carrier frames | che events | distinct final values | entropy | diversity rank | event rank |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for edition, inventory in payload["carrier_inventory"].items():
        che = inventory["che"]
        lines.append(
            f"| {edition} | {inventory['frame_count']} | {che['events']} | "
            f"{che['distinct_final_roots']} | {che['entropy_bits']:.3f} bits | "
            f"{che['diversity_rank']} | {che['event_rank']} |"
        )
    top = payload["carrier_inventory"]["ZL3b"]["che"]["top_values"]
    lines += [
        "", "ZL's most frequent values after the exact `che` frame are "
        + ", ".join(f"`{root}` ({count})" for root, count in top[:8]) + ".", "",
        "The four-form interpretation is a compositional grammatical skeleton, "
        "not a word-for-word plaintext. In particular, the evidence is more "
        "consistent with `che` being a reusable carrier/frame than with it being "
        "the noun for one pictured object. The English function of the frame "
        "and the values beyond independently grounded `ol`/`od` remain unknown.", "",
        f"ZL exact four-form occurrences exported: {payload['exported_occurrences']}. "
        f"Runtime: {payload['runtime_seconds']:.3f} seconds; cached text only.",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    started = time.perf_counter()
    dependencies = {
        "operators": json.loads(FIELD_OPERATOR_JSON.read_text(encoding="utf-8"))["status"],
        "switch": json.loads(FIELD_SWITCH_JSON.read_text(encoding="utf-8"))["status"],
    }
    corpora = {edition: label_corpus(path) for edition, path in SOURCES.items()}
    panels: dict[str, Any] = {}
    universal: set[tuple[str, ...]] | None = None
    for edition, corpus in corpora.items():
        for parity in (1, 0):
            counts = panel_counts(corpus, parity)
            bases = complete_bases(counts)
            universal = bases if universal is None else universal & bases
            name = f"{edition}:{'odd' if parity else 'even'}"
            panels[name] = {
                "complete_bases": [list(base) for base in sorted(bases)],
                "forms": {
                    form: dict(counts[units])
                    for form, units in form_units(("che",)).items()
                },
            }
    universal = universal or set()
    inventory = {
        edition: carrier_inventory(path) for edition, path in SOURCES.items()
    }
    dependency_pass = (
        dependencies["operators"] == "RESIDUAL_FIELD_SAME_BASE_OPERATORS_CONFIRMED"
        and dependencies["switch"] == "OD_OL_EXACT_BASE_FIELD_SWITCH_CONFIRMED"
    )
    inventory_pass = all(
        row["che"]["diversity_rank"] == 1 and row["che"]["event_rank"] == 1
        for row in inventory.values()
    )
    status = (
        "CHE_PRODUCTIVE_FOUR_FORM_CARRIER_PARADIGM_IDENTIFIED"
        if dependency_pass and universal == {("che",)} and inventory_pass
        else "CHE_FOUR_FORM_CARRIER_PARADIGM_NOT_CONFIRMED"
    )
    occurrences = export_zl_occurrences(corpora["ZL3b"], ("che",))
    payload = {
        "status": status, "dependency_status": dependencies,
        "universal_complete_bases": [list(base) for base in sorted(universal)],
        "panels": panels, "carrier_inventory": inventory,
        "exported_occurrences": len(occurrences),
        "runtime_seconds": time.perf_counter() - started,
    }
    write_tsv(occurrences)
    OUTPUT_JSON.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8",
    )
    report = render_report(payload)
    OUTPUT_REPORT.write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()

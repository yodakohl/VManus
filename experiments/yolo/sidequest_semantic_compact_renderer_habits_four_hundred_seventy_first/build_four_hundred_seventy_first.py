#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = ROOT / "experiments/yolo/sidequest_semantic_two_stage_renderer_four_hundred_seventieth"
PROSE = BASE / "FOUR_HUNDRED_SEVENTIETH_381_PROSE_TWO_STAGE_WRITER.tsv"
ASTRO = BASE / "FOUR_HUNDRED_SEVENTIETH_395_ASTRO_NAMESPACE_RENDERER.tsv"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(name)
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def majority(counter: Counter[str]) -> str:
    return sorted(counter, key=lambda item: (-counter[item], item))[0]


def main() -> None:
    prose = read(PROSE)
    body_counts: dict[str, Counter[str]] = defaultdict(Counter)
    for row in prose:
        body_counts[row["body_surface"]][row["observed_wrapper"]] += 1
    body_default = {body: majority(counts) for body, counts in body_counts.items()}

    prose_groups: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in prose:
        prose_groups[(row["body_surface"], row["register"], row["field_position"])].append(row)
    candidate_prose = []
    for key, rows in prose_groups.items():
        counts = Counter(row["observed_wrapper"] for row in rows)
        proposed = majority(counts)
        old_correct = sum(row["observed_wrapper"] == body_default[row["body_surface"]] for row in rows)
        new_correct = sum(row["observed_wrapper"] == proposed for row in rows)
        gain = new_correct - old_correct
        if gain >= 2:
            candidate_prose.append((key, proposed, gain, rows, counts))

    astro = read(ASTRO)
    parse_counts: dict[str, Counter[str]] = defaultdict(Counter)
    for row in astro:
        parse_counts[row["formal_parse"]][row["observed_surface"]] += 1
    parse_default = {parse: majority(counts) for parse, counts in parse_counts.items()}
    astro_groups: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in astro:
        astro_groups[(row["formal_parse"], row["local_namespace"], row["locus_position"])].append(row)
    candidate_astro = []
    for key, rows in astro_groups.items():
        counts = Counter(row["observed_surface"] for row in rows)
        proposed = majority(counts)
        old_correct = sum(row["observed_surface"] == parse_default[row["formal_parse"]] for row in rows)
        new_correct = sum(row["observed_surface"] == proposed for row in rows)
        gain = new_correct - old_correct
        if gain >= 2:
            candidate_astro.append((key, proposed, gain, rows, counts))

    habits = []
    prose_override = {}
    for key, proposed, gain, rows, counts in sorted(candidate_prose, key=lambda item: (-item[2], item[0])):
        body, register, position = key
        prose_override[key] = proposed
        habits.append({
            "habit_no": len(habits) + 1,
            "domain": "PROSE",
            "body_or_parse": body,
            "register_or_namespace": register,
            "position": position,
            "default_surface_or_wrapper": body_default[body],
            "override_surface_or_wrapper": proposed,
            "support_items": len(rows),
            "net_exact_gain": gain,
            "teaching_habit_de": f"Bei {body} in {register} an Position {position} setze Wrapper {proposed}.",
        })
    astro_override = {}
    for key, proposed, gain, rows, counts in sorted(candidate_astro, key=lambda item: (-item[2], item[0])):
        parse, namespace, position = key
        astro_override[key] = proposed
        habits.append({
            "habit_no": len(habits) + 1,
            "domain": "ASTRO",
            "body_or_parse": parse,
            "register_or_namespace": namespace,
            "position": position,
            "default_surface_or_wrapper": parse_default[parse],
            "override_surface_or_wrapper": proposed,
            "support_items": len(rows),
            "net_exact_gain": gain,
            "teaching_habit_de": f"Bei {parse} in {namespace} an Position {position} schreibe {proposed}.",
        })
    write("FOUR_HUNDRED_SEVENTY_FIRST_NINE_RENDERER_HABITS.tsv", habits)

    body_defaults = []
    for body, counts in sorted(body_counts.items()):
        body_defaults.append({
            "body_no": len(body_defaults) + 1,
            "body_surface": body,
            "default_wrapper": body_default[body],
            "support_events": sum(counts.values()),
            "wrapper_counts": "|".join(f"{wrapper}:{counts[wrapper]}" for wrapper in sorted(counts)),
        })
    write("FOUR_HUNDRED_SEVENTY_FIRST_173_BODY_DEFAULT_WRAPPERS.tsv", body_defaults)

    astro_defaults = []
    for parse, counts in sorted(parse_counts.items()):
        astro_defaults.append({
            "parse_no": len(astro_defaults) + 1,
            "formal_parse": parse,
            "default_surface": parse_default[parse],
            "support_groups": sum(counts.values()),
            "surface_counts": "|".join(f"{surface}:{counts[surface]}" for surface in sorted(counts)),
        })
    write("FOUR_HUNDRED_SEVENTY_FIRST_ASTRO_PARSE_DEFAULT_SURFACES.tsv", astro_defaults)

    predictions = []
    for row in prose:
        key = (row["body_surface"], row["register"], row["field_position"])
        wrapper = prose_override.get(key, body_default[row["body_surface"]])
        surface = row["body_surface"] if wrapper == "NONE" else wrapper + row["body_surface"]
        predictions.append({
            "writer_order": len(predictions) + 1,
            "domain": "PROSE",
            "item_id": row["event_id"],
            "unit_id": row["record_unit_id"],
            "page": row["page"],
            "locus": row["locus"],
            "formal_parse": row["component_parse"],
            "default_surface": (row["body_surface"] if body_default[row["body_surface"]] == "NONE" else body_default[row["body_surface"]] + row["body_surface"]),
            "habit_applied": "YES" if key in prose_override else "NO",
            "predicted_surface": surface,
            "observed_surface": row["observed_surface"],
            "exact_without_exemplar": "YES" if surface == row["observed_surface"] else "NO",
        })
    for row in astro:
        key = (row["formal_parse"], row["local_namespace"], row["locus_position"])
        surface = astro_override.get(key, parse_default[row["formal_parse"]])
        predictions.append({
            "writer_order": len(predictions) + 1,
            "domain": "ASTRO",
            "item_id": row["unified_id"],
            "unit_id": row["unit_id"],
            "page": row["page"],
            "locus": row["locus"],
            "formal_parse": row["formal_parse"],
            "default_surface": parse_default[row["formal_parse"]],
            "habit_applied": "YES" if key in astro_override else "NO",
            "predicted_surface": surface,
            "observed_surface": row["observed_surface"],
            "exact_without_exemplar": "YES" if surface == row["observed_surface"] else "NO",
        })
    write("FOUR_HUNDRED_SEVENTY_FIRST_776_COMPACT_RENDERER_PREDICTIONS.tsv", predictions)

    exceptions = []
    for row in predictions:
        if row["exact_without_exemplar"] == "NO":
            exceptions.append({
                "exception_no": len(exceptions) + 1,
                "domain": row["domain"],
                "item_id": row["item_id"],
                "unit_id": row["unit_id"],
                "page": row["page"],
                "locus": row["locus"],
                "formal_parse": row["formal_parse"],
                "compact_predicted_surface": row["predicted_surface"],
                "exemplar_surface": row["observed_surface"],
                "apprentice_action": "copy the local exemplar surface",
            })
    write("FOUR_HUNDRED_SEVENTY_FIRST_113_EXEMPLAR_RENDERER_EXCEPTIONS.tsv", exceptions)

    models = [
        {"model": "DOMAIN_DEFAULT_ONLY", "extra_habits": 0, "exact_groups": 642, "exemplar_exceptions": 134, "incremental_memory_items": 134},
        {"model": "NINE_REPEATED_HABITS", "extra_habits": len(habits), "exact_groups": sum(row["exact_without_exemplar"] == "YES" for row in predictions), "exemplar_exceptions": len(exceptions), "incremental_memory_items": len(habits) + len(exceptions)},
        {"model": "PASS470_LOOKUP_RENDERER", "extra_habits": 673, "exact_groups": 732, "exemplar_exceptions": 44, "incremental_memory_items": 717},
        {"model": "OCCURRENCE_EXEMPLAR", "extra_habits": 0, "exact_groups": 776, "exemplar_exceptions": 776, "incremental_memory_items": 776},
    ]
    write("FOUR_HUNDRED_SEVENTY_FIRST_RENDERER_COMPLEXITY_COMPARISON.tsv", models)

    md = ["# Nine renderer habits for an apprentice", ""]
    for row in habits:
        md.append(f"{row['habit_no']}. {row['teaching_habit_de']}")
    md.extend(["", "All other cards use their body or parse default. If that still differs from the master exemplar, copy one of the 113 listed local exceptions."])
    (HERE / "FOUR_HUNDRED_SEVENTY_FIRST_COMPACT_APPRENTICE_RENDERER.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    summary = {
        "status": "PASS",
        "renderer_habits": len(habits),
        "prose_exact": sum(row["domain"] == "PROSE" and row["exact_without_exemplar"] == "YES" for row in predictions),
        "astro_exact": sum(row["domain"] == "ASTRO" and row["exact_without_exemplar"] == "YES" for row in predictions),
        "combined_exact": sum(row["exact_without_exemplar"] == "YES" for row in predictions),
        "exemplar_exceptions": len(exceptions),
        "incremental_memory_items": len(habits) + len(exceptions),
    }
    (HERE / "FOUR_HUNDRED_SEVENTY_FIRST_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

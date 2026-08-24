#!/usr/bin/env python3
from __future__ import annotations

import csv
import io
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PROSE = ROOT / "experiments/yolo/sidequest_semantic_common_action_roots_four_hundred_sixty_eighth/FOUR_HUNDRED_SIXTY_EIGHTH_381_PROSE_EVENT_COMMON_ACTIONS.tsv"
LEDGER = ROOT / "experiments/yolo/sidequest_semantic_common_action_roots_four_hundred_sixty_eighth/FOUR_HUNDRED_SIXTY_EIGHTH_776_GROUP_COMMON_ACTION_LEDGER.tsv"

PAGES = ("f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r")
QUERY_COLUMNS = (
    "page,locus,group_index,group_count,register,hand,within_field_position,"
    "joint_tuple_id,host_id,observed_wrapper,known_label_renderer,renderer_state"
)


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


def guarded_gdt327_rows() -> tuple[list[dict[str, str]], dict[str, int]]:
    command = [str(ROOT / "vmanus-exp"), "query-tsv", "gdt327_joint_tuple_interlinear.tsv", "--selector", "page"]
    for page in PAGES:
        command.extend(["--allow", page])
    command.extend(["--columns", QUERY_COLUMNS, "--forbid-prefix", "f84"])
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=True)
    rows = list(csv.DictReader(io.StringIO(result.stdout), delimiter="\t"))
    stats_line = next(line for line in result.stderr.splitlines() if line.startswith("GUARD_STATS "))
    return rows, json.loads(stats_line.removeprefix("GUARD_STATS "))


def main() -> None:
    prose = read(PROSE)
    formal, guard_stats = guarded_gdt327_rows()
    if len(prose) != 381 or len(formal) != 381:
        raise ValueError((len(prose), len(formal)))
    for event, source in zip(prose, formal):
        if event["joint_tuple_id"] != source["joint_tuple_id"]:
            raise ValueError(event["event_id"])
        wrapper = source["observed_wrapper"]
        surface = event["surface"]
        if wrapper != "NONE" and not surface.startswith(wrapper):
            raise ValueError((event["event_id"], wrapper, surface))
        body = surface if wrapper == "NONE" else surface[len(wrapper):]
        source.update({
            "event_id": event["event_id"],
            "record_unit_id": event["record_unit_id"],
            "statement_id": event["statement_id"],
            "component_parse": event["component_parse"],
            "atomic_default_de": event["small_value_de"],
            "visible_surface": surface,
            "body_surface": body,
        })

    previous_wrapper = "START"
    previous_locus = None
    for row in formal:
        locus_key = (row["page"], row["locus"])
        row["previous_wrapper"] = "START" if locus_key != previous_locus else previous_wrapper
        previous_wrapper = row["observed_wrapper"]
        previous_locus = locus_key

    bodies_by_id: dict[str, set[str]] = defaultdict(set)
    events_by_id: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in formal:
        bodies_by_id[row["joint_tuple_id"]].add(row["body_surface"])
        events_by_id[row["joint_tuple_id"]].append(row)
    if any(len(values) != 1 for values in bodies_by_id.values()):
        raise ValueError("body instability")
    body_rows = []
    for joint_id, rows in sorted(events_by_id.items(), key=lambda item: min(int(row["event_id"][1:]) for row in item[1])):
        body = next(iter(bodies_by_id[joint_id]))
        body_rows.append({
            "body_no": len(body_rows) + 1,
            "joint_tuple_id": joint_id,
            "component_parse": rows[0]["component_parse"],
            "atomic_default_de": rows[0]["atomic_default_de"],
            "body_surface": body,
            "events": len(rows),
            "event_ids": "|".join(row["event_id"] for row in rows),
            "attested_wrappers": "|".join(sorted({row["observed_wrapper"] for row in rows})),
            "surface_rule": "observed_wrapper + body_surface; omit NONE",
        })
    write("FOUR_HUNDRED_SEVENTIETH_173_PROSE_BODY_LEXICON.tsv", body_rows)

    base_counts: dict[tuple[str, str, str], Counter[str]] = defaultdict(Counter)
    expanded_counts: dict[tuple[str, str, str, str], Counter[str]] = defaultdict(Counter)
    for row in formal:
        base = (row["body_surface"], row["register"], row["within_field_position"])
        expanded = base + (row["previous_wrapper"],)
        base_counts[base][row["observed_wrapper"]] += 1
        expanded_counts[expanded][row["observed_wrapper"]] += 1

    prose_predictions = []
    rule_keys = {}
    for row in formal:
        base = (row["body_surface"], row["register"], row["within_field_position"])
        expanded = base + (row["previous_wrapper"],)
        if len(base_counts[base]) == 1:
            predicted = next(iter(base_counts[base]))
            layer = "UNIQUE_BODY_REGISTER_POSITION"
        elif len(expanded_counts[expanded]) == 1:
            predicted = next(iter(expanded_counts[expanded]))
            layer = "PREVIOUS_WRAPPER_RESOLVES"
        else:
            predicted = majority(expanded_counts[expanded])
            layer = "EXPANDED_KEY_MAJORITY"
        predicted_surface = row["body_surface"] if predicted == "NONE" else predicted + row["body_surface"]
        rule_keys[expanded] = (predicted, layer, expanded_counts[expanded])
        prose_predictions.append({
            "event_id": row["event_id"],
            "record_unit_id": row["record_unit_id"],
            "statement_id": row["statement_id"],
            "page": row["page"],
            "locus": row["locus"],
            "component_parse": row["component_parse"],
            "joint_tuple_id": row["joint_tuple_id"],
            "body_surface": row["body_surface"],
            "register": row["register"],
            "field_position": row["within_field_position"],
            "previous_wrapper": row["previous_wrapper"],
            "predicted_wrapper": predicted,
            "observed_wrapper": row["observed_wrapper"],
            "predicted_surface": predicted_surface,
            "observed_surface": row["visible_surface"],
            "selection_layer": layer,
            "exact_surface_match": "YES" if predicted_surface == row["visible_surface"] else "NO",
        })
    write("FOUR_HUNDRED_SEVENTIETH_381_PROSE_TWO_STAGE_WRITER.tsv", prose_predictions)

    key_rows = []
    for key, (predicted, layer, counts) in sorted(rule_keys.items()):
        body, register, position, previous = key
        key_rows.append({
            "rule_no": len(key_rows) + 1,
            "body_surface": body,
            "register": register,
            "field_position": position,
            "previous_wrapper": previous,
            "predicted_wrapper": predicted,
            "selection_layer": layer,
            "support_events": sum(counts.values()),
            "observed_wrapper_counts": "|".join(f"{item}:{counts[item]}" for item in sorted(counts)),
        })
    write("FOUR_HUNDRED_SEVENTIETH_PROSE_WRAPPER_RULEBOOK.tsv", key_rows)

    ledger = read(LEDGER)
    astro = [row for row in ledger if row["domain"] == "ASTRO"]
    by_locus: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in astro:
        by_locus[(row["unit_id"], row["locus"])].append(row)
    for rows in by_locus.values():
        for index, row in enumerate(rows):
            row["locus_position"] = "ONLY" if len(rows) == 1 else "FIRST" if index == 0 else "LAST" if index == len(rows) - 1 else "MIDDLE"
    astro_counts: dict[tuple[str, str, str], Counter[str]] = defaultdict(Counter)
    for row in astro:
        key = (row["formal_parse"], row["owner_or_namespace"], row["locus_position"])
        astro_counts[key][row["visible_surface"]] += 1
    astro_predictions = []
    for row in astro:
        key = (row["formal_parse"], row["owner_or_namespace"], row["locus_position"])
        predicted = majority(astro_counts[key])
        astro_predictions.append({
            "unified_id": row["unified_id"],
            "unit_id": row["unit_id"],
            "page": row["page"],
            "locus": row["locus"],
            "formal_parse": row["formal_parse"],
            "atomic_default_de": row["atomic_default_de"],
            "local_namespace": row["owner_or_namespace"],
            "locus_position": row["locus_position"],
            "predicted_surface": predicted,
            "observed_surface": row["visible_surface"],
            "exact_surface_match": "YES" if predicted == row["visible_surface"] else "NO",
            "renderer_rule": "PARSE_PLUS_NAMESPACE_PLUS_LOCUS_POSITION",
        })
    write("FOUR_HUNDRED_SEVENTIETH_395_ASTRO_NAMESPACE_RENDERER.tsv", astro_predictions)

    astro_key_rows = []
    for key, counts in sorted(astro_counts.items()):
        parse, namespace, position = key
        astro_key_rows.append({
            "rule_no": len(astro_key_rows) + 1,
            "formal_parse": parse,
            "local_namespace": namespace,
            "locus_position": position,
            "predicted_surface": majority(counts),
            "support_groups": sum(counts.values()),
            "surface_counts": "|".join(f"{surface}:{counts[surface]}" for surface in sorted(counts)),
        })
    write("FOUR_HUNDRED_SEVENTIETH_ASTRO_RENDERER_RULEBOOK.tsv", astro_key_rows)

    exceptions = []
    for row in prose_predictions:
        if row["exact_surface_match"] == "NO":
            exceptions.append({
                "exception_no": len(exceptions) + 1,
                "domain": "PROSE",
                "item_id": row["event_id"],
                "unit_id": row["record_unit_id"],
                "page": row["page"],
                "locus": row["locus"],
                "formal_parse": row["component_parse"],
                "predicted_surface": row["predicted_surface"],
                "observed_surface": row["observed_surface"],
                "copy_rule": "copy observed scribe allograph from local exemplar",
            })
    for row in astro_predictions:
        if row["exact_surface_match"] == "NO":
            exceptions.append({
                "exception_no": len(exceptions) + 1,
                "domain": "ASTRO",
                "item_id": row["unified_id"],
                "unit_id": row["unit_id"],
                "page": row["page"],
                "locus": row["locus"],
                "formal_parse": row["formal_parse"],
                "predicted_surface": row["predicted_surface"],
                "observed_surface": row["observed_surface"],
                "copy_rule": "copy observed diagram allograph from local exemplar",
            })
    write("FOUR_HUNDRED_SEVENTIETH_RENDERER_EXCEPTIONS.tsv", exceptions)

    combined = []
    for row in prose_predictions:
        combined.append({
            "writer_order": len(combined) + 1,
            "domain": "PROSE",
            "item_id": row["event_id"],
            "unit_id": row["record_unit_id"],
            "page": row["page"],
            "locus": row["locus"],
            "formal_parse": row["component_parse"],
            "predicted_surface": row["predicted_surface"],
            "observed_surface": row["observed_surface"],
            "exact_without_exception": row["exact_surface_match"],
            "exact_with_exception_deck": "YES",
        })
    for row in astro_predictions:
        combined.append({
            "writer_order": len(combined) + 1,
            "domain": "ASTRO",
            "item_id": row["unified_id"],
            "unit_id": row["unit_id"],
            "page": row["page"],
            "locus": row["locus"],
            "formal_parse": row["formal_parse"],
            "predicted_surface": row["predicted_surface"],
            "observed_surface": row["observed_surface"],
            "exact_without_exception": row["exact_surface_match"],
            "exact_with_exception_deck": "YES",
        })
    write("FOUR_HUNDRED_SEVENTIETH_776_TWO_STAGE_SURFACE_WRITER.tsv", combined)

    summary = {
        "status": "PASS",
        "guard_stats": guard_stats,
        "prose_bodies": len(body_rows),
        "wrapper_inventory": sorted({row["observed_wrapper"] for row in formal}),
        "prose_exact_without_exceptions": sum(row["exact_surface_match"] == "YES" for row in prose_predictions),
        "prose_renderer_exceptions": sum(row["exact_surface_match"] == "NO" for row in prose_predictions),
        "astro_exact_without_exceptions": sum(row["exact_surface_match"] == "YES" for row in astro_predictions),
        "astro_renderer_exceptions": sum(row["exact_surface_match"] == "NO" for row in astro_predictions),
        "combined_exact_without_exceptions": sum(row["exact_without_exception"] == "YES" for row in combined),
        "combined_exact_with_exception_deck": sum(row["exact_with_exception_deck"] == "YES" for row in combined),
        "prose_wrapper_rules": len(key_rows),
        "astro_renderer_rules": len(astro_key_rows),
    }
    (HERE / "FOUR_HUNDRED_SEVENTIETH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

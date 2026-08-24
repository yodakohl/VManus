#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P470 = ROOT / "experiments/yolo/sidequest_semantic_two_stage_renderer_four_hundred_seventieth"
P486 = ROOT / "experiments/yolo/sidequest_semantic_flexible_renderer_four_hundred_eighty_sixth"

PROFILE_BY_UNIT = {
    **{f"H{index}": "P1_EARLY_HERBAL" for index in range(1, 4)},
    **{f"H{index}": "P2_LATE_HERBAL" for index in range(4, 6)},
    **{f"B{index}": "P3_BIOLOGICAL" for index in range(1, 7)},
    **{f"A{index}": "P4_CELESTIAL" for index in range(1, 4)},
}
PROFILES = tuple(dict.fromkeys(PROFILE_BY_UNIT.values()))
INNER_DEFAULTS = {
    "P1_EARLY_HERBAL": {"Y": "chey", "AIIN": "daiin", "AL": "dal", "AR": "char"},
    "P2_LATE_HERBAL": {"Y": "y", "AIIN": "aiin", "AL": "al", "AR": "ar"},
    "P3_BIOLOGICAL": {"Y": "dy", "AIIN": "saiin", "AL": "sal", "AR": "sar"},
    "P4_CELESTIAL": {"Y": "chy", "AIIN": "daiin", "AL": "dal", "AR": "dar"},
}


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


def majority(counts: Counter[str]) -> str:
    return sorted(counts, key=lambda value: (-counts[value], value))[0]


def inner_render(parse: str, profile: str) -> str:
    values = INNER_DEFAULTS[profile]
    fixed = {"K": "k", "OK": "ok", "O": "o", "E": "e", "OT": "ot"}
    return "".join(values.get(component, fixed.get(component, component.lower())) for component in parse.split("+"))


def main() -> None:
    cases = read(P486 / "FOUR_HUNDRED_EIGHTY_SIXTH_113_EXCEPTION_RECLASSIFICATION.tsv")
    prose = {row["event_id"]: row for row in read(P470 / "FOUR_HUNDRED_SEVENTIETH_381_PROSE_TWO_STAGE_WRITER.tsv")}
    astro = {row["unified_id"]: row for row in read(P470 / "FOUR_HUNDRED_SEVENTIETH_395_ASTRO_NAMESPACE_RENDERER.tsv")}
    entry = [row for row in cases if row["generative_class"] == "ENTRY_WRAPPER_ALLOGRAPH"]
    for row in entry:
        source = prose[row["item_id"]] if row["domain"] == "PROSE" else astro[row["item_id"]]
        row["position"] = source["field_position"] if row["domain"] == "PROSE" else source["locus_position"]
        row["profile"] = PROFILE_BY_UNIT[row["unit_id"]]

    global_counts: dict[str, Counter[str]] = defaultdict(Counter)
    profile_counts: dict[tuple[str, str], Counter[str]] = defaultdict(Counter)
    positional_counts: dict[tuple[str, str, str], Counter[str]] = defaultdict(Counter)
    for row in entry:
        global_counts[row["old_wrapper"]][row["new_wrapper"]] += 1
        profile_counts[(row["profile"], row["old_wrapper"])][row["new_wrapper"]] += 1
        positional_counts[(row["profile"], row["position"], row["old_wrapper"])][row["new_wrapper"]] += 1

    profile_rows = []
    for (profile, old), counts in sorted(profile_counts.items()):
        preferred = majority(counts)
        profile_rows.append({
            "profile": profile,
            "input_wrapper": old,
            "preferred_wrapper": preferred,
            "support_choices": sum(counts.values()),
            "preferred_choices": counts[preferred],
            "all_observed_choices": "|".join(f"{wrapper}:{counts[wrapper]}" for wrapper in sorted(counts)),
            "teaching_rule_de": f"Wenn die Meisterform mit {old} eintritt, bevorzugt {profile} die Form {preferred}; andere gelernte Wrapper bleiben erlaubt.",
        })
    write("FOUR_HUNDRED_EIGHTY_SEVENTH_TWENTY_PROFILE_PREFERENCES.tsv", profile_rows)

    positional_rows = []
    for (profile, position, old), counts in sorted(positional_counts.items()):
        preferred = majority(counts)
        positional_rows.append({
            "profile": profile,
            "position": position,
            "input_wrapper": old,
            "preferred_wrapper": preferred,
            "support_choices": sum(counts.values()),
            "preferred_choices": counts[preferred],
        })
    write("FOUR_HUNDRED_EIGHTY_SEVENTH_FORTY_ONE_POSITIONAL_PREFERENCES.tsv", positional_rows)

    profile_map = {(row["profile"], row["input_wrapper"]): row["preferred_wrapper"] for row in profile_rows}
    positional_map = {(row["profile"], row["position"], row["input_wrapper"]): row["preferred_wrapper"] for row in positional_rows}
    audit = []
    for row in entry:
        global_prediction = majority(global_counts[row["old_wrapper"]])
        profile_prediction = profile_map[(row["profile"], row["old_wrapper"])]
        positional_prediction = positional_map[(row["profile"], row["position"], row["old_wrapper"])]
        audit.append({
            "choice_order": len(audit) + 1,
            "domain": row["domain"],
            "item_id": row["item_id"],
            "unit_id": row["unit_id"],
            "page": row["page"],
            "position": row["position"],
            "profile": row["profile"],
            "body": row["preserved_body"],
            "input_wrapper": row["old_wrapper"],
            "observed_wrapper": row["new_wrapper"],
            "global_prediction": global_prediction,
            "global_exact": "YES" if global_prediction == row["new_wrapper"] else "NO",
            "profile_prediction": profile_prediction,
            "profile_exact": "YES" if profile_prediction == row["new_wrapper"] else "NO",
            "positional_prediction": positional_prediction,
            "positional_exact": "YES" if positional_prediction == row["new_wrapper"] else "NO",
        })
    write("FOUR_HUNDRED_EIGHTY_SEVENTH_102_OBSERVED_CHOICE_AUDIT.tsv", audit)

    copies = []
    for row in cases:
        for profile in PROFILES:
            if row["generative_class"] == "ENTRY_WRAPPER_ALLOGRAPH":
                old = row["old_wrapper"]
                chosen = profile_map.get((profile, old), old)
                chosen_text = "" if chosen == "BARE" else chosen
                generated = chosen_text + row["preserved_body"]
                choice_rule = f"{old}->{chosen}"
            else:
                generated = inner_render(row["formal_parse"], profile)
                choice_rule = row["generative_class"]
            copies.append({
                "copy_order": len(copies) + 1,
                "source_item_id": row["item_id"],
                "source_unit_id": row["unit_id"],
                "formal_parse": row["formal_parse"],
                "profile": profile,
                "choice_rule": choice_rule,
                "generated_surface": generated,
                "observed_surface": row["observed_surface"],
                "same_formal_card": "YES",
            })
    write("FOUR_HUNDRED_EIGHTY_SEVENTH_452_FOUR_PROFILE_TEACHING_COPIES.tsv", copies)

    summary = {
        "status": "PASS",
        "profiles": len(PROFILES),
        "entry_choices": len(entry),
        "global_old_wrapper_exact": sum(row["global_exact"] == "YES" for row in audit),
        "profile_old_wrapper_exact": sum(row["profile_exact"] == "YES" for row in audit),
        "positional_profile_exact": sum(row["positional_exact"] == "YES" for row in audit),
        "profile_preferences": len(profile_rows),
        "positional_preferences": len(positional_rows),
        "teaching_copies": len(copies),
        "meaning_or_formal_card_changes": 0,
    }
    (HERE / "FOUR_HUNDRED_EIGHTY_SEVENTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P468 = ROOT / "experiments/yolo/sidequest_semantic_common_action_roots_four_hundred_sixty_eighth"
P473 = ROOT / "experiments/yolo/sidequest_semantic_silent_owner_dictionary_four_hundred_seventy_third"
V71 = ROOT / "experiments/yolo/sidequest_theory_candidates_v71/V71_SELECTED_OWNER_LEDGER.tsv"


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


def initial_active(register: str, owner: str, owner_default: str) -> str:
    if register == "HERBAL":
        return owner_default
    return owner_default or f"Arbeitsposten bei {owner}"


def resolve(value: str, active: str) -> tuple[str, int]:
    hits = len(re.findall(r"\b(?:dies|dort)\b", value, flags=re.I))
    out = re.sub(r"\bdies\b", active, value, flags=re.I)
    out = re.sub(r"\bdort\b", active, out, flags=re.I)
    return out, hits


def update_active(value: str, before: str, owner: str) -> tuple[str, str]:
    low = value.lower()
    if "klarauszug" in low or "ergebnis" in low:
        return f"Ergebnisbestand bei {owner}", "RESULT_CREATED"
    if "ansatz" in low:
        return f"laufender Ansatz bei {owner}", "BATCH_ACTIVATED"
    if "wasser" in low or "lauf" in low:
        return f"Laufflüssigkeit bei {owner}", "FLOW_ACTIVATED"
    if "gabe" in low or "zutat" in low:
        return f"Zugabe bei {owner}", "ADDITION_ACTIVATED"
    if "portion" in low:
        return f"abgeteilte Portion von {before}", "PORTION_CREATED"
    if "entnahme" in low or "abziehen" in low or "nehmen" in low:
        return f"entnommene Fraktion aus {before}", "FRACTION_CREATED"
    if "auffangen" in low:
        return f"aufgefangener Bestand von {before}", "COLLECTION_CREATED"
    if "nächster posten" in low or "naechster posten" in low:
        return f"nächster Arbeitsposten bei {owner}", "NEXT_ITEM_ACTIVATED"
    if "fach" in low or "gefäß" in low or "gefaess" in low:
        return before, "TARGET_ONLY"
    return before, "ACTIVE_CARRIED"


def main() -> None:
    events = read(P468 / "FOUR_HUNDRED_SIXTY_EIGHTH_381_PROSE_EVENT_COMMON_ACTIONS.tsv")
    prose_owner = read(P473 / "FOUR_HUNDRED_SEVENTY_THIRD_116_OWNER_EXPANDED_PROSE_STATEMENTS.tsv")
    astro = read(P473 / "FOUR_HUNDRED_SEVENTY_THIRD_142_OWNER_EXPANDED_ASTRO_LOCI.tsv")
    owner_by_statement = {row["statement_id"]: row for row in prose_owner}
    owner_detail = {
        row["owner_code"]: (row["owner_class"], row["concrete_owner_de"], row["dies_resolves_to_de"])
        for row in prose_owner if "|" not in row["owner_code"]
    }
    owner_fields = [row for row in read(V71) if row["unit_kind"] == "PROSE_FIELD"]
    field_owner = {row["unit_id"]: row["selected_visible_owner"] for row in owner_fields}
    if len(field_owner) != 135 or not set(field_owner.values()) <= set(owner_detail):
        raise ValueError("owner field map")

    state: dict[str, dict[str, str]] = {}
    trace = []
    statement_values: dict[str, list[str]] = defaultdict(list)
    statement_hits: Counter[str] = Counter()
    statement_resets: Counter[str] = Counter()
    unresolved_targets: Counter[str] = Counter()
    for row in events:
        owner_row = owner_by_statement[row["statement_id"]]
        record = row["record_unit_id"]
        owner_code = field_owner[row["field_id"]]
        owner_class, concrete_owner, active_default = owner_detail[owner_code]
        reset = record not in state or state[record]["owner_code"] != owner_code
        if reset:
            before = initial_active(row["register"], concrete_owner, active_default)
            state[record] = {"owner_code": owner_code, "active": before}
            statement_resets[row["statement_id"]] += 1
        else:
            before = state[record]["active"]
        resolved, hits = resolve(row["wet_context_value_de"], before)
        after, transition = update_active(row["wet_context_value_de"], before, concrete_owner)
        state[record]["active"] = after
        statement_hits[row["statement_id"]] += hits
        if row["register"] == "HERBAL" and re.search(r"\bStelle\b", row["wet_context_value_de"], flags=re.I):
            unresolved_targets[row["statement_id"]] += 1
        statement_values[row["statement_id"]].append(resolved)
        trace.append({
            **row,
            "owner_code": owner_code,
            "owner_class": owner_class,
            "concrete_owner_de": concrete_owner,
            "owner_reset": "YES" if reset else "NO",
            "active_before_de": before,
            "reference_tokens_resolved": hits,
            "referent_resolved_value_de": resolved,
            "state_transition": transition,
            "active_after_de": after,
            "unresolved_invisible_target": "YES" if row["statement_id"] in unresolved_targets and re.search(r"\bStelle\b", row["wet_context_value_de"], flags=re.I) else "NO",
        })
    write("FOUR_HUNDRED_SEVENTY_FOURTH_381_REFERENT_TRACE.tsv", trace)

    statement_rows = []
    for owner_row in prose_owner:
        sid = owner_row["statement_id"]
        values = statement_values[sid]
        event_rows = [row for row in trace if row["statement_id"] == sid]
        owner_codes = list(dict.fromkeys(row["owner_code"] for row in event_rows))
        owners = list(dict.fromkeys(row["concrete_owner_de"] for row in event_rows))
        statement_rows.append({
            "statement_id": sid,
            "register": owner_row["register"],
            "record_unit_id": owner_row["record_unit_id"],
            "page": owner_row["page"],
            "owner_code": "|".join(owner_codes),
            "concrete_owner_de": " → ".join(owners),
            "events": owner_row["events"],
            "reference_tokens_resolved": statement_hits[sid],
            "owner_reset": "YES" if statement_resets[sid] else "NO",
            "unresolved_invisible_targets": unresolved_targets[sid],
            "referent_resolved_statement_de": "; ".join(values) + ".",
        })
    write("FOUR_HUNDRED_SEVENTY_FOURTH_116_REFERENT_RESOLVED_STATEMENTS.tsv", statement_rows)

    astro_rows = []
    for row in astro:
        astro_rows.append({
            **row,
            "referent_rule": "RESET_AT_EACH_VISIBLE_LOCUS",
            "active_before_de": row["dies_resolves_to_de"],
            "referent_resolved_locus_de": row["owner_expanded_reading_de"],
            "cross_locus_pronoun_carry": "NONE",
        })
    write("FOUR_HUNDRED_SEVENTY_FOURTH_142_ASTRO_LOCUS_REFERENTS.tsv", astro_rows)

    units = []
    for unit in [f"H{n}" for n in range(1, 6)] + [f"B{n}" for n in range(1, 7)]:
        rows = [row for row in statement_rows if row["record_unit_id"] == unit]
        units.append({
            "unit_order": len(units) + 1,
            "unit_id": unit,
            "page": rows[0]["page"],
            "domain": rows[0]["register"],
            "statements_or_loci": len(rows),
            "groups": sum(int(row["events"]) for row in rows),
            "references_resolved": sum(int(row["reference_tokens_resolved"]) for row in rows),
            "unresolved_invisible_targets": sum(int(row["unresolved_invisible_targets"]) for row in rows),
            "continuous_referent_resolved_reading_de": " ".join(row["referent_resolved_statement_de"] for row in rows),
        })
    for unit in ("A1", "A2", "A3"):
        rows = [row for row in astro_rows if row["diagram_id"] == unit]
        units.append({
            "unit_order": len(units) + 1,
            "unit_id": unit,
            "page": rows[0]["page"],
            "domain": "ASTRO",
            "statements_or_loci": len(rows),
            "groups": sum(int(row["groups"]) for row in rows),
            "references_resolved": 0,
            "unresolved_invisible_targets": 0,
            "continuous_referent_resolved_reading_de": " ".join(row["referent_resolved_locus_de"] for row in rows),
        })
    write("FOUR_HUNDRED_SEVENTY_FOURTH_14_REFERENT_RESOLVED_UNIT_EDITIONS.tsv", units)

    md = ["# Referent-resolved ten-page workshop edition", ""]
    for unit in units:
        md.extend([f"## {unit['unit_id']} — {unit['page']}", "", unit["continuous_referent_resolved_reading_de"], ""])
    (HERE / "FOUR_HUNDRED_SEVENTY_FOURTH_REFERENT_RESOLVED_TEN_PAGE_EDITION.md").write_text("\n".join(md), encoding="utf-8")

    transitions = Counter(row["state_transition"] for row in trace)
    summary = {
        "status": "PASS",
        "prose_events": len(trace),
        "prose_statements": len(statement_rows),
        "reference_tokens_resolved": sum(int(row["reference_tokens_resolved"]) for row in trace),
        "owner_resets": sum(row["owner_reset"] == "YES" for row in trace),
        "unresolved_invisible_target_events": sum(row["unresolved_invisible_target"] == "YES" for row in trace),
        "astro_loci": len(astro_rows),
        "astro_groups": sum(int(row["groups"]) for row in astro_rows),
        "units": len(units),
        "state_transitions": dict(sorted(transitions.items())),
    }
    (HERE / "FOUR_HUNDRED_SEVENTY_FOURTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

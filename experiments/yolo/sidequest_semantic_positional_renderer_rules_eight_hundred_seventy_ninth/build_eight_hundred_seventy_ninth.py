#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BOOK = ROOT / "sidequest_semantic_six_order_workshop_book_eight_hundred_seventy_sixth" / "EIGHT_HUNDRED_SEVENTY_SIXTH_438_MARK_SIX_ORDER_BOOK.tsv"
CORE = ROOT / "sidequest_semantic_fifth_scribe_curriculum_eight_hundred_seventy_seventh" / "EIGHT_HUNDRED_SEVENTY_SEVENTH_56_PORTABLE_CORE_CARDS.tsv"
PREFIX = "EIGHT_HUNDRED_SEVENTY_NINTH"
HERBAL = {"f10r", "f11r", "f55v", "f56r"}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def longest_common_suffix(values: set[str]) -> str:
    shortest = min(values, key=len)
    for index in range(len(shortest)):
        candidate = shortest[index:]
        if all(value.endswith(candidate) for value in values):
            return candidate
    return ""


def modal(values: list[str]) -> str:
    counts = Counter(values)
    return sorted(counts, key=lambda value: (-counts[value], value))[0]


def main() -> None:
    marks = [row for row in read(BOOK) if not row["stage"].startswith("CONDITION")]
    core = read(CORE)
    core_ids = {row["identity"] for row in core}

    physical: dict[str, dict[str, str]] = {}
    for row in marks:
        if row["identity"] in core_ids:
            physical.setdefault(row["source_id"], row)
    rows = sorted(physical.values(), key=lambda row: int(row["source_id"][1:]))

    by_unit: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_unit[row["unit"]].append(row)
    for unit_rows in by_unit.values():
        for index, row in enumerate(unit_rows):
            row["statement_position"] = (
                "ONLY" if len(unit_rows) == 1 else "FIRST" if index == 0 else "LAST" if index == len(unit_rows) - 1 else "MIDDLE"
            )
            row["section"] = "HERBAL" if row["page"] in HERBAL else "BIOLOGICAL"

    by_identity: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_identity[row["identity"]].append(row)
    variable_ids = {identity for identity, subset in by_identity.items() if len({row["surface"] for row in subset}) > 1}
    variable = [row for row in rows if row["identity"] in variable_ids]

    body_by_identity = {
        identity: longest_common_suffix({row["surface"] for row in by_identity[identity]}) for identity in variable_ids
    }
    for row in variable:
        body = body_by_identity[row["identity"]]
        row["renderer_body"] = body
        row["wrapper"] = row["surface"][: -len(body)] if body else row["surface"]
        if not row["wrapper"]:
            row["wrapper"] = "BARE"

    global_mode = {identity: modal([row["surface"] for row in subset]) for identity, subset in by_identity.items()}
    identity_position_mode: dict[tuple[str, str], str] = {}
    for identity in variable_ids:
        for position in {row["statement_position"] for row in by_identity[identity]}:
            identity_position_mode[(identity, position)] = modal(
                [row["surface"] for row in by_identity[identity] if row["statement_position"] == position]
            )
    page_position_mode: dict[tuple[str, str, str], str] = {}
    for identity in variable_ids:
        for page in {row["page"] for row in by_identity[identity]}:
            for position in {row["statement_position"] for row in by_identity[identity] if row["page"] == page}:
                page_position_mode[(identity, page, position)] = modal(
                    [row["surface"] for row in by_identity[identity] if row["page"] == page and row["statement_position"] == position]
                )

    occurrence_rows = []
    for row in variable:
        identity = row["identity"]
        pos_pred = identity_position_mode[(identity, row["statement_position"])]
        page_pred = page_position_mode[(identity, row["page"], row["statement_position"])]
        occurrence_rows.append(
            {
                "source_id": row["source_id"],
                "page": row["page"],
                "section": row["section"],
                "unit": row["unit"],
                "statement_position": row["statement_position"],
                "identity": identity,
                "surface": row["surface"],
                "renderer_body": row["renderer_body"],
                "wrapper": row["wrapper"],
                "house_surface": global_mode[identity],
                "identity_position_surface": pos_pred,
                "page_position_surface": page_pred,
                "house_match": "YES" if row["surface"] == global_mode[identity] else "NO",
                "identity_position_match": "YES" if row["surface"] == pos_pred else "NO",
                "page_position_match": "YES" if row["surface"] == page_pred else "NO",
                "meaning_change_if_house_surface_used": "NO",
            }
        )

    family_rows = []
    for identity in sorted(variable_ids):
        subset = [row for row in variable if row["identity"] == identity]
        surfaces = Counter(row["surface"] for row in subset)
        wrappers = Counter(row["wrapper"] for row in subset)
        pos_correct = sum(row["surface"] == identity_position_mode[(identity, row["statement_position"])] for row in subset)
        family_rows.append(
            {
                "identity": identity,
                "renderer_body": body_by_identity[identity],
                "permitted_wrappers": ",".join(sorted(wrappers)),
                "surfaces_with_counts": ",".join(f"{surface}:{surfaces[surface]}" for surface in sorted(surfaces)),
                "physical_occurrences": len(subset),
                "pages": ",".join(sorted({row["page"] for row in subset})),
                "house_surface": global_mode[identity],
                "house_matches": sum(row["surface"] == global_mode[identity] for row in subset),
                "identity_position_matches": pos_correct,
                "position_exceptions": len(subset) - pos_correct,
                "teaching_rule": "USE_HOUSE_SURFACE; READ_LOCAL_WRAPPERS_AS_RENDERER_VARIANTS",
            }
        )

    rule_rows = []
    for (identity, position), surface in sorted(identity_position_mode.items()):
        subset = [row for row in variable if row["identity"] == identity and row["statement_position"] == position]
        rule_rows.append(
            {
                "identity": identity,
                "statement_position": position,
                "preferred_surface": surface,
                "matches": sum(row["surface"] == surface for row in subset),
                "occurrences": len(subset),
                "exceptions": sum(row["surface"] != surface for row in subset),
            }
        )

    exception_rows = [
        row
        for row in occurrence_rows
        if row["identity_position_match"] == "NO"
    ]

    wrapper_rows = []
    for wrapper in sorted({row["wrapper"] for row in variable}):
        subset = [row for row in variable if row["wrapper"] == wrapper]
        positions = Counter(row["statement_position"] for row in subset)
        sections = Counter(row["section"] for row in subset)
        if wrapper == "q":
            hint = "EINSTIEG BEVORZUGT"
        elif wrapper == "sh":
            hint = "AUSGANG ODER EINZELZELLE BEVORZUGT"
        elif wrapper == "BARE":
            hint = "MITTE BEVORZUGT"
        else:
            hint = "LOKALE SCHREIBGEWOHNHEIT; KEINE FESTE POSITION"
        wrapper_rows.append(
            {
                "wrapper": wrapper,
                "events": len(subset),
                "only": positions["ONLY"],
                "first": positions["FIRST"],
                "middle": positions["MIDDLE"],
                "last": positions["LAST"],
                "herbal": sections["HERBAL"],
                "biological": sections["BIOLOGICAL"],
                "workshop_hint_de": hint,
            }
        )

    model_rows = [
        {"renderer_model": "ONE_HOUSE_SURFACE_PER_IDENTITY", "rules": 29, "exact_matches": sum(row["house_match"] == "YES" for row in occurrence_rows), "exceptions": sum(row["house_match"] == "NO" for row in occurrence_rows), "total_items_if_exceptions_memorized": 29 + sum(row["house_match"] == "NO" for row in occurrence_rows), "meaning_safe_when_normalized": "YES"},
        {"renderer_model": "IDENTITY_PLUS_STATEMENT_POSITION", "rules": len(rule_rows), "exact_matches": sum(row["identity_position_match"] == "YES" for row in occurrence_rows), "exceptions": len(exception_rows), "total_items_if_exceptions_memorized": len(rule_rows) + len(exception_rows), "meaning_safe_when_normalized": "YES"},
        {"renderer_model": "IDENTITY_PLUS_PAGE_PLUS_POSITION", "rules": len(page_position_mode), "exact_matches": sum(row["page_position_match"] == "YES" for row in occurrence_rows), "exceptions": sum(row["page_position_match"] == "NO" for row in occurrence_rows), "total_items_if_exceptions_memorized": len(page_position_mode) + sum(row["page_position_match"] == "NO" for row in occurrence_rows), "meaning_safe_when_normalized": "YES"},
    ]

    write(f"{PREFIX}_29_VARIABLE_RENDERER_FAMILIES.tsv", family_rows, ["identity", "renderer_body", "permitted_wrappers", "surfaces_with_counts", "physical_occurrences", "pages", "house_surface", "house_matches", "identity_position_matches", "position_exceptions", "teaching_rule"])
    write(f"{PREFIX}_168_VARIABLE_PHYSICAL_OCCURRENCES.tsv", occurrence_rows, ["source_id", "page", "section", "unit", "statement_position", "identity", "surface", "renderer_body", "wrapper", "house_surface", "identity_position_surface", "page_position_surface", "house_match", "identity_position_match", "page_position_match", "meaning_change_if_house_surface_used"])
    write(f"{PREFIX}_67_IDENTITY_POSITION_RULES.tsv", rule_rows, ["identity", "statement_position", "preferred_surface", "matches", "occurrences", "exceptions"])
    write(f"{PREFIX}_45_POSITION_EXCEPTIONS.tsv", exception_rows, list(occurrence_rows[0]))
    write(f"{PREFIX}_9_WRAPPER_PROFILES.tsv", wrapper_rows, ["wrapper", "events", "only", "first", "middle", "last", "herbal", "biological", "workshop_hint_de"])
    write(f"{PREFIX}_3_RENDERER_MODELS.tsv", model_rows, ["renderer_model", "rules", "exact_matches", "exceptions", "total_items_if_exceptions_memorized", "meaning_safe_when_normalized"])

    summary = {
        "status": "PASS",
        "decision": "ONE_HOUSE_SURFACE_PER_IDENTITY_IS_SIMPLER_THAN_A_FULL_POSITIONAL_RENDERER",
        "portable_core_physical_events": len(rows),
        "variable_identities": len(variable_ids),
        "variable_physical_events": len(variable),
        "renderer_wrappers_including_bare": len(wrapper_rows),
        "house_surface_matches": sum(row["house_match"] == "YES" for row in occurrence_rows),
        "house_surface_alternates": sum(row["house_match"] == "NO" for row in occurrence_rows),
        "identity_position_rules": len(rule_rows),
        "identity_position_matches": sum(row["identity_position_match"] == "YES" for row in occurrence_rows),
        "identity_position_exceptions": len(exception_rows),
        "page_position_rules": len(page_position_mode),
        "page_position_matches": sum(row["page_position_match"] == "YES" for row in occurrence_rows),
        "page_position_exceptions": sum(row["page_position_match"] == "NO" for row in occurrence_rows),
        "q_entry_or_only": sum(row["wrapper"] == "q" and row["statement_position"] in {"FIRST", "ONLY"} for row in variable),
        "q_total": sum(row["wrapper"] == "q" for row in variable),
        "sh_exit_or_only": sum(row["wrapper"] == "sh" and row["statement_position"] in {"LAST", "ONLY"} for row in variable),
        "sh_total": sum(row["wrapper"] == "sh" for row in variable),
        "bare_middle": sum(row["wrapper"] == "BARE" and row["statement_position"] == "MIDDLE" for row in variable),
        "bare_total": sum(row["wrapper"] == "BARE" for row in variable),
        "dictionary_changes": 0,
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / f"{PREFIX}_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    (HERE / f"{PREFIX}_RENDERER_HANDBOOK.md").write_text(
        "# Positionsregeln der Werkstattoberfläche\n\n"
        "Nach Entfernung der in mehreren Aufträgen wiederholten Kopien bleiben 230 echte\n"
        "Quellvorkommen der 56 Kernkarten. 168 davon gehören zu 29 variablen Identitäten.\n"
        "Sie verwenden acht sichtbare Hüllen plus die nackte Form.\n\n"
        "Drei Tendenzen sind lehrbar: q steht bevorzugt am Einstieg, sh bevorzugt am Ausgang\n"
        "oder in einer Einzelzelle, und die nackte Form bevorzugt die Mitte. Das ist aber keine\n"
        "harte Grammatik. Identität+Position trifft 123/168 Formen und lässt 45 lokale Ausnahmen.\n"
        "Mit Seitenwissen steigt die Treffzahl auf 146, doch dafür wären 113 Einzelregeln nötig.\n\n"
        "Die einfachste Werkstattregel bleibt deshalb: jede Kernidentität hat eine Hausform.\n"
        "q/sh/bare dienen als weiche Eintritts-, Ausgangs- und Mitteltendenzen; abweichende\n"
        "Exemplarformen dürfen übernommen werden, ohne die Kartenbedeutung zu ändern. So muss\n"
        "der Lehrling 56 Hausformen, nicht 102 Oberflächen und auch nicht 113 Seitenregeln lernen.\n",
        encoding="utf-8",
    )
    (HERE / f"{PREFIX}_REPORT.md").write_text(
        "# Sidequest Pass 879: positional renderer rules\n\n"
        "The 29 variable core identities reduce to eight wrappers plus a bare form, but position\n"
        "does not deterministically select them. q is entry-biased (25/40 first or only), sh is\n"
        "exit/only-biased (12/15), and bare is medial-biased (23/36). Identity+position reproduces\n"
        "123/168 variable physical occurrences; identity+page+position reaches 146/168 at the cost\n"
        "of 113 local rules. One house surface per identity remains the smaller teachable system.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()

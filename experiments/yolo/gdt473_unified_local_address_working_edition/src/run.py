#!/usr/bin/env python3
"""Compile all 183 admitted local-address events into one working edition."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt473_unified_local_address_working_edition"
OUT = BASE / "artifacts"
G459 = ROOT / "experiments/yolo/gdt459_local_nomenclator_content_atlas/artifacts/gdt459_183_address_interlinear.tsv"
G466 = ROOT / "experiments/yolo/gdt466_future_address_mixed_dictionary_intake/artifacts/gdt466_107_intake_dictionary.tsv"
G472 = ROOT / "experiments/yolo/gdt472_complete_address_template_dictionary/artifacts/gdt472_107_complete_template_assignments.tsv"

EDITION = OUT / "gdt473_183_unified_address_working_edition.tsv"
SURFACES = OUT / "gdt473_162_surface_consistency.tsv"
PAGES = OUT / "gdt473_6_page_summary.tsv"
COVERAGE = OUT / "gdt473_4_coverage_class_summary.tsv"
READABLE = OUT / "GDT473_COMPLETE_WORKING_EDITION.md"
RESULT = OUT / "gdt473_result.json"

FORMULA_TIER_MODE = {
    "A_EXACT_RUNNING_FORMULA": "PORTABLE_EXACT_RUNNING_FORMULA",
    "B_ATTESTED_RECIPE_NEW_SURFACE": "PORTABLE_ATTESTED_RECIPE_NEW_SURFACE",
    "C_SHORT_OR_REPEATED_COMPOSITION": "PROVISIONAL_SHORT_OR_REPEATED_FORMULA",
}

FORMULA_TIER_SCOPE = {
    "A_EXACT_RUNNING_FORMULA": "PORTABLE_EXACT_RUNNING_SURFACE",
    "B_ATTESTED_RECIPE_NEW_SURFACE": "PORTABLE_ATTESTED_RECIPE",
    "C_SHORT_OR_REPEATED_COMPOSITION": "PROVISIONAL_BOUNDED_COMPOSITION",
}

MODE_SHORT = {
    "PORTABLE_EXACT_RUNNING_FORMULA": "FORMEL A",
    "PORTABLE_ATTESTED_RECIPE_NEW_SURFACE": "FORMEL B",
    "PROVISIONAL_SHORT_OR_REPEATED_FORMULA": "FORMEL C",
    "CALIBRATED_FULL_FUNCTION_FORMULA": "VOLLE FUNKTION",
    "EXACT_PACKAGE_ONLY_FULL_FORMULA": "EXAKTPAKET",
    "FUNCTION_SHELL_PLUS_LEARNED_NAME": "FUNKTION + NAME",
    "OWNER_FAMILY_PLUS_LEARNED_NAME": "FAMILIE + NAME",
    "WHOLE_LEARNED_NAME": "GANZNAME",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"Refusing to write empty table {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def coverage_class(function_chars: int, learned_chars: int, hybrid_status: str) -> str:
    if learned_chars == 0:
        return "FULL_FUNCTION_FORMULA"
    if function_chars > 0:
        return "HYBRID_FUNCTION_AND_LEARNED_NAME"
    if hybrid_status == "OWNER_FAMILY_STEM_ONLY":
        return "OWNER_FAMILY_STRUCTURED_LEARNED_NAME"
    return "WHOLE_LEARNED_NAME"


def label_semantic_mode(assignment: dict[str, str]) -> str:
    mode = assignment["assignment_mode"]
    hybrid = assignment["gdt466_hybrid_status"]
    if mode == "GENERAL_ZERO_NAME_FUNCTION_TEMPLATE":
        return "CALIBRATED_FULL_FUNCTION_FORMULA"
    if mode == "EXACT_PACKAGE_ONLY_ZERO_NAME_CARD":
        return "EXACT_PACKAGE_ONLY_FULL_FORMULA"
    if hybrid == "FUNCTION_SHELL_PLUS_LEARNED_CORE":
        return "FUNCTION_SHELL_PLUS_LEARNED_NAME"
    if hybrid == "OWNER_FAMILY_STEM_ONLY":
        return "OWNER_FAMILY_PLUS_LEARNED_NAME"
    if hybrid == "WHOLE_LEARNED_LABEL":
        return "WHOLE_LEARNED_NAME"
    raise RuntimeError(f"Unexpected label assignment: {mode}/{hybrid}")


def markdown_escape(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def build_readable_edition(rows: list[dict[str, object]], page_rows: list[dict[str, object]]) -> str:
    page_summary = {str(row["physical_page"]): row for row in page_rows}
    by_page: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        by_page[str(row["physical_page"])].append(row)

    lines = [
        "# GDT473 — vollständige lokale Adress-Arbeitsausgabe",
        "",
        "Diese Ausgabe setzt alle 183 bereits zugelassenen lokalen Adressereignisse in ursprünglicher Quellenreihenfolge zusammen. Die deutschen Großschreibungen sind Arbeitswerte, gelernte Namen stehen weiterhin in eckigen Klammern. `EXAKTPAKET` bedeutet: genau diese ganze Form ist lesbar, das Paket ist nicht frei auf neue Formen übertragbar.",
        "",
        "| Gesamt | volle Formeln | Funktion + Name | Familienmarker + Name | Ganzname |",
        "|---:|---:|---:|---:|---:|",
        f"| {len(rows)} | {sum(r['coverage_class'] == 'FULL_FUNCTION_FORMULA' for r in rows)} | {sum(r['coverage_class'] == 'HYBRID_FUNCTION_AND_LEARNED_NAME' for r in rows)} | {sum(r['coverage_class'] == 'OWNER_FAMILY_STRUCTURED_LEARNED_NAME' for r in rows)} | {sum(r['coverage_class'] == 'WHOLE_LEARNED_NAME' for r in rows)} |",
        "",
    ]
    for page in by_page:
        summary = page_summary[page]
        lines.extend([
            f"## {page}",
            "",
            f"{summary['event_count']} Einträge; {summary['full_function_formula_count']} vollständige Formeln, {summary['hybrid_function_name_count']} Funktionshüllen mit gelerntem Namen, {summary['owner_family_name_count']} Familienmarker mit gelerntem Namen und {summary['whole_name_count']} Ganznamen.",
            "",
            "| Nr. | Locus | Form | vollständige Arbeitslesung | Modus |",
            "|---:|---|---|---|---|",
        ])
        for row in by_page[page]:
            duplicate = "" if int(row["local_surface_event_count"]) == 1 else f" ×{row['local_surface_event_count']}"
            lines.append(
                "| {ordinal} | {locus} | `{surface}`{duplicate} | {reading} | {mode} |".format(
                    ordinal=row["edition_ordinal"],
                    locus=markdown_escape(row["locus"]),
                    surface=markdown_escape(row["surface"]),
                    duplicate=duplicate,
                    reading=markdown_escape(row["working_reading_de"]),
                    mode=MODE_SHORT[str(row["edition_semantic_mode"])],
                )
            )
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    source = read_tsv(G459)
    dictionary = read_tsv(G466)
    assignments = read_tsv(G472)

    if len(source) != 183 or len(dictionary) != 107 or len(assignments) != 107:
        raise RuntimeError("Input deck size drift")
    dictionary_by_event = {row["source_event_id"]: row for row in dictionary}
    assignment_by_event = {row["source_event_id"]: row for row in assignments}
    if len(dictionary_by_event) != 107 or len(assignment_by_event) != 107:
        raise RuntimeError("Duplicate label source event")

    source_surface_count = Counter(row["surface"] for row in source)
    edition_rows: list[dict[str, object]] = []
    used_label_events: set[str] = set()
    for ordinal, row in enumerate(source, start=1):
        tier = row["decision_tier"]
        event_id = row["source_event_id"]
        if tier in FORMULA_TIER_MODE:
            semantic_mode = FORMULA_TIER_MODE[tier]
            route = "GDT459_FORMULA_SIDE"
            recipe = row["selected_recipe_or_whole_class"]
            reading = row["short_default_de"]
            function_chars = len(row["surface"])
            learned_chars = 0
            surface_chars = len(row["surface"])
            hybrid_status = "NOT_APPLICABLE_FORMULA_SIDE"
            assignment_mode = "GDT459_FORMULA_TIER"
            transfer_scope = FORMULA_TIER_SCOPE[tier]
            transferable_template = "NOT_APPLICABLE_FORMULA_EVENT"
            surface_template = row["surface"]
            meaning_template = reading
            slot_topology = "ZERO_NAME_FORMULA"
            familiarity = "GDT459_FORMULA_EVIDENCE"
            familiarity_rank = 0
            exact_dependency = "NONE"
        elif tier == "D_OWNER_LEARNED_WHOLE_LABEL":
            if event_id not in dictionary_by_event or event_id not in assignment_by_event:
                raise RuntimeError(f"Missing final label assignment: {event_id}")
            drow = dictionary_by_event[event_id]
            arow = assignment_by_event[event_id]
            if row["surface"] != drow["surface"] or row["surface"] != arow["surface"]:
                raise RuntimeError(f"Label surface mismatch: {event_id}")
            used_label_events.add(event_id)
            semantic_mode = label_semantic_mode(arow)
            route = "GDT472_COMPLETE_LABEL_DICTIONARY"
            recipe = arow["source_recipe"]
            reading = arow["source_reading_de"]
            function_chars = int(drow["known_function_character_count"])
            learned_chars = int(drow["remaining_learned_character_count"])
            surface_chars = int(drow["surface_character_count"])
            hybrid_status = arow["gdt466_hybrid_status"]
            assignment_mode = arow["assignment_mode"]
            transfer_scope = "TRANSFERABLE_EMPIRICAL_TEMPLATE" if arow["transferable"] == "YES" else "NONTRANSFERABLE_EXACT_PACKAGE"
            transferable_template = arow["transferable"]
            surface_template = arow["surface_template"]
            meaning_template = arow["meaning_template_de"]
            slot_topology = arow["slot_topology"]
            familiarity = arow["template_familiarity_state"]
            familiarity_rank = int(arow["template_familiarity_rank"])
            exact_dependency = arow["exact_package_dependency"]
        else:
            raise RuntimeError(f"Unexpected GDT459 tier: {tier}")

        if function_chars + learned_chars != surface_chars:
            raise RuntimeError(f"Character accounting mismatch: {event_id}")
        cover = coverage_class(function_chars, learned_chars, hybrid_status)
        edition_rows.append({
            "edition_id": f"G473-E{ordinal:03d}",
            "edition_ordinal": ordinal,
            "source_event_id": event_id,
            "gdt459_address_id": row["gdt459_address_id"],
            "physical_page": row["physical_page"],
            "register": row["register"],
            "locus": row["locus"],
            "source_order": row["source_order"],
            "owner_de": row["owner_de"],
            "surface": row["surface"],
            "content_class": row["content_class"],
            "gdt459_decision_tier": tier,
            "edition_route": route,
            "edition_semantic_mode": semantic_mode,
            "coverage_class": cover,
            "working_recipe": recipe,
            "working_reading_de": reading,
            "function_character_count": function_chars,
            "learned_character_count": learned_chars,
            "surface_character_count": surface_chars,
            "function_character_fraction": f"{function_chars / surface_chars:.6f}",
            "gdt466_hybrid_status": hybrid_status,
            "assignment_mode": assignment_mode,
            "transfer_scope": transfer_scope,
            "transferable_template": transferable_template,
            "surface_template": surface_template,
            "meaning_template_de": meaning_template,
            "slot_topology": slot_topology,
            "template_familiarity_state": familiarity,
            "template_familiarity_rank": familiarity_rank,
            "exact_package_dependency": exact_dependency,
            "gdt459_confidence": row["confidence"],
            "gdt459_decision_evidence": row["decision_evidence"],
            "local_surface_event_count": source_surface_count[row["surface"]],
            "duplicate_surface_status": "REPEATED_INVARIANT" if source_surface_count[row["surface"]] > 1 else "UNIQUE",
        })

    if used_label_events != set(assignment_by_event) or used_label_events != set(dictionary_by_event):
        raise RuntimeError("Final label decks do not exactly match the 107 GDT459 label events")

    by_surface: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in edition_rows:
        by_surface[str(row["surface"])].append(row)
    surface_rows: list[dict[str, object]] = []
    for surface in sorted(by_surface):
        selected = by_surface[surface]
        recipes = {str(row["working_recipe"]) for row in selected}
        readings = {str(row["working_reading_de"]) for row in selected}
        coverage_classes = {str(row["coverage_class"]) for row in selected}
        invariant = len(recipes) == len(readings) == len(coverage_classes) == 1
        surface_rows.append({
            "surface": surface,
            "event_count": len(selected),
            "pages": "|".join(sorted({str(row["physical_page"]) for row in selected})),
            "registers": "|".join(sorted({str(row["register"]) for row in selected})),
            "source_event_ids": "|".join(str(row["source_event_id"]) for row in selected),
            "working_recipe": "|".join(sorted(recipes)),
            "working_reading_de": "|".join(sorted(readings)),
            "coverage_class": "|".join(sorted(coverage_classes)),
            "consistency_status": "INVARIANT" if invariant else "CONFLICT",
        })

    page_rows: list[dict[str, object]] = []
    page_order = list(dict.fromkeys(str(row["physical_page"]) for row in edition_rows))
    for page in page_order:
        selected = [row for row in edition_rows if row["physical_page"] == page]
        page_rows.append({
            "physical_page": page,
            "register": selected[0]["register"],
            "event_count": len(selected),
            "distinct_surface_count": len({row["surface"] for row in selected}),
            "gdt459_formula_side_count": sum(row["edition_route"] == "GDT459_FORMULA_SIDE" for row in selected),
            "gdt472_label_side_count": sum(row["edition_route"] == "GDT472_COMPLETE_LABEL_DICTIONARY" for row in selected),
            "full_function_formula_count": sum(row["coverage_class"] == "FULL_FUNCTION_FORMULA" for row in selected),
            "hybrid_function_name_count": sum(row["coverage_class"] == "HYBRID_FUNCTION_AND_LEARNED_NAME" for row in selected),
            "owner_family_name_count": sum(row["coverage_class"] == "OWNER_FAMILY_STRUCTURED_LEARNED_NAME" for row in selected),
            "whole_name_count": sum(row["coverage_class"] == "WHOLE_LEARNED_NAME" for row in selected),
            "exact_package_only_count": sum(row["edition_semantic_mode"] == "EXACT_PACKAGE_ONLY_FULL_FORMULA" for row in selected),
            "function_character_count": sum(int(row["function_character_count"]) for row in selected),
            "learned_character_count": sum(int(row["learned_character_count"]) for row in selected),
            "surface_character_count": sum(int(row["surface_character_count"]) for row in selected),
        })

    coverage_counts = Counter(str(row["coverage_class"]) for row in edition_rows)
    coverage_rows = []
    for rank, label in enumerate([
        "FULL_FUNCTION_FORMULA",
        "HYBRID_FUNCTION_AND_LEARNED_NAME",
        "OWNER_FAMILY_STRUCTURED_LEARNED_NAME",
        "WHOLE_LEARNED_NAME",
    ], start=1):
        selected = [row for row in edition_rows if row["coverage_class"] == label]
        coverage_rows.append({
            "coverage_rank": rank,
            "coverage_class": label,
            "event_count": coverage_counts[label],
            "distinct_surface_count": len({row["surface"] for row in selected}),
            "function_character_count": sum(int(row["function_character_count"]) for row in selected),
            "learned_character_count": sum(int(row["learned_character_count"]) for row in selected),
            "pages": "|".join(sorted({str(row["physical_page"]) for row in selected})),
        })

    write_tsv(EDITION, edition_rows)
    write_tsv(SURFACES, surface_rows)
    write_tsv(PAGES, page_rows)
    write_tsv(COVERAGE, coverage_rows)
    READABLE.write_text(build_readable_edition(edition_rows, page_rows), encoding="utf-8")

    total_chars = sum(int(row["surface_character_count"]) for row in edition_rows)
    function_chars = sum(int(row["function_character_count"]) for row in edition_rows)
    result = {
        "status": "COMPLETE_183_EVENT_LOCAL_ADDRESS_WORKING_EDITION__94_FULL_FORMULAS_87_HYBRIDS_2_LEARNED_ONLY",
        "source_event_count": len(source),
        "distinct_surface_count": len(surface_rows),
        "gdt459_formula_side_event_count": sum(row["edition_route"] == "GDT459_FORMULA_SIDE" for row in edition_rows),
        "gdt472_final_label_event_count": sum(row["edition_route"] == "GDT472_COMPLETE_LABEL_DICTIONARY" for row in edition_rows),
        "coverage_class_counts": dict(coverage_counts),
        "full_function_event_count": coverage_counts["FULL_FUNCTION_FORMULA"],
        "hybrid_function_name_event_count": coverage_counts["HYBRID_FUNCTION_AND_LEARNED_NAME"],
        "owner_family_name_event_count": coverage_counts["OWNER_FAMILY_STRUCTURED_LEARNED_NAME"],
        "whole_name_event_count": coverage_counts["WHOLE_LEARNED_NAME"],
        "function_character_count": function_chars,
        "learned_character_count": total_chars - function_chars,
        "surface_character_count": total_chars,
        "function_character_fraction": round(function_chars / total_chars, 6),
        "duplicate_surface_count": sum(int(row["event_count"]) > 1 for row in surface_rows),
        "duplicate_surface_event_count": sum(int(row["event_count"]) for row in surface_rows if int(row["event_count"]) > 1),
        "surface_conflict_count": sum(row["consistency_status"] == "CONFLICT" for row in surface_rows),
        "nontransferable_exact_package_count": sum(row["edition_semantic_mode"] == "EXACT_PACKAGE_ONLY_FULL_FORMULA" for row in edition_rows),
        "nontransferable_exact_package_surfaces": [str(row["surface"]) for row in edition_rows if row["edition_semantic_mode"] == "EXACT_PACKAGE_ONLY_FULL_FORMULA"],
        "new_page_count": 0,
        "new_component_meaning_count": 0,
        "new_surface_spelling_count": 0,
    }
    RESULT.write_text(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

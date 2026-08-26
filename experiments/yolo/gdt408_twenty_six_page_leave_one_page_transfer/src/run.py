#!/usr/bin/env python3
"""Hold each of the 26 admitted pages out against the other 25."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
HERE = Path(__file__).resolve().parent.parent
OUT = HERE / "artifacts"
BASE = ROOT / "experiments/yolo/gdt407_unified_twenty_six_page_workshop_edition/artifacts"
RUNNING = BASE / "gdt407_4576_running_event_edition.tsv"
LOCAL = BASE / "gdt407_693_local_group_edition.tsv"
ATTACHMENTS = BASE / "gdt407_5051_attachment_edition.tsv"
PAGES = BASE / "gdt407_26_page_summary.tsv"
ATOM_DICT = ROOT / "experiments/yolo/gdt405_second_random_batch_recipe_lock/artifacts/gdt405_46_locked_atom_dictionary.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def recipe_atoms(recipe: str) -> tuple[str, ...]:
    return tuple(part for part in recipe.split("+") if part)


def contiguous(parts: tuple[str, ...], size: int) -> set[tuple[str, ...]]:
    return {parts[i:i+size] for i in range(len(parts)-size+1)}


FACTOR_AXES = (
    "selector_rule", "attachment_geometry", "action_core", "head_kind",
    "r_topology", "duplicate_mode", "duplicate_role",
)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    running = read_tsv(RUNNING)
    local = read_tsv(LOCAL)
    attachments = read_tsv(ATTACHMENTS)
    page_rows = read_tsv(PAGES)
    atom_rows = read_tsv(ATOM_DICT)
    atom_family = {row["atom"]: row["factor_family"] for row in atom_rows}
    pages = [row["physical_page"] for row in page_rows]
    assert (len(running), len(local), len(attachments), len(pages)) == (4576, 693, 5051, 26)

    event_replay: list[dict[str, object]] = []
    local_replay: list[dict[str, object]] = []
    attachment_replay: list[dict[str, object]] = []
    surface_replay: list[dict[str, object]] = []
    summary: list[dict[str, object]] = []

    for held in pages:
        held_running = [row for row in running if row["physical_page"] == held]
        train_running = [row for row in running if row["physical_page"] != held]
        held_local = [row for row in local if row["physical_page"] == held]
        train_local = [row for row in local if row["physical_page"] != held]
        held_attachments = [row for row in attachments if row["physical_page"] == held]
        train_attachments = [row for row in attachments if row["physical_page"] != held]

        surface_pages: dict[str, set[str]] = defaultdict(set)
        recipe_pages: dict[str, set[str]] = defaultdict(set)
        atom_pages: dict[str, set[str]] = defaultdict(set)
        package_pages: dict[tuple[str, ...], set[str]] = defaultdict(set)
        for row in train_running:
            page = row["physical_page"]
            surface_pages[row["surface"]].add(page)
            recipe_pages[row["component_recipe"]].add(page)
            parts = recipe_atoms(row["component_recipe"])
            for atom in parts:
                atom_pages[atom].add(page)
            for size in range(2, min(4, len(parts)) + 1):
                for gram in contiguous(parts, size):
                    package_pages[gram].add(page)

        surface_groups: dict[str, list[dict[str, str]]] = defaultdict(list)
        for row in held_running:
            surface_groups[row["surface"]].append(row)
            parts = recipe_atoms(row["component_recipe"])
            pairs = list(zip(parts, parts[1:]))
            unsupported_atoms = sorted({atom for atom in parts if not atom_pages.get(atom)})
            unsupported_local_atoms = [atom for atom in unsupported_atoms if atom_family[atom] == "LOCAL_OR_CLASS_SIGN"]
            unsupported_portable_atoms = [atom for atom in unsupported_atoms if atom_family[atom] != "LOCAL_OR_CLASS_SIGN"]
            unsupported_pairs = ["+".join(pair) for pair in pairs if not package_pages.get(pair)]
            max_span = 0
            for size in range(1, min(4, len(parts)) + 1):
                if size == 1 and any(atom_pages.get(part) for part in parts):
                    max_span = max(max_span, 1)
                elif size > 1 and any(package_pages.get(gram) for gram in contiguous(parts, size)):
                    max_span = max(max_span, size)
            if surface_pages.get(row["surface"]):
                replay_class = "EXACT_SURFACE_FROM_OTHER_PAGE"
            elif recipe_pages.get(row["component_recipe"]):
                replay_class = "EXACT_RECIPE_FROM_OTHER_PAGE"
            elif unsupported_portable_atoms:
                replay_class = "FAIL_PAGE_PRIVATE_ATOM"
            elif unsupported_local_atoms:
                replay_class = "KNOWN_CORE_PLUS_PAGE_PRIVATE_LOCAL_SIGN"
            elif not pairs:
                replay_class = "KNOWN_ATOM_NO_INTERNAL_PAIR"
            elif not unsupported_pairs:
                replay_class = "ALL_ADJACENT_PACKAGES_FROM_OTHER_PAGES"
            else:
                replay_class = "KNOWN_ATOMS_NEW_PACKAGE_COMPOSITION"
            event_replay.append({
                "held_page": held, "global_running_event_id": row["global_running_event_id"],
                "source_event_id": row["source_event_id"], "surface": row["surface"],
                "component_recipe": row["component_recipe"], "atom_count": len(parts),
                "other_surface_pages": "|".join(sorted(surface_pages.get(row["surface"], set()))) or "NONE",
                "other_recipe_pages": "|".join(sorted(recipe_pages.get(row["component_recipe"], set()))) or "NONE",
                "unsupported_atoms": "|".join(unsupported_atoms) or "NONE",
                "unsupported_portable_atoms": "|".join(unsupported_portable_atoms) or "NONE",
                "unsupported_local_atoms": "|".join(unsupported_local_atoms) or "NONE",
                "adjacent_pair_count": len(pairs),
                "supported_adjacent_pair_count": len(pairs) - len(unsupported_pairs),
                "unsupported_adjacent_pairs": "|".join(unsupported_pairs) or "NONE",
                "longest_other_page_span_max4": max_span,
                "leave_one_page_replay_class": replay_class,
            })

        for surface, rows in sorted(surface_groups.items()):
            recipes = sorted({row["component_recipe"] for row in rows})
            recipe_support = set().union(*(recipe_pages.get(recipe, set()) for recipe in recipes))
            surface_replay.append({
                "held_page": held, "surface": surface, "held_event_count": len(rows),
                "held_recipe_count": len(recipes), "held_recipes": " | ".join(recipes),
                "exact_surface_other_pages": "|".join(sorted(surface_pages.get(surface, set()))) or "NONE",
                "exact_recipe_other_pages": "|".join(sorted(recipe_support)) or "NONE",
                "surface_portability": "CROSS_PAGE" if surface_pages.get(surface) else "PAGE_PRIVATE",
                "recipe_portability": "CROSS_PAGE" if recipe_support else "PAGE_PRIVATE",
            })

        local_surface_pages: dict[str, set[str]] = defaultdict(set)
        local_recipe_pages: dict[str, set[str]] = defaultdict(set)
        for row in train_local:
            local_surface_pages[row["surface"]].add(row["physical_page"])
            local_recipe_pages[row["component_recipe"]].add(row["physical_page"])
        for row in held_local:
            if local_surface_pages.get(row["surface"]):
                replay_class = "EXACT_LOCAL_SURFACE_OTHER_PAGE"
            elif local_recipe_pages.get(row["component_recipe"]):
                replay_class = "LOCAL_RECIPE_SHAPE_OTHER_PAGE"
            else:
                replay_class = "PAGE_PRIVATE_LOCAL_COPY_ALLOWED"
            local_replay.append({
                "held_page": held, "source_event_id": row["source_event_id"], "locus": row["locus"],
                "surface": row["surface"], "component_recipe": row["component_recipe"],
                "source_local_role": row["source_local_role"],
                "other_surface_pages": "|".join(sorted(local_surface_pages.get(row["surface"], set()))) or "NONE",
                "other_recipe_pages": "|".join(sorted(local_recipe_pages.get(row["component_recipe"], set()))) or "NONE",
                "leave_one_page_replay_class": replay_class,
            })

        factor_values: dict[str, set[str]] = {axis: set() for axis in FACTOR_AXES}
        full_signatures: set[tuple[str, ...]] = set()
        selector_geometry: set[tuple[str, str]] = set()
        selector_head: set[tuple[str, str, str]] = set()
        for row in train_attachments:
            for axis in FACTOR_AXES:
                factor_values[axis].add(row[axis])
            full_signatures.add(tuple(row[axis] for axis in FACTOR_AXES))
            selector_geometry.add((row["selector_rule"], row["attachment_geometry"]))
            selector_head.add((row["selector_rule"], row["action_core"], row["head_kind"]))

        for row in held_attachments:
            missing = [f"{axis}={row[axis]}" for axis in FACTOR_AXES if row[axis] not in factor_values[axis]]
            signature = tuple(row[axis] for axis in FACTOR_AXES)
            sg = (row["selector_rule"], row["attachment_geometry"])
            sh = (row["selector_rule"], row["action_core"], row["head_kind"])
            if signature in full_signatures:
                replay_class = "EXACT_FACTOR_SIGNATURE_OTHER_PAGE"
            elif not missing:
                replay_class = "FACTORIZED_COMPOSITION_FROM_OTHER_PAGES"
            else:
                replay_class = "FAIL_PAGE_PRIVATE_FACTOR_VALUE"
            attachment_replay.append({
                "held_page": held, "global_attachment_id": row["global_attachment_id"],
                "global_running_event_id": row["global_running_event_id"], "surface": row["surface"],
                "focus_core": row["focus_core"], "selector_rule": row["selector_rule"],
                "attachment_geometry": row["attachment_geometry"], "action_core": row["action_core"],
                "head_kind": row["head_kind"], "r_topology": row["r_topology"],
                "duplicate_mode": row["duplicate_mode"], "duplicate_role": row["duplicate_role"],
                "missing_factor_values": "|".join(missing) or "NONE",
                "selector_geometry_seen_other_page": "YES" if sg in selector_geometry else "NO",
                "selector_head_seen_other_page": "YES" if sh in selector_head else "NO",
                "leave_one_page_replay_class": replay_class,
            })

        held_event_rows = [row for row in event_replay if row["held_page"] == held]
        held_local_rows = [row for row in local_replay if row["held_page"] == held]
        held_attachment_rows = [row for row in attachment_replay if row["held_page"] == held]
        event_counts = Counter(row["leave_one_page_replay_class"] for row in held_event_rows)
        local_counts = Counter(row["leave_one_page_replay_class"] for row in held_local_rows)
        attachment_counts = Counter(row["leave_one_page_replay_class"] for row in held_attachment_rows)
        private_portable_atoms = sorted({atom for row in held_event_rows for atom in row["unsupported_portable_atoms"].split("|") if atom != "NONE"})
        private_local_atoms = sorted({atom for row in held_event_rows for atom in row["unsupported_local_atoms"].split("|") if atom != "NONE"})
        missing_factors = sorted({item for row in held_attachment_rows for item in row["missing_factor_values"].split("|") if item != "NONE"})
        if not held_running:
            result = "PASS_LOCAL_COPY_ONLY__NO_PROSE_SCOPE"
        elif not private_portable_atoms and not missing_factors:
            result = "PASS_FACTORIZED_LEAVE_ONE_PAGE"
        else:
            result = "FAIL_PAGE_PRIVATE_CORE_OR_FACTOR"
        summary.append({
            "held_page": held, "running_event_count": len(held_running), "distinct_running_surface_count": len(surface_groups),
            "exact_surface_event_count": event_counts["EXACT_SURFACE_FROM_OTHER_PAGE"],
            "exact_recipe_event_count": event_counts["EXACT_RECIPE_FROM_OTHER_PAGE"],
            "package_composition_event_count": event_counts["ALL_ADJACENT_PACKAGES_FROM_OTHER_PAGES"],
            "known_atom_composition_event_count": event_counts["KNOWN_ATOMS_NEW_PACKAGE_COMPOSITION"] + event_counts["KNOWN_ATOM_NO_INTERNAL_PAIR"],
            "page_private_local_sign_event_count": event_counts["KNOWN_CORE_PLUS_PAGE_PRIVATE_LOCAL_SIGN"],
            "failed_event_count": event_counts["FAIL_PAGE_PRIVATE_ATOM"],
            "page_private_portable_atoms": "|".join(private_portable_atoms) or "NONE",
            "page_private_local_atoms": "|".join(private_local_atoms) or "NONE",
            "local_group_count": len(held_local),
            "exact_local_surface_count": local_counts["EXACT_LOCAL_SURFACE_OTHER_PAGE"],
            "local_recipe_shape_count": local_counts["LOCAL_RECIPE_SHAPE_OTHER_PAGE"],
            "page_private_local_copy_count": local_counts["PAGE_PRIVATE_LOCAL_COPY_ALLOWED"],
            "attachment_count": len(held_attachments),
            "exact_factor_signature_count": attachment_counts["EXACT_FACTOR_SIGNATURE_OTHER_PAGE"],
            "factorized_composition_count": attachment_counts["FACTORIZED_COMPOSITION_FROM_OTHER_PAGES"],
            "failed_attachment_count": attachment_counts["FAIL_PAGE_PRIVATE_FACTOR_VALUE"],
            "page_private_factor_values": "|".join(missing_factors) or "NONE",
            "leave_one_page_result": result,
        })

    event_path = OUT / "gdt408_4576_event_leaveout.tsv"
    local_path = OUT / "gdt408_693_local_leaveout.tsv"
    attachment_path = OUT / "gdt408_5051_attachment_leaveout.tsv"
    surface_path = OUT / "gdt408_surface_recipe_leaveout.tsv"
    summary_path = OUT / "gdt408_26_page_leaveout_summary.tsv"
    write_tsv(event_path, event_replay, list(event_replay[0]))
    write_tsv(local_path, local_replay, list(local_replay[0]))
    write_tsv(attachment_path, attachment_replay, list(attachment_replay[0]))
    write_tsv(surface_path, surface_replay, list(surface_replay[0]))
    write_tsv(summary_path, summary, list(summary[0]))

    result = {
        "status": "TWENTY_SIX_OF_TWENTY_SIX_PAGE_FACTOR_REPLAY_COMPLETE",
        "page_count": len(pages), "running_event_count": len(event_replay),
        "local_group_count": len(local_replay), "attachment_count": len(attachment_replay),
        "surface_rows": len(surface_replay),
        "surface_portability_counts": dict(sorted(Counter(row["surface_portability"] for row in surface_replay).items())),
        "recipe_portability_counts": dict(sorted(Counter(row["recipe_portability"] for row in surface_replay).items())),
        "page_result_counts": dict(sorted(Counter(row["leave_one_page_result"] for row in summary).items())),
        "event_replay_counts": dict(sorted(Counter(row["leave_one_page_replay_class"] for row in event_replay).items())),
        "local_replay_counts": dict(sorted(Counter(row["leave_one_page_replay_class"] for row in local_replay).items())),
        "attachment_replay_counts": dict(sorted(Counter(row["leave_one_page_replay_class"] for row in attachment_replay).items())),
        "pages_with_private_portable_atoms": [row["held_page"] for row in summary if row["page_private_portable_atoms"] != "NONE"],
        "pages_with_private_local_atoms": [row["held_page"] for row in summary if row["page_private_local_atoms"] != "NONE"],
        "pages_with_private_factor_values": [row["held_page"] for row in summary if row["page_private_factor_values"] != "NONE"],
        "source_sha256": {str(path.relative_to(ROOT)): sha256(path) for path in (RUNNING, LOCAL, ATTACHMENTS, PAGES, ATOM_DICT)},
        "output_sha256": {str(path.relative_to(HERE)): sha256(path) for path in (event_path, local_path, attachment_path, surface_path, summary_path)},
    }
    (OUT / "gdt408_result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

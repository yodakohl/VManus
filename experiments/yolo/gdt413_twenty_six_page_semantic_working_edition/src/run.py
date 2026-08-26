#!/usr/bin/env python3
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
HERE = ROOT / "experiments/yolo/gdt413_twenty_six_page_semantic_working_edition"
OUT = HERE / "artifacts"
GROUPS = ROOT / "experiments/yolo/gdt407_unified_twenty_six_page_workshop_edition/artifacts/gdt407_5269_unified_group_ledger.tsv"
EVENTS = ROOT / "experiments/yolo/gdt407_unified_twenty_six_page_workshop_edition/artifacts/gdt407_4576_running_event_edition.tsv"
STATEMENTS = ROOT / "experiments/yolo/gdt407_unified_twenty_six_page_workshop_edition/artifacts/gdt407_715_statement_edition.tsv"
PAGE_SUMMARY = ROOT / "experiments/yolo/gdt407_unified_twenty_six_page_workshop_edition/artifacts/gdt407_26_page_summary.tsv"
ATOM_DICT = ROOT / "experiments/yolo/gdt405_second_random_batch_recipe_lock/artifacts/gdt405_46_locked_atom_dictionary.tsv"
CORE_DICT = ROOT / "experiments/yolo/gdt412_chd_process_core_completion/artifacts/gdt412_final_19_core_dictionary.tsv"


def read_tsv(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def recipe_atoms(recipe):
    return [atom for card in recipe.split(" | ") for atom in card.split("+")]


def render(recipe, meanings):
    return " | ".join(" · ".join(meanings[atom] for atom in card.split("+")) for card in recipe.split(" | "))


def main():
    groups = read_tsv(GROUPS)
    events = read_tsv(EVENTS)
    statements = read_tsv(STATEMENTS)
    pages = read_tsv(PAGE_SUMMARY)
    base_atoms = read_tsv(ATOM_DICT)
    core_dictionary = read_tsv(CORE_DICT)

    core_by_root = {row["root"]: row for row in core_dictionary}
    component_rows = []
    meanings = {}
    categories = {}
    for row in base_atoms:
        atom = row["atom"]
        if atom in core_by_root:
            core = core_by_root[atom]
            value = core["selected_minimal_value_de"]
            layer = "PORTABLE_BROAD_WORKING_CORE"
            status = core["decision"]
            rule = core["portable_use_rule_de"]
        else:
            value = row["locked_working_value_de"]
            layer = "FORMAL_OR_LOCAL_CONTROL"
            status = "KEEP_CONTROL"
            rule = row["next_batch_policy"]
        meanings[atom] = value
        categories[atom] = row["factor_family"]
        component_rows.append({
            "atom": atom,
            "working_value_de": value,
            "factor_family": row["factor_family"],
            "semantic_layer": layer,
            "decision": status,
            "portable_rule_de": rule,
            "source_dictionary": "GDT412" if atom in core_by_root else "GDT405",
        })

    event_rows = []
    event_by_id = {}
    for row in events:
        atoms = recipe_atoms(row["component_recipe"])
        revised = render(row["component_recipe"], meanings)
        roots = [atom for atom in atoms if atom in core_by_root]
        out = {
            "global_running_ordinal": row["global_running_ordinal"],
            "global_running_event_id": row["global_running_event_id"],
            "physical_page": row["physical_page"],
            "source_panel": row["source_panel"],
            "register": row["register"],
            "locus": row["locus"],
            "source_order": row["source_order"],
            "source_statement_id": row["source_statement_id"],
            "owner_de": row["owner_de"],
            "surface": row["surface"],
            "component_recipe": row["component_recipe"],
            "working_core_reading_de": revised,
            "portable_core_inventory": "|".join(roots) if roots else "NONE",
            "reading_layer": "COMPOSITIONAL_WORKING_READING__OWNER_SUPPLIES_LOCAL_CONTENT",
            "surface_status": row["surface_status"],
            "admission_color": row["admission_color"],
        }
        event_rows.append(out)
        event_by_id[row["source_event_id"]] = out

    group_rows = []
    for row in groups:
        if row["group_kind"] == "RUNNING_EVENT":
            revised = render(row["component_recipe"], meanings)
            layer = "RUNNING_COMPOSITIONAL_WORKING_READING"
            local_expansion = row["owner_de"]
        else:
            revised = "LOKALE ADRESSE ODER KENNUNG KOPIEREN"
            layer = "LOCAL_COPY_ONLY__NO_PORTABLE_WORD_VALUE"
            local_expansion = row["owner_de"]
        group_rows.append({
            "global_group_ordinal": row["global_group_ordinal"],
            "global_group_id": row["global_group_id"],
            "group_kind": row["group_kind"],
            "physical_page": row["physical_page"],
            "source_panel": row["source_panel"],
            "register": row["register"],
            "locus": row["locus"],
            "source_order": row["source_order"],
            "source_statement_id": row["source_statement_id"],
            "owner_de": row["owner_de"],
            "surface": row["surface"],
            "component_recipe": row["component_recipe"],
            "working_reading_de": revised,
            "reading_layer": layer,
            "local_context_de": local_expansion,
            "surface_status": row["surface_status"],
            "admission_color": row["admission_color"],
            "source_local_role": row["source_local_role"] or "NONE",
        })

    core_categories = {root: row["structural_category"] for root, row in core_by_root.items()}
    statement_rows = []
    statements_by_page = defaultdict(list)
    for row in statements:
        atoms = recipe_atoms(row["recipe_sequence"])
        action_chain = [meanings[atom] for atom in atoms if core_categories.get(atom) == "HANDLUNG"]
        arguments = [meanings[atom] for atom in atoms if core_categories.get(atom) == "ARGUMENT"]
        relations = [meanings[atom] for atom in atoms if core_categories.get(atom) == "RELATION"]
        order = [meanings[atom] for atom in atoms if core_categories.get(atom) == "ORDER"]
        grades = [meanings[atom] for atom in atoms if categories.get(atom) == "GRADE"]
        revised = render(row["recipe_sequence"], meanings)
        out = {
            "global_statement_ordinal": row["global_statement_ordinal"],
            "global_statement_id": row["global_statement_id"],
            "physical_page": row["physical_page"],
            "register": row["register"],
            "owner_de": row["owner_de"],
            "event_count": row["event_count"],
            "first_global_group_ordinal": row["first_global_group_ordinal"],
            "last_global_group_ordinal": row["last_global_group_ordinal"],
            "surface_sequence": row["surface_sequence"],
            "recipe_sequence": row["recipe_sequence"],
            "working_core_reading_de": revised,
            "action_chain_de": " > ".join(action_chain) if action_chain else "ELLIPTISCH__HANDLUNG_AUS_BESITZER_ODER_VORIGEM_SATZ",
            "argument_inventory_de": " | ".join(arguments) if arguments else "NONE",
            "relation_inventory_de": " | ".join(relations) if relations else "NONE",
            "order_inventory_de": " | ".join(order) if order else "NONE",
            "grade_inventory_de": " | ".join(grades) if grades else "NONE",
            "end_mode": row["end_mode"],
            "owner_bound_workshop_paraphrase_de": f"Bei {row['owner_de']}: {revised}",
            "semantic_scope": "CORE_VALUES_PORTABLE__CONCRETE_NOUNS_AND_TECHNIQUE_OWNER_LOCAL",
        }
        statement_rows.append(out)
        statements_by_page[row["physical_page"]].append(out)

    event_root_mentions = Counter(atom for row in events for atom in recipe_atoms(row["component_recipe"]) if atom in core_by_root)
    page_rows = []
    for row in pages:
        page = row["physical_page"]
        page_events = [event for event in event_rows if event["physical_page"] == page]
        page_groups = [group for group in group_rows if group["physical_page"] == page]
        page_rows.append({
            **row,
            "semantic_statement_count": len(statements_by_page[page]),
            "running_reading_count": len(page_events),
            "local_copy_count": sum(group["group_kind"] != "RUNNING_EVENT" for group in page_groups),
            "chd_bearbeiten_mentions": sum(event["component_recipe"].split("+").count("CHD") for event in page_events),
            "air_bahn_mentions": sum(event["component_recipe"].split("+").count("AIR") for event in page_events),
            "page_reading_mode": "LOCAL_COPY_ONLY" if not page_events else "RUNNING_WORKSHOP_READING",
        })

    OUT.mkdir(parents=True, exist_ok=True)
    paths = {
        "dictionary": OUT / "gdt413_46_component_working_dictionary.tsv",
        "groups": OUT / "gdt413_5269_group_semantic_edition.tsv",
        "events": OUT / "gdt413_4576_event_semantic_edition.tsv",
        "statements": OUT / "gdt413_715_statement_semantic_edition.tsv",
        "pages": OUT / "gdt413_26_page_semantic_summary.tsv",
    }
    write_tsv(paths["dictionary"], component_rows, list(component_rows[0]))
    write_tsv(paths["groups"], group_rows, list(group_rows[0]))
    write_tsv(paths["events"], event_rows, list(event_rows[0]))
    write_tsv(paths["statements"], statement_rows, list(statement_rows[0]))
    write_tsv(paths["pages"], page_rows, list(page_rows[0]))

    lines = [
        "# GDT413 – Lesbare Arbeitsausgabe der 26 Seiten",
        "",
        "Diese Ausgabe setzt dieselben neunzehn breiten Kernwerte in alle 4.576 laufenden Ereignisse ein. Lokale Bild- und Kreiskennungen bleiben ausdrücklich Kopierwerte.",
        "",
        "## Neunzehn portable Kernwerte",
        "",
        "| Kern | Defaultwert | Rolle |",
        "|---|---|---|",
    ]
    for row in core_dictionary:
        lines.append(f"| `{row['root']}` | {row['selected_minimal_value_de']} | {row['structural_category']} |")
    lines += ["", "## Seiten", "", "| Seite | Register | laufend | lokal | Aussagen |", "|---|---|---:|---:|---:|"]
    for row in page_rows:
        lines.append(f"| {row['physical_page']} | {row['registers']} | {row['running_reading_count']} | {row['local_copy_count']} | {row['semantic_statement_count']} |")
    lines += ["", "## Kurze Rückleseprobe pro Seite", ""]
    for row in page_rows:
        page = row["physical_page"]
        lines.append(f"### {page}")
        lines.append("")
        if not statements_by_page[page]:
            lines.append("Nur lokale Adressen/Kennungen; kein Prosasatz geöffnet.")
        else:
            for statement in sorted(statements_by_page[page], key=lambda item: (int(item["event_count"]), int(item["global_statement_ordinal"])))[:2]:
                lines.append(f"- `{statement['global_statement_id']}` ({statement['owner_de']}): {statement['working_core_reading_de']}")
        lines.append("")
    lines += [
        "## Vollausgabe",
        "",
        "Alle 5.269 Gruppen, 4.576 laufenden Ereignisse und 715 Aussagen stehen ungekürzt in den TSV-Artefakten. Die deutsche Zeile ist eine Kernlesung; lokale Pflanzenteile, Körperstellen, Geräte und Himmelsnamen werden nicht aus den Kernen erfunden.",
    ]
    readable = OUT / "TWENTY_SIX_PAGE_WORKING_READING.md"
    readable.write_text("\n".join(lines) + "\n", encoding="utf-8")
    paths["readable"] = readable

    result = {
        "status": "COMPLETE_TWENTY_SIX_PAGE_SEMANTIC_WORKING_EDITION",
        "page_count": len(page_rows),
        "group_count": len(group_rows),
        "running_event_count": len(event_rows),
        "local_group_count": sum(row["group_kind"] != "RUNNING_EVENT" for row in group_rows),
        "statement_count": len(statement_rows),
        "component_count": len(component_rows),
        "portable_core_count": len(core_dictionary),
        "portable_core_values": {row["root"]: row["selected_minimal_value_de"] for row in core_dictionary},
        "portable_root_mention_count": sum(event_root_mentions.values()),
        "chd_mention_count": event_root_mentions["CHD"],
        "air_mention_count": event_root_mentions["AIR"],
        "source_sha256": {str(path.relative_to(ROOT)): sha256(path) for path in (GROUPS, EVENTS, STATEMENTS, PAGE_SUMMARY, ATOM_DICT, CORE_DICT)},
        "output_sha256": {name: sha256(path) for name, path in paths.items()},
    }
    (OUT / "gdt413_result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

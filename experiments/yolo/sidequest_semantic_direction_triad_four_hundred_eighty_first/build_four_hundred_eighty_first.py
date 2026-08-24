#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P480 = ROOT / "experiments/yolo/sidequest_semantic_quantity_triad_four_hundred_eightieth"

DIRECTION = {"AR": "QUELLE", "AL": "ZIELSTELLE", "AIR": "LAUF_BAHN"}


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


def parts(parse: str) -> list[str]:
    return parse.replace("WHOLE[", "").replace("]", "").split("+")


def direction_roots(parse: str) -> list[str]:
    return [root for root in DIRECTION if root in parts(parse)]


def revise_prose(value: str, roots: list[str], owner: str) -> str:
    out = value
    if "AIR" in roots:
        replacements = {
            "Wasser abziehen": "Flüssigkeit aus dem Lauf entnehmen",
            "Wasser zuführen": "Flüssigkeit in den Lauf geben",
            "Wasser in Gang setzen": "Flüssigkeitslauf eröffnen",
            "Wasser weiterführen": "Flüssigkeitslauf weiterführen",
            "Wasserlauf schließen": "Flüssigkeitslauf schließen",
        }
        for old, new in replacements.items():
            out = out.replace(old, new)
    if "AL" in roots:
        out = out.replace("an die Stelle", f"an die Zielstelle „{owner}“")
        out = out.replace("an der Stelle", f"bei der Zielstelle „{owner}“")
        out = out.replace("zur Stelle", f"zur Zielstelle „{owner}“")
        out = out.replace("Folgestelle", f"nächste Zielstelle bei „{owner}“")
        out = out.replace("Durchlassstelle", f"Durchgangsstelle bei „{owner}“")
        if out == "Stelle":
            out = f"Zielstelle „{owner}“"
    return out


def main() -> None:
    dictionary = read(P480 / "FOUR_HUNDRED_EIGHTIETH_173_QUANTITY_REVISED_DICTIONARY.tsv")
    prose = read(P480 / "FOUR_HUNDRED_EIGHTIETH_381_QUANTITY_REVISED_PROSE_EVENTS.tsv")
    astro = read(P480 / "FOUR_HUNDRED_EIGHTIETH_395_QUANTITY_REVISED_ASTRO_GROUPS.tsv")

    contexts = []
    revised_prose = []
    for row in prose:
        roots = direction_roots(row["component_parse"])
        value = revise_prose(row["pass480_event_de"], roots, row["concrete_owner_de"])
        out = dict(row)
        out["direction_roots"] = "|".join(roots) if roots else "NONE"
        out["direction_roles"] = "|".join(DIRECTION[root] for root in roots) if roots else "NONE"
        out["pass481_event_de"] = value
        out["pass481_direction_revision"] = "YES" if roots and value != row["pass480_event_de"] else "NO"
        revised_prose.append(out)
        if roots:
            contexts.append({"domain": "PROSE", "unit_id": row["record_unit_id"], "page": row["page"], "locus_or_statement": row["statement_id"], "group_or_event_id": row["event_id"], "surface": row["surface"], "component_parse": row["component_parse"], "direction_roots": "|".join(roots), "direction_roles": "|".join(DIRECTION[root] for root in roots), "context_value_de": value})
    write("FOUR_HUNDRED_EIGHTY_FIRST_381_DIRECTION_REVISED_PROSE_EVENTS.tsv", revised_prose)

    revised_dictionary = []
    for row in dictionary:
        roots = direction_roots(row["component_parse"])
        out = dict(row)
        out["direction_roots"] = "|".join(roots) if roots else "NONE"
        out["direction_roles"] = "|".join(DIRECTION[root] for root in roots) if roots else "NONE"
        out["pass481_value_de"] = revise_prose(row["pass480_value_de"], roots, "BILDSTELLE")
        out["pass481_revision"] = "YES" if roots else "NO"
        revised_dictionary.append(out)
    write("FOUR_HUNDRED_EIGHTY_FIRST_173_DIRECTION_REVISED_DICTIONARY.tsv", revised_dictionary)

    revised_astro = []
    for row in astro:
        roots = direction_roots(row["selected_component_parse"])
        out = dict(row)
        out["direction_roots"] = "|".join(roots) if roots else "NONE"
        out["direction_roles"] = "|".join(DIRECTION[root] for root in roots) if roots else "NONE"
        out["pass481_celestial_reading_de"] = row["pass480_celestial_reading_de"]
        out["pass481_direction_revision"] = "NO"
        revised_astro.append(out)
        if roots:
            contexts.append({"domain": "ASTRO", "unit_id": row["diagram_id"], "page": row["page"], "locus_or_statement": row["locus"], "group_or_event_id": row["group_serial"], "surface": row["surface"], "component_parse": row["selected_component_parse"], "direction_roots": "|".join(roots), "direction_roles": "|".join(DIRECTION[root] for root in roots), "context_value_de": out["pass481_celestial_reading_de"]})
    write("FOUR_HUNDRED_EIGHTY_FIRST_395_DIRECTION_REVISED_ASTRO_GROUPS.tsv", revised_astro)
    write("FOUR_HUNDRED_EIGHTY_FIRST_156_DIRECTION_CONTEXTS.tsv", contexts)

    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in revised_prose:
        by_statement[row["statement_id"]].append(row)
    formulas = []
    statement_rows = []
    for sid in dict.fromkeys(row["statement_id"] for row in revised_prose):
        rows = by_statement[sid]
        roots = {root for row in rows for root in direction_roots(row["component_parse"])}
        qroots = {row["quantity_root"] for row in rows if row["quantity_root"] != "NONE"}
        receiver = any(row["joint_tuple_id"] == "df1098831679a8ad1b39" for row in rows)
        source_values = [row["pass481_event_de"] for row in rows if "AR" in direction_roots(row["component_parse"])]
        quantity_values = [row["pass481_event_de"] for row in rows if row["quantity_root"] != "NONE"]
        path_values = [row["pass481_event_de"] for row in rows if "AIR" in direction_roots(row["component_parse"])]
        target_values = [row["pass481_event_de"] for row in rows if "AL" in direction_roots(row["component_parse"])]
        strict = bool(source_values and quantity_values and path_values and target_values)
        extended = bool(source_values and quantity_values and path_values and (target_values or receiver))
        formula = {
            "statement_id": sid,
            "register": rows[0]["register"],
            "record_unit_id": rows[0]["record_unit_id"],
            "page": rows[0]["page"],
            "events": len(rows),
            "source_present": "YES" if source_values else "NO",
            "quantity_present": "YES" if quantity_values else "NO",
            "path_present": "YES" if path_values else "NO",
            "target_present": "YES" if target_values else "NO",
            "receiver_whole_card_present": "YES" if receiver else "NO",
            "strict_four_slot_formula": "YES" if strict else "NO",
            "four_slot_with_receiver": "YES" if extended else "NO",
            "source_values_de": " | ".join(source_values) or "NONE",
            "quantity_values_de": " | ".join(quantity_values) or "NONE",
            "path_values_de": " | ".join(path_values) or "NONE",
            "target_values_de": " | ".join(target_values) if target_values else "ARBEITSFACH" if receiver else "NONE",
            "source_order_formula": " > ".join(("S" if "AR" in direction_roots(row["component_parse"]) else "Q" if row["quantity_root"] != "NONE" else "P" if "AIR" in direction_roots(row["component_parse"]) else "T" if "AL" in direction_roots(row["component_parse"]) or row["joint_tuple_id"] == "df1098831679a8ad1b39" else "X") for row in rows),
        }
        formulas.append(formula)
        statement_rows.append({"statement_id": sid, "register": rows[0]["register"], "record_unit_id": rows[0]["record_unit_id"], "page": rows[0]["page"], "events": len(rows), "event_ids": "|".join(row["event_id"] for row in rows), "direction_roots": "|".join(sorted(roots)) or "NONE", "quantity_roots": "|".join(sorted(qroots)) or "NONE", "direction_revised_statement_de": "; ".join(row["pass481_event_de"] for row in rows) + "."})
    write("FOUR_HUNDRED_EIGHTY_FIRST_116_SOURCE_QUANTITY_PATH_TARGET_FORMULAS.tsv", formulas)
    write("FOUR_HUNDRED_EIGHTY_FIRST_116_DIRECTION_REVISED_STATEMENTS.tsv", statement_rows)

    triad_rows = []
    for root, role in DIRECTION.items():
        p = [row for row in contexts if row["domain"] == "PROSE" and root in row["direction_roots"].split("|")]
        a = [row for row in contexts if row["domain"] == "ASTRO" and root in row["direction_roots"].split("|")]
        triad_rows.append({"root": root, "invariant_role_de": role, "prose_events": len(p), "prose_card_types": len({row["component_parse"] for row in p}), "prose_records": len({row["unit_id"] for row in p}), "astro_groups": len(a), "astro_loci": len({row["locus_or_statement"] for row in a}), "wet_context_de": {"AR": "aus dem genannten Bestand", "AL": "an der sichtbaren oder gelernten Zielstelle", "AIR": "Flüssigkeitslauf"}[root], "celestial_context_de": {"AR": "von dieser Position", "AL": "an dieser Position", "AIR": "Bahn"}[root]})
    write("FOUR_HUNDRED_EIGHTY_FIRST_DIRECTION_TRIAD_LEXICON.tsv", triad_rows)

    astro_loci: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in revised_astro:
        astro_loci[(row["diagram_id"], row["page"], row["locus"])].append(row)
    units = []
    for unit in [f"H{n}" for n in range(1, 6)] + [f"B{n}" for n in range(1, 7)]:
        rows = [row for row in statement_rows if row["record_unit_id"] == unit]
        units.append({"unit_order": len(units)+1, "unit_id": unit, "page": rows[0]["page"], "domain": rows[0]["register"], "statements_or_loci": len(rows), "groups": sum(int(row["events"]) for row in rows), "continuous_direction_revised_de": " ".join(row["direction_revised_statement_de"] for row in rows)})
    for unit in ("A1", "A2", "A3"):
        loci = [(key, rows) for key, rows in astro_loci.items() if key[0] == unit]
        units.append({"unit_order": len(units)+1, "unit_id": unit, "page": loci[0][0][1], "domain": "ASTRO", "statements_or_loci": len(loci), "groups": sum(len(rows) for _, rows in loci), "continuous_direction_revised_de": " ".join("; ".join(row["pass481_celestial_reading_de"] for row in rows) + "." for _, rows in loci)})
    write("FOUR_HUNDRED_EIGHTY_FIRST_14_DIRECTION_REVISED_UNIT_EDITIONS.tsv", units)

    md = ["# Direction-triad ten-page edition", ""]
    for unit in units:
        md.extend([f"## {unit['unit_id']} — {unit['page']}", "", unit["continuous_direction_revised_de"], ""])
    (HERE / "FOUR_HUNDRED_EIGHTY_FIRST_DIRECTION_TRIAD_TEN_PAGE_EDITION.md").write_text("\n".join(md), encoding="utf-8")

    summary = {"status": "PASS", "direction_roots": 3, "prose_direction_events": sum(row["domain"] == "PROSE" for row in contexts), "astro_direction_groups": sum(row["domain"] == "ASTRO" for row in contexts), "unique_direction_contexts": len(contexts), "strict_four_slot_statements": sum(row["strict_four_slot_formula"] == "YES" for row in formulas), "four_slot_with_receiver_statements": sum(row["four_slot_with_receiver"] == "YES" for row in formulas), "dictionary_cards": len(revised_dictionary), "prose_events": len(revised_prose), "statements": len(statement_rows), "astro_groups": len(revised_astro), "units": len(units), "groups": sum(int(row["groups"]) for row in units)}
    (HERE / "FOUR_HUNDRED_EIGHTY_FIRST_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

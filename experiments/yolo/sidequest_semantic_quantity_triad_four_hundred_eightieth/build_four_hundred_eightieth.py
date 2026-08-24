#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P479 = ROOT / "experiments/yolo/sidequest_semantic_result_stock_four_hundred_seventy_ninth"
P477 = ROOT / "experiments/yolo/sidequest_semantic_sentence_templates_four_hundred_seventy_seventh"
P472 = ROOT / "experiments/yolo/sidequest_semantic_continuous_ten_page_edition_four_hundred_seventy_second"

TRIAD = {"AIN": "PORTION", "AIIN": "SOLLMASS", "IIN": "SOLLSTUFE"}


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


def root_for(parse: str) -> str:
    found = [root for root in TRIAD if root in parts(parse)]
    if len(found) > 1:
        raise ValueError(parse)
    return found[0] if found else "NONE"


def revise_prose(value: str, root: str) -> str:
    if root == "AIN":
        return value.replace("Ansatzportion", "Portion des Ansatzes").replace("Portion", "Stoffportion")
    if root == "AIIN":
        out = value.replace("bemessen", "Sollmaß setzen")
        out = out.replace("nächstes Maß", "nächstes Sollmaß").replace("Folgemaß", "Folge-Sollmaß")
        out = out.replace("Auffangmass", "Auffang-Sollmaß").replace("Abfuehrmass", "Abführ-Sollmaß")
        out = re.sub(r"(?<!Soll)Maß", "Sollmaß", out)
        return out
    if root == "IIN":
        return value.replace("Sollstand", "Sollstufe")
    return value


def quantity_specific_sentence(pattern: str, q: str, referent: str) -> str:
    templates = {
        "PREPARE>MEASURE>MOVE": f"Bereite den Posten „{referent}“ vor, setze {q} und führe ihn zur bezeichneten Stelle.",
        "MEASURE>MOVE>MEASURE": f"Setze für „{referent}“ zuerst {q}, bewege den Posten und setze am Ziel den nächsten Wert.",
        "MOVE>PREPARE>MOVE": f"Führe „{referent}“ zur Arbeitsstelle, bearbeite den Posten dort und führe ihn weiter.",
        "MEASURE>MOVE": f"Nimm von „{referent}“ {q} und führe den bestimmten Teil zur bezeichneten Stelle.",
        "MEASURE>HOLD": f"Setze für „{referent}“ {q} und halte den Posten wie angegeben.",
        "MOVE>MEASURE": f"Führe „{referent}“ zur Stelle und setze dort {q}.",
        "MOVE>PREPARE": f"Führe „{referent}“ weiter und beginne damit den nächsten Arbeitsgang.",
        "PREPARE>MEASURE": f"Bereite „{referent}“ und setze dafür {q}.",
        "APPLY>MEASURE": f"Setze „{referent}“ an der Zielstelle an und bestimme {q}.",
    }
    return templates[pattern]


def main() -> None:
    dictionary = read(P479 / "FOUR_HUNDRED_SEVENTY_NINTH_173_RECEIVED_STOCK_DICTIONARY.tsv")
    events = read(P479 / "FOUR_HUNDRED_SEVENTY_NINTH_381_RECEIVED_STOCK_EVENTS.tsv")
    motifs = read(P477 / "FOUR_HUNDRED_SEVENTY_SEVENTH_MOTIF_OCCURRENCES.tsv")
    astro = read(P472 / "FOUR_HUNDRED_SEVENTY_SECOND_395_ASTRO_GROUP_CONTEXT_READINGS.tsv")

    triad_events = []
    revised_events = []
    for row in events:
        root = root_for(row["component_parse"])
        value = revise_prose(row["pass479_event_de"], root)
        out = dict(row)
        out["quantity_root"] = root
        out["quantity_kind"] = TRIAD.get(root, "NONE")
        out["pass480_event_de"] = value
        out["pass480_quantity_revision"] = "YES" if root != "NONE" and value != row["pass479_event_de"] else "NO"
        revised_events.append(out)
        if root != "NONE":
            triad_events.append({
                "domain": "PROSE",
                "unit_id": row["record_unit_id"],
                "page": row["page"],
                "locus_or_statement": row["statement_id"],
                "group_or_event_id": row["event_id"],
                "card_type_id": row["joint_tuple_id"],
                "surface": row["surface"],
                "component_parse": row["component_parse"],
                "quantity_root": root,
                "quantity_kind": TRIAD[root],
                "context_value_de": value,
            })
    write("FOUR_HUNDRED_EIGHTIETH_381_QUANTITY_REVISED_PROSE_EVENTS.tsv", revised_events)

    revised_dictionary = []
    for row in dictionary:
        root = root_for(row["component_parse"])
        out = dict(row)
        out["quantity_root"] = root
        out["quantity_kind"] = TRIAD.get(root, "NONE")
        out["pass480_value_de"] = revise_prose(row["pass479_value_de"], root)
        out["pass480_revision"] = "YES" if root != "NONE" else "NO"
        revised_dictionary.append(out)
    write("FOUR_HUNDRED_EIGHTIETH_173_QUANTITY_REVISED_DICTIONARY.tsv", revised_dictionary)

    revised_astro = []
    for row in astro:
        root = root_for(row["selected_component_parse"])
        out = dict(row)
        out["quantity_root"] = root
        out["quantity_kind"] = TRIAD.get(root, "NONE")
        value = row["celestial_context_reading_de"]
        if root == "AIIN":
            value = re.sub(r"\bWert\b", "Sollwert", value)
        out["pass480_celestial_reading_de"] = value
        out["pass480_quantity_revision"] = "YES" if root == "AIIN" else "NO"
        revised_astro.append(out)
        if root != "NONE":
            triad_events.append({
                "domain": "ASTRO",
                "unit_id": row["diagram_id"],
                "page": row["page"],
                "locus_or_statement": row["locus"],
                "group_or_event_id": row["group_serial"],
                "card_type_id": row["surface"],
                "surface": row["surface"],
                "component_parse": row["selected_component_parse"],
                "quantity_root": root,
                "quantity_kind": TRIAD[root],
                "context_value_de": value,
            })
    write("FOUR_HUNDRED_EIGHTIETH_395_QUANTITY_REVISED_ASTRO_GROUPS.tsv", revised_astro)
    write("FOUR_HUNDRED_EIGHTIETH_101_QUANTITY_TRIAD_CONTEXTS.tsv", triad_events)

    by_event = {row["event_id"]: row for row in revised_events}
    motif_rows = []
    for row in motifs:
        event_rows = [by_event[event] for event in row["event_ids"].split("|")]
        roots = list(dict.fromkeys(event["quantity_kind"] for event in event_rows if event["quantity_kind"] != "NONE"))
        measure_exists = any(event["action_phase"] == "MEASURE" for event in event_rows)
        kind = roots[0] if len(roots) == 1 else "MIXED" if roots else "OTHER_MEASURE" if measure_exists else "NONE"
        labels = {"PORTION": "eine Stoffportion", "SOLLMASS": "das vorgeschriebene Sollmaß", "SOLLSTUFE": "die vorgeschriebene Sollstufe"}
        nouns = {"PORTION": "Stoffportion", "SOLLMASS": "Sollmaß", "SOLLSTUFE": "Sollstufe"}
        if len(roots) == 1:
            quantity_label = labels[roots[0]]
        elif roots:
            quantity_label = "die Kombination aus " + " und ".join(nouns[root] for root in roots)
        elif measure_exists:
            quantity_label = "den lokal gelernten Messwert"
        else:
            quantity_label = "den laufenden Posten"
        referent = event_rows[0]["short_active_before_de"].replace("Ergebnisbestand", "Empfangsbestand")
        out = dict(row)
        out["quantity_kinds"] = "|".join(roots) if roots else kind
        out["quantity_specific_sentence_de"] = quantity_specific_sentence(row["phase_pattern"], quantity_label, referent)
        out["pass480_actual_span_de"] = "; ".join(event["pass480_event_de"] for event in event_rows)
        motif_rows.append(out)
    write("FOUR_HUNDRED_EIGHTIETH_79_QUANTITY_SPECIFIC_MOTIFS.tsv", motif_rows)

    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in revised_events:
        by_statement[row["statement_id"]].append(row)
    statement_rows = []
    for sid in dict.fromkeys(row["statement_id"] for row in revised_events):
        rows = by_statement[sid]
        statement_rows.append({
            "statement_id": sid,
            "register": rows[0]["register"],
            "record_unit_id": rows[0]["record_unit_id"],
            "page": rows[0]["page"],
            "events": len(rows),
            "event_ids": "|".join(row["event_id"] for row in rows),
            "quantity_roots": "|".join(dict.fromkeys(row["quantity_root"] for row in rows if row["quantity_root"] != "NONE")) or "NONE",
            "quantity_revised_statement_de": "; ".join(row["pass480_event_de"] for row in rows) + ".",
        })
    write("FOUR_HUNDRED_EIGHTIETH_116_QUANTITY_REVISED_STATEMENTS.tsv", statement_rows)

    astro_loci: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in revised_astro:
        astro_loci[(row["diagram_id"], row["page"], row["locus"])].append(row)
    units = []
    for unit in [f"H{n}" for n in range(1, 6)] + [f"B{n}" for n in range(1, 7)]:
        rows = [row for row in statement_rows if row["record_unit_id"] == unit]
        units.append({"unit_order": len(units)+1, "unit_id": unit, "page": rows[0]["page"], "domain": rows[0]["register"], "statements_or_loci": len(rows), "groups": sum(int(row["events"]) for row in rows), "continuous_quantity_revised_de": " ".join(row["quantity_revised_statement_de"] for row in rows)})
    for unit in ("A1", "A2", "A3"):
        loci = [(key, rows) for key, rows in astro_loci.items() if key[0] == unit]
        units.append({"unit_order": len(units)+1, "unit_id": unit, "page": loci[0][0][1], "domain": "ASTRO", "statements_or_loci": len(loci), "groups": sum(len(rows) for _, rows in loci), "continuous_quantity_revised_de": " ".join("; ".join(row["pass480_celestial_reading_de"] for row in rows) + "." for _, rows in loci)})
    write("FOUR_HUNDRED_EIGHTIETH_14_QUANTITY_REVISED_UNIT_EDITIONS.tsv", units)

    triad_rows = []
    for root, kind in TRIAD.items():
        p = [row for row in triad_events if row["domain"] == "PROSE" and row["quantity_root"] == root]
        a = [row for row in triad_events if row["domain"] == "ASTRO" and row["quantity_root"] == root]
        triad_rows.append({"root": root, "invariant_value_de": kind, "prose_events": len(p), "prose_card_types": len({row["card_type_id"] for row in p}), "prose_records": len({row["unit_id"] for row in p}), "astro_groups": len(a), "astro_loci": len({row["locus_or_statement"] for row in a}), "teaching_rule_de": {"AIN": "physisch oder formal abgeteilter Teil", "AIIN": "vorgegebener Mengen- oder Tabellenwert", "IIN": "zu erreichende Prozess- oder Tabellenstufe"}[root]})
    write("FOUR_HUNDRED_EIGHTIETH_QUANTITY_TRIAD_LEXICON.tsv", triad_rows)

    md = ["# Quantity-triad ten-page edition", ""]
    for unit in units:
        md.extend([f"## {unit['unit_id']} — {unit['page']}", "", unit["continuous_quantity_revised_de"], ""])
    (HERE / "FOUR_HUNDRED_EIGHTIETH_QUANTITY_TRIAD_TEN_PAGE_EDITION.md").write_text("\n".join(md), encoding="utf-8")

    summary = {"status": "PASS", "triad_roots": 3, "prose_triad_events": sum(row["domain"] == "PROSE" for row in triad_events), "astro_triad_groups": sum(row["domain"] == "ASTRO" for row in triad_events), "triad_contexts": len(triad_events), "dictionary_cards": len(revised_dictionary), "prose_events": len(revised_events), "statements": len(statement_rows), "astro_groups": len(revised_astro), "motif_occurrences": len(motif_rows), "units": len(units), "groups": sum(int(row["groups"]) for row in units)}
    (HERE / "FOUR_HUNDRED_EIGHTIETH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

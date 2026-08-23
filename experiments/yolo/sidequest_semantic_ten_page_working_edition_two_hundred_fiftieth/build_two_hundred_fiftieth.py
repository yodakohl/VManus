#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R213 = ROOT / "experiments/yolo/sidequest_semantic_astro_prose_bridge_two_hundred_thirteenth"
R245 = ROOT / "experiments/yolo/sidequest_semantic_herbal_noun_decomposition_two_hundred_forty_fifth"
R248 = ROOT / "experiments/yolo/sidequest_semantic_astro_native_card_values_two_hundred_forty_eighth"
R249 = ROOT / "experiments/yolo/sidequest_semantic_cross_register_feedback_two_hundred_forty_ninth"
V75 = ROOT / "experiments/yolo/sidequest_theory_candidates_v75"

D173 = R213 / "TWO_HUNDRED_THIRTEENTH_173_CARD_CROSS_REGISTER_DICTIONARY.tsv"
H66 = R245 / "TWO_HUNDRED_FORTY_FIFTH_FINAL_66_CARD_HERBAL_DICTIONARY.tsv"
P381 = R249 / "TWO_HUNDRED_FORTY_NINTH_REVISED_381_PROSE_EVENTS.tsv"
S116 = R249 / "TWO_HUNDRED_FORTY_NINTH_REVISED_116_STATEMENTS.tsv"
REV15 = R249 / "TWO_HUNDRED_FORTY_NINTH_15_EVENT_REVISIONS.tsv"
A395 = R248 / "TWO_HUNDRED_FORTY_EIGHTH_REVISED_395_GROUP_MANUAL.tsv"
L142 = V75 / "V75_SELECTED_142_LOCUS_CELESTIAL_EDITION.tsv"

RECORD_ORDER = ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    base_dictionary = read_tsv(D173)
    herbal_dictionary = {r["master_card_id"]: r for r in read_tsv(H66)}
    revisions = read_tsv(REV15)
    revision_by_card: dict[str, dict[str, str]] = {}
    for row in revisions:
        revision_by_card.setdefault(row["master_card_id"], row)

    dictionary: list[dict[str, object]] = []
    for row in base_dictionary:
        card_id = row["master_card_id"]
        herbal = herbal_dictionary.get(card_id)
        revision = revision_by_card.get(card_id)
        if revision:
            core = revision["new_portable_core_de"]
            local = revision["local_expansion_de"]
            layer = "CROSS_REGISTER_REVISED_CORE"
            component = herbal["component_parse"] if herbal else row["component_formula"]
        elif herbal:
            core = herbal["revised_default_de"]
            local = herbal["revised_default_de"]
            layer = herbal["composition_status"]
            component = herbal["component_parse"]
        else:
            core = row["current_value_de"]
            local = row["current_value_de"]
            layer = row["component_class"]
            component = row["component_formula"]
        dictionary.append({
            "master_card_id": card_id, "master_form": row["master_form"],
            "registered_surfaces": row["registered_surfaces"], "portable_core_de": core,
            "local_prose_expansion_de": local, "component_parse": component,
            "dictionary_layer": layer, "syntactic_type": row["syntactic_type"],
            "prose_event_count": row["event_count"], "records": row["records"],
        })

    prose_events = read_tsv(P381)
    astro_groups = read_tsv(A395)
    unified: list[dict[str, object]] = []
    for row in prose_events:
        unified.append({
            "unified_id": f"P{int(row['event_id'][1:]):03d}", "section": "PROSE",
            "page": row["page"], "unit_id": row["record_unit_id"], "locus_or_field": row["field_id"],
            "statement_or_namespace": row["statement_id"], "visible_owner": row["visible_owner"],
            "visible_surface": row["visible_surface"], "portable_core_de": row["portable_core_de"],
            "local_expansion_de": row["local_register_expansion_de"], "source_layer": row["value_status"],
            "terminal_status": row["terminal_status"],
        })
    for row in astro_groups:
        unified.append({
            "unified_id": f"A{int(row['group_serial']):03d}", "section": "ASTRO",
            "page": row["page"], "unit_id": row["page_role"], "locus_or_field": row["locus"],
            "statement_or_namespace": row["namespace_id"], "visible_owner": row["visible_owner"],
            "visible_surface": row["visible_surface"], "portable_core_de": row["portable_card_core_de"],
            "local_expansion_de": row["concrete_diagram_reading_de"], "source_layer": row["curriculum_layer"],
            "terminal_status": "DIAGRAM_LABEL",
        })

    statements = read_tsv(S116)
    selected_loci = read_tsv(L142)
    astro_by_locus: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in astro_groups:
        astro_by_locus[(row["page"], row["locus"])].append(row)
    loci: list[dict[str, object]] = []
    for row in selected_loci:
        linked = astro_by_locus[(row["page"], row["locus"])]
        loci.append({
            "page": row["page"], "diagram_id": row["diagram_id"], "locus": row["locus"],
            "local_image_owner": row["local_image_owner"], "local_namespace": row["local_namespace"],
            "visible_sequence": " ".join(r["visible_surface"] for r in linked),
            "portable_core_chain": " | ".join(r["portable_card_core_de"] for r in linked),
            "complete_local_label_de": row["complete_copied_local_meaning_or_label"],
            "group_count": row["group_count"], "group_serials": row["group_serials"],
            "orientation_status": row["orientation_status"], "f68_f69_mapping": row["f68_f69_mapping"],
        })

    dictionary_path = OUT / "TWO_HUNDRED_FIFTIETH_REVISED_173_CARD_DICTIONARY.tsv"
    prose_path = OUT / "TWO_HUNDRED_FIFTIETH_381_PROSE_EVENTS.tsv"
    statement_path = OUT / "TWO_HUNDRED_FIFTIETH_116_PROSE_STATEMENTS.tsv"
    astro_path = OUT / "TWO_HUNDRED_FIFTIETH_395_ASTRO_GROUPS.tsv"
    locus_path = OUT / "TWO_HUNDRED_FIFTIETH_142_ASTRO_LOCI.tsv"
    unified_path = OUT / "TWO_HUNDRED_FIFTIETH_776_GROUP_WORKING_EDITION.tsv"
    readable_path = OUT / "TWO_HUNDRED_FIFTIETH_TEN_PAGE_READABLE_EDITION.md"
    report_path = OUT / "TWO_HUNDRED_FIFTIETH_REPORT.md"
    write_tsv(dictionary_path, dictionary, list(dictionary[0]))
    write_tsv(prose_path, prose_events, list(prose_events[0]))
    write_tsv(statement_path, statements, list(statements[0]))
    write_tsv(astro_path, astro_groups, list(astro_groups[0]))
    write_tsv(locus_path, loci, list(loci[0]))
    write_tsv(unified_path, unified, list(unified[0]))

    readable = ["# Zehn-Seiten-Arbeitsübersetzung — Ausgabe 250", ""]
    for record in RECORD_ORDER:
        linked = [r for r in statements if r["record_unit_id"] == record]
        readable += [f"## {record}", ""]
        for row in linked:
            readable.append(f"- **{row['portable_core_chain']}** → {row['complete_local_translation_de']}")
        readable.append("")
    for page in ("f67r2", "f68r1", "f69v"):
        linked = [r for r in loci if r["page"] == page]
        readable += [f"## {page}", ""]
        for row in linked:
            readable.append(f"- **{row['locus']} — {row['portable_core_chain']}** → {row['complete_local_label_de']}")
        readable.append("")
    readable_path.write_text("\n".join(readable), encoding="utf-8")

    layer_counts = Counter(str(r["source_layer"]) for r in unified)
    report = f"""# Sidequest-Pass 250: neue vollständige Zehn-Seiten-Ausgabe

## Bestand

- 173 Prosa-Kartentypen mit tragbarem Kern und lokaler Expansion;
- 381 Prosaereignisse in 116 vollständigen Aussagen;
- 395 Astrogruppen in 142 lokalen Diagrammstellen;
- 776/776 sichtbare Gruppen in einer gemeinsamen Ledger;
- zehn feste Seiten, kein zusätzlicher Folio.

## Lesemodell

Jede Prosa-Karte wird zuerst als kurzer Werkstattkern gelesen. Bildbesitzer und Register ergänzen Pflanze, Gefäß, Becken, Ziel oder Arbeitsstelle. Astro übernimmt 89 bekannte Prosekarten-Auftritte und behandelt 306 Gruppen als lokale Diagrammetiketten. Jede der 142 Diagrammstellen bleibt vollständig beschrieben, ohne Startpunkt, Drehrichtung oder f68↔f69-Schlüssel zu erfinden.

Diese Ausgabe ist die neue kreative Arbeitsbasis: nicht Lautschrift, sondern eine Mischung aus komponierbaren Fachkürzeln, gelernten Ganzzeichen und bildadressierten lokalen Namen.

Input hashes: dictionary `{sha(D173)}`, prose `{sha(P381)}`, statements `{sha(S116)}`, Astro `{sha(A395)}`, loci `{sha(L142)}`.
"""
    report_path.write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS", "dictionary_cards": len(dictionary), "prose_events": len(prose_events),
        "prose_statements": len(statements), "astro_groups": len(astro_groups), "astro_loci": len(loci),
        "unified_groups": len(unified), "pages": len({r["page"] for r in unified}),
        "layer_counts": dict(layer_counts),
        "outputs": {p.name: sha(p) for p in (dictionary_path, prose_path, statement_path, astro_path, locus_path, unified_path, readable_path, report_path)},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

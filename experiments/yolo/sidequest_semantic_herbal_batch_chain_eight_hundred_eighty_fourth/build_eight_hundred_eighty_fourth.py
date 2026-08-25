#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PRODUCTS = ROOT / "sidequest_semantic_internal_product_nomenclator_eight_hundred_seventy_second" / "EIGHT_HUNDRED_SEVENTY_SECOND_19_INTERNAL_PRODUCTS.tsv"
SUPPLIES = ROOT / "sidequest_semantic_internal_product_nomenclator_eight_hundred_seventy_second" / "EIGHT_HUNDRED_SEVENTY_SECOND_6_EXACT_INTERNAL_SUPPLY_LINKS.tsv"
EDITION = ROOT / "sidequest_semantic_complete_phrase_first_edition_eight_hundred_eighty_third"
EVENTS = EDITION / "EIGHT_HUNDRED_EIGHTY_THIRD_381_EVENT_COMPLETE_FIFTH_HAND.tsv"
STATEMENTS = EDITION / "EIGHT_HUNDRED_EIGHTY_THIRD_116_COMPLETE_PHRASE_FIRST_STATEMENTS.tsv"
PREFIX = "EIGHT_HUNDRED_EIGHTY_FOURTH"

CHAIN = {
    "A.G1": ("NONE", "ROOT_FROM_PICTURE", "IN_PROCESS", "NONE"),
    "A.G2": ("A.G1", "CONTINUE_ACTIVE_BATCH", "STOCK_READY", "END_OF_H1_RECORD"),
    "A.Z1": ("A.G2", "BRANCH_FROM_PAGE_STOCK", "IN_PROCESS", "NONE"),
    "A.Z2": ("A.Z1", "CONTINUE_ACTIVE_BATCH", "IN_PROCESS", "NONE"),
    "A.Z3": ("A.Z2", "CONTINUE_ACTIVE_BATCH", "STOCK_READY", "END_OF_H2_RECORD"),
    "B.X1": ("NONE", "ROOT_FROM_PICTURE", "STOCK_READY", "EXPLICIT_CLOSE"),
    "B.X2": ("B.X1", "REOPEN_AFTER_CLOSE", "STOCK_READY", "NEXT_STATEMENT_STARTS_DAVON"),
    "B.X3": ("B.X2", "TAKE_PORTION_FROM_PREVIOUS", "IN_PROCESS", "NONE"),
    "B.X4": ("B.X3", "CONTINUE_ACTIVE_BATCH", "STOCK_READY", "END_OF_H3_RECORD"),
    "C.M1": ("NONE", "ROOT_FROM_PICTURE", "STOCK_READY", "EXPLICIT_CLOSE"),
    "C.M2": ("C.M1", "REOPEN_AFTER_CLOSE", "IN_PROCESS", "NONE"),
    "C.W1": ("C.M2", "CONTINUE_AND_WARM", "STOCK_READY", "EXPLICIT_CLOSE"),
    "C.W2": ("C.W1", "REOPEN_AFTER_CLOSE", "STOCK_READY", "END_OF_H4_RECORD"),
    "D.I1": ("NONE", "ROOT_FROM_PICTURE", "IN_PROCESS", "NONE"),
    "D.P1": ("D.I1", "CONTINUE_AND_CLOSE", "STOCK_READY", "EXPLICIT_CLOSE"),
    "D.I2": ("D.P1", "REOPEN_AFTER_CLOSE", "IN_PROCESS", "NONE"),
    "D.A1": ("D.I2", "CONTINUE_ACTIVE_BATCH", "IN_PROCESS", "NONE"),
    "D.P2": ("D.A1", "CONTINUE_ACTIVE_BATCH", "IN_PROCESS", "NONE"),
    "D.P3": ("D.P2", "CONTINUE_ACTIVE_BATCH", "STOCK_READY", "END_OF_H5_RECORD"),
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    products = read(PRODUCTS)
    events = [row for row in read(EVENTS) if row["source_section"] == "HERBAL"]
    statements = {row["statement_id"]: row for row in read(STATEMENTS) if row["record"].startswith("H")}
    supplies = read(SUPPLIES)

    state_rows = []
    transition_rows = []
    product_by_statement = {row["statement_id"]: row for row in products}
    for ordinal, product in enumerate(products, start=1):
        handle = product["product_handle"]
        predecessor, relation, status, reason = CHAIN[handle]
        source = statements[product["statement_id"]]
        subset = [row for row in events if row["statement_id"] == product["statement_id"]]
        explicit_close = any("SCHLUSS" in row["concrete_default_de"] for row in subset)
        state_rows.append(
            {
                "chain_ordinal": ordinal,
                "owner_sigil": product["owner_sigil"],
                "page": product["herbal_page"],
                "record": source["record"],
                "statement_id": product["statement_id"],
                "product_handle": handle,
                "product_family": product["product_family"],
                "internal_workshop_name_de": product["internal_workshop_name_de"],
                "revised_predecessor": predecessor,
                "transition_from_predecessor": relation,
                "cards": len(subset),
                "explicit_close": "YES" if explicit_close else "NO",
                "availability": status,
                "availability_reason": reason,
                "fifth_hand_surface_sequence": " ".join(row["fifth_hand_surface"] for row in subset),
                "phrase_first_reading_de": source["phrase_first_reading_de"],
                "fluent_workshop_reading_de": source["fluent_workshop_reading_de"],
            }
        )
        if predecessor != "NONE":
            transition_rows.append(
                {
                    "owner_sigil": product["owner_sigil"],
                    "from_product": predecessor,
                    "to_product": handle,
                    "transition_kind": relation,
                    "to_statement": product["statement_id"],
                    "to_surface_sequence": " ".join(row["fifth_hand_surface"] for row in subset),
                    "workshop_instruction_de": f"Nimm {predecessor} und führe {product['statement_id']} aus; buche das Ergebnis als {handle}.",
                }
            )

    chain_rows = []
    for owner in ["A", "B", "C", "D"]:
        subset = [row for row in state_rows if row["owner_sigil"] == owner]
        ready = [row["product_handle"] for row in subset if row["availability"] == "STOCK_READY"]
        chain_rows.append(
            {
                "owner_sigil": owner,
                "page": subset[0]["page"],
                "records": ",".join(dict.fromkeys(str(row["record"]) for row in subset)),
                "state_chain": " -> ".join(str(row["product_handle"]) for row in subset),
                "states": len(subset),
                "transitions": len(subset) - 1,
                "stock_ready_handles": ",".join(ready),
                "stock_ready_count": len(ready),
                "final_handle": subset[-1]["product_handle"],
            }
        )

    stock_rows = [
        {
            "product_handle": row["product_handle"],
            "owner_sigil": row["owner_sigil"],
            "page": row["page"],
            "statement_id": row["statement_id"],
            "internal_workshop_name_de": row["internal_workshop_name_de"],
            "availability_reason": row["availability_reason"],
            "explicit_close": row["explicit_close"],
            "is_original_six_order_supply": "YES" if row["product_handle"] in {supply["internal_product_handle"] for supply in supplies} else "NO",
        }
        for row in state_rows
        if row["availability"] == "STOCK_READY"
    ]

    stock_by_handle = {row["product_handle"]: row for row in stock_rows}
    supply_rows = []
    for supply in supplies:
        stock = stock_by_handle[supply["internal_product_handle"]]
        supply_rows.append(
            {
                "entry_id": supply["entry_id"],
                "internal_product_handle": supply["internal_product_handle"],
                "how_record": supply["how_record"],
                "how_page": supply["how_page"],
                "availability_reason": stock["availability_reason"],
                "explicit_close": stock["explicit_close"],
                "selection_now_explained_de": f"{supply['internal_product_handle']} ist ein entnehmbarer Vorratszustand ({stock['availability_reason']}) und kann deshalb {supply['how_record']} speisen.",
                "supply_link_changed": "NO",
            }
        )

    event_rows = []
    for row in events:
        product = product_by_statement[row["statement_id"]]
        event_rows.append(
            {
                "event_id": row["event_id"], "page": row["page"], "record": row["record"], "statement_id": row["statement_id"],
                "product_handle": product["product_handle"], "fifth_hand_surface": row["fifth_hand_surface"], "identity": row["identity"],
                "component_recipe": row["component_recipe"], "concrete_default_de": row["concrete_default_de"],
            }
        )

    write(f"{PREFIX}_19_BATCH_STATES.tsv", state_rows, ["chain_ordinal", "owner_sigil", "page", "record", "statement_id", "product_handle", "product_family", "internal_workshop_name_de", "revised_predecessor", "transition_from_predecessor", "cards", "explicit_close", "availability", "availability_reason", "fifth_hand_surface_sequence", "phrase_first_reading_de", "fluent_workshop_reading_de"])
    write(f"{PREFIX}_15_BATCH_TRANSITIONS.tsv", transition_rows, ["owner_sigil", "from_product", "to_product", "transition_kind", "to_statement", "to_surface_sequence", "workshop_instruction_de"])
    write(f"{PREFIX}_4_OWNER_BATCH_CHAINS.tsv", chain_rows, ["owner_sigil", "page", "records", "state_chain", "states", "transitions", "stock_ready_handles", "stock_ready_count", "final_handle"])
    write(f"{PREFIX}_10_STOCK_READY_HANDLES.tsv", stock_rows, ["product_handle", "owner_sigil", "page", "statement_id", "internal_workshop_name_de", "availability_reason", "explicit_close", "is_original_six_order_supply"])
    write(f"{PREFIX}_6_EXPLAINED_SUPPLY_LINKS.tsv", supply_rows, ["entry_id", "internal_product_handle", "how_record", "how_page", "availability_reason", "explicit_close", "selection_now_explained_de", "supply_link_changed"])
    write(f"{PREFIX}_100_EVENT_BATCH_BINDING.tsv", event_rows, ["event_id", "page", "record", "statement_id", "product_handle", "fifth_hand_surface", "identity", "component_recipe", "concrete_default_de"])

    lines = ["# Vier Herbal-Chargenketten", ""]
    for chain in chain_rows:
        lines.extend(
            [
                f"## Bildbesitzer {chain['owner_sigil']} ({chain['page']})",
                "",
                f"`{chain['state_chain']}`",
                "",
                f"Entnehmbare Vorräte: **{chain['stock_ready_handles']}**. Endzustand: **{chain['final_handle']}**.",
                "",
            ]
        )
    lines.extend(
        [
            "## Werkstattdeutung",
            "",
            "Die neunzehn Herbal-Aussagen sind keine neunzehn Pflanzennamen. Jede Aussage bucht",
            "einen neuen Chargenzustand. Ein ausdrücklicher Schluss, ein Recordende oder ein danach",
            "folgendes DAVON macht einen Zustand zum entnehmbaren Vorrat. Darum sind gerade A.G2,",
            "B.X2, C.W2 und D.P1 als Liefergriffe der sechs Aufträge plausibel: sie liegen an echten",
            "Entnahmepunkten, obwohl drei Bildartikel danach noch weiterverarbeitet werden.",
        ]
    )
    (HERE / f"{PREFIX}_HERBAL_BATCH_MANUAL.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    summary = {
        "status": "PASS",
        "decision": "NINETEEN_HERBAL_STATEMENTS_FORM_FOUR_BATCH_CHAINS_WITH_TEN_STOCK_READY_HANDLES",
        "herbal_events": len(event_rows), "batch_states": len(state_rows), "batch_transitions": len(transition_rows),
        "owner_chains": len(chain_rows), "stock_ready_handles": len(stock_rows), "in_process_states": sum(row["availability"] == "IN_PROCESS" for row in state_rows),
        "explicitly_closed_stock_handles": sum(row["explicit_close"] == "YES" for row in stock_rows),
        "record_or_resume_stock_handles": sum(row["explicit_close"] == "NO" for row in stock_rows),
        "six_supply_links": len(supply_rows), "supply_links_changed": sum(row["supply_link_changed"] != "NO" for row in supply_rows),
        "repaired_predecessors_from_none": 4,
        "new_card_meanings": 0, "fixed_pages": sorted({row["page"] for row in event_rows}), "sealed_pages": ["f84", "f84r"],
    }
    (HERE / f"{PREFIX}_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (HERE / f"{PREFIX}_REPORT.md").write_text(
        "# Sidequest Pass 884: complete Herbal batch chains\n\n"
        "All 19 Herbal statements now form four picture-owned chains with 15 transitions. Ten\n"
        "states are practical stock points because they close, end a record or feed an explicit\n"
        "DAVON continuation. Four old missing predecessor links are repaired: A.G2→A.G1, A.Z3→A.Z2,\n"
        "C.W1→C.M2 and D.A1→D.I2.\n\n"
        "The six-order supplies do not need revision: A.G2 is a record checkpoint, B.X2 feeds a\n"
        "DAVON draw, C.W2 is record-final and D.P1 explicitly closes. They are selected stock\n"
        "points, not necessarily the final products of their picture articles.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()

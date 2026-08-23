#!/usr/bin/env python3
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R147 = ROOT / "experiments/yolo/sidequest_semantic_recurrent_specialist_promotion_hundred_forty_seventh"
R150 = ROOT / "experiments/yolo/sidequest_semantic_eleven_record_source_book_hundred_fiftieth"
R151 = ROOT / "experiments/yolo/sidequest_semantic_open_carry_registers_hundred_fifty_first"
R144 = ROOT / "experiments/yolo/sidequest_semantic_layered_current_edition_hundred_forty_fourth"


def read_tsv(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name, rows):
    rows = list(rows)
    with (OUT / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def broad_role(syntactic_type):
    if syntactic_type == "TERMINAL_ACTION":
        return "OPERATION_CLOSE"
    if syntactic_type in {"TERMINAL_STATE", "TERMINAL_ORDERED_STATE"}:
        return "STATE_CLOSE"
    if syntactic_type == "CARRIED_PREPARATION":
        return "ANAPHOR"
    if "ANAPHOR" in syntactic_type:
        return "ANAPHOR"
    if syntactic_type in {"CONTINUATION_LINK", "LEARNED_ORDER_OR_LINK"}:
        return "LINK_OR_ORDER"
    if syntactic_type in {"ORDERED_OBJECT"}:
        return "ORDERED_OBJECT"
    if syntactic_type == "QUANTITY_ACTION":
        return "OPERATION"
    if "QUANTITY" in syntactic_type or "STAGE" in syntactic_type:
        return "QUANTITY_OR_STAGE"
    if syntactic_type in {"OBJECT", "PRODUCT_OBJECT", "INSERT_OBJECT", "LEARNED_OBJECT"}:
        return "OBJECT"
    if syntactic_type == "TARGET_STATE_ACTION":
        return "STATE"
    if syntactic_type == "STATE":
        return "STATE"
    if syntactic_type == "LEARNED_PROCESS_OR_STATE":
        return "PROCESS_OR_STATE"
    if syntactic_type == "LEARNED_PROCESS_OR_PATH":
        return "PATH_OPERATION"
    if syntactic_type == "LEARNED_TRANSFER_OR_ADDRESS":
        return "TRANSFER_OR_ADDRESS"
    if "ACTION" in syntactic_type:
        return "OPERATION"
    raise ValueError(syntactic_type)


ROLE_SPEECH = {
    "OPERATION_CLOSE": "ausführen und Schritt schließen",
    "STATE_CLOSE": "Zustand setzen und Schritt schließen",
    "ANAPHOR": "auf den laufenden Bezug zeigen",
    "LINK_OR_ORDER": "Folge oder Fortsetzung markieren",
    "ORDERED_OBJECT": "nächsten Arbeitsgegenstand wählen",
    "QUANTITY_OR_STAGE": "Menge oder Stufe setzen",
    "OBJECT": "Arbeitsgegenstand nennen",
    "STATE": "Zustand nennen",
    "PROCESS_OR_STATE": "örtlichen Prozess oder Zustand ausführen",
    "PATH_OPERATION": "örtlichen Weg oder Durchgang ausführen",
    "TRANSFER_OR_ADDRESS": "Quelle, Ziel oder Überführung setzen",
    "OPERATION": "Handlung ausführen",
}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    cards = read_tsv(R147 / "HUNDRED_FORTY_SEVENTH_173_PROMOTED_DICTIONARY.tsv")
    events = read_tsv(R150 / "HUNDRED_FIFTIETH_381_SOURCE_EVENTS.tsv")
    clauses = read_tsv(R151 / "HUNDRED_FIFTY_FIRST_116_CARRY_AWARE_CLAUSES.tsv")
    moulds = read_tsv(R144 / "HUNDRED_FORTY_FOURTH_116_LAYERED_STATEMENTS.tsv")
    mould_by_statement = {row["statement_id"]: row["mould_id"] for row in moulds}

    role_lexicon = []
    for row in cards:
        role = broad_role(row["syntactic_type"])
        role_lexicon.append({
            "master_card_id": row["master_card_id"], "master_form": row["master_form"],
            "card_value_de": row["portable_card_value_de"], "syntactic_type": row["syntactic_type"],
            "spoken_role": role, "role_instruction_de": ROLE_SPEECH[role],
            "portable_scope": row["portable_scope"], "event_count": row["event_count"], "records": row["records"],
        })
    write_tsv("HUNDRED_FIFTY_SECOND_173_ROLE_LEXICON.tsv", role_lexicon)
    role_by_id = {row["master_card_id"]: row["spoken_role"] for row in role_lexicon}

    role_events = []
    for row in events:
        role_events.append({
            **row, "spoken_role": role_by_id[row["master_card_id"]],
            "role_spoken_atom_de": f"{role_by_id[row['master_card_id']]}[{row['card_value_de']}]",
        })
    write_tsv("HUNDRED_FIFTY_SECOND_381_ROLE_EVENTS.tsv", role_events)

    by_statement = defaultdict(list)
    for row in role_events:
        by_statement[row["statement_id"]].append(row)
    role_clauses = []
    for row in clauses:
        ev = by_statement[row["statement_id"]]
        roles = [item["spoken_role"] for item in ev]
        values = [item["card_value_de"] for item in ev]
        role_clauses.append({
            "statement_id": row["statement_id"], "record_unit_id": row["record_unit_id"], "page": row["page"],
            "mould_id": mould_by_statement[row["statement_id"]],
            "boundary_from_previous": row["boundary_from_previous"], "owner_trace": row["owner_trace"],
            "role_sequence": ">".join(roles), "card_value_sequence_de": " | ".join(values),
            "role_annotated_clause_de": " — ".join(f"{role}[{value}]" for role, value in zip(roles, values)),
            "original_carry_aware_clause_de": row["source_book_clause_de"],
        })
    write_tsv("HUNDRED_FIFTY_SECOND_116_ROLE_PARSES.tsv", role_clauses)

    pattern_counts = Counter(row["role_sequence"] for row in role_clauses)
    pattern_rows = []
    for index, (pattern, count) in enumerate(sorted(pattern_counts.items(), key=lambda item: (-item[1], item[0])), 1):
        examples = [row["statement_id"] for row in role_clauses if row["role_sequence"] == pattern][:5]
        pattern_rows.append({
            "rank": str(index), "role_sequence": pattern, "statement_count": str(count),
            "example_statements": "|".join(examples),
            "spoken_instruction_de": "; dann ".join(ROLE_SPEECH[role] for role in pattern.split(">")),
        })
    write_tsv("HUNDRED_FIFTY_SECOND_ROLE_PATTERNS.tsv", pattern_rows)

    role_counts = Counter(row["spoken_role"] for row in role_events)
    manual = ["# Rollenkarte der gesprochenen Werkstattgrammatik", ""]
    for role, count in sorted(role_counts.items(), key=lambda item: (-item[1], item[0])):
        manual.append(f"- **{role}** ({count} Ereignisse): {ROLE_SPEECH[role]}")
    manual += ["", "The visible card order is never changed. The role labels only supply German case, connective",
               "and imperative framing around the already selected short card values."]
    (OUT / "HUNDRED_FIFTY_SECOND_SPOKEN_ROLE_CARD.md").write_text("\n".join(manual).rstrip() + "\n", encoding="utf-8")

    report = [
        "# Hundertzweiundfünfzigste Runde: die Karten haben Satzrollen", "",
        "Every one of the 173 cards and 381 occurrences now has one spoken role. The inventory is deliberately",
        "small: operation, operation+close, object, quantity/stage, anaphor, ordered object, link/order, state,",
        "state+close, process/state, path operation and transfer/address. No visible order is rearranged.", "",
        f"The 116 clauses instantiate {len(pattern_counts)} exact role sequences. This explains why raw German",
        "card strings often sounded awkward: nouns, targets and state words were being recited as if each were a",
        "standalone imperative. The role layer can now supply case and connective while the card value stays short.", "",
        "Next generate a second fluent German source book from these roles, keeping the literal chain beside every",
        "sentence so any grammatical smoothing remains visible rather than becoming a new dictionary meaning.",
    ]
    (OUT / "HUNDRED_FIFTY_SECOND_ROLE_GRAMMAR_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps({
        "cards": len(role_lexicon), "events": len(role_events), "statements": len(role_clauses),
        "spoken_roles": len(role_counts), "role_counts": dict(sorted(role_counts.items())),
        "distinct_role_sequences": len(pattern_counts),
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

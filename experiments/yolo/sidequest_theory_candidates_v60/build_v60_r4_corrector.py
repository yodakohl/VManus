#!/usr/bin/env python3
"""Build the independent V60 R4 exact-card pressure audit.

This reads only the canonical V59 exact-card release.  It never infers a
meaning from PAGE_HOST, spelling, or tuple coordinates: the eleven selected
joint-tuple IDs are treated as unrelated atomic cards.
"""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
V59 = ROOT / "experiments/yolo/sidequest_theory_candidates_v59"
DICT_IN = V59 / "V59_R1_FINAL_173_CARD_DICTIONARY.tsv"
EVENT_IN = V59 / "V59_R1_FINAL_381_PROSE_EVENT_INTERLINEAR.tsv"
FIELD_IN = V59 / "V59_R1_FINAL_135_FIELD_EDITION.tsv"

# Exact-ID decisions only.  The words are deliberately short source-side
# mnemonics; question marks preserve their exploratory status.
DECISIONS = {
    "2f1c5e56e8f0ff459065": ("MASS?", "PARAMETER_NOUN", "STANDARD?", "ZAHL?", 0.57,
        "Occurs in twenty portable slots, commonly beside an active item or operation; measure is the narrowest reusable workshop reading."),
    "276a7c2d74d1143446f4": ("ANWENDEN?", "ACTION", "VERWENDEN?", "AUSFÜHREN?", 0.55,
        "Occurs across Herbal and Bio and can take a measure, target, channel, or prepared item; APPLY is more executable than the old broad USE."),
    "e0b630cb1b5df5e7105b": ("BEREIT?", "STATE", "FERTIG?", "GEEIGNET?", 0.49,
        "Portable state-like card after preparations and before continuations; no occurrence identifies the particular state independently."),
    "7a4bb8136330ee4e6e56": ("ANSATZ?", "WORKING_MATERIAL_NOUN", "BEREITUNG?", "FLÜSSIGKEIT?", 0.46,
        "Seven Herbal occurrences occupy material-bearing continuations; the doubled occurrence warns that this may be a copied categorical card."),
    "dd0ecaf5e27d81befffc": ("ZIEL?", "RELATION_ARGUMENT", "AN?", "STELLE?", 0.56,
        "Ten occurrences can stand alone or precede a terminal transfer; TARGET is shorter and syntactically stable where AN required an omitted complement."),
    "b5df9126607030b95175": ("KLAR?", "STATE", "ENDE?", "PRÜFEN?", 0.38,
        "Four placements are not uniformly terminal, so the old phrase 'until liquid runs clear' is rejected; only a possible observable state survives."),
    "dec401773c1f0347793d": ("VORIGES?", "BACK_REFERENCE", "DARAUS?", "WIEDER?", 0.36,
        "Two cross-register occurrences plausibly reopen a previous item, but cannot identify whether the antecedent is material, operation, or slot."),
    "faf321940aed922846a9": ("ANTEIL?", "SELECTION_NOUN", "AUSWAHL?", "DAVON?", 0.39,
        "Both occurrences open a field before further operations; a selected share is useful but rests on only two events."),
    "0275fbf14e07935b0a45": ("TEMPERIEREN?", "ACTION", "WARM?", "HALTEN?", 0.52,
        "Seven Bio occurrences recur before use, filtering, rinsing, or closure; an operation fits more contexts than treating the card as the adjective WARM."),
    "7db18b2f0fb7ed0fcfd3": ("SPÜLEN?", "TERMINAL_ACTION", "DURCHGANG?", "SCHRITT_A?", 0.43,
        "All eight occurrences are close-bearing and several are singleton cells; RINSE is retained as the useful process hypothesis but closure confounding is explicit."),
    "de7321bface5628e35d6": ("ABLASSEN?", "TERMINAL_ACTION", "AUSLAUF?", "SCHRITT_B?", 0.47,
        "Eight Bio occurrences often follow targets or process cells and are terminal; DRAIN remains the best concrete rival to a purely categorical close."),
}


def read_tsv(path: Path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows, fields):
    with path.open("w", encoding="utf-8", newline="") as handle:
        out = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        out.writeheader()
        out.writerows(rows)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    dictionary = read_tsv(DICT_IN)
    events = read_tsv(EVENT_IN)
    fields = read_tsv(FIELD_IN)
    field_by_id = {row["field_id"]: row for row in fields}
    by_field = defaultdict(list)
    for event in events:
        by_field[event["field_id"]].append(event)

    decision_rows = []
    observed = Counter(event["joint_tuple_id"] for event in events)
    dictionary_by_id = {row["joint_tuple_id"]: row for row in dictionary}
    for joint_id, (winner, source_class, rival_1, rival_2, confidence, rationale) in DECISIONS.items():
        source = dictionary_by_id[joint_id]
        decision_rows.append({
            "joint_tuple_id": joint_id,
            "surface_examples": source["surface_examples"],
            "occurrences": observed[joint_id],
            "pages": source["pages"],
            "v59_mnemonic": source["ATOMIC_OR_WHOLE_CARD_MNEMONIC"],
            "v60_r4_selected_mnemonic": winner,
            "source_class": source_class,
            "rival_1": rival_1,
            "rival_2": rival_2,
            "confidence": f"{confidence:.2f}",
            "apprentice_rule": rationale,
            "strongest_contradiction": {
                "MASS?": "No visible quantity values are independently grounded.",
                "ANWENDEN?": "The same card may instead be a generic execute/release control.",
                "BEREIT?": "Its state value is inherited from local translations, not independently visible.",
                "ANSATZ?": "Two consecutive copies in f10r make an ordinary repeated noun awkward.",
                "ZIEL?": "Some standalone cells may be categorical values rather than arguments.",
                "KLAR?": "Neither clarity nor liquid is independently visible in any of four events.",
                "VORIGES?": "Only two events support anaphora.",
                "ANTEIL?": "Only two events and no independently visible partition.",
                "TEMPERIEREN?": "No temperature is directly encoded by the drawings.",
                "SPÜLEN?": "Every occurrence is exactly confounded with one close-bearing family.",
                "ABLASSEN?": "Every occurrence is exactly confounded with a different close-bearing family.",
            }[winner],
        })

    occurrence_rows = []
    for event in events:
        joint_id = event["joint_tuple_id"]
        if joint_id not in DECISIONS:
            continue
        seq = by_field[event["field_id"]]
        index = seq.index(event)
        field = field_by_id[event["field_id"]]
        occurrence_rows.append({
            "event_serial": event["event_serial"],
            "page": event["page"],
            "locus": event["locus"],
            "record": event["record"],
            "field_id": event["field_id"],
            "surface": event["surface"],
            "joint_tuple_id": joint_id,
            "selected_mnemonic": DECISIONS[joint_id][0],
            "previous_surface_in_field": seq[index - 1]["surface"] if index else "FIELD_START",
            "next_surface_in_field": seq[index + 1]["surface"] if index + 1 < len(seq) else "FIELD_END",
            "field_surface_sequence": field["surface_sequence"],
            "field_local_expansion_v59": field["LOCAL_IATROMEDICAL_EXPANSION"],
            "terminal_status": event["terminal_status"],
        })

    revised_dictionary = []
    for row in dictionary:
        row = dict(row)
        if row["joint_tuple_id"] in DECISIONS:
            row["ATOMIC_OR_WHOLE_CARD_MNEMONIC"] = DECISIONS[row["joint_tuple_id"]][0]
            row["source_lineage"] += ">V60_R4_EXACT_CARD_PRESSURE"
        revised_dictionary.append(row)

    revised_events = []
    for row in events:
        row = dict(row)
        if row["joint_tuple_id"] in DECISIONS:
            row["ATOMIC_OR_WHOLE_CARD_MNEMONIC"] = DECISIONS[row["joint_tuple_id"]][0]
            row["source_lineage"] += ">V60_R4_EXACT_CARD_PRESSURE"
        revised_events.append(row)

    outputs = {
        "decisions": HERE / "V60_R4_EXACT_CARD_DECISIONS.tsv",
        "occurrences": HERE / "V60_R4_85_OCCURRENCE_PRESSURE.tsv",
        "dictionary": HERE / "V60_R4_REVISED_173_CARD_DICTIONARY.tsv",
        "events": HERE / "V60_R4_REVISED_381_EVENT_LEDGER.tsv",
    }
    write_tsv(outputs["decisions"], decision_rows, list(decision_rows[0]))
    write_tsv(outputs["occurrences"], occurrence_rows, list(occurrence_rows[0]))
    write_tsv(outputs["dictionary"], revised_dictionary, list(dictionary[0]))
    write_tsv(outputs["events"], revised_events, list(events[0]))

    checks = {
        "eleven_exact_cards": len(decision_rows) == 11,
        "eighty_five_occurrences": len(occurrence_rows) == 85,
        "occurrence_sum_eighty_five": sum(observed[j] for j in DECISIONS) == 85,
        "dictionary_173": len(revised_dictionary) == 173,
        "events_381": len(revised_events) == 381,
        "two_distinct_rivals_each": all(r["rival_1"] != r["rival_2"] != r["v60_r4_selected_mnemonic"] for r in decision_rows),
        "no_f84": all(not r["page"].startswith("f84") for r in revised_events),
        "exact_id_only": all(r["mnemonic_scope"].endswith("EXACT_CARD_MNEMONIC") or "BIO_LOCAL" in r["mnemonic_scope"] for r in revised_dictionary if r["joint_tuple_id"] in DECISIONS),
    }
    result = {
        "schema": "SIDEQUEST_V60_R4_EXACT_CARD_PRESSURE_V1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "inputs": {str(path.relative_to(ROOT)): sha(path) for path in (DICT_IN, EVENT_IN, FIELD_IN)},
        "outputs": {str(path.relative_to(ROOT)): sha(path) for path in outputs.values()},
    }
    (HERE / "V60_R4_VALIDATION.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit("validation failed")


if __name__ == "__main__":
    main()

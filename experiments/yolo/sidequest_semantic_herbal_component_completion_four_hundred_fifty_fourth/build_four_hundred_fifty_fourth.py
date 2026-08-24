#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = ROOT / "experiments/yolo/sidequest_semantic_herbal_manual_transfer_four_hundred_fifty_third/FOUR_HUNDRED_FIFTY_THIRD_100_EVENT_HERBAL_EDITION.tsv"

# One compact value per exact card.  The status records whether the reading
# comes entirely from the Biological apprentice deck, needs one of the two new
# Herbal content signs, or remains a genuinely memorized whole card.
DECISIONS = {
    "65f320e75510b2f38182": ("CH+E+Y", "dies kurz abziehen", "BIOLOGICAL_COMPONENTS", "CH operation, short grade, current item"),
    "dedc383b600397a301ee": ("CTH+O+OR", "Ansatz bereit", "BIOLOGICAL_COMPONENTS", "ready state on the active batch"),
    "df1098831679a8ad1b39": ("OS", "Gefäß", "HERBAL_WHOLE_CARD", "compact container word; no honest shared parse"),
    "12efe866f335461823a6": ("CH+AIR", "Wasser abziehen", "BIOLOGICAL_COMPONENTS", "water plus draw operation"),
    "62ff059766b21c7de083": ("OT+Y+T+CH+OL", "danach dies fuellen und weiter abziehen", "BIOLOGICAL_COMPONENTS", "ordered fill and draw instruction"),
    "a6939862e33ece5a0483": ("E+T+Y", "dies kurz fuellen", "BIOLOGICAL_COMPONENTS", "short fill of current item"),
    "9ad66e67803a12e745de": ("OK+Y", "dies ansetzen", "BIOLOGICAL_COMPONENTS", "activate current item"),
    "e8a6105b5c3a6220b440": ("OT+CH+OL", "danach weiter abziehen", "BIOLOGICAL_COMPONENTS", "next then continue draw"),
    "7249edc4df3419c26999": ("Y+CH+E+OR", "diesen Ansatz kurz abziehen", "BIOLOGICAL_COMPONENTS", "current batch under short draw"),
    "f3c23f42baf625639e1e": ("CTH+AIIN", "auf Maß bereitstellen", "BIOLOGICAL_COMPONENTS", "ready state plus measure"),
    "af816c04e65874a0f2fa": ("O+CTH+OL+Y", "dies bereit weiterführen", "BIOLOGICAL_COMPONENTS", "continue current ready item"),
    "10488b911aae52b3b334": ("OT+CH+OR", "danach Ansatz abziehen", "BIOLOGICAL_COMPONENTS", "next batch draw"),
    "497cbd9c7401810ff56b": ("OT+OL", "danach fortsetzen", "BIOLOGICAL_COMPONENTS", "portable order pair"),
    "27d97af8c96eb056c2e6": ("O+Y+K+OR", "dies dem Ansatz zuführen", "BIOLOGICAL_COMPONENTS", "current item supplied to batch"),
    "409de02322e7b2ca0c62": ("K+IIN", "bis zur Sollstufe zuführen", "BIOLOGICAL_COMPONENTS", "supply up to named stage"),
    "834825c61d048a6b5628": ("CH+O+AIIN", "auf Maß abziehen", "BIOLOGICAL_COMPONENTS", "draw operation governed by measure"),
    "953ad19b79517fc8a211": ("T+SH+OL", "weiter gefuellt halten", "BIOLOGICAL_COMPONENTS", "fill, hold, continue"),
    "428a5e3662aa57b4b256": ("SH+O+AL", "an der Stelle halten", "BIOLOGICAL_COMPONENTS", "hold at target site"),
    "bdad9f9ea8b80f141496": ("CFHY", "auswringen", "HERBAL_WHOLE_CARD", "learned extraction operation"),
    "a8af08e69edab8e54f15": ("SH+Y+AIIN", "dies bis zum Maß halten", "BIOLOGICAL_COMPONENTS", "hold current item to measure"),
    "deb377381ceaf55ea310": ("P+Y", "dies hineinführen", "BIOLOGICAL_COMPONENTS", "inward operation on current item"),
    "2e2027b1951d79911e24": ("T+CH+O+DY", "fuellen und abziehen; Schluss", "BIOLOGICAL_COMPONENTS", "closed fill-draw cycle"),
    "577c03a928d674d420d7": ("SH+O+Y+T+Y", "dies halten und fuellen", "BIOLOGICAL_COMPONENTS", "hold then fill current item"),
    "d665560c8ff80799a82c": ("OL", "fortsetzen", "BIOLOGICAL_COMPONENTS", "wrapper variants of continue"),
    "b2812c8283c3a62438bd": ("K+Y", "dies zuführen", "BIOLOGICAL_COMPONENTS", "supply current item"),
    "a48efd6c4491a046ba78": ("OT+Y", "nächster Posten", "BIOLOGICAL_COMPONENTS", "next current-item slot"),
    "322281bd391aa621f568": ("OK+OL", "weiter ansetzen", "BIOLOGICAL_COMPONENTS", "activate continuation"),
    "403c1592f918c8f23b88": ("Y+K+AIN", "eine Portion davon zuführen", "BIOLOGICAL_COMPONENTS", "portion supplied from current item"),
    "d929a14ec45749b2e805": ("Y+K+AIN", "eine Portion davon zuführen", "BIOLOGICAL_COMPONENTS", "same instruction in a second exact card"),
    "97cc9ac109148723c472": ("O+DY", "Arbeitsgang abschließen", "BIOLOGICAL_COMPONENTS", "active operation plus licensed close"),
    "e026af581c99322fbd46": ("TALAM", "verwahren", "HERBAL_WHOLE_CARD", "learned storage word"),
    "f7dc90b2c31fd341f0a4": ("Y+K+AIIN", "dies auf Maß zuführen", "BIOLOGICAL_COMPONENTS", "measured supply of current item"),
    "807591efc3d3f7ddbfab": ("CHEO+AR", "Auszug aus der Quelle", "HERBAL_COMPONENT_EXTENSION", "new extract sign plus source"),
    "204b04837409088c48f9": ("OL+T+Y", "dies weiter fuellen", "BIOLOGICAL_COMPONENTS", "continue fill on current item"),
    "6afeb5c9ab9f6cbdea0d": ("OR+AIN", "Ansatzportion", "BIOLOGICAL_COMPONENTS", "batch plus portion"),
    "b9d7b6d68209a9019e7a": ("HO+CH+OR", "Zutat aus dem Ansatz abziehen", "HERBAL_COMPONENT_EXTENSION", "ingredient sign plus batch draw"),
    "2cc054357a929df85f64": ("HO", "Zutat", "HERBAL_COMPONENT_EXTENSION", "portable Herbal content sign"),
    "0ec6a45e2950e8e7061d": ("HO+AL+Y", "diese Zutat an die Stelle", "HERBAL_COMPONENT_EXTENSION", "ingredient assigned to target"),
    "893c570f3fa3fce99711": ("K+OL", "weiter zuführen", "BIOLOGICAL_COMPONENTS", "continue supply"),
    "c10aec6d4dd877ec8bd8": ("HO+Y", "diese Zutat", "HERBAL_COMPONENT_EXTENSION", "current ingredient"),
    "95987d6f198d6d247511": ("CH+EE+CKH+O+DY", "länger durch den Durchlass; Schluss", "BIOLOGICAL_COMPONENTS", "long passage operation with close"),
    "ad3581d3144f69a5912d": ("SH", "halten", "BIOLOGICAL_COMPONENTS", "bare hold operation, not a plant part"),
    "b74e9e65637b7c8538dd": ("K+E+Y", "dies kurz zuführen", "BIOLOGICAL_COMPONENTS", "short supply of current item"),
    "1322bc176443fc2a8a86": ("OK+OK+Y", "dies erneut ansetzen", "BIOLOGICAL_COMPONENTS", "repeated activation"),
    "087a47b5423438cd6b6a": ("OK+CHEO", "Auszug ansetzen", "HERBAL_COMPONENT_EXTENSION", "activate extract"),
    "75a523fcf039b006f97b": ("K+AL", "an die Stelle zuführen", "BIOLOGICAL_COMPONENTS", "supply to target"),
    "c71c72da4e09e0833392": ("K+HO+AR", "Zutat aus dem Vorrat zuführen", "HERBAL_COMPONENT_EXTENSION", "supply ingredient from source"),
    "61a075bc54793c1c781f": ("OT+O+AIN", "danach eine Portion", "BIOLOGICAL_COMPONENTS", "next portion in active operation"),
    "9bb7122b386ebbc6138f": ("K+E+OL", "kurz weiter zuführen", "BIOLOGICAL_COMPONENTS", "short continued supply"),
}


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


def main() -> None:
    source = read(BASE)
    pending_ids = {row["joint_tuple_id"] for row in source if row["lexicon_source"] == "HERBAL_LOCAL_CARD_PENDING_REANALYSIS"}
    if pending_ids != set(DECISIONS):
        raise ValueError((pending_ids - set(DECISIONS), set(DECISIONS) - pending_ids))

    events: list[dict[str, object]] = []
    for row in source:
        new = dict(row)
        joint_id = row["joint_tuple_id"]
        if joint_id in DECISIONS:
            parse, value, status, note = DECISIONS[joint_id]
            new.update({
                "component_parse": parse, "small_value_de": value,
                "completion_class": status, "completion_note": note,
                "value_changed_in_pass454": "YES" if value != row["small_value_de"] else "NO",
            })
        else:
            new.update({
                "component_parse": "TRANSFERRED_EXACT_CARD", "completion_class": "BIOLOGICAL_EXACT_CARD_TRANSFER",
                "completion_note": "unchanged exact-card transfer from Pass 453", "value_changed_in_pass454": "NO",
            })
        events.append(new)
    write("FOUR_HUNDRED_FIFTY_FOURTH_100_EVENT_HERBAL_EDITION.tsv", events)

    by_card: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in events:
        by_card[str(row["joint_tuple_id"])].append(row)
    dictionary = []
    for joint_id, rows in sorted(by_card.items(), key=lambda item: min(int(row["order"]) for row in item[1])):
        values = {str(row["small_value_de"]) for row in rows}
        parses = {str(row["component_parse"]) for row in rows}
        classes = {str(row["completion_class"]) for row in rows}
        if len(values) != 1 or len(parses) != 1 or len(classes) != 1:
            raise ValueError(joint_id)
        dictionary.append({
            "card_no": f"HERC{len(dictionary) + 1:02d}", "joint_tuple_id": joint_id,
            "surfaces": "|".join(sorted({str(row["surface"]) for row in rows})),
            "events": len(rows), "event_ids": "|".join(str(row["event_id"]) for row in rows),
            "records": "|".join(sorted({str(row["record_unit_id"]) for row in rows})),
            "component_parse": next(iter(parses)), "small_value_de": next(iter(values)),
            "completion_class": next(iter(classes)), "completion_note": rows[0]["completion_note"],
        })
    write("FOUR_HUNDRED_FIFTY_FOURTH_66_CARD_HERBAL_DICTIONARY.tsv", dictionary)

    decisions = [row for row in dictionary if row["joint_tuple_id"] in DECISIONS]
    write("FOUR_HUNDRED_FIFTY_FOURTH_49_CARD_DECISIONS.tsv", decisions)
    wholes = [row for row in decisions if row["completion_class"] == "HERBAL_WHOLE_CARD"]
    write("FOUR_HUNDRED_FIFTY_FOURTH_THREE_HERBAL_WHOLE_CARDS.tsv", wholes)

    component_rows = [
        {"component": "HO", "value_de": "Zutat", "role": "HERBAL_CONTENT_SIGN", "cards": 5,
         "rule": "HO alone names an ingredient; surrounding AL/Y/AR/OR operations specify its role"},
        {"component": "CHEO", "value_de": "Auszug", "role": "HERBAL_PREPARATION_SIGN", "cards": 2,
         "rule": "CHEO combines with AR for source and OK for activation"},
    ]
    write("FOUR_HUNDRED_FIFTY_FOURTH_TWO_HERBAL_COMPONENT_EXTENSIONS.tsv", component_rows)

    by_statement: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in events:
        by_statement[str(row["statement_id"])].append(row)
    statements = []
    for statement_id, rows in by_statement.items():
        statements.append({
            "statement_id": statement_id, "record_unit_id": rows[0]["record_unit_id"], "page": rows[0]["page"],
            "picture_owner": rows[0]["picture_owner"], "events": len(rows),
            "event_ids": "|".join(str(row["event_id"]) for row in rows),
            "field_ids": "|".join(dict.fromkeys(str(row["field_id"]) for row in rows)),
            "component_sequence": " > ".join(str(row["component_parse"]) for row in rows),
            "literal_reading_de": "; ".join(str(row["small_value_de"]) for row in rows) + ".",
            "changed_events_pass454": sum(row["value_changed_in_pass454"] == "YES" for row in rows),
        })
    write("FOUR_HUNDRED_FIFTY_FOURTH_19_STATEMENT_HERBAL_EDITION.tsv", statements)

    article_lines = ["# Five pictured-plant articles after component completion", ""]
    for record in ("H1", "H2", "H3", "H4", "H5"):
        owner = next(row["picture_owner"] for row in events if row["record_unit_id"] == record)
        article_lines.extend([f"## {record} — {owner}", ""])
        for row in statements:
            if row["record_unit_id"] == record:
                article_lines.append(f"- **{row['statement_id']}**: {row['literal_reading_de']}")
        article_lines.append("")
    (HERE / "FOUR_HUNDRED_FIFTY_FOURTH_FIVE_ARTICLE_EDITION.md").write_text("\n".join(article_lines), encoding="utf-8")

    summary = {
        "status": "PASS", "events": len(events), "cards": len(dictionary), "statements": len(statements),
        "completed_local_cards": len(decisions),
        "biological_component_cards": sum(row["completion_class"] == "BIOLOGICAL_COMPONENTS" for row in decisions),
        "herbal_extension_cards": sum(row["completion_class"] == "HERBAL_COMPONENT_EXTENSION" for row in decisions),
        "herbal_whole_cards": len(wholes),
        "new_herbal_components": len(component_rows),
        "events_changed_in_pass454": sum(row["value_changed_in_pass454"] == "YES" for row in events),
    }
    (HERE / "FOUR_HUNDRED_FIFTY_FOURTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

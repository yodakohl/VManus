#!/usr/bin/env python3
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R121 = ROOT / "experiments/yolo/sidequest_semantic_complete_working_edition_hundred_twenty_first"

ROLE = {
    "oldy": ("LINK_CLOSE", "weiterführen und schließen"),
    "choky": ("ACTION_ITEM", "den Posten ansetzen"),
    "cheeky": ("ACTION_STATE_ITEM", "den Posten länger wärmen"),
    "aiin": ("MEASURE", "nach Sollmaß"),
    "okal": ("ACTION_TARGET", "am Ziel ansetzen"),
    "char": ("SOURCE", "aus der Quelle"),
    "chdy": ("ACTION_ITEM", "den Posten umsetzen"),
    "chor": ("OBJECT_PREPARATION", "den Ansatz"),
    "chety": ("ACTION_PART", "einen Teil abteilen"),
    "cheey": ("STATE_RESULT", "bis zum Ergebnis"),
    "okaiin": ("ACTION_MEASURE", "das Sollmaß einstellen"),
    "chey": ("OBJECT_ITEM", "diesen Posten"),
    "cheol": ("LINK", "weiterführen"),
    "al": ("TARGET", "zum Ziel"),
    "cholor": ("LINK_PREPARATION", "den vorigen Ansatz weiterführen"),
    "checthy": ("STATE_ITEM", "den Posten bereit halten"),
    "otchey": ("ORDER_ITEM", "danach den nächsten Posten"),
}

SLOTS = [
    ("S1", "ORDER_OR_CARRY", "danach / vom vorigen Ansatz", "otchey|cholor|cheol"),
    ("S2", "ACTION", "ansetzen / umsetzen / teilen / wärmen", "choky|chdy|chety|cheeky|okal|okaiin"),
    ("S3", "OBJECT", "Posten / Ansatz / Teil", "chey|chor plus fused action cards"),
    ("S4", "SOURCE", "aus der Quelle", "char"),
    ("S5", "MEASURE", "nach Sollmaß", "aiin"),
    ("S6", "TARGET", "zum Ziel", "al"),
    ("S7", "STATE_OR_RESULT", "bis bereit / bis zum Ergebnis", "checthy|cheey"),
    ("S8", "CONTINUE_OR_CLOSE", "weiter / schließen", "cheol|oldy"),
]


def load(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name, rows):
    with (OUT / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    deck = load(R121 / "HUNDRED_TWENTY_FIRST_17_SHARED_CARDS.tsv")
    events = load(R121 / "HUNDRED_TWENTY_FIRST_381_EVENT_INTERLINEAR.tsv")
    statements = load(R121 / "HUNDRED_TWENTY_FIRST_116_CURRENT_STATEMENTS.tsv")
    card_by_id = {r["master_card_id"]: r for r in deck}
    deck_ids = set(card_by_id)
    by_statement = defaultdict(list)
    for row in events:
        by_statement[row["statement_id"]].append(row)

    edges = Counter()
    direct_edges = Counter()
    starts = Counter()
    ends = Counter()
    skeleton_rows = []
    for statement in statements:
        members = by_statement[statement["statement_id"]]
        all_ids = [r["master_card_id"] for r in members]
        shared_ids = [x for x in all_ids if x in deck_ids]
        shared_forms = [card_by_id[x]["master_form"] for x in shared_ids]
        for a, b in zip(all_ids, all_ids[1:]):
            if a in deck_ids and b in deck_ids:
                direct_edges[(a, b)] += 1
        for a, b in zip(shared_ids, shared_ids[1:]):
            edges[(a, b)] += 1
        if shared_ids:
            starts[shared_ids[0]] += 1
            ends[shared_ids[-1]] += 1
        skeleton_rows.append({
            "statement_id": statement["statement_id"],
            "record_unit_id": statement["record_unit_id"],
            "page": statement["page"],
            "shared_card_count": str(len(shared_ids)),
            "shared_master_cards": " ".join(shared_ids) if shared_ids else "NONE",
            "shared_surface_skeleton": " ".join(shared_forms) if shared_forms else "NONE",
            "source_phrase_expansion_de": " ".join(ROLE[x][1] for x in shared_forms) if shared_forms else "[kein gemeinsamer Ganzkartenwert]",
            "current_statement_reading_de": statement["current_reading_de"],
        })
    write_tsv("HUNDRED_TWENTY_SECOND_116_SHARED_CARD_SKELETONS.tsv", skeleton_rows)

    edge_rows = []
    for (a, b), count in sorted(edges.items(), key=lambda x: (-x[1], card_by_id[x[0][0]]["master_form"], card_by_id[x[0][1]]["master_form"])):
        edge_rows.append({
            "from_card": card_by_id[a]["master_form"],
            "from_role": ROLE[card_by_id[a]["master_form"]][0],
            "to_card": card_by_id[b]["master_form"],
            "to_role": ROLE[card_by_id[b]["master_form"]][0],
            "skeleton_edge_count": str(count),
            "direct_adjacent_count": str(direct_edges[(a, b)]),
            "intervening_section_card_count": str(count-direct_edges[(a, b)]),
        })
    write_tsv("HUNDRED_TWENTY_SECOND_DIRECTED_SHARED_NETWORK.tsv", edge_rows)

    profile_rows = []
    for card in deck:
        cid = card["master_card_id"]
        incoming = [(card_by_id[a]["master_form"], n) for (a, b), n in edges.items() if b == cid]
        outgoing = [(card_by_id[b]["master_form"], n) for (a, b), n in edges.items() if a == cid]
        incoming.sort(key=lambda x: (-x[1], x[0]))
        outgoing.sort(key=lambda x: (-x[1], x[0]))
        role, expansion = ROLE[card["master_form"]]
        profile_rows.append({
            "master_card_id": cid,
            "master_form": card["master_form"],
            "short_default_de": card["short_default_de"],
            "source_phrase_role": role,
            "source_phrase_expansion_de": expansion,
            "record_count": str(len(card["records"].split("|"))),
            "event_count": card["event_count"],
            "skeleton_start_count": str(starts[cid]),
            "skeleton_end_count": str(ends[cid]),
            "strongest_predecessors": "|".join(f"{x}:{n}" for x, n in incoming[:3]) or "NONE",
            "strongest_successors": "|".join(f"{x}:{n}" for x, n in outgoing[:3]) or "NONE",
        })
    write_tsv("HUNDRED_TWENTY_SECOND_SEVENTEEN_NETWORK_PROFILES.tsv", profile_rows)

    slot_rows = [{"slot_order": order, "source_slot": slot, "source_phrase_de": phrase, "shared_card_realizations": cards} for order, slot, phrase, cards in SLOTS]
    write_tsv("HUNDRED_TWENTY_SECOND_EIGHT_SLOT_SOURCE_ORDER.tsv", slot_rows)

    report = [
        "# Hundertzweiundzwanzigste Runde: die Mini-Sprache des gemeinsamen Decks", "",
        "Nach Entfernen aller Sektionskarten bleibt ein gerichtetes 17-Karten-Gerüst. Es ist keine",
        "gewöhnliche Wort-für-Wort-Sprache, sondern ein komprimierter Formulary-Stack. Die kleinste",
        "Quellphrase lautet:", "",
        "DANACH/VORIGER ANSATZ → HANDLUNG → POSTEN/ANSATZ/TEIL → QUELLE → MASS → ZIEL → ZUSTAND/ERGEBNIS → WEITER/SCHLUSS.", "",
        "Karten dürfen mehrere Nachbarplätze fusionieren: okaiin ist Handlung+Maß, okal Handlung+Ziel,",
        "choky Handlung+Posten, checthy Zustand+Posten. Deshalb können kurze Aussagen aus einer Karte",
        "bestehen. Zwei Rahmen überschreiben die lineare Ordnung: Y–AIIN–Y bindet dasselbe Maß an zwei",
        "Posten; OL–(OL+OR)–OL umklammert den vorigen Ansatz mit Fortsetzung.", "",
        "Die häufigsten Netzwerkkanten sind Ansatz→Posten, Posten→Sollmaß, Sollmaß→Posten,",
        "Fortsetzung→Sollmaß und Umsetzen/Posten→Fortsetzung. Das passt zu einer elliptischen",
        "Werkstattquelle, nicht zu isolierten Wortglossen.", "",
        "f84 und f84r blieben versiegelt.",
    ]
    (OUT / "HUNDRED_TWENTY_SECOND_SHARED_NETWORK_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    summary = {
        "status": "COMPLETE", "shared_cards": len(deck), "statements": len(skeleton_rows),
        "statements_with_shared_skeleton": sum(r["shared_card_count"] != "0" for r in skeleton_rows),
        "directed_edges": len(edge_rows), "slots": len(slot_rows),
        "top_edges": [{"edge": f"{r['from_card']}>{r['to_card']}", "count": int(r["skeleton_edge_count"])} for r in edge_rows[:8]],
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

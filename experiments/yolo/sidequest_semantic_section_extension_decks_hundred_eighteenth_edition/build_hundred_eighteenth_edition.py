#!/usr/bin/env python3
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R116 = ROOT / "experiments/yolo/sidequest_semantic_exact_portable_deck_hundred_sixteenth_edition"
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_atomic_defaults_hundred_first_edition/HUNDRED_FIRST_381_EVENT_ATOMIC_INTERLINEAR.tsv"

RECORD_ORDER = ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"]


def load(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name, rows):
    with (OUT / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    dictionary = load(R116 / "HUNDRED_SIXTEENTH_173_FINAL_TEACHING_DICTIONARY.tsv")
    events = load(EVENTS)
    by_card = defaultdict(list)
    for row in events:
        by_card[row["master_card_id"]].append(row)

    membership = []
    for row in dictionary:
        ev = by_card[row["master_card_id"]]
        h = [x for x in ev if x["record_unit_id"].startswith("H")]
        b = [x for x in ev if x["record_unit_id"].startswith("B")]
        status = "SHARED_17" if h and b else "HERBAL_EXTENSION_49" if h else "BIOLOGICAL_EXTENSION_107"
        membership.append({
            "master_card_id": row["master_card_id"],
            "master_form": row["master_form"],
            "registered_surfaces": row["all_registered_surfaces"],
            "semantic_atoms": row["semantic_atoms"],
            "short_default_de": row["short_default_de"],
            "section_deck_status": status,
            "herbal_event_count": str(len(h)),
            "biological_event_count": str(len(b)),
            "herbal_records": "|".join(sorted({x["record_unit_id"] for x in h})) or "NONE",
            "biological_records": "|".join(sorted({x["record_unit_id"] for x in b})) or "NONE",
            "final_teaching_tier": row["final_teaching_tier"],
        })
    write_tsv("HUNDRED_EIGHTEENTH_173_SECTION_MEMBERSHIP.tsv", membership)

    herbal_deck = [r for r in membership if r["section_deck_status"] in {"SHARED_17", "HERBAL_EXTENSION_49"}]
    bio_deck = [r for r in membership if r["section_deck_status"] in {"SHARED_17", "BIOLOGICAL_EXTENSION_107"}]
    write_tsv("HUNDRED_EIGHTEENTH_66_CARD_HERBAL_DECK.tsv", herbal_deck)
    write_tsv("HUNDRED_EIGHTEENTH_124_CARD_BIOLOGICAL_DECK.tsv", bio_deck)

    lessons = []
    seen_by_section = {"H": set(), "B": set()}
    card_map = {r["master_card_id"]: r for r in membership}
    for record in RECORD_ORDER:
        section = record[0]
        record_events = [r for r in events if r["record_unit_id"] == record]
        record_cards = list(dict.fromkeys(r["master_card_id"] for r in record_events))
        shared = [c for c in record_cards if card_map[c]["section_deck_status"] == "SHARED_17"]
        new_extension = [c for c in record_cards if card_map[c]["section_deck_status"] != "SHARED_17" and c not in seen_by_section[section]]
        reused_extension = [c for c in record_cards if card_map[c]["section_deck_status"] != "SHARED_17" and c in seen_by_section[section]]
        seen_by_section[section].update(record_cards)
        lessons.append({
            "record_unit_id": record,
            "page": record_events[0]["page"],
            "event_count": str(len(record_events)),
            "distinct_card_count": str(len(record_cards)),
            "shared_deck_cards_used": str(len(shared)),
            "new_extension_cards": str(len(new_extension)),
            "reused_extension_cards": str(len(reused_extension)),
            "new_extension_master_forms": "|".join(card_map[c]["master_form"] for c in new_extension) or "NONE",
            "lesson_instruction": "review shared deck, introduce listed new section cards, then copy the complete record",
        })
    write_tsv("HUNDRED_EIGHTEENTH_ELEVEN_INCREMENTAL_RECORD_LESSONS.tsv", lessons)

    h_counts = Counter(r["master_card_id"] for r in events if r["record_unit_id"].startswith("H"))
    b_counts = Counter(r["master_card_id"] for r in events if r["record_unit_id"].startswith("B"))
    md = [
        "# Zwei vollständige Fachdecks", "",
        "## Herbal", "",
        "17 gemeinsame Karten + 49 Herbal-Erweiterungen = 66 Karten für 100 Ereignisse.",
        "55 der 66 Karten erscheinen innerhalb Herbal nur einmal; der Lehrling braucht daher viel Exemplartraining.", "",
        "## Biological", "",
        "17 gemeinsame Karten + 107 Biological-Erweiterungen = 124 Karten für 281 Ereignisse.",
        "82 der 124 Karten erscheinen innerhalb Biological nur einmal, doch häufige Prozesskarten wiederholen sich stärker.", "",
        "Die beiden Decks vereinigen sich exakt wieder zum 173-Karten-Gesamtinventar.",
    ]
    (OUT / "HUNDRED_EIGHTEENTH_TWO_SECTION_DECKS.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    report = [
        "# Hundertachtzehnte Runde: getrennte Fachdecks", "",
        "Das Herbal-Deck hat 66 Karten: siebzehn gemeinsam und 49 exklusiv. Das Biological-Deck hat",
        "124 Karten: siebzehn gemeinsam und 107 exklusiv. Ihre Vereinigung ist exakt das 173-Karten-",
        "Inventar; es bleibt keine dritte Prosaschicht übrig.", "",
        "Die Asymmetrie ist sinnvoll. Herbal hat nur 100 Ereignisse, aber 55 von 66 Kartentypen sind dort",
        "Singletons: Bildartikel kopieren viele seltene Stoff-/Zubereitungswerte. Biological hat 281",
        "Ereignisse und 82 von 124 Singletontypen, wiederholt daneben aber sein Prozess- und Abschlussdeck",
        "deutlich häufiger.", "",
        "Elf inkrementelle Recordlektionen zeigen genau, welche neuen Fachkarten bei H1–H5 und B1–B6",
        "erstmals eingeführt und welche bereits wiederverwendet werden.", "",
        "f84 und f84r blieben versiegelt.",
    ]
    (OUT / "HUNDRED_EIGHTEENTH_SECTION_DECK_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    summary = {
        "status": "COMPLETE", "shared": 17, "herbal_extension": 49, "bio_extension": 107,
        "herbal_deck": len(herbal_deck), "bio_deck": len(bio_deck),
        "herbal_events": sum(h_counts.values()), "bio_events": sum(b_counts.values()),
        "herbal_singletons": sum(v == 1 for v in h_counts.values()), "bio_singletons": sum(v == 1 for v in b_counts.values()),
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

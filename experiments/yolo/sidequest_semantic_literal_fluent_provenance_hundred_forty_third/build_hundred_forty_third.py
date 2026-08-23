#!/usr/bin/env python3
import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent
EXP = OUT.parents[1]
R142 = EXP / "yolo" / "sidequest_semantic_ten_apprentice_lessons_hundred_forty_second"

FLUENT = {
    "L01": "Bei der frischen Bildpflanze: Stelle den Wurzelposten als Ansatz bereit; nimm davon einen Anteil, führe ihn durch Gefäß und Flüssigkeitslauf, setze ihn ein und bemiss den kurzen Teil.",
    "L02": "Bei der Charge des Randgefäßes: Gib einen Anteil zu, nimm davon den nächsten Anteil, lass ihn lange einwirken und schließe.",
    "L03": "Im gemeinsamen Figurenbecken: Übertrage den Posten zur Zielstelle, führe ihn weiter und schließe.",
    "L04": "Beim Übergangsansatz: Überführe ihn dorthin, nimm den nächsten Posten, lass ihn lange einwirken, setze ihn ein, führe weiter, lass kurz absetzen und schließe.",
    "L05": "Bei der Arbeitsflüssigkeit der Doppelbecken: Stelle das Sollmaß ein, bearbeite lange, halte lange, lass kurz einwirken und schließe.",
    "L06": "Beim Blattauszug: Führe den Zusatz zur Zielstelle, wringe ihn aus, halte ihn nach Sollmaß, seih nach, nimm den Klarauszug und schließe.",
    "L07": "Bei den zwei Portionen: Dies und dies stehen unter demselben Sollmaß; danach abführen und schließen.",
    "L08": "Beim weitergeführten Ansatz: Nimm den Folgeansatz, führe denselben Ansatz in der Fortsetzung weiter, stelle das Sollmaß ein und nimm davon.",
    "L09": "Am Hauptpaar mit sichtbarer Tuchanwendung: Gib die weitere Zutat zum Arbeitsgang, bearbeite sie weiter, nimm den Auszug vom Ausgang und wende ihn danach an.",
    "L10": "An der Durchlassstation des Mittelgeräts: Leite den Posten durch und setze ihn ein.",
}

PROVENANCE = {
    "L01": [("Bildpflanze", "PICTURE_OWNER"), ("Wurzelposten", "CARD_CONTENT"), ("Ansatz", "CARD_CONTENT"), ("Anteil", "CARD_CONTENT"), ("Gefäß", "CARD_CONTENT"), ("Flüssigkeitslauf", "CARD_CONTENT"), ("Sollmaß", "CARD_CONTENT"), ("ihn", "ACTIVE_REGISTER"), ("kurzer Teil", "CARD_CONTENT")],
    "L02": [("Charge", "PICTURE_OWNER"), ("Randgefäß", "PICTURE_OWNER"), ("Anteil", "CARD_CONTENT"), ("davon", "CARD_CONTENT"), ("nächster Anteil", "ACTIVE_REGISTER_PLUS_CARD"), ("lange einwirken", "CARD_CONTENT")],
    "L03": [("Figurenbecken", "PICTURE_OWNER"), ("Posten", "ACTIVE_REGISTER"), ("Zielstelle", "CARD_CONTENT"), ("weiter", "CARD_CONTENT")],
    "L04": [("Übergangsansatz", "PICTURE_OWNER"), ("dorthin", "CARD_CONTENT"), ("nächster Posten", "CARD_CONTENT"), ("lange einwirken", "CARD_CONTENT"), ("einsetzen", "CARD_CONTENT"), ("absetzen", "CARD_CONTENT")],
    "L05": [("Arbeitsflüssigkeit", "PICTURE_OWNER"), ("Doppelbecken", "PICTURE_OWNER"), ("Sollmaß", "CARD_CONTENT"), ("lange bearbeiten", "CARD_CONTENT"), ("lange halten", "CARD_CONTENT"), ("kurz einwirken", "CARD_CONTENT")],
    "L06": [("Blattauszug", "PICTURE_OWNER"), ("Zusatz", "CARD_CONTENT"), ("Zielstelle", "CARD_CONTENT"), ("auswringen", "CARD_CONTENT"), ("Sollmaß", "CARD_CONTENT"), ("nachseihen", "CARD_CONTENT"), ("Klarauszug", "CARD_CONTENT")],
    "L07": [("zwei Portionen", "PICTURE_OWNER"), ("dies", "CARD_CONTENT"), ("dasselbe Sollmaß", "BRACKET_FORMULA"), ("abführen", "CARD_CONTENT")],
    "L08": [("weitergeführter Ansatz", "PICTURE_OWNER"), ("Folgeansatz", "CARD_CONTENT"), ("derselbe Ansatz", "CARD_CONTENT"), ("Fortsetzung", "BRACKET_FORMULA"), ("Sollmaß", "CARD_CONTENT"), ("davon", "CARD_CONTENT")],
    "L09": [("Hauptpaar", "PICTURE_OWNER"), ("Tuchanwendung", "PICTURE_OWNER"), ("weitere Zutat", "CARD_CONTENT"), ("Arbeitsgang", "MOULD_GRAMMAR"), ("Auszug", "CARD_CONTENT"), ("Ausgang", "CARD_CONTENT"), ("anwenden", "CARD_CONTENT")],
    "L10": [("Durchlassstation", "PICTURE_OWNER"), ("Mittelgerät", "PICTURE_OWNER"), ("Posten", "ACTIVE_REGISTER"), ("durchleiten", "CARD_CONTENT"), ("einsetzen", "CARD_CONTENT")],
}

OVERREACH = [
    ("M01_MATERIAL_PREPARATION", "Ansatz/Produkt", "Not every member names a product; say material/preparation chain"),
    ("M02_SOURCE_SHARE_MEASURE", "bemessen in every member", "B2-S011 has share/source/contact but no separate measure card"),
    ("M03_TARGET_TRANSFER", "body or vessel target", "Target kind always comes from owner, not the shared target card"),
    ("M05_STATE_CLOSE", "heat as default", "The selected lesson has processing and holding; heat is only one family option"),
    ("M06_FILTER_CLEAR_PRODUCT", "filter cloth", "Wring/strain/clear are card content; cloth is not present in every member"),
    ("M09_APPLICATION_FASTEN", "one productive share-target-fasten syntax", "Its three members are store, apply and fasten whole-card variants; keep as a practical family"),
    ("ALL", "water", "No lesson requires the generic noun water; use liquid/run unless AIR or local owner supplies it"),
    ("ALL", "patient or disease", "Neither is encoded in these cards; a figure or external article may supply it"),
]


def read_tsv(name):
    with (R142 / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name, rows):
    with (OUT / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    lessons = read_tsv("HUNDRED_FORTY_SECOND_TEN_APPRENTICE_LESSONS.tsv")
    editions = []
    provenance_rows = []
    for row in lessons:
        editions.append({
            "lesson_id": row["lesson_id"], "mould_id": row["mould_id"],
            "source_statement_id": row["source_statement_id"], "target_page": row["target_page"],
            "target_owner_de": row["target_owner_de"], "visible_master_sequence": row["master_card_sequence"],
            "literal_card_reading_de": row["literal_values_de"],
            "fluent_owner_expansion_de": FLUENT[row["lesson_id"]],
            "translation_rule": "FLUENT_NOUNS_MUST_APPEAR_IN_PROVENANCE_LEDGER",
        })
        for term, source in PROVENANCE[row["lesson_id"]]:
            provenance_rows.append({
                "lesson_id": row["lesson_id"], "mould_id": row["mould_id"],
                "inserted_term_de": term, "source_layer": source,
                "portable_card_meaning": "YES" if source in {"CARD_CONTENT", "BRACKET_FORMULA"} else "NO",
                "reading_instruction": "read from card/formula" if source in {"CARD_CONTENT", "BRACKET_FORMULA"} else "supply only in this owner/register context",
            })
    overreach_rows = [{"mould_id": a, "withdraw_or_narrow": b, "replacement_rule": c} for a, b, c in OVERREACH]
    write_tsv("HUNDRED_FORTY_THIRD_TEN_LITERAL_FLUENT_LESSONS.tsv", editions)
    write_tsv("HUNDRED_FORTY_THIRD_EXPANSION_PROVENANCE.tsv", provenance_rows)
    write_tsv("HUNDRED_FORTY_THIRD_FLUENT_OVERREACH_REPAIRS.tsv", overreach_rows)

    readable = ["# Wörtliche und flüssige Lehrlingslesungen", ""]
    for row in editions:
        readable += [f"## {row['lesson_id']} · {row['mould_id']}", "", f"Karten: `{row['visible_master_sequence']}`", "",
                     f"Wörtlich: {row['literal_card_reading_de']}", "", f"Flüssig: {row['fluent_owner_expansion_de']}", "",
                     "Herkunft der konkreten Wörter:", ""]
        for p in [x for x in provenance_rows if x["lesson_id"] == row["lesson_id"]]:
            readable.append(f"- {p['inserted_term_de']}: {p['source_layer']}")
        readable.append("")
    (OUT / "HUNDRED_FORTY_THIRD_SIDE_BY_SIDE_READINGS.md").write_text("\n".join(readable).rstrip() + "\n", encoding="utf-8")

    report = [
        "# Hundertdreiundvierzigste Runde: Woher kommt jedes deutsche Wort?", "",
        "The ten owner-substituted lessons now have literal and fluent readings side by side. Every concrete fluent",
        "term is labeled CARD_CONTENT, PICTURE_OWNER, ACTIVE_REGISTER, BRACKET_FORMULA or MOULD_GRAMMAR. This keeps",
        "a readable German expansion without stuffing picture nouns back into the dictionary.", "",
        "The most important clean split is L09: `Tuchanwendung` comes from the visible B4 owner; the cards contribute",
        "further ingredient, processing, extract/source and application. Likewise basin, vessel, plant and station",
        "names are owner values. ANTEIL, SOLLMASS, KLARAUSZUG, ZIELSTELLE, AUSZUG and the short operations remain",
        "portable card contents.", "",
        "The audit also narrows three overly fluent mould descriptions. M02 does not always contain a separate",
        "measure action. M09 is a practical store/apply/fasten family, not one freely productive syntax. Filter cloth,",
        "water, patient and disease must not be silently supplied unless the picture/register explicitly does so.", "",
        "Next revise the ten-mould phrasebook with these provenance boundaries and create a new current dictionary",
        "edition in which portable word, owner argument and fluent expansion occupy separate columns.",
    ]
    (OUT / "HUNDRED_FORTY_THIRD_PROVENANCE_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps({"lessons": len(editions), "provenance_terms": len(provenance_rows), "portable_terms": sum(r["portable_card_meaning"] == "YES" for r in provenance_rows), "context_terms": sum(r["portable_card_meaning"] == "NO" for r in provenance_rows), "overreach_repairs": len(overreach_rows)}, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

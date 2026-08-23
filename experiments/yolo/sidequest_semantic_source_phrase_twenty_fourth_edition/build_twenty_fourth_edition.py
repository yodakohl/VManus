#!/usr/bin/env python3
from pathlib import Path
from collections import Counter, defaultdict
import csv
import json
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
UNITS = ROOT / "experiments/yolo/sidequest_semantic_stem_aligned_twentieth_edition/TWENTIETH_258_UNIT_TRANSLATIONS.tsv"


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path, fields, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


TEMPLATES = [
    ("P_FILTER", "PROSE", "OWNER > MATERIAL > PRESS/STRAIN > STAND > CLEAR RESULT > STORE", "Recipe de [OWNER]; exprime, cola, dimitte stare, clarum recipe et serva.", "Vom sichtbaren Besitzer nehmen; auswringen oder seihen; stehen lassen; sichtbaren Auszug nehmen; verwahren."),
    ("P_APPLICATION", "PROSE", "OWNER > PREPARATION > TARGET > CONTACT GRADE > FASTEN/CLOSE", "Recipe praeparatum de [OWNER]; pone ad locum, tene et liga.", "Bereitung des Besitzers nehmen; an die Stelle bringen; anlegen oder halten; befestigen und schließen."),
    ("P_WASH", "PROSE", "OWNER > WATER/LIQUID > WASH > OUTLET > CLOSE", "Recipe liquorem de [OWNER]; lava, per conductum duc, effunde et claude.", "Arbeitsflüssigkeit des Besitzers nehmen; waschen; durch den Lauf führen; abführen und schließen."),
    ("P_WARM", "PROSE", "OWNER > CURRENT ITEM > WARM/HOLD GRADE > READY/CLOSE", "Recipe de [OWNER]; calefac leniter, tene ad gradum et comple.", "Aktuellen Posten des Besitzers nehmen; gelinde wärmen; bis zur Stufe halten; bereitstellen oder schließen."),
    ("P_SETTLE", "PROSE", "OWNER > BATCH > STAND/SETTLE > GRADE > RESULT", "Recipe praeparatum de [OWNER]; dimitte stare ad gradum et recipe superius.", "Ansatz des Besitzers stehen oder absetzen lassen; Stufe abwarten; gewonnenen Anteil nehmen."),
    ("P_COLLECT", "PROSE", "OWNER > FLOW/OUTPUT > RECEIVER > MEASURE > CLOSE", "Recipe fluxum de [OWNER]; collige in vase, mensura et serva.", "Ausgabe oder Lauf des Besitzers auffangen; im Empfänger sammeln; bemessen und verwahren."),
    ("P_FLOW", "PROSE", "OWNER > SOURCE > COURSE/PASSAGE > TARGET > CURRENT/CLOSE", "Ab [OWNER] per cursum ad locum duc; ibi tene vel claude.", "Von der sichtbaren Quelle durch den Lauf zum Ziel führen; dort halten oder schließen."),
    ("P_TRANSFER", "PROSE", "OWNER > SOURCE > TRANSFER > TARGET > CURRENT/CLOSE", "Recipe de [OWNER]; transfer ab fonte ad locum et comple.", "Vom Besitzer oder Ausgang nehmen; zum Ziel umsetzen; den Posten weiterführen oder schließen."),
    ("P_MEASURE", "PROSE", "OWNER > PORTION/MEASURE/STAGE > SET > CURRENT", "Recipe de [OWNER] portionem ad mensuram; pone in gradu suo.", "Vom Besitzer eine Portion nehmen; auf Sollmaß oder Arbeitsstufe stellen."),
    ("P_PREPARE", "PROSE", "OWNER > INPUT/BATCH > PROCESS > CURRENT/CLOSE", "Recipe de [OWNER]; para, operare et serva quod fit.", "Vom sichtbaren Besitzer nehmen; Ansatz bereiten; bearbeiten; Ergebnis weitergeben oder verwahren."),
    ("A_SOURCE_TARGET", "ASTRO", "VISIBLE LOCUS > SOURCE > TARGET/COURSE > READ", "In figura [OWNER], ab fonte ad locum vel cursum lege.", "Am sichtbaren Diagrammplatz Quelle und Ziel oder Bahn lesen."),
    ("A_MARK_SELECT", "ASTRO", "VISIBLE LOCUS > SELECT/MARK > CURRENT VALUE > HOLD", "In figura [OWNER], elige locum, nota valorem et tene.", "Am sichtbaren Diagrammplatz auswählen; Wert markieren; aktuellen Eintrag halten."),
    ("A_GRADE_VALUE", "ASTRO", "VISIBLE LOCUS > VALUE/STAGE/GRADE > CURRENT/READ", "In figura [OWNER], gradum vel valorem statutum lege.", "Am sichtbaren Diagrammplatz Stufe, Grad oder Sollwert lesen."),
    ("A_CLASS_FIELD", "ASTRO", "VISIBLE LOCUS > CLASS/HOUSE/FIELD > VALUE", "In figura [OWNER], classem sive domum et valorem eius lege.", "Am sichtbaren Diagrammplatz Klasse, Haus, Paarfeld oder Rahmen lesen."),
    ("A_NEXT_CONTINUE", "ASTRO", "VISIBLE LOCUS > NEXT/CONTINUE > VALUE/COURSE", "In figura [OWNER], sequens accipe vel in eodem ordine continua.", "Am sichtbaren Diagrammplatz den nächsten Eintrag nehmen oder im selben Ring fortsetzen."),
    ("A_LOCAL_ENTRY", "ASTRO", "VISIBLE LOCUS > LEARNED LOCAL VALUE > READ", "In figura [OWNER], signum loci ex exemplari lege.", "Den lokalen Wert am sichtbaren Platz aus dem Meisterexemplar lesen."),
]

template_rows = [
    {
        "template_id": template_id,
        "register": register,
        "source_slot_order": slots,
        "latin_like_workshop_formula": latin,
        "german_source_order": german,
    }
    for template_id, register, slots, latin, german in TEMPLATES
]
template_map = {row["template_id"]: row for row in template_rows}
write(HERE / "TWENTY_FOURTH_SOURCE_ORDER_TEMPLATES.tsv", list(template_rows[0]), template_rows)


def atom_set(sequence):
    return {
        atom.strip()
        for group in sequence.split("|")
        for atom in group.split("+")
        if atom.strip() and atom.strip() != "NONE"
    }


def classify(row):
    atoms = atom_set(row["atom_sequence"])
    if row["register"] == "PROSE":
        if atoms & {"CFH", "CPH", "CKHE", "CHEEY"}:
            return "P_FILTER"
        if atoms & {"DAN", "LDDY"}:
            return "P_APPLICATION"
        if atoms & {"WASH"}:
            return "P_WASH"
        if atoms & {"CHK"}:
            return "P_WARM"
        if atoms & {"SHED"}:
            return "P_SETTLE"
        if atoms & {"SOLK"}:
            return "P_COLLECT"
        if atoms & {"AIR", "CKH"}:
            return "P_FLOW"
        if atoms & {"CHD", "P", "L"}:
            return "P_TRANSFER"
        if atoms & {"AIIN", "AIN", "IIN"}:
            return "P_MEASURE"
        return "P_PREPARE"
    if "AR" in atoms and ({"AL", "AIR"} & atoms):
        return "A_SOURCE_TARGET"
    if atoms & {"OD", "SEL", "YD"}:
        return "A_MARK_SELECT"
    if atoms & {"AIIN", "AIN", "IIN", "G", "E", "EE", "EEE"}:
        return "A_GRADE_VALUE"
    if atoms & {"YK", "OP", "K", "OS"}:
        return "A_CLASS_FIELD"
    if atoms & {"OT", "OL"}:
        return "A_NEXT_CONTINUE"
    return "A_LOCAL_ENTRY"


units = read(UNITS)
rows = []
for source in units:
    template_id = classify(source)
    template = template_map[template_id]
    owner = source["visible_owner"]
    rows.append(
        {
            "unit_serial": source["unit_serial"],
            "register": source["register"],
            "page": source["page"],
            "unit_id": source["unit_id"],
            "visible_owner": owner,
            "group_count": source["group_count"],
            "template_id": template_id,
            "source_slot_order": template["source_slot_order"],
            "latin_like_workshop_formula": template["latin_like_workshop_formula"].replace("[OWNER]", owner),
            "german_source_order": template["german_source_order"],
            "compressed_surface_sequence": source["surface_sequence"],
            "recovered_atom_sequence": source["atom_sequence"],
            "recovered_literal_de": source["literal_card_reading_de"],
            "fluent_owner_reading_de": source["owner_expansion_de"],
        }
    )
write(HERE / "TWENTY_FOURTH_258_SOURCE_PHRASE_EDITION.tsv", list(rows[0]), rows)

by_section = defaultdict(list)
for row in rows:
    key = row["unit_id"].split("-")[0] if row["register"] == "PROSE" else row["page"]
    by_section[key].append(row)

summary_rows = []
for key in ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6", "f67r2", "f68r1", "f69v"]:
    members = by_section[key]
    counts = Counter(row["template_id"] for row in members)
    summary_rows.append(
        {
            "section_id": key,
            "register": members[0]["register"],
            "page": members[0]["page"],
            "unit_count": len(members),
            "group_count": sum(int(row["group_count"]) for row in members),
            "template_sequence": " > ".join(row["template_id"] for row in members),
            "template_counts": "|".join(f"{name}:{counts[name]}" for name in sorted(counts)),
        }
    )
write(HERE / "TWENTY_FOURTH_FOURTEEN_SOURCE_SEQUENCES.tsv", list(summary_rows[0]), summary_rows)

selected_ids = ["H1-S001", "H3-S001", "H4-S002", "B1-S002", "B2-S016", "B4-S001", "f67r2.19", "f68r1.37", "f69v.19"]
selected = {row["unit_id"]: row for row in rows}
doc = [
    "# Vorstufe der Karten: plausible Meisterphrasen",
    "",
    "Die folgenden Formeln sind keine behauptete Voynich-Sprache. Sie zeigen eine",
    "knappe Rezept-, Stations- oder Tafelsprache, die ein Schreiber um 1420 in",
    "unser Kartensystem hätte verdichten können. Entscheidend ist die Reihenfolge",
    "Besitzer → Material/Adresse → Handlung → Menge/Richtung/Grad → Ergebnis.",
    "",
    "## Sechzehn Quellenrahmen",
    "",
]
for row in template_rows:
    doc.extend(
        [
            f"### {row['template_id']}",
            "",
            f"Slotfolge: `{row['source_slot_order']}`",
            "",
            f"Lateinähnliche Werkstattformel: *{row['latin_like_workshop_formula']}*",
            "",
            row["german_source_order"],
            "",
        ]
    )
doc.extend(["## Neun vollständige Verdichtungen", ""])
for unit_id in selected_ids:
    row = selected[unit_id]
    doc.extend(
        [
            f"### {unit_id} — {row['template_id']}",
            "",
            f"Vorstufe: *{row['latin_like_workshop_formula']}*",
            "",
            f"Karten: `{row['compressed_surface_sequence']}`",
            "",
            f"Kerne: `{row['recovered_atom_sequence']}`",
            "",
            f"Rücklesung: {row['recovered_literal_de']}",
            "",
            f"Flüssig: {row['fluent_owner_reading_de']}",
            "",
        ]
    )
doc.extend(
    [
        "## Ergebnis",
        "",
        "Die Kartenfolge braucht keine moderne Vollsatzsyntax. Sie passt besser zu",
        "einer knappen Quellphrase mit ausgelassenem Bildbesitzer, wiederholtem",
        "Arbeitsgegenstand und vielen Imperativen. Die lateinähnliche Zeile ist nur",
        "ein sprechbares Lehrgerüst; derselbe Compiler könnte ebenso von einer",
        "volkssprachlichen Werkstattanweisung gespeist werden.",
    ]
)
(HERE / "TWENTY_FOURTH_PLAUSIBLE_SOURCE_PHRASES.md").write_text("\n".join(doc).rstrip() + "\n", encoding="utf-8")

template_counts = Counter(row["template_id"] for row in rows)
summary = {
    "status": "PASS",
    "counts": {
        "templates": len(template_rows),
        "units": len(rows),
        "prose_units": sum(row["register"] == "PROSE" for row in rows),
        "astro_units": sum(row["register"] == "ASTRO" for row in rows),
        "groups": sum(int(row["group_count"]) for row in rows),
        "sections": len(summary_rows),
        "used_templates": len(template_counts),
    },
    "template_counts": dict(sorted(template_counts.items())),
}
(HERE / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(summary, ensure_ascii=False, indent=2))

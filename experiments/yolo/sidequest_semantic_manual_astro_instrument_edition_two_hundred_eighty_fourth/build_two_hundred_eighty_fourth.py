#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R275 = ROOT / "experiments/yolo/sidequest_semantic_three_astro_readings_two_hundred_seventy_fifth"
R276 = ROOT / "experiments/yolo/sidequest_semantic_astro_templates_two_hundred_seventy_sixth"
LOCI = R275 / "TWO_HUNDRED_SEVENTY_FIFTH_142_LOCUS_READINGS.tsv"
TEMPLATES = R276 / "TWO_HUNDRED_SEVENTY_SIXTH_142_TEMPLATE_ASSIGNMENTS.tsv"

TEMPLATE_ACTION = {
    "SOURCE_TO_TARGET": "Lies den bezeichneten Ausgangswert und übertrage ihn auf die angegebene Zielstelle.",
    "ADDRESSED_ENTRY": "Lies die Quell- oder Zieladresse dieses sichtbaren Platzes.",
    "FOLLOWING_RELATION": "Gehe zum Folgeposten und setze dort dieselbe Reihe oder die nächste Bedingung fort.",
    "ROW_CONTINUATION": "Führe den aktuellen Ring, das Band oder den Eintrag an diesem Platz weiter.",
    "CONDITION_ENTRY": "Setze oder lies die besondere Bedingung dieses Platzes.",
    "GRADED_OR_QUANTIFIED_VALUE": "Lies den Teilwert, Sollwert oder Grad dieses Platzes und stelle ihn ein.",
    "ACTION_OR_PATH": "Setze, halte oder übertrage den Posten entlang der hier bezeichneten Bahn.",
    "LOCAL_NAMED_ENTRY": "Lies oder kopiere den gelernten örtlichen Namen dieses Platzes.",
}

PAGE_EDITIONS = {
    "f67r2": {
        "title": "Doppelrad für Sektor- und Phasenwerte",
        "instrument": "CELESTIAL_SECTOR_AND_PHASE_LOOKUP_PAIR",
        "reading": (
            "Benutze die beiden Räder getrennt. Am rechten Rad wählst du einen der zwölf Sektorplätze, liest zwei Ringwerte "
            "und bei Bedarf einen der acht Phasenposten. Das linke Rad trägt ein dichteres Feldregister und zwölf äußere "
            "Sternstationen. Ein Eintrag kann einen örtlichen Namen, eine Adresse, einen Grad, eine Bedingung oder eine "
            "Quelle-Ziel-Zuweisung enthalten. Die beiden Außenlegenden benennen ihre Räder; die gemeinsame Legende erklärt "
            "nur die Paarung. Beginne dort, wo Bild oder Auftrag hinweist, nicht an einer angenommenen Zwölf-Uhr-Stelle."
        ),
        "concrete_use_wager": "choose a celestial sector and phase condition for a workshop action",
    },
    "f68r1": {
        "title": "Mehrpaneel-Sternstationsregister",
        "instrument": "SPATIAL_STAR_STATION_CATALOGUE",
        "reading": (
            "Lies zuerst nur den Kopf des tatsächlich benutzten Paneels. Der Mittelbereich besitzt einen eigenen Schlüssel, "
            "aber kein sicher einziges Zentrum. Danach wählst du eine der achtundzwanzig räumlichen Sternstellen und liest "
            "deren gelernten Namen zusammen mit Adresse, Bedingung, Grad oder Bahn. Die Sternplätze sind ein räumliches "
            "Register, keine zwingend umlaufende Liste. Diese Tafel identifiziert eine Himmelsstelle und ihren Arbeitswert; "
            "sie liefert keinen Schlüssel für f69v."
        ),
        "concrete_use_wager": "identify one of 28 celestial stations and read its local condition",
    },
    "f69v": {
        "title": "Drei getrennte Wahlräder mit 28er-Register links",
        "instrument": "THREE_CELESTIAL_CHOICE_WHEELS",
        "reading": (
            "Behandle linkes, mittleres und rechtes Rad als drei selbständige Nachschlagetafeln. Die Ringtexte der drei Räder "
            "geben je eine eigene Adresse oder Quelle-Ziel-Regel. Nur das linke Rad besitzt achtundzwanzig lokale Plätze: "
            "dort liest du Namen, Grad, Bedingung, Bahn oder Zuweisung des ausgewählten Postens. Die mittlere und rechte "
            "Rosette sind Vergleichs- oder Nebenräder, nicht Fortsetzungen der 28er-Liste. Der wahrscheinlichste Zweck ist "
            "eine Wahl günstiger Arbeitsbedingungen; die Plätze werden aber nicht automatisch als Tage durchnummeriert."
        ),
        "concrete_use_wager": "select one of 28 local celestial work conditions on the left wheel",
    },
}


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


def number(owner: str) -> int:
    match = re.search(r"_(\d+)$", owner)
    return int(match.group(1)) if match else 0


def owner_de(owner: str) -> str:
    n = number(owner)
    rules = (
        ("A1_RIGHT_SECTOR_SLOT_", lambda: f"Sektorplatz {n} des rechten Rades"),
        ("A1_RIGHT_RING_BAND_", lambda: f"Ringband {n} des rechten Rades"),
        ("A1_LEFT_LOCAL_FIELD_", lambda: f"Innenfeld {n - 14} des linken Rades"),
        ("A1_LEFT_OUTER_STAR_STATION_", lambda: f"äußere Sternstation {n} des linken Rades"),
        ("A1_RIGHT_PHASE_STATION_", lambda: f"Phasenposten {n} des rechten Rades"),
        ("A2_STAR_STATION_", lambda: f"Sternstation {n} des Mehrpaneelregisters"),
        ("A2_MULTIPANEL_HEADER_FRAGMENT_", lambda: f"Kopffragment {n} des Mehrpaneelregisters"),
        ("A3_LEFT_RADIAL_SLOT_", lambda: f"örtlicher Platz {n} des linken Wahlrades"),
    )
    for prefix, render in rules:
        if owner.startswith(prefix):
            return render()
    exact = {
        "A1_LEFT_OUTER_RING_TEXT": "Außenlegende des linken Rades",
        "A1_RIGHT_OUTER_RING_TEXT": "Außenlegende des rechten Rades",
        "A1_PAIRED_WHEEL_LEGEND_UNRESOLVED": "gemeinsame Legende des Radpaares",
        "A2_LEFT_PANEL_HEADER": "Kopf des linken Paneels",
        "A2_MIDDLE_PANEL_HEADER": "Kopf des mittleren Paneels",
        "A2_RIGHT_PANEL_HEADER": "Kopf des rechten Paneels",
        "A2_CENTRE_KEY_UNRESOLVED": "örtlicher Schlüssel im Mittelbereich",
        "A2_CENTRAL_LEGEND_UNRESOLVED": "Legende des Mittelbereichs",
        "A3_LEFT_WHEEL_RING_TEXT": "Ringtext des linken Wahlrades",
        "A3_MIDDLE_WHEEL_RING_TEXT": "Ringtext des mittleren Wahlrades",
        "A3_RIGHT_WHEEL_RING_TEXT": "Ringtext des rechten Wahlrades",
    }
    return exact[owner]


def clean_detail(value: str) -> str:
    value = value.replace("Lokalschluessel", "örtlicher Name")
    value = value.replace("lokaler Namensrest", "Namensendung")
    value = value.replace("Ganzzeichen", "gelerntes Zeichen")
    return value.strip().rstrip(".")


def owner_location_de(place: str) -> str:
    if place.startswith("Sektorplatz") or place.startswith("Ringband") or place.startswith("Phasenposten"):
        return f"Am {place}"
    if place.startswith("örtlicher Platz"):
        return f"Am {place.replace('örtlicher Platz', 'örtlichen Platz', 1)}"
    if place.startswith("Innenfeld") or place.startswith("Kopf") or place.startswith("Kopffragment") or place.startswith("Ringtext"):
        return f"Im {place}"
    if place.startswith("äußere Sternstation"):
        return f"An der {place.replace('äußere Sternstation', 'äußeren Sternstation', 1)}"
    if place.startswith("Sternstation"):
        return f"An der {place}"
    if "legende" in place.lower():
        if place.startswith("gemeinsame Legende"):
            place = place.replace("gemeinsame Legende", "gemeinsamen Legende", 1)
        return f"In der {place}"
    if place.startswith("örtlicher Schlüssel"):
        return f"Beim {place.replace('örtlicher Schlüssel', 'örtlichen Schlüssel', 1)}"
    raise ValueError(place)


def main() -> None:
    loci = {(r["page"], r["locus"]): r for r in read_tsv(LOCI)}
    template_rows = read_tsv(TEMPLATES)
    assert len(loci) == len(template_rows) == 142

    rows: list[dict[str, object]] = []
    for source in template_rows:
        base = loci[(source["page"], source["locus"])]
        place = owner_de(source["visible_owner"])
        detail = clean_detail(source["continuous_default_reading_de"])
        rows.append({
            "page": source["page"],
            "locus": source["locus"],
            "visible_owner": source["visible_owner"],
            "visible_owner_de": place,
            "namespace_id": source["namespace_id"],
            "group_count": int(source["group_count"]),
            "visible_sequence": base["visible_sequence"],
            "astro_template": source["astro_template"],
            "manual_locus_translation_de": f"{owner_location_de(place)}: {TEMPLATE_ACTION[source['astro_template']]} Kartenlesung: {detail}.",
            "concrete_default_role": {
                "f67r2": "SECTOR_OR_PHASE_LOOKUP_VALUE",
                "f68r1": "STAR_STATION_NAME_OR_CONDITION",
                "f69v": "CELESTIAL_CHOICE_OR_WORK_CONDITION",
            }[source["page"]],
            "orientation": "NOT_REQUIRED__SELECT_BY_VISIBLE_OWNER",
            "cross_page_key": "NONE",
        })

    editions: list[dict[str, object]] = []
    for page, spec in PAGE_EDITIONS.items():
        selected = [r for r in rows if r["page"] == page]
        editions.append({
            "page": page,
            "title_de": spec["title"],
            "instrument_type": spec["instrument"],
            "locus_count": len(selected),
            "group_count": sum(int(r["group_count"]) for r in selected),
            "namespace_count": len({str(r["namespace_id"]) for r in selected}),
            "continuous_instrument_reading_de": spec["reading"],
            "strongest_concrete_use_wager": spec["concrete_use_wager"],
            "start_direction_rotation": "choose by visible owner; no fixed start, direction, or rotation",
        })

    locus_path = OUT / "TWO_HUNDRED_EIGHTY_FOURTH_142_MANUAL_LOCUS_TRANSLATIONS.tsv"
    edition_path = OUT / "TWO_HUNDRED_EIGHTY_FOURTH_THREE_INSTRUMENT_NARRATIVES.tsv"
    readable_path = OUT / "TWO_HUNDRED_EIGHTY_FOURTH_COMPLETE_ASTRO_EDITION.md"
    report_path = OUT / "TWO_HUNDRED_EIGHTY_FOURTH_REPORT.md"
    write_tsv(locus_path, rows, list(rows[0]))
    write_tsv(edition_path, editions, list(editions[0]))

    md = [
        "# Vollständige manuelle Astro-Instrumentausgabe",
        "",
        "Jeder Ort ist ein eigener Nachschlageposten. Die Leserichtung kommt vom sichtbaren Auftrag oder Bildzeiger, nicht aus einer erfundenen Kreisrichtung.",
        "",
    ]
    for edition in editions:
        md.extend([
            f"## {edition['page']}: {edition['title_de']}",
            "",
            str(edition["continuous_instrument_reading_de"]),
            "",
        ])
        for row in [r for r in rows if r["page"] == edition["page"]]:
            md.append(f"- **{row['locus']}** — {row['manual_locus_translation_de']}")
        md.append("")
    readable_path.write_text("\n".join(md), encoding="utf-8")

    report_path.write_text(
        "# Sidequest-Pass 284: drei manuell lesbare Astro-Instrumente\n\n"
        "## Ergebnis\n\n"
        "Alle 142 Astro-Orte und 395 sichtbaren Gruppen haben nun einen knappen Nachschlagebefehl. f67r2 wird als getrenntes Sektor-/Phasen-Radpaar gelesen, "
        "f68r1 als räumlicher 28-Sternstationskatalog und f69v als drei Wahlräder, von denen nur das linke 28 lokale Arbeitsbedingungen trägt. "
        "Der kreative Zweck ist ein Himmelsalmanach für die Wahl oder Einstellung von Arbeitsbedingungen.\n\n"
        "Diese Lesung braucht weder festen Start noch Drehrichtung. Sie macht aus den 28 Plätzen keine automatisch geordneten Tage und verbindet f68r1 nicht mit f69v. "
        "Die drei Seiten benutzen dieselbe portable Adress-, Folge-, Grad- und Bahnsyntax, bleiben aber eigene Instrumente.\n\n"
        f"Inputs `{sha(LOCI)}` und `{sha(TEMPLATES)}`.\n",
        encoding="utf-8",
    )

    outputs = (locus_path, edition_path, readable_path, report_path)
    summary = {
        "status": "PASS",
        "loci": len(rows),
        "groups": sum(int(r["group_count"]) for r in rows),
        "pages": len(editions),
        "page_loci": dict(Counter(str(r["page"]) for r in rows)),
        "templates": dict(Counter(str(r["astro_template"]) for r in rows)),
        "outputs": {p.name: sha(p) for p in outputs},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

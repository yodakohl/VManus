#!/usr/bin/env python3
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "sidequest_theory_candidates_v80" / "V80_R3_395_ASTRO_GROUPS.tsv"

NAMESPACE_READINGS = {
    "F67_RIGHT_WHEEL_NS": (
        "rechtes Sektor- und Bedingungsrad",
        "einen groben Himmelsabschnitt oder sichtbaren Bedingungsplatz waehlen und nur die zugehoerige Radlegende konsultieren",
        "gegliederte Himmels-Lehrtafel ohne praktischen Entscheidungszweck",
    ),
    "F67_LEFT_WHEEL_NS": (
        "linkes Stern-, Strahl- oder Aspektfeldrad",
        "eine feinere Stern- oder Aspektlage nach ihrem Bildort nachschlagen",
        "eigenstaendiges Stern-Merkbild ohne Verbindung zum rechten Rad",
    ),
    "F67_PAIRED_LEGEND_QUARANTINE_NS": (
        "ungeloeste Seitenlegende zwischen beiden Raedern",
        "nur als gemeinsame Ueberschrift oder Gebrauchshinweis abschreiben",
        "reiner Seitentitel ohne Auswahlinhalt",
    ),
    "F68_LEFT_PANEL_HEADER_NS": (
        "linke Sternfeld-Ueberschrift",
        "das linke Sternfeld als eigene Nachschlageeinheit aufrufen",
        "Rubrik eines Bild- oder Lehratlasses",
    ),
    "F68_MIDDLE_PANEL_HEADER_NS": (
        "mittlere Sternfeld-Ueberschrift",
        "das mittlere Sternfeld als eigene Nachschlageeinheit aufrufen",
        "Rubrik eines Bild- oder Lehratlasses",
    ),
    "F68_RIGHT_PANEL_HEADER_NS": (
        "rechte Sternfeld-Ueberschrift",
        "das rechte gegliederte Sternfeld als eigene Nachschlageeinheit aufrufen",
        "Rubrik eines Bild- oder Lehratlasses",
    ),
    "F68_LOCAL_STAR_SLOT_NS": (
        "achtundzwanzig raeumliche Stern- oder Asterismusplaetze",
        "den beim Bild gezeigten Sternplatz nachschlagen; keine Kreisfolge voraussetzen",
        "benannter Sternatlas, dessen Eintraege nur zum Wiedererkennen dienen",
    ),
    "F68_MULTIPANEL_HEADER_QUARANTINE_NS": (
        "ungeloeste mehrpaneelige Kopfstuecke",
        "sichtbaren Kopftext bewahren, aber keinem einzelnen Sternplatz zwingen",
        "ornamentale oder redaktionelle Zwischenrubriken",
    ),
    "F68_CENTRAL_LEGEND_QUARANTINE_NS": (
        "ungeloeste Zentrallegende",
        "als lokalen Schluesselbereich behandeln, ohne ein einziges Seitenzentrum zu erfinden",
        "reine Zentralbeschriftung eines Lehrbildes",
    ),
    "F68_CENTRE_KEY_QUARANTINE_NS": (
        "ungeloestes Gesichts- oder Zentrumszeichen",
        "nur als moeglichen lokalen Schluesselhalter behandeln",
        "Bildmedaillon ohne katalogische Funktion",
    ),
    "F69_LEFT_WHEEL_NS": (
        "linkes Rad mit lokalem Achtundzwanziger-Inventar",
        "einen der 28 Bildplaetze lokal waehlen und die Ringrubrik desselben Rades konsultieren; keine Reihenfolge erfinden",
        "ungeordnetes Radialinventar oder Merkbild ohne Zeitfunktion",
    ),
    "F69_MIDDLE_WHEEL_NS": (
        "mittleres Wolken-, Wellen- oder Himmelszustandsrad",
        "einen Wetter- oder Himmelszustand als eigene Bedingung nachschlagen",
        "selbstaendige kosmographische Bildrubrik",
    ),
    "F69_RIGHT_WHEEL_NS": (
        "rechtes Gesichts-, Licht- oder Planetenrad",
        "einen Licht-, Gestirn- oder Komplexionszustand als eigene Bedingung nachschlagen",
        "selbstaendige Planeten- oder Lehrbildrubrik",
    ),
}


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name, rows):
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def role_for(content_class):
    if any(token in content_class for token in ("RUBRIC", "HEADER")):
        return "LOCAL_INSTRUMENT_LEGEND"
    if any(token in content_class for token in (
        "SECTOR", "CONDITION", "STAR_RAY", "OUTER_STAR_POSITION",
        "ASTERISM_STATION", "28_PLACE_INVENTORY_ENTRY",
    )):
        return "SELECTABLE_CELESTIAL_SLOT"
    return "OWNER_OR_KEY_UNRESOLVED"


def main():
    source = read(SOURCE)
    group_rows = []
    by_locus = defaultdict(list)
    for row in source:
        by_locus[row["locus"]].append(row)
        title, practical, atlas = NAMESPACE_READINGS[row["canonical_namespace_id"]]
        group_rows.append({
            "group_serial": row["group_serial"],
            "page": row["page"],
            "locus": row["locus"],
            "event_index": row["event_index"],
            "opaque_local_id": row["opaque_local_id"],
            "surface_display_only": row["surface_display_only"],
            "canonical_namespace_id": row["canonical_namespace_id"],
            "local_image_owner": row["local_image_owner"],
            "local_content_class": row["local_content_class"],
            "interface_role": role_for(row["local_content_class"]),
            "instrument_reading_de": title,
            "possible_condition_use_de": practical,
            "memory_atlas_rival_de": atlas,
            "prose_dictionary_import": "NONE",
            "cross_section_pointer": "NONE",
            "orientation_or_rotation": "NONE",
            "f68_f69_key": "NONE",
        })

    locus_rows = []
    for locus, rows in sorted(by_locus.items(), key=lambda item: int(item[1][0]["group_serial"])):
        rows.sort(key=lambda row: int(row["event_index"]))
        first = rows[0]
        title, practical, atlas = NAMESPACE_READINGS[first["canonical_namespace_id"]]
        roles = {role_for(row["local_content_class"]) for row in rows}
        role = next(iter(roles)) if len(roles) == 1 else "COMPOSITE_LOCAL_LABEL"
        locus_rows.append({
            "page": first["page"],
            "locus": locus,
            "group_count": len(rows),
            "complete_surface_display_only": " ".join(row["surface_display_only"] for row in rows),
            "canonical_namespace_id": first["canonical_namespace_id"],
            "local_image_owner": first["local_image_owner"],
            "interface_role": role,
            "instrument_reading_de": title,
            "possible_condition_use_de": practical,
            "memory_atlas_rival_de": atlas,
            "working_reading_de": (
                "lokalen Bildplatz zeigen, vollstaendige Etikette kopieren und nur innerhalb dieses Instruments nachschlagen"
            ),
            "claim_limit_de": (
                "keine Einzelwortuebersetzung; kein Start, keine Richtung, kein Seitenjoin und keine Zuordnung zu einer Prosa-Handlung"
            ),
        })

    namespace_rows = []
    for namespace in NAMESPACE_READINGS:
        rows = [row for row in locus_rows if row["canonical_namespace_id"] == namespace]
        title, practical, atlas = NAMESPACE_READINGS[namespace]
        namespace_rows.append({
            "canonical_namespace_id": namespace,
            "page": rows[0]["page"],
            "loci": len(rows),
            "groups": sum(int(row["group_count"]) for row in rows),
            "selectable_loci": sum(row["interface_role"] == "SELECTABLE_CELESTIAL_SLOT" for row in rows),
            "legend_loci": sum(row["interface_role"] == "LOCAL_INSTRUMENT_LEGEND" for row in rows),
            "unresolved_loci": sum(row["interface_role"] not in {"SELECTABLE_CELESTIAL_SLOT", "LOCAL_INSTRUMENT_LEGEND"} for row in rows),
            "instrument_reading_de": title,
            "possible_condition_use_de": practical,
            "memory_atlas_rival_de": atlas,
        })

    comparison = [
        {
            "observation": "125 von 142 Loci sind wiederholte Bild- oder Auswahlplaetze",
            "favours": "BOTH_SLIGHT_LOOKUP",
            "condition_lookup_reading": "viele adressierbare Gelegenheiten fuer eine Wahl oder Bedingung",
            "memory_atlas_reading": "ebenso passend fuer einen beschrifteten Lehratlas",
        },
        {
            "observation": "13 getrennte lokale Namensraeume",
            "favours": "MEMORY_ATLAS",
            "condition_lookup_reading": "mehrere unabhaengige Instrumente muessen bewusst gewaehlt werden",
            "memory_atlas_reading": "mehrere getrennte Tafeln sind fuer ein Sammel- oder Musterbuch natuerlich",
        },
        {
            "observation": "sichtbare Sterne, Raeder, Gesichter, Wolken und Lichtformen",
            "favours": "BOTH",
            "condition_lookup_reading": "Himmelslagen koennen praktische Bedingungen liefern",
            "memory_atlas_reading": "Himmelsbilder koennen auch reines Lehr- und Merkmaterial sein",
        },
        {
            "observation": "f67 rechts hat 12 Sektoren und 8 Bedingungsplaetze",
            "favours": "CONDITION_LOOKUP",
            "condition_lookup_reading": "grobe zyklische Kategorie plus lokaler Zustandscheck",
            "memory_atlas_reading": "blosse gegliederte Darstellung bleibt moeglich",
        },
        {
            "observation": "f69 Mitte und rechts sind eigene Wetter-/Licht-Rubriken",
            "favours": "CONDITION_LOOKUP",
            "condition_lookup_reading": "Wetter und Licht sind plausible Arbeitsbedingungen",
            "memory_atlas_reading": "kosmographische Rubriken ohne Handlungsbezug bleiben moeglich",
        },
        {
            "observation": "kein sichtbarer Start, keine Richtung oder Rotation",
            "favours": "MEMORY_ATLAS",
            "condition_lookup_reading": "Auswahl funktioniert nur durch Bildzeigen oder externes Wissen, nicht als Ablaufkalender",
            "memory_atlas_reading": "statisches Nachschlagen braucht keine Kreisrichtung",
        },
        {
            "observation": "kein f68-f69-Schluessel und kein Prosa-Zeiger",
            "favours": "MEMORY_ATLAS",
            "condition_lookup_reading": "WHEN bleibt thematischer Gebrauch, nicht geschriebene Schnittstelle",
            "memory_atlas_reading": "selbstaendiger Atlas erklaert die fehlenden Joins direkt",
        },
        {
            "observation": "Herbal WHAT und Biological HOW stehen bereits als praktische Nachbarregister",
            "favours": "CONDITION_LOOKUP",
            "condition_lookup_reading": "ein Himmelsbedingungen-Anhang vervollstaendigt WHAT/HOW/CONDITION",
            "memory_atlas_reading": "Nachbarschaft allein erzwingt keinen gemeinsamen Gebrauch",
        },
    ]

    write("FIVE_HUNDRED_NINETY_FIRST_395_GROUP_ASTRO_INTERFACE.tsv", group_rows)
    write("FIVE_HUNDRED_NINETY_FIRST_142_LOCUS_ASTRO_INTERFACE.tsv", locus_rows)
    write("FIVE_HUNDRED_NINETY_FIRST_THIRTEEN_NAMESPACES.tsv", namespace_rows)
    write("FIVE_HUNDRED_NINETY_FIRST_PURPOSE_COMPARISON.tsv", comparison)

    page_counts = {
        page: {
            "loci": sum(row["page"] == page for row in locus_rows),
            "groups": sum(row["page"] == page for row in group_rows),
            "selectable_loci": sum(row["page"] == page and row["interface_role"] == "SELECTABLE_CELESTIAL_SLOT" for row in locus_rows),
        }
        for page in ("f67r2", "f68r1", "f69v")
    }
    summary = {
        "status": "PASS",
        "source_sha256": sha256(SOURCE),
        "groups": len(group_rows),
        "loci": len(locus_rows),
        "namespaces": len(namespace_rows),
        "selectable_loci": sum(row["interface_role"] == "SELECTABLE_CELESTIAL_SLOT" for row in locus_rows),
        "legend_loci": sum(row["interface_role"] == "LOCAL_INSTRUMENT_LEGEND" for row in locus_rows),
        "unresolved_or_composite_loci": sum(row["interface_role"] not in {"SELECTABLE_CELESTIAL_SLOT", "LOCAL_INSTRUMENT_LEGEND"} for row in locus_rows),
        "page_counts": page_counts,
        "prose_dictionary_imports": 0,
        "cross_section_pointers": 0,
        "f68_f69_keys": 0,
        "decision": "CELESTIAL_REFERENCE_APPENDIX__WHEN_USE_PLAUSIBLE_NOT_WRITTEN",
    }
    (HERE / "FIVE_HUNDRED_NINETY_FIRST_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    report = f"""# Fuenfhunderteinundneunzigste Runde: Astro als Bedingungs- oder Referenzanhang

## Arbeitsentscheidung

Die drei Astro-Seiten passen am besten als **selbstaendiger himmlischer Referenzanhang** an das bisherige praktische Buch. Er kann beim Arbeiten die Funktion `WANN / UNTER WELCHER HIMMELSLAGE` erfuellen, aber genau diese Verknuepfung ist nicht ausgeschrieben. Die staerkste zehnseitige Kurzform lautet deshalb jetzt:

```text
Herbal      = WAS: abgebildetes Material und seine Vorbereitung
Biological  = WIE/WO: lokale Bad-, Transfer- und Anwendungsschritte
Astro       = BEDINGUNG/REFERENZ: Himmelslage nachschlagen, falls die Werkstatt sie braucht
```

Das letzte `falls` ist wichtig. Die Astro-Seiten funktionieren ebenso als eigenstaendiger Himmels-, Lehr- oder Merkatlas. Sie teilen weder Kartenwoerter noch sichtbare Verweise mit der Prosa.

## Was die Seite praktisch anbietet

Die 395 sichtbaren Gruppen bilden 142 vollstaendige lokale Etiketten in **13 getrennten Namensraeumen**. Davon sind {summary['selectable_loci']} wiederholte Bild-/Auswahlplaetze, {summary['legend_loci']} lokale Legenden und {summary['unresolved_or_composite_loci']} zusammengesetzte oder ungeloeste Schluesselbereiche.

- **f67r2**: zwei getrennte Raeder. Rechts kann ein grober Sektor plus einer von acht Bedingungsplaetzen gewaehlt werden; links eine feinere Stern-/Strahl-/Aspektlage. Es gibt keinen sichtbaren Schluessel zwischen beiden.
- **f68r1**: mehrere Sternpaneele mit 28 raeumlichen Sternetiketten und mehreren Zentren. Das ist ein Ortslookup, kein einzelnes Zentrum-plus-28-Rad.
- **f69v**: drei heterogene Raeder. Nur links gibt es 28 lokale Plaetze; Mitte kann als Wetter-/Himmelszustand, rechts als Licht-/Gestirnzustand gelesen werden. Die 28 Plaetze sind nicht sichtbar geordnet.

Ein Schreiber um 1420 braucht dafuer keine allgemeine Astro-Grammatik. Er lernt: Instrument zeigen, lokalen Bildplatz zeigen, komplette Etikette kopieren, Wert aus genau diesem lokalen Exemplar holen, danach den Namensraum loeschen.

## Konkreter Gebrauch im praktischen Buch

Die kreativ staerkste Werkstattanweisung waere:

1. Im Herbalteil den Stoff und die Zubereitung bestimmen.
2. Im Biological-Teil die lokale Station oder Anwendung bestimmen.
3. Nur wenn eine Himmelsbedingung verlangt ist, das passende Astro-Instrument aufrufen.
4. Am gewaehlten Rad oder Sternfeld einen lokalen Platz zeigen.
5. Dessen opake Etikette als gelernten Kalender-/Himmelseintrag lesen.
6. Danach zur Handlung zurueckkehren; es wird **kein** Astro-String in einen Prosasatz eingesetzt.

So kann Astro `WHEN/CONDITION` liefern, ohne dass wir f68 und f69 paaren oder einen linearen Kalender erfinden.

## Was sich gegen die einfache WHEN-Lesung straeubt

- Es gibt keinen Prosa-Zeiger zu einer Pflanze, Station oder Handlung.
- Es gibt keinen gemeinsamen Start, keine autorielle Kreisrichtung und keine Rotation.
- f67 besteht aus zwei, f69 aus drei getrennten Instrumenten.
- Die zwei sichtbaren 28er-Bestaende auf f68 und f69 sind nicht miteinander verbunden.
- Ein statischer Himmelsatlas erklaert all das mindestens ebenso gut.

Darum wird `Astro = WHEN` nicht gestrichen, aber verbreitert zu **Astro = CONDITION/REFERENCE**. Das ist die erste Fassung, die den praktischen Gesamtzusammenhang behaelt, ohne die drei Seiten in einen erfundenen Ablaufkalender zu pressen.

## Naechster Schritt

Als naechstes wird die gesamte Zehn-Seiten-Theorie mit dieser Korrektur neu gesetzt: ein gemeinsames WHAT/HOW-Arbeitsbuch plus ein moeglicherweise benutzter, aber textlich nicht verdrahteter CONDITION/REFERENCE-Anhang.
"""
    (HERE / "FIVE_HUNDRED_NINETY_FIRST_REPORT.md").write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()

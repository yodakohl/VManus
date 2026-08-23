#!/usr/bin/env python3
from pathlib import Path
import csv
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = ROOT / "experiments/yolo/sidequest_semantic_continuous_records_twenty_second_edition/TWENTY_SECOND_11_CONTINUOUS_RECORDS.tsv"
AUDIT = ROOT / "experiments/yolo/sidequest_semantic_noun_load_twenty_sixth_edition/TWENTY_SIXTH_ELEVEN_LEAN_RECORDS.tsv"


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path, fields, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


READINGS = {
    "H1": {
        "title": "Wurzel und erster Auszug",
        "text": "Nimm von der abgebildeten Pflanze die Wurzel und richte daraus einen Ansatz. Trenne einen Teil ab, gib ihn ins Arbeitsgefäß und lasse Wasser zulaufen. Führe den nächsten Teil weiter und stelle ihn auf das vorgeschriebene Maß. Nimm später erneut vom ersten Auszug, erwärme ihn gelinde und halte ihn zum Gebrauch bereit.",
        "bets": "Wurzel; Wasser als nasse AIR-Ausdeutung; Gebrauchszubereitung",
        "withdrawn": "Quellwasser; Glas; innerlicher Gebrauch; Stechen im Leib",
    },
    "H2": {
        "title": "Zwei Pflanzenfraktionen",
        "text": "Nimm eine erste Fraktion der abgebildeten Pflanze, zerkleinere sie und presse sie durch Tuch. Fange den Auszug auf, gib einen Zusatz im vorgeschriebenen Maß hinzu und erwärme gelinde. Nimm eine zweite Fraktion, führe den ersten Ansatz weiter und vereinige beide im gleichen Maß. Rühre sie zu einer weichen Bereitung, verwahre sie bedeckt und gebrauche sie an der bezeichneten Stelle.",
        "bets": "zwei Fraktionen; Tuchpressung; weiche äußere Bereitung",
        "withdrawn": "genaue Blühzeit; Olivenöl; glasiertes Gefäß; Geschwür oder Schwellung",
    },
    "H3": {
        "title": "Auswringen, Stehenlassen und Nachseihen",
        "text": "Nimm ausgewähltes Material der abgebildeten Pflanze und bringe es mit einem Auszugsmedium zur Arbeitsstelle. Wringe es aus, lasse den Auszug bis zum Sollstand stehen und seihe ihn nochmals. Nimm den sichtbaren klaren Anteil und stelle ihn beiseite. Behalte eine zweite Pflanzenportion zurück; gebrauche vom ersten Auszug ein kleines Maß und bereite die zweite Portion erwärmt für eine äußere Stelle.",
        "bets": "zweistufige Filtration; klarer Auszug; getrennte zweite Pflanzenportion",
        "withdrawn": "Frühjahr; Wein; Olivenöl; Gemüt/Brust; Lider/Auge",
    },
    "H4": {
        "title": "Blattansatz und warme zweite Bereitung",
        "text": "Zerkleinere Material der abgebildeten breitblättrigen Pflanze, gib ein Auszugsmedium hinzu und lasse den Ansatz verschlossen stehen. Miss eine Portion ab, wringe sie durch Tuch, lasse sie klar werden und verwahre den Auszug. Wasche damit die bezeichnete äußere Stelle. Führe zurückbehaltenes Pflanzenmaterial mit einem Zusatz als zweite, gelinde erwärmte Bereitung weiter und lege sie an die Stelle.",
        "bets": "breitblättriges Material; Auszug; Tuch; äußere Waschung und warme Bereitung",
        "withdrawn": "Weißwein; Leinwand; unreine Wunde; Honig",
    },
    "H5": {
        "title": "Kurze Auflage und getrennte Auszugsportion",
        "text": "Nimm Material der abgebildeten Pflanze und setze eine kleine Portion kurz an der bezeichneten äußeren Stelle ein. Nimm sie wieder ab, wasche die Stelle und wiederhole den Gang nur, wenn er passend bleibt. Trockne das übrige Pflanzenmaterial, bereite daraus einen milden Auszug, seihe ihn, gib einen Zusatz hinzu und gebrauche ein kleines Maß als getrennte zweite Zubereitung.",
        "bets": "kurze äußere Auflage; Nachwäsche; zweite milde Auszugsportion",
        "withdrawn": "Feuchtstandort; Warze/Hühnerauge; Schatten; Wein; Honig; Husten",
    },
    "B1": {
        "title": "Gemeinsames Beckenprogramm",
        "text": "Richte am gemeinsamen zweireihigen Figurenbecken eine bemessene Waschcharge ein. Führe sie durch die örtlichen Läufe, gib Portion und Zusatz zum Ziel, halte länger, übertrage und schließe. Setze nacheinander kurze Wasch-, Wärme-, Ruhe-, Durchlauf- und Abführgänge. Sammle den nutzbaren Anteil, reinige Becken und Leitung und führe die Restflüssigkeit über den unteren Ablauf ab.",
        "bets": "Figurenbad; bemessene Waschcharge; lokale Läufe und unterer Ablauf",
        "withdrawn": "bestimmte Krankheit; globaler geschlossener Wasserkreislauf",
    },
    "B2": {
        "title": "Obere Paarbecken, Mittelknoten und unteres Feld",
        "text": "Beginne an den oberen Paarbecken mit Spülen, Bemessen, Temperieren, Durchleiten und Abführen. Wechsle am sichtbaren Mittelknoten zu einer neuen örtlichen Mischung, lasse sie stehen, halte sie warm und prüfe den sichtbaren Zustand. Beim Wechsel ins untere Mehrfigurenfeld beginne eine neue Charge: führe ab, gleiche kurze und längere Gänge aus, wasche, setze einen Tuch- oder Einsatzgang und schließe am unteren Beckenrand.",
        "bets": "lokale Bade-/Waschstationen; Tuchgang; neue Charge nach Besitzerwechsel",
        "withdrawn": "ein einziger Apparat; feste Flussrichtung; bestimmte Körperbehandlung",
    },
    "B3": {
        "title": "Randstationen und Hauptpaar",
        "text": "Arbeite nacheinander an der oberen Fächerstation, dem runden Gefäß, dem korbartigen Empfänger und den unklaren Zwischenposten. Bemesse, übertrage, wärme, lasse stehen, sammle, wasche und führe ab; beginne bei jedem sichtbaren Besitzerwechsel den Gegenstandsbezug neu. Am verbundenen Hauptpaar führe einen längeren Einsatzgang aus, leite den nächsten Anteil weiter, gleiche die Portionen ab und beende den Posten am unteren Ziel.",
        "bets": "mehrere getrennte Stationsvignetten; lokaler Einsatzgang am sichtbaren Hauptpaar",
        "withdrawn": "globaler Kreislauf; sichere Richtung in den Zwischenposten; bestimmte Therapie",
    },
    "B4": {
        "title": "Einsatz, Tuch und Unterläufe",
        "text": "Am sichtbaren Hauptpaar setze den aktuellen Einsatz länger an, führe ihn weiter, befestige ihn und schließe. Übertrage dann eine bemessene Portion durch Tuch, halte sie warm und führe sie ab. Wechsle zur linken Unterlaufstation für einen kurzen Wärme-, Misch- und Waschgang. Nach dem sichtbaren Wechsel zum rechten S-Lauf leite den klaren Anteil zum Ziel, sammle kurz und führe den Rest ab.",
        "bets": "Tuch- oder Einsetzanwendung; Wärme; zwei getrennte Unterlaufstationen",
        "withdrawn": "sichere Wund-/Hautbehandlung; ein durchgängiger Anlagenfluss",
    },
    "B5": {
        "title": "Linker Fransen-Endposten",
        "text": "Nimm am linken Fransen-Endposten den nächsten Arbeitsanteil auf, setze ihn an und übertrage ihn. Lasse ihn an der örtlichen Zielstelle stehen, führe den vorherigen Gang fort, bemesse die nächste Öffnungsstufe und übertrage den aktuellen Posten zum Ziel.",
        "bets": "lokaler Endposten; Folgeanteil; Ziel und Öffnungsstufe",
        "withdrawn": "bestimmte Flüssigkeit oder Körperstelle",
    },
    "B6": {
        "title": "Rechter S-Lauf-Endposten",
        "text": "Sammle am rechten S-Lauf den längeren Arbeitsanteil. Bearbeite den aktuellen Posten kurz, bringe ihn zur bezeichneten Stelle, führe ihn nach Sollmaß weiter und leite ihn mit dem Tuchposten zum Endziel.",
        "bets": "lokaler S-Lauf; Tuchposten; bemessener Endtransfer",
        "withdrawn": "bestimmte Substanz oder medizinischer Zweck",
    },
}

base = {row["record_id"]: row for row in read(BASE)}
audit = {row["record_id"]: row for row in read(AUDIT)}
rows = []
for record_id in ("H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"):
    source = base[record_id]
    revision = READINGS[record_id]
    rows.append(
        {
            "record_id": record_id,
            "page": source["page"],
            "title_de": revision["title"],
            "statement_count": source["statement_count"],
            "group_count": source["group_count"],
            "statement_ids": source["statement_ids"],
            "image_owner_chain": source["image_owner_chain"],
            "balanced_continuous_reading_de": revision["text"],
            "retained_creative_bets": revision["bets"],
            "withdrawn_overdetail": revision["withdrawn"],
            "lean_clause_baseline_de": audit[record_id]["lean_record_reading_de"],
            "technical_rival_de": source["continuous_technical_rival_de"],
        }
    )
write(HERE / "TWENTY_SEVENTH_11_BALANCED_RECORDS.tsv", list(rows[0]), rows)

doc = [
    "# Ausgewogene fortlaufende Übersetzung der elf Prosa-Records",
    "",
    "Diese Fassung steht zwischen dem nackten Klauselgerüst und der reichen",
    "medizinischen Erzählung. Sie behält konkrete, wiederkehrende Werkstattobjekte",
    "wie Wurzel, Wasserlauf, Tuch, Auszug, Becken und sichtbare Station, streicht",
    "aber austauschbare Krankheiten, genaue Medien und unnötig genaue Geräte.",
    "",
]
for row in rows:
    doc.extend(
        [
            f"## {row['record_id']} — {row['title_de']} ({row['page']})",
            "",
            row["balanced_continuous_reading_de"],
            "",
            f"Bewusst behalten: {row['retained_creative_bets']}.",
            "",
            f"Zurückgenommen: {row['withdrawn_overdetail']}.",
            "",
            f"Technischer Rivale: {row['technical_rival_de']}",
            "",
        ]
    )
(HERE / "TWENTY_SEVENTH_BALANCED_CONTINUOUS_EDITION.md").write_text("\n".join(doc).rstrip() + "\n", encoding="utf-8")

summary = {
    "status": "PASS",
    "counts": {
        "records": len(rows),
        "statements": sum(int(row["statement_count"]) for row in rows),
        "groups": sum(int(row["group_count"]) for row in rows),
        "herbal_records": sum(row["record_id"].startswith("H") for row in rows),
        "biological_records": sum(row["record_id"].startswith("B") for row in rows),
    },
}
(HERE / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(summary, ensure_ascii=False, indent=2))

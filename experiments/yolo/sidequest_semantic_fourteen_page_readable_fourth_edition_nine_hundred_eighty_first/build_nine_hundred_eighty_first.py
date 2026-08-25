#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P974 = ROOT / "experiments/yolo/sidequest_semantic_image_owned_fourteen_page_edition_nine_hundred_seventy_fourth"
P980 = ROOT / "experiments/yolo/sidequest_semantic_158_unit_image_owned_codebook_nine_hundred_eightieth"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


READINGS = {
    "f10r": (
        "Von der doppelten Speicherwurzel einen Teil nehmen, in das Gefäß geben und mit Arbeitsflüssigkeit ansetzen. "
        "Den ersten Zug auffangen, weiterbearbeiten und nach Sollmaß schließen. Danach einen weiteren Wurzel-, Blatt- "
        "oder Kopfanteil nehmen, anwärmen, pressen und im Topf als zweite Charge weiterführen; diese Fortsetzung bleibt offen."
    ),
    "f11r": (
        "Vom blühenden dreikronigen Soden das Blütenkraut nehmen und einen Sudansatz bilden. Auswringen, die vorgeschriebene "
        "Stehzeit abwarten, nachseihen, den Klarlauf abnehmen und kalt stellen. Einen weiteren Blütenanteil zurücklegen; vom "
        "vorigen Ansatz die nächste Portion als Trank oder Gebrauchsauszug auf Sollmaß bringen."
    ),
    "f13r": (
        "Die große Wurzelkrone aktivieren. Einen ersten Wurzelteil und ein Brutknöllchen in den Ansatz geben, Teilmengen nach "
        "Sollmaß zufügen und den Blütenanteil mitführen; weiter auspressen und schließen. Danach Restwurzel durch den Durchlass "
        "führen, einen Blattanteil in den Folgeansatz geben, kurz halten und zur Zielstelle bringen. Einen letzten Pflanzenteil "
        "zugeben; die Fortsetzung bleibt offen."
    ),
    "f55v": (
        "Von der großen Doldenpflanze den Wurzelstock ansetzen. Die Sollmenge in Portionen teilen, abkühlen und verwahren. "
        "Weitere Blatt- und Doldenanteile zugeben, einzelne Züge anwärmen, zwischen Gefäßstellen versetzen und durch den "
        "Durchlass führen. Vier kleine Teilgänge schließen; der Hauptansatz läuft weiter."
    ),
    "f56r": (
        "Stängel und den jeweils gezeigten Knospen-, Blüten- oder reifen Kopfanteil getrennt nehmen. Den Stängel zerreiben, "
        "den Auszug einsetzen und abseihen. Einen Anteil auflegen oder an der bezeichneten Stelle auftragen, den nächsten "
        "Reifeanteil nach Sollmaß zugeben und die Gabe zur folgenden Anwendung weiterführen."
    ),
    "f88r": (
        "Die Seite enthält drei Chargenfächer. Oben sechs Drogenposten wählen, Sollmengen in das obere Gefäß geben und den "
        "Auszug weiterleiten. In der Mitte sechs neue Posten als zweiten Ansatz zugeben, länger halten und schließen. Unten "
        "vier Posten in der letzten Gefäßcharge ansetzen, nach Sollmaß fortführen, den Auszug leiten und den letzten Teilgang schließen."
    ),
    "f75r": (
        "Jede sichtbare Figur-, Becken- oder Rinnenstation einzeln bedienen: Posten an der Quellstelle einsetzen, eine Teilmenge "
        "zugeben, kurz oder länger halten, über den örtlichen Durchlass umsetzen, am Ziel neu ansetzen und die kleine Zelle "
        "schließen. Die dreieckige Insel bildet einen eigenen Stationsbesitzer; sie ist kein Anschluss eines weltweiten Kreislaufs."
    ),
    "f81v": (
        "Im gemeinsamen zweireihigen Badfeld eine Portion ansetzen, Zusatz und Arbeitsflüssigkeit nach Maß zugeben, kurz oder "
        "länger halten und durch den nächsten lokalen Lauf führen. Becken füllen, einzelne Züge schwenken oder einreiben, am "
        "Hahn weitergeben, in der Auffangschale sammeln und nach dem Absetzen schließen."
    ),
    "f82r": (
        "An der oberen Paarbeckenstation den Posten am Ziel ansetzen, durch das Seihtuch führen, beide Seiten angleichen und "
        "über den Überlauf weitergeben. An der mittleren Station Frischwasser zugeben und den Klarlauf zur Düse führen. In den "
        "unteren Bildern teilen, auf Sollmaß bringen, mit Warmwasser waschen, auffangen oder zum Bodenablauf führen."
    ),
    "f83r": (
        "Die Seite sammelt Anwendungsvarianten. Ansatz aufstreichen, im Becken länger und dann kurz einwirken lassen, eine "
        "Tuchauflage befestigen oder nachwaschen. Klarlauf und weitere Portionen durch lokale Überläufe, Seitenarme und "
        "Auffangstellen führen; jede sichtbare Verbindung gilt nur für ihr Bildpaar, nicht als ein einziger Kreislauf."
    ),
    "f67r2": (
        "Im ersten Himmelsrad einen Platz und seinen Wert wählen, im zweiten Rad einen getrennten Platz bestimmen und in der "
        "zugehörigen Tabelle Grad oder Arbeitsklasse nachschlagen. Die Einträge geben Auswahl- und Einstellwerte; die zwei "
        "Räder bleiben getrennte Instrumente."
    ),
    "f68r1": (
        "Eine Sternstelle im passenden Paneel wählen, ihren lokalen Eintrag lesen und Wert, Grad oder Klasse zuordnen. Die "
        "mehreren Zentren werden nicht zu einem einzigen Umlauf verbunden; weder Startpunkt noch Drehrichtung werden vorausgesetzt."
    ),
    "f69v": (
        "Im linken Rad einen der achtundzwanzig Plätze wählen und lokal kennzeichnen. Die beiden anderen Räder besitzen eigene "
        "Namen und Klassen. Zwischen den drei Verzeichnissen wird nicht automatisch weitergezählt; jedes wird für sich benutzt."
    ),
    "f70v": (
        "Im Widderring Reihe, Klasse, Platz und Grad wählen; der sichtbare LAUF ist hier ein Ringlauf. Im Fischring Haupt- und "
        "Unterplätze des Fischpaars bestimmen und den zugehörigen Wert eintragen. Beide Tafeln sind Himmelsadressen, keine Flüssigkeitsrezepte."
    ),
}


def main() -> None:
    source = read(P974 / "PASS974_14_PAGE_IMAGE_OWNED_EDITION.tsv")
    bindings = read(P980 / "PASS980_2511_EVENT_TEACHING_BINDING.tsv")
    layer_by_page = {}
    for page in READINGS:
        page_rows = [r for r in bindings if r["physical_page"] == page]
        counts = {}
        for row in page_rows:
            counts[row["primary_layer"]] = counts.get(row["primary_layer"], 0) + 1
        layer_by_page[page] = counts
    rows = []
    for row in source:
        page = row["physical_page"]
        rows.append({
            "physical_page": page,
            "book_stage": row["book_stage"],
            "unit_role_de": row["unit_role_de"],
            "visible_owner_or_namespace_de": row["visible_owner_or_namespace_de"],
            "events": row["events"],
            "prose_clauses": row["prose_clauses"],
            "local_address_events": row["local_address_events"],
            "primary_layer_counts": "|".join(f"{key}:{value}" for key, value in sorted(layer_by_page[page].items())),
            "complete_working_translation_de": READINGS[page],
        })
    write(HERE / "PASS981_FOURTEEN_PAGE_READABLE_EDITION.tsv", rows, list(rows[0]))

    order = ["I_STOFF", "II_ZUBEREITUNG", "III_ANWENDUNG", "IV_ZEIT_UND_AUSWAHL"]
    titles = {
        "I_STOFF": "I — Stoff und Pflanzenteil wählen",
        "II_ZUBEREITUNG": "II — Drogenposten im Gefäß ansetzen",
        "III_ANWENDUNG": "III — Bad, Auflage oder Station bedienen",
        "IV_ZEIT_UND_AUSWAHL": "IV — Himmelsplatz, Klasse oder Grad nachschlagen",
    }
    lines = [
        "# Pass 981 — lesbare vierte Arbeitsausgabe der vierzehn Seiten",
        "",
        "## Das Buch in einem Satz",
        "",
        "> Bildstoff wählen → im Gefäß zubereiten → an Bad/Station anwenden →",
        "> Himmelsplatz oder Arbeitsklasse auf der eigenen Tafel nachschlagen.",
        "",
        "Die folgenden Absätze sind die derzeit flüssigste Werkstattlektüre. Sie",
        "benutzen das 158-Einheiten-Codebuch und lassen Bildetiketten als gelernte",
        "Namen stehen, statt sie gewaltsam in Wurzeln zu zerlegen.",
        "",
    ]
    for stage in order:
        lines += [f"## {titles[stage]}", ""]
        for row in [r for r in rows if r["book_stage"] == stage]:
            lines += [
                f"### {row['physical_page']} — {row['visible_owner_or_namespace_de']}",
                "",
                row["complete_working_translation_de"],
                "",
            ]
    lines += [
        "## Der stärkste einzelne Übersetzungsauszug",
        "",
        "`tshol schoal cfhy shfydaiin cphy shey tchody`",
        "",
        "> Vom Blütenkraut einen Sudansatz bilden, auswringen, die vorgeschriebene",
        "> Stehzeit abwarten, nachseihen, den Klarlauf abnehmen und kalt stellen; Schluss.",
        "",
        "Hier ist `shey` nur KLARLAUF. Die übrigen Bedeutungen stehen in den",
        "Nachbarkarten; keine einzelne Karte muss einen ganzen Satz bedeuten.",
        "",
    ]
    (HERE / "PASS981_COMPLETE_READABLE_FOURTH_EDITION.md").write_text("\n".join(lines), encoding="utf-8")
    summary = {
        "status": "PASS",
        "pages": len(rows),
        "events": sum(int(r["events"]) for r in rows),
        "stages": {stage: sum(r["book_stage"] == stage for r in rows) for stage in order},
    }
    (HERE / "PASS981_BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

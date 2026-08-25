#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
PAGES = ROOT / "experiments/yolo/sidequest_semantic_three_layer_codebook_nine_hundred_forty_sixth/PASS946_14_PAGE_LAYER_COUNTS.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


UNIT_MAP = {
    "f10r": ("I_STOFF", "Pflanzenartikel A", "Gezeichnetes Kraut auswählen, Teile entnehmen und bis zur Brauchbarkeit verarbeiten"),
    "f11r": ("I_STOFF", "Pflanzenartikel B", "Pflanzenteil halten, Portion abtrennen und in einen zweiten Zug überführen"),
    "f13r": ("I_STOFF", "Pflanzenartikel C", "Fünf kurze Zubereitungsgänge für den gezeichneten Stoff"),
    "f55v": ("I_STOFF", "Pflanzenartikel D", "Mehrere Stoffportionen ansetzen, versetzen und durch einen Durchlass geben"),
    "f56r": ("I_STOFF", "Pflanzenartikel E", "Wiederholt kleine Anteile entnehmen und stufenweise neu ansetzen"),
    "f88r": ("II_ZUBEREITUNG", "Gefäß- und Zutatenregister", "Drei Gefäße mit drei lokalen Zutatenlisten und drei Zubereitungsblöcken"),
    "f75r": ("III_ANWENDUNG", "großes Bad-/Stationsblatt", "Viele örtliche Kurzaufträge an Figuren, Becken und grünen Stationen"),
    "f81v": ("III_ANWENDUNG", "gemeinsames Badfeld", "Posten zugeben, halten, über eine Verbindung weiterführen und neu ansetzen"),
    "f82r": ("III_ANWENDUNG", "mehrere Bad- und Leitungsstationen", "Lokal wählen, ansetzen, markieren, durch Anschluss führen und auffangen"),
    "f83r": ("III_ANWENDUNG", "Variantenatlas der Stationen", "Viele örtliche Ausführungsvarianten ohne einen einzigen Gesamtkreislauf"),
    "f67r2": ("IV_ZEIT_UND_AUSWAHL", "zwei Himmelsräder und Tabelle", "Ring- oder Tabellenposten auswählen und einer Stelle oder Stufe zuordnen"),
    "f68r1": ("IV_ZEIT_UND_AUSWAHL", "mehrteilige Sternstellentafel", "Lokalen Eintrag einer markierten Sternstelle zuordnen"),
    "f69v": ("IV_ZEIT_UND_AUSWAHL", "drei getrennte Himmelsverzeichnisse", "Örtliche Himmelsplätze nach Klasse und Wert nachschlagen"),
    "f70v": ("IV_ZEIT_UND_AUSWAHL", "Widder- und Fischring", "Figurenplatz nach Reihe, Grad, Quelle und Ziel aufsuchen"),
}

STAGES = [
    ("I_STOFF", "WAS", "Bild zeigt den einfachen Stoff; Text wählt Teil, Portion, Sollmaß und ersten Zubereitungsgang.", "f10r|f11r|f13r|f55v|f56r"),
    ("II_ZUBEREITUNG", "WORAUS UND WORIN", "Lokale Wurzel-/Blattnamen werden drei Gefäßen und drei kompakten Ansatzfolgen zugeordnet.", "f88r"),
    ("III_ANWENDUNG", "WIE UND WO", "Figuren, Becken und Anschlüsse liefern den lokalen Besitzer; Text gibt Ansatz, Haltegrad, Wechsel und Ende.", "f75r|f81v|f82r|f83r"),
    ("IV_ZEIT_UND_AUSWAHL", "WANN ODER UNTER WELCHER KONSTELLATION", "Getrennte Himmelsräder liefern Auswahl-, Stellen-, Grad- und Wertadressen, nicht dieselbe Werkstattprosa.", "f67r2|f68r1|f69v|f70v"),
]


def main() -> None:
    pages = read_tsv(PAGES)
    rows: list[dict[str, object]] = []
    for page in pages:
        stage, role, concrete = UNIT_MAP[page["physical_page"]]
        rows.append({
            "physical_page": page["physical_page"],
            "book_stage": stage,
            "unit_role_de": role,
            "concrete_function_de": concrete,
            "events": page["events"],
            "productive_compositions": page["productive_compositions"],
            "learned_formula_cards": page["learned_formula_cards"],
            "local_nomenclator_or_addresses": page["local_nomenclator_or_addresses"],
            "page_reading_de": page["current_page_reading_de"],
        })
    write_tsv(OUT / "PASS947_14_UNIT_BOOK_MAP.tsv", rows, list(rows[0]))

    stage_rows = [
        {"book_stage": stage, "question_de": question, "function_de": function, "pages": pages}
        for stage, question, function, pages in STAGES
    ]
    write_tsv(OUT / "PASS947_4_STAGE_WORKFLOW.tsv", stage_rows, list(stage_rows[0]))

    theory = [
        "# Arbeitsbuch der einfachen Stoffe, Zubereitungen, Bäder und Himmelszeiten",
        "",
        "## Beste derzeitige Gesamtlesung",
        "",
        "Ein möglicher Werkstatttitel wäre *Liber simplicium, compositionum, balneorum et temporum caelestium*: ein bildgeführtes praktisches Kompendium, das nicht jedes Sachwort ausschreibt, sondern Bildbesitzer, lokale Namen, gelernte Arbeitsformeln und produktive Kürzel verbindet.",
        "",
        "Die vier Abteilungen beantworten eine einfache Arbeitsfolge:",
        "",
        "1. **Was?** — Welcher einfache Pflanzenstoff und welcher Teil davon?",
        "2. **Woraus und worin?** — Welche Zutaten kommen in welchen Ansatz oder welches Gefäß?",
        "3. **Wie und wo?** — An welcher Bade-, Körper- oder Leitungsstation wird der Posten angesetzt, gehalten, umgesetzt oder abgesetzt?",
        "4. **Wann/unter welchem Himmel?** — Welcher Ringplatz, Grad oder Sternort wird für den betreffenden Eintrag nachgeschlagen?",
        "",
        "Es braucht keine sichtbaren Querverweise zwischen den Seiten. Die Werkstatt verbindet die Abteilungen durch denselben kleinen Kartenapparat und durch die Reihenfolge des praktischen Wissens.",
        "",
        "## Die vierzehn Einheiten",
        "",
    ]
    for row in rows:
        theory.extend([f"### {row['physical_page']} — {row['unit_role_de']}", "", f"{row['concrete_function_de']}. {row['page_reading_de']}", ""])
    theory.extend([
        "## Konkrete Werkstattgeschichte",
        "",
        "Der Meister zeichnet oder übernimmt zuerst die Pflanzen, Gefäße, Badstationen und Räder. Danach setzt der Schreiber neben jeden Besitzer die örtlichen Nomenklatorkarten und füllt die Prosa aus 47 vertrauten Formeln sowie selteneren Kürzelkompositionen. Ein zweiter Schreiber kann dieselben Formeln anders ansetzen oder mit q/s/ch/d einleiten, ohne ein neues Wort zu schaffen.",
        "",
        "Die medizinische Lesung ist damit nicht auf einzelne erfundene Krankheitsnamen angewiesen. Ihr Kern ist praktisch: Stoff auswählen, Ansatz bilden, Menge und Ziel festlegen, lokal anwenden, Zustand/Grad beachten und den passenden Himmelseintrag konsultieren.",
    ])
    (OUT / "PASS947_COMPLETE_WORKING_THEORY.md").write_text("\n".join(theory) + "\n", encoding="utf-8")

    report = """# Pass 947 — die Buchfunktion schließt sich

Die 14 Seiten lassen sich jetzt als vierteiliger Arbeitsweg lesen:

`PFLANZENSTOFF → GEFÄSSZUBEREITUNG → BAD/ANWENDUNG → HIMMELSAUSWAHL`.

f88r ist das fehlende Gelenk. Seine drei Gefäße und Zutatenreihen machen aus den
fünf Pflanzenartikeln einen Vorrat für konkrete Zubereitungen; die Biological-
Seiten zeigen örtliche Anwendung und Stationsbetrieb; die Himmelsräder liefern
getrennte Auswahl- und Stellenregister. Das gemeinsame Codebuch verbindet die
Abteilungen, ohne dass eine Seite die andere wörtlich zitieren muss.

Der stärkste kreative Arbeitstitel lautet: **Arbeitsbuch der einfachen Stoffe,
Zubereitungen, Bäder und Himmelszeiten.**
"""
    (OUT / "PASS947_REPORT.md").write_text(report, encoding="utf-8")
    summary = {"units": len(rows), "events": sum(int(row["events"]) for row in rows), "stages": len(stage_rows), "outputs": {}}
    for path in sorted(OUT.glob("PASS947_*")):
        summary["outputs"][path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    (OUT / "PASS947_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

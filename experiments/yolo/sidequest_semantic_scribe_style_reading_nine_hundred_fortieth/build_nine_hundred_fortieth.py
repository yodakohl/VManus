#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
PHASES = ROOT / "experiments/yolo/sidequest_semantic_complete_process_maps_nine_hundred_twenty_sixth/PASS926_1435_PHASE_ASSIGNMENTS.tsv"
CLAUSES = ROOT / "experiments/yolo/sidequest_semantic_macro_clause_translation_nine_hundred_thirty_seventh/PASS937_354_MACRO_CLAUSE_TRANSLATIONS.tsv"
PAGES = ROOT / "experiments/yolo/sidequest_semantic_integrated_fourteen_page_edition_nine_hundred_thirty_ninth/PASS939_14_PAGE_SUMMARY.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


WORDS = {
    "OK": "ansetzen",
    "O": "bearbeiten",
    "SH": "halten",
    "CH": "entnehmen",
    "CHD": "umsetzen",
    "K": "zugeben",
    "S": "auswählen",
    "T": "einstellen",
    "SHED": "absetzen lassen",
    "R": "markieren",
    "P": "einsetzen",
    "CTH": "bis bereit führen",
    "CHK": "behandeln",
    "SOLK": "auffangen",
    "LSH": "spülen",
    "CPH": "umleiten",
    "CFH": "trennen",
}

MACROS = [
    (("SH", "OK", "SH", "OK"), "halten, neu ansetzen, wieder halten und erneut ansetzen"),
    (("CH", "O", "CTH", "O"), "entnehmen und bis zur Bereitschaft bearbeiten"),
    (("OK", "OK", "OK"), "in drei Stufen ansetzen"),
    (("CHD", "OK", "CHD"), "umsetzen, am neuen Ort ansetzen und weiter umsetzen"),
    (("CH", "O", "CTH"), "entnehmen, bearbeiten und bis bereit führen"),
    (("O", "CH", "O"), "bearbeiten, einen Teil entnehmen und weiterbearbeiten"),
    (("T", "CH", "O"), "einstellen, entnehmen und bearbeiten"),
    (("CHD", "OK"), "umsetzen und dort ansetzen"),
    (("SH", "K"), "halten und anschließend zugeben"),
    (("K", "CH"), "zugeben und einen Anteil entnehmen"),
    (("CH", "O"), "entnehmen und bearbeiten"),
    (("O", "S"), "bearbeiten und den nächsten Posten auswählen"),
    (("S", "OK"), "auswählen und ansetzen"),
    (("OK", "K"), "ansetzen und zugeben"),
    (("SH", "O"), "halten und bearbeiten"),
    (("OK", "CH"), "ansetzen und entnehmen"),
    (("O", "CTH"), "bis zur Bereitschaft bearbeiten"),
    (("P", "CH"), "einsetzen und entnehmen"),
]

PHASE_OPENERS = {
    "SELECT": "Auswahl — ",
    "PREPARE": "Vorbereitung — ",
    "EXECUTE": "Arbeitsgang — ",
    "CONDITION": "Zustand — ",
    "TRANSFER": "Weitergabe — ",
    "CONTEXT": "Örtlicher Bezug — ",
}


def parse_codes(text: str) -> list[str]:
    if not text or text == "NONE":
        return []
    return [part.strip() for part in text.replace("|", ">").split(">") if part.strip() and part.strip() != "NONE"]


def speak_codes(codes: list[str]) -> str:
    if not codes:
        return "mit dem angegebenen Posten weiterarbeiten"
    chunks: list[str] = []
    pos = 0
    while pos < len(codes):
        matched = False
        for pattern, phrase in MACROS:
            n = len(pattern)
            if tuple(codes[pos:pos + n]) == pattern:
                chunks.append(phrase)
                pos += n
                matched = True
                break
        if matched:
            continue
        run = 1
        while pos + run < len(codes) and codes[pos + run] == codes[pos]:
            run += 1
        word = WORDS[codes[pos]]
        if run == 2:
            chunks.append(f"zweimal {word}")
        elif run == 3:
            chunks.append(f"dreimal {word}")
        elif run > 3:
            chunks.append(f"{run}-mal {word}")
        else:
            chunks.append(word)
        pos += run
    if len(chunks) == 1:
        return chunks[0]
    return ", ".join(chunks[:-1]) + " und " + chunks[-1]


def polished_clause(clause: dict[str, str], phase_rows: list[dict[str, str]]) -> tuple[str, int, str]:
    blocks: list[tuple[str, list[str]]] = []
    for row in phase_rows:
        phase = row["phase"]
        codes = parse_codes(row["minimal_verb_sequence"])
        if blocks and blocks[-1][0] == phase:
            blocks[-1][1].extend(codes)
        else:
            blocks.append((phase, list(codes)))
    sentences: list[str] = []
    for phase, codes in blocks:
        body = speak_codes(codes)
        opener = PHASE_OPENERS[phase]
        sentence = opener + body
        sentences.append(sentence[0].upper() + sentence[1:] + ".")
    end = clause["end_reason"]
    if end == "LICENSED_DY_CLOSE":
        sentences.append("Damit ist dieser Arbeitszug beendet.")
    elif end == "PAGE_END_OPEN":
        sentences.append("Der Arbeitszug wird im nächsten Eintrag fortgesetzt.")
    return " ".join(sentences), len(blocks), ">".join(phase for phase, _ in blocks)


SCRIBE_READINGS = {
    "f10r": "Vom gezeichneten Kraut zuerst den bezeichneten Teil nehmen, in den Ansatz setzen und kurz halten. Bis zur Brauchbarkeit durcharbeiten und durch den vorgesehenen Durchlass führen. Für den zweiten Ansatz weitere Portionen nach Sollmaß entnehmen, nacheinander zugeben, den Auszug prüfen und die Arbeit für den folgenden Eintrag offenlassen.",
    "f11r": "Den ausgewählten Pflanzenteil im Ansatz halten, bearbeiten und die brauchbare Portion abtrennen. Für den zweiten Zug weitere Teile abmessen und zugeben; den Ansatz weiterführen, nochmals halten und die Fortsetzung nicht abschließen.",
    "f13r": "Fünf kleine Arbeitsgänge zum gezeichneten Kraut: Stoff einsetzen, Anteil entnehmen, nach Maß zugeben, kurz halten und durch den bezeichneten Gang führen. Vier Gänge werden beendet; der letzte Zusatz bleibt für den nächsten Arbeitsschritt bereit.",
    "f55v": "Die Pflanzenzubereitung portionsweise ansetzen. Bestandteile nach Maß zugeben, zwischen den bezeichneten Stellen umsetzen und zwischendurch kleine Proben entnehmen. Einzelne Portionen durch den Durchlass führen; vier Nebenarbeiten schließen, während der Hauptansatz weitergeführt wird.",
    "f56r": "Aus dem gezeichneten Stoff wiederholt kleine Anteile nehmen und in mehreren Stufen neu ansetzen. Weitere Anteile zugeben, die einzelnen Züge halten und prüfen und das Arbeitsgut zur nächsten Stelle bringen. Zwei Gänge enden; der letzte bleibt zur anschließenden Verwendung offen.",
    "f75r": "Jede kleine Zelle ist ein eigener Stationsauftrag: Posten ansetzen, kurz oder länger halten, zur nächsten Stelle bringen, dort neu ansetzen und beenden. Je nach Bild werden Teile entnommen, zugegeben, aufgefangen oder abgesetzt; die sieben Bildnamen ordnen die betreffenden Becken und Figurenplätze.",
    "f81v": "Am gemeinsamen Badfeld jeden Posten ansetzen, die bezeichnete Menge zugeben und für die notierte Stufe halten. Danach über die nächste Verbindung weiterführen, an der Folgestelle neu ansetzen und gegebenenfalls absetzen. Die beiden Bildkarten nennen nächste Einheit und Fortsetzung am Ziel.",
    "f82r": "Die dargestellten Stationen nacheinander, aber jeweils örtlich, bedienen: Posten wählen, ansetzen, Zustand markieren und durch Anschluss oder Durchlass weiterführen. Nach Zeichnung zugeben, halten, umsetzen und einzelne Ausgänge auffangen. Die dreizehn Beschriftungen liefern Quelle, Ziel, Unterplatz, Lauf, Stufe und Sollwert.",
    "f83r": "Ein Variantenbuch für örtliche Stationen: auswählen, ansetzen, halten, zur verbundenen Stelle umsetzen, dort erneut ansetzen und anschließend absetzen oder auffangen. Jede sichtbare Beckenverbindung besitzt ihren eigenen Arbeitszug; zusammen bilden sie keinen geschlossenen Kreislauf.",
    "f67r2": "In den beiden Rädern den bezeichneten Tabellenposten auswählen, seinen eingetragenen Arbeitswert ausführen und zur zugeordneten Stelle oder Stufe wechseln. Die kurzen Blöcke sind Nachschlageeinträge; sie werden nicht als fortlaufendes Rezept gelesen.",
    "f68r1": "In mehreren Sternfeldern jeweils den bezeichneten Eintrag wählen, die örtliche Anweisung ausführen und ihn der markierten Sternstelle zuordnen. Weder ein gemeinsames Zentrum noch eine feste Umlaufrichtung wird verlangt.",
    "f69v": "Drei getrennte Himmelsverzeichnisse: links achtundzwanzig örtliche Plätze, daneben zwei anders gegliederte Räder. Jeder Platz trägt seine eigene Klasse, Stelle oder Wertangabe; die drei Verzeichnisse werden nicht zu einer einzigen Folge verbunden.",
    "f70v": "Im Widderrad und im Fischring die Figuren nach Reihe, Klasse, Ringplatz, Grad sowie Quell- oder Zielstelle aufsuchen. Der Lauf bezeichnet hier den Weg im Ring. Die Einträge sind Bildadressen und Wertangaben, keine Pflanzen- oder Badehandlungen.",
    "f88r": "Aus den gezeichneten Vorrats- und Zutatenposten den benötigten Anteil wählen, die Zubereitung ansetzen und weitere Bestandteile zugeben. Den Ansatz halten, prüfen und auf die bezeichneten Gefäße oder Stellen verteilen; einzelne Portionen durch einen Durchlass führen.",
}


def main() -> None:
    phase_rows = read_tsv(PHASES)
    clauses = read_tsv(CLAUSES)
    pages = read_tsv(PAGES)
    by_clause: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in phase_rows:
        by_clause[row["clause_id"]].append(row)

    polished: list[dict[str, object]] = []
    for clause in clauses:
        text, blocks, phases = polished_clause(clause, by_clause[clause["clause_id"]])
        polished.append({
            "clause_id": clause["clause_id"],
            "physical_page": clause["physical_page"],
            "register": clause["register"],
            "start_event": clause["start_event"],
            "end_event": clause["end_event"],
            "events": clause["events"],
            "phase_blocks": blocks,
            "phase_sequence": phases,
            "end_reason": clause["end_reason"],
            "scribe_style_translation_de": text,
        })
    write_tsv(OUT / "PASS940_354_SCRIBE_STYLE_CLAUSES.tsv", polished, list(polished[0]))

    page_rows: list[dict[str, object]] = []
    for row in pages:
        page_rows.append({
            "physical_page": row["physical_page"],
            "page_model": row["page_model"],
            "events": row["events"],
            "prose_clauses": row["prose_clauses"],
            "scribe_style_page_reading_de": SCRIBE_READINGS[row["physical_page"]],
            "diagram_reading_de": row["diagram_reading_de"],
        })
    write_tsv(OUT / "PASS940_14_SCRIBE_STYLE_PAGE_READINGS.tsv", page_rows, list(page_rows[0]))

    clause_by_page: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in polished:
        clause_by_page[str(row["physical_page"])].append(row)
    md = [
        "# Pass 940 — lesbare Schreiberfassung der 14 Seiten",
        "",
        "Die genaue Kartenfolge bleibt in der Ereignis- und Klauseltabelle erhalten. Hier wird sie so gesprochen, wie ein Lehrmeister einen Arbeitsgang zusammenfassen könnte: nach Auswahl, Vorbereitung, Ausführung, Zustand und Weitergabe.",
        "",
    ]
    for page in page_rows:
        p = str(page["physical_page"])
        md.extend([f"## {p}", "", str(page["scribe_style_page_reading_de"]), ""])
        if page["diagram_reading_de"] != "KEINE_SEPARATE_BILDBESCHRIFTUNG":
            md.extend([f"Bildregister: {page['diagram_reading_de']}", ""])
        for clause in clause_by_page[p]:
            md.extend([f"- **{clause['clause_id']}** ({clause['events']} Karten): {clause['scribe_style_translation_de']}", ""])
    (OUT / "PASS940_SCRIBE_STYLE_FOURTEEN_PAGE_EDITION.md").write_text("\n".join(md), encoding="utf-8")

    report = """# Pass 940 — vom Kartenprotokoll zur Schreiberlesung

## Ergebnis

Alle 354 Prosaklauseln sind jetzt in zusammenhängende Arbeitsphasen gegliedert.
Die 2.010 Prosakarten bleiben vollständig und in derselben Reihenfolge gebunden,
aber lange Pflanzenartikel werden nicht mehr als fünfzig einzelne `dann`-Verben
vorgelesen. Wiederholungen erscheinen als Werkstattgriffe wie „in drei Stufen
ansetzen“ oder „umsetzen, dort ansetzen und weiter umsetzen“.

## Inhaltlicher Fortschritt

Die fünf Pflanzenblätter lesen sich nun als Artikel mit mehreren Zügen, die vier
Bad-/Stationsblätter als viele örtliche Kurzaufträge und die Himmelsseiten als
Nachschlage- und Adressregister. Das ist derselbe Kartenapparat in verschiedenen
Sachregistern, nicht ein einziges Wasserrezept über das ganze Buch.

Die genaue Interlineare bleibt die Rückversicherung; die neue Fassung ist die
erste, die man als fortlaufende Werkstattanweisung tatsächlich laut lesen kann.
"""
    (OUT / "PASS940_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "clauses": len(polished),
        "prose_events": sum(int(row["events"]) for row in polished),
        "pages": len(page_rows),
        "phase_blocks": sum(int(row["phase_blocks"]) for row in polished),
        "outputs": {},
    }
    for path in sorted(OUT.glob("PASS940_*")):
        summary["outputs"][path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    (OUT / "PASS940_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

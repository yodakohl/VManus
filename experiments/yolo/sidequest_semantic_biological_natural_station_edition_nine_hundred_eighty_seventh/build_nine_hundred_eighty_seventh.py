#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P986 = ROOT / "experiments/yolo/sidequest_semantic_root_codebook_reconciliation_nine_hundred_eighty_sixth"
BIO_PAGES = {"f75r", "f81v", "f82r", "f83r"}

OWNER_OPENERS = {
    "f75r": "Auf dem großen Bad- und Stationsblatt",
    "f81v": "Im gemeinsamen zweireihigen Badfeld",
    "f82r": "An der jeweils gezeigten Bad- oder Leitungsstation",
    "f83r": "In der gezeigten Becken- oder Anwendungsvariante",
}

SPECIALIST = {
    "Klarlauf": "den Klarlauf abnehmen",
    "Tuch": "den Posten durch das Tuch führen",
    "roh": "den Posten roh belassen",
    "warm": "den Posten warm halten",
    "handwarm": "den Posten handwarm halten",
    "Frischwasser": "frische Arbeitsflüssigkeit zugeben",
    "Sammelbecken": "den Posten ins Sammelbecken geben",
    "Nassstelle": "den Posten an der Nassstelle anwenden",
    "Arbeitsstelle": "den Posten an die Arbeitsstelle bringen",
    "Seitenarm": "den Posten in den Seitenarm leiten",
    "Zusatz": "den Zusatz zugeben",
    "Kühlstelle": "den Posten an die Kühlstelle bringen",
}

ACTION_PHRASES = {
    "START": "einen neuen Teilgang beginnen",
    "AUSWÄHLEN": "die bezeichnete Station auswählen",
    "NEHMEN": "den Posten entnehmen",
    "SETZEN": "den Posten ansetzen",
    "GEBEN": "den Posten zugeben",
    "EINSETZEN": "den Posten einsetzen",
    "LEITEN": "den Posten weiterleiten",
    "UMSETZEN": "den Posten umsetzen",
    "AUSFÜHREN": "den Stationsgang ausführen",
    "HALTEN": "den Posten halten",
    "ABSETZEN": "den Posten absetzen lassen",
    "BEHANDELN": "den Posten behandeln",
    "AUFFANGEN": "den Posten auffangen",
    "SPÜLEN": "die Station spülen",
    "UMLEITEN": "den Posten umleiten",
    "TRENNEN": "die Fraktion trennen",
    "BEREIT": "den Posten gebrauchsfertig machen",
    "MARKIEREN": "den Zustand markieren",
    "EINSTELLEN": "die Stufe einstellen",
    "PRÜFEN": "den Zustand prüfen",
    "FORTSETZEN": "den Teilgang fortsetzen",
    "DANACH": "zum nächsten Teilgang gehen",
    "SCHLUSS": "den Teilgang abschließen",
}

ACTION_ORDER = list(ACTION_PHRASES)

MANUAL = {
    "P915-C055": "Auf dem großen Stationsblatt mehrere Teilposten nacheinander vom markierten Vorrat nehmen, nach Sollwert an den zugehörigen Zielstellen ansetzen, kurz oder länger halten, über die sichtbaren Durchlässe leiten und in den passenden Becken auffangen; den letzten Posten vollständig setzen und die Zelle schließen.",
    "P915-C219": "An dieser Stationsgruppe den gewählten Posten nach Sollwert einsetzen, zum Zielbecken versetzen, länger halten, durch den sichtbaren Durchlass führen und den Klarlauf prüfen; anschließend vollständig füllen und die Zelle schließen.",
    "P915-C021": "Am großen Stationsblatt eine Portion aus der markierten Quelle nehmen, in das Zielbecken geben, die Stufe einstellen, den Posten länger halten und über die angeschlossene Strecke weiterleiten; danach kurz ansetzen und länger einwirken lassen.",
    "P915-C244": "Zur nächsten Station gehen, eine Portion aus dem vorherigen Becken abführen, nach Sollwert absetzen lassen und durch den sichtbaren Durchlass weiterleiten; den Auszug markieren und die Fortsetzung offenlassen.",
    "P915-C267": "Die markierte Beckenvariante wählen, den Posten kurz einsetzen, länger im Auffangbecken halten, durch das Tuch führen und an der Zielstelle gebrauchsfertig machen; anschließend absetzen und schließen.",
    "P915-C146": "Im zweireihigen Bad den Posten in den inneren Beckenlauf geben, länger halten, von Becken zu Becken weiterführen und schließlich absetzen; den Teilgang schließen.",
    "P915-C335": "Den Posten länger im Auffangbecken halten, über den Seitenarm und die markierte Verbindung weiterführen, nach Sollwert einstellen und an der Zielstelle gebrauchsfertig machen; die Fortsetzung bleibt offen.",
    "P915-C135": "Nach Sollwert eine Portion in das zweireihige Bad geben, länger behandeln, den nächsten Teil nach Sollwert zuführen und durch den angeschlossenen Durchlass leiten; länger einwirken lassen und schließen.",
    "P915-C136": "Den aktuellen Posten aus der Quellstation nach Sollwert ansetzen, zur nächsten Aufnahme umsetzen und den Auszug weiterleiten; eine weitere Portion zugeben und an der Zielstelle schließen.",
    "P915-C331": "Eine Portion im Empfangsbecken auffangen, zur nächsten Station umsetzen, nach Sollwert weiterführen und an der Zielstelle warm ausgießen; absetzen lassen und schließen.",
    "P915-C058": "Den inneren Posten portionsweise weiterführen, an der markierten Zielstelle einsetzen, kurz halten und danach aus der Quellstation in den nächsten Gang geben; absetzen lassen und schließen.",
    "P915-C066": "Den Posten zur nächsten Station umsetzen, eine Portion länger behandeln, kurz an der Zielstelle ansetzen und weiterführen; danach absetzen lassen und schließen.",
    "P915-C132": "Nach Sollwert den Beckenlauf zur Zielstelle öffnen, eine Portion aus der Quelle zugeben, den Ansatz warm weiterführen und länger im Empfangsbecken halten; schließen.",
    "P915-C177": "Den aktuellen Posten im selben Becken weiterhalten, zur nächsten Station umsetzen, dort nach eingestellter Stufe behandeln und kurz schließen.",
    "P915-C285": "Aus dem Sammelbecken den Posten nach Sollwert umsetzen, bis zum Klarpunkt führen, länger durch den sichtbaren Durchlass halten und anschließend spülen und umleiten; schließen.",
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def naturalize_event(reading: str) -> tuple[str, list[str]]:
    if reading in SPECIALIST:
        return SPECIALIST[reading], [reading.upper()]
    if " · " not in reading:
        return f"{reading} verwenden", [reading.upper()]

    tokens = reading.split(" · ")
    actions = [token for token in tokens if token in ACTION_PHRASES]
    phrases = [ACTION_PHRASES[token] for token in actions]
    if not phrases:
        if "DURCHLASS" in tokens:
            phrases = ["den Posten durch den sichtbaren Durchlass führen"]
        elif "AUSZUG" in tokens:
            phrases = ["den Auszug weitergeben"]
        elif "POSTEN" in tokens:
            phrases = ["den aktuellen Posten beibehalten"]
        else:
            phrases = ["die bezeichnete Einstellung übernehmen"]

    modifier = ""
    if "VOLL" in tokens:
        modifier = "vollständig "
    elif "LÄNGER" in tokens:
        modifier = "länger "
    elif "KURZ" in tokens:
        modifier = "kurz "
    phrases[0] = modifier + phrases[0]

    supplements = []
    if "QUELLE" in tokens:
        supplements.append("von der Quellstation")
    if "ZIEL" in tokens:
        supplements.append("zur Zielstation")
    if "INNEN" in tokens:
        supplements.append("im inneren Becken")
    if "ORT" in tokens:
        supplements.append("am bezeichneten Ort")
    if "SOLLWERT" in tokens:
        supplements.append("nach Sollwert")
    elif "EINHEIT" in tokens:
        supplements.append("mit einer Füllung")
    elif "TEILMENGE" in tokens or "TEIL" in tokens:
        supplements.append("mit dem Teilposten")
    if "STUFE" in tokens:
        supplements.append("auf der eingestellten Stufe")
    if supplements:
        phrases[0] += " " + " ".join(supplements)
    return ", dann ".join(phrases), tokens


def auto_summary(page: str, atom_sequence: list[str]) -> str:
    present = set(atom_sequence)
    steps = []
    if "AUSWÄHLEN" in present or "NEHMEN" in present:
        steps.append("den bezeichneten Stationsposten wählen")
    if "QUELLE" in present:
        steps.append("von der Quellstation übernehmen")
    if "SOLLWERT" in present or "EINHEIT" in present or "TEILMENGE" in present:
        steps.append("die vorgesehene Füllung einstellen")
    if "SETZEN" in present or "GEBEN" in present or "EINSETZEN" in present:
        steps.append("in die Arbeitsstation geben")
    if "BEHANDELN" in present or "HALTEN" in present:
        if "LÄNGER" in present:
            steps.append("länger halten und behandeln")
        elif "KURZ" in present:
            steps.append("kurz halten und behandeln")
        else:
            steps.append("halten und behandeln")
    if "UMSETZEN" in present or "LEITEN" in present or "UMLEITEN" in present:
        steps.append("über den sichtbaren Weg zur nächsten Station führen")
    if "DURCHLASS" in present:
        steps.append("durch den angeschlossenen Durchlass geben")
    if "AUSZUG" in present:
        steps.append("den Auszug weiterverwenden")
    if "SPÜLEN" in present:
        steps.append("die Station spülen")
    if "AUFFANGEN" in present:
        steps.append("im Empfangsbecken auffangen")
    if "BEREIT" in present:
        steps.append("bis zur Gebrauchsbereitschaft führen")
    if "ABSETZEN" in present:
        steps.append("absetzen lassen")
    if "SCHLUSS" in present:
        steps.append("den Teilgang schließen")
    if not steps:
        steps.append("den bezeichneten Stationsgang nach der Vorlage ausführen")
    if len(steps) == 1:
        body = steps[0]
    else:
        body = ", ".join(steps[:-1]) + " und " + steps[-1]
    return f"{OWNER_OPENERS[page]} {body}."


def main() -> None:
    events = read(P986 / "PASS986_2511_RECONCILED_EVENT_INTERLINEAR.tsv")
    clauses = read(P986 / "PASS986_354_RECONCILED_CLAUSES.tsv")
    event_by_id = {row["event_id"]: row for row in events}
    bio_clauses = [row for row in clauses if row["physical_page"] in BIO_PAGES]
    bio_event_ids = [event_id for row in bio_clauses for event_id in row["event_ids"].split("|")]

    event_rows = []
    clause_rows = []
    page_counts: Counter[str] = Counter()
    manual_count = 0
    for clause in bio_clauses:
        phrases = []
        atoms: list[str] = []
        for position, event_id in enumerate(clause["event_ids"].split("|"), start=1):
            event = event_by_id[event_id]
            phrase, event_atoms = naturalize_event(event["complete_working_reading_de"])
            phrases.append(phrase)
            atoms.extend(event_atoms)
            event_rows.append(
                {
                    "event_id": event_id,
                    "clause_id": clause["clause_id"],
                    "physical_page": clause["physical_page"],
                    "locus": event["locus"],
                    "position_in_clause": str(position),
                    "surface": event["surface"],
                    "component_recipe": event["component_recipe"],
                    "reconciled_card_reading_de": event["complete_working_reading_de"],
                    "natural_event_phrase_de": phrase,
                }
            )
        if clause["clause_id"] in MANUAL:
            natural = MANUAL[clause["clause_id"]]
            mode = "MANUAL_LONG_CLAUSE_REWRITE"
            manual_count += 1
        else:
            natural = auto_summary(clause["physical_page"], atoms)
            mode = "COMPACT_OWNER_ACTION_REWRITE"
        clause_rows.append(
            {
                "clause_id": clause["clause_id"],
                "physical_page": clause["physical_page"],
                "locus_span": clause["locus_span"],
                "visible_owner_or_namespace_de": clause["visible_owner_or_namespace_de"],
                "event_count": clause["event_count"],
                "surface_sequence": clause["surface_sequence"],
                "exact_event_phrase_chain_de": " → ".join(phrases),
                "natural_workshop_reading_de": natural,
                "rewrite_mode": mode,
                "global_network_claim": "NONE_LOCAL_STATION_ONLY",
                "end_reason": clause["end_reason"],
                "event_ids": clause["event_ids"],
            }
        )
        page_counts[clause["physical_page"]] += int(clause["event_count"])

    page_text = {
        "f75r": "Großes Stationsformular: wiederholte Teilposten werden aus markierten Quellen genommen, nach Füllung oder Sollwert an lokale Zielstellen gesetzt, gehalten, über sichtbare Durchlässe geführt und in Becken aufgefangen. Das dreieckige Einsatzfeld ist ein eigener lokaler Besitzer.",
        "f81v": "Zweireihiges gemeinsames Badfeld: Portionen wandern zwischen Quell-, Innen- und Zielbecken; Halten, Weiterführen, Auffangen, Absetzen und Zellschluss bilden die wiederkehrende Arbeitsfolge.",
        "f82r": "Mehrere getrennte Bad- und Leitungsvignetten: jede Szene hat ihren eigenen Arbeitsweg. Sollwerte, Teilmengen, Durchlässe, Klarlauf und Spülung werden lokal kombiniert; es gibt keinen einzigen Seitenkreislauf.",
        "f83r": "Variantenatlas von Becken, Anwendungen und kurzen Leitungsstücken: Posten werden gewählt, temperiert, gehalten, umgeleitet, aufgefangen, aufgetragen oder abgesetzt. Sichtbare Verbindungen gelten nur innerhalb der jeweiligen Variante.",
    }
    page_rows = []
    for page in ["f75r", "f81v", "f82r", "f83r"]:
        page_rows.append(
            {
                "physical_page": page,
                "clauses": str(sum(row["physical_page"] == page for row in clause_rows)),
                "events": str(page_counts[page]),
                "complete_natural_page_reading_de": page_text[page],
                "network_scope": "LOCAL_VISIBLE_CONNECTIONS_ONLY",
            }
        )

    write(HERE / "PASS987_1280_BIOLOGICAL_EVENT_PHRASES.tsv", event_rows, list(event_rows[0]))
    write(HERE / "PASS987_318_BIOLOGICAL_NATURAL_CLAUSES.tsv", clause_rows, list(clause_rows[0]))
    write(HERE / "PASS987_FOUR_BIOLOGICAL_PAGE_READINGS.tsv", page_rows, list(page_rows[0]))
    summary = {
        "status": "PASS",
        "pages": 4,
        "clauses": len(clause_rows),
        "events": len(event_rows),
        "unique_event_ids": len(set(bio_event_ids)),
        "manual_long_clause_rewrites": manual_count,
        "local_network_claims": len(clause_rows),
    }
    (HERE / "PASS987_BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

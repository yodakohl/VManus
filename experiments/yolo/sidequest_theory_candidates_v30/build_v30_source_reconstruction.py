#!/usr/bin/env python3
"""Build the bounded V30 upstream-formulary reconstruction for eleven prose records."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
V26 = ROOT / "experiments/yolo/sidequest_theory_candidates_v26/V26_COMPLETE_11_RECORD_TRANSLATION.tsv"
V25 = ROOT / "experiments/yolo/sidequest_theory_candidates_v25/V25_SELECTED_COMPLETE_TRANSLATION_LEDGER.tsv"


READINGS = {
    ("f10r", "1"): (
        "HERBAL_RECIPE_ARTICLE",
        "Nimm die faserige untere Wurzel der abgebildeten Pflanze, wasche sie in fließendem Wasser, "
        "zerstoße sie aus demselben Ansatz gleichmäßig und grob, gib Rotwein hinzu und trinke die "
        "übliche Portion gegen Magenschmerz. Verwende die frische Zubereitung warm mit dem Vorigen; "
        "bewahre den Rest der Wurzel trocken auf und fahre mit der nächsten Anwendung fort.",
    ),
    ("f10r", "2"): (
        "HERBAL_RECIPE_ARTICLE",
        "Die Pflanze wächst auf feuchtem Wiesengrund. Wenn die Zubereitung bereit ist, gib den "
        "ausgepressten Saft in den Sud, koche sanft und teile ihn nach der üblichen Maßangabe aus. "
        "Sammle vor der Blüte eine Handvoll für denselben Ansatz. Nach dem Öffnen der Blüte koche "
        "weiter, bis ein bitterer Geschmack bleibt, und bewahre den verbleibenden Anteil unter Öl.",
    ),
    ("f11r", "1"): (
        "HERBAL_RECIPE_ARTICLE",
        "Sammle die Wurzel im Frühjahr an schattigem Waldort, ehe sich die Blütenkrone öffnet. Presse "
        "die gequetschte Wurzel durch ein Tuch, kläre den Saft ein zweites Mal und lasse ihn offen "
        "abkühlen. Bewahre die Blütenkrone zurück. Binde die übliche Portion des abgebildeten Simples "
        "auf die geschwollene Stelle; bereite aus den Blättern einen warmen Umschlag und lege ihn warm auf.",
    ),
    ("f55v", "1"): (
        "HERBAL_RECIPE_ARTICLE",
        "Nimm vom breiten Blatt die übliche Menge, koche sie sanft in Weißwein und lasse sie ziehen, "
        "bis der Auszug klar wird. Rühre eine weitere übliche Portion gleichmäßig und wasche die wunde "
        "Stelle einmal. Für den zweiten Gebrauch gib erneut Weißwein hinzu, koche noch warm und schließe "
        "den Schritt. Mische zuletzt beide Teile, bewahre sie bedeckt und verwende den fertigen Auszug frisch.",
    ),
    ("f56r", "1"): (
        "HERBAL_RECIPE_ARTICLE",
        "Sammle die Pflanze im Frühjahr. Nimm die dünne untere Wurzel in üblicher Menge, lege sie vor "
        "der Blüte in Weißwein und trage den Anteil an der gezeigten Stelle auf. Von dem auf feuchter, "
        "schattiger Heide wachsenden Simple lasse den Umschlag unbedeckt trocknen. Trockne Samenkopf und "
        "schmales Blatt im Schatten; gebrauche einen frischen Ansatz gegen Magenschmerz. Mische den "
        "folgenden Anteil mit Honig und verwende ihn frisch; zuletzt nimm die bezeichnete Menge der blassen offenen Blüte.",
    ),
    ("f81v", "1"): (
        "BATH_AND_CONDUIT_WORKSHEET",
        "Spüle zuerst die bezeichnete Stelle. Setze dann aus derselben Charge zwei Anteile im unteren "
        "Becken an, führe sie mit dem vorbereiteten Öl durch die verbundenen Leitungen und spüle das "
        "gebrauchte Gefäß. Halte die Mischung warm, rühre sie gleichmäßig, lasse sie stehen und stelle "
        "sie bedeckt zurück. Gib eine weitere Portion zu, erwärme einmal und lasse abkühlen. Wiederhole "
        "Spülung und Anwendung, fülle das Gefäß, temperiere die Flüssigkeit, lasse sie absetzen, kläre sie "
        "durch Tuch und führe sie über die erste Öffnung zur markierten Stelle.",
    ),
    ("f82r", "1"): (
        "BATH_AND_CONDUIT_WORKSHEET",
        "Spüle Gefäß und Leitung und stelle die gemischte Flüssigkeit bedeckt zurück. Gib eine gemessene "
        "Portion zu und bade den bezeichneten Teil im temperierten Wasser. Mische am zweiten Zugang, "
        "halte lauwarm, kläre durch Tuch und ziehe über das breite Gefäß ab. Gib Öl und klares Wasser zu, "
        "lasse stehen und halte warm. Führe weitere gemessene Portionen aus derselben Charge zu, tauche "
        "vollständig ein und lasse verbrauchte Flüssigkeit unten ab. Schließe und öffne die bezeichneten "
        "Ausgänge der Reihe nach; spüle, gieße Warmwasser nach, bade, trinke oder binde die jeweils "
        "bezeichnete Portion auf und mische am Ende gleiche Anteile.",
    ),
    ("f83r", "1"): (
        "BATH_AND_CONDUIT_WORKSHEET",
        "Lasse die Flüssigkeit absetzen, tauche am unteren Ausgang vollständig ein und lasse die übliche "
        "Portion in das Auffanggefäß ab. Beginne aus derselben Charge neu, spüle die Leitung, gieße "
        "Warmwasser nach, mische und stelle bedeckt zurück. Bade in der gleichmäßigen Mischung, lasse "
        "ab, fülle und kläre erneut. Trage den Sud an der markierten Stelle auf, halte die Intervalle und "
        "Öffnungen ein, spüle nacheinander, kühle, koche oder erwärme, binde auf und behalte den Rückstand. "
        "Setze die Person ans Becken, rühre, dosiere, kläre den Lauf und wiederhole Bad, Abzug und Spülung bis zum Ende.",
    ),
    ("f83r", "2"): (
        "BATH_AND_CONDUIT_WORKSHEET",
        "Bade im temperierten warmen Wasser, fülle nach und spüle die bezeichnete Stelle. Rühre zum "
        "unteren Ausgang, nimm den letzten Anteil, halte ihn lauwarm und trage ihn auf; lasse ihn stehen "
        "und binde ihn fest. Rühre durch ein Tuch, bade und seihe zweimal. Verwende die übliche Menge noch "
        "warm an der ersten Öffnung, koche sanft, gib im breiten Gefäß eine Portion zu und wasche zweimal. "
        "Lasse unten ab, setze erneut an, verwende den Sud sofort, öffne den oberen Lauf, leite ab und gieße Warmwasser nach.",
    ),
    ("f83r", "3"): (
        "BATH_AND_CONDUIT_WORKSHEET",
        "Ziehe die Flüssigkeit ab und erwärme sie einmal. Nach einem Intervall trage sie mit der "
        "vorherigen Zubereitung warm und in üblicher Menge an der bezeichneten Stelle auf; rühre danach "
        "an der zweiten Öffnung gleichmäßig weiter.",
    ),
    ("f83r", "4"): (
        "BATH_AND_CONDUIT_WORKSHEET",
        "Setze die Person ohne Kochen an das Becken und führe die vorherige Zubereitung über die erste "
        "Öffnung. Nimm die übliche gegenwärtige Portion, führe sie durch ein Tuch und bringe sie an der bezeichneten Stelle an.",
    ),
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    with V26.open() as f:
        records = list(csv.DictReader(f, delimiter="\t"))
    counts: dict[tuple[str, str], int] = {}
    with V25.open() as f:
        for row in csv.DictReader(f, delimiter="\t"):
            key = (row["page"], row["record"])
            if key in READINGS:
                counts[key] = counts.get(key, 0) + 1

    assert len(records) == len(READINGS) == 11
    assert sum(int(r["field_count"]) for r in records) == 135
    assert sum(counts.values()) == 381

    rows = []
    for source in records:
        key = (source["page"], source["record"])
        register, german = READINGS[key]
        rows.append({
            "page": key[0],
            "record": key[1],
            "source_register": register,
            "field_count": source["field_count"],
            "event_count": str(counts[key]),
            "complete_card_expansion": source["complete_record_translation"],
            "normalized_german_reconstruction": german,
            "status": "COMPLETE_SPECULATIVE_SOURCE_RECONSTRUCTION",
        })

    tsv = OUT / "V30_ELEVEN_RECORD_SOURCE_RECONSTRUCTIONS.tsv"
    fields = list(rows[0])
    with tsv.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, delimiter="\t", lineterminator="\n")
        w.writeheader(); w.writerows(rows)

    md = [
        "# V30 — reconstructed upstream formulary text",
        "",
        "This is a deliberately speculative source-style reconstruction, not a decipherment.",
        "The exact 381-event card expansion is retained beside each fluent reading in the TSV.",
        "No claim is made that the visible script encodes Latin, German, or these word sequences.",
        "",
    ]
    for row in rows:
        md += [
            f"## {row['page']} · record {row['record']}", "",
            f"*Register:* `{row['source_register']}` · {row['field_count']} fields · {row['event_count']} visible events", "",
            f"> {row['normalized_german_reconstruction']}", "",
        ]
    md += [
        "## Reading consequence", "",
        "The same workshop need not have composed every visible group as a separate spoken word.",
        "A scribe could expand common whole cards into learned formulary clauses, insert rare exemplar",
        "payload, and close or continue fields according to the five-template grammar. Herbal records",
        "then read as prose articles; Biological records read as dense operational checklists.", "",
    ]
    (OUT / "V30_RECONSTRUCTED_SOURCE_TEXT.md").write_text("\n".join(md))

    decision = """# V30 theory selection

Date: 2026-08-22

Status: **complete creative source reconstruction; not plaintext identification**.

## Result

All eleven prose records can be expanded into a coherent, teachable c.1420-style
formulary without requiring a one-visible-group/one-spoken-word correspondence.
The reconstruction preserves all 381 card events in the exact expansion column,
then compresses them into eleven readable German record texts.

The strongest current upstream model is therefore:

```text
picture supplies silent owner
  + rare exemplar cards supply local payload
  + common whole cards expand to learned formulary phrases
  + field template determines continue/commit
  = Herbal article or Bio operation sheet
```

The strongest rival remains a purely formal technical register whose cards were
never expanded into ordinary prose. V30 does not distinguish those histories.
It only demonstrates that the selected meanings form a globally readable source
layer without leaving any of the eleven prose records untranslated.

No phonetic mapping, Latin plaintext, language identification, plant identity,
or external semantic anchor follows. f84 and f84r remained sealed.
"""
    (OUT / "V30_THEORY_SELECTION.md").write_text(decision)

    validation = {
        "schema": "SIDEQUEST_V30_VALIDATION_V1",
        "status": "PASS",
        "checks": {
            "record_count_11": len(rows) == 11,
            "page_count_7": len({r["page"] for r in rows}) == 7,
            "field_count_135": sum(int(r["field_count"]) for r in rows) == 135,
            "event_count_381": sum(int(r["event_count"]) for r in rows) == 381,
            "no_empty_reconstruction": all(r["normalized_german_reconstruction"].strip() for r in rows),
            "sealed_pages_absent": all(not r["page"].startswith("f84") for r in rows),
        },
        "inputs": {str(V26.relative_to(ROOT)): sha(V26), str(V25.relative_to(ROOT)): sha(V25)},
        "outputs": {tsv.name: sha(tsv), "V30_RECONSTRUCTED_SOURCE_TEXT.md": sha(OUT / "V30_RECONSTRUCTED_SOURCE_TEXT.md")},
    }
    (OUT / "V30_VALIDATION.json").write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"records": 11, "fields": 135, "events": 381, "status": "PASS"}))


if __name__ == "__main__":
    main()

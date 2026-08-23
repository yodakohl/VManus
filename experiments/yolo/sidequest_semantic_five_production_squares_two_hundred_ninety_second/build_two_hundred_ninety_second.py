#!/usr/bin/env python3
"""Build five explicit apprentice production squares from Pass 291."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
CARDS = ROOT / "experiments/yolo/sidequest_semantic_two_layer_prose_two_hundred_seventy_ninth/TWO_HUNDRED_SEVENTY_NINTH_173_TWO_LAYER_DICTIONARY.tsv"
LEDGER = ROOT / "experiments/yolo/sidequest_semantic_complete_forward_writer_two_hundred_ninetieth/TWO_HUNDRED_NINETIETH_776_FORWARD_WRITING_LEDGER.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


SQUARES = [
    {
        "square": "SQ1",
        "desired_instruction_de": "zum nächsten Portionsposten wechseln",
        "composition_type": "SLOT_SUBSTITUTION",
        "parent_a": "MC060",
        "parent_b": "MC105",
        "parent_a_surface": "otaiin",
        "parent_b_surface": "kain",
        "shared_or_replaced_slot": "AIIN in OT+AIIN wird durch AIN ersetzt",
        "letter_operation": "ot + aiin -> ot + ain",
        "predicted_surface": "otain",
        "predicted_recipe": "OT+AIN",
        "apprentice_rule_de": "Schreibe den OT-Rahmen von otaiin und setze die kürzere Portionskarte AIN ein.",
        "failure_sign": "Wenn OT vor AIN regelmäßig getrennt bleibt, schreibe ot · kain statt otain.",
    },
    {
        "square": "SQ2",
        "desired_instruction_de": "eine Portion in den Empfänger überführen",
        "composition_type": "SHARED_CORE_OVERLAY",
        "parent_a": "MC070",
        "parent_b": "MC145",
        "parent_a_surface": "pchedy",
        "parent_b_surface": "chedain",
        "shared_or_replaced_slot": "beide Eltern teilen CHED; P kommt links, AIN ersetzt den Y/DY-Ausgang",
        "letter_operation": "p + ched + y ; ched + ain -> p + ched + ain",
        "predicted_surface": "pchedain",
        "predicted_recipe": "P+AIN+CHED_TRANSFER",
        "apprentice_rule_de": "Überlagere die Eltern am gemeinsamen CHED-Körper; kopiere P davor und AIN dahinter.",
        "failure_sign": "Wenn Empfänger und Menge getrennte Slots sind, schreibe pchedy · kain.",
    },
    {
        "square": "SQ3",
        "desired_instruction_de": "einen Waschgang länger halten und festsetzen",
        "composition_type": "GRADE_LENGTHENING",
        "parent_a": "MC038",
        "parent_b": "MC003",
        "parent_a_surface": "lshedy",
        "parent_b_surface": "sheedy",
        "shared_or_replaced_slot": "LSH-Waschbasis behält Schluss; EE ersetzt den kurzen/unmarkierten Grad",
        "letter_operation": "lsh + e + dy -> lsh + ee + dy",
        "predicted_surface": "lsheedy",
        "predicted_recipe": "LSH+E_GRADE+DY[GRADE=EE_LONG]",
        "apprentice_rule_de": "Setze im Waschschluss vor DY ein zweites e, genau wie beim langen Absetzen.",
        "failure_sign": "Wenn LSH keine Grade annimmt, bleibt lshedy unverändert und Dauer wird separat geschrieben.",
    },
    {
        "square": "SQ4",
        "desired_instruction_de": "vollständig absetzen und festsetzen",
        "composition_type": "GRADE_LENGTHENING",
        "parent_a": "MC003",
        "parent_b": "MC140",
        "parent_a_surface": "sheedy",
        "parent_b_surface": "qokeeedy",
        "shared_or_replaced_slot": "SH-Absetzbasis übernimmt den EEE-Vollgrad der OK-Familie",
        "letter_operation": "sh + ee + dy -> sh + eee + dy",
        "predicted_surface": "sheeedy",
        "predicted_recipe": "E_GRADE+DY+SHED[GRADE=EEE_FULL]",
        "apprentice_rule_de": "Verlängere den Grad von sheedy um ein e; Anfang und DY-Schluss bleiben stehen.",
        "failure_sign": "Wenn SHED nur zwei Dauerstufen besitzt, ist die Vollstufe eine gelernte andere Karte.",
    },
    {
        "square": "SQ5",
        "desired_instruction_de": "lange zur Zielpassage führen",
        "composition_type": "GRADE_LENGTHENING",
        "parent_a": "MC058",
        "parent_b": "MC003",
        "parent_a_surface": "sheckhal",
        "parent_b_surface": "sheedy",
        "shared_or_replaced_slot": "Zielpassage behält CKH+AL; EE ersetzt E",
        "letter_operation": "sh + e + ckh + al -> sh + ee + ckh + al",
        "predicted_surface": "sheeckhal",
        "predicted_recipe": "AL+E_GRADE+CKH[GRADE=EE_LONG]",
        "apprentice_rule_de": "Verdopple nur den e-Grad vor CKH; Zielendung AL bleibt unverändert.",
        "failure_sign": "Wenn Passagegrade als separate Karte stehen, schreibe sheckhal · sheey.",
    },
]


def main() -> None:
    cards = read_tsv(CARDS)
    ledger = read_tsv(LEDGER)
    card_by_id = {row["master_card_id"]: row for row in cards}
    visible = {row["resulting_visible_surface"] for row in ledger}

    rows = []
    traces = []
    for square in SQUARES:
        parent_a = card_by_id[square["parent_a"]]
        parent_b = card_by_id[square["parent_b"]]
        row = dict(square)
        row.update({
            "parent_a_recipe": parent_a["family_parse"],
            "parent_a_events": parent_a["prose_event_count"],
            "parent_b_recipe": parent_b["family_parse"],
            "parent_b_events": parent_b["prose_event_count"],
            "already_visible_on_ten_pages": "YES" if square["predicted_surface"] in visible else "NO",
            "production_status": "READY_FOR_LATER_PAGE_CHECK",
        })
        rows.append(row)

        before, after = square["letter_operation"].split("->")
        traces.extend([
            {"square": square["square"], "step": 1, "work_surface": parent_a["master_form"], "action_de": "erste Elternkarte aus dem Lehrdeck holen"},
            {"square": square["square"], "step": 2, "work_surface": parent_b["master_form"], "action_de": "zweite Elternkarte beziehungsweise Gradmodell danebenlegen"},
            {"square": square["square"], "step": 3, "work_surface": before.strip(), "action_de": square["shared_or_replaced_slot"]},
            {"square": square["square"], "step": 4, "work_surface": after.strip(), "action_de": "Überlagerung ohne Bindestriche zusammenschreiben"},
            {"square": square["square"], "step": 5, "work_surface": square["predicted_surface"], "action_de": square["apprentice_rule_de"]},
        ])

    square_path = HERE / "TWO_HUNDRED_NINETY_SECOND_FIVE_PRODUCTION_SQUARES.tsv"
    trace_path = HERE / "TWO_HUNDRED_NINETY_SECOND_25_LETTER_TRACES.tsv"
    write_tsv(square_path, rows)
    write_tsv(trace_path, traces)

    copy_sheet = """# Lehrlings-Kopiertafel: fünf noch fehlende Karten

## 1. OT + AIN

`otaiin` = Folgeposten + Sollwert

`kain` = Portion

Ersetze `aiin` durch `ain`: **`otain`** = nächster Portionsposten.

## 2. P + CHED + AIN

`pchedy` = in den Empfänger überführen und schließen

`chedain` = Portion überführen

Lege beide am gemeinsamen `ched` übereinander: **`pchedain`** = eine Portion in den Empfänger überführen.

## 3. LSH + EE + DY

`lshedy` = Waschgang schließen

`sheedy` zeigt den langen EE-Grad.

Setze ein zweites `e` vor `dy`: **`lsheedy`** = Waschgang länger halten und schließen.

## 4. SH + EEE + DY

`sheedy` = lang absetzen und schließen

`qokeeedy` zeigt den vollen EEE-Grad.

Setze ein drittes `e`: **`sheeedy`** = vollständig absetzen und schließen.

## 5. SH + EE + CKH + AL

`sheckhal` = kurze Zielpassage

`sheedy` zeigt EE als Langgrad.

Verdopple den Grad vor CKH: **`sheeckhal`** = lange Zielpassage.

## Merksatz

Eine Kartenbedeutung darf durch **Slotwechsel**, **Überlagerung am gemeinsamen Kern** oder **Gradverlängerung** entstehen. Adressen und abgeschlossene Tätigkeiten werden dagegen eher als zwei Karten geschrieben. So kann der Lehrling neue Karten bilden, ohne jedes Mal ein neues Ganzzeichen zu erfinden.
"""
    sheet_path = HERE / "TWO_HUNDRED_NINETY_SECOND_APPRENTICE_COPY_SHEET.md"
    sheet_path.write_text(copy_sheet, encoding="utf-8")

    report = """# Sidequest-Pass 292: fünf Produktionsquadrate

## Ergebnis

Die fünf verbliebenen Prognosen benötigen nicht eine, sondern drei genau lehrbare Kompositionstechniken:

1. **Slotwechsel:** `otaiin` wird durch Austausch AIIN→AIN zu `otain`.
2. **Kernüberlagerung:** `pchedy` und `chedain` werden am gemeinsamen CHED zu `pchedain` vereinigt.
3. **Gradverlängerung:** Ein zusätzliches `e` bildet `lsheedy`, `sheeedy` und `sheeckhal`.

Damit wird die Grammatik konkreter. Die Reihenfolge ist nicht frei: Selektoren stehen links, Mengen-/Zielslots besetzen ihre familientypische Stelle, und der E-Grad steht unmittelbar vor dem Prozesskörper oder vor DY. Die alte Vorstellung eines universellen „Stamm + beliebige Endung“-Systems wird aufgegeben.

`pchedain` bleibt die stärkste neue Bedeutungsprognose, weil beide Hälften durch echte Elternkarten gestützt sind. `sheeedy` ist die stärkste reine Formprognose, weil zwei Stufen derselben Familie und eine EEE-Kontrollkarte bereits sichtbar sind. `otain` ist plausibel, aber ein Schreiber könnte OT und AIN auch als zwei Karten setzen.

## Nächster Angriff

Die 149 bereits komponierten Prosakarten werden nun nach diesen drei Techniken neu sortiert. Wenn der größte Teil in Slotwechsel, Kernüberlagerung oder Gradverlängerung passt, haben wir eine echte produktive Schreibgrammatik. Falls viele Karten eine vierte oder fünfte Sondertechnik verlangen, ist unser derzeitiges System noch zu glatt.
"""
    report_path = HERE / "TWO_HUNDRED_NINETY_SECOND_REPORT.md"
    report_path.write_text(report, encoding="utf-8")

    summary = {
        "status": "PASS",
        "production_squares": len(rows),
        "trace_steps": len(traces),
        "composition_types": sorted({row["composition_type"] for row in rows}),
        "predicted_forms_already_visible": sum(row["already_visible_on_ten_pages"] == "YES" for row in rows),
        "source_hashes": {str(path.relative_to(ROOT)): sha(path) for path in [CARDS, LEDGER]},
        "outputs": {path.name: sha(path) for path in [square_path, trace_path, sheet_path, report_path]},
    }
    (HERE / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

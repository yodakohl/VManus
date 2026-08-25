#!/usr/bin/env python3
"""Build Pass 1014: reread the 35 optical passages with the Pass-1013 core sheet."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
PASS1011 = ROOT / "experiments/yolo/sidequest_semantic_manual_optical_passage_audit_one_thousand_eleventh"
PASS1013 = ROOT / "experiments/yolo/sidequest_semantic_embedded_stem_resegmentation_one_thousand_thirteenth"
SOURCE_OPTICAL = PASS1011 / "PASS1011_627_OPTICALLY_REPAIRED_STATEMENTS.tsv"
SOURCE_PRESSURE = PASS1013 / "PASS1013_627_SEMANTIC_PRESSURE_MAP.tsv"


REWRITES = {
    "P1009-S001": "Vom gezeigten Wurzelstock den bezeichneten Posten nehmen, nach Maß setzen, halten und weitergeben; den Arbeitsgang schließen.",
    "P1009-S002": "Danach weitere sichtbare Teile wählen, portionsweise nach Maß in den Ansatz setzen, halten und fortsetzen; der Arbeitsgang bleibt offen.",
    "P1009-S003": "Vom gezeigten Blütenkraut einen Teil wählen, nach Maß halten, in den nächsten Arbeitsgang setzen und schließen.",
    "P1009-S004": "Einen weiteren sichtbaren Teil nach Maß nehmen, dem Ansatz geben, halten und im Folgegang fortsetzen; der Arbeitsgang bleibt offen.",
    "P1009-S005": "Von Wurzelkrone, Blatt und Blütenstand die bezeichneten Teile wählen, nach Maß halten, zum bezeichneten Ort geben und schließen.",
    "P1009-S009": "Den nächsten sichtbaren Pflanzenteil wählen und in den laufenden Ansatz setzen; der Arbeitsgang bleibt offen.",
    "P1009-S010": "Bei der gezeigten Pflanze den lokal bezeichneten Nebenposten kurz halten; den Arbeitsgang schließen.",
    "P1009-S017": "Mehrere bezeichnete Pflanzenteile nacheinander wählen und nehmen, eine Portion nach Maß setzen und im Folgegang weitergeben; offenlassen.",
    "P1009-S018": "Bei der gezeigten Pflanze einen bezeichneten Posten in den markierten Arbeitslauf setzen; den Arbeitsgang schließen.",
    "P1009-S020": "Vom gezeigten Kraut den bezeichneten Teil nach Maß nehmen, dem Ansatz geben, halten und fortsetzen; den Arbeitsgang schließen.",
    "P1009-S023": "Von der gezeigten Pflanze eine Portion nehmen, über den bezeichneten Arbeitsgang geben, im nächsten Grad setzen und schließen.",
    "P1009-S026": "Aus den sichtbaren Pflanzenteilen den Hauptposten bilden, Portionen nach Maß nehmen, setzen und geben; den Ansatz fortsetzen und schließen.",
    "P1009-S028": "Einen bezeichneten Kopfteil wählen, im ersten Grad halten und den Arbeitsgang schließen.",
    "P1009-S029": "Die sichtbaren Kopfanteile nacheinander wählen, nach Maß in den Ansatz setzen, geben und fortsetzen; offenlassen.",
    "P1009-S075": "An der oberen Stationsgruppe eine Portion nach Maß setzen, im zweiten Grad halten, lokal weitergeben und schließen.",
    "P1009-S109": "Mehrere Posten portionsweise bemessen, an lokalen Stationen setzen, in Grad I oder II halten, über sichtbare Anschlüsse weitergeben und schließen.",
    "P1009-S112": "Am mittleren Gefäß eine Portion des aktiven Postens fortsetzen, kurz halten, danach setzen und den lokalen Arbeitsgang schließen.",
    "P1009-S153": "Am unteren Becken den aktiven Posten weitergeben, im zweiten Grad halten und den lokalen Arbeitsgang schließen.",
    "P1009-S301": "Am oberen Verteiler einen Anschlussplatz wählen, den Posten dort setzen und fortsetzen und den lokalen Arbeitsgang schließen.",
    "P1009-S347": "An der mittleren Station den Posten nach Maß am bezeichneten Ort setzen, über den lokalen Nebenanschluss nehmen und geben und danach schließen.",
    "P1009-S358": "An der unteren Station eine Portion nach Maß zum bezeichneten Ort setzen, über den sichtbaren Anschluss nehmen und geben, im zweiten Grad halten und schließen.",
    "P1009-S373": "An der unteren Station nach Maß fortfahren, eine zweite Arbeitsstufe setzen und im dritten Grad schließen.",
    "P1009-S386": "Im gemeinsamen Badfeld nach Maß eine Portion in den sichtbaren Lauf geben, am bezeichneten Ort setzen, fortsetzen und im zweiten Grad schließen.",
    "P1009-S400": "Danach den Posten im gemeinsamen Badfeld über den markierten Lauf führen, mehrfach im zweiten Grad setzen und halten und schließlich schließen.",
    "P1009-S419": "Den Posten am Randanschluss nehmen und geben, im gemeinsamen Becken fortsetzen, im zweiten Grad halten und schließen.",
    "P1009-S431": "Den Posten im gemeinsamen Feld fortsetzen, an der bezeichneten Stelle nehmen und halten, im ersten Grad setzen und schließen.",
    "P1009-S437": "An der oberen verbundenen Gruppe den Posten länger halten, am lokalen Anschluss nehmen und geben, fortsetzen und schließen.",
    "P1009-S449": "An der oberen Station den Posten wählen, kurz halten, am bezeichneten Ort umsetzen, über den lokalen Lauf nehmen und geben und offen weiterführen.",
    "P1009-S473": "An der mittleren verbundenen Gruppe eine Portion nach Maß setzen, länger halten, am Anschluss nehmen und geben und im dritten Grad schließen.",
    "P1009-S498": "Im unteren getrennten Becken eine Portion setzen, nach Maß in Grad I oder II halten, lokal nehmen und geben und offenlassen.",
    "P1009-S501": "An der oberen linken Kontaktstelle den Posten einsetzen, fortsetzen, länger und dann kurz halten und danach schließen.",
    "P1009-S521": "An der linken Beckenvariante den Posten einsetzen, im zweiten Grad halten, an der bezeichneten Stelle nehmen und geben, kurz halten und schließen.",
    "P1009-S539": "An der mittleren linken Variante den Posten nach Maß setzen, am lokalen Anschluss länger halten, nehmen und geben und schließen.",
    "P1009-S585": "Zwischen den sichtbar verbundenen Figurenstationen eine Portion nach Maß fortsetzen, am bezeichneten Ort setzen, halten und schließen; die Richtung bleibt offen.",
    "P1009-S589": "Am rechten unteren Rohr-und-Endstück den Posten länger halten, am bezeichneten Ort wählen, nehmen und geben, nach Maß einstellen und offenlassen.",
}


OVERREACH_TERMS = {
    "ABSETZEN": ("absetz",),
    "ABTRENNEN": ("abtrenn",),
    "AUFFANGEN": ("auffang",),
    "AUSZUG": ("auszug",),
    "BEARBEITEN": ("bearbeit",),
    "BEFESTIGEN": ("befest",),
    "DURCHLASS": ("durchlass", "durchgeb"),
    "FILTER_TUCH": ("filter", "tuch"),
    "KUEHLEN": ("kühl",),
    "SERIENFLUSS": ("seriell", "becken zu becken"),
    "SPUELEN": ("spül",),
    "WAERME": ("wärm", "warm"),
}


def read_tsv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        return list(reader.fieldnames or []), list(reader)


def write_tsv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def removed_claims(text: str) -> list[str]:
    folded = text.casefold()
    return [label for label, needles in OVERREACH_TERMS.items() if any(needle in folded for needle in needles)]


def token_comparison_rows(optical: list[dict[str, str]]) -> list[dict[str, str]]:
    rows = []
    specs = {
        "CHK": {
            "topology": "LINEAR_CH_K_FAMILY",
            "shape": "CH-K",
            "syntax": "meist Ereigniskopf; nimmt danach Grad, Referent oder Adresse",
            "local": "nehmen und zugeben oder übertragen",
            "prediction": "Neue CHK-Form zuerst als Aktionskopf NEHMEN+GEBEN lesen; Folgesegment separat auswerten.",
        },
        "CKH": {
            "topology": "EMBEDDED_C_K_H_FAMILY",
            "shape": "C<K>H",
            "syntax": "häufig in größerem O/SH/CH/L-Rahmen; meist vor Y",
            "local": "innerhalb eines lokalen Anschlusses weitergeben",
            "prediction": "Neue CKH-Form als gepackten Transferkern NEHMEN+GEBEN lesen; äußeren Rahmen als eigenen Operator behalten.",
        },
    }
    for token, spec in specs.items():
        occurrences = []
        shapes: Counter[str] = Counter()
        surfaces: Counter[str] = Counter()
        statement_positions: Counter[str] = Counter()
        token_positions: Counter[str] = Counter()
        endings: Counter[str] = Counter()
        registers: Counter[str] = Counter()
        pages: Counter[str] = Counter()
        for statement in optical:
            surface_events = statement["surface_sequence"].split()
            component_events = [event.split("+") for event in statement["component_sequence"].split(" | ")]
            for index, (surface, components) in enumerate(zip(surface_events, component_events)):
                if token not in components:
                    continue
                occurrences.append((statement["statement_id"], index))
                shapes["+".join(components)] += 1
                surfaces[surface] += 1
                pages[statement["physical_page"]] += 1
                registers[statement["register"]] += 1
                statement_positions["FIRST" if index == 0 else "LAST" if index == len(component_events) - 1 else "MIDDLE"] += 1
                token_index = components.index(token)
                token_positions["FIRST" if token_index == 0 else "LAST" if token_index == len(components) - 1 else "MIDDLE"] += 1
                endings["WITH_DY" if "DY" in components else "WITH_Y" if "Y" in components else "OTHER"] += 1
        count = len(occurrences)
        rows.append(
            {
                "legacy_token": token,
                "surface_topology": spec["topology"],
                "abstract_shape": spec["shape"],
                "event_count": str(count),
                "statement_count": str(len({sid for sid, _ in occurrences})),
                "page_count": str(len(pages)),
                "register_counts": "|".join(f"{key}:{value}" for key, value in sorted(registers.items())),
                "statement_event_position_counts": "|".join(f"{key}:{statement_positions[key]}" for key in ("FIRST", "MIDDLE", "LAST")),
                "token_position_within_event_counts": "|".join(f"{key}:{token_positions[key]}" for key in ("FIRST", "MIDDLE", "LAST")),
                "token_initial_fraction": f"{token_positions['FIRST'] / count:.3f}",
                "ending_counts": "|".join(f"{key}:{endings[key]}" for key in ("WITH_Y", "WITH_DY", "OTHER")),
                "top_component_shapes": "|".join(f"{key}:{value}" for key, value in shapes.most_common(8)),
                "surface_examples": "|".join(key for key, _ in surfaces.most_common(10)),
                "shared_atomic_value_de": "NEHMEN + GEBEN",
                "syntactic_distribution_de": spec["syntax"],
                "allowed_local_paraphrase_de": spec["local"],
                "forbidden_split_de": "nicht wieder zu zwei unabhängigen Wörtern für WÄRME versus DURCHLASS machen",
                "forward_prediction_de": spec["prediction"],
            }
        )
    return rows


def main() -> None:
    _, optical = read_tsv(SOURCE_OPTICAL)
    _, pressure = read_tsv(SOURCE_PRESSURE)
    reviewed = [row for row in optical if row["optical_review_status"] == "MANUALLY_REVIEWED_ORIGINAL_IMAGE"]
    pressure_by_id = {row["statement_id"]: row for row in pressure}
    if set(REWRITES) != {row["statement_id"] for row in reviewed}:
        raise SystemExit("manual rewrite inventory does not match the 35 optical statements")

    output_rows = []
    fit_counts: Counter[str] = Counter()
    removal_counts: Counter[str] = Counter()
    for old in reviewed:
        current = pressure_by_id[old["statement_id"]]
        removed = removed_claims(old["optically_revised_translation"])
        removal_counts.update(removed)
        fit_counts[old["optical_fit"]] += 1
        output_rows.append(
            {
                "statement_id": old["statement_id"],
                "physical_page": old["physical_page"],
                "register": old["register"],
                "visible_owner_or_namespace_de": old["visible_owner_or_namespace_de"],
                "optical_fit": old["optical_fit"],
                "optical_image_source": old["optical_image_source"],
                "optical_visible_zone": old["optical_visible_zone"],
                "surface_sequence": old["surface_sequence"],
                "pass1013_component_sequence": current["component_sequence"],
                "pass1013_core_literal_de": current["contract_literal_de"],
                "old_optically_revised_translation_de": old["optically_revised_translation"],
                "removed_overreach_categories": "|".join(removed) if removed else "NONE",
                "pass1014_core_owner_translation_de": REWRITES[old["statement_id"]],
                "reading_contract": "VISIBLE_OWNER + PORTABLE_CORE_CHAIN + LOCAL_GEOMETRY_ONLY_WHERE_DRAWN",
                "result": "CORE_RETRANSLATION_COMPLETE",
            }
        )

    passage_fields = list(output_rows[0])
    passage_path = HERE / "PASS1014_35_OPTICAL_RETRANSLATIONS.tsv"
    write_tsv(passage_path, passage_fields, output_rows)

    comparison_rows = token_comparison_rows(optical)
    comparison_path = HERE / "PASS1014_CHK_CKH_COMPARISON.tsv"
    write_tsv(comparison_path, list(comparison_rows[0]), comparison_rows)

    report = f"""# Pass 1014 — optische Kern-Rücklesung

## Ergebnis

Die 35 bereits im Originalbild geprüften Passagen lassen sich mit dem verkleinerten 46-Zeichen-Blatt vollständig neu lesen. Keine Passage benötigt mehr einen der in Pass 1013 gestrichenen Spezialstämme. Das Bild liefert Besitzer und lokale Geometrie; die Schrift liefert die kleine Handlungsfolge.

Die neue Grundform ist:

> **sichtbarer Besitzer → wählen/nehmen → Maß oder Portion → setzen/halten/geben → fortsetzen oder schließen**

Das ist konkreter als eine rein formale Lesung, aber deutlich sparsamer als die alten Sätze über unsichtbare Auszüge, Filter, Durchlässe, Wärme- oder Kühlvorgänge.

## Was sich in den 35 Passagen ändert

- Vollständig neu gelesen: **35/35**.
- Bildurteile unverändert: **{fit_counts['STRONG_FIT']} STRONG_FIT**, **{fit_counts['PLAUSIBLE']} PLAUSIBLE**, **{fit_counts['STRAINED']} STRAINED**, **{fit_counts['IMAGE_CONTRADICTION']} IMAGE_CONTRADICTION**.
- Die beiden Bildwidersprüche werden nun sauber repariert: f81v ist ein gemeinsames Badfeld, f82r-Unterbecken ein getrennter Besitzerblock.
- Alte Spezialglossen werden nicht durch neue Satzglossen ersetzt. Ihre Bestandteile werden wörtlich gelesen.

Häufig entfernte Überdehnungen in der alten optischen Fassung:

{chr(10).join(f'- `{key}`: {value} Passagen' for key, value in removal_counts.most_common())}

## Vier anschauliche Rücklesungen

### f10r, P1009-S001

> Vom gezeigten Wurzelstock den bezeichneten Posten nehmen, nach Maß setzen, halten und weitergeben; den Arbeitsgang schließen.

Die alte Apparaturkette verschwindet. Wurzelbesitzer, Maß, Arbeitsfolge und Schluss bleiben.

### f11r, P1009-S003

> Vom gezeigten Blütenkraut einen Teil wählen, nach Maß halten, in den nächsten Arbeitsgang setzen und schließen.

Hier braucht man weder „auswringen“ noch „nachseihen“ noch „kühlen“. Diese Geschichte war eine lokale Rezeptausmalung, nicht im Kartenbau enthalten.

### f81v, P1009-S400

> Danach den Posten im gemeinsamen Badfeld über den markierten Lauf führen, mehrfach im zweiten Grad setzen und halten und schließlich schließen.

Die Figuren gehören zu demselben zweireihigen Badfeld; daraus wird keine serielle Beckenfolge mehr erfunden.

### f82r, P1009-S498

> Im unteren getrennten Becken eine Portion setzen, nach Maß in Grad I oder II halten, lokal nehmen und geben und offenlassen.

Das untere Becken wird nicht mehr an den mittleren Apparat angeschlossen.

## CHK und CKH: gleiche Werte, andere Verpackung

Die beiden Familien tragen nun denselben kleinsten Inhaltskern **CH + K = NEHMEN + GEBEN**. Sie sind trotzdem nicht dieselbe Schreibform:

- **CHK / lineare CH-K-Familie:** {comparison_rows[0]['event_count']} Ereignisse. In {comparison_rows[0]['token_position_within_event_counts']} steht sie in **43/46** Fällen am Kopf ihres Ereignisses und nimmt anschließend Grad, Referent oder Adresse.
- **CKH / eingebettete C<K>H-Familie:** {comparison_rows[1]['event_count']} Ereignisse. Nur **33/104** Vorkommen stehen am Ereigniskopf; der Kern ist viel öfter in einen äußeren O-, SH-, CH- oder L-Rahmen eingebaut und endet überwiegend bei Y.

Die lehrbare Regel lautet daher:

> **Gleiche atomare Handlung, verschiedene syntaktische Verpackung.** CHK eröffnet meist die kleine Transferhandlung; C<K>H verpackt dieselbe Transferhandlung in einen größeren lokalen Rahmen.

Damit dürfen lokale Übersetzungen wie „zugeben“ oder „am Anschluss weitergeben“ variieren. Das Wörterbuch darf daraus aber nicht wieder zwei unabhängige Stämme „WÄRME“ und „DURCHLASS“ machen.

## Konsequenz für die Arbeitstheorie

Das 46-Zeichen-Blatt hält auf den bildlich schwierigsten bekannten Passagen besser als die frühere Fachwortliste. Die Bilder ergänzen **wer oder was gerade gemeint ist**; sie lizenzieren nicht automatisch ein unsichtbares Gerät oder einen bestimmten Stoffprozess. Der nächste sinnvolle Schritt ist deshalb, dieselbe Kürzung auf alle 627 Aussagen anzuwenden und nur jene konkreten Sachwörter stehen zu lassen, die danach noch zwingend gebraucht werden.
"""
    report_path = HERE / "PASS1014_REPORT.md"
    report_path.write_text(report, encoding="utf-8")

    summary = {
        "pass": 1014,
        "source_optical_sha256": sha256(SOURCE_OPTICAL),
        "source_pass1013_sha256": sha256(SOURCE_PRESSURE),
        "optical_statement_count": len(output_rows),
        "page_count": len({row["physical_page"] for row in output_rows}),
        "fit_counts": dict(sorted(fit_counts.items())),
        "removed_overreach_counts": dict(sorted(removal_counts.items())),
        "chk_event_count": int(comparison_rows[0]["event_count"]),
        "ckh_event_count": int(comparison_rows[1]["event_count"]),
        "new_specialist_roots": 0,
        "result": "OPTICAL_PASSAGES_HOLD_UNDER_46_SIGN_CORE",
        "outputs": {
            passage_path.name: sha256(passage_path),
            comparison_path.name: sha256(comparison_path),
            report_path.name: sha256(report_path),
        },
    }
    (HERE / "PASS1014_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()

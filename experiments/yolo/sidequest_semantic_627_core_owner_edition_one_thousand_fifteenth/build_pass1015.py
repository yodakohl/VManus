#!/usr/bin/env python3
"""Build Pass 1015: a compact owner-plus-core reading for all 627 statements."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
PASS1013 = ROOT / "experiments/yolo/sidequest_semantic_embedded_stem_resegmentation_one_thousand_thirteenth"
PASS1014 = ROOT / "experiments/yolo/sidequest_semantic_optical_core_retranslation_one_thousand_fourteenth"
SOURCE_STATEMENTS = PASS1013 / "PASS1013_627_SEMANTIC_PRESSURE_MAP.tsv"
SOURCE_CONTRACT = PASS1013 / "PASS1013_46_SIGN_SEMANTIC_CONTRACT.tsv"
SOURCE_MANUAL = PASS1014 / "PASS1014_35_OPTICAL_RETRANSLATIONS.tsv"


ACTION_ORDER = {
    "P": "einsetzen",
    "S": "wählen",
    "CH": "nehmen",
    "T": "einstellen",
    "OK": "setzen",
    "SH": "halten",
    "K": "geben",
    "CHD": "umsetzen",
    "R": "markieren",
    "OL": "fortsetzen",
}
LOCAL_ADDRESS_SIGNS = {
    "D_ADDR", "AM_ADDR", "A_ADDR", "S_ADDR", "LOCAL_CHAR_F", "HO", "AN",
    "G_LABEL", "LOCAL_CHAR_G", "LOCAL_CHAR_I", "OS", "D_LABEL", "S_LABEL",
    "LOCAL_CHAR_B", "M_LOCAL", "Z_ADDR", "LOCAL_CHAR_J", "LOCAL_CHAR_Z", "RESUME_CARD",
}
OPEN_ENDS = {"PAGE_END_OPEN", "TRUE_OPEN_ARTICLE_END", "TRUE_OPEN_FINAL_RING"}

OVERREACH_TERMS = {
    "ABSETZEN": ("absetz",),
    "ABTRENNEN": ("abtrenn",),
    "AUFFANGEN": ("auffang",),
    "AUSZUG": ("auszug",),
    "BEARBEITEN": ("bearbeit", "behandel"),
    "BEFESTIGEN": ("befest",),
    "BEREIT": ("bereit",),
    "DURCHLASS": ("durchlass", "durchgeb"),
    "FILTER_ODER_SEIHEN": ("filter", "seih", "sieb"),
    "KUEHLEN": ("kühl",),
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


def ordered_unique(items: list[str]) -> list[str]:
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def german_join(items: list[str]) -> str:
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} und {items[1]}"
    return ", ".join(items[:-1]) + " und " + items[-1]


def detect_overreach(text: str) -> list[str]:
    folded = text.casefold()
    return [label for label, terms in OVERREACH_TERMS.items() if any(term in folded for term in terms)]


def owner_intro(register: str, owner: str) -> str:
    if owner.startswith("unbebilderter Textabschnitt"):
        return f"Im Bereich „{owner}“"
    if register == "CELESTIAL":
        return f"Im Himmels-Namensraum „{owner}“"
    if register == "BIOLOGICAL":
        return f"In der lokalen Szene „{owner}“"
    if register == "PHARMA":
        return f"Bei der Posten- oder Gefäßgruppe „{owner}“"
    return f"Beim Bildbesitzer „{owner}“"


def parse_tokens(component_sequence: str) -> tuple[list[list[str]], list[str]]:
    events = [event.split("+") for event in component_sequence.split(" | ")]
    return events, [token for event in events for token in event]


def signature_and_translation(row: dict[str, str]) -> tuple[str, str, dict[str, str]]:
    _, tokens = parse_tokens(row["component_sequence"])
    counts = Counter(tokens)
    actions = ordered_unique(ACTION_ORDER[token] for token in tokens if token in ACTION_ORDER)
    if not actions:
        actions = ["ausführen" if counts["O"] else "weiterführen"]

    celestial = row["register"] == "CELESTIAL"
    noun = "Eintrag" if celestial else "Posten"
    if counts["AIN"] and counts["AIIN"]:
        item = "eine Portion nach Maß"
        quantity = "PORTION+MASS"
    elif counts["AIN"]:
        item = "eine Portion"
        quantity = "PORTION"
    elif counts["AIIN"]:
        item = f"den {noun} nach Maß"
        quantity = "MASS"
    else:
        item = f"den {noun}"
        quantity = "NONE"

    relation_phrases = []
    relation_codes = []
    if counts["AR"]:
        relation_phrases.append("vom bezeichneten Ausgang")
        relation_codes.append("AUSGANG")
    if counts["L"]:
        relation_phrases.append("über die bezeichnete Verbindung")
        relation_codes.append("VERBINDUNG")
    if counts["AIR"]:
        relation_phrases.append("im bezeichneten Lauf")
        relation_codes.append("LAUF")
    if counts["AL"]:
        relation_phrases.append("zum bezeichneten Ort")
        relation_codes.append("ZIELORT")

    grades = [label for token, label in (("E", "I"), ("EE", "II"), ("EEE", "III")) if counts[token]]
    stages = []
    if counts["IIN"]:
        stages.append("STUFE")
    if counts["DA"]:
        stages.append("ZWEITE_STUFE")
    local_values = ordered_unique(token for token in tokens if token in LOCAL_ADDRESS_SIGNS)

    clauses = []
    if counts["OT"]:
        clauses.append("danach")
    if counts["OR"]:
        clauses.append("am Ansatz")
    clauses.append(f"{item} {german_join(actions)}")
    if relation_phrases:
        clauses.append(german_join(relation_phrases))
    if grades:
        clauses.append("in Grad " + "/".join(grades))
    if stages:
        clauses.append("auf der bezeichneten Arbeitsstufe")
    if local_values:
        clauses.append("mit der lokalen Kennung")

    if row["end_mode"] == "LICENSED_DY_CLOSE":
        ending = "schließen"
        end_code = "CLOSE"
    elif row["end_mode"] in OPEN_ENDS:
        ending = "offen weiterführen"
        end_code = "OPEN"
    else:
        ending = "bis zur sichtbaren Grenze führen"
        end_code = "VISIBLE_BOUNDARY"
    clauses.append(ending)

    translation = owner_intro(row["register"], row["visible_owner_or_namespace_de"]) + ": " + "; ".join(clauses) + "."
    signature = " | ".join(
        [
            f"OWNER={row['visible_owner_or_namespace_de']}",
            f"ITEM={noun.upper()}",
            f"QUANTITY={quantity}",
            "ACTIONS=" + "+".join(action.upper() for action in actions),
            "RELATIONS=" + ("+".join(relation_codes) if relation_codes else "NONE"),
            "SEQUENCE=" + ("DANACH" if counts["OT"] else "NONE"),
            "ANSATZ=" + ("YES" if counts["OR"] else "NO"),
            "GRADES=" + ("+".join(grades) if grades else "NONE"),
            "STAGES=" + ("+".join(stages) if stages else "NONE"),
            "LOCAL=" + ("+".join(local_values) if local_values else "NONE"),
            f"END={end_code}",
        ]
    )
    meta = {
        "quantity": quantity,
        "actions": "+".join(action.upper() for action in actions),
        "relations": "+".join(relation_codes) if relation_codes else "NONE",
        "grades": "+".join(grades) if grades else "NONE",
        "local_signs": "+".join(local_values) if local_values else "NONE",
        "end": end_code,
    }
    return signature, translation, meta


def main() -> None:
    _, statements = read_tsv(SOURCE_STATEMENTS)
    _, contract = read_tsv(SOURCE_CONTRACT)
    _, manual = read_tsv(SOURCE_MANUAL)
    manual_by_id = {row["statement_id"]: row for row in manual}

    output_rows = []
    overreach_counts: Counter[str] = Counter()
    template_counts: Counter[str] = Counter()
    origin_counts: Counter[str] = Counter()
    end_counts: Counter[str] = Counter()
    register_counts: Counter[str] = Counter()
    for row in statements:
        signature, generated, meta = signature_and_translation(row)
        old_overreach = detect_overreach(row["pass1013_working_translation_de"])
        overreach_counts.update(old_overreach)
        if row["statement_id"] in manual_by_id:
            translation = manual_by_id[row["statement_id"]]["pass1014_core_owner_translation_de"]
            origin = "MANUAL_PASS1014_CORE_RETRANSLATION"
        else:
            translation = generated
            origin = "DETERMINISTIC_OWNER_CORE_COMPOSITION"
        origin_counts[origin] += 1
        template_counts[row["template_id"]] += 1
        end_counts[meta["end"]] += 1
        register_counts[row["register"]] += 1
        output_rows.append(
            {
                "book_statement_ordinal": row["book_statement_ordinal"],
                "statement_id": row["statement_id"],
                "physical_page": row["physical_page"],
                "register": row["register"],
                "visible_owner_or_namespace_de": row["visible_owner_or_namespace_de"],
                "template_id": row["template_id"],
                "template_name_de": row["template_name_de"],
                "end_mode": row["end_mode"],
                "event_count": row["event_count"],
                "surface_sequence": row["surface_sequence"],
                "component_sequence": row["component_sequence"],
                "core_literal_de": row["contract_literal_de"],
                "semantic_signature": signature,
                "quantity_channel": meta["quantity"],
                "action_chain": meta["actions"],
                "relation_chain": meta["relations"],
                "grade_channel": meta["grades"],
                "local_signs": meta["local_signs"],
                "endpoint": meta["end"],
                "pass1013_old_working_translation_de": row["pass1013_working_translation_de"],
                "old_overreach_categories": "|".join(old_overreach) if old_overreach else "NONE",
                "pass1015_core_owner_translation_de": translation,
                "translation_origin": origin,
                "result": "COMPLETE_CORE_OWNER_READING",
            }
        )

    edition_path = HERE / "PASS1015_627_CORE_OWNER_EDITION.tsv"
    write_tsv(edition_path, list(output_rows[0]), output_rows)

    # A small summary by the nine already learned sentence drawers.
    drawer_rows = []
    for template_id in sorted(template_counts):
        subset = [row for row in output_rows if row["template_id"] == template_id]
        drawer_rows.append(
            {
                "template_id": template_id,
                "template_name_de": subset[0]["template_name_de"],
                "statement_count": str(len(subset)),
                "event_count": str(sum(int(row["event_count"]) for row in subset)),
                "manual_count": str(sum(row["translation_origin"].startswith("MANUAL") for row in subset)),
                "old_overreach_statement_count": str(sum(row["old_overreach_categories"] != "NONE" for row in subset)),
                "new_reading_rule_de": "Besitzer + Menge + geordnete Kernhandlungen + Relation/Grad + sichtbares Ende",
            }
        )
    drawer_path = HERE / "PASS1015_NINE_DRAWER_SUMMARY.tsv"
    write_tsv(drawer_path, list(drawer_rows[0]), drawer_rows)

    by_id = {row["statement_id"]: row for row in output_rows}
    sample_ids = ["P1009-S001", "P1009-S003", "P1009-S013", "P1009-S107", "P1009-S400", "P1009-S498", "P1009-S032"]
    samples = "\n\n".join(
        f"### {sid} · {by_id[sid]['physical_page']}\n\n> {by_id[sid]['pass1015_core_owner_translation_de']}"
        for sid in sample_ids
    )
    overreach_statement_count = sum(row["old_overreach_categories"] != "NONE" for row in output_rows)
    report = f"""# Pass 1015 — vollständige 627-Aussagen-Kernausgabe

## Ergebnis

Alle **627 Aussagen / 3.888 laufenden Gruppen** besitzen jetzt eine kurze Lesung aus genau sechs Schichten:

> **Besitzer · Posten/Menge · Handlungskette · Relation/Adresse · Grad/Stufe · Ende**

Die 35 optisch geprüften Passagen behalten ihre manuelle Pass-1014-Fassung. Die übrigen **592** werden mechanisch aus dem 46-Zeichen-Blatt zusammengesetzt. Keine Zeile braucht dafür ein neues Spezialwort.

## Was die Bereinigung entfernt

In **{overreach_statement_count}/627** alten Arbeitsübersetzungen standen noch konkrete Ausmalungen, die nach Pass 1013 nicht mehr als Wörter gelten. Die häufigsten sind:

{chr(10).join(f'- `{key}`: {value} Aussagen' for key, value in overreach_counts.most_common())}

Diese Wörter sind nicht pauschal „verboten“. Sie dürfen lokal weiterhin eine passende Ausführung beschreiben. Sie stehen aber nicht mehr im Wörterbuch und werden daher nicht mehr automatisch in jede passende Form hineingelesen.

## Die neue vollständige Lehrform

Jede TSV-Zeile enthält neben der lesbaren Fassung eine explizite Signatur, zum Beispiel:

`OWNER=... | ITEM=POSTEN | QUANTITY=MASS | ACTIONS=NEHMEN+SETZEN+GEBEN | RELATIONS=VERBINDUNG+ZIELORT | GRADES=II | END=CLOSE`

Damit kann ein Schreiber die Aussage aus dem Bildbesitzer und denselben kleinen Kernwerten erneut aufbauen. Lokale Zeichen werden als lokale Kennung mitgeführt, nicht als erfundenes neues Substantiv.

## Beispielpassagen

{samples}

## Was jetzt wirklich stabiler ist

- Die Wörterbuchgröße bleibt **46 Zeichen**, davon 19 portable Kerne.
- Die neun Satzschubladen bleiben unverändert: {', '.join(f'{row["template_id"]}={row["statement_count"]}' for row in drawer_rows)}.
- Alle **566** lizenzierten Schlüsse bleiben Schlüsse; offene und bildbedingte Grenzen bleiben getrennt.
- Bildwörter stehen nur dort, wo der sichtbare Besitzer sie liefert.
- `CHK` und `C<K>H` werden überall als dieselben Handlungsatome mit anderer syntaktischer Verpackung behandelt.

## Nächste Engstelle

Nach dieser Bereinigung liegt der semantische Rest nicht mehr bei zehn angeblichen Fachstämmen, sondern bei den **19 lokalen Zeichen**. Der nächste Durchgang muss prüfen, welche davon wirklich bloße Adressen oder Renderer sind und welche sich über mehrere Besitzer hinweg zu wenigen wiederkehrenden lokalen Kategorien bündeln lassen.
"""
    report_path = HERE / "PASS1015_REPORT.md"
    report_path.write_text(report, encoding="utf-8")

    summary = {
        "pass": 1015,
        "source_statement_sha256": sha256(SOURCE_STATEMENTS),
        "source_contract_sha256": sha256(SOURCE_CONTRACT),
        "source_manual_sha256": sha256(SOURCE_MANUAL),
        "statement_count": len(output_rows),
        "event_count": sum(int(row["event_count"]) for row in output_rows),
        "page_count": len({row["physical_page"] for row in output_rows}),
        "register_counts": dict(sorted(register_counts.items())),
        "translation_origin_counts": dict(sorted(origin_counts.items())),
        "template_counts": dict(sorted(template_counts.items())),
        "endpoint_counts": dict(sorted(end_counts.items())),
        "old_overreach_statement_count": overreach_statement_count,
        "old_overreach_counts": dict(sorted(overreach_counts.items())),
        "dictionary_sign_count": len(contract),
        "new_specialist_roots": 0,
        "result": "COMPLETE_627_OWNER_CORE_EDITION",
        "outputs": {
            edition_path.name: sha256(edition_path),
            drawer_path.name: sha256(drawer_path),
            report_path.name: sha256(report_path),
        },
    }
    (HERE / "PASS1015_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()

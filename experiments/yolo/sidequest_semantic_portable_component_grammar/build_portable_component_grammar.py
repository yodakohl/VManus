#!/usr/bin/env python3
"""Build a small creative component language from the 44 shared surfaces."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
COMMON = ROOT / "experiments/yolo/sidequest_semantic_common_44_card_lexicon"
UNIQUE = ROOT / "experiments/yolo/sidequest_semantic_unique_master_glosses"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: str(row.get(field, "")) for field in fields})


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


COMPONENTS = [
    ("A01", "AIIN", "VORGABEWERT", "ARGUMENT", "aiin / okaiin / otaiin"),
    ("A02", "AIN", "ANTEIL", "ARGUMENT", "okain / orain / ykain"),
    ("A03", "AR", "VOM AUSGANG", "DIRECTION", "char / otar / qokar"),
    ("A04", "AL", "ZUM ZIEL", "DIRECTION", "dal / okal / otal"),
    ("A05", "Y", "AKTUELLER POSTEN", "REFERENT", "y / chdy / otchey"),
    ("A06", "OK", "SETZEN", "OPERATION", "oky / okey / okal"),
    ("A07", "OL", "FORTSETZEN", "ORDER", "ol / oldy / otol"),
    ("A08", "OT", "FOLGEND", "ORDER", "otar / otchey / oteey"),
    ("A09", "E", "KURZ", "GRADE", "okey / kchey / otedy"),
    ("A10", "EE", "LÄNGER", "GRADE", "okeey / oteey / sheey"),
    ("A11", "EEE", "VOLLSTÄNDIG", "GRADE", "qokeeedy"),
    ("A12", "CHD", "ÜBERTRAGEN", "OPERATION", "chdy / otchdy / dchedy"),
    ("A13", "OR", "ANSATZ ODER SATZ", "OBJECT", "or / olor / otchor"),
    ("A14", "HO", "EINGANGSPOSTEN", "OBJECT", "cho / chochor / chodaly"),
    ("A15", "KCH", "BEARBEITEN", "OPERATION", "kchy / kchey / kchal"),
    ("A16", "SH", "HALTEN", "STATE", "sheey / rsheal / dsheol"),
    ("A17", "CLOSE", "SCHLIESSEN", "CLOSURE", "oldy / qokedy / otchdy"),
    ("W01", "CHEEY", "FREIGEGEBENER WERT", "LEARNED_WHOLE_CARD", "cheey / shey"),
    ("W02", "DAIN", "ABDECKTRÄGER", "LEARNED_WHOLE_CARD", "dain"),
    ("W03", "ODY", "ZURÜCKNEHMEN", "LEARNED_WHOLE_CARD", "ody"),
    ("W04", "OS", "UMSCHLIESSENDER TRÄGER", "LEARNED_WHOLE_CARD", "os"),
]


SEED_PARSE_BY_MC = {
    "MC039": "AIIN", "MC055": "AR", "MC074": "CHD+Y", "MC154": "AL",
    "MC119": "CHEEY", "MC123": "Y", "MC034": "HO", "MC026": "OK+Y",
    "MC153": "OL", "MC059": "DAIN", "MC122": "KCH+E+Y", "MC117": "KCH+Y",
    "MC100": "ODY", "MC017": "OK+AIN", "MC040": "OK+AL", "MC103": "OK+Y",
    "MC002": "OK+EE+Y", "MC007": "OK+E+Y", "MC019": "OL+CLOSE",
    "MC157": "OL+OR", "MC080": "OR", "MC159": "OS", "MC121": "OT+AR",
    "MC067": "OT+CHD+CLOSE", "MC171": "OT+Y", "MC063": "OT+EE+Y",
    "MC053": "OT+OL", "MC140": "OK+EEE+CLOSE", "MC095": "SH+EE+Y",
}


PREDICTIONS = {
    "chary": ("AR+Y", "POSTEN VOM AUSGANG"),
    "chdal": ("CHD+AL", "ZUM ZIEL ÜBERTRAGEN"),
    "chedain": ("CHD+AIN", "ANTEIL ÜBERTRAGEN"),
    "cheedar": ("CHD+AR", "VOM AUSGANG ÜBERTRAGEN"),
    "chochor": ("HO+OR", "EINGANGSANSATZ"),
    "chodaiin": ("HO+AIIN", "EINGANGSWERT"),
    "chodaly": ("HO+AL+Y", "EINGANGSPOSTEN ZUM ZIEL"),
    "choy": ("HO+Y", "AKTUELLER EINGANGSPOSTEN"),
    "chkain": ("AIN", "ANTEIL"),
    "kchal": ("KCH+AL", "AM ZIEL BEARBEITEN"),
    "kchol": ("KCH+OL", "WEITER BEARBEITEN"),
    "keol": ("E+OL", "KURZ FORTSETZEN"),
    "teol": ("E+OL", "KURZ FORTSETZEN"),
    "okaiin": ("OK+AIIN", "AUF VORGABEWERT SETZEN"),
    "qokar": ("OK+AR", "VOM AUSGANG SETZEN"),
    "qokaly": ("OK+AL+Y", "AKTUELLEN POSTEN AM ZIEL SETZEN"),
    "qokedy": ("OK+E+CLOSE", "KURZ SETZEN; SCHLUSS"),
    "qokeedy": ("OK+EE+CLOSE", "LÄNGER SETZEN; SCHLUSS"),
    "qokchdy": ("OK+CHD+CLOSE", "SETZEN UND ÜBERTRAGEN; SCHLUSS"),
    "okchedy": ("OK+CHD+CLOSE", "SETZEN UND ÜBERTRAGEN; SCHLUSS"),
    "okchol": ("OK+OL", "FORTSETZUNG SETZEN"),
    "okeeol": ("OK+EE+OL", "LÄNGER FORTSETZEN"),
    "otaiin": ("OT+AIIN", "FOLGEWERT"),
    "otal": ("OT+AL", "DANACH ZUM ZIEL"),
    "otchor": ("OT+OR", "FOLGEANSATZ"),
    "otedy": ("OT+E+CLOSE", "KURZE FOLGE; SCHLUSS"),
    "qotedaiin": ("OT+E+AIIN", "KURZER FOLGEWERT"),
    "qoteedy": ("OT+EE+CLOSE", "LANGE FOLGE; SCHLUSS"),
    "qolchey": ("OL+Y", "AKTUELLEN POSTEN FORTSETZEN"),
    "qotchol": ("OT+OL", "DANACH FORTSETZEN"),
    "qotchy": ("OT+Y", "FOLGEPOSTEN"),
    "orain": ("OR+AIN", "ANSATZANTEIL"),
    "olkain": ("OL+AIN", "WEITERER ANTEIL"),
    "ykaiin": ("Y+AIIN", "POSTENWERT"),
    "ykain": ("Y+AIN", "POSTENANTEIL"),
    "raly": ("AL+Y", "AKTUELLEN POSTEN ZUM ZIEL"),
    "ral": ("AL", "ZUM ZIEL"),
    "rol": ("OL", "FORTSETZEN"),
    "rsheal": ("SH+E+AL", "KURZ AM ZIEL HALTEN"),
    "dchdy": ("CHD+CLOSE", "ÜBERTRAGEN; SCHLUSS"),
    "dchedy": ("CHD+CLOSE", "ÜBERTRAGEN; SCHLUSS"),
    "dalchdy": ("AL+CHD+CLOSE", "ZUM ZIEL ÜBERTRAGEN; SCHLUSS"),
    "olchedy": ("OL+CHD+CLOSE", "WEITER ÜBERTRAGEN; SCHLUSS"),
    "otchedy": ("OT+CHD+CLOSE", "FOLGEPOSTEN ÜBERTRAGEN; SCHLUSS"),
    "schoal": ("HO+AL", "EINGANGSPOSTEN ZUM ZIEL"),
    "dsheol": ("SH+E+OL", "KURZ HALTEN UND FORTSETZEN"),
}


PASSAGE_READINGS = {
    "H2-S002": "Nimm den Folgeansatz, führe Ansatz und Fortsetzungsansatz weiter, stelle den Vorgabewert ein und entnimm ihn vom Ausgang.",
    "H5-S001": "Setze einen Eingangsansatz an, bringe den Eingangsposten zum Ziel, nimm den Vorgabewert, bearbeite weiter, beginne den Folgeansatz und setze den aktuellen Posten am Ziel.",
    "B1-S002": "Setze den Vorgabewert, setze das Beckenwasser am Ziel an, nimm vom Ausgang, führe weiter, gib Anteil und weiteren Anteil zum Ziel, halte dort länger, übertrage und schließe.",
    "B3-S032": "Übertrage einen Anteil und den aktuellen Posten, setze den kurzen Folgewert und den Folgewert, führe die kurze Folge aus und schließe.",
}


def main() -> None:
    common_lexicon = read_tsv(COMMON / "COMMON_44_CARD_LEXICON.tsv")
    common_reader = read_tsv(COMMON / "TEN_PAGE_776_COMMON_READER.tsv")
    dictionary = read_tsv(UNIQUE / "UNIQUE_173_MASTER_DICTIONARY.tsv")
    events = read_tsv(UNIQUE / "UNIQUE_381_EVENT_INTERLINEAR.tsv")
    statements = read_tsv(UNIQUE / "UNIQUE_116_STATEMENT_EDITION.tsv")

    dictionary_by_mc = {row["master_card_id"]: row for row in dictionary}
    dictionary_by_head = {row["master_head_form"]: row for row in dictionary}
    if len(dictionary_by_mc) != 173 or len(dictionary_by_head) != 173:
        raise ValueError("master dictionary is not uniquely keyed")
    if set(SEED_PARSE_BY_MC) != {row["prose_master_card_id"] for row in common_lexicon}:
        raise ValueError("29 seed parses do not equal the shared-surface master-card inventory")
    if not set(PREDICTIONS).issubset(dictionary_by_head):
        raise ValueError(f"missing predicted heads: {sorted(set(PREDICTIONS) - set(dictionary_by_head))}")
    predicted_mcs = {dictionary_by_head[head]["master_card_id"] for head in PREDICTIONS}
    if predicted_mcs & set(SEED_PARSE_BY_MC):
        raise ValueError("a predicted card is already a common seed card")

    component_rows = []
    for component_id, symbol, meaning, component_class, examples in COMPONENTS:
        component_rows.append({
            "component_id": component_id,
            "symbol": symbol,
            "short_meaning_de": meaning,
            "component_class": component_class,
            "composition_position_de": {
                "ARGUMENT": "bei Posten, Maß oder Wert",
                "DIRECTION": "vor oder nach der Handlung",
                "REFERENT": "als laufender Gegenstand",
                "OPERATION": "als Handlungskern",
                "ORDER": "vor der folgenden Handlung",
                "GRADE": "zwischen Handlung und Referent oder Schluss",
                "OBJECT": "als Arbeitsgegenstand",
                "STATE": "als Haltehandlung",
                "CLOSURE": "immer am Kartenende",
                "LEARNED_WHOLE_CARD": "unteilbar auswendig lernen",
            }[component_class],
            "observed_examples": examples,
            "apprentice_gloss_de": f"{symbol} heißt immer kurz {meaning}",
        })
    write_tsv(
        OUT / "PORTABLE_17_ATOMS_AND_4_WHOLE_CARDS.tsv",
        component_rows,
        ["component_id", "symbol", "short_meaning_de", "component_class", "composition_position_de", "observed_examples", "apprentice_gloss_de"],
    )

    surfaces_by_mc: dict[str, list[str]] = defaultdict(list)
    nucleus_by_mc: dict[str, str] = {}
    for row in common_lexicon:
        mc = row["prose_master_card_id"]
        surfaces_by_mc[mc].append(row["visible_surface"])
        old = nucleus_by_mc.setdefault(mc, row["common_nucleus_de"])
        if old != row["common_nucleus_de"]:
            raise ValueError(f"shared master card has two nuclei: {mc}")
    event_counts = Counter(row["master_card_id"] for row in events)
    seed_rows = []
    for mc in sorted(SEED_PARSE_BY_MC):
        card = dictionary_by_mc[mc]
        seed_rows.append({
            "master_card_id": mc,
            "master_head_form": card["master_head_form"],
            "shared_visible_surfaces": ";".join(sorted(surfaces_by_mc[mc])),
            "atom_sequence": SEED_PARSE_BY_MC[mc],
            "portable_nucleus_de": nucleus_by_mc[mc],
            "current_prose_meaning_de": card["unique_short_meaning_de"],
            "prose_event_count": event_counts[mc],
            "composition_mode": "PORTABLE_ATOM_COMPOSITION" if SEED_PARSE_BY_MC[mc] not in {"CHEEY", "DAIN", "ODY", "OS"} else "LEARNED_PORTABLE_WHOLE_CARD",
        })
    write_tsv(
        OUT / "SEED_29_MASTER_CARD_COMPOSITIONS.tsv",
        seed_rows,
        ["master_card_id", "master_head_form", "shared_visible_surfaces", "atom_sequence", "portable_nucleus_de", "current_prose_meaning_de", "prose_event_count", "composition_mode"],
    )

    prediction_rows = []
    prediction_by_mc: dict[str, tuple[str, str]] = {}
    for head in sorted(PREDICTIONS):
        atoms, nucleus = PREDICTIONS[head]
        card = dictionary_by_head[head]
        mc = card["master_card_id"]
        prediction_by_mc[mc] = (atoms, nucleus)
        prediction_rows.append({
            "master_card_id": mc,
            "master_head_form": head,
            "registered_surface_family": card["registered_surface_family"],
            "atom_sequence": atoms,
            "predicted_nucleus_de": nucleus,
            "existing_short_meaning_de": card["unique_short_meaning_de"],
            "source_component_formula": card["component_reading"],
            "prose_event_count": event_counts[mc],
            "prediction_use_de": "aus bekannten Kurzbausteinen lesen statt als neue Ganzkarte lernen",
        })
    write_tsv(
        OUT / "PREDICTED_ADDITIONAL_PROSE_CARDS.tsv",
        prediction_rows,
        ["master_card_id", "master_head_form", "registered_surface_family", "atom_sequence", "predicted_nucleus_de", "existing_short_meaning_de", "source_component_formula", "prose_event_count", "prediction_use_de"],
    )

    event_by_id = {row["event_id"]: row for row in events}
    surface_to_mc = {row["visible_surface"]: row["prose_master_card_id"] for row in common_lexicon}
    reader_rows = []
    for row in common_reader:
        if row["register"] == "PROSE":
            event = event_by_id[row["source_group_id"]]
            mc = event["master_card_id"]
            if mc in SEED_PARSE_BY_MC:
                status = "SHARED_SEED_CARD"
                atoms = SEED_PARSE_BY_MC[mc]
                nucleus = nucleus_by_mc[mc]
            elif mc in prediction_by_mc:
                status = "PREDICTED_FROM_PORTABLE_ATOMS"
                atoms, nucleus = prediction_by_mc[mc]
            else:
                status = "LOCAL_LEARNED_CARD"
                atoms = "LOCAL_WHOLE"
                nucleus = row["final_register_reading_de"]
        elif row["shared_card_status"] == "COMMON_44_CARD":
            mc = surface_to_mc[row["visible_surface"]]
            status = "SHARED_SEED_CARD"
            atoms = SEED_PARSE_BY_MC[mc]
            nucleus = nucleus_by_mc[mc]
        else:
            status = "LOCAL_ASTRO_CARD"
            atoms = "LOCAL_OWNER_VALUE"
            nucleus = row["final_register_reading_de"]
        reader_rows.append({
            **row,
            "portable_component_status": status,
            "portable_atom_sequence": atoms,
            "portable_nucleus_de": nucleus,
            "final_local_expansion_de": row["final_register_reading_de"],
        })
    reader_fields = list(common_reader[0]) + [
        "portable_component_status", "portable_atom_sequence", "portable_nucleus_de", "final_local_expansion_de",
    ]
    write_tsv(OUT / "TEN_PAGE_776_PORTABLE_COMPONENT_READER.tsv", reader_rows, reader_fields)

    statement_by_id = {row["statement_id"]: row for row in statements}
    passage_lines = [
        "# Vier Passagen mit der gemeinsamen Kompositionssprache", "",
        "Die linke Seite liest jede Meisterkarte aus kurzen Bausteinen; die flüssige Zeile setzt erst danach Besitzer und Werkstattgegenstand ein.", "",
    ]
    for statement_id, new_reading in PASSAGE_READINGS.items():
        statement = statement_by_id[statement_id]
        passage_lines += [f"## {statement_id} · {statement['page']} · {statement['loci']}", "", f"**Sichtbar:** `{statement['surface_sequence']}`", "", "**Kartenweise:**", ""]
        for event in (row for row in events if row["statement_id"] == statement_id):
            mc = event["master_card_id"]
            if mc in SEED_PARSE_BY_MC:
                atoms = SEED_PARSE_BY_MC[mc]
                nucleus = nucleus_by_mc[mc]
                status = "gemeinsame Meisterkarte"
            elif mc in prediction_by_mc:
                atoms, nucleus = prediction_by_mc[mc]
                status = "aus gemeinsamen Atomen vorhergesagt"
            else:
                atoms = "LOCAL_WHOLE"
                nucleus = event["unique_short_meaning_de"].upper()
                status = "lokale Ganzkarte"
            passage_lines.append(f"- `{event['surface_display']}` → `{atoms}` → **{nucleus}** ({status})")
        passage_lines += ["", f"**Neue flüssige Lesung:** {new_reading}", "", f"**Bisherige Lesung:** {statement['fluent_workshop_sentence_de']}", ""]
    (OUT / "FOUR_REWRITTEN_COMPONENT_PASSAGES.md").write_text("\n".join(passage_lines).rstrip() + "\n", encoding="utf-8")

    status_counts = Counter(row["portable_component_status"] for row in reader_rows)
    predicted_events = sum(event_counts[mc] for mc in prediction_by_mc)
    seed_events = sum(event_counts[mc] for mc in SEED_PARSE_BY_MC)
    prose_portable = seed_events + predicted_events
    report = f"""# Portable Kompositionssprache der zehn Seiten

## Der neue Kern

Die 44 gemeinsamen sichtbaren Formen sind keine 44 unabhängigen Wörter. In der Prosa gehören sie zu nur 29 Meisterkarten. Diese 29 Karten lassen sich mit 17 kurzen Atomen und vier gelernten Ganzkarten schreiben: Wert, Anteil, Ausgang, Ziel, aktueller Posten, Setzen, Fortsetzen, Folge, drei Grade, Übertragen, Ansatz, Eingang, Bearbeiten, Halten und Schluss; daneben bleiben CHEEY, DAIN, ODY und OS als kleine auswendig gelernte Brückenkarten.

Diese Sprache liest nicht `shey` als ganzen Satz und nicht `or` als konkrete Arznei. Sie liest zuerst **freigegebener Wert** oder **Ansatz/Satz**; Bild und Register liefern danach Klarauszug, Diagrammwert, Zubereitung oder Bedingungssatz.

## Der eigentliche Fortschritt

Die 29 gemeinsamen Meisterkarten decken {seed_events} Prosaereignisse. Ihre Atome sagen weitere {len(PREDICTIONS)} bisher nicht gemeinsame Meisterkarten mit {predicted_events} Prosaereignissen voraus. Damit werden {len(SEED_PARSE_BY_MC) + len(PREDICTIONS)} von 173 Prosakarten und {prose_portable} von 381 Prosaereignissen aus derselben kleinen Sprache lesbar; sie müssen nicht mehr einzeln auswendig gelernt werden. Auf den Diagrammseiten bleiben die 89 gemeinsamen Vorkommen anschließbar. Im vollständigen Reader tragen damit {status_counts['SHARED_SEED_CARD'] + status_counts['PREDICTED_FROM_PORTABLE_ATOMS']} von 776 sichtbaren Gruppen eine portable Atomlesung.

Die produktivsten Vorhersagen sind:

- `OT + OR = FOLGEANSATZ`, `OT + AIIN = FOLGEWERT`, `OT + E + CLOSE = KURZE FOLGE; SCHLUSS`;
- `OK + AIIN = AUF VORGABEWERT SETZEN`, `OK + AL + Y = AKTUELLEN POSTEN AM ZIEL SETZEN`;
- `CHD + AIN = ANTEIL ÜBERTRAGEN`, `OL + CHD + CLOSE = WEITER ÜBERTRAGEN; SCHLUSS`;
- `HO + OR = EINGANGSANSATZ`, `HO + AL + Y = EINGANGSPOSTEN ZUM ZIEL`;
- `Y + AIIN = POSTENWERT`, `OR + AIN = ANSATZANTEIL`, `OL + AIN = WEITERER ANTEIL`.

## Vier lesbare Folgen

`H2-S002` wird fast vollständig zu Folgeansatz → Ansatz → danach fortsetzen → fortsetzen → Fortsetzungsansatz → fortsetzen → Vorgabewert → vom Ausgang. `H5-S001` liest sich als Eingangsposten, Ziel, Wert, Weiterbearbeitung und Folgeansatz. `B1-S002` zeigt Wert, Ziel, Quelle, Portion, Fortsetzung, längeres Halten und Schluss. `B3-S032` ist eine besonders saubere Kurzform aus Anteilübertragung, aktuellem Posten, Folgewert und Schluss.

## Werkstattregel

Der Lehrling lernt 17 Atome, vier Brückenkarten und die Reihenfolge **ORDER → OPERATION → ARGUMENT/DIRECTION → GRADE → REFERENT oder CLOSE**. Schreiberrahmen wie `q`, `s`, `ch`, `d`, `r` oder `t` dürfen die sichtbare Form wechseln, erhalten aber in dieser kleinen Sprache keinen zusätzlichen Sachwert. Eine Karte außerhalb dieser Kombinationen bleibt eine lokale gelernte Ganzkarte.
"""
    (OUT / "PORTABLE_COMPONENT_GRAMMAR_REPORT.md").write_text(report, encoding="utf-8")

    pocket_lines = [
        "# Taschenkarte der portablen Kompositionssprache", "",
        "## Die siebzehn Atome", "",
    ]
    for row in component_rows[:17]:
        pocket_lines.append(f"- `{row['symbol']}` = **{row['short_meaning_de']}** — {row['composition_position_de']}")
    pocket_lines += ["", "## Vier gelernte Brückenkarten", ""]
    for row in component_rows[17:]:
        pocket_lines.append(f"- `{row['symbol']}` = **{row['short_meaning_de']}**")
    pocket_lines += ["", "## Schreibfolge", "", "`ORDER → OPERATION → ARGUMENT/DIRECTION → GRADE → Y oder CLOSE`", "", "Beispiele:", "", "- `OT+OR` → Folgeansatz", "- `OK+AIIN` → auf Vorgabewert setzen", "- `OL+CHD+CLOSE` → weiter übertragen; Schluss", "- `HO+AL+Y` → Eingangsposten zum Ziel", "- `SH+E+AL` → kurz am Ziel halten", ""]
    (OUT / "PORTABLE_COMPONENT_POCKET_CARD.md").write_text("\n".join(pocket_lines), encoding="utf-8")

    content_names = [
        "PORTABLE_17_ATOMS_AND_4_WHOLE_CARDS.tsv", "SEED_29_MASTER_CARD_COMPOSITIONS.tsv",
        "PREDICTED_ADDITIONAL_PROSE_CARDS.tsv", "TEN_PAGE_776_PORTABLE_COMPONENT_READER.tsv",
        "FOUR_REWRITTEN_COMPONENT_PASSAGES.md", "PORTABLE_COMPONENT_GRAMMAR_REPORT.md",
        "PORTABLE_COMPONENT_POCKET_CARD.md",
    ]
    summary = {
        "status": "BUILT",
        "portable_atoms": 17,
        "learned_bridge_cards": 4,
        "shared_visible_surfaces": len(common_lexicon),
        "shared_master_seed_cards": len(SEED_PARSE_BY_MC),
        "predicted_additional_prose_cards": len(PREDICTIONS),
        "portable_prose_card_types": len(SEED_PARSE_BY_MC) + len(PREDICTIONS),
        "seed_prose_events": seed_events,
        "predicted_prose_events": predicted_events,
        "portable_prose_events": prose_portable,
        "astro_seed_events": sum(row["register"] == "ASTRO" and row["portable_component_status"] == "SHARED_SEED_CARD" for row in reader_rows),
        "portable_unified_groups": status_counts["SHARED_SEED_CARD"] + status_counts["PREDICTED_FROM_PORTABLE_ATOMS"],
        "complete_reader_groups": len(reader_rows),
        "rewritten_passages": len(PASSAGE_READINGS),
        "source_sha256": {
            "common_44_lexicon": sha256(COMMON / "COMMON_44_CARD_LEXICON.tsv"),
            "common_776_reader": sha256(COMMON / "TEN_PAGE_776_COMMON_READER.tsv"),
            "unique_173_dictionary": sha256(UNIQUE / "UNIQUE_173_MASTER_DICTIONARY.tsv"),
            "unique_381_events": sha256(UNIQUE / "UNIQUE_381_EVENT_INTERLINEAR.tsv"),
        },
        "output_sha256": {name: sha256(OUT / name) for name in content_names},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

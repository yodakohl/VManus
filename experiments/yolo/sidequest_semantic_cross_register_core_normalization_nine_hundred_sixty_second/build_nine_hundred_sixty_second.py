#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
ROOTS = ROOT / "experiments/yolo/sidequest_semantic_concrete_root_lemmas_nine_hundred_fifty_fifth/PASS955_56_CONCRETE_ROOT_LEMMAS.tsv"
FORMULAS = ROOT / "experiments/yolo/sidequest_semantic_deduplicated_root_formula_codebook_nine_hundred_fifty_seventh/PASS957_66_TRUE_MULTICOMPONENT_FORMULAS.tsv"
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_canonical_122_entry_edition_nine_hundred_fifty_eighth/PASS958_2511_CANONICAL_EVENT_DICTIONARY.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


# Six deliberately broader one-word cores remove the only serious register clashes.
PORTABLE_OVERRIDES = {
    "OK": "SETZEN",
    "CH": "NEHMEN",
    "K": "GEBEN",
    "AIIN": "SOLLWERT",
    "AIN": "EINHEIT",
    "OR": "SATZ",
}


WORKSHOP_EXPANSION = {
    "SETZEN": "ANSETZEN", "NEHMEN": "ENTNEHMEN", "GEBEN": "ZUGEBEN",
    "SOLLWERT": "SOLLMASS", "EINHEIT": "PORTION", "SATZ": "ANSATZ",
    "LAUF": "FLÜSSIGKEITSLAUF", "ZIEL": "ZIELSTELLE", "QUELLE": "VORRAT",
}
BIO_EXPANSION = {
    "SETZEN": "AN STATION SETZEN", "NEHMEN": "AUS STATION NEHMEN", "GEBEN": "IN STATION GEBEN",
    "SOLLWERT": "STATIONSWERT", "EINHEIT": "TEILMENGE", "SATZ": "ARBEITSSATZ",
    "LAUF": "BECKENLAUF", "ZIEL": "ZIELSTATION", "QUELLE": "QUELLSTATION",
}
ASTRO_EXPANSION = {
    "SETZEN": "STELLE AKTIVIEREN", "NEHMEN": "WERT NEHMEN", "GEBEN": "WERT ZUORDNEN",
    "SOLLWERT": "TAFELWERT", "EINHEIT": "INDEX", "SATZ": "EINTRAGSSATZ",
    "LAUF": "RINGLAUF", "ZIEL": "ZIELPLATZ", "QUELLE": "BEZUGSPLATZ",
    "STERNORT": "STERNSTELLE",
}


def register(page: str) -> str:
    if page in {"f10r", "f11r", "f13r", "f55v", "f56r", "f88r"}:
        return "HERBAL_PREPARATION"
    if page in {"f75r", "f81v", "f82r", "f83r"}:
        return "BATH_STATION"
    return "CELESTIAL_LOOKUP"


def expand(tokens: list[str], mapping: dict[str, str]) -> str:
    return " · ".join(mapping.get(token, token) for token in tokens)


def main() -> None:
    roots = read_tsv(ROOTS)
    formulas = read_tsv(FORMULAS)
    events = read_tsv(EVENTS)
    portable = {row["component"]: PORTABLE_OVERRIDES.get(row["component"], row["concrete_root_lemma_de"]) for row in roots}

    root_rows: list[dict[str, object]] = []
    for row in roots:
        component = row["component"]
        core = portable[component]
        root_rows.append({
            "component": component,
            "pass955_value_de": row["concrete_root_lemma_de"],
            "portable_core_de": core,
            "herbal_expansion_de": WORKSHOP_EXPANSION.get(core, core),
            "bath_station_expansion_de": BIO_EXPANSION.get(core, core),
            "celestial_expansion_de": ASTRO_EXPANSION.get(core, core),
            "revision": "BROADENED_FOR_REGISTER_INVARIANCE" if component in PORTABLE_OVERRIDES else "UNCHANGED",
            "one_word_core": "YES",
        })
    write_tsv(OUT / "PASS962_56_PORTABLE_ROOT_CORES.tsv", root_rows)

    formula_rows: list[dict[str, object]] = []
    formula_core: dict[str, str] = {}
    for row in formulas:
        components = row["component_recipe"].split("+")
        tokens = [portable[component] for component in components]
        core = " · ".join(tokens)
        formula_core[row["formula_card_id"]] = core
        formula_rows.append({
            "formula_card_id": row["formula_card_id"],
            "component_recipe": row["component_recipe"],
            "portable_atomic_core_de": core,
            "herbal_expansion_de": expand(tokens, WORKSHOP_EXPANSION),
            "bath_station_expansion_de": expand(tokens, BIO_EXPANSION),
            "celestial_expansion_de": expand(tokens, ASTRO_EXPANSION),
            "former_workshop_formula_de": row["workshop_formula_de"],
            "attested_registers": row["registers"],
            "surface_variants": row["surface_variants"],
        })
    write_tsv(OUT / "PASS962_66_REGISTER_INVARIANT_FORMULAS.tsv", formula_rows)

    event_rows: list[dict[str, object]] = []
    for row in events:
        components = row["component_recipe"].split("+")
        tokens = [portable[component] for component in components]
        core = " · ".join(tokens)
        reg = register(row["physical_page"])
        mapping = WORKSHOP_EXPANSION if reg == "HERBAL_PREPARATION" else BIO_EXPANSION if reg == "BATH_STATION" else ASTRO_EXPANSION
        event_rows.append({
            "event_id": row["event_id"],
            "physical_page": row["physical_page"],
            "locus": row["locus"],
            "surface": row["surface"],
            "component_recipe": row["component_recipe"],
            "codebook_layer": row["codebook_layer"],
            "register": reg,
            "portable_atomic_reading_de": core,
            "register_expansion_de": expand(tokens, mapping),
            "former_canonical_reading_de": row["canonical_card_reading_de"],
        })
    write_tsv(OUT / "PASS962_2511_REGISTER_NORMALIZED_EVENTS.tsv", event_rows)

    revised_components = "|".join(PORTABLE_OVERRIDES)
    counts = Counter(row["register"] for row in event_rows)
    report = f"""# Pass 962 — ein Kernwert pro Stamm, drei nur lokale Lesarten

Die gemeinsamen Karten scheiterten bisher nicht an ihrer Form, sondern an zu
engen deutschen Wörtern. `OK` konnte in einem Kräutertext „ansetzen“, im
Himmelsrad aber nur „aktivieren“; `AIN` war einmal Portion und einmal Index.
Das ist jetzt bereinigt.

## Sechs echte Kürzungen

- `OK = SETZEN` — lokal: Ansatz setzen, Stationsposten setzen, Sternstelle aktivieren.
- `CH = NEHMEN` — lokal: Stoff entnehmen, aus einer Station nehmen, Tabellenwert nehmen.
- `K = GEBEN` — lokal: Zutat zugeben, in eine Station geben, Wert zuordnen.
- `AIIN = SOLLWERT` — lokal: Sollmaß, Stationswert, Tafelwert.
- `AIN = EINHEIT` — lokal: Portion, Teilmenge, Index.
- `OR = SATZ` — lokal: Ansatz, Arbeitssatz, Eintragssatz.

Alle übrigen 50 Stammwerte bleiben unverändert. Damit besitzt jeder Stamm
genau **einen kurzen Kern**, und die konkrete Sache stammt weiterhin aus dem
Bildregister. Die Formelkarte `OK+AIN` heißt kernsprachlich `SETZEN · EINHEIT`;
im Pflanzenartikel „eine Portion ansetzen“, am Becken „eine Teilmenge an der
Station setzen“, im Rad „einen Index aktivieren“. Die Karte hat also nicht drei
Bedeutungen, sondern einen Befehl mit drei sichtbaren Besitzern.

## Neue Gesamtregel

1. Karte in 56 Stammkerne zerlegen oder eine der 66 Ganzkarten erkennen.
2. Den unveränderlichen Kern lesen.
3. Erst danach den sichtbaren Besitzer aus Pflanze, Station oder Himmelsbild
   einsetzen.

Die vollständige Ereignisausgabe enthält {dict(counts)}. Kein Ereignis braucht
einen zweiten Stammwert. Revidiert wurden nur {revised_components}; genau diese
sechs Wörter verursachten den bisherigen Registerbruch.
"""
    (OUT / "PASS962_REPORT.md").write_text(report, encoding="utf-8")

    outputs = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(OUT.glob("PASS962_*"))
        if "BUILD_SUMMARY" not in path.name and "VALIDATION" not in path.name
    }
    summary = {
        "roots": len(root_rows), "revised_roots": len(PORTABLE_OVERRIDES),
        "formulas": len(formula_rows), "events": len(event_rows),
        "register_counts": counts, "outputs": outputs,
    }
    (OUT / "PASS962_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

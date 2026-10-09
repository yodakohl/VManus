#!/usr/bin/env python3
"""Fast, deliberately exploratory stem pass over the fixed V80 ten-page deck."""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
V80 = ROOT / "experiments/yolo/sidequest_theory_candidates_v80"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def canonical_form(display: str) -> str:
    return min(display.split("|"), key=lambda value: (len(value), value))


def atom_parse(form: str) -> list[tuple[str, str]]:
    """Return a permissive workshop parse, not a linguistic segmentation."""
    exact = {
        "y": [("Y", "DIES")],
        "aiin": [("AIIN", "MASS")],
        "ol": [("OL", "UND/MIT")],
        "cthy": [("CTHY", "BEREIT")],
        "lchedy": [("LCH", "ABLEITEN"), ("DY", "FERTIG")],
        "chdy": [("CH", "MISCHEN"), ("DY", "FERTIG")],
        "tedy": [("E", "RUHEN"), ("DY", "FERTIG")],
        "shey": [("EY", "ZUSTAND")],
        "okaiin": [("OK", "AUSFÜHREN"), ("AIIN", "MASS")],
        "al": [("AL", "ZIEL")],
        "dal": [("AL", "ZIEL")],
        "ar": [("AR", "QUELLE")],
        "dar": [("AR", "QUELLE")],
        "or": [("OR", "ANSATZ")],
    }
    if form in exact:
        return exact[form]
    atoms: list[tuple[str, str]] = []
    body = form
    if body.endswith("dy") and len(body) > 2:
        atoms.append(("DY", "FERTIG"))
        body = body[:-2]
    if body.startswith("lch"):
        atoms.append(("LCH", "ABLEITEN"))
    elif body.startswith("ok"):
        atoms.append(("OK", "AUSFÜHREN"))
    elif body.startswith("ot"):
        atoms.append(("OT", "WEITERER"))
    elif body.startswith("ol"):
        atoms.append(("OL", "VERBINDEN"))
    elif body.startswith("ch") and len(body) > 3:
        atoms.append(("CH", "BEARBEITEN"))

    endings = [
        ("aiin", "MASS"),
        ("ain", "ANTEIL"),
        ("al", "ZIEL"),
        ("ar", "QUELLE"),
        ("or", "ANSATZ"),
        ("ol", "MIT"),
        ("ey", "ZUSTAND"),
    ]
    for ending, meaning in endings:
        if body.endswith(ending):
            atoms.append((ending.upper(), meaning))
            break
    if body == "y":
        atoms.append(("Y", "DIES"))
    if body == "cthy":
        atoms.append(("CTHY", "BEREIT"))
    return list(dict.fromkeys(atoms))


def compact_default(tokens: list[str], terminal_count: int, total: int) -> tuple[str, str]:
    joined = " ".join(tokens).lower()
    rules = [
        (("et?",), "UND/MIT"),
        (("per?", "vorschrift", "gemäss"), "NACH VORGABE"),
        (("bemess", "maß", "anteil", "menge", "portion"), "ABMESSEN"),
        (("station", "bezeichnete stelle", "ziel", "ablauf hin"), "ZUM ZIEL"),
        (("abführ", "ablauf", "zieh", "abgieß"), "ABLEITEN"),
        (("spül", "wasch"), "SPÜLEN"),
        (("rühr", "misch", "gleichmäßig"), "MISCHEN"),
        (("bereit", "prüfzustand", "klar", "zustand"), "ZUSTAND PRÜFEN"),
        (("temper", "warm", "erwärm", "feuer"), "ERWÄRMEN"),
        (("stehen", "setzen", "absetzen", "ruhe"), "RUHEN LASSEN"),
        (("seih", "tuch", "wring", "filter"), "SEIHEN"),
        (("nimm", "sammle"), "NEHMEN"),
        (("gib", "fülle", "gieße"), "ZUGEBEN"),
        (("gebrauch", "anwend", "lege", "trank"), "ANWENDEN"),
        (("fortführ", "weiter", "selben", "vorigen", "daraus"), "WEITER"),
        (("gefäß", "becken"), "GEFÄSS"),
        (("wasser", "flüssigkeit", "auszug", "ansatz", "charge"), "FLÜSSIGKEIT"),
        (("öffnung", "lauf", "verbunden"), "LEITUNG"),
        (("zeit", "dauer"), "ZEIT"),
        (("pflanze", "kraut", "blätter", "wurzel", "blüten"), "PFLANZENTEIL"),
        (("verwahr", "bedeckt"), "BEWAHREN"),
    ]
    for needles, gloss in rules:
        if any(needle in joined for needle in needles):
            return gloss, "MOST_COMMON_CONTEXT_COMPRESSION"
    if total and terminal_count == total:
        return "ABSCHLIESSEN", "TERMINAL_DEFAULT"
    return "LOKALER POSTEN", "OPEN_EXEMPLAR_DEFAULT"


def main() -> None:
    cards = read_tsv(V80 / "V80_CANONICAL_173_CARD_DICTIONARY.tsv")
    events = read_tsv(V80 / "V80_CANONICAL_381_PROSE_EVENT_INTERLINEAR.tsv")
    by_id: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        by_id[event["joint_tuple_id"]].append(event)

    out: list[dict[str, object]] = []
    for card in cards:
        joint = card["joint_tuple_id"]
        evs = by_id[joint]
        form = canonical_form(card["surface_examples_display_only"])
        atoms = atom_parse(form)
        token_counts = Counter(event["master_memorized_selected_token"] for event in evs)
        token_list = [token for token, _ in token_counts.most_common()]
        terminal = sum(event["terminal_status"] == "TERMINAL" for event in evs)
        gloss, source = compact_default(token_list, terminal, len(evs))
        exact_defaults = {
            "y": "DIESER POSTEN",
            "aiin": "MASS",
            "ol": "UND/MIT",
            "cthy": "BEREIT",
            "lchedy": "ABLEITEN; FERTIG",
            "chdy": "MISCHEN; FERTIG",
            "tedy": "RUHEN; FERTIG",
            "shey": "ZUSTAND PRÜFEN",
            "okaiin": "NACH VORGABE",
            "al": "ZUM ZIEL",
            "dal": "ZUM ZIEL",
            "ar": "DARAUS",
            "dar": "DARAUS",
            "or": "ANSATZ",
        }
        if form in exact_defaults:
            gloss = exact_defaults[form]
            source = "EXPLICIT_WORKSHOP_CORE_OVERRIDE"
        atom_gloss = " + ".join(meaning for _, meaning in atoms) or "GANZKARTE"
        if gloss == "LOKALER POSTEN" and atoms:
            gloss = atom_gloss
            source = "STEM_COMPOSITION_DEFAULT"
        out.append(
            {
                "joint_tuple_id": joint,
                "surface_examples": card["surface_examples_display_only"],
                "canonical_short_form": form,
                "visible_occurrences": card["visible_occurrences"],
                "pages": card["pages"],
                "workshop_atom_parse": " + ".join(f"{atom}={meaning}" for atom, meaning in atoms) or "UNGETEILTE_GANZKARTE",
                "simple_default_meaning": gloss,
                "default_source": source,
                "most_common_context": token_counts.most_common(1)[0][0] if token_counts else "NONE",
                "second_context": token_counts.most_common(2)[1][0] if len(token_counts) > 1 else "NONE",
                "terminal_share": f"{terminal}/{len(evs)}",
                "status": "CREATIVE_WORKING_DEFAULT__NOT_DECIPHERMENT",
            }
        )

    fields = list(out[0])
    write_tsv(HERE / "R4_FAST_REVISED_173_DICTIONARY.tsv", fields, out)

    stem_rows = [
        {"atom": "DY", "default": "FERTIG", "use": "Schritt/Zelle abschließen", "confidence": "HIGH_WORKING", "historical_analogue": "explicit/finis; recipe step closure"},
        {"atom": "AIIN", "default": "MASS", "use": "Menge oder lokaler Sollwert", "confidence": "HIGH_WORKING", "historical_analogue": "ana; mensura; uncia"},
        {"atom": "AL", "default": "ZIEL", "use": "zu einer Stelle/Station", "confidence": "MEDIUM_HIGH", "historical_analogue": "ad"},
        {"atom": "AR", "default": "QUELLE", "use": "daraus/vom vorigen Ansatz", "confidence": "MEDIUM", "historical_analogue": "ab/de/dictus"},
        {"atom": "OL/L", "default": "MIT", "use": "verbinden oder fortsetzen", "confidence": "MEDIUM_HIGH", "historical_analogue": "et/cum/item"},
        {"atom": "LCH", "default": "ABLEITEN", "use": "zum unteren oder nächsten Empfänger", "confidence": "MEDIUM_HIGH", "historical_analogue": "cola/effunde/transfunde"},
        {"atom": "EY", "default": "ZUSTAND", "use": "prüfen bis bereit", "confidence": "MEDIUM", "historical_analogue": "donec/fiat"},
        {"atom": "OK", "default": "AUSFÜHREN", "use": "aktiven Schritt eröffnen/anwenden", "confidence": "MEDIUM", "historical_analogue": "recipe/accipere/fac"},
        {"atom": "OT", "default": "WEITERER", "use": "anderer/nächster markierter Posten", "confidence": "LOW_MEDIUM", "historical_analogue": "item/aliud"},
        {"atom": "CTHY", "default": "BEREIT", "use": "Bereitschaft oder Prüfzustand", "confidence": "MEDIUM", "historical_analogue": "paratus/fiat"},
        {"atom": "Y", "default": "DIES", "use": "aktueller sichtbarer Posten", "confidence": "MEDIUM", "historical_analogue": "hic/iste/dictus"},
        {"atom": "Q/S/CH/D/T", "default": "SCHREIBVARIANTE", "use": "Eintritt/Position/Hand, normalerweise keine neue Bedeutung", "confidence": "HIGH_WORKING", "historical_analogue": "scribal allography and abbreviation variants"},
    ]
    write_tsv(HERE / "R4_FAST_STEM_LEXICON.tsv", list(stem_rows[0]), stem_rows)
    print(f"WROTE {len(out)} cards and {len(stem_rows)} stem rows")


if __name__ == "__main__":
    main()

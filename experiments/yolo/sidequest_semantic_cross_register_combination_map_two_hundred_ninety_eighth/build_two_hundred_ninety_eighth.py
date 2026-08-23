#!/usr/bin/env python3
"""Build the 29-family prose/Astro combination map and cross-register leads."""

from __future__ import annotations

import csv
import hashlib
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
FAMILIES = ROOT / "experiments/yolo/sidequest_semantic_root_pruning_two_hundred_ninety_seventh/TWO_HUNDRED_NINETY_SEVENTH_29_PRODUCTIVE_FAMILIES.tsv"
RECIPES = ROOT / "experiments/yolo/sidequest_semantic_final_writer_conventions_two_hundred_eighty_eighth/TWO_HUNDRED_EIGHTY_EIGHTH_149_DETERMINISTIC_RECIPES.tsv"
ASTRO = ROOT / "experiments/yolo/sidequest_semantic_astro_surface_transfer/ASTRO_395_SURFACE_PARSE.tsv"


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


def recipe_tokens(recipe: str) -> list[str]:
    return [part.split("[")[0] for part in recipe.split("+")]


ASTRO_MAP = {"CHD": "CHED_TRANSFER", "HO": "CHO_INPUT"}


LEADS = [
    ("X01", "okaiiin", "OK+IIN", "Arbeitsstufe einsetzen", "HIGH", "Astro writes the exact missing OK+stage pair."),
    ("X02", "iokeeor", "OK+OR", "Bedingungsansatz einsetzen", "HIGH", "Astro writes OK+OR with a local renderer frame."),
    ("X03", "olar", "OL+AR", "aus derselben Quelle weiter", "HIGH", "Astro supplies the exact continuation+source card."),
    ("X04", "alaiin", "AL+AIIN", "Sollwert am Ziel setzen", "HIGH", "Astro has two visible target+measure allographs, alaiin and aldaiin."),
    ("X05", "chedaiin", "CHED_TRANSFER+AIIN", "Sollwert überführen", "HIGH", "Astro puts AIIN on the right side of the transfer core."),
    ("X06", "eckhear", "AR+CKHE", "von der Quelle seihen", "HIGH", "Astro writes the missing separator+source pairing."),
    ("X07", "qotair", "AIR+OT", "zum nächsten Lauf wechseln", "HIGH", "Astro combines the next selector with the path/run family."),
    ("X08", "otcheody", "CHEO+OT", "zum nächsten Auszug wechseln", "MEDIUM", "Astro combines OT and CHEO; final local material is not imported as prose meaning."),
    ("X09", "saral", "AL+AR", "von der Quelle zum Ziel", "HIGH", "Astro explicitly places source and target in one card."),
    ("X10", "salsain", "AIN+AL", "Portion am Ziel", "HIGH", "Astro supplies a target+portion card absent from prose."),
    ("X11", "otokeeey", "OK+OT", "den folgenden Einsatz vollständig ausführen", "MEDIUM", "Astro combines OT and OK and visibly carries a full grade-like extension."),
    ("X12", "okolar", "AR+OK+OL", "einsetzen und aus gleicher Quelle fortfahren", "MEDIUM", "Astro realizes the three-family OK+OL+AR chain."),
]


def main() -> None:
    family_rows = read_tsv(FAMILIES)
    families = [row["family_id"] for row in family_rows]
    family_set = set(families)
    recipes = read_tsv(RECIPES)
    astro = read_tsv(ASTRO)

    prose_cards: Counter[tuple[str, str]] = Counter()
    prose_events: Counter[tuple[str, str]] = Counter()
    prose_surfaces: dict[tuple[str, str], set[str]] = defaultdict(set)
    for row in recipes:
        tokens = sorted(set(token for token in recipe_tokens(row["final_recipe"]) if token in family_set))
        for pair in itertools.combinations(tokens, 2):
            prose_cards[pair] += 1
            prose_events[pair] += int(row["event_support"])
            prose_surfaces[pair].add(row["canonical_form"])

    astro_groups: Counter[tuple[str, str]] = Counter()
    astro_surfaces: dict[tuple[str, str], set[str]] = defaultdict(set)
    astro_triples: dict[tuple[str, ...], set[str]] = defaultdict(set)
    for row in astro:
        raw = row["detected_literal_atoms"]
        if raw == "NONE":
            continue
        tokens = []
        for token in raw.split("+"):
            mapped = ASTRO_MAP.get(token, token)
            if mapped in family_set:
                tokens.append(mapped)
        unique = sorted(set(tokens))
        for pair in itertools.combinations(unique, 2):
            astro_groups[pair] += 1
            astro_surfaces[pair].add(row["visible_surface"])
        if len(unique) >= 3:
            for triple in itertools.combinations(unique, 3):
                astro_triples[triple].add(row["visible_surface"])

    pair_rows = []
    for left, right in itertools.combinations(sorted(families), 2):
        pair = (left, right)
        prose = prose_cards[pair]
        astro_count = astro_groups[pair]
        if prose and astro_count:
            status = "BOTH_REGISTERS"
        elif prose:
            status = "PROSE_ONLY"
        elif astro_count:
            status = "ASTRO_ONLY_VISIBLE_COMBINATION"
        else:
            status = "UNSEEN_PAIR"
        pair_rows.append({
            "family_a": left,
            "family_b": right,
            "pair": f"{left}+{right}",
            "prose_card_types": prose,
            "prose_events": prose_events[pair],
            "prose_surfaces": "|".join(sorted(prose_surfaces[pair])) or "NONE",
            "astro_groups": astro_count,
            "astro_surfaces": "|".join(sorted(astro_surfaces[pair])) or "NONE",
            "register_status": status,
            "workshop_use": "portable combination observed" if status == "BOTH_REGISTERS" else ("cross-register spelling lead" if status == "ASTRO_ONLY_VISIBLE_COMBINATION" else ("prose-licensed combination" if status == "PROSE_ONLY" else "do not invent without another parent")),
        })
    pair_path = HERE / "TWO_HUNDRED_NINETY_EIGHTH_406_FAMILY_PAIR_MAP.tsv"
    write_tsv(pair_path, pair_rows)

    triple_rows = []
    for triple, surfaces in sorted(astro_triples.items()):
        triple_rows.append({
            "family_triple": "+".join(triple),
            "astro_surface_count": len(surfaces),
            "astro_surfaces": "|".join(sorted(surfaces)),
            "prose_exact_triple_present": "YES" if any(set(triple) <= set(recipe_tokens(row["final_recipe"])) for row in recipes) else "NO",
            "interpretation": "visible three-family workshop composition; local diagram owner supplies the object",
        })
    triple_path = HERE / "TWO_HUNDRED_NINETY_EIGHTH_ASTRO_TRIPLE_COMPOSITIONS.tsv"
    write_tsv(triple_path, triple_rows)

    astro_surface_set = {row["visible_surface"] for row in astro}
    lead_rows = []
    for lead_id, surface, recipe, value, confidence, reason in LEADS:
        atoms = sorted(ASTRO_MAP.get(token, token) for token in recipe.split("+"))
        pair_statuses = []
        for pair in itertools.combinations(atoms, 2):
            canonical_pair = tuple(sorted(pair))
            pair_statuses.append(next(row["register_status"] for row in pair_rows if (row["family_a"], row["family_b"]) == canonical_pair))
        lead_rows.append({
            "lead_id": lead_id,
            "visible_astro_surface": surface,
            "productive_family_recipe": recipe,
            "proposed_prose_workshop_value_de": value,
            "confidence": confidence,
            "pair_statuses": "|".join(pair_statuses),
            "reason": reason,
            "visible_in_astro": "YES" if surface in astro_surface_set else "NO",
            "prose_use_policy": "candidate spelling only; prose owner would supply the practical object",
        })
    lead_path = HERE / "TWO_HUNDRED_NINETY_EIGHTH_12_CROSS_REGISTER_SPELLING_LEADS.tsv"
    write_tsv(lead_path, lead_rows)

    counts = Counter(row["register_status"] for row in pair_rows)
    manual = """# Kombinationskarte der 29 Familien

## Gebrauch

Die 29 produktiven Familien ergeben 406 mögliche ungeordnete Paare. Die Karte trennt vier Fälle:

- Paar in Prosa und Astro sichtbar;
- nur in Prosa sichtbar;
- nur im Astro-Register sichtbar;
- nirgends sichtbar.

Ein Astro-Treffer beweist keine medizinische Wortbedeutung. Er zeigt aber, dass die Werkstatt genau diese beiden Kürzelfamilien in einer Karte zusammenschreiben konnte. Der Besitzer des jeweiligen Registers liefert den Gegenstand.

## Zwölf sofort brauchbare Schreibungen

Besonders wertvoll sind Astro-Karten, die eine in der Prosa fehlende Kombination schon ausführen:

- `okaiiin` — OK+IIN, Arbeitsstufe einsetzen;
- `iokeeor` — OK+OR, Bedingungsansatz einsetzen;
- `olar` — OL+AR, aus derselben Quelle weiter;
- `alaiin|aldaiin` — AL+AIIN, Sollwert am Ziel;
- `chedaiin` — CHED+AIIN, Sollwert überführen;
- `eckhear` — CKHE+AR, von der Quelle seihen;
- `qotair` — OT+AIR, zum nächsten Lauf;
- `otcheody` — OT+CHEO, zum nächsten Auszug;
- `saral` — AR+AL, Quelle zum Ziel;
- `salsain` — AL+AIN, Portion am Ziel;
- `otokeeey` — OT+OK mit vollem Grad;
- `okolar` — OK+OL+AR als Dreierkette.

Diese Formen sind stärker als frei erfundene Komposita: Die Zeichenfolgen stehen bereits auf den zehn Seiten. Neu ist nur ihre praktische Prosa-Expansion.
"""
    manual_path = HERE / "TWO_HUNDRED_NINETY_EIGHTH_COMBINATION_MANUAL.md"
    manual_path.write_text(manual, encoding="utf-8")

    report = f"""# Sidequest-Pass 298: registerübergreifende Kombinationskarte

## Ergebnis

Für die 29 produktiven Familien wurden alle 406 Paare erfasst. Davon sind {counts['BOTH_REGISTERS']} in beiden Registern, {counts['PROSE_ONLY']} nur in der Prosa, {counts['ASTRO_ONLY_VISIBLE_COMBINATION']} nur im Astro-Register und {counts['UNSEEN_PAIR']} nirgends sichtbar.

Die Astro-Seiten schließen mehrere Prosaparadigmen nicht durch neue Daten, sondern innerhalb derselben zehn Seiten: `okaiiin`, `olar`, `alaiin`, `chedaiin`, `eckhear`, `qotair`, `saral` und `salsain` sind bereits echte Schriftformen. Damit verschiebt sich die nächste Arbeit von „Wie könnte das Wort aussehen?“ zu „Welche lokale praktische Expansion bekommt die bereits sichtbare Karte?“

Zwölf dieser Formen werden als konkrete Prosa-Schreibleads ausgewählt. Ihre Astro-Bedeutung wird nicht in die Prosa kopiert; nur die Kompositionsfähigkeit und sichtbare Schreibung werden übernommen.

## Nächster Angriff

Die zwölf registerübergreifenden Formen werden nun in die elf Prosa-Records eingesetzt, jedoch nur dort, wo ihre Slotfolge einen bestehenden Zwei-Karten-Ausdruck verkürzen kann. Dadurch testen wir, welche Formen der Schreiber tatsächlich als Abkürzung gebraucht hätte und welche im Diagrammregister bleiben sollten.
"""
    report_path = HERE / "TWO_HUNDRED_NINETY_EIGHTH_REPORT.md"
    report_path.write_text(report, encoding="utf-8")

    summary = {
        "status": "PASS",
        "productive_families": len(families),
        "possible_pairs": len(pair_rows),
        "pair_status_counts": dict(sorted(counts.items())),
        "astro_triples": len(triple_rows),
        "cross_register_leads": len(lead_rows),
        "all_leads_visible_in_astro": all(row["visible_in_astro"] == "YES" for row in lead_rows),
        "source_hashes": {str(path.relative_to(ROOT)): sha(path) for path in [FAMILIES, RECIPES, ASTRO]},
        "outputs": {path.name: sha(path) for path in [pair_path, triple_path, lead_path, manual_path, report_path]},
    }
    (HERE / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

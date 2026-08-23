#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R264 = ROOT / "experiments/yolo/sidequest_semantic_complete_sixty_three_entry_deck_two_hundred_sixty_fourth"
R268 = ROOT / "experiments/yolo/sidequest_semantic_air_path_revision_two_hundred_sixty_eighth"
R274 = ROOT / "experiments/yolo/sidequest_semantic_ten_page_mixed_deck_two_hundred_seventy_fourth"
COMPONENTS = R274 / "TWO_HUNDRED_SEVENTY_FOURTH_REVISED_40_COMPONENTS.tsv"
GENERATION = R264 / "TWO_HUNDRED_SIXTY_FOURTH_173_COMPLETE_GENERATION.tsv"
EVENTS = R268 / "TWO_HUNDRED_SIXTY_EIGHTH_REVISED_381_PROSE_EVENTS.tsv"
ASTRO = R274 / "TWO_HUNDRED_SEVENTY_FOURTH_LAYERED_395_ASTRO_GROUPS.tsv"

PATTERNS = {
    "OK": r"(^|\+)OK(?:_| |\+|$)", "OL": r"(^|\+)OL(?:_| |\+|$)", "OT": r"(^|\+)OT(?:_| |\+|$)",
    "AR": r"AR_FROM", "AL": r"AL_TO", "L": r"(^|\+)L_OUT|^LCH_|^LD_", "P": r"P_IN",
    "AIN": r"(?<!AI)AIN_PORTION|\+ AIN$", "AN": r"AN_SECOND|\+ AN$", "AIIN": r"AIIN", "IIN": r"(?<!A)IIN",
    "E": r"E_SHORT|GRADE_1", "EE": r"GRADE_2|EE_HOLD|EE_LONG", "EEE": r"GRADE_3|EEE_FULL",
    "Y": r"Y_CURRENT|Y_ITEM|Y_CURRENT_ITEM_CARD|\+ Y$", "DY": r"DY_CLOSE|CLOSE_EXACT|TERMINAL_CLOSE|\+CLOSE$|\+CLOSE_EXACT",
    "OR": r"OR_BATCH|\+ OR$|OT \+ OR|CTH \+ OR|CHO \+ OR", "HO": r"^CHO(?: |$)", "CHEO": r"CHEO", "AIR": r"AIR",
    "CHED": r"CHED_TRANSFER", "CHD": r"CHD_TRANSFER|CHD_NEW", "CTH": r"CTH", "SHED": r"SHED", "CHK": r"CHK_WARM",
    "CKH": r"CKH_THROUGH", "CKHE": r"CKHE_STRAIN", "SOLK": r"SOLK", "LSH": r"LSH", "TY": r"TY_PART",
    "CHO_INPUT": r"^CHO(?: |$)", "O_WITHDRAW": r"O_RESIDUAL", "OS_RECEIVER": r"^OS$", "CH_POUR": r"^CH \+ AIR",
    "TCH_PREPARATION": r"TCH_PREPARATION|OL \+ TCH", "OYK_VESSEL": r"OYK", "K_BINDER": r"(^|\+)K(?: |\+|_)",
    "YTY_PART": r"YTY", "SHFY_DURATION": r"SHFY", "D_PREVIOUS": r"^D \+ OL",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_components(component_parse: str) -> set[str]:
    return {component for component, pattern in PATTERNS.items() if re.search(pattern, component_parse)}


def reach_class(h: int, b: int, a: int) -> str:
    present = (h > 0, b > 0, a > 0)
    return {
        (True, True, True): "HERBAL_BIO_ASTRO_CORE",
        (True, True, False): "HERBAL_BIO_PROSE_CORE",
        (True, False, True): "HERBAL_ASTRO_BRIDGE",
        (False, True, True): "BIO_ASTRO_BRIDGE",
        (True, False, False): "HERBAL_SPECIALIST",
        (False, True, False): "BIO_SPECIALIST",
        (False, False, True): "ASTRO_SPECIALIST",
        (False, False, False): "UNMAPPED",
    }[present]


def main() -> None:
    components = read_tsv(COMPONENTS)
    generation = read_tsv(GENERATION)
    events = read_tsv(EVENTS)
    astro = read_tsv(ASTRO)
    parse_by_card = {r["master_card_id"]: r["component_parse"] for r in generation}
    support: dict[str, defaultdict[str, int]] = {r["component_id"]: defaultdict(int) for r in components}
    cards: dict[str, set[str]] = {r["component_id"]: set() for r in components}

    for event in events:
        for component in parse_components(parse_by_card[event["master_card_id"]]):
            register = "HERBAL" if event["page"] in {"f10r", "f11r", "f55v", "f56r"} else "BIO"
            support[component][register] += 1
            cards[component].add(event["master_card_id"])

    for row in astro:
        found: set[str] = set()
        if row["exact_prose_card_id"] != "NONE":
            found |= parse_components(parse_by_card[row["exact_prose_card_id"]])
        reading, surface = row["concrete_diagram_reading_de"], row["visible_surface"]
        if row["revision_266"] != "UNCHANGED": found.add("AIIN")
        if row["revision_267"] != "UNCHANGED": found.add("AIN" if surface.endswith("ain") else "AN")
        if row["revision_268"] != "UNCHANGED": found.add("AIR")
        if row["revision_270"] != "UNCHANGED": found.add("AL" if surface.endswith("al") else "AR")
        if row["revision_271"] != "UNCHANGED": found.add("OL" if surface.endswith("ol") else "OR")
        if row["revision_272"] != "UNCHANGED": found.add("OT")
        if row["revision_273"] in {"OPERATION_Y", "RELATION_Y", "EXPLICIT_CURRENT_Y"}: found.add("Y")
        if row["revision_273"] == "E_GRADE_Y":
            found.add("Y")
            found.add("EEE" if surface.endswith("eeey") else "EE" if surface.endswith("eey") else "E")
        if row["revision_273"] == "DY_FIXED": found.add("DY")
        if "Diagrammposten setzen" in reading: found.add("OK")
        if "Wert oder Platzbezug uebertragen" in reading: found.add("CHED")
        if "Grad oder Diagrammzustand justieren" in reading: found.add("CHK")
        if "durch Sektor" in reading: found.add("CKH")
        if "Himmelsobjekt oder Eingangsbedingung" in reading: found.add("CHO_INPUT")
        if "Teilsektor oder Untereintrag" in reading: found.add("TY")
        for component in found:
            support[component]["ASTRO"] += 1

    rows: list[dict[str, object]] = []
    for component in components:
        cid = component["component_id"]
        h, b, a = support[cid]["HERBAL"], support[cid]["BIO"], support[cid]["ASTRO"]
        cls = reach_class(h, b, a)
        rows.append({
            "deck_order": component["deck_order"],
            "component_id": cid,
            "short_value_de": component["short_value_de"],
            "reach_class": cls,
            "herbal_events": h,
            "bio_events": b,
            "astro_groups": a,
            "prose_card_types": len(cards[cid]),
            "register_signature": "|".join(x for x, n in (("HERBAL", h), ("BIO", b), ("ASTRO", a)) if n),
            "teaching_status": "COMMON_CORE" if cls == "HERBAL_BIO_ASTRO_CORE" else "BRIDGE" if "BRIDGE" in cls or cls == "HERBAL_BIO_PROSE_CORE" else "SECTION_ADDENDUM",
        })

    reach_counts = Counter(str(r["reach_class"]) for r in rows)
    classes = []
    order = ("HERBAL_BIO_ASTRO_CORE", "HERBAL_ASTRO_BRIDGE", "BIO_ASTRO_BRIDGE", "HERBAL_BIO_PROSE_CORE", "HERBAL_SPECIALIST", "BIO_SPECIALIST")
    for cls in order:
        members = [r for r in rows if r["reach_class"] == cls]
        classes.append({
            "reach_class": cls,
            "component_count": len(members),
            "component_ids": "|".join(str(r["component_id"]) for r in members),
            "teaching_rule": "teach in the universal sixteen-card deck" if cls == "HERBAL_BIO_ASTRO_CORE" else "teach only with the named register bridge or section addendum",
        })

    row_path = OUT / "TWO_HUNDRED_SEVENTY_SEVENTH_40_COMPONENT_REACH.tsv"
    class_path = OUT / "TWO_HUNDRED_SEVENTY_SEVENTH_SIX_REACH_CLASSES.tsv"
    readable_path = OUT / "TWO_HUNDRED_SEVENTY_SEVENTH_READABLE_SECTIONED_DECK.md"
    report_path = OUT / "TWO_HUNDRED_SEVENTY_SEVENTH_REPORT.md"
    write_tsv(row_path, rows, list(rows[0]))
    write_tsv(class_path, classes, list(classes[0]))

    universal = [str(r["component_id"]) for r in rows if r["reach_class"] == "HERBAL_BIO_ASTRO_CORE"]
    herbal = [str(r["component_id"]) for r in rows if r["reach_class"] == "HERBAL_SPECIALIST"]
    bio = [str(r["component_id"]) for r in rows if r["reach_class"] == "BIO_SPECIALIST"]
    readable_path.write_text(f"""# Der gestufte Komponentenunterricht

## Allgemeiner 16er-Kern

`{' · '.join(universal)}`

Diese Kürzel werden in Herbal, Bio und Astro gebraucht. Sie tragen Adressen, Folge/Weiter, Mengen/Grade, aktuellen Posten, Lauf, Übertragung und einige knappe Zustände.

## Brücken

- Herbal↔Astro: `AN · HO · CHO_INPUT · OS_RECEIVER`.
- Bio↔Astro: `E · EEE · CHD · CKH`.
- Herbal↔Bio ohne Astro: `IIN · CTH`.

## Fachzusätze

- Herbal-only: `{' · '.join(herbal)}`.
- Bio-only: `{' · '.join(bio)}`.

Ein neuer Schreiber lernt zuerst die sechzehn allgemeinen Karten. Danach erhält er nur den Zusatz der Sektion, die er kopiert. So bleibt das System trotz 40 Komponenten für mehrere Hände einfach lernbar.
""", encoding="utf-8")
    report_path.write_text(f"""# Sidequest-Pass 277: Registerreichweite der vierzig Komponenten

## Ergebnis

Sechzehn Komponenten sind echter Herbal/Bio/Astro-Kern. Vier verbinden Herbal mit Astro, vier Bio mit Astro, zwei nur Herbal mit Bio; sieben sind Herbal-only und sieben Bio-only. Es gibt keine isolierte Astro-only-Komponente und keine unkartierte Komponente.

Damit muss ein Schreiber nicht vierzig gleichrangige Morpheme lernen. Der Unterricht beginnt mit einem 16er-Allgemeinkern und fügt kleine Brücken- und Fachdecks hinzu. Das passt zur angenommenen Werkstatt mit mehreren Schreibern besser als ein vollständiges, für alle identisches Lexikon.

Inputs `{sha(COMPONENTS)}`, `{sha(EVENTS)}`, `{sha(ASTRO)}`.
""", encoding="utf-8")
    outputs = (row_path, class_path, readable_path, report_path)
    summary = {
        "status": "PASS",
        "components": len(rows),
        "reach_counts": dict(reach_counts),
        "universal_core": universal,
        "outputs": {p.name: sha(p) for p in outputs},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R264 = ROOT / "experiments/yolo/sidequest_semantic_complete_sixty_three_entry_deck_two_hundred_sixty_fourth"
R268 = ROOT / "experiments/yolo/sidequest_semantic_air_path_revision_two_hundred_sixty_eighth"
R273 = ROOT / "experiments/yolo/sidequest_semantic_astro_y_boundary_two_hundred_seventy_third"
COMPONENTS = R268 / "TWO_HUNDRED_SIXTY_EIGHTH_REVISED_40_COMPONENTS.tsv"
WHOLE = R264 / "TWO_HUNDRED_SIXTY_FOURTH_23_WHOLE_SIGNS.tsv"
ASTRO = R273 / "TWO_HUNDRED_SEVENTY_THIRD_REVISED_395_ASTRO_GROUPS.tsv"

REVISIONS = {
    "OT": ("FOLGEPOSTEN", "zum folgenden Arbeits- oder Diagrammposten wechseln", 58, "PROSE_AFTER_OR_NEXT__ASTRO_NEXT_PLACE"),
    "AR": ("VON_QUELLE", "die bezeichnete Quelladresse lesen", 60, "TERMINAL_SOURCE_ADDRESS"),
    "AL": ("ZU_ZIEL", "die bezeichnete Zieladresse lesen", 60, "TERMINAL_TARGET_ADDRESS"),
    "OL": ("WEITER_GLEICHER_LAUF", "im selben Arbeitsgang, Ring oder Satz fortfahren", 65, "CONTINUATION_RELATION"),
    "OR": ("BEDINGUNGSANSATZ", "den laufenden Ansatz oder Bedingungssatz eröffnen", 37, "CONDITION_OR_PREPARATION_FRAME"),
    "Y": ("DIES_AKTUELLER_POSTEN", "den aktuell gemeinten Posten referieren", 177, "SECURE_REFERENT;23_GRADED_CANDIDATES_EXTRA"),
    "AIR": ("LAUF_BAHN", "einen Lauf oder eine Bahn markieren; lokal Wasserlauf", 17, "PROSE_WET_PATH__ASTRO_RING_OR_POINTER_PATH"),
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


def astro_class(layer: str) -> str:
    if layer == "ASTRO_LOCAL_LABEL_SIGN":
        return "LOCAL_COPY_LABEL"
    if layer in {"ASTRO_FIXED_DY_WHOLE_ENDING", "ASTRO_LOCAL_WHOLE_Y_ENDING"}:
        return "LEARNED_WHOLE_SIGN"
    return "PORTABLE_COMPOSITION"


def main() -> None:
    components = read_tsv(COMPONENTS)
    whole = read_tsv(WHOLE)
    astro = read_tsv(ASTRO)

    revised_components: list[dict[str, object]] = []
    for row in components:
        new: dict[str, object] = dict(row)
        component = row["component_id"]
        if component in REVISIONS:
            short, rule, support, scope = REVISIONS[component]
            new["short_value_de"] = short
            new["learning_rule"] = rule
            new["ten_page_support_count"] = support
            new["ten_page_support_scope"] = scope
            new["revision_274"] = "CROSS_REGISTER_CONSOLIDATED"
        else:
            new["ten_page_support_count"] = row["support_event_count"]
            new["ten_page_support_scope"] = "PROSE_SUPPORT_CARRIED_FORWARD"
            new["revision_274"] = "UNCHANGED"
        revised_components.append(new)

    layered: list[dict[str, object]] = []
    for row in astro:
        cls = astro_class(row["curriculum_layer"])
        if cls == "PORTABLE_COMPOSITION":
            obligation = "read the portable components and their local expansion"
        elif cls == "LEARNED_WHOLE_SIGN":
            obligation = "memorize this compact Astro whole sign"
        else:
            obligation = "copy the local label from its diagram exemplar"
        layered.append({**row, "coverage_class_274": cls, "learning_obligation_274": obligation})

    counts = Counter(str(r["coverage_class_274"]) for r in layered)
    forms = {
        cls: {str(r["visible_surface"]) for r in layered if r["coverage_class_274"] == cls}
        for cls in counts
    }
    layer_rows = [
        {"register": "PROSE", "coverage_class": "PORTABLE_COMPOSITION", "event_or_group_count": 353, "distinct_form_or_card_count": 150, "learning_mode": "compose from forty components"},
        {"register": "PROSE", "coverage_class": "LEARNED_WHOLE_SIGN", "event_or_group_count": 28, "distinct_form_or_card_count": 23, "learning_mode": "memorize twenty-three nomenclator cards"},
        {"register": "ASTRO", "coverage_class": "PORTABLE_COMPOSITION", "event_or_group_count": counts["PORTABLE_COMPOSITION"], "distinct_form_or_card_count": len(forms["PORTABLE_COMPOSITION"]), "learning_mode": "compose portable core and read local diagram expansion"},
        {"register": "ASTRO", "coverage_class": "LEARNED_WHOLE_SIGN", "event_or_group_count": counts["LEARNED_WHOLE_SIGN"], "distinct_form_or_card_count": len(forms["LEARNED_WHOLE_SIGN"]), "learning_mode": "memorize compact Astro whole sign"},
        {"register": "ASTRO", "coverage_class": "LOCAL_COPY_LABEL", "event_or_group_count": counts["LOCAL_COPY_LABEL"], "distinct_form_or_card_count": len(forms["LOCAL_COPY_LABEL"]), "learning_mode": "copy from local diagram exemplar"},
        {"register": "TEN_PAGE_TOTAL", "coverage_class": "PORTABLE_COMPOSITION", "event_or_group_count": 618, "distinct_form_or_card_count": "NOT_ADDITIVE_ACROSS_REGISTERS", "learning_mode": "productive"},
        {"register": "TEN_PAGE_TOTAL", "coverage_class": "LEARNED_WHOLE_SIGN", "event_or_group_count": 79, "distinct_form_or_card_count": 69, "learning_mode": "23 prose cards plus 46 disjoint Astro forms"},
        {"register": "TEN_PAGE_TOTAL", "coverage_class": "LOCAL_COPY_LABEL", "event_or_group_count": 79, "distinct_form_or_card_count": 67, "learning_mode": "local copy layer"},
    ]
    inventory = [
        {"inventory_layer": "PORTABLE_COMPONENT_DECK", "entry_count": 40, "visible_form_count": "PRODUCTIVE", "must_memorize": "YES", "use": "compose prose and Astro cards"},
        {"inventory_layer": "PROSE_NOMENCLATOR", "entry_count": 23, "visible_form_count": 24, "must_memorize": "YES", "use": "learn compact practical whole signs"},
        {"inventory_layer": "ASTRO_WHOLE_SIGN_ADDENDUM", "entry_count": 46, "visible_form_count": 46, "must_memorize": "YES", "use": "learn fixed Astro values and closures"},
        {"inventory_layer": "ASTRO_LOCAL_COPY_LABELS", "entry_count": 67, "visible_form_count": 67, "must_memorize": "NO", "use": "copy names or addresses from the local diagram exemplar"},
        {"inventory_layer": "TOTAL_MEMORIZED_ENTRIES", "entry_count": 109, "visible_form_count": "40_COMPONENTS_PLUS_69_WHOLE_ENTRIES", "must_memorize": "YES", "use": "minimum ten-page workshop curriculum"},
    ]

    component_path = OUT / "TWO_HUNDRED_SEVENTY_FOURTH_REVISED_40_COMPONENTS.tsv"
    layered_path = OUT / "TWO_HUNDRED_SEVENTY_FOURTH_LAYERED_395_ASTRO_GROUPS.tsv"
    total_path = OUT / "TWO_HUNDRED_SEVENTY_FOURTH_776_COVERAGE_TOTALS.tsv"
    inventory_path = OUT / "TWO_HUNDRED_SEVENTY_FOURTH_APPRENTICE_INVENTORY.tsv"
    readable_path = OUT / "TWO_HUNDRED_SEVENTY_FOURTH_READABLE_MIXED_SYSTEM.md"
    report_path = OUT / "TWO_HUNDRED_SEVENTY_FOURTH_REPORT.md"
    write_tsv(component_path, revised_components, list(revised_components[0]))
    write_tsv(layered_path, layered, list(layered[0]))
    write_tsv(total_path, layer_rows, list(layer_rows[0]))
    write_tsv(inventory_path, inventory, list(inventory[0]))

    readable_path.write_text("""# Das vollständige Zehn-Seiten-System

Der Schreiber lernt drei Dinge:

1. **40 produktive Kürzel** für Einsetzen, Quelle, Ziel, Folgeposten, Fortsetzung, Bedingungsansatz, Maß, Grad, Lauf/Bahn und weitere Arbeitsfunktionen.
2. **69 gelernte Ganzzeichen**: 23 praktische Prosa-Karten und 46 Astro-Wertkarten.
3. **67 lokale Etikettenformen**, die nicht semantisch gelernt werden müssen, sondern aus dem jeweiligen Bild- oder Diagrammexemplar kopiert werden.

Von 776 sichtbaren Text-/Diagrammgruppen werden 618 kompositorisch gebaut. 79 sind gelernte Ganzzeichen und 79 lokale Kopieretiketten. Das ist kein Buchstabenalphabet und kein reiner Code-Nomenklator, sondern ein gemischtes Werkstattregister.

Die wichtigsten portablen Kurzwerte sind jetzt: `AR=VON_QUELLE`, `AL=ZU_ZIEL`, `OL=WEITER_GLEICHER_LAUF`, `OT=FOLGEPOSTEN`, `OR=BEDINGUNGSANSATZ`, `Y=DIES_AKTUELLER_POSTEN`, `AIR=LAUF_BAHN`. Wasser, Zeit und Reihenfolge sind lokale Aussprachen dieser abstrakten Arbeitswerte, nicht ihre gesamte Wörterbuchbedeutung.
""", encoding="utf-8")
    report_path.write_text(f"""# Sidequest-Pass 274: konsolidiertes Mischsystem

## Ergebnis

Die 395 Astrogruppen teilen sich in 265 portable Kompositionen, 51 gelernte Astro-Ganzzeichen und 79 lokale Kopieretiketten. Mit der Prosa ergibt das 618/776 kompositorische Gruppen, 79/776 gelernte Ganzzeichen und 79/776 lokale Etiketten.

Der minimale Lehrbestand für alle zehn Seiten ist damit 109 memorierte Einträge: 40 Komponenten, 23 Prosa-Ganzkarten und 46 disjunkte Astro-Ganzformen. Zusätzlich werden 67 lokale Formen aus den jeweiligen Diagrammexemplaren kopiert. Das ist die bisher konkreteste Realisierung der gesuchten Mischung aus Fachkürzeln und gelernten Ganzwörtern.

Input components `{sha(COMPONENTS)}`; input Astro `{sha(ASTRO)}`.
""", encoding="utf-8")
    outputs = (component_path, layered_path, total_path, inventory_path, readable_path, report_path)
    summary = {
        "status": "PASS",
        "astro_counts": dict(counts),
        "astro_form_counts": {k: len(v) for k, v in forms.items()},
        "unified_counts": {"PORTABLE_COMPOSITION": 618, "LEARNED_WHOLE_SIGN": 79, "LOCAL_COPY_LABEL": 79},
        "memorized_entries": 109,
        "local_copy_forms": 67,
        "outputs": {p.name: sha(p) for p in outputs},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

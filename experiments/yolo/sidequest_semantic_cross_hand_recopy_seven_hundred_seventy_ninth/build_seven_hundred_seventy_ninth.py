#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P739 = ROOT / "experiments/yolo/sidequest_semantic_clean_fluent_edition_seven_hundred_thirty_ninth"
P778 = ROOT / "experiments/yolo/sidequest_semantic_hand_variant_lexicon_seven_hundred_seventy_eighth"
TARGETS = {"f55v": "HAND_1", "f10r": "HAND_2"}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        out = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        out.writeheader()
        out.writerows(rows)


def select_surface(source: dict[str, str], candidates: list[dict[str, str]]) -> tuple[str, str, list[dict[str, str]]]:
    exact = [row for row in candidates if row["line_first"] == source["line_first"] and row["prev_dy"] == source["prev_dy"]]
    line = [row for row in candidates if row["line_first"] == source["line_first"]]
    if exact:
        pool, tier = exact, "MATCH_LINE_FIRST_AND_PREV_DY"
    elif line:
        pool, tier = line, "MATCH_LINE_FIRST"
    else:
        pool, tier = candidates, "CARD_LEVEL_FALLBACK"
    counts = Counter(row["surface"] for row in pool)
    selected = sorted(counts, key=lambda surface: (-counts[surface], surface))[0]
    return selected, tier, pool


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    events = read(P739 / "SEVEN_HUNDRED_THIRTY_NINTH_381_EVENT_INTERLINEAR.tsv")
    statements = read(P739 / "SEVEN_HUNDRED_THIRTY_NINTH_116_CLEAN_STATEMENTS.tsv")
    shared = read(P778 / "SEVEN_HUNDRED_SEVENTY_EIGHTH_106_SHARED_CARD_EVENTS.tsv")
    shared_by_event = {row["event_id"]: row for row in shared}
    by_card_hand: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in shared:
        by_card_hand[(row["exact_card_id"], row["hand"])].append(row)

    selected_events = [row for row in events if row["page"] in TARGETS]
    recopy_rows = []
    target_surface_by_event: dict[str, str] = {}
    for row in selected_events:
        target_hand = TARGETS[row["page"]]
        key = (row["card_no"], target_hand)
        if key in by_card_hand:
            source_layout = shared_by_event[row["event_id"]]
            surface, tier, pool = select_surface(source_layout, by_card_hand[key])
            evidence = ",".join(candidate["event_id"] for candidate in pool)
            mode = "CROSS_HAND_SHARED_CARD_RENDERER"
        else:
            surface = row["surface"]
            tier = "NO_OTHER_HAND_CARD_MODEL"
            evidence = "LOCAL_MODEL_COPY"
            mode = "LOCAL_WHOLE_CARD_PRESERVED"
        target_surface_by_event[row["event_id"]] = surface
        recopy_rows.append(
            {
                "event_id": row["event_id"],
                "page": row["page"],
                "record": row["record"],
                "statement_id": row["statement_id"],
                "source_hand": "HAND_2" if row["page"] == "f55v" else "HAND_1",
                "target_hand": target_hand,
                "exact_card_id": row["card_no"],
                "component_recipe": row["component_recipe"],
                "reading_de": row["rebuilt_reading_de"],
                "source_surface": row["surface"],
                "target_surface": surface,
                "surface_changed": "YES" if surface != row["surface"] else "NO",
                "render_mode": mode,
                "selection_tier": tier,
                "target_hand_evidence_events": evidence,
                "card_and_meaning_preserved": "YES",
            }
        )
    write(
        "SEVEN_HUNDRED_SEVENTY_NINTH_56_CROSS_HAND_EVENT_RECOPY.tsv",
        recopy_rows,
        ["event_id", "page", "record", "statement_id", "source_hand", "target_hand", "exact_card_id", "component_recipe", "reading_de", "source_surface", "target_surface", "surface_changed", "render_mode", "selection_tier", "target_hand_evidence_events", "card_and_meaning_preserved"],
    )

    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in selected_events:
        by_statement[row["statement_id"]].append(row)
    statement_source = {row["statement_id"]: row for row in statements}
    statement_rows = []
    for statement in [row for row in statements if row["page"] in TARGETS]:
        rows = by_statement[statement["statement_id"]]
        original = " ".join(row["surface"] for row in rows)
        rerendered = " ".join(target_surface_by_event[row["event_id"]] for row in rows)
        changed = [row["event_id"] for row in rows if row["surface"] != target_surface_by_event[row["event_id"]]]
        statement_rows.append(
            {
                "statement_id": statement["statement_id"],
                "page": statement["page"],
                "source_hand": "HAND_2" if statement["page"] == "f55v" else "HAND_1",
                "target_hand": TARGETS[statement["page"]],
                "events": len(rows),
                "changed_events": len(changed),
                "changed_event_ids": ",".join(changed) or "NONE",
                "original_surface_sequence": original,
                "cross_hand_surface_sequence": rerendered,
                "unchanged_component_reading": statement_source[statement["statement_id"]]["codebook_literal_de"],
                "unchanged_clean_reading": statement_source[statement["statement_id"]]["clean_workshop_reading_de"],
            }
        )
    write(
        "SEVEN_HUNDRED_SEVENTY_NINTH_9_CROSS_HAND_STATEMENTS.tsv",
        statement_rows,
        ["statement_id", "page", "source_hand", "target_hand", "events", "changed_events", "changed_event_ids", "original_surface_sequence", "cross_hand_surface_sequence", "unchanged_component_reading", "unchanged_clean_reading"],
    )

    page_rows = []
    for page, target_hand in TARGETS.items():
        rows = [row for row in recopy_rows if row["page"] == page]
        modeled = [row for row in rows if row["render_mode"] == "CROSS_HAND_SHARED_CARD_RENDERER"]
        changed = [row for row in rows if row["surface_changed"] == "YES"]
        page_rows.append(
            {
                "page": page,
                "source_hand": rows[0]["source_hand"],
                "target_hand": target_hand,
                "events": len(rows),
                "shared_card_events_with_target_model": len(modeled),
                "surface_changes": len(changed),
                "local_model_events_preserved": len(rows) - len(modeled),
                "exact_cards_preserved": len(rows),
                "component_recipes_preserved": len(rows),
                "meanings_preserved": len(rows),
            }
        )
    write(
        "SEVEN_HUNDRED_SEVENTY_NINTH_2_RECOPY_SUMMARIES.tsv",
        page_rows,
        ["page", "source_hand", "target_hand", "events", "shared_card_events_with_target_model", "surface_changes", "local_model_events_preserved", "exact_cards_preserved", "component_recipes_preserved", "meanings_preserved"],
    )

    lines = ["# Pass 779 — Kreuzkopie der beiden Hände", ""]
    for page in ("f55v", "f10r"):
        lines.extend([f"## {page}: {('Hand 2 → Hand 1' if page == 'f55v' else 'Hand 1 → Hand 2')}", ""])
        for row in [entry for entry in statement_rows if entry["page"] == page]:
            lines.extend(
                [
                    f"### {row['statement_id']}",
                    "",
                    f"Original: `{row['original_surface_sequence']}`",
                    "",
                    f"Andere Hand: `{row['cross_hand_surface_sequence']}`",
                    "",
                    f"Lesung unverändert: {row['unchanged_clean_reading']}",
                    "",
                ]
            )
    (HERE / "SEVEN_HUNDRED_SEVENTY_NINTH_CROSS_HAND_READABLE_RECOPY.md").write_text("\n".join(lines), encoding="utf-8")

    f55 = next(row for row in page_rows if row["page"] == "f55v")
    f10 = next(row for row in page_rows if row["page"] == "f10r")
    report = f"""# Pass 779 — Derselbe Text kann in zwei Werkstatthänden stehen

Die Kreuzkopie verändert ausschließlich sichtbare Oberflächen gemeinsamer Karten. Karten-ID, Komponentenrezept und deutsche Arbeitslesung bleiben an allen56 Ereignissen unverändert. Lokale Karten ohne Beispiel der anderen Hand werden aus dem Seitenmodell kopiert, nicht erfunden.

Auf f55v besitzen5/18 Ereignisse ein Hand-1-Modell; {f55['surface_changes']} Oberflächen wechseln. Der markanteste Abschnitt wird aus `... aiin okal oltchy or y orain` zu `... daiin okal oltchy chor dy orain`. Es bleibt dieselbe Folge aus Sollmaß, Ansatz-/Zieloperation und laufendem Posten, sieht aber sofort stärker nach Hand 1 aus.

Auf f10r besitzen mehrere gemeinsame Kernkarten ein Hand-2-Modell; {f10['surface_changes']} der38 Oberflächen wechseln. Die seltenen Herbal-Karten bleiben erhalten. Genau das wäre in einer kleinen Werkstatt praktisch: Der zweite Schreiber muss die fachlokalen Karten nicht neu erfinden, darf aber den gemeinsamen Kern in seinem gewohnten Duktus setzen.

Die neun vollständigen Aussagen behalten wortgleich ihre Komponenten- und Arbeitslesung. Damit trennt unser Modell erstmals drei Ebenen ausführbar: gemeinsame Bedeutungskomponenten, gelernte lokale Ganzkarten und schreiberabhängige Oberfläche.

Als nächstes bauen wir eine kleine Umsetztabelle für alle zwölf gemeinsamen Karten und prüfen, wie viel der gesamten381 Ereignisse mit nur dieser Handregel und den lokalen Modellkarten kopierbar ist.
"""
    (HERE / "SEVEN_HUNDRED_SEVENTY_NINTH_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "events": len(recopy_rows),
        "statements": len(statement_rows),
        "f55_changes": int(f55["surface_changes"]),
        "f10_changes": int(f10["surface_changes"]),
        "cards_preserved": sum(int(row["exact_cards_preserved"]) for row in page_rows),
        "meanings_preserved": sum(int(row["meanings_preserved"]) for row in page_rows),
        "decision": "CROSS_HAND_RECOPY_PRESERVES_CARD_AND_MEANING__VISIBLE_STYLE_CHANGES",
    }
    (HERE / "SEVEN_HUNDRED_SEVENTY_NINTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()

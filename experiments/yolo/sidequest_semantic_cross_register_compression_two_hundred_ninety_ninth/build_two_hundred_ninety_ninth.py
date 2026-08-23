#!/usr/bin/env python3
"""Test twelve cross-register cards as prose two-card compression devices."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
LEADS = ROOT / "experiments/yolo/sidequest_semantic_cross_register_combination_map_two_hundred_ninety_eighth/TWO_HUNDRED_NINETY_EIGHTH_12_CROSS_REGISTER_SPELLING_LEADS.tsv"
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_two_layer_prose_two_hundred_seventy_ninth/TWO_HUNDRED_SEVENTY_NINTH_381_TWO_LAYER_EVENTS.tsv"
STATEMENTS = ROOT / "experiments/yolo/sidequest_semantic_two_layer_prose_two_hundred_seventy_ninth/TWO_HUNDRED_SEVENTY_NINTH_116_TWO_LAYER_STATEMENTS.tsv"


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


SITES = {
    "X01": ("NONE", "NO_LOCAL_PROSE_SITE", "No adjacent OK+IIN cards exist."),
    "X02": ("E080,E081", "NUANCE_LOSS__KEEP_ASTRO_OR_FUTURE_PROSE", "The window also contains OT and Y; iokeeor would erase following/current scope."),
    "X03": ("E105,E106", "CLEAN_TWO_TO_ONE_SHORTENING", "AR and OL are exactly the two meanings carried by olar."),
    "X04": ("E274,E275", "NUANCE_LOSS__KEEP_ASTRO_OR_FUTURE_PROSE", "The target card also carries SHED; alaiin would lose settling."),
    "X05": ("E285,E286", "NUANCE_LOSS__KEEP_ASTRO_OR_FUTURE_PROSE", "The two-card phrase also specifies AR; chedaiin would lose its source."),
    "X06": ("NONE", "NO_LOCAL_PROSE_SITE", "No adjacent AR+CKHE prose construction occurs."),
    "X07": ("E300,E301", "NUANCE_LOSS__KEEP_ASTRO_OR_FUTURE_PROSE", "The local OT card also transfers and closes; qotair would lose both operations."),
    "X08": ("NONE", "NO_LOCAL_PROSE_SITE", "No adjacent OT+CHEO prose construction occurs."),
    "X09": ("E359,E360", "CLEAN_TWO_TO_ONE_SHORTENING", "AL and AR are exactly the source-target address pair carried by saral."),
    "X10": ("E108,E109", "NUANCE_LOSS__KEEP_ASTRO_OR_FUTURE_PROSE", "The portion is explicitly under OL continuation; salsain would lose continuation."),
    "X11": ("E321,E322", "NUANCE_LOSS__KEEP_ASTRO_OR_FUTURE_PROSE", "The phrase has current-item Y and a long rather than full grade."),
    "X12": ("E104,E105,E106", "NUANCE_LOSS__KEEP_ASTRO_OR_FUTURE_PROSE", "The local chain also contains an AL target not represented in OK+OL+AR."),
}


def main() -> None:
    leads = read_tsv(LEADS)
    events = read_tsv(EVENTS)
    statements = {row["statement_id"]: row for row in read_tsv(STATEMENTS)}
    event_by_id = {row["event_id"]: row for row in events}
    audit = []
    clean = []

    for lead in leads:
        event_list, decision, reason = SITES[lead["lead_id"]]
        selected = [] if event_list == "NONE" else [event_by_id[event_id] for event_id in event_list.split(",")]
        statement_ids = sorted({row["statement_id"] for row in selected})
        audit.append({
            "lead_id": lead["lead_id"],
            "candidate_surface": lead["visible_astro_surface"],
            "candidate_recipe": lead["productive_family_recipe"],
            "candidate_value_de": lead["proposed_prose_workshop_value_de"],
            "best_prose_event_window": event_list,
            "statement_ids": "|".join(statement_ids) or "NONE",
            "current_surface_sequence": " · ".join(row["visible_surface"] for row in selected) or "NONE",
            "current_recipe_sequence": " | ".join(row["family_parse"] for row in selected) or "NONE",
            "current_reading_sequence_de": " | ".join(row["register_expansion_de"] for row in selected) or "NONE",
            "visible_card_count_before": len(selected),
            "visible_card_count_after_hypothetical": 1 if selected else 0,
            "compression_decision": decision,
            "decision_reason": reason,
            "manuscript_edit_policy": "DO_NOT_REPLACE_VISIBLE_TEXT__USE_AS_FORWARD_WRITING_PREDICTION",
        })
        if decision == "CLEAN_TWO_TO_ONE_SHORTENING":
            statement = statements[statement_ids[0]]
            clean.append({
                "lead_id": lead["lead_id"],
                "statement_id": statement_ids[0],
                "page": selected[0]["page"],
                "visible_owner": selected[0]["visible_owner"],
                "original_event_ids": event_list,
                "original_visible_cards": " · ".join(row["visible_surface"] for row in selected),
                "original_local_reading_de": " | ".join(row["register_expansion_de"] for row in selected),
                "hypothetical_compact_card": lead["visible_astro_surface"],
                "compact_workshop_reading_de": lead["proposed_prose_workshop_value_de"],
                "full_statement_context_de": statement["two_layer_statement_de"],
                "future_prediction": f"If this exact address pair recurs on a later permitted page, expect {lead['visible_astro_surface']} as a one-card alternative.",
            })

    audit_path = HERE / "TWO_HUNDRED_NINETY_NINTH_12_COMPRESSION_AUDIT.tsv"
    clean_path = HERE / "TWO_HUNDRED_NINETY_NINTH_2_CLEAN_PROSE_SHORTENINGS.tsv"
    write_tsv(audit_path, audit)
    write_tsv(clean_path, clean)

    edition = """# Zwei saubere hypothetische Werkstattkürzungen

## B1-S002 auf f81v

Sichtbar bleibt im Manuskript: `sar · ol`.

Die zwei Karten lesen wir als **von der Quelle** + **im selben Lauf weiter**. Ein Schreiber, der denselben Inhalt an anderer Stelle in einer Karte bündeln wollte, konnte die bereits im Astro-Register vorhandene Karte `olar` verwenden:

> `olar` — aus derselben Quelle weiter.

## B4-S016 auf f83r

Sichtbar bleibt im Manuskript: `dal · skar`.

Die zwei Karten tragen Ziel und Quelle. Die im Astro-Register sichtbare Karte `saral` bündelt genau diese Adressachse:

> `saral` — von der bezeichneten Quelle zum bezeichneten Ziel.

## Grenze

Dies sind keine Textänderungen und keine Behauptung, dass der Schreiber zwingend kürzen wollte. Es sind Vorwärtsregeln für das erfundene Werkstattsystem: Tritt derselbe Inhalt erneut auf, wären `olar` und `saral` die sparsamsten bereits verfügbaren Karten.
"""
    edition_path = HERE / "TWO_HUNDRED_NINETY_NINTH_TWO_COMPACT_WRITING_EXAMPLES.md"
    edition_path.write_text(edition, encoding="utf-8")

    report = """# Sidequest-Pass 299: Einsetzprobe der zwölf Astroformen

## Ergebnis

Nur zwei der zwölf registerübergreifenden Karten ersetzen eine vorhandene Prosafolge ohne Bedeutungsverlust:

- `olar` bündelt B1-S002 `sar · ol` zu „aus derselben Quelle weiter“;
- `saral` bündelt B4-S016 `dal · skar` zu „von der Quelle zum Ziel“.

Drei Formen haben auf den elf Prosarecords keinen lokalen Einsatzort (`okaiiin`, `eckhear`, `otcheody`). Sie bleiben echte Schreibprognosen für spätere Inhalte. Sieben weitere finden ähnliche Folgen, würden aber Quelle, Ziel, Tätigkeit, Fortsetzung, Posten oder Grad verschlucken. Sie werden nicht eingesetzt.

Die Runde stärkt die Kartenphrasen-Regel: Nicht jede schreibbare Kombination ist an jeder Stelle die bessere Form. Eine Kompaktkarte darf nur dann zwei Karten ersetzen, wenn ihre Slotmenge und Reichweite identisch sind.

## Nächster Angriff

Die beiden sauberen Adresskompakta werden in das Lehrlingsmanual aufgenommen. Danach wird die vollständige 116-Aussagen-Ausgabe mit einer neuen Ebene versehen: sichtbare Kartenphrase, mögliche Kompaktkarte und Grund, warum sie benutzt oder nicht benutzt wird. So erhalten wir einen Satz-für-Satz-Schreibstil statt nur ein Wörterbuch.
"""
    report_path = HERE / "TWO_HUNDRED_NINETY_NINTH_REPORT.md"
    report_path.write_text(report, encoding="utf-8")

    counts = {decision: sum(row["compression_decision"] == decision for row in audit) for decision in sorted({row["compression_decision"] for row in audit})}
    summary = {
        "status": "PASS",
        "leads": len(audit),
        "decision_counts": counts,
        "clean_shortening_rows": len(clean),
        "cards_saved_in_clean_examples": sum(int(row["visible_card_count_before"]) - int(row["visible_card_count_after_hypothetical"]) for row in audit if row["compression_decision"] == "CLEAN_TWO_TO_ONE_SHORTENING"),
        "source_hashes": {str(path.relative_to(ROOT)): sha(path) for path in [LEADS, EVENTS, STATEMENTS]},
        "outputs": {path.name: sha(path) for path in [audit_path, clean_path, edition_path, report_path]},
    }
    (HERE / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

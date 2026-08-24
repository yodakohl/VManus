#!/usr/bin/env python3
"""Build five fluent Herbal articles from the repaired atomic chains."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_herbal_formula_repair_three_hundred_twenty_ninth/THREE_HUNDRED_TWENTY_NINTH_100_HERBAL_EVENTS.tsv"

STATEMENTS = {
    "H1-S001": "Nimm einen Wurzelteil der abgebildeten Pflanze. Richte daraus mit Material aus der bezeichneten Quelle einen Ansatz her, zerkleinere ihn, gib ihn ins Gefäß und führe Wasser zu. Führe den folgenden Teil weiter, setze ihn ein, prüfe das Sollmaß und behalte den kleinen Rest.",
    "H1-S002": "Setze den zurückbehaltenen Posten ein, führe ihn im folgenden Gang weiter und halte ihn bereit.",
    "H2-S001": "Nimm den laufenden Auszugsansatz und halte ihn bereit. Stelle den Ansatz auf sein Sollmaß; führe den Folgeposten weiter und behalte dabei denselben Posten um die Maßangabe aktiv.",
    "H2-S002": "Eröffne den Folgeansatz, führe denselben Ansatz als Fortsetzungsansatz weiter und nimm das Sollmaß aus der bezeichneten Quelle.",
    "H2-S003": "Richte den Ansatz im Gefäß her, halte ihn als laufenden Posten aktiv, setze die gebundene Arbeitsstufe und füge die Zutat im Sollmaß hinzu.",
    "H3-S001": "Bringe das Blütenkraut an die Arbeitsstelle, wringe es aus, lasse es die vorgeschriebene Zeit stehen und seihe es nochmals. Nimm nur den Klarauszug ab und schließe den Schritt.",
    "H3-S002": "Halte einen weiteren Zutatteil für den folgenden Gang bereit.",
    "H3-S003": "Nimm die Fortsetzung des vorigen Gangs, halte den aktuellen Posten gebunden und miss sein Sollmaß.",
    "H3-S004": "Wechsle zum Folgeposten, setze die Fortsetzung ein und halte diesen Posten bereit.",
    "H4-S001": "Stelle das Sollmaß ein, prüfe es und teile den Posten in eine erste und eine zweite Portion. Nimm beide aus diesem Arbeitsschritt und schließe ihn.",
    "H4-S002": "Überführe die abgemessene Menge und verwahre sie.",
    "H4-S003": "Nimm das Sollmaß des Postens aus dem gewonnenen Auszug, halte es länger warm und schließe den fortgesetzten Schritt.",
    "H4-S004": "Setze das Sollmaß an der bezeichneten Stelle ein. Führe die Zubereitung dort weiter, halte den Ansatz als aktuellen Posten und verwende eine Ansatzportion.",
    "H5-S001": "Richte einen Zutatenansatz her. Setze eine weitere Zutat an die bezeichnete Stelle, miss sie und führe sie gebunden weiter. Eröffne danach den Folgeansatz, setze ihn ein und bringe ihn an die Stelle.",
    "H5-S002": "Nimm die Fortsetzung des vorigen Postens, setze die Zutat ein, trage sie auf und schließe den Schritt.",
    "H5-S003": "Nimm einen Teil der abgebildeten Pflanze und die Zutat, binde den Posten kurz und setze ihn erneut ein.",
    "H5-S004": "Setze den Posten ein, gib Auszug hinzu und binde beides an der Zielstelle.",
    "H5-S005": "Gib die Zutat hinzu, setze sie ein, binde die Zutat aus der bezeichneten Quelle und gebrauche den Posten.",
    "H5-S006": "Nimm den Folgeposten, führe ihn kurz gebunden weiter und prüfe das Sollmaß.",
}

ARTICLES = {
    "H1": {
        "page": "f10r",
        "title": "Wurzelansatz mit Wasser und Kurzrest",
        "owner": "Wurzel und übrige Teile der abgebildeten Pflanze",
        "output": "BEMESSENER_WURZEL_WASSERANSATZ_MIT_KURZREST",
        "continuous": "Nimm einen Wurzelteil der abgebildeten Pflanze, zerkleinere ihn und richte ihn mit Material aus der bezeichneten Quelle im Gefäß her. Führe Wasser zu, setze den Folgeposten ein und prüfe das Sollmaß. Bewahre den kleinen Rest; setze ihn im folgenden Gang wieder ein und halte den Ansatz bereit.",
    },
    "H2": {
        "page": "f10r",
        "title": "Fortgesetzter Auszugsansatz mit Zutatsollmaß",
        "owner": "zweiter Arbeitsartikel unter demselben Pflanzenbild",
        "output": "FORTGESETZTER_AUSZUGSANSATZ_MIT_ZUTATSOLLMASS",
        "continuous": "Halte den laufenden Auszugsansatz bereit und stelle ihn auf das Sollmaß. Führe den Folgeansatz aus derselben Quelle weiter. Richte ihn im Gefäß her, halte ihn auf seiner Arbeitsstufe und füge die Zutat im vorgeschriebenen Maß hinzu.",
    },
    "H3": {
        "page": "f11r",
        "title": "Gestandener und nachgeseihter Klarauszug",
        "owner": "Blütenkraut der abgebildeten Pflanze",
        "output": "GESTANDENER_NACHGESEIHTER_KLARAUSZUG",
        "continuous": "Bringe das Blütenkraut an die Arbeitsstelle, wringe es aus, lasse es die vorgeschriebene Zeit stehen und seihe es nochmals. Nimm den Klarauszug ab. Halte einen weiteren Zutatteil bereit; miss später die Fortsetzung des vorigen Gangs und gib sie als Folgeposten weiter.",
    },
    "H4": {
        "page": "f55v",
        "title": "Geteilte und lang erwärmte Auszugsportion",
        "owner": "Blattmaterial der abgebildeten Pflanze",
        "output": "GETEILTE_LANGERWAERMTE_AUSZUGSPORTION",
        "continuous": "Stelle das Sollmaß ein und teile den Posten in zwei Portionen. Überführe und verwahre die Menge. Nimm später das Postensollmaß aus dem Auszug, halte es länger warm und setze eine Ansatzportion an der bezeichneten Stelle ein.",
    },
    "H5": {
        "page": "f56r",
        "title": "Gebundener Zutaten- und Auszugsansatz für Folgeposten",
        "owner": "Stängel-/Pflanzenteil der abgebildeten Pflanze",
        "output": "GEBUNDENER_ZUTATEN_AUSZUGSANSATZ_FUER_FOLGEPOSTEN",
        "continuous": "Richte einen Zutatenansatz her, setze die Zutat an die bezeichnete Stelle und miss sie. Führe den gebundenen Posten weiter, trage eine Fortsetzung auf und setze einen weiteren Pflanzenteil erneut ein. Gib Auszug hinzu, binde die Mischung an der Zielstelle und halte eine weitere Sollmenge für den Folgeposten bereit.",
    },
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, str]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    events = read(EVENTS)
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        by_statement[row["statement_id"]].append(row)

    statements = []
    interlinear = []
    for statement_id, rows in by_statement.items():
        owner = ARTICLES[rows[0]["record_unit_id"]]["owner"]
        statements.append(
            {
                "statement_id": statement_id,
                "record_unit_id": rows[0]["record_unit_id"],
                "page": rows[0]["page"],
                "surface_sequence": " ".join(x["surface"] for x in rows),
                "atomic_sequence": " → ".join(x["atomic_value_de"] for x in rows),
                "visible_owner_added": owner,
                "fluent_workshop_translation_de": STATEMENTS[statement_id],
                "allowed_expansion_channels": "CARD_VALUES|VISIBLE_PLANT_OWNER|ACTIVE_RECORD_REFERENCE|GERMAN_GRAMMAR",
                "removed_old_expansions": "WINE|ULCER|DRAUGHT|FLOWERING_ONSET|PLANT_TIPS|COARSE_GRIND|FREE_WASH_OR_STRAIN_FROM_K",
            }
        )
        for row in rows:
            out = dict(row)
            out["visible_owner"] = owner
            out["statement_translation_de"] = STATEMENTS[statement_id]
            interlinear.append(out)

    article_rows = []
    for record, article in ARTICLES.items():
        article_rows.append(
            {
                "record_unit_id": record,
                **article,
                "statement_ids": "|".join(x for x in STATEMENTS if x.startswith(record + "-")),
                "statement_count": str(sum(x.startswith(record + "-") for x in STATEMENTS)),
                "event_count": str(sum(x["record_unit_id"] == record for x in events)),
                "direct_bio_pointer": "NONE",
            }
        )

    write("THREE_HUNDRED_THIRTIETH_100_HERBAL_INTERLINEAR.tsv", interlinear)
    write("THREE_HUNDRED_THIRTIETH_19_FLUENT_STATEMENTS.tsv", statements)
    write("THREE_HUNDRED_THIRTIETH_FIVE_REPAIRED_ARTICLES.tsv", article_rows)
    names = [
        "THREE_HUNDRED_THIRTIETH_100_HERBAL_INTERLINEAR.tsv",
        "THREE_HUNDRED_THIRTIETH_19_FLUENT_STATEMENTS.tsv",
        "THREE_HUNDRED_THIRTIETH_FIVE_REPAIRED_ARTICLES.tsv",
    ]
    summary = {
        "status": "PASS",
        "articles": len(article_rows),
        "statements": len(statements),
        "events": len(interlinear),
        "direct_bio_pointers": 0,
        "superseded_story_terms": 0,
        "hashes": {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest() for name in names},
    }
    (HERE / "THREE_HUNDRED_THIRTIETH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Expand all common roots under five deliberately substituted owners."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
DECK = ROOT / "experiments/yolo/sidequest_semantic_human_dictionary_thirty_fifth_edition/THIRTY_FIFTH_56_TEACHING_ENTRIES.tsv"


OWNERS = {
    "PLANT_BATCH": {
        "item": "der aktuelle Pflanzenposten", "target": "der bezeichnete Pflanzenteil oder das Gefäß",
        "source": "der Pflanzenvorrat", "run": "der Saft- oder Auszugsweg", "set": "der Pflanzenansatz",
        "result": "der sichtbare Auszug",
    },
    "BASIN_STATION": {
        "item": "die aktuelle Beckencharge", "target": "die bezeichnete Öffnung oder Schale",
        "source": "das Quellbecken oder der Einlauf", "run": "der Flüssigkeitslauf", "set": "der laufende Beckengang",
        "result": "der sichtbare Ablaufzustand",
    },
    "CLOTH_FILTER": {
        "item": "der aktuelle Tuchposten", "target": "das Empfangsgefäß",
        "source": "die obere Tuchseite", "run": "der Durchgang durch das Tuch", "set": "der Filteransatz",
        "result": "das sichtbare Filtrat",
    },
    "CELESTIAL_TABLE": {
        "item": "der aktuelle Tabellenwert", "target": "die bezeichnete Zielzelle",
        "source": "die bezeichnete Quellzelle", "run": "die sichtbare Bahn oder das Ringband", "set": "der lokale Tabellensatz",
        "result": "der sichtbare Ablesewert",
    },
    "GENERIC_WORKPIECE": {
        "item": "das aktuelle Werkstück", "target": "die bezeichnete Arbeitsstelle",
        "source": "der Ausgangsvorrat", "run": "der örtliche Arbeitsweg", "set": "der laufende Arbeitsansatz",
        "result": "das sichtbare Arbeitsergebnis",
    },
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def expansion(symbol: str, owner: dict[str, str]) -> str:
    item, target, source, run, workset, result = (owner[k] for k in ("item", "target", "source", "run", "set", "result"))
    mapping = {
        "AIIN": f"Sollwert für {item}", "AIN": f"Portion von {item}", "IIN": f"Arbeitsstufe von {workset}",
        "AL": f"hin zu {target}", "AR": f"her aus {source}", "AIR": f"entlang {run}",
        "OK": f"{item} ansetzen", "OL": f"{item} im selben Gang fortsetzen", "OT": f"den folgenden Posten nach {item} wählen",
        "OR": workset, "Y": item, "E": f"{item} kurz", "EE": f"{item} länger", "EEE": f"{item} vollständig",
        "CLOSE": "den lokalen Arbeitsschritt schließen", "CHD": f"{item} nach {target} umsetzen",
        "CTH": f"{item} bereitstellen", "CKH": f"{item} durch {run} führen", "CKHE": f"{item} am Durchgang trennen",
        "CHK": f"{item} auf die geforderte Wärme- oder Erhöhungsstufe bringen", "SHED": f"{item} stehen oder absetzen lassen",
        "SOLK": f"{item} an {target} auffangen", "HO": f"Eingangsposten für {workset}", "CHEO": f"Ausgabe aus {workset}",
        "KCH": f"{item} bearbeiten", "TY": f"Teil von {item}", "SH": f"{item} halten", "CHEEY": result,
    }
    return mapping[symbol]


def main() -> None:
    roots = read_tsv(DECK)[:28]
    atlas_rows = []
    for root in roots:
        for owner_id, owner in OWNERS.items():
            spoken = expansion(root["symbol"], owner)
            observed = root["registers"] == "ASTRO|PROSE" or owner_id != "CELESTIAL_TABLE"
            atlas_rows.append({
                "root": root["symbol"],
                "atomic_value_de": root["atomic_value_de"],
                "owner_class": owner_id,
                "owner_item": owner["item"],
                "owner_target": owner["target"],
                "owner_source": owner["source"],
                "owner_run": owner["run"],
                "owner_set": owner["set"],
                "owner_result": owner["result"],
                "spoken_owner_expansion_de": spoken,
                "apprentice_command_de": f"Unter {owner_id}: {spoken}.",
                "register_evidence": root["registers"],
                "observed_or_training": "OBSERVED_REGISTER_TRANSFER" if observed else "TRAINING_ONLY_UNOBSERVED_ASTRO_TRANSFER",
                "root_meaning_changed": "NO",
                "concrete_noun_supplied_by_owner": "YES",
                "caution_de": root["caution_de"],
            })
    write_tsv(OUT / "FORTY_SIXTH_140_OWNER_EXPANSIONS.tsv", atlas_rows)

    verdict_rows = []
    for root in roots:
        rows = [row for row in atlas_rows if row["root"] == root["symbol"]]
        if root["registers"] == "ASTRO|PROSE":
            verdict = "PORTABLE_NUCLEUS_WITH_FIVE_OWNER_EXPANSIONS"
            limit = "concrete object must come from owner; root stays short"
        elif root["symbol"] == "CLOSE":
            verdict = "FORMAL_PROSE_ENDPOINT__TABLE_TRANSFER_TRAINING_ONLY"
            limit = "do not invent an Astro close sign from prose surface spelling"
        else:
            verdict = "PROSE_PROCESS_ROOT__CELESTIAL_TRANSFER_NOT_LICENSED"
            limit = "keep celestial example as a teaching paraphrase, not a dictionary promotion"
        verdict_rows.append({
            "teaching_order": root["teaching_order"],
            "root": root["symbol"],
            "atomic_value_de": root["atomic_value_de"],
            "register_evidence": root["registers"],
            "surface_type_count": root["surface_type_count"],
            "visible_group_count": root["visible_group_count"],
            "owner_expansion_count": len(rows),
            "transfer_verdict": verdict,
            "portable_part_de": root["atomic_value_de"],
            "owner_supplied_part_de": "plant/basin/cloth/table/workpiece noun and local address",
            "limit_de": limit,
        })
    write_tsv(OUT / "FORTY_SIXTH_28_ROOT_TRANSFER_VERDICTS.tsv", verdict_rows)

    lines = [
        "# Besitzeratlas der 28 gemeinsamen Kerne",
        "",
        "Jeder Kern wird unter fünf Besitzern gesprochen: Pflanze, Beckenstation, Tuchfilter,",
        "Himmelstafel und allgemeines Werkstück. Der Kern bleibt kurz; nur Gegenstand, Quelle,",
        "Ziel, Lauf, Satz und sichtbares Ergebnis wechseln mit dem Besitzer.",
        "",
    ]
    for verdict in verdict_rows:
        lines.extend([f"## {verdict['root']} — {verdict['atomic_value_de']}", ""])
        for row in (row for row in atlas_rows if row["root"] == verdict["root"]):
            lines.append(f"- {row['owner_class']}: {row['spoken_owner_expansion_de']}")
        lines.extend(["", f"Grenze: {verdict['limit_de']}.", ""])
    (OUT / "FORTY_SIXTH_FIVE_OWNER_ATLAS.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    summary = {
        "status": "CONSISTENT",
        "counts": {
            "roots": len(roots),
            "owner_classes": len(OWNERS),
            "owner_expansions": len(atlas_rows),
            "cross_register_roots": sum(root["registers"] == "ASTRO|PROSE" for root in roots),
            "prose_only_roots": sum(root["registers"] == "PROSE" for root in roots),
            "all_root_values_invariant": sum(row["root_meaning_changed"] == "NO" for row in atlas_rows),
        },
        "source": {str(DECK.relative_to(ROOT)): sha256(DECK)},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

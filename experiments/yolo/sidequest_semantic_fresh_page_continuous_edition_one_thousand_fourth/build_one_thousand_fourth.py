#!/usr/bin/env python3
"""Build Pass 1004: resolve 13 variants and read across physical lines."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P1003 = ROOT / "experiments/yolo/sidequest_semantic_four_fresh_page_transfer_one_thousand_third"
SOURCE_EVENTS = P1003 / "PASS1003_657_FRESH_EVENT_INTERLINEAR.tsv"
SOURCE_COMBINED = P1003 / "PASS1003_3168_COMBINED_EVENT_INTERLINEAR.tsv"
ROOT_SOURCE = (
    ROOT
    / "experiments/yolo/sidequest_semantic_canonical_scribe_workshop_sixth_edition_nine_hundred_ninety_sixth"
    / "PASS996_53_PORTABLE_ROOTS.tsv"
)

PAGE_ORDER = {"f17r": 0, "f77r": 1, "f88v": 2, "f71v": 3}
PAGE_TITLES = {
    "f17r": "Pflanzenartikel",
    "f77r": "Becken- und Stationsartikel",
    "f88v": "Gefäss- und Zutatenartikel",
    "f71v": "Ring- und Himmelsregister",
}
CONTEXT_FIELD = {
    "MATERIAL": "material_workshop_expansion_de",
    "STATION": "station_workshop_expansion_de",
    "CELESTIAL": "celestial_relational_expansion_de",
}

# Every residue is decomposed with the existing 53-root inventory.
RESOLUTIONS = {
    "P1003-E0001": ("LOCAL_CHAR_F+SH+O+DY", "f + sh + o + dy"),
    "P1003-E0032": ("O+P+Y+D_ADDR+LOCAL_CHAR_G", "o + p + y + d + g"),
    "P1003-E0049": ("CH+E+T+E+LOCAL_CHAR_G", "ch + e + t + e + g"),
    "P1003-E0053": ("S+E+P+CH+Y", "z/s + e + p + ch + y"),
    "P1003-E0057": ("D_ADDR+Y+CH+E+AR", "d + y + ch + e + ar"),
    "P1003-E0064": ("CH+Y+P+CH+AM_ADDR", "ch + y + p + ch + am"),
    "P1003-E0228": ("L+LOCAL_CHAR_F+CH+E+AL", "l + f + ch + e + al"),
    "P1003-E0312": ("D_ADDR+OL+CH+L", "d + ol + ch + l"),
    "P1003-E0464": ("O+P+Y+K+E+Y", "o + p + y + k + e + y"),
    "P1003-E0493": ("CH+OT+AM_ADDR", "ch + ot + am"),
    "P1003-E0508": ("T+O+AIR+Y", "t + o + air + y"),
    "P1003-E0526": ("K+EE+O+D_ADDR+AIIN", "k + ee + o + d + aiin"),
    "P1003-E0648": ("OK+E+O+S+AR", "ok + e + o + s + ar"),
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str] | None = None) -> None:
    if fields is None:
        if not rows:
            raise ValueError(f"cannot infer columns for {path}")
        fields = list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in fields} for row in rows)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def locus_number(locus: str) -> int:
    return int(locus.rsplit(".", 1)[1])


def compact(values: list[str]) -> str:
    output: list[str] = []
    for value in values:
        if output and output[-1] == value:
            output[-1] = value + " ×2"
        else:
            output.append(value)
    return " → ".join(output)


def main() -> int:
    roots = read_tsv(ROOT_SOURCE)
    root_by_component = {row["recognition_form"]: row for row in roots}
    atomic = {key: row["atomic_meaning_de"] for key, row in root_by_component.items()}

    def root_default(recipe: str) -> str:
        if recipe == "LOCAL_ADDRESS":
            return "BILDADRESSE"
        missing = [part for part in recipe.split("+") if part not in root_by_component]
        if missing:
            raise ValueError(f"unknown roots in {recipe}: {missing}")
        return " · ".join(atomic[part] for part in recipe.split("+"))

    def local_expansion(row: dict[str, str]) -> str:
        if row["component_recipe"] == "LOCAL_ADDRESS":
            return f"Name oder Kennung für {row['visible_owner_de']}"
        values = [
            root_by_component[part][CONTEXT_FIELD[row["register"]]]
            for part in row["component_recipe"].split("+")
        ]
        prefix = {"MATERIAL": "am Stoffbild", "STATION": "an der Station", "CELESTIAL": "im Ring"}[
            row["register"]
        ]
        return f"{prefix} {row['visible_owner_de']}: " + " · ".join(values)

    source = read_tsv(SOURCE_EVENTS)
    revised: list[dict[str, str]] = []
    decisions: list[dict[str, object]] = []
    for original in source:
        row = dict(original)
        if row["fresh_event_id"] in RESOLUTIONS:
            old_recipe = row["component_recipe"]
            recipe, visible_parse = RESOLUTIONS[row["fresh_event_id"]]
            row["component_recipe"] = recipe
            row["portable_default_de"] = root_default(recipe)
            row["local_contextual_expansion_de"] = local_expansion(row)
            row["transfer_class"] = "VISIBLE_ROOT_COMPOSITION_RESOLVED"
            row["source_surface"] = row["surface"]
            row["edit_distance"] = "0"
            row["confidence"] = "MEDIUM_HIGH"
            row["note"] = "Direkte sichtbare Zerlegung mit dem vorhandenen Wurzelvorrat; kein neuer Stamm."
            decisions.append(
                {
                    "event_id": row["fresh_event_id"],
                    "page": row["physical_page"],
                    "locus": row["locus"],
                    "surface": row["surface"],
                    "pass1003_recipe": old_recipe,
                    "visible_parse": visible_parse,
                    "pass1004_recipe": recipe,
                    "portable_default_de": row["portable_default_de"],
                    "decision": "RESOLVED_WITH_EXISTING_ROOTS",
                }
            )
        revised.append(row)

    if len(decisions) != 13:
        raise ValueError(f"expected 13 repairs, got {len(decisions)}")
    if any(row["transfer_class"] == "TENTATIVE_ROOTED_VARIANT" for row in revised):
        raise ValueError("tentative variant remains")

    write_tsv(HERE / "PASS1004_13_VARIANT_DECISIONS.tsv", decisions)
    write_tsv(HERE / "PASS1004_657_REVISED_EVENT_INTERLINEAR.tsv", revised, list(source[0]))

    by_surface: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in revised:
        by_surface[row["surface"]].append(row)
    class_priority = {
        "EXACT_REGISTERED_SURFACE": 5,
        "VISIBLE_ROOT_COMPOSITION_RESOLVED": 4,
        "VISIBLE_NEW_COMPOSITION": 3,
        "NEAR_REGISTERED_ALLOGRAPH": 2,
        "LOCAL_OWNER_ADDRESS": 1,
    }
    surface_rows: list[dict[str, object]] = []
    for surface in sorted(by_surface):
        rows = by_surface[surface]
        content = [row for row in rows if row["component_recipe"] != "LOCAL_ADDRESS"]
        representative = content[0] if content else rows[0]
        if content and len({row["component_recipe"] for row in content}) != 1:
            raise ValueError(f"unreconciled running surface {surface}")
        classes = Counter(row["transfer_class"] for row in rows)
        primary = max(classes, key=lambda item: (classes[item], class_priority[item]))
        surface_rows.append(
            {
                "surface": surface,
                "events": len(rows),
                "pages": "|".join(sorted({row["physical_page"] for row in rows}, key=PAGE_ORDER.get)),
                "kinds": "|".join(sorted({row["kind"] for row in rows})),
                "primary_transfer_class": primary,
                "component_recipe": representative["component_recipe"],
                "portable_default_de": representative["portable_default_de"],
                "source_surface": representative["source_surface"],
                "edit_distance": representative["edit_distance"],
                "owner_bound_label_use": "YES" if any(row["kind"] == "L" for row in rows) else "NO",
                "confidence": representative["confidence"],
            }
        )
    write_tsv(HERE / "PASS1004_393_REVISED_SURFACE_DICTIONARY.tsv", surface_rows)

    by_locus: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in revised:
        by_locus[(row["physical_page"], row["locus"])].append(row)
    locus_rows: list[dict[str, object]] = []
    for (page, locus), rows in sorted(
        by_locus.items(), key=lambda item: (PAGE_ORDER[item[0][0]], locus_number(item[0][1]))
    ):
        rows.sort(key=lambda row: int(row["group_index"]))
        locus_rows.append(
            {
                "physical_page": page,
                "locus": locus,
                "kind": rows[0]["kind"],
                "owner_id": rows[0]["owner_id"],
                "visible_owner_de": rows[0]["visible_owner_de"],
                "surface_sequence": " ".join(row["surface"] for row in rows),
                "component_sequence": " | ".join(row["component_recipe"] for row in rows),
                "portable_reading_de": " ; ".join(row["portable_default_de"] for row in rows),
                "local_workshop_reading_de": " ; ".join(row["local_contextual_expansion_de"] for row in rows),
                "groups": len(rows),
            }
        )
    write_tsv(HERE / "PASS1004_111_REVISED_LOCUS_READINGS.tsv", locus_rows)

    running = [row for row in revised if row["kind"] != "L"]
    raw_statements: list[tuple[list[dict[str, str]], str]] = []
    current: list[dict[str, str]] = []
    for row in running:
        if current and (row["physical_page"], row["owner_id"]) != (
            current[-1]["physical_page"],
            current[-1]["owner_id"],
        ):
            raw_statements.append((current, "OWNER_BOUNDARY_OPEN"))
            current = []
        current.append(row)
        if row["component_recipe"].split("+")[-1] == "DY":
            raw_statements.append((current, "LICENSED_DY_CLOSE"))
            current = []
    if current:
        raw_statements.append((current, "PAGE_END_OPEN"))

    statement_rows: list[dict[str, object]] = []
    serial: Counter[str] = Counter()
    for rows, end_reason in raw_statements:
        page = rows[0]["physical_page"]
        serial[page] += 1
        loci: list[str] = []
        for row in rows:
            if not loci or loci[-1] != row["locus"]:
                loci.append(row["locus"])
        components = [part for row in rows for part in row["component_recipe"].split("+")]
        values = [atomic[part] for part in components]
        prefix = {
            "MATERIAL": "Am Bildstoff",
            "STATION": "An der gezeichneten Station",
            "CELESTIAL": "Im bezeichneten Ringabschnitt",
        }[rows[0]["register"]]
        reading = f"{prefix} ({rows[0]['visible_owner_de']}): {compact(values).lower()}"
        if end_reason == "LICENSED_DY_CLOSE":
            reading += "; Teilgang geschlossen."
        else:
            reading += "; offen bis Besitzerwechsel oder Seitenende."
        statement_rows.append(
            {
                "statement_id": f"P1004-{page.upper()}-S{serial[page]:03d}",
                "physical_page": page,
                "register": rows[0]["register"],
                "owner_id": rows[0]["owner_id"],
                "visible_owner_de": rows[0]["visible_owner_de"],
                "first_locus": loci[0],
                "last_locus": loci[-1],
                "locus_count": len(loci),
                "crosses_physical_line": "YES" if len(loci) > 1 else "NO",
                "groups": len(rows),
                "first_event_id": rows[0]["fresh_event_id"],
                "last_event_id": rows[-1]["fresh_event_id"],
                "end_reason": end_reason,
                "surface_sequence": " ".join(row["surface"] for row in rows),
                "component_sequence": " | ".join(row["component_recipe"] for row in rows),
                "portable_sequence_de": " ; ".join(row["portable_default_de"] for row in rows),
                "continuous_workshop_reading_de": reading,
            }
        )
    write_tsv(HERE / "PASS1004_110_CONTINUOUS_STATEMENTS.tsv", statement_rows)

    combined_source = read_tsv(SOURCE_COMBINED)
    combined = [row for row in combined_source if row["edition_source"] != "PASS1003_FRESH_TRANSFER"]
    for row in revised:
        combined.append(
            {
                "event_id": row["fresh_event_id"],
                "physical_page": row["physical_page"],
                "locus": row["locus"],
                "kind": row["kind"],
                "surface": row["surface"],
                "component_recipe": row["component_recipe"],
                "portable_default_de": row["portable_default_de"],
                "local_contextual_expansion_de": row["local_contextual_expansion_de"],
                "edition_source": "PASS1004_FRESH_CONTINUOUS",
            }
        )
    write_tsv(HERE / "PASS1004_3168_COMBINED_EVENT_INTERLINEAR.tsv", combined, list(combined_source[0]))

    overview = {
        "f17r": "Die ganze gezeichnete Pflanze ist stiller Besitzer; der Text führt Teil-, Quellen-, Mass-, Ansatz- und Durchlassoperationen daran aus.",
        "f77r": "Der lange Stationsartikel arbeitet Figuren-, Becken-, Bogen- und Auslassgruppen zellenweise ab; Dauer, Quelle, Ziel und Durchlass wechseln lokal.",
        "f88v": "Drei Gefäss- und Zutatenpartien werden getrennt behandelt; Etiketten benennen lokal, der Lauftext organisiert Ansatz, Zugabe, Quelle, Ziel und Abschluss.",
        "f71v": "Drei Ringgruppen verwenden dieselbe Reihen-, Ziel-, Quell-, Grad- und Postenalgebra als Adressregister, nicht als Stoffwortschatz.",
    }
    lines = [
        "# Pass 1004 — vollständige Vierseiten-Werkstattlesung",
        "",
        "Die 13 bisherigen Restformen sind ohne neuen Grundstamm zerlegt. Physische Zeilen sind nur Schreibraum: Ein Lauf endet erst an einer lizenzierten Schlusskarte, einem sichtbaren Besitzerwechsel oder am Seitenende.",
        "",
    ]
    for page in PAGE_ORDER:
        lines.extend([f"## {page} — {PAGE_TITLES[page]}", "", overview[page], ""])
        for row in (item for item in statement_rows if item["physical_page"] == page):
            lines.append(
                f"- **{row['statement_id']}** ({row['first_locus']}→{row['last_locus']}; "
                f"{row['groups']} Gruppen): {row['surface_sequence']} — "
                f"{row['continuous_workshop_reading_de']}"
            )
        lines.append("")
    (HERE / "PASS1004_FOUR_COMPLETE_READINGS.md").write_text("\n".join(lines), encoding="utf-8")

    page_counts = Counter(row["physical_page"] for row in statement_rows)
    closed = sum(row["end_reason"] == "LICENSED_DY_CLOSE" for row in statement_rows)
    cross = sum(row["crosses_physical_line"] == "YES" for row in statement_rows)
    report = (
        "# Pass 1004 — Restformen geschlossen, vier Seiten durchgelesen\n\n"
        "Die 13 Restformen aus Pass 1003 lassen sich sichtbar mit dem vorhandenen "
        "53-Wurzel-Vorrat schreiben. Es bleibt keine tentative Form und es kommt "
        "kein neuer Grundstamm hinzu. Auffällige Reparaturen sind fshody = "
        "f+sh+o+dy, dychear = d+y+ch+e+ar, chypcham = ch+y+p+ch+am, "
        "toairy = t+o+air+y und okeosar = ok+e+o+s+ar. Das seltene z in "
        "zepchy wird als lokale Schreiberform des Auswahlträgers S gelesen.\n\n"
        "## Zeilenübergreifende Ausgabe\n\n"
        f"Die 608 laufenden Gruppen bilden {len(statement_rows)} Werkstattaussagen. "
        f"{cross} überschreiten mindestens eine physische Zeile. {closed} enden "
        f"an einer lizenzierten Schlusskarte; {len(statement_rows) - closed} laufen "
        "offen bis zu einem sichtbaren Besitzerwechsel oder Seitenende. Die Zeile "
        "ist ausdrücklich kein Satzende.\n\n"
        f"- f17r: {page_counts['f17r']} Aussagen;\n"
        f"- f77r: {page_counts['f77r']} Aussagen;\n"
        f"- f88v: {page_counts['f88v']} Aussagen;\n"
        f"- f71v: {page_counts['f71v']} Aussagen.\n\n"
        "Die vier Seiten sind vier Anwendungen derselben kleinen Werkstattgrammatik: "
        "Pflanzenbild, lokale Körper-/Beckenstation, Gefäss-/Zutatenpartie und "
        "Ringposition liefern jeweils den Besitzer. AIR bleibt daher LAUF, nicht "
        "allgemein WASSER. Die vollständige Ausgabe führt alle 110 Aussagen einzeln "
        "auf. Sie ist eine kreative Werkstattlesung, keine historische Klartextbehauptung.\n"
    )
    (HERE / "PASS1004_REPORT.md").write_text(report, encoding="utf-8")

    outputs = [
        "PASS1004_13_VARIANT_DECISIONS.tsv",
        "PASS1004_657_REVISED_EVENT_INTERLINEAR.tsv",
        "PASS1004_393_REVISED_SURFACE_DICTIONARY.tsv",
        "PASS1004_111_REVISED_LOCUS_READINGS.tsv",
        "PASS1004_110_CONTINUOUS_STATEMENTS.tsv",
        "PASS1004_3168_COMBINED_EVENT_INTERLINEAR.tsv",
        "PASS1004_FOUR_COMPLETE_READINGS.md",
        "PASS1004_REPORT.md",
    ]
    summary = {
        "status": "PASS",
        "decision": "ALL_THIRTEEN_VARIANTS_RESOLVED_AND_ALL_RUNNING_GROUPS_CONTINUOUSLY_ASSIGNED",
        "fresh_pages": 4,
        "fresh_groups": len(revised),
        "running_groups": len(running),
        "label_groups": len(revised) - len(running),
        "unique_surfaces": len(surface_rows),
        "resolved_variants": len(decisions),
        "tentative_variants_remaining": 0,
        "new_portable_roots": 0,
        "continuous_statements": len(statement_rows),
        "cross_line_statements": cross,
        "licensed_closed_statements": closed,
        "open_owner_or_page_final_statements": len(statement_rows) - closed,
        "page_statement_counts": dict(page_counts),
        "transfer_class_counts": dict(sorted(Counter(row["transfer_class"] for row in revised).items())),
        "combined_groups": len(combined),
        "combined_pages": len({row["physical_page"] for row in combined}),
        "source_hashes": {
            "pass1003_fresh_events": sha(SOURCE_EVENTS),
            "pass1003_combined_events": sha(SOURCE_COMBINED),
            "pass996_roots": sha(ROOT_SOURCE),
        },
        "output_hashes": {name: sha(HERE / name) for name in outputs},
    }
    (HERE / "PASS1004_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

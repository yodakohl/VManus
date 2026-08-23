#!/usr/bin/env python3
"""Build one short common workshop lexicon for all 44 shared surfaces."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
READER = ROOT / "experiments/yolo/sidequest_semantic_ten_page_unified_reader"
PATHS = ROOT / "experiments/yolo/sidequest_semantic_selected_job_paths"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: str(row.get(field, "")) for field in fields})


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


FAMILY_SPECS = [
    ("F01_AIIN_VALUE", "Vorgabewert", "aiin daiin saiin", "AIIN mit Karten-/Rendererrahmen", "Maß oder Sollwert", "Grad oder Sollwert"),
    ("F02_AR_SOURCE", "vom Ausgang", "char dar sar", "AR mit Karten-/Rendererrahmen", "aus dem aktiven Ansatz", "vom bezeichneten Ausgang"),
    ("F03_AL_TARGET", "zum Ziel", "cheal dal sal", "AL mit Karten-/Rendererrahmen", "dorthin", "zum bezeichneten Zielplatz"),
    ("F04_Y_CURRENT", "aktueller Posten", "chey chy dy sy y", "Y-Karte mit Karten-/Rendererrahmen", "dieses Material oder dieser Arbeitsposten", "dieser lokale Diagrammposten"),
    ("F05_RELEASED_VALUE", "freigegebener Wert", "cheey shey", "gelernte SHEY/CHEEY-Karte", "klarer oder ausgelesener Auszug", "abgelesener oder freigegebener Wert"),
    ("F06_HO_INPUT", "Eingangsposten", "cho", "HO-Eingangskarte", "Zutat", "Eingangsobjekt oder Eingangsbedingung"),
    ("F07_OK_CURRENT_SET", "aktuellen Posten setzen", "choky okchy oky", "OK + aktuelle Y-Karte", "Materialposten ansetzen", "Diagrammposten setzen"),
    ("F08_OL_CONTINUE", "fortsetzen", "chol ol tol", "OL-Fortsetzung mit Rahmen", "Arbeitsgang fortsetzen", "im selben Ring oder Band fortsetzen"),
    ("F09_CHD_TRANSFER", "aktuellen Posten übertragen", "chdy", "CHD-Transfer + aktuelle Y-Karte", "laufenden Stoffposten umsetzen", "auf den bezeichneten Diagrammplatz übertragen"),
    ("F10_DAIN_CARRIER", "Abdeckträger", "dain", "gelernte DAIN-Karte", "Tuch", "Band-, Schleier- oder Abdeckträger"),
    ("F11_KCH_PROCESS", "bearbeiten", "kchey kchy", "KCH-Bearbeitung + optional Kurzgrad", "Material bearbeiten", "Diagrammplatz bearbeiten"),
    ("F12_ODY_WITHDRAW", "zurücknehmen", "ody", "gelernte ODY-Karte", "zum Abkühlen aus dem Arbeitsgang nehmen", "Diagrammposten zurücknehmen"),
    ("F13_OK_AIN_ADD", "gezählten Teil zugeben", "okain", "OK + AIN-Portion", "eine Portion zugeben", "einen gezählten Teilwert zugeben"),
    ("F14_OK_AL_TARGET", "am Ziel setzen", "okal", "OK + AL-Ziel", "dort ansetzen", "am Zielplatz setzen"),
    ("F15_OK_GRADE", "Arbeitsgrad setzen", "okeey okey qokeeedy", "OK + E/EE/EEE-Grad + offene oder geschlossene Endkarte", "kurz, länger oder vollständig ansetzen", "kurze, lange oder vollständige Diagrammstufe setzen"),
    ("F16_OR_SET", "Ansatz oder Satz", "olor or sor", "OR-Ansatz, optional mit OL-Fortsetzung", "Zubereitungsansatz", "Bedingungs- oder Tabellensatz"),
    ("F17_OS_ENCLOSURE", "umschließender Träger", "os", "gelernte OS-Karte", "Mischgefäß", "umschließendes Diagrammfeld"),
    ("F18_OT_FOLLOW", "Folgeposten", "otar otchdy otchey oteey otol", "OT-Folge + Quelle, Transfer, Posten, Grad oder Fortsetzung", "nächster Arbeitsposten oder Folgegang", "nächster Platz oder folgende Diagrammhandlung"),
    ("F19_OL_CLOSE", "Fortsetzung schließen", "oldy", "OL-Fortsetzung + gelernte Schlusskarte", "Arbeitsfortsetzung abschließen", "Eintrag nach Fortsetzung schließen"),
    ("F20_SH_EE_HOLD", "länger halten", "sheey", "SH-Halten/Ruhen + langer EE-Grad + aktuelle Karte", "länger ruhen lassen", "diese Position länger halten"),
]


CARD_NUCLEI = {
    "aiin": "VORGABEWERT", "daiin": "VORGABEWERT", "saiin": "VORGABEWERT",
    "char": "VOM AUSGANG", "dar": "VOM AUSGANG", "sar": "VOM AUSGANG",
    "chdy": "AKTUELLEN POSTEN ÜBERTRAGEN",
    "cheal": "ZUM ZIEL", "dal": "ZUM ZIEL", "sal": "ZUM ZIEL",
    "cheey": "FREIGEGEBENER WERT", "shey": "FREIGEGEBENER WERT",
    "chey": "AKTUELLER POSTEN", "chy": "AKTUELLER POSTEN", "dy": "AKTUELLER POSTEN", "sy": "AKTUELLER POSTEN", "y": "AKTUELLER POSTEN",
    "cho": "EINGANGSPOSTEN",
    "choky": "AKTUELLEN POSTEN SETZEN", "okchy": "AKTUELLEN POSTEN SETZEN", "oky": "AKTUELLEN POSTEN SETZEN",
    "chol": "FORTSETZEN", "ol": "FORTSETZEN", "tol": "FORTSETZEN",
    "dain": "ABDECKTRÄGER",
    "kchey": "KURZ BEARBEITEN", "kchy": "BEARBEITEN",
    "ody": "ZURÜCKNEHMEN",
    "okain": "GEZÄHLTEN TEIL ZUGEBEN",
    "okal": "AM ZIEL SETZEN",
    "okeey": "LANGE STUFE SETZEN", "okey": "KURZE STUFE SETZEN", "qokeeedy": "VOLLSTÄNDIG SETZEN; SCHLUSS",
    "olor": "FORTGESETZTER ANSATZ", "or": "ANSATZ", "sor": "ANSATZ",
    "os": "UMSCHLIESSENDER TRÄGER",
    "otar": "DANACH VOM AUSGANG", "otchdy": "FOLGENDEN POSTEN ÜBERTRAGEN; SCHLUSS",
    "otchey": "NÄCHSTER POSTEN", "oteey": "NÄCHSTER POSTEN; LANGE STUFE", "otol": "DANACH FORTSETZEN",
    "oldy": "FORTSETZEN; SCHLUSS",
    "sheey": "LÄNGER HALTEN",
}


METAPHORICAL_FORMS = {"cheey", "dain", "ody", "olor", "or", "os", "shey", "sor"}


def main() -> None:
    bridge = read_tsv(READER / "CROSS_REGISTER_44_SURFACE_BRIDGE.tsv")
    trace = read_tsv(READER / "TEN_PAGE_776_READER_TRACE.tsv")
    selected_echoes = read_tsv(PATHS / "SELECTED_9_CROSS_REGISTER_ECHOS.tsv")
    selected_choices = read_tsv(PATHS / "SELECTED_13_ASTRO_CHOICES.tsv")
    selected_paths = read_tsv(PATHS / "FOUR_SELECTED_JOB_PATHS.tsv")

    family_by_surface: dict[str, tuple[str, str, str, str, str, str]] = {}
    for spec in FAMILY_SPECS:
        for surface in spec[2].split():
            if surface in family_by_surface:
                raise ValueError(f"surface in two common families: {surface}")
            family_by_surface[surface] = spec
    if set(family_by_surface) != set(CARD_NUCLEI):
        raise ValueError("common family inventory and card values differ")
    bridge_by_surface = {row["visible_surface"]: row for row in bridge}
    if set(bridge_by_surface) != set(CARD_NUCLEI):
        raise ValueError("the common dictionary does not cover the exact 44-surface bridge")

    selected_echo_surfaces = {row["visible_surface"] for row in selected_echoes}
    prose_occurrences = Counter(row["visible_surface"] for row in trace if row["register"] == "PROSE")
    astro_occurrences = Counter(row["visible_surface"] for row in trace if row["register"] == "ASTRO")

    lexicon_rows: list[dict[str, object]] = []
    for surface in sorted(bridge_by_surface):
        source = bridge_by_surface[surface]
        family_id, family_name, members, composition, prose_family, astro_family = family_by_surface[surface]
        lexicon_rows.append({
            "visible_surface": surface,
            "prose_master_card_id": source["prose_master_card_id"],
            "family_id": family_id,
            "family_name_de": family_name,
            "common_nucleus_de": CARD_NUCLEI[surface],
            "composition_de": composition,
            "prose_local_expansion_de": source["prose_unique_reading_de"],
            "astro_local_expansions_de": source["astro_owner_readings_de"],
            "prose_occurrence_count": prose_occurrences[surface],
            "astro_occurrence_count": astro_occurrences[surface],
            "astro_owner_count": source["astro_owner_count"],
            "fit_type": "WORKSHOP_REGISTER_METAPHOR" if surface in METAPHORICAL_FORMS else "DIRECT_SHARED_OPERATION",
            "selected_path_echo": "YES" if surface in selected_echo_surfaces else "NO",
            "teaching_rule_de": f"{surface} heißt kurz {CARD_NUCLEI[surface]}; Besitzer und Register nennen den konkreten Gegenstand",
        })
    lexicon_fields = [
        "visible_surface", "prose_master_card_id", "family_id", "family_name_de", "common_nucleus_de",
        "composition_de", "prose_local_expansion_de", "astro_local_expansions_de",
        "prose_occurrence_count", "astro_occurrence_count", "astro_owner_count", "fit_type",
        "selected_path_echo", "teaching_rule_de",
    ]
    write_tsv(OUT / "COMMON_44_CARD_LEXICON.tsv", lexicon_rows, lexicon_fields)

    family_rows: list[dict[str, object]] = []
    for family_id, family_name, members, composition, prose_family, astro_family in FAMILY_SPECS:
        member_list = members.split()
        family_rows.append({
            "family_id": family_id,
            "family_name_de": family_name,
            "member_count": len(member_list),
            "visible_members": ";".join(member_list),
            "composition_rule_de": composition,
            "shared_operation_de": family_name.upper(),
            "prose_expansion_de": prose_family,
            "astro_expansion_de": astro_family,
            "apprentice_rule_de": "zuerst gemeinsamen Kern lesen, dann Besitzer einsetzen",
        })
    family_fields = [
        "family_id", "family_name_de", "member_count", "visible_members", "composition_rule_de",
        "shared_operation_de", "prose_expansion_de", "astro_expansion_de", "apprentice_rule_de",
    ]
    write_tsv(OUT / "COMMON_20_FAMILY_GRAMMAR.tsv", family_rows, family_fields)

    shared_surfaces = set(bridge_by_surface)
    common_occurrence_rows: list[dict[str, object]] = []
    complete_reader_rows: list[dict[str, object]] = []
    for row in trace:
        surface = row["visible_surface"]
        if surface in shared_surfaces:
            family_id = family_by_surface[surface][0]
            nucleus = CARD_NUCLEI[surface]
            shared_status = "COMMON_44_CARD"
            reader_path = "COMMON_NUCLEUS_THEN_REGISTER_EXPANSION"
            common_occurrence_rows.append({
                "common_occurrence_serial": f"C{len(common_occurrence_rows) + 1:03d}",
                "register": row["register"],
                "page": row["page"],
                "source_group_id": row["source_group_id"],
                "reading_unit_id": row["reading_unit_id"],
                "visible_owner": row["visible_owner"],
                "visible_surface": surface,
                "family_id": family_id,
                "common_nucleus_de": nucleus,
                "register_expansion_de": row["resolved_reading_de"],
                "selected_path_echo": "YES" if surface in selected_echo_surfaces else "NO",
            })
        else:
            family_id = "LOCAL_OR_REGISTER_CARD"
            nucleus = row["resolved_reading_de"]
            shared_status = "NOT_SHARED_ACROSS_REGISTERS"
            reader_path = "CURRENT_LOCAL_READER_VALUE"
        complete_reader_rows.append({
            **row,
            "shared_card_status": shared_status,
            "common_family_id": family_id,
            "common_nucleus_de": nucleus,
            "final_register_reading_de": row["resolved_reading_de"],
            "common_reader_path": reader_path,
        })
    occurrence_fields = [
        "common_occurrence_serial", "register", "page", "source_group_id", "reading_unit_id",
        "visible_owner", "visible_surface", "family_id", "common_nucleus_de",
        "register_expansion_de", "selected_path_echo",
    ]
    write_tsv(OUT / "COMMON_187_OCCURRENCE_TRACE.tsv", common_occurrence_rows, occurrence_fields)
    complete_fields = list(trace[0]) + [
        "shared_card_status", "common_family_id", "common_nucleus_de",
        "final_register_reading_de", "common_reader_path",
    ]
    write_tsv(OUT / "TEN_PAGE_776_COMMON_READER.tsv", complete_reader_rows, complete_fields)

    # Re-read the thirteen selected condition choices with the common lexicon.
    complete_by_group = {row["source_group_id"]: row for row in complete_reader_rows}
    header_lines = [
        "# Vier Auftragsköpfe im gemeinsamen Kartenwörterbuch", "",
        "Gemeinsame Karten werden zuerst mit ihrem kurzen Kern gelesen. Nur Formen außerhalb des 44er-Bestands bleiben lokale Besitzerwerte.", "",
    ]
    for path in selected_paths:
        did = path["work_order_id"]
        header_lines += [f"## {did} — {path['title_de']}", "", f"**Flüssige Bedingung:** {path['selected_condition_de']}", ""]
        for choice in (row for row in selected_choices if row["work_order_id"] == did):
            group_ids = choice["source_group_ids"].split(";")
            parts = []
            for group_id in group_ids:
                item = complete_by_group[group_id]
                if item["shared_card_status"] == "COMMON_44_CARD":
                    parts.append(f"`{item['visible_surface']}` = {item['common_nucleus_de']}")
                else:
                    parts.append(f"`{item['visible_surface']}` = lokaler Wert: {item['final_register_reading_de']}")
            header_lines.append(f"- **{choice['selection_id']}** — " + "; ".join(parts))
        header_lines.append("")
    (OUT / "FOUR_JOB_HEADERS_COMMON_CARDS.md").write_text("\n".join(header_lines).rstrip() + "\n", encoding="utf-8")

    pocket_lines = [
        "# Taschenwörterbuch der 44 gemeinsamen Karten", "",
        "Diese Karten stehen mit exakt derselben sichtbaren Form in praktischer Prosa und in den Diagrammen. Die kurze Bedeutung bleibt gleich; Bildbesitzer und Register konkretisieren sie.", "",
        "## Zwanzig Lehrfamilien", "",
    ]
    for row in family_rows:
        pocket_lines.append(
            f"- **{row['family_id']} · {row['family_name_de']}:** `{str(row['visible_members']).replace(';', '`, `')}` — Prosa: {row['prose_expansion_de']}; Diagramm: {row['astro_expansion_de']}."
        )
    pocket_lines += ["", "## Alle 44 Karten", ""]
    for row in lexicon_rows:
        marker = " ★" if row["selected_path_echo"] == "YES" else ""
        pocket_lines += [
            f"### `{row['visible_surface']}`{marker}", "",
            f"- Kern: **{row['common_nucleus_de']}**",
            f"- Prosa: {row['prose_local_expansion_de']}",
            f"- Diagramm: {row['astro_local_expansions_de']}",
            f"- Familie: {row['family_id']}", "",
        ]
    pocket_lines += ["★ = in einem der vier konkreten Musteraufträge ausgewählt.", ""]
    (OUT / "COMMON_44_POCKET_DICTIONARY.md").write_text("\n".join(pocket_lines).rstrip() + "\n", encoding="utf-8")

    direct_count = sum(row["fit_type"] == "DIRECT_SHARED_OPERATION" for row in lexicon_rows)
    metaphor_count = len(lexicon_rows) - direct_count
    prose_shared = sum(row["register"] == "PROSE" for row in common_occurrence_rows)
    astro_shared = sum(row["register"] == "ASTRO" for row in common_occurrence_rows)
    affected_units = len({(row["register"], row["reading_unit_id"]) for row in common_occurrence_rows})
    report = f"""# Gemeinsames 44-Karten-Wörterbuch

## Ergebnis

Alle 44 sichtbaren Formen, die sowohl in der Prosa als auch auf den Diagrammseiten vorkommen, lassen sich jetzt mit einem kurzen gemeinsamen Werkstattkern lesen. Sie ordnen sich in 20 lehrbare Familien. Der gemeinsame Bestand umfasst 187 sichtbare Vorkommen: {prose_shared} in der Prosa und {astro_shared} in den Diagrammen, verteilt über {affected_units} Aussagen oder sichtbare Diagrammorte.

Bei {direct_count} Karten ist die Übereinstimmung direkt: Quelle, Ziel, aktueller Posten, Fortsetzung, Setzen, kurzer oder langer Grad, Übertragung und Schluss bleiben in beiden Registern dieselbe Operation. {metaphor_count} Karten brauchen eine kleine Werkstattmetapher, aber keine beliebige Bedeutungsänderung.

## Die wichtigsten gemeinsamen Familien

- `aiin/daiin/saiin` = **Vorgabewert**: Stoffmaß in der Prosa, Platzgrad im Diagramm.
- `char/dar/sar` = **vom Ausgang**; `cheal/dal/sal` = **zum Ziel**.
- `chey/chy/dy/sy/y` = **aktueller Posten**.
- `choky/okchy/oky` = **aktuellen Posten setzen**.
- `chol/ol/tol` = **fortsetzen**.
- `okeey/okey/qokeeedy` = **lange, kurze oder vollständige Setzstufe**.
- Die OT-Reihe bezeichnet den **Folgeposten** und kombiniert ihn mit Quelle, Transfer, Grad oder Fortsetzung.

## Acht nützliche Metaphern und Grenzfälle

`cheey/shey` heißt im Kern nicht zwingend Wasser, sondern **freigegebener oder ausgelesener Wert**: im Arbeitsgang der klare Auszug, im Diagramm der abgelesene Wert. `dain` ist ein **Abdeckträger**, konkret Tuch oder Diagrammband. `or/sor/olor` ist ein **Ansatz oder Satz**, praktisch eine Zubereitung, tabellarisch ein Bedingungssatz. `os` ist der **umschließende Träger**, praktisch das Gefäß, graphisch das Feld. `ody` heißt am knappsten **zurücknehmen**: den Stoff zum Abkühlen aus dem aktiven Gang nehmen oder einen Diagrammposten zurücknehmen.

## Was das für die vier Aufträge ändert

Neun der 21 konkret ausgewählten Diagrammgruppen verwenden eine der gemeinsamen Karten. Dadurch sind ihre Auftragsköpfe nicht bloß lokal erfundene Himmelswerte: `aiin`, `cheey`, `cho`, `dal`, `dy`, `okeey`, `okey`, `oldy` und `sheey` sprechen dieselbe kurze Werkstattsprache wie die Prosa. Die zwölf übrigen gewählten Diagrammgruppen bleiben lokale Besitzerwerte.

Das vollständige 776-Gruppen-Lesebuch bleibt erhalten. `TEN_PAGE_776_COMMON_READER.tsv` ergänzt lediglich den gemeinsamen Kern und bewahrt daneben jede bisherige konkrete Registerlesung.
"""
    (OUT / "COMMON_44_CARD_REPORT.md").write_text(report, encoding="utf-8")

    content_names = [
        "COMMON_44_CARD_LEXICON.tsv", "COMMON_20_FAMILY_GRAMMAR.tsv",
        "COMMON_187_OCCURRENCE_TRACE.tsv", "TEN_PAGE_776_COMMON_READER.tsv",
        "FOUR_JOB_HEADERS_COMMON_CARDS.md", "COMMON_44_POCKET_DICTIONARY.md",
        "COMMON_44_CARD_REPORT.md",
    ]
    summary = {
        "status": "BUILT",
        "common_surfaces": len(lexicon_rows),
        "common_families": len(family_rows),
        "direct_shared_operations": direct_count,
        "workshop_register_metaphors": metaphor_count,
        "common_occurrences": len(common_occurrence_rows),
        "prose_common_occurrences": prose_shared,
        "astro_common_occurrences": astro_shared,
        "affected_reading_units": affected_units,
        "selected_path_echo_surfaces": len(selected_echo_surfaces),
        "complete_reader_groups": len(complete_reader_rows),
        "source_sha256": {
            "cross_register_bridge": sha256(READER / "CROSS_REGISTER_44_SURFACE_BRIDGE.tsv"),
            "unified_reader_trace": sha256(READER / "TEN_PAGE_776_READER_TRACE.tsv"),
            "selected_echoes": sha256(PATHS / "SELECTED_9_CROSS_REGISTER_ECHOS.tsv"),
        },
        "output_sha256": {name: sha256(OUT / name) for name in content_names},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

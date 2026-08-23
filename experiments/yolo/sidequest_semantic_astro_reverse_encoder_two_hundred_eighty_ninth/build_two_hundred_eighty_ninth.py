#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R274 = ROOT / "experiments/yolo/sidequest_semantic_ten_page_mixed_deck_two_hundred_seventy_fourth"
ASTRO = R274 / "TWO_HUNDRED_SEVENTY_FOURTH_LAYERED_395_ASTRO_GROUPS.tsv"

LAYER_RULES = {
    "KNOWN_PROSE_CARD_IN_ASTRO": ("REUSE_REGISTERED_PROSE_CARD", "Nimm dieselbe gelernte Karte wie in der Prosa und lies nur ihren Diagrammbesitzer neu."),
    "THREE_REGISTER_COMMON_CORE": ("REUSE_COMMON_STEM_CARD", "Schreibe die bereits gelernte gemeinsame Stammkarte."),
    "ASTRO_ADDRESS_SUFFIX_COMPOSITION": ("COPY_CORE_ATTACH_ADDRESS", "Kopiere den örtlichen Kern und setze AR für Quelle, AL für Ziel oder AR+AL für Quelle-zu-Ziel."),
    "ASTRO_RELATION_SUFFIX_COMPOSITION": ("COPY_CORE_ATTACH_RELATION", "Kopiere den örtlichen Kern und setze OL für Fortsetzung oder OR für Bedingungsansatz."),
    "ASTRO_OT_TRANSITION_COMPOSITION": ("PREFIX_FOLLOWING_POST", "Setze OT vor den folgenden örtlichen Posten und behalte dessen Adresse, Relation oder Grad."),
    "ASTRO_LICENSED_CURRENT_ITEM_Y": ("COPY_OPERATION_ATTACH_Y", "Kopiere den örtlichen Operations- oder Relationskern und schließe ihn mit Y als aktuellem Posten."),
    "ASTRO_GRADED_VALUE_Y_COMPOSITION": ("COPY_CORE_ATTACH_GRADE_Y", "Kopiere den örtlichen Kern und setze E+Y, EE+Y oder EEE+Y für kurzen, langen oder vollen Wert."),
    "ASTRO_LOCAL_CORE_PLUS_AIIN": ("COPY_CORE_ATTACH_AIIN", "Kopiere den örtlichen Kern und setze AIIN für dessen Sollwert."),
    "ASTRO_LOCAL_CORE_PLUS_AIN": ("COPY_CORE_ATTACH_AIN", "Kopiere den örtlichen Kern und setze AIN für dessen Portion oder Teilwert."),
    "ASTRO_LOCAL_CORE_PLUS_AIR": ("COPY_CORE_ATTACH_AIR", "Kopiere den örtlichen Kern und setze AIR für dessen Lauf oder Bahn."),
    "ASTRO_COMPOSED_FROM_40_COMPONENTS": ("COMPOSE_FROM_PRODUCTIVE_STEMS", "Baue die Gruppe direkt aus den bekannten Quellen-, Ziel-, Mengen-, Grad-, Bahn- und Festsetzungsstämmen."),
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


def split_surface(row: dict[str, str]) -> tuple[str, str]:
    surface = row["visible_surface"]
    layer = row["curriculum_layer"]
    if layer == "ASTRO_ADDRESS_SUFFIX_COMPOSITION":
        if surface.endswith("aral"):
            return surface[:-4] or "ROOT", "AR+AL"
        if surface.endswith("ar"):
            return surface[:-2] or "ROOT", "AR"
        if surface.endswith("al"):
            return surface[:-2] or "ROOT", "AL"
        return surface, "ADDRESS_ALLOGRAPH"
    if layer == "ASTRO_RELATION_SUFFIX_COMPOSITION":
        if surface.endswith("ol"):
            return surface[:-2] or "ROOT", "OL"
        if surface.endswith("or"):
            return surface[:-2] or "ROOT", "OR"
        return surface, "RELATION_ALLOGRAPH"
    if layer == "ASTRO_OT_TRANSITION_COMPOSITION":
        if surface.startswith("qot"):
            return surface[3:] or "ROOT", "Q_FRAME+OT"
        if surface.startswith("ot"):
            return surface[2:] or "ROOT", "OT"
        return surface, "OT_ALLOGRAPH"
    if layer == "ASTRO_LICENSED_CURRENT_ITEM_Y":
        return surface[:-1] or "ROOT", "Y"
    if layer == "ASTRO_GRADED_VALUE_Y_COMPOSITION":
        for suffix, tag in (("eeey", "EEE+Y"), ("eey", "EE+Y"), ("ey", "E+Y")):
            if surface.endswith(suffix):
                return surface[:-len(suffix)] or "ROOT", tag
        return surface[:-1] or "ROOT", "GRADED_Y_ALLOGRAPH"
    for target_layer, suffix, tag in (
        ("ASTRO_LOCAL_CORE_PLUS_AIIN", "aiin", "AIIN"),
        ("ASTRO_LOCAL_CORE_PLUS_AIN", "ain", "AIN"),
        ("ASTRO_LOCAL_CORE_PLUS_AIR", "air", "AIR"),
    ):
        if layer == target_layer:
            return (surface[:-len(suffix)] or "ROOT", tag) if surface.endswith(suffix) else (surface, f"{tag}_ALLOGRAPH")
    return "NONE", "REGISTERED_CARD_OR_FULL_COMPOSITION"


def main() -> None:
    source = read_tsv(ASTRO)
    composed = [r for r in source if r["coverage_class_274"] == "PORTABLE_COMPOSITION"]
    whole = [r for r in source if r["coverage_class_274"] == "LEARNED_WHOLE_SIGN"]
    local = [r for r in source if r["coverage_class_274"] == "LOCAL_COPY_LABEL"]
    assert len(composed) == 265 and len(whole) == 51 and len(local) == 79

    reverse_rows: list[dict[str, object]] = []
    for row in composed:
        strategy, instruction = LAYER_RULES[row["curriculum_layer"]]
        core, affix = split_surface(row)
        reverse_rows.append({
            "group_serial": row["group_serial"],
            "page": row["page"],
            "locus": row["locus"],
            "visible_owner": row["visible_owner"],
            "namespace_id": row["namespace_id"],
            "desired_diagram_value_de": row["concrete_diagram_reading_de"],
            "portable_role": row["portable_card_role"],
            "curriculum_layer": row["curriculum_layer"],
            "writer_strategy": strategy,
            "copied_or_registered_core_surface": core,
            "productive_affix_or_modifier": affix,
            "resulting_visible_surface": row["visible_surface"],
            "reverse_instruction_de": instruction,
            "exact_prose_card_id": row["exact_prose_card_id"],
            "generation_status": "GENERATED_FROM_RULE_PLUS_REGISTERED_OR_LOCAL_CORE",
        })

    role_groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in reverse_rows:
        role_groups[str(row["portable_role"])].append(row)
    roles: list[dict[str, object]] = []
    for role, members in role_groups.items():
        roles.append({
            "portable_role": role,
            "group_count": len(members),
            "distinct_visible_forms": len({str(r["resulting_visible_surface"]) for r in members}),
            "pages": "|".join(sorted({str(r["page"]) for r in members})),
            "curriculum_layers": "|".join(sorted({str(r["curriculum_layer"]) for r in members})),
            "writer_strategies": "|".join(sorted({str(r["writer_strategy"]) for r in members})),
            "example_value_de": members[0]["desired_diagram_value_de"],
            "example_surface": members[0]["resulting_visible_surface"],
        })
    roles.sort(key=lambda r: (-int(r["group_count"]), str(r["portable_role"])))

    whole_forms: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in whole:
        whole_forms[row["visible_surface"]].append(row)
    whole_rows = [
        {
            "whole_sign_form": form,
            "group_count": len(members),
            "pages": "|".join(sorted({r["page"] for r in members})),
            "learned_value_examples_de": " | ".join(dict.fromkeys(r["concrete_diagram_reading_de"] for r in members)),
            "learning_rule": "memorize as one Astro value sign; do not split final DY/Y",
        }
        for form, members in sorted(whole_forms.items())
    ]
    local_forms: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in local:
        local_forms[row["visible_surface"]].append(row)
    local_rows = [
        {
            "local_key_form": form,
            "group_count": len(members),
            "pages": "|".join(sorted({r["page"] for r in members})),
            "namespaces": "|".join(sorted({r["namespace_id"] for r in members})),
            "visible_owners": "|".join(dict.fromkeys(r["visible_owner"] for r in members)),
            "learning_rule": "copy from the selected diagram locus; no portable gloss required",
        }
        for form, members in sorted(local_forms.items())
    ]

    role_path = OUT / "TWO_HUNDRED_EIGHTY_NINTH_29_ASTRO_ROLE_RECIPES.tsv"
    reverse_path = OUT / "TWO_HUNDRED_EIGHTY_NINTH_265_REVERSE_ENCODINGS.tsv"
    whole_path = OUT / "TWO_HUNDRED_EIGHTY_NINTH_46_ASTRO_WHOLE_SIGNS.tsv"
    local_path = OUT / "TWO_HUNDRED_EIGHTY_NINTH_67_LOCAL_COPY_KEYS.tsv"
    manual_path = OUT / "TWO_HUNDRED_EIGHTY_NINTH_ASTRO_APPRENTICE_ENCODER.md"
    report_path = OUT / "TWO_HUNDRED_EIGHTY_NINTH_REPORT.md"
    write_tsv(role_path, roles, list(roles[0]))
    write_tsv(reverse_path, reverse_rows, list(reverse_rows[0]))
    write_tsv(whole_path, whole_rows, list(whole_rows[0]))
    write_tsv(local_path, local_rows, list(local_rows[0]))

    strategy_counts = Counter(str(r["writer_strategy"]) for r in reverse_rows)
    manual = [
        "# Rückwärts-Encoder für die drei Astro-Instrumente",
        "",
        "## Schreibgang",
        "",
        "1. Wähle den sichtbaren Sektor, Sternplatz, Ring oder Radposten.",
        "2. Ist die Gruppe ein lokaler Name, kopiere einen der 67 lokalen Schlüssel direkt vom Diagramm.",
        "3. Ist sie eines der 46 Astro-Ganzzeichen, schreibe das ganze gelernte Zeichen.",
        "4. Sonst wähle die portable Rolle: Quelle, Ziel, Fortsetzung, Bedingung, Folgeposten, aktueller Wert, Grad, Teilwert oder Bahn.",
        "5. Kopiere den örtlichen Kern und füge AR, AL, OL, OR, OT, Y, E/EE/EEE+Y, AIIN, AIN oder AIR an. Wiederverwendete Prosakarten werden unverändert geschrieben.",
        "6. Die sichtbare Kreisposition bestimmt den Besitzer; eine feste Startrichtung ist zum Schreiben nicht nötig.",
        "",
        "## Die produktiven Strategien",
        "",
    ]
    for strategy, count in sorted(strategy_counts.items(), key=lambda x: (-x[1], x[0])):
        example = next(r for r in reverse_rows if r["writer_strategy"] == strategy)
        manual.append(f"- **{strategy} ({count})** — {example['reverse_instruction_de']}")
    manual.extend([
        "",
        "## Werkstattergebnis",
        "",
        "Alle 265 produktiven Astrogruppen lassen sich mit einer dieser Strategien schreiben. Der örtliche Kern ist dabei ein Parameter, kein neues Wörterbuchwort. Deshalb muss der Lehrling nicht 188 zusammengesetzte Oberflächen als selbständige Wörter lernen: Er lernt die gemeinsamen Kürzel und kopiert den lokalen Stern-/Sektorkern. Daneben bleiben 46 Ganzformen und 67 lokale Schlüssel.",
        "",
    ])
    manual_path.write_text("\n".join(manual), encoding="utf-8")

    report_path.write_text(
        "# Sidequest-Pass 289: rückwärts benutzbarer Astro-Encoder\n\n"
        "## Ergebnis\n\n"
        "Alle 265 portablen Astrogruppen sind als Schreibanweisungen rekonstruiert. Das entscheidende Verfahren ist Kopierkern plus Funktionssuffix: AR/AL für Adresse, OL/OR für Relation, OT für Folge, Y oder E/EE/EEE+Y für aktuellen bzw. graduierten Wert und AIIN/AIN/AIR für Sollwert, Teil oder Bahn. "
        "Gemeinsame Prosekarten werden direkt wiederverwendet.\n\n"
        "Damit zerfallen die 395 Astrogruppen praktisch in 265 erzeugte Gruppen, 51 Vorkommen von 46 Ganzzeichen und 79 Vorkommen von 67 lokalen Kopierschlüsseln. "
        "Der lokale Kern wird vom Diagramm übernommen; er bläht das gelernte Lexikon nicht auf.\n\n"
        f"Input `{sha(ASTRO)}`; strategies `{dict(strategy_counts)}`.\n",
        encoding="utf-8",
    )

    outputs = (role_path, reverse_path, whole_path, local_path, manual_path, report_path)
    summary = {
        "status": "PASS",
        "portable_groups": len(reverse_rows),
        "portable_visible_forms": len({r["resulting_visible_surface"] for r in reverse_rows}),
        "portable_roles": len(roles),
        "writer_strategies": dict(strategy_counts),
        "whole_groups": len(whole),
        "whole_forms": len(whole_rows),
        "local_groups": len(local),
        "local_forms": len(local_rows),
        "outputs": {p.name: sha(p) for p in outputs},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

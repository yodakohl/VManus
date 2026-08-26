#!/usr/bin/env python3
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
HERE = ROOT / "experiments/yolo/gdt414_next_page_semantic_failure_deck"
OUT = HERE / "artifacts"
EVENTS = ROOT / "experiments/yolo/gdt413_twenty_six_page_semantic_working_edition/artifacts/gdt413_4576_event_semantic_edition.tsv"
LEAVEOUT = ROOT / "experiments/yolo/gdt408_twenty_six_page_leave_one_page_transfer/artifacts/gdt408_4576_event_leaveout.tsv"
CORE_DICT = ROOT / "experiments/yolo/gdt412_chd_process_core_completion/artifacts/gdt412_final_19_core_dictionary.tsv"
COMPONENT_DICT = ROOT / "experiments/yolo/gdt413_twenty_six_page_semantic_working_edition/artifacts/gdt413_46_component_working_dictionary.tsv"

REGISTERS = ("HERBAL", "BIOLOGICAL", "CELESTIAL", "PHARMA", "SOURCE_SECTION_T")
SUPPORT_RANK = {
    "EXACT_SURFACE_FROM_OTHER_PAGE": 0,
    "EXACT_RECIPE_FROM_OTHER_PAGE": 1,
    "ALL_ADJACENT_PACKAGES_FROM_OTHER_PAGES": 2,
    "KNOWN_ATOMS_NEW_PACKAGE_COMPOSITION": 3,
    "KNOWN_ATOM_NO_INTERNAL_PAIR": 4,
    "KNOWN_CORE_PLUS_PAGE_PRIVATE_LOCAL_SIGN": 5,
}

POLICIES = {
    "Y": ("dieser Teil; dieses Gefäß; diese Station; dieser Sektor", "nicht als Schluss lesen, auch wenn die Oberfläche dy lautet", "der Kern müsste ohne Besitzer ein festes fremdes Nomen benennen"),
    "OK": ("ansetzen; aktivieren; in den Arbeitsgang setzen", "nicht automatisch erhitzen, spülen oder beginnen", "die Karte wäre nur ein Gegenstand und kein Einsetz-/Aktivierungskopf"),
    "OL": ("weiter; mit dem Vorigen; im selben Gang", "niemals aus der Oberfläche Öl ableiten", "es gibt weder Vorbezug noch fortsetzbaren Geschwistergang"),
    "OT": ("danach; nächster Geschwistergang", "nicht automatisch erneut oder rückwärts", "der Kern müsste stabil VORHER statt DANACH bedeuten"),
    "AL": ("Ziel; Empfänger; Körper-/Stationsstelle", "keine Anatomie und keine Richtung ohne Besitzer erfinden", "dieselbe Hülle erzwingt wiederholt die Ausgangsseite"),
    "AR": ("Quelle; Ausgang; Entnahmestelle", "kein sichtbarer Pfeil darf stillschweigend ergänzt werden", "dieselbe Hülle erzwingt wiederholt den Ziel-/Empfängerwert"),
    "AIIN": ("Maß; Dosis; Grad; Positionswert", "keine Zahl, Waage oder Einheit behaupten, wenn sie nicht lokal vorliegt", "der Kern müsste eine konkrete Substanz oder Person benennen"),
    "AIN": ("Anteil; Portion; Sektoranteil", "nicht automatisch eins oder gleiche Teile", "der Kern verhält sich als unteilbarer Gegenstand statt Anteilslot"),
    "OR": ("Arbeits-, Becken-, Satz- oder Sektoreinheit", "nicht universell Ansatz, Sud oder Gefäß", "der Kern müsste registerübergreifend eine konkrete Stoffart benennen"),
    "L": ("Verbindung; Mitbezug; Anschluss", "nicht Öl und nicht zwingend Rohr", "es bleibt wiederholt kein zweiter Bezug oder anschließbares Paket"),
    "AIR": ("Wasserlauf; Ringbahn; Kurs; Leitungsbahn", "nicht Wasser als Stoff und nicht sichtbare Flussrichtung", "die Karte müsste als stillstehender Stoff ohne Bahnbezug gelesen werden"),
    "CH": ("entnehmen; aufnehmen; heranziehen", "nicht den ganzen folgenden Arbeitsgang in NEHMEN packen", "der Kern ist wiederholt nur Zustand oder Schluss und keine Entnahmehandlung"),
    "SH": ("halten; ruhen lassen; aufbewahren", "nicht automatisch Wärme, Klarheit oder Dauer", "die Karte erzwingt wiederholt eine Übergabe statt Beibehaltung"),
    "K": ("zugeben; zuteilen; zuordnen", "nicht automatisch Wasser oder Empfänger", "die Karte erzwingt wiederholt Entnahme statt Übergabe/Zuweisung"),
    "S": ("auswählen; entscheiden; prüfend auswählen", "nicht universell trennen oder prüfen", "der Kern hat keinen Auswahlkontrast und bezeichnet nur Behandlung"),
    "CHD": ("mischen; umsetzen; auftragen; abführen; weiterbearbeiten", "nicht als Schluss lesen; Schluss braucht eine lizenzierte Endhülle", "die nackte CHD+Y-Familie verlangt einen anderen Grundwert als POSTEN BEARBEITEN"),
    "T": ("einstellen; bestimmen; einen Grad setzen", "nicht automatisch Zeit oder Wärme", "der Kern hat wiederholt keinen einstellbaren Wert, Grad oder Zielbezug"),
    "R": ("markieren; verweisen; kennzeichnen", "nicht als Stoff oder eigenes Ziel lesen", "Kopf- und Schwanzlage lassen sich nicht mehr als Markierung vereinen"),
    "P": ("einsetzen; einbringen; an einer Stelle ansetzen", "nicht universell Satz- oder Absatzbeginn", "der Kern bleibt wiederholt rein zeitlicher Beginn ohne eingesetzten Posten"),
}


def read_tsv(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cards(recipe):
    return recipe.split(" | ")


def flattened(recipe):
    return [(card_index, atom_index, atom) for card_index, card in enumerate(cards(recipe), 1) for atom_index, atom in enumerate(card.split("+"), 1)]


def pack(counter, limit=8):
    return "|".join(f"{key}:{value}" for key, value in counter.most_common(limit)) if counter else "NONE"


def main():
    events = read_tsv(EVENTS)
    leaveout = read_tsv(LEAVEOUT)
    roots = read_tsv(CORE_DICT)
    components = read_tsv(COMPONENT_DICT)
    root_by_id = {row["root"]: row for row in roots}
    component_ids = {row["atom"] for row in components}
    leaveout_by_event = {row["global_running_event_id"]: row for row in leaveout}
    recipe_frequency = Counter(row["component_recipe"] for row in events)

    mention_rows = []
    root_register_mentions = defaultdict(Counter)
    root_register_pages = defaultdict(lambda: defaultdict(set))
    root_register_events = defaultdict(lambda: defaultdict(set))
    root_register_companions = defaultdict(Counter)
    root_support = defaultdict(Counter)
    root_surfaces = defaultdict(Counter)
    root_pages = defaultdict(set)
    for event in events:
        atoms = flattened(event["component_recipe"])
        support = leaveout_by_event[event["global_running_event_id"]]
        for flat_ordinal, (card_ordinal, atom_ordinal, atom) in enumerate(atoms, 1):
            if atom not in root_by_id:
                continue
            companions = [other for _, _, other in atoms if other != atom]
            root_register_mentions[(atom, event["register"])]["mentions"] += 1
            root_register_pages[atom][event["register"]].add(event["physical_page"])
            root_register_events[atom][event["register"]].add(event["global_running_event_id"])
            root_register_companions[(atom, event["register"])].update(companions)
            root_support[atom][support["leave_one_page_replay_class"]] += 1
            root_surfaces[atom][event["surface"]] += 1
            root_pages[atom].add(event["physical_page"])
            mention_rows.append({
                "root": atom,
                "working_value_de": root_by_id[atom]["selected_minimal_value_de"],
                "global_running_event_id": event["global_running_event_id"],
                "global_running_ordinal": event["global_running_ordinal"],
                "physical_page": event["physical_page"],
                "register": event["register"],
                "locus": event["locus"],
                "source_statement_id": event["source_statement_id"],
                "owner_de": event["owner_de"],
                "surface": event["surface"],
                "component_recipe": event["component_recipe"],
                "card_ordinal": card_ordinal,
                "atom_ordinal_in_card": atom_ordinal,
                "flat_atom_ordinal": flat_ordinal,
                "leave_one_page_support_class": support["leave_one_page_replay_class"],
                "other_surface_pages": support["other_surface_pages"],
                "other_recipe_pages": support["other_recipe_pages"],
                "unsupported_adjacent_pairs": support["unsupported_adjacent_pairs"],
                "working_core_reading_de": event["working_core_reading_de"],
                "semantic_disposition": "KEEP_BROAD_DEFAULT__LOCAL_EXPANSION_FROM_OWNER",
            })

    matrix_rows = []
    for root in root_by_id:
        for register in REGISTERS:
            key = (root, register)
            matrix_rows.append({
                "root": root,
                "working_value_de": root_by_id[root]["selected_minimal_value_de"],
                "register": register,
                "mention_count": root_register_mentions[key]["mentions"],
                "event_count": len(root_register_events[root][register]),
                "page_count": len(root_register_pages[root][register]),
                "pages": "|".join(sorted(root_register_pages[root][register])) if root_register_pages[root][register] else "NONE",
                "top_companion_atoms": pack(root_register_companions[key]),
                "allowed_register_expansion_de": POLICIES[root][0],
                "register_rule": "DEFAULT BLEIBT GLEICH; NUR BESITZERLOKALE KONKRETISIERUNG",
            })

    deck_rows = []
    weakest_rows = []
    for root, row in root_by_id.items():
        root_mentions = [item for item in mention_rows if item["root"] == root]
        weakest = max(
            root_mentions,
            key=lambda item: (
                SUPPORT_RANK[item["leave_one_page_support_class"]],
                -recipe_frequency[item["component_recipe"]],
                -int(item["global_running_ordinal"]),
            ),
        )
        allowed, warning, red = POLICIES[root]
        deck_rows.append({
            "root": root,
            "working_value_de": row["selected_minimal_value_de"],
            "structural_category": row["structural_category"],
            "mention_count": len(root_mentions),
            "event_count": len({item["global_running_event_id"] for item in root_mentions}),
            "page_count": len(root_pages[root]),
            "register_count": len({item["register"] for item in root_mentions}),
            "leave_one_page_support_counts": pack(root_support[root], 10),
            "allowed_owner_local_expansions_de": allowed,
            "do_not_overread_de": warning,
            "green_next_page_condition_de": "Kernrolle und Default bleiben erhalten; neuer Gegenstand kommt nur aus Besitzer/Hülle",
            "amber_next_page_condition_de": "Default bleibt möglich, aber Komplement- oder Besitzerklasse ist auf den 26 Seiten neu",
            "red_next_page_condition_de": red,
            "weakest_current_event_id": weakest["global_running_event_id"],
            "weakest_current_support_class": weakest["leave_one_page_support_class"],
        })
        weakest_rows.append({
            **weakest,
            "recipe_global_frequency": recipe_frequency[weakest["component_recipe"]],
            "why_weakest_de": "seltenste/wenigst anderweitig paketgestützte vorhandene Verwendung; Default bleibt dennoch lesbar",
            "next_page_comparison_use": "Neue Verwendung zuerst gegen diesen Grenzfall lesen, nicht gegen den bequemsten Standardfall",
        })

    decisions = [
        {"code": "GREEN_SEMANTIC_REPLAY", "condition_de": "Bekannter Kern behält Rolle und Default; Besitzer/Hülle konkretisiert nur lokal", "action_de": "unverändert lesen und lokale Expansion notieren"},
        {"code": "AMBER_NEW_LOCAL_EXPANSION", "condition_de": "Default bleibt brauchbar, aber Besitzer oder Komplementtyp ist neu", "action_de": "breiten Kern behalten; neue lokale Expansion separat führen"},
        {"code": "AMBER_NEW_VISIBLE_COMPOSITION", "condition_de": "Bekannte Kerne bilden eine neue sichtbare Karte", "action_de": "Kernsumme lesen; keine Ganzwortbedeutung erfinden"},
        {"code": "RED_CORE_ROLE_CHANGE", "condition_de": "Lesung verlangt eine andere Strukturschublade des Kerns", "action_de": "stoppen und als echten Modellwiderspruch melden"},
        {"code": "RED_SECOND_PORTABLE_MEANING", "condition_de": "Besitzer/Hülle kann die abweichende Bedeutung nicht tragen", "action_de": "nicht lokal retten; Kernmodell neu prüfen"},
        {"code": "RED_LOCAL_LABEL_LEXICALIZED", "condition_de": "Eine Bild-/Ringkennung wird nur zur Rettung als portables Wort gelesen", "action_de": "als lokale Kopie belassen; keine Übersetzung erzwingen"},
        {"code": "RED_UNSEEN_PORTABLE_ATOM", "condition_de": "Neue Karte braucht einen unsichtbaren oder neuen Inhaltskern", "action_de": "nicht zulassen; sichtbare Zerlegung oder lokales Ganzzeichen verlangen"},
        {"code": "RED_SCOPE_REPAIR", "condition_de": "Bedeutung funktioniert nur mit Besitzerwechsel oder mehr als einer Karte Vorgriff", "action_de": "nicht semantisch reparieren; Parserbruch melden"},
    ]

    OUT.mkdir(parents=True, exist_ok=True)
    paths = {
        "deck": OUT / "gdt414_19_core_semantic_failure_deck.tsv",
        "mentions": OUT / "gdt414_8505_root_mention_pressure_ledger.tsv",
        "matrix": OUT / "gdt414_95_root_register_guardrails.tsv",
        "weakest": OUT / "gdt414_19_weakest_existing_contexts.tsv",
        "decisions": OUT / "gdt414_eight_next_page_decisions.tsv",
    }
    write_tsv(paths["deck"], deck_rows, list(deck_rows[0]))
    write_tsv(paths["mentions"], mention_rows, list(mention_rows[0]))
    write_tsv(paths["matrix"], matrix_rows, list(matrix_rows[0]))
    write_tsv(paths["weakest"], weakest_rows, list(weakest_rows[0]))
    write_tsv(paths["decisions"], decisions, list(decisions[0]))

    lines = [
        "# Semantic error deck for the next four pages",
        "",
        "Use this after visible recipe parsing and owner assignment. The goal is not to freeze exploration; it is to stop a new pictured object from silently changing a portable core.",
        "",
        "## The nineteen defaults",
        "",
        "| Core | Default | Allowed local readings | Hard warning |",
        "|---|---|---|---|",
    ]
    for row in deck_rows:
        lines.append(f"| `{row['root']}` | {row['working_value_de']} | {row['allowed_owner_local_expansions_de']} | {row['do_not_overread_de']} |")
    lines += [
        "",
        "## Fast use",
        "",
        "1. Segment the visible card with the existing component inventory.",
        "2. Read every known core with the table above before looking for a specialist gloss.",
        "3. Let the pictured owner or local hull supply the concrete noun and technique.",
        "4. Mark a novel but compatible owner expansion amber; do not change the core.",
        "5. Mark red only when the core must change role or take a second portable meaning.",
        "6. Compare a red candidate with the listed weakest existing context before revising anything.",
        "",
        "## The useful hard distinctions",
        "",
        "- `Y` is a current item, never closure by surface alone.",
        "- `AIIN/OR/AIN` are value/unit/share, not automatically measure/preparation/portion.",
        "- `AL/AR/AIR` are target/source/course, but a drawing supplies any concrete direction.",
        "- `CH/CHD` separate taking from processing; `DY` or another licensed hull supplies closure.",
        "- `K/S/T` separate giving, choosing, and setting even when a celestial table expands them as assignment, choice, and parameter setting.",
        "- Local labels stay local labels even if their surface resembles a recipe card.",
    ]
    handbook = OUT / "NEXT_FOUR_PAGE_SEMANTIC_ERROR_DECK.md"
    handbook.write_text("\n".join(lines) + "\n", encoding="utf-8")
    paths["handbook"] = handbook

    result = {
        "status": "NEXT_PAGE_SEMANTIC_FAILURE_DECK_READY",
        "root_count": len(deck_rows),
        "root_mention_count": len(mention_rows),
        "register_guardrail_count": len(matrix_rows),
        "weakest_context_count": len(weakest_rows),
        "decision_code_count": len(decisions),
        "running_event_count": len(events),
        "all_roots_all_registers": all(sum(row["mention_count"] > 0 for row in matrix_rows if row["root"] == root) == 5 for root in root_by_id),
        "source_sha256": {str(path.relative_to(ROOT)): sha256(path) for path in (EVENTS, LEAVEOUT, CORE_DICT, COMPONENT_DICT)},
        "output_sha256": {name: sha256(path) for name, path in paths.items()},
    }
    (OUT / "gdt414_result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

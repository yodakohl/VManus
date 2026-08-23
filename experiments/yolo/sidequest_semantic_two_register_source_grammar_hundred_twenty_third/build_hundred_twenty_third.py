#!/usr/bin/env python3
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R121 = ROOT / "experiments/yolo/sidequest_semantic_complete_working_edition_hundred_twenty_first"
R122 = ROOT / "experiments/yolo/sidequest_semantic_shared_deck_network_hundred_twenty_second"

ROLE = {
    "oldy": ("CLOSE", "weiterführen und schließen"),
    "choky": ("ACTION", "den Posten ansetzen"),
    "cheeky": ("ACTION", "den Posten länger wärmen"),
    "aiin": ("MEASURE", "nach Sollmaß"),
    "okal": ("ACTION", "am Ziel ansetzen"),
    "char": ("SOURCE", "aus der Quelle"),
    "chdy": ("ACTION", "den Posten umsetzen"),
    "chor": ("OBJECT", "den Ansatz"),
    "chety": ("ACTION", "einen Teil abteilen"),
    "cheey": ("STATE", "bis zum Ergebnis"),
    "okaiin": ("ACTION", "das Sollmaß einstellen"),
    "chey": ("OBJECT", "diesen Posten"),
    "cheol": ("LINK", "weiterführen"),
    "al": ("TARGET", "zum Ziel"),
    "cholor": ("ORDER", "den vorigen Ansatz weiterführen"),
    "checthy": ("STATE", "den Posten bereit halten"),
    "otchey": ("ORDER", "danach den nächsten Posten"),
}

ORDERS = {
    "HERBAL_ARTICLE": ["ACTION", "STATE", "OBJECT", "ORDER", "LINK", "SOURCE", "MEASURE", "TARGET", "CLOSE"],
    "BIOLOGICAL_CELL": ["ACTION", "SOURCE", "TARGET", "ORDER", "LINK", "STATE", "MEASURE", "OBJECT", "CLOSE"],
}

TEMPLATES = [
    ("T01", "HERBAL_ARTICLE", "SOURCE_HEADER", "[SOURCE] ACTION ACTION MEASURE", "Quelle als Rubrik vor zwei Arbeitsschritten"),
    ("T02", "HERBAL_ARTICLE", "STATE_OBJECT", "STATE OBJECT MEASURE", "Zustand oder Bereitstellung eröffnet die Materialkette"),
    ("T03", "HERBAL_ARTICLE", "OBJECT_MEASURE", "OBJECT OBJECT MEASURE", "mehrere Materialposten erhalten einen nachgestellten Wert"),
    ("T04", "HERBAL_ARTICLE", "MEASURE_HEADER", "[MEASURE] ACTION OBJECT", "vorangestelltes Sollmaß gilt für die folgende Handlung"),
    ("T05", "BIOLOGICAL_CELL", "ACTION_ROUTE", "ACTION SOURCE TARGET LINK MEASURE", "Arbeitskopf, Adresse, Lauf und Wert"),
    ("T06", "BIOLOGICAL_CELL", "TARGET_VALUE_HEADER", "[TARGET MEASURE] ACTION", "übernommene Ziel- und Werteinstellung vor dem Zellbefehl"),
    ("T07", "BOTH", "PAIRED_MEASURE_FRAME", "OBJECT MEASURE OBJECT", "zwei Posten unter demselben Sollmaß"),
    ("T08", "BOTH", "CARRY_BATCH_FRAME", "LINK ORDER LINK", "vorigen Ansatz in einer Fortsetzungsklammer tragen"),
]

EXERCISES = [
    ("X01", "HERBAL_ARTICLE", "Aus der Quelle einen Teil abteilen, den Posten ansetzen und nach Sollmaß bemessen.", "char chety choky aiin"),
    ("X02", "HERBAL_ARTICLE", "Den Ansatz bereit halten und den Posten nach Sollmaß führen.", "checthy chor chey aiin"),
    ("X03", "HERBAL_ARTICLE", "Den Ansatz und diesen Posten nach Sollmaß übernehmen.", "chor chey aiin"),
    ("X04", "HERBAL_ARTICLE", "Das Sollmaß vorgeben, am Ziel ansetzen und den Ansatz übernehmen.", "aiin okal chor chey"),
    ("X05", "HERBAL_ARTICLE", "Danach den nächsten Posten ansetzen, nach Sollmaß und zum Ziel.", "otchey choky aiin al"),
    ("X06", "BOTH", "Zwei Posten unter dasselbe Sollmaß stellen.", "chey aiin chey"),
    ("X07", "BOTH", "Den vorigen Ansatz im fortgesetzten Arbeitsgang mitführen.", "cheol cholor cheol"),
    ("X08", "BIOLOGICAL_CELL", "Sollmaß einstellen, aus der Quelle zum Ziel führen, bereit halten und schließen.", "okaiin char al checthy oldy"),
    ("X09", "BIOLOGICAL_CELL", "Umsetzen, danach den nächsten Posten ansetzen und weiterführen.", "chdy otchey choky cheol"),
    ("X10", "BIOLOGICAL_CELL", "Ziel und Sollmaß übernehmen, dann das Sollmaß einstellen.", "al aiin okaiin"),
    ("X11", "BIOLOGICAL_CELL", "Den Posten ansetzen, bis zum Ergebnis führen und schließen.", "choky cheey oldy"),
    ("X12", "BIOLOGICAL_CELL", "Sollmaß einstellen, am Ziel aus der Quelle ansetzen und nach Sollmaß weiterführen.", "okaiin okal char cheol aiin"),
]


def read_tsv(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name, rows):
    rows = list(rows)
    if not rows:
        raise ValueError(name)
    with (OUT / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def collapse_frames(cards):
    units = []
    index = 0
    while index < len(cards):
        if cards[index:index + 7] == ["checthy", "al", "chey", "aiin", "chey", "al", "checthy"]:
            units.append(("STATE_TARGET_PAIR_ENVELOPE", "OBJECT"))
            index += 7
        elif cards[index:index + 3] == ["chey", "aiin", "chey"]:
            units.append(("PAIRED_MEASURE_FRAME", "OBJECT"))
            index += 3
        elif cards[index:index + 3] == ["cheol", "cholor", "cheol"]:
            units.append(("CARRY_BATCH_FRAME", "LINK"))
            index += 3
        else:
            units.append((cards[index], ROLE[cards[index]][0]))
            index += 1
    return units


def order_audit(cards, register):
    units = collapse_frames(cards)
    roles = [role for _, role in units]
    header = []
    payload = list(roles)
    if "ACTION" in payload:
        first_action = payload.index("ACTION")
        header = payload[:first_action]
        payload = payload[first_action:]
    chunks = []
    current = []
    for role in payload:
        if role == "ACTION" and current and current[-1] != "ACTION":
            chunks.append(current)
            current = [role]
        else:
            current.append(role)
    if current:
        chunks.append(current)
    rank = {role: index for index, role in enumerate(ORDERS[register])}
    inversions = 0
    for chunk in chunks:
        inversions += sum(
            rank[chunk[left]] > rank[chunk[right]]
            for left in range(len(chunk))
            for right in range(left + 1, len(chunk))
        )
    if inversions == 0:
        fit = "DIRECT_REGISTER_TEMPLATE"
    elif inversions == 1:
        fit = "ONE_LOCAL_CARRY_OR_FRONTING"
    else:
        fit = "STACKED_CELL_REQUIRES_LOCAL_REORDERING"
    return units, header, chunks, inversions, fit


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    skeletons = read_tsv(R122 / "HUNDRED_TWENTY_SECOND_116_SHARED_CARD_SKELETONS.tsv")
    deck = read_tsv(R121 / "HUNDRED_TWENTY_FIRST_17_SHARED_CARDS.tsv")
    card_by_form = {row["master_form"]: row for row in deck}
    observed_sequences = {row["shared_surface_skeleton"] for row in skeletons if row["shared_surface_skeleton"] != "NONE"}
    observed_spans = set()
    for sequence in observed_sequences:
        cards = sequence.split()
        for left in range(len(cards)):
            for right in range(left + 1, len(cards) + 1):
                observed_spans.add(" ".join(cards[left:right]))

    audit_rows = []
    for row in skeletons:
        if row["shared_surface_skeleton"] == "NONE":
            continue
        register = "HERBAL_ARTICLE" if row["record_unit_id"].startswith("H") else "BIOLOGICAL_CELL"
        cards = row["shared_surface_skeleton"].split()
        units, header, chunks, inversions, fit = order_audit(cards, register)
        audit_rows.append({
            "statement_id": row["statement_id"],
            "record_unit_id": row["record_unit_id"],
            "page": row["page"],
            "register_grammar": register,
            "shared_surface_skeleton": row["shared_surface_skeleton"],
            "collapsed_units": " | ".join(unit for unit, _ in units),
            "carried_header_roles": "|".join(header) or "NONE",
            "ordered_payload_chunks": " || ".join(">".join(chunk) for chunk in chunks) or "NONE",
            "local_order_inversions": str(inversions),
            "fit_class": fit,
            "spoken_source_reading_de": row["source_phrase_expansion_de"],
        })
    write_tsv("HUNDRED_TWENTY_THIRD_57_OBSERVED_REGISTER_PARSES.tsv", audit_rows)

    template_rows = [
        {"template_id": tid, "register": register, "template_name": name, "card_role_order": order, "workshop_use": use}
        for tid, register, name, order, use in TEMPLATES
    ]
    write_tsv("HUNDRED_TWENTY_THIRD_EIGHT_SOURCE_TEMPLATES.tsv", template_rows)

    exercise_rows = []
    for exercise_id, register, source, sequence in EXERCISES:
        cards = sequence.split()
        ids = [card_by_form[card]["master_card_id"] for card in cards]
        if sequence in observed_sequences:
            status = "EXACT_OBSERVED_SKELETON"
        elif sequence in observed_spans:
            status = "OBSERVED_CONTIGUOUS_FORMULA"
        else:
            status = "NEW_WORKSHOP_COMBINATION"
        exercise_rows.append({
            "exercise_id": exercise_id,
            "register": register,
            "ordinary_source_command_de": source,
            "compiled_master_cards": sequence,
            "compiled_master_card_ids": " ".join(ids),
            "literal_card_backreading_de": " ".join(ROLE[card][1] for card in cards),
            "manuscript_status": status,
        })
    write_tsv("HUNDRED_TWENTY_THIRD_TWELVE_SOURCE_TO_CARD_EXERCISES.tsv", exercise_rows)

    direct = sum(row["fit_class"] == "DIRECT_REGISTER_TEMPLATE" for row in audit_rows)
    one = sum(row["fit_class"] == "ONE_LOCAL_CARRY_OR_FRONTING" for row in audit_rows)
    stacked = len(audit_rows) - direct - one
    exact = sum(row["manuscript_status"] == "EXACT_OBSERVED_SKELETON" for row in exercise_rows)
    span = sum(row["manuscript_status"] == "OBSERVED_CONTIGUOUS_FORMULA" for row in exercise_rows)
    novel = len(exercise_rows) - exact - span
    summary = {
        "status": "COMPLETE",
        "observed_shared_skeletons": len(audit_rows),
        "direct_register_template": direct,
        "one_local_carry_or_fronting": one,
        "stacked_local_reordering": stacked,
        "source_templates": len(template_rows),
        "source_to_card_exercises": len(exercise_rows),
        "exact_observed_exercises": exact,
        "observed_formula_span_exercises": span,
        "new_workshop_combinations": novel,
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    report = [
        "# Hundertdreiundzwanzigste Runde: zwei Register statt einer starren Wortfolge", "",
        "Der Acht-Platz-Stack aus R122 war als erste Skizze nützlich, aber zu glatt. Die Karten zeigen",
        "zwei lernbare Schreibweisen. Herbal-Artikel bevorzugen Handlung/Zustand, Materialkette,",
        "Fortsetzung/Quelle, nachgestelltes Maß und Ziel. Biological-Zellen bevorzugen Arbeitskopf,",
        "Quelle/Ziel, Lauf, Zustand, Maß und erst dann den betroffenen Posten. Ein bereits aktives Maß,",
        "Ziel oder eine Quelle darf als kurze Feldrubrik vorangestellt werden.", "",
        "Nach Zusammenziehen der beiden echten Klammerformeln und der übernommenen Feldrubriken passen",
        f"{direct} der 57 Gerüste direkt, {one} mit genau einer lokalen Fortführung und {stacked} als",
        "sichtbar gestapelte Zellen. Das spricht nicht für zwei Sprachen, sondern für Artikelprosa gegen",
        "Formularzellen innerhalb derselben Werkstatt.", "",
        "Die zwölf Gegenläufe zeigen, dass man aus gewöhnlichen kurzen Befehlen wieder Kartenfolgen bauen",
        "kann. Einige sind exakt beobachtet, andere beobachtete Teilformeln, und die übrigen sind neue",
        "Lehrlingskombinationen. Damit ist die Grammatik erstmals vorwärts benutzbar, ohne jede Karte zu",
        "einem ganzen deutschen Satz aufzublasen.", "",
        "Nächster Schritt: dieselben zwölf Befehle durch die vier Schreiberprofile rendern und zurücklesen.",
        "Danach werden die fünf lokalen Abweichungen einzeln als echte Fortführung, Rubrik oder falsche",
        "Bedeutungszuordnung entschieden.",
    ]
    (OUT / "HUNDRED_TWENTY_THIRD_TWO_REGISTER_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Build the V72 R2 historical, image-owner-constrained 116-statement edition.

This script deliberately consumes only the frozen V69 formal prose tables and
the centrally selected V71 owner ledger.  It never reads a manuscript image,
surface spelling, joint-tuple coordinates, or any active V72 sibling output.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
V69 = ROOT / "experiments/yolo/sidequest_theory_candidates_v69"
V71 = ROOT / "experiments/yolo/sidequest_theory_candidates_v71"
OUT = ROOT / "experiments/yolo/sidequest_theory_candidates_v72"

STATEMENTS = V69 / "V69_R4_FINAL_116_STATEMENT_EDITION.tsv"
FIELDS = V69 / "V69_R4_FINAL_135_FIELD_EDITION.tsv"
EVENTS = V69 / "V69_R4_FINAL_381_PROSE_EVENT_INTERLINEAR.tsv"
OWNERS = V71 / "V71_SELECTED_OWNER_LEDGER.tsv"

LEDGER_OUT = OUT / "V72_R2_116_STATEMENTS.tsv"
REVISIONS_OUT = OUT / "V72_R2_REVISIONS.tsv"
REPORT_OUT = OUT / "V72_R2_HISTORICAL_STATEMENT_REPORT.md"


R2_BACKGROUND = [
    "Du kennst zeitgenössische Herbarien, Materia medica, Rezeptbücher, Abkürzungen und kompilierte Sammelhandschriften.",
    "Du vergleichst Namen, Beschreibungen, Qualitäten, Habitate, Zubereitungen, Anwendungen und Rezeptfortsetzungen.",
    "Du unterscheidest überlieferte Textpraxis von modernen Tabellen-, Datenbank- oder Übersetzungsannahmen.",
    "Du darfst historische Quellen recherchieren, aber niemals Voynich-Formen über Klang oder Buchstabenähnlichkeit zuordnen.",
    "Du lieferst die historisch plausibelste Quelltextstruktur samt Gegenbelegen und eng begrenzter Pseudoübersetzung.",
]


HERBAL_PARAPHRASES = {
    "H1-S001": "Von der ganzen abgebildeten Pflanze: nimm einen Teil der Wurzel, säubere und zerkleinere ihn, bereite daraus mit einem nicht abgebildeten Medium einen Auszug, gebrauche den vorgeschriebenen Anteil und verwahre den Rest trocken.",
    "H1-S002": "Vom selben Pflanzenartikel: erwärme einen frischen Auszug, führe ihn als Fortsetzung der vorherigen Bereitung und gebrauche ihn, sobald der örtliche Bereitschaftszustand erreicht ist.",
    "H2-S001": "Von der ganzen abgebildeten Pflanze: sammle einen oberirdischen Teil zur passenden Reife, zerstoße und presse ihn, führe die Flüssigkeit als neuen Ansatz und bemesse den zuzubereitenden Anteil.",
    "H2-S002": "Vom selben Artikel: nimm vor voller Blüte eine Handvoll Pflanzenstoff, entnimm daraus einen Anteil, verknüpfe ihn mit der vorherigen Bereitung und halte das vorgeschriebene Maß ein.",
    "H2-S003": "Vom selben Artikel: verarbeite einen bei geöffneter Blüte genommenen Teil, prüfe den Auszug am örtlichen Endzustand und bewahre den abgeteilten Rest in einem nicht abgebildeten Medium auf.",
    "H3-S001": "Von der ganzen abgebildeten Pflanze: nimm im Frühjahr einen unterirdischen Teil, presse den zerkleinerten Stoff durch ein Tuch, kläre den Auszug durch erneutes Seihen und lasse ihn anschließend abkühlen.",
    "H3-S002": "Vom selben Pflanzenartikel: behalte den blühenden oder kopfförmigen Teil als getrennten Vorrat zurück.",
    "H3-S003": "Vom selben Pflanzenartikel: nimm einen aktiven Anteil, lege ihn als Auflage an die im Rezept vorausgesetzte Stelle und bemesse ihn nach örtlicher Vorschrift.",
    "H3-S004": "Vom selben Pflanzenartikel: bereite aus einem Blattteil eine warme Auflage, lege sie im gebrauchsfertigen Zustand auf und führe den verwendeten Anteil als laufende Bereitung.",
    "H4-S001": "Von der ganzen abgebildeten Pflanze: setze einen neuen abgemessenen Posten an, erhitze einen Blattteil sanft in einem nicht abgebildeten Medium und lasse ihn bis zum örtlichen Prüfzustand ziehen.",
    "H4-S002": "Vom selben Pflanzenartikel: bemesse einen Anteil, vermenge ihn gleichmäßig und gebrauche ihn einmal als Waschung an der im Rezept vorausgesetzten Stelle.",
    "H4-S003": "Vom selben Pflanzenartikel: bereite einen zweiten Gebrauchsposten mit einem nicht abgebildeten Medium und verarbeite ihn bei mäßiger Wärme bis zum Abschluss des Arbeitsschritts.",
    "H4-S004": "Vom selben Pflanzenartikel: bemesse und vereinige zwei Anteile, verwahre die Bereitung bedeckt und gebrauche die fertige Flüssigkeit frisch.",
    "H5-S001": "Von der ganzen abgebildeten Pflanze: sammle sie zur passenden Jahreszeit, nimm einen unterirdischen oder sonst örtlich bestimmten Teil, bemesse ihn, lasse ihn in einem nicht abgebildeten Medium ziehen und führe den gebrauchsfertigen Anteil an die im Rezept vorausgesetzte Zielstelle.",
    "H5-S002": "Vom selben Pflanzenartikel: nimm Material von einem feuchten oder schattigen Standort, bereite daraus einen anwendbaren Anteil und lasse eine daraus gefertigte Auflage unbedeckt trocknen.",
    "H5-S003": "Vom selben Pflanzenartikel: trenne einen kleinen Kopf- oder Samenstand und einen schmalen Blattteil und trockne den Vorrat im Schatten.",
    "H5-S004": "Vom selben Pflanzenartikel: gebrauche die frisch bereitete Zubereitung nach der im Receptarium vorausgesetzten Indikation und bewahre den Rest trocken im Schatten.",
    "H5-S005": "Vom selben Pflanzenartikel: nimm den folgenden Teil oder Zusatz, vereinige die frische Bereitung mit einem nicht abgebildeten Bindemittel und gebrauche sie frisch vermischt.",
    "H5-S006": "Vom selben Pflanzenartikel: nimm den bezeichneten Anteil des hellen geöffneten Blütenteils und bemesse ihn nach örtlicher Vorschrift.",
}


OWNER_LABELS = {
    "WHOLE_BROAD_TOOTHED_RADIAL_FLOWERED_HERB": "der ganzen abgebildeten breitblättrigen Pflanze",
    "WHOLE_LARGE_ROSETTE_LEAF_RED_CLUSTERED_FLOWER_HERB": "der ganzen abgebildeten Rosettenpflanze mit rotem Blütenstand",
    "WHOLE_NARROW_LEAF_WHITE_FLOWER_HERB": "der ganzen abgebildeten schmalblättrigen Pflanze mit heller Blüte",
    "WHOLE_ROUND_LEAF_MULTI_RED_FLOWER_HERB": "der ganzen abgebildeten rundblättrigen Pflanze mit mehreren roten Blüten",
    "B1_SHARED_TWO_ROW_POOL": "dem gemeinsamen zweireihigen Beckenfeld",
    "B2_UPPER_PAIRED_BASINS_AND_CYLINDER": "dem oberen Paarbecken mit Zylinder",
    "B2_MIDDLE_LEFT_DEVICE_AND_INLINE_NODE": "der mittleren linken Geräte- und Knotenstation",
    "B2_MIDDLE_RIGHT_AMBIGUOUS_STATION": "der noch nicht sicher zugewiesenen mittleren rechten Station",
    "B2_LOWER_GREEN_MULTI_FIGURE_POOL": "dem unteren grünen Mehrfigurenbecken",
    "B2_LOWER_POOL_EDGE_STATIONS": "den lokalen Randstationen des unteren Beckens",
    "B3_UPPER_MARGIN_OPEN_FAN_STATION": "der oberen offenen Fächerstation am Rand",
    "B3_MIDDLE_MARGIN_ROUND_VESSEL_STATION": "der mittleren runden Gefäßstation am Rand",
    "B3_LOWER_MARGIN_BASKET_VESSEL_STATION": "der unteren korb- oder gefäßartigen Randstation",
    "B3_MARGIN_TO_MAIN_GAP_UNRESOLVED": "dem nicht auflösbaren Zwischenraum zwischen Rand und Hauptbild",
    "B3_MAIN_ARCH_LINKED_PAIR": "dem durch den Hauptbogen verbundenen Figurenpaar",
    "B4_MAIN_ARCH_LINKED_PAIR": "dem durch den Hauptbogen verbundenen Figurenpaar",
    "B4_MAIN_LEFT_OPEN_FRINGE_STATION": "der linken offenen Fransenstation des Hauptbildes",
    "B4_MAIN_RIGHT_S_RUN_MULTIPORT_STATION": "der rechten S-förmigen Mehrfachanschluss-Station",
    "B5_LEFT_OPEN_FRINGE_STATION": "der linken offenen Fransenstation",
    "B6_RIGHT_S_RUN_MULTIPORT_STATION": "der rechten S-förmigen Mehrfachanschluss-Station",
}


CROSS_OWNER_PARAPHRASES = {
    "B2-S012": "An der nicht sicher zugewiesenen mittleren rechten Station endet ein lokaler Satz mit dem Abziehen einer klaren Flüssigkeit; am unteren grünen Mehrfigurenbecken beginnt getrennt davon ein Satz über Prüfen, Temperieren, Bemessen und vollständiges Benetzen. Dies sind zwei benachbarte Stationsartikel, nicht ein behaupteter durchgehender Lauf.",
    "B3-S016": "An der unteren korb- oder gefäßartigen Randstation steht als lokaler Exemplarabschluss das Schließen eines Ablaufs; im anschließenden unaufgelösten Zwischenraum kann ein neuer Satz über Abkühlen enden. Eine gemeinsame Vorrichtung wird nicht vorausgesetzt.",
    "B3-S026": "Im unaufgelösten Zwischenraum kann ein Stationsartikel über Einrichten, Absetzen, Mischen, Bemessen und Erreichen eines Prüfzustands stehen; am Hauptbogenpaar folgt getrennt ein kurzer Satz über das Absetzen einer Flüssigkeit. Die Textfolge behauptet keine sichtbare Verbindung beider Besitzer.",
    "B4-S015": "An der linken offenen Fransenstation kann ein lokaler Artikel Bemessen, Prüfen und Warten beschreiben; an der rechten S-förmigen Mehrfachanschluss-Station folgt getrennt ein Satz über Öffnen und Ablassen. Der Übergang ist eine Artikelgrenze, kein globaler Rohrlauf.",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def ordered_unique(items: list[str]) -> list[str]:
    return list(dict.fromkeys(items))


def strip_v69_exemplar(text: str) -> str:
    """Remove the V69 A-code wrapper while retaining its explicit source exemplar."""
    if text.startswith("[EXEMPLAR:") and text.endswith("]"):
        parts = text[:-1].split(":", 2)
        if len(parts) == 3:
            return parts[2].strip()
    return text.strip()


def placeholder_type(source: str) -> str:
    s = source.casefold()
    if any(k in s for k in ("wenn ", "bevor ", "bis ", "solange", "dauer", "warm", "kühl", "klar", "abkühl", "ohne kochen", "frühjahr")):
        return "CONDITION"
    if any(k in s for k in ("stelle", "bereich", "becken", "öffnung", "ablauf", "lauf", "ziel", "haut", "wund", "körper")):
        return "TARGET_OR_STATION"
    if any(k in s for k in ("wasser", "flüssigkeit", "wurzel", "blatt", "blüte", "kraut", "portion", "anteil", "zusatz", "tuch", "wein", "honig", "gefäß", "mischung")):
        return "SUBSTANCE_OR_OBJECT"
    if any(k in s for k in ("vorigen", "daraus", "derselben", "diese aktive", "fortführen")):
        return "LOCAL_LINK"
    if any(k in s for k in ("nimm", "gib", "misch", "rühr", "spül", "wasch", "halte", "lasse", "zieh", "seih", "erwärm", "temper", "gebrauch", "samm", "trock", "öffne", "schließe", "richte", "fülle", "lege", "tauche", "benetze", "koche", "presse", "zerstoß")):
        return "ACTION"
    return "SOURCE_ARGUMENT"


def literal_piece(event: dict[str, str]) -> str:
    pieces: list[str] = []
    if event["selected_exact_mnemonic"] != "UNKNOWN":
        pieces.append(f"[CARD:{event['selected_exact_mnemonic']}]")
    if event["strict_formal_prompt"] != "NONE":
        pieces.append(f"[FORMAL:{event['strict_formal_prompt']}]")
    if not pieces:
        pieces.append(f"[EXEMPLAR {placeholder_type(event['iatromedical_source_segment'])}]")
    if event["terminal_status"] == "TERMINAL":
        pieces.append("[CLOSE]")
    return " ".join(pieces)


def source_class(record: str) -> str:
    if record.startswith("H"):
        return "HERBAL_ARTICLE_OR_RECEPTARIUM_ENTRY"
    if record in {"B1", "B2"}:
        return "LOCAL_BALNEOLOGICAL_STATION_ARTICLE"
    return "LOCAL_BALNEOLOGICAL_OR_THERAPEUTIC_STATION_ARTICLE"


def bio_paraphrase(statement: dict[str, str], owners: list[str]) -> str:
    sid = statement["statement_id"]
    if sid in CROSS_OWNER_PARAPHRASES:
        return CROSS_OWNER_PARAPHRASES[sid]
    base = strip_v69_exemplar(statement["iatromedical_statement_text"])
    local = " und ".join(OWNER_LABELS.get(owner, owner) for owner in owners)
    if any("UNRESOLVED" in owner or "AMBIGUOUS" in owner for owner in owners):
        return f"Als ein konkreter, aber eigentümerseitig ungesicherter Stationsartikel bei {local}: {base}. Die Handlungen sind Exemplarfüllungen; nur ihre Reihenfolge ist formal erhalten."
    return f"Als konkreter lokaler Bade- oder Stationsartikel bei {local}: {base}."


def score_repair(
    record: str,
    statuses: list[str],
    owners: list[str],
    statement_events: list[dict[str, str]],
) -> tuple[int, str]:
    all_formal = all(
        e["selected_exact_mnemonic"] != "UNKNOWN" or e["strict_formal_prompt"] != "NONE"
        for e in statement_events
    )
    any_formal = any(
        e["selected_exact_mnemonic"] != "UNKNOWN" or e["strict_formal_prompt"] != "NONE"
        for e in statement_events
    )
    if len(owners) > 1:
        return 4, "Die V69-Aussage überquert verschiedene V71-Bildbesitzer und muss in lokale Artikelteile getrennt werden."
    if "UNRESOLVED" in statuses:
        return 3, "V71 kann dem Feld keinen sichtbaren Besitzer zuweisen; die konkrete Füllung bleibt daher ein typisiertes Quellenexemplar."
    if record.startswith("H"):
        return 3, "Die frühere taxonomisch und stofflich enge Lesung wird auf den ganzen Bildpflanzenartikel plus unbebilderte Receptarium-Argumente zurückgebaut."
    if all_formal:
        return 0, "Sichtbarer lokaler Besitzer und vollständig bekannte Karten-/Formalfolge erlauben die Quellenklasse ohne strukturelle Reparatur."
    if any_formal:
        return 1, "Der lokale Besitzer und mindestens ein formaler Anker bleiben; übrige Rollen werden nur als Exemplarargumente ergänzt."
    return 2, "Der lokale Besitzer ist sichtbar, doch die gesamte Handlungskette bleibt eine konkrete historische Exemplarfüllung."


def build() -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    statements = read_tsv(STATEMENTS)
    fields = {row["field_id"]: row for row in read_tsv(FIELDS)}
    events = read_tsv(EVENTS)
    events_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        events_by_statement[event["statement_id"]].append(event)

    owner_rows = {
        row["unit_id"]: row
        for row in read_tsv(OWNERS)
        if row["unit_kind"] == "PROSE_FIELD"
    }

    output: list[dict[str, str]] = []
    revisions: list[dict[str, str]] = []
    for statement in statements:
        sid = statement["statement_id"]
        record = statement["record_unit_id"]
        field_ids = statement["constituent_fields"].split("|")
        selected = [owner_rows[fid] for fid in field_ids]
        owners = ordered_unique([row["selected_visible_owner"] for row in selected])
        statuses = ordered_unique([row["owner_status"] for row in selected])
        defaults = ordered_unique([row["silent_argument_default"] for row in selected])
        rivals = ordered_unique([row["strongest_rival"] for row in selected])
        loci = ordered_unique([fields[fid]["locus"] for fid in field_ids])
        statement_events = events_by_statement[sid]

        if len(field_ids) == 1:
            line_crossing = "NO__SINGLE_FIELD"
        elif len(loci) == 1:
            line_crossing = "NO_PHYSICAL_LOCUS_CHANGE__MULTI_FIELD"
        else:
            line_crossing = "YES__CROSS_FORMAL_LOCUS"
        if len(owners) > 1:
            owner_crossing = "CROSS_FIELD_OWNER_CHANGE"
        elif len(field_ids) > 1:
            owner_crossing = "CROSS_FIELD_SAME_OWNER_CONTINUATION"
        else:
            owner_crossing = "SINGLE_FIELD_OWNER"

        event_layers: list[str] = []
        current_owner = None
        for event in statement_events:
            field_owner = owner_rows[event["field_id"]]["selected_visible_owner"]
            if field_owner != current_owner:
                status = owner_rows[event["field_id"]]["owner_status"]
                event_layers.append(f"[OWNER:{field_owner};STATUS:{status}]")
                current_owner = field_owner
            event_layers.append(f"E{event['event_serial']}:{literal_piece(event)}")
        literal = " > ".join(event_layers)

        if record.startswith("H"):
            paraphrase = HERBAL_PARAPHRASES[sid]
        else:
            paraphrase = bio_paraphrase(statement, owners)

        repair_cost, repair_reason = score_repair(record, statuses, owners, statement_events)
        if len(owners) > 1:
            contradiction = "Die alte Einzelaussage verbindet voneinander verschiedene V71-Bildbesitzer; sichtbar ist nur die lokale Nachbarschaft, nicht ein gemeinsamer Apparat oder Stoffstrom."
            revision_action = "SPLIT_AT_V71_OWNER_BOUNDARY; RETAIN_EVENT_ORDER"
        elif "UNRESOLVED" in statuses:
            contradiction = "Für mindestens ein Feld existiert kein ausgewählter sichtbarer Besitzer; konkrete Stoffe, Richtung und Handlung sind daher nicht bildbestätigt."
            revision_action = "REPLACE_ASSERTED_OWNER_WITH_TYPED_UNRESOLVED_STATION"
        elif record.startswith("H"):
            contradiction = "Das Bild bestätigt nur die ganze Pflanze; exakte Art, Teilwahl, Wasser, Wein, Gerät, Indikation und Dosis sind unbebilderte Quellenargumente."
            revision_action = "REMOVE_TAXONOMIC_IDENTITY; REANCHOR_TO_WHOLE_PLANT_ARTICLE"
        else:
            contradiction = "Der sichtbare Besitzer lizenziert nur einen lokalen Stationsartikel; Stoff, Bewegungsrichtung, Dauer und therapeutischer Zweck bleiben Quellenexemplar, nicht Bildbefund."
            revision_action = "LOCALIZE_TO_V71_OWNER; RETAIN_FORMAL_SEQUENCE_ONLY"

        row = {
            "statement_id": sid,
            "record_unit_id": record,
            "page": statement["page"],
            "statement_ordinal_in_record": statement["statement_ordinal_in_record"],
            "constituent_fields": statement["constituent_fields"],
            "constituent_loci": "|".join(loci),
            "event_serials": statement["event_serials"],
            "v71_owner_statuses": "|".join(statuses),
            "v71_visible_owners": "|".join(owners),
            "v71_silent_argument_defaults": " || ".join(defaults),
            "literal_owner_card_exemplar_layer": literal,
            "historical_source_class": source_class(record),
            "concrete_source_class_paraphrase": paraphrase,
            "strongest_rival": " || ".join(rivals),
            "repair_cost_0_4": str(repair_cost),
            "repair_reason": repair_reason,
            "line_crossing": line_crossing,
            "owner_crossing": owner_crossing,
            "strongest_contradiction": contradiction,
            "v69_revision_action": revision_action,
            "semantic_ceiling": "HISTORICAL_SOURCE_EXEMPLAR_NOT_TRANSLATION_OR_CARD_VALUE",
        }
        output.append(row)
        revisions.append(
            {
                "statement_id": sid,
                "record_unit_id": record,
                "constituent_fields": statement["constituent_fields"],
                "v71_revision_action": revision_action,
                "repair_cost_0_4": str(repair_cost),
                "reason": repair_reason,
                "retained_from_v69": "event order; exact mnemonic cards; strict formal prompts; terminal placement",
                "rejected_from_v69": (
                    "single global process across owner boundary"
                    if len(owners) > 1
                    else "asserted visible owner" if "UNRESOLVED" in statuses
                    else "taxonomic identity and pictured recipe apparatus" if record.startswith("H")
                    else "unlicensed global apparatus, direction, substance, or indication"
                ),
            }
        )
    return output, revisions


def write_tsv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def md_escape(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


def build_report(rows: list[dict[str, str]]) -> str:
    by_record: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_record[row["record_unit_id"]].append(row)
    cost_counts = Counter(row["repair_cost_0_4"] for row in rows)
    owner_change = sum(row["owner_crossing"] == "CROSS_FIELD_OWNER_CHANGE" for row in rows)
    unresolved = sum("UNRESOLVED" in row["v71_owner_statuses"] for row in rows)
    line_cross = sum(row["line_crossing"].startswith("YES") for row in rows)

    out: list[str] = []
    out += [
        "# V72 R2 — historisch lokalisierte Rekonstruktion aller 116 Prosaaussagen",
        "",
        "## Unveränderter R2-Hintergrund",
        "",
    ]
    out += [f"{i}. {line}" for i, line in enumerate(R2_BACKGROUND, 1)]
    out += [
        "",
        "## Ergebnis zuerst",
        "",
        "Alle 116 V69-Aussagen sind auf die zentral ausgewählten V71-Bildbesitzer zurückgeführt. Die Ausgabe ist keine Übersetzung: Sie hält Eigentümer, Ereignisreihenfolge, bekannte Karten/Formalprompts und Schlusspunkte wörtlich auseinander und füllt den übrigen Inhalt nur mit genau einem konkret benannten historischen Quellenexemplar. Kein Karten-, Stamm- oder Lautwert wird vergeben.",
        "",
        f"Die Revision findet {owner_change} Aussagen mit echtem Eigentümerwechsel, {unresolved} Aussagen mit mindestens einem unaufgelösten Besitzer und {line_cross} Aussagen über mehr als einen formalen Locus. Reparaturkosten: " + ", ".join(f"{k}→{cost_counts[k]}" for k in sorted(cost_counts, key=int)) + ".",
        "",
        "Die entscheidende Korrektur ist lokal: Ein benachbarter Textabschnitt darf zwei Bildstationen nacheinander besitzen, ohne dass daraus ein einziger hydraulischer Kreislauf, ein globales Bad oder eine gemeinsame Substanz folgt. Herbal-Seiten dürfen dagegen nach gewöhnlicher Artikel-/Receptarium-Ordnung unbebilderte Zutaten, Medien oder Anwendungen ergänzen, solange diese ausdrücklich Exemplarargumente bleiben.",
        "",
        "## Eingefrorene Rekonstruktionsregel",
        "",
        "1. V71 bestimmt den sichtbaren Besitzer; bei `UNRESOLVED` wird kein Ersatzbesitzer erfunden.",
        "2. Die Literalzeile enthält nur `[OWNER]`, bekannte `[CARD]`, bekannte `[FORMAL]`, typisierte `[EXEMPLAR …]` und `[CLOSE]` in der Reihenfolge der 381 V69-Ereignisse.",
        "3. Die konkrete Paraphrase ist genau ein historisch plausibles Quellenklassenexemplar. Sie ist weder Lesung der Glyphen noch Kartenbedeutung.",
        "4. Ein V71-Eigentümerwechsel trennt lokale Artikelteile. Sichtnähe allein erzeugt weder Rohrverbindung noch Stoffkontinuität.",
        "5. Reparaturkosten: 0 = lokaler Besitzer plus vollständig bekannte Formalfolge; 1 = formaler Anker plus Exemplarergänzung; 2 = sichtbarer Besitzer, aber reine Exemplarhandlung; 3 = Pflanzenreduktion oder unaufgelöster Besitzer; 4 = alte Aussage überquert verschiedene Besitzer.",
        "",
        "## Vollständiger Durchgang durch alle elf Prosarecords",
        "",
    ]
    record_notes = {
        "H1": "Ein Pflanzenartikel; weder Artname noch Wasser/Wein sind bildlich bestätigt.",
        "H2": "Fortsetzung desselben Seitenartikels; Ernte-, Press- und Dosisdetails bleiben Receptarium-Exemplar.",
        "H3": "Neuer Pflanzenartikel; Teil- und Anwendungsfolge wird nicht aus der Zeichnung abgelesen.",
        "H4": "Neuer Pflanzenartikel; Zubereitungsmedien und Indikation bleiben stumm vorausgesetzt.",
        "H5": "Neuer Pflanzenartikel; F014→F015 darf als normaler Artikelübergang über loci fortlaufen.",
        "B1": "Alle Aussagen gehören dem gemeinsamen zweireihigen Beckenfeld; keine Kleinstfigur wird künstlich zum Satzbesitzer.",
        "B2": "Mehrere lokale Stationen; insbesondere B2-S012 wird am Eigentümerwechsel geteilt.",
        "B3": "Randstationen, unaufgelöster Zwischenraum und Hauptbogenpaar bleiben getrennte Besitzer.",
        "B4": "Hauptbogenpaar und beide Endstationen bleiben lokal; B4-S015 ist kein durchgehender Apparat.",
        "B5": "Nur die linke offene Fransenstation besitzt diesen Record.",
        "B6": "Nur die rechte S-förmige Mehrfachanschluss-Station besitzt diesen Record.",
    }
    for record in ("H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"):
        out += [f"### {record}", "", record_notes[record], "", "| Aussage | V71-Besitzer | Kosten | Konkretes Quellenexemplar | Widerspruch |", "|---|---|---:|---|---|"]
        for row in by_record[record]:
            out.append(
                "| " + " | ".join(
                    [
                        row["statement_id"],
                        md_escape(row["v71_visible_owners"]),
                        row["repair_cost_0_4"],
                        md_escape(row["concrete_source_class_paraphrase"]),
                        md_escape(row["strongest_contradiction"]),
                    ]
                ) + " |"
            )
        out.append("")

    out += [
        "## Vier harte Revisionen",
        "",
        "- `B2-S012`: F058 bleibt unaufgelöst; F059 gehört bereits dem unteren grünen Pool. Die alte Einzelaussage wird geteilt.",
        "- `B3-S016`: F086 gehört der unteren Randstation, F087 dem unaufgelösten Zwischenraum. Abfluss und Abkühlen dürfen zwei Artikelabschlüsse sein.",
        "- `B3-S026`: F098 ist unaufgelöst, F099 gehört dem Hauptbogenpaar. Das Absetzen am Paar ist keine sichtbare Fortsetzung der vorausgehenden Einrichtung.",
        "- `B4-S015`: F125 gehört der linken Fransenstation, F126 der rechten S-Station. Prüfen/Warten und Öffnen/Ablassen werden nicht zu einem Apparat globalisiert.",
        "",
        "## Historische Gattungskalibrierung",
        "",
        "Diese Quellen belegen nur zeitnahe Darstellungs- und Textgattungen, nicht die Identität eines Voynich-Motivs:",
        "",
        "1. British Library, [Egerton MS 747](https://searcharchives.bl.uk/catalog/032-001983805), *Tractatus de herbis*, ca. 1280–1350 — Pflanzenartikel mit Bild und unbebilderter Textinformation.",
        "2. British Library, [Egerton MS 2020](https://searcharchives.bl.uk/catalog/032-001982947), Carrara-Herbal, ca. 1390–1404 — spätmittelalterliche Bildherbal-Praxis.",
        "3. Morgan Library, [MS G.74, f.23r](https://ica.themorgan.org/manuscript/page/22/77063), *De balneis Puteolanis*, ca. 1400 — lokale Badevignette als Gattungsvergleich.",
        "4. Biblissima/BnF, [Latin 8161, f.23](https://portail.biblissima.fr/en/ark:/43093/ifdata38fe2523aff0ab85012f88057adb9c6897a121d1), Bade-/Beckenszene — Vergleich für lokale Stationseigentümer.",
        "5. Biblioteca Angelica, [MS 1474](https://bibliotecaangelica.cultura.gov.it/de-balneis-puteolanis/), *De balneis Puteolanis* — balneologische Bild-/Textgattung.",
        "",
        "## Grenze",
        "",
        "Die Rekonstruktion liefert eine historisch verständliche Quelltextform, keine Entzifferung. Ein sichtbarer Pflanzen- oder Stationsbesitzer kann einen Artikel rahmen; er beweist weder das unbebilderte Rezeptargument noch die Bedeutung eines Voynich-Zeichens. `f84` und `f84r` blieben vollständig versiegelt.",
        "",
        "## Reproduzierbarkeit",
        "",
        "Aus dem Repository-Stamm ausführen:",
        "",
        "```bash",
        "python experiments/yolo/sidequest_theory_candidates_v72/build_v72_r2_statement_reconstruction.py",
        "python experiments/yolo/sidequest_theory_candidates_v72/validate_v72_r2_statement_reconstruction.py",
        "```",
        "",
    ]
    return "\n".join(out)


def main() -> None:
    rows, revisions = build()
    write_tsv(LEDGER_OUT, rows)
    write_tsv(REVISIONS_OUT, revisions)
    REPORT_OUT.write_text(build_report(rows), encoding="utf-8")
    digest = hashlib.sha256(LEDGER_OUT.read_bytes()).hexdigest()
    print(json.dumps({"rows": len(rows), "sha256": digest, "report": REPORT_OUT.name}, ensure_ascii=False))


if __name__ == "__main__":
    main()

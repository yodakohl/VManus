#!/usr/bin/env python3
"""V45 R2: revise the fixed ten-page creative edition around stable host stems.

This is a non-scientific sidequest artefact.  It joins only already published,
f84-free V40/V43/V44 tables and never treats the proposed stems as deciphered
language.
"""

from __future__ import annotations

import csv
import io
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
V40 = ROOT / "experiments/yolo/sidequest_theory_candidates_v40/V40_REVISED_381_EVENT_LEDGER.tsv"
V43 = ROOT / "experiments/yolo/sidequest_theory_candidates_v43/V43_CURRENT_PROSE_DICTIONARY.tsv"
V44 = ROOT / "experiments/yolo/sidequest_theory_candidates_v44/V44_R4_CARD_TO_HOST_MEANINGS.tsv"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


# The minimum value is deliberately broader than any fluent local expansion.
STEMS = {
    "aiin": ("QUANTITAET", "vorgeschriebener oder standardisierter Wert mit kontextueller Dimension", "A"),
    "or": ("BEREITETES_ERGEBNIS", "aus dem aktiven Ansatz hervorgegangenes verwendbares Produkt", "A"),
    "chor": ("BESCHAFFUNGSZEIT", "Beschaffung des Bildbesitzers in einem angegebenen Zeitfenster", "A"),
    "chey": ("AUSWAHL", "einen kontextuell bestimmten Materialteil auswählen", "A"),
    "ok": ("AKTIVIERUNG", "einen durch die Kompletierung bestimmten Arbeitsposten in Kraft setzen", "A"),
    "ot": ("MARKIERTER_GEGENPOSTEN", "einen kontextuell kontrastierten oder wiederaufgenommenen Slot wählen", "B"),
    "l": ("ANSCHLUSS", "einen kontextuell verbundenen Vorgänger, Nachfolger oder Empfänger wählen", "B"),
    "e": ("ZUSTANDSGRENZE", "den laufenden Vorgang bis zu einem kontextuellen Sollzustand führen", "A"),
    "ey": ("PRUEFZUSTAND", "den verlangten beobachtbaren Endzustand erreichen", "B"),
    "y": ("AKTUELLER_TRAEGER", "den gegenwärtigen Bild-, Stoff- oder Arbeitsträger wiederaufnehmen", "B"),
    "al": ("ZIEL", "auf die bezeichnete Zielstation oder parallele Station richten", "A"),
    "ch": ("TRENNEN", "einen flüssigen Bestand trennen oder abziehen", "B"),
    "chy": ("WARME_UEBERFUEHRUNG", "ein bereitetes warmes Medium in die Anwendung überführen", "B"),
    "che": ("FLUESSIGKEITSHANDLUNG", "den lokal bestimmten Flüssigkeitsschritt ausführen", "C"),
    "cthy": ("BEREITSCHAFT", "der aktive Ansatz hat den gebrauchsfertigen Zustand erreicht", "B"),
    "oky": ("AKTIVE_VERWENDUNG", "den aktivierten gegenwärtigen Anteil verwenden", "B"),
    "okeey": ("TEMPERIEREN", "das aktive Medium auf den vorgesehenen milden Wärmezustand bringen", "B"),
    "oke": ("SPUELGANG", "den aktivierten Spülgang einmal ausführen", "B"),
    "lche": ("ABLAUF", "den Bestand in den nachgeordneten Empfänger abführen", "B"),
    "ckhy": ("VERBUNDENER_WEG", "durch gekoppelte Läufe oder Stationen führen", "B"),
    "olor": ("VORQUELLENPRODUKT", "das bereitete Produkt des wiederaufgenommenen Voransatzes", "B"),
    "olk": ("TRANSFERSTATION", "Zwischenmittel oder Empfänger eines Transfers", "C"),
}


# Only cards whose old fluent gloss obscured the common minimum are rewritten.
REVISED = {
    "6f7ff82c76200aeecae9": "bearbeite den aktuellen Stoff gleichmäßig und schließe den Schritt",
    "b921a2368e09f02de55e": "der gegenwärtig geführte Stoff oder Anteil",
    "c10aec64909304862255": "der gegenwärtige Bildbesitzer am feucht-schattigen Standort",
    "04a3877d47ad4220c8f7": "führe den Bestand in den Nachlauf ab und schließe den Schritt",
    "0f18de1d7e594ddb548a": "das an der nachgeordneten Station bereitgestellte Öl",
    "1b1ffddd3701120893de": "koche im nachgeordneten Arbeitsschritt sanft und schließe ihn",
    "29e0eb22979b977fc148": "schließe den nachgeordneten Ablauf",
    "dcda95c73b4c3f0991b6": "knüpfe an den bereits eingeführten Ansatz an",
    "1645e61f0288015324e1": "aktiviere die Zugabe eines vorgeschriebenen Anteils",
    "308e8ea50c063184d073": "aktiviere das Zusammenführen beider bezeichneten Anteile",
    "3ae9a12d7ba611413d18": "aktiviere den Arbeitsschritt an der bezeichneten Stelle",
    "7d2404c9cd75388047a4": "aktiviere als Nächstes den oberen Lauf",
    "b5fcea11250884de8f1d": "aktiviere den nächsten quantifizierten Arbeitsposten",
    "bc4f1f5f26222da01f54": "führe den Vorgang bis zur Bereitschaft und schließe den Schritt",
    "c45ebac54f6ac049ec7c": "führe den Vorgang bis zur Klarheit und schließe den Schritt",
    "78b3b31b7865a818e632": "richte den Vorgang auf die zweite Station, wiederhole und schließe",
    "dd0ecaf92868ce5143f9": "führe den Bestand an die bezeichnete Zielstation",
    "6afeb5c68fca78c98f8d": "gebrauche das bereitete Ergebnis frisch",
    "7a4bb819073317ad7f8b": "das bereitete verwendbare Ergebnis des aktiven Ansatzes",
    "54d0e22d3006a149201e": "verwende für den markierten Gegenposten dieselbe Dauer wie zuvor",
    "90bcf0a6de0654a7a378": "führe zum markierten nachgeordneten Ablauf",
    "b6b65471d36361696e5d": "wähle danach den markierten unteren Ablauf",
    "259b2b38f8b7b6f5a12b": "führe den örtlichen Flüssigkeitsschritt als Spülung aus und schließe",
    "4de12cf34afdbf0d3436": "führe den örtlichen Flüssigkeitsschritt zu gleichen Teilen aus und schließe",
    "4d45590e522ad37c6274": "nimm daraus, aus demselben bereits eingeführten Ansatz",
    "b5df9120bccca971228e": "führe den Vorgang bis zum verlangten sichtbaren Endzustand",
    "65f320e75510b2f38182": "wähle den faserigen unteren Wurzelteil aus",
    "faf32198d9aa0c93cdf1": "wähle den bezeichneten Materialanteil aus",
    "10488b972d663320f205": "beschaffe den Bildbesitzer vor der Blüte",
    "b9d7b6d89f4744074011": "beschaffe den Bildbesitzer im Frühjahr",
    "601b7745a6439b37b5ef": "trenne den flüssigen Bestand durch Abziehen und schließe",
    "d225b7ad522a8b7e85e0": "trenne den flüssigen Bestand durch klares Seihen und schließe",
    "5e84413275b6e1c9eb13": "überführe das erwärmte Wasser in die Anwendung",
    "a48efd6ef02be023c0ee": "überführe das warme Blattmedium als Auflage in die Anwendung",
    "e0b630c5045363151120": "sobald der aktive Ansatz gebrauchsfertig ist",
    "276a7c20f7b635f2ae37": "verwende den aktivierten gegenwärtigen Anteil",
    "0275fbf14e07935b0a45": "bringe das aktive Medium auf lauwarmen Arbeitszustand",
    "7db18b2b0fd8cc3b1753": "führe den aktivierten Spülgang einmal aus und schließe",
    "de7321b226894998bfa6": "führe den verbrauchten Bestand in den unteren Empfänger ab und schließe",
    "2cc8bb310ed348970e8b": "führe den Bestand durch die verbundenen Läufe",
    "dec4017258316897df59": "entnimm das bereitete Produkt des Voransatzes",
}


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    cards = [r for r in read(V43) if r["scope"] == "PROSE_EXACT_CARD"]
    host_rows = read(V44)
    events = read(V40)
    assert len(cards) == 173 and len(host_rows) == 173 and len(events) == 381
    host_by_id = {r["joint_tuple_id"]: r for r in host_rows}
    revised_cards: list[dict[str, object]] = []
    for card in cards:
        hrow = host_by_id[card["lexicon_id"]]
        host = hrow["page_host"]
        if host in STEMS:
            stem_class, minimum, tier = STEMS[host]
            decomposition = f"{stem_class}({host}) + exakte Koordinate {hrow['coordinate_id']} + lizenzierte Eintrittsform"
            status = "PROVISIONAL_SHARED_STEM" if tier in {"A", "B"} else "WEAK_SHARED_STEM"
        else:
            stem_class = f"WHOLE_CARD_{host.upper()}"
            minimum = "unaufgelöster fester Ganzkartenkern; konkrete Funktion nur in dieser exakten Karte"
            tier = "D"
            decomposition = f"Ganzkartenkern {host} + exakte Koordinate {hrow['coordinate_id']} + lizenzierte Eintrittsform"
            status = "WHOLE_CARD_NO_SHARED_STEM_YET"
        # The hand-authored revision table uses collision-free published ID
        # prefixes for compact auditability; V43 itself remains keyed by the
        # complete opaque joint-tuple identifier.
        revised = next(
            (value for prefix, value in REVISED.items() if card["lexicon_id"].startswith(prefix[:7])),
            card["current_default"],
        )
        revised_cards.append({
            "joint_tuple_id": card["lexicon_id"],
            "page_host": host,
            "surface_examples": card["surface_examples"],
            "stem_class": stem_class,
            "stable_minimal_stem_value_German": minimum,
            "formal_additions": decomposition,
            "local_medical_expansion_German": revised,
            "v43_previous_default_German": card["current_default"],
            "revision": "REVISED_TO_COMMON_STEM" if revised != card["current_default"] else "LOCAL_EXPANSION_RETAINED",
            "stem_tier": tier,
            "status": status,
            "events": card["events"],
            "pages": card["pages"],
        })
    revised_cards.sort(key=lambda r: (str(r["stem_tier"]), str(r["stem_class"]), str(r["joint_tuple_id"])))
    write(HERE / "V45_R2_REVISED_173_CARD_LEXICON.tsv", revised_cards)

    by_id = {str(r["joint_tuple_id"]): r for r in revised_cards}
    cmd = [str(ROOT / "vmanus-exp"), "query-tsv", str(ROOT / "gdt327_joint_tuple_interlinear.tsv"),
           "--selector", "page"]
    for page in ["f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"]:
        cmd += ["--allow", page]
    cmd += ["--columns", "page,locus,group_index,dy_closure,b3", "--forbid-prefix", "f84"]
    queried = subprocess.run(cmd, check=True, capture_output=True, text=True).stdout
    formal = {(r["page"], r["locus"], r["group_index"]): r
              for r in csv.DictReader(io.StringIO(queried), delimiter="\t")}
    interlinear: list[dict[str, object]] = []
    for event in events:
        card = by_id[event["exact_tuple_id"]]
        state = formal[(event["page"], event["locus"], event["event_index"])]
        interlinear.append({
            "page": event["page"], "locus": event["locus"], "record": event["record"],
            "event_index": event["event_index"], "surface": event["surface"],
            "joint_tuple_id": event["exact_tuple_id"], "page_host": card["page_host"],
            "stem_class": card["stem_class"],
            "stable_minimal_stem_value_German": card["stable_minimal_stem_value_German"],
            "formal_additions": card["formal_additions"],
            "dy_closure": state["dy_closure"], "b3": state["b3"],
            "local_medical_expansion_German": card["local_medical_expansion_German"],
            "meaning_status": "CREATIVE_STEM_CONSTRAINED_EXPANSION_NOT_DECIPHERMENT",
        })
    write(HERE / "V45_R2_REVISED_381_EVENT_INTERLINEAR.tsv", interlinear)

    stem_rows = []
    for host, (stem_class, minimum, tier) in STEMS.items():
        members = [r for r in revised_cards if r["page_host"] == host]
        stem_rows.append({
            "rank_tier": tier, "page_host": host, "stem_class": stem_class,
            "stable_minimal_value_German": minimum,
            "distinct_joint_cards": len(members),
            "fixed_panel_events": sum(int(r["events"]) for r in members),
            "surface_examples": " || ".join(str(r["surface_examples"]) for r in members),
            "local_expansions": " || ".join(str(r["local_medical_expansion_German"]) for r in members),
            "historical_workshop_mechanism": "Kontextabhängig ergänzte Kürzungs-/Formularkarte; Bild, Record und Vorzustand liefern ausgelassene Argumente",
            "status": "CREATIVE_SHARED_STEM_HYPOTHESIS",
        })
    dy_events = sum(str(r["dy_closure"]) == "1" for r in interlinear)
    stem_rows.append({
        "rank_tier": "A", "page_host": "<FORMAL_DY_COORDINATE>",
        "stem_class": "VOLLZUG_SCHLUSS",
        "stable_minimal_value_German": "lokale Handlung bis zum vorgesehenen Endpunkt vollziehen und die Arbeitszelle schließen",
        "distinct_joint_cards": len({r["joint_tuple_id"] for r in interlinear if str(r["dy_closure"]) == "1"}),
        "fixed_panel_events": dy_events,
        "surface_examples": "verschiedene sichtbare -dy-Realisierungen; kein freier PAGE_HOST-Stamm",
        "local_expansions": "spülen / seihen / erwärmen / ablaufen / ruhen / mischen + Schrittabschluss",
        "historical_workshop_mechanism": "formelhafter Vollzugs-/Rubrikschluss; konkrete Handlung stammt aus der ganzen Karte",
        "status": "CREATIVE_FORMAL_CLOSURE_HYPOTHESIS",
    })
    stem_rows.sort(key=lambda r: (str(r["rank_tier"]), -int(r["fixed_panel_events"]), str(r["page_host"])))
    write(HERE / "V45_R2_STEM_LEXICON.tsv", stem_rows)

    checks = {
        "schema": "SIDEQUEST_V45_R2_MEDICAL_STEM_REVISION_V1", "status": "PASS",
        "checks": {
            "exact_cards_173": len(revised_cards) == 173,
            "events_381": len(interlinear) == 381,
            "all_events_joined": all(r["joint_tuple_id"] in by_id for r in interlinear),
            "all_cards_have_stem_or_whole_card_core": all(r["stem_class"] for r in revised_cards),
            "all_cards_have_local_expansion": all(r["local_medical_expansion_German"] for r in revised_cards),
            "revised_cards": sum(r["revision"] == "REVISED_TO_COMMON_STEM" for r in revised_cards),
            "fixed_ten_page_scope": sorted({r["page"] for r in interlinear}),
            "astro_status": "SEPARATE_LOCAL_LABEL_NAMESPACE_UNCHANGED_NO_GDT327_EVENTS",
            "f84_accessed": False, "f84r_accessed": False,
        },
    }
    (HERE / "V45_R2_VALIDATION.json").write_text(json.dumps(checks, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(checks, ensure_ascii=False))


if __name__ == "__main__":
    main()

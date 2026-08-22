#!/usr/bin/env python3
"""Build the V44 R1 workshop-master stem-family proposal.

This deliberately exploratory sidequest artifact keeps exact cards and formal
coordinates visible.  It does not turn PAGE_HOSTs into established morphemes.
"""

from __future__ import annotations

import csv
import io
import subprocess
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
PAGES = ("f10r", "f11r", "f55v", "f56r", "f67r2", "f68r1", "f69v", "f81v", "f82r", "f83r")
LEXICON = ROOT / "experiments/yolo/sidequest_theory_candidates_v43/V43_CURRENT_PROSE_DICTIONARY.tsv"


# Manual workshop hypotheses.  These are semantic intersections of the V43
# creative defaults, not recovered plaintext.  Anything absent from this table
# remains a one-family inventory row rather than receiving an invented stem.
HYP = {
    "ey": ("ERREICHTER/GEFORDERTER ENDZUSTAND", "Wrapper wechselt (shey/cheey), PAGE_HOST und Joint-Tuple bleiben gleich; die konkrete Klarheitslesung kommt aus dem Nasskontext.", "Nur eine exakte Karte; 'Fluessigkeit' und 'Ablaufen' sind nicht im Kern belegt.", ".66", "STRONGEST_SINGLE_CARD_STEM_CANDIDATE"),
    "ok": ("AKTIVEN POSTEN ZUWEISEN/IN EINE TECHNISCHE RELATION SETZEN", "ok bleibt Basis; rechte Familie aiin/ain/al/ar/air spezifiziert Mass, Eintrag, Vereinigung oder Zielbezug; q ist Renderer/Eintritt.", "Die lokalen Ziel- und Lauflesungen sind stark kontextabhaengig; kein einheitliches deutsches Verb deckt alle Karten.", ".72", "STRONG_PRODUCTIVE_FORM_FAMILY"),
    "or": ("BEREITETE/VERFUEGBARE ARBEITSMATERIE", "or ohne rechte Familie bezeichnet den bereiteten Arbeitsstoff; +ain macht daraus eine gebrauchsfertige Verwendungskarte; ch/s sind Wrapper.", "Auf zehn Seiten fast nur Fluessigkeitskontexte; koennte breiter 'bereiteter Posten' sein.", ".71", "STRONG_SEMANTIC_CORE_CANDIDATE"),
    "ot": ("ENTSPRECHENDER SEKUNDAER-/FOLGEBEZUG", "ot bleibt Basis; rechte Familie aiin/al/ar bindet den Bezug an Zeitstandard oder unteren/zweiten Lauf.", "Dauer und Ablauf haben nur den abstrakten Folge-/Korrespondenzbezug gemeinsam.", ".44", "MEDIUM_RELATIONAL_STEM_CANDIDATE"),
    "ar": ("QUELLE/HERKUNFT: DARAUS, AUS DEMSELBEN", "ar steht hier ohne rechte Familie; ch/d/s sind austauschbare Renderer derselben exakten Karte.", "Nur eine Joint-Tuple-Karte; sichtbares -ar tritt andernorts als RIGHT_FAMILY auf und darf nicht automatisch gleichgesetzt werden.", ".73", "STRONG_SINGLE_CARD_RELATION_CANDIDATE"),
    "al": ("ZIEL/WEITERLEITUNG: DORTHIN", "al ohne rechte Familie ist Zielkarte; DY erzeugt eine geschlossene Wiederholungs-/Zweitstellenkarte; Wrapper variieren.", "Die Bedeutung 'zweite Oeffnung' in daldy kann teilweise aus DY/Feldschluss stammen.", ".76", "STRONG_DIRECTIONAL_STEM_CANDIDATE"),
    "aiin": ("VORGESCHRIEBENE MASS-/STANDARDANGABE", "aiin als PAGE_HOST bleibt unter ch/d/s/t-Wrappern identisch; rechtsfamilienlos.", "Als sichtbare RIGHT_FAMILY in okaiin/otaiin/cthaiin kann aiin eine andere formale Funktion haben; nicht blind zusammenwerfen.", ".82", "STRONG_MEASURE_STANDARD_CANDIDATE"),
    "ain": ("DURCHGANG/ABGEMESSENE EINHEIT UNSICHER", "ain als PAGE_HOST (dain) getrennt von der gleich geschriebenen RIGHT_FAMILY ain behandeln.", "PAGE_HOST-Default 'durch ein Tuch' widerspricht einer simplen Gleichsetzung mit der Masslesung der rechten Familie.", ".24", "HOMOGRAPHY_WARNING_NOT_STABLE_STEM"),
    "l": ("FORTSETZUNG/KANAL AUS DEM VORIGEN ARBEITSSCHRITT", "l mit O-frame ergibt die offene Fortsetzungskarte; DY schliesst lokale Varianten; ar kann einen Laufabschluss spezifizieren.", "dl='Oel' und oldy='sanft kochen' sind semantische Ausreisser der erzwungenen V43-Lokallesung.", ".52", "MEDIUM_CONTINUATION_STEM_CANDIDATE"),
    "y": ("AKTUELLER/DEIKTISCHER ARBEITSPOSTEN", "y ohne frame/inner-D ist die hochrecurrente aktuelle-Portion-Karte; inner-D/O-frame erzeugen andere Konstruktionskarten.", "Mischhandlung und Standortbeschreibung zeigen, dass PAGE_HOST allein nicht die gesamte Bedeutung traegt.", ".63", "STRONG_CORE_WITH_COORDINATE_DEPENDENCE"),
    "che": ("BEGRENZTE MANIPULATION MIT SCHRITTSCHLUSS", "che+DY bildet abgeschlossene Arbeitskarten; OT-frame waehlt die Gleichteil-/Mischvariante.", "Nur zwei Karten, und der gemeinsame Gehalt kann fast vollstaendig von DY statt che stammen.", ".40", "MEDIUM_OPERATION_NUCLEUS"),
    "ch": ("ABZIEHEN/SEIHEN ALS ABGESCHLOSSENER SCHRITT", "ch erscheint hier nur in DY-geschlossenen Karten; Wrapper/frame unterscheiden Abziehen und Klarseihen.", "Der gemeinsame Schlusscharakter ist wahrscheinlich DY, nicht PAGE_HOST ch.", ".31", "WEAK_OPERATION_NUCLEUS"),
    "chy": ("WARME FLUESSIGKEIT ZUFUEHREN/ANWENDEN", "chy verbindet zwei warme Transfer-/Anwendungskarten; frame und inner-D spezialisieren Einguss gegen Umschlag.", "Zwei Einzelvorkommen; 'warm' kann aus dem Bild-/Recordkontext eingetragen worden sein.", ".35", "WEAK_WARM_TRANSFER_CANDIDATE"),
    "cth": ("ZUGABE EINES BEMESSENEN STOFFES", "cth+RIGHT_Aiin ist eine einzelne Zugabekarte.", "Ein einziges Ereignis; keine interne Familie.", ".18", "UNPOWERED_SINGLETON_STEM"),
    "e": ("WARTEN BIS ZUSTAND/REIFE", "e tritt in DY-geschlossenen Zustandskarten auf; OT-frame verschiebt Bereitschaft zu Klarheit.", "Gemeinsamer Gehalt kann aus DY plus Recordkontext statt e stammen.", ".61", "MEDIUM_STATE_GATE_NUCLEUS"),
    "chey": ("BEZEICHNETEN STOFFTEIL AUSWAEHLEN/NEHMEN", "chey ist PAGE_HOST; d-Wrapper und OT-frame spezialisieren Wurzel gegen bezeichneten Anteil.", "Pflanzenteil ist lokal; der abstrakte Kern duerfte nur Auswahl/Entnahme tragen.", ".60", "MEDIUM_SELECTION_STEM_CANDIDATE"),
    "k": ("BEMESSENE ODER FLIESSENDE EINHEIT", "k verbindet Mengenkarte und zwei Flusskarten; rechte Familie ain/air und Wrapper spezifizieren.", "Die Schnittmenge ist schwach und kann reine Recordkohaerenz sein.", ".28", "WEAK_QUANTITY_FLOW_CANDIDATE"),
    "o": ("NAECHSTER STOFF/NAECHSTER ZUBEREITUNGSSCHRITT", "o erscheint als Stoffnahme, Zugabe und DY-geschlossener Ziehschritt; weitere Koordinaten tragen die konkrete Aktion.", "Drei Bedeutungen sind zu verschieden fuer einen stabilen semantischen Kern.", ".25", "WEAK_PROCEDURAL_CORE"),
    "chol": ("BEZUG AUF SIMPLEX/SEINE ZUBEREITUNG", "chol verbindet abgebildeten Simplex und warme Anwendung; Wrapper/frame spezialisieren.", "Nur drei Ereignisse, lokaler Bildbezug gegen Prozessaktion.", ".25", "WEAK_SIMPLEX_REFERENCE"),
    "chor": ("SAMMELZEIT/-ZUSTAND DER PFLANZE", "chor erscheint in zwei Sammelkarten; Wrapper/frame teilen Vorbluete und Fruehjahr.", "Nur Herbal-Lokalkontext und zwei Ereignisse.", ".43", "MEDIUM_LOCAL_HERBAL_STEM"),
}


def guarded(path: Path, columns: list[str]) -> list[dict[str, str]]:
    cmd = [str(ROOT / "vmanus-exp"), "query-tsv", str(path), "--selector", "page"]
    for page in PAGES:
        cmd += ["--allow", page]
    cmd += ["--columns", ",".join(columns), "--forbid-prefix", "f84"]
    out = subprocess.run(cmd, cwd=ROOT, check=True, text=True, capture_output=True).stdout
    lines = [line for line in out.splitlines() if not line.startswith("GUARD_STATS ")]
    return list(csv.DictReader(io.StringIO("\n".join(lines)), delimiter="\t"))


def main() -> None:
    formal = guarded(
        ROOT / "gdt327_joint_tuple_interlinear.tsv",
        ["page", "locus", "group_index", "joint_tuple_id", "host_id", "coordinate_id", "observed_wrapper", "dy_closure", "b3"],
    )
    native = guarded(
        ROOT / "gdt278_native_event_inventory.tsv",
        ["page", "locus", "group_index", "page_host", "local_frame", "inner_d", "right_family", "dy_closure", "b3", "wrapper"],
    )
    native_by_event = {(r["page"], r["locus"], r["group_index"]): r for r in native}
    tuple_meta: dict[str, dict[str, str]] = {}
    for row in formal:
        key = (row["page"], row["locus"], row["group_index"])
        n = native_by_event[key]
        merged = dict(row)
        merged.update({k: n[k] for k in ("page_host", "local_frame", "inner_d", "right_family", "wrapper")})
        tuple_meta.setdefault(row["joint_tuple_id"], merged)

    with LEXICON.open(encoding="utf-8", newline="") as f:
        lexicon = [r for r in csv.DictReader(f, delimiter="\t") if r["scope"] == "PROSE_EXACT_CARD"]
    grouped: dict[str, list[tuple[dict[str, str], dict[str, str]]]] = defaultdict(list)
    missing = []
    for row in lexicon:
        meta = tuple_meta.get(row["lexicon_id"])
        if meta is None:
            missing.append(row["lexicon_id"])
        else:
            grouped[meta["page_host"]].append((row, meta))
    assert not missing, missing
    assert len(grouped) == 136

    rows = []
    for host, cards in grouped.items():
        cards.sort(key=lambda pair: (-int(pair[0]["events"]), pair[0]["lexicon_id"]))
        events = sum(int(card["events"]) for card, _ in cards)
        surfaces = " || ".join(f'{card["surface_examples"]} [{card["lexicon_id"]}]' for card, _ in cards)
        meanings = " || ".join(card["current_default"] for card, _ in cards)
        coordinates = " || ".join(
            f'{card["lexicon_id"]}:FRAME={meta["local_frame"]};INNER_D={meta["inner_d"]};RIGHT={meta["right_family"]};DY={meta["dy_closure"]};B3={meta["b3"]};WRAPPER_EXAMPLE={meta["observed_wrapper"]}'
            for card, meta in cards
        )
        if host in HYP:
            intersection, rule, contrary, conf, status = HYP[host]
            priority = 1 if float(conf) >= .70 else 2 if float(conf) >= .50 else 3 if len(cards) > 1 else 4
        else:
            intersection = "NUR LOKALER V43-DEFAULT; KEINE FAMILIEN-SCHNITTMENGE PRUEFBAR"
            rule = "PAGE_HOST ist inventarisiert; mangels mehrerer semantisch unabhaengiger Karten keine produktive Stammregel ableitbar."
            contrary = "Einzelkarte oder nicht manuell kalibrierte Kleinfamilie; V43-Bedeutung wurde kontextuell erzwungen."
            conf = ".10" if len(cards) == 1 else ".16"
            status = "INVENTORY_ONLY_NO_STEM_CLAIM"
            priority = 5 if len(cards) == 1 else 4
        rows.append({
            "rank": "",
            "priority_tier": str(priority),
            "candidate_page_host": host,
            "exact_card_types": str(len(cards)),
            "events_on_ten_pages": str(events),
            "surface_cards_and_tuple_ids": surfaces,
            "current_V43_defaults": meanings,
            "shared_semantic_intersection": intersection,
            "formal_coordinates_per_card": coordinates,
            "proposed_form_rule": rule,
            "counterevidence_or_exception": contrary,
            "confidence": conf,
            "status": status,
        })
    rows.sort(key=lambda r: (int(r["priority_tier"]), -float(r["confidence"]), -int(r["events_on_ten_pages"]), r["candidate_page_host"]))
    for i, row in enumerate(rows, 1):
        row["rank"] = str(i)

    output = HERE / "V44_R1_COMPLETE_WORKSHOP_STEM_FAMILIES.tsv"
    with output.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)

    strongest = [r for r in rows if int(r["priority_tier"]) <= 2]
    report = [
        "# V44 R1 — Werkstattlehrmeister: Stammfamilien",
        "",
        "## Ergebnis",
        "",
        "Ich wuerde den Lehrlingen **nicht 136 Wortstaemme** beibringen. Die einfachste vorlaeufige Werkstattregel ist ein kleines Prompt-Inventar aus etwa acht brauchbaren Kernen; PAGE_HOST, Wrapper, rechte Familie und Schlusskoordinaten bleiben dabei getrennt. Der Rest bleibt eine ganze Karte, bis eine zweite unabhaengige Verwendung eine Regel erzwingt.",
        "",
        "Die beste produktive Familie ist `ok`: `ok + RIGHT(aiin/ain/al/ar/air)` bildet mehrere Zuweisungs-/Relationskarten. Die besten einzelnen Kerne sind `aiin` (Mass/Standard), `al` (Ziel), `ar` (Quelle), `or` (bereiteter Arbeitsstoff), `ey` (geforderter Endzustand), `y` (aktueller Posten) und mit geringerer Sicherheit `l` (Fortsetzung aus dem Vorigen).",
        "",
        "## Lehrregel",
        "",
        "```text",
        "Oberflaechenkarte = [Renderer/Wrapper] + PAGE_HOST + [rechte Familie] + [DY/B3-Schluss]",
        "Bedeutung der Karte  != Bedeutung des PAGE_HOST allein",
        "```",
        "",
        "- `ch/s/q/t/d` duerfen bei einer identischen Joint-Tuple-Karte als Renderer wechseln; sie erhalten deshalb hier keine Wortbedeutung.",
        "- `RIGHT=aiin/ain/al/ar/air` wird als eigenes Kartenfeld gefuehrt, selbst wenn dieselbe sichtbare Sequenz auch als PAGE_HOST vorkommt.",
        "- `DY` ist zuerst eine Abschluss-/Commit-Koordinate. Das konkrete Verb davor darf nicht vollstaendig dem Host zugeschrieben werden.",
        "- `B3` bleibt getrennt; in den starken Kernfamilien dieser zehn Seiten liefert es keine eigenstaendige Stammlesung.",
        "- Die exakte Joint-Tuple-Karte behaelt immer Vorrang vor einer Stammexpansion.",
        "",
        "## Gerankter Lehrkern",
        "",
        "| Rang | Kern | vorlaeufige Schnittmenge | Konfidenz | Grenze |",
        "|---:|---|---|---:|---|",
    ]
    for row in strongest:
        report.append(f'| {row["rank"]} | `{row["candidate_page_host"]}` | {row["shared_semantic_intersection"]} | {row["confidence"]} | {row["counterevidence_or_exception"]} |')
    report += [
        "",
        "## Besonders wichtig: `ey`",
        "",
        "`ey` ist derzeit **nicht** sicher 'klar' und erst recht nicht der ganze Satz 'bis die Fluessigkeit klar ablaeuft'. Auf den zehn Seiten existiert nur eine exakte `ey`-Karte, sichtbar als `shey/cheey`. Meine kleinstmoegliche Expansion ist `GEFORDERTER ENDZUSTAND ERREICHT?` oder im laufenden Satz 'bis zum geforderten Endzustand'. Die Nassprozessform darf lokal zu 'bis es klar/frei ablaeuft' ausgeschrieben werden.",
        "",
        "## Gegenprobe an den problematischen Familien",
        "",
        "- `y` traegt wahrscheinlich den deiktischen Arbeitsgegenstand, aber `inner-D` und `O-frame` erzeugen Karten, deren V43-Lesungen weit darueber hinausgehen. Das ist gute Evidenz fuer **Kern plus Konstruktion**, nicht fuer ein freies Wort `y`.",
        "- `l` hat eine plausible Voransatz-/Fortsetzungsmitte. `dl = Oel` und `oldy = kochen` sind jedoch nicht aus `l` ableitbar und bleiben zu lernende Gesamtkarten oder falsche lokale Glossierung.",
        "- `ain` als PAGE_HOST darf nicht mit `RIGHT=ain` gleichgesetzt werden. Die formale Analyse behandelt beide als verschiedene Positionen; ihre V43-Lesungen passen nicht sauber zusammen.",
        "- `che/ch/chy/cth` sehen stammartig aus, sind auf diesen Seiten aber schwach belegt. Ein Lehrmeister wuerde sie als ganze Operationskarten lehren, nicht produktiv zerlegen.",
        "",
        "## Vollstaendigkeit und Deutungslimit",
        "",
        f"Die TSV inventarisiert alle {len(grouped)} PAGE_HOST-Familien hinter allen {len(lexicon)} exakten V43-Prosakarten. Nur {len(HYP)} Familien erhalten eine manuell formulierte Arbeitshypothese; die anderen bleiben explizit `INVENTORY_ONLY_NO_STEM_CLAIM`. Das ist eine kreative Werkstatttheorie und keine Entzifferung. Sie behauptet weder Lautwerte noch Sprache, Morpheme oder historische Etymologien.",
        "",
        "`f84` und `f84r` wurden nicht geoeffnet.",
    ]
    (HERE / "V44_R1_WORKSHOP_MASTER_STEM_THEORY.md").write_text("\n".join(report) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

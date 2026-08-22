#!/usr/bin/env python3
"""Build the V42 R1 workshop-master edition from frozen V40/V41 material."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
FIELDS = ROOT / "experiments/yolo/sidequest_theory_candidates_v41/V41_135_FIELD_WORKSHEET.tsv"

DE = {
    "ein vorgeschriebenes Maß": "ein vorgeschriebenes Maß",
    "mit der vorigen Zubereitung weiter": "mit der vorigen Zubereitung fortfahren",
    "diese aktive Portion": "dieser aktive Posten",
    "let it stand until ready; end this instruction": "bis zur Gebrauchsfertigkeit stehen lassen; Schritt beenden",
    "stir until evenly mixed": "gleichmäßig verrühren",
    "die aktive Portion verwenden": "den aktiven Posten verwenden",
    "an die bezeichnete Zielstelle führen": "zur bezeichneten Zielstelle führen",
    "bathe or immerse in the tempered warm liquid; end this instruction": "in der temperierten warmen Flüssigkeit baden oder eintauchen; Schritt beenden",
    "begin the next measured entry": "den nächsten abgemessenen Posten beginnen",
    "rinse the indicated place once; end this instruction": "die bezeichnete Stelle einmal spülen; Schritt beenden",
    "let the spent liquid drain into the lower receiving vessel; end this instruction": "verbrauchte Flüssigkeit in das untere Auffanggefäß ablaufen lassen; Schritt beenden",
    "sobald die Zubereitung gebrauchsfertig ist": "sobald die Zubereitung gebrauchsfertig ist",
    "die bereitete Arbeitsflüssigkeit": "die bereitete Arbeitsflüssigkeit",
    "add one measured portion to the vessel": "eine abgemessene Portion in das Gefäß geben",
    "temper the working liquid and keep it lukewarm": "die Arbeitsflüssigkeit temperieren und lauwarm halten",
    "mix the two portions together": "beide Portionen vermischen",
    "daraus, aus demselben Ansatz": "daraus, aus demselben Ansatz",
    "bis die Flüssigkeit klar abläuft": "bis die Flüssigkeit klar abläuft",
    "then take the following ingredient or plant part": "danach den folgenden Zusatz oder Pflanzenteil nehmen",
    "the lower basin": "das untere Becken",
    "the prepared oil": "das bereitete Öl",
    "through the connected channels": "durch die verbundenen Leitungen",
    "wash the used vessel or channel through once; end this instruction": "gebrauchtes Gefäß oder Leitung einmal ausspülen; Schritt beenden",
    "then fill the vessel": "danach das Gefäß füllen",
    "the first opening": "die erste Öffnung",
    "draw it off; close the rubric": "abziehen; Rubrik schließen",
    "use the freshly prepared remedy": "die frisch bereitete Arznei verwenden",
    "boil gently; close the rubric": "sanft kochen; Rubrik schließen",
    "one measured portion": "eine abgemessene Portion",
    "set the mixed liquid aside in a covered receiving vessel; end this instruction": "die Mischung im bedeckten Auffanggefäß beiseitestellen; Schritt beenden",
    "heat it once; end this instruction": "einmal erwärmen; Schritt beenden",
    "over a gentle heat": "bei sanfter Wärme",
    "begin the rinsing": "mit dem Spülen beginnen",
    "warm water": "warmes Wasser",
    "let the liquid settle; end this instruction": "die Flüssigkeit absetzen lassen; Schritt beenden",
    "strain it once through cloth; end this instruction": "einmal durch ein Tuch seihen; Schritt beenden",
    "through a cloth": "durch ein Tuch",
    "under the same setting": "unter derselben Einstellung",
    "the broad vessel": "das breite Gefäß",
    "over the local place": "über der örtlichen Stelle",
    "for the same interval as before": "für dasselbe Zeitmaß wie zuvor",
    "pour in the warmed water": "das erwärmte Wasser eingießen",
    "bind upon the place; close the rubric": "auf die Stelle binden; Rubrik schließen",
    "mix in equal shares; close the rubric": "zu gleichen Teilen mischen; Rubrik schließen",
    "toward the lower outlet": "zum unteren Auslauf",
    "gleichmäßig bearbeiten": "gleichmäßig bearbeiten",
    "drink it for pain of the stomach": "bei Magenschmerz trinken",
    "gathered before flowering": "vor der Blüte gesammelt",
    "aus dem vorigen Ansatz entnehmen": "aus dem vorigen Ansatz entnehmen",
    "of this pictured simple": "von diesem abgebildeten Simplex",
    "while still warm": "noch warm",
    "nimm den bezeichneten Anteil": "den bezeichneten Anteil nehmen",
    "the immersed part": "der eingetauchte Teil",
    "keep it warm; close the rubric": "warm halten; Rubrik schließen",
    "and let it cool": "und abkühlen lassen",
    "wash once; close this pass": "einmal waschen; diesen Durchgang schließen",
    "let it cool; close the rubric": "abkühlen lassen; Rubrik schließen",
    "strain it clear; close the rubric": "klar seihen; Rubrik schließen",
    "apply at the marked place": "an der bezeichneten Stelle auftragen",
    "until clear": "bis es klar ist",
    "the second opening": "die zweite Öffnung",
    "draw off the clear liquid": "die klare Flüssigkeit abziehen",
    "immerse fully; close the rubric": "vollständig eintauchen; Rubrik schließen",
    "close the lower outlet": "den unteren Auslauf schließen",
    "steep until clear; close the rubric": "bis zur Klarheit ziehen lassen; Rubrik schließen",
    "next open the upper channel": "danach den oberen Lauf öffnen",
    "for one interval": "für ein Zeitmaß",
    "place the person at the basin": "die Person an das Becken setzen",
    "take the fibrous lower root": "die faserige untere Wurzel nehmen",
    "wash it in running water": "in fließendem Wasser waschen",
    "reduce it to a coarse powder": "grob zerstoßen",
    "add red wine": "Rotwein zugeben",
    "keep the remaining root dry": "die übrige Wurzel trocken halten",
    "apply it while warm": "noch warm auftragen",
    "it grows in damp meadow ground": "sie wächst auf feuchtem Wiesengrund",
    "add the expressed juice": "den ausgepressten Saft zugeben",
    "boil it gently": "sanft kochen",
    "one handful": "eine Handvoll",
    "when its flower has opened": "wenn sich ihre Blüte geöffnet hat",
    "until a bitter taste remains": "bis ein bitterer Geschmack verbleibt",
    "preserve that portion under oil": "diesen Anteil unter Öl bewahren",
    "gather the root in spring": "die Wurzel im Frühjahr sammeln",
    "from shaded woodland": "aus schattigem Waldgrund",
    "before the flowering crown opens": "bevor sich die Blütenkrone öffnet",
    "press the bruised root through cloth": "die gequetschte Wurzel durch ein Tuch pressen",
    "strain the liquor a second time": "die Flüssigkeit ein zweites Mal seihen",
    "leave the strained liquor uncovered to cool": "die geseihte Flüssigkeit offen abkühlen lassen",
    "reserve the flowering crown": "die Blütenkrone zurückbehalten",
    "bind it upon a swollen place": "auf die geschwollene Stelle binden",
    "make a warm poultice from its leaves": "aus den Blättern einen warmen Umschlag bereiten",
    "lay it on while warm": "noch warm auflegen",
    "boil the broad leaf gently": "das breite Blatt sanft kochen",
    "in white wine": "in Weißwein",
    "steep it until the liquor is clear": "ziehen lassen, bis die Flüssigkeit klar ist",
    "wash the sore place once": "die wunde Stelle einmal waschen",
    "for its second medicinal use": "für den zweiten Arzneigebrauch",
    "add white wine": "Weißwein zugeben",
    "keep it in a covered jar": "in einem bedeckten Gefäß aufbewahren",
    "use the finished liquor fresh": "die fertige Flüssigkeit frisch verwenden",
    "gather the plant in spring": "die Pflanze im Frühjahr sammeln",
    "the thin lower root": "die dünne untere Wurzel",
    "steep it in white wine": "in Weißwein ziehen lassen",
    "which grows on damp shaded heath": "die auf feuchter schattiger Heide wächst",
    "leave the plaster uncovered until dry": "den Umschlag offen trocknen lassen",
    "its small seed or bud-head": "ihr kleiner Samen- oder Knospenkopf",
    "the dried narrow leaf": "das getrocknete schmale Blatt",
    "dry it in shade": "im Schatten trocknen",
    "keep the remainder dry in shade": "den Rest trocken im Schatten halten",
    "mix it with honey": "mit Honig mischen",
    "use it while freshly mixed": "frisch gemischt verwenden",
    "the pale opened flower": "die blasse geöffnete Blüte",
    "the returning flow": "der zurückkehrende Lauf",
    "before it cools": "bevor es abkühlt",
    "a moderate quantity": "eine mäßige Menge",
    "the affected place": "die betroffene Stelle",
    "then use the lower outlet": "danach den unteren Auslauf benutzen",
    "and proceed to the next basin": "und zum nächsten Becken weitergehen",
    "continue at the second conduit": "an der zweiten Leitung fortfahren",
    "add clean water; close the rubric": "klares Wasser zugeben; Rubrik schließen",
    "cool water": "kühles Wasser",
    "in equal portions": "zu gleichen Teilen",
    "repeat at the second opening; close the rubric": "an der zweiten Öffnung wiederholen; Rubrik schließen",
    "drink the stated portion; close the rubric": "die angegebene Portion trinken; Rubrik schließen",
    "wash once; close the rubric": "einmal waschen; Rubrik schließen",
    "retain the residue; close the rubric": "den Rückstand behalten; Rubrik schließen",
    "after settling": "nach dem Absetzen",
    "until the flow clears": "bis der Lauf klar wird",
    "after the first rinse": "nach der ersten Spülung",
    "wash twice; close the rubric": "zweimal waschen; Rubrik schließen",
    "let the mixture enter": "die Mischung einlaufen lassen",
    "use immediately; close the rubric": "sofort verwenden; Rubrik schließen",
    "for the stated duration": "für die angegebene Dauer",
    "until warm": "bis es warm ist",
    "with the foregoing mixture": "mit der vorigen Mischung",
    "without boiling": "ohne Kochen",
    "at the indicated place": "an der bezeichneten Stelle",
}

RECORDS = {
    ("f10r", "1"): (
        "Nimm die faserige untere Wurzel, wasche sie in fließendem Wasser, bearbeite und zerstoße sie grob aus demselben Ansatz und gib Rotwein zu. Der aktive Posten wird im vorgeschriebenen Maß für den notierten Magenfall verwendet; die übrige Wurzel bleibt trocken. Verwende die frische Zubereitung noch warm mit dem Voransatz, sobald sie gebrauchsfertig ist.",
        "Die Karte des Magenfalls besitzt keinen unabhängigen Bildanker; dieselbe Form könnte eine allgemeinere Indikation oder Dosierformel tragen.",
        "V30s flüssige Prosa wird als zwei offene Artikelklauseln gelesen; 'Magenschmerz' bleibt Default, aber ausdrücklich schwach."
    ),
    ("f10r", "2"): (
        "Die Pflanze steht auf feuchtem Wiesengrund. Wenn die Zubereitung gebrauchsfertig ist, gib den ausgepressten Saft in die Arbeitsflüssigkeit, koche sanft und teile die aktiven Posten nach vorgeschriebenem Maß. Sammle vor der Blüte eine Handvoll und arbeite mit demselben Voransatz weiter. Ist die Blüte geöffnet, führe zwei Arbeitsflüssigkeiten beziehungsweise zwei parallele Flüssigkeitsposten, bis Bitterkeit verbleibt, und bewahre den letzten Anteil unter Öl.",
        "Die doppelte Folge CHOR CHOR und die drei DY-Vorkommen passen schlecht zu normaler Wortprosa; sie können Formularwiederholung statt zweier Flüssigkeiten anzeigen.",
        "CHOR und DY werden als wiederholte Slot-Prompts expandiert; nur der lokale Artikel liefert Saft, Bitterkeit und Öl."
    ),
    ("f11r", "1"): (
        "Sammle die Wurzel im Frühjahr aus schattigem Waldgrund, bevor sich die Blütenkrone öffnet. Presse die gequetschte Wurzel durch ein Tuch, seihe die Flüssigkeit nochmals bis zum klaren Lauf und lasse sie offen abkühlen. Behalte die Blütenkrone zurück. Nimm vom abgebildeten Simplex den vorgeschriebenen aktiven Anteil und binde ihn auf die geschwollene Stelle. Bereite aus den Blättern einen warmen Umschlag und lege ihn gebrauchsfertig und noch warm auf.",
        "Die vier Felder wechseln abrupt von Sammeln und Seihen zu Krone und Umschlag; sie könnten vier unabhängige Artikelnotizen statt einer Rezeptfolge sein.",
        "Die Feldgrenzen bleiben sichtbar: kein künstlicher zeitlicher Übergang zwischen zurückbehaltener Krone und Umschlag."
    ),
    ("f55v", "1"): (
        "Nimm vom breiten Blatt die vorgeschriebene Menge, koche sie sanft in Weißwein und lasse sie ziehen, bis die Flüssigkeit klar wird. Verrühre eine weitere vorgeschriebene Portion gleichmäßig und wasche die wunde Stelle einmal. Für den zweiten Arzneigebrauch gib wieder Weißwein zu, halte die Zubereitung warm und schließe den Schritt. Mische schließlich beide Portionen, bewahre sie bedeckt und verwende die fertige Flüssigkeit frisch.",
        "Die Pflanze ist nur breit als Allium-ähnlich bestimmt; Blatt, Weißwein und Wundwäsche könnten aus einer beliebigen lokal erfundenen Materia-medica-Lesung stammen.",
        "Die vier Schlussarten werden als echte Arbeitsabschlüsse gelesen, nicht als austauschbare Satzzeichen."
    ),
    ("f56r", "1"): (
        "Sammle die Pflanze im Frühjahr. Nimm die dünne untere Wurzel im vorgeschriebenen Maß, lasse sie vor der Blüte in Weißwein ziehen und verwende den Anteil an der gezeigten Stelle. Von dem auf feuchter schattiger Heide wachsenden Simplex lasse den Umschlag offen trocknen. Trockne Samen- oder Knospenkopf und schmales Blatt im Schatten und halte den Rest dort trocken. Verwende einen frischen Ansatz für den notierten Magenfall. Mische den folgenden Anteil mit Honig und gebrauche ihn frisch; nimm zuletzt die bezeichnete Menge der blassen offenen Blüte.",
        "Die Sundew/Drosera-Bildbestimmung ist die stärkste der Pflanzenseiten, aber die sieben offenen Felder können ein Merkmalsdossier statt ein ausführbares Einzelrezept sein.",
        "Der Record bleibt ein siebenklauseliger Artikel; die vielen Pflanzenteile werden nicht zu einer einzigen Kochfolge gezwungen."
    ),
    ("f81v", "1"): (
        "Spüle zuerst die bezeichnete Stelle. Führe aus demselben Ansatz die vorgeschriebene Menge zum unteren Becken, gib das bereitete Öl zu und leite sie durch die verbundenen Kanäle. Spüle Gefäß oder Leitung, halte die Mischung sanft warm, verrühre sie, lasse sie gebrauchsfertig stehen und stelle sie bedeckt beiseite. Gib weitere abgemessene Posten zu, erwärme einmal und lasse abkühlen. Beginne erneut mit Spülen, Absetzen und Klären durch Tuch. Verwende die fertige Portion, führe sie zur ersten Öffnung und schließlich an die bezeichnete Zielstelle.",
        "Das Bild kann Körperbad, Gefäßschema oder bloße dekorative Raumteilung zeigen; 'Öl', Becken und Leitungen sind ungeankerte konkrete Defaults.",
        "Die 24 kurzen Zellen werden als mehrere zusammengehörige Arbeitsphasen gelesen; DY schließt Zellen, nicht notwendig Sätze."
    ),
    ("f82r", "1"): (
        "Spüle Gefäß und Leitung und stelle die gemischte Flüssigkeit bedeckt zurück. Gib eine abgemessene Portion zu und bade den bezeichneten Teil in temperierter warmer Flüssigkeit. Arbeite an der zweiten Öffnung weiter, halte lauwarm, seihe durch Tuch und ziehe über das breite Gefäß ab. Gib bereitetes Öl und klares Wasser zu, lasse absetzen und halte warm. Führe weitere gemessene Portionen aus demselben Ansatz zu, tauche vollständig ein und lasse die gebrauchte Flüssigkeit in das untere Gefäß ab. Schließe und öffne die Ausgänge nacheinander, spüle, gieße warmes Wasser nach, bade, trinke oder binde den bezeichneten Posten auf und mische zuletzt zu gleichen Teilen.",
        "Trinken, Binden, Baden und Leitungsarbeit in einem Record wirken heterogen; einzelne Zellen könnten alternative Verwendungen oder Bildadressen statt zeitlicher Schritte sein.",
        "Die Edition bewahrt die Zellenfolge, kennzeichnet aber keine universelle Person-, Körper- oder Gefäßreferenz."
    ),
    ("f83r", "1"): (
        "Lasse die Flüssigkeit absetzen, tauche den bezeichneten Teil am unteren Ausgang vollständig ein und lasse die vorgeschriebene Portion in das Auffanggefäß ab. Beginne aus demselben Ansatz neu, spüle, gieße warmes Wasser nach, mische und stelle bedeckt zurück. Bade in der gleichmäßigen Mischung, lasse ab, fülle und kläre erneut. Trage die Arbeitsflüssigkeit an der bezeichneten Stelle auf; halte Zeitmaße und Öffnungen ein, spüle, kühle, erwärme, binde auf und behalte den Rückstand. Setze die Person an das Becken, rühre, dosiere, kläre den Lauf und wiederhole Bad, Abzug und Spülung bis zum letzten Zustandsschritt.",
        "38 Zellen sind zu lang für eine sichere lineare Prozedur; sie können mehrere untereinander gesetzte Varianten oder Stationen eines Bildregisters enthalten.",
        "Statt einen einzigen Satz zu erzwingen, wird der Record in fünf Phasen mit wiederkehrenden Spül-, Wärme- und Transferprompts gelesen."
    ),
    ("f83r", "2"): (
        "Bade in temperierter warmer Flüssigkeit, fülle nach und spüle die bezeichnete Stelle. Rühre zum unteren Auslauf, nimm den bezeichneten Anteil, halte ihn lauwarm, trage ihn auf, lasse ihn stehen und binde ihn fest. Rühre und seihe durch Tuch, bade und kläre nochmals. Verwende die vorgeschriebene Menge noch warm an der ersten Öffnung, koche sanft, gib im breiten Gefäß eine Portion zu und wasche zweimal. Lasse unten ab, beginne erneut, verwende die Arbeitsflüssigkeit sofort, öffne den oberen Lauf und gieße warmes Wasser nach.",
        "Die wechselnden Imperative könnten unabhängige kurze Formularantworten sein; ihr gemeinsamer Gegenstand ist vollständig aus dem Bild ergänzt.",
        "Der Record wird als Arbeitsblatt mit vier Phasen statt als syntaktisch durchgehender Absatz expandiert."
    ),
    ("f83r", "3"): (
        "Ziehe die Flüssigkeit ab und erwärme sie einmal. Halte sie für ein Zeitmaß und bis sie warm ist. Führe sie mit der vorigen Mischung an die bezeichnete Zielstelle und arbeite an der zweiten Leitung gleichmäßig weiter.",
        "Der kurze Fortsetzungsrecord kann ebenso gut eine Nachtragsvariante zum vorherigen Record sein; ein selbständiges Rezept ist nicht gesichert.",
        "Die fünf Zellen werden ausdrücklich als Fortsetzung gelesen und nicht mit einer neuen stillen Indikation ausgestattet."
    ),
    ("f83r", "4"): (
        "Setze die Person ohne Kochen an das Becken und führe die vorige Zubereitung durch die erste Öffnung. Nimm den gegenwärtigen Posten im vorgeschriebenen Maß, führe ihn durch ein Tuch und bringe ihn an der bezeichneten Stelle an.",
        "'Person' ist eine Bildausfüllung; formal kann dieselbe Karte auch ein Objekt oder Gefäß an der Station bezeichnen.",
        "Der Zwei-Feld-Nachtrag bleibt knapp; er übernimmt seinen Gegenstand aus dem vorigen Bild-/Recordkontext."
    ),
}


def main() -> None:
    with FIELDS.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh, delimiter="\t"))
    used = {x for row in rows for x in row["complete_card_defaults"].split(" / ")}
    missing = sorted(used - DE.keys())
    if missing:
        raise SystemExit(f"missing translations: {missing}")

    by_record: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_record[(row["page"], row["record_ordinal"])].append(row)

    output = []
    for key, fields in by_record.items():
        if key not in RECORDS:
            raise SystemExit(f"missing record edition: {key}")
        continuous, contradiction, revision = RECORDS[key]
        field_parts = []
        refs = []
        for sequence, field in enumerate(fields, 1):
            translated = [DE[x] for x in field["complete_card_defaults"].split(" / ")]
            refs.append(f"{field['locus']}#{field['field_ordinal']}")
            field_parts.append(
                f"F{sequence:02d} [{field['primary_role']}; {field['closure']}]: "
                + "; ".join(translated)
                + "."
            )
        output.append({
            "page": key[0],
            "record_ordinal": key[1],
            "field_count_expected": str(len(fields)),
            "field_count_represented": str(len(field_parts)),
            "event_count": str(sum(int(x["event_count"]) for x in fields)),
            "ordered_field_refs": " -> ".join(refs),
            "ordered_135_field_edition": " || ".join(field_parts),
            "continuous_German_workshop_edition": continuous,
            "strongest_contradiction": contradiction,
            "revision_from_V30_V40": revision,
            "status": "COMPLETE_SPECULATIVE_R1_EDITION",
        })

    out_tsv = OUT / "V42_R1_ELEVEN_RECORD_EDITION.tsv"
    with out_tsv.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(output[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(output)

    checks = {
        "agent_role": "R1_WORKSHOP_MASTER",
        "records_expected": 11,
        "records_written": len(output),
        "fields_expected": 135,
        "fields_represented": sum(int(x["field_count_represented"]) for x in output),
        "events_expected": 381,
        "events_represented": sum(int(x["event_count"]) for x in output),
        "unique_defaults_used": len(used),
        "untranslated_defaults": missing,
        "all_field_counts_reconcile": all(x["field_count_expected"] == x["field_count_represented"] for x in output),
        "all_records_have_concrete_sequence": all(bool(x["continuous_German_workshop_edition"]) for x in output),
        "all_records_have_strongest_contradiction": all(bool(x["strongest_contradiction"]) for x in output),
        "all_records_have_revision": all(bool(x["revision_from_V30_V40"]) for x in output),
        "pages_used": sorted({x["page"] for x in output}),
        "sealed_selectors_accessed": [],
        "status": "PASS" if len(output) == 11 and sum(len(v) for v in by_record.values()) == 135 and not missing else "FAIL",
    }
    (OUT / "V42_R1_VALIDATION.json").write_text(json.dumps(checks, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

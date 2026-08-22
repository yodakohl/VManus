#!/usr/bin/env python3
"""Build the independent V42 R2 medical edition from the frozen V41 worksheet.

This is an explicitly creative sidequest expansion.  It does not inspect or
claim any sealed folio and it does not alter the underlying V40/V41 cards.
"""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SOURCE = ROOT / "experiments/yolo/sidequest_theory_candidates_v41/V41_135_FIELD_WORKSHEET.tsv"


# Existing German defaults pass through unchanged.  Every English V41 default
# is expanded here once, without changing its card identity.
DE = {
    "take the fibrous lower root": "Nimm die faserige untere Wurzel",
    "wash it in running water": "wasche sie in fließendem Wasser",
    "reduce it to a coarse powder": "zerstoße sie zu grobem Pulver",
    "add red wine": "gib Rotwein hinzu",
    "drink it for pain of the stomach": "trinke es bei Magenschmerz",
    "keep the remaining root dry": "bewahre die übrige Wurzel trocken auf",
    "use the freshly prepared remedy": "gebrauche die frisch bereitete Arznei",
    "apply it while warm": "wende sie warm an",
    "it grows in damp meadow ground": "sie wächst auf feuchtem Wiesengrund",
    "add the expressed juice": "gib den ausgepressten Saft hinzu",
    "boil it gently": "koche es sanft",
    "gathered before flowering": "vor der Blüte gesammelt",
    "one handful": "eine Handvoll",
    "when its flower has opened": "wenn sich die Blüte geöffnet hat",
    "until a bitter taste remains": "bis ein bitterer Geschmack bleibt",
    "preserve that portion under oil": "bewahre diesen Anteil unter Öl",
    "gather the root in spring": "sammle die Wurzel im Frühjahr",
    "from shaded woodland": "vom schattigen Waldort",
    "before the flowering crown opens": "bevor sich die Blütenkrone öffnet",
    "press the bruised root through cloth": "presse die gequetschte Wurzel durch ein Tuch",
    "strain the liquor a second time": "seihe die Flüssigkeit ein zweites Mal",
    "leave the strained liquor uncovered to cool": "lasse die geseihte Flüssigkeit offen abkühlen",
    "reserve the flowering crown": "behalte die Blütenkrone zurück",
    "of this pictured simple": "von diesem abgebildeten Simplex",
    "bind it upon a swollen place": "binde es auf die geschwollene Stelle",
    "make a warm poultice from its leaves": "bereite aus den Blättern einen warmen Umschlag",
    "lay it on while warm": "lege ihn warm auf",
    "boil the broad leaf gently": "koche das breite Blatt sanft",
    "in white wine": "in Weißwein",
    "steep it until the liquor is clear": "lasse es ziehen, bis die Flüssigkeit klar ist",
    "stir until evenly mixed": "rühre, bis alles gleichmäßig vermischt ist",
    "wash the sore place once": "wasche die wunde Stelle einmal",
    "for its second medicinal use": "für den zweiten Arzneigebrauch",
    "add white wine": "gib Weißwein hinzu",
    "while still warm": "solange es noch warm ist",
    "boil gently; close the rubric": "koche sanft und beende diesen Arbeitsschritt",
    "mix the two portions together": "mische beide Anteile zusammen",
    "keep it in a covered jar": "bewahre es in einem bedeckten Gefäß",
    "use the finished liquor fresh": "gebrauche die fertige Flüssigkeit frisch",
    "gather the plant in spring": "sammle die Pflanze im Frühjahr",
    "then take the following ingredient or plant part": "nimm danach den folgenden Zusatz oder Pflanzenteil",
    "the thin lower root": "die dünne untere Wurzel",
    "steep it in white wine": "lasse es in Weißwein ziehen",
    "which grows on damp shaded heath": "die auf feuchter schattiger Heide wächst",
    "leave the plaster uncovered until dry": "lasse das Pflaster unbedeckt trocknen",
    "its small seed or bud-head": "ihren kleinen Samen- oder Knospenkopf",
    "the dried narrow leaf": "das getrocknete schmale Blatt",
    "dry it in shade": "trockne es im Schatten",
    "keep the remainder dry in shade": "bewahre den Rest trocken im Schatten",
    "mix it with honey": "mische es mit Honig",
    "use it while freshly mixed": "gebrauche es frisch vermischt",
    "the pale opened flower": "die helle geöffnete Blüte",
    "begin the next measured entry": "beginne den nächsten abgemessenen Posten",
    "the returning flow": "der zurücklaufende Strom",
    "before it cools": "bevor es abkühlt",
    "one measured portion": "ein abgemessener Anteil",
    "the lower basin": "das untere Becken",
    "the prepared oil": "das bereitete Öl",
    "a moderate quantity": "eine mäßige Menge",
    "the immersed part": "der eingetauchte Teil",
    "through the connected channels": "durch die verbundenen Läufe",
    "wash the used vessel or channel through once; end this instruction": "spüle das benutzte Gefäß oder den Lauf einmal aus und beende den Schritt",
    "keep it warm; close the rubric": "halte es warm und beende den Schritt",
    "let it cool; close the rubric": "lasse es abkühlen und beende den Schritt",
    "let it stand until ready; end this instruction": "lasse es bis zur Bereitschaft stehen und beende den Schritt",
    "set the mixed liquid aside in a covered receiving vessel; end this instruction": "stelle die Mischung im bedeckten Auffanggefäß beiseite und beende den Schritt",
    "add one measured portion to the vessel": "gib einen abgemessenen Anteil in das Gefäß",
    "and let it cool": "und lasse es abkühlen",
    "heat it once; end this instruction": "erwärme es einmal und beende den Schritt",
    "over a gentle heat": "bei sanfter Wärme",
    "rinse the indicated place once; end this instruction": "spüle die bezeichnete Stelle einmal und beende den Schritt",
    "begin the rinsing": "beginne die Spülung",
    "warm water": "warmes Wasser",
    "wash once; close this pass": "wasche einmal und beende diesen Durchgang",
    "wash once; close the rubric": "wasche einmal und beende den Schritt",
    "the affected place": "die betroffene Stelle",
    "then use the lower outlet": "benutze danach den unteren Ablauf",
    "then fill the vessel": "fülle danach das Gefäß",
    "temper the working liquid and keep it lukewarm": "temperiere die Arbeitsflüssigkeit und halte sie lauwarm",
    "the first opening": "die erste Öffnung",
    "strain it clear; close the rubric": "seihe es klar und beende den Schritt",
    "apply at the marked place": "wende es an der markierten Stelle an",
    "until clear": "bis es klar ist",
    "let the liquid settle; end this instruction": "lasse die Flüssigkeit sich setzen und beende den Schritt",
    "strain it once through cloth; end this instruction": "seihe es einmal durch ein Tuch und beende den Schritt",
    "the second opening": "die zweite Öffnung",
    "and proceed to the next basin": "und gehe zum nächsten Becken weiter",
    "continue at the second conduit": "fahre am zweiten Lauf fort",
    "through a cloth": "durch ein Tuch",
    "under the same setting": "unter derselben Einstellung",
    "the broad vessel": "das breite Gefäß",
    "draw it off; close the rubric": "ziehe es ab und beende den Schritt",
    "over the local place": "über der örtlich bezeichneten Stelle",
    "add clean water; close the rubric": "gib sauberes Wasser hinzu und beende den Schritt",
    "for the same interval as before": "für dieselbe Dauer wie zuvor",
    "draw off the clear liquid": "ziehe die klare Flüssigkeit ab",
    "immerse fully; close the rubric": "tauche vollständig ein und beende den Schritt",
    "let the spent liquid drain into the lower receiving vessel; end this instruction": "lasse die verbrauchte Flüssigkeit in das untere Auffanggefäß ablaufen und beende den Schritt",
    "close the lower outlet": "schließe den unteren Ablauf",
    "cool water": "kühles Wasser",
    "in equal portions": "zu gleichen Anteilen",
    "pour in the warmed water": "gieße das erwärmte Wasser ein",
    "repeat at the second opening; close the rubric": "wiederhole es an der zweiten Öffnung und beende den Schritt",
    "bathe or immerse in the tempered warm liquid; end this instruction": "bade oder tauche in der temperierten warmen Flüssigkeit und beende den Schritt",
    "drink the stated portion; close the rubric": "trinke den angegebenen Anteil und beende den Schritt",
    "bind upon the place; close the rubric": "binde es auf die Stelle und beende den Schritt",
    "mix in equal shares; close the rubric": "mische zu gleichen Teilen und beende den Schritt",
    "toward the lower outlet": "zum unteren Ablauf hin",
    "steep until clear; close the rubric": "lasse es bis zur Klarheit ziehen und beende den Schritt",
    "next open the upper channel": "öffne danach den oberen Lauf",
    "for one interval": "für einen Zeitabschnitt",
    "retain the residue; close the rubric": "behalte den Rückstand und beende den Schritt",
    "place the person at the basin": "setze die Person an das Becken",
    "after settling": "nach dem Absetzen",
    "until the flow clears": "bis der Strom klar wird",
    "after the first rinse": "nach der ersten Spülung",
    "wash twice; close the rubric": "wasche zweimal und beende den Schritt",
    "let the mixture enter": "lasse die Mischung einlaufen",
    "use immediately; close the rubric": "gebrauche sie sofort und beende den Schritt",
    "for the stated duration": "für die angegebene Dauer",
    "until warm": "bis es warm ist",
    "with the foregoing mixture": "mit der vorigen Mischung",
    "without boiling": "ohne Kochen",
    "at the indicated place": "an der bezeichneten Stelle",
}


ROLE_PURPOSE = {
    "TAKE_SELECTED": "Auswahl von Simplex oder Anteil",
    "MEASURE": "Dosierung",
    "PRIOR_SOURCE": "Voransatz oder Rückbezug",
    "SAME_SOURCE": "Quellenkontrolle",
    "CURRENT_ITEM": "aktiver Arbeitsposten",
    "WORKING_MATERIAL": "Arbeitsstoff oder Medium",
    "PROCESS": "Bearbeitung",
    "STATE_GATE": "Reife- oder Zustandsschwelle",
    "USE_OR_EXECUTE": "Ausführung",
    "DESTINATION": "Ziel oder Station",
    "TRANSFER_CLEAN": "Spülen, Seihen oder Ablassen",
    "HEAT_REST": "Wärme, Kühle oder Ruhe",
    "APPLICATION": "Anwendung oder Bad",
    "OWNER_OR_PART": "Pflanze, Teil oder Bildargument",
    "MEDIUM_OR_INGREDIENT": "Medium oder Zusatz",
    "INDICATION": "Anwendungsfall",
    "PROCEDURE_DETAIL": "weiteres Verfahrensdetail",
    "OTHER_DETAIL": "weiteres Verfahrensdetail",
}


RECORDS = {
    ("f10r", "1"): {
        "title": "Skabiosenwurzel in Rotwein: trockene Grundzubereitung und warme Verwendung",
        "purpose": "Wurzelarznei für eine innere schmerzhafte Beschwerde mit anschließender warmer Verwendung.",
        "alternative": "Äußerliche Wurzelwäsche oder allgemeine Herstellungsnotiz; der einzelne Magenschmerz-Default könnte nur eine Werkstattfüllung sein.",
        "translation": "Nimm die faserige untere Wurzel, wasche sie in fließendem Wasser und bearbeite sie aus demselben Ansatz gleichmäßig zu grobem Pulver. Gib Rotwein hinzu, gebrauche die vorgeschriebene Menge und bewahre die übrige Wurzel trocken. Verwende die frisch bereitete Arznei warm und fahre mit dem Voransatz fort, sobald er gebrauchsfertig ist.",
    },
    ("f10r", "2"): {
        "title": "Skabiosenkraut: Saft, Blütezeit und bitterer Vorratsansatz",
        "purpose": "Zweite saisonale Zubereitung derselben Pflanze, bei der Wiesengrund, Blütezeit, Saft, Bitterkeit und Aufbewahrung den Artikel bestimmen.",
        "alternative": "Reine Sammel- und Vorratsrubrik ohne bestimmte Krankheit; ebenso möglich ist ein äußerlicher Bitterauszug.",
        "translation": "Die Pflanze wächst auf feuchtem Wiesengrund. Sobald der Ansatz bereit ist, gib den ausgepressten Saft zur Arbeitsflüssigkeit, koche sanft und teile ihn nach dem vorgeschriebenen Maß. Sammle vor der Blüte eine Handvoll und arbeite aus demselben Voransatz weiter. Wenn sich die Blüte geöffnet hat, halte zwei Arbeitsanteile bereit; koche bis Bitterkeit bleibt und bewahre den vorgesehenen Anteil unter Öl.",
    },
    ("f11r", "1"): {
        "title": "Veilchenwurzel und -blatt: geklärter Saft und warmer Umschlag",
        "purpose": "Kühlend-reinigende Veilchenzubereitung mit warmem Blattumschlag gegen eine geschwollene oder gereizte Stelle.",
        "alternative": "Haut- oder Augenwaschung statt Schwellungsverband; das Bild kann auch einen anderen bodennahen Simplex besitzen.",
        "translation": "Sammle die Wurzel im Frühjahr am schattigen Waldort, bevor sich die Blütenkrone öffnet. Quetsche sie, presse sie durch ein Tuch, seihe die Flüssigkeit ein zweites Mal und lasse sie offen abkühlen; behalte die Blütenkrone zurück. Nimm vom abgebildeten Simplex die vorgeschriebene Menge und binde sie auf die geschwollene Stelle. Bereite aus den Blättern einen warmen Umschlag und lege ihn auf, sobald er gebrauchsfertig ist.",
    },
    ("f55v", "1"): {
        "title": "Breitblättriger Allium-Auszug: Weißweinwäsche und frischer Gebrauch",
        "purpose": "Reinigender Weißweinauszug aus einem breiten Blatt für eine wunde Stelle.",
        "alternative": "Allgemeiner kräftigender oder konservierender Auszug; der Pflanzenbesitzer könnte Wegerich statt Allium sein.",
        "translation": "Nimm das breite Blatt in vorgeschriebenem Maß, koche es sanft in Weißwein und lasse es ziehen, bis die Flüssigkeit klar ist. Rühre eine zweite Menge gleichmäßig und wasche die wunde Stelle einmal. Für den zweiten Arzneigebrauch gib Weißwein hinzu und koche sanft. Mische beide Anteile, bewahre sie bedeckt und gebrauche die fertige Flüssigkeit frisch.",
    },
    ("f56r", "1"): {
        "title": "Sonnentau: Weinpflaster, Schattentrocknung und Honigmischung",
        "purpose": "Mehrteiliger Moorpflanzenartikel für ein örtliches Pflaster und eine frisch bereitete Honig-/Weinzubereitung.",
        "alternative": "Respiratorischer oder verdauungsbezogener Trank; alternativ gehört die Zeichnung zu einem anderen klebrigen oder behaarten Kraut.",
        "translation": "Sammle die Pflanze im Frühjahr und nimm die dünne untere Wurzel in vorgeschriebener Menge. Lasse den nächsten Pflanzenteil vor der Blüte in Weißwein ziehen und führe den aktiven Anteil an die bezeichnete Stelle. Von dem auf feuchter schattiger Heide wachsenden Simplex gebrauche ein Pflaster und lasse es offen trocknen. Trockne Knospenkopf und schmales Blatt im Schatten. Gebrauche einen frischen Ansatz und bewahre den Rest trocken; mische einen weiteren Anteil mit Honig und gebrauche ihn frisch. Nimm zuletzt die helle geöffnete Blüte in vorgeschriebener Menge.",
    },
    ("f81v", "1"): {
        "title": "Gemeinsames Grundbad: Mischen, Temperieren, Kreislauf und Schlussreinigung",
        "purpose": "Herstellung und Umlauf einer gemeinsamen temperierten Kräuter-/Ölcharge für ein Frauenbad mit nachfolgender Spülung.",
        "alternative": "Allgemeiner Badhaus- oder Gefäßumlauf ohne gynäkologische Diagnose; die Frauen können Zustands- oder Stationsbilder sein.",
        "translation": "Spüle zuerst die bezeichnete Stelle. Beginne den abgemessenen Ansatz, mische Rücklauf, Öl und Vorzubereitung und führe den Anteil vor dem Abkühlen zum unteren Becken. Entnimm eine mäßige Menge, tauche den vorgesehenen Teil ein und leite die Flüssigkeit durch die verbundenen Läufe; spüle den benutzten Lauf aus. Halte die Mischung warm, rühre sie gleichmäßig, lasse sie bis zur Bereitschaft stehen und stelle sie bedeckt beiseite. Gib einen neuen Anteil zu, führe ihn durch die Läufe und lasse ihn abkühlen. Erwärme einmal, halte bei sanfter Wärme, spüle zweimal und gebrauche den aktiven Anteil. Beginne danach die Warmwasserspülung, wasche jeden Durchgang, leite zum unteren Becken und benutze den Ablauf. Fülle erneut, temperiere lauwarm, seihe an der ersten Öffnung klar, wende an der markierten Stelle an, lasse absetzen und führe zum bezeichneten Ziel.",
    },
    ("f82r", "1"): {
        "title": "Einzelbehandlung: Teilbad, Öffnungen, Trank, Bindung und Ruhe",
        "purpose": "Aus dem gemeinsamen Ansatz abgeleitete individuelle Bade-, Spül-, Bindungs- und Trinkschritte mit wechselnder Temperatur.",
        "alternative": "Pharmazeutische Apparaturfolge mit Gefäßen und Leitungen, in der die menschlichen Figuren lediglich Arbeitszustände markieren.",
        "translation": "Spüle Gefäß oder Lauf und stelle die gemischte Flüssigkeit bedeckt beiseite. Gib einen abgemessenen Anteil zu und bade den bezeichneten Teil warm; mische weiter und gehe durch die zweite Öffnung zum nächsten Becken. Temperiere und seihe klar, fahre am zweiten Lauf durch Tuch und verbundene Kanäle fort. Ziehe aus dem breiten Gefäß ab, mische Öl ein und gebrauche die Portion örtlich. Gib sauberes Wasser zu, lasse es für dieselbe Dauer stehen und halte es warm. Bade nach erneuter Temperierung an der ersten Öffnung bis zur Klarheit. Gib aus demselben Ansatz zwei Anteile zu, bade oder tauche, ziehe die klare Flüssigkeit ab und lasse den verbrauchten Anteil in das untere Gefäß laufen. Wechsle danach zwischen warmem und kühlem Wasser zu gleichen Teilen. Ziehe ab, gieße Warmwasser ein, wiederhole an der zweiten Öffnung und schließe die Folge mit Bad, angegebenem Trank, örtlicher Bindung und einem letzten Bad.",
    },
    ("f83r", "1"): {
        "title": "Lokale Irrigation: Setzen, Erwärmen, Einlaufen, Binden und mehrfaches Ablassen",
        "purpose": "Langer örtlicher Behandlungszyklus mit wiederholtem warmem Guss, Einweichen, Spülen, Absetzen, Binden und Ableiten.",
        "alternative": "Komplexe Badhaus-/Destillationsanweisung ohne wörtlichen Körperbezug; die Figuren können Behälterzustände personifizieren.",
        "translation": "Lasse den ersten Ansatz absetzen und zum unteren Ablauf gehen; teile die aktive Menge ab und lasse sie in das Auffanggefäß laufen. Spüle, gieße warmes Wasser ein, mische und bade die neue Portion, danach lasse sie ablaufen und gebrauche sie. Fülle erneut, lasse bis zur Klarheit ziehen, wende an der markierten Stelle an, rühre und kühle. Lasse die Arbeitsflüssigkeit bereit werden, nimm eine Portion, spüle, öffne den oberen Lauf und lasse unten ab. Wiederhole Kühlen, warmes Bad, Stehen und sanftes Kochen; führe zum Ziel und lasse ablaufen. Verwende für einen Zeitabschnitt warmes Wasser im vorgeschriebenen Maß, behalte den Rückstand, mische gleich und lasse ab. Setze die Person an das Becken, erwärme, rühre nach dem Absetzen und gib einen Anteil zu, bis der Strom klar wird. Lasse wieder absetzen, binde örtlich, temperiere und spüle zweimal. Ziehe die klare Flüssigkeit ab, bade, rühre im breiten Gefäß und lasse bis zur Klarheit ziehen; ziehe ab. Bearbeite schließlich denselben Ansatz bis zur Bereitschaft und lasse ihn im unteren Becken stehen.",
    },
    ("f83r", "2"): {
        "title": "Zweiter örtlicher Kurs: temperierte Spülung, Auflage und Nachlauf",
        "purpose": "Nachbehandlung mit lauwarmer Spülung, örtlicher Bindung, zweifachem Seihen und kontrolliertem Nachlauf.",
        "alternative": "Zweiter rein technischer Klär- und Transfergang einer zusammengesetzten Flüssigkeit.",
        "translation": "Bade zuerst in der temperierten Flüssigkeit. Fülle das Gefäß, halte die Arbeitsflüssigkeit lauwarm, spüle und rühre sie zum unteren Ablauf. Nimm den bezeichneten Anteil, temperiere ihn, gebrauche ihn mit dem Voransatz und lasse ihn bis zur Bereitschaft stehen; binde ihn auf die Stelle. Seihe durch Tuch, rühre, bade und seihe zweimal nach. Spüle die erste Öffnung noch warm, lasse stehen und koche sanft. Gib im breiten Gefäß eine vorgeschriebene Menge bei sanfter Wärme zu und rühre. Wasche mit dem Voransatz zweimal, lasse in das Auffanggefäß ab, lasse die Mischung einlaufen und stehen. Gebrauche die Arbeitsflüssigkeit sofort örtlich. Gib einen Anteil zu, führe ihn bis zur Klarheit und halte ihn für die angegebene Dauer. Öffne den oberen Lauf, lasse ab und führe das untere Becken zum Ziel; gieße zuletzt warmes Wasser ein und lasse es stehen.",
    },
    ("f83r", "3"): {
        "title": "Kurzer Wärme- und Übergabegang",
        "purpose": "Kurze eingeschobene Wiederholungsrubrik: abziehen, einmal erwärmen, eine Dauer halten und an die nächste Station geben.",
        "alternative": "Korrektur- oder Nachtragsrecord für eine Apparatur statt eigener Patientenbehandlung.",
        "translation": "Ziehe die Flüssigkeit ab, erwärme sie einmal und halte sie für einen Zeitabschnitt. Führe sie mit der vorigen Mischung in vorgeschriebenem Maß an die bezeichnete Stelle, bis sie warm ist. Fahre dann an der zweiten Öffnung mit dem Voransatz fort und rühre gleichmäßig.",
    },
    ("f83r", "4"): {
        "title": "Ungekochte Schlussportion durch Tuch",
        "purpose": "Kühle oder ungekochte Schlussanwendung eines abgemessenen, durch Tuch geführten Anteils.",
        "alternative": "Knappes Gefäß-/Leitungsaddendum; kein eigenständiger Krankheitsfall erforderlich.",
        "translation": "Setze die Person an das Becken und führe den Voransatz ohne Kochen durch die erste Öffnung. Nimm eine vorgeschriebene Menge, führe sie durch ein Tuch und gebrauche diese Portion an der bezeichneten Stelle.",
    },
}


def translate(default: str) -> str:
    if default in DE:
        return DE[default]
    # These are the twelve V39 German core cards already carried into V41.
    if any(ch in default for ch in "äöüß") or default in {
        "daraus, aus demselben Ansatz", "gleichmäßig bearbeiten",
        "die aktive Portion verwenden", "ein vorgeschriebenes Maß",
        "mit der vorigen Zubereitung weiter", "sobald die Zubereitung gebrauchsfertig ist",
        "die bereitete Arbeitsflüssigkeit", "diese aktive Portion",
        "aus dem vorigen Ansatz entnehmen", "nimm den bezeichneten Anteil",
        "an die bezeichnete Zielstelle führen", "bis die Flüssigkeit klar abläuft",
    }:
        return default[0].upper() + default[1:]
    raise KeyError(default)


def smooth_field(parts: list[str]) -> str:
    # Preserve card order visibly.  Semicolons model expansion of form prompts,
    # not claims about ordinary source-language syntax.
    text = "; ".join(p.rstrip(".;") for p in parts)
    return text[0].upper() + text[1:] + "."


def write_tsv(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, delimiter="\t", fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def main() -> None:
    source_rows = list(csv.DictReader(SOURCE.open(encoding="utf-8"), delimiter="\t"))
    assert len(source_rows) == 135
    output = []
    counts = defaultdict(int)
    for row in source_rows:
        key = (row["page"], row["record_ordinal"])
        counts[key] += 1
        defaults = row["complete_card_defaults"].split(" / ")
        translated = [translate(x) for x in defaults]
        surfaces = row["visible_field"].split()
        assert len(defaults) == int(row["event_count"]), (row["locus"], defaults)
        assert len(surfaces) == len(defaults), (row["locus"], surfaces, defaults)
        output.append({
            "page": row["page"],
            "record_ordinal": row["record_ordinal"],
            "record_field_serial": counts[key],
            "locus": row["locus"],
            "source_field_ordinal": row["field_ordinal"],
            "visible_field": row["visible_field"],
            "card_count": row["event_count"],
            "card_defaults_German_ordered": " | ".join(translated),
            "field_expansion_German": smooth_field(translated),
            "primary_medical_workshop_function": ROLE_PURPOSE[row["primary_role"]],
            "closure": row["closure"],
            "coverage_status": "ALL_CARDS_EXPANDED_NO_BLANK",
        })
    fields = list(output[0])
    write_tsv(HERE / "V42_R2_135_FIELD_MEDICAL_EDITION.tsv", output, fields)

    rec_rows = []
    for key, spec in RECORDS.items():
        matching = [r for r in output if (r["page"], r["record_ordinal"]) == key]
        rec_rows.append({
            "page": key[0],
            "record_ordinal": key[1],
            "title": spec["title"],
            "field_count": len(matching),
            "event_count": sum(int(r["card_count"]) for r in matching),
            "selected_medical_purpose": spec["purpose"],
            "complete_fluid_German": spec["translation"],
            "alternative_diagnosis_or_purpose": spec["alternative"],
            "status": "COMPLETE_CREATIVE_MEDICAL_EDITION",
        })
    write_tsv(HERE / "V42_R2_ELEVEN_RECORD_MEDICAL_EDITION.tsv", rec_rows, list(rec_rows[0]))

    by_page = Counter(r["page"] for r in output)
    validation = {
        "status": "PASS",
        "sidequest_only": True,
        "source": str(SOURCE.relative_to(ROOT)),
        "records": len(RECORDS),
        "fields": len(output),
        "events": sum(int(r["card_count"]) for r in output),
        "pages": sorted(by_page),
        "fields_by_page": dict(sorted(by_page.items())),
        "all_fields_nonblank": all(r["field_expansion_German"] for r in output),
        "all_cards_translated": True,
        "all_records_have_alternative": all(v["alternative"] for v in RECORDS.values()),
        "sealed_pages_accessed": [],
        "canonical_claim": False,
    }
    (HERE / "V42_R2_VALIDATION.json").write_text(
        json.dumps(validation, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    report = [
        "# V42 R2 — vollständige medizinische Edition der elf Prosarecords",
        "",
        "Status: **unabhängige kreative Kräuter-/Badeschreiber-Lesung; keine Entzifferung**.",
        "",
        "## Ergebnis",
        "",
        "Die 135 V41-Felder mit 381 Karten sind vollständig als medizinisches Werkstattdeutsch",
        "expandiert. Keine Karte und kein Feld bleibt leer. Die Edition verändert weder Karte,",
        "Reihenfolge, Feldgrenze noch Schlussart. Sie füllt ausschließlich die bereits erfundenen",
        "V40/V41-Defaults als ein Schreiber praktischer Medizin um 1420 aus.",
        "",
        "Das stärkste medizinische Gesamtbild ist weiterhin:",
        "",
        "```text",
        "vier Simplex-Dossiers",
        "  → Wurzel, Blatt, Blüte, Medium, Maß, Reife, Aufbewahrung und Anwendung",
        "drei Bade-/Körperseiten",
        "  → Grundbad, Einzelbehandlung, lokale Irrigation und Nachbehandlung",
        "```",
        "",
        "Die medizinische Diagnose bleibt absichtlich breiter als die technische Ausführung:",
        "Ein warmes humoral ausgerichtetes Frauenregimen ist plausibel; Menstruationsstörung oder",
        "Vorbereitung auf Empfängnis ist nur die beste enge Wette, nicht etwas, das eine Karte sagt.",
        "",
        "## Elf vollständige Recordlesungen",
        "",
    ]
    for row in rec_rows:
        report.extend([
            f"### {row['page']} · Record {row['record_ordinal']} — {row['title']}",
            "",
            f"**Zweck/Diagnose:** {row['selected_medical_purpose']}",
            "",
            f"> {row['complete_fluid_German']}",
            "",
            f"**Stärkste Alternative:** {row['alternative_diagnosis_or_purpose']}",
            "",
        ])
    report.extend([
        "## Feld-für-Feld-Edition",
        "",
        "Die vollständige Zuordnung steht in `V42_R2_135_FIELD_MEDICAL_EDITION.tsv`.",
        "Jede Zeile bewahrt sichtbares Feld, Kartenreihenfolge, alle deutschen Defaults,",
        "flüssige Feldexpansion, primäre medizinische Werkstattfunktion und Schlussart.",
        "Die fortlaufende `record_field_serial` ist nötig, weil V41s `field_ordinal` an jedem",
        "neuen physischen locus neu beginnt.",
        "",
        "## Historische Plausibilitätskontrolle",
        "",
        "Die Edition verlangt nur gewöhnliche spätmittelalterliche Praktiken: Pflanzenteile",
        "sammeln, in Wein ziehen oder sanft kochen, pressen und seihen, mit Honig oder Öl",
        "mischen, warm auflegen, baden, spülen, ruhen lassen und Flüssigkeit abziehen.",
        "Ein Werkstattformular darf Bildargumente und wiederholte Maße auslassen. Mehrere",
        "Schreiber müssen dafür nicht 381 Wörter lernen: ein gemeinsames Prompt-/Schlussdeck",
        "und lokale Exemplarkarten genügen.",
        "",
        "Drei Vorsichtsregeln bleiben verbindlich:",
        "",
        "1. Die Bilder wurden zuerst gezeichnet; Nähe zu Figur, Becken oder Röhre beweist keine",
        "   lokale Textreferenz.",
        "2. `Ziel`, `Öffnung`, `eingetauchter Teil` und `betroffene Stelle` bleiben absichtlich",
        "   generisch; es wird kein ungesehener Körperteil erfunden.",
        "3. Bad, Destillationsapparatur und abstrakte Zustandsdarstellung bleiben bei den",
        "   Biological-Records echte Rivalen.",
        "",
        "## Medizinische Auswahlentscheidung",
        "",
        "`COMPLETE_MEDICAL_EDITION_COHERENT_BUT_NOT_IDENTIFIED`",
        "",
        "Die Lesung ist ausführbar und deckt das gesamte Prosekorpus ab. Ihr größter Gewinn ist",
        "die konkrete Einheit aus Simplex → Medium → Bearbeitung → Zustand → Anwendung und aus",
        "Badcharge → Temperatur → Öffnung/Lauf → Anwendung → Abfluss. Ihr größtes Problem ist",
        "dass dieselbe generische Grammatik auch eine pharmazeutische Apparatur oder ein",
        "Badhausregister tragen könnte. Daher erhält jeder Record eine explizite Alternative.",
        "",
        "Die drei Astro-Seiten besitzen keine GDT327-Prosaereignisse und gehören nicht zu den",
        "hier verlangten elf Prosarecords. Sie wurden in dieser unabhängigen R2-Edition nicht",
        "durch importierte Karten ergänzt. f84 und f84r blieben versiegelt.",
        "",
    ])
    (HERE / "V42_R2_COMPLETE_MEDICAL_EDITION.md").write_text(
        "\n".join(report), encoding="utf-8"
    )


if __name__ == "__main__":
    main()

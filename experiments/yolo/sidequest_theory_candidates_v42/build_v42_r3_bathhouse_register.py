#!/usr/bin/env python3
"""Build the V42 R3 non-medical bathhouse-register counter-reading.

This is a deliberately speculative sidequest artifact.  It re-expands the
already frozen V40/V41 cards and fields; it does not inspect any new page.
"""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
FIELDS = ROOT / "experiments/yolo/sidequest_theory_candidates_v41/V41_135_FIELD_WORKSHEET.tsv"


GERMAN = {
    "a moderate quantity": "eine mäßige Menge",
    "add clean water; close the rubric": "gib klares Wasser zu; schließe diesen Arbeitsgang",
    "add one measured portion to the vessel": "gib eine gemessene Portion in das Gefäß",
    "add red wine": "gib Rotwein als Auszugsmittel zu",
    "add the expressed juice": "gib den ausgepressten Pflanzensaft zu",
    "add white wine": "gib Weißwein als Auszugsmittel zu",
    "after settling": "nach dem Absetzen",
    "after the first rinse": "nach der ersten Spülung",
    "an die bezeichnete Zielstelle führen": "führe den Arbeitsstrom zur bezeichneten Station",
    "and let it cool": "und lasse ihn abkühlen",
    "and proceed to the next basin": "und gehe zum nächsten Becken weiter",
    "apply at the marked place": "bringe den Zusatz an der bezeichneten Badestelle ein",
    "apply it while warm": "bringe ihn warm in den vorgesehenen Badelauf ein",
    "at the indicated place": "an der bezeichneten Arbeitsstation",
    "aus dem vorigen Ansatz entnehmen": "entnimm es aus dem vorigen Ansatz",
    "bathe or immerse in the tempered warm liquid; end this instruction": "bade oder tauche im temperierten warmen Wasser; beende die Zelle",
    "before it cools": "bevor der Ansatz erkaltet",
    "before the flowering crown opens": "bevor sich die Blütenkrone öffnet",
    "begin the next measured entry": "beginne den nächsten abgemessenen Arbeitsposten",
    "begin the rinsing": "beginne die Spülung",
    "bind it upon a swollen place": "binde den gefüllten Kräuterbeutel über den bezeichneten Einlass",
    "bind upon the place; close the rubric": "binde den Kräuterbeutel an der bezeichneten Station fest; schließe die Zelle",
    "bis die Flüssigkeit klar abläuft": "bearbeite weiter, bis die Flüssigkeit klar abläuft",
    "boil gently; close the rubric": "siede sanft; schließe die Zelle",
    "boil it gently": "siede es sanft",
    "boil the broad leaf gently": "siede das breite Blatt sanft aus",
    "close the lower outlet": "schließe den unteren Auslass",
    "continue at the second conduit": "setze am zweiten Wasserlauf fort",
    "cool water": "kaltes Wasser",
    "daraus, aus demselben Ansatz": "daraus, aus demselben Ansatz",
    "die aktive Portion verwenden": "verwende die aktive Portion im laufenden Arbeitsgang",
    "die bereitete Arbeitsflüssigkeit": "die bereitete Arbeitsflüssigkeit",
    "diese aktive Portion": "dieser aktive Arbeitsposten",
    "draw it off; close the rubric": "ziehe die Flüssigkeit ab; schließe die Zelle",
    "draw off the clear liquid": "ziehe die klare Flüssigkeit ab",
    "drink it for pain of the stomach": "prüfe eine kleine Probe auf Stärke und Verträglichkeit",
    "drink the stated portion; close the rubric": "schöpfe die vorgeschriebene Prüfportion ab; schließe die Zelle",
    "dry it in shade": "trockne es im Schatten",
    "ein vorgeschriebenes Maß": "ein vorgeschriebenes Maß",
    "for its second medicinal use": "für den zweiten Badehausgebrauch",
    "for one interval": "für einen Arbeitszeitraum",
    "for the same interval as before": "für denselben Zeitraum wie zuvor",
    "for the stated duration": "für die vorgeschriebene Dauer",
    "from shaded woodland": "aus schattigem Wald",
    "gather the plant in spring": "sammle die Pflanze im Frühjahr",
    "gather the root in spring": "sammle die Wurzel im Frühjahr",
    "gathered before flowering": "vor der Blüte gesammelt",
    "gleichmäßig bearbeiten": "bearbeite den Ansatz gleichmäßig",
    "heat it once; end this instruction": "erhitze einmal; beende die Zelle",
    "immerse fully; close the rubric": "tauche vollständig ein; schließe die Zelle",
    "in equal portions": "zu gleichen Teilen",
    "in white wine": "in Weißwein",
    "it grows in damp meadow ground": "sie wächst auf feuchtem Wiesengrund",
    "its small seed or bud-head": "ihren kleinen Samen- oder Knospenkopf",
    "keep it in a covered jar": "bewahre es in einem bedeckten Gefäß",
    "keep it warm; close the rubric": "halte es warm; schließe die Zelle",
    "keep the remainder dry in shade": "halte den Rest trocken im Schatten",
    "keep the remaining root dry": "bewahre die übrige Wurzel trocken",
    "lay it on while warm": "lege den Kräuterbeutel warm an die Arbeitsstation",
    "leave the plaster uncovered until dry": "lasse den Kräuterpack offen trocknen",
    "leave the strained liquor uncovered to cool": "lasse die geseihte Flüssigkeit offen abkühlen",
    "let it cool; close the rubric": "lasse es abkühlen; schließe die Zelle",
    "let it stand until ready; end this instruction": "lasse es bis zur Arbeitsbereitschaft stehen; beende die Zelle",
    "let the liquid settle; end this instruction": "lasse die Flüssigkeit absetzen; beende die Zelle",
    "let the mixture enter": "lasse die Mischung einlaufen",
    "let the spent liquid drain into the lower receiving vessel; end this instruction": "lasse die verbrauchte Flüssigkeit in das untere Auffanggefäß ab; beende die Zelle",
    "make a warm poultice from its leaves": "fülle aus den Blättern einen warmen Kräuterbeutel",
    "mit der vorigen Zubereitung weiter": "arbeite mit dem vorigen Ansatz weiter",
    "mix in equal shares; close the rubric": "mische zu gleichen Teilen; schließe die Zelle",
    "mix it with honey": "mische es mit Honig als Bindemittel",
    "mix the two portions together": "mische beide Portionen zusammen",
    "next open the upper channel": "öffne als Nächstes den oberen Wasserlauf",
    "nimm den bezeichneten Anteil": "nimm den bezeichneten Anteil",
    "of this pictured simple": "von diesem abgebildeten Badezusatz",
    "one handful": "eine Handvoll",
    "one measured portion": "eine gemessene Portion",
    "over a gentle heat": "über sanfter Wärme",
    "over the local place": "über der bezeichneten Badestelle",
    "place the person at the basin": "setze den Badenden an das Becken",
    "pour in the warmed water": "gieße erwärmtes Wasser ein",
    "preserve that portion under oil": "bewahre jenen Anteil unter Öl",
    "press the bruised root through cloth": "presse die gequetschte Wurzel durch ein Tuch",
    "reduce it to a coarse powder": "zerstoße sie grob",
    "repeat at the second opening; close the rubric": "wiederhole es an der zweiten Öffnung; schließe die Zelle",
    "reserve the flowering crown": "behalte die Blütenkrone als Vorrat zurück",
    "retain the residue; close the rubric": "behalte den Rückstand; schließe die Zelle",
    "rinse the indicated place once; end this instruction": "spüle die bezeichnete Arbeitsstelle einmal; beende die Zelle",
    "set the mixed liquid aside in a covered receiving vessel; end this instruction": "stelle die gemischte Flüssigkeit im bedeckten Auffanggefäß zurück; beende die Zelle",
    "sobald die Zubereitung gebrauchsfertig ist": "sobald der Ansatz arbeitsbereit ist",
    "steep it in white wine": "lasse es in Weißwein ausziehen",
    "steep it until the liquor is clear": "lasse es ausziehen, bis die Flüssigkeit klar ist",
    "steep until clear; close the rubric": "lasse es bis zur Klärung ausziehen; schließe die Zelle",
    "stir until evenly mixed": "rühre bis zur gleichmäßigen Mischung",
    "strain it clear; close the rubric": "seihe es klar; schließe die Zelle",
    "strain it once through cloth; end this instruction": "seihe es einmal durch Tuch; beende die Zelle",
    "strain the liquor a second time": "seihe die Flüssigkeit ein zweites Mal",
    "take the fibrous lower root": "nimm die faserige untere Wurzel",
    "temper the working liquid and keep it lukewarm": "tempere die Arbeitsflüssigkeit und halte sie lauwarm",
    "the affected place": "die zu bedienende Badestelle",
    "the broad vessel": "das breite Gefäß",
    "the dried narrow leaf": "das getrocknete schmale Blatt",
    "the first opening": "die erste Öffnung",
    "the immersed part": "der eingetauchte Teil",
    "the lower basin": "das untere Becken",
    "the pale opened flower": "die blasse geöffnete Blüte",
    "the prepared oil": "das bereitete Öl",
    "the returning flow": "der Rücklauf",
    "the second opening": "die zweite Öffnung",
    "the thin lower root": "die dünne untere Wurzel",
    "then fill the vessel": "fülle dann das Gefäß",
    "then take the following ingredient or plant part": "nimm dann den folgenden Zusatz oder Pflanzenteil",
    "then use the lower outlet": "benutze dann den unteren Auslass",
    "through a cloth": "durch ein Tuch",
    "through the connected channels": "durch die verbundenen Wasserläufe",
    "toward the lower outlet": "zum unteren Auslass",
    "under the same setting": "bei derselben Anlageneinstellung",
    "until a bitter taste remains": "bis eine bittere Prüfqualität bleibt",
    "until clear": "bis zur Klarheit",
    "until the flow clears": "bis der Wasserlauf klar wird",
    "until warm": "bis es warm ist",
    "use immediately; close the rubric": "verwende den Ansatz sofort; schließe die Zelle",
    "use it while freshly mixed": "verwende es frisch gemischt",
    "use the finished liquor fresh": "verwende die fertige Flüssigkeit frisch",
    "use the freshly prepared remedy": "verwende den frisch bereiteten Badezusatz",
    "warm water": "warmes Wasser",
    "wash it in running water": "wasche sie in fließendem Wasser",
    "wash once; close the rubric": "spüle einmal; schließe die Zelle",
    "wash once; close this pass": "spüle einmal; schließe diesen Durchlauf",
    "wash the sore place once": "spüle die zu reinigende Stelle einmal",
    "wash the used vessel or channel through once; end this instruction": "spüle das gebrauchte Gefäß oder den Wasserlauf einmal durch; beende die Zelle",
    "wash twice; close the rubric": "spüle zweimal; schließe die Zelle",
    "when its flower has opened": "wenn sich ihre Blüte geöffnet hat",
    "which grows on damp shaded heath": "die auf feuchter schattiger Heide wächst",
    "while still warm": "solange es noch warm ist",
    "with the foregoing mixture": "mit der vorigen Mischung",
    "without boiling": "ohne Sieden",
}


ROLE = {
    "SAME_SOURCE": "HERKUNFT DES ANSATZES",
    "PROCESS": "BEARBEITUNGSWEISE",
    "USE_OR_EXECUTE": "AUSZUFÜHRENDER ARBEITSGANG",
    "MEASURE": "MENGE ODER MASS",
    "TRANSFER_CLEAN": "WASSERWEG, SPÜLUNG ODER ABLASS",
    "APPLICATION": "EINSATZ AM BECKEN ODER AN DER STATION",
    "OWNER_OR_PART": "ROHSTOFF ODER ANLAGENTEIL",
    "MEDIUM_OR_INGREDIENT": "ARBEITSFLÜSSIGKEIT ODER ZUSATZ",
    "INDICATION": "VERWENDUNGSZWECK ODER QUALITÄTSPRÜFUNG",
    "PRIOR_SOURCE": "VORANSATZ ODER RÜCKLAUF",
    "STATE_GATE": "REIFE- ODER ENDZUSTAND",
    "HEAT_REST": "WÄRME, KÜHLUNG ODER RUHE",
    "WORKING_MATERIAL": "AKTUELLE ARBEITSFLÜSSIGKEIT",
    "CURRENT_ITEM": "AKTIVER ARBEITSPOSTEN",
    "TAKE_SELECTED": "AUSWAHL DES BEZEICHNETEN ANTEILS",
    "DESTINATION": "ZIELBECKEN ODER ARBEITSSTATION",
    "PROCEDURE_DETAIL": "ANLAGEN- ODER DURCHLAUFDETAIL",
}


RECORDS = {
    ("f10r", "1"): (
        "ROTWURZEL-BADANSATZ",
        "Nimm die faserige untere Wurzel, wasche sie in fließendem Wasser, zerstoße sie grob und setze sie mit Rotwein an. Prüfe eine kleine Probe auf Stärke und Verträglichkeit; verwende die vorgeschriebene Portion frisch und warm im Badelauf und bewahre die übrige Wurzel trocken für den nächsten Ansatz."
    ),
    ("f10r", "2"): (
        "WIESENKRAUT-SAFT UND VORRAT",
        "Verarbeite das auf feuchtem Wiesengrund gewachsene Kraut, sobald der Ansatz bereit ist: gib den ausgepressten Saft in die Arbeitsflüssigkeit, siede sanft und teile gemessene Posten ab. Sammle vor der Blüte eine Handvoll für den Voransatz; nach dem Öffnen der Blüte arbeite bis zur bitteren Prüfqualität weiter und bewahre einen Anteil unter Öl."
    ),
    ("f11r", "1"): (
        "FRÜHJAHRSWURZEL UND KRÄUTERBEUTEL",
        "Sammle die Wurzel im Frühjahr im schattigen Wald vor dem Öffnen der Blütenkrone. Presse sie durch Tuch, seihe zweimal und lasse die Flüssigkeit offen abkühlen; behalte die Blütenkrone zurück. Fülle den abgebildeten Zusatz in einen Kräuterbeutel, binde ihn über den bezeichneten Einlass und lege ihn arbeitsbereit warm an."
    ),
    ("f55v", "1"): (
        "BREITBLATT-WEINEXTRAKT",
        "Siede die vorgeschriebene Menge des breiten Blatts in Weißwein und lasse sie bis zur Klarheit ausziehen. Rühre einen zweiten gemessenen Posten gleichmäßig und spüle damit die zu reinigende Stelle. Bereite für den zweiten Gebrauch einen weiteren warmen Weißweinansatz; vereinige beide Teile, bewahre sie bedeckt und verwende die fertige Flüssigkeit frisch."
    ),
    ("f56r", "1"): (
        "SIEBENTEILIGER BADEZUSATZ-VORRAT",
        "Sammle die Pflanze im Frühjahr. Nimm die dünne untere Wurzel in vorgeschriebenem Maß, lasse sie vor der Blüte in Weißwein ausziehen und führe die Portion zur bezeichneten Badestation. Trockne den Kräuterpack, den Samen- oder Knospenkopf und das schmale Blatt im Schatten. Prüfe den frischen Ansatz, bewahre den Rest trocken, mische einen weiteren Teil mit Honig als Bindemittel und bemesse zuletzt die blasse offene Blüte."
    ),
    ("f81v", "1"): (
        "ERSTER WASSERLAUF UND RÜCKLAUF",
        "Spüle zuerst die bezeichnete Arbeitsstelle. Setze aus Rücklauf und Voransatz gemessene Portionen im unteren Becken an, gib bereitetes Öl zu und führe sie durch die verbundenen Wasserläufe. Spüle Gefäße und Leitungen, halte den Ansatz warm, rühre, lasse ihn stehen und stelle ihn bedeckt zurück. Fülle nach, erhitze einmal, kühle, wiederhole die Spülung und leite die geklärte Flüssigkeit über die erste Öffnung zur bezeichneten Station."
    ),
    ("f82r", "1"): (
        "VOLLSTÄNDIGER BADE- UND SPÜLZYKLUS",
        "Spüle Gefäß und Wasserlauf, stelle die Mischung bedeckt zurück und gib eine gemessene Portion zu. Bade im temperierten Wasser; wechsle danach über zweite Öffnung, Tuch und verbundenen Lauf zum nächsten Becken. Ziehe über das breite Gefäß ab, gib Öl und klares Wasser zu, halte den Ansatz warm und lasse ihn ruhen. Führe weitere Portionen ein, tauche vollständig, lasse unten ab und schalte anschließend die Öffnungen für Spülung, Warmwasser, Bad, Prüfportion und festgebundenen Kräuterbeutel der Reihe nach."
    ),
    ("f83r", "1"): (
        "LANGER BECKEN-, KLÄR- UND ABLASSLAUF",
        "Lasse die Flüssigkeit absetzen, führe sie zum unteren Auslass und tauche die gemessene Portion vollständig ein; lasse den verbrauchten Anteil in das Auffanggefäß ab. Beginne mit Warmwasser und Voransatz neu, spüle, mische, temperiere, kühle, siede und kläre in den bezeichneten Gefäßen. Öffne und schließe obere und untere Läufe, führe die Arbeitsflüssigkeit zu den markierten Stationen, behalte den Rückstand und wiederhole Bad, Spülung, Filterung und Ablass bis zum klaren Endlauf."
    ),
    ("f83r", "2"): (
        "ZWEITER BECKEN- UND FILTERLAUF",
        "Bade im temperierten Wasser, fülle das Gefäß und spüle die Arbeitsstelle. Rühre zum unteren Auslass, nimm den bezeichneten Anteil, halte ihn lauwarm und binde den Kräuterbeutel an der Station fest. Seihe den Ansatz zweimal durch Tuch, benutze die vorgeschriebene warme Menge an der ersten Öffnung, siede sanft und spüle das breite Gefäß zweimal. Lasse unten ab, führe einen neuen Posten sofort ein, öffne den oberen Lauf und fülle Warmwasser nach."
    ),
    ("f83r", "3"): (
        "KURZER WIEDERHOLUNGSLAUF",
        "Ziehe die Flüssigkeit ab, erhitze sie einmal und halte einen Arbeitszeitraum ein. Führe sie dann mit der vorigen Mischung in vorgeschriebenem Maß zur bezeichneten Station und rühre am zweiten Wasserlauf gleichmäßig weiter."
    ),
    ("f83r", "4"): (
        "UNGESOTTENER DIREKTLAUF",
        "Setze den Badenden ohne Sieden an das Becken und führe den Voransatz über die erste Öffnung. Nimm die vorgeschriebene aktive Portion, leite sie durch Tuch und bringe sie an der bezeichneten Arbeitsstation ein."
    ),
}


def read_tsv(path: Path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict], fields: list[str]):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    source = read_tsv(FIELDS)
    seen_record_fields = defaultdict(int)
    out = []
    missing = set()
    for row in source:
        key = (row["page"], row["record_ordinal"])
        seen_record_fields[key] += 1
        defaults = row["complete_card_defaults"].split(" / ")
        for default in defaults:
            if default not in GERMAN:
                missing.add(default)
        phrases = [GERMAN.get(default, f"[UNÜBERSETZT: {default}]") for default in defaults]
        primary = ROLE[row["primary_role"]]
        secondary = "; ".join(ROLE[x] for x in row["secondary_roles"].split("+") if x)
        close = "abgeschlossene Arbeitszelle" if row["closure"] != "OPEN_FIELD_END" else "offene Fortsetzung"
        expansion = f"{primary}: " + "; ".join(phrases) + f". ({close})"
        out.append({
            "page": row["page"],
            "record_ordinal": row["record_ordinal"],
            "field_serial_in_record": seen_record_fields[key],
            "locus": row["locus"],
            "visible_field": row["visible_field"],
            "event_count": row["event_count"],
            "technical_primary_function": primary,
            "technical_secondary_functions": secondary,
            "technical_card_expansion_German": " | ".join(phrases),
            "complete_field_expansion_German": expansion,
            "closure": row["closure"],
            "coverage_status": "COMPLETE_NONMEDICAL_DEFAULT",
        })

    record_rows = []
    for key, count in seen_record_fields.items():
        title, text = RECORDS[key]
        record_rows.append({
            "page": key[0],
            "record_ordinal": key[1],
            "technical_register_title": title,
            "field_count": count,
            "complete_German_expansion": text,
            "interpretive_status": "SPECULATIVE_COMPLETE_NONMEDICAL_RIVAL",
        })

    write_tsv(
        OUT / "V42_R3_135_FIELD_BATHHOUSE_EDITION.tsv",
        out,
        list(out[0]),
    )
    write_tsv(
        OUT / "V42_R3_ELEVEN_RECORD_BATHHOUSE_EDITION.tsv",
        record_rows,
        list(record_rows[0]),
    )

    counts = Counter(row["page"] for row in out)
    validation = {
        "status": "PASS" if not missing and len(out) == 135 and len(record_rows) == 11 else "FAIL",
        "scope": "V42_R3_NONMEDICAL_BATHHOUSE_REGISTER",
        "source_fields": len(source),
        "expanded_fields": len(out),
        "expanded_records": len(record_rows),
        "visible_events": sum(int(row["event_count"]) for row in out),
        "page_field_counts": dict(counts),
        "unique_card_defaults_translated": len({x for row in source for x in row["complete_card_defaults"].split(" / ")}),
        "missing_card_defaults": sorted(missing),
        "blank_expansions": sum(not row["complete_field_expansion_German"] for row in out),
        "new_pages_opened": 0,
        "f84_accessed": False,
        "f84r_accessed": False,
        "scientific_claim": False,
    }
    (OUT / "V42_R3_VALIDATION.json").write_text(
        json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if validation["status"] != "PASS":
        raise SystemExit(json.dumps(validation, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

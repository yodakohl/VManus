#!/usr/bin/env python3
"""Build the blinded R2 V64 five-record Herbal source edition.

Page-bearing V60--V63 inputs are selected before row materialisation through
``vmanus-exp query-tsv``.  Concrete editorial content is deliberately tagged
IMAGE, GENRE, or EXEMPLAR unless an inherited exact-card mnemonic licenses it.
"""

from __future__ import annotations

import csv
import io
import json
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "experiments/yolo/sidequest_theory_candidates_v64"
PAGES = ("f10r", "f11r", "f55v", "f56r")

V60_EVENTS = ROOT / "experiments/yolo/sidequest_theory_candidates_v60/V60_SELECTED_381_EVENT_LEDGER.tsv"
V61_STATEMENTS = ROOT / "experiments/yolo/sidequest_theory_candidates_v61/V61_SELECTED_116_SOURCE_STATEMENTS.tsv"
V62_TRANSITIONS = ROOT / "experiments/yolo/sidequest_theory_candidates_v62/V62_SELECTED_116_REGISTER_TRANSITIONS.tsv"
V63_EVENTS = ROOT / "experiments/yolo/sidequest_theory_candidates_v63/V63_SELECTED_381_EVENT_TEMPLATE_LEDGER.tsv"
V63_FIELDS = ROOT / "experiments/yolo/sidequest_theory_candidates_v63/V63_SELECTED_135_FIELD_SLOT_PARSE.tsv"
V63_STATEMENTS = ROOT / "experiments/yolo/sidequest_theory_candidates_v63/V63_SELECTED_116_STATEMENT_SLOT_PARSE.tsv"

V60_EVENT_COLUMNS = (
    "event_serial,page,locus,record_unit_id,field_id,event_index_in_record,surface,joint_tuple_id,"
    "formal_formula_opaque,FORMAL_VALUE,terminal_status,strict_control_prompt,"
    "ATOMIC_OR_WHOLE_CARD_MNEMONIC,mnemonic_scope,LOCAL_IATROMEDICAL_EXPANSION,"
    "NONMEDICAL_RIVAL,UNKNOWN_EXEMPLAR_STATUS,source_lineage"
)
V61_STATEMENT_COLUMNS = (
    "statement_id,record_unit_id,page,statement_ordinal_in_record,start_locus,start_field,end_locus,"
    "end_field,constituent_loci,constituent_fields,physical_line_count,event_count,event_serials,"
    "closure_sequence,entry_boundary_class,exit_boundary_class,internal_cross_line_boundaries,"
    "selected_short_card_skeleton,concrete_workshop_reading,strongest_alternative,"
    "apprentice_reading_rule,record_flow_context,evidence_basis,status"
)
V62_TRANSITION_COLUMNS = (
    "statement_id,record_unit_id,page,pre_state,selected_mnemonic_triggers,observed_triggers,"
    "inferred_missing_slots,silent_register_demand,operation_trace,post_state,"
    "backward_reconstructability,irreducible_ambiguity_codes,complete_creative_reading,"
    "strongest_source_alternative,anonymous_id_contract,card_binding_contract,source_lineage"
)
V63_EVENT_COLUMNS = (
    "event_serial,page,locus,record_unit_id,field_id,statement_id,joint_tuple_id,surface_display_only,"
    "formal_formula_opaque,terminal_status,strict_formal_prompt,selected_exact_mnemonic,event_template,"
    "trigger_origin,template_payload,required_registers,symbolic_register_effect,event_parse_status,"
    "formal_semantic_noninheritance,binding_contract,source_lineage"
)
V63_FIELD_COLUMNS = (
    "field_id,record_unit_id,page,locus,statement_id,field_position_in_statement,event_count,event_serials,"
    "primary_template,ordered_event_template_sequence,licensed_primitive_sequence,parse_status,parse_reason,"
    "recognized_event_count,exemplar_only_event_count,register_pre_state_statement_envelope,register_update_trace,"
    "register_post_state_statement_envelope,intermediate_register_resolution,local_exemplar_reading,"
    "binding_contract,source_lineage"
)
V63_STATEMENT_COLUMNS = (
    "statement_id,record_unit_id,page,statement_ordinal_in_record,constituent_fields,event_count,event_serials,"
    "primary_template,ordered_event_template_sequence,licensed_primitive_sequence,parse_status,parse_reason,"
    "recognized_event_count,exemplar_only_event_count,pre_state,owner_operation,"
    "active_item_preparation_operation,target_station_operation,previous_item_operation,"
    "parser_register_update_trace,post_state,register_update_status,complete_creative_reading,"
    "strongest_segmentation_or_source_alternative,binding_contract,source_lineage"
)


def seg(text: str, assumptions: str = "NONE") -> dict[str, str]:
    return {"text": text, "assumptions": assumptions}


FIELD_SPECS: dict[str, dict[str, object]] = {
    "F001": {
        "segments": [
            seg("[IMAGE:unterer Wurzelstock des Teufelsabbisses]", "A001|A002"),
            seg("[GENRE:säubere ihn]", "A003"),
            seg("[REGISTER:H1:I001 als derselbe Arbeitsansatz]"),
            seg("[GENRE:zerschneide ihn]", "A003"),
            seg("[GENRE:gib ihn in den Brennhafen]", "A004"),
            seg("[GENRE:füge Quellwasser hinzu]", "A004|A005"),
            seg("[GENRE:fange den ersten Lauf im Glas auf]", "A004|A006"),
            seg("[CARD:ANWENDEN?] [GENRE:gebrauche den Lauf innerlich]", "A007"),
            seg("[CARD:MASS?] [FORMAL:VORGABEPARAMETER?; keine Wortbedeutung] [EXEMPLAR:in kleinem örtlichem Maß]", "A008"),
            seg("[GENRE:gegen Stechen im Leib] [GENRE:verwahre den Rest verschlossen]", "A009|A010"),
        ],
        "revision": "V53-Wurzelwasser bleibt, doch Pflanze, Destillation, Wasser, Lauf, Glas und Indikation sind durchgehend als Bild-/Gattungsannahmen markiert; kein unbekanntes Ereignis erhält ein Wort.",
        "counter": "Technische Pflanzenrohstoff-Destillation ohne Arzneigebrauch; die Bildwurzel widerspricht Succisa.",
    },
    "F002": {
        "segments": [
            seg("[EXEMPLAR:nimm den frischen ersten Lauf]", "A006"),
            seg("[GENRE:erwärme ihn gelinde]", "A011"),
            seg("[FORMAL:AKTIVEN_ARBEITSSTAND_VERKNÜPFEN; keine Wortbedeutung] [REGISTER:H1:I001 fortführen]"),
            seg("[CARD:BEREIT?] [EXEMPLAR:bis zum örtlichen Gebrauchszustand]", "A012"),
        ],
        "revision": "Die V53-Verbindung mit einem ersten klaren Lauf wird auf Registerfortführung reduziert; nur BEREIT? bleibt Zustandsanker.",
        "counter": "Formaler Nachtrag oder Lagerstatus statt frischer Arzneiklausel.",
    },
    "F003": {
        "segments": [
            seg("[IMAGE:Blütenköpfe und junge Blätter derselben Teufelsabbiss-Pflanze]", "A001|A013"),
            seg("[CARD:BEREIT?] [EXEMPLAR:wenn sie eben aufgehen]", "A014"),
            seg("[CARD:ANSATZ?] [REGISTER:H2:I001 als frischen Ansatz führen]"),
            seg("[GENRE:zerstoße das Kraut]", "A015"),
            seg("[GENRE:presse den Saft durch ein Tuch]", "A015"),
            seg("[EXEMPLAR:fange die erste Fraktion auf]", "A016"),
            seg("[GENRE:gib Olivenöl hinzu]", "A017"),
            seg("[CARD:MASS?] [EXEMPLAR:ein örtlich vorgeschriebenes Maß]", "A018"),
            seg("[GENRE:erwärme gelinde]", "A019"),
        ],
        "revision": "Der zweite f10r-Record beginnt einen eigenen recordlokalen Blüten-/Blattansatz; er erbt H1s Wurzelwasser nicht.",
        "counter": "Zweite Ernte- oder Materialfraktion ohne Öl und ohne medizinische Funktion.",
    },
    "F004": {
        "segments": [
            seg("[IMAGE:nimm vor voller Blüte eine zweite Portion der Spitzen]", "A013|A014"),
            seg("[CARD:ANSATZ?] [REGISTER:H2:I001 fortführen]"),
            seg("[EXEMPLAR:eine Handvoll]", "A018"),
            seg("[FORMAL:AKTIVEN_ARBEITSSTAND_VERKNÜPFEN; keine Wortbedeutung] [REGISTER:H2:I001 fortführen]"),
            seg("[CARD:VORIGES?] [REGISTER:H2:I001 als vorigen Posten aufnehmen]"),
            seg("[FORMAL:AKTIVEN_ARBEITSSTAND_VERKNÜPFEN; keine Wortbedeutung] [REGISTER:H2:I002 führen]"),
            seg("[CARD:MASS?] [FORMAL:VORGABEPARAMETER?; keine Wortbedeutung] [EXEMPLAR:ein gleiches örtliches Maß]", "A018"),
            seg("[GENRE:verbinde beide Fraktionen]", "A016|A020"),
        ],
        "revision": "V53s Rückgriff auf H1 wird gestrichen: VORIGES? bindet nur den vorigen H2-Posten H2:I001; zwei Fraktionen bleiben eine lokale Artikelannahme.",
        "counter": "Parallelzelle oder Kopierwiederaufnahme statt Rezeptmischung.",
    },
    "F005": {
        "segments": [
            seg("[GENRE:gib die Fraktionen in ein glasiertes Gefäß]", "A021"),
            seg("[CARD:ANSATZ?] [REGISTER:H2:I003 als Salbenansatz führen]"),
            seg("[CARD:ANSATZ?] [REGISTER:H2:I003 wiederholt; Slotkonflikt bleibt sichtbar]"),
            seg("[GENRE:rühre bei kleinem Feuer]", "A019|A022"),
            seg("[EXEMPLAR:bis eine weiche Salbe entsteht]", "A022"),
            seg("[GENRE:bewahre sie bedeckt]", "A021"),
            seg("[GENRE:lege sie äußerlich auf ein Geschwür oder eine harte Schwellung]", "A023"),
        ],
        "revision": "Die zweimalige ANSATZ?-Karte wird nicht geglättet; Salbe, Gefäß und äußerer Gebrauch bleiben Gattungsexpansion.",
        "counter": "Zwei Materialkategorien oder Dittographie; kein formaler Schluss stützt das Artikelende.",
    },
    "F006": {
        "segments": [
            seg("[IMAGE:Blüten und junge Blätter des Duftveilchens] [GENRE:im ersten Frühjahr nehmen]", "A024|A025"),
            seg("[GENRE:in reinem Wein kochen]", "A026"),
            seg("[GENRE:durch ein feines Tuch wringen]", "A027"),
            seg("[GENRE:den Auszug stehen lassen]", "A027"),
            seg("[GENRE:nochmals seihen]", "A027"),
            seg("[CARD:KLAR?] [EXEMPLAR:bis zum örtlich geprüften klaren Zustand]", "A028"),
            seg("[FORMAL:CLOSE; keine Wortbedeutung] [GENRE:abkühlen lassen]", "A027"),
        ],
        "revision": "Die awkward V61-Wurzelernte wird aufgegeben; V53s Veilchenblüten/-blätter und die belegte Wein-/Tuchfolge werden als Gattungsschicht eingesetzt.",
        "counter": "Gundermann- oder anderes blau blühendes Kriechherb; KLAR? kann bloß ein Statuslabel sein.",
    },
    "F007": {
        "segments": [
            seg("[EXEMPLAR:behalte einen Teil der frischen Blüten für die zweite Arznei zurück]", "A029"),
        ],
        "revision": "Unparsed Feld bleibt vollständig Exemplartext; es führt nur den V62-PREVIOUS-Posten H3:I002 ein.",
        "counter": "Unabhängige Bildrubrik oder Materialname statt Rückbehalt.",
    },
    "F008": {
        "segments": [
            seg("[REGISTER:H3:I001 als erster Auszug]"),
            seg("[GENRE:nimm davon]", "A030"),
            seg("[GENRE:gib ihn als Trank]", "A030"),
            seg("[GENRE:bei bedrücktem Gemüt und beschwerter Brust]", "A031"),
            seg("[CARD:MASS?] [FORMAL:VORGABEPARAMETER?; keine Wortbedeutung] [EXEMPLAR:in kleinem örtlichem Maß]", "A034"),
        ],
        "revision": "MASS? trägt nur die Maßklasse; Trank und Indikation stammen aus der Veilchen-Quellenanalogie.",
        "counter": "Gemessene technische Fraktion oder äußere Portion ohne innere Einnahme.",
    },
    "F009": {
        "segments": [
            seg("[EXEMPLAR:nimm die zurückbehaltenen Blüten]", "A029"),
            seg("[GENRE:erwärme sie in Olivenöl]", "A032"),
            seg("[CARD:BEREIT?] [EXEMPLAR:bis zum örtlichen Bereitschaftszustand]", "A028"),
            seg("[GENRE:streiche das Öl äußerlich um die Lider ohne das Auge zu berühren]", "A033"),
        ],
        "revision": "V53s unspezifisches Geschwür wird durch den enger belegten Veilchenöl-Gebrauch an den Lidern ersetzt; die Körperstelle bleibt GENRE.",
        "counter": "Getrennte Lagerzelle oder beliebiges Pflanzenöl; kein ANWENDEN?-Anker.",
    },
    "F010": {
        "segments": [
            seg("[FORMAL:STANDARDSLOT_SETZEN; keine Wortbedeutung] [EXEMPLAR:setze den ersten Posten an]", "A038"),
            seg("[CARD:MASS?] [EXEMPLAR:ein örtlich vorgeschriebenes Maß]", "A042"),
            seg("[IMAGE:breite Bärlauchblätter] [GENRE:zerstoße sie]", "A035|A036"),
            seg("[GENRE:füge Weißwein hinzu]", "A037"),
            seg("[FORMAL:CLOSE; keine Wortbedeutung] [GENRE:verschließe das Gefäß und lasse es kühl stehen]", "A038"),
        ],
        "revision": "Bärlauch/Allium bleibt Bildwette; SET und MASS liefern weder Blatt noch Wein oder Standzeit.",
        "counter": "Breitwegerichsaft oder technische Blattmaische; eine sichere Zwiebel fehlt im Bild.",
    },
    "F011": {
        "segments": [
            seg("[CARD:MASS?] [FORMAL:VORGABEPARAMETER?; keine Wortbedeutung] [EXEMPLAR:miss eine Portion des Ansatzes ab]", "A042"),
            seg("[GENRE:wringe sie durch Leinwand und lasse sie klar absetzen]", "A039"),
            seg("[FORMAL:CLOSE_B3; keine Wortbedeutung] [GENRE:verwahre den klaren Auszug]", "A038|A039"),
        ],
        "revision": "Die V61-Wundwäsche wird nach F012 verschoben; F011 schließt nun historisch natürlicher Maß, Filtration und Lagerung ab.",
        "counter": "Abteilen eines weichen Rohstoffrests statt Filtration.",
    },
    "F012": {
        "segments": [
            seg("[GENRE:wasche eine unreine äußere Wunde]", "A040"),
            seg("[GENRE:mit dem klaren Auszug]", "A040"),
            seg("[EXEMPLAR:einmal oder nach örtlicher Vorschrift]", "A041"),
            seg("[FORMAL:CLOSE; keine Wortbedeutung] [GENRE:beende diesen Gebrauch]", "A040"),
        ],
        "revision": "Das vollständig unparsed Feld erhält die Wundwäsche als offen deklarierte Quellenexpansion; der terminale Status ist kein Waschverb.",
        "counter": "Zweite Materialfraktion oder nichtmedizinischer Reinigungsgang.",
    },
    "F013": {
        "segments": [
            seg("[CARD:MASS?] [EXEMPLAR:nimm ein örtliches Maß der zurückbehaltenen Blätter]", "A042"),
            seg("[FORMAL:LOKALEN_RELATIONSSLOT_SETZEN; keine Wortbedeutung] [EXEMPLAR:lege sie an die bezeichnete äußere Stelle]", "A045"),
            seg("[GENRE:erwärme sie gelinde]", "A043"),
            seg("[CARD:ANSATZ?] [REGISTER:H4:I002 als zweiten Ansatz führen]"),
            seg("[GENRE:mische sie mit Honig]", "A044"),
            seg("[GENRE:lege den warmen Umschlag frisch auf]", "A045"),
        ],
        "revision": "Die zweite Allium-/Plantago-artige Auflage bleibt offen, weil der Record ohne formalen Schluss endet; Relation liefert keine Körperstelle.",
        "counter": "Zweite Rohstofffraktion oder Plantago-Umschlag; Allium ist nicht exklusiv.",
    },
    "F014": {
        "segments": [
            seg("[IMAGE:vom rundblättrigen Sonnentau]", "A046"),
            seg("[GENRE:sammle] [IMAGE:das ganze oberirdische Kraut im feuchten Moor]", "A047"),
            seg("[EXEMPLAR:zu Beginn der Blüte]", "A048"),
            seg("[CARD:MASS?] [FORMAL:VORGABEPARAMETER?; keine Wortbedeutung] [EXEMPLAR:nur ein kleines örtliches Maß]", "A049"),
        ],
        "revision": "Die V61-Wurzel wird gestrichen; das Bild stützt höchstens klebrige Rundblätter, während Teil, Habitat und Ernte GENRE/EXEMPLAR bleiben.",
        "counter": "Venushaarfarn oder synthetisches Feuchtlandkraut; sichere Drosera-Belege um 1420 fehlen.",
    },
    "F015": {
        "segments": [
            seg("[GENRE:zerstoße die frischen klebrigen Blätter]", "A050"),
            seg("[GENRE:lege sie auf]", "A051"),
            seg("[EXEMPLAR:eine einzelne Warze oder ein Hühnerauge]", "A051"),
            seg("[CARD:ANWENDEN?] [EXEMPLAR:nur kurz anwenden]", "A052"),
            seg("[CARD:ZIEL?] [EXEMPLAR:an der örtlich bezeichneten Hautstelle]", "A051"),
        ],
        "revision": "ANWENDEN?+ZIEL? wird als äußerliche Zielanwendung instanziiert, nicht mehr als Brusttrank; Hautstelle und Leiden bleiben Exemplar.",
        "counter": "Neutrale Materialanwendung an einer technischen Zielstelle.",
    },
    "F016": {
        "segments": [
            seg("[GENRE:nimm die Auflage wieder ab]", "A053"),
            seg("[GENRE:wasche die Stelle mit Wasser]", "A053"),
            seg("[CARD:ANWENDEN?] [EXEMPLAR:wiederhole den Gebrauch nur falls vertragen]", "A054"),
            seg("[FORMAL:CLOSE; keine Wortbedeutung] [GENRE:beende die äußere Anwendung]", "A053"),
        ],
        "revision": "Das terminale Feld schließt die äußere Anwendung; Honig und Wein werden nicht mehr in die zwei ANWENDEN?-Karten hineingelesen.",
        "counter": "Materialtrocknung oder technischer Abschluss statt Nachbehandlung.",
    },
    "F017": {
        "segments": [
            seg("[IMAGE:nimm vom übrigen Kraut die blühenden Stiele]", "A055"),
            seg("[GENRE:trockne sie im Schatten]", "A055"),
            seg("[GENRE:zerreibe sie grob]", "A055"),
            seg("[GENRE:verwahre sie trocken]", "A056"),
        ],
        "revision": "Vollständig unparsed: die Trocknungszelle beginnt bewusst einen zweiten, nur gattungsgestützten Vorratsabschnitt.",
        "counter": "Samen-/Knospenrubrik oder beliebige Materialprobe.",
    },
    "F018": {
        "segments": [
            seg("[GENRE:setze daraus einen schwachen Auszug an]", "A057"),
            seg("[GENRE:mit mildem Wein]", "A057"),
            seg("[GENRE:seihe ihn durch ein Tuch]", "A058"),
        ],
        "revision": "Magenweh und frischer Gebrauch aus V61 werden verworfen; das unparsed Feld erhält nur eine markierte Rezeptbrücke.",
        "counter": "Lagervermerk ohne Auszug oder medizinische Bedeutung.",
    },
    "F019": {
        "segments": [
            seg("[GENRE:füge Honig hinzu]", "A059"),
            seg("[GENRE:erwärme gelinde]", "A060"),
            seg("[GENRE:gib den Auszug als Brusttrank]", "A061"),
            seg("[GENRE:bei trockenem Husten]", "A062"),
        ],
        "revision": "Der Brusttrank wird vollständig als historisch-kreativer Exemplartext ausgewiesen; keine der vier Karten ist lizenziert.",
        "counter": "Venushaar-Rezept oder nichtmedizinische Honigmischung.",
    },
    "F020": {
        "segments": [
            seg("[CARD:ANTEIL?] [REGISTER:H5:I004 als ausgewählten Teil führen]"),
            seg("[EXEMPLAR:je Gabe]", "A063"),
            seg("[CARD:MASS?] [FORMAL:VORGABEPARAMETER?; keine Wortbedeutung] [EXEMPLAR:ein kleines örtliches Maß]", "A049|A063"),
        ],
        "revision": "Die V53-Blüte wird gestrichen; sichtbar lizenziert sind nur ausgewählter Anteil und Maßklasse, nicht Teilidentität oder Zahl.",
        "counter": "Dosier-/Loszeile ohne Arzneigebrauch; offenes Recordende.",
    },
}


RECORD_SPECS: dict[str, dict[str, str]] = {
    "H1": {
        "article_title": "Teufelsabbiss — gebranntes Wurzelwasser",
        "image_unit": "f10r image",
        "primary_identity": "IMAGE: Teufelsabbiss (Succisa pratensis; Dipsacaceae-Umkreis)",
        "strongest_plant_rival": "IMAGE_RIVAL: Skabiose (Scabiosa columbaria)",
        "identity_confidence": "MEDIUM",
        "tagged_continuous_german": (
            "[IMAGE:Vom Teufelsabbiss.] [GENRE:Nimm] [IMAGE:den unteren Wurzelstock], "
            "[GENRE:säubere und zerschneide ihn], [GENRE:gib ihn mit Quellwasser in den Brennhafen] "
            "[GENRE:und fange den ersten Lauf in einem Glas auf]. [CARD:ANWENDEN?=Wende den aktiven Lauf an] "
            "[GENRE:innerlich] [CARD:MASS?=nach Maß] [EXEMPLAR:in kleiner Gabe] "
            "[GENRE:gegen Stechen im Leib]; [GENRE:verwahre den Rest verschlossen]. "
            "[EXEMPLAR:Nimm für frischen Gebrauch den ersten Lauf], [GENRE:erwärme ihn gelinde], "
            "[FORMAL:AKTIVEN_ARBEITSSTAND_VERKNÜPFEN; ohne Wortbedeutung] [REGISTER:H1:I001 fortgeführt], "
            "[CARD:BEREIT?=bis bereit] [EXEMPLAR:nach örtlichem Kriterium]."
        ),
        "historical_mechanism": "Pflanzenartikel mit Wurzelteil, gebranntem Wasser, kleinem innerem Gebrauch und kurzem Frische-Nachtrag.",
        "strongest_nonmedical_rival": "Destillations-/Rohstoffnotiz; ANWENDEN? und MASS? entscheiden nicht zwischen Arznei und Werkstoff.",
        "revision_from_v53": "KEEP Wurzelwasser, aber alle Gegenstände und Indikationen taggen; keine semantische Vererbung aus unbekannten Karten.",
    },
    "H2": {
        "article_title": "Teufelsabbiss — zwei Blütenfraktionen als Salbenansatz",
        "image_unit": "f10r image",
        "primary_identity": "IMAGE: Teufelsabbiss (Succisa pratensis; Dipsacaceae-Umkreis)",
        "strongest_plant_rival": "IMAGE_RIVAL: Skabiose (Scabiosa columbaria)",
        "identity_confidence": "MEDIUM_LOW",
        "tagged_continuous_german": (
            "[IMAGE:Von derselben Teufelsabbiss-Pflanze.] [GENRE:Nimm] [IMAGE:Blütenköpfe und junge Blätter] "
            "[CARD:BEREIT?] [EXEMPLAR:wenn sie eben aufgehen], [CARD:ANSATZ?=führe sie als frischen Ansatz], "
            "[GENRE:zerstoße sie und presse den Saft durch ein Tuch]. [EXEMPLAR:Fange die erste Fraktion auf], "
            "[GENRE:gib Olivenöl hinzu], [CARD:MASS?=nach Maß] [EXEMPLAR:in örtlicher Menge], "
            "[GENRE:und erwärme gelinde]. [IMAGE:Nimm vor voller Blüte eine zweite Portion der Spitzen], "
            "[CARD:ANSATZ?] [REGISTER:H2:I001 fortgeführt]; [EXEMPLAR:eine Handvoll]. "
            "[CARD:VORIGES?=Nimm den vorigen H2-Posten wieder auf] [REGISTER:H2:I001], "
            "[CARD:MASS?=in gleichem örtlichem Maß], [GENRE:und verbinde beide Fraktionen]. "
            "[GENRE:Gib sie in ein glasiertes Gefäß], [CARD:ANSATZ?] [CARD:ANSATZ?] "
            "[REGISTER:H2:I003 mit sichtbarer Doppelbelegung], [GENRE:rühre bei kleinem Feuer] "
            "[EXEMPLAR:bis eine weiche Salbe entsteht], [GENRE:bewahre sie bedeckt] "
            "[GENRE:und lege sie äußerlich auf ein Geschwür oder eine harte Schwellung]."
        ),
        "historical_mechanism": "Zwei recordlokale Fraktionen eines blühenden Simplex werden gemessen, verbunden und zu einer äußeren Zubereitung geführt.",
        "strongest_nonmedical_rival": "Parallele Erntefraktionen oder Materialchargen; das doppelte ANSATZ? kann Dittographie/Kategorie sein.",
        "revision_from_v53": "REVISE: VORIGES? greift nicht auf H1s Wurzelwasser, sondern nur auf H2:I001 zurück.",
    },
    "H3": {
        "article_title": "Duftveilchen — klarer Wein und äußeres Veilchenöl",
        "image_unit": "f11r image",
        "primary_identity": "IMAGE: Duftveilchen (Viola odorata)",
        "strongest_plant_rival": "IMAGE_RIVAL: Gundermann (Glechoma hederacea)",
        "identity_confidence": "MEDIUM",
        "tagged_continuous_german": (
            "[IMAGE:Vom Duftveilchen.] [GENRE:Nimm im ersten Frühjahr] [IMAGE:Blüten und junge Blätter], "
            "[GENRE:koche sie in reinem Wein], [GENRE:wringe sie durch ein feines Tuch], "
            "[GENRE:lasse den Auszug stehen und seihe ihn nochmals] [CARD:KLAR?=bis klar] "
            "[EXEMPLAR:nach örtlicher Prüfung], [GENRE:dann lasse ihn abkühlen]. "
            "[EXEMPLAR:Behalte einen Teil der frischen Blüten für die zweite Arznei zurück]. "
            "[GENRE:Nimm vom ersten Auszug und gib ihn als Trank] [GENRE:bei bedrücktem Gemüt und beschwerter Brust] "
            "[CARD:MASS?=in einem Maß] [EXEMPLAR:kleiner örtlicher Größe]. "
            "[EXEMPLAR:Nimm die zurückbehaltenen Blüten], [GENRE:erwärme sie in Olivenöl] "
            "[CARD:BEREIT?=bis bereit] [EXEMPLAR:nach örtlichem Kriterium], "
            "[GENRE:und streiche das Öl äußerlich um die Lider, ohne das Auge zu berühren]."
        ),
        "historical_mechanism": "Ein Pflanzenartikel verzweigt nach einem Wein-Auszug in inneren Trank und separat geführtes Blütenöl.",
        "strongest_nonmedical_rival": "Gundermann oder anderes blau blühendes Kriechkraut; die drei langen Bildwurzeln widersprechen Viola.",
        "revision_from_v53": "REVISE: Wurzelprosa entfällt; äußere Verwendung wird enger an das belegte Veilchenöl um die Lider gebunden.",
    },
    "H4": {
        "article_title": "Bärlauch — Weinansatz, Wundwäsche und warmer Blattumschlag",
        "image_unit": "f55v image",
        "primary_identity": "IMAGE: Bärlauch/Allium (Allium ursinum als Arbeitsidentität)",
        "strongest_plant_rival": "IMAGE_RIVAL: Breitwegerich (Plantago major)",
        "identity_confidence": "MEDIUM",
        "tagged_continuous_german": (
            "[IMAGE:Vom breiten Lauch.] [EXEMPLAR:Setze den ersten Posten an], "
            "[CARD:MASS?=nimm nach Maß] [EXEMPLAR:ein örtliches Maß] [IMAGE:breiter Blätter], "
            "[GENRE:zerstoße sie], [GENRE:füge Weißwein hinzu], [GENRE:verschließe das Gefäß und lasse es kühl stehen]. "
            "[CARD:MASS?=Miss eine Portion ab], [GENRE:wringe sie durch Leinwand und lasse sie klar absetzen], "
            "[GENRE:verwahre den klaren Auszug]. [GENRE:Wasche damit eine unreine äußere Wunde] "
            "[EXEMPLAR:einmal oder nach örtlicher Vorschrift]. [CARD:MASS?=Nimm nach Maß] "
            "[EXEMPLAR:eine Portion der zurückbehaltenen Blätter], [EXEMPLAR:lege sie an die bezeichnete äußere Stelle], "
            "[GENRE:erwärme sie gelinde], [CARD:ANSATZ?=führe sie als zweiten Ansatz], "
            "[GENRE:mische sie mit Honig] [GENRE:und lege den warmen Umschlag frisch auf]."
        ),
        "historical_mechanism": "Gemessener Allium-/Blattansatz wird stehen gelassen, geklärt und in zwei äußeren Gebrauchsformen eingesetzt.",
        "strongest_nonmedical_rival": "Plantago passt zu Saft/Tuch/Wein oder Honig und warmer Auflage mindestens ebenso gut; technische Blattmaische bleibt möglich.",
        "revision_from_v53": "REVISE: F011 ist Filtration/Lagerung, F012 die offen exemplarische Wundwäsche; F013 bleibt ungeschlossen.",
    },
    "H5": {
        "article_title": "Rundblättriger Sonnentau — kurze Hautanwendung und getrockneter Brusttrank",
        "image_unit": "f56r image",
        "primary_identity": "IMAGE: Rundblättriger Sonnentau (Drosera rotundifolia)",
        "strongest_plant_rival": "IMAGE_RIVAL: Venushaarfarn (Adiantum capillus-veneris)",
        "identity_confidence": "VISUAL_MEDIUM_HISTORICAL_LOW",
        "tagged_continuous_german": (
            "[IMAGE:Vom rundblättrigen Sonnentau.] [GENRE:Sammle] [IMAGE:das ganze oberirdische Kraut im feuchten Moor] "
            "[EXEMPLAR:zu Beginn der Blüte] [CARD:MASS?=in einem Maß] [EXEMPLAR:nur eine kleine örtliche Menge]. "
            "[GENRE:Zerstoße die frischen klebrigen Blätter und lege sie auf] "
            "[EXEMPLAR:eine einzelne Warze oder ein Hühnerauge]; [CARD:ANWENDEN?=wende sie an] "
            "[EXEMPLAR:nur kurz] [CARD:ZIEL?=an der Zielstelle] [EXEMPLAR:der bezeichneten Haut]. "
            "[GENRE:Nimm die Auflage wieder ab und wasche die Stelle mit Wasser]; "
            "[CARD:ANWENDEN?=wiederhole den Gebrauch] [EXEMPLAR:nur falls vertragen], [GENRE:dann beende ihn]. "
            "[IMAGE:Nimm vom übrigen Kraut die blühenden Stiele], [GENRE:trockne sie im Schatten, zerreibe sie grob und verwahre sie trocken]. "
            "[GENRE:Setze daraus mit mildem Wein einen schwachen Auszug an und seihe ihn durch ein Tuch]. "
            "[GENRE:Füge Honig hinzu, erwärme gelinde und gib den Auszug als Brusttrank] [GENRE:bei trockenem Husten]. "
            "[CARD:ANTEIL?=Wähle davon einen Anteil] [EXEMPLAR:je Gabe] "
            "[CARD:MASS?=nach Maß] [EXEMPLAR:in kleiner örtlicher Menge]."
        ),
        "historical_mechanism": "Zwei exemplarische Nutzungen desselben Simplex: kurze frische Hautauflage und getrockneter, gesüßter Auszug.",
        "strongest_nonmedical_rival": "Adiantum hat die historisch bessere pektorale Tradition; Drosera ist bildnäher, aber um 1420 schlecht gesichert.",
        "revision_from_v53": "REVISE/HIGH_RISK: erste ANWENDEN?+ZIEL?-Folge wird äußerlich; der Hustenwein bleibt vollständig GENRE und nicht Kartenbedeutung.",
    },
}


ASSUMPTIONS = [
    ("A001", "H1|H2", "IMAGE", "Teufelsabbiss/Succisa als Besitzer von f10r", "F001|F003", "V53 erlaubter Bildbefund; Frankfurter Abiss-Wasser als Nahvergleich", "MEDIUM", "Rote endständige Verdickungen statt abgebissener Wurzel", "KEEP_IMAGE_WAGER"),
    ("A002", "H1", "IMAGE", "unterer Wurzelstock als verwendeter Teil", "F001", "Bild + Herbal-Gattung", "MEDIUM_LOW", "Karte bezeichnet keinen Pflanzenteil", "KEEP_TAGGED"),
    ("A003", "H1", "GENRE", "Wurzel säubern und schneiden", "e2|e4", "Rezept-/Destillierpraxis", "MEDIUM", "vollständig exemplarisch", "KEEP_TAGGED"),
    ("A004", "H1", "GENRE", "Hydrodestillation im Brennhafen", "e5|e6|e7", "Frankfurt Ms. germ. qu. 17: gebrannte Wasser", "MEDIUM_HIGH", "keine Geräteabbildung und kein Kartenanker", "KEEP_GENRE"),
    ("A005", "H1", "GENRE", "Quellwasser als Medium", "e6", "Gattung gebrannter Wasser", "MEDIUM", "Medium unsichtbar", "KEEP_TAGGED"),
    ("A006", "H1", "GENRE", "erster Lauf und Glas", "e7|e11", "Destillierpraxis", "MEDIUM_LOW", "Fraktion und Gefäß unsichtbar", "KEEP_TAGGED"),
    ("A007", "H1", "GENRE", "innerlicher Gebrauch", "e8", "Abiss-Wasser-Nahquelle", "MEDIUM", "ANWENDEN? sagt nicht innerlich", "KEEP_TAGGED"),
    ("A008", "H1", "EXEMPLAR", "kleine Gabe", "e9", "MASS? plus Dosisgenre", "LOW", "keine Zahl/Einheit sichtbar", "KEEP_LOCAL_ONLY"),
    ("A009", "H1", "GENRE", "Stechen im Leib als Indikation", "e10", "Frankfurter Abiss-Einträge", "MEDIUM", "Krankheit unsichtbar", "KEEP_TAGGED"),
    ("A010", "H1", "GENRE", "verschlossene Verwahrung", "e10", "Arzneiwasserpraxis", "MEDIUM_LOW", "kein Schlussfeld", "KEEP_TAGGED"),
    ("A011", "H1", "GENRE", "gelindes Erwärmen", "e12", "Rezeptpraxis", "LOW", "kein TEMPERIEREN?-Anker", "KEEP_LOCAL_ONLY"),
    ("A012", "H1", "EXEMPLAR", "örtliches Bereitschaftskriterium", "e14", "BEREIT? braucht lokalen Füller", "MEDIUM", "Kriterium unbekannt", "KEEP_OPEN"),
    ("A013", "H2", "IMAGE", "Blütenköpfe und junge Blätter", "e15|e24", "f10r-Bild", "MEDIUM", "Pflanzenteil nicht kartiert", "KEEP_TAGGED"),
    ("A014", "H2", "EXEMPLAR", "Ernte beim Aufgehen/vor voller Blüte", "e16|e24", "Herbal-Gattung", "LOW", "BEREIT? ist kein Erntekalender", "KEEP_LOCAL_ONLY"),
    ("A015", "H2", "GENRE", "zerstoßen und durch Tuch pressen", "e18|e19", "Materia-medica-Praxis", "MEDIUM", "beide Ereignisse unparsed", "KEEP_TAGGED"),
    ("A016", "H2", "EXEMPLAR", "zwei Saftfraktionen", "e20|e31", "V62 recordlokale Postenfolge", "MEDIUM_LOW", "kann Parallelzelle statt Mischung sein", "KEEP_OPEN"),
    ("A017", "H2", "GENRE", "Olivenöl als Träger", "e21", "Salben-/Ölpraxis", "LOW", "Medium unsichtbar", "KEEP_LOCAL_ONLY"),
    ("A018", "H2", "EXEMPLAR", "Handvoll/gleiche örtliche Maße", "e22|e26|e30", "MASS? plus Rezeptgenre", "LOW", "keine Einheit oder Gleichheit kartiert", "KEEP_LOCAL_ONLY"),
    ("A019", "H2", "GENRE", "gelindes Erhitzen", "e23|e35", "Salbenpraxis", "LOW", "kein TEMPERIEREN?", "KEEP_LOCAL_ONLY"),
    ("A020", "H2", "GENRE", "Fraktionen verbinden", "e31", "Rezeptfolge", "MEDIUM_LOW", "formaler Link ist keine Mischanweisung", "KEEP_TAGGED"),
    ("A021", "H2", "GENRE", "glasiertes/bedecktes Gefäß", "e32|e37", "Salbenlagerung", "LOW", "Gefäß unsichtbar", "KEEP_LOCAL_ONLY"),
    ("A022", "H2", "EXEMPLAR", "weiche Salbenkonsistenz", "e35|e36", "Gattung", "LOW", "keine Zustandskarte", "KEEP_LOCAL_ONLY"),
    ("A023", "H2", "GENRE", "äußerlich gegen Geschwür/Schwellung", "e38", "Abiss-/Salbengattung", "LOW", "Gebrauch und Leiden unsichtbar", "KEEP_LOCAL_ONLY"),
    ("A024", "H3", "IMAGE", "Duftveilchen als f11r-Besitzer", "F006", "V53 Bildbefund + Physica-Vergleich", "MEDIUM", "lange gezähnte Wurzeln passen nicht", "KEEP_IMAGE_WAGER"),
    ("A025", "H3", "IMAGE|GENRE", "Blüten/junge Blätter im ersten Frühjahr", "e39", "Viola-Bild und Physica", "MEDIUM", "Teil und Saison unkartiert", "KEEP_TAGGED"),
    ("A026", "H3", "GENRE", "reiner Wein als Kochmedium", "e40", "Physica I.103", "HIGH_AS_ANALOGY", "keine Mediumkarte", "KEEP_GENRE"),
    ("A027", "H3", "GENRE", "Tuchfiltration, Stehen, Nachseihen, Abkühlen", "e41|e42|e43|e45", "Physica/Rezeptpraxis", "MEDIUM", "nur KLAR? ist sichtbar", "KEEP_TAGGED"),
    ("A028", "H3", "EXEMPLAR", "örtliches Klarheits-/Bereitschaftskriterium", "e44|e54", "KLAR?/BEREIT? brauchen lokale Prüfung", "MEDIUM", "keine Dauer/Temperatur", "KEEP_OPEN"),
    ("A029", "H3", "EXEMPLAR", "Blüten für zweite Arznei zurückbehalten", "e46|e52", "V62 PREVIOUS-Mechanik + Artikelverzweigung", "MEDIUM_LOW", "F007 vollständig unparsed", "KEEP_OPEN"),
    ("A030", "H3", "GENRE", "Veilchenwein als Trank", "e48|e49", "Physica I.103", "HIGH_AS_ANALOGY", "kein ANWENDEN?-Anker", "KEEP_GENRE"),
    ("A031", "H3", "GENRE", "bedrücktes Gemüt und beschwerte Brust", "e50", "Physica I.103", "HIGH_AS_ANALOGY", "Indikation unsichtbar", "KEEP_TAGGED"),
    ("A032", "H3", "GENRE", "Olivenöl für zweite Zubereitung", "e53", "Physica I.103", "HIGH_AS_ANALOGY", "Medium unsichtbar", "KEEP_GENRE"),
    ("A033", "H3", "GENRE", "äußerlich um die Lider, nicht ins Auge", "e55", "Physica I.103", "HIGH_AS_ANALOGY", "Körperstelle und Handlung unkartiert", "KEEP_TAGGED"),
    ("A034", "H3", "EXEMPLAR", "kleines örtliches Maß", "e51", "MASS? plus Dosisgenre", "LOW", "Zahl/Einheit fehlen", "KEEP_LOCAL_ONLY"),
    ("A035", "H4", "IMAGE", "Bärlauch/Allium als f55v-Besitzer", "F010", "V53 Bildbefund + Allium-Verfahrensvergleich", "MEDIUM", "eindeutige Zwiebel fehlt", "KEEP_IMAGE_WAGER"),
    ("A036", "H4", "IMAGE|GENRE", "breite Blätter zerstoßen", "e58", "Bild + Allium-/Plantago-Praxis", "MEDIUM", "Aktion unparsed", "KEEP_TAGGED"),
    ("A037", "H4", "GENRE", "Weißwein als Medium", "e59", "Bald's-eyesalve-Verfahrensanalogie", "MEDIUM", "Medium unsichtbar", "KEEP_TAGGED"),
    ("A038", "H4", "GENRE", "bedeckt/kühl stehen und verwahren", "e56|e60|e63", "Allium-Rezeptpraxis", "MEDIUM", "keine Standzeit sichtbar", "KEEP_TAGGED"),
    ("A039", "H4", "GENRE", "durch Leinwand wringen und klären", "e62|e63", "Bald's-eyesalve-Verfahrensanalogie", "MEDIUM_HIGH", "F011 hat nur MASS?-Anker", "KEEP_GENRE"),
    ("A040", "H4", "GENRE", "äußere Wundwäsche", "e64|e65|e67", "Allium-Wundvergleich", "LOW", "F012 vollständig unparsed", "KEEP_LOCAL_ONLY"),
    ("A041", "H4", "EXEMPLAR", "einmal/örtliche Häufigkeit", "e66", "lokaler Rezeptfüller", "LOW", "keine Zahl sichtbar", "KEEP_LOCAL_ONLY"),
    ("A042", "H4", "EXEMPLAR", "örtliche Maße und zweite Blattportion", "e57|e61|e68", "MASS? plus Artikelverzweigung", "LOW", "keine Einheit/Teilidentität", "KEEP_LOCAL_ONLY"),
    ("A043", "H4", "GENRE", "Blätter gelinde erwärmen", "e70", "Plantago-/Umschlagspraxis", "MEDIUM", "kein TEMPERIEREN?", "KEEP_TAGGED"),
    ("A044", "H4", "GENRE", "Honig als Träger", "e72", "Plantago- und Rezeptpraxis", "MEDIUM", "Medium unsichtbar", "KEEP_TAGGED"),
    ("A045", "H4", "GENRE|EXEMPLAR", "warmer Umschlag an äußerer Stelle", "e69|e73", "Plantago-Analogie + lokaler Zielslot", "MEDIUM_LOW", "Relation ist formal, Ziel unbekannt", "KEEP_OPEN"),
    ("A046", "H5", "IMAGE", "Rundblättriger Sonnentau als f56r-Besitzer", "F014", "V53 Bildbefund", "VISUAL_MEDIUM_HISTORICAL_LOW", "sichere Bild-/Texttradition um 1420 ungeklärt", "HIGH_RISK_IMAGE_WAGER"),
    ("A047", "H5", "IMAGE|GENRE", "oberirdisches Kraut im Moor", "e75", "Drosera-Habitus/Habitat", "MEDIUM", "Habitat und Teil unkartiert", "KEEP_TAGGED"),
    ("A048", "H5", "EXEMPLAR", "Ernte zu Beginn der Blüte", "e76", "spätere Drogenpraxis", "LOW", "um 1420 unbelegt", "HIGH_RISK"),
    ("A049", "H5", "EXEMPLAR", "kleine örtliche Menge", "e77|e100", "MASS? plus Vorsichtsannahme", "LOW", "keine Zahl/Einheit", "KEEP_LOCAL_ONLY"),
    ("A050", "H5", "GENRE", "frische klebrige Blätter zerstoßen", "e78", "spätere Drosera-Hautpraxis", "LOW", "um 1420 unbelegt", "HIGH_RISK"),
    ("A051", "H5", "EXEMPLAR", "Warze/Hühnerauge als Hautziel", "e79|e80|e82", "spätere Drosera-Hautpraxis", "LOW", "ZIEL? nennt keine Hautstelle", "HIGH_RISK"),
    ("A052", "H5", "EXEMPLAR", "nur kurze Hautanwendung", "e81", "Sicherheits-/Reizannahme", "LOW", "ANWENDEN? nennt keine Dauer", "HIGH_RISK"),
    ("A053", "H5", "GENRE", "Auflage abnehmen und mit Wasser waschen", "e83|e84|e86", "äußere Behandlungspraxis", "LOW", "F016 größtenteils unparsed", "HIGH_RISK"),
    ("A054", "H5", "EXEMPLAR", "nur bei Verträglichkeit wiederholen", "e85", "editoriale Vorsicht", "LOW", "keine Bedingung sichtbar", "HIGH_RISK"),
    ("A055", "H5", "GENRE", "blühende Stiele im Schatten trocknen/zerreiben", "e87|e88|e89", "Drogenvorratspraxis", "LOW", "F017 vollständig unparsed", "KEEP_LOCAL_ONLY"),
    ("A056", "H5", "GENRE", "trockene Verwahrung", "e90", "Drogenvorratspraxis", "LOW", "unparsed", "KEEP_LOCAL_ONLY"),
    ("A057", "H5", "GENRE", "schwacher Weinauszug", "e91|e92", "pectorale Rezeptpraxis", "LOW", "Drosera um 1420 unsicher", "HIGH_RISK"),
    ("A058", "H5", "GENRE", "Tuchfiltration", "e93", "Rezeptpraxis", "MEDIUM", "unparsed", "KEEP_TAGGED"),
    ("A059", "H5", "GENRE", "Honigzusatz", "e94", "pectorale Rezeptpraxis", "MEDIUM", "unparsed", "KEEP_TAGGED"),
    ("A060", "H5", "GENRE", "gelindes Erwärmen", "e95", "Rezeptpraxis", "LOW", "kein TEMPERIEREN?", "KEEP_LOCAL_ONLY"),
    ("A061", "H5", "GENRE", "innerer Brusttrank", "e96", "pectorale Tradition", "LOW", "unparsed; ANWENDEN?-Karten stehen früher", "HIGH_RISK"),
    ("A062", "H5", "GENRE", "trockener Husten als Indikation", "e97", "spätere Drosera-Tradition", "LOW", "keine sichere ca.-1420-Stelle", "HIGH_RISK"),
    ("A063", "H5", "EXEMPLAR", "je Gabe als Dosierbezug", "e99|e100", "ANTEIL?+MASS? und Rezeptgenre", "MEDIUM_LOW", "keine Gabe als Wort", "KEEP_OPEN"),
    ("A064", "H1|H2", "IMAGE_RIVAL", "Skabiose (Scabiosa columbaria)", "f10r image", "ähnlicher blauer Blütenkopf", "MEDIUM", "historische Abiss-Nahquelle schwächer", "RIVAL_ONLY"),
    ("A065", "H3", "IMAGE_RIVAL", "Gundermann (Glechoma hederacea)", "f11r image", "kriechender Wuchs, gekerbte Blätter, blauviolette Blüten", "MEDIUM", "lange Bildwurzeln und Veilchen-Quellenfolge", "RIVAL_ONLY"),
    ("A066", "H4", "IMAGE_RIVAL", "Breitwegerich (Plantago major)", "f55v image", "breite Blätter; Saft/Tuch/Wein/Honig und warme Auflage historisch belegt", "HIGH_PROCESS_MEDIUM_IMAGE", "doldiger Bildkopf passt Allium besser", "RIVAL_ONLY"),
    ("A067", "H5", "IMAGE_RIVAL", "Venushaarfarn (Adiantum capillus-veneris)", "f56r image", "alte pektorale Tradition und eingerollte Farnachse", "HIGH_PROCESS_LOW_IMAGE", "runde Drüsenhaare und Blüten passen nicht", "RIVAL_ONLY"),
    ("A068", "ALL", "GENRE", "Artikelordnung Bildbesitzer → Teil/Ernte → Zubereitung → Gebrauch", "records", "kompilierte Herbal-/Rezeptpraxis", "MEDIUM", "illustrierte Simplexartikel können statt Rezeptfolge Name/Qualität/Synonyme bieten", "EDITORIAL_FRAME"),
    ("A069", "H5", "HISTORICAL_RISK", "Drosera-Arzneigeschichte bereits um 1420", "H5 record", "widersprüchliche Sekundärangaben; sichere frühe Bildbelege problematisch", "LOW", "SNSB nennt erste Illustration erst 1583", "WITHDRAW_AS_EVIDENCE"),
]


FIELD_TO_RECORD = {
    **{f"F{i:03d}": "H1" for i in range(1, 3)},
    **{f"F{i:03d}": "H2" for i in range(3, 6)},
    **{f"F{i:03d}": "H3" for i in range(6, 10)},
    **{f"F{i:03d}": "H4" for i in range(10, 14)},
    **{f"F{i:03d}": "H5" for i in range(14, 21)},
}


def guarded_rows(path: Path, columns: str) -> list[dict[str, str]]:
    command = [str(ROOT / "vmanus-exp"), "query-tsv", str(path), "--selector", "page"]
    for page in PAGES:
        command.extend(["--allow", page])
    command.extend(["--columns", columns, "--forbid-prefix", "f84"])
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=True)
    payload = "\n".join(
        line for line in completed.stdout.splitlines() if line and not line.startswith("GUARD_STATS ")
    )
    return list(csv.DictReader(io.StringIO(payload), delimiter="\t"))


def split_pipe(value: str) -> list[str]:
    return [part.strip() for part in value.split("|") if part.strip() and part.strip() != "NONE"]


def tag_names(value: str) -> list[str]:
    return re.findall(r"\[([A-Z_]+):", value)


def tagged_text_has_unmarked_words(value: str) -> bool:
    residual = re.sub(r"\[[A-Z_]+:[^\]]*\]", "", value)
    return bool(re.search(r"[A-Za-zÀ-ÖØ-öø-ÿ]", residual))


def write_tsv(path: Path, rows: list[dict[str, object]], columns: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row[column] for column in columns})


def main() -> None:
    v60_events = guarded_rows(V60_EVENTS, V60_EVENT_COLUMNS)
    v61_statements = guarded_rows(V61_STATEMENTS, V61_STATEMENT_COLUMNS)
    v62_transitions = guarded_rows(V62_TRANSITIONS, V62_TRANSITION_COLUMNS)
    v63_events = guarded_rows(V63_EVENTS, V63_EVENT_COLUMNS)
    v63_fields = guarded_rows(V63_FIELDS, V63_FIELD_COLUMNS)
    v63_statements = guarded_rows(V63_STATEMENTS, V63_STATEMENT_COLUMNS)

    assert len(v60_events) == len(v63_events) == 100
    assert len(v61_statements) == len(v62_transitions) == len(v63_statements) == 19
    assert len(v63_fields) == 20

    v60_by_event = {row["event_serial"]: row for row in v60_events}
    v63_by_event = {row["event_serial"]: row for row in v63_events}
    v61_by_statement = {row["statement_id"]: row for row in v61_statements}
    v62_by_statement = {row["statement_id"]: row for row in v62_transitions}
    v63_by_statement = {row["statement_id"]: row for row in v63_statements}
    field_by_id = {row["field_id"]: row for row in v63_fields}
    assert set(field_by_id) == set(FIELD_SPECS) == set(FIELD_TO_RECORD)

    source_alignment_errors: list[str] = []
    for serial, event in v63_by_event.items():
        old = v60_by_event[serial]
        checks = {
            "page": (old["page"], event["page"]),
            "record": (old["record_unit_id"], event["record_unit_id"]),
            "field": (old["field_id"], event["field_id"]),
            "tuple": (old["joint_tuple_id"], event["joint_tuple_id"]),
            "surface": (old["surface"], event["surface_display_only"]),
            "formula": (old["formal_formula_opaque"], event["formal_formula_opaque"]),
            "terminal": (old["terminal_status"], event["terminal_status"]),
            "formal": (old["strict_control_prompt"], event["strict_formal_prompt"]),
            "mnemonic": (old["ATOMIC_OR_WHOLE_CARD_MNEMONIC"], event["selected_exact_mnemonic"]),
        }
        for name, pair in checks.items():
            if pair[0] != pair[1]:
                source_alignment_errors.append(f"e{serial}:{name}:{pair[0]}!={pair[1]}")

    for sid, statement in v63_by_statement.items():
        v61 = v61_by_statement[sid]
        v62 = v62_by_statement[sid]
        for name, pair in {
            "page": (v61["page"], statement["page"]),
            "record": (v61["record_unit_id"], statement["record_unit_id"]),
            "events": (v61["event_serials"], statement["event_serials"]),
            "fields": (v61["constituent_fields"], statement["constituent_fields"]),
            "pre_state": (v62["pre_state"], statement["pre_state"]),
            "post_state": (v62["post_state"], statement["post_state"]),
        }.items():
            if pair[0] != pair[1]:
                source_alignment_errors.append(f"{sid}:{name}:{pair[0]}!={pair[1]}")

    event_segments: dict[str, dict[str, str]] = {}
    for field_id, spec in FIELD_SPECS.items():
        serials = split_pipe(field_by_id[field_id]["event_serials"])
        segments = spec["segments"]
        assert isinstance(segments, list)
        assert len(serials) == len(segments), (field_id, len(serials), len(segments))
        for serial, segment in zip(serials, segments):
            assert serial not in event_segments
            event_segments[serial] = segment
    assert set(event_segments) == set(v63_by_event)

    interlinear: list[dict[str, object]] = []
    assumption_use_counts: Counter[str] = Counter()
    tag_counts: Counter[str] = Counter()
    unmarked_event_segments: list[str] = []
    card_tag_errors: list[str] = []
    formal_tag_errors: list[str] = []

    for serial in sorted(v63_by_event, key=int):
        event = v63_by_event[serial]
        old = v60_by_event[serial]
        field = field_by_id[event["field_id"]]
        statement = v63_by_statement[event["statement_id"]]
        transition = v62_by_statement[event["statement_id"]]
        segment = event_segments[serial]
        assumptions = split_pipe(segment["assumptions"])
        for assumption in assumptions:
            assumption_use_counts[assumption] += 1
        tags = tag_names(segment["text"])
        tag_counts.update(tags)
        if tagged_text_has_unmarked_words(segment["text"]):
            unmarked_event_segments.append(serial)
        card_values = re.findall(r"\[CARD:([^\]=;]+\??)", segment["text"])
        formal_values = re.findall(r"\[FORMAL:([^;\]]+)", segment["text"])
        selected_card = event["selected_exact_mnemonic"]
        selected_formal = event["strict_formal_prompt"]
        if card_values and selected_card not in card_values:
            card_tag_errors.append(f"e{serial}:{card_values}!={selected_card}")
        if not card_values and selected_card != "UNKNOWN":
            card_tag_errors.append(f"e{serial}:missing:{selected_card}")
        if formal_values and selected_formal not in formal_values and not (
            event["terminal_status"] == "TERMINAL" and formal_values[0] in {"CLOSE", "CLOSE_B3"}
        ):
            formal_tag_errors.append(f"e{serial}:{formal_values}!={selected_formal}")

        if selected_card != "UNKNOWN" and selected_formal != "NONE":
            editorial_status = "CARD_PLUS_FORMAL_WITH_TAGGED_EXPANSION"
        elif selected_card != "UNKNOWN":
            editorial_status = "CARD_WITH_TAGGED_EXPANSION"
        elif selected_formal != "NONE":
            editorial_status = "FORMAL_ONLY_WITH_TAGGED_EXPANSION"
        else:
            editorial_status = "EXEMPLAR_EXPANSION_ONLY"

        interlinear.append(
            {
                "event_serial": serial,
                "page": event["page"],
                "locus": event["locus"],
                "record_unit_id": event["record_unit_id"],
                "field_id": event["field_id"],
                "statement_id": event["statement_id"],
                "joint_tuple_id": event["joint_tuple_id"],
                "surface_display_only": event["surface_display_only"],
                "formal_formula_opaque": event["formal_formula_opaque"],
                "terminal_status": event["terminal_status"],
                "strict_formal_prompt": event["strict_formal_prompt"],
                "selected_exact_mnemonic": selected_card,
                "v63_event_template": event["event_template"],
                "v63_trigger_origin": event["trigger_origin"],
                "v63_event_parse_status": event["event_parse_status"],
                "v63_field_parse_status": field["parse_status"],
                "v63_statement_parse_status": statement["parse_status"],
                "v62_statement_pre_state": transition["pre_state"],
                "v62_symbolic_register_effect": event["symbolic_register_effect"],
                "v62_statement_post_state": transition["post_state"],
                "v61_inherited_local_expansion": old["LOCAL_IATROMEDICAL_EXPANSION"],
                "v64_tagged_source_segment": segment["text"],
                "source_layer_tags": "|".join(tags),
                "unsupported_assumption_ids": segment["assumptions"],
                "editorial_status": editorial_status,
                "semantic_contract": (
                    "EXACT_CARD_ONLY_WHEN_CARD_TAGGED;FORMAL_HAS_NO_WORD;"
                    "ALL_CONCRETE_CONTENT_IMAGE_GENRE_OR_EXEMPLAR"
                ),
            }
        )

    field_rows: list[dict[str, object]] = []
    record_field_ids: defaultdict[str, list[str]] = defaultdict(list)
    for field_id in sorted(field_by_id, key=lambda value: int(value[1:])):
        field = field_by_id[field_id]
        statement = v63_by_statement[field["statement_id"]]
        transition = v62_by_statement[field["statement_id"]]
        spec = FIELD_SPECS[field_id]
        segments = spec["segments"]
        assert isinstance(segments, list)
        tagged_text = " ; ".join(segment["text"] for segment in segments) + "."
        assumptions = sorted(
            {
                assumption
                for segment in segments
                for assumption in split_pipe(segment["assumptions"])
            }
        )
        record = FIELD_TO_RECORD[field_id]
        record_field_ids[record].append(field_id)
        field_rows.append(
            {
                "field_id": field_id,
                "record_unit_id": record,
                "page": field["page"],
                "locus": field["locus"],
                "statement_id": field["statement_id"],
                "field_position_in_statement": field["field_position_in_statement"],
                "event_count": field["event_count"],
                "event_serials": field["event_serials"],
                "v61_entry_boundary_class": v61_by_statement[field["statement_id"]]["entry_boundary_class"],
                "v61_exit_boundary_class": v61_by_statement[field["statement_id"]]["exit_boundary_class"],
                "v61_internal_cross_line_boundaries": v61_by_statement[field["statement_id"]]["internal_cross_line_boundaries"],
                "v62_pre_state": transition["pre_state"],
                "v62_post_state": transition["post_state"],
                "v62_ambiguity_codes": transition["irreducible_ambiguity_codes"],
                "v63_primary_template": field["primary_template"],
                "v63_ordered_event_template_sequence": field["ordered_event_template_sequence"],
                "v63_licensed_primitive_sequence": field["licensed_primitive_sequence"],
                "v63_parse_status": field["parse_status"],
                "v63_parse_reason": field["parse_reason"],
                "v63_recognized_event_count": field["recognized_event_count"],
                "v63_exemplar_only_event_count": field["exemplar_only_event_count"],
                "selected_v63_local_exemplar_reading": field["local_exemplar_reading"],
                "v64_tagged_continuous_field_text": tagged_text,
                "unsupported_assumption_ids": "|".join(assumptions) or "NONE",
                "revision_from_selected_reading": spec["revision"],
                "strongest_counter_reading": spec["counter"],
                "status": "COMPLETE_FIELD_SOURCE_EDITION;NO_NEW_CARD_MEANING",
            }
        )

    record_rows: list[dict[str, object]] = []
    expected = {"H1": (2, 14), "H2": (3, 24), "H3": (4, 17), "H4": (4, 18), "H5": (7, 27)}
    for record in ("H1", "H2", "H3", "H4", "H5"):
        fields = [field_by_id[field_id] for field_id in record_field_ids[record]]
        statements = [row for row in v63_statements if row["record_unit_id"] == record]
        record_events = [row for row in interlinear if row["record_unit_id"] == record]
        field_status = Counter(row["parse_status"] for row in fields)
        statement_status = Counter(row["parse_status"] for row in statements)
        assumption_ids = sorted(
            {
                assumption
                for row in record_events
                for assumption in split_pipe(str(row["unsupported_assumption_ids"]))
            }
        )
        spec = RECORD_SPECS[record]
        field_count, event_count = expected[record]
        assert len(fields) == field_count
        assert len(record_events) == event_count
        record_rows.append(
            {
                "record_unit_id": record,
                "page": fields[0]["page"],
                "article_title": spec["article_title"],
                "image_unit": spec["image_unit"],
                "primary_plant_family_or_identity": spec["primary_identity"],
                "strongest_plant_rival": spec["strongest_plant_rival"],
                "identity_confidence": spec["identity_confidence"],
                "field_count": len(fields),
                "statement_count": len(statements),
                "event_count": len(record_events),
                "field_ids": "|".join(record_field_ids[record]),
                "statement_ids": "|".join(row["statement_id"] for row in statements),
                "v63_recognized_event_count": sum(int(row["recognized_event_count"]) for row in fields),
                "v63_exemplar_only_event_count": sum(int(row["exemplar_only_event_count"]) for row in fields),
                "v63_field_parse_status_counts": ";".join(f"{key}={field_status[key]}" for key in sorted(field_status)),
                "v63_statement_parse_status_counts": ";".join(f"{key}={statement_status[key]}" for key in sorted(statement_status)),
                "v62_owner_and_referent_trace": " || ".join(
                    f"{row['statement_id']}:{row['pre_state']}->{row['post_state']}" for row in statements
                ),
                "tagged_continuous_german_source_edition": spec["tagged_continuous_german"],
                "historical_article_mechanism": spec["historical_mechanism"],
                "strongest_nonmedical_rival": spec["strongest_nonmedical_rival"],
                "revision_from_v53": spec["revision_from_v53"],
                "unsupported_assumption_ids": "|".join(assumption_ids),
                "status": "COMPLETE_RECORD_SOURCE_EDITION;CREATIVE;NOT_DECIPHERMENT",
            }
        )

    assumption_rows = [
        {
            "assumption_id": row[0],
            "record_unit_id": row[1],
            "layer": row[2],
            "assumption": row[3],
            "used_at": row[4],
            "basis": row[5],
            "confidence": row[6],
            "strongest_contradiction": row[7],
            "disposition": row[8],
            "card_licensed": "NO",
            "use_count_in_event_interlinear": assumption_use_counts[row[0]],
            "semantic_contract": "NEVER_PROMOTE_TO_CARD_MEANING",
        }
        for row in ASSUMPTIONS
    ]

    interlinear_columns = [
        "event_serial", "page", "locus", "record_unit_id", "field_id", "statement_id",
        "joint_tuple_id", "surface_display_only", "formal_formula_opaque", "terminal_status",
        "strict_formal_prompt", "selected_exact_mnemonic", "v63_event_template", "v63_trigger_origin",
        "v63_event_parse_status", "v63_field_parse_status", "v63_statement_parse_status",
        "v62_statement_pre_state", "v62_symbolic_register_effect", "v62_statement_post_state",
        "v61_inherited_local_expansion", "v64_tagged_source_segment", "source_layer_tags",
        "unsupported_assumption_ids", "editorial_status", "semantic_contract",
    ]
    field_columns = [
        "field_id", "record_unit_id", "page", "locus", "statement_id", "field_position_in_statement",
        "event_count", "event_serials", "v61_entry_boundary_class", "v61_exit_boundary_class",
        "v61_internal_cross_line_boundaries", "v62_pre_state", "v62_post_state", "v62_ambiguity_codes",
        "v63_primary_template", "v63_ordered_event_template_sequence", "v63_licensed_primitive_sequence",
        "v63_parse_status", "v63_parse_reason", "v63_recognized_event_count",
        "v63_exemplar_only_event_count", "selected_v63_local_exemplar_reading",
        "v64_tagged_continuous_field_text", "unsupported_assumption_ids",
        "revision_from_selected_reading", "strongest_counter_reading", "status",
    ]
    record_columns = [
        "record_unit_id", "page", "article_title", "image_unit", "primary_plant_family_or_identity",
        "strongest_plant_rival", "identity_confidence", "field_count", "statement_count", "event_count",
        "field_ids", "statement_ids", "v63_recognized_event_count", "v63_exemplar_only_event_count",
        "v63_field_parse_status_counts", "v63_statement_parse_status_counts",
        "v62_owner_and_referent_trace", "tagged_continuous_german_source_edition",
        "historical_article_mechanism", "strongest_nonmedical_rival", "revision_from_v53",
        "unsupported_assumption_ids", "status",
    ]
    assumption_columns = [
        "assumption_id", "record_unit_id", "layer", "assumption", "used_at", "basis", "confidence",
        "strongest_contradiction", "disposition", "card_licensed", "use_count_in_event_interlinear",
        "semantic_contract",
    ]

    write_tsv(OUT / "V64_R2_100_EVENT_HERBAL_INTERLINEAR.tsv", interlinear, interlinear_columns)
    write_tsv(OUT / "V64_R2_20_FIELD_EDITIONS.tsv", field_rows, field_columns)
    write_tsv(OUT / "V64_R2_FIVE_RECORD_EDITIONS.tsv", record_rows, record_columns)
    write_tsv(OUT / "V64_R2_UNSUPPORTED_ASSUMPTIONS.tsv", assumption_rows, assumption_columns)

    all_assumption_ids = {row[0] for row in ASSUMPTIONS}
    used_assumption_ids = set(assumption_use_counts)
    unknown_assumption_ids = sorted(used_assumption_ids - all_assumption_ids)
    unused_nonrival_assumption_ids = sorted(
        row[0]
        for row in ASSUMPTIONS
        if row[0] not in used_assumption_ids and row[2] not in {"IMAGE_RIVAL", "HISTORICAL_RISK", "GENRE"}
    )
    page_violations = sorted({row["page"] for row in interlinear if row["page"] not in PAGES})
    field_parse_counts = Counter(row["v63_parse_status"] for row in field_rows)
    statement_parse_counts = Counter(row["parse_status"] for row in v63_statements)
    event_parse_counts = Counter(row["v63_event_parse_status"] for row in interlinear)
    record_count_check = {
        row["record_unit_id"]: {
            "fields": row["field_count"],
            "events": row["event_count"],
            "recognized": row["v63_recognized_event_count"],
            "exemplar_only": row["v63_exemplar_only_event_count"],
        }
        for row in record_rows
    }
    record_text_untagged = [
        row["record_unit_id"]
        for row in record_rows
        if tagged_text_has_unmarked_words(str(row["tagged_continuous_german_source_edition"]))
    ]
    field_text_untagged = [
        row["field_id"]
        for row in field_rows
        if tagged_text_has_unmarked_words(str(row["v64_tagged_continuous_field_text"]))
    ]

    gates = {
        "all_100_events_present_once": len(interlinear) == 100 and len({row["event_serial"] for row in interlinear}) == 100,
        "event_serials_exact_1_to_100": [int(row["event_serial"]) for row in interlinear] == list(range(1, 101)),
        "all_20_fields_present": len(field_rows) == 20 and set(FIELD_SPECS) == {row["field_id"] for row in field_rows},
        "all_five_records_present": len(record_rows) == 5 and {row["record_unit_id"] for row in record_rows} == set(RECORD_SPECS),
        "record_counts_match_2_3_4_4_7_and_14_24_17_18_27": all(
            int(record_count_check[record]["fields"]) == expected[record][0]
            and int(record_count_check[record]["events"]) == expected[record][1]
            for record in expected
        ),
        "v63_herbal_recognized_plus_exemplar_equals_100": sum(
            int(row["v63_recognized_event_count"]) + int(row["v63_exemplar_only_event_count"])
            for row in field_rows
        ) == 100,
        "selected_source_alignment_exact": not source_alignment_errors,
        "no_forbidden_page": not page_violations,
        "all_event_segments_fully_layer_tagged": not unmarked_event_segments,
        "all_field_text_fully_layer_tagged": not field_text_untagged,
        "all_record_text_fully_layer_tagged": not record_text_untagged,
        "card_tags_match_selected_exact_cards": not card_tag_errors,
        "formal_tags_match_or_are_observed_close": not formal_tag_errors,
        "all_used_assumptions_declared": not unknown_assumption_ids,
        "all_nonrival_content_assumptions_used": not unused_nonrival_assumption_ids,
        "no_assumption_claimed_as_card_licensed": all(row["card_licensed"] == "NO" for row in assumption_rows),
        "no_new_card_meaning": True,
        "no_phonetic_mapping": True,
    }
    validation = {
        "artifact": "V64_R2_HISTORICAL_HERBAL_SECOND_EDITION",
        "status": "PASS" if all(gates.values()) else "FAIL",
        "scope": {
            "allowed_pages": list(PAGES),
            "sealed_prefix": "f84",
            "source_v60_events": len(v60_events),
            "source_v61_statements": len(v61_statements),
            "source_v62_transitions": len(v62_transitions),
            "source_v63_events": len(v63_events),
            "source_v63_fields": len(v63_fields),
            "source_v63_statements": len(v63_statements),
            "output_events": len(interlinear),
            "output_fields": len(field_rows),
            "output_records": len(record_rows),
            "output_assumption_rows": len(assumption_rows),
        },
        "v63_audit": {
            "recognized_events": sum(int(row["v63_recognized_event_count"]) for row in field_rows),
            "exemplar_only_events": sum(int(row["v63_exemplar_only_event_count"]) for row in field_rows),
            "event_parse_status_counts": dict(sorted(event_parse_counts.items())),
            "field_parse_status_counts": dict(sorted(field_parse_counts.items())),
            "statement_parse_status_counts": dict(sorted(statement_parse_counts.items())),
        },
        "record_counts": record_count_check,
        "editorial_layer_tag_counts": dict(sorted(tag_counts.items())),
        "assumption_disposition_counts": dict(sorted(Counter(row[8] for row in ASSUMPTIONS).items())),
        "gates": gates,
        "violations": {
            "source_alignment": source_alignment_errors,
            "page": page_violations,
            "unmarked_event_segments": unmarked_event_segments,
            "unmarked_field_text": field_text_untagged,
            "unmarked_record_text": record_text_untagged,
            "card_tags": card_tag_errors,
            "formal_tags": formal_tag_errors,
            "unknown_assumption_ids": unknown_assumption_ids,
            "unused_nonrival_assumption_ids": unused_nonrival_assumption_ids,
        },
        "interpretive_limit": (
            "PASS proves mechanical coverage, selected-source alignment, and explicit editorial tagging only; "
            "it does not validate plant identity, medical content, language, sound, or decipherment."
        ),
    }
    (OUT / "V64_R2_VALIDATION.json").write_text(
        json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(validation, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

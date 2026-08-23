# Kompaktes Werkstatt-Codebuch der zehn Seiten

## Modus wählen

- **PROSA:** Herbal/Bio → Besitzer setzen, Quellenprogramm laden, zwanzig Rollen komponieren, Karte rendern.
- **ASTRO:** Instrument/Namensraum/Platz wählen, opake Gruppen kopieren, nur lokal lesen.

## Zwanzig Prosa-Rollen

| Rolle | Kurzbedeutung | Karten-/Quellenbasis |
|---|---|---|
| OWNER_SELECT | sichtbaren Seiten-/Szenenbesitzer setzen | Bild oder Layout |
| PART_SELECT | Pflanzenteil oder örtlichen Gegenstand wählen | Herbal-Quellenprogramm |
| MATERIAL_ADD | Medium, Portion oder Zusatz zugeben | AIN/TY/HO/DL + Quellenfüllung |
| MEASURE | Sollmaß oder Stufe eintragen | AIIN/IIN |
| SET | laufenden Arbeitsposten ansetzen | OK |
| CUT_CRUSH | Pflanzenstoff zerteilen oder zerstoßen | Herbal-Ganzkarte |
| GRADE | kurze, längere oder volle Stufe setzen | E/EE/EEE |
| HEAT | wärmen oder temperieren | CHK |
| SETTLE | ruhen oder absetzen | SH/SHED |
| PASS_STRAIN | durchlassen, auswringen oder seihen | CKH/CKHE/CFH/CPH |
| WASH | waschen oder spülen | gelernte WASH-Familie |
| DRAIN | örtlich abführen oder ausgießen | AR/CKH/SK |
| COLLECT_STORE | sammeln, auffangen oder verwahren | SOLK/TALAM |
| TARGET | örtliche Zielstelle setzen | AL |
| TRANSFER | Posten umsetzen | CHD/CHED |
| CONTINUE | Folge oder Fortsetzung markieren | OT/OL |
| READY | Bereitschaft prüfen | CTH |
| USE_APPLY | Mittel gebrauchen oder äußerlich anwenden | DAN + Quellenfüllung |
| FASTEN | örtlich befestigen | LDDY |
| CLOSE | lokalen Schritt schließen | lizenzierte Terminalkarte |

## 43 Karten-/Kürzelwerte

| Eintrag | Form | Wert | Werkstattrolle | Lernart |
|---|---|---|---|---|
| ROOT_AIIN | AIIN | Sollwert | MEASURE | PRODUCTIVE_COMPOSITION |
| ROOT_AIN | AIN | Anteil | MATERIAL_ADD | PRODUCTIVE_COMPOSITION |
| ROOT_IIN | IIN | Stufe | MEASURE | PRODUCTIVE_COMPOSITION |
| ROOT_AL | AL | Ziel | TARGET | PRODUCTIVE_COMPOSITION |
| ROOT_AR | AR | Quelle | PART_SELECT | PRODUCTIVE_COMPOSITION |
| ROOT_AIR | AIR | Lauf | PASS_STRAIN | PRODUCTIVE_COMPOSITION |
| ROOT_OK | OK | ansetzen | SET | PRODUCTIVE_COMPOSITION |
| ROOT_OL | OL | weiter | CONTINUE | PRODUCTIVE_COMPOSITION |
| ROOT_OT | OT | danach | CONTINUE | PRODUCTIVE_COMPOSITION |
| ROOT_OR | OR | Ansatz | SET | PRODUCTIVE_COMPOSITION |
| ROOT_Y | Y | dies | PART_SELECT | PRODUCTIVE_COMPOSITION |
| ROOT_E | E | kurz | GRADE | PRODUCTIVE_COMPOSITION |
| ROOT_EE | EE | länger | GRADE | PRODUCTIVE_COMPOSITION |
| ROOT_EEE | EEE | vollständig | GRADE | PRODUCTIVE_COMPOSITION |
| ROOT_CLOSE | CLOSE | Ende | CLOSE | PRODUCTIVE_COMPOSITION |
| ROOT_CHD | CHD | umsetzen | TRANSFER | PRODUCTIVE_COMPOSITION |
| ROOT_CTH | CTH | bereit | READY | PRODUCTIVE_COMPOSITION |
| ROOT_CKH | CKH | Durchlass | PASS_STRAIN | PRODUCTIVE_COMPOSITION |
| ROOT_CKHE | CKHE | trennen | PASS_STRAIN | PRODUCTIVE_COMPOSITION |
| ROOT_CHK | CHK | wärmen | HEAT | PRODUCTIVE_COMPOSITION |
| ROOT_SHED | SHED | absetzen | SETTLE | PRODUCTIVE_COMPOSITION |
| ROOT_SOLK | SOLK | sammeln | COLLECT_STORE | PRODUCTIVE_COMPOSITION |
| ROOT_HO | HO | Zutat | MATERIAL_ADD | PRODUCTIVE_COMPOSITION |
| ROOT_CHEO | CHEO | Auszug | COLLECT_STORE | PRODUCTIVE_COMPOSITION |
| ROOT_KCH | KCH | bearbeiten | CUT_CRUSH | PRODUCTIVE_COMPOSITION |
| ROOT_TY | TY | Teil | PART_SELECT | PRODUCTIVE_COMPOSITION |
| ROOT_SH | SH | halten | SETTLE | PRODUCTIVE_COMPOSITION |
| ROOT_CHEEY | CHEEY | Ergebnis | READY | PRODUCTIVE_COMPOSITION |
| N01_CFH | cfhy | auswringen | PASS_STRAIN | LEARN_EXACT_WHOLE_OR_REGISTER_SPLIT |
| N02_CPH | cphy|ocphy | nachseihen | PASS_STRAIN | LEARN_EXACT_WHOLE_OR_REGISTER_SPLIT |
| N03_PARTITION | ches|chety|chty | teilen | PART_SELECT | LEARN_EXACT_WHOLE_OR_REGISTER_SPLIT |
| N04_HO | cho|sho|tshol | Zutat | MATERIAL_ADD | LEARN_EXACT_WHOLE_OR_REGISTER_SPLIT |
| N05_DCHE | dchey | Wurzelteil | PART_SELECT | LEARN_EXACT_WHOLE_OR_REGISTER_SPLIT |
| N06_PREV | dchol|schol | vorher | CONTINUE | LEARN_EXACT_WHOLE_OR_REGISTER_SPLIT |
| N07_WASH | lshedy|lsho|rshedy | waschen | WASH | LEARN_EXACT_WHOLE_OR_REGISTER_SPLIT |
| N08_LDDY | qokylddy | befestigen | FASTEN | LEARN_EXACT_WHOLE_OR_REGISTER_SPLIT |
| N09_SK | skar | ausgießen | DRAIN | LEARN_EXACT_WHOLE_OR_REGISTER_SPLIT |
| N10_DAN | sotodan | anwenden | USE_APPLY | LEARN_EXACT_WHOLE_OR_REGISTER_SPLIT |
| N11_DL | dl | Zusatz | MATERIAL_ADD | LEARN_EXACT_WHOLE_OR_REGISTER_SPLIT |
| N12_TALAM | talam | verwahren | COLLECT_STORE | LEARN_EXACT_WHOLE_OR_REGISTER_SPLIT |
| S01_DAIN | dain | Tuch|Portion | PASS_STRAIN|MATERIAL_ADD | LEARN_EXACT_WHOLE_OR_REGISTER_SPLIT |
| S02_ODY | ody | kühlen|markieren | GRADE|ASTRO_LOCAL_MARK | LEARN_EXACT_WHOLE_OR_REGISTER_SPLIT |
| S03_OS | os | Gefäß|Feld | OWNER_SELECT | LEARN_EXACT_WHOLE_OR_REGISTER_SPLIT |

## 44 Quellenwörter

| ID | Register | Wort | Einheiten | Herkunft |
|---|---|---|---|---|
| H_R01 | HERBAL | Wasser | H1,H5 | RECURRING_CARD_ANCHORED |
| H_R02 | HERBAL | Auszugsflüssigkeit | H3,H4,H5 | WORKSHOP_FUNCTION_CLASS |
| H_R03 | HERBAL | Trägerstoff | H2,H3 | WORKSHOP_FUNCTION_CLASS |
| H_R04 | HERBAL | Bindestoff | H4,H5 | WORKSHOP_FUNCTION_CLASS |
| H_R05 | HERBAL | Restteil | H1 | WORKSHOP_FUNCTION_CLASS |
| H_R06 | HERBAL | dosiertes Mittel | H1,H3,H5 | WORKSHOP_FUNCTION_CLASS |
| H_R07 | HERBAL | streichfähiges Mittel | H2 | WORKSHOP_FUNCTION_CLASS |
| H_R08 | HERBAL | äußerliche Anwendung | H3 | WORKSHOP_FUNCTION_CLASS |
| H_R09 | HERBAL | Waschung | H4,H5 | RECURRING_CARD_ANCHORED |
| H_R10 | HERBAL | gebundene Anwendung | H2,H4,H5 | WORKSHOP_FUNCTION_CLASS |
| H_R11 | HERBAL | Tuch | H2,H3,H4,H5 | RECURRING_CARD_ANCHORED |
| B_B01 | BATH_SERVICE | Badende | B1,B2,B3,B4 | VISIBLE_OWNER_ANCHORED |
| B_B02 | BATH_SERVICE | Becken | B1,B2,B3,B4 | VISIBLE_OWNER_ANCHORED |
| B_B03 | BATH_SERVICE | Badwasser | B1,B2,B3,B4,B5,B6 | VISIBLE_OWNER_ANCHORED |
| B_B04 | BATH_SERVICE | Kräuterzusatz | B1,B2 | RECURRING_CARD_ANCHORED |
| B_B05 | BATH_SERVICE | Badwärme | B1,B2,B3,B4,B5 | RECURRING_CARD_ANCHORED |
| B_B06 | BATH_SERVICE | Badezeit | B1,B2,B5 | RECURRING_CARD_ANCHORED |
| B_B07 | BATH_SERVICE | Körperstelle | B1,B4 | VISIBLE_OWNER_ANCHORED |
| B_B08 | BATH_SERVICE | Teilbad | B1,B2 | VISIBLE_OWNER_ANCHORED |
| B_B09 | BATH_SERVICE | Tuch | B3,B4,B6 | RECURRING_CARD_ANCHORED |
| B_B10 | BATH_SERVICE | Umschlag | B4 | RECURRING_CARD_ANCHORED |
| B_B11 | BATH_SERVICE | Seihgang | B1,B2,B3,B4,B6 | RECURRING_CARD_ANCHORED |
| B_B12 | BATH_SERVICE | Einlass | B2,B4,B6 | VISIBLE_OWNER_ANCHORED |
| B_B13 | BATH_SERVICE | Ablauf | B1,B2,B3,B4,B5 | VISIBLE_OWNER_ANCHORED |
| B_B14 | BATH_SERVICE | Wasserlauf | B2,B4,B6 | VISIBLE_OWNER_ANCHORED |
| B_B15 | BATH_SERVICE | Auffangbecken | B3,B4 | VISIBLE_OWNER_ANCHORED |
| B_B16 | BATH_SERVICE | Dienststation | B4,B5,B6 | VISIBLE_OWNER_ANCHORED |
| B_B17 | BATH_SERVICE | Arbeitsstelle | B4,B5,B6 | VISIBLE_OWNER_ANCHORED |
| C_A01 | CELESTIAL | Wahlrad | A1 | VISIBLE_OWNER_ANCHORED |
| C_A02 | CELESTIAL | Himmelssektor | A1 | VISIBLE_OWNER_ANCHORED |
| C_A03 | CELESTIAL | Sternort | A1,A2 | VISIBLE_OWNER_ANCHORED |
| C_A04 | CELESTIAL | Bedingungsfeld | A1 | VISIBLE_OWNER_ANCHORED |
| C_A05 | CELESTIAL | Ringrubrik | A1 | VISIBLE_OWNER_ANCHORED |
| C_A06 | CELESTIAL | Himmelszeichen | A1,A2 | LOCAL_NOMENCLATOR_ONLY |
| C_A07 | CELESTIAL | Kalenderzeichen | A1,A3 | LOCAL_NOMENCLATOR_ONLY |
| C_A08 | CELESTIAL | Wahlzeichen | A1 | LOCAL_NOMENCLATOR_ONLY |
| C_A09 | CELESTIAL | Sterntafel | A2 | VISIBLE_OWNER_ANCHORED |
| C_A10 | CELESTIAL | 28er Feld | A2,A3 | VISIBLE_OWNER_ANCHORED |
| C_A11 | CELESTIAL | Rosettenrad | A3 | VISIBLE_OWNER_ANCHORED |
| C_A12 | CELESTIAL | Wetterzeichen | A3 | LOCAL_NOMENCLATOR_ONLY |
| C_A13 | CELESTIAL | Lichtzeichen | A3 | LOCAL_NOMENCLATOR_ONLY |
| C_A14 | CELESTIAL | Zeitzeichen | A3 | LOCAL_NOMENCLATOR_ONLY |
| C_A15 | CELESTIAL | Eigenschaftszeichen | A3 | LOCAL_NOMENCLATOR_ONLY |
| C_A16 | CELESTIAL | Ortsschlüssel | A1,A2,A3 | LOCAL_NOMENCLATOR_ONLY |

## Acht Astro-Regeln

1. **OPEN_INSTRUMENT** — aktives Rad, Paneel oder Rosetteninstrument öffnen
2. **SELECT_NAMESPACE** — nur den örtlichen Namensraum dieses Teilbilds laden
3. **SELECT_LOCAL_SLOT** — sichtbaren lokalen Sektor-, Stern- oder Feldplatz wählen
4. **COPY_OPAQUE_GROUPS** — alle Gruppen dieses Platzes in gegebener lokaler Folge kopieren
5. **READ_WITH_LOCAL_KEY** — Wert nur mit dem Meisterschlüssel dieses Namensraums lesen
6. **RESET_AT_NAMESPACE_CHANGE** — beim Rad-/Paneel-/Rosettenwechsel vollständig neu beginnen
7. **PRESERVE_NO_ORIENTATION** — keinen Startpunkt, Drehsinn oder Rang ergänzen
8. **NO_CROSSPAGE_JOIN** — keinen Schlüssel zwischen A1, A2 und A3 übertragen

## Zwölf Prosa-Schreibregeln

1. **CHOOSE_REGISTER** — Herbal oder Biological wählen; die Inhaltsnomenklaturen nie vermischen.
2. **SET_OWNER** — Am Recordbeginn und nach sichtbarer Szenenlücke den kleinsten Bildbesitzer setzen.
3. **LOAD_SOURCE_PROGRAM** — Nur die endliche Quellenwortliste des aktiven Records laden.
4. **SELECT_OBJECT** — Pflanzenteil, Figur, Becken oder Dienststation aus Besitzer plus Quellenprogramm wählen.
5. **ADD_MATERIAL** — Medium, Portion oder Zusatz vor der zugehörigen Prozesskarte einsetzen.
6. **SET_MEASURE** — AIIN/IIN nur als Maß-, Stufen- oder Wertslot des aktiven Programms lesen.
7. **RUN_PROCESS** — Ansetzen, zerteilen, wärmen, ruhen, waschen oder seihen in Kartenreihenfolge ausführen.
8. **APPLY_GRADE** — E/EE/EEE erst nach der Prozessbasis als kurz/länger/voll lesen.
9. **MOVE_LOCALLY** — Ziel, Umsetzen, Durchlass und Ablauf nur innerhalb des sichtbaren Besitzers führen.
10. **USE_OR_STORE** — Herbal kann Mittel gebrauchen/verwahren; Bio kann lokal anwenden/befestigen/entleeren.
11. **CLOSE_BY_CARD** — Nur eine lizenzierte Terminalkarte schließt; sichtbares dy allein genügt nicht.
12. **WRAP_AND_RENDER** — Zeilenumbruch nach Platz, dann exakte Karte im Renderer der Hand kopieren.

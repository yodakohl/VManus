# Fehlerbuch für den Werkstattlehrling

Jede Lektion zeigt vier echte Aussagen. Der Meister lässt genau einen Fehler zu,
lässt den Lehrling die konkrete Folge benennen und setzt dann die kurze Regel daneben.

## E01_WRONG_OWNER — OWNER

Merksatz: **Erst schauen, dann schreiben.**

Fehler: beim sichtbaren Stationswechsel den alten Bildbesitzer weiterführen. Folge: die richtige Handlung wird am falschen Becken, Pflanzenteil oder Gerät ausgeführt. Reparatur: OWNER beim sichtbaren Wechsel umsetzen und TARGET neu prüfen.

- `B2-S007` · sichtbar `dshedy`
  - falsche Wahl: OWNER=B2_UPPER_PAIRED_BASINS_AND_CYLINDER statt B2_MIDDLE_LEFT_DEVICE_AND_INLINE_NODE
  - richtig: SHED+E+CLOSE
- `B3-S005` · sichtbar `schedy`
  - falsche Wahl: OWNER=B3_UPPER_MARGIN_OPEN_FAN_STATION statt B3_MIDDLE_MARGIN_ROUND_VESSEL_STATION
  - richtig: CHD+CLOSE
- `B4-S011` · sichtbar `saiin cheky okeeol okain chdy sol lkedy`
  - falsche Wahl: OWNER=B4_MAIN_ARCH_LINKED_PAIR statt B4_MAIN_LEFT_OPEN_FRINGE_STATION
  - richtig: AIIN | CHK+E+Y | OK+EE+OL | OK+AIN | CHD+Y | OL | L+E+CLOSE
- `B2-S011` · sichtbar `okain char okain qokeedy`
  - falsche Wahl: OWNER=B2_MIDDLE_LEFT_DEVICE_AND_INLINE_NODE statt B2_MIDDLE_RIGHT_AMBIGUOUS_STATION
  - richtig: OK+AIN | AR | OK+AIN | OK+EE+CLOSE

## E02_ACTIVE_PREVIOUS_SWAP — ACTIVE_PREVIOUS

Merksatz: **Der Stein ist jetzt; die Kerbe war vorher.**

Fehler: den Vorposten statt des laufenden Postens bearbeiten. Folge: eine bereits abgelegte Fraktion wird erneut behandelt und der neue Posten bleibt liegen. Reparatur: ACTIVE und PREVIOUS als zwei getrennte Kerben führen.

- `H1-S001` · sichtbar `dchey cthoor char chty os chair otytchol oky daiin etyd`
  - falsche Wahl: ACTIVE=Vorposten H1-2 statt Arbeitsposten H1-1
  - richtig: DCHE+Y | CTH+OR | AR | PARTITION+TY | OS | AIR | OT+TY+OL | OK+Y | AIIN | E+TY
- `H2-S002` · sichtbar `qotchor chor otol chol cholor chol daiin dar`
  - falsche Wahl: ACTIVE=Vorposten H2-1 statt Arbeitsposten H2-1
  - richtig: OT+OR | OR | OT+OL | OL | OL+OR | OL | AIIN | AR
- `H3-S002` · sichtbar `shoyty`
  - falsche Wahl: ACTIVE=Vorposten H3-2 statt Arbeitsposten H3-1
  - richtig: HO+Y+TY
- `H4-S003` · sichtbar `ykaiin cheoar cheeky oldy`
  - falsche Wahl: ACTIVE=Vorposten H4-1 statt Arbeitsposten H4-1
  - richtig: Y+AIIN | CHEO+AR | CHK+EE+Y | OL+CLOSE

## E03_SOURCE_TARGET_SWAP — AR_AL

Merksatz: **AR heraus, AL hinan.**

Fehler: Quelle AR und Ziel AL vertauschen. Folge: der Schreiber entnimmt aus der Zielschale oder bringt den Posten an die Vorratsquelle. Reparatur: AR immer als Ausgangsadresse, AL immer als Zieladresse lesen.

- `H3-S001` · sichtbar `tshol schoal cfhy shfydaiin cphy shey tchody`
  - falsche Wahl: AR↔AL
  - richtig: HO+L | HO+AL | CFH+Y | SH+AIIN | CPH+Y | CHEEY | HO+CLOSE
- `H4-S002` · sichtbar `daiin chedy talam`
  - falsche Wahl: AR↔AL
  - richtig: AIIN | CHD+Y | AL+AM
- `H5-S001` · sichtbar `chochor cho chodaly daiin sho kchol otchor choky dal`
  - falsche Wahl: AR↔AL
  - richtig: HO+OR | HO | HO+AL+Y | AIIN | HO | KCH+OL | OT+OR | OK+Y | AL
- `B1-S002` · sichtbar `okaiin kair okal sar ol kain olkain al ol rol dl olor ol sheckhal daiin qokeedal daiin chckhy schedy`
  - falsche Wahl: AR↔AL
  - richtig: OK+AIIN | AIR | OK+AL | AR | OL | AIN | OL+AIN | AL | OL | OL | LOCAL_WHOLE | OL+OR | OL | CKH+E+AL | AIIN | OK+EE+AL | AIIN | CKH+Y | CHD+CLOSE

## E04_QUANTITY_CLASS_SWAP — AIIN_AIN_IIN

Merksatz: **Wert, Teil, Stufe sind drei Dinge.**

Fehler: Sollwert, Portion und Prozessstufe als dieselbe Mengenangabe behandeln. Folge: eine Portion wird zur Stufe oder ein Sollstand zur abzutrennenden Menge. Reparatur: AIIN=Sollwert, AIN=Portion und IIN=Stufe getrennt halten.

- `H2-S001` · sichtbar `ycheor cthy chor cthaiin qoctholy dy chy taiin shy`
  - falsche Wahl: AIIN→AIN, AIN→IIN oder IIN→AIIN
  - richtig: Y+CHEO+OR | CTH+Y | OR | CTH+AIIN | CTH+OL+Y | Y | Y | AIIN | Y
- `H3-S003` · sichtbar `dchol chy kchy dy daiin`
  - falsche Wahl: AIIN→AIN, AIN→IIN oder IIN→AIIN
  - richtig: PREV+OL | Y | KCH+Y | Y | AIIN
- `H4-S001` · sichtbar `qokaiin chaiin ykain ykan ody`
  - falsche Wahl: AIIN→AIN, AIN→IIN oder IIN→AIIN
  - richtig: OK+AIIN | AIIN | Y+AIN | Y+AIN | ODY
- `H5-S006` · sichtbar `otchey keol daiin`
  - falsche Wahl: AIIN→AIN, AIN→IIN oder IIN→AIIN
  - richtig: OT+Y | E+OL | AIIN

## E05_ORDER_SWAP — OL_OT

Merksatz: **OL bleibt, OT springt.**

Fehler: Fortsetzung OL und nächsten Posten OT vertauschen. Folge: der laufende Ansatz wird zu früh verlassen oder ein neuer Posten nie begonnen. Reparatur: OL behält den Gang, OT öffnet den folgenden Gang.

- `H1-S002` · sichtbar `qokchy qotchol chol cthy`
  - falsche Wahl: OL↔OT
  - richtig: OK+Y | OT+OL | OL | CTH+Y
- `H3-S004` · sichtbar `qotchy okchol cthy dy`
  - falsche Wahl: OL↔OT
  - richtig: OT+Y | OK+OL | CTH+Y | Y
- `H4-S004` · sichtbar `aiin okal oltchy or y orain`
  - falsche Wahl: OL↔OT
  - richtig: AIIN | OK+AL | OL+CTH+Y | OR | Y | OR+AIN
- `H5-S002` · sichtbar `schol choy choky cheeckhody`
  - falsche Wahl: OL↔OT
  - richtig: PREV+OL | HO+Y | OK+Y | EE+CKH+HO+CLOSE

## E06_GRADE_SWAP — E_EE_EEE

Merksatz: **Ein Strich kurz, zwei länger, drei voll.**

Fehler: kurzen, längeren und vollen Grad gleich ausführen. Folge: Kontakt, Halten oder Tabellenstufe dauert falsch lang. Reparatur: E kurz, EE länger, EEE vollständig nur innerhalb der lizenzierten Familie.

- `H5-S003` · sichtbar `sh cho kchey qokokchy`
  - falsche Wahl: E→EE, EE→EEE oder EEE→E
  - richtig: SH | HO | KCH+E+Y | OK+OK+Y
- `B1-S001` · sichtbar `qokedy`
  - falsche Wahl: E→EE, EE→EEE oder EEE→E
  - richtig: OK+E+CLOSE
- `B2-S003` · sichtbar `qokain dy qokeedy`
  - falsche Wahl: E→EE, EE→EEE oder EEE→E
  - richtig: OK+AIN | Y | OK+EE+CLOSE
- `B3-S001` · sichtbar `olkeedy`
  - falsche Wahl: E→EE, EE→EEE oder EEE→E
  - richtig: SOLK+EE+CLOSE

## E07_CURRENT_CLOSE_SWAP — Y_CLOSE

Merksatz: **Y bleibt in der Hand; Schluss legt ab.**

Fehler: laufenden Posten Y und lokale Schlusskarte vertauschen. Folge: der Arbeitsposten wird vorzeitig geschlossen oder eine fertige Zelle bleibt offen. Reparatur: Y hält ACTIVE verfügbar; nur die registrierte Schlusskarte beendet die Zelle.

- `H2-S003` · sichtbar `oykchor shor chor chy kaiiin dy chodaiin`
  - falsche Wahl: Y↔CLOSE
  - richtig: Y+KCH+OR | OR | OR | Y | IIN | Y | HO+AIIN
- `H5-S004` · sichtbar `okchy chokcheo kchal`
  - falsche Wahl: Y↔CLOSE
  - richtig: OK+Y | OK+CHEO | KCH+AL
- `B1-S003` · sichtbar `qol sshkchdy`
  - falsche Wahl: Y↔CLOSE
  - richtig: OL | SH+KCH+CHD+CLOSE
- `B2-S001` · sichtbar `dchedy`
  - falsche Wahl: Y↔CLOSE
  - richtig: CHD+CLOSE

## E08_RENDERER_AS_WORD — SCRIBE_FRAME

Merksatz: **Die Handform spricht nicht mit.**

Fehler: q/s/ch/d/t-Schreiberrahmen als zusätzliche Handlung lesen. Folge: vor die echte Karte wird ein nie diktierter Arbeitsschritt eingeschoben. Reparatur: zuerst registrierte Oberfläche zum Kartenkörper normalisieren, dann Bedeutung lesen.

- `H5-S005` · sichtbar `sho chokchy kchoar sotodan`
  - falsche Wahl: Schreiberrahmen als eigenes Verb
  - richtig: HO | OK+Y | CHEO+AR | OT+DAN
- `B1-S004` · sichtbar `chedy ol shedy`
  - falsche Wahl: Schreiberrahmen als eigenes Verb
  - richtig: CHD+Y | OL | SHED+E+CLOSE
- `B2-S002` · sichtbar `qolchedy`
  - falsche Wahl: Schreiberrahmen als eigenes Verb
  - richtig: OL+CHD+CLOSE
- `B3-S002` · sichtbar `qotal chkeedy`
  - falsche Wahl: Schreiberrahmen als eigenes Verb
  - richtig: OT+AL | CHK+EE+CLOSE

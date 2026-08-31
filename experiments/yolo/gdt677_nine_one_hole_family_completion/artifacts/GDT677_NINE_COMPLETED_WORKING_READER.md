# GDT677 — nine newly completed V51 lines

Each Voynich token remains visible in the TSV companion. These are concrete replaceable working readings, not claimed plaintext.

## f106r.23 · MIXED_RECORD

**ZL3b:** `ychedy qckhedy dair al qokedy shecphy qokchy otedy dar aror`

**Arbeitslesung:** Getrocknete Droge, fertig · Arzneikompositum bis Mittelstufe bereiten und abschließen · abgemessene Fraktion II · Rohstoffklasse I · heiß, Mittelstufe, abgeschlossen · bis Mittelstufe eingeweichtes und abgeschlossenes Arzneikompositum · heiß-trocken, Anfangsstufe · kalter Ansatz, Mittelstufe, abgeschlossen · abgemessene Fraktion I · eine Portion der ersten Drogenfraktion.

**Geschlossen:** `aror` = eine Portion der ersten Drogenfraktion (`AR_FRACTION_I+OR_PORTION`)

**Aktionen:** 2 (qckhedy)

**Audit:** GDT677 closes aror; Nach dar ergibt sich abgemessene Fraktion I gefolgt von einer Portion derselben Fraktion.

## f107r.40 · NOMINAL_REGISTER

**ZL3b:** `lolkaiin chey qokaiin chal aiin okaiin olkar otair okal okal`

**Arbeitslesung:** Holzstoff, heiß auf Stufe III · trocken, Mittelstufe · heiß, Grad III · Rohstoffklasse I, trocken, Anfangsstufe · Menge III · heiß, Grad III, im Ansatz · erste erhitzte Drogenfraktion im Ansatz · zweite kalte Drogenfraktion im Ansatz · Rohstoffklasse I im heißen Anfangsansatz · Rohstoffklasse I im heißen Anfangsansatz.

**Geschlossen:** `lolkaiin` = Holzstoff, heiß auf Stufe III (`LOL_WOOD_MATERIAL+K_HOT+AIIN_III`)

**Aktionen:** NONE (NONE)

**Audit:** GDT677 closes lolkaiin; Vor Trocken-, Heiß- und Fraktionsfeldern eine direkte Stoff-/Stufenbezeichnung.

## f112r.36 · QUANTITY_LABEL

**ZL3b:** `sain ol checkhy olchain okeey olam`

**Arbeitslesung:** Saatgut, Charge II · Ansatz/Gut · trockenes Arzneikompositum, Anfangsstufe · Holzdrogenansatz, trocken auf Stufe II · heißer Ansatz, Endstufe · ein Maß Ansatz-/Drogenmaterial.

**Geschlossen:** `olchain` = Holzdrogenansatz, trocken auf Stufe II (`O_PREP+L_WOOD+CH_DRY+AIN_II`)

**Aktionen:** NONE (NONE)

**Audit:** GDT677 closes olchain; Zwischen trockenem Kompositum und heißem Endansatz ein abgestufter trockener Zwischenansatz.

## f56r.6 · MIXED_RECORD

**ZL3b:** `ykcho dy dchey keey daiin y`

**Arbeitslesung:** Hieraus einen heiß-trockenen Ansatz bereiten · Qualitäts-/Wertfeld geschlossen · abgemessene Trockendroge der Mittelstufe, abgeschlossen · heiß, Endstufe · Grad/Maß III · Eintrag abgeschlossen.

**Geschlossen:** `ykcho` = hieraus einen heiß-trockenen Ansatz bereiten (`Y_REFERENCE+KCHO_HOT_DRY_PREP`)

**Aktionen:** 1 (ykcho)

**Audit:** GDT677 closes ykcho; Der Ansatzschritt eröffnet die Zeile; die folgenden Schluss- und Messfelder beschreiben sein Ergebnis.

## f77r.38 · ACTION_SEQUENCE

**ZL3b:** `pol shedy qoeedy qokaiin chcphey qol ltaiin shedy qol`

**Arbeitslesung:** Pulverstoff · feucht, Mittelstufe, abgeschlossen · vollständig fertiggestellten Ansatz nehmen · heiß, Grad III · bis Mittelstufe getrocknetes und abgeschlossenes Arzneikompositum · Drogenstoff zugeben · Holzdroge, kalt auf Stufe III · feucht, Mittelstufe, abgeschlossen · Drogenstoff zugeben.

**Geschlossen:** `ltaiin` = Holzdroge, kalt auf Stufe III (`L_WOOD+T_COLD+AIIN_III`)

**Aktionen:** 3|6|9 (qoeedy|qol|qol)

**Audit:** GDT677 closes ltaiin; Zwischen Zugebe- und Feuchtfeldern als konkret bezeichnetes Zugabegut lesbar.

## f80v.27 · NOMINAL_REGISTER

**ZL3b:** `pshol kain olkar shey qokain dal oltaiin okain shal qoty`

**Arbeitslesung:** Eingeweichter Pulverstoff · heiß, Grad II · erste erhitzte Drogenfraktion im Ansatz · feucht, Mittelstufe · heiß, Grad II · abgemessene Rohstoffmenge I · Holzdrogenansatz, kalt auf Stufe III · heiß, Grad II, im Zubereitungsrahmen · Rohstoffklasse I, feucht, Anfangsstufe · kalt, Anfangsstufe.

**Geschlossen:** `oltaiin` = Holzdrogenansatz, kalt auf Stufe III (`O_PREP+L_WOOD+T_COLD+AIIN_III`)

**Aktionen:** NONE (NONE)

**Audit:** GDT677 closes oltaiin; Im Heiß-/Kaltregister sauberer Gegenpol zu den benachbarten Heizstufen.

## f86v5.2 · ACTION_SEQUENCE

**ZL3b:** `losair yteody qokar shy qokar shor qopchol tal ol ytol otam otam`

**Arbeitslesung:** Zweite Fraktion des Drogenholzpostens · kalte Zubereitung, abgeschlossen · heiße Drogenfraktion I · feucht, Anfangsstufe · heiße Drogenfraktion I · Blüten-/Fruchtstand · getrockneten Pulverstoff nehmen · Rohstoffklasse I, kalt, Anfangsstufe · Ansatz/Gut · hiervon den Drogenstoff abkühlen · ein Maß kalten Ansatzes · ein Maß kalten Ansatzes.

**Geschlossen:** `losair` = zweite Fraktion des Drogenholzpostens (`LOS_WOOD_BATCH+AIR_FRACTION_II`)

**Aktionen:** 7|10 (qopchol|ytol)

**Audit:** GDT677 closes losair; RF1b trennt los air und wählt zwei bereits gelernte Ganzwörter; lo+sair bleibt als sichtbarer Samenabsud-Rivale erhalten.

## f86v5.24 · MIXED_RECORD

**ZL3b:** `oar aiin ykain okal kchody chckhy otaiin olkar otaiin`

**Arbeitslesung:** Drogenfraktion I im Ansatz · Menge III · hiervon auf Stufe II erhitzen · Rohstoffklasse I im heißen Anfangsansatz · fertiggestellter heiß-trockener Ansatz · trockenes Arzneikompositum, Anfangsstufe · kalt, Grad III, im Zubereitungsrahmen · erste erhitzte Drogenfraktion im Ansatz · kalt, Grad III, im Zubereitungsrahmen.

**Geschlossen:** `kchody` = fertiggestellter heiß-trockener Ansatz (`K_HOT+CH_DRY+O_PREP+DY_FINISHED`)

**Aktionen:** 3 (ykain)

**Audit:** GDT677 closes kchody; Nominales Zustandsregister; Ergebnislesung ist lokaler als ein neuer Imperativ.

## f86v6.5 · NOMINAL_REGISTER

**ZL3b:** `tar lol chol olkar daiin chear or otshey qokar opchey taiky qotar`

**Arbeitslesung:** Kalte Drogenfraktion I · Holzstoff · Trockengut · erste erhitzte Drogenfraktion im Ansatz · Grad/Maß III · trockene Fraktion I · Drogenportion · kalt-feuchter Ansatz, Mittelstufe · heiße Drogenfraktion I · Trockenpulver-Ansatz, Form I · kalt angesetzte Charge, leicht angewärmt · kalte Drogenfraktion I.

**Geschlossen:** `taiky` = kalt angesetzte Charge, leicht angewärmt (`T_COLD+[AI_OPAQUE_LOCAL]+K_HOT+Y_START_OR_CLOSE`)

**Aktionen:** NONE (NONE)

**Audit:** GDT677 closes taiky; Zwischen Trockenpulver-Ansatz Form I und kalter Fraktion I; praktisch brauchbar, aber niedrigste Sicherheit.

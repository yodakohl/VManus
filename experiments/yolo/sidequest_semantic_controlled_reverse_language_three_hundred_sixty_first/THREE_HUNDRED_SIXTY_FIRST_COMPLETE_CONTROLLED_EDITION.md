# Kontrollierte, vollständig rücklesbare Werkstattsprache

Freies Deutsch bleibt als Lesefassung erhalten. Die zweite Zeile benutzt
genau 159 Slot-Wert-Phrasen und lässt sich ohne Synonymwahl zurücklesen.

## H1

### H1-S001

**Frei:** Nimm einen Wurzelteil der abgebildeten Pflanze. Richte daraus mit Material aus der bezeichneten Quelle einen Ansatz her, zerkleinere ihn, gib ihn ins Gefäß und führe Wasser zu. Führe den folgenden Teil weiter, setze ihn ein, prüfe das Sollmaß und behalte den kleinen Rest.

**Kontrolliert:** `BEZUG[Wurzelteil] · SCHLUSS[Bereitansatz] · BEZUG[Quelle] · MASS[Zerkleinern] · BEZUG[Gefäß] · TRANSFER[Wasserzulauf] · BEZUG[Folgeteilfortsetzung] · ZIEL[Einsetzen] · MASS[Sollmaß] · SCHLUSS[Kurzrest]`

**Zurückgelesen:** Wurzelteil → Bereitansatz → Quelle → Zerkleinern → Gefäß → Wasserzulauf → Folgeteilfortsetzung → Einsetzen → Sollmaß → Kurzrest

### H1-S002

**Frei:** Setze den zurückbehaltenen Posten ein, führe ihn im folgenden Gang weiter und halte ihn bereit.

**Kontrolliert:** `ZIEL[Einsetzen] · BEZUG[Folgefortsetzung] · BEZUG[Fortsetzung] · SCHLUSS[Bereit]`

**Zurückgelesen:** Einsetzen → Folgefortsetzung → Fortsetzung → Bereit

## H2

### H2-S001

**Frei:** Nimm den laufenden Auszugsansatz und halte ihn bereit. Stelle den Ansatz auf sein Sollmaß; führe den Folgeposten weiter und behalte dabei denselben Posten um die Maßangabe aktiv.

**Kontrolliert:** `BEZUG[Auszugsansatz] · SCHLUSS[Bereit] · BEZUG[Ansatz] · MASS[Bereitsollmaß] · BEZUG[Folgefortsetzungsposten] · BEZUG[Diesposten] · BEZUG[Diesposten] · MASS[Sollmaß] · BEZUG[Diesposten]`

**Zurückgelesen:** Auszugsansatz → Bereit → Ansatz → Bereitsollmaß → Folgefortsetzungsposten → Diesposten → Diesposten → Sollmaß → Diesposten

### H2-S002

**Frei:** Eröffne den Folgeansatz, führe denselben Ansatz als Fortsetzungsansatz weiter und nimm das Sollmaß aus der bezeichneten Quelle.

**Kontrolliert:** `BEZUG[Folgeansatz] · BEZUG[Ansatz] · BEZUG[Folgefortsetzung] · BEZUG[Fortsetzung] · BEZUG[Fortsetzungsansatz] · BEZUG[Fortsetzung] · MASS[Sollmaß] · BEZUG[Quelle]`

**Zurückgelesen:** Folgeansatz → Ansatz → Folgefortsetzung → Fortsetzung → Fortsetzungsansatz → Fortsetzung → Sollmaß → Quelle

### H2-S003

**Frei:** Richte den Ansatz im Gefäß her, halte ihn als laufenden Posten aktiv, setze die gebundene Arbeitsstufe und füge die Zutat im Sollmaß hinzu.

**Kontrolliert:** `BEZUG[Gefäßansatz] · BEZUG[Ansatz] · BEZUG[Ansatz] · BEZUG[Diesposten] · SCHLUSS[Bindestufe] · BEZUG[Diesposten] · MASS[Zutatsollmaß]`

**Zurückgelesen:** Gefäßansatz → Ansatz → Ansatz → Diesposten → Bindestufe → Diesposten → Zutatsollmaß

## H3

### H3-S001

**Frei:** Bringe das Blütenkraut an die Arbeitsstelle, wringe es aus, lasse es die vorgeschriebene Zeit stehen und seihe es nochmals. Nimm nur den Klarauszug ab und schließe den Schritt.

**Kontrolliert:** `BEZUG[Blütenkraut] · ZIEL[Zieleingabe] · TRANSFER[Auswringen] · TRANSFER[Standzeit] · TRANSFER[Nachseihen] · TRANSFER[Klarauszug] · TRANSFER[Rücknahmeschluss]`

**Zurückgelesen:** Blütenkraut → Zieleingabe → Auswringen → Standzeit → Nachseihen → Klarauszug → Rücknahmeschluss

### H3-S002

**Frei:** Halte einen weiteren Zutatteil für den folgenden Gang bereit.

**Kontrolliert:** `BEZUG[Zutatfolgeteil]`

**Zurückgelesen:** Zutatfolgeteil

### H3-S003

**Frei:** Nimm die Fortsetzung des vorigen Gangs, halte den aktuellen Posten gebunden und miss sein Sollmaß.

**Kontrolliert:** `BEZUG[Vorfortsetzung] · BEZUG[Diesposten] · SCHLUSS[Bindeposten] · BEZUG[Diesposten] · MASS[Sollmaß]`

**Zurückgelesen:** Vorfortsetzung → Diesposten → Bindeposten → Diesposten → Sollmaß

### H3-S004

**Frei:** Wechsle zum Folgeposten, setze die Fortsetzung ein und halte diesen Posten bereit.

**Kontrolliert:** `BEZUG[Folgeposten] · ZIEL[Fortsetzungseinsatz] · SCHLUSS[Bereit] · BEZUG[Diesposten]`

**Zurückgelesen:** Folgeposten → Fortsetzungseinsatz → Bereit → Diesposten

## H4

### H4-S001

**Frei:** Stelle das Sollmaß ein, prüfe es und teile den Posten in eine erste und eine zweite Portion. Nimm beide aus diesem Arbeitsschritt und schließe ihn.

**Kontrolliert:** `MASS[Sollstellung] · MASS[Sollmaß] · MASS[Postenportion] · MASS[Postenzweitportion] · TRANSFER[Rücknahmeschluss]`

**Zurückgelesen:** Sollstellung → Sollmaß → Postenportion → Postenzweitportion → Rücknahmeschluss

### H4-S002

**Frei:** Überführe die abgemessene Menge und verwahre sie.

**Kontrolliert:** `MASS[Sollmaß] · TRANSFER[Umsetzen] · SCHLUSS[Verwahren]`

**Zurückgelesen:** Sollmaß → Umsetzen → Verwahren

### H4-S003

**Frei:** Nimm das Sollmaß des Postens aus dem gewonnenen Auszug, halte es länger warm und schließe den fortgesetzten Schritt.

**Kontrolliert:** `MASS[Postensollmaß] · TRANSFER[Auszugnahme] · ZUSTAND[Langwärme] · BEZUG[Fortschluss]`

**Zurückgelesen:** Postensollmaß → Auszugnahme → Langwärme → Fortschluss

### H4-S004

**Frei:** Setze das Sollmaß an der bezeichneten Stelle ein. Führe die Zubereitung dort weiter, halte den Ansatz als aktuellen Posten und verwende eine Ansatzportion.

**Kontrolliert:** `MASS[Sollmaß] · ZIEL[Zieleinsatz] · BEZUG[Fortsetzungszubereitung] · BEZUG[Ansatz] · BEZUG[Diesposten] · MASS[Ansatzportion]`

**Zurückgelesen:** Sollmaß → Zieleinsatz → Fortsetzungszubereitung → Ansatz → Diesposten → Ansatzportion

## H5

### H5-S001

**Frei:** Richte einen Zutatenansatz her. Setze eine weitere Zutat an die bezeichnete Stelle, miss sie und führe sie gebunden weiter. Eröffne danach den Folgeansatz, setze ihn ein und bringe ihn an die Stelle.

**Kontrolliert:** `BEZUG[Zutatenansatz] · BEZUG[Zutat] · ZIEL[Zutatstelle] · MASS[Sollmaß] · BEZUG[Zutat] · BEZUG[Bindefortsetzung] · BEZUG[Folgeansatz] · ZIEL[Einsetzen] · ZIEL[Stelle]`

**Zurückgelesen:** Zutatenansatz → Zutat → Zutatstelle → Sollmaß → Zutat → Bindefortsetzung → Folgeansatz → Einsetzen → Stelle

### H5-S002

**Frei:** Nimm die Fortsetzung des vorigen Postens, setze die Zutat ein, trage sie auf und schließe den Schritt.

**Kontrolliert:** `BEZUG[Vorfortsetzung] · BEZUG[Zutatposten] · ZIEL[Einsetzen] · SCHLUSS[Auftragsschluss]`

**Zurückgelesen:** Vorfortsetzung → Zutatposten → Einsetzen → Auftragsschluss

### H5-S003

**Frei:** Nimm einen Teil der abgebildeten Pflanze und die Zutat, binde den Posten kurz und setze ihn erneut ein.

**Kontrolliert:** `BEZUG[Pflanzenteil] · BEZUG[Zutat] · SCHLUSS[Kurzbindeposten] · ZIEL[Wiedereinsatz]`

**Zurückgelesen:** Pflanzenteil → Zutat → Kurzbindeposten → Wiedereinsatz

### H5-S004

**Frei:** Setze den Posten ein, gib Auszug hinzu und binde beides an der Zielstelle.

**Kontrolliert:** `ZIEL[Einsetzen] · MASS[Auszugzugabe] · ZIEL[Zielbindung]`

**Zurückgelesen:** Einsetzen → Auszugzugabe → Zielbindung

### H5-S005

**Frei:** Gib die Zutat hinzu, setze sie ein, binde die Zutat aus der bezeichneten Quelle und gebrauche den Posten.

**Kontrolliert:** `BEZUG[Zutat] · ZIEL[Einsetzen] · BEZUG[Quellenzutatbindung] · ZIEL[Gebrauchen]`

**Zurückgelesen:** Zutat → Einsetzen → Quellenzutatbindung → Gebrauchen

### H5-S006

**Frei:** Nimm den Folgeposten, führe ihn kurz gebunden weiter und prüfe das Sollmaß.

**Kontrolliert:** `BEZUG[Folgeposten] · BEZUG[Kurzbindefortsetzung] · MASS[Sollmaß]`

**Zurückgelesen:** Folgeposten → Kurzbindefortsetzung → Sollmaß

## B1

### B1-S001

**Frei:** Bei GEMEINSAMES_BEHANDLUNGSBECKEN: Lass ihn kurz einwirken.

**Kontrolliert:** `ZUSTAND[Kurzkontakt]`

**Zurückgelesen:** Kurzkontakt

### B1-S002

**Frei:** Bei GEMEINSAMES_BEHANDLUNGSBECKEN: Stelle das Sollmaß ein; dann führe durch den Beckenlauf; dann setze an der Zielstelle ein; dann nimm aus der bezeichneten Quelle; dann führe den laufenden Gang fort; dann nimm eine Portion; dann nimm einen weiteren Anteil; dann binde die bezeichnete Stelle; dann führe den laufenden Gang fort; dann schließe am nächsten Abschnitt an; dann gib den Zusatz zu; dann führe denselben Ansatz weiter; dann führe den laufenden Gang fort; dann führe ihn kurz durch die Zielpassage; dann arbeite nach dem vorgeschriebenen Maß; dann setze ihn lange am Ziel ein; dann arbeite nach dem vorgeschriebenen Maß; dann leite den Posten hindurch; dann führe den Posten über.

**Kontrolliert:** `MASS[Sollstellung] · TRANSFER[Beckenlauf] · ZIEL[Zieleinsatz] · BEZUG[Quelle] · BEZUG[Fortsetzung] · MASS[Portion] · MASS[Folgeportion] · ZIEL[Stelle] · BEZUG[Fortsetzung] · BEZUG[Anschluss] · MASS[Zusatz] · BEZUG[Fortsetzungsansatz] · BEZUG[Fortsetzung] · TRANSFER[Zielkurzpassage] · MASS[Sollmaß] · ZUSTAND[Ziellanghalt] · MASS[Sollmaß] · TRANSFER[durchleiten] · TRANSFER[überführen]`

**Zurückgelesen:** Sollstellung → Beckenlauf → Zieleinsatz → Quelle → Fortsetzung → Portion → Folgeportion → Stelle → Fortsetzung → Anschluss → Zusatz → Fortsetzungsansatz → Fortsetzung → Zielkurzpassage → Sollmaß → Ziellanghalt → Sollmaß → durchleiten → überführen

### B1-S003

**Frei:** Bei GEMEINSAMES_BEHANDLUNGSBECKEN: Führe den laufenden Gang fort; dann setze um und schließe den Schritt.

**Kontrolliert:** `BEZUG[Fortsetzung] · TRANSFER[Umsetzschluss]`

**Zurückgelesen:** Fortsetzung → Umsetzschluss

### B1-S004

**Frei:** Bei GEMEINSAMES_BEHANDLUNGSBECKEN: Setze den laufenden Posten um; dann führe den laufenden Gang fort; dann lass ihn kurz absetzen.

**Kontrolliert:** `TRANSFER[Umsetzen] · BEZUG[Fortsetzung] · TRANSFER[Kurzabsetzung]`

**Zurückgelesen:** Umsetzen → Fortsetzung → Kurzabsetzung

### B1-S005

**Frei:** Bei GEMEINSAMES_BEHANDLUNGSBECKEN: Führe ihn weiter.

**Kontrolliert:** `BEZUG[weiterführen]`

**Zurückgelesen:** weiterführen

### B1-S006

**Frei:** Bei GEMEINSAMES_BEHANDLUNGSBECKEN: Gib einen Anteil zu; dann leite den Posten hindurch; dann gib den Zusatz zu; dann halte die Zielmarke ein.

**Kontrolliert:** `MASS[Zugabe] · TRANSFER[durchleiten] · MASS[Zusatz] · ZIEL[Zielmarke]`

**Zurückgelesen:** Zugabe → durchleiten → Zusatz → Zielmarke

### B1-S007

**Frei:** Bei GEMEINSAMES_BEHANDLUNGSBECKEN: Setze einen neuen Posten ein.

**Kontrolliert:** `ZIEL[Neueinsatz]`

**Zurückgelesen:** Neueinsatz

### B1-S008

**Frei:** Bei GEMEINSAMES_BEHANDLUNGSBECKEN: Halte diesen Posten aktiv; dann führe den laufenden Gang fort; dann wärme ihn kurz; dann führe den laufenden Gang fort; dann lass ihn kurz absetzen.

**Kontrolliert:** `BEZUG[Diesposten] · BEZUG[Fortsetzung] · ZUSTAND[Kurzwärme] · BEZUG[Fortsetzung] · TRANSFER[Kurzabsetzung]`

**Zurückgelesen:** Diesposten → Fortsetzung → Kurzwärme → Fortsetzung → Kurzabsetzung

### B1-S009

**Frei:** Bei GEMEINSAMES_BEHANDLUNGSBECKEN: Lass ihn kurz einwirken.

**Kontrolliert:** `ZUSTAND[Kurzkontakt]`

**Zurückgelesen:** Kurzkontakt

### B1-S010

**Frei:** Bei GEMEINSAMES_BEHANDLUNGSBECKEN: Lass ihn kurz einwirken.

**Kontrolliert:** `ZUSTAND[Kurzkontakt]`

**Zurückgelesen:** Kurzkontakt

### B1-S011

**Frei:** Bei GEMEINSAMES_BEHANDLUNGSBECKEN: Leite den Posten hindurch; dann setze den Posten ein.

**Kontrolliert:** `TRANSFER[durchleiten] · ZIEL[Einsetzen]`

**Zurückgelesen:** durchleiten → Einsetzen

### B1-S012

**Frei:** Bei GEMEINSAMES_BEHANDLUNGSBECKEN: Führe einen Waschgang aus; dann lass ihn kurz einwirken; dann führe einen Waschgang aus.

**Kontrolliert:** `TRANSFER[Waschgang] · ZUSTAND[Kurzkontakt] · TRANSFER[Waschgang]`

**Zurückgelesen:** Waschgang → Kurzkontakt → Waschgang

### B1-S013

**Frei:** Bei GEMEINSAMES_BEHANDLUNGSBECKEN: Führe einen Waschgang aus.

**Kontrolliert:** `TRANSFER[Waschgang]`

**Zurückgelesen:** Waschgang

### B1-S014

**Frei:** Bei GEMEINSAMES_BEHANDLUNGSBECKEN: Setze den laufenden Posten um; dann führe auf dem Weg weiter; dann führe ihn am Ziel ab; dann führe den laufenden Gang fort; dann wechsle zur folgenden Quelle.

**Kontrolliert:** `TRANSFER[Umsetzen] · BEZUG[Weiterweg] · TRANSFER[Zielabführung] · BEZUG[Fortsetzung] · BEZUG[Folgequelle]`

**Zurückgelesen:** Umsetzen → Weiterweg → Zielabführung → Fortsetzung → Folgequelle

### B1-S015

**Frei:** Bei GEMEINSAMES_BEHANDLUNGSBECKEN: Nimm einen kleinen Teil; dann führe den vorigen Posten über.

**Kontrolliert:** `MASS[Kurzteil] · TRANSFER[Rücktransfer]`

**Zurückgelesen:** Kurzteil → Rücktransfer

### B1-S016

**Frei:** Bei GEMEINSAMES_BEHANDLUNGSBECKEN: Setze an der Zielstelle ein; dann lass ihn länger einwirken; dann führe den laufenden Gang fort; dann lass ihn kurz absetzen.

**Kontrolliert:** `ZIEL[Zieleinsatz] · ZUSTAND[Langkontakt] · BEZUG[Fortsetzung] · TRANSFER[Kurzabsetzung]`

**Zurückgelesen:** Zieleinsatz → Langkontakt → Fortsetzung → Kurzabsetzung

### B1-S017

**Frei:** Bei GEMEINSAMES_BEHANDLUNGSBECKEN: Binde die bezeichnete Stelle; dann führe ihn kurz weiter; dann führe ihn über.

**Kontrolliert:** `ZIEL[Stelle] · BEZUG[Kurzfortgang] · TRANSFER[Transfer]`

**Zurückgelesen:** Stelle → Kurzfortgang → Transfer

### B1-S018

**Frei:** Bei GEMEINSAMES_BEHANDLUNGSBECKEN: Stelle das Auffanggefäß bereit; dann halte ihn kurz; dann stelle die Arbeitsstufe ein; dann sammle ihn lange.

**Kontrolliert:** `TRANSFER[Auffanggefäß] · ZUSTAND[Kurzhalt] · MASS[Arbeitsstufe] · TRANSFER[Langsammlung]`

**Zurückgelesen:** Auffanggefäß → Kurzhalt → Arbeitsstufe → Langsammlung

### B1-S019

**Frei:** Bei GEMEINSAMES_BEHANDLUNGSBECKEN: Lass ihn kurz absetzen.

**Kontrolliert:** `TRANSFER[Kurzabsetzung]`

**Zurückgelesen:** Kurzabsetzung

### B1-S020

**Frei:** Bei GEMEINSAMES_BEHANDLUNGSBECKEN: Wärme ihn kurz; dann lass ihn hindurch.

**Kontrolliert:** `ZUSTAND[Kurzwärme] · TRANSFER[durchlassen]`

**Zurückgelesen:** Kurzwärme → durchlassen

### B1-S021

**Frei:** Bei GEMEINSAMES_BEHANDLUNGSBECKEN: Binde die bezeichnete Stelle.

**Kontrolliert:** `ZIEL[Stelle]`

**Zurückgelesen:** Stelle

## B2

### B2-S001

**Frei:** Bei PAARBECKEN_MIT_MITTELZYLINDER: Führe den Posten über.

**Kontrolliert:** `TRANSFER[überführen]`

**Zurückgelesen:** überführen

### B2-S002

**Frei:** Bei PAARBECKEN_MIT_MITTELZYLINDER: Führe ihn weiter.

**Kontrolliert:** `BEZUG[weiterführen]`

**Zurückgelesen:** weiterführen

### B2-S003

**Frei:** Bei PAARBECKEN_MIT_MITTELZYLINDER: Gib einen Anteil zu; dann halte diesen Posten aktiv; dann lass ihn lange einwirken.

**Kontrolliert:** `MASS[Zugabe] · BEZUG[Diesposten] · ZUSTAND[Langkontakt]`

**Zurückgelesen:** Zugabe → Diesposten → Langkontakt

### B2-S004

**Frei:** Bei PAARBECKEN_MIT_MITTELZYLINDER: Setze an der Zielstelle ein; dann führe ihn durch die Abführpassage; dann führe ihn ab; dann lass ihn länger einwirken; dann ziehe die getrennte Fraktion ab.

**Kontrolliert:** `ZIEL[Zieleinsatz] · TRANSFER[Abführpassage] · TRANSFER[Abführung] · ZUSTAND[Langkontakt] · TRANSFER[Trennabzug]`

**Zurückgelesen:** Zieleinsatz → Abführpassage → Abführung → Langkontakt → Trennabzug

### B2-S005

**Frei:** Bei PAARBECKEN_MIT_MITTELZYLINDER: Setze an der Zielstelle ein; dann sammle ihn bis zur Sollmenge; dann leite den Posten hindurch; dann stelle das Sollmaß ein; dann stelle das Sollmaß ein; dann setze den nächsten Durchgang an; dann wärme ihn lange; dann ziehe ihn ab.

**Kontrolliert:** `ZIEL[Zieleinsatz] · TRANSFER[Sollsammlung] · TRANSFER[durchleiten] · MASS[Sollstellung] · BEZUG[Folgevorbereitung] · ZUSTAND[Langwärmen] · TRANSFER[abziehen]`

**Zurückgelesen:** Zieleinsatz → Sollsammlung → durchleiten → Sollstellung → Folgevorbereitung → Langwärmen → abziehen

### B2-S006

**Frei:** Bei PAARBECKEN_MIT_MITTELZYLINDER: Führe ihn länger im Folgegang weiter; dann setze an der Zielstelle ein; dann führe ihn kurz hindurch; dann setze den Posten ein.

**Kontrolliert:** `BEZUG[Langfolge] · ZIEL[Zieleinsatz] · TRANSFER[Kurzpassage] · ZIEL[Einsetzen]`

**Zurückgelesen:** Langfolge → Zieleinsatz → Kurzpassage → Einsetzen

### B2-S007

**Frei:** Bei ZWISCHENGERAET_MIT_KNOTEN: Setze den vorigen Posten ab und schließe.

**Kontrolliert:** `TRANSFER[Vorabsetzschluss]`

**Zurückgelesen:** Vorabsetzschluss

### B2-S008

**Frei:** Bei ZWISCHENGERAET_MIT_KNOTEN: Arbeite danach nach dem nächsten Maß; dann setze den Quellposten ein; dann lass ihn kurz absetzen.

**Kontrolliert:** `MASS[Folgemaß] · ZIEL[Quelleinsatz] · TRANSFER[Kurzabsetzung]`

**Zurückgelesen:** Folgemaß → Quelleinsatz → Kurzabsetzung

### B2-S009

**Frei:** Bei ZWISCHENGERAET_MIT_KNOTEN: Lass danach den nächsten Posten absetzen.

**Kontrolliert:** `TRANSFER[Folgeabsetzen]`

**Zurückgelesen:** Folgeabsetzen

### B2-S010

**Frei:** Bei ZWISCHENGERAET_MIT_KNOTEN: Lass ihn länger einwirken; dann setze den Posten ein; dann führe zum Auslass; dann nimm den Klarauszug.

**Kontrolliert:** `ZUSTAND[Langkontakt] · ZIEL[Einsetzen] · TRANSFER[Auslass] · TRANSFER[Klarauszug]`

**Zurückgelesen:** Langkontakt → Einsetzen → Auslass → Klarauszug

### B2-S011

**Frei:** Bei AMBIGUER_RECHTER_POSTEN: Gib einen Anteil zu; dann nimm aus der bezeichneten Quelle; dann gib einen Anteil zu; dann lass ihn lange einwirken.

**Kontrolliert:** `MASS[Zugabe] · BEZUG[Quelle] · MASS[Zugabe] · ZUSTAND[Langkontakt]`

**Zurückgelesen:** Zugabe → Quelle → Zugabe → Langkontakt

### B2-S012

**Frei:** Bei AMBIGUER_RECHTER_POSTEN: Nimm das abzuführende Gut. Neuer lokaler Posten: Bei MEHRPLATZ_BADBECKEN: Nimm den Klarauszug; dann bereite ihn kurz vor; dann lass ihn länger einwirken; dann ziehe den klaren Anteil ab; dann arbeite nach dem vorgeschriebenen Maß; dann halte diesen Posten aktiv; dann setze ihn vollständig ein.

**Kontrolliert:** `TRANSFER[Abführgut] · TRANSFER[Klarauszug] · ZUSTAND[Kurzvorbereitung] · ZUSTAND[Langkontakt] · TRANSFER[Klarabzug] · MASS[Sollmaß] · BEZUG[Diesposten] · ZIEL[Volleinsatz]`

**Zurückgelesen:** Abführgut → Klarauszug → Kurzvorbereitung → Langkontakt → Klarabzug → Sollmaß → Diesposten → Volleinsatz

### B2-S013

**Frei:** Bei MEHRPLATZ_BADBECKEN: Führe ihn ab.

**Kontrolliert:** `TRANSFER[abführen]`

**Zurückgelesen:** abführen

### B2-S014

**Frei:** Bei MEHRPLATZ_BADBECKEN: Ziehe ihn aus der Quelle ab.

**Kontrolliert:** `TRANSFER[Quellabzug]`

**Zurückgelesen:** Quellabzug

### B2-S015

**Frei:** Bei RAND_ZUFUEHR_ABFUEHRSTATIONEN: Nimm danach den klaren Ablauf; dann lass ihn lange einwirken.

**Kontrolliert:** `BEZUG[Folgeklarlauf] · ZUSTAND[Langkontakt]`

**Zurückgelesen:** Folgeklarlauf → Langkontakt

### B2-S016

**Frei:** Bei RAND_ZUFUEHR_ABFUEHRSTATIONEN: Binde die bezeichnete Stelle; dann führe ihn von der Quelle ab; dann teile den Posten; dann arbeite nach dem vorgeschriebenen Maß; dann führe ihn länger im Folgegang weiter; dann stelle das Sollmaß ein; dann lass ihn kurz einwirken; dann führe ihn zu.

**Kontrolliert:** `ZIEL[Stelle] · TRANSFER[Quellabführung] · MASS[teilen] · MASS[Sollmaß] · BEZUG[Langfolge] · MASS[Sollstellung] · ZUSTAND[Kurzkontakt] · TRANSFER[Zuführung]`

**Zurückgelesen:** Stelle → Quellabführung → teilen → Sollmaß → Langfolge → Sollstellung → Kurzkontakt → Zuführung

### B2-S017

**Frei:** Bei RAND_ZUFUEHR_ABFUEHRSTATIONEN: Halte den zugeführten Posten kurz am Ziel; dann schließe den Schritt am Ziel ab.

**Kontrolliert:** `ZUSTAND[Zielkurzhalt] · ZIEL[Zielschluss]`

**Zurückgelesen:** Zielkurzhalt → Zielschluss

### B2-S018

**Frei:** Bei RAND_ZUFUEHR_ABFUEHRSTATIONEN: Lass ihn lange einwirken.

**Kontrolliert:** `ZUSTAND[Langkontakt]`

**Zurückgelesen:** Langkontakt

### B2-S019

**Frei:** Bei RAND_ZUFUEHR_ABFUEHRSTATIONEN: Setze ab und schließe.

**Kontrolliert:** `TRANSFER[Absetzschluss]`

**Zurückgelesen:** Absetzschluss

### B2-S020

**Frei:** Bei RAND_ZUFUEHR_ABFUEHRSTATIONEN: Führe die lange Folgestufe aus.

**Kontrolliert:** `BEZUG[Langfolgestufe]`

**Zurückgelesen:** Langfolgestufe

### B2-S021

**Frei:** Bei RAND_ZUFUEHR_ABFUEHRSTATIONEN: Lass ihn lange einwirken.

**Kontrolliert:** `ZUSTAND[Langkontakt]`

**Zurückgelesen:** Langkontakt

### B2-S022

**Frei:** Bei RAND_ZUFUEHR_ABFUEHRSTATIONEN: Führe ihn ab.

**Kontrolliert:** `TRANSFER[Abführung]`

**Zurückgelesen:** Abführung

## B3

### B3-S001

**Frei:** Bei OFFENER_FAECHERZULAUF: Sammle ihn lange.

**Kontrolliert:** `TRANSFER[Langsammlung]`

**Zurückgelesen:** Langsammlung

### B3-S002

**Frei:** Bei OFFENER_FAECHERZULAUF: Führe ihn danach dorthin; dann wärme ihn lange.

**Kontrolliert:** `ZIEL[Folgeziel] · ZUSTAND[Langwärmen]`

**Zurückgelesen:** Folgeziel → Langwärmen

### B3-S003

**Frei:** Bei OFFENER_FAECHERZULAUF: Halte diesen Posten aktiv; dann arbeite nach dem vorgeschriebenen Maß; dann halte diesen Posten aktiv; dann führe ihn ab.

**Kontrolliert:** `BEZUG[Diesposten] · MASS[Sollmaß] · BEZUG[Diesposten] · TRANSFER[abführen]`

**Zurückgelesen:** Diesposten → Sollmaß → Diesposten → abführen

### B3-S004

**Frei:** Bei OFFENER_FAECHERZULAUF: Stelle das Sollmaß ein; dann führe ihn danach dorthin; dann nimm aus der bezeichneten Quelle.

**Kontrolliert:** `MASS[Sollstellung] · ZIEL[Folgeziel] · BEZUG[Quelle]`

**Zurückgelesen:** Sollstellung → Folgeziel → Quelle

### B3-S005

**Frei:** Bei RUNDE_ZWISCHENSTATION: Führe den Posten über.

**Kontrolliert:** `TRANSFER[überführen]`

**Zurückgelesen:** überführen

### B3-S006

**Frei:** Bei RUNDE_ZWISCHENSTATION: Führe den aktuellen Posten über; dann setze an der Zielstelle ein; dann führe ihn weiter.

**Kontrolliert:** `TRANSFER[Postentransfer] · ZIEL[Zieleinsatz] · BEZUG[weiterführen]`

**Zurückgelesen:** Postentransfer → Zieleinsatz → weiterführen

### B3-S007

**Frei:** Bei RUNDE_ZWISCHENSTATION: Stelle das Sollmaß ein; dann setze den laufenden Posten um; dann lass ihn lange einwirken.

**Kontrolliert:** `MASS[Sollstellung] · TRANSFER[Umsetzen] · ZUSTAND[Langkontakt]`

**Zurückgelesen:** Sollstellung → Umsetzen → Langkontakt

### B3-S008

**Frei:** Bei RUNDE_ZWISCHENSTATION: Führe ihn ab.

**Kontrolliert:** `TRANSFER[abführen]`

**Zurückgelesen:** abführen

### B3-S009

**Frei:** Bei RUNDE_ZWISCHENSTATION: Setze den Posten ein.

**Kontrolliert:** `ZIEL[Einsetzen]`

**Zurückgelesen:** Einsetzen

### B3-S010

**Frei:** Bei KORB_SAMMELGEFAESS: Führe ihn dem Ziel zu; dann führe ihn kurz zum Folgeschritt weiter.

**Kontrolliert:** `TRANSFER[Zielzuführung] · BEZUG[Kurzfolge]`

**Zurückgelesen:** Zielzuführung → Kurzfolge

### B3-S011

**Frei:** Bei KORB_SAMMELGEFAESS: Führe die vorbereitete Portion über; dann setze den Posten ein; dann setze den laufenden Posten um; dann nimm den Posten aus der Quelle.

**Kontrolliert:** `TRANSFER[Vorbereitungstransfer] · ZIEL[Einsetzen] · TRANSFER[Umsetzen] · BEZUG[Quellposten]`

**Zurückgelesen:** Vorbereitungstransfer → Einsetzen → Umsetzen → Quellposten

### B3-S012

**Frei:** Bei KORB_SAMMELGEFAESS: Verwende den Ansatz; dann lass ihn kurz absetzen.

**Kontrolliert:** `BEZUG[Ansatz] · TRANSFER[Kurzabsetzung]`

**Zurückgelesen:** Ansatz → Kurzabsetzung

### B3-S013

**Frei:** Bei KORB_SAMMELGEFAESS: Stelle das Sollmaß ein; dann nimm eine Portion; dann bereite ihn kurz vor; dann lass ihn kurz einwirken.

**Kontrolliert:** `MASS[Sollstellung] · MASS[Portion] · ZUSTAND[Kurzvorbereitung] · ZUSTAND[Kurzkontakt]`

**Zurückgelesen:** Sollstellung → Portion → Kurzvorbereitung → Kurzkontakt

### B3-S014

**Frei:** Bei KORB_SAMMELGEFAESS: Setze ihn in den Lauf ein; dann lass ihn lange absetzen.

**Kontrolliert:** `ZIEL[Laufeinsatz] · TRANSFER[Langabsetzen]`

**Zurückgelesen:** Laufeinsatz → Langabsetzen

### B3-S015

**Frei:** Bei KORB_SAMMELGEFAESS: Führe ihn ab.

**Kontrolliert:** `TRANSFER[abführen]`

**Zurückgelesen:** abführen

### B3-S016

**Frei:** Bei KORB_SAMMELGEFAESS: Ziehe ihn ab. Neuer lokaler Posten: Bei UNVERBUNDENER_UEBERGABEPOSTEN: Führe den vorigen Posten über.

**Kontrolliert:** `TRANSFER[Abzug] · TRANSFER[Rücktransfer]`

**Zurückgelesen:** Abzug → Rücktransfer

### B3-S017

**Frei:** Bei UNVERBUNDENER_UEBERGABEPOSTEN: Lass ihn lange einwirken.

**Kontrolliert:** `ZUSTAND[Langkontakt]`

**Zurückgelesen:** Langkontakt

### B3-S018

**Frei:** Bei UNVERBUNDENER_UEBERGABEPOSTEN: Lass ihn kurz absetzen.

**Kontrolliert:** `TRANSFER[Kurzabsetzung]`

**Zurückgelesen:** Kurzabsetzung

### B3-S019

**Frei:** Bei UNVERBUNDENER_UEBERGABEPOSTEN: Lass ihn nach dem Einsatz absetzen.

**Kontrolliert:** `TRANSFER[Einsatzabsetzen]`

**Zurückgelesen:** Einsatzabsetzen

### B3-S020

**Frei:** Bei UNVERBUNDENER_UEBERGABEPOSTEN: Binde die bezeichnete Stelle; dann führe ihn ab.

**Kontrolliert:** `ZIEL[Stelle] · TRANSFER[abführen]`

**Zurückgelesen:** Stelle → abführen

### B3-S021

**Frei:** Bei UNVERBUNDENER_UEBERGABEPOSTEN: Stelle das Sollmaß ein; dann halte den Posten bereit; dann binde die bezeichnete Stelle; dann halte diesen Posten aktiv; dann arbeite nach dem vorgeschriebenen Maß; dann lass ihn am Ziel absetzen; dann bereite ihn kurz vor; dann halte diesen Posten aktiv; dann binde die bezeichnete Stelle; dann halte den Posten bereit; dann führe ihn zum Ziel über.

**Kontrolliert:** `MASS[Sollstellung] · SCHLUSS[Bereit] · ZIEL[Stelle] · BEZUG[Diesposten] · MASS[Sollmaß] · TRANSFER[Zielabsetzung] · ZUSTAND[Kurzvorbereitung] · BEZUG[Diesposten] · ZIEL[Stelle] · SCHLUSS[Bereit] · TRANSFER[Zieltransfer]`

**Zurückgelesen:** Sollstellung → Bereit → Stelle → Diesposten → Sollmaß → Zielabsetzung → Kurzvorbereitung → Diesposten → Stelle → Bereit → Zieltransfer

### B3-S022

**Frei:** Bei UNVERBUNDENER_UEBERGABEPOSTEN: Führe danach den nächsten Posten über.

**Kontrolliert:** `TRANSFER[Folgetransfer]`

**Zurückgelesen:** Folgetransfer

### B3-S023

**Frei:** Bei UNVERBUNDENER_UEBERGABEPOSTEN: Führe ihn ab.

**Kontrolliert:** `TRANSFER[abführen]`

**Zurückgelesen:** abführen

### B3-S024

**Frei:** Bei UNVERBUNDENER_UEBERGABEPOSTEN: Führe den Posten über.

**Kontrolliert:** `TRANSFER[überführen]`

**Zurückgelesen:** überführen

### B3-S025

**Frei:** Bei UNVERBUNDENER_UEBERGABEPOSTEN: Setze einen neuen Posten ein.

**Kontrolliert:** `ZIEL[Neueinsatz]`

**Zurückgelesen:** Neueinsatz

### B3-S026

**Frei:** Bei UNVERBUNDENER_UEBERGABEPOSTEN: Führe ihn von der Quelle über; dann lass ihn bis zum Sollstand absetzen; dann setze den laufenden Posten um; dann gib einen Anteil zu; dann halte den Posten bereit; dann stelle ihn am Zielgefäß bereit. Neuer lokaler Posten: Bei SICHTBAR_VERBUNDENES_PAAR: Sammle ihn lange.

**Kontrolliert:** `TRANSFER[Quelltransfer] · TRANSFER[Sollabsetzung] · TRANSFER[Umsetzen] · MASS[Zugabe] · SCHLUSS[Bereit] · ZIEL[Zielbereitung] · TRANSFER[Langsammlung]`

**Zurückgelesen:** Quelltransfer → Sollabsetzung → Umsetzen → Zugabe → Bereit → Zielbereitung → Langsammlung

### B3-S027

**Frei:** Bei SICHTBAR_VERBUNDENES_PAAR: Führe die lange Folgestufe aus.

**Kontrolliert:** `BEZUG[Langfolgestufe]`

**Zurückgelesen:** Langfolgestufe

### B3-S028

**Frei:** Bei SICHTBAR_VERBUNDENES_PAAR: Lass ihn länger einwirken; dann lass ihn kurz einwirken.

**Kontrolliert:** `ZUSTAND[Langkontakt] · ZUSTAND[Kurzkontakt]`

**Zurückgelesen:** Langkontakt → Kurzkontakt

### B3-S029

**Frei:** Bei SICHTBAR_VERBUNDENES_PAAR: Führe den laufenden Gang fort; dann nimm den ganzen bezeichneten Teil; dann lass ihn kurz einwirken.

**Kontrolliert:** `BEZUG[Fortsetzung] · MASS[Vollteil] · ZUSTAND[Kurzkontakt]`

**Zurückgelesen:** Fortsetzung → Vollteil → Kurzkontakt

### B3-S030

**Frei:** Bei SICHTBAR_VERBUNDENES_PAAR: Setze den Posten ein; dann arbeite nach dem vorgeschriebenen Maß; dann führe ihn im Lauf weiter; dann führe danach den nächsten Posten über.

**Kontrolliert:** `ZIEL[Einsetzen] · MASS[Sollmaß] · BEZUG[Weiterlauf] · TRANSFER[Folgetransfer]`

**Zurückgelesen:** Einsetzen → Sollmaß → Weiterlauf → Folgetransfer

### B3-S031

**Frei:** Bei SICHTBAR_VERBUNDENES_PAAR: Lass ihn lange einwirken.

**Kontrolliert:** `ZUSTAND[Langkontakt]`

**Zurückgelesen:** Langkontakt

### B3-S032

**Frei:** Bei SICHTBAR_VERBUNDENES_PAAR: Führe einen Anteil über; dann setze den laufenden Posten um; dann halte die kurze Sollstufe ein; dann arbeite danach nach dem nächsten Maß; dann führe ihn kurz zum Folgeschritt weiter.

**Kontrolliert:** `TRANSFER[Anteilstransfer] · TRANSFER[Umsetzen] · MASS[Kurzsoll] · MASS[Folgemaß] · BEZUG[Kurzfolge]`

**Zurückgelesen:** Anteilstransfer → Umsetzen → Kurzsoll → Folgemaß → Kurzfolge

### B3-S033

**Frei:** Bei SICHTBAR_VERBUNDENES_PAAR: Ziehe ihn ab.

**Kontrolliert:** `TRANSFER[abziehen]`

**Zurückgelesen:** abziehen

### B3-S034

**Frei:** Bei SICHTBAR_VERBUNDENES_PAAR: Stelle die Arbeitsstufe ein; dann halte den Posten bereit; dann zerkleinere den Posten; dann arbeite danach nach dem nächsten Maß; dann führe zum Zwischenziel; dann lass ihn kurz absetzen.

**Kontrolliert:** `MASS[Arbeitsstufe] · SCHLUSS[Bereit] · MASS[Zerkleinern] · MASS[Folgemaß] · ZIEL[Zwischenziel] · TRANSFER[Kurzabsetzung]`

**Zurückgelesen:** Arbeitsstufe → Bereit → Zerkleinern → Folgemaß → Zwischenziel → Kurzabsetzung

## B4

### B4-S001

**Frei:** Bei ANWENDUNGS_UND_DURCHLASS_PAAR: Lass ihn lange einwirken.

**Kontrolliert:** `ZUSTAND[Langkontakt]`

**Zurückgelesen:** Langkontakt

### B4-S002

**Frei:** Bei ANWENDUNGS_UND_DURCHLASS_PAAR: Nimm den nächsten Einsatzposten; dann lass ihn länger einwirken; dann lass ihn kurz einwirken.

**Kontrolliert:** `BEZUG[Weiterposten] · ZUSTAND[Langkontakt] · ZUSTAND[Kurzkontakt]`

**Zurückgelesen:** Weiterposten → Langkontakt → Kurzkontakt

### B4-S003

**Frei:** Bei ANWENDUNGS_UND_DURCHLASS_PAAR: Setze den laufenden Posten um; dann führe ihn danach dorthin; dann nimm das nächste; dann lass ihn länger einwirken; dann setze den Posten ein; dann führe den laufenden Gang fort; dann lass ihn kurz absetzen.

**Kontrolliert:** `TRANSFER[Umsetzen] · ZIEL[Folgeziel] · BEZUG[Folgeposten] · ZUSTAND[Langkontakt] · ZIEL[Einsetzen] · BEZUG[Fortsetzung] · TRANSFER[Kurzabsetzung]`

**Zurückgelesen:** Umsetzen → Folgeziel → Folgeposten → Langkontakt → Einsetzen → Fortsetzung → Kurzabsetzung

### B4-S004

**Frei:** Bei ANWENDUNGS_UND_DURCHLASS_PAAR: Befestige ihn.

**Kontrolliert:** `SCHLUSS[befestigen]`

**Zurückgelesen:** befestigen

### B4-S005

**Frei:** Bei ANWENDUNGS_UND_DURCHLASS_PAAR: Lege die Einlage ein; dann setze den laufenden Posten um; dann lass ihn lange einwirken.

**Kontrolliert:** `MASS[Einlage] · TRANSFER[Umsetzen] · ZUSTAND[Langkontakt]`

**Zurückgelesen:** Einlage → Umsetzen → Langkontakt

### B4-S006

**Frei:** Bei ANWENDUNGS_UND_DURCHLASS_PAAR: Lass ihn hindurch.

**Kontrolliert:** `TRANSFER[durchlassen]`

**Zurückgelesen:** durchlassen

### B4-S007

**Frei:** Bei ANWENDUNGS_UND_DURCHLASS_PAAR: Lass ihn hindurch.

**Kontrolliert:** `TRANSFER[durchlassen]`

**Zurückgelesen:** durchlassen

### B4-S008

**Frei:** Bei ANWENDUNGS_UND_DURCHLASS_PAAR: Arbeite nach dem vorgeschriebenen Maß; dann halte den Posten länger warm; dann halte ihn lange; dann lass ihn kurz einwirken.

**Kontrolliert:** `MASS[Sollmaß] · ZUSTAND[Langwärme] · ZUSTAND[Langhalt] · ZUSTAND[Kurzkontakt]`

**Zurückgelesen:** Sollmaß → Langwärme → Langhalt → Kurzkontakt

### B4-S009

**Frei:** Bei ANWENDUNGS_UND_DURCHLASS_PAAR: Lass ihn kurz absetzen.

**Kontrolliert:** `TRANSFER[Kurzabsetzung]`

**Zurückgelesen:** Kurzabsetzung

### B4-S010

**Frei:** Bei ANWENDUNGS_UND_DURCHLASS_PAAR: Führe fort und schließe.

**Kontrolliert:** `BEZUG[Fortschluss]`

**Zurückgelesen:** Fortschluss

### B4-S011

**Frei:** Bei OFFENE_LINKSSTATION: Arbeite nach dem vorgeschriebenen Maß; dann wärme ihn kurz; dann setze den Gang lange fort; dann gib einen Anteil zu; dann setze den laufenden Posten um; dann führe den laufenden Gang fort; dann ziehe kurz ab und schließe.

**Kontrolliert:** `MASS[Sollmaß] · ZUSTAND[Kurzwärme] · BEZUG[Langfortsetzung] · MASS[Zugabe] · TRANSFER[Umsetzen] · BEZUG[Fortsetzung] · TRANSFER[Kurzabzugsschluss]`

**Zurückgelesen:** Sollmaß → Kurzwärme → Langfortsetzung → Zugabe → Umsetzen → Fortsetzung → Kurzabzugsschluss

### B4-S012

**Frei:** Bei OFFENE_LINKSSTATION: Führe ihn ab.

**Kontrolliert:** `TRANSFER[abführen]`

**Zurückgelesen:** abführen

### B4-S013

**Frei:** Bei OFFENE_LINKSSTATION: Setze den verbleibenden Posten erneut ein; dann lass ihn kurz absetzen.

**Kontrolliert:** `ZIEL[Wiedereinsatz] · TRANSFER[Kurzabsetzung]`

**Zurückgelesen:** Wiedereinsatz → Kurzabsetzung

### B4-S014

**Frei:** Bei OFFENE_LINKSSTATION: Verwende den Ansatz; dann halte diesen Posten aktiv; dann führe ihn kurz hindurch; dann schließe den Lauf ab.

**Kontrolliert:** `BEZUG[Ansatz] · BEZUG[Diesposten] · TRANSFER[Kurzdurchgang] · TRANSFER[Laufschluss]`

**Zurückgelesen:** Ansatz → Diesposten → Kurzdurchgang → Laufschluss

### B4-S015

**Frei:** Bei OFFENE_LINKSSTATION: Gib einen Anteil zu; dann nimm den Klarauszug; dann nimm eine Portion; dann führe ihn durch die Zielpassage. Neuer lokaler Posten: Bei S_FOERMIGER_MEHRPORT: Sammle ihn kurz; dann führe ihn ab.

**Kontrolliert:** `MASS[Zugabe] · TRANSFER[Klarauszug] · MASS[Portion] · TRANSFER[Zielpassage] · TRANSFER[Kurzsammlung] · TRANSFER[abführen]`

**Zurückgelesen:** Zugabe → Klarauszug → Portion → Zielpassage → Kurzsammlung → abführen

### B4-S016

**Frei:** Bei S_FOERMIGER_MEHRPORT: Nimm einen weiteren Anteil; dann binde die bezeichnete Stelle; dann gieße ihn von der Quellseite zu; dann lass ihn kurz absetzen.

**Kontrolliert:** `MASS[Folgeportion] · ZIEL[Stelle] · TRANSFER[Quellausguss] · TRANSFER[Kurzabsetzung]`

**Zurückgelesen:** Folgeportion → Stelle → Quellausguss → Kurzabsetzung

## B5

### B5-S001

**Frei:** Bei LINKER_NACHTRAGSPOSTEN: Führe ihn danach über.

**Kontrolliert:** `TRANSFER[Nachtransfer]`

**Zurückgelesen:** Nachtransfer

### B5-S002

**Frei:** Bei LINKER_NACHTRAGSPOSTEN: Setze einen neuen Posten ein.

**Kontrolliert:** `ZIEL[Neueinsatz]`

**Zurückgelesen:** Neueinsatz

### B5-S003

**Frei:** Bei LINKER_NACHTRAGSPOSTEN: Lass ihn am Ziel absetzen; dann binde die bezeichnete Stelle; dann führe den laufenden Gang fort; dann ziehe ihn weiter ab; dann führe ihn zum Ziel über; dann arbeite nach dem vorgeschriebenen Maß; dann führe den laufenden Gang fort; dann stelle die Endstufe ein; dann setze den laufenden Posten um.

**Kontrolliert:** `TRANSFER[Zielabsetzung] · ZIEL[Stelle] · BEZUG[Fortsetzung] · TRANSFER[Weiterabzug] · TRANSFER[Zieltransfer] · MASS[Sollmaß] · BEZUG[Fortsetzung] · MASS[Endstufe] · TRANSFER[Umsetzen]`

**Zurückgelesen:** Zielabsetzung → Stelle → Fortsetzung → Weiterabzug → Zieltransfer → Sollmaß → Fortsetzung → Endstufe → Umsetzen

## B6

### B6-S001

**Frei:** Bei RECHTER_NACHTRAGSPOSTEN: Sammle ihn lange; dann bearbeite ihn kurz; dann nimm den Endposten; dann führe den laufenden Gang fort; dann arbeite nach dem vorgeschriebenen Maß; dann führe den laufenden Gang fort; dann lege die Einlage ein; dann halte diesen Posten aktiv; dann führe bis zum Endziel.

**Kontrolliert:** `TRANSFER[Langsammlung] · ZUSTAND[Kurzbearbeitung] · SCHLUSS[Endposten] · BEZUG[Fortsetzung] · MASS[Sollmaß] · BEZUG[Fortsetzung] · MASS[Einlage] · BEZUG[Diesposten] · ZIEL[Endziel]`

**Zurückgelesen:** Langsammlung → Kurzbearbeitung → Endposten → Fortsetzung → Sollmaß → Fortsetzung → Einlage → Diesposten → Endziel

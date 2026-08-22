# V74 R3 — Biological station-atlas third edition

Status: kreative technische Zehnseiten-Arbeitsedition, keine Entzifferung oder Übersetzung.

## Ergebnis

Alle **281 Ereignisse**, **115 Felder**, **97 Aussagen** und **6 Records** auf f81v/f82r/f83r besitzen jetzt eine konkrete lokale Betriebslesung. Die Edition behandelt die Bilder als Atlas von Bad-, Wasch-, Geräte-, Gefäß-, Kontroll- und Abschlussstationen. Sie erzeugt ausdrücklich keinen Gesamtwasserkreislauf.

Von 281 Ereignissen bleiben 191 reine Exemplarwerte; 90 besitzen mindestens eine eingefrorene exakte Karten- oder Formalklasse. Auch dort sind Wasser, Tuch, Temperatur, Platz, Gefäß und Arbeitshandlung nur konkrete Quellenfüllungen, keine Bedeutungen der sichtbaren Gruppen.

## Ausführbare Registerregel

```text
BEGIN B-record: clear OWNER, ACTIVE, TARGET, PREVIOUS, MEASURE
SET smallest V71 owner for the current field
IF owner changes: block physical carry; retain record ID only as bookkeeping
IF owner unresolved: quarantine ACTIVE and TARGET until the exemplar resolves it
EXECUTE exact event in V69 order with its opaque card/formal layer
APPLY concrete occurrence default only at the local owner
VISIBLE contact permits local comparison, never source/sink/direction
CLOSE closes a field; FLUSH?/DRAIN? close only their local post
END B-record: clear every register
B5 -> B6: mandatory hard reset, no inherited value
```

Sichtbarer Kontakt und Registervererbung sind getrennte Größen. Der B4-Unterlauf kann sichtbar am Gefäß ansetzen, während der Text beim Besitzerwechsel trotzdem einen neuen lokalen Posten eröffnet. Umgekehrt erzeugt `LINK_ACTIVE` niemals eine gezeichnete Leitung.

## Die sechs Records

### B1 — f81v

Führe f81v als gemeinsames zweireihiges Badefeldregister: Plätze zählen und zuweisen, lokale Maße und Zeiten setzen, Tücher oder Gefäße bereitstellen, einzelne Plätze temperieren, spülen oder schließen. Die gemeinsame Umgrenzung erlaubt einen Poolbesitzer, aber keine Reihen- oder Flussfolge.

Umfang: 66 Ereignisse, 24 Felder, 21 Aussagen.

### B2 — f82r

Führe f82r als Atlas getrennter Konfigurationen. Bediene zuerst die obere Paarbecken-/Zylinderstation, setze danach die mittlere linke Geräte-/Knotenstation neu, quarantäniere Linie und Liegepodest in F057–F058, eröffne das untere Mehrfigurenfeld erst bei F059 und führe die Randposten ab F062 separat. Jeder Besitzerwechsel sperrt physischen Carry.

Umfang: 62 Ereignisse, 26 Felder, 22 Aussagen.

### B3 — f83r

Führe f83r zunächst als drei getrennte Randstationen: offenes Fächerende, Rundgefäß und Korbgefäß. Nach F086 beginnt eine ungelöste Zone F087–F098 ohne Bildkante. Erst F099 eröffnet das tatsächlich bogenverbundene Hauptpaar; beide Seiten bleiben gleichrangig und ungerichtet.

Umfang: 86 Ereignisse, 38 Felder, 34 Aussagen.

### B4 — f83r

Eröffne das f83r-Hauptpaar als neuen B4-Record. Buche Paarvergleich und lokale Bedienung, setze bei F120 den linken offenen Fransenposten neu und bei F126 den rechten S-Lauf-/Mehrarmknoten nochmals neu. Sichtbare lokale Anschlüsse erlauben Wartung, aber keinen globalen Kreislauf.

Umfang: 47 Ereignisse, 20 Felder, 16 Aussagen.

### B5 — f83r

Führe ausschließlich den linken offenen Fransenposten als eigenen B5-Record, prüfe, reinige und schließe ihn lokal und lösche am Ende ACTIVE, TARGET und PREVIOUS.

Umfang: 11 Ereignisse, 5 Felder, 3 Aussagen.

### B6 — f83r

Beginne nach vollständigem Reset einen eigenen B6-Record für den rechten S-Lauf-/Mehrarmknoten. Prüfe, adressiere und schließe nur diesen Posten; kein B5-Wert darf übernommen werden.

Umfang: 9 Ereignisse, 2 Felder, 1 Aussagen.

## Kontaktgraph und harte Sperren

Der maschinenlesbare Graph enthält ausschließlich `UNDIRECTED` oder `NONE`. Positive lokale Kontakte sind die obere f82r-Paar-/Zylinderkonfiguration, der f82r-Geräte-/Inline-Knoten, die Hauptbogenpaare sowie die lokalen f83r-Unterläufe. Echte Sperren liegen zwischen den f82r-Konfigurationen, zwischen den drei f83r-Randstationen, über F087–F098, zwischen linkem und rechtem Unterlauf sowie zwingend zwischen B5 und B6.

Vier V72-Aussagen behalten einen internen Besitzerbruch: `B2-S012`, `B3-S016`, `B3-S026` und `B4-S015`. F057–F058 sowie F087–F098 bleiben unaufgelöst; ihre konkreten Defaults sind Quarantänehandlungen im Register und kein imaginärer Stofftransport.

## Stationsvergleich

Für jede der 16 lokalen Besitzerklassen stehen technische, medizinische und formal-ikonographische Gegenlesung nebeneinander. f81v und das untere f82r-Feld tragen Bad-/Poollesungen am stärksten. Geräte-, Gefäß- und Unterlaufstationen tragen eine technische Bedienlesung. Offene Fächer, Bögen und Knoten behalten jedoch starke ikonographische Rivalen; die zwei ungelösten Besitzer werden formal quarantänisiert.

## Gewinn und Grenze

Die Edition ist ausführbar, weil ein Schreiber nur Record, lokalen Besitzer, Exemplarwert und Abschlussstatus verfolgen muss. Sie ist zugleich streng lokal: kein Pfeil, gemeinsamer Vorrat, Quelle, Senke oder Rücklauf wird ergänzt. Der Preis ist hoch: 191/281 konkrete Vorgänge kommen vollständig aus dem angenommenen Masterexemplar, und selbst die 90 typisierten Vorgänge bestimmen keinen Gegenstand oder Zweck.

Keine neue Karte, kein Stamm, Laut, Wort, POS, Sprache oder Klartext wurde eingeführt. f84 und f84r blieben versiegelt.

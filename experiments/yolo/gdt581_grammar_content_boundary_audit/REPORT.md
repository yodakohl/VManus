# GDT581 — Vollständige Grammatik-/Inhaltsgrenze

## Ergebnis

`PASS_15889_COMPLETE_SLOTS__13702_CONTENT_CARRIERS__2187_CONTROL_SLOTS__4026_INHERITED_ALIASES__5672_FOCUS_HOSTS__8_FINAL_RECIPE_RECONCILIATIONS__269_FOCUS_VOICE_REPAIRS__232_EVENT_REPAIRS__2_SAFE_EXPLICIT_REMOTE_SLOTS__744_LOCAL_CARD_HOSTS__1973_LOCAL_COMPONENTS__107_NAME_SLOTS__ZERO_UNOWNED_SLOTS__5122_EXACT_ROUNDTRIPS`

Die Grammatikpolitur ist für den nächsten inhaltlichen Versuch abgeschlossen:
Auf den dreißig zugelassenen Seiten gibt es keinen strukturell herrenlosen Slot
mehr. Das heißt nicht, dass seine sachliche Bedeutung schon bekannt ist. Es
heißt, dass wir für jeden offenen Inhaltsplatz wissen, **wo** er geschrieben
steht, **zu welchem Kopf** er gehört und **welche Steuerungszeichen nicht mit
Inhalt gefüllt werden dürfen**.

## Das vollständige Inventar

| Schicht | Gesamt | Inhaltsträger | Steuerung |
|---|---:|---:|---:|
| 5.122 laufende Ereignisse | 13.809 | 11.938 | 1.871 |
| 744 lokale Karten | 1.973 | 1.657 | 316 |
| ownergebundene Namenskernspannen | 107 | 107 | 0 |
| **vollständiges Universum** | **15.889** | **13.702** | **2.187** |

Die 13.702 Inhaltsträger sind die erlaubten Andockstellen eines späteren
konkreten Wörterbuchs. Sie umfassen Handlungs-, Objekt-, Relations-, Grad- und
Modifier-Occurrences sowie lokale Komponenten und gelernte Namenkerne. Die
2.187 Steuerungsplätze bleiben Zustand, Wiederaufnahme oder lokales
Makro/Zeichen. Ein späterer Bedeutungsversuch darf deshalb nicht einfach jede
Silbe mit `Wasser`, `Öl`, `Wurzel`, `erwärmen` oder einem anderen Stoff- oder
Prozesswort füllen: Er muss auf einen der 13.702 Inhaltsplätze zielen und dessen
festen Host respektieren.

Die getrennte Vererbungstabelle enthält 4.026 Aliase, davon 1.741 Handlungs-
und 2.285 Objektaliase. Sie zeigen auf eine frühere geschriebene Occurrence in
derselben Aussage oder auf einen Besitzerdefault. Gerade dadurch vergrößern sie
das Wörterbuch nicht künstlich: Ein geerbter Wert ist ein Verweis, kein zweites
unsichtbares Wort.

## Acht notwendige Reparaturen am Endrezept

Der Abgleich der 5.051 alten GDT407- und 621 GDT515-Anschlüsse mit den
endgültigen GDT580-Rezepten erfordert genau acht und nur acht Eingriffe:

- Vier reine Positionsupdates: G515-A00245, A00258, A00404 und A00422 behalten
  dieselben Root-Occurrences und Köpfe an neuen Koordinaten.
- Zwei echte Kopfwechsel werden vom bereits bestehenden Nächster-Kopf-Selektor
  erzwungen: EEE in G515-E0423 und Y in G515-E0426 wechseln von einer nicht
  mehr passenden CH-Occurrence auf K.
- G515-A00165 entfällt, weil G515-E0182 im Endrezept OL statt des alten L
  enthält.
- G515-E0253 erhält den neu vorhandenen AIIN-Slot als Argument von CH.

Danach enthält die Fokuskarte wieder vollständig 5.672 geschriebene
Occurrences. Grad- und Modifierhosts bleiben getrennt nachvollziehbar: 333
Gradzuweisungen samt 18 bekannten Grenzgefahren sowie 1.810 nichtgradige
Modifier besitzen eine konkrete Hülle oder einen konkreten Handlung- bzw.
Besitzerkopf.

## Die hörbare Mehrdeutigkeit war real

Die vorherige flüssige deutsche Ausgabe konnte den richtigen strukturellen
Anschluss verdecken. Wenn eine Klausel mit `Halte ...`, `Kennzeichne ...` oder
`Nimm ...` beginnt, klingt ein späterer Zusatz automatisch wie ein Argument
dieser hörbaren Handlung — selbst wenn die Attachment-Tabelle ihn an den
Besitzer, die folgende Karte oder eine andere vorherige Handlung bindet.

Der vollständige Audit findet 269 solche Fokus-Occurrences in 232 Ereignissen:

| Geometrie | Reparaturen |
|---|---:|
| Besitzerrahmen | 128 |
| begrenzt folgende Karte | 98 |
| vorherige Karte | 24 |
| fortgeführte Handlung | 19 |

Diese Geometrie beziehungsweise die Abweichung ihrer Selektorköpfe liefert den
**diagnostischen Auslöser**. Sie ist nicht automatisch der Host, der in der
reparierten Stimme gesprochen werden muss. GDT581 trennt daher
`selector_trigger_class` von `voice_repair_class`: 228 Zeilen sprechen ihren
wirksamen primären Handlungs- oder Besitzerkopf. Bei 41 ausgewählten
Grad-Slots liegt die wirksame GDT558-Bindung dagegen auf einer
`CONTROL_ENVELOPE`. Diese Grade sprechen ausdrücklich den exakten
Steuerungsrahmen und nicht den älteren Handlungs- oder Besitzerselektorkopf,
der nur den Audit ausgelöst hatte.

Die Strukturstimme benennt in diesen Ereignissen jede betroffene und jede
benachbarte Inhaltsposition mit maschinenlesbarer Slot- und Hostadresse. Sie
spricht insgesamt alle 292 Fokus-Slots und 62 nichtgradigen Modifier dieser 232
Ereignisse aus; sichtbare lokale Handlungen und etwaige Steuerungsreste bleiben
ebenfalls erhalten. Das ist absichtlich expliziter und weniger literarisch als
GDT580. Sein Zweck ist nicht schöne Prosa, sondern eine unmissverständliche
Trägerstruktur für die nächste Bedeutungsrunde.

### Drei entscheidende Beispiele

**G515-E0385** zeigt, warum ein einziges Ereignis nicht einfach eine einzige
Handlungsstimme besitzen kann. Seine beiden D_ADDR-Occurrences außen und innen
gehören zum fortgeführten R/Kennzeichnen in G515-E0383@4. Der AR-Slot zwischen
ihnen gehört dagegen zum fortgeführten OK/Eintragen in G515-E0383@2. GDT581
spricht alle drei Anschlüsse getrennt aus und bewahrt damit die
Außen/Innen-Struktur.

**G407-E3963** ist der schwierigere Gleichrootfall. Der AR/Ausgangs-Slot gehört
zum vorherigen CH in G407-E3962@4. Grad und Objekt gehören zum lokalen CH in
G407-E3963@2. Weil beide Köpfe CH heißen, hätte ein bloßer Vergleich der
Rootnamen den Fehler übersehen. Die Occurrence-Adresse macht die Differenz
explizit.

**G515-E0379** ist kein Fehler. GDT580 sagt für beide AL-Slots bereits hörbar
`Beim vorangehenden Festlegen` und bindet sie an T in G515-E0378@3. Diese zwei
Slots bleiben als sichere Ausnahmen unverändert. Damit besitzen alle 25
entfernten AL/AR-Slots eine vollständige Disposition: 23 werden in GDT581
explizit repariert, zwei waren bereits korrekt ausgesprochen.

## Die lokale Schicht bleibt eigenständig

Die 744 lokalen Karten werden nicht in laufende Sätze hineingezogen. Sie
behalten exakte Seite, Locus, Besitzer und Karten-ID und zerfallen in 183
GDT479-Mikrorecordkarten, 510 GDT513-Restkarten und 51 neue lokale
GDT515-Karten. Ihre 1.973 Komponenten haben jeweils einen Karten-, Record-,
Bundle- oder lokalen Handlungshost.

Die 107 Namensslots liegen als exakte Spannen in 89 namenführenden Labels. Sie
verteilen sich auf 60 Sternpositions-, 38 Drogen/Zutaten-, sieben
Bad/Auslass- und zwei Pflanzenpositionen und enthalten 72 rohe Kernformen. Das
ist ein brauchbares Adressbuch für spätere Einzelbedeutungen, aber noch kein
Namenslexikon: `content_class` stammt vom Besitzerkontext, nicht aus einer
entzifferten Kernbedeutung.

## Vollständiger Rückweg

Die neue Ausgabe behält alle 5.122 Event-IDs, alle 793 festen
Aussagezuordnungen und die dreißig Seiten. 232 Ereignisse, 178 Aussagen und 21
Seiten erhalten eine explizitere Strukturstimme; die übrigen Ereignisse
übernehmen ihren GDT580-Text. Für jedes Ereignis liegt der unveränderte
GDT580-Wortlaut als Rückkanal vor, und jede Aussage wird nur aus ihrer festen
Eventfolge aufgebaut. So werden alle 5.122 GDT580-Ereignisse und alle 793
GDT580-Aussagen exakt rekonstruiert.

Dieser Rückweg beweist, dass bei der Politur nichts verloren ging. Er beweist
nicht, dass die deutschen Arbeitslabels die historische Sprache oder Bedeutung
des Manuskripts wiedergeben.

Der unabhängige Source-Validator besteht 68/68 Prüfungen. Ein getrennt
durchgeführter manueller Stimmenaudit findet in allen 232 reparierten
Ereignissen null verlorene Slotmarker, null OWNER-Imperative und null falsche
Kopfrichtung; die synthetischen Grenzfälle `D-Stelle` und `führe den Gang
weiter` werden ebenfalls korrekt nicht als lokale Handlung gelesen.

## Was GDT581 für den nächsten Schritt leistet

Der nächste Bedeutungsversuch kann nun konkrete Kandidaten an klar benannte
Positionen setzen und sofort fragen:

- hält dieselbe Kandidatenbedeutung an allen Occurrences eines Stamms;
- passt sie zum jeweiligen Handlungs-, Relations-, Besitzer-, Steuerungs- oder
  lokalen Kartenhost;
- bleibt sie außerhalb der 2.187 reinen Steuerungsslots; und
- ergibt sie in den expliziten Hostblöcken noch eine plausible Komposition?

Damit ist die Grammatik nicht „bewiesen“, aber ausreichend ausgeräumt, um
Sachbedeutungen nicht weiter auf unklare Satzanschlüsse zu stapeln.

## Claim ceiling

GDT581 bestätigt eine vollständige, reversible **Arbeits-Strukturstimme** über
den gegenwärtigen dreißig Seiten. Es bestätigt keine Voynich-Wortbedeutung,
keinen Klartext, keine Sprache oder historische Syntax, kein Codebuch, keine
Textsorte und keine Identität von Stoffen, Pflanzen, Körperteilen, Krankheiten,
Heilungen, Gefäßen oder Verfahren. Auch die deutschen Wörter der Ausgabe sind
editorielle Funktionslabels und keine behaupteten Übersetzungen.

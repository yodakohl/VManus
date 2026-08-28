# GDT581 method

## Frage

Ist die gegenwärtige Grammatik der dreißig zugelassenen Seiten vollständig
genug, um als feste Trägerstruktur für konkrete Bedeutungsversuche zu dienen?
Konkret: Lässt sich jede geschriebene Funktions- oder Inhaltsposition von einer
reinen Steuerungsposition unterscheiden, einem exakten lokalen, entfernten oder
Besitzer-Host zuweisen und in der deutschen Arbeitsstimme ohne falschen
Kopfanschluss aussprechen?

## Eingaben

GDT580 liefert die vollständige laufende Ausgabe mit 5.122 Ereignissen, 793
Aussagen und dreißig Seiten sowie seine sechs expliziten
Wiederaufnahme-Slotspannen. Die endgültigen Rezepte werden mit den 5.051
GDT407- und 621 GDT515-Fokusanschlüssen abgeglichen. Weitere bereits bestehende
Strukturschichten liefern:

- GDT416 und GDT539: geerbte Handlungs- und Objektverweise;
- GDT471/GDT472: ownergebundene Namenstemplates und exakte Namenskernspannen;
- GDT479/GDT513/GDT515: die vollständigen 744 lokalen Karten;
- GDT558: 333 Grad-Hosts und die 18 bekannten falschen
  Vererbungsgefahren;
- GDT567/GDT568: die vorhandene Besitzerstimme und 45 beobachtete
  Register-mal-Handlungs-Zellen;
- GDT577/GDT579: explizite Wiederholungs- und Außen/Innen-Scope-Hosts.

Keine neue Seite, Abbildung, Transkription, Oberfläche, Rezeptfamilie oder
Stammbedeutung wird zugelassen. f84 und f84r bleiben gesperrt.

## 1. Fokusanschlüsse auf die endgültigen Rezepte übertragen

Die 5.672 alten Fokuszeilen werden nicht nach bloßer Spaltenposition, sondern
nach `(event_id, root, occurrence_rank)` in das jeweilige GDT580-Rezept
übertragen. Der Handlungskopf wird ebenso über seine konkrete
Root-Occurrence verfolgt. Der unveränderte Selektor wird nur dann neu auf dem
Endrezept ausgeführt, wenn die ursprünglich ausgewählte Occurrence dort nicht
mehr existiert oder die veränderte Geometrie einen neuen nächsten Kopf
erzwingt.

Der Abgleich erzeugt genau acht materielle Reconciliations:

| ID | Ereignis | Behandlung |
|---|---|---|
| C01 | G515-E0182 | den veralteten L-Fokus löschen; das Endrezept enthält OL, nicht L |
| C02 | G515-E0244 | OR und seinen zweiten S-Kopf nur auf ihre neuen Positionen setzen |
| C03 | G515-E0253 | Y und T nur auf ihre neuen Positionen setzen |
| C04 | G515-E0423 | EEE durch den unveränderten Nächster-Kopf-Selektor von CH auf K umhängen |
| C05 | G515-E0423 | Y auf die neue Position desselben K-Kopfes setzen |
| C06 | G515-E0426 | Y nach Wegfall der alten CH-Occurrence durch denselben Selektor auf K umhängen |
| C07 | G515-E0437 | Y auf seine neue Position bei demselben CH-Kopf setzen |
| C08 | G515-E0253 | den im Endrezept neu vorhandenen AIIN-Slot als Argument von CH einfügen |

Vier Änderungen sind reine Koordinatenupdates, zwei echte, vom bestehenden
Selektor erzwungene Kopfwechsel, eine ist eine Löschung und eine eine
Einfügung. Danach existieren wieder genau 5.672 Fokus-Occurrences mit je einem
primären Host.

Grad-Slots werden über `(event_id, grade_atom_position)` an die 333
GDT558-Hüllen angeschlossen. Diese Positionskennung ist notwendig, weil die
dortige laufende `grade_occurrence`-Nummer nicht ereignislokal ist. Die 18
bekannten Grenzgefahren werden unverändert mitgeführt.

Die 1.810 übrigen laufenden Modifier erhalten ihren Host in fester Reihenfolge:
expliziter GDT579-Scope, konfliktfreier GDT577-Wiederholungs-Host, nächste
sichtbare Handlung mit Linksbevorzugung bei Gleichstand, sichtbare
Zustandshülle, eindeutiger Fokus-Host-Konsens, geerbter Handlungsalias und
zuletzt der Besitzerrahmen. Diese Reihenfolge weist einen Host zu; sie erzeugt
keine neue Lexembedeutung.

## 2. Vollständiges Slotuniversum

Ein Slot ist hier eine konkrete geschriebene Occurrence oder eine bereits
abgegrenzte Namenskernspanne, kein postuliertes Wörterbuchwort. Das Universum
setzt sich zusammen aus:

| Schicht | Slots | Inhaltsträger | nur Steuerung |
|---|---:|---:|---:|
| laufende Ereignisrezepte | 13.809 | 11.938 | 1.871 |
| lokale Komponenten | 1.973 | 1.657 | 316 |
| lokale Namenskernspannen | 107 | 107 | 0 |
| **gesamt** | **15.889** | **13.702** | **2.187** |

Laufende Handlungen sind ihre eigenen Köpfe. Objekt-, Relations- und
Grad-Occurrences übernehmen den reconcilierten Fokus-Host; Zustandswurzeln
bleiben Steuerung; nichtgradige Modifier verwenden die oben beschriebene
Hostreihenfolge. `LOCAL_X` ist ein ownergebundener gelernter Kern,
`RESUME_CARD` eine Steuerungswiederaufnahme. Jeder Ledger-Eintrag speichert
Boundary-Klasse, Fill-Status, primären Governor, Realisierungsscope und Quelle.

Die 4.026 Vererbungen werden in einer separaten Alias-Tabelle geführt: 1.741
Handlungs- und 2.285 Objektaliase, davon 3.278 zu einer früheren Occurrence in
derselben Aussage und 748 zu einem Besitzerdefault. Ein Alias darf auf eine
vorhandene lexikalische Quelle zeigen, wird aber niemals als neue geschriebene
Occurrence oder neuer Wörterbuchplatz gezählt.

## 3. Lokale Schicht

Alle 744 lokalen Karten behalten ihre exakte Karten-ID, Seite, Register,
Locus- und Besitzerbindung. Sie zerfallen disjunkt in 183
GDT479-Mikrorecordkarten, 510 GDT513-Restkarten und 51 neue lokale
GDT515-Karten. Wo vorhanden, bleiben Record- und Bundle-Governor erhalten; die
lokale Schicht darf keinen Kopf aus einem laufenden Satz erben.

Ihre 1.973 Komponenten umfassen 415 Handlungs-, 389 Objekt-, 313 Relations-,
179 Grad-, 196 Form/Stufen-, 165 Siglen/Klassen- und 316 Steuerungskomponenten.
Hinzu kommen 107 exakt ausgeschnittene Namensslots in 89 namenführenden Labels:
60 Sternpositions-, 38 Drogen/Zutaten-, sieben Bad/Auslass- und zwei
Pflanzen-Slots. Diese enthalten 72 verschiedene rohe Kernformen beziehungsweise
80 `content_class × raw_core`-Typen. Die Klassen sind Besitzerkontext; die rohen
Kerne sind weder bestätigte Objektnamen noch frei zerlegbare Funktionswörter.

## 4. Hörbaren Kopf gegen den strukturellen Kopf prüfen

Für jede GDT580-Klausel wird die erste hörbare Imperativhandlung mit einer
endlichen Wortgrenzenliste erkannt. `entnimm/nimm`, `halte`,
`gib/ordne/führe ... zu`, `wähle`, `bearbeite`, `stelle/lege`,
`markiere/kennzeichne`, `trage` und `setze` werden auf die bereits vorhandenen
neun Handlungsroots abgebildet; bei `setze` unterscheidet ein freies `ein` im
selben Koordinationssegment P von OK. Ein bloßes `führe den Gang weiter` ist
OL-Steuerungsstimme und wird nicht als K-Handlung gezählt; ebenso verhindert
die Bindestrichgrenze, dass `D-Stelle` als Imperativ `stelle` gelesen wird.

Eine Fokus-Occurrence wird für eine explizite Kopfblock-Reparatur gewählt,
wenn:

1. Besitzerinhalt in der bisherigen Klausel wie Inhalt einer lokalen Handlung
   klingt;
2. ein begrenzt folgender Handlungskopf nicht der ersten hörbaren Handlung
   entspricht;
3. ein vorheriger oder fortgeführter Handlungskopf nicht der ersten hörbaren
   Handlung entspricht; oder
4. dieselbe Rootbezeichnung zwei verschiedene Handlungs-Occurrences verdeckt.

Das ergibt 269 Fokuszeilen in 232 Ereignissen: 128 Besitzer-, 98
Folgekarten-, 24 Vorherkarten- und 19 fortgeführte Anschlüsse. Nach
diagnostischer Auslöserklasse sind es 128 Besitzerfehler, 98
Folgekarten-Rootkonflikte, 42 entfernte Rootkonflikte und ein
occurrence-spezifischer Gleichrootfall.

Der physische Auslöser und die gesprochene Reparatur bleiben zwei getrennte
Felder. `selector_trigger_class` hält fest, **warum** die alte Klausel in den
Audit gelangte; dafür gilt weiterhin die ursprüngliche Attachment-Geometrie
und ihr Selektorkopf. `voice_repair_class` und `voice_head_link` bestimmen
dagegen, **welcher wirksame Grammatikhost** ausgesprochen wird. Bei 228 der 269
Zeilen ist das ein expliziter primärer Handlungs- oder Besitzerblock. Bei 41
ausgewählten Grad-Slots hat GDT558 jedoch den wirksamen Host bereits als
`CONTROL_ENVELOPE` bestimmt. Sie werden deshalb als
`GRADE_CONTROL_ENVELOPE_BEATS_EVENT_WIDE_ACTION` mit einem exakten
`CONTROL:event:carrier_envelope`-Link gesprochen, nicht mit dem älteren
Handlungs- oder Besitzerkopf, der lediglich den Audit ausgelöst hat.

Ein ausgewähltes Ereignis wird vollständig und in Atomreihenfolge als
Strukturstimme neu ausgegeben, nicht nur an der auffälligen Stelle geflickt.
Jeder seiner Fokus-Slots erhält einen eigenen Block
`Bezug/Lokal [wirksamer Kopf oder Steuerungsrahmen]: Phrase [exakter Slot]`;
ebenso jeder nichtgradige Modifier. Sichtbare Handlungen ohne eigenen
Inhaltsblock werden ausdrücklich genannt, reine Steuerungsreste als
Strukturspur erhalten. Dadurch repräsentieren die 232 reparierten Ereignisse
alle ihre 292 Fokus-Slots und alle 62 nichtgradigen Modifier genau einmal.

Drei Grenzfälle sind fest im Verfahren verankert:

- **G515-E0385:** Die beiden D_ADDR-Slots außen und innen gehören weiterhin zu
  R in G515-E0383@4. Der dazwischenliegende AR-Slot gehört jedoch zum
  fortgeführten OK in G515-E0383@2. Eine einzige ereignisweite Stimme
  „fortgeführtes Kennzeichnen“ wäre daher falsch.
- **G407-E3963:** Der AR-Slot gehört zu CH in G407-E3962@4, während Grad und
  Objekt an das ebenfalls CH genannte lokale G407-E3963@2 gebunden sind. Der
  Rootname allein reicht nicht; die Handlung-Occurrence muss hörbar sein.
- **G515-E0379:** Beide AL-Slots sind schon in GDT580 ausdrücklich als
  `Beim vorangehenden Festlegen` an T in G515-E0378@3 gebunden. Diese zwei
  sicheren Slots werden nicht noch einmal umgeschrieben.

Von den 25 entfernten AL/AR-Occurrences werden damit 23 explizit repariert und
die zwei G515-E0379-Slots als bereits explizit belegt.

## 5. Ausgabe und exakter GDT580-Rückweg

Die Ereignisausgabe enthält weiterhin genau 5.122 feste Event-IDs. Für die 232
reparierten Ereignisse speichert sie neben der Strukturstimme den unveränderten
GDT580-Quelltext; alle übrigen 4.890 Ereignisse übernehmen GDT580 direkt.
Aussagen werden ausschließlich aus ihrer festen Event-ID-Folge neu
zusammengesetzt. Die gespeicherten Rückkanäle müssen alle 5.122
Ereignisklauseln und alle 793 GDT580-Aussagen exakt rekonstruieren. Das prüft
Reversibilität und Identität, nicht die sachliche Wahrheit der deutschen
Arbeitsbedeutungen.

## Entscheidung und Claim ceiling

Der Pass gilt nur, wenn alle 15.889 Slots eindeutig klassifiziert und gehostet
sind, die 13.702/2.187-Trennung aufgeht, kein Slot ohne Besitzer bleibt, die
5.672 Fokuszeilen nach genau acht dokumentierten Reconciliations vollständig
sind, die 4.026 Aliase keine geschriebenen Slots erzeugen, die lokale
744-Karten-Schicht vollständig separat bleibt, die 269 ausgewählten
Stimmkonflikte exakt 232 Ereignisse ergeben, alle 25 entfernten AL/AR-Slots eine
explizite Disposition besitzen und der GDT580-Rückweg vollständig ist.

GDT581 bestätigt ausschließlich eine **Strukturstimme**: eine endliche
Zuordnung geschriebener Occurrences zu grammatischen Köpfen und zu offenen
Inhalts- oder geschlossenen Steuerungsplätzen. Deutsche Wörter wie `Entnehmen`,
`Zielgefäß`, `Grad` und `Besitzerrahmen` sind Arbeitslabels. Der Pass bestätigt
keine Voynich-Übersetzung, kein Lexem, keine Sprache oder Syntax, kein
historisches Codebuch, keine Gattung und keine konkrete Substanz, Pflanze,
Krankheit, Handlung oder Objektidentität.

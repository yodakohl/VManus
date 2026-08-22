# V58 R3 — stärkster ausführbarer nichtmedizinischer Rivale

Status: kreative Vergleichsausgabe, keine Entzifferung.

## Ergebnis

Der stärkste Rivale ist kein reines Wasserwerk, sondern:

`ILLUSTRIERTES_PFLANZENROHSTOFF_UND_WASCHHAUSREGISTER_PLUS_EIGENSTAENDIGER_ARBEITSALMANACH`

Das reine Wasserwerk erklärt die sechs Biological-Records unmittelbar, aber
nur `6/14 = 42,9 %` der Record-/Diagrammeinheiten als Inhalt. Die fünf
Pflanzenbilder erzwingen ein Rohstoffregister, die drei Kreis-/Sternseiten ein
Almanachregister. Der Hybrid zahlt daher zwei zusätzliche Domänenschablonen
und zwei nicht sichtbare Brücken:

1. Die fünf Pflanzenlose liefern Wasch-, Färbe-, Duft-, Zurichtungs- oder
   Bindemittel an den Bade-/Waschhausbetrieb.
2. Die drei Diagramme terminieren oder wählen Werkstattarbeiten.

Keine Karte und kein vollständiges Feld belegt eine dieser Brücken. Der Hybrid
ist dennoch der faire stärkste nichtmedizinische Kontrolltext, weil die
Biological-Seiten einen wirklichen Apparate-/Auslasslayer besitzen und die
gemeinsamen V56-Prompts generische Betriebsgrößen statt medizinischer Wörter
sind.

## Ausführbarer Weg source → cards → workflow

Der Rivale benutzt unverändert die V57-Maschine. Ein Meister muss zunächst
einen normierten Arbeitszettel liefern:

```text
WORK_ORDER := REGISTER + VISIBLE_OWNER + RECORD_TEMPLATE + CELL+
CELL       := LOCAL_EXACT_CARD_ID*
              + optional CORE_CONTROL
              + copied JOIN/SPACE
              + optional attached CLOSE
LAYOUT     := copied LINE_RESET positions

CORE_CONTROL :=
  P01  Vorgabeparameter aufrufen
  P02  Standardslot setzen
  P03  lokalen Relationsslot setzen
  P04  aktiven Arbeitsstand verknüpfen
```

Die acht Tier-B-Werte bleiben Fragezeichen-Mnemonics. Sie dürfen eine
Korrektur anregen, wählen aber keine Karte. Jede andere Bedeutung wird als
`LOCAL(EXACT_CARD_ID)` aus dem passenden Herbal-, Bio- oder Astro-Bogen
kopiert. `CLOSE` bestätigt nur die Zelle; `JOIN`, `SPACE` und Zeilenreset
tragen keine Handlung.

Beim Rücklesen entsteht zuerst nur:

```text
OWNER_HANDLE
+ PARAMETER / STANDARD_SLOT / RELATION_SLOT / LINK_ACTIVE
+ LOCAL_CARD_IDS
+ OPEN_OR_CLOSED_FIELD
+ PHYSICAL_REFLOW
```

Erst ein registerlokales Betriebsbuch erweitert dies zum konkreten Ablauf:

```text
Pflanzenmaterial:
  ANNEHMEN > TRENNEN > AUSZIEHEN > DOSIEREN > LAGERN/AUSGEBEN

Bade-/Waschhaus:
  CHARGE > BECKEN > TEMPERIEREN > LEITEN > KLÄREN > ABLASSEN > ÜBERGEBEN

Arbeitsalmanach:
  ADRESSE WÄHLEN > LOKALEN WERT KOPIEREN > ARBEIT STARTEN/HALTEN/VERSCHIEBEN
```

Dieser Weg ist deterministisch, sofern exakte Karten, Positionen und Layout
schon im Exemplar stehen. Aus freier Werkstattprosa allein ist er ebenso wenig
deterministisch wie die medizinische Lesung.

## Vollständige nichtmedizinische Ausgabe

`V58_R3_FOURTEEN_OPERATING_ENTRIES.tsv` enthält alle Einheiten:

- fünf Herbal-Rohstofflose mit zusammen 20 Feldern und 100 Ereignissen;
- sechs Bade-/Waschhausläufe mit 115 Feldern und 281 Ereignissen;
- drei getrennte Almanachdiagramme mit 142 Loci und 395 Gruppen.

Die feste Gesamtform bleibt damit `5 + 6 + 3 = 14` Einheiten,
`135/135` Prosa-Felder, `381/381` Prosa-Ereignisse und `395/395`
Astro-Gruppen. Das ist formale Abdeckung, keine zusätzliche Semantik.

### Herbal

Die Bilder werden als Materialbesitzer gelesen. H1/H2 buchen Wurzel- und
Oberteilansatz, H3 einen geklärten Duft-/Färbeauszug, H4 Blattwaschmittel und
Polierpaste, H5 einen Binder/Klärhilfsposten. Die Prozessfolge ist jeweils
ausführbar. Ihr Preis sind fünf individuelle, nicht abgebildete
Werkstattprodukte. Besonders H1 verliert gegen den ausgewählten medizinischen
Abiss-Wasser-Vergleich; H5 besitzt in der erlaubten Basis gar keinen engen
nichtmedizinischen Mechanismus.

### Biological

Hier ist der Rivale am stärksten. Die sechs Records bilden einen
Grundkreislauf, eine Einzelstation, einen langen Spül-/Filterzyklus, eine warme
Nachwäsche, eine Schichtübergabe und einen offenen Kaltfiltergang. Personen
können Badende oder Bediener sein, ohne Krankheiten zu behaupten. Umgekehrt
stützen zwei Labels an offenen Auslässen ohne lokale Figur einen echten
Apparat. Kein Kartenwert bedeutet trotzdem Wasser, Becken, Rohr, Tuch,
Temperatur oder Ware.

### Astro

Die Diagrammarchitektur wird nicht umgedeutet: f67r2 bleibt ein 7/12-Selektor,
f68r1 ein räumliches Zentrum-plus-28-Verzeichnis ohne Start oder Richtung und
f69v ein geordneter 28er-Regelkatalog. Nur der **Anwendungszweck** wird
nichtmedizinisch als Arbeitsalmanach gesetzt. Das kostet drei lokale
Inhaltsannahmen. Eine direkte f68r1↔f69v-Zuordnung bleibt verboten.

## Vergleich und Kostenrechnung

Die vollständige Matrix steht in `V58_R3_COMPARISON.tsv`. Die Skala `0–2`
misst nur relative Passung in der festen Sidequest-Ausgabe:

- `2`: direkt beziehungsweise vollständig innerhalb der ausgewählten Form;
- `1`: ausführbar, aber mit erheblichen lokalen Ergänzungen;
- `0`: das Modell scheitert für diesen Prüfpunkt.

Auf acht vorab genannten Kriterien erhält der Rivale `10/16`, die ausgewählte
iatromedizinische Theorie `12/16`. Die Punktzahl ist ein transparentes
Arbeitsurteil, kein statistischer Test.

Wichtige Gleichstände:

- Beide bewahren 381 Prosaereignisse und 395 Astro-Gruppen.
- Beide besitzen nur 45/381 harte Prompt-Ereignisse und 145/381 ausgewählte
  schwache/formale Annotationen.
- Bei beiden liegen 162/173 Prosa-Kartentypen außerhalb des elfteiligen
  Brückendecks.
- Beide brauchen Bildbesitzer, lokale Exemplare und zwei unbelegte
  registerübergreifende Inhaltsbrücken.
- Beide sind nur als beaufsichtigte Exemplarlehre lernbar.

Gezählte lokale Inhaltsausnahmen des Rivalen: acht — fünf individuelle
Herbal-Endprodukte und drei Arbeitsalmanach-Funktionen. Die sechs Bio-Records
benötigen dagegen nur eine wiederverwendbare Anlagenregel. Die Medizinseite
hat mindestens dieselbe Größenordnung: fünf lokale Arznei-/Anwendungsartikel
und drei Astro-Funktionen; ihre Bio-Schicht bleibt ein gemischtes
Patienten-/Apparateregister.

## Historischer Mechanismus

Ein um 1420 geführtes Werkstattbuch könnte bebilderte Rohstoffblätter,
abgekürzte Chargenzellen, Musterkopie, sichtbare Anlagenargumente und einen
separaten Kalenderteil vereinigen. Badehaus, Waschhaus, Färbe-/Zurichtungsarbeit
und Hauswirtschaft bilden dafür eine plausible praktische Ökologie. Innerhalb
der erlaubten V53–V57-Basis fehlt jedoch ein naher nichtmedizinischer Donor.

Die medizinische Seite besitzt spezifischere ausgewählte Analogien: den
Abiss-/Teufelsabbiss-Wassermechanismus, therapeutische Badliteratur und
iatromathematische Regimenpraxis. Diese Analogien beweisen ebenfalls keine
Kartenwerte, geben dem medizinischen Hybrid aber den historischen Vorsprung.

## Entscheidung

`PURE_WATERWORK_WITHDRAWN`

`NONMEDICAL_HYBRID_RETAIN_AS_STRONGEST_CONTROL`

`IATROMEDICAL_THEORY_RETAINS_NARROW_OVERALL_LEAD`

Der nichtmedizinische Rivale gewinnt die Biological-Schicht und zeigt, dass
die gemeinsame Kartenkontrolle keinerlei Medizin erzwingt. Er gewinnt die
zehn Seiten insgesamt nicht: Er reduziert weder opake Karten noch stille
Argumente, und seine Pflanzenprodukte sowie der Werkstattalmanach benötigen
mehrere unbelegte Zwecke. Die schärfste künftige Trennung wäre ein externer,
unabhängig ausgewählter Referent für **einen** Pflanzenendzweck oder **eine**
Astro-Regel; ohne ihn bleiben beide vollständigen Texte kreative
meisterseitige Expansionen.

Es wurden keine neuen Seiten, keine Substring-/Hostwerte und keine versiegelten
Seitendaten verwendet. Kein Commit oder Push wurde ausgeführt.

# V54 R2 — historische Biological-Ausgabe

**Rolle:** handschriftenkundiger Arzt- und Herbal-Schreiber um 1420.
**Status:** vollständige kreative Record-Ausgabe, keine Entzifferung.
**Umfang:** f81v/1, f82r/1 und f83r/1–4; 6 Records, 115 Felder und 281
Ereignisse.

## Auswahl

Die beste historische Gesamtlesung ist weder ein reines Frauenkrankheitenbuch
noch ein bloßer Rohrplan, sondern ein **therapeutisches Bad-/Irrigations-
Arbeitsblatt mit eigenständiger Apparateschicht**:

- Menschen- und insbesondere Frauenfiguren machen körperbezogene
  Badetherapie als Seitenrahmen plausibel.
- Becken, begrenzte Farbzonen, Bögen, Röhren und offene Auslässe machen eine
  technische Bedienfolge ebenso real.
- Kein lokaler Textanker nennt Frau, Gebärmutter, Menstruation, Bad, Wasser,
  Rohr oder Gefäß.
- Deshalb bezeichnet die flüssige Ausgabe Arbeitsgänge des ganzen Records;
  sie verteilt diese Gegenstände nicht auf einzelne Karten.

Ein städtisches Badehaus ohne Heilzweck bleibt der stärkste Gesamtgegner. Eine
enge gynäkologische Lesung — etwa Menstruationsförderung oder
Empfängnisvorbereitung — fällt hinter das breitere therapeutische Bad zurück.

## Schichtentrennung

1. **Strikt:** exakte Reihenfolge und Formelbaum aus V49; V50/V51 liefern nur
   `SETZEN`, `MARKIEREN`, `VERKNÜPFEN`, `AN?`, `BEREITUNG?`, `TEIL?`,
   `MASS?`, `KLAR?`, `VERWENDEN?`, `ABLASSEN?`, `SPÜLEN?`, `BEREIT?`,
   `WARM?`, `ZUVOR?`.
2. **Formal:** `CLOSE` ist nur Feldschluss. Eingebettete `<ARG_*>` erben kein
   Ganzkarten-Merkwort. `FRAME_OT` realisiert den formalen Operator
   `OT=MARKIEREN`; `FRAME_O` bleibt ein unübersetzter Rahmen.
3. **Bild:** Figur, Becken, Röhre, Bogen und Auslass sind Seitenargumente, nie
   automatisch Besitzer eines benachbarten Feldes.
4. **Historische Erweiterung:** Wasser, Tuch, warm/kühl, Bad, Spülung,
   Kompresse und Gefäßfolge werden erst für Feld- oder Recordprozess ergänzt.

Die 115 bereits vollständigen V42/V49-Felddefaults dienen als
Abdeckungsnachweis; V54 baut sie nicht erneut in 115 redundanten Zeilen auf.
`V54_R2_SIX_RECORDS.tsv` bewahrt für jeden Record die vollständige
Prozesslesung, die gesamte ausgewählte Ankerspur und den stärksten Rivalen.

## Zählung und Ankerdruck

| Record | Felder | Ereignisse | ausgewählte Anker | opak | Schlussfelder |
|---|---:|---:|---:|---:|---:|
| f81v/1 | 24 | 66 | 27 | 39 | 17 |
| f82r/1 | 26 | 62 | 24 | 38 | 19 |
| f83r/1 | 38 | 86 | 36 | 50 | 31 |
| f83r/2 | 20 | 47 | 19 | 28 | 16 |
| f83r/3 | 5 | 11 | 4 | 7 | 2 |
| f83r/4 | 2 | 9 | 3 | 6 | 0 |
| **Summe** | **115** | **281** | **113** | **168** | **85** |

Die 113 benannten Ereignisse verteilen sich auf: 22× `SETZEN`, 22×
`VERKNÜPFEN`, 11× `MASS?`, 10× `AN?`, je 8× `ABLASSEN?` und `SPÜLEN?`, je
7× `MARKIEREN`, `VERWENDEN?` und `WARM?`, 4× `BEREIT?`, 3× `KLAR?`, 2×
`BEREITUNG?`, je 1× `TEIL?` und `ZUVOR?`. Die scheinbar medizinisch
entscheidenden Inhalte liegen somit überwiegend in den 168 opaken Ereignissen
und der Bild-/Quellenerweiterung.

## Bildbefund: Frauen oder Apparateschema?

Die Entscheidung verwendet ausschließlich die vorhandene erlaubte
Dokumentation:

- **f82r:** GDT239 beschreibt zwei obere Figurenpaare mit verbindenden
  Linien/Röhren, eine grün begrenzte Zone mit mehreren Figuren und eine
  getrennte blaue Zone mit einer Figur. Von 13 Labels ist nur f82r.10 sicher
  *auf* einem kreuzförmigen Bauteil; zwölf sind lediglich nahe einem Objekt.
  Das Dossier weist ausdrücklich jede Lesung `BACA = Wasser/Fluss` zurück.
- **f83r:** Die Direktsichtung findet zwei obere Labels an einem gemeinsamen
  Bogen in gemischter Nähe von Mensch und Röhrenende; der Besitzer ist
  unentscheidbar. Zwei untere Labels stehen unmittelbar an offenen
  mehrstrichigen Auslässen, ohne lokale Figur. Hier gewinnt die
  Apparateschicht lokal klar.
- **f81v:** V42 lässt Figuren als Patientinnen, Stationen oder Zustandsbilder
  offen; keine Feld-Figur-Zuordnung ist gesichert.

Damit sind die Figuren echte Evidenz für einen körperbezogenen
Darstellungsraum, aber keine Lizenz für „Gebärmutter“, „Vagina“, „Patientin“
oder einen bestimmten Körperteil in der Schrift. Umgekehrt sind die Auslässe
echte Apparateevidenz, aber kein Beweis für ein nichtmedizinisches Wasserwerk.

## Historische Vergleichsgrößen

Die Analogien kalibrieren nur das mögliche Artikelgenre:

1. Das im 13.–15. Jahrhundert breit überlieferte **Trotula-Kompendium** kennt
   Frauenbäder, Waschungen, Dämpfe, Pessare und Auflagen. Das macht eine
   körperbezogene Frauenheilkunde mit warmen Medien gewöhnlich, liefert aber
   keinen mehrstufigen verrohrten Kreislauf. Referenz: Monica H. Green (Hg./
   Übers.), *The Trotula: A Medieval Compendium of Women's Medicine*, 2001.
2. Petrus von Ebolis **De balneis Puteolanis** verbindet bildlich dargestellte
   Badende mit krankheitsbezogenen Thermalbädern. Es ist der stärkste
   ikonographische Genrevergleich, erklärt jedoch keine Folge kleiner
   Setz-/Verknüpf-/Schlussfelder.
3. **Magninus Mediolanensis, Regimen sanitatis** behandelt Temperatur,
   Aufenthaltsdauer, Zeitpunkt und Nachverhalten beim Bad. Das stützt
   Warm-/Ruhe-/Wechselgänge, nicht ihre Bindung an eine einzelne Frau.
4. Die lateinische chirurgische **al-Zahrawi-Tradition** kennt Kanülen,
   Spritzen und klystierartige Flüssigkeitszuführung. Sie macht lokale
   Irrigation technisch denkbar, ist aber keine Parallele für die gesamte
   gezeichnete Beckenlandschaft.
5. Ein spätmittelalterliches **Badehaus** konnte Wasser erwärmen, in Zuber
   schöpfen, ablassen, Tücher und Kräuterauflagen verwenden. Für einen
   geschlossenen modernen Rohrkreislauf oder präzise hydraulische Ventile
   bietet diese gewöhnliche Praxis keinen Freibrief.

## Sechs Recordentscheidungen

### B1 — f81v/1: Grundbad und Spülcharge

Mehrere Portionen werden gesetzt, mit vorhandenem Arbeitsstand verbunden,
gemessen, warm gehalten, wiederholt gespült, abgesetzt und an eine weitere
Station gegeben. Medizinisch ist dies das gemeinsame Grundbad; technisch ein
Zisternen-/Mischgang. Öl, Rücklauf und Frauenkrankheit aus V42 sind nur noch
Record-Erweiterungen. **Konfidenz: niedrig bis mittel.**

### B2 — f82r/1: individuelle Badestation

Portionen werden warm gehalten, geklärt, verwendet, ergänzt und abgelassen;
warm und kühl können wechseln. Die beste medizinische Ausgabe ist Teilbad
oder örtliche Waschung mit möglicher Tuchkompresse. V42s ausdrücklicher Trank
wird gestrichen. GDT239 hält die Apparaturlesung vollständig offen.
**Konfidenz: niedrig bis mittel.**

### B3 — f83r/1: langer Irrigations-/Badgang

Die stärkste Prozessspur der sechs Records: Markieren, Messen, Setzen,
wiederholtes Ablassen, Verwenden, Spülen, Erwärmen und Erreichen eines
Bereitungsstands. Dies passt zu örtlicher Lavage in einer Badeanlage ebenso
wie zu einem hydraulischen Gefäßprozess. Die lokal menschenfreien Auslässe
sind der stärkste Gegenbeleg zur Patientenprosa. **Konfidenz: niedrig bis
mittel.**

### B4 — f83r/2: warmer Nachgang

Ein bezeichneter Teil wird warm gespült, mit dem vorigen Stand verwendet,
durch Tuch geklärt, erneut gemessen, abgelassen und nachgegossen. Medizinisch
ist dies Nachwaschung/Kompressengang; technisch ein zweiter Klärzyklus.
Bindung und zweifaches Seihen bleiben Ganzrecordwetten. **Konfidenz: niedrig
bis mittel.**

### B5 — f83r/3: kurzer Wärme- und Übergabegang

Nur `AN? → VERKNÜPFEN → MASS? → VERKNÜPFEN` ist ausgewählt. Erwärmen,
Zeitmaß, zweite Öffnung und Rühren stammen vollständig aus der
Quellenexpansion. Ein technischer Nachtrag ist sparsamer als ein neuer
Patientenfall. **Konfidenz: niedrig.**

### B6 — f83r/4: offenes Schlussaddendum

Formal bleiben nur `VERKNÜPFEN → MASS? → VERKNÜPFEN`; beide Felder sind
offen. Die bevorzugte Lesung ist eine kalte/ungekochte Filtrations- und
Übergabenotiz. V42s „Person an das Becken“ wird verworfen; Tuch, erste
Öffnung und Körperstelle bleiben Rivalen. **Konfidenz: niedrig.**

## Revision gegenüber V42 und V49

- `E=BIS` und `CKHY=VERBINDUNG/LEITUNG` werden vollständig entfernt.
- `AL=ZU` wird zu objektlosem `AN?`; Körperstelle, Becken oder Auslass stehen
  nie still im Atom.
- `OR=ANSATZ` wird `BEREITUNG?`; Flüssigkeit und Charge sind Recordkontext.
- `EY=FERTIG` wird `KLAR?`, `OKEEY=LAUWARM` wird `WARM?`, `OKY=NUTZEN` wird
  `VERWENDEN?`, `CHEY=ANTEIL` wird `TEIL?`.
- `LCHE=ABLASSEN?` und `OKE=SPÜLEN?` bleiben kreativ nützlich, aber vollständig
  mit `CLOSE` konfundiert.
- `CLOSE` spricht nicht „beende den Schritt“; es markiert nur das Feldende.
- Trinken, Binden, Öl, Frau, Gebärmutter, erste/zweite Öffnung, unteres Becken,
  Tuch und klares Strömen werden aus den Kartenwerten entfernt. Wo sie in der
  Ausgabe verbleiben, sind sie sichtbar als Record- oder Quellenexpansion.

## Urteil

V54 verbessert V42/V49 nicht durch mehr medizinische Einzelheiten, sondern
durch eine strengere Mischentscheidung: **therapeutische Balneologie mit
Apparatebetrieb**. Die Menschen verhindern, dass ein reines Rohrregister
genügt; die lokal menschenfreien Auslässe und die hohe Schlussdichte
verhindern, dass eine fortlaufende Frauenheilkundeprosa genügt. Keine
Klangzuordnung, Krankheit oder anatomische Öffnung ist gewonnen.

## Protokollabweichung

Bei einer falschen PDF-Seitenformel wurde versehentlich ein einziges
Faksimilebild von f88v/f89r geöffnet. Es wurden daraus keine Textdaten,
Bildargumente, Pflanzen-/Apparaturwerte oder Kartenannahmen übernommen. Die
Abbildung wurde vollständig verworfen; danach erfolgte keine weitere
Bildöffnung. Sämtliche oben verwendeten Beobachtungen stammen aus der
freigegebenen V42-, GDT239- und f83r-Dokumentation.

**Validierung: PASS — 6 Records, 115 Felder, 281 Ereignisse; 113 ausgewählte
Anker, 168 opake Ereignisse und 85 formal geschlossene Felder.**

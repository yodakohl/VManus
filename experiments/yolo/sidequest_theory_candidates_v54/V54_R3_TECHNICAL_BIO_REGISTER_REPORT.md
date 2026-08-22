# V54 R3 — Technisches Bio-Register mit ausführbaren Arbeitszellen

Status: vollständige kreative R3-Arbeitslesung der sechs erlaubten Records auf
`f81v`, `f82r` und `f83r`; keine Entzifferung und keine bestätigte historische
Buchgattung. `f84` und `f84r` wurden nicht geöffnet.

## Ergebnis

Die beste technische Defaultwelt ist ein **Becken-, Leitungs- und
Chargenregister mit lokalen Commits**. Sie liest die 115 Felder nicht als 115
Sätze, sondern als geordnete Arbeitszellen. Sichtbare Figuren und
becken-/leitungsartige Formen dürfen die stillen Owner liefern; kein solches
Nomen wird dadurch zum Kartenwert.

Die sechs vollständigen Recordfassungen und ihre lückenlosen Feldbereiche
stehen in `V54_R3_SIX_RECORD_TECHNICAL_SUMMARIES.tsv`. Die dortigen Graphen
decken `F1–F24`, `F1–F26`, `F1–F38`, `F1–F20`, `F1–F5` und `F1–F2` ab. Damit
wird die bereits in V42 publizierte kartengenaue Vollabdeckung aller 115
Felder und 281 Ereignisse genutzt, ohne sie in V54 redundant neu abzudrucken.

## Ausführbarer Zustand

Für jeden Record gilt derselbe kleine Zustandsvektor:

```text
S = <BECKEN, LEITUNG, CHARGE, TEMPERATUR,
     ZUFLUSS, ABFLUSS, STATION, COMMIT>

apply(FIELD, S) -> S'
OPEN              -> S' wird an die nächste Zelle weitergereicht
final CLOSE       -> lokaler COMMIT nach dem Payload; keine gesprochene Karte
```

Die acht Achsen sind praktische Registerplätze, keine Übersetzungen. Ein Feld
darf mehrere Plätze ändern. Ein offenes Record-Ende wird als externe Übergabe
geführt; es erhält keinen erfundenen Schluss. Das ist besonders wichtig für
f83r-R3 und f83r-R4.

## Vier strikt getrennte Ebenen

1. **Kartenanker:** ausschließlich die ausgewählten V50/V51-Merkwörter.
   `CKHY`, `E` und alle übrigen opaken Karten bleiben `UNKNOWN`.
2. **Formale Achse:** exakte `SET`, `MARK`, `LINK`, `FRAME`, `RIGHT` und
   `CLOSE`-Struktur. RIGHT erbt niemals `MASS?` oder `AN?` von einer Karte.
3. **Sichtbarer Owner:** Figur, Becken, Öffnung oder Leitung nur aus Bild und
   Layout; die Recordzuordnung bleibt eine stille Annahme.
4. **Lokale Expansion:** konkrete Wörter wie Wasser, Tuch, Filtereinsatz,
   Rücklauf, Gefäß, Wärme oder Badender. Sie machen den Ablauf ausführbar,
   zählen aber nicht als Kartenbeleg.

V52 bleibt damit unverändert:

```text
FIELD := NONCLOSE* TERMINAL?
```

Aus der Feldgrammatik entsteht keine deutsche Satzsyntax. Der Prozessgraph ist
eine bewusst gewählte technische Welt, die erst nach der Ankerlesung geprüft
wird.

## Vollständigkeits- und Strukturzählung

| Record | Felder | Ereignisse | CLOSE | OPEN | SET | MARK | LINK | FRAME | RIGHT | ausgewählte Anker | UNKNOWN |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| f81v-R1 | 24 | 66 | 17 | 7 | 4 | 1 | 11 | 9 | 12 | 27 | 39 |
| f82r-R1 | 26 | 62 | 19 | 7 | 9 | 1 | 2 | 3 | 14 | 24 | 38 |
| f83r-R1 | 38 | 86 | 31 | 7 | 7 | 4 | 2 | 7 | 19 | 36 | 50 |
| f83r-R2 | 20 | 47 | 16 | 4 | 2 | 1 | 3 | 4 | 7 | 19 | 28 |
| f83r-R3 | 5 | 11 | 2 | 3 | 0 | 0 | 2 | 3 | 2 | 4 | 7 |
| f83r-R4 | 2 | 9 | 0 | 2 | 0 | 0 | 2 | 2 | 0 | 3 | 6 |
| **Gesamt** | **115** | **281** | **85** | **30** | **22** | **7** | **22** | **28** | **54** | **113** | **168** |

`SET`, `MARK`, `LINK`, `FRAME`, `RIGHT` und `CLOSE` sind überlappende
Formelmerkmale. „Ausgewählte Anker“ und `UNKNOWN` sind dagegen disjunkt und
summieren sich auf 281. Die vier biologischen `CKHY`-Vorkommen zählen nach V51
zu `UNKNOWN`; so bleibt die V52-Gesamtdeckung konsistent.

## Modellvergleich

### Technisches Betriebsregister

Es gewinnt bei f81v-R1, f82r-R1, f83r-R1 und f83r-R2 klar als kreative
Defaultlesung. Wiederholtes Spülen, Setzen, Temperieren, Weiterleiten,
Ablassen und lokales Schließen ergibt gewöhnliche Arbeitszellen. Der Kontrast
zwischen LINK-lastigem f81v, SET-lastigem f82r und CLOSE/MARK-lastigem
f83r-R1 lässt sich als unterschiedliche Betriebsaufgabe ausdrücken.

Es gewinnt f83r-R3 und f83r-R4 nur provisorisch. Dort muss der sichtbare
Beckenbestand als Eingangszustand übernommen und der Commit außerhalb des
Records gesucht werden.

### Medizinische Anwendung

Sie bleibt der stärkste Rival bei f82r-R1 und f83r-R2: sichtbare Menschen in
Becken, Wärme, Flüssigkeit und ein befestigter Materialeinsatz passen ohne
Weiteres zu einer Badetherapie. Sie verliert als Kartenlesung, weil kein
ausgewählter Anker Krankheit, Körperteil, Patient, Arznei oder Indikation
bezeichnet. Bei den langen Records würde sie zudem viele einzelne
Anwendungssätze aus wiederkehrenden Bedienformen machen.

### Formular- oder Musterregister

Dieses Modell erklärt Parataxe, Wiederholung und 85 terminale Felder am
sichersten, ohne Stoffbedeutungen zu erfinden. Es ist der stärkste Rival für
f81v-R1, f83r-R1, f83r-R3 und besonders f83r-R4. Es verliert dort, wo eine
vollständige konkrete Quellenfassung verlangt ist: reine Formularrollen sagen
nicht, welcher Zustand über eine Öffnung fließt, erwärmt oder abgelassen wird.

Das faire Urteil lautet daher:

```text
lange Bio-Records:       technischer Betrieb als beste kreative Expansion
sichtbare Bad-Szenen:    medizinische Anwendung bleibt realer Inhaltsrivale
kurze/offene Records:    Formular-/Musterregister nahezu gleich stark
belegte Kartensemantik:  keines der drei Modelle
```

## Revision gegenüber V42 und V49

- V42s Badehaus-/Wasserwerkarchitektur wird beibehalten, aber ausführbar in
  acht Zustandsachsen zerlegt.
- V42s semantisches „beende die Zelle“ wird entfernt. `CLOSE` ist nur lokaler
  Commit; 30 Felder bleiben offen.
- V49s `E=BIS`, `CKHY=VERBINDUNG`, `OKEEY=LAUWARM`, `EY=FERTIG`,
  `OR=ANSATZ` und `CHEY=ANTEIL` werden gemäß V50/V51 korrigiert zu
  `UNKNOWN`, `UNKNOWN`, `WARM?`, `KLAR?`, `BEREITUNG?` und `TEIL?`.
- V49s medizinisch klingendes „trinken“ auf f82r wird in dieser technischen
  Welt zur Entnahme einer Prüfportion. Beides ist lokale Expansion, kein
  Kartenwert.
- Becken, Leitung, Wasser, Filter, Materialpaket, Badender, Rücklauf und
  Stationsrichtung bleiben stets in den Bild-/Registerspalten; sie werden
  nicht in unbekannte Karten hineingelesen.

## Stärkster Gesamtwiderspruch

168/281 Ereignisse bleiben ohne ausgewählten Anker. Selbst die ausführbarste
Beckenwelt kann deshalb mit gewöhnlicher Betriebsroutine fast jede opake Folge
füllen. Die 85 Feldschlüsse stützen Zellen, identifizieren aber weder
„Commit“ als Manuskriptwort noch Wassertechnik als Inhalt. V54 verbessert die
interne Handhabbarkeit und korrigiert V42/V49-Konfundierungen; es liefert keine
unabhängige Bestätigung einer Badehaus-, Medizin- oder Formularlesung.

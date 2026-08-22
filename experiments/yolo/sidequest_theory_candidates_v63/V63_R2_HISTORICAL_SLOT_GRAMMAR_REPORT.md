# V63 R2 — Historischer Drucktest einer Prompt-Slotgrammatik

Status: kreative Quellenrekonstruktion; keine Entzifferung, keine Laut- oder
Sprachzuweisung.

## Entscheidung

**Bedingt behalten: als knappe, exemplarabhängige Registergrammatik; nicht als
vollständige Satzgrammatik.** Von 116 V61-Statements besitzen 61 (52,6 %) einen
vorab lizenzierten Exact-Card- oder Formalprompt. Davon passen 46 ohne Eingriff
in eine oder mehrere Vorlagen, 12 nur mit nichtkanonischer Nachstellung und 3
enthalten einen echten wiederholten Exact-Slot-Konflikt. 55 Statements bleiben
korrekt `EXEMPLAR_ONLY`.

Das ist für einen Schreiber um 1420 als Rezept-/Arbeitsregister lehrbar: vier
anonyme Laufregister werden gehalten und acht kurze Rubriktypen aus dem
Exemplar ausgefüllt. Es ist nicht selbstgenügsam. Die sichtbaren Prompts
bestimmen weder Stoff, Einheit, Patient, Körperteil, Gefäß noch Dauer.

## Fester Test vor der Abbildung

Die acht Vorlagen wurden als exklusive Lizenzierungstabelle festgelegt, bevor
die 116 Statements mechanisch zugeordnet wurden:

| Vorlage | lizenzierende sichtbare/formale Anker | Quellslots |
|---|---|---|
| `T1_MEASUREMENT` | `MASS?`, `ANTEIL?`, `VORGABEPARAMETER?` | `ACTIVE > PARAMETER[LOCAL_EXEMPLAR]` |
| `T2_DESTINATION` | `ZIEL?`, `LOKALEN_RELATIONSSLOT_SETZEN` | `ACTIVE > TARGET` |
| `T3_BATCH_REFERENCE` | `ANSATZ?`, `VORIGES?`, `STANDARDSLOT_SETZEN`, `AKTIVEN_ARBEITSSTAND_VERKNÜPFEN` | `PREVIOUS(optional) > ACTIVE` |
| `T4_STATE_GATE` | `BEREIT?`, `KLAR?` | `ACTIVE > STATE > CRITERION[LOCAL_EXEMPLAR]` |
| `T5_APPLY` | `ANWENDEN?` | `ACTIVE > TARGET` |
| `T6_TEMPER` | `TEMPERIEREN?` | `ACTIVE > DEGREE_OR_DURATION[LOCAL_EXEMPLAR]` |
| `T7_RINSE` | `SPÜLEN?` | `ACTIVE > TARGET > FORMAL_CLOSE` |
| `T8_DRAIN` | `ABLASSEN?` | `ACTIVE > TARGET > FORMAL_CLOSE` |

Die vollständigen Frames, historischen Mechanismen und Gegenlesungen stehen
in `V63_R2_SLOT_TEMPLATES.tsv`. `OWNER`, `ACTIVE`, `TARGET` und `PREVIOUS`
sind ausschließlich die anonymen recordlokalen V62-Register. `LOCAL_EXEMPLAR`
ist ein offener Eintrag, kein still erschlossenes Sachwort.

Abbildungsregeln:

1. Reihenfolge ist die Reihenfolge der V60-`event_serials`, nicht die physische
   Zeile. Ein Formalprompt und `MASS?` am selben Ereignis zählen als ein Anker.
2. Die kanonische Arbeitsfolge lautet Rückgriff/Ansatz → Maß → Temperieren →
   Zustandsprüfung → Ziel/Anwendung → Spülen oder Ablassen. Der Zielslot darf
   unmittelbar vor oder nach seiner Handlung stehen; er wurde deshalb bei der
   Inversionsprüfung nicht erzwungen.
3. Eine wiederholte identische Exact-Card im selben V61-Statement bleibt ein
   Slotkonflikt. Sie wird nicht still zu zwei verschiedenen Größen umgedeutet.
4. `SPÜLEN?` und `ABLASSEN?` müssen der letzte lizenzierte Handlungsanker sein;
   `CLOSE` ist formal und bleibt unausgesprochen.
5. Ohne einen der festgelegten Anker lautet das Ergebnis `EXEMPLAR_ONLY`, auch
   wenn die V61-Lokalprosa attraktiv klingt.

## Vollständiges Ergebnis

| Klasse | Statements | Anteil aller 116 |
|---|---:|---:|
| `SINGLE_TEMPLATE_FIT` | 32 | 27,6 % |
| `COMPOSITE_FIT` | 14 | 12,1 % |
| `FITS_WITH_ORDER_STRAIN` | 12 | 10,3 % |
| `CONFLICTING` | 3 | 2,6 % |
| `EXEMPLAR_ONLY` | 55 | 47,4 % |

Unter den 61 promptlizenzierten Statements sind 46/61 (75,4 %) glatt, 12/61
(19,7 %) umstellungsbedürftig und 3/61 (4,9 %) konfliktbelastet. Die 85
ausgewählten Exact-Card-Vorkommen und 45 Formalprompt-Vorkommen ergeben wegen
elf überlappender `MASS?`/`VORGABEPARAMETER?`-Ereignisse 119 geordnete
Templateanker.

| Vorlage | Anker | Statements mit Vorlage |
|---|---:|---:|
| Messung | 22 | 20 |
| Ziel | 16 | 14 |
| Ansatz/Rückgriff | 37 | 25 |
| Zustand | 11 | 10 |
| Anwenden | 10 | 10 |
| Temperieren | 7 | 7 |
| Spülen | 8 | 8 |
| Ablassen | 8 | 8 |

Alle 16 terminalen Aktionskarten stehen am Ende ihres jeweiligen Ankerstroms;
kein Statement kombiniert `SPÜLEN?` und `ABLASSEN?`. Das ist die stärkste
positive Ordnungsbeobachtung. Sie bleibt durch V60s bekannte Konfundierung mit
zwei formalen Schlussfamilien relativiert.

Registerunterschied: Herbal hat 14/19 promptlizenzierte Statements (10 glatt,
3 umgestellt, 1 konfliktbelastet); Biological 47/97 (36 glatt, 9 umgestellt,
2 konfliktbelastet). Das Rezeptregister trägt die Vorlage also besser als die
kurzen Bio-Arbeitszellen. Dort bleiben 50/97 Aussagen exemplarabhängig.

## Vollständige Quellbeispiele

Die Klammern trennen sichtbaren Anker und stille Registerfüllung. Kein
Klammerinhalt beansprucht eine Voynich-Lautung.

**Ansatz/Rückgriff → Maß, H2-S002 (glatt):**

> `[STILL:OWNER=H2:O01] ; [ANCHOR:e25:K:ANSATZ? | e27:F:AKTIVEN_ARBEITSSTAND_VERKNÜPFEN | e28:K:VORIGES? | e29:F:AKTIVEN_ARBEITSSTAND_VERKNÜPFEN] [STILL:PREVIOUS=H2:I001] wieder aufnehmen und als [STILL:ACTIVE=H2:I002] führen ; [ANCHOR:e30:F:VORGABEPARAMETER?+K:MASS?] von [STILL:ACTIVE=H2:I002] den bezeichneten Anteil nach [STILL:PARAMETER=LOKALES_EXEMPLAR] nehmen.`

Historisch ist dies eine plausible kurze Rezept-/Vorratsfolge: laufenden oder
vorigen Posten übernehmen, danach dessen örtlich angegebenes Maß. Gegenlesung:
Kopierzeiger plus Parameter-/Losspalte, ganz ohne sprachlichen Rückgriff.

**Maß → Anwendung → nachgestelltes Ziel, H5-S001 (glatt):**

> `[STILL:OWNER=H5:O01] ; [ANCHOR:e77:F:VORGABEPARAMETER?+K:MASS?] von [STILL:ACTIVE=H5:I001] den bezeichneten Anteil nach [STILL:PARAMETER=LOKALES_EXEMPLAR] nehmen ; [ANCHOR:e81:K:ANWENDEN?] [STILL:ACTIVE=H5:I001] an [STILL:TARGET=H5:T001] anwenden ; [ANCHOR:e82:K:ZIEL?] [STILL:ACTIVE=H5:I001] an [STILL:TARGET=H5:T001] führen.`

Die Nachstellung des Zielmarkers ist für einen knappen Registereintrag
ausführbar. Der stärkere Gegenparse liest `ZIEL?` als Bildadresse und
`ANWENDEN?` als neutralen Operationscode.

**Temperieren → Spülen → stummer Schluss, B3-S028 (glatt):**

> `[STILL:OWNER=B3:O01] ; [ANCHOR:e293:K:TEMPERIEREN?] [STILL:ACTIVE=B3:I003] nach [STILL:DEGREE_OR_DURATION=LOKALES_EXEMPLAR] temperieren ; [ANCHOR:e294:K:SPÜLEN?] [STILL:TARGET=B3:T013] mit [STILL:ACTIVE=B3:I003] spülen ; [FORMAL:CLOSE;STILL].`

Die Folge passt ebenso zu Bad-/Irrigationsarbeit wie zu technischer
Apparaturreinigung. Weder Körpergebrauch noch Wasser ist sichtbar belegt.

**Klarheitsbedingung → Ablassen, B4-S015 (glatt):**

> `[STILL:OWNER=B4:O01] ; [ANCHOR:e353:K:KLAR?] [STILL:ACTIVE=B4:I007] stehen lassen, bis [STILL:CRITERION=LOKALES_EXEMPLAR] erfüllt ist ; [ANCHOR:e357:K:ABLASSEN?] [STILL:ACTIVE=B4:I007] nach [STILL:TARGET=B4:T010] ablassen ; [FORMAL:CLOSE;STILL].`

Das ist eine gute rezeptartige Endpunktfolge. Der gleich starke technische
Parse lautet Zustandslabel → Wasserwerk-/Werkstattablauf.

**Kein Prompt, H3-S002:**

> `[STILL:OWNER=H3:O01] ; [STILL:ACTIVE=H3:I001] [STILL:OPERATION=LOKALES_EXEMPLAR] [STILL:TARGET=H3:T002] ausführen.`

Hier ist gerade keine sichtbare Quellgrammatik gewonnen. Die ganze Operation
bleibt Exemplartext.

## Konflikte und stärkster Gegenvergleich

Die drei harten Wiederholungen sind:

- `H2-S003`: zweimal `ANSATZ?`;
- `B1-S002`: zweimal `MASS?`;
- `B3-S021`: je zweimal `BEREIT?` und `ZIEL?`.

Sie können durch parallele lokale Füller oder eine feinere Statementteilung
erklärt werden, aber V63 nimmt diese Reparatur nicht vor. Zwölf weitere
Statements besitzen 13 Umkehrungen der kanonischen Phasenfolge. Historische
Rezeptprosa erlaubt Nachstellungen; ein Formularmodell erklärt sie jedoch
einfacher als eine feste Syntax.

Der stärkste Gesamtrivale ist deshalb ein **semantikarmes Werkstattformular**:
SET/LINK/RELATION/PARAMETER sind Spalten- oder Kopierkontrollen, die Exact
Cards bezeichnen lokale Klassen beziehungsweise zwei Schlussoperationen. Das
Modell lernt dieselbe Abfolge ohne medizinische Wörter und trägt ebenso
Pflanzenrohstoff, Färberei, Wasserwerk oder Badehaus. Die medizinische Lesung
gewinnt lediglich historische Natürlichkeit in den Herbal-Folgen; sie gewinnt
keine exklusiven Referenten.

## Lehrbarkeit um 1420

Ein praktischer Schreiber könnte die Maschine durch Exemplarlernen beherrschen:

1. Bild-/Recordbesitzer einmal setzen;
2. laufenden und vorigen Posten getrennt halten;
3. acht Promptklassen als kurze Rubriken lernen;
4. Zahl, Einheit, Ziel und Prüfkriterium nur aus dem lokalen Exemplar einsetzen;
5. terminale Handlung ausführen und den formalen Schluss nicht mitlesen.

Der Lernaufwand ist kleiner als bei einer freien Geheimprosa, aber größer als
bei normaler Abbreviatur: Zielüberschreibung, doppelter Maßslot,
Ansatz/Previous-Verwechslung und das Aussprechen von `CLOSE` sind erwartbare
Kopierfehler. Ein Meisterexemplar oder mündliche Einweisung bleibt nötig. Die
55 `EXEMPLAR_ONLY`-Statements und V62s Verlaufsspeicher verhindern, dass ein
Lehrling den Text allein aus den Promptkarten rekonstruiert.

**Endurteil:** kohärente und lehrbare *Slot-Schicht* für ein
Rezept-/Arbeitsregister; zu dünn und zu registerabhängig für eine behauptete
Voynich-Satzgrammatik.

## Reproduzierbarkeit und Scope

Der Builder fragt die ausgewählten V60-, V61- und V62-TSVs nur über
`./vmanus-exp query-tsv` mit sieben einzeln angegebenen Allow-Werten und
`--forbid-prefix f84` ab. Er erzeugt 8 Templatezeilen und 116 Mappingzeilen;
alle 381 Eventserien werden genau einmal getragen. Die Validierung meldet
`PASS`. Keine neue Seite, kein `f84`/`f84r`, keine V63-Geschwisterdatei und
keine Klangzuordnung wurden benutzt.

# Sidequest V13 R1 — die L/O-Karte als fortsetzbarer Nachbarschaftslink

Date: 2026-08-21

Status: **explorative Arbeitshypothese, kein GDT-Ergebnis und keine
Uebersetzung**. Perspektive R1: Lehrmeister einer Schreibwerkstatt um 1420.

## Ergebnis vorweg

Die einfachste lehrbare Regel ist enger als das bisherige freie
`ASSOCIATE(active_node, local_or_inherited_node)`:

```text
MEDIAL:       A — L/O — B       => LINK(A,B)
KETTE:        A — L/O — B — L/O — C
                                => LINK(A,B); LINK(B,C)
FELDANFANG:       L/O — B       => LINK(inherited_left,B)
FELDENDE:     A — L/O           => LINK(A,inherited_right)
EINZELFELD:       L/O           => repeat/retain the inherited link
```

Die konstante Funktion ist damit **SETZE DIESELBE ART VON VERBINDUNG FORT**.
Eine vorsichtige quellklassenartige Ruecklesung lautet `MIT / VERBUNDEN MIT /
IN GLEICHER BEZIEHUNG`; an den Raendern lautet sie `WIE ZUVOR VERBINDEN` oder
`VERBINDUNG FORTSETZEN`. Das ist keine Identifikation eines gesprochenen
Wortes.

Der Gewinn gegenueber V6 ist klein, aber praktisch wichtig: Ein Lehrling muss
nicht in jedem medialen Fall einen frei gewaehlten aktiven Knoten suchen. Er
verbindet zunaechst schlicht die Nachbarn. Vererbung ist nur dann erlaubt, wenn
die Karte an einem Feldrand keinen sichtbaren Nachbarn besitzt.

## Quellen, Umfang und Versiegelung

Verwendet wurden nur:

- `VOYNICH_CURRENT_ROUTE.md`;
- `SIDEQUEST_SCRIBE_WORKSHOP_CURRENT.md`;
- das eingefrorene `V13_SELECTION_PROTOCOL.md`;
- ausschliesslich das R1-Profil aus
  `SIDEQUEST_FOUR_AGENT_BACKGROUNDS.md`;
- die f84-freie GDT327-Interlinearquelle fuer die zehn festgelegten Seiten.

Die Quelle wurde mit `./vmanus-exp query-tsv` und zehn einzeln angegebenen
`--allow`-Werten auf dem rohen Feld `page` abgefragt; `--forbid-prefix f84`
war aktiv. Der Guard meldete 381 ausgegebene und 8,067 verworfene Ereignisse.
Die drei Kreis-/Astronomieseiten besitzen keine GDT327-Ereignisse. `f84` und
`f84r` wurden weder geoeffnet noch abgefragt. Kein V13-Geschwisterbericht wurde
gelesen. Es wurden keine Teilstrings, Laute, Sprachen oder externen Bedeutungen
importiert.

## Notation

- `L` bezeichnet nur die exakte Karte `dcda95c81a5460feb191`.
- `Y`, `AIIN` und `CTHY` sind die bereits eingefrorenen anonymen Ganzkarten.
- Sechsstellige Zeichenfolgen sind eindeutige Praefixe anderer exakter
  GDT327-Karten, keine Wortlesungen.
- `w·X` gibt den beobachteten Renderer/Wrapper einer Karte an.
- `[C]` bedeutet: diese exakte Nutzlastkarte traegt die formale
  Abschlussrealisierung. Sie ist nicht bloss Interpunktion.
- `P` und `N` sind das vollstaendige unmittelbar vorherige bzw. folgende Feld
  desselben Absatzrecords. `START/END` markieren dessen Rand.

## Vollstaendige Rekonstruktion der 19 Vorkommen

Es gibt 19 Ereignisse in 16 Feldern: f10r 3, f81v 9, f83r 7. Die Spalte
`Stellen` zaehlt jede L/O-Karte im Zielfeld einzeln. Damit sind auch die drei
Doppelfelder vollstaendig erfasst.

| IDs | Record und Zielfeld | vollstaendiges Zielfeld | Stellung / Operanden | Record-Nachbarschaft |
|---|---|---|---|---|
| 01 | f10r R1, f10r.5/F1 | `q·9ad66e q·e8a610 ch·L CTHY` | 3/4, explizit links+rechts | P `d·65f320 dedc38 ch·4d4559 ch·80ebbb df1098 ch·12efe8 62ff05 276a7c d·AIIN a69398`; N END |
| 02–03 | f10r R2, f10r.8/F1 | `q·10488b ch·7a4bb8 497cbd ch·L ch·dec401 ch·L d·AIIN d·4d4559` | 4/8 und 6/8, beide explizit | P `7249ed CTHY ch·7a4bb8 f3c23f q·af816c d·Y ch·Y t·AIIN sh·Y`; N `27d97a sh·7a4bb8 ch·7a4bb8 ch·Y 409de0 d·Y ch·834825` |
| 04–05 | f81v R1, f81v.2/F2 | `b5fcea 22fb87 308e8e s·4d4559 L 9da1b6 94df48 dd0eca L 1496a7 d·0f18de` | 5/12 und 9/12, beide explizit | P `q·7db18b[C]`; N f81v.7/F1 unten |
| 06 | f81v R1, f81v.7/F1 | `dec401 L sh·4eab18 d·AIIN q·93f69c d·AIIN ch·2cc8bb s·259b2b[C]` | 2/8, explizit | P f81v.2/F2 oben; N f81v.7/F2 unten |
| 07 | f81v R1, f81v.7/F2 | `q·L` | einzig, beide Operanden geerbt | P f81v.7/F1; N `s·54e32e[C]` |
| 08 | f81v R1, f81v.17/F2 | `che·6f7ff8 L sh·bc4f1f[C]` | 2/3, explizit; rechter Operand schliesst | P `s·54e32e[C]`; N `q·28ffbc[C]` |
| 09–10 | f81v R1, f81v.18/F2 | `che·Y L che·d904bf L sh·bc4f1f[C]` | 2/5 und 4/5, explizite Kette; letzter rechter Operand schliesst | P `q·87411f[C]`; N `q·7db18b[C]` |
| 11 | f81v R1, f81v.21/F3 | `che·6f7ff8 q·c20557 433713 q·L b6b654` | 4/5, explizit | P `2e7e89[C]`; N `a7af89 07913e[C]` |
| 12 | f81v R1, f81v.24/F2 | `q·308e8e 0275fb q·L che·bc4f1f[C]` | 3/4, explizit; rechter Operand schliesst | P `a7af89 07913e[C]`; N `s·dd0eca t·a06244 d·d225b7[C]` |
| 13 | f83r R1, f83r.20/F4 | `s·L che·9247e3 q·7db18b[C]` | 1/3, linker Operand geerbt | P `q·0275fb q·7db18b[C]`; N `q·276a7c s·AIIN` |
| 14 | f83r R2, f83r.26/F1 | `faf321 q·0275fb q·276a7c t·L sh·bc4f1f[C]` | 4/5, explizit; rechter Operand schliesst | P `che·6f7ff8 90bcf0`; N `q·eb2e4b[C]` |
| 15 | f83r R2, f83r.37/F1 | `s·L b958a5[C]` | 1/2, linker Operand geerbt; rechter schliesst | P `s·AIIN che·d904bf daf32e 1645e6 ch·6f7ff8`; N `de7321[C]` |
| 16 | f83r R3, f83r.48/F1 | `d·dd0eca che·L 8c97df ch·00d8eb AIIN` | 2/5, explizit | P `sh·abb23e`; N f83r.49/F1 unten |
| 17 | f83r R3, f83r.49/F1 | `s·L d·fcc1de che·6f7ff8` | 1/3, linker Operand geerbt | P f83r.48/F1; N END |
| 18 | f83r R4, f83r.52/F1 | `s·1bfd78 q·43eb9a 3e9c7f L` | 4/4, rechter Operand in Fortsetzung geerbt | P START; N f83r.54/F1 unten |
| 19 | f83r R4, f83r.54/F1 | `d·AIIN L d·53cd06 che·Y 97ddca` | 2/5, explizit | P f83r.52/F1; N END |

Die Positionssumme ist damit exakt:

```text
14 MIDDLE mit zwei sichtbaren Nachbarn
 3 FIRST  mit geerbtem linken Nachbarn
 1 ONLY   mit zwei geerbten Nachbarn
 1 LAST   mit geerbtem rechten Nachbarn
```

Zwoelf Vorkommen liegen in Feldern, die noch im selben Feld schliessen, sieben
in offenen Feldern. Die Verteilung widerspricht nicht einer Relation; sie
widerspricht nur der unnoetig engen Forderung, dass beide Operanden immer
ausgeschrieben sein muessen.

## Die ausfuehrbare Schreibregel fuer einen Lehrling

Der Lehrmeister braucht nur eine Musterkarte und vier Randfaelle zu lehren:

1. Halte im laufenden Absatz die zuletzt offene Verbindung und deren letzte
   Karte im Gedachtnis. Ein physischer Zeilenwechsel loescht diesen Zustand
   nicht; ein neuer Absatz setzt ihn normalerweise zurueck.
2. Steht L/O zwischen zwei Karten, verbinde genau den unmittelbaren linken und
   rechten Nachbarn. Erfinde keinen ferneren Bezug.
3. Folgt spaeter im selben Feld wieder L/O, beginne mit dem zuletzt erreichten
   rechten Nachbarn. So entsteht eine Kette mit derselben Verbindungsart.
4. Fehlt am Feldanfang der linke Nachbar, uebernimm ihn aus dem laufenden
   Record. Fehlt am Feldende der rechte, lass die Verbindung bis zur
   Fortsetzung offen.
5. Steht L/O allein, kopiere die bereits aktive Verbindung fuer diesen Slot:
   weder neue Verbindungsart noch neue Teilnehmer werden notiert.
6. Eine abschliessende Nutzlastkarte kann zugleich rechter Operand sein und
   das Feld committen. Man darf sie nicht zu blosser Interpunktion entleeren.
7. Rendere danach die exakte L/O-Karte positionsgerecht. `ch·L`, freies `L`,
   `q·L`, `s·L`, `t·L` und `che·L` sind hier Erscheinungen derselben Karte,
   nicht sechs verschiedene Woerter.

Diese Regel ist klein genug fuer Vorzeigen, Nachschreiben und Korrektur. Vor
allem ist die Vererbung kontrolliert: nur eine fehlende Randstelle darf aus dem
Recordzustand ergaenzt werden.

## Der Ein-Karten-Fall f81v.7

`f81v.7/F2 = q·L` steht nicht isoliert im Absatz. Direkt davor liegt das lange,
abgeschlossene f81v.7/F1 mit einer ausdruecklichen medialen L/O-Verbindung;
danach folgen kurze geschlossene Zellen. Die konkrete Werkstattlesung ist:

> Fuer diesen leeren Slot gilt dieselbe eben gesetzte Verbindung mit den
> bereits aktiven Teilnehmern; schreibe nur die Linkkarte und fahre fort.

Das ist ein **Ditto der Relation**, nicht notwendig ein Ditto ihres gesamten
Inhalts. Diese Deutung ist attraktiv, weil ein Lehrling genau so Schreibraum
spart. Sie bleibt spekulativ: Das Einzelfeld koennte auch ein autonomer
Ein-Karten-Wert sein.

## Wiederholte Ketten und die Abschlussfaelle

### `X–L/O–Y–L/O–CLOSE`

Der vollstaendige reale Fall ist f81v.18/F2:

```text
Y — L/O — d904bf — L/O — bc4f1f[C]
```

Die sparsamste Vorwaertsaktion lautet:

```text
LINK(Y,d904bf)
LINK(d904bf,bc4f1f)
COMMIT(bc4f1f)
```

Rueckgelesen: **Der markierte Eintrag steht mit dem lokalen Eintrag in der
gleichen fortgesetzten Beziehung; dieser steht ebenso mit dem abschliessend
festgehaltenen Wert in Beziehung.** Das ist eine Kette, nicht schon der Beweis
zweier gleichrangiger Operanden unter einem gemeinsamen Zentrum. Eine
sternfoermige Lesung `LINK(Y,d904bf); LINK(Y,bc4f1f)` bleibt ein echter Rivale,
braucht aber die zusaetzliche Regel, dass der erste Anker ueber die zweite
L/O-Karte hinweg aktiv bleibt.

### Die vier weiteren `L/O–CLOSE`-Konstruktionen

Neben dem eben behandelten Kettenende gibt es vier weitere unmittelbare
L/O-vor-Abschluss-Faelle:

```text
f81v.17/F2   6f7ff8 — L/O — bc4f1f[C]
f81v.24/F2   0275fb — L/O — bc4f1f[C]
f83r.26/F1   276a7c — L/O — bc4f1f[C]
f83r.37/F1             L/O — b958a5[C]   # links geerbt
```

In allen vier ist die Abschlusskarte zugleich die sichtbare rechte
Nutzlastkarte. Daher muss L/O nicht selbst `CLOSE`, `BEENDET` oder ein
Satzzeichen bedeuten. Drei Konstruktionen teilen `bc4f1f[C]`, die vierte hat
`b958a5[C]`; das passt zu einer stabilen Linkoperation vor verschiedenen
exakten Commit-Nutzlasten.

## Herbal und Biological mit derselben Regel

Auf f10r ist L/O immer medial und offen. Das passt zu reflowter, fortlaufender
Herbal-Prosa: Nachbarkarten werden verknuepft, ohne dass jedes Feld lokal
committet. Auf f81v/f83r erscheint dieselbe Karte auch an Feldraendern und vor
Commit-Karten. Das passt zu kurzen, geerbten Biological-Zellen.

Es ist keine zweite Bedeutung erforderlich:

```text
Herbal A:      laengere offene LINK-Ketten
Biological B:  kuerzere LINK-Ketten, Randvererbung und lokaler Commit
```

Die fluente Quellsprache koennte den Link je nach Register als *mit*, *zu*,
*von*, *bei*, *ebenso* oder ganz ohne gesprochenes Gegenstueck ausgedrueckt
haben. Diese Varianten werden nicht der Karte als Lexikonbedeutungen
zugewiesen.

## Ruecklesung aufeinanderfolgender wirklicher Zeilen

### f81v.17–18

```text
f81v.17  54e32e[C] |
          6f7ff8 — L/O — bc4f1f[C] |
          28ffbc[C] |
          1645e6 2cc8bb 0f18de 4da0f0

f81v.18  87411f[C] |
          Y — L/O — d904bf — L/O — bc4f1f[C] |
          7db18b[C] | 7db18b[C] |
          2cc8bb 276a7c
```

Quellklassenartige Ruecklesung:

> Setze und bestaetige den ersten lokalen Wert. Verknuepfe den naechsten
> Eintrag mit dem festgehaltenen Wert und bestaetige ihn; bestaetige den
> folgenden Einzelslot; notiere die offene Fortsetzung. Setze danach den neuen
> Einzelslot. Verknuepfe den markierten Eintrag mit dem naechsten und diesen in
> gleicher Weise mit dem festgehaltenen Abschlusswert. Bestaetige die beiden
> folgenden Einzelslots und notiere die Fortsetzung.

`Wert`, `Eintrag` und `Slot` sind Formklassen. Keine Substanz, Handlung,
Koerperstelle oder Menge wird eingesetzt.

### f83r.48–49 und f83r.52–54

```text
f83r.48  dd0eca — L/O — 8c97df — 00d8eb — AIIN
f83r.49            L/O — fcc1de — 6f7ff8

f83r.52  1bfd78 — 43eb9a — 3e9c7f — L/O
f83r.54  AIIN — L/O — 53cd06 — Y — 97ddca
```

Ruecklesung:

> Verknuepfe den ersten lokalen Eintrag mit dem naechsten und fuehre die
> offene Angabe bis zum Standard-/Referenzslot. Im Folgefeld uebernimm den
> linken Teilnehmer und setze die Verbindung zum neuen Eintrag fort. Im
> naechsten Record lasse die am Zeilenende gesetzte Verbindung offen; nimm in
> der Fortsetzung den Referenzslot als rechten Teilnehmer auf und verknuepfe
> ihn weiter mit dem folgenden lokalen Eintrag.

Gerade f83r.52→54 macht die Randregel nuetzlich: Das letzte L/O muss nicht als
ungrammatisches Satzendwort weginterpretiert werden. Es kann eine fuer die
Fortsetzung offen gelassene Werkstattanweisung sein. Ob `AIIN` tatsaechlich
der geerbte rechte Teilnehmer ist, bleibt eine konkrete, innerhalb der festen
Seiten pruefbare Vorhersage.

## Typische Lehrlingsfehler und Korrekturzeichen

1. **Zeilenreset:** Der Lehrling vergisst die offene rechte Stelle von
   f83r.52. Folge: f83r.54 beginnt ohne anschliessbaren Zustand.
2. **Freie Fernverknuepfung:** Er waehlt trotz zweier sichtbarer Nachbarn einen
   entfernteren Anker. Korrektur: medial immer zuerst die Nachbarn verbinden.
3. **Stern statt Kette:** In `A–L–B–L–C` bindet er beide Male an A. Das darf nur
   ein anderes Exemplar erzwingen; die Grundregel geht schrittweise A→B→C.
4. **Einzelkarte als leer:** Er ueberspringt f81v.7/F2. Korrektur: die blanken
   Operanden bedeuten Vererbung, nicht Wirkungslosigkeit.
5. **Commit als Satzzeichen:** Er liest `bc4f1f[C]` nur als Punkt und verliert
   den rechten Nutzlastwert.
6. **Falscher Wrapper:** Er kopiert die mediale Erscheinung der L/O-Karte an
   den Feldanfang, statt den positionsgerechten Renderer zu verwenden.
7. **Unnoetige Verdopplung:** Er schreibt beim geerbten Link beide Teilnehmer
   erneut aus und zerstoert dadurch den kurzen Slot-Stencil.

## Fuehrende Hypothese, staerkster Rivale und Konfidenz

### Fuehrend

```text
L/O = CONTINUE SAME LINK
source-class: WITH / LINKED TO / IN THE SAME RELATION / AS ABOVE
```

- Konfidenz fuer die fortsetzbare Linkfunktion: **0.72**.
- Konfidenz fuer eine tatsaechlich semantische Assoziation im Quelltext:
  **0.52**.
- Konfidenz fuer irgendeine einzelne englische Praeposition: **0.18**.

Die 0.72 gilt nicht als Beweiswahrscheinlichkeit. Sie rangiert diese Theorie
innerhalb des bewusst explorativen Zehn-Seiten-Modells.

### Staerkster Rivale

Der staerkste Rivale ist eine **rein formale Relations-/Fortsetzungskarte ohne
gesprochenes Gegenstueck**. Sie sagt dem Schreiber nur, dass zwei Formularslots
demselben Kantenfach angehoeren. Konfidenz: **0.34** als alternative
Quellarchitektur. Sie deckt alle Positionen mindestens ebenso gut ab, liefert
aber weniger nuetzliche Ruecklesung und erklaert die unmittelbaren
Nachbarschaftsketten nicht einfacher.

Ein gewoehnliches polyfunktionales `UND/MIT/VON` bleibt bei **0.22**. Es ist in
den 14 medialen Faellen fluessig, muss aber fuer drei Anfangs-, einen End- und
den Ein-Karten-Fall dieselbe Randvererbung nachtraeglich einfuehren. Die Werte
sind nicht als disjunkte statistische Posterioren zu lesen.

## Schwierige Stellen

- f81v.7/F2 kann eine autonome Ein-Karten-Kategorie statt eines Relation-Dittos
  sein.
- f83r.52→54 macht AIIN zum naheliegenden Fortsetzungsziel, beweist aber nicht,
  dass physische Zeilengrenzen niemals resetten.
- Die Kettenlesung von f81v.18 ist sparsamer als die Sternlesung, doch die
  Kartenrollen der drei Teilnehmer sind nicht unabhaengig bekannt.
- Die drei gleichen `bc4f1f[C]` nach L/O koennten eine feste Formel bilden,
  statt frei eingesetzte rechte Operanden zu sein.
- f10r liefert nur mediale offene Faelle; die Randregel wird fast vollstaendig
  von Biological getragen.

Keine dieser Stellen macht die fuehrende Annahme unmoeglich. Sie begrenzen nur
ihre Genauigkeit.

## Neue Vorhersagen innerhalb der festen Seiten

1. **Nachbarschaft vor Fernbezug:** Jede mediale L/O-Karte soll zunaechst mit
   ihren unmittelbaren Karten lesbar sein. Eine Theorie, die systematisch einen
   ferneren Anker benoetigt, schlaegt diese Werkstattregel.
2. **Kettenfortsetzung:** Bei zwei L/O im selben Feld soll der rechte Nachbar
   des ersten Links die Ausgangskarte des zweiten sein. Unabhaengig erkennbare
   Rollen, die stattdessen einen konstanten ersten Anker zeigen, wuerden die
   Sternlesung bevorzugen.
3. **Feldanfang:** Die drei FIRST-Faelle sollen einen plausiblen linken Zustand
   aus dem vorherigen Feld desselben Records uebernehmen; sie duerfen keinen
   Absatzneustart ohne Besitzer verlangen.
4. **Feldende:** Der einzige LAST-Fall f83r.52 soll in f83r.54 einen passenden
   rechten Teilnehmer finden. AIIN ist der erste konkrete Kandidat.
5. **Einzelkarte:** f81v.7/F2 soll denselben Slot-/Linkzustand wie das direkt
   vorherige Feld weiterfuehren, nicht einen neuen Gegenstand einfuehren.
6. **Pre-close:** Die fuenf unmittelbaren L/O-vor-Abschluss-Ereignisse — das
   Ende der Doppelkette plus die vier separat gelisteten Konstruktionen —
   sollen die Abschlusskarte als rechten Nutzlastteilnehmer erlauben. Eine
   reine Punktlesung des Closers sollte schlechter werden.
7. **Rendererfehler:** Positionsfehler sollten eher den Wrapper als die exakte
   L/O-Kartenidentitaet betreffen; die semantische Funktion soll nicht mit
   `ch/q/s/t/che` wechseln.

## R1-Entscheidung

`ASSOCIATED WITH / SAME RELATION` bleibt stehen und wird nicht mangels Beweis
zurueckgezogen. Die bessere Lehrform ist:

> **Setze L/O zwischen die zwei Karten, die in derselben Verbindung stehen.
> Bei Wiederholung gehe kettenweise zum naechsten Nachbarn. Fehlt ein Nachbar
> am Feldrand, uebernimm ihn aus dem laufenden Record; steht L/O allein,
> wiederhole die aktive Verbindung.**

Das ist auf allen 19 Vorkommen ausfuehrbar, vereinheitlicht Herbal und
Biological und erzeugt konkrete Fehler- und Fortsetzungsvorhersagen. Es bleibt
eine absichtlich belastbare Arbeitshypothese, bis eine widersprechende
Operandenzuweisung oder eine einfachere vollstaendige Regel sie ersetzt.

# V52 R3 — Kleine ausführbare Feldgrammatik

Status: kreative Werkstattgrammatik über den 135 bereits festen Feldern. Sie
ist ein deterministischer Strukturparser, keine Übersetzung und kein
produktiver Manuskriptgenerator.

## Ergebnis

Eine einzige Feldhülle und fünf disjunkte Dispatchmuster decken alle 135
Felder und alle 381 Ereignisse:

```text
FIELD := NONCLOSE* TERMINAL?
TERMINAL := CLOSE(CORE) | CLOSE_B3(CORE)
```

Dabei muss `FIELD` mindestens ein Ereignis enthalten. In den festen Daten gibt
es 90 geschlossene und 45 offene Felder. Alle 90 top-level `CLOSE`-Wrapper
stehen genau einmal und ausschließlich am Feldende; ein interner oder zweiter
Abschluss kommt nicht vor.

Nach der Hüllenprüfung wird jedes Feld in dieser festen Priorität genau einem
Muster zugewiesen:

```text
P1 SET_CHAIN     enthält SET
P2 LINK_CHAIN    enthält kein SET, aber LINK
P3 MARK_CHAIN    enthält weder SET noch LINK, aber MARK
P4 SINGLETON     enthält keinen formalen Operator und genau ein Ereignis
P5 NONOP_CHAIN   enthält keinen formalen Operator und mindestens zwei Ereignisse
```

Die Priorität ist Teil der ausführbaren Regel. So fällt ein Feld mit `MARK`
und `SET` eindeutig unter P1, ein Feld mit `MARK` und `LINK`, aber ohne `SET`,
unter P2.

## Eingabedisziplin

Der Parser benutzt nur:

1. die bereits feste Feldgrenze und Ereignisreihenfolge;
2. den exakten Formelbaum jedes Ereignisses;
3. die drei ausgewählten formalen Namen `SETZEN`, `MARKIEREN`,
   `VERKNÜPFEN`;
4. die ausgewählten V50/V51-Atome als nachgeschlagene Annotationen exakter
   Hosts oder Ganzkarten.

Die lokale deutsche Prosa war beim Bau und bei der Musterwahl kein Feature.
Ihre Auswertung wurde separat erst nach dem Freeze als Widerspruchstest
zugeschaltet.

Für alle 135 Zeilen stimmen `event_count` und die unabhängig gesplitteten
Längen von Oberfläche, Formel, Atomfolge und lokaler Prosa überein. Ihre Summe
ist jeweils 381. Das Ereignisregister enthält ebenfalls genau diese 381
Ereignisse.

## Tokenebene ohne neue Segmentierung

Jedes Ereignis bleibt ein bereits vorhandener exakter Formelbaum:

```text
FORMAL ::= SET(<ARG_*>) | MARK(<ARG_*>) | LINK | LINK(<ARG_*>)
           sowie dieselben Kerne unter vorhandenen FRAME/CLOSE-Wrappern
ATOM   ::= exakter PAGE_HOST oder exakte wiederkehrende Ganzkarte
OPAQUE ::= jeder nicht ausgewählte exakte Wert
```

`FRAME`, `RIGHT`, `VARIANT_D` und `B3` werden rekursiv bewahrt, aber nicht neu
gedeutet. Insbesondere ist `<ARG_AIIN>` eine RIGHT-Familie und nicht die exakte
Ganzkarte `AIIN=MASS?`; ebenso ist `<ARG_AL>` nicht `AL=AN?`.

Die aktiven schwachen Annotationen sind:

```text
V50: AL=AN?  OR=BEREITUNG?  CHEY=TEIL?  E=UNKNOWN
V51: AIIN=MASS?  EY=KLAR?  OKY=VERWENDEN?  LCHE=ABLASSEN?
     OKE=SPÜLEN?  CTHY=BEREIT?  OKEEY=WARM?  CKHY=UNKNOWN
     OLOR=ZUVOR?
```

Diese Wörter bestimmen kein Muster. Sie beschriften erst nach der formalen
Klassifikation einen bereits identifizierten exakten Token.

## Die fünf Muster

| ID | Muster | Felder | Ereignisse | geschlossen / offen | Länge | benannte Ereignisse | H / B / C |
|---|---|---:|---:|---:|---:|---:|---:|
| P1 | `SET_CHAIN` | 22 | 96 | 10 / 12 | 2–11 | 47 | 2 / 20 / 0 |
| P2 | `LINK_CHAIN` | 18 | 68 | 9 / 9 | 1–8 | 35 | 3 / 15 / 0 |
| P3 | `MARK_CHAIN` | 4 | 15 | 3 / 1 | 2–6 | 5 | 0 / 4 / 0 |
| P4 | `SINGLETON` | 49 | 49 | 42 / 7 | 1 | 10 | 1 / 48 / 0 |
| P5 | `NONOP_CHAIN` | 42 | 153 | 26 / 16 | 2–10 | 48 | 14 / 28 / 0 |
|  | **gesamt** | **135** | **381** | **90 / 45** | **1–11** | **145** | **20 / 115 / 0** |

`H/B/C` bezeichnet Herbal/Biological/Circle. Die 135-Feld-Tabelle enthält nur
die vier Herbal- und drei Biological-Seiten. Für die drei Kreis-Seiten gibt es
hier keine Feldzeile; diese Grammatik beansprucht dort keine Coverage.

P1 umfasst 16 reine SET-Felder, 4 SET+LINK-Felder und 2 SET+MARK-Felder. P2
umfasst 17 reine LINK-Felder und ein MARK+LINK-Feld. P3 enthält die vier
übrigen MARK-Felder. Damit sind alle 44 operatortragenden Felder disjunkt
erfasst.

## Coverage und harte Grenze

- Strukturcoverage: 135/135 Felder und 381/381 Ereignisse, jeweils 100 %.
- Abschlussregel: 89 gewöhnliche `CLOSE` und ein `CLOSE_B3`; 0 interne und 0
  doppelte Abschlüsse.
- Formale Operatoren: 57/381 Ereignisse (15,0 %): 24 SET, 7 MARK, 26 LINK.
- Ausgewählte schwache Atome/Ganzkarten: 88/381 Ereignisse (23,1 %).
- Zusammen benannt: 145/381 Ereignisse (38,1 %).
- Mindestens ein benannter Token: 83/135 Felder (61,5 %).
- Vollständig benannt: nur 17/135 Felder (12,6 %).
- Ohne jeden benannten Token: 52/135 Felder (38,5 %).
- Opak bleiben 236/381 Ereignisse und 118/135 nicht vollständig benannte
  Felder.
- 41 FRAME-Ereignisse in 33 Feldern und 66 RIGHT-Ereignisse in 43 Feldern
  werden nur strukturell durchgereicht.

Die 100-%-Zahl gilt daher ausschließlich für Parsebarkeit, nicht für
Bedeutungscoverage.

## Ausführbarer Parser

```text
parse_field(events):
    require len(events) >= 1
    require every event is an already fixed exact formula tree

    close_positions = positions whose top-level node is CLOSE or CLOSE_B3
    reject if len(close_positions) > 1
    reject if close_positions exists and its position is not len(events)

    if any tree contains SET:                  return P1_SET_CHAIN
    if no tree contains SET and any contains LINK:
                                                return P2_LINK_CHAIN
    if no tree contains SET or LINK and any contains MARK:
                                                return P3_MARK_CHAIN
    if len(events) == 1:                       return P4_SINGLETON
    return P5_NONOP_CHAIN
```

Danach annotiert ein separater Lookup die exakten bekannten IDs. Ein
unbekannter Token bleibt `UNKNOWN[id]`. Der inverse Kodierer darf nur eine der
135 belegten vollständigen Feldfolgen wiedergeben. Die Muster lizenzieren
keine neue Kartenfolge, keinen neuen Host×RIGHT×FRAME×CLOSE-Typ und keine neue
Oberflächenvariante.

## Fünf Beispielbuchungen

### P1 — SET_CHAIN

`f82r / record 1 / f82r.7 / field 2`:

```text
MARK(<ARG_AIIN>) | SET(<ARG_AR>) | CLOSE(UNKNOWN_HOST[E])
MARKIEREN[ARG_AIIN] | SETZEN[ARG_AR] | CLOSE(UNKNOWN[E])
```

`ARG_AIIN` wird nicht zu `MASS` umgeschrieben; die exakte Ganzkarte liegt hier
nicht vor.

### P2 — LINK_CHAIN

`f10r / record 2 / f10r.8 / field 1`:

```text
FRAME_OT(UNKNOWN_HOST[CHOR]) | UNKNOWN_HOST[OR] |
FRAME_OT(UNKNOWN_HOST[OL]) | FRAME_O(LINK) | UNKNOWN_HOST[OLOR] |
FRAME_O(LINK) | UNKNOWN_HOST[AIIN] | UNKNOWN_HOST[AR]

FRAME_OT(UNKNOWN[CHOR]) | BEREITUNG? | FRAME_OT(UNKNOWN[OL]) |
FRAME_O(VERKNÜPFEN) | ZUVOR? | FRAME_O(VERKNÜPFEN) | MASS? |
UNKNOWN[AR]
```

### P3 — MARK_CHAIN

`f83r / record 1 / f83r.3 / field 2`:

```text
MARK(<ARG_AL>) | CLOSE(UNKNOWN_HOST[KEE])
MARKIEREN[ARG_AL] | CLOSE(UNKNOWN[KEE])
```

Auch hier bleibt `ARG_AL` vom Host `AL=AN?` getrennt.

### P4 — SINGLETON

`f81v / record 1 / f81v.2 / field 1`:

```text
CLOSE(UNKNOWN_HOST[OKE])
CLOSE(CARD[OKE]{SPÜLEN?})
```

Die Klammer bewahrt die V51-Konfundierung: `SPÜLEN?` ist ein Ganzkartenmerker,
nicht der isolierte Wert unter CLOSE.

### P5 — NONOP_CHAIN

`f83r / record 1 / f83r.20 / field 5`:

```text
UNKNOWN_HOST[OKY] | UNKNOWN_HOST[AIIN]
VERWENDEN? | MASS?
```

Die zwei Merkwörter erzeugen keine zusätzliche Satzsyntax. Das Muster sagt nur
„mehrgliedrige Folge ohne formalen Operator“.

## Illegale und ungeklärte Fälle

### Im festen Material illegal

Kein Feld verletzt die drei harten Bedingungen: nichtleer, höchstens ein
top-level CLOSE, CLOSE nur final. Die Zahl beobachteter strukturell illegaler
Felder ist daher 0.

Für einen künftigen Decoder bleiben folgende Formen ausdrücklich unzulässig,
bis ein bereits festes Beispiel sie belegt:

- leeres Feld;
- internes oder mehrfaches top-level CLOSE;
- neu erfundene exakte Formel oder Kartenidentität;
- aus einem Muster generierte, aber nie beobachtete Ereignisfolge;
- Gleichsetzung eines RIGHT-Namens mit einer gleich geschriebenen Ganzkarte;
- Zerlegung einer sichtbaren Karte in vermeintliche Atome.

### Ungeklärt

- Warum 45 Felder offen und 90 geschlossen sind, ist semantisch unbekannt.
- Die Operatorposition innerhalb des BODY trägt hier keine eigenständige
  Bedeutung; die Muster sind Dispatchklassen, keine Prozesssyntax.
- P3/MARK ist nur Biological belegt.
- 236 opake Ereignisse verhindern eine vollständige atomare Komposition.
- FRAME, RIGHT, `VARIANT_D` und `B3` besitzen keine ausgewählte Bedeutung.
- Die drei Kreis-Seiten sind in der 135-Feld-Quelle nicht vertreten.

## Nachträglicher Prosa-Widerspruchstest

Erst nach dem Freeze der Grammatik wurde die lokale Prosa geprüft. Bei 86/90
geschlossenen Feldern enthält das letzte lokale Segment ausdrücklich
„beende“. Bei 0/45 offenen Feldern und bei keinem inneren Segment steht dieses
Abschlusswort. Vier geschlossene Felder lassen den Abschluss in der Prosa aus:

```text
f11r  record 1  f11r.1  field 1
f55v  record 1  f55v.5  field 1
f55v  record 1  f55v.5  field 2
f56r  record 1  f56r.8  field 1
```

Das ist keine unabhängige Bestätigung, weil die kreative Prosa bereits aus
derselben formalen Arbeitstheorie stammt. Es ist lediglich ein interner
Editionswiderspruch. Die minimale Reparatur ergänzt bei diesen vier ganzen
lokalen Segmenten die neutrale Abschlussklausel; sie ändert kein Atom.

## Minimale Reparaturen

Es sind keine strukturellen Feld- oder Formeländerungen nötig.

1. Zehn bereits ausgewählte V50/V51-Remaps werden nur in der Atomannotation
   nachgeführt. Das betrifft 71 Ereignisse in 55 verschiedenen Feldern. Exakte
   Formel, Oberfläche und lokale kreative Expansion bleiben unverändert.
2. Vier lokale Schlusssegmente erhalten den fehlenden neutralen Abschluss.
   Diese Prosaänderung wird ausdrücklich nicht in den Kartenwert eingezogen.
3. Alle 236 unbenannten Ereignisse bleiben opak; „Reparatur durch Raten“ ist
   verboten.

Die Einzelzeilen stehen in `V52_R3_REPAIRS.tsv`. Damit ist die Feldgrammatik
klein, deterministisch und vollständig parsefähig, ohne vollständige
Übersetzbarkeit vorzutäuschen.

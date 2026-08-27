# GDT579 — nur echte Nachbarn teilen sich eine Scopephrase

## Ergebnis

`PASS_17_SCOPE_PAIRS__7_ADJACENT_FACTORIZED__10_INTERRUPTED_SLOT_EXPLICIT__34_SCOPE_SLOTS__15_INTERVENING_ATOMS__27_ORDERED_MODIFIER_FRAGMENTS__5122_EXACT_ROUNDTRIPS`.

Alle siebzehn Außen/Innen-Paare besitzen jetzt eine konkrete Stimme. Der
entscheidende Fortschritt ist aber, dass nicht alle siebzehn blind gleich
behandelt werden:

| schriftliche Form | Paare | Stimme |
|---|---:|---|
| gleiche Wurzel direkt benachbart | 7 | gemeinsame Basis, beide Scopeplätze |
| durch andere Atome unterbrochen | 10 | zwei vollständige, lokal gebundene Scopephrasen |

Die kurze Nachbarform lautet beispielsweise:

```text
P+AR+AR
Setze ein; von der Ausgangsposition im äußeren und im inneren Zweig.
```

AR@1 bleibt OUTER und AR@2 INNER. Nur die zweite deutsche Vollnennung von
`von der Ausgangsposition` entfällt; beide Atompositionen und beide Scopewörter
haben eigene Spans und eine vollständige Expansion.

## Warum nicht alle siebzehn zusammenziehen?

Die zehn übrigen Paare enthalten zwischen außen und innen zusammen fünfzehn
geschriebene Atome: zehn Handlungen und fünf Modifier oder Sigla. Eine globale
Koordination würde genau die Struktur verstecken, die wir gerade lesen wollen.

```text
P+O+LOCAL_CHAR_F+O+CH+E+Y

Setze den Pflanzenposten ein und nimm ihn;
beim Einsetzen: zur Ausführung im äußeren Zweig;
bei der f-Kennmarke;
beim Nehmen: zur Ausführung im inneren Zweig;
auf Grad I.
```

Die frühere Stimme hatte die f-Kennmarke ans Ende des Modifierblocks gestellt.
Die neue Zeile erhält erstmals die sichtbare Folge O außen → f → O innen → E
und unterscheidet zugleich die beiden Handlungsköpfe.

Dasselbe gilt für die anspruchsvollsten Karten:

```text
CH+E+P+A_ADDR+K+E+O
...; beim Nehmen: auf Grad I im äußeren Zweig;
an der A-Stelle;
beim Zugeben: auf Grad I im inneren Zweig;
zur Ausführung.

D_ADDR+AR+D_ADDR
...; beim fortgeführten Kennzeichnen: an der D-Stelle im äußeren Zweig;
von der Ausgangszeile;
beim fortgeführten Kennzeichnen: an der D-Stelle im inneren Zweig.

T+O+SH+E+O
...; beim Festlegen: zur Ausführung im äußeren Zweig;
auf Grad I;
beim Festhalten: zur Ausführung im inneren Zweig.
```

## Kleine Kopfgrammatik statt Sondertexte

Die 34 Scope-Slots benötigen keine siebzehn frei erfundenen Lesungen. Zwanzig
Bindungen kommen unverändert aus GDT407, acht aus GDT515. Vier O-Slots verwenden
GDT577s nächste sichtbare Handlung; zwei D_ADDR-Slots verwenden einen einzigen
expliziten aktiven R/Kennzeichnen-Kontext. Die Platzierungen sind 25 POST_HEAD,
drei PRE_HEAD und sechs CONTEXT_HEAD.

Die zehn unterbrochenen Paare reduzieren sich auf zwei Klammern um denselben
Kopf, sieben verschiedene Handlungsvorkommen und einen aktiven Kontextkopf.
Die sieben Nachbarpaare teilen sich in fünf gleiche Köpfe auf derselben Seite
und zwei Kontextfälle. `G407-E4142` behält dabei korrekt seinen festen
VISIBLE_OWNER-Kopf; ihm wird keine unsichtbare Handlung erfunden.

PRE/POST bleibt wie in GDT578 ein Strukturkanal. Die Prosa sagt niemals „vor
oder nach der Handlung“ und erzeugt daher keine zusätzliche Prozesszeit. Auch
`zweimal`, `erneut`, `wieder` oder ähnliche Wiederholungspartikeln werden für
Scopepaare nicht verwendet: außen und innen sind zwei geordnete Scopewerte,
kein Zählwert.

## Vollständige Ausgabe

Gegenüber GDT578 ändern sich genau siebzehn Nichtzustandsereignisse, siebzehn
Aussagen und zehn Seiten; 5.105 Ereignisse bleiben bytegleich. Drei dieser
Aussagen enthalten vier andere Ereignisse, die GDT578 bereits verbessert hat.
Weil Aussagen ausschließlich aus ihren festen Ereignisschlüsseln neu gebaut
werden, bleiben auch diese vier Stimmen exakt erhalten.

Alle 5.122 Ereignisse und 793 Aussagen rekonstruieren die GDT578-Quelle
bytegenau. Gegenüber GDT574 umfasst die kumulierte Arbeitsstimme nun 763
Ereignisse, 309 Aussagen und weiterhin 28 Seiten.

## Bedeutung für die Arbeitstheorie

Der Scope verhält sich nicht wie ein frei verschiebbares deutsches Suffix.
Direkte Zwillinge können eine Basis teilen; unterbrochene Zwillinge tragen
lokale Köpfe und bewahren den Inhalt dazwischen. Das ist eine brauchbare
Kompositionsregel für die Arbeitsübersetzung, ohne `äußerer/innerer Zweig` zu
einem behaupteten Voynich-Wort oder einer Konjunktion zu erklären.

Als nächster enger Rest bleiben die drei wirklich roh benachbarten
Relations-/Modifierwiederholungen aus GDT575. Sie können auf eine kleine
Zweischlitz-Zählstimme geprüft werden, ohne die jetzt geschlossenen 17
Scopepaare wieder anzufassen.

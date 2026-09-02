# GDT750 — Ein enger Ganzformfilter macht lokale Zustände konkret

## Ergebnis

Unmittelbare Nachbarschaft allein ist unbrauchbar.  Auf 1.134 reader-exakten
Vorkommen bekannter Ganzwörter erzeugt der rohe Radius-1-Transfer 203 richtige,
aber 371 falsche Qualitäts-/Stufenachsen.  Auch das bloße Entfernen von
Abschlusskarten ändert daran fast nichts: 186 richtige gegen 331 falsche.

Der zusätzliche Ganzformfilter verändert das Bild.  Eine Achse darf nur
sprechen, wenn mindestens zwei bekannte edit-distance-one Ganzwörter sie für
die vollständige Zielform unabhängig bevorzugen und der unmittelbar
angrenzende bekannte Host dieselbe Achse trägt.  In der bekannten
Vorkommenskalibrierung trifft diese Regel nur fünfzehn Positionen, dort aber 19
Achsen ohne eine falsche Achse: Precision 1,000, Recall 0,0097.  Die Regel ist
damit sehr schmal, aber sie produziert erstmals konkrete lokale Zustände statt
universeller Arbeitsprosa.

| Variante | Positionen | TP | FP | Precision | Recall | Verwendung |
|---|---:|---:|---:|---:|---:|---|
| roher direkter Host | 342 | 203 | 371 | 0,354 | 0,104 | verworfen |
| direkter Host ohne `CLOSE` | 310 | 186 | 331 | 0,360 | 0,095 | verworfen |
| Distanz 1, Mehrfachform, Radius 1 | 15 | 19 | 0 | 1,000 | 0,0097 | aktiv |
| Distanz 1, Mehrfachform, Radius 2 | 24 | 28 | 0 | 1,000 | 0,0144 | nur Suche |
| Distanz 2, Mehrfachform, Radius 1 | 64 | 67 | 21 | 0,761 | 0,0343 | Sensitivität |
| Distanz 2, Mehrfachform, Radius 2 | 97 | 101 | 30 | 0,771 | 0,0518 | Sensitivität |

Radius zwei bleibt trotz sauberer Kalibrierung still, weil Nähe ohne
nachgewiesene Bindung kein Hostrecht erzeugt.  Bei den siebzehn Zielwörtern
liefert er ohnehin keine zusätzliche Außenkarte.  Edit-Distanz zwei kauft etwas
Abdeckung mit klaren Widersprüchen und bleibt ebenfalls stumm.

## Die neunzehn konkreten Außenstellen

Von 1.684 Zielvorkommen sind 1.311 reader-exakte Stellen außerhalb der 57
GDT748-Entdeckungspositionen.  Der aktive Filter lizenziert davon neunzehn
Stellen, fünf Ganzformen und insgesamt 32 Achsen:

| Form | aktive Stellen/Seiten | lokale Achsen | praktische Lesart |
|---|---:|---|---|
| `okeey` | 14/10 | HOT 13; END 13 | 12× heißer Endzustand, 1× heiß, 1× Endstufe |
| `cheol` | 2/2 | DRY 2 | zweimal trockener Zustand |
| `cheey` | 1/1 | END 1 | einmal End-/Vollstufe |
| `cheky` | 1/1 | DRY 1 | einmal trockener Zustand |
| `sheey` | 1/1 | MOIST 1; END 1 | einmal feuchter/eingeweichter Endzustand |

Der stärkste neue Arbeitsbefund ist `okeey`.  Seine vollständige Form erhält
aus den bekannten edit-distance-one Nachbarn `okeedy` und `ykeey` unabhängig
die Karte HOT+END.  An zwölf Außenstellen steht unmittelbar `qokeey` oder
`ykeey` mit derselben Doppelachse; an einer weiteren Stelle trägt `okey` HOT,
an einer `oteey` nur die vereinbare END-Achse.  Deshalb darf der Renderer an
diesen konkreten Stellen sagen:

```text
f103v.4  y cheey qokeey [okeey] lkees ol qoteedy ykeedy
          … qokeey — heißer Zustand an der End-/Vollstufe — …

f17v.20  ykeey [okeey] cheor chol sho odaiin
          ykeey — heißer Zustand an der End-/Vollstufe — …
```

Das ist noch nicht `okeey = heiß` und auch nicht `okeey = Ende`.  Es ist die
engere Aussage, dass diese vierzehn Vorkommen einen heißen/endstufigen
Zustandsslot besetzen.  Gerade diese Trennung verhindert, dass eine lokale
Rolle wieder zu einem erfundenen Wörterbucheintrag wird.

`cheol` ist der zweitbeste kleine Befund: zwei Außenstellen auf zwei Seiten
werden jeweils durch das unmittelbar benachbarte `cheos` als DRY gebunden.
`cheky` erhält an einer Stelle DRY und widerspricht damit der alten globalen
MIDDLE_STAGE-Voreinstellung; seine allgemeine Stufe bleibt offen.  Die
Einzelkarten `cheey` und `sheey` sind verwendbar, aber noch keine
formweiten Defaults.

## Was ausdrücklich still bleibt

Zwölf Formen erhalten keine aktive Außenkarte.  Besonders wichtig sind
`qochey` und `okechy`: Beide besitzen zwar Formprioren oder konkurrierende
Arbeitstheorien, aber keine passende unmittelbare Hostbindung.  GDT750 erfindet
deshalb für keine ihrer Stellen eine neue Lesart.  `chdy`, `kchdy`, `lkeey`,
`okal`, `okedy`, `olkaiin`, `olkar`, `oty`, `qokaiin` und `qokedy` bleiben
ebenfalls bei ihren stillen, rivalisierbaren Vorannahmen.

## Bedeutung für den Renderer

GDT750 repariert einen konkreten Defekt der bisherigen Übersetzung: Eine
Ganzformrolle wird nicht mehr überall gesprochen, nur weil dieselbe Form in
einer guten Serie vorkam.  Zugleich zeigt das Experiment einen skalierbaren
Weg zur Konkretheit:

1. vollständige Formfamilien liefern eine unabhängige Zustandsprior;
2. ein reales benachbartes Ganzwort entscheidet, ob diese Achse an der
   einzelnen Stelle aktiv ist;
3. nur der gebundene Slot wird gerendert, alle übrigen Vorkommen bleiben offen.

Ein nachgeschalteter, reproduzierbarer Routencheck verhindert hier einen
naheliegenden Fehlstart. Unter 5.007 reader-exakten offenen Stellen gibt es
3.447 Oberflächen; 738 Formen wiederholen sich. Nur 28 davon besitzen einen
Mehrfachprior in Distanz eins. Der aktive Filter findet genau eine Stelle:
`qochey` auf f104v.23, also die bereits ausgeschlossene GDT748-
Entdeckungsposition. Außerhalb des alten Decks entstehen **null** neue Karten.
Die pauschale Ausweitung auf alle offenen Formen wird deshalb nicht gestartet.

Auch das einfache Hinzunehmen von Träger-, Mengen- und Prozessachsen scheitert:
Auf 1.158 bekannten Vorkommen liefert es 19 richtige und 14 falsche Achsen;
alle vierzehn Fehler sind `MATERIAL`-Übertragungen auf `chol`. Trägerrollen
folgen also nicht derselben Kopierregel wie Qualitäts-/Stufenrollen.

Der produktive neue Kandidat ist enger und kompositionell interessanter. Im
sauberen Bestand existieren 51 vollständige `qX`/`X`-Paare mit 2.060 versus
1.701 reader-exakten Vorkommen. Die geerbten Karten bewahren in 47/51 Paaren
exakt dieselben Qualitäts-/Stufenachsen; in 41/51 trägt nur die unpräfigierte
Form `PREPARATION`, niemals nur die q-Form. Das könnte zirkulär aus älteren
Rendererannahmen stammen und ist daher noch keine Evidenz für ein q-Morphem.
Die rohe Platzierung ist jedoch unabhängig in dieselbe Richtung verschoben:
Die q-Seite liegt in 33/51 Paaren früher, endet seltener die Zeile
(109/2.060 gegen 156/1.701), und zwölf verschiedene Paare stehen 44-mal direkt
nebeneinander auf 27 Seiten. Die nächste Route prüft deshalb genau diese 51
**vollständigen Formpaare** gegen rohe Position und Nachbarschaft. Erst wenn
das trägt, darf daraus eine vorhersagende Träger-/Feldschale werden.

Der GDT388-Einlass enthält neunzehn reale gleichzeilige Hostrelationen und
bleibt erwartungsgemäß ausschließlich wegen unversiegelten formalen Zugriffs
invalid und nicht score-ready.  Es werden null Lexeme, null Komponentenwerte,
null neue Seiten und keine Literalidentitäten exportiert.

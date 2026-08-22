# V40 — Rückübertragung des gemeinsamen Kerns

## Umfang

Die zwölf V39-Karten wurden nicht an neuen Seiten getestet, sondern in alle
ihre tatsächlichen Stellen auf den festen Prosaseiten zurückgetragen:

- 381 vollständige Kartenereignisse;
- 106 V39-Kernereignisse;
- 47 betroffene physische Textzeilen;
- 18 besonders dichte oder wiederholte Druckkontexte;
- 0 leere Bedeutungen.

Alle Nichtkernkarten behalten ihre konkreten V25-Defaults. Damit wird nicht nur
eine attraktive Lehrzeile, sondern die gesamte bisherige zehnseitige
Prosaübersetzung belastet.

## Wichtigste Korrektur: Karten als Prompts

Die Bedeutungsfelder überleben, doch mehrere Karten lesen sich schlecht als
gewöhnliche Substantive oder Verben in fortlaufender Prosa:

- f10r.6 enthält drei Realisierungen derselben `dy`-Karte;
- f10r.9 enthält zwei unmittelbar benachbarte `chor` und zwei `dy`;
- f10r.8 enthält `chol … cholor … chol`;
- f81v.18 enthält zweimal `chol`;
- f81v.7 enthält zweimal `daiin` und mehrere Vorbezugsformen.

Als normales Deutsch wäre „diese Portion, diese Portion, diese Portion“ oder
„Arbeitsflüssigkeit, Arbeitsflüssigkeit“ verdächtig. Als knappes
Werkstattformular ist es natürlich:

```text
DIESER POSTEN: ...
DIESER POSTEN: ...
VORGESCHRIEBENES MASS: ...
DIESER POSTEN: ...
```

oder:

```text
ARBEITSFLÜSSIGKEIT A: ...
ARBEITSFLÜSSIGKEIT B: ...
DIESER POSTEN: bis bitter
DIESER POSTEN: unter Öl bewahren
```

Die führende Lesung wird deshalb **nicht bedeutungsärmer**, sondern ihre
Satzebene ändert sich: Die gemeinsamen Karten sind wiederholbare
Rubrik-/Relationsprompts, deren ausgeschriebene deutsche Form je nach lokalem
Inhalt leicht variiert.

## Sechs belastende Stellen

### f10r.2

Kartenkern: `char chty ... oky daiin`

> Aus demselben Ansatz: bearbeite die gewaschene faserige Wurzel gleichmäßig,
> gib Rotwein zu und verwende den aktiven Anteil im vorgeschriebenen Maß; halte
> den Rest trocken.

Die alte „Charge“ war unnötig modern. Ein knapper Ansatz-Rückbezug funktioniert.

### f10r.6

Kartenkern: `cthy chor ... dy dy daiin dy`

> Wenn die Zubereitung gebrauchsfertig ist: Arbeitsflüssigkeit. Gib den
> ausgepressten Saft zu und koche sanft. Dieser aktive Posten: der Saft; dieser
> aktive Posten: die Flüssigkeit im vorgeschriebenen Maß; dieser aktive Posten:
> der zurückbehaltene Anteil.

Die Dreierfolge unterstützt `dy` eher als deiktisches Prompt **DIESER POSTEN**
als als eigenständiges Wort PORTION.

### f10r.8

Kartenkern: `chor ... chol cholor chol daiin char`

> Vor der Blüte sammeln. Arbeitsflüssigkeit: eine Handvoll. Mit dem Voransatz:
> daraus einen Anteil entnehmen; erneut mit dem Voransatz im vorgeschriebenen
> Maß, aus demselben Ansatz.

Das ist redundant, aber als Quellenkontrolle in einer technischen Notiz
verständlich. Als elegante normale Prosa wäre es schlecht.

### f10r.9

Kartenkern: `chor chor dy ... dy`

> Wenn die Blüte geöffnet ist: Arbeitsflüssigkeit A; Arbeitsflüssigkeit B.
> Dieser Posten: bis ein bitterer Geschmack bleibt. Dieser Posten: unter Öl
> bewahren.

Die Nachbarschaft zweier gleicher Karten wird als parallele Slotwiederholung,
nicht als zwei identische ausgesprochene Substantive gelesen.

### f81v.18

Kartenkern: `dy chol ... chol ... oky`

> Einmal erhitzen. Dieser aktive Posten: mit dem Voransatz bei sanfter Wärme;
> mit dem Voransatz stehen lassen, einmal spülen, noch einmal spülen, durch die
> verbundenen Leitungen führen und dann verwenden.

Hier passt die Promptlesung sehr gut zu einer wiederholten Bade-/Leitungsfolge.

### f83r.14

Kartenkern: `dal ... cthy dal dy`

> Abkühlen, im temperierten Bad anwenden, stehen lassen und sanft kochen. Zum
> bezeichneten Ziel führen und in das untere Gefäß ablaufen lassen. Neuer
> Eintrag: wenn gebrauchsfertig, zum bezeichneten Ziel; dieser aktive Posten.

Zweimal `dal` bezeichnet plausibel zwei getrennte Ziele oder Stationen. Es ist
kein universelles Körperwort.

## Ergebnis für das Schreibsystem

Die beste kreative Gesamtform ist nun:

```text
seltene Inhaltskarte
  + wiederholbares Kern-Prompt
  + lokale Spezifikation
  + inhaltstragende Schlusskarte
```

Ein Schreiber liest also nicht jedes sichtbare Gruppe-zu-Gruppe-Ereignis als
ein normales gesprochenes Wort. Er expandiert eine Karte wie `dy` zu „dieser
Posten/diese Portion/dieser Arbeitsteil“, abhängig vom bereits aktiven
Registerslot. Trotzdem besitzt jede Karte einen festen Defaultwert.

## Entscheidung

`TWELVE_CARD_CORE_SURVIVES_AS_MEDICAL_WORKSHEET_PROMPTS`

Keine der zwölf Karten muss verworfen werden. Die nominale medizinische
Mini-Satz-Lesung wird jedoch zurückgenommen. Der Kern ist am besten als
technische Prompt- und Referenzsprache zu verstehen, die auf den festen Seiten
medizinisch ausgefüllt wird.

Das ist weiterhin eine kreative vollständige Arbeitstheorie, keine
Entzifferung. Die Rückübertragung nutzt keine neue Seite und keine neue
semantische Evidenz. f84 und f84r blieben versiegelt.


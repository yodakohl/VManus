# GDT448 — Echter Kontext hilft, aber er macht aus Rot nicht beliebig Grün

## Ergebnis

Von den 30.763 GDT447-Nachbarkanten stammen 25.576 aus den 1.268 Rezepten, die
im aktuellen 4.576-Ereignis-Strom wirklich vorkommen. Ihre 4.275 verschiedenen
eingehenden Kontexte ergeben 61.878 lokale Einsetzproben.

Der neutrale und der kontextuelle Leser vergleichen sich so:

| Entscheidung | neutral | im echten Kontext |
|---|---:|---:|
| grün | 53.476 | 54.622 |
| gelb | 1.743 | 1.345 |
| Stopp | 6.659 | 5.911 |

60.633 Fälle bleiben unverändert. Der echte Kontext ändert 1.245 Fälle:

- 757 neutrale Stopps werden lesbar;
- 443 gelbe Fälle werden grün;
- 36 grüne Fälle werden gelb;
- nur 9 zunächst lesbare Fälle stoppen.

Die Stoppzahl sinkt netto um 748 beziehungsweise 11,2 Prozent. Das ist keine
freie Kontextmagie, sondern eine sehr schmale Wirkung.

## Was genau wird gerettet?

Alle 757 Rettungen hatten neutral genau denselben Grund:

```text
CLOSE:NO_ACTIVE_ACTION
```

Im realen Strom steht bereits ein Handlungskopf zur Verfügung. 748 Fälle
werden dadurch grün und neun gelb. Keine rote direkte Handlungspaarung und
keine verbotene Fokusbindung wird durch bloßen Kontext wegdiskutiert.

Umgekehrt sind auch die neun neuen Stopps vollständig bekannt:

- achtmal bindet `EEE` im echten Scope an `CHD`;
- einmal bindet `EEE` an `R`.

Das sind genau die zwei schon vorhandenen Grad-III-Lücken `CHD←EEE` und
`R←EEE`. Der Kontext entdeckt sie an Stellen, an denen der neutrale Test keinen
linken oder rechten Kopf sah.

## Warum das wichtig ist

Ein künftiger sichtbarer Schluss darf nicht mehr pauschal im neutralen Zustand
geprüft werden. Er muss den aktuellen Handlungskopf bekommen. Gleichzeitig
darf eine ansonsten harmlose Gradkarte nicht ohne ihren realen
Aussageanschluss zertifiziert werden.

Die praktisch bessere Aufnahmefolge lautet damit:

```text
1. exakte Zielidentität prüfen;
2. realen Besitzer- und Aussagescope einsetzen;
3. sichtbare Faktoren ausführen;
4. bei fehlendem Kopf oder verbotener Grad-III-Kante sicher stoppen.
```

Identität bleibt dabei vollkommen stabil: 0 von 61.878 Kontexten ändern die
Identitätsroute, 0 tragen die Quellidentität mit und jeder Stopp bewahrt den
eingehenden Zustand.

## Grenze

Die Probe ersetzt jeweils nur eine Karte in einem realen Eingangskontext. Sie
behauptet nicht, dass diese Nachbarform tatsächlich existiert, wie sie
geschrieben würde oder dass der nachfolgende Manuskriptstrom nach einer
künstlichen Ersetzung unverändert bliebe. Der Gewinn ist enger, aber nützlich:
Unser Leser behandelt geerbte Köpfe jetzt realistisch, ohne rote Faktoren zu
verwässern.

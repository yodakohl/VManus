# GDT455 — Ein dichter Fehlerstrom bleibt lokal begrenzt

## Ergebnis

Der Baseline-Lauf reproduziert alle 4.576 Entscheidungen und alle 4.576
Handlungs-/Argumentzustände. Der sichtbare Störplan ersetzt anschließend 1.026
Karten, also 22,42 Prozent des ganzen Stroms, in 513 Zwei-Karten-Bursts.

| Karte 1 | Karte 2 | Bursts |
|---|---|---:|
| lesbar | lesbar | 246 |
| lesbar | Stopp | 126 |
| Stopp | lesbar | 86 |
| Stopp | Stopp | 55 |

Der vollständige Strom enthält danach 4.234 grüne, 20 gelbe und 322 gestoppte
Karten. Alle 322 Stopps liegen auf absichtlich ersetzten Karten. Die 3.550
unveränderten echten Karten lesen vollständig weiter: 3.541 grün und neun gelb,
null Stopp. Jeder Stopp bewahrt Handlung, Argument und Aussage-Scope.

## Zustandsrückkehr

Von den 513 Bursts:

- erreichen 383 vor dem nächsten Fehler wieder exakt den Baseline-Zustand;
- treffen 123 vorher auf den nächsten planmäßigen Burst derselben Bank;
- enden sieben mit ihrer Besitzerbank, worauf eine unabhängige Bank beginnt.

Die 383 direkten Rückkehrfälle benötigen höchstens sechs unveränderte Karten;
259 davon nur eine. Die sieben Endfälle wechseln sämtlich in eine andere
Besitzerbank. Ein abweichender Zustand kann daher weder heimlich über eine
Bankgrenze springen noch einen echten Folgekarten-Stopp erzeugen.

## Warum das mehr ist als GDT454

GDT454 behandelte jeden Burst als eigenen lokalen Angriff. GDT455 lässt 513
Angriffe gleichzeitig im selben 4.576er Strom stehen. Frühere lesbare
Ersatzkarten dürfen den Zustand wirklich verändern, spätere Stopps müssen genau
diesen veränderten Zustand bewahren, und die nächste Aussage erbt nur ihre
eigene Besitzerbank. Dass jeder der 57 isolierten Bankläufe Ereignis für
Ereignis mit dem globalen Lauf übereinstimmt, macht diese Trennung ausführbar
statt nur redaktionell.

Das Resultat bestätigt weiterhin kein Wort und keine Manuskriptform. Es zeigt,
dass der Intake auf einer später freigegebenen Seite mehrere sichtbare neue
Kompositionen verarbeiten oder sauber ablehnen kann, ohne dass eine Ablehnung
die folgenden bekannten Karten vergiftet.

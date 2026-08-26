# GDT452 — Ein Stopp beschädigt den folgenden Strom nicht

## Ergebnis

Die 5.911 roten GDT448-Proben entsprechen 6.008 wirklichen
Ziel×Ereignis-Situationen. Alle 6.008 stoppen erneut am erwarteten Faktor und
alle 6.008 bewahren Handlung und Argument.

765 liegen am Ende ihrer Aussage und haben deshalb keine unmittelbare
Folgekarte. Für die übrigen 5.243 sieht der Anschluss so aus:

| Anschluss nach dem Stopp | Fälle |
|---|---:|
| sofort grün | 5.231 |
| sofort gelb | 9 |
| abhängiger Schluss stoppt ebenfalls | 3 |

Damit lesen 5.240/5.243 tatsächliche Folgekarten unmittelbar weiter.

## Die drei scheinbaren Ausnahmen

Alle drei sind verschiedene Mutationen derselben f89r-Stelle:

```text
Quellkarte:       P+O+R+A_ADDR+CH+OL
rote Zielkarte:   ... P+R ...        -> STOP PAIR:P>R
wirkliche Folge:  Y+O+DY             -> STOP CLOSE:NO_ACTIVE_ACTION
nächste Aussage:  OT+E+OL            -> READ
```

Das ist keine beschädigte Synchronisation. Die verworfene Zielkarte durfte den
Kopf `CH` nicht setzen; daher darf der unmittelbar abhängige Schluss ihn auch
nicht erfinden. Am Anfang der nächsten Aussage lesen alle drei Varianten wieder
grün. Der zweite Stopp ist die korrekte Fehlerkaskade.

## Was wir jetzt wissen

Der Zustandsschutz ist nicht nur eine Angabe im Zertifikat. In 5.240 normalen
Anschlüssen funktioniert die wirkliche nächste Karte; in den einzigen drei
Abhängigkeiten verhindert derselbe Schutz eine falsche Schlusslesung und der
nächste Aussagerahmen synchronisiert wieder.

Die neun gelben Anschlüsse sind keine neuen Fehler: acht waren im Original
grün und werden unter dem erhaltenen Alternativzustand vorsichtiger, einer war
schon gelb. Es gibt keine Freigabe eines roten Faktors.

Das stärkt den praktischen Intake, nicht die Übersetzung: keine Bedeutung,
Oberfläche oder zukünftige Vorkommensbehauptung wird verändert.

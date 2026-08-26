# GDT450 — Der Kurzfilter ist sehr gut, aber achtmal gefährlich falsch

## Ergebnis

Aus 65.746 gewichteten Ziel×Ereignis-Proben entstehen 35.577
Ziel×gehaltene-Seite-Folds über 24 gespeicherte physische Seitenkennungen.

| Holdout-Ergebnis | Folds |
|---|---:|
| korrekt lesbar | 20.052 |
| korrekt Stopp | 2.400 |
| **falsch freigegeben** | **8** |
| fälschlich gestoppt | 2 |
| Training gemischt, daher Enthaltung | 53 |
| Ziel ohne andere Trainingsseite | 13.062 |

Unter den 22.462 entscheidenden, trainierbaren Folds liegen nur zehn Fehler.
Das ist als Prior oder Suchsortierung hervorragend. Als Ausführungsfreigabe
reicht es nicht: Acht Fehler gehen in die gefährliche Richtung.

## Die acht Falschfreigaben

```text
f83r  D_ADDR+EEE+Y   CHD<-EEE
f76r  E+DY           Schluss ohne Kopf
f76r  EE+DY          Schluss ohne Kopf
f82r  EEE+Y          CHD<-EEE
f83r  OT+EEE+AIIN    CHD<-EEE
f88v  OT+EEE+O       CHD<-EEE
f82r  OT+EEE+OR      CHD<-EEE
f72r  OT+O+DY        Schluss ohne Kopf
```

Alle acht liegen in einem operativen Kontext, der für dieses Ziel auf den
Trainingsseiten noch nicht vorkam. Fünf treffen `CHD<-EEE`, drei verlieren den
aktiven Schlusskopf. Es gibt also kein neues Rätsel: Der Holdout findet genau
die zwei Kontextinformationen wieder, die eine pauschale Zielklasse nicht
speichern kann.

## Die zwei harmlosen Gegenfehler

`OT+EEE+AIIN` auf f95v und `OT+EEE+O` auf f72r werden aus einem einzigen
Trainingsstopp zu vorsichtig als Stopp vorhergesagt, sind lokal aber lesbar.
Auch das zeigt: Ein Zielrezept besitzt keine feste Ausführungsfarbe unabhängig
vom Scope.

## Konsequenz für die nächste Seite

Das GDT449-Deck bleibt nützlich, aber seine Rolle ist jetzt fest:

```text
GDT449 sortiert und warnt.
GDT446/GDT448 zertifiziert den tatsächlich sichtbaren Kontext.
Bei Widerspruch gewinnt immer das Live-Zertifikat.
```

Die zehn GDT449-Warnziele sollten im Lehrblatt prominent stehen. Für alle
anderen Ziele darf „historisch überall lesbar“ die Prüfung beschleunigen, aber
niemals einen roten Scopefaktor überstimmen.

## Grenze

Dies ist ein Holdout innerhalb derselben 26-Seiten-Arbeitsbasis und kein Test
auf einer wirklich neuen Seite. Er ist trotzdem härter als die globale
GDT449-Zählung, weil jede Falschfreigabe aus dem Training entfernt war. Der
nächste sinnvolle Schritt ist deshalb ein integrierter Intake-Befehl, der den
Robustheitsprior sichtbar ausgibt, aber technisch unmöglich als Override
verwenden kann.

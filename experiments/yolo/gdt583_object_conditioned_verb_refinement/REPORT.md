# GDT583 — Vier breite Handlungen bekommen konkrete Kontextstimmen

Status: `PASS_1921_TARGET_SLOTS__1623_RUNNING_EVENTS__FOUR_ACTION_CLASSES__OBJECT_GRADE_RELATION_CHAIN_REFINEMENT__TWENTY_PASSAGES__ZERO_NEW_SLOTS`

## Ergebnis

Die Verbesserung ist umgesetzt. Alle 1.921 Vorkommen von `T`, `SH`, `CHD`
und `S` besitzen jetzt neben dem breiten GDT582-Kern genau eine
kontextabhängige Arbeitslesung. Die Regel greift nicht auf das ganze sichtbare
Wort als Bedeutungsblock zu, sondern auf den bereits von GDT581 festgelegten
Aktionskopf und dessen eigene Argumente.

| Klasse | Slots | tragender Kern | neue konkrete Stimmen |
|---|---:|---|---|
| `T` | 384 | einstellen / temperieren | festlegen, regulieren, erwärmen, abkühlen, trocknen |
| `SH` | 794 | halten / ruhen | Position festhalten, im Bad halten, Auszug ziehen lassen, einweichen |
| `CHD` | 341 | bearbeiten / behandeln | berechnen, behandeln, zerreiben |
| `S` | 402 | auswählen / trennen | umleiten, abseihen, sieben, abtrennen |

1.291 Slots ändern gegenüber GDT582 tatsächlich ihre deutsche Aktionsform.
630 behalten eine schon passende oder bewusst breite Form, erhalten aber
trotzdem eine explizite Regelkarte. Betroffen sind 1.623 laufende Ereignisse,
158 lokale Karten und 591 Aussagen.

## Beispielparagraph

`G407-S010`, Herbal:

> Erwärme den Ansatz und lass ihn im selben Arbeitsgang weiterziehen. Lass
> die Zubereitung am Ziel- oder Auffanggefäß stehen. Zieh die feine
> Pflanzencharge ab und lass Pflanzencharge und Auszug beziehungsweise
> Arbeitsmaß zusammen ziehen. Nimm die Charge heraus und bring sie wieder ein;
> lass sie auf Stufe I ziehen. Temperiere abschließend und zieh die Zubereitung
> ab, dann schließe den Arbeitsgang.

Diese Lesung ist flüssiger als die Slotliste, behauptet aber weiterhin nicht,
dass `t`, `sh` oder `ch` für sich die deutschen Wörter seien. Der vollständige
maschinenlesbare Satz und alle Slot-IDs bleiben im TSV daneben erhalten.

## Der wichtigste Fortschritt: Reihenfolge erzeugt Richtung

Vor GDT583 blieb `T` fast überall bei „einstellen oder temperieren“. Ein Grad
allein kann nicht sagen, ob etwas wärmer, kälter oder trockener werden soll.
Die Aktionsfolge kann es als Arbeitstheorie dagegen unterscheiden:

| feste Folge | Arbeitslesung | Slots | Reichweite |
|---|---|---:|---|
| Herbal/Pharma `T→SH` | erwärmen, danach ziehen/halten | 10 | 6 Seiten / 6 Owner |
| Physical `SH→T` | nach dem Halten/Badgang abkühlen | 12 | 7 Seiten / 7 Owner |
| Herbal/Pharma `T→CHD` | vor dem Aufarbeiten trocknen | 3 | nur f95v; mutig lokal |

So wird `G407-E4496` zu „Erwärme die Pflanzencharge; halte sie auf Grad I“,
`G407-E1758` zu „Halte im Bad auf Grad II; kühle den Stationsansatz ab“ und
`G407-E4476` zu „Trockne die Pflanzencharge; zerreibe sie“.

Die Gegenprobe ist wichtig: `G407-E3036 = Y+T+E` wird nur „temperiere auf Grad
I“, nicht „kühle“. `G407-E0297 = Y+T+O+IIN` wird „stelle Form oder Stufe ein“,
nicht „trockne“. Die Richtung stammt aus der Aktionsnachbarschaft, nicht aus
einer nachträglich erfundenen Gleichung `E=Hitze`.

## Objekt und Owner liefern die übrigen konkreten Verben

Die vollständigen GDT581-Hosts erlauben auch Argumente, die erst in einer
folgenden Karte ausgeschrieben werden. Dadurch entstehen folgende produktive
Mikrolesungen:

- `S` in Herbal/Pharma mit `AIIN`: 34-mal **abseihen**;
- `S` dort mit Portion/Einheit/Feinform: 16-mal **sieben**;
- Biological `S` mit Ziel-, Quellen-, Kontakt- oder Wegrelation: 44-mal
  **umleiten**;
- `SH` in Herbal/Pharma mit `AIIN`: 17-mal **Auszug ziehen lassen**;
- `SH` mit Material plus Grad/Form: 40-mal **einweichen**;
- Biological `SH` bei bebildertem Badowner plus Objekt/Grad/Form: 254-mal
  **im Bad halten beziehungsweise baden**;
- Herbal/Pharma `CHD` mit Feststoffsignal, aber ohne `AIIN`: 23-mal
  **zerreiben**.

Ein anschaulicher Remote-Fall ist `G407-E0360`: Die nackte `S`-Karte regiert
`AIIN` und `Y` in den folgenden Karten. Die ganze Hostphrase kann deshalb
„Seihe den Pflanzenauszug“ heißen, obwohl das einzelne Oberflächenstück nicht
als vollständiges Wort „seihen“ ausgegeben wird.

## Was bewusst breit bleibt

Die Durchsatzregeln erzwingen keine schlechte Präzision. 101 physische
`T`-Vorkommen bleiben „einstellen oder temperieren“, weil eine Charge allein
Wärme, Kälte und Trocknung nicht trennt. 272 `SH`-Vorkommen bleiben „halten“,
162 `S`-Vorkommen „auswählen“ und 39 `CHD`-Vorkommen „bearbeiten“.

Die zwölf aus GDT507 bekannten `CH→SH`-Argumentbrücken heißen vorrangig
„halten“: ein vom Entnehmen übernommenes Objekt beweist noch kein Bad oder
Einweichen. Ebenso bleibt der einzige beobachtete Biological-Träger
`S+OL+CHD+Y` bei „wähle aus; behandle“. Entfernte Einzelkopf-Rechtecke in
anderen Registern werden nicht zu einer erfundenen universellen Phrase
„seihen und zerreiben“.

## Lesbare Edition und Prüfung

Alle zwanzig bisherigen Prüfpassagen wurden manuell geglättet, vier pro
Register. Ihre Ereignisfolge bleibt erhalten; die exakte, rückverfolgbare
Fassung steht daneben. Der unabhängige Validator importiert weder Generator
noch Regelmodul. Er rekonstruiert alle direkten und vollständigen Hosts,
Aktionsnachbarn, 29 First-Match-Regeln, 1.921 Entscheidungen, betroffenen
Ereignisse/Karten/Aussagen und die zwanzig Passagen direkt aus GDT582. Alle
25 Prüfungen bestehen.

## Neue Arbeitsbasis

GDT583 ersetzt nicht das GDT582-Wörterbuch. Es ergänzt dessen vier breite
portable Kerne um eine occurrence-gebundene zweite Ebene:

```text
portable Klasse + Register/Owner + eigener Argumenthost + Aktionsrichtung
    → konkrete, austauschbare Arbeitslesung
```

Damit sind die konkreten Verben endlich in der vorhandenen Notation verortet,
ohne aus einer lokalen schönen Passage sofort ein universelles Stammlexikon zu
machen. Als nächstes sollten dieselben 29 Regeln gegen alle 591 betroffenen
Aussagen nach schlechten Kollokationen durchsucht und nur die tatsächlichen
Restgruppen geglättet werden; neue Seiten sind dafür noch nicht nötig.

## Claim ceiling

Dies ist die bisher beste vollständige Arbeitstheorie für diese vier Klassen
auf den dreißig zugelassenen Seiten. Sie bestätigt keine Sprache, kein
historisches Codebuch, keinen Klartext und kein Manuskriptwort. `erwärmen`,
`kühlen`, `trocknen`, `abseihen`, `einweichen` und `zerreiben` sind
kontextgebundene deutsche Defaultstimmen, keine portable Übersetzung eines
einzelnen Zeichens oder Stamms. Kein neuer Slot, Root, Surface, Parser oder
Seite wurde hinzugefügt.

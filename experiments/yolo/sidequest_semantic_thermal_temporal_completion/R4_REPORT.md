# R4 — Kanzleikorrektor: Wärme, Dauer und Reihenfolge

## Ergebnis

Die bisherige Nasswerkstatt-Lesung wird nicht um weitere Satzglossen erweitert.
Stattdessen erhält sie eine kleine, lehrbare Prozesssprache mit voneinander
getrennten Achsen:

- `OT = FOLGE`: Folgeansatz, Folgemaß, Folgeposten, Folgestelle;
- `OL = WEITER`: weiter, Ansatz weiterführen, weitere Portion, weiter ruhen;
- `OK+OK = NOCHMAL`: Wiederholung desselben Arbeitsschritts;
- `IIN = STUFE`, `E = KURZ`, `EE = LANG`, `EEE = GANZ`;
- `CHK = WÄRMEN`, `SHED = RUHEN`, `CTHY = FERTIG`;
- `Y` hält den aktuellen Posten offen; die gelernte Endkarte schließt ihn.

Damit werden **54 Kartentypen / 134 Ereignisse / 80 Aussagen** neu geordnet.
Die vollständige Ausgabe umfasst weiterhin 173 Karten, 381 Ereignisse,
116 Aussagen und elf Records.

## Warum diese Ordnung besser ist

Die frühere Ausgabe ließ dieselbe kleine Karte je nach Stelle etwa „mit dem
vorigen Ansatz“, „und“, „weiter“ oder eine ganze Fortsetzungsanweisung heißen.
R4 setzt nur `WEITER`. Der geerbte Besitzer und Ansatz liefern das Objekt.
Entsprechend bedeutet `OT` nicht abwechselnd „nimm“, „danach“, „nächster
Behälter“ und „wiederhole“, sondern nur `FOLGE`. Eine sichtbare Verdopplung von
`OK` übernimmt die Wiederholungsfunktion.

Eine konkrete Altlast fällt dabei weg: Die zweimalige Karte `OLDY` heißt in
beiden Fällen `WEITER; SCHLUSS`; sie darf auf f83r nicht plötzlich „sanft
erwärmen“ heißen, wenn ihre gleiche Karte auf f55v nur einen Gang beendet.

Das erzeugt eine einfache Lehrmeisterregel:

> Behalte den aktiven Posten. Setze mit `OL` denselben Gang fort, gehe mit `OT`
> zum Folgeposten und wiederhole mit verdoppeltem `OK`. Setze erst danach
> Stufe, Dauer, Wärme oder Schluss.

## Thermisches Netz

Die produktive Achse sagt nicht, *welcher Stoff* erwärmt wird. Das kommt aus
Bildbesitzer, Ansatz oder gelernter Ganzkarte. Sie liefert nur Prozess und
Grad:

| Ebene | Arbeitswert |
|---|---|
| `QEKY` | ROH |
| `QOTCHOL`, `OLTCHY` | ANWÄRMEN |
| `CHK+E` | KURZ WÄRMEN |
| `CHK+EE` | LANG WARMHALTEN |
| `ROL` | HEISS |
| `LOL` | WARM |
| `SHECTHY` | TEMPERIERT |
| `CTHY` | FERTIG |
| `TCHODY`, `CHARY`, `RAL` | KÜHLEN |
| `ODY` | KÜHL; SCHLUSS |

Die verschiedenen Ganzkarten für `ANWÄRMEN` und `KÜHLEN` werden bewusst nicht
in erfundene Buchstabenmorpheme zerlegt. Sie gehören zum gelernten
Nomenklatoranteil des Systems.

## Zeit und Endpunkte

Satzlange Altglossen werden zu kurzen Kartenwerten:

- `SHFYDAIIN = RUHEZEIT`, nicht „für die vorgeschriebene Zeit stehen lassen“;
- `CHLDAIIN = ABSETZMASS`, nicht „bis zum vorgeschriebenen Stand absetzen“;
- `CHCKHAL = DAUER`;
- `CHEALROR = KLAR`, nicht „bis der Strom klar wird“.

Die Verben, Objekte und Präpositionen entstehen erst beim Lesen des ganzen
Feldes. Ein Kartenwert bleibt dadurch klein genug, um von mehreren Schreibern
gelernt zu werden.

## Konkrete Rücklesungen

### f10r, H1-S002

`laufenden Posten einsetzen · ANWÄRMEN · WEITER · FERTIG`

> Den laufenden Posten einsetzen, anwärmen, den Gang weiterführen; fertig.

### f11r, H3-S001

`Blütenkraut · Weinsud · auswringen · RUHEZEIT · nachseihen · Klarauszug · KÜHLEN/SCHLUSS`

> Das bezeichnete Blütenkraut im Auszugsmedium bearbeiten, auswringen, für die
> Ruhezeit stehen lassen, nachseihen, den klaren Auszug kühlen; Schluss.

### f83r, B3-S026

`Beckenstation · ABSETZMASS · Posten umsetzen · Portion zugeben · FERTIG · KLAR · länger auffangen/SCHLUSS`

> An der bezeichneten Beckenstation bis zum Absetzmaß führen, den Posten
> umsetzen, eine Portion zugeben; wenn fertig und klar, länger auffangen;
> Schluss.

### f83r, B5-S003

`Ruheplatz · Stelle · WEITER · WARM · umsetzen · Maß · WEITER · zweite STUFE · Posten umsetzen`

> Am Ruheplatz den warmen Posten weiterführen, an der Stelle umsetzen, nach Maß
> weiterführen und in der zweiten Stufe erneut umsetzen.

## Historischer Mechanismus

Die vorgeschlagene Architektur ist näher an einer gemischten Werkstatt-
Kurzschrift als an einem gewöhnlichen Wörterbuch: wenige produktive
Ordnungs-/Gradzeichen plus gelernte Ganzkarten für Stoffe, Zustände und
Spezialhandlungen. Zeitnahe medizinische, alchemistische und Rezeptcodices
zeigen genau die relevante Mischung aus wiederkehrenden Operationsformeln,
Maßen, Dauerangaben, Zustandsendpunkten und lokal gelernten Kürzeln; sie belegen
nicht die einzelnen Voynich-Zuordnungen. Vergleichsmaterial sind u. a. das
[Manoscritto Bolognese](https://bub.unibo.it/it/allegati/manoscritto-bolognese-traduzione/%40%40download/file/manoscrittobolognese-traduzione.pdf),
[Wellcome MS.140](https://wellcomecollection.org/works/actgjagb),
[Wellcome MS.5262](https://wellcomecollection.org/works/nuckbt25) und
[Wellcome MS.418](https://wellcomecollection.org/works/f6nzyzh4).

## Offene Schwächen

- `OL = WEITER` ist über 19 Ereignisse sehr attraktiv, kann aber eine rein
  formale Verknüpfung sein.
- `OT = FOLGE` ist kompositionell sauber, doch mehrere Mitglieder sind selten.
- Die Wärmeleiter enthält viele gelernte Einzelkarten; ihre genaue Temperatur
  ist nicht autonom rücklesbar.
- `ROH`, `HEISS`, `WARM`, `KLAR` und `DAUER` sind kreative Arbeitswerte, keine
  entzifferten Wörter.
- Das Netz erklärt Prozessreihenfolge besser als konkrete Pflanzen-, Körper-
  oder Stoffnamen.

## Dateien

- `R4_173_DICTIONARY.tsv`
- `R4_381_INTERLINEAR.tsv`
- `R4_116_SENTENCES.tsv`
- `R4_11_RECORDS.md`
- `R4_PARADIGM.tsv`
- `R4_BUILD.py`
- `R4_VALIDATE.py`
- `R4_VALIDATION.json`

f84 und f84r blieben versiegelt.

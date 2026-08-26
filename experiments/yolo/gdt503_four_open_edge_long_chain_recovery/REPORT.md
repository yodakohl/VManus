# GDT503 — die letzten vier Kanten waren nicht bloß atomar

Status: `BOTH_OPEN_RECIPES_HAVE_ONE_OLD_DIRECTIONAL_CHAIN__DIRECT_AND_SEPARATOR_SUPPORT_DISTINGUISHED`

## Ergebnis

GDT501/GDT502 hatten vier Zielzellen als „atomic-only“ stehen lassen:
`CH+CHD` und `CH+OK`, jeweils in PHARMA und SOURCE_SECTION_T. Das war innerhalb
des engen damaligen Suchraums richtig — es gibt weiterhin **kein** altes
eigenständiges Rezept mit genau diesen beiden Handlungsköpfen. Als Aussage über
die gesamte alte Kettenbasis war die Bezeichnung aber zu schwach.

Beide gerichteten Paare kommen je einmal in einer längeren alten Handlungskette
vor:

- `CH>OK` steckt in `P+OT+CH+OK+OR` auf f76r. `CH` und `OK` sind dort auch auf
  Komponentenebene unmittelbar benachbart: „Danach setze die Stationseinheit
  ein, entnimm die Stationseinheit und setze die Stationseinheit im
  Stationsgang an.“ Das ist `EMBEDDED_DIRECT_COMPONENT_ADJACENCY`.
- `CH>CHD` steckt in `K+CH+EE+D_ADDR+CHD+Y` auf f55v. Die Handlungsreihenfolge
  stimmt, doch `EE+D_ADDR` trennt die Köpfe sichtbar: „Gib den Pflanzenposten
  zu, nimm den Pflanzenposten und bearbeite den Pflanzenposten; auf Grad II; an
  der bezeichneten Stelle.“ Das ist
  `ORDERED_ACTION_CHAIN_WITH_VISIBLE_SEPARATOR`.

Beide Klauseln projizieren exakt durch den alten GDT416-Compiler zurück.

## Was sich dadurch ändert

Die vier Karten haben nun mehr als bloße Einzelwurzelstützung. Für `CH+OK` ist
die gewünschte Handlungsfolge sogar lokal eingebettet. Für `CH+CHD` ist nur die
gerichtete Folge belegt; der Einschub darf nicht unterschlagen werden. Deshalb
bleiben alle vier Zielsätze als komponierte Arbeitssätze unverändert:

- „Nimm/Entnimm das zuvor Genannte und bearbeite es.“
- „Nimm das zuvor Genannte und setze es als Ansatz an.“ beziehungsweise
  „Entnimm das zuvor Genannte und trage es ein.“

Die Korrektur betrifft also die **Stärke und Art der alten Strukturstützung**,
nicht die zugrunde gelegten Wurzelbedeutungen und nicht den deutschen Satz.

## Richtungs- und Familienkontext

Die Umkehrung hilft, die beiden Fälle auseinanderzuhalten. `CHD>CH` ist in der
alten breiten Kettenbasis gar nicht belegt; `OK>CH` dagegen 29-mal. Die Daten
werden deshalb nicht auf ein symmetrisches ungeordnetes Paar reduziert.

Auch die Handlungsklassen sind keineswegs leer. Für den Übergang
SELECT→HOLD_PROCESS liefern `CH>SH`, `S>SH` und `S>CHD` zusammen 21 alte
Ereignisse. Für SELECT→MOVE_SET liefern fünf verwandte Paare zusammen 230.
Diese 251 Peer-Ereignisse machen die Komposition plausibler, ersetzen aber den
fehlenden eigenständigen Zieltyp nicht.

GDT444 enthält außerdem elf akzeptierte Ein-Fokus-Trennrouten für `CH>CHD`.
Alle elf lassen das direkte Paar ausdrücklich unpromoviert. Das passt zur
jetzigen Lesart: Reihenfolge ja, direkte Zwei-Kopf-Einheit nein.

## Ergebnisgrenze und nächster Schritt

Der unabhängige Validator besteht 54 von 54 Prüfungen. Es wurde keine neue
Seite verwendet und keine Oberfläche oder Vorkunft vorhergesagt. Als Nächstes
sollten die 46 bereits konkreten GDT502-Vergleichskarten auf ihren semantischen
Zusatz geprüft werden: Bewirkt die jeweils hinzugefügte Komponente im deutschen
Satz tatsächlich denselben kleinen Bedeutungsunterschied über alle Register?

`BROADER_CHAIN_SUPPORT_ONLY__TWO_HEAD_TARGETS_REMAIN_COMPOSED__NO_SURFACE_PREDICTION`

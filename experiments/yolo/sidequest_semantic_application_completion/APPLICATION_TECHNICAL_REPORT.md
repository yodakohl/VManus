# Technischer Anwendungs- und Wartungsdurchgang

Rolle: **Badehaus- und Apparatezeichner einer Werkstatt um 1420**. Status:
kreative Arbeitslesung auf den festen zehn Sidequest-Seiten, keine behauptete
Entzifferung. Verwendet wurden nur die aktuelle Sidequest-Route, die ausgewählte
Filtrationsedition und die bereits zugelassenen lokalen Bildbesitzer. Es wurde
keine weitere Seite und kein neues Bild geöffnet. `f84` und `f84r` blieben
versiegelt.

## Ergebnis

Die Anwendungskarten bilden am besten **keine eigene Körpersprache**. Sie bilden
eine kurze, lehrbare Ziel- und Kontaktgrammatik, die ein Schreiber sowohl für
einen Menschen als auch für ein Becken, ein Gefäß, einen Einsatz oder einen
Leitungsabschnitt verwenden kann:

```text
ZUBEREITEN -> PORTION -> ZIELSTELLE -> ANSETZEN/WASCHEN
            -> KURZ / LÄNGER / VOLLSTÄNDIG HALTEN -> SCHLIESSEN
```

Der jeweilige Bildbesitzer oder ein gelerntes Ganzwort liefert den Sachträger.
So kann `AL` bei einer Pflanzensalbe eine Auflagestelle, im Figurenbecken eine
Badestelle und am f83r-S-Lauf eine technische Übergabestelle sein. Das ist ein
einfaches Werkstattsystem: Der Lehrling lernt **eine** Adress- und
Kontaktgrammatik, nicht für jede Abbildung neue Verben.

Der vollständige Prüfbestand umfasst **19 exakte Karten, 58 Ereignisse und 45
ganze Aussagen**. Jede Karte, jedes Ereignis, jeder Besitzer und jede vollständige
betroffene Aussage steht in `APPLICATION_TECHNICAL_PARADIGM.tsv`. Keine der
Zielkarten erhielt einen unbekannten Default.

## Die lehrbare Kurzgrammatik

| Baustein | kurzer Werkstattwert | was er nicht festlegt |
|---|---|---|
| `AL` | **ZIEL- ODER ARBEITSSTELLE** | Haut, Becken, Gefäß, Leitung oder Pflanzenteil |
| `OK` | **IN DEN ARBEITSGANG SETZEN / ANSETZEN** | weder Stoff noch Ziel |
| `E` | **KURZER KONTAKT** | keine genaue Zeit |
| `EE` | **ANHALTENDER KONTAKT** | keine genaue Zeit oder Temperatur |
| `EEE` | **VOLLSTÄNDIGER KONTAKT** | welches Objekt durchtränkt wird |
| `Y` | **DER LAUFENDE POSTEN / DIES** | nicht „offen“ und nicht Wasser |
| terminales `DY` | **ARBEITSSCHRITT SCHLIESSEN** | nicht jedes sichtbare `dy` |
| `LDDY` in `QOKYLDDY` | **BEFESTIGEN; SCHLUSS** | nicht von selbst „warme Kompresse“ |

Daraus entstehen ohne neue Ganzsätze:

```text
AL          Ziel- oder Arbeitsstelle
OKAL        an der Zielstelle einsetzen
OKALY       den laufenden Posten an der Zielstelle einsetzen
OTAL        danach zur Zielstelle
OKEEDAL     an der Zielstelle länger in Kontakt halten

OKEY        den laufenden Posten kurz anlegen/benetzen, offen
OKEEY       den laufenden Posten länger in Kontakt halten, offen
OKEDY       kurz benetzen/spülen; Schluss
OKEEDY      länger in Kontakt halten/einweichen; Schluss
OKEEEDY     vollständig benetzen/durchtränken; Schluss
```

`q`, die wechselnden sichtbaren Hüllen und die renderergebundenen Varianten
ändern diese Kartenwerte nicht.

## Entscheidung für alle neunzehn Zielkarten

| Karte | Ereignisse | kurzer konstanter Wert | beste lokale Entscheidung |
|---|---:|---|---|
| `AL` | 10 | Ziel-/Arbeitsstelle | neutral; Besitzer wählt Körper oder Station |
| `OKAL` | 6 | an der Zielstelle einsetzen | H4 mögliche Auflage; biologische Belege meist Station |
| `QOKALY` | 1 | laufenden Posten an Zielstelle einsetzen | B2-Filterkette klar technisch |
| `OTAL` | 3 | danach zur Zielstelle | lokale Stationsfolge, keine bewiesene Flussrichtung |
| `OKEEDAL` | 1 | am Ziel länger halten | B1-Beckenbuchung; Teilbad und Anlagenkontakt bleiben isomorph |
| `OKEY` | 2 | kurz anlegen/benetzen | B1-Waschrahmen körpernah, B2-Transferrahmen technisch |
| `OKEEY` | 7 | länger in Kontakt halten | ein Körperfall, mehrere Charge-/Stationsfälle |
| `OKEDY` | 8 | kurz benetzen/spülen; Schluss | gleicher Schluss für Körper- und Leitungswaschung |
| `OKEEDY` | 10 | länger halten/einweichen; Schluss | Bad, Ansatz, Tuch und Stationsbereich je nach Besitzer |
| `OKEEEDY` | 1 | vollständig durchtränken; Schluss | B2-S012 körpernah, Tuch bleibt Rivale |
| `LCHEEY` | 1 | benetzte Stelle | B2-S012: stärkster Körperbesitz, aber kein Anatomiewort |
| `DSHEOL` | 1 | bestreichen | B1-Gefäß-/Auffangkette eher technische Fläche |
| `SHECTHEDCHY` | 1 | auftragen | f83r-Figuren-/Gefäßstation bleibt doppellesbar |
| `QOLKY` | 1 | behandelte Stelle | wegen folgendem Auslass eher Stationspunkt als Körperteil |
| `KCHOL` | 1 | auflegen | H5-Anwendung textlich stark; Bild zeigt nur Pflanze |
| `CHOY` | 1 | mit Wasser waschen | in H5 am besten vorbereitende Pflanzenwaschung |
| `RSHEDY` | 1 | Waschportion verwenden; Schluss | lokale Körperwaschung oder technische Spülportion |
| `CHEECKHODY` | 1 | außen anwenden; Schluss | H5 körpernah; Außenbeschichtung bleibt Rivale |
| `QOKYLDDY` | 1 | laufenden Posten befestigen; Schluss | B4-Auflage stark, Filter-/Einsatzbefestigung gleich möglich |

## `LDDY`: die konkrete neue Entscheidung

`LDDY` kommt im Zielbestand nur eingebettet in `QOKYLDDY` bei E326 vor. Eine
freie Zerlegung in `L`, `D` und `DY` wäre daher erfunden. Der B4-Zusammenhang
gibt aber einen sehr guten gelernten Werkstattwert:

```text
B4-S001  OKEEDY
         länger einweichen/halten; Schluss

B4-S002  Gefäß füllen -> OKEEY -> OKEDY
         füllen -> länger halten -> kurz benetzen; Schluss

B4-S003  umsetzen -> OTAL -> nächsten Posten wählen
         -> OKEEY -> einsetzen -> ruhen; Schluss

B4-S004  QOKYLDDY
         laufenden Posten befestigen; Schluss

B4-S005  DAIN -> durcharbeiten -> OKEEDY
         Tuch -> bearbeiten -> länger einweichen; Schluss
```

Damit lautet der kurze Kartenkern:

```text
LDDY = BEFESTIGEN; DEN SCHRITT SCHLIESSEN
```

Die Körperfassung ist: „Lege die feuchte Auflage an die bezeichnete Stelle und
befestige sie; Ende.“ Die Apparatefassung ist: „Setze das feuchte Tuch oder den
Einsatz an die Öffnung und befestige ihn; Ende.“ Beide brauchen genau denselben
Kartenwert. **Warm**, **Wunde**, **Haut** und **Filter** gehören daher nicht in
`LDDY`; sie sind lokale Sachträger. Der sichtbare Bogen von f83r zeigt weder
Tuch noch Verband noch Knoten und entscheidet diese Alternative nicht.

## Was die Bildgeometrie wirklich beiträgt

| Besitzerbereich | sichtbarer Beitrag | begünstigte Lesung | nicht sichtbar |
|---|---|---|---|
| f55v/f56r Herbal | ganze Pflanze | Rezept-/Materialbesitz | Körper, Gefäß, Wasser, Auflage, Werkzeug |
| f81v gemeinsames Feld | viele Figuren innerhalb einer grünen Umgrenzung | Badekontakt **und** gemeinsames Becken | einzelne Zielstelle, Flussrichtung, Verband |
| f82r obere Paarstation | Figuren in Gefäßen, Bögen, Mittelzylinder; Hand am Bogenende | lokale Bedienung von Körper und Gerät | eindeutige Quelle, Senke, Hautziel |
| f82r mittlerer Knoten | Gerät-/Linienknoten | technischer Lauf | Patientenziel |
| f82r unteres Mehrfigurenfeld | Figuren schneiden direkt dieselbe grüne Fläche | stärkster sichtbarer Körper-/Flüssigkeitskontakt | bestimmtes Körperteil oder Tuch |
| f82r Randstationen | Figuren und kleine Gefäße am Feldrand | lokale Wasch- oder Portionierstelle | Verbindung zwischen allen Plätzen |
| f83r Randgefäße | einzelne Figuren in runder beziehungsweise korbartiger Station | Körperkontakt oder Gefäßbehandlung | Auftragsrichtung |
| f83r Hauptpaar | zwei Figuren und echter blauer Bogen | gemeinsamer Kontakt-/Stationsbesitzer | Pfeil, Auflage, Filtertuch, Hautstelle |
| f83r rechter S-Lauf/Fransenende | sichtbarer Lauf zum Mehrarmknoten beziehungsweise offenes Ende | Anlagen- und Übergabestelle | globaler Kreislauf |

Die Bilder wurden vor dem Text angelegt. Deshalb ist die Nähe eines Wortes zu
einer Kontur kein eigener semantischer Beweis: Texttaschen sind oft bloß die
verbliebenen freien Flächen. Belastbar ist nur der kleine lokale Besitzer, nicht
eine aus der Zeilenlage erfundene Leitung.

## Ganze Passagen, an denen die Alternative entscheidet

### H5-S001 und H5-S002: Anwendung am stärksten, aber ungemalt

```text
H5-S001
Pflanzenzubereitung -> Pflanze -> Blütebeginn -> Maß -> Pflanze
-> KCHOL AUFLEGEN -> nächste Zubereitung -> laufender Posten -> AL ZIELSTELLE

H5-S002
vom vorigen Posten nehmen -> CHOY MIT WASSER WASCHEN
-> laufenden Posten einsetzen -> CHEECKHODY AUSSEN ANWENDEN; SCHLUSS
```

Flüssig: „Nimm von der Pflanze beim Blütebeginn das vorgeschriebene Maß und
lege das Material auf die Arbeitsstelle. Bereite den nächsten Posten. Nimm vom
vorigen Ansatz, wasche ihn mit Wasser und wende ihn außen an; Ende.“ Das ist
eine gute Auflagen-/Salbenlesung. Das Bild selbst zeigt jedoch nur die Pflanze;
Auslegen auf einer Schale und Beschichten eines Gegenstands bleiben möglich.

### B1-S002: Anlagenbuchung stärker

Die vollständige Aussage stellt Maß und laufende Beckenflüssigkeit ein, setzt
den Posten mit `OKAL` an eine Zielstelle, gibt mehrere Portionen aus demselben
Vorrat hinzu, hält ihn mit `OKEEDAL` länger am Ziel, führt ihn durch den
Durchlauf und schließt die Arbeitsbewegung. Eine Person kann darin baden; die
Kartenfolge beschreibt aber stärker die **Bedienung des gemeinsamen Beckens**
als eine einzelne Hautbehandlung.

### B1-S012: perfekte Doppellesung

```text
LSHO -> OKEY -> LSHEDY
Waschgang -> laufenden Posten kurz anlegen -> waschen; Schluss
```

Körper: „Beginne die Waschung, lege den Ansatz kurz an und wasche die Stelle;
Ende.“ Anlage: „Beginne den Spülgang, setze das Arbeitsstück kurz an und spüle
es; Ende.“ Die grammatische Lesung ist in beiden Fassungen dieselbe.

### B1-S014 und B1-S018: zwei vermeintliche Körperwörter kippen technisch

`B1-S014` lautet vollständig:

```text
Posten durcharbeiten -> QOLKY BEHANDELTE STELLE -> Auslassstelle
-> mit Vorigem weiter -> danach auslassen
```

Darum wird `QOLKY` nicht länger als anatomisches Wort festgeschrieben. Ein
bearbeiteter Stationspunkt erklärt den anschließenden Auslass einfacher.

`B1-S018` lautet:

```text
Gefäß füllen -> DSHEOL BESTREICHEN -> Sollstufe
-> länger auffangen; Schluss
```

Auch hier ist das Bestreichen einer Gefäß-, Fugen-, Tuch- oder
Stationsfläche mindestens so gut wie das Bestreichen eines Körpers.

### B2-S005: eindeutigster Anlagenkontext

```text
QOKALY Ziel einsetzen -> Seihtuch -> Durchlauf -> Maß -> Maß
-> gleiche Einstellung -> länger warm halten -> abziehen; Ende
```

`QOKALY` bedeutet hier nicht „zweite Behandlung“, sondern schlicht: den
laufenden Posten am Ziel einsetzen. Alles Weitere ist Filter-/Durchlaufarbeit.

### B2-S012: eindeutigster Körperanwendungskontext

Nach dem sichtbaren Besitzerwechsel in der Aussage folgt im unteren grünen
Mehrfigurenfeld:

```text
OKEEY länger halten -> LCHEEY benetzte Stelle -> Maß
-> laufender Posten -> OKEEEDY vollständig durchtränken; Schluss
```

Flüssig: „Halte den Ansatz länger an der benetzten Stelle, nimm das
vorgeschriebene Maß und durchtränke den Bereich vollständig; Ende.“ Das ist die
stärkste Körperlesung, weil Figuren und Fläche direkt zusammentreffen. Trotzdem
heißt `LCHEEY` nur **benetzte Stelle**; ein Tuch oder ein Einsatz kann ebenso
vollständig benetzt werden.

### B2-S016: Stationsbedienung stärker

```text
AL Zielstelle -> aus Quelle hinausführen -> gleiche Anteile -> Maß
-> nächsten Posten länger halten -> auf Maß stellen
-> OKEY kurz anlegen -> hineinführen; Schluss
```

Das ist eine Quellen-, Portionier- und Übergabekette. `OKEY` bleibt „kurz
anlegen/benetzen“; die lokale Ausführung ist hier eher ein Einsatz oder
Arbeitsstück als eine Körperauflage.

### B4-S001 bis B4-S005: Auflage und Einsatz bleiben bewusst isomorph

Die zusammenhängende B4-Folge kann als Auflagenarbeit gelesen werden:

> Weiche die Auflage länger ein. Fülle das Gefäß, halte sie im Ansatz und
> benetze sie kurz. Bringe sie danach zur Zielstelle und lass sie ruhen. Lege
> den laufenden Posten an und befestige ihn; Ende. Nimm das nächste Tuch,
> arbeite es durch und weiche es ein.

Sie kann mit denselben Karten aber auch als Anlagenwartung gelesen werden:

> Weiche den Einsatz ein. Fülle das Gefäß, halte den Einsatz im Ansatz und
> spüle ihn kurz. Bringe ihn zur Zielöffnung und lass ihn setzen. Befestige ihn;
> Ende. Nimm das nächste Tuch, bearbeite es und weiche es ein.

Der B4-Text trägt also stark **nasses Tuch/Einsatz plus Befestigung**. Er trägt
nicht aus eigener Kraft die Entscheidung Patient gegen Apparat.

## Werkstattfazit

Die beste neue Basis ist:

1. **Körperanwendung und Anlagenwartung teilen eine Grammatik.** Das macht das
   System für mehrere Schreiber um 1420 einfach erlernbar.
2. `AL`, `OK`, die drei E-Grade, `Y` und terminales `DY` bleiben produktiv.
3. `LCHEEY`, `DSHEOL`, `SHECTHEDCHY`, `QOLKY`, `KCHOL`, `CHOY`, `RSHEDY` und
   `CHEECKHODY` sind kurze gelernte Ganzkarten; ihre Werte wurden auf ein bis
   drei Wörter gekürzt.
4. **`LDDY = befestigen; Schluss`** ist die beste konkrete Ergänzung. Eine
   warme Auflage oder ein Filtereinsatz ist der lokale Gegenstand, nicht die
   Bedeutung des Kerns.
5. Der stärkste Körperfall ist `B2-S012`; die stärksten technischen Fälle sind
   `B1-S002`, `B2-S005` und `B2-S016`. `B4-S001` bis `B4-S005` ist die wertvolle
   Brücke: exakt dieselbe Notation funktioniert für Auflage und Einsatz.

Damit ist die Zielkette konkret und lehrbar:

```text
PREPARATION -> PORTION -> TARGET -> APPLY/WASH -> HOLD -> CLOSE
```

Slots dürfen ausgelassen oder vom lokalen Besitzer geerbt werden; eine Aussage
muss nicht mit einer physischen Zeile enden. Die volle Ereignis- und
Aussagenabdeckung steht in der Paradigmentabelle.

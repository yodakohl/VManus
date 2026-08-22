# R3 — Wärme, Zeit, Prozessstufe und Werkstattschluss

## Ergebnis

Die kleinste ausführbare technische Arbeitsnotation auf den festen Prosaseiten
ist:

```text
[OT FOLGE | OL FORTSETZUNG]
    + PROZESSBASIS
    + [E STUFE I | EE STUFE II | EEE STUFE III]
    + [Y OFFEN | terminale DY-KONSTRUKTION SCHLUSS]
```

Die Prozessbasis kann beispielsweise `OK=ANSETZEN`, `CHK=WÄRMEN`,
`SHED=ABSETZEN`, `CTH=BEREIT` oder `SOLK=AUFFANGEN` sein. `E/EE/EEE`
sind keine Wörter für kurz, lang und vollständig. Sie sind eine geordnete
Skala, die je nach Basis als Dauer, Stärke oder Vollständigkeit ausgeführt
wird. `Y` hält einen aktuellen Posten offen; nur eine bereits lizenzierte
terminale `DY`-Konstruktion verbucht den Schluss.

Das ist eine kreative Werkstattlesung, keine Entzifferung. Bearbeitet wurden
nur `f10r`, `f11r`, `f55v`, `f56r`, `f81v`, `f82r` und `f83r`. Die drei
Astroseiten wurden nicht verändert. `f84` und `f84r` blieben vollständig
versiegelt.

## Rolle des technischen Registerschreibers

Die unveränderte R3-Perspektive behandelt die Karten wie Einträge eines
Werkstattregisters: ein gespeicherter Wert wird mit Maß, Stufe, Folgebezug und
Commit-Zeichen verbunden. Die Regel muss von mehreren Händen abschreibbar sein,
ohne moderne Algebra vorauszusetzen. Deshalb wird nicht jede ähnliche
Oberfläche zerlegt. Für häufige Raster lernt der Schreiber ein kleines Schema;
für widersprechende Fachkarten lernt er ein vollständiges Exemplar.

## 1. Ausführbare Schreib- und Leseregel

### Schritt A — Prozessbasis wählen

| Basis | kurzer Werkstattwert | Beispiele |
|---|---|---|
| `OK` | ansetzen / in Arbeit stellen | `OKY`, `OKEY`, `OKEEY`, `OKEDY`, `OKEEDY`, `OKEEEDY` |
| `CHK` | wärmen | `CHEKY`, `CHEEKY`, `CHKEEY`, `CHKEEDY` |
| `SHED` | absetzen | `SHEDY`, `SHEEDY`, `SHEDAL`, `SOLSHEDY`, `QOKSHEDY` |
| `CTH` | bereit | `CTHY`, `CTHEY` |
| `SOLK` | auffangen | `SOLKEY`, `SOLKEEY`, `SOLKEEDY` |

`SHED` erhält bewusst den konkreten Wert **ABSETZEN** statt des alten
„ruhen oder absetzen“. In den technischen Wasser-/Filtrationspassagen ist
Absetzen eine ausführbare Handlung; die Doppellesung war nur ein Ausweg.

### Schritt B — Stufe eintragen

| sichtbarer Grad | Registerwert | typische lokale Ausführung |
|---|---|---|
| unmarkiert | Basiszustand | ansetzen, bereit |
| `E` | Stufe I | kurz, mild, erster Durchgang |
| `EE` | Stufe II | länger, stärker, anhaltend |
| `EEE` | Stufe III | vollständig, bis zum Endgrad |

Die Skala ist in mehreren unabhängigen Basen lesbar:

```text
OK+E+Y       kurz ansetzen        OK+EE+Y       länger ansetzen
OK+E+DY      kurz ...; Schluss    OK+EE+DY      länger ...; Schluss
OK+EEE+DY    vollständig ...; Schluss

CHK+E+Y      kurz wärmen          CHK+EE+Y      länger wärmen
CHK+EE+DY    länger wärmen; Schluss

SHED+E+DY    absetzen; Schluss    SHED+EE+DY    länger absetzen; Schluss

SOLK+E+Y     kurz auffangen       SOLK+EE+Y     länger auffangen
SOLK+EE+DY   länger auffangen; Schluss
```

Die beiden Oberflächen `CHEEKY` und `CHKEEY` speichern beide
`CHK+EE+Y`. Einmal steht die Stufe innerhalb der sichtbaren CH–K-Hülle, einmal
danach. Für einen Schreiber sind das zwei zu lernende Schreiblagen desselben
Werts, kein Grund für zwei Bedeutungen.

### Schritt C — offen lassen oder verbuchen

- `...Y` bezeichnet in den gebundenen Rastern den offenen beziehungsweise
  weitergeführten Posten.
- `...DY` schließt nur dort, wo die **gesamte exakte Karte** als terminale
  Konstruktion lizenziert ist.
- Ein nacktes `dy` ist kein globales Schlusswort: die exakte
  `CHEY|CHY|DY|SHY|SY|Y`-Familie enthält sogar eine `dy`-Oberfläche mit dem
  offenen Wert „dieser Arbeitsposten“.

Der Lehrling darf daher nie allein die letzten zwei Zeichen sehen und
„Schluss“ eintragen. Er muss die vollständige Karte oder das gelernte Raster
erkennen. Alle 37 bereits aktiven Schlusskartentypen sind im Paradigma einzeln
erfasst.

### Schritt D — Folge oder Fortsetzung voranstellen

`OT` und `OL` sind keine Inhaltswörter:

| Träger | Registerwert | Beispiele |
|---|---|---|
| `OT` | Folge / danach / nächster | nächster Ansatz, nächstes Sollmaß, Folgeposten, danach umsetzen |
| `OL` | mit dem Vorigen fortsetzen | voriger Ansatz, voriger Posten, weitere Portion, Vorigen weiterführen |
| `OK+OK` | erneuter Arbeitsaufruf | Posten erneut ansetzen |

Damit werden scheinbar verschiedene Satzglossen auf kurze Werte reduziert:

```text
OT+OR       nächster Ansatz
OL+OR       voriger Ansatz
OT+AIIN     nächstes Sollmaß
OT+OL       danach fortsetzen
OT+CHED+DY  danach umsetzen; Schluss
OL+CHED+DY  Vorigen weiterführen; Schluss
OK+OK+CHY   Posten erneut ansetzen
```

`ROL`, `LOL`, `OLTCHY`, `OTYTCHOL` und `QOTEDAIIN` werden gerade **nicht**
blind nach sichtbarem `OL` oder `OT` zerlegt. Ihre exakten Kartenwerte
widersprechen einer solchen mechanischen Teilung.

Daneben bleibt ein kleiner gelernter Reihenfolgenstapel: `CHODALY=BLÜTEBEGINN`,
vier verschiedene exakte Karten für **ERSTE ÖFFNUNG**, `CHEEETY=ERSTE
SPÜLUNG`, `DALDY/LCHECKHY=ZWEITE ÖFFNUNG`, `SHOYTY=FÜR DEN ZWEITEN GEBRAUCH
ZURÜCKLEGEN`, `QOTCHY=ZURÜCKBEHALTENE BLÜTEN` sowie die Gleichheitskarten
`OCTHEOL=GLEICHE EINSTELLUNG` und `CHES=GLEICHE ANTEILE`. Sie sind zeitlich
oder ordinal lesbar, liefern aber noch keinen gemeinsamen sichtbaren Stamm.

## 2. Maß ist nicht Zeit, und Zielstufe ist nicht Sollmaß

Die ähnlich aussehenden Registerwerte bleiben getrennt:

```text
AIIN         Sollmaß
OK+AIIN      auf Sollmaß einstellen
OT+AIIN      nächstes Sollmaß
Y+AIIN       Sollmaß des Postens

IIN          Zielstufe
K+IIN        weiche Zielstufe
DA+IIN       zweite Öffnungsstufe
```

`AIIN` bedeutet also nicht von sich aus Zeit. Erst eine Fachhülle macht daraus
einen Prozessparameter:

```text
SHFY+AIIN    Standzeit
CHLD+AIIN    Absetzstand
```

Das ist als Registerverfahren einfach: derselbe vorgeschriebene Zahlen-/Maßwert
wird je nach Besitzer als Menge, Standzeit oder Absetzstand gelesen. Dagegen
speichert `IIN` eine Zielstufe. Die Zahl der sichtbaren `i` und die exakte
Kartenidentität dürfen deshalb nicht geglättet werden.

## 3. Wärmeinventar: ein produktives Raster plus Ganzkarten

### Produktiv

Nur die `CHK`-Familie verhält sich wie eine kleine Wärmegrammatik:

| Karte | Default | Aufbau |
|---|---|---|
| `CHEKY` | kurz wärmen | `CHK + E + Y` |
| `CHEEKY` | länger wärmen | `CHK + EE + Y`, interne Schreiblage |
| `CHKEEY` | Posten länger wärmen | `CHK + EE + Y`, nachgestellte Schreiblage |
| `CHKEEDY` | länger wärmen; Schluss | `CHK + EE + DY` |

### Gelernte Fachkarten

| Karte | kurzer Default | warum kein freier Stamm erzwungen wird |
|---|---|---|
| `SCHOAL` | Weinsud | Produktname; der Satzplatz liefert das Bereiten |
| `QOTCHOL` | sanft wärmen | `OTYTCHOL=auffangen` und `TSHOL=Blütenkraut` blockieren freies `TCHOL` |
| `OLTCHY` | sanft wärmen | kein selbständiges `TCHY`; initiales `OL` muss hier nicht Fortsetzung sein |
| `CHARY` | abkühlen | einmalige Ganzkarte |
| `RAL` | abkühlen | zweite Ganzkarte ohne sichtbaren gemeinsamen Kühlstamm |
| `TCHODY` | abkühlen; Schluss | gelernte Kühlbasis plus terminale Konstruktion |
| `ROL` | vor Abkühlung | gelernte thermische Grenze, nicht `R+OL` |
| `LOL` | Warmpunkt | kurzer Endpunkt statt Satz „bis es warm ist“ |
| `QEKY` | ungekocht | negativer Zustand; nicht frei als E/Y-Raster zerlegt |
| `ODY` | Kühllager; Schluss | vollständige Kühllagerkarte; kein globales `O=kühl` |
| `SHECTHY` | temperiert | Zustand, nicht Warmwasser und nicht CTH-Bereitschaft |
| `RSHEAL` | Warmwasser | Material, keine Wärmeanweisung |
| `SKAR` | Warmausguss | Material/Transfer, keine CHK-Karte |

Damit bleibt `SCHOAL` sauber: Die Wörterbuchkarte sagt **WEINSUD**, nicht
„koche die Pflanze in Wein“. Im flüssigen Satz kann der Schreiber aus dem
Vorbereitungsplatz „Bereite den Weinsud“ lesen.

## 4. Harte Gegenbeispiele gegen Überzerlegung

| scheinbare Ähnlichkeit | tatsächliche aktive Karte | Konsequenz |
|---|---|---|
| `CHCKHAL` / `SHECKHAL` | Dauer / mäßige Menge | `CKHAL` ist kein freier Dauerstamm |
| `CTHY` / `CTHOOR` / `CTHAIIN` | bereit / säubern / Kraut zerstoßen | `CTH` ist nur im gebundenen Bereitschaftsraster produktiv |
| `SHECTHY` / `SHECTHEDCHY` | temperiert / aufstreichen | lange Oberfläche schlägt Teilähnlichkeit |
| `AIIN` / `DAIIIN` / `QOTEDAIIN` / `CHODAIIN` | Sollmaß / Öffnungsstufe / breites Gefäß / Geschwür | sichtbares DAIIN reicht nicht zur Maßzerlegung |
| `QOTCHOL` / `OTYTCHOL` / `TSHOL` | sanft wärmen / auffangen / Blütenkraut | kein allgemeines TCHOL-Wort |
| terminales `...DY` / nacktes `dy` | Schlusskonstruktion / aktueller Posten | Schluss ist konstruktionsgebunden |

Diese Ausnahmen sind kein Versagen der Werkstattnotation. Ein Register um
1420 darf eine kleine produktive Abkürzungsschicht und daneben gelernte
Fachkürzel oder Ganzkarten besitzen. Der Fehler wäre, jede sichtbare
Teilähnlichkeit nachträglich zu Grammatik zu erklären.

## 5. Zusammenhängende Rücklesungen

Die Kartenwerte bleiben kurz; erst die Aussage fügt sie zusammen.

1. **H1-S002 — `QOKCHY · QOTCHOL · CHOL · CTHY`**

   „Setze den Posten an, wärme ihn sanft, führe ihn mit dem vorigen Ansatz
   fort; nun ist er gebrauchsfertig.“

2. **H2-S002 — `QOTCHOR ... OTOL ... CHOLOR ... DAIIN`**

   „Nimm den nächsten Ansatz, führe danach mit dem vorigen fort und halte das
   Sollmaß aus demselben Vorrat ein.“

3. **H3-S001 — `TSHOL · SCHOAL · CFHY · SHFYDAIIN · CPHY · SHEY · TCHODY`**

   „Bereite aus dem Blütenkraut den Weinsud, wringe ihn aus, halte die
   Standzeit ein, seihe nach, nimm den Klarauszug und lasse ihn abkühlen;
   Schluss.“

4. **H4-S003 — `YKAIIN · CHEOAR · CHEEKY · OLDY`**

   „Nimm das Sollmaß des Postens und den Auszug daraus, wärme länger, führe
   fort und schließe.“

5. **B1-S008 — `CHEY · OL · CHEKY · OL · SHEDY`**

   „Führe diesen Posten mit dem vorigen fort, wärme ihn auf Stufe I, führe
   wieder mit dem vorigen fort und lasse ihn absetzen; Schluss.“

6. **B2-S005 — `... QOKAIIN · QOKAIIN · OCTHEOL · CHKEEY · LDY`**

   „Führe den Posten durch Seihtuch und Durchlass, stelle zweimal dasselbe
   Sollmaß ein, wärme den Posten länger, ziehe ihn ab und schließe.“

7. **B3-S014 — `OKAIR · SHEEDY`**

   „Setze das Wasser in Gang und lasse es auf Stufe II absetzen; Schluss.“

8. **B3-S026 — `CHEEDAR · CHLDAIIN ... CHECTHY ... SOLKEEDY`**

   „Richte die Beckenstation ein, warte bis zum Absetzstand, setze eine Portion
   um; sobald sie gebrauchsfertig und klar ist, fange länger auf und schließe.“

9. **B4-S010 — `OLDY`**

   „Fortsetzen; Schluss.“ Die frühere ganze Aussage „Erwärme den Bade- oder
   Waschzusatz sanft“ war nicht in dieser Karte gespeichert und wurde entfernt.

10. **B4-S015 — `... CHCKHAL · SOLKEY · LCHEDY`**

    „Gib die Portion des Klarauszugs für die angegebene Dauer, fange kurz auf,
    führe hinaus und schließe.“

11. **B5-S003 — `SHEDAL ... LOL ... AIIN ... DAIIIN ...`**

    „Arbeite an der Absetzstelle mit dem vorigen Posten bis zum Warmpunkt,
    halte das Sollmaß ein und setze an der zweiten Öffnungsstufe weiter um.“

## 6. Wo das Modell scheitert oder bewusst stoppt

- `E/EE/EEE` ordnet Stufen, beweist aber nicht, ob jede Stufe Minuten,
  Temperatur, Intensität oder Vollständigkeit zählt. Die Prozessbasis bestimmt
  die lokale Ausführung.
- Die beiden Schreiblagen von `CHK+EE+Y` sind nur für die vorhandenen exakten
  Karten gleichgesetzt. Daraus folgt kein universelles Umstellungsverfahren.
- `DY` ist kein freies Schlusswort; nur die lizenzierte terminale Konstruktion
  schließt.
- `OT` bedeutet Folge, nicht automatisch Wiederholung. Explizite Wiederholung
  ist am klarsten in `OK+OK+CHY`; `LKEDY` bleibt eine gelernte zweite Waschung.
- `AIIN` ist Sollmaß, nicht Zeit. `SHFY` und `CHLD` schaffen erst Standzeit und
  Absetzstand.
- `SCHOAL`, `QOTCHOL`, `OLTCHY`, `CHARY`, `RAL`, `ROL`, `LOL`, `QEKY`,
  `ODY`, `SHECTHY`, `RSHEAL` und `SKAR` bleiben Fachkarten. Eine attraktive
  Zerlegung wird nicht allein durch Buchstabenähnlichkeit erlaubt.
- Die Ausgabe sagt weiterhin nicht, ob ein technischer Posten medizinisch,
  badehäuslich, alchemisch oder rein apparativ ist. Die Bilder und lokalen
  Besitzer dürfen eine konkrete Passage ausführen, aber keinen globalen Stamm
  umdefinieren.

## 7. Umfang und Dateien

| Bestandteil | Umfang |
|---|---:|
| Wörterbuch | 173 Karten |
| Interlinear | 381 Ereignisse |
| Aussagen | 116 |
| vollständige Records | 11 |
| revidierte exakte Kartentypen | 54 |
| revidierte Ereignisse | 170 |
| betroffene Aussagen | 87 |
| Paradigma-/Gegenbeispielzeilen | 106 |
| einzeln auditierte Schlusskartentypen | 37 |

Artefakte:

- `R3_173_DICTIONARY.tsv`
- `R3_381_INTERLINEAR.tsv`
- `R3_116_SENTENCES.tsv`
- `R3_11_RECORDS.md`
- `R3_PARADIGM.tsv`
- `R3_BUILD_THERMAL_TEMPORAL.py`
- `R3_VALIDATION.json`
- `R3_BUILD_SUMMARY.json`

Die Validierung ist `PASS`: 173/381/116/11 vollständig, alle Defaults konkret
und nichtleer, Ereignis-Karten-Bindung konsistent, alle 37 ausgewählten
Schlussfamilien und alle geforderten Wärme-/Zeitkarten inventarisiert, alle
Gegenbeispiele vorhanden, nur die sieben erlaubten Prosaseiten, keine
Astroänderung und kein Zugriff auf `f84` oder `f84r`.

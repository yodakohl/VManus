# V13 R3 — L/O als mitgeführter Beziehungsstrich

Datum: 2026-08-21

Status: unabhängiger explorativer Sidequest-Kandidat; keine Übersetzung und
kein GDT-Ergebnis. Perspektive R3 (technischer Register-/Notationsschreiber).
Die V13-Ergebnisse der anderen Rollen wurden nicht gelesen. `f84` und `f84r`
blieben versiegelt.

## Entscheidung

Die beste konkrete Funktion der exakten Karte
`dcda95c81a5460feb191` ist:

```text
L/O := TRAGE DIESEN EINTRAG UNTER DEMSELBEN BEZUG EIN
       / VERBINDE IHN MIT DEM AKTIVEN EINTRAG
```

Eine knappe Quellparaphrase ist **„mit / dazu / unter demselben Bezug“**.
Das ist kein Wörterbucheintrag. Technisch ist L/O ein Beziehungsstrich mit
zwei möglichen Endpunkten. Sichtbare Nachbarn liefern die Endpunkte; fehlt
einer an einer Feldkante, kommt er aus dem aktiven Registereintrag. Fehlen
beide im Ein-Karten-Feld, gilt der Strich als Ditto-Buchung: dieselbe
Beziehung wird für den nächsten bzw. fortgesetzten Eintrag beibehalten.

Das Modell ist konkreter als bloß `RELATION_EDGE`, behauptet aber weder
Gleichheit noch eine bestimmte Richtung wie „A wird auf B angewandt“. Die
Richtung bleibt eine Eigenschaft des jeweiligen Registerstencils.

Arbeitskonfidenz: **0,74**. Stärkster Rivale ist **AND/ALSO als
Listenkoordinator** mit **0,46**. Die Werte sind getrennte Plausibilitäten,
keine normierten Wahrscheinlichkeiten.

## Datenzugang und Kartenidentität

Die sieben erlaubten Prosaseiten wurden mit `./vmanus-exp query-tsv`, sieben
einzeln angegebenen `--allow`-Werten und `--forbid-prefix f84` aus
`gdt327_joint_tuple_interlinear.tsv`, `gdt276_event_inventory.tsv` und dem
GDT374-Record-Inventar gezogen. Es wurden 381 Ereignisse und genau 19 Treffer
selektiert. Die Kreis-Seiten enthalten keine GDT327-Ereignisse und tragen
daher zu dieser exakten Karte nichts bei.

Die 19 Treffer liegen nur auf `f10r` (3), `f81v` (9) und `f83r` (7). Ihre
sichtbaren Formen sind Renderer derselben Karte:

| Renderer | Oberfläche | Treffer |
|---|---|---:|
| `ch` | `chol` | 3 |
| keiner | `ol` | 8 |
| `q` | `qol` | 3 |
| `s` | `sol` | 3 |
| `t` | `tol` | 1 |
| `che` | `cheol` | 1 |

Darum werden keine Bedeutungen aus `ch/q/s/t/che` und keine Unterstrings oder
Laute abgeleitet.

## Vollständige 19er-Inventur

In der Kontextspalte trennt `|` vollständige Felder derselben physischen
Zeile. Eckige Klammern markieren ausschließlich die exakte L/O-Karte. `C*`
bezeichnet eine nachfolgende Karte mit formalem DY-Schluss; es ist kein
semantischer Klartext.

| Nr. | Ort; Record/Feld | Lage | vollständiger Zeilen-/Feldkontext | Ausführung |
|---:|---|---|---|---|
| 1 | f10r.5; R1/F1 | medial | `qokchy qotchol [chol] cthy` | linker und rechter Kartenblock sichtbar |
| 2 | f10r.8; R2/F1 | medial, wiederholt | `qotchor chor otol [chol] cholor [chol] daiin dar` | erste Kante einer Kette |
| 3 | f10r.8; R2/F1 | medial, wiederholt | derselbe vollständige Kontext | zweite Kante derselben Kette |
| 4 | f81v.2; R1/F2 | medial, wiederholt | `qokedy | okaiin kair okal sar [ol] kain olkain al [ol] rol dl` | erste interne Zuordnung |
| 5 | f81v.2; R1/F2 | medial, wiederholt | derselbe vollständige Kontext | zweite interne Zuordnung |
| 6 | f81v.7; R1/F1 | medial | `olor [ol] sheckhal daiin qokeedal daiin chckhy schedy | [qol]` | gewöhnliche Kante vor Ditto-Feld |
| 7 | f81v.7; R1/F2 | **einzige Karte** | derselbe vollständige Kontext | beide Endpunkte geerbt; Relation/Bezug fortführen |
| 8 | f81v.17; R1/F2 | medial, vor Schluss | `sshkchdy | chedy [ol] shedy(C*) | qolchedy | qokain shckhy dl ral` | rechter Endpunkt ist aktueller Bezug; dann schließen |
| 9 | f81v.18; R1/F2 | medial, wiederholt | `qokchdy | chey [ol] cheky [ol] shedy(C*) | qokedy | qokedy | chckhy qoky` | `X–L/O–Y–L/O–CLOSE`, erste Kante |
| 10 | f81v.18; R1/F2 | medial, vor Schluss | derselbe vollständige Kontext | Y nochmals an aktiven Bezug buchen; schließen |
| 11 | f81v.21; R1/F3 | medial | `lsho qokey lshedy | lshedy | chedy qolky lchedal [qol] otar` | bilaterale Buchung; der folgende Schluss ist nicht DY |
| 12 | f81v.24; R1/F2 | medial, vor Schluss | `ytey okchedy | qokal okeey [qol] cheedy(C*) | sal teol dchdy | ly` | sichtbarer linker Block, geerbter Bezug, schließen |
| 13 | f83r.20; R1/F4 | **Feldanfang** | `solkeedy | qoteedy | qokeey qokedy | [sol] cheeety qokedy | qoky saiin` | linken Endpunkt aus F3 übernehmen |
| 14 | f83r.26; R2/F1 | medial, vor Schluss | `otchey qokeey qoky [tol] shedy(C*) | qokylddy` | linken Block an aktiven Bezug buchen; schließen |
| 15 | f83r.37; R2/F1 | **Feldanfang**, vor Schluss | `[sol] lkedy(C*) | lchedy | qokol shedy` | linker Endpunkt geerbt; kurze Zuordnung sofort schließen |
| 16 | f83r.48; R3/F1 | medial | `dal [cheol] lol chdal aiin` | beide Kartenblöcke sichtbar |
| 17 | f83r.49; R3/F1 | **Zeilen-/Feldanfang** | `[sol] daiiin chedy` | aktiven Endpunkt aus f83r.48 fortführen |
| 18 | f83r.52; R4/F1 | **Feldende** | `solkeey qekey raly [ol]` | linken Block merken; rechter Endpunkt bleibt offen |
| 19 | f83r.54; R4/F1 | medial | `daiin [ol] dain chey ldalor` | `daiin` verbraucht die offene Kante; danach neue Kante |

Die Positionsbilanz lautet 14 medial, 3 FIRST, 1 ONLY und 1 LAST. Zehn
mediale Belege haben auf beiden Seiten gewöhnliche Kartenblöcke. Vier
mediale Belege stehen unmittelbar vor derselben DY-Schlusskarte
(`bc4f1f5c...`: f81v.17, f81v.18, f81v.24, f83r.26). Zusätzlich folgt auf
das feldinitiale L/O von f83r.37 eine andere DY-Schlusskarte
(`b958a512...`). Damit gibt es **vier gleiche L/O–CLOSE-Konstruktionen plus
einen fünften, formal anderen Schlussfall**. Diese Trennung erklärt die
scheinbare Zähldifferenz zwischen „vier Konstruktionen“ und „fünfmal folgt
Schluss“.

## Ausführbare Schreibregel

Der Schreiber führt drei kleine Gedächtnisplätze, wie sie auch bei Listen,
Konten oder Rubriken praktikabel sind:

```text
H = aktiver Seiten-/Recordbezug (durch Bild, Rubrik oder letzten Commit gesetzt)
P = letzter vollständiger Kartenblock im laufenden Feld
E = offene rechte Kante, anfangs leer
```

Dann gilt:

1. Eine gewöhnliche Payload-Karte wird an den laufenden Block `P` angehängt.
   Falls `E` offen ist, ist der erste neue vollständige Block ihr rechter
   Endpunkt; danach wird `E` gelöscht.
2. Bei `P L/O Q` schreibe den Beziehungsstrich zwischen `P` und dem folgenden
   Block `Q`: „Q gehört mit/zu P unter dem aktiven Bezug H“.
3. Beginnt ein Feld mit L/O, setze den fehlenden linken Endpunkt auf den zuletzt
   committed/aktiven Eintrag; lies danach den rechten Block.
4. Endet ein Feld mit L/O, speichere `P` in `E`; der nächste nutzbare Block
   füllt den rechten Endpunkt auch über die physische Zeile hinweg.
5. Folgt auf L/O unmittelbar CLOSE, setze den fehlenden rechten Endpunkt auf
   `H` und schließe die so gebuchte Zuordnung. CLOSE ist kein Operand.
6. Steht L/O allein, kopiere die zuletzt geltende Beziehungsschablone und ihre
   aktiven Endpunkte in das nächste/fortgesetzte Feld: ein notationales
   „desgleichen unter diesem Bezug“.
7. Bei `X–L/O–Y–L/O–Z` entstehen zwei aufeinanderfolgende Buchungen im selben
   Rahmen. Die sparsamste Rücklesung ist eine Kette `X mit Y; Y weiter mit Z`;
   wo das Register einen festen Kopf H vorgibt, ist auch „Y und Z beide unter
   X/H“ zulässig. Die zehn Seiten entscheiden diese interne Richtung nicht.

Das ist mit Feder, Zeile und Gedächtnis des Schreibers ausführbar. Es setzt
keine moderne Algebra voraus: L/O verhält sich wie ein wiederholter
Zuordnungsstrich oder ein ausgeschriebenes „mit/dito“ in einem Register.

## Zwangsparsen der schwierigen Formen

### `X–L/O–Y–L/O–CLOSE`

f81v.18/F2 ist exakt:

```text
chey – L/O – cheky – L/O – shedy(CLOSE)
```

Rücklesung:

```text
Buche CHEKY in Beziehung zu CHEY;
halte CHEKY im gleichen aktiven Bezug H;
schließe den Eintrag.
```

Der zweite Strich ist nicht leer. Er macht die sonst nur aus der
Schlussposition erschlossene Rückbindung an H ausdrücklich. Ein bloßes
gesprochenes „und“ ergibt dagegen „X und Y und Schluss“, was möglich, aber
weniger zweckmäßig ist.

### Die vier gleichen `L/O–CLOSE`-Fälle

```text
f81v.17  chedy – L/O – CLOSE
f81v.18  cheky – L/O – CLOSE
f81v.24  okeey – L/O – CLOSE
f83r.26  qoky  – L/O – CLOSE
```

Jedes Mal ist der linke Block sichtbar. Der rechte Endpunkt wird als H
ergänzt: „diesen Block noch unter dem geltenden Bezug buchen; dann commit“.
Der zusätzliche f83r.37-Fall `L/O–anderes CLOSE` erbt links den vorherigen
aktiven Eintrag und rechts H; er ist eine extrem kurze vollständige Buchung.

### Das Ein-Karten-Feld f81v.7

Die ganze Zeile endet:

```text
olor – L/O – sheckhal daiin qokeedal daiin chckhy schedy | L/O
```

Der letzte Strich kopiert nicht einen unbekannten Gegenstand, sondern den
eben eingerichteten **Beziehungsrahmen**. Das ist der stärkste Einzelbeleg für
Vererbungsnotation: Medium, Partitiv und gewöhnliche Präposition benötigen
hier ein lautloses Komplement; die Ditto-Regel benötigt nur den ohnehin
aktiven Registerzustand.

## Vorwärtskodierung und Rückleseproben

Vorwärts, als Werkstattanweisung:

> Setze die L/O-Karte zwischen zwei zu verbindende Buchungsblöcke. Ist der
> linke Block schon durch die vorige Zelle gegeben, setze L/O zuerst. Soll der
> rechte Block erst in der nächsten Zeile kommen, setze L/O zuletzt. Vor dem
> Schlusszeichen bedeutet L/O „noch unter dem geltenden Bezug“. Soll die
> ganze Zuordnung unverändert weitergelten, schreibe L/O allein. Rendere die
> Karte nach dem lizenzierten Zell-/Zeilenstencil.

Rückwärts, f83r Record 3, drei aufeinanderfolgende reale Zeilen:

```text
f83r.47  otchdy | qokchdy | shedal
f83r.48  dal – L/O – lol chdal aiin
f83r.49  L/O – daiiin chedy
```

Quellklasse:

```text
mehrere kurze gesetzte Zellen;
buche den DAL-Block zusammen mit dem LOL…AIIN-Block;
führe denselben Bezug beim DAIIN…-Block fort.
```

Rückwärts, f83r Record 4 über die Zeilenkante:

```text
f83r.52  solkeey qekey raly – L/O
f83r.54  daiin – L/O – dain chey ldalor
```

Quellklasse:

```text
halte den ersten Block zur Zuordnung offen;
verbinde ihn mit DAIIN und führe DAIIN im gleichen Rahmen
mit dem folgenden Block weiter; Record schließen.
```

Diese Rücklesungen benennen bewusst keine Kräuter, Körperteile, Mengen oder
Handlungen. Sie sind dennoch kontinuierlicher als `UNKNOWN`, weil sie die
Abhängigkeiten der Blöcke festlegen.

## Herbal/Biological-Transfer

Auf f10r steht L/O ausschließlich medial und zweimal als wiederholter
Zuordnungsstrich. Das passt zu langen offenen Herbal-Blöcken, in denen beide
Seiten gewöhnlich ausgeschrieben werden. Auf f81v/f83r kommen zusätzlich
kurze geschlossene Zellen, Feldanfang, Feldende und das Einzelkarten-Ditto vor.
Das erfordert keine zweite Bedeutung: Der Biological-Stencil lässt mehr
Argumente durch den aktiven Record und seine Commit-Struktur weg.

Eine plausible inhaltliche Expansion wäre im Herbal „Teil/Substanz **mit**
Eintrag“ und im Biological „Station/Anwendung **mit bzw. unter** Konfiguration“.
Diese Substantive sind nicht identifiziert. Übertragbar ist nur die
Registerhandlung **gemeinsam unter einem aktiven Bezug buchen**.

## Vergleich der Modelle

| Modell | 19 Belege | Ein-Karten-Feld | Kanten/Schluss | Gesamturteil |
|---|---:|---:|---:|---|
| mitgeführter Beziehungsstrich: WITH/UNDER SAME REFERENCE | 19/19 | natürliches Ditto | eine Vererbungsregel | **führend, 92/100** |
| reines Argument-Slot-Zeichen ohne Quellparaphrase | 19/19 | natürlich | sehr gut | 86/100; formal fast gleich gut, aber weniger Rückleseleistung |
| AND/ALSO-Koordinator | 19/19 mit Ellipse | „desgleichen“ möglich | final und vor CLOSE gezwungen | **stärkster Rivale, 78/100** |
| OF/FROM/BELONGING TO | 19/19 mit Vererbung | möglich | Richtung an Kanten unbekannt | 69/100 |
| IN/WITHIN/MEDIUM | 19/19 nur mit starker Ellipse | sehr unnatürlich | vor CLOSE und final schwach | 61/100 |
| Teil/Anteil/Partitiv | 19/19 nur abstrakt | sehr unnatürlich | keine Zahl-/Ganzes-Evidenz | 56/100 |
| gewöhnliches häufiges Formelwort | formal möglich | möglich | erklärt Renderer, Carry und Kette nicht | 63/100 |

Der reine Slot-Rivale ist formal eng verwandt und bleibt wichtig. Er verliert
nur, weil V13 eine konkrete Gesamtlesung verlangt: „unter demselben Bezug
buchen“ erzeugt brauchbare, registergerechte Rücktexte, ohne eine engere
Sachbedeutung zu erfinden. AND/ALSO ist der stärkste wirklich andere Rivale,
weil es alle wiederholten medialen Folgen flüssig macht. Es erklärt jedoch
`X–L/O–CLOSE`, das alleinige L/O und das feldfinale L/O nur durch jeweils neue
Ellipsen- oder Catchword-Annahmen.

## Scheitern und feste Vorhersagen

Das Modell scheitert oder muss ersetzt werden, wenn innerhalb der zehn Seiten
einer der folgenden Fälle gezeigt wird:

1. Feld-/Zeilenanfang setzt den aktiven Bezug zwingend zurück; dann können die
   drei FIRST-, der ONLY- und der LAST-Beleg keine Endpunkte erben.
2. Das einzelne `qol` auf f81v.7 besitzt nachweislich einen eigenen
   obligatorischen Payload und ist kein Fortsetzungs-/Ditto-Feld.
3. Die vier gleichen CLOSE-Karten verlangen stets die unmittelbar vorherige
   Karte als vollständigen Sachwert; dann wäre L/O dort Wert statt Relation.
4. Die wiederholten Folgen benötigen verschiedene, unvereinbare Relationen
   auf den zwei Strichen; eine exakte Karte könnte sie nicht ausführen.
5. Ein einheitliches AND/ALSO-Modell erzeugt ohne zusätzliche Sonderregeln
   bessere kontinuierliche Rücklesungen aller Kantenfälle.

Nur auf den bereits festen Seiten sagt das Modell voraus:

- feldinitiales L/O muss lokal auf einen noch aktiven committed Block oder
  Recordbezug folgen;
- feldfinales L/O muss den nächsten nutzbaren Block als rechten Endpunkt
  zulassen, bei f83r.52 konkret das folgende `daiin` von f83r.54;
- alleinstehendes L/O sollte in einer Fortsetzungsumgebung stehen, wie auf
  f81v.7 unmittelbar nach einem bereits realisierten L/O-Rahmen;
- `A–L/O–B–L/O–C` sollte als Kette oder als zwei Buchungen unter demselben
  lokalen Kopf lesbar bleiben, nicht als drei voneinander unabhängige Werte;
- Rendererwechsel dürfen die zugrunde liegende Carry-/Beziehungsfunktion
  nicht ändern.

## Schluss

Für die explorative Zehn-Seiten-Decodierung sollte die V6-Lesung nicht
zurückgenommen, sondern präzisiert werden:

```text
L/O ~= WITH / ENTER UNDER THE SAME ACTIVE REFERENCE

operation:
  LINK(left_or_inherited, right_or_inherited, active_record)
```

Das Wort „associated“ allein war zu weich. Die neue Fassung sagt einem
Schreiber, **was er speichern, wann er erben und wie er weiterkopieren muss**.
Sie deckt alle 19 Vorkommen mit einer Regel, macht f81v.7 zum Ditto-Fall und
erklärt die Schlussnähe als Rückbindung an den aktiven Record. AND/ALSO bleibt
ein ernsthafter Rivale, aber nicht die führende Werkstattregel.

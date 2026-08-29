# GDT630 method

## Question

Welche sichtbaren Stoff- oder Pflanzenteilköpfe binden an die 15 fusionierten
und 120 getrennten `BASE+d+aN`-Ausdrücke? Ist Fusion eine ganze Stoffklausel
oder nur eine variable Schreibung der inneren Qualitäts-/Wertphrase? Kann
dieselbe kompositionelle Lesung konkrete Klauseln in beiden Oberflächen-
reihenfolgen erzeugen?

## Inputs

Der Lauf benutzt die geerbte 179-Seiten-Allowlist aus GDT628. f1r ist
ausgeschlossen; f84 und f84r werden vor Materialisierung verboten. Token- und
Kreuztranskription werden ausschließlich mit `vmanus-exp query-tsv`, expliziten
Seiten-Allowwerten und projizierten Spalten gelesen. Es wird keine neue Seite
und kein Bild geöffnet.

GDT628 liefert das 54-Zellen-OL/OR-Gitter, die registrierten Schreibwege und
die getrennten OL-/OR-Phrasen. GDT629 liefert V6 und die ersten `chol`-
Grenzbrücken. Bekannte Partköpfe kommen aus der GDT625-`cth`-Familie und den
geerbten `dair/sair`-Rollen sowie aus GDT623/GDT629. Die historischen
Syntaxvergleiche werden aus GDT627 übernommen. ZL3b, IT2a und RF1b bleiben
alternative Lesungen desselben Manuskripts.

## Method

1. Materialisiere alle ZL3b-Ausdrücke `BASE+d+aN` und `BASE | d+aN`, wobei
   `BASE` exakt eine der 54 registrierten OL/OR-Zellen und N einer der Werte
   I–IV ist.
2. Teile jeden Ausdruck in drei semantische Klassen:

   ```text
   QUALITY_CORE+ol   kernhaltige Qualitätsphrase
   ol                nackter Qualitäts-/Materialträger, Kern offen
   ...or             Teil-/Nominalträger, Qualität offen
   ```

3. Erfasse drei Tokens links und rechts, ohne daraus automatisch eine Bindung
   zu machen. Eine konkrete Part–Qualität–Grad-Klausel entsteht nur bei einem
   unmittelbar benachbarten, bereits zugelassenen Partkopf und einem
   kernhaltigen OL-Ausdruck. Kontakte in Distanz zwei oder drei bleiben
   `NEAR ... BINDING OPEN`.
4. Prüfe in jeder Leserfassung, ob dieselbe Basis-/Wertzelle fusioniert,
   getrennt, mit einer anderen Grenze oder gar nicht erscheint. „Grenz-
   normalisiert stabil“ verlangt in allen drei Lesungen dieselbe zusammen-
   hängende Zeichenfolge; es setzt die Leser nicht als unabhängige Belege an.
5. Vergleiche für jede der sechs tatsächlich fusionierten Basis-/Wertzellen
   alle getrennten Gegenstücke, ihre unmittelbaren Außentokens und Partanker.
6. Gib Part-vor-Qualität und Qualität-vor-Part getrennt aus. In flüssigem
   Deutsch wird der Partname zuerst genannt; die sichtbare Reihenfolge bleibt
   im Artefakt erhalten.
7. Bewahre für getrennte `dN`-Formen die Dosislesung und für beide Ordnungen
   die Alternative „zwei benachbarte technische Zellen“. Kein unbekannter
   Nachbar bekommt ein Ersatzverb oder ein generisches Stoffwort.
8. Merge alle 32 V6-Einträge unverändert und ergänze sechs Klausel-/Rahmen-
   einträge zu V7.

## Decision rule and claim ceiling

Das primäre Arbeitsmodell lautet:

```text
PART | OL_QUALITY | d+a+N
OL_QUALITY | d+a+N | PART
OL_QUALITY+d+a+N | PART
```

Die sichtbaren Zellen ergeben in allen drei Formen „Part: Qualität, Grad N“.
Die beidseitige Reihenfolge kann Nominalsyntax, eine vorangestellte Rubrik oder
eine lokale Tabellen-/Zellpaarung sein; GDT630 entscheidet diese drei
historischen Realisierungen noch nicht. Getrennte Werte behalten einen
Portionsrivalen. Nacktes `ol+dN` und OR+dN bleiben Grad/Menge/Klasse offen.

Fusion wird nur für die sechs beobachteten Basis-/Wertzellen beansprucht. Da
14/15 fusionierte Belege Wert III und nur einer Wert II tragen, ist sie keine
frei erfundene I–IV-Regel. Der Lauf identifiziert keine Sprache, Aussprache,
absolute Einheit oder ganze Zeilenübersetzung.

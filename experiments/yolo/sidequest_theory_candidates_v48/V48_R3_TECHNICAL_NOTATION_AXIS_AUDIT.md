# V48 R3 — technischer Register- und Notationsaudit

## Ergebnis

Ich habe alle 145 in V47 opaken exakten Karten (121 PAGE_HOST-Typen)
geprüft, ohne einen eingefrorenen V47-Wert zu verändern. Unter einer
technischen Registerlesung ist nur **eine** zusätzliche Achse gerade noch
vertretbar:

```text
LCHED = NACHGEORDNETE STATION/WEITERFÜHRUNG
```

Sie deckt drei exakte Karten ab:

```text
lched     HOST LCHED=NACHGEORDNETE STATION/WEITERFÜHRUNG
lchedal   HOST LCHED=NACHGEORDNETE STATION/WEITERFÜHRUNG
          + RIGHT AL=ZIEL-/PARALLELPLATZ
lchedar   HOST LCHED=NACHGEORDNETE STATION/WEITERFÜHRUNG
          + RIGHT AR=QUELLEN-/LOKALRELATION
```

Der Minimalwert bleibt in allen drei Karten identisch. Er bezeichnet weder
Wasser noch Becken. Solche konkrete Wörter bleiben ausschließlich in der
lokalen kreativen Expansion. Die Achse ist nur provisorisch: Sie hat drei
Ereignisse auf zwei Bio-Seiten und ist damit keine starke Sprachbehauptung.

## Warum die attraktiven Scheinfamilien nicht aufgenommen wurden

### CH, CHE und EE

Sechs exakte Karten und elf Ereignisse sehen zunächst wie wiederkehrende
Operationsstämme aus. Ihr gemeinsames Verhalten ist aber bereits vollständig
durch `DY` erklärt: jede Karte ist eine DY-geschlossene Operation; der jeweilige
Host fügt keine unabhängig belegte Invariante hinzu. Eine neue Bedeutung wäre
doppelte Buchführung.

### D, ED, K, OLK und YK

Diese fünf Hosts umfassen 13 exakte Karten und 17 Ereignisse. Sie erscheinen
vor allem als Träger verschiedener RIGHT-Kompletierungen. Das belegt
RIGHT-Valenz, aber keine gemeinsame Inhaltsachse. `OLK` kann insbesondere nicht
„Tuch“ oder „Becken“ heißen: genau diese zwei lokalen Lesungen widersprechen
einem gemeinsamen Objektwert.

### CHY

Die zwei Karten unterscheiden sich bereits durch `FRAME OT` gegen `INNER-D`.
„Warmes Medium“ stammt nur aus den lokalen kreativen Übersetzungen. Es ist kein
unabhängiger formaler Befund.

### Y

Y ist mit 30 Ereignissen häufig, aber seine drei exakten Karten verteilen sich
auf eine nackte, eine `INNER-D`- und eine `FRAME O`-Konstruktion. Die lokalen
Lesungen reichen von Arbeitsposten bis Standortbeschreibung. Häufigkeit ist
hier kein gemeinsamer Wert.

### CHEY und CHOR

Ihre lokalen Lesungen wirken semantisch ähnlich, doch gerade diese
Pflanzen-/Materialdeutung durfte in diesem Audit keine Achse definieren. Ohne
die lokale Übersetzung bleibt nur eine kleine Frame-Alternation. Beide bleiben
unbekannt.

## Kompressionsbilanz

```text
V47 gemeinsame Achsen:              19 exakte Karten
V48 R3 neue provisorische Achse:      3 exakte Karten
V48 R3 insgesamt regelgelesen:       22 exakte Karten
wiederkehrende unteilbare Ganzkarten: 9 exakte Karten
weiterhin opak:                     142 exakte Karten
```

Die Bilanz ist absichtlich klein. Eine Achse wie „RIGHT-valenter Träger“ oder
„vor DY stehender Träger“ ist eine nützliche formale Klasse, aber noch keine
zusätzliche rücklesbare Einheit, wenn RIGHT beziehungsweise DY bereits separat
in der Komposition stehen.

## Dateien

- `V48_R3_CANDIDATE_AXIS_AUDIT.tsv` prüft alle 121 opaken Hosttypen und damit
  sämtliche 145 opaken V47-Karten.
- `V48_R3_COMPLETE_173_CARD_DICTIONARY.tsv` enthält das vollständige
  Kartenwörterbuch.
- `V48_R3_COMPLETE_381_EVENT_INTERLINEAR.tsv` enthält alle Prosavorkommen.
- `V48_R3_COMPLETE_135_FIELD_TRANSLATION.tsv` enthält alle Felder.
- `V48_R3_VALIDATION.json` prüft Umfang, Unverändertheit und die besonders
  gefährdeten Hosts `CH/CHY/CHE/OLK/Y`.

Dies ist eine kreative Werkstattnotation, keine Entzifferung. `f84` und `f84r`
wurden nicht geöffnet.

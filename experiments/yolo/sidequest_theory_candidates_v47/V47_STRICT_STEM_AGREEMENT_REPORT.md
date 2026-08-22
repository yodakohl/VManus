# V47 — Übersetzungsrunde mit strikt übereinstimmenden Stämmen

## Was diesmal anders ist

Das Komponentenlexikon wurde **vor** der neuen Übersetzung geschlossen. Keine
lokale deutsche Übersetzung darf einen Stamm nachträglich umdefinieren.

Es gibt nur drei zulässige Fälle:

1. ein eingefrorener gemeinsamer Hostwert;
2. eine wiederkehrende, aber unteilbare Ganzkarte;
3. ein unbekannter Host mit ausschließlich lokalem Kartenwert.

## Eingefrorene gemeinsame Hostwerte

```text
OK = spezifizierten Arbeitsposten einsetzen/aktivieren
OR = bereitetes Ergebnis oder Arbeitsmedium
AL = Ziel- oder Parallelstation
E  = bis zur Zustandsgrenze führen
OT = markierten Bezug oder Weg wählen
L  = angeschlossene Station oder Fortsetzung
```

Diese sechs Werte erscheinen im gesamten Wörterbuch wortgleich. `OR` bleibt
der einzige vorläufige Inhaltskern; die übrigen fünf sind formale oder
relationale Achsen.

## Eingefrorene Kompletierungen

```text
RIGHT-AIIN = Standard-/Parameterplatz
RIGHT-AIN  = begrenzte Einheit oder Passage
RIGHT-AL   = Ziel-/Parallelplatz
RIGHT-AR   = Quellen-/Lokalrelation
RIGHT-AIR  = Fluss-/Laufweg
FRAME-O    = Kontext/Voransatz fortsetzen
FRAME-OT   = markierten Sekundärbezug setzen
INNER-D    = gelernte Operations-/Zustandsvariante
DY         = lokalen Arbeitsschritt schließen
B3         = besonderen Zellschluss setzen
```

Diese Werte gelten überall gleich. PAGE_HOST `ain` wird dadurch nicht mit der
Kompletierung RIGHT-AIN gleichgesetzt; beide sind verschiedene formale Ebenen.

## Wiederkehrende Ganzkarten

`AIIN`, `EY`, `OKY`, `LCHE`, `OKE`, `CTHY`, `OKEEY`, `CKHY` und `OLOR`
behalten konkrete Arbeitslabels. Sie heißen ausdrücklich nicht „produktive
Wortstämme“, weil im festen Panel jeweils nur eine exakte Kartenart existiert.

## Unbekannt bleibt unbekannt

`CH`, `CHY`, `CHE`, `OLK` und `Y` erhalten auf Hostebene durchgehend
`UNBEKANNT`. Ihre lokale kreative Kartenübersetzung darf weiter lesbar sein,
trägt aber nichts zum gemeinsamen Stammlexikon bei.

Dasselbe gilt für alle sonstigen nicht eingefrorenen Hosts.

## Beispiel der strikten Komposition

```text
qokaiin
  HOST OK    = ARBEITSPOSTEN AKTIVIEREN
  RIGHT AIIN = STANDARD-/PARAMETERPLATZ
  lokal      = beginne/aktiviere den nächsten quantifizierten Posten

qotal
  HOST OT    = MARKIERTEN BEZUG ODER WEG WÄHLEN
  RIGHT AL   = ZIEL-/PARALLELPLATZ
  lokal      = zum markierten unteren Ablauf führen

shey / cheey
  GANZKARTE EY = SOLLZUSTANDSKARTE
  lokal        = bis zum verlangten sichtbaren Endzustand
```

Kein Bestandteil darf in einer anderen Karte plötzlich „Wasser“, „Wurzel“,
„warm“ oder „klar“ heißen. Solche Wörter gehören ausschließlich zur lokalen
kreativen Expansion.

## Vollständigkeit

- `V47_STRICT_173_CARD_DICTIONARY.tsv`: vollständiges Kartenwörterbuch;
- `V47_STRICT_381_EVENT_INTERLINEAR.tsv`: jedes Prosavorkommen;
- `V47_STRICT_135_FIELD_TRANSLATION.tsv`: alle Felder als strikte und flüssige
  Parallelfassung;
- `V47_VALIDATION.json`: maschineller Gleichheitstest der Host- und
  RIGHT-Werte.

Die flüssige Zehnseitenübersetzung bleibt vollständig, aber nur die streng
eingefrorenen Komponenten dürfen als wiederkehrende Teile gelesen werden.
Dies ist weiterhin eine kreative Werkstatttheorie, keine Entzifferung. `f84`
und `f84r` blieben versiegelt.

# Pass 1023 — Generalisierungscheck über alle 4.345 Anschlüsse

## Kurze Antwort

Ja. Die wörtliche Vollregel

```text
nicht-L/AIR schließt links; L/AIR rahmt rechts
```

erzeugt außerhalb der 120 Gleichstände **vier klare Widersprüche**. Die
Gleichstandsentscheidung selbst bleibt gut; falsch ist nur ihre Ausdehnung auf
jede ungleiche Mehrkopfstellung.

| Urteil der strengen Vollregel | Fokusvorkommen |
|---|---:|
| passt zur vorhandenen Kartenbindung | 2.859 |
| beide Seiten haben denselben Kopfwert; Position nicht aus der Spur trennbar | 28 |
| klare Gegenbindung | 4 |
| verlangte Seite hat keinen örtlichen Kopf; Stapelrückfall nötig | 1.454 |
| **gesamt** | **4.345** |

## Die vier Gegenfälle

| Anschluss | Karte | strenge Linkslesung | vorhandene Bindung |
|---|---|---|---|
| `SA00090` | `SH+O+Y+T+Y` | `Y→SH=HALTEN` | `Y→T=EINSTELLEN` |
| `SA00557` | `OK+O+E+S` | `E→OK=SETZEN` | `E→S=WÄHLEN` |
| `SA00563` | `S+OR+AIIN+R` | `AIIN→S=WÄHLEN` | `AIIN→R=MARKIEREN` |
| `SA00636` | `CH+O+E+R` | `E→CH=NEHMEN` | `E→R=MARKIEREN` |

In allen vier Karten ist der rechte Kopf ein Atom näher als der linke. Das
Ausführungszeichen `O` oder der schon geschlossene erste Zusatz verlängert den
Abstand zum linken Kopf, ohne selbst einen neuen Kopf zu bilden.

Der schärfste Kontrast steht bereits in wiederkehrenden Kartenformen:

```text
CH + E + O + R  →  E schließt an CH an       (links 1, rechts 2)
CH + O + E + R  →  E schließt an R an        (links 2, rechts 1)
```

Ebenso zeigt eine einzige Karte beide Richtungen:

```text
S + OR + AIIN + R
    OR   → S
         AIIN → R
```

Damit ist Abstand bei Argumenten und Graden nicht bloß dekorativ.

## Alle Zwei-Kopf-Stellen

Insgesamt besitzen 191 Fokusvorkommen einen Handlungskopf auf beiden Seiten:

- 120 haben den bereits bearbeiteten Gleichabstand;
- 71 haben ungleichen Abstand.

Die 71 ungleichen Fälle teilen sich vollständig:

- 56 Argument-/Gradstellen haben links den näheren Kopf und binden links;
- 5 Argument-/Gradstellen haben rechts den näheren Kopf und binden rechts;
- 3 `AL/AR`-Stellen behalten trotz näherem rechten Kopf ihre feste linke
  Beziehungsseite;
- 7 `L`-Stellen nehmen den näheren rechten Kopf.

Von den fünf rechten Argument-/Gradstellen sind die vier oben genannten
Bindungen klar unterscheidbar. In der fünften tragen beide Seiten
`T=EINSTELLEN`; die Atomposition bleibt in der ausgeschriebenen Wertspur offen.

## `L/AIR`-Gegenprobe

Für die Vorwärtsrahmen entsteht kein klarer Widerspruch:

- 123 Stellen besitzen einen rechten Kartenkopf: 122× `L`, 1× `AIR`; alle
  123 binden an dessen Wert.
- Acht dieser Stellen besitzen zugleich einen linken Kopf. Eine ist
  gleichweit, sieben haben den rechten Kopf näher; alle acht gehen rechts.
- 60 Stellen haben keinen rechten, aber einen linken Kopf. Sie benutzen diesen
  als örtlichen Rückfall: 46× `L`, 14× `AIR`.
- 93 Stellen haben gar keinen örtlichen Kopf und benötigen den vorhandenen
  Besitzer-/Gang-/Erbstapel.

Es gibt allerdings keine Karte, in der `L/AIR` einen vorhandenen, aber weiter
entfernten rechten Kopf gegen einen näheren linken wählen müsste. Der
Rechtsrahmen ist daher widerspruchsfrei, aber diese stärkste Entfernungslage
kommt im Bestand nicht vor.

## Kleinste haltbare Generalisierung

Die 120er-Regel braucht nur eine begrenzte Präzisierung:

```text
1. Pass-1021-Pakete zuerst öffnen.

2. Y / AIIN / AIN / OR und E / EE / EEE:
   den nächsten örtlichen Handlungskopf nehmen;
   nur bei genauem Gleichstand links schließen.

3. AL / AR:
   am linken Kopf bleiben — zuerst örtlich, dann am bereits offenen Stapelkopf;
   nur wenn links nichts offen ist, den einzigen rechten Kopf nehmen.

4. L / AIR:
   den rechten Kopf rahmen;
   fehlt er, den laufenden linken Kopf als örtlichen Rückfall benutzen.

5. Fehlt jeder örtliche Kopf:
   Besitzer-, Gang-, Vorwärts- und Erbstapel aus Pass 1022 benutzen.
```

Diese Fassung trifft alle **3.100** Fokusvorkommen mit mindestens einem
örtlichen Handlungskopf beziehungsweise einem bei `AL/AR` bereits offenen
linken Kopf. Die übrigen 1.245 Karten besitzen überhaupt keinen örtlichen Kopf
und sind deshalb kein Test der Seiten-/Abstandsregel.

## Was unverändert bleibt

- Alle 120 Gleichstände behalten ihre Entscheidung: Argumente, Grade und
  `AL/AR` links; der eine `L`-Fall rechts.
- Kein Wurzelwert wird verschoben.
- Mehrkopfkarten bleiben verschachtelt.
- Die Pass-1021-Doppelregel wird vor jeder Nachbarschaftsbindung geöffnet.
- 28 Gleichwertfälle bleiben als Positionsvorbehalt sichtbar und werden nicht
  zu Gegenbelegen umetikettiert.

`EQUAL_DISTANCE_GENERALIZATION_AUDIT.tsv` enthält jede der 4.345 Stellen mit
beiden örtlichen Köpfen, Abständen, vorhandener Bindung, Urteil der strengen
Regel und Ergebnis der kleinen Reparatur.

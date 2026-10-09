# Ein zurücklesbares Schreibsystem mit bestandenem Grundtest

Der feste Prototyp schreibt 1.054 Rezepttexte mit zusammen 80.931 Wörtern und liest sie vollständig zurück. Er besteht die vereinbarten zehn statistischen Grundbedingungen sowie die verschärfte Bedingung für benachbarte, sehr ähnliche Wörter. Geprüft wurden vier Quellbestände gegen drei bereits bekannte Voynich-Transkriptionen. Die Tabellen wurden an diesen bekannten Daten angepasst.

**Das ist keine Voynich-Übersetzung.** Beim genaueren Wortbau bestehen deutliche Abweichungen: beispielsweise folgt in den Voynich-Zusammenfassungen auf q zu rund98% ein o, im Prototyp nur zu26–30%. Außerdem benötigt der Entwurf eine Tabelle mit2.130 Einträgen. Der Grundtest allein ist also kein ausreichendes Auswahlkriterium für eine historische Rekonstruktion.

Die Regel ist überschaubar: Man zerlegt ein bekanntes Quellwort anhand einer Tabelle in möglichst lange Stücke. Jedes Stück bekommt seinen festen Code; dessen Anfang hängt zusätzlich von einem kleinen Zähler ab. Das Ende zeigt, ob das Quellwort fertig ist. Der Leser arbeitet dieselben Regeln rückwärts ab.

Ein Beispiel aus **unserer eigenen Kodierung**:

```text
cphoeeel iaaoeey qeoech deeoach roooaeal keoeeach qaeech yaeeol
```

Es ergibt den bekannten Quelltext:

```text
des ersten von hecht pratten dv solt nemen
```

Die Gruppen sehen durch die verwendeten Arbeitszeichen ähnlich aus; sie stammen nicht aus dem Voynich-Manuskript. Daraus darf keine Bedeutung eines echten Voynichwortes abgeleitet werden.

- [Vollständiger Bericht und Grenzen](REPORT.md)
- [Regeln zum Lesen von Hand](artifacts/MANUAL_RULES.md)
- [Rückwärtstabelle](artifacts/MANUAL_INVERSE.tsv)
- [Blind vorgelegte Leseprobe](artifacts/MANUAL_CHALLENGE.md) und [vollständige erfolgreiche Rücklesung](artifacts/MANUAL_READER.md)
- [Alle festgelegten statistischen Prüfungen](artifacts/SCREEN.tsv)
- [Ausführbare Prüfung und Ergebnisse](artifacts/VALIDATION.json)

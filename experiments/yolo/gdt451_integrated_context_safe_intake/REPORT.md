# GDT451 — Der schnelle Leser kann den sicheren Leser nicht mehr überstimmen

## Ergebnis

Der integrierte Aufnahmebefehl ist fertig. Für jede bereits sichtbare
Komponentenfolge zeigt er gleichzeitig:

- ob die exakte Folge schon bekannt ist;
- wie sie sich in den bisher beobachteten Nachbarkontexten verhielt;
- was der konkrete aktuelle Kontext erlaubt;
- die endgültige Entscheidung.

Die letzte Zeile stammt immer aus dem Live-Kontext. Der Code enthält keinen
Override durch Identität oder historischen Erfolg.

## Vollständiger Gegenlauf

| Prüfung | Ergebnis |
|---|---:|
| bestehender Strom | 4.576/4.576 identisch |
| davon grün | 4.566 |
| davon gelb | 10 |
| synthetische Kontextproben | 61.878/61.878 identisch |
| darin lokale Stopps | 5.911 |
| Stopps mit erhaltenem Zustand | 5.911/5.911 |
| bekannte Falschfreigaben | 8/8 jetzt `STOP` |
| Validator | 35/35 `PASS` |

Die 18.381 Zielrezepte werden als Suchprior gespeichert. Davon sind zehn
wirklich kontextabhängig. Bei ihnen sagt der Befehl ausdrücklich
`HISTORY_CONTEXT_DEPENDENT__LIVE_DECIDES`.

## Die entscheidenden Angriffe

```text
D_ADDR+EEE+Y nach CHD  -> STOP FOCUS:CHD<-EEE
E+DY ohne Handlungskopf -> STOP CLOSE:NO_ACTIVE_ACTION
E+DY mit geerbtem CH     -> lesbar
```

Genau daran scheiterte ein bloßer Zielprior: dieselbe sichtbare Folge kann je
nach geerbtem Zustand lesbar sein oder stoppen. GDT451 behält deshalb die
schnelle Vorwarnung, entscheidet aber niemals daraus.

## Was uns das praktisch bringt

Beim späteren Öffnen weiterer Seiten müssen wir nicht mehr zwischen zwei
Werkzeugen wählen. Wir geben sichtbare Komponenten und den lokalen Zustand in
einen Befehl. Bekanntheit wird angezeigt, echte lokale Unmöglichkeit bleibt
rot, und ein Stopp verändert den laufenden Zustand nicht.

Das ist eine Sicherheits- und Durchsatzverbesserung. Es bestätigt kein Wort,
keine Oberfläche und kein zukünftiges Auftreten.

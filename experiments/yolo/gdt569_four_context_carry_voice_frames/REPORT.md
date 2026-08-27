# GDT569 — vier Kontextlagen erklären 1.442 scheinbar unvollständige Zeilen

Status:
`PASS_4_CONTEXT_MODES__693_ACTION_CARRIES__1208_ARGUMENT_CARRIES__1348_PRIOR_ARGUMENT_REALIZATIONS__1442_STATE_CLAUSES_CONTEXT_EXPLICIT__19_CARRIED_ARGUMENT_CELLS__ZERO_ROOT_CHANGE`

## Der konkrete Fund

Nach der Substantiv-, Relations- und Verbvereinheitlichung bleibt kein diffuser
Sprachrest. Zwei einfache Fragen reichen für jede der1.656 Zustandskarten:

1. Ist die aktive Handlung auf dieser Karte geschrieben oder aus dem Kontext
   übernommen?
2. Ist das aktive Argument hier geschrieben oder aus dem Kontext übernommen?

Die Antworten ergeben exakt vier Lagen:

| Kontextlage | Karten | neue Lesestimme |
|---|---:|---|
| Handlung lokal, Argument lokal | 214 | unveränderte GDT568-Zeile |
| Handlung lokal, Argument getragen | 749 | `denselben/dieselbe …` |
| Handlung getragen, Argument lokal | 234 | `im laufenden Gang …` |
| Handlung und Argument getragen | 459 | beide kleinen Marker |

Damit sind1.442 Karten nicht semantisch komplizierter als die übrigen214. Sie
benutzen nur einen oder zwei bereits aktive Satzslots. Das ist genau der
Mechanismus, der lange Fantasiebedeutungen unnötig macht.

## Das Argument wird natürlich statt technisch markiert

Die alten ownergebundenen Kontrollzeilen schreiben auf1.208/1.208 passenden
Karten `[wie zuvor]`. GDT569 spricht denselben Sachverhalt als normales
deutsches Argument aus:

```text
Weiter: halte den Kennwert fest.
→ Weiter: halte denselben Kennwert fest.

Setze den Stationswert im Stationsgang an; auf Grad II; schließe den Schritt.
→ Setze denselben Stationswert im Stationsgang an; auf Grad II;
  schließe den Schritt.
```

Alle19 tatsächlich vorhandenen Register×Argument-Zellen werden gebraucht:
laufender Eintrag, Pflanzenposten, Positionswert, Stationsanteil,
Ansatzeinheit und ihre Geschwister. `Y`, `AIIN`, `AIN` und `OR` behalten ihre
kurzen Werte; nur der deutsche Artikel zeigt den Vorbezug.

Insgesamt entstehen1.348 solche Argumentrealisierungen. Die Kontrollausgabe
hat1.354 `[wie zuvor]`-Marker. Die Differenz von sechs ist vollständig erklärt:
Sechs Karten schreiben eine Handlung zweimal; die alte Ausgabe wiederholt den
ganzen Satzteil, während die knappe Ausgabe weiterhin `zweimal` sagt.

```text
alt/lang: Entnimm den Stationsanteil [wie zuvor], entnimm ... [wie zuvor] …
neu/kurz: Entnimm denselben Stationsanteil zweimal …
```

## Die getragene Handlung braucht nur drei Satzrahmen

693 Karten übernehmen eine Handlung:544 aus einer früheren sichtbaren Karte
derselben Aussage und149 aus dem ownergebundenen Anfangsdefault. Ihre komplette
GDT562-Quellspur bleibt erhalten. Drei Oberflächenrahmen genügen:

| Rahmen | Karten | Beispiel |
|---|---:|---|
| Weiter | 339 | `Weiter im laufenden Gang: halte …` |
| Danach | 316 | `Danach im laufenden Gang: wähle …` |
| ohne OT/OL-Präfix | 38 | `Im laufenden Gang: … schließe den Schritt` |

Jede der693 Kontrollzeilen besitzt bereits einen entsprechenden
Gang-/Satz-/Fortsetzungs- oder Abschlusszeiger. Die neue Ausgabe vereinheitlicht
diese alten Stile auf eine einzige praktische Bezeichnung.

Beide Träger zusammen lesen sich nun beispielsweise so:

```text
Danach: wähle den laufenden Eintrag; auf Grad I; zur Ausführung …
→ Danach im laufenden Gang: wähle denselben laufenden Eintrag;
  auf Grad I; zur Ausführung …
```

## Was das für die Arbeitstheorie bedeutet

Die gegenwärtige Kompositionssprache hat jetzt eine sehr konkrete Form:

```text
19 kurze Wurzelwerte
+ ownergebundene Nomen/Relationen/Verbrahmen
+ zwei lebende Satzslots: aktive Handlung, aktives Argument
+ OT/OL/DY als Weiter-/Danach-/Abschlusssteuerung
```

Eine kurze Karte wie `OL` muss daher niemals „halte denselben Pflanzenanteil im
laufenden Arbeitsgang“ als Ganzwort bedeuten. `OL` liefert FORTSETZEN; Handlung,
Argument und Register liefern den Rest. Das ist bislang die sparsamste
vollständige Erklärung für die langen deutschen Arbeitszeilen.

Die neue Ausgabe verändert1.442 Zustandszeilen,711 Aussagen und alle28
laufenden Seiten. Die214 vollständig lokalen Zustandszeilen und alle3.466
Nichtzustandszeilen bleiben bytegleich. Alle5.122 Ereignisse,793 Aussagen und30
zugelassenen Seiten bleiben in derselben Reihenfolge. Alle51 Prüfungen bestehen.

## Nächster Arbeitsweg

Der größte verbleibende Unterschied sitzt jetzt in kleinen
Modifikatorfügungen—etwa `zur Ausführung` gegen `als Ausführung`, gestufte
Konjunktionen und die seltenen umgekehrten OT/OL-Rahmen. Als Nächstes werden
diese Reste nach geschriebenem Modifikatortyp und Reihenfolge auf wenige
Fügekarten reduziert. Keine neue Seite und keine Wurzelumdeutung ist nötig.

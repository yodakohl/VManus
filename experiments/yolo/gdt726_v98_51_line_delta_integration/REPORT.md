# GDT726 — vollständiger V98/V98R1-Reader

Status: PASS_V98_51_LINE_DELTA_INTEGRATION__479_POSITIONS_CONSUMED_ONCE__474_EXACT_UNITS__V98R1_471_PRACTICAL_UNITS__357_CONTEXT_DELTAS__9_NEW_LOCAL_RENDER_PATCHES_PLUS_1_INHERITED_COMPANION__6_OPEN_MEANING_DEBTS__ZERO_CORE_SCORE_EXPORT_DELTA__ALL_H0_NONE

## Ergebnis

Der aktuelle Arbeitsbestand ist jetzt wirklich als vollständiger Reader
materialisiert: **51 Zeilen auf 36 bereits verwendeten Seiten, 479
Tokenpositionen, keine Lücke und keine Doppelverwendung**. V98 unterscheidet
sich an 357 Positionen von V57; 122 Positionen bleiben gleich. Diese Deltas
liegen in 50 der 51 Zeilen. Die sieben V56→V57-Änderungen sind vollständig
enthalten.

Der Exaktkanal ergibt 474 Einheiten: 468 direkte Kontextausgaben, fünf
einmalige Span-Ausgaben und ein geerbter Companion. Der praktische Kanal
ergibt 471 Einheiten: 456 direkte Kontexte, acht einmalige Spans, sechs neue
Positionsformulierungen und derselbe Companion. Beide Kanäle konsumieren
alle 479 Positionen genau einmal.

## Was praktisch besser wurde

Neun lokale Reparaturen verändern acht Zeilen:

| Locus | vorheriger Bruch | V98R1-Ausgabe |
|---|---|---|
| f104v.2 | `davon: Wert III` | `davon drei Maße` |
| f83v.12 | `drei · feuchte Mischung, Anfangsstufe` | `drei Portionen der feuchten Mischung auf Anfangsstufe` |
| f116r.12 | zwei nackte `zwei` | `davon zwei Portionen`; `zwei Portionen des Materials I im kalten Anfangsansatz` |
| f8r.15 | `drei · Materialmaß` | `drei Materialmaße` |
| f105r.31 | nacktes `eingeweicht` | `vorstehendes Holz, eingeweicht` |
| f107r.2 | generischer Kopf `Behandlung` | `anschließend bis zur letzten Stufe weiterführen und abschließen` |
| f115r.23 | drei Verben ohne sichtbaren Patienten | `diese leicht getrocknete Zubereitung erhitzen, trocknen und ansetzen` |
| f86v6.25 | überladene Wiederholung des heißen Blütenkopfs | `von der vorstehenden fertigen Blütenmasse: Anteil I, davon ein Maß` |

Auf f116r.12 bleibt `heißer Ansatz, Grad II` ausdrücklich als eigene Einheit
stehen. Die Mengenbindung hat dort keine Gradinformation verschluckt.

## Was nicht als Reparatur ausgegeben wird

Sechs offene Punkte würden die behauptete Bedeutung ändern und bleiben daher
im Reader sichtbar:

| Schuld | Positionen | offene Entscheidung |
|---|---:|---|
| `kodeey` | P025 | Zubereitungsdosis oder fertige Portion |
| `cpheesy` | P030 | Arzneikompositum oder neutrales Kompositum |
| `tail` | P053 | Rohdroge II oder Material II |
| Dosisfamilie | 6 | Dosis, Portion, Maß oder bloßer Wert je lokalem Kopf |
| Zeilenanfang `hiervon` | 4 | echter Rückbezug über die Recordgrenze oder offener Anschluss |
| dreifaches `sheky` | 3 | wiederholter Prozess, drei Patienten oder Scope-Wiederholung |

Das ist die entscheidende Trennung: Ein hässlicher Satz darf geglättet werden;
eine unsichere Stoff-, Einheiten- oder Handlungsbedeutung darf nicht als bloße
Stilkorrektur verschwinden.

## Sonderregeln

Die fünf geerbten Spanregeln werden in beiden Kanälen je einmal ausgeführt.
Die drei neuen Mengenbindungen kommen nur im praktischen Kanal vor. Die zwei
f7r.2-Direktivzeilen beschreiben weiterhin genau einen `keo r`-Span; die acht
sichtbaren f7r.2-Einheiten sind in beiden Kanälen unverändert. Der
f76v.10-Companion gibt weiterhin einmal `drei Portionen des vorstehenden
eingeweichten Arzneikompositums` aus, während der Wörterbuchkern von
`daiin#6` `Wert III`, sein Kontext `drei` und sein Score 42 bleiben.

## Kontrolle

Der unabhängige Validator importiert `run.py` nicht. Er liest dieselben
Primärtabellen und Spezifikationen, baut beide Editionen erneut und vergleicht
zeilenweise:

- 10 TSV-Artefakte mit insgesamt 2.082 Datenzeilen,
- den kompletten 51-Zeilen-Markdownreader,
- alle 479 Positionskonsumtionen in beiden Kanälen,
- die acht eingefrorenen f7r.2-Einheiten,
- das vollständige `RESULT.json`.

Alle Prüfungen bestehen. Es gibt null Wörterbuchkern-, Kontext-, Score- oder
Komponentenexportänderungen und null Treffer der alten generischen
`Arbeitsgut`/`Arbeitsschritt`-Sprache.

## Bedeutung des Ergebnisses

GDT726 ist noch keine flüssige historische Übersetzung. Es ist aber auch
nicht mehr nur eine lose Wörterbuchsammlung: Zu jeder der 479 Stellen ist nun
sichtbar, welche konkrete V98-Lesung eingeht, welche Stellen gemeinsam eine
Phrase bilden und welcher deutsche Text tatsächlich ausgegeben wird. Der
praktische Reader kann dadurch genau dort kritisiert werden, wo noch eine
echte Bedeutungsentscheidung fehlt.

Es wurden keine neue Seite, kein Bild und keine Transkription geöffnet; weder
f84 noch f84r wurde verwendet. Alle historischen Felder bleiben `H0_NONE`.

## Nächste Route

Nicht weiter global glätten. Als Nächstes werden die sechs offenen
Bedeutungsgruppen gegen alle bereits vorhandenen V98-Fundstellen und ihre
unmittelbaren Stoff-, Mengen- und Aktionsköpfe ausgespielt. Das Ziel ist eine
konkrete Defaultentscheidung je Gruppe oder ein klar benannter lokaler
Dispatch — danach wird derselbe 51-Zeilen-Reader erneut gebaut, sodass jede
Entscheidung sofort in echten Passagen sichtbar wird.

Der Duplikatscreen verweist vor allem auf GDT683s abgeschlossene OL-Schuld,
GDT704s einzelne materialgebundene Wiederholung, GDT694s Anteil-Terminologie
und GDT593s occurrence-lokale Mengenreferenzen. Keiner dieser Läufe entscheidet
die sechs V98-Gruppen. Übernommen wird nur ihr brauchbares Muster: lokale
geschriebene Köpfe schlagen ferne oder generische Ergänzungen; neue
Bedeutungen werden nicht aus dem Renderer zurück in Teilstrings exportiert.

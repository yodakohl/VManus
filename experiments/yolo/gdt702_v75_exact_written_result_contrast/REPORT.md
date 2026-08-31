# GDT702 — ein geschriebenes Ergebnis unmittelbar rechts der Aktion

Status: `PASS_V75_11_TARGET_RIGHT_CONTEXTS__7_NOMINAL_3_ACTION_1_EOS__1_EXACT_WRITTEN_RESULT__2X2_DEFAULTS_REJECTED__C012_OCCURRENCE_BOUND__ZERO_WORD_DELTA`

## Ergebnis

Für jede der elf GDT701-Zielaktionen wurde genau der erste semantische Eintrag
nach der vollständigen Aktionsklausel geprüft. Rechts folgen sieben
Nominalblöcke, drei weitere Aktionsklauseln und einmal das Zeilenende. Nur ein
Fall vereint ohne semantischen Zwischeneintrag einen geschriebenen
Materialkopf, Materialübereinstimmung und einen in GDT687 exakt als `HIGH`
typisierten Fertigzustand:

```text
f105v.1
#3 olpcheey  trocken gebundenes Holzpulver, Form II
       └── C001 ──> #4 ykaiin  hiervon auf Stufe III erhitzen
                         └── C012, B_WORKING_LOCAL ──>
                             #5 olpchedy  fertiges Holzextraktpulver
```

Die konkrete Werkstattlektüre lautet:

> Das trocken gebundene Holzpulver, Form II, auf Stufe III erhitzen.
>
> Geschriebenes Ergebnis: fertiges Holzextraktpulver.

C012 verbindet ausschließlich `ykaiin#4` mit `olpchedy#5`. Die späteren
Nominaleinträge #6 und #7 gehören nicht zur Kante; `ypcheddy#8` erhält weder
#5 noch das Heizresultat als zugelassenen Teilnehmer. Aus dem Wort
*Holzextraktpulver* wird insbesondere keine zusätzliche Operation
„extrahieren“ abgeleitet.

## Warum die übrigen zehn Zielaktionen keine Ergebniskante erhalten

- Zwei unmittelbare Rechteinträge sind nur zustandsartig und tragen keinen
  Materialkopf (`kain` nach C003 und C008).
- Vier sind Materialregister ohne exakt geschriebenen Resultatstatus; bei C005
  widerspricht der Holz-Kopf zudem dem zugegebenen Arzneikompositum.
- Nach C004, C007 und C011 beginnt jeweils eine neue Aktion. Das freie `dy#7`
  bei C011 bleibt dabei ausschließlich struktureller Klauselstopp.
- C002 endet an der Zeilengrenze.

Spätere resultatähnliche Wörter innerhalb eines rechten Nominalblocks wurden
nicht selektiv vorgezogen. Der erste semantische Eintrag ist die feste Grenze.

## Zwei Kreuzkontraste und drei verworfene Defaults

Der 2×2-Kontrast sperrt zwei naheliegende Kurzschlüsse: Das zweite `ykaiin`
bei `f86v6.25#5` wird unmittelbar nur von *Drogenportion* gefolgt, nicht von
einem exakt typisierten Ergebnis. Das zweite `olpchedy` bei `f105v.14#4`
folgt zwar ebenfalls einer Aktion, dort aber dem Nehmen eines heißen
Drogenanteils III ohne den passenden Holzpulverrahmen.

Damit sind drei Defaults verworfen:

1. **Aktionsoberflächen-Default:** `ykaiin` erzeugt nicht allgemein
   `olpchedy`.
2. **Ergebnisoberflächen-/Nachbarschafts-Default:** `olpchedy` ist nicht nach
   jeder unmittelbar vorausgehenden Aktion deren Ergebnis.
3. **Block-Skip-Default:** Ein späteres resultatähnliches Wort darf den ersten
   rechten semantischen Eintrag nicht überspringen.

## Zirkularität und Claim-Grenze

Die Materialübereinstimmung beruht auf dem bereits eingefrorenen deutschen
Arbeitsrenderer. GDT682 hatte dieselbe Stelle schon proseartig als Ergebnis
gelesen, und GDT687 hatte `olpchedy#5` bereits als nominalen Fertigzustand
klassifiziert. GDT702 entdeckt daher weder die Bedeutung noch ein unabhängiges
historisches Ergebniswort; es formalisiert diese vorhandene Werkstattlektüre
erstmals als occurrence-genaue, gegen alle elf Zielaktionen abgegrenzte
Relation.

Der Graph wächst von 11 auf 12 Kanten und von 23 auf 24 eindeutige Knoten. Die
neue Kante erweitert die bestehende Komponente M002, daher bleiben es neun
Komponenten; die Renderpositionen steigen von 26 auf 27. Wortbedeutungen,
Seiten und die eingefrorenen 479 Token-/51 Zeilen-/3 Span-Inhalte ändern sich
nicht. C012 ist eine lokale B-tier-Arbeitshypothese, keine portable
Aktions-Ausgabe-Regel und kein extern bestätigtes Plaintextresultat.

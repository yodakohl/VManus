# Pass 1024 — Zehn Seiten als neue Lehrlingsblätter

## Ergebnis

Pass 1023 enthält insgesamt 4.345 Fokusanschlüsse. Die zehn verlangten
Herbal-/Pharma-Seiten tragen davon **1.249**; nur diese 1.249 sind Prüfzeilen.
Die übrigen Pass-1023-Zeilen dienen ausschließlich als Unterrichtsnachweis von
anderen Seiten. Bei jeder Prüfung ist die gerade geprüfte Seite aus ihrem
eigenen Regelbeleg entfernt.

Neun Seiten lassen sich vollständig mit feinen Regeltypen erklären, die auf
mindestens einer anderen Seite vorkommen. **f18r besitzt genau einen
seitenprivaten Untergriff:**

```text
P + D_ADDR + R + AIR + DY
→ P[ HIER; R[LAUF] ]; SCHLUSS
```

Der allgemeine Griff `R_POSITIONAL_MARKING` ist auf vielen anderen Seiten
bekannt. Die genaue Unterform `R_POSITIONAL_NESTED` — ein inneres `R` zwischen
äußerem Kopf und eigenem Rechtsglied — erscheint jedoch nur hier. Unter der
strengen Forderung „der Regeltyp selbst muss fremdseitig vorkommen“ besteht
f18r deshalb nicht vollständig. Als Anwendung des bereits gelernten
allgemeinen R-Griffs bleibt die Karte mechanisch lesbar, aber das wäre eine
Extrapolation und kein echter Fremdseitenbeleg.

## Seitenübersicht

| Seite | Reg. | Anschlüsse | örtlich | Stapel | vorwärts | Besitzer | in P1023 entschieden / geändert | Fremdseiten-Replay |
|---|---|---:|---:|---:|---:|---:|---:|---|
| f10r | Herbal | 82 | 50 | 32 | 0 | 0 | 1 / 0 | vollständig |
| f11r | Herbal | 54 | 33 | 21 | 0 | 0 | 1 / 0 | vollständig |
| f13r | Herbal | 68 | 48 | 20 | 0 | 0 | 1 / 0 | vollständig |
| f17r | Herbal | 62 | 48 | 12 | 2 | 0 | 5 / 2 | vollständig |
| f18r | Herbal | 70 | 43 | 24 | 2 | 1 | 5 / 2 | ein privater R-Untergriff |
| f55v | Herbal | 120 | 81 | 36 | 3 | 0 | 7 / 3 | vollständig |
| f56r | Herbal | 94 | 68 | 25 | 1 | 0 | 6 / 1 | vollständig |
| f88r | Pharma | 151 | 118 | 33 | 0 | 0 | 6 / 0 | vollständig |
| f88v | Pharma | 176 | 133 | 37 | 4 | 2 | 9 / 5 | vollständig |
| f89r | Pharma | 372 | 255 | 105 | 2 | 10 | 17 / 5 | vollständig |
| **gesamt** |  | **1.249** | **877** | **345** | **14** | **13** | **58 / 18** | **1.248 streng fremdgestützt** |

Die 18 gegenüber Pass 1022 geänderten Anschlüsse sind genau 14 begrenzte
Vorgriffe und vier `R`-Schwanzkorrekturen. Keine Änderung braucht einen neuen
Kernwert.

## Herbal getrennt

Die sieben Pflanzenseiten liefern 550 Anschlüsse:

- 371 werden innerhalb der eigenen Karte gebunden;
- 170 benutzen vorige oder ältere offene Köpfe;
- acht greifen genau eine Karte voraus;
- ein `AR` bleibt beim sichtbaren Besitzer;
- 26 ehemalige Alternativen werden in Pass 1023 ausgewählt, acht davon ändern
  den alten Default.

Sechs der sieben Seiten bestehen den strengen Fremdseitentest vollständig.
f18r verliert nur den einen inneren R-Untergriff. Das f13r-Paket
`OK+OR+OR+Y` ist zwar als OR-Außen/Innen-Kombination seitenprivat, aber nicht
als Regel: Paketabstieg und Doppelöffnung kommen auf anderen Seiten an den
CH-Doppelpaketen vor. Ein Lehrling darf also die gelernte Doppelregel anwenden,
ohne für f13r etwas Neues zu erfinden.

Verlangt man zusätzlich einen Beleg aus einer **anderen Herbal-Seite**, werden
drei sonst tragfähige Griffe dünner:

- f17r: der einseitige `L/AIR`-Vorgriff ist nur aus anderen Registern bekannt;
- f18r: `AR/AL` am Besitzer ist in Herbal sonst nicht belegt; der R-Innengriff
  bleibt auch registerübergreifend privat;
- f55v: der `Q`-Paketvorgriff ist in Herbal sonst nicht belegt.

f10r, f11r, f13r und f56r lassen sich sogar ausschließlich aus anderen
Herbal-Seiten unterrichten.

## Pharma getrennt

Die drei Pharmaseiten liefern 699 Anschlüsse:

- 506 sind örtliche Kartenbindungen;
- 175 benutzen den Stapel;
- sechs greifen begrenzt voraus;
- zwölf bleiben am Besitzer;
- 32 ehemalige Alternativen werden entschieden, zehn davon ändern den alten
  Default.

Alle drei Pharmaseiten bestehen den normalen Fremdseitentest. Unter der
strengeren Forderung „nur eine andere Pharmaseite darf lehren“ bleiben zwei
Abhängigkeiten:

- f88v braucht für `OT` als Geschwister-Vorgriff ein Beispiel aus einem
  anderen Register;
- f89r braucht für nacktes `AR/AL` am Besitzer ein Beispiel aus einem anderen
  Register.

f88r kann vollständig aus f88v/f89r beziehungsweise anderen Pharmaseiten
gespielt werden.

## Direkte Regeln und Stapelfälle

Die 877 örtlichen Anschlüsse brauchen nur die bereits bekannten Familien:

- nächster Handlungskopf, bei Gleichstand links;
- `AL/AR` links;
- `L/AIR` rechts oder mangels rechten Kopfes auf den laufenden linken Kopf;
- `R` als Kopf beziehungsweise innerer Kopf nach seiner Stellung.

Die 345 Stapelfälle teilen sich in unmittelbare vorige Karte, älteren offenen
Kopf und die vier R-Schwanzfälle. Die 13 Besitzerfälle sind neun bereits klare
Besitzerrückfälle plus vier in Pass 1023 ausdrücklich entschiedene
`AR/AL`-Adressen. Die 14 Vorgriffe bleiben auf genau eine Karte und den
vorhandenen Besitzerrahmen beschränkt.

## Was wirklich seitenprivat ist

Auf der groben Strukturebene erscheinen 15 Anschlusszeilen in 14 Kombinationen
nur auf ihrer eigenen Seite. Dreizehn dieser Kombinationen setzen jedoch
fremdseitig belegte Regeln lediglich neu zusammen. Beispiele:

- f13r: äußere und innere OR-EINHEIT im bekannten Doppelpaket;
- f55v: ein geerbter Kopf mit `EEE=GRAD III`;
- f88r/f89r: freie doppelte Posten oder Ziele mit bereits bekannten
  Wiederholungs- und Stapelgriffen;
- f88v: `AR` bleibt links, obwohl der rechte Kopf näher steht.

Nur `R_POSITIONAL_NESTED` auf f18r ist ein wirklich seitenprivater feiner
Regeltyp.

Auf der Ebene ganzer Kartenformen sind 309 Anschlusszeilen beziehungsweise
300 Form-Fokus-Kombinationen seitenprivat. Das ist kein Problem für den
Lehrling: neue gelernte Ganzkarten waren ausdrücklich erlaubt, solange ihre
Kerne mit vorhandenen Regeln geöffnet werden. Exakte Formneuheit darf daher
nicht mit einer neuen Klammerregel verwechselt werden.

## Schluss

Die Herbal-/Pharma-Werkstatt ist fast vollständig fremdseitig lehrbar:

```text
1.248 / 1.249 Anschlüsse besitzen ihren feinen Regeltyp auf einer anderen Seite.
1.249 / 1.249 besitzen wenigstens ihren allgemeinen Elternregeltyp anderswo.
```

Die ehrliche Reststelle ist f18r `P+D_ADDR+R+AIR+DY`. Sie verlangt keine neue
Bedeutung, ist aber der einzige Fall, dessen genaue innere R-Stellung ohne die
eigene Seite nicht demonstriert werden kann.

## Dateien

- `HERBAL_PHARMA_REPLAY_ATTACHMENTS.tsv` — alle 1.249 Prüfanschlüsse mit
  Fremdseiten-Unterrichtsnachweis
- `HERBAL_PHARMA_REPLAY_PAGE_SUMMARY.tsv` — zehn Seiten einzeln
- `HERBAL_PHARMA_REPLAY_PRIVATE_PATTERNS.tsv` — 14 private
  Strukturkombinationen
- `HERBAL_PHARMA_REPLAY_SUMMARY.json` — kompakte Gesamtzählung
- `HERBAL_PHARMA_REPLAY_BUILD.py` — vollständiger Neubau

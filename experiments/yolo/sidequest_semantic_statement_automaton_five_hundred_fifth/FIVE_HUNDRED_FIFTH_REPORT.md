# Pass 505 — eine Fünf-Zustands-Ablaufmaschine

Die 72 verschiedenen Satzprogramme müssen nicht einzeln gelernt werden. Ihre
470 Handlungstoken lassen sich mit fünf Zuständen schreiben:

1. `START`: noch keine Handlung;
2. `WORK`: ein laufender Arbeitsgang;
3. `AFTER_SOURCE`: etwas wurde aus einer Quelle genommen;
4. `AFTER_METER`: Maß oder Stufe wurde gesetzt;
5. `CLOSED`: die Zelle ist abgeschlossen.

Von `START` setzt der Schreiber eines der sieben Arbeitsprimitive. Danach darf
er weitere Arbeitsprimitive anschließen oder die Zelle schließen. `CLOSE` ist
immer endgültig. Eine offene Aussage darf dagegen in jedem Arbeitszustand
enden und in der nächsten physischen Zeile weiterlaufen.

## Die drei kleinen Sperren

Von 56 möglichen Primitivpaaren kommen 53 tatsächlich vor. Nur drei fehlen:

- `SOURCE_DRAW → MOVE_PASS`;
- `SOURCE_DRAW → TARGET_HANDOFF`;
- `METER_CHECK → CLOSE`.

Als einfache Lehrregel heißt das: Nach einer Entnahme wird der Posten erst
angesetzt, geprüft, gehalten oder fortgeführt, bevor er weiterbewegt oder
übergeben wird. Nach dem Messen folgt noch eine Ausführung, nicht sofort der
Schluss.

Diese Fünf-Zustands-Maschine akzeptiert alle 116 Aussagen. Sie ersetzt keine
Kartenbedeutung und errät keinen Bildgegenstand; sie ordnet lediglich die
bereits gewählten acht Werkstatthandlungen.

## Häufige Bio-Wege

Die neun Programme aus Pass 504 bleiben bevorzugte, leicht zu kopierende
Pfade. Zusammen decken sie 53 Bio-Aussagen. Besonders gewöhnlich sind:

- halten oder Zustand setzen, dann schließen: 21;
- bewegen oder durchlassen, dann schließen: 14;
- ansetzen oder beschicken, dann schließen: 4.

Damit braucht ein Lehrling eine allgemeine Ablaufregel plus neun häufige
Schablonen. Die 63 nur einmal beobachteten Programme sind keine 63 neuen
Wörter oder Formkarten mehr.

Als Nächstes wird geprüft, ob Herbal und Biological dieselbe Maschine nur mit
verschiedenen Start- und Schlussgewohnheiten verwenden. Das würde die mehreren
Schreiber und Register mit einer gemeinsamen, leicht lernbaren Werkstattregel
erklären.

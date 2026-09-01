# GDT725 method

## Frage

Welche konkrete Defaultfunktion ist für jede der letzten sechzehn
LOW_STRUCTURAL_OR_MANUAL_HARDCAP-Lesarten am nützlichsten, wenn 21 tatsächliche
Fundstellen, die ursprünglichen Ganzwortkarten und die lokalen Nachbarn
gleichzeitig sichtbar bleiben?

## Eingaben

- V97 mit 324 aktiven Lesarten, 479 Positionsausgaben, 35 Auditzeilen und dem
  vollständigen 1.586-Zeilen-Wörterbuch aus GDT724.
- Die tatsächlich verantwortlichen Kartenzeilen aus GDT675, GDT677, GDT678,
  GDT680 und GDT681.
- GDT687s sieben exakte Positionsentscheidungen für nacktes `y` und freies
  `dy`.
- GDT686s exakte lokale Mengenbindung für `daiin#6` auf f76v.10.
- Drei feste Spezifikationen: sechzehn Wörterbuchentscheidungen, 21 lokale
  Fundstellenrenderer und eine reine Companion-Zeilenausgabe.

## Methode

1. Die 16 Reading-IDs werden unabhängig von ihrer Oberflächenidentität
   behandelt. Insbesondere bleiben `y#1/y#2` und `dy#1/dy#2` getrennt.
2. Bei `y`, `dy` und `yey` werden strukturelle Funktion und sichtbare Ausgabe
   getrennt: etwa `[STRUKTUR: SATZSCHLUSS]` als Wörterbuchdefault und `.` als
   Renderer. Das ist keine behauptete gesprochene Übersetzung.
3. Ein konkretes Aktionsganzwort bleibt konkret, wenn seine Ursprungskarte die
   Aktion selbst trägt. Das gilt für `aiijy`, `da`, `qy` und `ypchesy`;
   keinerlei Verbwert wird auf Teilstrings exportiert.
4. Bei nominalen Ganzwörtern wird nur ein ersetzbarer lokaler Kopf entfernt:
   Arznei aus `cpheesy`, Zubereitung aus `kodeey`, Ansatz aus `otytchol` und
   Rohdroge aus `tail`. Die exakte Fundstelle darf den Kopf weiterhin flüssig
   ausgeben.
5. Drei Rivalen pro Lesart bleiben offen. Scores, Confidence-Level,
   Komponentenexport und historischer Status werden nicht angehoben.
6. Alle 324 aktiven Lesarten, 479 Kontexte und 1.586 Wörterbuchzeilen werden
   neu gebaut; die fünf gebundenen Spans und Sonderrenderer bleiben als Karten
   bytegleich.
7. In den 18 Zielzeilen werden vorhandene gebundene Spans wirklich als eine
   Ausgabe konsumiert. B001 und B002 werden so je einmal ausgegeben. Zusätzlich
   stellt eine an GDT686 gebundene, score-neutrale Companion-Regel auf f76v.10
   den lokalen Mengen- und Stoffkopf wieder her, ohne `daiin#6 = Wert III` zu
   ändern.

## Entscheidungsregel und Grenze

Der gewählte Default muss konkreter sein als ein bloßer Rollenname, darf aber
nicht mehr Identität oder Handlung tragen als die exakte Ganzwortkarte. Ein
Strukturzeichen erhält eine benannte Strukturfunktion statt einer erfundenen
gesprochenen Bedeutung. Eine bereits minimale, praktisch brauchbare
Ganzwortlesung wird nicht aus bloßer Vorsicht entleert.

V98 ist eine explorative deutsche Arbeitslesung. Sie identifiziert weder
Klartext noch Sprache, Lautung, historisches Codebuch, konkrete Zutat,
Krankheit, Patient oder Heilmittel. Es wurden keine neue Seite, kein Bild,
keine neue Transkription und weder f84 noch f84r geöffnet.

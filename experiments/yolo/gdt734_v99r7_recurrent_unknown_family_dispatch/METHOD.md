# GDT734 — Methode

## Frage und feste Basis

Kann der vollständige GDT733-Cache durch bereits lizenzierte aktive
Ganzwortwerte und eine kleine, einzeln redigierte Tranche wiederkehrender
Restformen konkreter werden, ohne exakte Kontexte, gebundene Spans, Scores,
Evidenz oder Exportrechte still umzuschreiben?

Die kanonische Basis besteht aus GDT733s 32.339-Zellen-Register und
4.128-Zeilen-Reader sowie dem vollständigen 1.586-Lesarten-Wörterbuch aus
GDT730. GDT637 und GDT678 liefern eng begrenzte Familienkontrollen; die
Blockerregeln stammen unverändert aus GDT731. Alle Eingaben werden durch das
Manifest und die Paritätstabelle gebunden.

## Pass 1 — technischer Ganzwort-Exportfix

Der erste Pass sucht aktive Lesarten mit bedingungsloser
Ganzwort-Exportlizenz, deren identische Oberflächen in GDT733 dennoch als
unbekannt stehen. Ursache ist der alte Projektionsfilter, der nur
`GLOBAL_V48_DEFAULT`, nicht aber `ACTIVE_WORKING_DEFAULT` einsammelte.

71 Oberflächen werden an 305 Positionen repariert. `dchey` und `olkar` bleiben
wegen ihres Kontext- beziehungsweise Span-Scope ausgeschlossen. Für 28
exportierbare Ganzwörter prüft ein redaktionelles Deck die gesprochene Fassung;
26 werden gekürzt oder von occurrence-lokalen Patienten bereinigt. Semantischer
Kern, Score, Confidence, Evidenz und Scope bleiben dabei unverändert.

## Pass 2 — 20 explorative exakte Ganzwörter

Aus dem wiederkehrenden Restbestand werden nur vorab aufgeführte Formen mit
genau einer graphemischen Zweiteilung unter den derzeit konkreten
V99R4-Lesarten bearbeitet. Diese Eindeutigkeit ist Navigation, kein
semantischer Beleg. Jede Form erhält eine manuelle Entscheidung:

- 9 `PROMOTE_COMPOSITIONAL_WHOLE`: beide Teilkarten liefern nichtredundante,
  scope-kompatible Rollen;
- 5 `REVISE_ROLE_CONSTRAINED_WHOLE`: nur ein nominaler oder enger Rollenwert
  ist sicher genug;
- 6 `LEARNED_WHOLE_NO_COMPOSITIONAL_CREDIT`: der Split ist redundant oder
  semantisch unbrauchbar; nur das exakte Ganzwort läuft.

Kein Kandidat exportiert seine Komponenten. Imperative sind nur erlaubt, wenn
die gewählte Ganzwortkomposition bereits eine Aktionskarte und einen
passenden Patienten bindet; sonst bleibt die Fassung nominal.

## Scoreformeln

Der Score ist ein interner Auditindex, keine Wahrscheinlichkeit und keine
historische Bestätigung. Ausgangspunkt ist der schwächere Teilscore. Die
Wiederholung liefert höchstens zwölf Punkte, zwei Punkte je abgeschlossener
Verdopplung der Vorkommenszahl:

```text
bonus = min(12, 2 * floor(log2(occurrences)))
COMPOSITIONAL = min(59, min(part scores) + bonus)
ROLE_CONSTRAINED = min(39, max(20, min(part scores) + bonus - 5))
LEARNED_WHOLE = min(35, max(20, min(part scores) + bonus - 10))
```

Ein eindeutiger Split selbst gibt null Punkte. Alle 20 neuen Lesarten bleiben
W1 oder W2.

## Präzedenz und praktische Einheiten

Die Ausgabe folgt strikt dieser Reihenfolge:

1. exakte positionsgebundene V99-Kontexte;
2. bestehende gebundene Render-once-Spans und Strukturinterpunktion;
3. der lizenzierte aktive Ganzwortfix aus Pass 1;
4. der exakte Kandidat aus Pass 2;
5. unveränderte GDT733-Zelle.

Höhere Ebenen dürfen durch eine gleich geschriebene globale Oberfläche nicht
überschrieben werden. Die 32.319 praktischen Einheiten, acht aktuellen
Bound-Spans, acht Legacy-Merges und vier Interpunktionsanhänge werden
positionsgenau weitergeführt.

## Rollenmatrix und historische Vergleiche

Die 19 beobachteten Vollformen werden als Kreuzmatrix von `cth`, `p`, `s` und
vorsichtig `olk` mit `-ol`, `-or`, `-aiin`, `-ain`, `-ar`, `-dy` beschrieben.
Innerhalb der Arbeitstheorie sind die tragfähigen Rollen Material, Portion,
Index III/II und Anteil I. Das legt weder eine Einheit noch Menge, Grad oder
Charge fest. `olkol` widerspricht einem universellen `-ol`, `olk` bleibt ein
gebundener Kopf und `-dy` wird nicht portiert.

Pal. lat. 1256, Wellcome MS 542/683/MS 5262 und ein ausdrücklich sekundärer
Nomenklatorüberblick zeigen nur, dass gelernte Drogennamen, Fachkürzel,
Qualitäts-/Dosisfelder und Restnamen historisch gemeinsam vorkommen können.
Jeder Vergleich trägt `relation_credit=0`, `voynich_sign_value_credit=0` und
`H0_NONE`. Clm 667 wird korrekt auf 1481–1490 datiert und ist später als die
Zielzeit.

## Validierung und Claim ceiling

Der unabhängige Validator darf `run.py` nicht importieren. Er rekonstruiert
Schlüssel, Zählungen und Deltas aus den gebundenen Eingaben, prüft die
71/305- und 20/226-Populationen, die 9/5/6-Entscheidungen, Scoreformeln,
Wörterbuchvollständigkeit, Nichtzielparität, Span-/Unit-Erhalt, historische
Nullkredite, 179 erlaubte Seiten und den Ausschluss von `f84/f84r`.

GDT734 ist ein explorativer Wörterbuch- und Cache-Renderer. Es identifiziert
keinen Klartext, keine Sprache, Phonetik, Spezies, Krankheit, Heilung,
historische Einheit oder freien Voynich-Komponentenwert.

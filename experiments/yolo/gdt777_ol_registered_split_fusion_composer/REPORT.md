# GDT777 — registrierte Ganz- und Splitfelder nach `ol`

Status: `PASS__23_REGISTERED_SPANS__14_FALLBACKS_REPLACED__9_CONTEXTUAL_SHARPENED__163_CONTEXTUAL__NO_COMPONENT_EXPORT`.

## Ergebnis

Die feste Oberflächenregel findet **23** reader-exakte Spannen: **16**
`ol + Ganzform`-Vorkommen und **7** `ol + Kopf + body`-Vorkommen. Sie
repräsentieren **17** registrierte fusionierte H-Formen. Vierzehn bisherige
Fallbacks erhalten einen kurzen Feldwert; neun schon kontextuelle Ausgaben
werden geschärft. Damit steigt die kontextuelle Abdeckung des unveränderten
376er `ol`-Bestands von **149 auf 163**, und **120** rechte Token werden im
Gesamtrenderer kollisionsfrei genau einmal konsumiert.

Die Vorabschätzung enthielt `ol s al`. Das `al`-Token ist in der bewachten
Lesung nicht reader-exakt und wird von derselben Regel ausgeschlossen. Ebenso
bleiben fünf nicht-exakte rechte Ganzformen und ein nicht-exaktes `s aiin`
draußen. Der globale Negativkontrollwert ist deutlich: `sal` hat 33 exakte
fusionierte Vorkommen, `s al` aber null exakte unter fünf rohen Paaren. Es gibt
keine handverlesene Occurrence-ID-Liste.

## Konkrete Arbeitswerte

Die neue Ausgabe benutzt kurze gebundene Felder wie `Binnenfeld: heißer Anteil
I`, `Binnenfeld: Trockenansatz`, `Bezugsfeld: Wert III`, `Eintragsfeld:
Trockenresultat I` und `Bezugsfeld: Feuchtresultat II`. `s aiin` erhält an
seinen vier exakten `ol`-Positionen den GDT759-Wert `Menge: drei Drachmen`;
`drei gleiche Teile` und `drei Unzen` bleiben als Rivalen sichtbar. Keine
Karte macht `p`, `s`, `r` oder `l` zu einem Wort oder einer Abkürzung.

## Split gegen Fusion im bewachten Cache

- `r aiin` / `raiin`: split=6, fused=45, Register-Cosinus=0.913, Klasse `DISTINCT_SURFACE_CONSTRUCTIONS__REGISTERED_BODY_SHARED`.
- `r ain` / `rain`: split=4, fused=14, Register-Cosinus=0.479, Klasse `DISTINCT_SURFACE_CONSTRUCTIONS__REGISTERED_BODY_SHARED`.
- `s aiin` / `saiin`: split=23, fused=89, Register-Cosinus=0.807, Klasse `ALTERNATE_READER_BOUNDARY_EQUIVALENT__FIELD_BODY_SHARED`.
- `s chey` / `schey`: split=1, fused=4, Register-Cosinus=1.000, Klasse `DISTINCT_SURFACE_CONSTRUCTIONS__REGISTERED_BODY_SHARED`.

Nur `s aiin` / `saiin` besitzt die vier normalisierten
Alternate-Reader-Grenzbrücken aus GDT759. Die anderen Splitformen teilen hier
nur einen registrierten Inhalts-body mit der fusionierten Ganzform; sie werden
nicht als identische Schreibung oder als austauschbares Lexem behauptet.

## Vier Passage-Patches

- `f55v.10`: `oaiin ol s aiin okaiin oky ytaiin otar y kal ykar ol`
  → oaiin ⟦Menge: drei Drachmen⟧ okaiin oky ytaiin otar y kal ykar ol

- `f105r.15`: `lksheey ol r aiin okeedy olkeeody lkaiin okeeol oteeol shod daiin aral`
  → lksheey ⟦Bezugsfeld: Wert III⟧ okeedy olkeeody lkaiin okeeol oteeol shod daiin aral

- `f108v.25`: `sheeol okeey kaiin okaiin ol lchey ctheo r aiin cheey qokeey qokeeaiin al`
  → sheeol okeey kaiin okaiin ⟦Binnenfeld: trockene Form I⟧ ctheo r aiin cheey qokeey qokeeaiin al

- `f82r.31`: `cheol ol rsheedy lchedy qoty lcheeor qokain cheedy lched`
  → cheol ⟦Bezugsfeld: Feuchtresultat II⟧ lchedy qoty lcheeor qokain cheedy lched

Doppelklammern markieren ersetzbare exakte Feldwerte; unmarkiertes EVA bleibt
ungelöst. Die Zeilen sind keine Klartextübersetzungen.

## Grenze

Das GDT388-Paket enthält **23** deskriptive Transkriptionsrelationen. Der
Intake lautet `VALID_ACQUISITION_NOT_SCORE_READY`; alle Kanten bleiben
`INELIGIBLE_EXPLORATORY_TEXT_RELATION`. Es wurden keine neuen Seiten, Bilder,
OCR, Transkriptionen, `f84`- oder `f84r`-Daten geöffnet.

# GDT770-Präregistrierung — targetmaskiertes Valenzturnier

Datum der Festlegung: 2026-09-03
Status vor Ausführung: `REGISTERED_UNSCORED`

## Festes Ziel

In fünfzehn bereits zugelassenen vollständigen Reader-Zeilen werden die
bisherigen Rollen und deutschen Defaults von `ol`, `ckhy`, `ols` und `otar`
verdeckt. Getestet wird, welche der in
`src/CANDIDATE_POLICY_SPECS.tsv` festgeschriebenen Ganzwort-Policies direkte,
target-unabhängige Strukturwaisen beseitigt. Es gibt keinen Fluency- oder
Übersetzungsscore.

## Vor der Wertung eingefroren

- Kohorte: exakt `src/COHORT_15_LINE_SPECS.tsv`, ohne Nachsuche oder Austausch
  einer Zeile.
- Targets: exakt `ol|ckhy|ols|otar`; alle exakten Gleichheiten einer Zeile
  werden gleichzeitig maskiert. Die feste Kohorte enthält 17 reader-exakte
  Zielstellen (`ol=5`, `ckhy=4`, `ols=3`, `otar=5`); `pcheey` ist kein Target.
- Kandidaten: 18 Kandidaten-IDs und 22 feste Zweigzeilen in
  `src/CANDIDATE_POLICY_SPECS.tsv`.
- Strukturquelle: ausschließlich die reader-exakten Rollen der unmittelbaren
  linken und rechten Nicht-Target-Nachbarn. Targetrollen, alte Targetdefaults,
  Targetevidenz und Targetkonfidenz erhalten null Kredit.
- Drei schon lizenzierte targetfreie Spans werden vor der Nachbarsuche
  kollabiert (131 Token, 128 Scoreknoten). Der vierte Span
  `G770-SPAN-X4P7` ist target-owned und ausschließlich render-only: Beim
  Scoring bleiben `ols` an G770-L004 Ordinal 11 und der rechte `VALUE`-Nachbar
  `aiin` an Ordinal 12 getrennt und bindbar; erst die Reader-Ausgabe verbraucht
  beide als eine Einheit und hat damit 127 praktische Reader-Einheiten. Kein
  targettragender Span wird im Score kollabiert. Eine nicht-exakte
  Targetdublette wäre eine opake ungewertete Barriere und kein Donor; die feste
  Kohorte enthält keine solche Dublette.
- Bindung: die in `METHOD.md` definierte deterministische nächste Kante; kein
  Überspringen des direkten Nachbarn und keine Neuwahl nach Sichtung des
  Ergebnisses.
- Strafdeck: exakt `+6/+5/+4/+3/+2/+1` gemäß
  `src/PENALTY_SPECS.tsv`.
- Target-unabhängige reine Prädikatsabschlüsse: die 17 expliziten Werte in
  `src/TARGET_INDEPENDENT_SLOT_CONSTRAINTS.tsv`; im festen Bestand sind alle
  null. Die alte Rolle eines maskierten Targets darf diese Werte nicht setzen.
- Primärscore: ausschließlich Strafdifferenz gegen das targetgleiche
  `OPAQUE_NULL`.
- Resampling-Einheit: Seite; bei einem Holdout werden alle Kohortenzeilen der
  Seite gemeinsam entfernt.

## Feste Kandidaten

- `ol`: NULL; positionales `von/aus` nach linker Menge, sonst zweiseitiges
  `und/mit`; invariantes `Ansatz/Basis`; invariantes messbares
  `Produkt/Resultat`.
- `ckhy`: NULL; positional final mit Patient `mischen`, medial `Mischung`;
  invariantes `mischen`; invariantes Nomen `Mischung`; invariantes Nomen
  `Infusion/Dekokt`.
- `ols`: NULL; positional vor rechtem Wert `Maß/Dosis`, sonst final
  `Endportion`, sonst `Produktposten`; invariantes `Zubereitung`; invariantes
  `Fertigprodukt/Colatura`; invariantes `abseihen`.
- `otar`: NULL; allgemeines `weiter/dann`; Endpunkt `bis`; nominales
  `Übergangs-/Zubereitungsfeld`.

Es dürfen weder Kandidaten zusammengelegt noch neue Synonyme als eigener
Scorekandidat ergänzt werden. Schrägstriche in `renderer_de` sind eine einzige
ersetzbare Anzeige, kein nachträglich auswählbares Subdeck.

## Vorab festgelegte Entscheidung

Ein Gewinner muss auf der vollen Kohorte:

1. `delta_vs_null >= 4` erreichen;
2. jeden Rivalen mit einer Margin von mindestens `4` schlagen;
3. mindestens zwei echte Nullwaisen auf mindestens zwei Seiten entfernen;
4. in jedem Leave-one-page-out-Fold strikt vor NULL und allen Rivalen bleiben;
5. bei `POSITIONAL` außerdem mindestens vier vor dem besten invarianten
   Rivalen liegen und mindestens zwei qualifizierte Seiten **pro Zweig**
   besitzen.

Ein exakter Voll- oder Fold-Gleichstand geht an NULL. Es gibt keinen
sekundären Fluency-, Häufigkeits-, Geschichts- oder GDT769-Prior-Tiebreak.

## Bereits bekannte Abdeckungslücken

Der feste Zeilenbestand darf die folgenden Lücken offen ausgeben:

- keine saubere Menge unmittelbar vor `ol` für den `von/aus`-Zweig;
- zwei mediale und zwei finale `ckhy`-Seiten, aber nur eine
  patientenqualifizierte finale Seite;
- nur eine `ols`-Seite mit rechtem Wert;
- nur eine strikte Prozess–`otar`–Endpunkt-Seite.

Deshalb wird ein betroffener Kandidat mit zu wenigen qualifizierten Seiten als
`INSUFFICIENT_BRANCH_COVERAGE` markiert. Die Kohorte wird nicht erweitert, und
weder ein Zweig noch ein nächstplatzierter Kandidat wird aus Bequemlichkeit zum
Gewinner erklärt. Ein anderer Kandidat kann nur über seine eigenen vollständig
bestandenen Gates gewinnen.

## Vorab-Falsifikatoren

- Ein Positionsmodell ohne alle notwendigen Zweigseiten ist nicht
  score-bereit, selbst wenn seine beobachteten Zweige günstig aussehen.
- Ein invariantes Vorgangsmodell verliert durch jeden patientenlosen Gebrauch;
  ein invariantes Maßmodell durch jeden wertlosen Gebrauch.
- Ein Relator oder Folgenwort braucht zwei verschiedene Seitenkanten; reine
  Mittelstellung genügt nicht.
- Zeilenfinalität allein ist kein `PREDICATE_ONLY_CLOSE`; ohne eine
  target-unabhängige Markierung feuert P02 nicht.
- `bis` braucht rechts einen target-unabhängigen Endpunkt. Ein allgemeiner
  Zustands- oder Abschlussdefault ist kein automatisch geeigneter Endpunkt.
- Ein Produkt/Resultat ohne gebundene Quelle erhält die feste Strafe; eine
  Menge oder ein Wert allein identifiziert keine Colatura, Infusion oder
  Zubereitung.
- Strukturidentische Kandidaten bleiben bei gleichem Score gebunden; ihre
  deutschen Anzeigen brechen den Gleichstand nicht. Damit geht insbesondere
  ein nicht strukturell trennbares Nomenpaar an NULL.
- Das bloße Ersetzen einer Maske entfernt noch keine Nullwaise. Die gesonderte
  Zwei-Waisen-/Zwei-Seiten-Hürde bleibt bestehen.

## Zulässige Ausgänge

- `PROVISIONAL_POLICY_WIN`: genau ein Nicht-Null-Kandidat besteht alle Gates;
- `OPAQUE_NULL`: kein Kandidat besteht alle Gates oder es gibt einen exakten
  Gleichstand;
- `INSUFFICIENT_BRANCH_COVERAGE`: eine erklärte Pflichtverzweigung oder die
  replizierte Endpunktbindung hat weniger als ihre festgelegten zwei Seiten.

Die Kandidatenebene und die Targetebene bleiben getrennt: eine unterdeckte
Policy wird als solche berichtet, während der Targetdefault NULL bleibt, falls
kein anderer Kandidat unabhängig alle Gewinnerhürden nimmt.

## Aussage- und Datengrenze

Strukturtags und deutsche Rendereranzeigen bleiben getrennt. Jeder
`default_is_translation`, EVA/Latin-, Substring-, Komponenten-, Lexem- und
Klartextkredit ist null. GDT770 darf höchstens eine kohortenlokale
Ganzwort-Policy priorisieren; es bestätigt keine Bedeutung, Wortart,
Komponente oder historische Rezeptlesung.

Es werden keine neue Manuskriptseite, kein Bild, keine OCR und keine neue
Transkription geöffnet. `f84` und `f84r` bleiben unberührt.

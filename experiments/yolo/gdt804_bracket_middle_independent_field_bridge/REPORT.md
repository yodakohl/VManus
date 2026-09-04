# GDT804 — wholespezifische Klammermitten, kein pauschaler Stoffslot

Status: `PARTIAL__11_BRACKET_MIDDLES__0_OPEN_SLOT_INTERSECTION__72_COMMON_MASK_FIELDS__18_OF_45_FIELD_CELLS__15_POSITIONAL_AMOUNT_NEIGHBOURS__0_GDT760_CLEAN_CONTENT_CONTACTS__FIELD_ASSOCIATION_MATCH_SENSITIVE__CONTENT_SLOT_UNRESOLVED__41_ZL3B_QUALITY_VALUE_SPANS__33_CROSS_READER_SEQUENCES__CHEOL_SPECIFICITY_UNRESOLVED__ZERO_LEXEMES`

## Ergebnis

Die elf Mittelwörter der zwölf GDT803-Klammern sind **nicht** einfach elf
bereits bestätigte Pflanzen- oder Zutatennamen. Ihre exakte Schnittmenge mit
dem identischen offenen Oberflächendeck aus GDT744/GDT745 ist **null**. Das
heißt nur, dass sie dort nicht vorselektiert waren; es widerlegt keine
Inhaltsrolle. Der neue gemeinsame
Maskenlauf entfernt deshalb alle 155 gepaarten `Xl`-Formen gleichzeitig als
Bedeutungsanker. Trotzdem bleiben 72 von GDT744s Feldern durch fremde Anker
lizenziert.

In diesen unabhängigen Feldern liegen 18 von
45 exponierten Mittelwortzellen. Gegen die
5.000 am besten aggregiert gematchten Kontrollsets sind es im Mittel
11.3728 Treffer
(`p=0.000199960007998`). Aber auch die bloße
Feldexposition ist ungewöhnlich hoch (Nullmittel
35.1998;
`p=0.00199960007998`), und die
Trefferquote 0.400 liegt im aggregierten
Matching ebenfalls hoch (`p=0.00239952009598`).
Das Resultat ist jedoch match-sensitiv: Unter dem individuellen Zehn-Nachbarn-
Matching fällt die Trefferquote auf `p=0.371076289237`;
im individuellen Leave-`ol`-out-Lauf auf
`p=0.536934630654`. Die Rohcounts werden
von `ol` dominiert; Richtung und Stärke hängen aber vom Kontrollmodell ab.
Installiert wird deshalb nur ein **kontrollsensitiver Sachfeld-Nachbarschaftslead**,
kein Lemma- oder
Zutatenbeweis.

## Die Mengenkarte bestätigt keinen einheitlichen Stoffslot

GDT804 findet 15 Nachbarn auf
der von GDT760 bevorzugten Seite (FIRST→rechts, MIDDLE→links), davon
14 zuvor offene Kandidaten.
Das sind **keine automatisch lizenzierten Inhaltsplätze**: Keine der fünfzehn
ausgewählten Mittelformseiten war in GDT760 bereits ein sauberer CONTENT_PREP-
Kontakt. In `f88r.10` steht zwar `cheol` auf der bevorzugten linken Seite, aber
GDT760s tatsächliche Inhaltslizenz gehört rechts zu `cheos`. Die offenen
Positionsnachbarn liegen im aggregierten Null bei 14.0056
(`p=0.648470305939`).
Damit fällt der behauptete einheitliche Stoffslot weg.

## Die Zwei-Achsen-Lesung bleibt Kandidat, nicht Ergebnis

Im ZL3b-Cache stehen `chol`, `cheol` und `sheol` 41-mal direkt vor
`dain/daiin`. Davon sind 33 Paarsequenzen in allen drei Leserfassungen
vorhanden; der strengere tokenweise Stabilitätsgate behält 32:

| Paar | ZL3b | beide Tokens stabil | Sequenz in allen drei | extern zur GDT803-Entdeckung |
|---|---:|---:|---:|---:|
| `cheol daiin` | 4 | 2 | 3 | 2 |
| `chol daiin` | 29 | 25 | 25 | 25 |
| `chol dain` | 4 | 3 | 3 | 3 |
| `sheol daiin` | 3 | 1 | 1 | 1 |
| `sheol dain` | 1 | 1 | 1 | 1 |

GDT759 hatte zwei `chor chol daiin`-Stellen bereits explorativ als Pflanzenteil
plus Trockenheitszustand plus Wert III gerendert. GDT764s historischer Comparator
E010 belegt nur die passende Rezeptbucharchitektur aus Qualität und Grad, nicht
die Voynich-Wortwerte. Außerdem war die Familie `chol/cheol/sheol` semantisch
post hoc gewählt. Im gleichberechtigten Zensus aller elf Klammermitten besitzt
`ol` 9 externe
extern positionsstabile rechte Werte und `qokol` 4,
`cheol` dagegen nur 1.
Damit bleibt folgende Lesung ein konkreter Satzkandidat, aber kein ausgewählter
Wortwert:

```text
qokain cheol daiin
≈ heiß im II. Grad; trocken im III. Grad
```

Die sichere Ausgabe bleibt `qokain-Qualitätsfeld; cheol-Feld, Wert III`.
`qokain=heiß II` stammt aus GDT636 und ist eine geerbte interne Ganzwort-/Kompositionstheorie,
nicht unabhängig als Klartext bestätigt. `cheol` selbst ist gegen seine zwölf
outcome-blind K12-Kontrollen ohne Spezifitätsvorsprung: Im rohen ZL3b-Zensus werden
Count/Rate/beides von 7/7/5 der zwölf Kontrollen
erreicht oder übertroffen; im strengeren positionsstabilen Zensus sogar von
8/10/8.
Sichere und aggressive Lesung bleiben deshalb getrennt.

## Elf wholespezifische Arbeitswerte

| Form | gegenwärtiger Default | unabhängige Felder | bevorzugte Mengenseite | GDT760-Inhaltskontakt | beide Tokens positionsstabil vor dain/daiin | Entscheidung |
|---|---|---:|---:|---:|---:|---|
| `cheol` | Stoff-/Zubereitungs- oder Qualitätsachse; Identität offen | 4 | 3 | 0 | 2 | MATERIAL_OR_QUALITY_AXIS |
| `otal` | Materia-/Qualitätseintrag; Achse offen | 2 | 1 | 0 | 1 | PREPARATION_OR_QUALITY_HEAD |
| `ol` | allgemeiner mengenfähiger Zubereitungs-/Inhaltsträger | 9 | 9 | 0 | 9 | GENERAL_CONTENT_CARRIER |
| `chal` | Trockenstoff-/Trockenheitsfeld; Ausgangsform offen | 0 | 0 | 0 | 1 | QUALITY_OR_MATERIAL_FIELD |
| `chedal` | Trockenstoff-/Mengenfeld; genaue Identität offen | 0 | 0 | 0 | 1 | MATERIAL_OR_AMOUNT_FIELD |
| `qotal` | Kalt-/Materialfeld; genaue Achse offen | 0 | 0 | 0 | 1 | QUALITY_OR_MATERIAL_FIELD |
| `qokeol` | Heißbehandlungs-/Heißstofffeld; Träger offen | 1 | 0 | 0 | 1 | PROCESS_OR_PREPARATION_FIELD |
| `qokol` | Erhitzungs-/Zubereitungsfeld; Verbstatus offen | 1 | 1 | 0 | 4 | PROCESS_OR_PREPARATION_FIELD |
| `okal` | Kennstellen-/Systemeintrag; Ansatz-/Materialrivale offen | 1 | 1 | 0 | 0 | OPAQUE_SYSTEM_ENTRY |
| `okail` | Ansatz-/Form-II-Eintrag; Identität offen | 0 | 0 | 0 | 0 | OPAQUE_ENTRY |
| `sail` | Chargen-/Form-II-Eintrag; Stoffart offen | 0 | 0 | 0 | 0 | OPAQUE_ENTRY |

`cheol` bleibt wegen vier fremd verankerten Feldern der beste
**Materialrivale** der Klammermitten; GDT760 fügt keinen lizenzierten
Inhaltskontakt hinzu. Seine
Trockenheits-/Zwei-Achsen-Lesung erhält jedoch keinen Spezifitätsvorsprung. `ol` bleibt
der stärkste allgemeine mengenfähige Träger, aber gerade deshalb kein guter Kandidat
für ein einzelnes konkretes Medium wie Öl, Wasser oder Wein. `sail`, `okal` und
`okail` bleiben opake Einträge; insbesondere wird die verworfene Samenlesung von
`sail` nicht wiederbelebt.

## Nächste Route

Alle elf Mittelwörter werden gleich behandelt. Ihre zwölf Entdeckungsstellen
bleiben markiert und werden abgezogen; positionsstabile rechte Kontexte werden
gegen dieselben K12-Kontrollen verglichen. `qokol`, `ol` und `cheol` gehen als
gleichberechtigte Prozess-, Träger- und Materialrivalen hinein. Erst wenn eine
Ganzform dieselbe konkrete Rolle in mehreren unabhängigen Konstruktionen hält,
wird ein Stoff- oder Eigenschaftswert eingesetzt.

Die 41 Textadjazenzen wurden außerdem als GDT388-Paket eingereicht. Der Intake
bleibt erwartungsgemäß `INVALID_PACKET`: Die Auswahl erfolgte nach Formalzugriff,
es gibt keine mobile Null und 41 Kanten liegen unter der Kapazitätsgrenze 50.
Sie zählen deshalb als interne Textbeobachtung, nicht als scorefähige unabhängige
Relationsevidenz.

Keine neue Seite, kein Bild und keine Transkription wurde geöffnet; `f84/f84r`
bleiben ausgeschlossen. Alle deutschen Werte sind ersetzbare Arbeitsrenderer,
nicht bestätigter Klartext.

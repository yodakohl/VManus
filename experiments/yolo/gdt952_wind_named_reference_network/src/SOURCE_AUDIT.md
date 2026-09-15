# Walters W.73 wind diagram: source-only edge audit

Date: 2026-09-15. Source-only audit for the official Walters description of
W.73. No f67r2 target contents, target labels, images, mixed TSV, or new
Voynich material were opened.

## Source frame

The official catalogue describes W.73 as a late-twelfth-century English Latin
compendium. Its fol. 2r wind diagram has twelve colored Latin names and a
corresponding sector of Latin characterization for each wind. The names begin
at the left/North and proceed clockwise. The catalogue explicitly distinguishes
this diagram from the preceding illustrated rota on fol. 1v; they are not two
independent witnesses of the same target relation.

Source: [Walters Ms. W.73 description](https://thedigitalwalters.org/Data/WaltersManuscripts/html/W73/description.html), fol. 2r, catalogue comment. The relevant complete Latin is in the fol. 2r comment, including the directional clauses and the final Circius etymology.

The twelve canonical names in the fol. 2r order are:

`Septentrio, Aquilo, Vulturnus, Subsolanus, Eurus, Euroauster, Auster,
Euronothus, Affricus, Zephirus, Chorus, Circius`.

The catalogue aliases are separate identity claims, not directed edges:

| canonical | alias or spelling variant in the catalogue/source |
|---|---|
| Septentrio | Aparctias / Aparcias |
| Aquilo | Boreas |
| Vulturnus | Boetias in fol. 2r; Calcias in the fol. 1v list |
| Subsolanus | Apeliotes / Apheliotes / Afeliotes |
| Eurus | no paired alias supplied in the fol. 2r list |
| Euroauster | Auroauster in the Latin characterization |
| Auster | Nothus |
| Euronothus | no paired alias supplied |
| Affricus | Lyps |
| Zephirus | Favonius / Fauonius |
| Chorus | Argestes |
| Circius | Tracias / Thracias |

## Eight certain named-reference edges; ninth uncertain

An arrow below means that the sector for the source wind explicitly locates
or etymologically relates it to the named target. It does not mean that the
source wind blows in the target wind's direction. The short Latin excerpts are
kept only as anchors; the catalogue's English translations carry the full
sentence.

| source | target | relation and direction | source anchor / qualification |
|---|---|---|---|
| Vulturnus | Subsolanus | spatial, right (`dexter`) | “dexter est Subsolani”; Vulturnus is right of Subsolanus |
| Eurus | Subsolanus | spatial, left (`sinistro`) | “ex sinistro latere ueniens subsolani”; Eurus comes from Subsolanus's left |
| Euroauster / Auroauster | Auster | spatial, right | catalogue translates the `a dextris` clause as right of Auster; the same sentence also names Auster as the other side |
| Euroauster / Auroauster | Eurus | etymological/side reference | `ex una parte habeat eurum ex altero austrum`: Eurus is explicitly named as one side of Euroauster |
| Euronothus | Auster | spatial, left | catalogue translates the `a sinistra parte` clause as left of Auster |
| Affricus | Zephirus | spatial, right | the `ex zephiri dextro` clause places Affricus at Zephirus's right |
| Chorus | Zephirus (via Favonius) | spatial, left | Chorus is left of Favonius; Favonius is the supplied alias of Zephirus |
| Circius | Septentrio | spatial, right | Circius is right of Septentrio in the `a dextris septentrionis` clause |
| Circius | unresolved; editorially intended Chorus | etymological “joined to” relation, not spatial | raw text says `euro`; catalogue corrects the intended referent to Chorus |

The first seven rows are the mandatory directed spatial references. The
Euroauster→Eurus row is the eighth certain edge: it is a named etymological
side reference, not a ninth spatial position. The final Circius row is the
ninth and remains uncertain: the printed Latin's `euro` can be read literally
as Eurus, while the catalogue's parenthetical correction says it should be
Chorus. It is therefore not legitimate to silently create a clean
Circius→Eurus edge. A frozen source graph should retain `raw=euro`,
`corrected_target=Chorus`, and `correction_status=editorial`, while treating
Circius→Septentrio as unambiguous spatial evidence.

These clauses are asymmetric. For example, Vulturnus is stated to be right of
Subsolanus, while Eurus is stated to come from Subsolanus's left; they are not
two interchangeable aliases for one relation. `Euroauster` itself is described
as having Eurus on one side and Auster on the other. This is the explicit
Euroauster→Eurus named reference recorded above, but it does not license an
additional spatial arrow to Eurus. Likewise, the Chorus relation reaches
Favonius, not the literal name Zephirus; treating it as Chorus→Zephirus
requires a declared synonym collapse `Favonius = Zephirus`. Without that
collapse, the edge target must remain the alias surface `Favonius`, and
Favonius must not be counted as a second independent wind node.

## Whole-form and inflection warning

Treating the twelve names as identical whole-form labels requires a declared
choice between surface-sensitive and canonical-lexeme modes. In the Latin
clauses, the referenced names appear in inflected forms: `Subsolani` (genitive
of Subsolanus), `Austri` (genitive of Auster), `zephiri` (genitive of Zephirus),
`fauovnii` (genitive of Favonius), and `septentrionis` (genitive of
Septentrio). Equating each with its nominative node is a case/inflection
normalization hypothesis, not a consequence of the diagram.

The source graph should therefore preserve both the written form and the
canonical node. A surface-equality test keeps `Subsolani` distinct from
`Subsolanus`; a canonical-equality test must list the normalization rules
before any target exposure. `Auroauster`/`Euroauster` is a spelling variant,
not a Latin case ending, and the `euro`/Chorus issue is a source correction,
not normalization. No target whole-form identity follows from any of these
source equivalences.

## Consequence for GDT952

The useful source-level consequence is a small directed, off-diagonal wind
graph with explicit alias edges and one editorially uncertain etymological
edge. A future target comparison can be meaningfully different from a ring
adjacency or visual-order test only if it freezes this distinction: directed
source-to-neighbor edges, canonical alias normalization, and the Circius
correction must be fixed before target labels are seen. A target result that
requires reversing left/right, treating aliases as extra nodes, or choosing
between Eurus and Chorus after exposure would be a model repair.

The catalogue establishes that a medieval diagram can write named, asymmetric
cross-references in sector prose. It does not establish that any Voynich label
is a wind name, that its whole forms are case-insensitive, or that the
manuscript contains this graph.

### Correction record

The initial version treated the uncertain Circius `euro` clause as the eighth
row and omitted the certain Euroauster→Eurus named reference. The table and
count above correct that bookkeeping while retaining the raw Circius wording
and its editorial Chorus correction. The seven spatial edges, the
Euroauster→Eurus etymological edge, and the Circius uncertain edge remain
separate source claims.

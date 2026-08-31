# GDT696 method

## Question and fixed scope

Can a finite set of already licensed local donor/action relations make the V68
working edition more concrete without changing a token gloss, line text, bound
span, page or unresolved reference?

The scope remains the 479 tokens, 51 lines and 36 pages frozen by GDT695. No
transcription or image is opened, and f84/f84r are forbidden.

## Source deck

`src/V69_LOCAL_ACTION_EDGES.tsv` names exactly nine occurrence-level edges. An
edge specifies its locus, written source ordinal(s), optional written reference
ordinal, target action ordinal, exact expected surfaces and V68 glosses, one
short relation-explicit German rendering, provenance, support tier and a rival
control. It cannot be applied at another occurrence.

The `source_start/end` span is the complete written left-participant block,
not a claim that every position is a donor. `left_role_map` assigns each member
separately. In particular, C007 marks #2 as `OUTPUT_LABEL` and only #3 as
`DONOR_SOURCE_SHARE`; C009 separates the preparation head from its measure
pool. The token overlay retains both the edge membership and these exact roles.

The six stronger edges are:

1. f105v.1 `olpcheey` → `ykaiin`: heat the written dry-bound wood powder.
2. f113v.17 `cthororaiin` → `yteeeor`: cool one of three herb portions.
3. f75r.3 `orchey` → `qey`: take the explicitly preceding middle-dried portion.
4. f80v.35 `olkar` → the first `qol`: add drug material to the hot wood-preparation share.
5. f77r.38 `chcphey` → the first `qol`: add the written dried finished compound.
6. f86v6.25 `qodar` → `ykaiin`: heat the just-measured drug share.

The three working edges are kept in a separate tier: at f86v6.25 `qokar`
supplies the selected hot-share label while `olkar` supplies the source
preparation share before `qodar`; f80v.35 retains the second `qol`
continuation; and f104v.2 supplies the three-measure pool before the one-measure
action. None is exported as a nearest-donor rule.

## Exhaustive reference and rival accounting

A fixed German expression scan finds exactly 27 V68 positions containing
`hiervon`, `hieraus`, `hierzu`, `hieran`, `vorstehend...`, `davon` or `dieses`.
`src/V69_REFERENCE_DECISIONS.tsv` must match every one exactly. Five positions
link to stronger edges and one to a working edge. The other 21 remain as seven
object rivals, five unresolved line-initial references, two unresolved local
rivals, three structural connectors, one process-scope carry, one intratoken
measure, one inherited nominal binding and one exact nominal reference.

`src/V69_RELATION_RIVALS.tsv` separately joins seventeen attractive but
unlicensed source/action proposals back to V68: seven explicit-reference
rivals and ten proximity-only candidates. Every target must still be a real
V68 action ordinal. These rows are controls, never fallback edges.

## Deterministic checks and outputs

The builder joins every source, reference and target by exact locus and ordinal
and requires exact V68 surface and gloss equality. It verifies the GDT676 T03
template and the two occurrence corrections for f77r.38 and f80v.35, then
writes the nine-edge deck, 27-position reference census, seventeen-rival deck,
complete 479-token and 51-line relation overlays, three-span freeze, census and
human reader.

The line overlay repeats `v68_clause_translation_de` byte-for-byte as V69 text.
Concrete relation renderings live only in a separate annotation column. Thus
the useful new information is explicit, but it cannot silently rewrite the
dictionary.

## Decision rule and claim ceiling

Pass requires exactly 5 `A_STRONG_LICENSED`, 1
`A_MINUS_EXPLICIT_OUTPUT` and 3 `B_WORKING_LOCAL` edges, an exhaustive
27-position reference census, all seventeen rivals held, exact action targets,
479/51/3 unchanged token/line/span records, zero new meanings or pages and no
f84/f84r access.

V69 is an occurrence-bound editorial relation overlay on an exploratory German
working reader. It does not establish Voynich pronouns, case, syntax,
plaintext, language or procedure, and it gives no substring a portable new
meaning.

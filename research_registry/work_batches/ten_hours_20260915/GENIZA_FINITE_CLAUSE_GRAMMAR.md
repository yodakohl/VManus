# Draft finite clause grammar from PGP40129

This is source material for a bounded constructive-language discussion. It
uses only the three selected complete head-bounded records in
`PGP40129_SOURCE.json`: Peach (recto 5–13 before `אלרמֹאן`), Pomegranate
(recto 13 through verso 5 before `אלספרגֹל`), and Quince (verso 5–14 before
`אלתֹפאחֹ`). It does not access Voynich text or reserves, assign symbol values,
repair GDT965, or make clinical claims.

The machine-readable draft is [`GENIZA_FINITE_CLAUSE_GRAMMAR.json`](GENIZA_FINITE_CLAUSE_GRAMMAR.json).
The source packet hash is `8e2246879c5b2dd1e8f00600fda7f8110c997c0cdaed4f56cb07ff003f23ed36`;
the construction-source dossier hash is
`a0e58038c0e7ea9ffd7a9ced1ff2a3364c1d7ba4689cae0273476d41dbb01291`.

## Finite bundles

The draft has 14 observed exact templates, grouped into four peach, five
pomegranate, and five quince templates. A future paragraph selects exactly
one fruit bundle. This prevents a sour pomegranate condition from combining
with a quince outcome or a peach follow-up. A pronoun must resolve to the
selected head or to an argument explicitly introduced by that template.

| Bundle | Head and source span | Licensed template IDs | Condition discipline |
|---|---|---|---|
| PEACH | `אלכוך`, recto 5–13 before `אלרמֹאן` | T01–T04 | Base cold/moist; T04 requires cold-temperament eaters; T02 keeps its explicit apricot comparator. |
| POMEGRANATE | `אלרמֹאן`, recto 13–verso 5 before `אלספרגֹל` | T05–T09 | Sour, sweet, named-type, and cited-case branches retain their own outcomes. |
| QUINCE | `אלספרגֹל`, verso 5–14 before `אלתֹפאחֹ` | T10–T14 | Before/after-food, unripe, sour, sweet, and comparative branches cannot cross-combine. |

## Templates and readings

All entries below are `observed_exact`, with source offsets in the JSON. The
English text is a working rendering of the public Princeton/Avetisyan source
translation where available; it is not a clinical assertion.

### Peach

* **T01** — `אלכוך. בארד רטב` (recto 5): explicit peach head with cold and
  moist properties. The source line continues with additional properties.
* **T02** — `ואלגדא / אלמתולד מנה אגלטֹ מן אלגדא אלמתולד מן אלמשמש / וליס יפסד פי
  אלמעדה כפסאד אלמשמש.` (recto 5 tail–7): food produced from peach
  is compared with apricot food, followed by a stomach-spoilage clause.
  `אלמשמש` is a fixed source comparator, not a second freely chosen paragraph
  head.
* **T03** — the recto 7–11 sequence from `ומא כאן` through
  `אגלטֹ ואבטא אנהצֹאמא.`: the source contrasts a soft peach whose pit is
  easily removed with material adhering to the pit, then compares digestion
  and stomach departure. `מנה`, `נואה`, and `פהו` retain their source-linked
  dependencies; exact predicate attachment remains an interpretive judgment.
* **T04** — the recto 11–13 phrase beginning `ומתי אכלה אצחאב` and ending
  before the pomegranate head: cold-temperament eaters are followed by one of
  three attested ginger/honey options. The alternatives are source list
  members, not free cross-products.

### Pomegranate

* **T05** — `אלרמֹאן` through `ואלכבד אלחארתין מסכן ללקי` (recto 13–16):
  base coldness, sour condition, yellow-bile suppression, and a coordinated
  stomach+liver target. The full context makes `אלחארתין` a working
  dual-agreement modifier over `ללמעדה ואלכבד`; exact case remains open.
* **T06** — `וחב אלרמאן אלחאמץֹ` through `... אלבטן.` (recto 16–18):
  sour dried seed and its stated nature/bilious-substance outcome. `עקל
  אלטביעה` is treated as a likely verb–object sequence, not idāfa.
* **T07** — `ואלרמאן אלחלוא מעתדל פי / אלחרארה ואלברודה והו רטב אלמזאגֹ.`
  (recto 18–19): sweet pomegranate, balanced heat/cold, moist temperament.
* **T08** — the named-type sequence `ואלנוע אלמערוף מנה באלמליסי` through
  recto 21: soft-seed type, acute cough from heat, and cold-stomach outcome.
* **T09** — the verso 1–5 cited case before the quince head: a woman, the
  repeated `פם מעדתהא` body relation, pomegranate water, barley drink, and
  stated outcomes. This is an editorial working rendering because published
  English coverage is incomplete; `ודלך` and the final effect wording remain
  unresolved. The source attribution and pronoun dependencies remain part of
  the template.

### Quince

* **T10** — `אלספרגֹל` through `אלטעאם וגדאוה כתיר.` (verso 5–8): cold, dry,
  astringent quince with before-food and after-food branches. `אלטביעה`
  belongs to the nature/recipient effect phrase and is not treated as a simple
  pronoun for quince.
* **T11** — unripe branch from `ומא כאן מנה גיר נצֹיגֹ` through
  `קוי אלחבס ללטביעה.` (verso 8–10): indigestion, slow emptying, and strong
  constriction as source-described outcomes.
* **T12** — sour branch `ומא כאן מן אלספרגֹל חאמצֹא` through `אלתאלתה`
  (verso 10–11): cold in the second degree and dry in the third. The three
  consecutive holam marks in `בארדֹֹֹ` remain untouched.
* **T13** — sweet branch `ומא כאן מנה חלוא` through the comparative period
  ending `אכתר יבסא.` (verso 11–13): balanced heat/cold and an
  astringency-to-dryness comparison.
* **T14** — continuation beginning `ומאוה אשד תקויה ללמעדה` (verso 13–14):
  a displayed clause segment whose English translation is incomplete.
  `ומאוה` may be a water/juice form or another continuation; omitted meanings
  are not supplied, and this segment is not a productive slot template.

## Copy versus generation

The 14 templates are source quotations or source-exact slices and therefore
carry `utterance_status: observed_exact`. The finite paths make T01, T05, and
T10 the explicit starts; subsequent templates require their immediately
preceding source-linked context and preserve reference resolution. The JSON
lists three `generated_novel` recipes (L01–L03) that select one exact
ginger/honey follow-up from T04 and remove the source disjunction. These are
recipes only; no novel sentence is emitted.
If a later generator substitutes an attested noun or property inside a
licensed bundle, it must mark the result `generated_novel`, preserve the source
template ID, list every substitution, and report that the resulting utterance
has no direct historical attestation. A generated paragraph must contain one
head bundle and resolve every `מנה`, `פהו`, `אכלה`, `בעדה`, `והו`, or similar
reference to that bundle's declared antecedent. Any later noun or property
substitution must be finite, typed, and recorded with its exact source form and
bundle.

## Source limits

The construction is useful because it links article-bearing noun/property
frames, condition clauses, body targets, coordinated properties, possessive
suffixes, and explicit outcomes. It remains a conditional finite grammar from
one historical witness. It does not prove that every `אל` is an article, that
every following word is an adjective, or that its historical medical claims
are clinically true. Supplemental recto 2, verso 19/21, and right-margin
material are excluded from the three-record grammar.

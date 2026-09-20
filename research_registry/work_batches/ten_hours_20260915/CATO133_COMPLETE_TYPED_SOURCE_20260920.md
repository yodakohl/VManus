# Cato *De Agri Cultura* 133 — complete typed source AST

Status: `SOURCE_ONLY_COMPILED`; no target gloss, target selection, or historical
identity claim.

The source witness is the 1934 Hooper/Ash Loeb edition as presented by the
proofread [English page](https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Cato/De_Agricultura/H%2A.html)
and [Latin page](https://penelope.uchicago.edu/Thayer/L/Roman/Texts/Cato/De_Agricultura/H%2A.html).
The online page headers identify W. D. Hooper and H. B. Ash, *Cato on
Agriculture*, Loeb Classical Library, London 1934. The earlier dossier's
Goetz/Teubner provenance label was incorrect for this witness; the JSON records
the correction explicitly.

The complete owned span is the heading and §§133.1–4:

```latin
Propagatio pomorum ceterarumque arborum. Arboribus abs terra pulli qui nati erunt, eos in terram deprimito, extollito, uti radicem capere possint. Inde, ubi tempus erit, effodito seritoque recte. Ficum, oleam, malum Punicum, mala strutea, cotonea aliaque mala omnia, laurum Cypriam, Delphicam, prunum, murtum coniugulum et murtum album et nigrum, nuces Abellanas, Praenestinas, platanum, haec omnia genera a capitibus propagari eximique ad hunc modum oportebit. Quae diligentius seri voles, in calicibus seri oportet. In arboribus radices uti capiant, calicem pertusum sumito tibi aut quasillum; per eum ramulum trasserito; eum quasillum terra inpleto calcatoque, in arbore relinquito. Ubi bimum erit, ramum tenerum infra praecidito, cum quasillo serito. Eo modo quod vis genus arborum facere poteris uti radices bene habeant. Item vitem in quasillum propagato terraque bene operito, anno post praecidito, cum qualo serito.
```

The English witness gives three procedures: ground shoots are pressed down with
tips raised for possible rooting, then dug and planted straight at a proper
time; selected plants may be rooted on a tree in a perforated pot or basket,
filled and packed with earth, left on the tree, cut below after a two-year state,
and planted with the basket; vines are put through a basket, covered with earth,
cut after one year, and planted with the basket.

## Interface

The executable representation is in
`CATO133_COMPLETE_TYPED_SOURCE_20260920.json`. Its `tree` field is recursive:
`[OP_NAME, child1, ...]`; leaves are prefixed atom strings (`ref:`, `prop:`,
`num:`, `ent:`), and `atom_types` maps every used leaf/operator atom to
`REFERENCE`, `PROPERTY`, `NUMBER`, `ENTITY`, or `OP`. `node_index` and
`node_trees` retain proposition identifiers and source spans. `source_ownership`
is keyed by complete source-span proposition and points to those identifiers.

`SEQ(left,right)` is binary and preserves source order. Species are a binary
`CONS(head,tail)` chain ending in nullary `NIL`; the list is expanded twice in
the root for the two source claims about all genera. Operator arities and typed
signatures are recorded in `type_system.signatures`; no variable-arity or
opaque `REST` node is used.

The root tree is structurally:

```text
[SEQ,
  [SEQ, [SEQ, [TITLE, topic], ground-shoot-procedure + species-list-procedure], careful-pot/basket-procedure],
  vine-procedure]
```

The JSON expands every abbreviation above into fixed-arity operations. Its
source ownership table covers heading, ground emergence/press/raise/purpose,
proper-time digging and straight planting, all 15 inventory entries, head/crown
propagation and extraction, careful selection and pot/basket alternatives,
thread/fill/pack/leave, two-year condition, lower cut, basket planting,
capability claim, and vine propagation/cover/one-year cut/`qualus` planting.

## Source constraints retained in the tree

- The ground-shoot branch has no invented age, basket, attachment, or cut. Its
  only time value is typed `num:proper_time = UNKNOWN/TIME`.
- `uti radicem capere possint` and `uti radices bene habeant` are represented as
  purpose/capability properties. The AST does not assert that rooting actually
  succeeded.
- The species list is explicit: fig, olive, pomegranate, *mala strutea*,
  quince, all other fruit, Cyprian and Delphic laurel, plum, conjuglan myrtle,
  white and black myrtle, Abellan and Praenestine nuts, and plane tree. The
  uncertain botanical labels remain source labels.
- `calix` versus `quasillus`, the antecedent of `bimum`, the reference point of
  `infra`, and `qualus` versus `quasillus` remain typed uncertainties. They are
  not resolved by target results or by English convenience.
- Imperatives have an unspecified addressee; no personal owner or agent is
  inserted. `a capitibus` is retained as a reference to heads/crowns without
  selecting a modern anatomical interpretation.

Compiler conventions such as recursive `SEQ`, `CONS/NIL`, and explicit
reference atoms are serialization choices for repeatable source compilation,
not claims about Latin phonetics, a target language, or a Voynich parser.

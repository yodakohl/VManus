# Independent first-contract review: recipient predicate/modifier interfaces

27 September 2026. I read the route, `RECIPIENT_RESTRICTION_ROOT_DECISION.md`,
the bounded source preselection and source critic, then only the frozen
`RECIPIENT_AUTHOR_CONTRACT.md` (SHA256
`bba51d28c245cb7287a42190c315c426dedacb13da6c72e658d48d641c47e23d`). I did
not inspect an unfinished whole draft, target values or new data. This is a
contract-level interface check, not a semantic selection or target review.

## Typed predicate and modifier interface

The denotations are explicit and mutually composable:

```text
Pred[c] = Material[c] -> Proposition
A_c(b) : Pred[c]
B_c(P) : Pred[c] -> Pred[c]
B_c(P)(D)(x) = D(x) AND P(x)
```

Thus `dar`/`daiin` yield recipient-indexed suitability predicates, and the
`qo`-prefixed forms yield modifiers of a separately supplied material
description. `B` preserves the input material and owner/source context while
adding suitability of the same `x`. A bare application says `P(x)` and does
not imply liver origin; a modified application says both `D(x)` and `P(x)`.
The contract correctly avoids inventing an incompatible “description” sort
where the source provides only a unary material predicate. The actual type
change is a predicate passed as input to a predicate-transformer.

The five licensed cuts, fixed recipient values and `ain=KIDNEYS` are
consistent with those signatures. The ar/aiin/ain permutation is explicitly
one of six choices, not a source-identified mapping. The common context `c`
is captured by an explicit context binder; mismatched material/context domains
do not silently coerce. The contract defines what the later grammar must
write, rather than presuming any additional whole form or old reference rule.

## Binders, references and origin projection

The syntax/value distinction is unusually clear and internally coherent:
literal strings are syntax; lexical entries must specify a constructor and
its denotation; a reference handle is not the value it denotes; and a
material binder node is not itself a material witness. A binder contributes
an assertion/schema with a stated scope. A witness can continue only within
that declared scope or via a written continuation. Missing bindings are
gaps, with no nearest-token/last-organ escape hatch.

The origin-projection rule is licensed by the modifier's explicit conjunction:
from an assertion `B_c(A_c(b))(D)(x)` one may project `D(x)` by conjunction
elimination, then refer to that **same bound x**. This does not require
inverting a predicate to recover its recipient or guessing how a historical
description was built. The contract also refuses to infer a source field
from a modifier value. The downstream use remains a concrete authoring
obligation: a later clause must fall inside a continuing scope or have an
explicit continuation and a reference whose denotation is x. That is not a
contract contradiction; it is the precise thing the author must demonstrate.

One harmless notation boundary remains for the author to make explicit in
the eventual lexical/grammar account: `RESIDUE_FROM(liver,c)` is called a
separately written description obligation, and by the stated definition of
MaterialDescription it must denote an element of `Pred[c]`. This is enough
to fix the expected semantic type, but not a lexical constructor, source
meaning assignment, or surface expression. The contract correctly leaves
that realization open rather than inventing a token here.

## Common context and repeated use

The single `c` is captured through all intended applications. The contract
requires actual bare applications of the same `A_c` for spleen and gall
bladder, including explicit gall-bladder membership/instantiation; actual
modifier applications for spleen and gall bladder to the written liver-residue
description; and an unchanged kidney application. It separately requires at
least one subsequent origin-preserving use of the same modified witness.
This prevents counting `A_c(b)` merely because it is evaluated internally
inside `B_c(A_c(b))`. It also prevents counting three recipient constants
as three meanings of the suitability predicate.

The source's generic attraction/capability clauses can support generic
predicate applications without inventing meals or material-transfer events.
The required body-condition/context binder and explicit scope are additional
authoring commitments, properly charged in the contract. The source does
not provide measured case populations, non-liver suitable material, or a
historical compositional grammar.

## Weak countermodel and serious rival

The contract distinguishes its two countermodels correctly. Independent
existentials for origin and suitability can both be true without a shared
witness, so they cannot replace the source's `exists x [D(x) AND P(x)]`
residue qualification. Separately, the bare predicate is not generally the
same assertion as `D(x) AND P(x)`; the contract does not claim that Galen
actually supplies a suitable non-liver witness, only that this distinction
is permitted by the formal scopes.

These checks do **not** defeat the serious rival. It can use separate
recipient-qualified material descriptions and ordinary clauses to preserve
both origin and suitability for the same witness, then reuse that witness
downstream. The contract states this rival explicitly and does not infer
that extensional equivalence proves or disproves an internal factorization.
That is the appropriate limit: a later candidate must demonstrate repeated
typed applications and bindings, but the source alone cannot prefer the
factorized representation.

## Review conclusion

I find no contradiction in the frozen predicate, modifier, context, binder,
reference or projection interfaces. The key distinctions are specified:
bare versus modified predicate; syntactic handle versus denoted value;
binder node versus bound material; same x versus separate existential
witnesses; and weak binding error versus a fully source-compatible
separate-description rival. The remaining work is deliberately deferred to
the whole grammar: bind a compatible context, realize the liver-origin
description, make the required bare and modified applications, preserve the
same witness through projection, and retain all source obligations. This
review does not predict whether a finite target account will succeed.

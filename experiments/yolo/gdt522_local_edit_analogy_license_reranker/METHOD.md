# GDT522 method

## Question

Can old pairs of closely related visible forms predict the corresponding
local change in a new component recipe, without storing target surfaces as
whole-form exceptions?

## Inputs

- GDT407's 1,558 invariant old running surface types and recipes;
- GDT516's 159 current new-to-old-base surfaces and selected recipes;
- GDT521's complete finite-candidate score.

No new page is admitted.

## Analogy extraction

For every old big form, delete one to three contiguous visible characters. If
the result is another old form, compare their recipes. The recipe relation is
accepted when deleting zero to three contiguous atoms from the big recipe
produces the small recipe. Zero atoms is allowed only when the recipes are
identical; it records a visible insertion with no new recipe atom.

Each signature contains:

```text
visible inserted block + visible position
    -> atom inserted block + atom position
```

Positions are `LEFT`, `INNER` or `RIGHT`; null atom insertions use `NULL`.
Repeated deletion paths inside the same big/small pair count only once per
signature.

The full model contains 1,081 signatures from 3,493 unique
big/small/signature relations, under 585 visible block/position conditions.
Forty-nine signatures are visible-but-null relations.

## Candidate feature

For a target surface, only deletion routes of the minimum visible width are
retained. The target is always the big form; reverse analogies are excluded.
For a candidate recipe, the same local recipe deletion must recover the old
base recipe.

For an attested signature:

```text
p = (signature support + 0.5)
    / (visible-condition total + 0.5 * observed option count)

reliability = support / (support + 2)

bonus = reliability * (1.1 + log(p))

GDT522 score = GDT521 score - 0.40 * bonus
```

An unsupported candidate receives no analogy bonus. A supported but poor
conditional mapping can receive a negative bonus. This prevents a merely
frequent visible insertion from overpowering a rarer but unambiguous mapping.

## Rehearsal and decision rule

The old SHA-256 four-way rotation rebuilds the compiler, renderer, boundary,
short-history and analogy models from the other three groups. The emitted
ladder covers a broad exploratory grid; `COND_C110_W040` is the selected
lossless current setting.

Exact-event and known surface/role cards retain precedence. A local analogy is
a renderer/composition license, not a word translation or confirmed plaintext.

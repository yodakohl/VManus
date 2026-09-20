# Cato 133 source review — AST corrections before any bind

Status: source-only audit; the original
`research_registry/work_batches/ten_hours_20260915/CATO133_COMPLETE_TYPED_SOURCE_20260920.json`
is preserved byte-for-byte. This review is separate so root can replace the
AST and hash deliberately.

Primary provenance is the proofread 1934 Hooper/Ash Loeb witness:
[Latin page](https://penelope.uchicago.edu/Thayer/L/Roman/Texts/Cato/De_Agricultura/H%2A.html),
§133 at line 30–31 of the accessed page. The English page is the paired
[1934 Loeb translation](https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Cato/De_Agricultura/H%2A.html).
The Latin says:

- `Arboribus abs terra pulli ... deprimito, extollito, uti radicem capere possint`;
- `ubi tempus erit, effodito seritoque recte`;
- `haec omnia genera a capitibus propagari eximique ad hunc modum oportebit`;
- `Quae diligentius seri voles, in calicibus seri oportet`;
- `... calicem pertusum sumito tibi aut quasillum; per eum ramulum trasserito; eum quasillum terra inpleto calcatoque, in arbore relinquito`;
- `Ubi bimum erit, ramum tenerum infra praecidito, cum quasillo serito`;
- `Eo modo quod vis genus arborum facere poteris uti radices bene habeant`;
- `Item vitem in quasillum propagato terraque bene operito, anno post praecidito, cum qualo serito`.

## Corrections

| Existing AST issue | Minimal source-faithful correction | Remaining uncertainty |
|---|---|---|
| Species `CONS` root is `platanus`, producing reverse order | Build `CONS(ficus, CONS(olea, ... CONS(platanus,NIL)))` in the Latin order | Repeating the list under both propagation/extraction claims is a serializer choice, not a source repetition. Prefer one list value consumed by a `FOR_ALL(list, SEQ(PROPAGATE_FROM_HEADS, EXTRACT_BY_METHOD))` or equivalent. |
| `DIG` sits outside `WHEN(proper_time, PLANT)` | Use `WHEN(PROPER_TIME_UNKNOWN, SEQ(DIG, PLANT_STRAIGHT))`; `ubi tempus erit` scopes both `effodito` and `seritoque recte` | Proper time has no number or age. |
| Rooting purpose wraps only `RAISE` | Use `PURPOSE(SEQ(PRESS_INTO_GROUND, RAISE_TIP), ROOTING_POSSIBLE)`; the purpose follows both imperatives | This is a purpose/capability, never an assertion that roots actually formed. |
| `sumito` (“take”) is omitted by a bare `ALT` | Add a fixed-arity `TAKE(CONTAINER_CHOICE)` before threading; retain `ALT(PERFORATED_POT,BASKET)` as its argument | The Latin gives an alternative object, not a target symbol or a selected vessel. |
| Final capability is restricted to `careful_targets` | Bind `quod vis genus arborum` to a broader `ANY_DESIRED_TREE_GENUS` reference; keep the careful branch as its preceding local context | “Any genus you wish” is a capability claim, not an assertion that every listed tree rooted. |
| `num:proper_time` is typed as a number | Represent `ubi tempus erit` as a typed unknown condition/reference (`PROPER_TIME_CONDITION`), not a numeric value | The only exact numbers are `bimum` (two years) and `anno post` (one year). |
| Vine duration is attached directly to the vine as if plant age | Encode `AFTER_TIME(VINE_PROPAGATION_AND_COVER, ONE_YEAR, CUT)`; `anno post` is “a year afterward” relative to the preceding procedure | It is not a claim that the vine’s biological age is one year. Preserve `terraque bene operito` as a well-cover/earth operation with its qualifier. |
| Full species list appears twice in the root tree | Treat the list as one source value and apply a binary `FOR_ALL`/sequence constructor if needed | The two verbs `propagari` and `eximique` are both source-owned, but duplicate list serialization is not source evidence. |

## Constraints that remain safe

The ground branch has no written basket, cut, or age. Its tip is raised and its
shoot is pressed into earth for the stated purpose of possible rooting; later,
at an unknown proper time, it is dug and planted straight/right. The pot/basket
branch explicitly contains the taking, alternative container, threading, earth
filling/packing, leaving on the tree, two-year condition with unresolved
antecedent, tender branch cut below an unresolved reference point, and planting
with the basket. The vine branch has its own basket, earth-cover qualifier,
one-year-after interval, cut, and `qualus` planting container.

No actual root success, personal owner, modern botanical identity, target word,
or target participant role follows from this source.

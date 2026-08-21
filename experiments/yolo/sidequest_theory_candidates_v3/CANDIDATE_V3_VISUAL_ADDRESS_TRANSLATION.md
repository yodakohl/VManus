# V3 candidate: the drawn-argument address grammar

Date: 2026-08-21

Status: speculative ten-page sidequest theory. This is not a GDT result, a
decipherment, or a claim that any Voynich form has the English meaning used in
the paraphrases below. Confirmed English lexemes: **0**. Confirmed plaintext
clauses: **0**.

## Scope and evidence discipline

This candidate uses only the fixed pages:

- Herbal: `f10r`, `f11r`, `f55v`, `f56r`;
- Biological: `f81v`, `f82r`, `f83r`;
- circle/astronomical: `f67r2`, `f68r1`, `f69v`.

No `f84` or `f84r` material was used. ZL3b, IT2a and RF1b are alternate
readings, not replications. The picture descriptions are existing public human
annotations. Tentative plant identifications and the proposed zodiac/month or
lunar-mansion identifications are possibilities, not ownership evidence. The
circle pages have no GDT327 events, so their readings below use layout and
surface strings only.

Four levels are kept separate throughout:

1. **drawn/inherited argument**: what a reader can point to without text;
2. **anonymous formal role**: HEAD, LINK, POINTER, PARAMETER, STATE, COMMIT;
3. **source-class expansion**: address, connect, prepared, setting, duration;
4. **fluent paraphrase**: an English sentence supplied only to show coherence.

Brackets in a paraphrase mark silent pictured material. A slash marks a real
field boundary, `⟫` an attached close, and `(?)` an unsupported expansion.

## Core proposal

The image is not merely a decorated noun at the top of a prose recipe. It is a
small, page-local argument frame. The scribe can leave several source
arguments silent because the reader can recover them by pointing:

```text
HERBAL DRAWING                    BIO DRAWING
[this simple]                     [this installation/application]
  ├─ [root]                         ├─ [this body/figure]
  ├─ [leaf class A/B]               ├─ [this vessel/pool]
  ├─ [flower/fruit]                 ├─ [this inlet/outlet/path]
  └─ [whole plant/habitat]          └─ [this junction/station]

CIRCLE DRAWING
[this configured time-map]
  ├─ [current compartment/ray]
  ├─ [current star or local entry]
  ├─ [centre/sun/moon anchor]
  └─ [ordinal/cyclic setting]
```

The text need not repeatedly say *plant*, *leaf*, *woman*, *water*, *tube*,
*star* or *month*. It records what cannot be drawn economically: which visible
slot is active, how slots relate, the setting or quantity attached to them, a
prepared/conditioned state, and where a local specification commits.

Thus a source-like record is reconstructed as:

```text
DRAWN FRAME + [silent slot]
  + ADDRESS/ENTRY
  + POINTER/ITEM
  + RELATION/PATH
  + PARAMETER/SETTING
  + QUALIFIED STATE
  + PAYLOAD-BEARING COMMIT
```

This is compatible with a formula-card workshop register. The exact card is
the stable unit; wrappers and line reflow are downstream rendering. The
proposal adds a semantic *interface* to the anonymous grammar, not a claim
that the cards are ordinary words.

## Two visual-address models compared

### Model A — pictured-subject ellipsis

The picture silently supplies only the dossier subject: `[this plant]` or
`[this bath]`. Every remaining argument is textual. On this model `qokaiin`
is most naturally a spoken instruction head, L/O a conjunction or
preposition, AIIN a stated amount, Y a generic noun, and CTHY a quality.

Advantages:

- it is close to ordinary recipe prose;
- `qokaiin`'s 7/9 field-entry skew fits an instruction head;
- long Herbal rows can be read as compressed descriptive clauses.

Failures:

- the rich Bio geometry is almost unused even though figures, pools, paths,
  junctions, inlet and outlet are already visible;
- Y and L/O must act like very underspecified spoken words to cross Herbal and
  Bio;
- `Y–AIIN–Y` invites a false universal “equal amount” reading even though its
  pictured operands are not independently symmetric;
- the many short close-bearing Bio fields would repeatedly name arguments that
  are immediately adjacent in the drawing;
- it offers no principled bridge to radial and compartmental Astro text.

### Model B — drawn-argument frame

The picture supplies the subject *and a page-local inventory of addressable
roles*. Cards do not name one visible class universally. They select an active
slot or state a relation among slots. The same formal card can therefore have
different fluent expansions while retaining one abstract function.

Examples:

```text
same POINTER function:
  Herbal  -> [this organ/part]
  Bio     -> [this figure/station/path endpoint]

same PARAMETER function:
  Herbal  -> degree, portion, preparation setting
  Bio     -> duration, level, stage, route setting

same LINK function:
  Herbal  -> with/from/on the pictured part
  Bio     -> in/to/through the pictured vessel or path
```

Advantages:

- it makes the image carry information proportional to its complexity;
- it preserves stable abstract card functions without universal picture
  glosses;
- it explains why a field can be short yet useful: the missing noun and often
  one relational argument are visible;
- it treats Astro compartment/ray position as the same *kind* of silent
  address while respecting Astro's separate surface namespace;
- it turns the `f82r.3–4` repeated `qokaiin` into a carried address operation,
  not necessarily a repeated liquid noun or spoken imperative.

Costs and contradictions:

- no line is securely linked to one pictured component;
- the picture provides several possible slots but no proven reading order;
- semantic role must not be inferred from proximity alone;
- a pointer can look like a generic item card unless a fixed-page positional
  test separates them;
- the model can become unfalsifiable if every unknown card is called a silent
  deictic. The stopping rule below prevents that.

**Choice: Model B.** It explains all three registers with fewer lexical
switches. Model A remains the strongest alternative and wins if future fixed-
page work shows that text position is independent of visible slot geometry.

## Compact provisional dictionary

The dictionary is functional. English expansions vary only where the pictured
role varies; that is contextual filling of one slot, not card-function
switching.

| form/construction | fixed anonymous function | source-class expansion | pictured completion | confidence |
|---|---|---|---|---:|
| exact `qokaiin` (`b5fcea1e…`) | ADDRESS/ENTRY HEAD | attend to, enter, use the current registered slot | active part, medium, path, station or setting chosen from the page frame | .46 formal; .31 source class |
| L/O (`dcda95c8…`) | LINK / CO-MEMBER | with, in, to, from, through, belonging with | relation determined by visible adjacency or current register | .39 formal; .26 source class |
| AIIN (`2f1c5e56…`) | PARAMETER / INDEX | stated degree, share, duration, stage or table value | scale is inherited from dossier/register | .28; only .12 for quantity alone |
| Y (`b921a237…`) | SLOT POINTER / ITEM TAG | this/other member, endpoint or marked item | referent supplied by a local visible or discourse slot | .27 |
| CTHY (`e0b630cb…`) | QUALIFIED STATE | prepared, conditioned, suitable, at-state | bearer supplied by active pictured part/station | .25 |
| exact close-bearing card | PAYLOAD + COMMIT | set/complete this local value | scope is the current short cell | .78 for commitment, no lexical value |
| free Y-like surface after wrapper removal | ordinary Y card | same POINTER function | not punctuation or closure | inherited formal distinction |
| `Y–AIIN–Y` | TWO-SLOT SHARED-SETTING FRAME | first member and second member under one stated setting | operands are two active picture/discourse slots | .34 construction; .12 equal amount |

### Function changes required

None of the six core entries changes anonymous function. Their fluent English
does change because silent arguments differ:

- L/O may surface as *with*, *in*, *to*, *from* or *through*; all are
  realizations of `RELATE(current slot, pictured slot)`.
- AIIN may be amount, degree, duration, stage or index; all instantiate an
  unspoken register-specific scale.
- Y may point to a plant organ, body/station, or prior item; all instantiate a
  slot pointer.
- `qokaiin` may be paraphrased *use*, *enter*, *at* or *for*; its fixed claim
  is only that it opens/reactivates an address frame.

If these contextual completions are counted as lexical senses, the model has
four highly polysemous words and should be rejected. Its claim is instead that
they are notation-like relation cards whose arguments are typed by the page.

## What may be silent on each fixed page

### Herbal dossiers

All four pages can omit `[this pictured simple]`. More specifically:

- `f10r`: the drawing has two visibly distinct leaf shapes and multiple
  clusters. It can license `[leaf/organ A]`, `[leaf/organ B]`, `[flower]` and
  `[whole simple]` as different silent slots without identifying the species.
- `f11r`: dense leaves, small flowers, a stem/root line, distinct leaf shapes
  and a flat-topped root license `[leaf mass]`, `[flowering top]` and `[root]`.
- `f55v`: a page-filling plant with very large upward leaves, composite root
  and dotted flower/fruit region licenses `[large leaf]`, `[root/tree-like
  base]` and `[flower/fruit above]`. This is the best Herbal page for a
  preparation-medium address because its Currier-B form resembles Bio
  production, but the picture does not show water.
- `f56r`: the palm-like base, two needle-bearing blue leaves, blue flowers and
  spiralling tendril license several unusually discriminable organ slots.

The text may still explicitly encode habitat or medium; neither is necessarily
drawn. The theory predicts a contrast: organ/part references should be more
elliptical than a nonvisible habitat, liquid, dose or timing instruction.

### Biological configurations

- `f81v`: `[large green pool]`, `[inlet]`, `[outlet]`, `[upper/lower row of
  figures]` and `[body in pool]` are recoverable visually. “Water” may be
  silent as the medium, but green color alone does not prove the substance.
- `f82r`: two upper figures with paired connections and a joining element,
  another differently connected pair, a lower green pool, and one separate
  blue pool offer explicit slots for body, vessel, path, junction and medium.
- `f83r`: a narrow vertical figure-bearing structure and two lower structures
  joined by a rainbow-shaped path offer station, path, paired endpoint and
  application/body slots.

This makes Bio fields resemble checked cells: the drawing supplies the row
object, while a close commits its undrawn setting or state. It does **not**
prove bathing, gynecology, alchemy, anatomy or hydraulic operation.

### Circle and astronomical lookup pages

- `f67r2`: a central star/cloud image, twelve outer segments, moon faces,
  segment-local red wording, local paragraphs and twelve star labels allow
  `[current segment]`, `[central anchor]` and `[segment phase/icon]` to remain
  silent. Month/zodiac and seven-planet readings remain tentative.
- `f68r1`: the sun, moon and 29 scattered labelled stars make the star's
  plotted position its address. A label need not repeat “star” or its spatial
  relation to the sun/moon.
- `f69v`: the central star, 28 inward radial entries, pipe-like openings and
  three outer circular texts make ordinal ray position and centre/periphery
  relation silent. A lunar-mansion identification is possible, not assumed.

The Astro prediction is consequently local: position itself carries timing or
configuration. The prose cards from Herbal/Bio are not imported into Astro.

## Consecutive real-field parses

### f82r.2–4: connected-pair configuration with a carried address

The real field division is:

```text
f82r.2  dchedy⟫ / qolchedy⟫ /
        qokain dy qokeedy⟫ / qokal lcheckhy lched
f82r.3  qokeey lcheckhedy⟫ /
        qokaly solkaiin chckhy qokaiin
f82r.4  qokaiin octheol chkeey ldy⟫ /
        oteey qokal sheckhy qoky
```

The image already supplies connected figures, two kinds of connection, a
junction, pools and bodies. A conservative source-class parse is:

```text
[current component/state] COMMIT /
[related component/state] COMMIT /
[set the current route] POINTER [value] COMMIT /
[relation/setting of the pictured assembly]

[configuration] [junction/path-state] COMMIT /
[set/relate] PARAMETER [qualified item] ADDRESS—
ADDRESS [pictured route/station] [configured item] COMMIT /
[second setting] [relation] [qualified item]
```

Fluent paraphrase, deliberately no more specific than the drawing supports:

> For the pictured connected assembly: fix the first local state; fix its
> related state; set the route at the stated value. Record the junction
> configuration. For the current addressed path—continued at the next physical
> line—apply the indicated setting to the pictured station and commit it; then
> record the second linked condition.

The repeated `qokaiin` is best treated as one logical address copied at the
margin. Counting it twice remains a literal alternative. Calling it WATER is
weaker: one occurrence pair cannot distinguish content continuity from a
catchword, and the Herbal occurrence has no drawn liquid owner.

### f83r.3: the two-slot setting construction

The real four-field line is:

```text
olkeedy⟫ / qotal chkeedy⟫ /
chey daiin chey lchedy⟫ / qokaiin qotal dar
```

Exact-card abstraction:

```text
[L/O-bearing payload] COMMIT /
[payload] COMMIT /
Y — AIIN — Y — [L/O-bearing payload] COMMIT /
qokaiin — [payload] — [payload]
```

The page shows a vertical station sequence and a lower joined pair. That does
not prove which drawing owns this line, but it supplies a plausible dyadic
frame. Source-class parse:

```text
[linked station state] COMMIT /
[second station value] COMMIT /
POINTER-A — SHARED SETTING — POINTER-B — LINKED STATE COMMIT /
ADDRESS [next/current pictured member] [residual value]
```

Fluent paraphrase:

> Fix the linked station state; fix the second value. Put this member and the
> other member under the same stated setting, and commit their linkage. Then
> address the next pictured member under the following value.

“Same stated setting” is safer than “equal amounts.” Bodies or endpoints can
share a duration, bath level, stage, route, quality or dose without being
symmetric substances.

### f10r.5–6: an Herbal stress test

The relevant real lines are:

```text
f10r.5  qokchy qotchol chol cthy
f10r.6  ycheor cthy chor cthaiin qoctholy dy chy taiin shy
```

GDT327 places all of each line in one open field. In `f10r.6`, the exact tail
contains a Y card followed by `Y–AIIN–Y`; CTHY is also present earlier. The
drawing independently offers two leaf shapes and multiple clusters.

Source-class parse:

```text
f10r.5  [unresolved head/item] — [relation] — L/O — CTHY
f10r.6  [item] — CTHY — [item] — [parameter-bearing item] — [relation]
         — Y — (Y — AIIN — Y)
```

Fluent paraphrase:

> For the pictured simple, note the linked part in its prepared condition.
> For the next item, record the conditioned part and its setting; this pictured
> member and the other pictured member share the stated parameter.

This is a risky visual reading, not a decoded recipe. Its virtue is that it
uses the same PARAMETER and POINTER functions as `f83r.3` while allowing the
picture—not the cards—to decide that the two slots are plant organs rather
than stations. Its weakness is that no text-to-leaf ownership is established;
the two distinct leaves may be artistically composite rather than functional
operands.

### f81v.17: a close-rich Bio stencil

The field stencil is `1C | 3C | 1C | 4O`:

```text
sshkchdy⟫ / chedy ol shedy⟫ / qolchedy⟫ /
qokain dl ral
```

Anonymous parse:

```text
[state] COMMIT /
[state] — L/O — [state] COMMIT /
[L/O-linked state] COMMIT /
[open setting/path specification]
```

Fluent paraphrase:

> In the pictured pool system, fix one local state; fix the related state in
> the medium/path; fix the linked outlet or station state; then leave the next
> setting open for continuation.

The words *medium*, *outlet* and *station* are supplied by the page frame, not
assigned to L/O or a closer. This parse would survive if the liquid were not
water and if the figures represented material states rather than patients.

### Astro pseudo-translation without imported prose cards

`f69v` contains three circular outer texts and 28 inward radial entries. The
radial entries include single-group and two-group labels, for example:

```text
f69v.4  okeey sar
f69v.5  okeo dy
f69v.6  ochoyk
f69v.7  ykeey
f69v.8  ytary
f69v.9  oeesy
```

The only justified continuous pseudo-translation is structural:

> [At radial setting 1:] local entry A; [at setting 2:] local entry B; [at
> setting 3:] local entry C; continue around the configured 28-place array,
> under the instruction or caption carried by the outer circular bands.

For `f67r2`, the twelve compartments similarly support:

> [For this compartment and its drawn phase/icon:] record the red heading,
> then the local conditions; repeat for the next compartment.

For `f68r1`:

> [At this plotted star address:] its local label; repeat across the field
> between the drawn sun and moon anchors.

These are layout readings, not translations of the surface forms. They show
that a drawn-address architecture can naturally make timing/configuration
silent without pretending that Astro uses the prose card dictionary.

## The six requested semantic forks

### Water, habitat and medium

These must remain distinct.

- Bio visually licenses a bounded colored medium on `f81v` and `f82r`; it does
  not prove the lexical card WATER.
- Herbal habitat is usually not drawn. A habitat claim should therefore need
  an explicit textual value and should not be silently completed from a leaf.
- A preparation medium may be inherited from a register routine even when not
  drawn. This makes “in the working medium” a possible source expansion of a
  LINK plus silent argument, not a gloss for `qokaiin` or L/O.

### Plant part

The strongest picture-address opportunity is not plant identity but contrast
among visible parts. `f10r` and `f56r` show multiple organ classes. Y is the
best weak pointer candidate; CTHY can predicate a state of the selected part.
Neither card means LEAF, ROOT or FLOWER.

### Vessel and path

Bio drawings provide bounded pools, connecting tubes/lines, a junction,
inlet/outlet and paired endpoints. L/O is a plausible abstract relation card,
while `qokaiin` can activate a path/station address. Neither means TUBE or
FLOW. The exact component label on the `f82r` cross-shaped element is formally
consumed as a whole and supplies no stripped lexical “tube name.”

### Body and application

Figures can silently fill patient, body-site, material-personification or
stage roles. The theory commits only to `FIGURE/STATION SLOT`. An application
reading becomes preferable if close-bearing fields align with distinct figure
contacts rather than merely with paragraph typography.

### Quantity and setting

AIIN is promoted slightly as `REGISTER-SCALE PARAMETER` and demoted as a
quantity word. Quantity is one possible scale in Herbal; level, duration,
stage or index may be more natural in Bio/Astro. `Y–AIIN–Y` says two slots share
or compare under one setting; it does not prove equal allocation.

### Timing

The circle pages supply local ordinal/cyclic position visually. Their labels
can omit “at the nth hour/month/mansion.” In Bio, timing would be an undrawn
parameter and thus a possible AIIN expansion. The theory predicts functional
analogy, not shared exact cards, across those namespaces.

## What survives, weakens or fails from V2

Survives:

- picture/page address is a real source of possible ellipsis;
- `qokaiin` is the best entry-head candidate;
- L/O is a broad internal relation candidate;
- exact closers are payload-bearing cards with a shared commitment behavior;
- free Y and attached DY behavior must remain distinct;
- Astro is a separate local lookup namespace;
- the `f82r.3–4` repeat is best parsed once as a carried logical head, locally.

Strengthens:

- Y becomes a slot-pointer candidate rather than an undifferentiated item;
- AIIN becomes a register-scaled setting/index rather than quantity by
  default;
- `Y–AIIN–Y` becomes a two-slot shared-setting frame.

Weakens:

- a spoken TAKE/USE imperative for `qokaiin`; ADDRESS/ACTIVATE is broader;
- generic “prepared property” for CTHY; its bearer is now explicitly supplied
  by an active picture slot;
- a single unified WHAT/HOW/WHEN dictionary. The integration is architectural,
  not lexical.

Fails:

- `qokaiin = WATER` or one universal medium;
- L/O = WATER, IN, WITH or any single English preposition;
- AIIN = AMOUNT as the default;
- Y = WOMAN, LEAF, STAR or any universal pictured noun;
- closure = punctuation or one fixed RESULT word;
- `Y–AIIN–Y = equal amounts` without independently symmetric operands.

## Strongest alternative lexicon

The best rival is a **substance/process lexicon**:

| form | rival reading |
|---|---|
| `qokaiin` | working matrix or liquid carrier |
| L/O | contact/inclusion in that matrix |
| AIIN | process exposure or quantity |
| Y | generic material/item |
| CTHY | processed/prepared condition |
| closer | achieved local product/state |

It gives fluent medical-alchemical prose and explains why `qokaiin` can carry
across a line as continuous material. It loses because `qokaiin` is strongly
field-initial, has nine different right neighbors, has no singly owned liquid
referent, and occurs on pictured Herbal `f55v` where water is not shown. It
also makes the same content noun do the work that address structure already
explains. The rival wins if fixed-page visual ownership places `qokaiin`
specifically at liquid-bearing components and not at dry/solid or route-only
components.

## Contradiction ledger

1. **No line-to-component ownership.** Every Bio paraphrase can currently be
   shifted to another nearby figure or conduit.
2. **Herbal compositeness.** Distinct drawn organs may be diagnostic collage,
   not two practical operands.
3. **Entry versus address.** A general imperative and an address opener predict
   nearly the same position for `qokaiin`.
4. **AIIN breadth.** A scale variable can hide unrestricted polysemy unless
   fixed-page neighbors constrain its admissible scales.
5. **Y frequency.** A pointer should correlate with repeated or contrastive
   roles, but current ownership annotations do not establish that.
6. **L/O English variation.** The abstract LINK class is coherent only if its
   two operands are more visually/structurally homogeneous than those around
   matched interior cards.
7. **Closers carry content.** Treating every close as merely “done” erases exact
   terminal identities and contradicts the best current grammar.
8. **Astro analogy is unscored.** Compartment and radial addresses are visible,
   but no exact prose-card transfer is available or claimed.
9. **The fluent translations contain silent nouns.** Their usefulness is
   explanatory only; they cannot count as recovered words.
10. **Possible nonsemantic alternative.** A visual pattern/exercise book can
    produce page-local stencils and repeated cards without denotation.

## Fixed-page predictions

These are deliberately risky and confined to the ten pages.

1. **Address diversity.** The nine exact `qokaiin` continuations should sort
   into more diverse item/relation families than frequency- and page-matched
   interior cards, while `qokaiin` itself remains entry-biased. Failure favors
   an ordinary content noun.
2. **Carry coherence.** Counting the `f82r.3–4` boundary repeat once should make
   the logical field more similar to other `qokaiin`-headed fields than
   counting it twice or attaching the first copy to the previous item list.
3. **Relation operands.** L/O-adjacent operands on fixed Bio pages should more
   often occupy compatible station/path/short-cell roles than operands around
   matched interior cards. No particular English preposition is predicted.
4. **Visible-part contrast.** The `f10r.6` and `f83r.3` `Y–AIIN–Y`
   environments should each admit two independently distinguishable local
   slots. If either environment is visually monadic, withdraw the two-slot
   reading.
5. **Parameter, not quantity.** AIIN neighbors should cluster with pointer/item
   cards across Herbal and Bio but need not correlate with visible multiplicity.
   A multiplicity-only result would restore AMOUNT; neither result would leave
   AIIN ungrounded.
6. **CTHY bearer.** On the fixed pages, CTHY should appear in fields that also
   contain or inherit an active pointer/item more often than matched portable
   cards. If it is equally common in empty/open heads, PROPERTY/STATE weakens.
7. **Commit locality.** After page and field length are held fixed, exact
   terminal identity may depend on the preceding construction, but all terminal
   families should retain the shared local-commit placement. A pure punctuation
   account predicts no identity dependence.
8. **Bio geometry versus typography.** If the drawn-frame model is correct,
   short closed cells near figure/path changes should be denser than in prose
   zones with no local geometric transition. If only Currier-B typography
   predicts closure, visual addressing loses.
9. **Herbal explicit-medium cost.** A nonpictured habitat/medium should require
   a longer or extra value-bearing construction compared with a silently
   pointed plant part. No exact card is preselected as HABITAT or WATER.
10. **Astro local order.** On `f69v`, the 28 radial strings should show stronger
    adjacency/alternation structure in physical ray order than under label
    alphabetization. On `f68r1`, spatial neighbors—not an invented cyclic
    order—are the proper comparison. On `f67r2`, within-segment text should be
    more structurally parallel across the twelve compartments than labels
    pooled across all three Astro pages.
11. **No universal picture gloss.** A card assigned LEAF, WATER, BODY, TUBE or
    STAR must fail if its exact occurrences cross an incompatible fixed-page
    picture class without a stable abstract relation. This is a hard rejection
    rule, not a request for contextual synonymy.

## Stopping rule

A fluent line is admissible only when every expressed element is tagged as one
of:

```text
P = independently pictured/inherited
F = formal card role
S = speculative source-class expansion
U = unsupported filler
```

The parse stops at the first `U`. A candidate does not gain coverage from
English articles, verbs, substances, body parts, plant parts, measures,
directions or temporal values unless they are P, F or explicitly marked S.
No card may acquire a new anonymous function merely to save one line. No more
than one unresolved source-class choice is permitted per field in a reported
continuous pseudo-translation. If two consecutive fields require different
functions for the same exact card, the passage is counted unparsed. Picture
proximity alone cannot upgrade S to a lexical claim.

Applied to the passages above, the maximal common paraphrase is:

> For the object and local roles already drawn, activate the current slot;
> relate it to another pictured or inherited slot under the stated parameter
> or condition; commit the local specification; carry the active address over
> a physical line when necessary.

That is a coherent source architecture. It is not Voynich plaintext.

## Bottom line

The drawn-argument model is the strongest picture-addressed V3 theory because
it explains visual richness, short Bio cells, cross-register core cards and
Astro layout with one mechanism while refusing universal picture glosses.
Its most useful semantic advance is narrow: `qokaiin` may open an address,
L/O may relate addressed slots, AIIN may set a register-specific scale, Y may
point to two slots, CTHY may qualify the active slot, and a closer may commit
the cell. The pictures then silently supply plant part, body/station,
vessel/path, medium or cyclic setting as appropriate.

The theory remains one ownership test away from collapse. Until a fixed-page
line is independently tied to a visible component, every fluent English
sentence above is a controlled pseudo-translation, not a decipherment.

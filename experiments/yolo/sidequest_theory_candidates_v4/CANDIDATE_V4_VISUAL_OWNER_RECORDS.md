# V4 candidate — drawn-owner and address grammar

Date: 2026-08-21

Status: **speculative sidequest candidate, not a GDT result and not a
translation**.

## Scope and evidence discipline

This candidate uses only the fixed Herbal/Biological pages `f10r`, `f11r`,
`f55v`, `f56r`, `f81v`, `f82r`, and `f83r`. The circle pages were not needed
for the record test. No `f84` or `f84r` material was opened. ZL3b supplies the
surface reading; exact-card identity and fields come from guarded GDT327 rows.
Alternate readings are not counted as additional witnesses.

The visual inventory is deliberately weak. The Herbal annotations establish a
single illustrated-simple page class but do not own a plant part to a line or
paragraph. On `f82r`, the permitted annotations establish upper connected
figures, linear connections, a lower green bounded region, and a separate blue
bounded region, but ownership of the prose records is unknown. On `f83r`,
later labels lie near figures, tube/arch ends, and structure outlets; two label
owners are explicitly ambiguous and none owns the opening prose records.

One source-handling correction is recorded here. A guarded query with
`joint_tuple_id` as selector was mistakenly allowed by tuple rather than by
page and displayed non-fixed, nonsealed rows. No off-scope row was retained,
counted, or used below; the fixed-page query was rerun correctly with `page` as
the selector and an explicit seven-page allow-list. No `f84*` row was
displayed.

## Visual-role freeze before record interpretation

These are candidate **silent roles**, frozen from the permitted visual facts
before assigning functions to cards in the selected records. They are not
picture glosses.

| selected record | owner | part | path | vessel/station | medium | ownership limit |
|---|---|---|---|---|---|---|
| `f10r` R1, lines 1–5 | pictured simple/page dossier | whole plant; an unspecified organ is possible | none pictured as an operational path | none | none independently pictured | the plant owns the page plausibly, but no organ owns a particular line |
| `f10r` R2, lines 6–12 | same pictured simple, reactivated at the paragraph start | same unresolved whole/part fork | none | none | none | paragraph inheritance is plausible; a change of plant part is not visible |
| `f83r` R1, lines 1–8 | page-local figure/apparatus system | figure, arch/tube end, or outlet are candidates | connection/arch is available page-locally | connected structure or endpoint is available | no independently owned liquid | no annotation ties the opening paragraph to one figure, tube, or outlet |
| `f83r` R2, lines 9–17 | same page system, with a new paragraph address | same candidate components | same connection system | same candidate stations/endpoints | unresolved; color/region is not a substance identification | paragraph reset is visible, but local visual ownership remains unknown |
| `f82r` R1, lines 1–9 (carry diagnostic) | upper connected system or page apparatus | one of the connected figures/components | two linear elements plus a joining element | upper/lower system or bounded region | green/blue region only, not WATER | the prose-to-system association is page-level; no line-to-component leader exists |

The only licensed role switches are therefore register- or paragraph-level:

- Herbal owner: pictured simple; Bio owner: a page-local figure/apparatus
  system.
- Herbal part: whole-versus-organ unresolved; Bio part: figure/component or
  endpoint unresolved.
- `PATH` and `VESSEL/STATION` are available only in Bio.
- `MEDIUM` is **unfilled** in Herbal and remains an unowned colored/bounded
  region candidate in Bio. It never becomes a universal WATER argument.
- A new paragraph may reactivate or change the current visual address, but the
  fixed annotations cannot tell which component it selects.

## Three competing grammars

### M1 — subject-only ellipsis

The picture silently supplies only “this plant” or “this apparatus.” All other
arguments must be in the card stream.

This is parsimonious for Herbal, but it does not explain why Bio can sustain
many short closed cells around a multi-component drawing without repeatedly
naming components, paths, or endpoints. It also gives the `f82r.3–4` boundary
repeat no special function beyond a copied entry head.

### M2 — drawn-argument addressing

The picture supplies a current owner and a small set of addressable local
arguments. Text selects or reactivates an address, relates pointers to it,
binds an opaque value, qualifies its state, and commits a local cell.

```text
RECORD := inherited PAGE_OWNER + ADDRESS_FRAME+
ADDRESS_FRAME := ADDRESS? + POINTER/RELATION/VALUE/STATE* + TERMINAL(COMMIT)?
ADDRESS := qokaiin  [activate or renew the current drawn/dossier address]
RELATION := L/O     [associate with the current owner, slot, or path]
VALUE := AIIN       [bind a parameter/index/reference; not necessarily amount]
POINTER := Y        [current item/endpoint anaphor]
STATE := CTHY       [property/configuration state of the active address]
```

The bracketed terms are source-class paraphrases. They are not English lexeme
assignments. Exact terminal cards retain opaque payload identity plus a shared
COMMIT realization; they are neither typed English results nor punctuation.

### M3 — text-only formula register

The page chooses Herbal or Bio stencils, but no drawn argument participates in
record interpretation. `qokaiin` is a formula entry marker, L/O a generic
relation, AIIN a parameter, Y a formal item tag, and CTHY a state.

M3 fits placement nearly as well as M2 and is the strongest losing model. It
cannot, however, say what repeated tags and relations range over, and it must
encode every Bio component distinction in otherwise opaque local cards. Its
pseudo-translation is consequently a template description rather than a
record addressed to anything.

## Fixed card mapping and awkward positions

The same M2 mapping is applied to every fixed-page occurrence: `qokaiin` 9,
L/O 19, AIIN 20, Y 18, and CTHY 7. No occurrence is discarded.

| card/construction | chosen role | attractive evidence | awkward evidence and treatment | role switches |
|---|---|---|---|---:|
| exact `qokaiin` | address activation/reactivation | 7/9 field-initial; nine different right neighbors | one medial use is renewal inside a frame; one field-final use is anticipatory carry/catchword, specifically licensed by the exact repeat at `f82r.3–4` | 0 lexical; activation timing switches initial/renewal/carry |
| exact L/O | owner-relative association/slot relation | 14/19 medial; repeated internal and pre-close use | first/last/only placements lexicalize an open or completed relation frame rather than changing to a substance | 0 lexical; frame completeness changes |
| exact AIIN | parameter/index/reference binder | occupies interiors and the center of `Y–AIIN–Y` | six FIRST and five LAST uses bar a narrow infix or quantity reading; a whole value frame may be opened or left at a boundary | 0 lexical; field scope changes |
| exact Y | anaphoric current-item/endpoint pointer | mostly medial; two dyadic frames | first/last positions allow a pointer frame to open or remain pending; free Y is not DY closure | 0 lexical; antecedent type switches plant/item/component/endpoint |
| exact CTHY | state/property qualification | 7/7 compatible with qualification and 6/7 medial | the one field-final case is a complete state frame, not a terminal closer | 0 lexical; bearer changes with active owner |
| `Y–AIIN–Y` | pointer–shared parameter/reference–pointer | exact path on `f10r.6` and `f83r.3` | `f10r.6` has an extra adjacent Y, and neither picture owns symmetric operands; therefore no “equal amounts” expansion | 0 constructional |

“Zero lexical switches” is achieved by keeping the roles abstract. Referential
fillers do switch, and all switches are exposed: Y can point to an inherited
plant/item in Herbal and to a figure/component/endpoint in Bio; CTHY qualifies
whichever address is active; L/O ranges over association, slot, or path because
the drawing supplies the second argument. If these are treated as universal
picture nouns, the model fails.

## Consecutive-record translations

Provenance codes are `P` independently pictured/inherited, `F` formal card
role, and `S` speculative source expansion. Opaque spans are left opaque; no
unsupported substance, action, body part, amount, or direction is inserted.

### Herbal pair: `f10r` R1 and R2

`f10r` R1 is the actual five-line paragraph `f10r.1–5`. It contains AIIN in
line 2 and ends with the exact L/O–CTHY sequence in line 5.

> **Pseudo-translation:** For the pictured simple [P], maintain its dossier
> address [S]. Bind a parameter/reference [F: AIIN] amid opaque descriptors;
> continue the open description. In the final line, associate the current
> item with its stated property/configuration [F: L/O–CTHY].

`f10r` R2 is the consecutive seven-line paragraph `f10r.6–12`. Its first line
contains CTHY and the exact tail `Y–AIIN–Y`, preceded by an additional Y; later
lines contain repeated L/O, AIIN, and Y cards.

> **Pseudo-translation:** Reactivate the same pictured-simple dossier [P/S].
> Qualify the current owner [F: CTHY], then set a pointer frame whose final
> three cards are pointer–parameter/reference–pointer [F: Y–AIIN–Y]; the extra
> adjacent pointer remains unresolved. Continue by associating current items
> [F: L/O, Y] and binding further parameters/references [F: AIIN] through the
> remaining open lines.

This is less fluent than “use equal parts”: the image establishes neither two
symmetrical plant parts nor a measure. M2 improves continuity by allowing the
same unspoken owner to survive the physical line breaks, but it does not
identify the preparation or use.

### Biological pair: `f83r` R1 and R2

`f83r` R1 is the actual eight-line paragraph `f83r.1–8`. Line 3 contains the
exact `Y–AIIN–Y` field, followed by a close-bearing payload, and then begins a
new field with exact `qokaiin`. Line 6 reuses exact `qokaiin` in a new field.

> **Pseudo-translation:** For the inherited page apparatus/figure system [P,
> owner uncertain], commit two initial local specifications [F]. Open a
> two-pointer frame under one parameter/reference [F: Y–AIIN–Y] and commit its
> opaque payload [F]. Activate the next drawn address [F: qokaiin], relate and
> configure opaque local entries, then activate another address [F: qokaiin]
> and commit the following cells [F].

`f83r` R2 is the consecutive paragraph `f83r.9–17`. Exact `qokaiin` begins a
field at `f83r.11` and again at `f83r.14`; the latter is followed immediately
by CTHY. AIIN begins the line-15 field, with Y and two CTHY occurrences later
in the record.

> **Pseudo-translation:** Renew the page-system address for the second record
> [P/S]. Activate a local station or component [F: qokaiin; referent unknown]
> and enter its opaque specifications. Activate another address and qualify
> its state [F: qokaiin–CTHY]. Open a parameter/reference frame [F: AIIN],
> point back to a current item [F: Y], apply further state qualifications [F:
> CTHY], and commit the remaining local cells [F].

The visual grammar improves this pair by giving “current,” “another,” and
“back” possible drawn antecedents. Those are controlled source expansions,
not recovered plaintext. It cannot decide whether the active referent is a
person, tube, outlet, bounded region, or abstract station.

### Boundary diagnostic: `f82r` R1

In the actual first paragraph `f82r.1–9`, exact `qokaiin` is the final card of
the second field on `f82r.3` and the first card of the first field on
`f82r.4`. This is the only exact same-record boundary-card repeat among the 46
fixed transitions reported by the current theory.

> **Pseudo-translation:** Announce the next drawn/dossier address at the end of
> the available line [F], then reactivate that same address at the new line
> [F] and supply its relation/configuration before committing the local cell.

M2 treats the pair once at the source level and twice at the rendered level.
The live alternatives are ordinary repetition and dittography. A continuous
working medium is not preferred because no colored region owns this prose and
the exact card has diverse continuations.

## Model comparison

The frozen V4 rubric is applied abductively, not as a statistical result.

| model | coverage /25 | continuity /20 | few role changes /15 | discrimination /15 | history /10 | controlled fluency /10 | predictions /5 | total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| M2 drawn-argument addressing | 23 | 18 | 13 | 12 | 8 | 8 | 4 | **86** |
| M3 text-only formula register | 23 | 15 | 14 | 8 | 8 | 6 | 3 | **77** |
| M1 subject-only ellipsis | 21 | 13 | 12 | 7 | 8 | 6 | 2 | **69** |

M2 wins because it resolves all six required constructions with one operator
mapping and gives the Bio short-cell register an economical source layer. It
does not win by identifying any pictured object. M3 remains the strongest
losing lexicon and should replace M2 if address-sensitive predictions fail.

The strongest losing lexicon is therefore:

```text
qokaiin = formula entry marker
L/O = generic relation
AIIN = parameter/value/index
Y = formal item tag
CTHY = state/property
terminal = opaque payload + COMMIT
```

The rejected working-medium fork would instead set `qokaiin = medium` and L/O
to a medium relation. It loses because the fixed pages provide no owned medium
for all nine exact occurrences, the card is field-first in 7/9 cases, and its
nine right neighbors differ. Literal WATER remains unsupported.

## Risky fixed-page predictions

1. In a fresh ownership annotation restricted to these pages, qokaiin-headed
   fields should occur preferentially where a paragraph or local cell can
   plausibly renew a drawn/dossier address; the f82r boundary pair should own
   one referent, not two substances.
2. L/O should fall between fields or cards whose candidate visual arguments
   are more homogeneous than those around frequency- and position-matched
   interior cards. Failure favors M3.
3. The two `Y–AIIN–Y` records should admit two addressable operands under one
   frame. If neither does, retract the dyadic reading and reduce Y to a formal
   tag.
4. CTHY should cluster in records where a stable owner can bear a changed
   state, without requiring the same pictured noun across Herbal and Bio.
5. Exact terminal identity may correlate with preceding construction after
   page and field length are held fixed, but no terminal family should map
   cleanly to a universal pictured object. A null result retains COMMIT and
   rejects typed terminal semantics.

## Decision and ceiling

Choose **M2 drawn-argument addressing**, with M3 text-only formula register as
the adversarial fallback. The gain is record-level economy: inherited owner,
part/path/station candidates need not be repeatedly verbalized, and the same
five abstract cards can operate across Herbal and Bio without becoming picture
nouns. The cost is substantial referential uncertainty, explicitly preserved
at every record.

No English lexeme, plaintext clause, plant, substance, action, amount, disease,
body part, direction, or apparatus function is identified. The result is a
provenance-controlled source-class paraphrase, not a translation.

# Joint comparative grouping: owned source and prospective constraint

2026-09-15; bounded resumed pipeline, checkpoint 15:05 UTC.
Status: RAW_UNREVIEWED_NOT_SELECTED. No target cache, new image or decoder.

This proposal learns comparative phrase grouping, participant references and
relation meanings together. Its content restriction is a signed comparison on
one identified part and axis, alongside a separately scoped resemblance claim.
It imposes no paragraph header, source order, fixed number of fields, literal
three-word frame or whole-source copy. The comparative submodel is concrete;
the complete unknown-text writing contract is not yet frozen. It is a raw
whole-reading constraint proposal, not an already executable target experiment.

## Exact owned source and occurrence independence

The sources are Dioscorides, De materia medica I.1, I.2 and IV.20, in the
existing Wellmann Greek digital edition (print edition 1907–1914; ancient work
usually dated to the first century CE). The existing source audit retained
Greek terms, uncertainties and all main-text content. No new source was fetched.
The original XML [public source](https://raw.githubusercontent.com/OpenGreekAndLatin/First1KGreek/master/data/tlg0656/tlg001/tlg0656.tlg001.1st1K-grc1.xml)
has SHA-256 `e2a2175c5ca1c1a2313c5816bc79c7fa1c9103766fcad193356d0c13ce6746bc`.
These are three distinct main-text passages in one edited work, not three
independent manuscripts or independent confirmations of the author's botany.
The three full chapter texts were reread; complete bytes remain in the raw
proposal as well as in the existing caches.

I.1 begins with this complete descriptive sentence, including the flower and
name-explanation content rather than silently truncating it:

> ἶρις Ἰλλυρικὴ φύλλα φέρει ὅμοια ξιφίῳ, μείζονα δὲ καὶ πλατύτερα καὶ λιπαρώτερα, ἄνθη ἐπὶ καυλῶν παράλληλα, ἐπικαμπῆ, ποικίλα· ἢ γὰρ λευκὰ ἢ ὠχρὰ ἢ μήλινα ἢ πορφυρᾶ ἢ κυανίζοντα ὁρᾶται, ὅθεν διὰ τὴν ποικιλίαν ἀπεικάσθη Ἴριδι οὐρανίᾳ.

The plant's leaves resemble ξιφίῳ but are larger, broader and fleshier. Flowers,
their position and colour alternatives follow; the final Iris-of-the-sky
comparison explains the name. That celestial Iris is not another plant
reference. The cache is [Wellmann_I_1.txt](dioscorides_cache/Wellmann_I_1.txt),
SHA-256 `f33747322f44a6a55c0648a799b3566e318cac898edab1c3d8e146a654904774`.

I.2's complete opening sentence is:

> ἄκορον τὰ μὲν φύλλα ἔχει ἐμφερῆ ἴριδι, στενότερα δέ, καὶ τὰς ῥίζας δὲ οὐκ ἀνομοίους, διαπεπλεγμένας δὲ καὶ οὐκ εἰς εὐθὺ πεφυκυίας, ἀλλὰ πλαγίας καὶ ἐξ ἐπιπολῆς, γόνασι διειλημμένας, ὑπολεύκους, δριμείας δὲ τῇ γεύσει καὶ τῇ ὀσμῇ οὐκ ἀηδεῖς.

Acoron's leaves resemble Iris but are narrower. Its roots are then described
as not unlike, with separate arrangement and qualities. The narrower predicate
does not silently spread to roots. Later in the same chapter “as Iris” belongs
to a sitz-bath use comparison; that is not another width edge. The complete
[Wellmann_I_2.txt](dioscorides_cache/Wellmann_I_2.txt) has SHA-256
`4ebd50b1d5bf899ba4c995f5c7f2b49f5d7106e46b1d900a475d60ac56931bc2`.

IV.20's full opening naming/comparison unit, up to the next explicit stalk
description, is:

> ξιφίον· οἱ δὲ φασγάνιον, οἱ δὲ μαχαιρίωνα καλοῦσι διὰ τὸ τοῦ φύλλου σχῆμα· ἔοικε γὰρ ἴριδι, ἔλαττον ὂν καὶ στενώτερον, ἄποξυ ὡς μαχαίριον, ἰνῶδες·

The named ξιφίον has two reported alternative names, explained by leaf shape;
it resembles Iris but is smaller/narrower, sharp like a small knife, and fibrous.
The opaque I.1 form ξιφίῳ is linked to IV.20 ξιφίον by the existing philological
audit. It is not normalized to a literal sword or a modern species. These
reported names are aliases within one source entry, not additional independent
plants. The complete [Wellmann_IV_20.txt](dioscorides_cache/Wellmann_IV_20.txt)
has SHA-256 `b67c0a0a9276f5cfcbf5fcf5314d394e8f3f008b77692812c4554ce602758a0b`.

The complete source inventories remain
[DIOSCORIDES_FIRST3_SEMANTIC_SOURCE.json](DIOSCORIDES_FIRST3_SEMANTIC_SOURCE.json)
and [DIOSCORIDES_XIPHION_SOURCE.json](DIOSCORIDES_XIPHION_SOURCE.json).
They retain preparation, application, reported efficacy, uncertain Greek terms,
and all later clauses. The new comparison module does not claim to translate
those chapters while discarding their other content.

## Part scope is a real branch, not a convenient resolution

I.1 and I.2 explicitly name leaves. In IV.20 the comparative subject is neuter
ξιφίον, immediately after a leaf-shape explanation; an explicit leaf noun is
not repeated as comparative subject. Preserve two prospective source readings:

- **Leaf ellipsis:** smaller/narrower continues the leaf comparison. I.1 and
  IV.20 then describe inverse leaf-width relations on the same named pair.
- **Broader plant-shape scope:** IV.20 compares the plant's general form. Its
  width/size claim must remain on a separate scope unless part alignment is
  justified; no exact leaf-width inverse closure is claimed from it.

These branches are philological uncertainty, not knobs selected to improve a
target score. Larger/smaller, broader/narrower and fleshier are distinct axes;
they are not merged into one generic “more” value. Resemblance is not equality
of width or identity of plants. No transitivity or universally symmetric
linguistic use of “resembles” is assumed merely from its name.

## Proposed joint constraint, with a source-only wrong-reading consequence

The semantic kernel uses typed participant, part and axis nodes, plus
`COMPARE(axis,sign,part(x),part(y))`, `RESEMBLES(scope,x,y)`, and conjunction
with explicitly unified shared arguments. It admits a part expressed with
its owner or carried once across a coordinated predicate list. That carried
argument must resolve to the same node in every conjunct under one shared rule.
New parts, meanings and exception contexts cannot be invented for an occurrence.

The proposed learning unit is a complete paragraph or entry with latent
constituent boundaries inside its preserved written-group sequence. Candidate
part/owner attachment, comparison argument order, signed relation and any
shared-argument coordination are selected jointly. A global lexical/realization
rule must recur across the complete accounts; an individually chosen meaning
for each phrase is inadmissible. An inverse relation may be written through
argument order or through a different comparative form. This proposal does
not require a new literal inverse marker or equate surface reversal with
semantic inversion. Precise finite lexical/realization alternatives still need
registration before a target search; no such search is selected here.

Let I, X and A denote the three source plant referents. Under leaf ellipsis,
the actual source constraints normalize to:

```
width(leaves(I)) > width(leaves(X))     I.1
width(leaves(X)) < width(leaves(I))     IV.20, conditional leaf scope
width(leaves(A)) < width(leaves(I))     I.2
```

The first two make one order fact in inverse wording, not two independent
inequalities or confirmations. The third adds a different named participant.
Both strict total orders `X < A < I` and `A < X < I` are possible; X and A may
also have equal widths. No X/A ordering is supplied. Consistent renaming,
order-preserving rescaling and the unresolved scope branch survive.

A rival that reads the second comparative with the same positive direction
while retaining its X-to-I arguments demands X>I as well as I>X. It produces
a strict cycle and fails under the leaf branch. A rival that merges resemblance
with width equality also fails because the same source pair resembles and
differs in width. These are content contradictions after one shared grouping
and role assignment, not tests of whether two opaque strings happen to swap.
The broader-scope branch does not license the first contradiction across
different part axes; retaining this limitation prevents false closure.

The smallest prospective target consequence is likewise conditional but
concrete: two linked descriptions of the same owned participants and the same
part/axis must retain the opposite order relation when their argument roles
reverse. A separately observed part comparison could fix the sign and reject
the globally reversed interpretation. Cross-page drawings do **not** establish
absolute width unless their scale relation is justified; leaf aspect ratio is
not silently substituted for the source's width. No such target owner or scale
was inspected or selected here. A coherent joint hypothesis can begin without
a confirmed word, while its observable ownership/scale assumptions remain
explicit. All remaining text must be accounted for in a later complete grammar;
unmodeled groups cannot be hidden as explanatory padding.

## Primary predecessors and retained counters

The live route, recipes topic, bounded searches and comparative/inverse and
joint-grouping route-checks preceded this card. Full primary reads included:

- [GDT918](../../../experiments/yolo/gdt918_reciprocal_center_serial_transfer/REPORT.md):
  its primary literal reciprocal-center nomination stopped on capacity; there
  was no even-leaf evaluation. Its fixed literal triples are not relaxed here.
  Joint signed comparisons are different content, not a rescue of those triples.
- IDEA000050's complete review: direction may be encoded by argument order;
  an obligatory inverse marker cannot be inferred. Its missing specified
  contrast remains. No old `ol` meaning is adopted.
- IDEA000006's complete review: disjoint contextual realizations and finite
  sampling can defeat observed reciprocal frame transfer despite shared meaning.
  No observed frame-equality requirement is introduced.
- [GDT386](../../../experiments/yolo/gdt386_independent_relation_edge_capacity/REPORT.md):
  its owned parent-edge capacity stop stands; local geometry and similar plant
  drawings are not authorial cross-record reference arrows.
- [RTA001](../../../experiments/semantic_assumptions/results/rta001_result_report.md):
  positive formal held gains did not beat its registered wrong-pairing test
  (p=0.888428). A future joint comparison model must retain a rival that preserves
  graph/topological structure while changing the semantic endpoint assignment;
  compression of relation patterns alone would not identify meaning.

The parked source-copy and fixed-header families remain parked or closed;
Greek source ownership is no license for a Greek phonetic code. This new raw
card supplies a concrete typed inverse-comparison consequence and complete
source clauses. It makes no target selection, morphology fit, meaning claim,
capacity estimate or permission to reopen reserves.

Access disclosure: the requested route/decision and historical primary reports
contain already published target excerpts. Those reports were read for claim
scope; no fresh blindness is claimed. No raw target corpus, cached target row,
target image or reserved material was opened. Existing source/proposal bytes
were not changed.

# Galen III.13: intake for an owner, compartment and nutritional-case frame

Source-only intake, 27 September 2026. Started 03:52:34 UTC; hard ceiling
04:07:34 UTC. This is a distinct candidate assessment, not a change to the
frozen origin critique or a target-word proposal. Inputs are the current route,
the complete already-owned III.13, and `GALEN_ORIGIN_SOURCE_CRITIC_A.md`.
No target table, word assignment, new source, image, reserve, contact,
registry/state or Git action was used.

**Decision: source-content feasibility is positive, with a narrower claim than
architectural identification.** The connected nutrition account supports
stomach-to-liver and liver-vein-to-stomach supply with different supplier
owners. Its exclusion of appropriated liver material makes compartment and
nutritional status consequential. The later spleen case adds another supplier,
but its transfer is modal and its precise compartment and nutritional phase
are unspecified. These are substantive reusable relations; they do not prove
that a ContentFrame, rather than an ordinary guarded FROM relation, is the
representation employed. A writer is not selected by this intake alone.

## What the candidate can and cannot preserve

The proposed frame can keep an explicitly supplied organ owner, nutritional
case, material description, and distinction between available contents and
material appropriated to that organ. Withdrawal can then use this stored
information while taking a separately expressed recipient, guard, quantity and
modal status. This requires no inverse from an arbitrary material predicate.

There is a consequential granularity issue. In the fasting example, the organ
owner is liver, but the immediate withdrawal site is the **cavity of veins in
the liver**. Calling the whole liver the immediate site would erase the very
contrast the passage makes. The organ and its owned compartment must therefore
remain distinguishable. “Supplier organ = stored organ owner” is a defensible
coarse projection; “immediate source site = organ owner” is not the complete
source assertion. Nor does owner mean maker, ultimate origin, residual origin,
or owner of the material after a transfer.

A withdrawal record may retain its source owner while separately naming the
recipient. It must not thereby leave transferred material permanently located
in the source organ. Later presentation to a recipient is a separate assertion,
not an automatic overwrite of a source frame or a silent identity of cases.

The source has genuine, limited material anaphora: what was presented to the
stomach becomes adherent there and is subsequently assimilated; previously
presented material in liver and intestines likewise proceeds to adhesion.
This licenses continuity within those stated nutritional trajectories. It
does not identify one physical portion across every transfer, alternative
feeding case, organ, or spleen-processing episode.

## Actual repeated relations and their different arguments

Local paragraph numbers below refer to the fixed whole-chapter extraction,
not additional canonical subdivisions.

| Source case | Stored content and owner | Withdrawal/supply assertion | Consequence and limit |
|---|---|---|---|
|III.13, P18, p.309: first proposed period|Stomach; first-period digestion/presentation; aliment remaining in the stomach.|Some is taken from stomach to liver, within the explicitly imagined nutritional schedule.|Stomach and liver are distinct endpoints. Later liver presentation cannot be attributed to the stomach merely because stomach was the supplier. Source language separates contents from the coats receiving nourishment; calling these contents luminal is an interpretation of that distinction, not a separately quoted anatomical label here.|
|P20–21, p.311: no new meal after the three periods|Liver as organ owner; cavity of its veins; available juice; fasting/need case.|Stomach draws from liver veins, with mesenteric veins also named. Available venous juice is taken by the stronger, needier part.|This is the reverse organ-level direction. It is a conditional nutritional account, not an observed transfer of the identical earlier portion. Both source and recipient must remain available to describe reversal.|
|P20, p.311: contrasting unavailable material|Liver; already appropriated material in adhesion/assimilation; actual organ body, including flesh and vessels.|The proposed stomach withdrawal is expressly not from this material/body in this case.|The same coarse owner does not license the same withdrawal. A bare organ-name projection loses an explicit positive/negative distinction. The negative concerns withdrawal, not unsuitability for stomach or exclusive material origin.|
|P21, pp.311–313: processed spleen supply|Spleen; matter worked up from thick-leaning material received from liver; precise compartment and nutritional phase unstated.|Some may be drawn to venously connected organs, including stomach. Spleen surplus may go to stomach at one time; appropriate spleen nutriment may be drawn from stomach at another.|This is another source owner and a temporal reversal, but neither an actual completed event nor evidence of a splenic lumen in this sentence. Processing does not erase the preceding liver relation.|

Thus the first two positive rows already give two supplier owners. They are
not two instantiations with every other argument fixed: recipient, period and
guard vary too. That is adequate for an exploratory repeated transfer
construction, but not a controlled demonstration that changing only an owner
field caused a different output.

The spleen row cannot be forced into a schema requiring every material to be
either explicitly luminal or explicitly adherent/assimilating. A frame may
retain the stated nutritional case without inventing one of those phases; if
the proposed type instead requires a known phase and one of only those two
compartments, this row has an exact missing input. The same caution applies to
assigning a precise local nutritional phase to mesenteric-vein contents.

The source also repeats a separate owner-sensitive nutritional progression:
presentation, adhesion and assimilation. Stomach and liver enter these phases
at different periods. This strengthens the usefulness of retaining organ and
case together. It does not make phase advancement an automatic consequence of
withdrawal, nor put all material in an organ at one phase: available vessel
contents coexist with material already being appropriated.

## What later statements actually need

1. **The phase schedule needs organ ownership.** In the third period stomach
   assimilation and liver/intestine adhesion coexist. After a new meal,
   stomach presentation coexists with their assimilation and peripheral
   adhesion. Replacing these owners with one constant would change the
   assertions, rather than merely their notation.
2. **The fasting exception needs compartment and status.** Liver ownership
   alone cannot distinguish withdrawable venous juice from material already
   appropriated to liver. The source supplies the distinction, but a proposed
   frame/withdrawal grammar must still state how it uses it; simply storing a
   field does not enforce an exclusion.
3. **The conclusion needs both endpoints and time.** P22's return through
   previously reverse-used vessels depends on liver/spleen versus stomach and
   on different times. It does not identify one transfer event or one unchanged
   material token going out and back.
4. **The spleen continuation needs processing and modality.** Its prior liver
   supply and subsequent processing explain the offered possibility of onward
   supply. Keeping only a generic material name drops content, but retaining
   a spleen supplier does not by itself preserve the prior processing claim.

These are genuine dependencies of the stated content. The source does not
require that they be implemented as projections from a stored computational
object. Explicit relational statements with ordinary anaphora can retain them.

## Strong rivals, without importing the failed origin identification

**One globally constant supplier.** A withdrawal construction whose only
supplier output is liver cannot itself state the stomach-to-liver case or
spleen-to-stomach possibility with their named sources. It is inadequate if
these cases must all be assertions of that one construction. Nevertheless,
an author could put the other FROM assertions elsewhere and leave this
operator constant. The whole source alone does not forbid that allocation;
an eventual written-construction comparison would need to own those uses.

**A supplier constant within each case.** If a case index independently
encodes its supplier, a function that ignores the owner field could recover
the right supplier from the case. The source's cases correlate with their
named owners, so the existing narrative does not exclude this possibility.
Counting case-specific supplier stipulations is necessary before claiming
compression. Merely assigning a different case name to each example is no
argument for dependence on a stored owner.

**Generic FROM(location).** This is the strongest content-compatible rival.
A FROM relation whose location is an owned compartment, with explicit
recipient, material restriction, nutritional case and modality, can express
every transfer above. Separate phase assertions can express appropriation and
its exclusion. It need not confuse anatomical containment with tissue
appropriation. A coarse FROM(liver) alone loses the p.311 distinction, but
the stronger relational rival does not. Packing the same arguments into a
ContentFrame may be useful composition; without actual written sharing it is
only a change of representation, not a source-discriminated hypothesis.

No rival is rejected by calling transferred matter RESIDUE_FROM its immediate
supplier. No equivalence of TRANSFERRED, PROPER, USEFUL and NOURISHING is used.
No possibility is promoted to actuality. The adverse cases elsewhere in the
chapter also prevent a universal claim that every transfer is nutritional or
that every appropriate material is available to every needy part.

## Smallest complete consecutive source unit

Use **III.13, local P15–22, printed pp.307–313**, the complete connected
nutrition-period account with its opening timing qualification and concluding
common-stock/reversal argument. This is the previously owned 6594-byte unit.
It is smaller than the chapter, but not just the attractive p.311 exclusion
and p.313 spleen sentences. P18–20 cannot be detached from the preceding
presentation/adhesion/assimilation explanation; P21's continuation and P22's
conclusion must remain. The complete chapter has also been read, and this
bounded unit is not called full-chapter equivalence.

Every substantive obligation in that chosen unit is retained below:

| Unit | Complete content obligations |
|---|---|
|P15, p.307|Rapid reversal in the named respiratory/cardiac structures versus sometimes many-day reversal in veins between liver and stomach/intestines.|
|P16, pp.307–309|Each organ draws nearby food, takes useful fluid to satiety, stores it, then makes it adhere and assimilates it; presentation precedes adhesion, which precedes actual nutrition. Presentation fills the part with its appropriate liquid. Parts grasp food as stomach does. Stomach's action brings digestion, but is not deliberately undertaken to prepare food for other organs; the author rejects that rational-purpose attribution.|
|P17, p.309|Attraction/utilisation and food alteration coexist. After saturation, stomach treats excess as burden and drives it down while its own adhesion proceeds. Intestinal transit is taken up mostly by veins and a little by arteries, with presentation to intestinal coats.|
|P18, p.309|The three periods are explicitly an imagined explanatory division. First: gastric digestion/presentation to satiety; some uptake from stomach to liver.|
|P19, p.309|Second: passage through intestines, presentation to intestines and liver until satiety, a little dispersal to the body, and adhesion in stomach of previously presented material.|
|P20, pp.309–311|Third: stomach assimilation of adherent material, liver/intestine adhesion, peripheral dispersal/presentation. If another meal follows, stomach again digests/presents to its coats, liver/intestines assimilate, peripheral parts undergo adhesion. If instead stomach remains unfed, it draws from mesenteric/liver veins. Actual liver body is excluded; the definition includes flesh and contained vessels. Material already appropriated, especially during adhesion/assimilation, is distinguished from available venous-cavity juice taken by the stronger and needier part.|
|P21, pp.311–313|Needy, unfed stomach obtains from liver veins. Spleen takes thick-leaning liver material and works it into more useful matter. Some could be drawn to venously connected omentum, mesentery, small intestine, colon and stomach. At different times spleen may discharge surplus into stomach or draw appropriate spleen nutriment from stomach.|
|P22, p.313|General attraction/addition at different times; common food-stock analogy includes simultaneous or successive feeding, stopping and beginning, and taking from another with ready abundance when oneself needy. Conclusion permits inward return from body surface and liver/spleen-to-stomach movement through vessels used in the opposite direction.|

The surrounding chapter retains conditional need/relative strength, disease
and nonnutritive surplus transfer, and explicit rejection of simultaneous
opposite traffic as the intended claim. The following P23 returns to
cardiac/arterial cavities, imperfect valve closure and reflux, not an
unqualified modern circulation model. These surrounding claims are context
and limitations, not additional mandatory content silently added to the
chosen P15–22 synopsis. Conversely, the selected synopsis cannot be advertised
as accounting for all of them.

## Minimum content commitments and decision consequence

A nontrivial version must explicitly distinguish: organ owner from owned
compartment; material description from a particular material witness;
appropriation phase from mere location; each nutritional case from another;
source from recipient; partial quantities from whole stocks; possibility from
asserted conditional consequence; and different times from simultaneous
traffic. The source motivates all these distinctions, but does not specify
their written encodings. Unknown spleen phase/compartment must remain unknown.

At the content level, the smallest meaningful reuse challenge is a single
withdrawal construction instantiated with stomach and liver supplier frames,
plus the liver-body exclusion and the two-owner phase continuation. The
spleen possibility remains a whole-unit obligation with its qualifications;
it cannot serve as an unqualified third positive event. Shared data must be
used in a later statement, not merely stored under an English field name.

This is a viable **content inventory for a distinct exploratory construction**,
not the unchanged568 residual-origin extension. It gives more than a second
supplier synonym. It does not, by itself, justify another freely assigned whole
glossary: the strongest generic-FROM account remains equally compatible. If
an eventual author cannot expose actual reused ownership/compartment/case
arguments in written constructions, park that writer instead of counting
record notation as compositional savings. No target feasibility judgment or
target selection is made in this source-only intake.

## Receipts and limits

Primary: Galen, *On the Natural Faculties* III.13, 1916 Loeb English translation,
[complete chapter](https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Galen/Natural_Faculties/3%2A.html#R13).
This is the owned translation, not a medieval witness identification, Greek
collation, or claim of present clinical truth. The cached transcription's
not-proofread qualification remains; no conjectural wording is needed here.

Cache: `external_cache/galen3_frame_source.html`, 102400 bytes, SHA256
`1d0f8547ae087a7c97d36f7600cee05dbb1b3321beb973b3065bba2ea8b0ad24`.
Whole III.13: P containing `NAME="R13"` through before P containing `NAME="R14"`,
23 paragraphs, byte interval [61437,83302), 21865 bytes, SHA256
`8ace19b2282c478696b8d86a60bb8c4818d54a4d04720e8dc3d879093dc412e0`.
Its printed-page sequence spans 289–315.

Selected P15–22: byte interval [75314,81908), 6594 bytes, SHA256
`2dd0e03d49716cad9d5c4028801c253e3d3e0d6c427fb3ed97197e0c935dcd96`.
Starts with the P marked `ID="p307"`; stops before the final arteries/heart
paragraph. Extraction used read-only local HTML/text bookkeeping; no source
or target payload was downloaded or modified.

Frozen earlier critique SHA256:
`285d95ae1a2b173bb716c407d1e0f8ef144cf33aee0fc453880545bde814ad0f`.
It remains unchanged. This intake narrows a different construction and does
not alter its negative judgment on default RESIDUE_FROM or constant-on-D
discrimination for the old candidate.

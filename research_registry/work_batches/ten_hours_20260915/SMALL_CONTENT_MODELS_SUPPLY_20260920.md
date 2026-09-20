# Three bounded small content models

Status: `RAW_UNREVIEWED`, source/constructor supply only (2026-09-20). No
Voynich target text, image, reserve, mixed TSV, decoder, experiment, ledger,
route or publication was opened or changed here. These are finite historical
content constructors that could later be paired with an already exposed whole
passage; none assigns a target word or claims independent meaning.

The live route and the `composition`/`transfer` topics were read first. The
screen used `./vmanus-exp route-check`, bounded `ideas search`/`ideas
duplicates`, and the claim-bearing source packets named below. Structural
word-part reuse remains a constraint, not a semantic gloss.

## A. Euclid I.5: equal sides produce two coupled angle equalities

**Primary.** Euclid, *Elements* I.5, complete proposition and demonstration in
the Heath-derived text at
<https://www.euclids-elements.org/elements/books/bookI/propositions/propI5/>
(especially the stated construction and proof steps). The report-owned
predecessor `research_registry/proposals/raw_f77r_euclid_proof_references.json`
and IDEA383 cover Euclid I.1's equilateral construction; this model uses the
different I.5 invariant that joins interior and exterior base-angle results.
IDEA125's general straightedge/compass program remains a broader predecessor,
not evidence for this particular proposition.

### Complete finite constructor

The source's argument types are `POINT`, `SEGMENT`, `ANGLE`, `TRIANGLE`,
`EQUAL`, `EXTEND`, `CUT_EQUAL`, `JOIN`, `SAS_CONGRUENCE`, `WHOLE_MINUS_REMAINDER`,
and `CONCLUDE`. The source-owned clause sequence is:

1. Introduce isosceles `ABC` with `AB = AC`; extend `AB` to `D` and `AC` to
   `E`. The target claims are `angle(ABC)=angle(ACB)` and
   `angle(FBC)=angle(GCB)` after the auxiliary construction.
2. Choose `F` on `BD`; cut `AG` from the longer `AE` so `AG = AF`; join `FC`
   and `GB`.
3. Use `AF=AG`, `AB=AC`, and the common included angle at `A` to derive
   `triangle(AFC) ≅ triangle(AGB)`. Carry out the source's consequences:
   `FC=GB`, `angle(ACF)=angle(ABG)`, and `angle(AFC)=angle(AGB)`.
4. Subtract equal segments from equal wholes to derive `BF=CG`.
5. Use `BF=CG`, `FC=GB`, and common `BC` to derive
   `triangle(BFC) ≅ triangle(CGB)`, hence
   `angle(FBC)=angle(GCB)` and `angle(BCF)=angle(CBG)`.
6. Subtract the equal inner pieces from the equal whole angles to conclude
   `angle(ABC)=angle(ACB)`, while retaining the separately proved exterior
   equality `angle(FBC)=angle(GCB)`.

The deterministic reduction must reject a missing `F`, `G`, extension, or
common-side identity; it may not replace one with a nearest point. Global
renaming of points, reflection, and scale remain symmetries.

### Nontrivial consequence and rival

The same `AB=AC` input carries two distinct outputs: the inner base-angle
equality and the equality of the angles under the produced sides. Swapping the
two base endpoints preserves both only if all endpoint and extension roles are
swapped together. A flat “equal-side pair” label can predict the first output,
but cannot derive the second without the auxiliary `F/G` construction and the
two congruence steps. The named rival is therefore **R-I5-flat**: store only
`AB=AC -> ABC-base-equality`, leaving the exterior result as an unbound
assertion. A future target contrast would require one fixed writer to reuse the
same endpoint parts in both equality chains; no target binding is currently
owned.

**Strongest failure.** The admitted target could lack any independently owned
point/angle relations, or its repeated components could not express the
auxiliary construction without local exceptions. That would leave this source
model exploratory, not refuted by an absent target binding.

## B. Aristotle *Physics* II.8: regular end-directed sequence versus incidental result

**Primary.** Aristotle, *Physics* II.8, Bekker 198b10–199b33, complete chapter
at the Internet Classics Archive:
<https://classics.mit.edu/Aristotle/physics.2.ii.html>.
The source packet is not a target translation and no modern purpose gloss is
imported. The nearest retained cards are IDEA030's generic causal-connector
question, IDEA322's different zoological vessel account, and IDEA327's
*Tabula smaragdina* process analogy; none owns this natural-purpose versus
incidental-result distinction.

### Complete finite constructor

Use typed values `SERIES`, `END`, `MATERIAL_CONDITION`, `REGULARITY`,
`INTERFERENCE`, `AGENT_CAPACITY`, `RESULT`, and `CAUSE_KIND`. The chapter can
be reduced without adding an unspoken universal law:

1. Register a natural series and its proposed completion. The objection gives
   a material/necessity chain: drawn-up vapor cools, becomes water, descends,
   and a crop grows; a spoiled crop is a different resulting consequence.
2. Mark whether the result is regular or occurs only incidentally. The
   chapter's teeth example supplies a purpose challenge; its answer invokes
   regular or usual natural formation rather than one accidental occurrence.
3. If the series reaches the same completion regularly and no impediment is
   present, emit `FOR_END(series,end)`. The examples are leaves providing
   shade, roots descending for nourishment, and animals making nests/webs.
4. If an external event produces an end-like result without being undertaken
   for that end, emit `INCIDENTAL(result,cause)`; do not rewrite it as a
   deliberate `FOR_END`. A human agent capable of deliberation is additionally
   required for the narrower `CHANCE` label; lower animals/inanimate cases may
   be `SPONTANEOUS` under the chapter's distinction.
5. If an impediment or failed formation appears, emit `FAILED_ATTEMPT(series,
   intended_end)` and retain the intended end; do not erase the end because the
   outcome failed. Material conditions enable a result but are not thereby its
   final cause.

### Nontrivial consequence and rival

The same broad rain-to-crop chain can have different typed relations: ordinary
regular growth supports `FOR_END(rain-series,crop)`, while a one-off spoiled
crop remains `INCIDENTAL(spoiled-crop,rain)`. A model that labels every result
as its purpose (R-II8-result-purpose) predicts the same relation for both and
loses the chapter's counterexample. A model that labels every natural sequence
as chance loses the regularity and no-impediment steps. The observable content
contrast is therefore a relation/state change over a shared event, not a name
or quantity change.

**Strongest failure.** Without a fixed target constructor for regularity,
impediment, and cause-kind, this can collapse into arbitrary post-hoc labels.
The future writer must expose these arguments globally; no target word is
treated as a confirmed operator here.

## C. Phaedrus I.1: rebutted allegations do not become true through the outcome

**Primary.** The complete fifteen-line *Lupus et Agnus* text and inventory are
already owned in
`research_registry/work_batches/ten_hours_20260915/DISCOURSE_CONSTRAINT_RAW_SOURCES_20260920.json`
and its report. It gives: upstream wolf/downstream lamb; water-direction
rebuttal; a second six-month allegation defeated by the lamb's not-yet-born
status; a new father participant; killing; and the narrator's moral about
invented causes.

### Complete finite constructor

`LOCATE(wolf,upstream)`, `LOCATE(lamb,downstream)`,
`ACCUSE(speaker,addressee,claim)`, `REBUT(argument,claim)`,
`ENDORSE(narrator,argument)`, `INTRODUCE_KIN(father,lamb)`,
`ACT(wolf,kill,lamb)`, and `MORAL(generalization)` consume every source role.
The first rebuttal computes causal direction (water runs from wolf toward
lamb); the second computes temporal existence (the lamb was not born six
months earlier); the father substitution changes the alleged participant; the
later killing is an action and does not upgrade either allegation to a fact.

### Status and contrast

This model is a deliberate retained duplicate of IDEA397 and IDEA415, so no
new card is added. It remains useful as the third family in this shortlist:
its discriminator is commitment scope plus a non-entailing outcome, unlike
Euclid's endpoint congruence and Aristotle's purpose/incidence distinction.
The flat-truth rival and outcome-validates-charge rival are already named in
those retained cards; this dossier does not silently reopen them.

## Supply decision

Register A and B as new `RAW_UNREVIEWED` cards below. Keep C attached as an
explicit duplicate/no-add model. None independently identifies a Voynich
participant, role, or word meaning. The smallest later review would choose one
already exposed complete report-owned passage, freeze a finite writer with all
typed arguments visible, and compare the named rival's changed relation; no
new target access is justified by this source supply alone.

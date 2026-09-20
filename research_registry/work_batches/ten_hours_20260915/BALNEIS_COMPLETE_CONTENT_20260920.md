# Four complete bath descriptions: source content before a target contract

Phase: exploratory source construction. Root,20September2026. This is a source
reading, not a Voynich translation. No new Voynich paragraph was opened or
selected for this construction. All earlier manuscript exposure remains.
GDT967's original fixed lexical-incidence failure is unchanged.

## Sources and interpretation policy

The base remains the unchanged [ALIM553 text](balneis_cache/ALIM553.txt),
SHA256 `397968f02fc5faf54161f2c0df9e7557f96d36e649a27a140e64c2cfe0c69ecd`.
Numbers below are physical source-file lines, not an invented verse numbering.
The complete bodies are VII74–85, XI123–134, XIX219–230 and XXXIII393–404.
XI's separate heading is line122. Source headings are metadata, not silently
discarded prose. The source attribution and edition are recorded in GDT211.

Root also directly viewed the complete manuscript pages7v,11v,26v,35v of
[Cologny, Fondation Martin Bodmer, Cod. Bodmer135](https://www.e-codices.unifr.ch/de/list/one/fmb/cb-0135),
first at reduced size and then at original image resolution. This is a separate
medieval witness, not a correction silently substituted into ALIM. The
[IIIF manifest](https://www.e-codices.ch/metadata/iiif/fmb-cb-0135/manifest.json)
and image identities are in the adjacent receipt. No image pixels are republished.
The observations are the model's own visual readings, without expert review or
OCR. Normalized u/v and expanded abbreviations in the notes are interpretive.

The institution's digital images are attributed to e-codices, CC BY-NC4.0.
The newly consulted Musa Medievalis display uses the same modern edition family;
it is not counted as an independent textual witness. Search excerpts from other
editions were navigation only and do not resolve the uncertain readings below.

All therapeutic statements below describe what the historical source claims.
They are not assertions of efficacy. No botanical or medical word is thereby
assigned to Voynich script.

## A shared representation, with its limits

Use referents `W`(this bath's water), `B`(the bath/place), `P`(recipient),
`D`(ailment), `S`(spring), and explicitly introduced parts/people/places.
These are analytical variables, not proposed written signs. Clause operations
include `LOCATE`, `ATTRIBUTE`, `AFFECT`, `CAUSE`, `CONDITION`, `NEGATE`,
`COMPARE`, `ADVISE`, `REPORT`, `WITNESS`, `REPEAT` and `TEMPORAL`.
Arguments retain their owners: the patient's heat tolerance is not water heat;
water's cooling is not cooling the patient. The same operation may act on
different types only where its argument structure states this.

`AFFECT(W,P,benefit)` cannot replace a named effect such as restoring sight.
Effect content, degree, source restriction, contrast and reported status are
separate fields. No unique token meaning “the whole of clause123” is permitted.
Body parts and named ailments are concept constants, including genuine source
singletons. Their number does not itself make a manuscript code identifiable.

The tables cover every source line. They do **not** establish a fully resolved
formal source: several readings and scopes remain explicitly open. A line with
an unresolved relation is not a free residual slot for matching a target.

## VII — Foris Cripte, all12lines

| Line | Complete content obligation | Shared representation and scope |
|---|---|---|
|74|The named water emerges/is situated beside the sea shore.|`LOCATE(W,NEAR(sea_shore))`; introduction of the named bath/water. “edita” retains emergence versus situation as a lexical nuance.|
|75|It removes the burden of weakness from the stomach.|`AFFECT(W,stomach,REMOVE(weakness))`; burden metaphor retained in the wording, not a separate measured load.|
|76|It harms dropsical recipients although very sweet to drink.|`CONTRAST(ATTRIBUTE(W,sweet,drink,very),AFFECT(W,P[hydrops],harm))`; sweetness is no positive-effect entailment.|
|77|It lacks a consuming/reducing power; that explains the harm.|`CAUSE(NEGATE(HAS_POWER(W,consume)),harm76)`; object of “consume” is not supplied by the line. Do not silently insert a particular humour.|
|78|It is accustomed to cool heated limbs gently.|`HABITUAL(AFFECT(W,limbs[heated],cool,gently))`; ALIM ignitos versus native inignitos/ignitos reading noted below.|
|79|It heals an injured lung and then/also the liver.|Two owned effects on lung and liver; `inde` leaves temporal versus connective nuance open. Injury is explicit for lung, not automatically copied to liver.|
|80|It is a remedy for the chest and a friendly remedy for cough.|Two benefit descriptions, chest and cough; “friendly” evaluative modifier retained. They are not two identical claims about one organ.|
|81|It moistens limbs dried by the burning heat of fever.|`AFFECT(W,limbs[DRIED_BY(heat[fever])],moisten)`; causal qualification belongs to the patient's limbs.|
|82|That water is led through hidden passages of the earth.|`PASSAGE(W,hidden(earth_channels))`; same referent as next line, not a new independent application command.|
|83|It helps sick people whose skin is diseased.|`AFFECT(W,P[sick AND diseased(skin)],benefit)`; the skin condition is retained.|
|84|The ancients are cited; the stated matter is remarkable to tell.|`REPORT(ancients,claim85)` plus `EVALUATE(claim85,remarkable)` is the provisional forward scope; a wider closing scope remains possible.|
|85|A water-supply relation involving Foris Cripte and Bulla.|`SUPPLY(source,destination,water)` with unresolved orientation across witnesses; no fixed Bulla-to-Foris edge is licensed from this collation.|

The previous reading of “consuming power” did not name its exact physiological
object. The source does not authorize turning it into a specific evaporation,
drainage or phlegm-removal operation. It also does not say that drinking very
sweet water in general harms every dropsical person.

## XI — Sancta Anastasia, all12lines

| Line | Complete content obligation | Shared representation and scope |
|---|---|---|
|123|People attribute/dedicate this bath to Anastasia.|`ATTRIBUTE(people,B,Anastasia)`; an attribution statement, not merely an arbitrary bath-name token.|
|124|It provides many advantages for human use.|`AFFECT(B,human_use,benefit,many)`; general evaluative introduction.|
|125|It refreshes the limbs of the “ingratus” body.|`AFFECT(W,limbs(body[ingratus]),refresh)`; sick/unpleasant/ungrateful nuance is not resolved into a new clinical diagnosis.|
|126|The water also renews the body's powers.|`AFFECT(W,powers(body),renew)`; renewal here concerns bodily powers, not replacement of the water in134.|
|127|A remarkable fact: whoever digs the sand…|`EVALUATE(claim128,remarkable)` and `CONDITION(DIG(P,sand),claim128)`; not a completed event in one patient's biography.|
|128|…hot water flows in the middle of the hole.|`FLOW(W[hot],AT(middle(hole_from127)))`; owner of the hole is the digging clause.|
|129|That water, fresh in its own spring, removes symptoms…|`AFFECT(W[fresh AND at(own_spring)],P,REMOVE(symptoms))`, under130.|
|130|…if the sick person can endure the water's heat.|`CONDITION(ENDURE(P[sick],heat(W)),claim129)`; this is a recipient guard, not a guarantee for every user.|
|131|Removed from its spring, it brings no utility.|`AFFECT(W[removed_from(own_spring)],P,utility,none)`; **not** “water left at its source”.|
|132|The same water, made cold, is of little benefit.|`AFFECT(W[cooled],P,benefit,little)`; same kind/referent is stated, but no executed cooling event or location is fixed.|
|133|Whoever seeks good relief from their illness…|`SEEK(P,RELIEF(own_illness,well))`; native witness says cito, quickly, in place of ALIM bene, well.|
|134|…will experience help if they renew the water.|`CONDITION(RENEW(P,W),AFFECT(W,P,benefit))`; antecedent P comes from133. Water replacement versus refreshing is a lexical uncertainty, not automatic physical identity conservation.|

The contrast is **not** the four-step instruction “take, remove, cool, renew the
same portion”. No executed trajectory and no conservation of a particular water
portion are written. Freshness, place, temperature and tolerance are different
dimensions. In particular, removed and cooled water are not declared disjoint
classes. On their overlap, literal exact-zero utility and small-positive utility
would conflict. A source reader must retain possible rhetorical approximation,
context restriction or unresolved overlap; it may not invent a precedence rule
after a target match. This affects a proposed numerical state machine even
though both clauses are understandable as ordinary prose.

Two renewals also concern different objects: bodily powers126 versus water134.
A serializer must either share a genuinely relational RENEW operation with
explicit objects, or declare separate senses in advance. It cannot collapse
the two clauses while claiming to preserve all content.

## XIX — Culma, all12lines, including the two previously truncated lines

| Line | Complete content obligation | Shared representation and scope |
|---|---|---|
|219|Culma is remarkable among other baths/waters.|`COMPARE(B,other_baths,remarkable)`; an introduction and evaluation.|
|220|Its approach has no straight path.|`NEGATE(STRAIGHT(path_to(B)))`; concerns access, not water flow.|
|221|Instead the waters are reached by a winding/oblique route.|`APPROACH(P,W,oblique_path)`; ALIM medicis versus native apparent modicas is left as a source variant.|
|222|A flame going ahead shows the uncertain way to you.|`SHOW(preceding_flame,path[uncertain],P)`; an access aid, not a written heating operation on the water.|
|223|The interior/hidden water provokes sweating within.|`AFFECT(W,P,CAUSE(sweating))`; native latens versus ALIM lateris changes the description of W and is retained.|
|224|It helps nerves weighed down by heavy phlegm/rheum.|`AFFECT(W,nerves[BURDENED_BY(heavy(humour))],benefit)`; the two witnesses use flegma/reuma. No automatic modern diagnostic equivalence.|
|225|It restores sight to eyes and steps to the lame…|Two restoration effects: vision and walking; guard226 provisionally scopes both.|
|226|…unless the ailment has been established for a long time.|`CONDITION(NOT(longstanding(D)),effects225)`; not an unconditional cure. A broader backward scope would be a different source analysis.|
|227|The assertion is called certain and known to many.|`REPORT(speaker,certainty(claim228))` and `KNOWN_TO(claim228,many)`; provisional forward scope, not independent clinical evidence.|
|228|Culma harms the healthy and helps diseased limbs.|Two recipient-conditioned effects of opposite polarity; generic “helps” does not erase the specific chronicity guard on225.|
|229|Therefore one who does not need treatment should avoid it.|`ADVISE(P[NOT(need_treatment)],AVOID(B))`; a recommendation with a recipient condition.|
|230|One who nevertheless seeks it should avoid lingering in the water.|Native `uitet … moram` supports `ADVISE(visitor,AVOID(long_stay_in_water))`; ALIM's nitet/peti wording is not silently replaced. Antecedent scope, all visitors versus the preceding healthy person, remains explicitly open.|

The generic help of sick limbs228 and the special non-chronic restoration225–226
must coexist. They cannot both be compressed to a universal “Culma cures disease”.
Nor does harm to healthy people imply that every ill person benefits under all
conditions. The access flame is not evidence of a separate fire-processing stage.

## XXXIII — De Cruce in ALIM, body at Bodmer135f35v, all12lines

| Line | Complete content obligation | Shared representation and scope |
|---|---|---|
|393|The water/bath of the Cross is strongly praised.|`EVALUATE(W_of_Cross,praiseworthy,very)`; witness rubric says Sancta Lucia while the body says Crucis. Keep both identities, not a silent equation.|
|394|The praise/benefit concerns people whose gout is already hardened/has dominated.|`RECIPIENT(P[podagra AND established])` attached to393; ALIM iam indurata and native condominata differ.|
|395|It strengthens nerves and expels phlegm from them.|`AFFECT(W,nerves,strengthen)` and `EXPEL(W,phlegm,FROM(nerves))`; them has an explicit local owner.|
|396|It helps dropsical recipients with a specified phlegmatic cause.|`AFFECT(W,P[hydrops CAUSED_BY(phlegm[qualifier])],benefit)`; qualifier ALIM grosso, native salso. Do not remove this condition to manufacture an exact counterpart to VII.|
|397|A clause mentioning consumption, a swollen spleen and liver.|ALIM Consueuit eam versus native Ipsam consumit: syntax/argument direction unresolved. No definite cure or consumption triple is asserted. This blocks a fully resolved four-record compiler.|
|398|It benefits a belly suffering a hypochondrial burden.|`AFFECT(W,belly[BURDENED_BY(hypochondrial_condition)],benefit)`; source grammar differs across witnesses. Preserve the historical category, not a modern psychiatric meaning.|
|399|For cold gout lodged in the nerves…|`RECIPIENT(P[cold_gout AT(nerves)])`, governing advice400.|
|400|…frequent the water, which grows as it is emptied.|`ADVISE(P,REPEAT(visit(W)))` and `RELATION(emptying(W),increase(W))`; not an unbounded physical law or self-replicating volume.|
|401|The speaker saw someone repeatedly bathe/visit here.|`WITNESS(speaker,REPEAT(visit(P0,B)))`; an explicitly introduced individual.|
|402|That person had been unable to bring a hand/hands to the mouth.|`NEGATE(ABLE(P0,BRING(hand,TO(mouth))))`; same P0, not a new generic patient.|
|403|After a short time, through enjoyment of the water's power…|`TEMPORAL(short_interval,claim404)` and `CAUSE(power(W),claim404)` are attributed by the speaker, not independently established.|
|404|…the person departed/returned healthy, under an explicit witness formula.|`BECOME(P0,healthy)` plus return/departure and `WITNESS(...)`; ALIM many witnesses versus native Christ as witness are different claims, retained separately.|

This is the only selected entry that contains a named-by-description individual
and an explicit before/after anecdote. Its story is not evidence that every other
entry should be serialized as an executed patient trajectory.

## Native collation: material differences, not an edited replacement text

| Body | Location | Root's native visual reading | Consequence |
|---|---|---|---|
|VII|7v, final verse|`Ipsa foriscripte bulle ministrat aquam`|Apparent bulle versus ALIM bulla prevents treating the supply direction as securely identical.|
|XI|11v, verse11|`Qui petit ergo suo cito de langore iuvari`|Quickly versus ALIM well is retained; both keep the relief-seeking recipient.|
|XI|11v, verses7–10|Fresh in own spring; patient must endure heat; removed from spring no utility; cooled little benefit.|Confirms the presence of distinct guards/degrees, not an executed four-state process.|
|XIX|26v, verses3,5,6|Apparent modicas; latens; reuma.|Do not silently normalize them to ALIM medicis/lateris/flegma. Modicas reading remains tentative.|
|XIX|26v, verses7–8|`Luminibus lumen reddit vestigia claudis / Passio ni fuerit inveterata diu`|The chronicity restriction is materially visible.|
|XIX|26v, final two verses|`Hanc igitur caveat qui non eget arte medendi / Nam qui forte petit uitet in amne moram`|Avoidance and avoidance of lingering are present; the beneficiary scope remains interpretive.|
|XXXIII|35v, rubric/body|Sancte Lucie / Crucis|Different heading and body identity must not be fused into an unqualified source key.|
|XXXIII|35v, verses2–5|`Iam quibus podagra condominata fuit`; `fleumata pellit`; `fleumate salso`; `Ipsam consumit splene tumente iecur`|Material qualifier and syntax differences;397 remains unresolved.|
|XXXIII|35v, final verse|`Teste michi Christo sanus et hinc redit` (normalized, last verb read as redit)|Witness formula differs from ALIM; return/departure variant retained, not harmonized.|

These are selected collation notes from inspection of all four full pages, not a
claim to a critical edition. Abbreviations and ambiguous letters remain human
reading judgments. The old source caches and experiments are byte-preserved.

## What this construction permits next

The four records cannot honestly be reduced to one signed-effect table or one
deterministic water trajectory. Complete content includes attribution, route
description, causation, metaphor, advice, testimony, different argument owners
and uncertain source clauses. Generic positive/negative matching would lose
the actual information intended to help identify a reading.

XI is the best bounded *complete-content candidate* of these four because its
12lines can be represented without inventing a missing main relation. Its
qualifier and overlap uncertainties still have to be frozen in any writing
contract. That is source-side suitability, not a Voynich match or independent
confirmation. A next target attempt must encode the attribution and digging
episode as well as the attractive water-condition contrasts. It must keep the
two differently owned renewals and avoid converting all words into machine
steps. It may not obtain “full coverage” by giving every unmatched clause its
own arbitrary atom.

No target serialization is selected in this document. Source coverage and source
plausibility do not themselves supply a historical code. The known GDT887
whole-word code failure, GDT967 lexical-incidence failure, GDT979 partial-action
code failure and GDT980 truth-without-information counterexample remain live
countercases. GDT596's exact reconstruction of an analyst-written bath reader
does not supply the missing semantic binding; GDT933 shows why unexplained
intervening groups cannot be filled with reference defaults.

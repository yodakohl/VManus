# GDT888 — Joint named-mention reconstruction with a held record

## Decision and budget

Can one global code for six independently named Alphita headwords reproduce
complete name-mention counts across five training records and predict a sixth
record on other physical leaves? No compatible training lexicon rejects this
finite name compiler; multiple lexicons leave the reconstruction unidentified.
Only one common surface lexicon permits the frozen held-record prediction. A
successful prediction yields a conditional candidate requiring independent native
and semantic validation, not confirmed words. Budget80min05:20–06:40UTC includes
preparation, implementation, validation and publication. That window was interrupted
before any target fit. On resumption16:59UTC, the remaining fixed implementation,
validation and publication were reassessed with a17:00–18:00UTC limit. The inactive
gap is not research time; no source or scientific contract changes. No automatic segmentation,
suffix, exception, weaker-count or control-corpus successor.

GDT187/214 did not bind a global externally named graph. GDT341/342 compared
record-local anonymous recipe graphs. GDT887's ordinary Latin-atom/group equations
failed before their entity stage; no such ordinary-atom equations are reused here.
GDT735/737 motivate considering a fixed prefix/body rule, but establish no name
meaning or grammatical case. This is a distinct pre-target source-graph contract.

## Independently collated source

Use Selden B.35 as printed in Mowat1887 Alphita: source objects95/97/99/152/170/228,
printed32/34/36/89/107/165. SOURCE.json preserves complete article bodies, native
image pointers/hashes, exact name positions and qualifications. Bracketed Selden
material stays; Sloane-only additions and modern notes do not enter the graph.
The source-stage OCR navigation was unreliable for ownership and qualified names;
all six selected articles were instead collated directly against the printed pages.

Names C=Cardo, B=Cardo benedictus, D=Carduncellus, L=Labrum ueneris,
M=Matrona, S=Senecio. Within these six exact names, count every written body
mention, irrespective of whether its relation is Respice, identity or another
construction. These are name-incidence edges, not claims that all are Respice
edges or botanical equivalences. Match the longest complete name first; B never
also contributes C. Do not merge Matrana with Matrona or Senecium/Senicion with S.
D followed by [terestris] contributes the written D name, retaining its modifier.
Names outside this fixed six-name universe remain outside the count model.

Training rows, with repeated names retaining multiplicity:

    C: L
    B: D S L S
    D: B
    L: C
    M: C

The entire S outgoing row is excluded from FIT_TEMPLATE.json and the fitter.
Its expected body incidence remains only in SOURCE.json and the evaluator.
The source graph remains connected and asymmetric when S's complete outgoing
row is withheld. This source-only fact does not imply a unique Voynich embedding.

## Fixed target and literal encoding

Reuse GDT887 SELECTED.json, its665 complete ZL-defined blocks and unchanged
reading eligibility. Six mixed non-P frames remain excluded whole. ZL3b/IT2a/RF1b
are readings of one manuscript, plus a strict all-three raw/STA consensus panel.
This is a new computational split of existing admitted data, not previously unseen
manuscript material. No additional selectors or images; f84/f84r remain sealed.

Training records come only from odd numbered physical fNN leaves. The five
assigned training records occupy five distinct leaves. Even-leaf input to fitting
contains only eligible first-group codes and paragraph/leaf identifiers; no even
body groups. Whole-block eligibility is the previously frozen data-quality rule.
A matching even head must exist for S. All matching eligible even S-head blocks
are retained for prediction, with physical-leaf dependence explicit.

Each first complete STA group is hypothesized to encode its entry head. All
remaining groups constitute its body. For each of six distinct nonempty bodies B_e:

    head(e) = P_head + B_e
    mention(e) = P_body + B_e

Both global prefixes have0,1 or2 exact STA members. Enumerate every prefix pair;
no suffix or per-name/hand/paragraph alteration is permitted. Distinct bodies imply
distinct names within either context; cross-context coincidences are allowed.
For every training record, the complete multiset of its body groups matching any
of the six mention forms must equal its frozen row exactly, including zeros and
multiplicities. Other groups remain unmodelled, rather than receiving invented
translations. This assumes selected name forms are not homographs of unmodelled
contents in these records. It is not a whole-paragraph Latin translation.

## Identification, held prediction and validation

Enumerate every compatible training assignment, distinct body map and prefix pair.
Alternative prefix decompositions count as one surface lexicon only if all six
head and mention forms are identical. Alternative training paragraphs may share
that lexicon; retain every assignment. No ranking or held-body filtering chooses
among competing lexicons. Incomplete enumeration permits no uniqueness claim.

The default run writes the fit and its concrete PREDICTIONS.json without reading
held bodies. If a reading panel has exactly one surface lexicon, freeze and publish
those predictions before a separate run.py --evaluate invocation opens its held input.
Predict from the external S article the exact counts of all six learned mention
forms in every retained eligible even S-head body. Zero or several lexicons stop
that panel before held-body evaluation. Report all predictions and failures; a
failed held prediction cannot be repaired by selecting a different training fit.
Reading panels remain separate and do not supply independent replication.

Independent validation recompiles source counts, checks the source-only symmetry
claim, replays the blinded target projection and separately enumerates complete
solutions. Positive, contradictory, alternate-prefix and competing-lexicon fixtures
must pass. New positive relation evidence requires a GDT388 packet and all capacity,
held-folio, provenance and mobile-null gates before any score or semantic promotion.
A compatibility count or source-only asymmetry is not a passed relation gate.

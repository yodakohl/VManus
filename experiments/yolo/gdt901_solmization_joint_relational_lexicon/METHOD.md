# GDT901 — joint relational lexicon for a complete operational register

Decision2026-09-10 02:12UTC. Wholebudget02:12–03:32UTC80minutes: source/compiler
checkpoint02:27, preparation/implementation, atmost30minfit/projections, independent
validation andpublication. No automatic source/compiler/optimizerrepair atlimit.

Unknown after888/899: does a complete externallynamed operational network force
one shared manuscriptlexicon when allrecordassignments and allwordvalues are
unknown together?888's six-name incidence graph had18differentITlexicons; its
asymmetric source didnotidentify a targetembedding.899's complete condition-code
model timedout; failure to find a key was not exclusion. This is a different
source and a relational whole-word projection law, not another solver for899.
No prior workingGerman meanings, learned prefixes or heldtext are inherited.

Source: Hieronymus of Moravia, Tractatus de musica chapter12, fixedTML electronic
transcription of Cserba1935 pp49–55. Wholechapter:22pitchrecords (flat/squareB
separate twice and modernaddition ee retained),42voice/origin/cantus memberships,
52explicit directedmutations, eightzero records. Two independent source readings
must agree before selection. Source graph rigidity is conditional on complete
relations, not evidence for their presence in Voynich. No native medieval or
printededition collation is claimed by the electronic source check.

Compiler projects each whole pitchrecord to its named pitch, then each membership
in sourceorder (voice,cantustype,origin), then each detailed mutation in source
order (fromvoice,tovoice,direction,destinationcantus,destinationorigin). A zero
record ends with ZERO. Origins equal to the record's pitch use one shared SELF
atom, resolved by the recordhead. Explicit source-pitch spellingaliases are
bound in the sourcegraph. Every record, membership, mutation and zero is included.
The introductory duplicate voice/pair lists and explanatoryprose are not copied;
this is a complete operational-register projection, not literal Latin prose.
The no-cross-pitch prohibition is enforced by mutation construction. Flat/squareB
remain distinct values; the absence of naturalhexachordorigin cc is preserved.

The morphological model is the pre-fit union in MODEL_SPEC.json: pitch names
have HEAD and ORIGIN roles; voices have MEMBER, FROM and TO roles. Two global
partitions of pitchroles and five globalpartitions of voiceroles give10cases.
Within a roleclass, each completeword is one globalprefix plus the semantic
root plus one globalsuffix. The root is nonempty and shared across allroles;
affixes may be empty. Different realized form atoms have distinct completeword
values. Role equality is global for the family, with no root-specific syncretism.
Cantus types, directions, SELF and ZERO have one wholewordvalue each. The fully
merged rolecase is the original35-atom wholeword model. Case formcounts range
from35 to54; sourcegraph, events and all416positions remain unchanged.

Every unassigned targetwordtype is globalbackground. For each of22distinct
selected wholeparagraphs, removing background words must produce its ENTIRE
fixed realized-form record in order. First rawword encodes the pitchhead.
There are no pertoken background choices, BPE units, cleanup, free record IDs
or soft mismatches. This is a conceptual register inside surrounding text;
it does not claim that every source or target proseword is translated.

Target is only the fixed alreadyexposed GDT893odd wholeparagraph packet: ZL14,
IT259,RF11,CONS1. All22source records mandatory withinONE panel; paragraphs
selectedjointly with wordvalues. Insufficientpanels stopforcapacity. No evenbody,
newvisualpage, rawmixedsource or other sourcewindow. Alternative readings are
one manuscript. Any candidate remains conditional until independent heldmeaning
and unchanged relation gates could be satisfied; none is assumed here.

Complete finite inference: assign atomwordvalues and paragraphindices jointly.
For every realizedform and source record, its exact sourcecount must equal its assigned
word's complete targetparagraphcount. Head constraints, global realized-form injectivity and exact sharedroot/affix
factorizations alsoapply. These necessary countconstraints form the initial CP-SAT model.
For a candidate, replay the entire projected sequence. If it differs, impose
only a necessary forbidden tuple (paragraphindex,wordvalueA,wordvalueB) for each
violated two-atom projection. Pairwise projections plus individual counts uniquely
determine a word; these cuts do not change the model or drop validsolutions.
Continue until a fullwitness, completeUNSAT, or UNKNOWN at the fixedbudget.
Derived histogram and head domains may remove impossible values without tuning.

A positive witness must replay all22completeparagraphprojections, allsharedvalues
and distinct records. Then query each realized-form wordvalue and eachrecordlocation against
the ORIGINAL complete model with that one first-witnessvalue forbidden; do not
freeze other variables. Eachquerycap30seconds, sharedfit/projectionbudget1800s.
Exact queries retain necessary lazycuts. Report SAT alternatives, proved fixed
values, or UNKNOWN; no best-score selection. Missing witnesses cannot establish
exclusion. An ambiguouslexicon is unidentified; a uniqueconditionalkey still
requires independentmeaning evidence. A complete exclusion closes only this
source/compiler/head/background/lexicon/scope conjunction. No threshold or source
repair follows any outcome.

Checkpoint02:14:48 sourcefreeze SHA0daf60d86d63ec371137378310871dd0f3bc0b7d16ac78770986b66647fe5d65:
22records35atoms416positions. Bothsourcegraphs agree, and SELF resolution
recovers the full operational network. A first exactnecessary domain stage is
part of this model: for eachatom, the histogram of its counts acrossall22source
records must fit injectively into the histogram of a single candidateword's
counts across alltargetparagraphs. Exactmultiplicity0 is included. Headatoms
must also occur as paragraph-firstwords. Empty domains prove the fullmodel
impossible; nonempty domains do not identify a key. Full CP-SAT implementation
is required only if this necessary stage leaves a panel, under the unchanged
registered contract and totalbudget. No model change is licensed by the gate.

Pre-fit morphologyfreeze02:23:12UTC (MODEL_SPEC SHA119be016d348b28d0915792bdb59a2c4f40496ed821be9c5fcddae2c2856b17a)
retains the original source seal and its35-atom audit. No actual targetdomain
or fit result existed when this union was chosen. Histogram necessity is
applied separately to every realized form in each of the10cases; it ignores
root/affix constraints only as a sound relaxation. A surviving histogram domain
is not a morphological witness. Union exclusion requires everycase tofail.
A unique complete surfacelexicon need not identify its stem/affix factorization.
Those parameters must be separately projected before any stemmeaning claim; a
first factorization or an arbitrary canonical boundary cannot establish one.

Implementation checkpoint before the full fit: all10 IT histogram domains
survive, independently reproduced; otherpanels have fewer than22paragraphs.
The unchanged10cases run concurrently, each with1800seconds total including
model construction, necessary cuts and projections, two CP-SAT workers percase.
Outer cleanup allowance20seconds, no restart. OR-Tools9.14.6206; independent
Z3 count/head relaxation runs10cases withoneworker each,1200seconds including
construction. At most30 solverworkers combined. Its SAT is relaxationonly;
its UNSAT excludes that completecase. Fullmodel UNSAT requires the exact primary
encoding; independently replayed positive witnesses and necessary cuts do not
constitute independently proved universal solverresults. Exact necessary-domain
JSON bytes are stored with deterministic gzip compression; no value changed.

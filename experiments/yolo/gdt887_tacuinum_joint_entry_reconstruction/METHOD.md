# GDT887 — Joint inverse medical-record compiler

## Question and research decision

Can three complete Voynich paragraphs realize one fixed, externally named
Tacuinum entry network, with a common lexeme dictionary and one shared change
between entity heads and corrective mentions? The source identity at Apium's
corrective field is withheld from the fitter and must be completed as one of
Lactuca, Piretrum, Apium or Feniculum. This is source-fact completion within a
finite candidate set, not a claim of unseen Voynich folios or independent human
blindness. The source answer was known during design.

GDT809 supplied16 hypothetical dictionary entries for46/145 positions in four
paragraphs; it did not bind every position to a named external record network.
735/737 establish some prefix/body and positional structure but no head meanings.
814 leaves quality, polarity and possessive alternatives open. Here complete
paragraph equations, repeated atoms, fixed field order and global entity bodies
must agree jointly. Private singleton atoms contribute position/coverage only;
they provide no independent lexical evidence. This is a new conditional notation
model, not evidence that the Voynich is a Tacuinum copy or written in Latin.

Decision: no solutions excludes this finite compiler on eligible paragraphs;
several possible held entities means no identifying reconstruction. Only if all
solutions choose Lactuca is the declared source-fact prediction fulfilled.
A named Voynich mapping additionally requires identical paragraph and group
assignments across every solution; successful fact completion alone is insufficient.
Any candidate needs a separately frozen independent manuscript test before meaning
promotion. Budget2h from03:57UTC, including preparation, validation and publication;
stop at05:57UTC. No automatic new tokenizer, suffix rule or control corpus.

## Fixed external serialization

SOURCE.json transcribes the entire three consecutive entries of BnF Latin9333,
external026r/026v/027r, from the cited MediManus edition. Gallica returned403;
no new original-folio collation is claimed. An independent comparison confirms
all three texts and field boundaries against the cached published transcription.

source.py defines a single lexical serialization before target access. The written
entity head Herba piretri is one named entity. Exact aliases join only declared
forms, including apium/apio/appio and lactuce/lactucis, thermal inflections and
first-degree forms. FINE remains distinct from DEGREE_I. The grammatical words
et/in/cum are uniformly implicit in the fixed record grammar. All other value
words remain in their source order. This omission is a model assumption, not a
claim that those words are unwritten in Latin or meaningless. Seven written field
rubrics are globally either implicit or explicit; these two finite variants have
34/24/17 or43/33/26 group slots respectively. No target length chooses atomization.

FIT_TEMPLATES.json is the fitter's sole source template. It contains a single typed
@HELD entity slot, constructed before reading its answer text. The fixed potential
identities are LACTUCA, PIRETRUM, APIUM, FENICULUM. No literal answer, source prose
or expected identity enters the fit. All source values, qualifiers and multiple
suitability arguments remain bound; no convenient four-equal-fields reduction.

## Target frame and encoding

Reuse only boundary metadata from GDT807's665 strict paragraphs, within the179-page
GDT631 allowlist. Rebuild complete unmasked source groups from the literal separator
and exact STA atlases through selector-first query-tsv. Source-marked P loci inside
the fixed numeric endpoints must reproduce each frame's source-line count and
boundary flags. Metadata disagreements are instrument failures, not negative fits.
Never read masked807 content/features as a complete paragraph.

Preserve every raw group and source ID. A paragraph-reading is eligible only when
all its P loci are available, every group is clear lowercase literal material with
definite internal separators, and every exact STA member sequence is nonempty
and has zero marked alternative sites. Exclude the whole reading on any failure;
never clip a difficult line. Analyse ZL3b, IT2a, RF1b separately and an all-three
identical raw-group/STA consensus panel. These are readings of one manuscript.
The three assigned paragraphs must lie on three distinct physical leaves, using
fNN keys. GDT807's misleading physical_folio column contains fNNr/v face keys;
retain that original metadata separately and normalize before the disjointness test. No
unknown source-order constraint or new visual admission is imposed.

One ordinary source atom has one globally fixed complete STA-group value; distinct
ordinary atoms have distinct values. For each entity e, a distinct nonempty body
B_e is shared by its forms:

    head(e) = P_head + B_e
    corrective(e) = P_corrective + B_e

The two global prefixes contain0,1 or2 exact STA members, chosen exhaustively.
They cannot vary by entity, paragraph, hand or occurrence. This one-sided model
is motivated by existing prefix/body structure, not by Latin declension endings.
No suffix change, glyph deletion or per-word exception is available. Entity surface
values, including both generated contexts for all four entities, cannot collide
with ordinary dictionary values. Cross-context collisions between different
entities are permitted; only their bodies must be distinct. Every target group occupies
exactly one source slot; no words remain as uncharged unknown padding.

## Exhaustive solution set and validation

For each reading and rubric variant, enumerate all complete length-compatible
paragraphs, retain all ordinary-atom-consistent assignments, then all disjoint-folio
triples with a compatible shared dictionary and every permissible prefix pair.
Infer the held identity from its resulting body among the four distinct entities.
Store every accepted assignment, prefixes, dictionary and group-aligned reading;
report the union of possible held identities. All solutions count, including those
predicting a different source identity. No fit ranking or desired-answer selection.
If budget prevents exhaustion, report INCOMPLETE; no uniqueness claim.

Validation independently reconstructs source-slot patterns and constraints,
replays guarded target reconstruction, checks every candidate assignment, and
checks positive and conflicting miniature instances. Prefix transfer ambiguity
must be enumerated, never resolved by the known external answer. An empty solution
set identifies no word; a nonempty set is conditional reconstruction only. f84 and
f84r stay forbidden. New relation evidence is not score-ready without GDT388 gates.
